#!/usr/bin/env python3
"""
Content Generator — Affiliate Promo Machine
Generates multi-channel marketing content for affiliate promotions:
email swipes, social media posts, ad copy, and video scripts.

Usage:
    python3 content_generator.py --data product.json --type all
    python3 content_generator.py --data product.json --type emails --output emails.md
    python3 content_generator.py --data product.json --type social
    python3 content_generator.py --data product.json --type ads
    python3 content_generator.py --data product.json --type video

Output: JSON or Markdown content to stdout or file.
"""

import argparse
import json
import os
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# Content Templates
# ---------------------------------------------------------------------------

# ---- EMAIL SWIPES ----

EMAIL_CURIOSITY = """## Email Swipe #1 — Curiosity Angle

**Subject Line Options:**
1. This changes everything about {niche}...
2. I was NOT expecting this from {vendor_name}
3. The {niche} tool everyone's whispering about

---

Hey {{{{first_name}}}},

I just got early access to something that made my jaw drop.

{vendor_name} has been quietly building {product_name} behind the scenes, and it just went live today.

Without giving too much away, here's what caught my attention:

{feature_bullets}

I've been testing it for the past few days and the results speak for themselves.

But here's the thing — the launch price is only available for a limited time. After that, it moves to {future_price}.

**[Check out {product_name} here (+ my exclusive bonuses)]({affiliate_link})**

I'll share more details tomorrow, but if you're in the {niche} space, you'll want to see this now.

To your success,
{{{{your_name}}}}

P.S. I've put together an exclusive bonus package worth ${total_bonus_value} for anyone who grabs {product_name} through my link. Details on the page above.

---
"""

EMAIL_URGENCY = """## Email Swipe #2 — Urgency Angle

**Subject Line Options:**
1. [CLOSING SOON] {product_name} launch price ends tonight
2. Last chance: {product_name} at {price} (going to {future_price})
3. ⏰ Hours left to grab {product_name} + my bonuses

---

Hey {{{{first_name}}}},

Quick heads up — the launch special for {product_name} is about to end.

Right now, you can get lifetime access for just {price}.

After the launch period? It's moving to {future_price}. That's not a scare tactic — it's just how launch pricing works.

Here's what you're getting:

{feature_bullets}

Plus, when you grab it through my link, you also get:

{bonus_bullets}

**Total bonus value: ${total_bonus_value} — yours FREE.**

**[Grab {product_name} + Bonuses Before Price Increases →]({affiliate_link})**

Don't sit on this one.

Best,
{{{{your_name}}}}

P.S. {vendor_name} offers a {guarantee_days}-day money-back guarantee, so there's zero risk. But the low price? That's disappearing soon.

---
"""

EMAIL_VALUE = """## Email Swipe #3 — Value Angle

**Subject Line Options:**
1. How I'm using {product_name} to save 10+ hours/week
2. {product_name} review: Is it worth {price}? (My honest take)
3. I tested {product_name} so you don't have to — here's what happened

---

Hey {{{{first_name}}}},

I want to give you my honest breakdown of {product_name} by {vendor_name}.

**What is it?**
{product_overview}

**What I like:**
{pro_bullets}

**What could be better:**
{con_bullets}

**My verdict:**
{verdict}

**The price:**
Right now it's {price} (one-time). After launch, it goes to {future_price}. At the current price, it's a no-brainer if you're in the {niche} space.

**My exclusive bonuses (worth ${total_bonus_value}):**
{bonus_bullets}

**[Get {product_name} + All My Bonuses Here →]({affiliate_link})**

Hope this helps you make an informed decision.

Cheers,
{{{{your_name}}}}

---
"""

# ---- SOCIAL MEDIA POSTS ----

