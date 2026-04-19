# Global Control Workflow Creation Guide

## Prerequisites

Before creating workflows via API, ensure these are configured in your Global Control dashboard:

1. **Sending Domain** — Required for "from" email addresses
2. **Workflow Group** — Workflows must belong to a group
3. **Valid API Key** — Must have proper permissions

---

## Step-by-Step Instructions

### Step 1: Configure Your Dashboard

Log into Global Control at: `https://app.globalcontrol.io`

1. **Add a Domain:**
   - Go to Settings → Domains
   - Add and verify your sending domain
   - Example: `yourdomain.com`

2. **Create a Workflow Group:**
   - Go to Workflows → Groups
   - Click "Create Group"
   - Name it (e.g., "Email Sequences")

3. **Get the Group ID:**
   - Use the API to get the group ID: `GET /api/ai/workflows/groups`
   - Or find it in the dashboard URL when viewing the group

---

### Step 2: Create Workflow via API

**Endpoint:** `POST /api/ai/workflows`

**Headers:**
```
X-API-KEY: your_api_key_here
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Your Workflow Name",
  "description": "Description of what this workflow does",
  "status": "active",
  "workflowGroupId": "your_group_id_here"
}
```

**Example:**
```bash
curl -X POST \
  -H "X-API-KEY: 9ee9d1006f37fe14b3b9fe06b15ce39d207e3b61d765914a1b6bc7a2f8030219" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo: AI Evolution Sequence",
    "description": "3-email sequence about AI evolution",
    "status": "active",
    "workflowGroupId": "your_group_id"
  }' \
  https://api.globalcontrol.io/api/ai/workflows
```

---

### Step 3: Add Email Flows

**Endpoint:** `PUT /api/ai/workflows/{workflow_id}`

**Headers:**
```
X-API-KEY: your_api_key_here
Content-Type: application/json
```

**Request Body:**
```json
{
  "flows": [
    {
      "type": "SEND_EMAIL",
      "index": 0,
      "data": {
        "name": "Email 1: Welcome",
        "subject": "Your Subject Line",
        "body": "<p>HTML email content here</p>",
        "from_email": "your_verified_email@domain.com",
        "from_name": "Your Name",
        "reply_to": "reply@domain.com"
      }
    },
    {
      "type": "TIMER",
      "index": 1,
      "data": {
        "waitFor": "2",
        "timeIn": "days"
      }
    },
    {
      "type": "SEND_EMAIL",
      "index": 2,
      "data": {
        "name": "Email 2: Follow-up",
        "subject": "Second Email Subject",
        "body": "<p>More HTML content</p>",
        "from_email": "your_verified_email@domain.com",
        "from_name": "Your Name",
        "reply_to": "reply@domain.com"
      }
    }
  ]
}
```

