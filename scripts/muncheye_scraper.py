#!/usr/bin/env python3
"""
MunchEye Scraper — Affiliate Promo Machine
Scrapes MunchEye.com for daily software launches, categorizes them as
regular or premium, and extracts structured product data.

Usage:
    python3 muncheye_scraper.py --mode today
    python3 muncheye_scraper.py --mode upcoming --days 7
    python3 muncheye_scraper.py --mode premium
    python3 muncheye_scraper.py --mode search --query "AI tool"

Output: JSON to stdout (pipe-friendly) or saved to file with --output flag.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print(json.dumps({
        "error": "Missing dependencies. Install with: pip3 install requests beautifulsoup4",
        "success": False
    }))
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_URL = "https://www.muncheye.com/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
REQUEST_TIMEOUT = 30  # seconds


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _safe_text(element):
    """Return stripped text from a BS4 element or empty string."""
    return element.get_text(strip=True) if element else ""


def _safe_attr(element, attr, default=""):
    """Return an attribute value from a BS4 element or default."""
    return element.get(attr, default) if element else default


def _parse_price(text):
    """Extract a numeric price from text like '$17', 'Free', '$27-$97'."""
    if not text:
        return {"raw": "", "low": 0, "high": 0, "is_free": True}
    text = text.strip()
    if text.lower() in ("free", "freebie", "$0", "0"):
        return {"raw": text, "low": 0, "high": 0, "is_free": True}
    prices = re.findall(r"\$?([\d,]+(?:\.\d{2})?)", text)
    nums = [float(p.replace(",", "")) for p in prices]
    return {
        "raw": text,
        "low": min(nums) if nums else 0,
        "high": max(nums) if nums else 0,
        "is_free": False,
    }


def _parse_date(text):
    """Attempt to parse a human-readable date string into ISO format."""
    text = text.strip() if text else ""
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return text  # return raw if unparseable


# ---------------------------------------------------------------------------
# Core Scraping
# ---------------------------------------------------------------------------
def fetch_page(url):
    """Fetch a URL and return a BeautifulSoup object."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as exc:
        print(json.dumps({"error": str(exc), "success": False}), file=sys.stderr)
        return None


def parse_launch_row(row):
    """Parse a single launch row/card from MunchEye into a structured dict."""
    launch = {
        "product_name": "",
        "vendor_name": "",
        "launch_date": "",
        "launch_date_iso": "",
        "price": {},
        "niche": "",
        "jv_page_url": "",
        "sales_page_url": "",
        "muncheye_url": "",
        "commission": "",
        "prize_pool": "",
        "is_premium": False,
        "description": "",
        "platform": "",
    }

    # Product name — typically in an <a> or heading inside the row
    name_el = (
        row.select_one("h2 a, h3 a, .launch-title a, td:first-child a, .product-name a")
        or row.select_one("a[href*='muncheye.com']")
        or row.select_one("a")
    )
    launch["product_name"] = _safe_text(name_el)
    launch["muncheye_url"] = urljoin(BASE_URL, _safe_attr(name_el, "href"))

    # JV page link
    jv_link = row.select_one("a[href*='jvpage'], a[href*='jvzoo'], a[href*='warriorplus']")
    if jv_link:
        launch["jv_page_url"] = _safe_attr(jv_link, "href")

    # Vendor
    vendor_el = row.select_one(".vendor, .launch-vendor, td:nth-child(2)")
    launch["vendor_name"] = _safe_text(vendor_el)

    # Date
    date_el = row.select_one(".launch-date, .date, td:nth-child(3), time")
    raw_date = _safe_text(date_el) or _safe_attr(date_el, "datetime")
    launch["launch_date"] = raw_date
    launch["launch_date_iso"] = _parse_date(raw_date)

    # Price
    price_el = row.select_one(".price, .launch-price, td:nth-child(4)")
    launch["price"] = _parse_price(_safe_text(price_el))

    # Niche / Category
    niche_el = row.select_one(".niche, .category, .launch-niche, td:nth-child(5)")
    launch["niche"] = _safe_text(niche_el)

    # Commission
    comm_el = row.select_one(".commission, td:nth-child(6)")
    launch["commission"] = _safe_text(comm_el)

    # Premium badge detection
    premium_indicators = row.select(".premium, .featured, .badge-premium, .star")
    if premium_indicators:
        launch["is_premium"] = True
    # Also check CSS classes on the row itself
    row_classes = " ".join(row.get("class", []))
    if any(kw in row_classes.lower() for kw in ("premium", "featured", "highlight")):
        launch["is_premium"] = True

    # Description snippet
    desc_el = row.select_one(".description, .launch-desc, p")
    launch["description"] = _safe_text(desc_el)

    return launch


