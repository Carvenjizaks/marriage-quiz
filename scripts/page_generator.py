#!/usr/bin/env python3
"""
Page Generator — Affiliate Promo Machine
Generates high-converting bonus/review pages by filling in HTML templates
with product data. Supports all 4 template styles.

Usage:
    python3 page_generator.py --data product.json --template review
    python3 page_generator.py --data product.json --template random --output output.html

Input: JSON file with product data (see schema below).
Output: Complete standalone HTML file.
"""

import argparse
import json
import os
import random
import re
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "..", "templates")

TEMPLATE_MAP = {
    "review": "review-template.html",
    "comparison": "comparison-template.html",
    "urgency": "urgency-template.html",
    "authority": "authority-template.html",
}

# Default product data schema (used as fallback for missing fields)
DEFAULT_DATA = {
    "product_name": "Product Name",
    "product_tagline": "The ultimate solution for your needs.",
    "product_overview": "A comprehensive overview of the product.",
    "product_description": "Detailed description of what the product does.",
    "vendor_name": "Vendor Name",
    "launch_date": datetime.now().strftime("%B %d, %Y"),
    "price": "$27",
    "future_price": "$97",
    "savings": "$70",
    "niche": "Software",
    "affiliate_link": "#",
    "rating": "4.8",
    "overall_score": "9.2",
    "overall_score_pct": "92",
    "verdict_label": "Highly Recommended",
    "verdict": "This product delivers exceptional value for its price point.",
    "final_verdict": "After thorough analysis, this product earns a strong recommendation.",
    "executive_summary": "A comprehensive analysis of this product reveals strong value.",
    "key_takeaway": "This is one of the best launches in this niche this quarter.",
    "recommendation_text": "Based on my analysis, I recommend this product.",
    "value_assessment": "Excellent value at the launch price point.",
    "guarantee_days": "30",
    "guarantee_text": "If you are not satisfied, you can request a full refund within 30 days.",
    "problem_statement": "Many marketers struggle with this exact challenge.",
    "product_slug": "product-name",
    "copies_sold": "347",
    "copies_remaining": "153",
    "stock_percentage": "69",
    "countdown_end_date": "",
    "countdown_hours": "24",
    "current_year": str(datetime.now().year),
    "total_bonus_value": "997",
    "competitor_1": "Alternative A",
    "competitor_2": "Alternative B",
    "comp1_price": "$47/mo",
    "comp2_price": "$97/mo",
    "features": [],
    "pros": [],
    "cons": [],
    "bonuses": [],
    "faqs": [],
    "testimonials": [],
    "pricing_tiers": [],
    "comparison_rows": [],
    "reasons": [],
    "audience_segments": [],
    "score_categories": [],
}


# ---------------------------------------------------------------------------
# Template Engine
# ---------------------------------------------------------------------------
def render_simple_vars(html, data):
    """Replace {{variable}} placeholders with data values."""
    def replacer(match):
        key = match.group(1).strip()
        value = data.get(key, match.group(0))  # Keep original if not found
        if isinstance(value, (dict, list)):
            return match.group(0)  # Don't replace complex types here
        return str(value)

    return re.sub(r"\{\{(\w+)\}\}", replacer, html)


def render_loops(html, data):
    """
    Handle simple Mustache-style loops:
    {{#items}} ... {{/items}}
    Supports nested {{variable}} inside loops.
    """
    loop_pattern = re.compile(
        r"\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}",
        re.DOTALL
    )

    def loop_replacer(match):
        key = match.group(1)
        template_block = match.group(2)
        items = data.get(key, [])

        if not isinstance(items, list):
            return ""

        rendered_blocks = []
        for item in items:
            block = template_block
            if isinstance(item, dict):
                for k, v in item.items():
                    block = block.replace("{{" + k + "}}", str(v))
            elif isinstance(item, str):
                block = block.replace("{{" + key + "}}", item)
            rendered_blocks.append(block)

        return "".join(rendered_blocks)

    # Apply loop rendering (may need multiple passes for nested loops)
    for _ in range(3):
        new_html = loop_pattern.sub(loop_replacer, html)
        if new_html == html:
            break
        html = new_html

    return html


def render_template(template_html, data):
    """Full template rendering: loops first, then simple variables."""
    html = render_loops(template_html, data)
    html = render_simple_vars(html, data)
    return html