SOCIAL_TWITTER = """## Twitter/X Thread

**Tweet 1 (Hook):**
🚀 Just discovered {product_name} by {vendor_name} and I'm impressed.

If you're in the {niche} space, this is a game-changer.

Here's my quick breakdown 🧵👇

**Tweet 2 (Problem):**
The problem: {problem_short}

Most solutions either cost too much or don't deliver.

**Tweet 3 (Solution):**
{product_name} solves this with:

{feature_list_short}

And the best part? It's {price} ONE-TIME right now.

**Tweet 4 (Proof):**
I've been testing it and here's what stood out:

✅ {top_pro_1}
✅ {top_pro_2}
✅ {top_pro_3}

**Tweet 5 (CTA):**
🎁 I've put together ${total_bonus_value} in exclusive bonuses for anyone who grabs it through my link.

Check it out here: {affiliate_link}

Launch price won't last long.

---
"""

SOCIAL_FACEBOOK = """## Facebook Post

🔥 **{product_name} — My Honest Take**

I just got access to {product_name} by {vendor_name} and I wanted to share my thoughts with you.

**What it does:** {product_overview_short}

**What I love:**
{feature_bullets}

**Who it's for:** Anyone in the {niche} space who wants to {main_benefit}.

**The deal:** It's currently {price} (launch special). After launch, it goes to {future_price}.

🎁 **BONUS:** I've put together an exclusive bonus package worth ${total_bonus_value} for anyone who grabs it through my link.

👉 {affiliate_link}

Drop a comment if you have questions — happy to help!

#AffiliateMarketing #{niche_hashtag} #SoftwareLaunch #ProductReview

---
"""

SOCIAL_LINKEDIN = """## LinkedIn Post

**I just reviewed {product_name} — here's my professional assessment.**

In the {niche} space, finding tools that actually deliver on their promises is rare. {product_name} by {vendor_name} is one of those rare finds.

**Key Highlights:**
{feature_bullets}

**Value Proposition:**
At {price} (launch pricing), this represents significant value compared to alternatives like {competitor_1} ({comp1_price}) and {competitor_2} ({comp2_price}).

**My Recommendation:**
{verdict}

If you're a professional in the {niche} space, this deserves your attention.

Full review + exclusive bonuses: {affiliate_link}

*Disclosure: This post contains an affiliate link.*

---
"""

SOCIAL_INSTAGRAM = """## Instagram Caption

✨ NEW TOOL ALERT ✨

Just tested {product_name} and I'm genuinely impressed. Here's why:

{feature_list_emoji}

💰 Launch price: {price} (normally {future_price})
🎁 My exclusive bonuses: ${total_bonus_value} value

Link in bio for full review + bonuses 👆

.
.
.
#{niche_hashtag} #ProductReview #SoftwareLaunch #TechReview #{product_hashtag} #DigitalMarketing #OnlineBusiness #Entrepreneur

---
"""

SOCIAL_TIKTOK = """## TikTok Script

**Hook (0-3 sec):**
"Stop scrolling if you're in the {niche} space — this tool just launched and it's insane."

**Problem (3-8 sec):**
"So you know how {problem_short}? Yeah, that's been driving me crazy too."

**Solution (8-20 sec):**
"I just found {product_name} and it literally does:
- {feature_1}
- {feature_2}
- {feature_3}
And the crazy part? It's only {price} right now."

**Proof (20-35 sec):**
"Let me show you real quick... [SCREEN RECORDING OF PRODUCT]
See? {top_pro_1}. That alone is worth it."

**CTA (35-45 sec):**
"Link in bio for my full review plus I'm throwing in ${total_bonus_value} in bonuses if you grab it through my link. Launch price ends soon so don't sleep on this."

**Text Overlay:** "{product_name} Review | Link in Bio"
**Sound:** Trending audio or original voiceover
**Hashtags:** #{niche_hashtag} #{product_hashtag} #TechReview #SoftwareReview #ToolReview

---
"""

# ---- AD COPY ----

AD_COPY_1 = """## Facebook/Instagram Ad Copy — Variation 1 (Problem-Solution)

**Headline:** {product_name} — {main_benefit} Without the Headache

**Primary Text:**
Tired of {problem_short}?

{product_name} just launched and it's changing the game for {niche} professionals.

✅ {feature_1}
✅ {feature_2}
✅ {feature_3}

🔥 Launch special: {price} (normally {future_price})
🎁 PLUS: ${total_bonus_value} in exclusive bonuses

Click below to see my full review and claim your bonuses.

**CTA Button:** Learn More
**Link:** {affiliate_link}

---
"""