def scrape_launches(url=BASE_URL):
    """Scrape all launches from a MunchEye page."""
    soup = fetch_page(url)
    if not soup:
        return []

    launches = []

    # Strategy 1: Table rows
    rows = soup.select("table tr, .launch-row, .launch-item, .launch-card, article.launch")
    for row in rows:
        # Skip header rows
        if row.find("th"):
            continue
        launch = parse_launch_row(row)
        if launch["product_name"]:
            launches.append(launch)

    # Strategy 2: If no table, try div-based layout
    if not launches:
        cards = soup.select(".entry, .post, .product-card, div[class*='launch']")
        for card in cards:
            launch = parse_launch_row(card)
            if launch["product_name"]:
                launches.append(launch)

    return launches


# ---------------------------------------------------------------------------
# Mode Handlers
# ---------------------------------------------------------------------------
def get_today_launches():
    """Get launches scheduled for today."""
    all_launches = scrape_launches()
    today = datetime.now().strftime("%Y-%m-%d")
    today_launches = [l for l in all_launches if l["launch_date_iso"] == today]
    # If date filtering yields nothing, return all (MunchEye homepage = today)
    return today_launches if today_launches else all_launches


def get_upcoming_launches(days=7):
    """Get launches within the next N days."""
    all_launches = scrape_launches()
    today = datetime.now()
    cutoff = today + timedelta(days=days)
    upcoming = []
    for launch in all_launches:
        try:
            ld = datetime.strptime(launch["launch_date_iso"], "%Y-%m-%d")
            if today <= ld <= cutoff:
                upcoming.append(launch)
        except (ValueError, TypeError):
            upcoming.append(launch)  # include if date unparseable
    return upcoming


def get_premium_launches():
    """Get only premium/featured launches."""
    all_launches = scrape_launches()
    return [l for l in all_launches if l["is_premium"]]


def search_launches(query):
    """Search launches by keyword in name, niche, or description."""
    all_launches = scrape_launches()
    query_lower = query.lower()
    return [
        l for l in all_launches
        if query_lower in l["product_name"].lower()
        or query_lower in l["niche"].lower()
        or query_lower in l["description"].lower()
    ]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Scrape MunchEye.com for software launches"
    )
    parser.add_argument(
        "--mode",
        choices=["today", "upcoming", "premium", "search", "all"],
        default="today",
        help="Scraping mode (default: today)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look ahead for 'upcoming' mode (default: 7)",
    )
    parser.add_argument(
        "--query",
        type=str,
        default="",
        help="Search query for 'search' mode",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    args = parser.parse_args()

    # Dispatch
    if args.mode == "today":
        launches = get_today_launches()
    elif args.mode == "upcoming":
        launches = get_upcoming_launches(args.days)
    elif args.mode == "premium":
        launches = get_premium_launches()
    elif args.mode == "search":
        if not args.query:
            print(json.dumps({"error": "--query required for search mode", "success": False}))
            sys.exit(1)
        launches = search_launches(args.query)
    else:
        launches = scrape_launches()

    result = {
        "success": True,
        "mode": args.mode,
        "count": len(launches),
        "scraped_at": datetime.now().isoformat(),
        "launches": launches,
    }

    indent = 2 if args.pretty else None
    output = json.dumps(result, indent=indent, default=str)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Saved {len(launches)} launches to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