# ---------------------------------------------------------------------------
# Data Preparation
# ---------------------------------------------------------------------------
def prepare_data(raw_data):
    """Merge raw data with defaults and ensure all required fields exist."""
    data = {**DEFAULT_DATA, **raw_data}

    # Auto-generate product slug if not provided
    if data.get("product_slug") == DEFAULT_DATA["product_slug"] and data["product_name"] != DEFAULT_DATA["product_name"]:
        data["product_slug"] = re.sub(r"[^a-z0-9]+", "-", data["product_name"].lower()).strip("-")

    # Ensure current year
    data["current_year"] = str(datetime.now().year)

    # Auto-number bonuses if not numbered
    for i, bonus in enumerate(data.get("bonuses", []), 1):
        if isinstance(bonus, dict) and "bonus_number" not in bonus:
            bonus["bonus_number"] = str(i)

    # Auto-number features
    for i, feature in enumerate(data.get("features", []), 1):
        if isinstance(feature, dict) and "feature_number" not in feature:
            feature["feature_number"] = str(i)

    # Auto-number reasons
    for i, reason in enumerate(data.get("reasons", []), 1):
        if isinstance(reason, dict) and "reason_number" not in reason:
            reason["reason_number"] = str(i)

    # Calculate total bonus value if not set
    if data.get("total_bonus_value") == DEFAULT_DATA["total_bonus_value"]:
        total = 0
        for bonus in data.get("bonuses", []):
            if isinstance(bonus, dict):
                try:
                    total += float(str(bonus.get("bonus_value", "0")).replace(",", ""))
                except (ValueError, TypeError):
                    pass
        if total > 0:
            data["total_bonus_value"] = f"{total:,.0f}"

    return data


