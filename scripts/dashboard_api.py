#!/usr/bin/env python3
"""
Dashboard API Client — Affiliate Promo Machine
Interacts with the dashboard backend for CRUD operations on promotions,
settings management, and analytics.

Usage:
    python3 dashboard_api.py --action list
    python3 dashboard_api.py --action add --data promotion.json
    python3 dashboard_api.py --action get --id "deployment-id"
    python3 dashboard_api.py --action update --id "deployment-id" --data update.json
    python3 dashboard_api.py --action delete --id "deployment-id"
    python3 dashboard_api.py --action settings
    python3 dashboard_api.py --action update-settings --data settings.json
    python3 dashboard_api.py --action stats

Supports both local file-based storage and remote dashboard API.
"""

import argparse
import json
import os
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "dashboard", "data")
PROMOTIONS_FILE = os.path.join(DATA_DIR, "promotions.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "auto_promote_premium": True,
    "default_bonuses": [
        {
            "bonus_title": "Quick Start Guide",
            "bonus_description": "Step-by-step guide to get maximum results from your purchase.",
            "bonus_value": "97",
        }
    ],
    "preferred_templates": ["review", "comparison", "urgency", "authority"],
    "vercel_project_prefix": "promo",
    "notification_email": "",
    "social_platforms": ["twitter", "facebook", "linkedin", "instagram", "tiktok"],
    "email_platform": "",
    "auto_deploy": True,
    "ftc_disclosure": True,
    "max_daily_promotions": 5,
    "updated_at": datetime.now().isoformat(),
}


# ---------------------------------------------------------------------------
# Local Storage Layer
# ---------------------------------------------------------------------------
class LocalStorage:
    """File-based JSON storage for promotions and settings."""

    def __init__(self, data_dir=DATA_DIR):
        self.data_dir = data_dir
        self.promotions_file = os.path.join(data_dir, "promotions.json")
        self.settings_file = os.path.join(data_dir, "settings.json")
        os.makedirs(data_dir, exist_ok=True)

    def _load_json(self, filepath, default=None):
        if default is None:
            default = []
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return default
        return default

    def _save_json(self, filepath, data):
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

    # -- Promotions --

    def list_promotions(self, status=None, limit=50):
        """List all promotions, optionally filtered by status."""
        promos = self._load_json(self.promotions_file, [])
        if status:
            promos = [p for p in promos if p.get("status") == status]
        return promos[:limit]

    def get_promotion(self, promo_id):
        """Get a single promotion by ID."""
        promos = self._load_json(self.promotions_file, [])
        for p in promos:
            if p.get("id") == promo_id:
                return p
        return None

    def add_promotion(self, data):
        """Add a new promotion."""
        promos = self._load_json(self.promotions_file, [])
        # Ensure required fields
        record = {
            "id": data.get("id", f"promo-{int(datetime.now().timestamp())}"),
            "product_name": data.get("product_name", "Unknown"),
            "vendor_name": data.get("vendor_name", "Unknown"),
            "affiliate_link": data.get("affiliate_link", ""),
            "bonus_page_url": data.get("bonus_page_url", ""),
            "alias_urls": data.get("alias_urls", []),
            "project_name": data.get("project_name", ""),
            "status": data.get("status", "active"),
            "launch_date": data.get("launch_date", ""),
            "price": data.get("price", ""),
            "niche": data.get("niche", ""),
            "template_used": data.get("template_used", ""),
            "deployed_at": data.get("deployed_at", datetime.now().isoformat()),
            "clicks": data.get("clicks", 0),
            "conversions": data.get("conversions", 0),
            "earnings": data.get("earnings", 0),
            "email_swipes": data.get("email_swipes", []),
            "social_posts": data.get("social_posts", []),
            "ad_copy": data.get("ad_copy", []),
            "video_script": data.get("video_script", ""),
            "notes": data.get("notes", ""),
        }
        promos.append(record)
        self._save_json(self.promotions_file, promos)
        return record

    def update_promotion(self, promo_id, updates):
        """Update an existing promotion."""
        promos = self._load_json(self.promotions_file, [])
        for i, p in enumerate(promos):
            if p.get("id") == promo_id:
                promos[i].update(updates)
                promos[i]["updated_at"] = datetime.now().isoformat()
                self._save_json(self.promotions_file, promos)
                return promos[i]
        return None

    def delete_promotion(self, promo_id):
        """Delete a promotion by ID."""
        promos = self._load_json(self.promotions_file, [])
        original_count = len(promos)
        promos = [p for p in promos if p.get("id") != promo_id]
        if len(promos) < original_count:
            self._save_json(self.promotions_file, promos)
            return True
        return False

    def toggle_promotion(self, promo_id):
        """Toggle a promotion's status between active and paused."""
        promos = self._load_json(self.promotions_file, [])
        for i, p in enumerate(promos):
            if p.get("id") == promo_id:
                current = p.get("status", "active")
                new_status = "paused" if current == "active" else "active"
                promos[i]["status"] = new_status
                promos[i]["updated_at"] = datetime.now().isoformat()
                self._save_json(self.promotions_file, promos)
                return promos[i]
        return None

    # -- Settings --

    def get_settings(self):
        """Get current settings."""
        settings = self._load_json(self.settings_file, None)
        if settings is None:
            settings = DEFAULT_SETTINGS.copy()
            self._save_json(self.settings_file, settings)
        return settings

    def update_settings(self, updates):
        """Update settings."""
        settings = self.get_settings()
        settings.update(updates)
        settings["updated_at"] = datetime.now().isoformat()
        self._save_json(self.settings_file, settings)
        return settings

    # -- Analytics --

    def get_stats(self):
        """Get aggregate statistics."""
        promos = self._load_json(self.promotions_file, [])
        active = [p for p in promos if p.get("status") == "active"]
        total_clicks = sum(p.get("clicks", 0) for p in promos)
        total_conversions = sum(p.get("conversions", 0) for p in promos)
        total_earnings = sum(p.get("earnings", 0) for p in promos)

        return {
            "total_promotions": len(promos),
            "active_promotions": len(active),
            "paused_promotions": len(promos) - len(active),
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "total_earnings": total_earnings,
            "conversion_rate": (
                f"{(total_conversions / total_clicks * 100):.1f}%"
                if total_clicks > 0
                else "0%"
            ),
            "top_performers": sorted(
                promos, key=lambda x: x.get("clicks", 0), reverse=True
            )[:5],
            "recent_deployments": sorted(
                promos, key=lambda x: x.get("deployed_at", ""), reverse=True
            )[:5],
        }