AD_COPY_2 = """## Facebook/Instagram Ad Copy — Variation 2 (Social Proof)

**Headline:** Why {niche} Pros Are Switching to {product_name}

**Primary Text:**
{copies_sold}+ people have already grabbed {product_name} since it launched.

Here's why:

→ {top_pro_1}
→ {top_pro_2}
→ {top_pro_3}

And right now, it's just {price} (one-time payment).

I've been using it myself and put together a detailed review + ${total_bonus_value} in exclusive bonuses for my audience.

Don't miss the launch pricing.

**CTA Button:** Get Offer
**Link:** {affiliate_link}

---
"""

# ---- VIDEO SCRIPT ----

VIDEO_SCRIPT = """## YouTube Review Video Script

**Title Options:**
1. {product_name} Review — Is It Worth {price}? (Honest Breakdown)
2. {product_name} by {vendor_name} — Full Demo + Exclusive Bonuses
3. I Tested {product_name} So You Don't Have To — Here's My Verdict

**Thumbnail Text:** "{product_name} — Worth It?"

---

### INTRO (0:00 - 0:45)
"Hey everyone, welcome back to the channel. Today I'm reviewing {product_name} by {vendor_name}, which just launched on {launch_date}.

I've been testing this for the past few days and I want to give you my completely honest breakdown — the good, the bad, and whether it's actually worth your {price}.

Plus, I've put together an exclusive bonus package worth over ${total_bonus_value} for anyone who grabs it through my link in the description. More on that at the end.

Let's dive in."

### WHAT IS IT? (0:45 - 2:00)
"So what exactly is {product_name}?

{product_overview}

It's positioned in the {niche} space and it's designed for {target_audience}."

### DEMO / WALKTHROUGH (2:00 - 6:00)
"Let me show you the inside. [SCREEN SHARE]

{feature_walkthrough}

As you can see, {demo_commentary}."

### WHAT I LIKE (6:00 - 8:00)
"Now let me tell you what I genuinely like about this:

{pro_bullets}

{top_pro_detail}"

### WHAT COULD BE BETTER (8:00 - 9:00)
"No product is perfect, so here's what could be improved:

{con_bullets}

These aren't dealbreakers, but worth mentioning."

### PRICING (9:00 - 10:00)
"Let's talk pricing.

The front-end is {price}, which gets you {fe_details}.

{pricing_breakdown}

Compared to alternatives like {competitor_1} at {comp1_price} and {competitor_2} at {comp2_price}, this is very competitive."

### MY BONUSES (10:00 - 11:30)
"Now here's where it gets really good. If you grab {product_name} through my link in the description, you'll also get my exclusive bonus package:

{bonus_bullets}

That's ${total_bonus_value} in total value, completely free."

### VERDICT (11:30 - 12:30)
"So, is {product_name} worth it?

{verdict}

I'm giving it a {rating} out of 5.

If you're in the {niche} space, I'd say go for it — especially at the launch price."

### OUTRO (12:30 - 13:00)
"Link is in the description below. Make sure to forward your receipt to claim your bonuses.

If you found this review helpful, hit that like button and subscribe for more honest product reviews.

See you in the next one!"

---

**Description Template:**
🔥 {product_name} + My Exclusive Bonuses: {affiliate_link}

In this video, I review {product_name} by {vendor_name} and give you my honest verdict.

🎁 My Exclusive Bonuses (${total_bonus_value} value):
{bonus_list_simple}

⏰ Timestamps:
0:00 Intro
0:45 What Is {product_name}?
2:00 Demo & Walkthrough
6:00 What I Like
8:00 What Could Be Better
9:00 Pricing Breakdown
10:00 My Exclusive Bonuses
11:30 Final Verdict

*Affiliate Disclosure: This video contains affiliate links. I may earn a commission if you purchase through my link.*

---
"""