def generate_sample_data():
    """Generate sample product data for testing."""
    return {
        "product_name": "AI Content Suite Pro",
        "product_tagline": "Create months of content in minutes with AI-powered automation.",
        "product_overview": "AI Content Suite Pro is a revolutionary content creation platform that leverages advanced AI to generate blog posts, social media content, email sequences, and video scripts in minutes.",
        "product_description": "Built for marketers, agencies, and content creators who need to produce high-quality content at scale without sacrificing quality or spending hours writing.",
        "vendor_name": "TechVentures Inc.",
        "launch_date": datetime.now().strftime("%B %d, %Y"),
        "price": "$37",
        "future_price": "$97/mo",
        "savings": "$60+",
        "niche": "AI / Content Marketing",
        "affiliate_link": "https://jvz.com/c/your-id/product-id",
        "rating": "4.7",
        "overall_score": "9.0",
        "overall_score_pct": "90",
        "verdict_label": "Highly Recommended",
        "verdict": "AI Content Suite Pro delivers exceptional value at its launch price. The AI quality is impressive, the templates are well-designed, and the time savings are real.",
        "final_verdict": "After extensive testing, AI Content Suite Pro earns a strong recommendation for anyone serious about content marketing.",
        "executive_summary": "AI Content Suite Pro represents a significant leap forward in AI-assisted content creation. It combines GPT-4 level quality with an intuitive interface and practical templates.",
        "key_takeaway": "This is the most complete AI content solution I have reviewed this quarter — and the launch price makes it a no-brainer.",
        "recommendation_text": "Based on thorough testing, I recommend AI Content Suite Pro for marketers and agencies looking to scale content production.",
        "value_assessment": "At $37 one-time vs. competitors charging $97/month, this is exceptional value.",
        "problem_statement": "Creating consistent, high-quality content across multiple platforms is time-consuming and expensive. Most marketers either burn out or produce mediocre content.",
        "guarantee_days": "30",
        "guarantee_text": "Try AI Content Suite Pro risk-free for 30 days. If it does not meet your expectations, contact support for a full refund.",
        "product_slug": "ai-content-suite-pro",
        "copies_sold": "412",
        "copies_remaining": "88",
        "stock_percentage": "82",
        "total_bonus_value": "2,485",
        "competitor_1": "Jasper AI",
        "competitor_2": "Copy.ai",
        "comp1_price": "$49/mo",
        "comp2_price": "$36/mo",
        "features": [
            {"feature_title": "AI Blog Writer", "feature_description": "Generate full blog posts with SEO optimization in under 2 minutes.", "feature_analysis": "The blog writer produces remarkably coherent long-form content.", "feature_impact": "High"},
            {"feature_title": "Social Media Suite", "feature_description": "Create platform-specific posts for Twitter, Facebook, LinkedIn, and Instagram.", "feature_analysis": "Each platform gets tailored content with appropriate tone and length.", "feature_impact": "High"},
            {"feature_title": "Email Sequence Builder", "feature_description": "Build complete email marketing sequences with AI-generated copy.", "feature_analysis": "The email sequences follow proven frameworks like AIDA and PAS.", "feature_impact": "Medium-High"},
            {"feature_title": "Video Script Generator", "feature_description": "Create YouTube and TikTok scripts with hooks, body, and CTAs.", "feature_analysis": "Scripts include timing markers and visual cues for easy recording.", "feature_impact": "Medium"},
        ],
        "pros": [
            {"pro": "Exceptional AI writing quality", "pro_title": "AI Quality", "pro_detail": "Output rivals human-written content in most categories."},
            {"pro": "One-time pricing at launch", "pro_title": "Pricing Model", "pro_detail": "No monthly fees during launch — massive savings vs. competitors."},
            {"pro": "50+ content templates included", "pro_title": "Template Library", "pro_detail": "Covers every major content type and marketing framework."},
            {"pro": "Commercial license included", "pro_title": "Commercial Rights", "pro_detail": "Use for client work and agency projects."},
        ],
        "cons": [
            {"con": "Requires internet connection", "con_title": "Online Only", "con_detail": "No offline mode available — requires stable internet."},
            {"con": "Learning curve for advanced features", "con_title": "Complexity", "con_detail": "Some advanced features take time to master fully."},
        ],
        "bonuses": [
            {"bonus_title": "Content Calendar Masterclass", "bonus_description": "A complete video course on planning 90 days of content in one sitting.", "bonus_value": "497"},
            {"bonus_title": "500 ChatGPT Prompts Pack", "bonus_description": "Curated prompts for marketing, sales, and content creation.", "bonus_value": "297"},
            {"bonus_title": "SEO Checklist & Toolkit", "bonus_description": "Step-by-step SEO optimization checklist with free tool recommendations.", "bonus_value": "197"},
            {"bonus_title": "Private Community Access", "bonus_description": "Join our exclusive community of content marketers for networking and support.", "bonus_value": "997"},
            {"bonus_title": "1-on-1 Setup Call (30 min)", "bonus_description": "Personal onboarding call to set up your account and strategy.", "bonus_value": "497"},
        ],
        "faqs": [
            {"faq_question": "How do I claim my bonuses?", "faq_answer": "After purchasing through my link, forward your receipt to bonuses@example.com and I will send you access within 24 hours."},
            {"faq_question": "Is there a money-back guarantee?", "faq_answer": "Yes, the vendor offers a full 30-day money-back guarantee. No questions asked."},
            {"faq_question": "Do I need any technical skills?", "faq_answer": "No. The interface is designed for non-technical users. If you can type, you can use this tool."},
            {"faq_question": "Will the price increase after launch?", "faq_answer": "Yes. The vendor has confirmed the price will move to a monthly subscription model after the launch period ends."},
        ],
        "testimonials": [
            {"testimonial_text": "This tool cut my content creation time by 80%. I now publish daily instead of weekly.", "testimonial_author": "Sarah M., Content Marketer"},
            {"testimonial_text": "The email sequences it generates are better than what my copywriter was producing.", "testimonial_author": "David R., Agency Owner"},
        ],
        "pricing_tiers": [
            {"tier_name": "Front-End", "tier_price": "$37", "tier_details": "Core AI content suite with 50+ templates", "tier_value_color": "green", "tier_value_label": "Best Value", "tier_notes": "Recommended starting point"},
            {"tier_name": "OTO 1 — Pro", "tier_price": "$67", "tier_details": "Unlimited usage + priority AI processing", "tier_value_color": "green", "tier_value_label": "Good Value", "tier_notes": "Worth it for heavy users"},
            {"tier_name": "OTO 2 — Agency", "tier_price": "$97", "tier_details": "Multi-user accounts + client management", "tier_value_color": "yellow", "tier_value_label": "Situational", "tier_notes": "Only if you run an agency"},
            {"tier_name": "OTO 3 — Reseller", "tier_price": "$197", "tier_details": "Resell the product and keep 100% profit", "tier_value_color": "yellow", "tier_value_label": "Situational", "tier_notes": "For product resellers only"},
        ],
        "comparison_rows": [
            {"feature_name": "AI Writing Quality", "product_value": "★★★★★", "product_class": "check-icon font-bold", "comp1_value": "★★★★☆", "comp1_class": "", "comp2_value": "★★★☆☆", "comp2_class": ""},
            {"feature_name": "One-Time Pricing", "product_value": "✓", "product_class": "check-icon text-xl font-bold", "comp1_value": "✗", "comp1_class": "cross-icon text-xl", "comp2_value": "✗", "comp2_class": "cross-icon text-xl"},
            {"feature_name": "50+ Templates", "product_value": "✓", "product_class": "check-icon text-xl font-bold", "comp1_value": "✓", "comp1_class": "check-icon text-xl", "comp2_value": "Limited", "comp2_class": "text-gray-400"},
            {"feature_name": "Commercial License", "product_value": "✓", "product_class": "check-icon text-xl font-bold", "comp1_value": "Extra $$$", "comp1_class": "text-gray-400", "comp2_value": "✗", "comp2_class": "cross-icon text-xl"},
            {"feature_name": "Video Scripts", "product_value": "✓", "product_class": "check-icon text-xl font-bold", "comp1_value": "✗", "comp1_class": "cross-icon text-xl", "comp2_value": "✗", "comp2_class": "cross-icon text-xl"},
        ],
        "reasons": [
            {"reason_title": "Unbeatable Launch Price", "reason_description": "Get lifetime access for a one-time fee of $37 — competitors charge $50-100 per month."},
            {"reason_title": "Superior AI Quality", "reason_description": "Powered by the latest AI models with fine-tuning specifically for marketing content."},
            {"reason_title": "All-in-One Platform", "reason_description": "Blog posts, social media, emails, and video scripts — all from one dashboard."},
            {"reason_title": "Commercial License Included", "reason_description": "Use for client work immediately without paying extra for commercial rights."},
            {"reason_title": "Active Development", "reason_description": "The vendor ships weekly updates and actively responds to feature requests."},
        ],
        "audience_segments": [
            {"segment_icon": "📝", "segment_title": "Content Creators", "segment_description": "Bloggers, YouTubers, and social media managers who need consistent content."},
            {"segment_icon": "📈", "segment_title": "Digital Marketers", "segment_description": "Marketers running campaigns across email, social, and paid channels."},
            {"segment_icon": "🏢", "segment_title": "Agencies", "segment_description": "Marketing agencies managing content for multiple clients simultaneously."},
        ],
        "score_categories": [
            {"category_name": "AI Writing Quality", "category_score": "9.5", "category_score_pct": "95", "category_notes": "Among the best AI writing I have tested."},
            {"category_name": "Ease of Use", "category_score": "8.5", "category_score_pct": "85", "category_notes": "Clean interface with minor learning curve."},
            {"category_name": "Template Variety", "category_score": "9.0", "category_score_pct": "90", "category_notes": "50+ templates covering all major content types."},
            {"category_name": "Value for Money", "category_score": "9.5", "category_score_pct": "95", "category_notes": "One-time price is unbeatable vs. monthly competitors."},
            {"category_name": "Support & Updates", "category_score": "8.0", "category_score_pct": "80", "category_notes": "Responsive support, weekly updates."},
            {"category_name": "Output Customization", "category_score": "8.5", "category_score_pct": "85", "category_notes": "Good control over tone, length, and style."},
        ],
    }


