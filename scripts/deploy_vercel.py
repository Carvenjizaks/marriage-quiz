#!/usr/bin/env python3
"""
Vercel Deployer — Affiliate Promo Machine
Deploys generated bonus pages to Vercel using the Vercel API.
Handles project creation, file upload, and deployment.

Usage:
    python3 deploy_vercel.py --html bonus-page.html --name "ai-content-suite-review"
    python3 deploy_vercel.py --dir ./deploy-folder --name "my-promo"
    python3 deploy_vercel.py --html page.html --name "promo" --team "my-team"

Requires: VERCEL_TOKEN environment variable.
"""

import argparse
import base64
import hashlib
import json
import os
import sys
import time
from datetime import datetime

try:
    import requests
except ImportError:
    print(json.dumps({
        "error": "Missing dependency. Install with: pip3 install requests",
        "success": False
    }))
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VERCEL_API = "https://api.vercel.com"
DASHBOARD_DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "dashboard", "data"
)


# ---------------------------------------------------------------------------
# Vercel API Client
# ---------------------------------------------------------------------------
class VercelDeployer:
    """Client for Vercel deployment API."""

    def __init__(self, token=None, team_id=None):
        self.token = token or os.environ.get("VERCEL_TOKEN", "")
        self.team_id = team_id
        if not self.token:
            raise ValueError(
                "VERCEL_TOKEN not set. Get one at: "
                "https://vercel.com/account/tokens"
            )
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _params(self):
        """Return team query params if applicable."""
        return {"teamId": self.team_id} if self.team_id else {}

    def check_auth(self):
        """Verify the Vercel token is valid."""
        resp = requests.get(
            f"{VERCEL_API}/v2/user",
            headers=self.headers,
            params=self._params(),
            timeout=15,
        )
        if resp.status_code == 200:
            user = resp.json().get("user", {})
            return {
                "success": True,
                "username": user.get("username", ""),
                "email": user.get("email", ""),
            }
        return {"success": False, "error": resp.text}

    def _file_to_upload(self, filepath, deploy_path):
        """Prepare a file for Vercel deployment."""
        with open(filepath, "rb") as f:
            content = f.read()
        sha = hashlib.sha1(content).hexdigest()
        return {
            "file": deploy_path,
            "sha": sha,
            "size": len(content),
            "data": base64.b64encode(content).decode("utf-8"),
        }

    def deploy_files(self, files, project_name, framework=None):
        """
        Deploy files to Vercel.

        Args:
            files: List of dicts with 'file' (deploy path) and 'data' (base64 content)
            project_name: Name for the Vercel project
            framework: Optional framework hint (e.g., 'static')

        Returns:
            Deployment result dict
        """
        # Sanitize project name
        safe_name = "".join(
            c if c.isalnum() or c in "-_" else "-"
            for c in project_name.lower()
        ).strip("-")[:50]

        payload = {
            "name": safe_name,
            "files": files,
            "projectSettings": {
                "framework": framework or None,
                "buildCommand": "",
                "outputDirectory": "",
                "installCommand": "",
            },
            "target": "production",
        }

        resp = requests.post(
            f"{VERCEL_API}/v13/deployments",
            headers=self.headers,
            params=self._params(),
            json=payload,
            timeout=60,
        )

        if resp.status_code in (200, 201):
            data = resp.json()
            return {
                "success": True,
                "deployment_id": data.get("id", ""),
                "url": f"https://{data.get('url', '')}",
                "project_name": safe_name,
                "ready_state": data.get("readyState", ""),
                "created_at": data.get("createdAt", ""),
                "alias": [f"https://{a}" for a in data.get("alias", [])],
            }
        else:
            return {
                "success": False,
                "status_code": resp.status_code,
                "error": resp.text,
            }

    def deploy_html(self, html_path, project_name):
        """Deploy a single HTML file as index.html."""
        file_entry = self._file_to_upload(html_path, "index.html")
        return self.deploy_files([file_entry], project_name)

    def deploy_directory(self, dir_path, project_name):
        """Deploy an entire directory to Vercel."""
        files = []
        for root, dirs, filenames in os.walk(dir_path):
            # Skip hidden dirs and node_modules
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
            for filename in filenames:
                if filename.startswith("."):
                    continue
                filepath = os.path.join(root, filename)
                deploy_path = os.path.relpath(filepath, dir_path)
                files.append(self._file_to_upload(filepath, deploy_path))

        if not files:
            return {"success": False, "error": "No files found in directory"}

        return self.deploy_files(files, project_name)

    def get_deployment_status(self, deployment_id):
        """Check the status of a deployment."""
        resp = requests.get(
            f"{VERCEL_API}/v13/deployments/{deployment_id}",
            headers=self.headers,
            params=self._params(),
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "success": True,
                "state": data.get("readyState", ""),
                "url": f"https://{data.get('url', '')}",
                "alias": [f"https://{a}" for a in data.get("alias", [])],
            }
        return {"success": False, "error": resp.text}

    def wait_for_ready(self, deployment_id, timeout=120, interval=5):
        """Poll deployment status until ready or timeout."""
        start = time.time()
        while time.time() - start < timeout:
            status = self.get_deployment_status(deployment_id)
            if not status["success"]:
                return status
            state = status.get("state", "")
            if state == "READY":
                return status
            if state in ("ERROR", "CANCELED"):
                return {
                    "success": False,
                    "error": f"Deployment ended with state: {state}",
                }
            time.sleep(interval)
        return {"success": False, "error": "Deployment timed out"}

    def list_projects(self, limit=20):
        """List recent Vercel projects."""
        resp = requests.get(
            f"{VERCEL_API}/v9/projects",
            headers=self.headers,
            params={**self._params(), "limit": limit},
            timeout=15,
        )
        if resp.status_code == 200:
            projects = resp.json().get("projects", [])
            return {
                "success": True,
                "projects": [
                    {
                        "id": p.get("id"),
                        "name": p.get("name"),
                        "url": f"https://{p.get('name')}.vercel.app",
                        "updated_at": p.get("updatedAt"),
                    }
                    for p in projects
                ],
            }
        return {"success": False, "error": resp.text}

    def delete_project(self, project_name):
        """Delete a Vercel project."""
        resp = requests.delete(
            f"{VERCEL_API}/v9/projects/{project_name}",
            headers=self.headers,
            params=self._params(),
            timeout=15,
        )
        return {"success": resp.status_code in (200, 204), "status_code": resp.status_code}