# ---------------------------------------------------------------------------
# Content Generation
# ---------------------------------------------------------------------------
def prepare_content_vars(data):
    """Prepare template variables from product data."""
    features = data.get("features", [])
    pros = data.get("pros", [])
    cons = data.get("cons", [])
    bonuses = data.get("bonuses", [])

    # Feature bullets
    feature_bullets = "\n".join(
        f"• {f.get('feature_title', f) if isinstance(f, dict) else f}: "
        f"{f.get('feature_description', '') if isinstance(f, dict) else ''}"
        for f in features[:5]
    )

    feature_list_short = "\n".join(
        f"• {f.get('feature_title', f) if isinstance(f, dict) else f}"
        for f in features[:4]
    )

    feature_list_emoji = "\n".join(
        f"✅ {f.get('feature_title', f) if isinstance(f, dict) else f}"
        for f in features[:5]
    )

    pro_bullets = "\n".join(
        f"✅ {p.get('pro', p.get('pro_title', p)) if isinstance(p, dict) else p}"
        for p in pros[:5]
    )

    con_bullets = "\n".join(
        f"⚠️ {c.get('con', c.get('con_title', c)) if isinstance(c, dict) else c}"
        for c in cons[:3]
    )

    bonus_bullets = "\n".join(
        f"🎁 Bonus #{i+1}: {b.get('bonus_title', b) if isinstance(b, dict) else b} "
        f"(Value: ${b.get('bonus_value', '???') if isinstance(b, dict) else '???'})"
        for i, b in enumerate(bonuses[:5])
    )

    bonus_list_simple = "\n".join(
        f"- {b.get('bonus_title', b) if isinstance(b, dict) else b}"
        for b in bonuses[:5]
    )

    niche_hashtag = data.get("niche", "Software").replace(" ", "").replace("/", "")
    product_hashtag = data.get("product_name", "Product").replace(" ", "")

    return {
        "product_name": data.get("product_name", "Product"),
        "vendor_name": data.get("vendor_name", "Vendor"),
        "price": data.get("price", "$27"),
        "future_price": data.get("future_price", "$97"),
        "niche": data.get("niche", "Software"),
        "affiliate_link": data.get("affiliate_link", "#"),
        "product_overview": data.get("product_overview", ""),
        "product_overview_short": data.get("product_overview", "")[:200],
        "verdict": data.get("verdict", "Recommended."),
        "rating": data.get("rating", "4.5"),
        "total_bonus_value": data.get("total_bonus_value", "997"),
        "guarantee_days": data.get("guarantee_days", "30"),
        "launch_date": data.get("launch_date", "Today"),
        "copies_sold": data.get("copies_sold", "300+"),
        "competitor_1": data.get("competitor_1", "Alternative A"),
        "competitor_2": data.get("competitor_2", "Alternative B"),
        "comp1_price": data.get("comp1_price", "$47/mo"),
        "comp2_price": data.get("comp2_price", "$97/mo"),
        "problem_short": data.get("problem_statement", "the current tools don't cut it")[:150],
        "main_benefit": features[0].get("feature_title", "save time") if features and isinstance(features[0], dict) else "save time",
        "feature_bullets": feature_bullets,
        "feature_list_short": feature_list_short,
        "feature_list_emoji": feature_list_emoji,
        "feature_1": features[0].get("feature_title", "Feature 1") if features and isinstance(features[0], dict) else "Feature 1",
        "feature_2": features[1].get("feature_title", "Feature 2") if len(features) > 1 and isinstance(features[1], dict) else "Feature 2",
        "feature_3": features[2].get("feature_title", "Feature 3") if len(features) > 2 and isinstance(features[2], dict) else "Feature 3",
        "top_pro_1": pros[0].get("pro", pros[0].get("pro_title", "")) if pros and isinstance(pros[0], dict) else (pros[0] if pros else "Great value"),
        "top_pro_2": pros[1].get("pro", pros[1].get("pro_title", "")) if len(pros) > 1 and isinstance(pros[1], dict) else "Easy to use",
        "top_pro_3": pros[2].get("pro", pros[2].get("pro_title", "")) if len(pros) > 2 and isinstance(pros[2], dict) else "Excellent support",
        "top_pro_detail": pros[0].get("pro_detail", "") if pros and isinstance(pros[0], dict) else "",
        "pro_bullets": pro_bullets,
        "con_bullets": con_bullets,
        "bonus_bullets": bonus_bullets,
        "bonus_list_simple": bonus_list_simple,
        "niche_hashtag": niche_hashtag,
        "product_hashtag": product_hashtag,
        "target_audience": data.get("audience_segments", [{}])[0].get("segment_title", "marketers") if data.get("audience_segments") else "marketers",
        "fe_details": data.get("pricing_tiers", [{}])[0].get("tier_details", "the core product") if data.get("pricing_tiers") else "the core product",
        "pricing_breakdown": "\n".join(
            f"- {t.get('tier_name', '')}: {t.get('tier_price', '')} — {t.get('tier_details', '')}"
            for t in data.get("pricing_tiers", [])[:4]
        ),
        "feature_walkthrough": "\n".join(
            f"- {f.get('feature_title', '')}: {f.get('feature_description', '')}"
            for f in features[:4]
        ) if features else "Show the main dashboard and key features.",
        "demo_commentary": "the interface is clean and the features work as advertised",
    }


