import asyncio
from datetime import datetime, timezone
import asyncpg

import os
from dotenv import load_dotenv

load_dotenv()

async def populate_all():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is required. Please check your .env file.")

    conn = await asyncpg.connect(db_url, timeout=15)
    user_id = '00000000-0000-0000-0000-000000000001'
    now = datetime.now(timezone.utc)
    c1 = "11111111-1111-1111-1111-111111111111"
    c2 = "22222222-2222-2222-2222-222222222222"
    c3 = "33333333-3333-3333-3333-333333333333"
    c4 = "44444444-4444-4444-4444-444444444444"

    # Study Sessions
    sessions = [
        ("51111111-1111-1111-1111-111111111111", user_id, c1, "Deep Work: Memory Allocator C Implementation", "deep_work", datetime.fromisoformat("2026-10-24T10:00:00+00:00"), datetime.fromisoformat("2026-10-24T12:00:00+00:00"), 120, False, True, now, now),
        ("52222222-2222-2222-2222-222222222222", user_id, c2, "Revision: Cryptography Drill with Alexa", "revision", datetime.fromisoformat("2026-10-24T14:30:00+00:00"), datetime.fromisoformat("2026-10-24T16:00:00+00:00"), 90, False, True, now, now),
        ("53333333-3333-3333-3333-333333333333", user_id, c4, "Lecture: Distributed Consensus & Paxos", "lecture", datetime.fromisoformat("2026-10-25T09:00:00+00:00"), datetime.fromisoformat("2026-10-25T10:30:00+00:00"), 90, False, False, now, now),
        ("54444444-4444-4444-4444-444444444444", user_id, c3, "Linear Algebra Problem Set Deep Focus", "deep_work", datetime.fromisoformat("2026-10-25T11:00:00+00:00"), datetime.fromisoformat("2026-10-25T12:30:00+00:00"), 90, False, False, now, now)
    ]
    for s in sessions:
        await conn.execute("""
            INSERT INTO public.study_sessions (id, user_id, course_id, title, session_type, start_time, end_time, duration_minutes, completed, alexa_synced, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            ON CONFLICT (id) DO NOTHING
        """, *s)

    # Reminders
    reminders = [
        ("61111111-1111-1111-1111-111111111111", user_id, c2, "Review RSA Public Key proof before morning quiz", datetime.fromisoformat("2026-10-25T08:30:00+00:00"), "urgent", "pending", now, now),
        ("62222222-2222-2222-2222-222222222222", user_id, c1, "Submit kernel lab partner selection", datetime.fromisoformat("2026-10-26T17:00:00+00:00"), "medium", "pending", now, now),
        ("63333333-3333-3333-3333-333333333333", user_id, c3, "Pick up Linear Algebra recommended textbook from campus library", datetime.fromisoformat("2026-10-27T12:00:00+00:00"), "low", "completed", now, now)
    ]
    for r in reminders:
        await conn.execute("""
            INSERT INTO public.reminders (id, user_id, course_id, title, due_date, priority, status, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (id) DO NOTHING
        """, *r)

    # Learning Resources
    resources = [
        ("71111111-1111-1111-1111-111111111111", c1, "Buddy Allocator Internals & Memory Fragmentation", "Operating Systems", "https://campus.edu/resources/buddy-allocator", "notes", "Step-by-step guide to power-of-two block allocation and coalescing", now),
        ("72222222-2222-2222-2222-222222222222", c2, "Zero Trust Architecture & Perimeter Security", "Cybersecurity", "https://campus.edu/resources/zero-trust", "article", "NIST SP 800-207 guidelines summarized for undergrad coursework", now),
        ("73333333-3333-3333-3333-333333333333", c3, "Eigenvalues & Spectral Theorem Visualizations", "Applied Linear Algebra", "https://campus.edu/resources/eigen-visuals", "video", "Interactive 3D geometric interpretation of transformations", now),
        ("74444444-4444-4444-4444-444444444444", c4, "Raft Consensus Algorithm Paper & Lecture Slides", "Distributed Computing", "https://campus.edu/resources/raft-guide", "official_docs", "In Search of an Understandable Consensus Algorithm (Ongaro & Ousterhout)", now)
    ]
    for res in resources:
        await conn.execute("""
            INSERT INTO public.learning_resources (id, course_id, title, topic, url, resource_type, summary, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (id) DO NOTHING
        """, *res)

    print("All Supabase tables populated successfully!")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(populate_all())