# ---------------------------------------------------------------------------
# Remote API Client (for deployed dashboard)
# ---------------------------------------------------------------------------
class RemoteAPI:
    """Client for the deployed dashboard API."""

    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def _request(self, method, path, data=None):
        import requests
        url = f"{self.base_url}{path}"
        try:
            if method == "GET":
                resp = requests.get(url, timeout=15)
            elif method == "POST":
                resp = requests.post(url, json=data, timeout=15)
            elif method == "PUT":
                resp = requests.put(url, json=data, timeout=15)
            elif method == "DELETE":
                resp = requests.delete(url, timeout=15)
            else:
                return {"error": f"Unknown method: {method}"}
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def list_promotions(self):
        return self._request("GET", "/api/promotions")

    def get_promotion(self, promo_id):
        return self._request("GET", f"/api/promotions?id={promo_id}")

    def add_promotion(self, data):
        return self._request("POST", "/api/promotions", data)

    def update_promotion(self, promo_id, data):
        return self._request("PUT", f"/api/promotions?id={promo_id}", data)

    def delete_promotion(self, promo_id):
        return self._request("DELETE", f"/api/promotions?id={promo_id}")

    def get_settings(self):
        return self._request("GET", "/api/settings")

    def update_settings(self, data):
        return self._request("PUT", "/api/settings", data)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Dashboard API client")
    parser.add_argument(
        "--action",
        required=True,
        choices=[
            "list", "get", "add", "update", "delete", "toggle",
            "settings", "update-settings", "stats",
        ],
        help="Action to perform",
    )
    parser.add_argument("--id", default="", help="Promotion ID (for get/update/delete/toggle)")
    parser.add_argument("--data", default="", help="JSON file with data (for add/update/update-settings)")
    parser.add_argument("--status", default="", help="Filter by status (for list)")
    parser.add_argument("--remote", default="", help="Remote dashboard URL (uses local storage if empty)")
    parser.add_argument("--output", default="", help="Output file path")
    args = parser.parse_args()

    # Initialize storage
    if args.remote:
        storage = RemoteAPI(args.remote)
    else:
        storage = LocalStorage()

    # Load data file if provided
    input_data = {}
    if args.data:
        with open(args.data, "r") as f:
            input_data = json.load(f)

    # Dispatch
    result = None
    if args.action == "list":
        result = storage.list_promotions(status=args.status if args.status else None)
    elif args.action == "get":
        if not args.id:
            result = {"error": "--id required for get action"}
        else:
            result = storage.get_promotion(args.id)
    elif args.action == "add":
        if not input_data:
            result = {"error": "--data required for add action"}
        else:
            result = storage.add_promotion(input_data)
    elif args.action == "update":
        if not args.id or not input_data:
            result = {"error": "--id and --data required for update action"}
        else:
            result = storage.update_promotion(args.id, input_data)
    elif args.action == "delete":
        if not args.id:
            result = {"error": "--id required for delete action"}
        else:
            result = storage.delete_promotion(args.id)
    elif args.action == "toggle":
        if not args.id:
            result = {"error": "--id required for toggle action"}
        else:
            result = storage.toggle_promotion(args.id)
    elif args.action == "settings":
        result = storage.get_settings()
    elif args.action == "update-settings":
        if not input_data:
            result = {"error": "--data required for update-settings action"}
        else:
            result = storage.update_settings(input_data)
    elif args.action == "stats":
        result = storage.get_stats()

    # Output
    output = json.dumps(result, indent=2, default=str)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Result saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
