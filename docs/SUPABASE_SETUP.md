# Supabase Setup & Configuration Guide

This guide walks you through connecting **CampusPilot** to a Supabase-hosted PostgreSQL database.

---

## 1. Create a Supabase Project

1. Navigate to [https://supabase.com](https://supabase.com) and log in.
2. Click **New Project**.
3. Select your organization, choose a project name (e.g., `campuspilot-db`), and set a secure database password.
4. Select your preferred region (closest to your users).
5. Wait ~2 minutes for the database cluster to initialize.

---

## 2. Run Database Migrations

You can apply the CampusPilot schema using either the **Supabase Dashboard SQL Editor** or the **Supabase CLI**.

### Option A: Using the SQL Editor (Fastest)
1. In your Supabase Project Dashboard, go to **SQL Editor** (left sidebar).
2. Click **New query**.
3. Open the file `supabase/migrations/20261023000000_initial_schema.sql` in this repository.
4. Copy and paste the entire SQL contents into the query editor.
5. Click **Run**.
6. Verify that the following 6 tables appear in **Table Editor**:
   - `user_profiles`
   - `courses`
   - `assignments`
   - `exams`
   - `study_sessions`
   - `assistant_messages`

### Option B: Using Supabase CLI
```bash
# Link project (replace with your project ref)
npx supabase link --project-ref your-project-ref

# Push migrations
npx supabase db push
```

---

## 3. Retrieve Connection Details & API Keys

From your Supabase Project Settings:
1. Go to **Project Settings** $\rightarrow$ **API**:
   - **Project URL**: Copy this into `SUPABASE_URL`
   - **anon / public key**: Copy this into `SUPABASE_ANON_KEY`
   - **service_role key**: Copy this into `SUPABASE_SERVICE_ROLE_KEY` (Used securely by the Python backend only; never exposed to frontend)
2. Go to **Project Settings** $\rightarrow$ **Database**:
   - Under **Connection string** $\rightarrow$ **URI**: Copy the PostgreSQL connection URI into `DATABASE_URL`.
   - Format: `postgresql://postgres.[ref]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require`

---

## 4. Local Development Fallback

CampusPilot is architected with a local development fallback:
- If `DATABASE_URL` is omitted, the Python backend automatically initializes a local SQLite file (`campuspilot_dev.db`) and seeds it with default student data (Kishor, CS301, Cybersecurity, etc.).
- This allows full frontend and API development without requiring an active Supabase cloud subscription or internet access.
