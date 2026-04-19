# Supabase Backend Setup for Marriage Quiz

## 📋 Overview

This is a complete Supabase backend solution for the Marriage Quiz with:
- PostgreSQL database for storing quiz responses
- Password-protected admin dashboard
- Real-time statistics and data visualization

## 📁 Files

| File | Description |
|------|-------------|
| `supabase-setup-instructions.md` | Step-by-step Supabase setup guide |
| `database-schema.sql` | SQL to create the quiz_responses table |
| `quiz.html` | Updated quiz form with Supabase integration |
| `admin-dashboard.html` | Password-protected admin dashboard |

## 🚀 Quick Start

### 1. Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com) and sign up/login
2. Click **New Project**
3. Enter project details and create

### 2. Run Database Schema

1. In Supabase, go to **SQL Editor** → **New query**
2. Copy contents of `database-schema.sql`
3. Click **Run**

### 3. Get API Keys

1. Go to **Project Settings** → **API**
2. Copy:
   - **Project URL**
   - **anon public** API key (for quiz form)
   - **service_role** secret (for admin dashboard)

### 4. Update Configuration

#### In `quiz.html`:
Replace these placeholders:
```javascript
const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY';
```

#### In `admin-dashboard.html`:
Replace these placeholders:
```javascript
const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_SERVICE_ROLE_KEY = 'YOUR_SUPABASE_SERVICE_ROLE_KEY';
const ADMIN_PASSWORD = 'admin123'; // Change this!
```

### 5. Deploy

Upload `quiz.html` and `admin-dashboard.html` to your web server.

## 🔒 Security Notes

⚠️ **IMPORTANT:**
- Never commit the `admin-dashboard.html` with the service_role key to public repositories
- The service_role key has full database access - protect it!
- Change the default admin password before deploying
- For production, consider using environment variables or a backend proxy

## 📊 Database Schema

### quiz_responses table

| Field | Type | Description |
|-------|------|-------------|
| `id` | uuid | Primary key, auto-generated |
| `location` | text | User's location (namibia, south_africa, other) |
| `pressure` | text | Primary pressure source |
| `financial_tension` | integer | 1-10 scale |
| `impact_area` | text | Area most impacted |
| `difficult_talks` | integer | 1-10 scale |
| `greatest_need` | text | What they need most |
| `open_to_help` | text | Whether they're open to help |
| `biggest_challenge` | text | Optional free text |
| `created_at` | timestamp | Auto-generated |

## 🔗 API Usage

### Submit Quiz Response

The quiz form automatically POSTs to Supabase using the JavaScript client.

### Admin Dashboard

- Visit `admin-dashboard.html` in your browser
- Enter the admin password
- View all responses, statistics, and summaries

## 📞 Support

See `supabase-setup-instructions.md` for detailed instructions and troubleshooting.