# ---------------------------------------------------------------------------
# Main Generator
# ---------------------------------------------------------------------------
def generate_page(data_path, template_name="random", output_path=None):
    """Generate a bonus page from data and template."""

    # Load product data
    if data_path == "sample":
        raw_data = generate_sample_data()
    else:
        with open(data_path, "r") as f:
            raw_data = json.load(f)

    data = prepare_data(raw_data)

    # Select template
    if template_name == "random":
        template_name = random.choice(list(TEMPLATE_MAP.keys()))
        print(f"Selected template: {template_name}", file=sys.stderr)

    if template_name not in TEMPLATE_MAP:
        print(json.dumps({"error": f"Unknown template: {template_name}. Options: {list(TEMPLATE_MAP.keys())}"}))
        sys.exit(1)

    template_file = os.path.join(TEMPLATES_DIR, TEMPLATE_MAP[template_name])
    if not os.path.exists(template_file):
        print(json.dumps({"error": f"Template file not found: {template_file}"}))
        sys.exit(1)

    with open(template_file, "r") as f:
        template_html = f.read()

    # Render
    rendered_html = render_template(template_html, data)

    # Output
    if output_path:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, "w") as f:
            f.write(rendered_html)
        print(json.dumps({
            "success": True,
            "template": template_name,
            "output": output_path,
            "product": data["product_name"],
        }))
    else:
        print(rendered_html)

    return rendered_html


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Generate affiliate bonus/review pages")
    parser.add_argument(
        "--data",
        required=True,
        help="Path to product data JSON file, or 'sample' for demo data",
    )
    parser.add_argument(
        "--template",
        choices=list(TEMPLATE_MAP.keys()) + ["random"],
        default="random",
        help="Template style to use (default: random)",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Output HTML file path (default: stdout)",
    )
    parser.add_argument(
        "--sample-data",
        action="store_true",
        help="Print sample product data JSON and exit",
    )
    args = parser.parse_args()

    if args.sample_data:
        print(json.dumps(generate_sample_data(), indent=2))
        return

    generate_page(args.data, args.template, args.output if args.output else None)


if __name__ == "__main__":
    main()