# ---------------------------------------------------------------------------
# Dashboard Integration
# ---------------------------------------------------------------------------
def update_dashboard_record(deployment_result, product_data):
    """Update the dashboard data file with the new deployment."""
    os.makedirs(DASHBOARD_DATA_DIR, exist_ok=True)
    data_file = os.path.join(DASHBOARD_DATA_DIR, "promotions.json")

    # Load existing data
    promotions = []
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            try:
                promotions = json.load(f)
            except json.JSONDecodeError:
                promotions = []

    # Create promotion record
    record = {
        "id": deployment_result.get("deployment_id", f"local-{int(time.time())}"),
        "product_name": product_data.get("product_name", "Unknown"),
        "vendor_name": product_data.get("vendor_name", "Unknown"),
        "affiliate_link": product_data.get("affiliate_link", ""),
        "bonus_page_url": deployment_result.get("url", ""),
        "alias_urls": deployment_result.get("alias", []),
        "project_name": deployment_result.get("project_name", ""),
        "status": "active" if deployment_result.get("success") else "failed",
        "launch_date": product_data.get("launch_date", ""),
        "price": product_data.get("price", ""),
        "niche": product_data.get("niche", ""),
        "template_used": product_data.get("template_used", ""),
        "deployed_at": datetime.now().isoformat(),
        "clicks": 0,
        "conversions": 0,
    }

    promotions.append(record)

    with open(data_file, "w") as f:
        json.dump(promotions, f, indent=2)

    return record


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Deploy bonus pages to Vercel")
    parser.add_argument("--html", help="Path to HTML file to deploy")
    parser.add_argument("--dir", help="Path to directory to deploy")
    parser.add_argument("--name", required=True, help="Project name for Vercel")
    parser.add_argument("--team", default="", help="Vercel team ID (optional)")
    parser.add_argument("--token", default="", help="Vercel token (or use VERCEL_TOKEN env)")
    parser.add_argument("--wait", action="store_true", help="Wait for deployment to be ready")
    parser.add_argument("--data", default="", help="Product data JSON for dashboard update")
    parser.add_argument("--output", default="", help="Output file for deployment result")
    parser.add_argument("--check-auth", action="store_true", help="Check Vercel auth and exit")
    parser.add_argument("--list-projects", action="store_true", help="List Vercel projects and exit")
    parser.add_argument("--delete", default="", help="Delete a Vercel project by name")
    args = parser.parse_args()

    try:
        deployer = VercelDeployer(
            token=args.token if args.token else None,
            team_id=args.team if args.team else None,
        )
    except ValueError as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)

    # Check auth
    if args.check_auth:
        result = deployer.check_auth()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)

    # List projects
    if args.list_projects:
        result = deployer.list_projects()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)

    # Delete project
    if args.delete:
        result = deployer.delete_project(args.delete)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)

    # Deploy
    if not args.html and not args.dir:
        parser.error("Either --html or --dir is required for deployment")

    if args.html:
        if not os.path.exists(args.html):
            print(json.dumps({"success": False, "error": f"File not found: {args.html}"}))
            sys.exit(1)
        result = deployer.deploy_html(args.html, args.name)
    else:
        if not os.path.isdir(args.dir):
            print(json.dumps({"success": False, "error": f"Directory not found: {args.dir}"}))
            sys.exit(1)
        result = deployer.deploy_directory(args.dir, args.name)

    # Wait for ready
    if args.wait and result.get("success") and result.get("deployment_id"):
        print("Waiting for deployment to be ready...", file=sys.stderr)
        status = deployer.wait_for_ready(result["deployment_id"])
        result.update(status)

    # Update dashboard
    if args.data and result.get("success"):
        with open(args.data, "r") as f:
            product_data = json.load(f)
        record = update_dashboard_record(result, product_data)
        result["dashboard_record"] = record

    # Output
    output = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Deployment result saved to {args.output}", file=sys.stderr)
    else:
        print(output)

    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