def generate_content(data, content_type="all"):
    """Generate marketing content from product data."""
    v = prepare_content_vars(data)
    content = {}

    templates = {
        "emails": [
            ("Curiosity Angle", EMAIL_CURIOSITY),
            ("Urgency Angle", EMAIL_URGENCY),
            ("Value Angle", EMAIL_VALUE),
        ],
        "social": [
            ("Twitter/X Thread", SOCIAL_TWITTER),
            ("Facebook Post", SOCIAL_FACEBOOK),
            ("LinkedIn Post", SOCIAL_LINKEDIN),
            ("Instagram Caption", SOCIAL_INSTAGRAM),
            ("TikTok Script", SOCIAL_TIKTOK),
        ],
        "ads": [
            ("Ad Copy — Problem-Solution", AD_COPY_1),
            ("Ad Copy — Social Proof", AD_COPY_2),
        ],
        "video": [
            ("YouTube Review Script", VIDEO_SCRIPT),
        ],
    }

    types_to_generate = list(templates.keys()) if content_type == "all" else [content_type]

    for ctype in types_to_generate:
        if ctype not in templates:
            continue
        content[ctype] = []
        for name, template in templates[ctype]:
            try:
                rendered = template.format(**v)
            except KeyError as e:
                rendered = f"[Template rendering error: missing key {e}]\n\n{template}"
            content[ctype].append({
                "name": name,
                "content": rendered,
            })

    return content


def format_as_markdown(content, product_name):
    """Format all generated content as a single Markdown document."""
    md = f"# Marketing Content — {product_name}\n\n"
    md += f"*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*\n\n"
    md += "---\n\n"

    section_titles = {
        "emails": "📧 Email Swipes",
        "social": "📱 Social Media Posts",
        "ads": "📢 Ad Copy",
        "video": "🎬 Video Script",
    }

    for section, items in content.items():
        md += f"# {section_titles.get(section, section.title())}\n\n"
        for item in items:
            md += item["content"] + "\n\n"

    return md


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Generate affiliate marketing content")
    parser.add_argument("--data", required=True, help="Path to product data JSON or 'sample'")
    parser.add_argument(
        "--type",
        choices=["all", "emails", "social", "ads", "video"],
        default="all",
        help="Content type to generate (default: all)",
    )
    parser.add_argument("--output", default="", help="Output file path")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format")
    args = parser.parse_args()

    # Load data
    if args.data == "sample":
        # Import sample data from page_generator
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from page_generator import generate_sample_data
        data = generate_sample_data()
    else:
        with open(args.data, "r") as f:
            data = json.load(f)

    content = generate_content(data, args.type)

    if args.format == "json":
        output = json.dumps(content, indent=2)
    else:
        output = format_as_markdown(content, data.get("product_name", "Product"))

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Content saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
