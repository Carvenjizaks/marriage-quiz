#!/usr/bin/env python3
"""
JV Page Analyzer — Affiliate Promo Machine
Visits a JV (Joint Venture) page and extracts all affiliate-relevant data:
swipes, commission details, prize pools, sales page URL, demo links, etc.

Usage:
    python3 jv_page_analyzer.py --url "https://example.com/jv"
    python3 jv_page_analyzer.py --url "https://example.com/jv" --output analysis.json

Output: Structured JSON with all extracted data.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse

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
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
REQUEST_TIMEOUT = 30


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _safe_text(el):
    return el.get_text(strip=True) if el else ""


def _safe_attr(el, attr, default=""):
    return el.get(attr, default) if el else default


def _extract_emails_from_text(text):
    """Extract email addresses from text."""
    return list(set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)))


def _extract_urls(soup, base_url):
    """Extract all unique URLs from the page."""
    urls = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("http", "//")):
            urls.add(href)
        elif href.startswith("/"):
            urls.add(urljoin(base_url, href))
    return list(urls)


# ---------------------------------------------------------------------------
# Extraction Functions
# ---------------------------------------------------------------------------
def extract_commission_details(soup, page_text):
    """Extract commission percentages and structure."""
    commissions = {
        "front_end": "",
        "upsells": "",
        "recurring": "",
        "raw_mentions": [],
        "cookie_duration": "",
        "platform": "",
    }

    # Look for commission percentages
    commission_patterns = [
        r"(\d{1,3})%\s*(?:commission|commissions)",
        r"commission[s]?\s*[:=]\s*(\d{1,3})%",
        r"(\d{1,3})%\s*(?:across|on)\s*(?:the\s*)?(?:entire\s*)?funnel",
        r"front[\s-]?end\s*[:=]?\s*(\d{1,3})%",
        r"(?:OTO|upsell)[s]?\s*[:=]?\s*(\d{1,3})%",
    ]
    for pattern in commission_patterns:
        matches = re.findall(pattern, page_text, re.IGNORECASE)
        commissions["raw_mentions"].extend(matches)

    # Front-end commission
    fe_match = re.search(r"front[\s-]?end\s*[:=]?\s*(\d{1,3})%", page_text, re.IGNORECASE)
    if fe_match:
        commissions["front_end"] = f"{fe_match.group(1)}%"

    # General commission (if no front-end specific)
    if not commissions["front_end"]:
        gen_match = re.search(r"(\d{1,3})%\s*commission", page_text, re.IGNORECASE)
        if gen_match:
            commissions["front_end"] = f"{gen_match.group(1)}%"

    # Platform detection
    if "jvzoo" in page_text.lower():
        commissions["platform"] = "JVZoo"
    elif "warriorplus" in page_text.lower() or "warrior+" in page_text.lower():
        commissions["platform"] = "WarriorPlus"
    elif "clickbank" in page_text.lower():
        commissions["platform"] = "ClickBank"

    # Cookie duration
    cookie_match = re.search(r"(\d+)[\s-]?day\s*cookie", page_text, re.IGNORECASE)
    if cookie_match:
        commissions["cookie_duration"] = f"{cookie_match.group(1)} days"

    return commissions


def extract_prize_details(soup, page_text):
    """Extract JV contest / prize pool information."""
    prizes = {
        "total_pool": "",
        "positions": [],
        "contest_dates": "",
        "raw_text": "",
    }

    # Prize pool total
    pool_match = re.search(
        r"\$\s*([\d,]+(?:\.\d{2})?)\s*(?:in\s*)?(?:prize|cash|contest)",
        page_text, re.IGNORECASE
    )
    if pool_match:
        prizes["total_pool"] = f"${pool_match.group(1)}"

    # Individual prize positions
    position_patterns = [
        r"(?:1st|first)\s*(?:place|prize)?\s*[:=\-]?\s*\$\s*([\d,]+)",
        r"(?:2nd|second)\s*(?:place|prize)?\s*[:=\-]?\s*\$\s*([\d,]+)",
        r"(?:3rd|third)\s*(?:place|prize)?\s*[:=\-]?\s*\$\s*([\d,]+)",
    ]
    labels = ["1st Place", "2nd Place", "3rd Place"]
    for pattern, label in zip(position_patterns, labels):
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            prizes["positions"].append({
                "position": label,
                "amount": f"${match.group(1)}"
            })

    # Contest dates
    date_match = re.search(
        r"contest\s*(?:runs?|dates?|period)\s*[:=]?\s*(.+?)(?:\.|$)",
        page_text, re.IGNORECASE
    )
    if date_match:
        prizes["contest_dates"] = date_match.group(1).strip()

    return prizes


def extract_swipes(soup):
    """Extract email swipes from the JV page."""
    swipes = []

    # Common swipe containers
    swipe_sections = soup.select(
        ".swipe, .email-swipe, .swipes, [id*='swipe'], "
        "[class*='swipe'], .email-copy, .promo-email, "
        "textarea, pre, .copy-box"
    )

    for section in swipe_sections:
        text = section.get_text(strip=True)
        if len(text) > 50:  # Filter out short snippets
            swipes.append({
                "content": text[:3000],  # Cap at 3000 chars
                "subject_line": "",
                "type": "extracted",
            })

    # Try to find subject lines
    subject_patterns = soup.find_all(
        string=re.compile(r"subject\s*(?:line)?[:=]", re.IGNORECASE)
    )
    for sp in subject_patterns:
        parent = sp.parent
        if parent:
            text = parent.get_text(strip=True)
            subj_match = re.search(r"subject\s*(?:line)?[:=]\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
            if subj_match:
                for swipe in swipes:
                    if not swipe["subject_line"]:
                        swipe["subject_line"] = subj_match.group(1).strip()
                        break

    return swipes


def extract_sales_page_url(soup, page_text, base_url):
    """Find the sales page / product page URL."""
    # Common patterns for sales page links
    selectors = [
        "a[href*='salespage']",
        "a[href*='sales-page']",
        "a[href*='preview']",
        "a[href*='demo']",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            return _safe_attr(el, "href")

    # Look for links with text containing "sales page", "preview", "demo"
    for a in soup.find_all("a", href=True):
        link_text = a.get_text(strip=True).lower()
        if any(kw in link_text for kw in ("sales page", "preview", "demo", "see the offer")):
            return a["href"]

    # Regex in page text
    sp_match = re.search(
        r"(?:sales\s*page|product\s*page|preview)\s*[:=]?\s*(https?://[^\s<\"']+)",
        page_text, re.IGNORECASE
    )
    if sp_match:
        return sp_match.group(1)

    return ""


def extract_demo_urls(soup, page_text):
    """Extract demo/preview video and page URLs."""
    demos = []

    # Video embeds
    for iframe in soup.find_all("iframe", src=True):
        src = iframe["src"]
        if any(domain in src for domain in ("youtube", "vimeo", "wistia", "loom")):
            demos.append({"type": "video", "url": src})

    # Video links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True).lower()
        if any(kw in text for kw in ("demo", "preview", "watch", "video")):
            demos.append({"type": "link", "url": href, "label": a.get_text(strip=True)})
        elif any(domain in href for domain in ("youtube.com", "vimeo.com", "youtu.be")):
            demos.append({"type": "video", "url": href})

    return demos


def extract_product_features(soup, page_text):
    """Extract product features and selling points from the page."""
    features = []

    # Look for bullet points / list items in feature sections
    feature_sections = soup.select(
        ".features, .product-features, [class*='feature'], "
        "ul, ol"
    )
    for section in feature_sections:
        items = section.find_all("li")
        for item in items:
            text = item.get_text(strip=True)
            if 10 < len(text) < 500:
                features.append(text)

    # Deduplicate
    seen = set()
    unique_features = []
    for f in features:
        normalized = f.lower().strip()
        if normalized not in seen:
            seen.add(normalized)
            unique_features.append(f)

    return unique_features[:20]  # Cap at 20 features


def extract_vendor_bonuses(soup, page_text):
    """Extract bonuses offered by the vendor."""
    bonuses = []

    # Look for bonus sections
    bonus_sections = soup.select(
        ".bonus, .bonuses, [class*='bonus'], [id*='bonus']"
    )
    for section in bonus_sections:
        items = section.find_all(["li", "div", "p", "h3", "h4"])
        for item in items:
            text = item.get_text(strip=True)
            if 10 < len(text) < 500 and "bonus" in text.lower():
                bonuses.append(text)

    # Regex fallback
    if not bonuses:
        bonus_matches = re.findall(
            r"bonus\s*#?\d*\s*[:=\-]?\s*(.+?)(?:\n|<|$)",
            page_text, re.IGNORECASE
        )
        bonuses.extend([m.strip() for m in bonus_matches if len(m.strip()) > 10])

    return bonuses[:10]


def extract_pricing_tiers(soup, page_text):
    """Extract pricing tiers / funnel structure."""
    tiers = []

    # Common patterns
    tier_patterns = [
        (r"front[\s-]?end\s*[:=\-]?\s*\$\s*([\d,.]+)", "Front-End"),
        (r"(?:OTO|upsell)\s*#?1\s*[:=\-]?\s*\$\s*([\d,.]+)", "OTO 1"),
        (r"(?:OTO|upsell)\s*#?2\s*[:=\-]?\s*\$\s*([\d,.]+)", "OTO 2"),
        (r"(?:OTO|upsell)\s*#?3\s*[:=\-]?\s*\$\s*([\d,.]+)", "OTO 3"),
        (r"(?:OTO|upsell)\s*#?4\s*[:=\-]?\s*\$\s*([\d,.]+)", "OTO 4"),
        (r"downsell\s*[:=\-]?\s*\$\s*([\d,.]+)", "Downsell"),
    ]
    for pattern, label in tier_patterns:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            tiers.append({"name": label, "price": f"${match.group(1)}"})

    return tiers


# ---------------------------------------------------------------------------
# Main Analyzer
# ---------------------------------------------------------------------------
def analyze_jv_page(url):
    """Full analysis of a JV page. Returns structured JSON."""
    result = {
        "success": False,
        "url": url,
        "analyzed_at": datetime.now().isoformat(),
        "product_name": "",
        "commission": {},
        "prizes": {},
        "swipes": [],
        "sales_page_url": "",
        "demo_urls": [],
        "features": [],
        "vendor_bonuses": [],
        "pricing_tiers": [],
        "all_urls": [],
        "contact_emails": [],
        "page_title": "",
        "meta_description": "",
    }

    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        result["error"] = f"Failed to fetch page: {str(exc)}"
        return result

    soup = BeautifulSoup(resp.text, "html.parser")
    page_text = soup.get_text(separator=" ", strip=True)

    # Basic meta
    result["page_title"] = _safe_text(soup.find("title"))
    meta_desc = soup.find("meta", attrs={"name": "description"})
    result["meta_description"] = _safe_attr(meta_desc, "content")

    # Product name from title
    title = result["page_title"]
    for suffix in (" JV", " - JV", " | JV", " Affiliate", " Joint Venture"):
        if suffix.lower() in title.lower():
            result["product_name"] = title.split(suffix)[0].strip()
            break
    if not result["product_name"]:
        h1 = soup.find("h1")
        result["product_name"] = _safe_text(h1) if h1 else title

    # Extract all components
    result["commission"] = extract_commission_details(soup, page_text)
    result["prizes"] = extract_prize_details(soup, page_text)
    result["swipes"] = extract_swipes(soup)
    result["sales_page_url"] = extract_sales_page_url(soup, page_text, url)
    result["demo_urls"] = extract_demo_urls(soup, page_text)
    result["features"] = extract_product_features(soup, page_text)
    result["vendor_bonuses"] = extract_vendor_bonuses(soup, page_text)
    result["pricing_tiers"] = extract_pricing_tiers(soup, page_text)
    result["all_urls"] = _extract_urls(soup, url)
    result["contact_emails"] = _extract_emails_from_text(page_text)

    result["success"] = True
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Analyze a JV page for affiliate data")
    parser.add_argument("--url", required=True, help="JV page URL to analyze")
    parser.add_argument("--output", default="", help="Output file path (default: stdout)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    result = analyze_jv_page(args.url)

    indent = 2 if args.pretty else None
    output = json.dumps(result, indent=indent, default=str)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Analysis saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
