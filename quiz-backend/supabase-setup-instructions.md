# Supabase Setup Instructions for Marriage Quiz

## Step 1: Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name:** `marriage-quiz` (or your preferred name)
   - **Database Password:** Create a strong password (save this!)
   - **Region:** Choose closest to your users (e.g., `us-east-1` for US East Coast)
5. Click "Create new project" (takes ~2 minutes to provision)

## Step 2: Get Your API Credentials

Once your project is ready:

1. Go to **Project Settings** (gear icon in left sidebar)
2. Click **API** in the sidebar
3. Copy these values (you'll need them):
   - **Project URL** (e.g., `https://xxxxxxxxxxxxxx.supabase.co`)
   - **anon public** API key (starts with `eyJ...`)
   - **service_role** secret (for admin operations - keep this secure!)

## Step 3: Run the Database Schema

1. Go to **SQL Editor** in the left sidebar
2. Click **New query**
3. Copy and paste the contents of `database-schema.sql` from this folder
4. Click **Run** to create the table

## Step 4: Configure Row Level Security (RLS)

The schema includes RLS policies for security. By default:
- Anyone can INSERT new quiz responses
- Only authenticated users can SELECT (for the admin dashboard)

### To enable admin access:

Option A: Use Service Role Key (Recommended for admin dashboard)
- Use the `service_role` key in your admin dashboard
- This bypasses RLS and has full access

Option B: Create an admin user
1. Go to **Authentication** → **Users**
2. Click **Add user**
3. Create an admin user with email/password
4. Use this to sign in on the admin dashboard

## Step 5: Update Your Frontend

1. Copy your **Project URL** and **anon public** API key
2. Open `quiz.html` and replace:
   - `YOUR_SUPABASE_URL` with your actual project URL
   - `YOUR_SUPABASE_ANON_KEY` with your anon public key

3. Open `admin-dashboard.html` and replace:
   - `YOUR_SUPABASE_URL` with your actual project URL
   - `YOUR_SUPABASE_SERVICE_ROLE_KEY` with your service_role key (for admin access)

## Step 6: Deploy

Upload these files to your web server:
- `quiz.html` - The quiz form (already updated)
- `admin-dashboard.html` - The admin panel

## Security Notes

⚠️ **IMPORTANT:**
- Never commit `admin-dashboard.html` with the service_role key to public repositories
- The service_role key has full database access - protect it!
- Consider using environment variables or a backend proxy for production
- For production, implement proper authentication instead of simple password protection

## Testing

1. Open `quiz.html` in a browser
2. Submit a test quiz response
3. Open `admin-dashboard.html`
4. Enter the admin password: `admin123` (change this in production!)
5. You should see your test response in the table

## Troubleshooting

**CORS Errors:**
- Go to **API Settings** in Supabase
- Add your domain to "Allowed Origins" (or use `*` for testing)

**RLS Errors:**
- Check that the RLS policies were created properly
- Verify you're using the correct API key

**Connection Errors:**
- Double-check your Supabase URL and API keys
- Ensure your project is active (not paused)

## Need Help?

- Supabase Docs: https://supabase.com/docs
- JavaScript Client: https://supabase.com/docs/reference/javascript
