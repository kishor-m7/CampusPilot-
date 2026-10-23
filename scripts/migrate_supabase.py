import asyncio
import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def run_migrations():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is required. Please check your .env file.")

    print("Connecting to Supabase PostgreSQL via DATABASE_URL...")
    conn = await asyncpg.connect(db_url, timeout=15)
    print("Successfully connected to Supabase PostgreSQL!")

    # 1. Initial Schema
    print("Applying migration 20261023000000_initial_schema.sql...")
    with open("supabase/migrations/20261023000000_initial_schema.sql", "r", encoding="utf-8") as f:
        sql1 = f.read()
    await conn.execute(sql1)
    print("Migration 1 applied successfully!")

    # 2. Reminders & Resources Schema
    print("Applying migration 20261023000001_reminders_and_resources.sql...")
    with open("supabase/migrations/20261023000001_reminders_and_resources.sql", "r", encoding="utf-8") as f:
        sql2 = f.read()
    await conn.execute(sql2)
    print("Migration 2 applied successfully!")

    # 3. Check public tables
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
    rows = await conn.fetch(query)
    table_names = [r["table_name"] for r in rows]
    print(f"Tables in Supabase public schema: {table_names}")

    # 4. Check if demo user exists
    user_count = await conn.fetchval("SELECT count(*) FROM public.user_profiles")
    print(f"User profiles count in Supabase: {user_count}")

    await conn.close()
    print("Database migration finished successfully.")

if __name__ == "__main__":
    asyncio.run(run_migrations())