**Important Notes:**
- Flows use sequential index (0, 1, 2, 3...)
- TIMER flows create delays between emails
- PUT appends flows (doesn't replace)
- Email body must be HTML

---

## Demo Workflow: AI Evolution Sequence

### Email 1: Welcome (Immediate)

**Subject:** Welcome — here's what to expect (+ something about AI)

**Body:**
```html
<p>Hey [First Name],</p>
<p>Welcome to the list!</p>
<p>Over the next few days, I'll be sharing some insights about AI that most people are missing right now.</p>
<p>Not the hype. Not the noise. The actual shifts happening behind the scenes.</p>
<p>Including why the CEO of Nvidia recently said we're at a tipping point that will change everything.</p>
<p>More on that in a moment.</p>
<p>For now, just wanted to say thanks for being here.</p>
<p>Talk soon,<br>Carven</p>
<p>P.S. — Keep an eye out for Email #2. I'll share something that might save you months of trial and error.</p>
```

---

### Email 2: Courtesy Check-in (2 days later)

**Subject:** Quick question about AI...

**Body:**
```html
<p>Hey [First Name],</p>
<p>Quick check-in.</p>
<p>I sent an email a couple days ago about the AI shift happening right now.</p>
<p>Wanted to make sure you saw it — especially the part about what Nvidia's CEO is saying about the platform that will change everything.</p>
<p>If you missed it, here's the short version:</p>
<p>We're not just talking about ChatGPT or Midjourney anymore.</p>
<p>There's a bigger play happening. One that affects how businesses actually operate, scale, and compete.</p>
<p>Some people are seeing it. Most aren't.</p>
<p><strong>Question for you:</strong></p>
<p>Are you interested in getting the latest updates on OpenClaw and what's actually working right now?</p>
<p>If yes, just reply with "YES" and I'll make sure you get the inside track.</p>
<p>If not, no worries — you'll stay on the list for the regular updates.</p>
<p>Either way, thanks for reading.</p>
<p>Carven</p>
<p>P.S. — Either way, Email #3 is coming tomorrow. I'll break down exactly how AI is evolving and what it means for you.</p>
```

---

### Email 3: AI Evolution (2 days later)

**Subject:** How AI is actually evolving (not what you're hearing)

**Body:**
```html
<p>Hey [First Name],</p>
<p>Everyone's talking about AI right now.</p>
<p>But here's what most people are getting wrong:</p>
<p>They're focused on the tools.</p>
<p>ChatGPT. Midjourney. Claude.</p>
<p>Useful? Sure.</p>
<p>But they're missing the bigger shift.</p>
<p><strong>The real evolution isn't the tools. It's the systems.</strong></p>
<p>Here's what I mean:</p>
<p>For the past year, AI has been about prompts and single outputs.</p>
<p>You ask. It answers. Done.</p>
<p>But that's changing.</p>
<p>The next wave — the one Nvidia's CEO is pointing to — is about <strong>AI systems that actually run parts of your business.</strong></p>
<p>Not just writing emails. Not just generating images.</p>
<p>But handling workflows. Making decisions. Executing tasks.</p>
<p>That's where OpenClaw comes in.</p>
<p>It's not another AI tool. It's an AI operating system.</p>
<p>And right now, early adopters are using it to:</p>
<ul>
  <li>Automate content pipelines</li>
  <li>Deploy sales funnels in minutes</li>
  <li>Run affiliate campaigns on autopilot</li>
  <li>Build businesses without the usual overhead</li>
</ul>
<p>The people who see this shift early are positioning themselves ahead of the curve.</p>
<p>The ones who wait? They'll be playing catch-up in 6 months.</p>
<p><strong>So here's my question:</strong></p>
<p>Do you want to see how this actually works?</p>
<p>I put together a quick overview showing what's possible.</p>
<p>No fluff. Just the actual system and how it fits together.</p>
<p>Check it out if you're curious.</p>
<p>Either way, now you know what's actually happening behind the AI headlines.</p>
<p>Talk soon,<br>Carven</p>
<p>P.S. — This isn't about jumping on a trend. It's about seeing where things are headed and making a smart move before everyone else catches on.</p>
```

---

## API Reference

### Key Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| Get Workflows | GET | `/api/ai/workflows` |
| Create Workflow | POST | `/api/ai/workflows` |
| Update Workflow | PUT | `/api/ai/workflows/{id}` |
| Get Workflow Groups | GET | `/api/ai/workflows/groups` |
| Get Tags | GET | `/api/ai/tags` |
| Fire Tag | POST | `/api/ai/tags/fire-tag/{tagId}` |
| Get Contacts | GET | `/api/ai/contacts?search=TERM` |
| Get Domains | GET | `/api/ai/domains` |

### Authentication

**Header:** `X-API-KEY: your_api_key`

**API Key:** `9ee9d1006f37fe14b3b9fe06b15ce39d207e3b61d765914a1b6bc7a2f8030219`

**Base URL:** `https://api.globalcontrol.io/api/ai`

---

## Troubleshooting

### "Something Went Wrong" Error
- Check that workflowGroupId is valid
- Ensure from_email is a verified domain
- Verify API key has proper permissions

### "Invalid Json Format" Error
- Don't send Content-Type header on GET requests
- Only use Content-Type: application/json on POST/PUT

### Workflow Not Triggering
- Check workflow status is "active"
- Verify contact has valid email
- Check if contact is in correct tag/segment

---

## Saved Credentials

**Location:** `~/.openclaw/workspace/.env.personal`

```
GLOBALCONTROL_API_KEY=9ee9d1006f37fe14b3b9fe06b15ce39d207e3b61d765914a1b6bc7a2f8030219
GLOBALCONTROL_API_URL=https://api.globalcontrol.io/api/ai
```

---

**Created:** 2026-04-19
**Skill:** Global Control v2.0
