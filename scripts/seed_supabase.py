import asyncio
import json
from datetime import datetime, timezone
import asyncpg

import os
from dotenv import load_dotenv

load_dotenv()

async def seed():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is required. Please check your .env file.")

    conn = await asyncpg.connect(db_url, timeout=15)
    user_id = '00000000-0000-0000-0000-000000000001'
    now = datetime.now(timezone.utc)

    # 1. Profile
    user = await conn.fetchrow("SELECT id FROM public.user_profiles WHERE id = $1", user_id)
    if not user:
        prefs = json.dumps({"response_style": "concise", "syllabus_parsing": True, "voice_confirmations": True})
        await conn.execute("""
            INSERT INTO public.user_profiles (id, email, full_name, major, semester, current_gpa, target_gpa, weekly_target_hours, ai_preferences, alexa_sync_enabled, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb, $10, $11, $12)
        """, user_id, "kishor@campus.edu", "Kishor", "B.Tech CS", "Sem 6", 3.78, 3.90, 24.0, prefs, True, now, now)
        print("Seeded User Profile into Supabase.")

        # 2. Courses
        c1 = "11111111-1111-1111-1111-111111111111"
        c2 = "22222222-2222-2222-2222-222222222222"
        c3 = "33333333-3333-3333-3333-333333333333"
        c4 = "44444444-4444-4444-4444-444444444444"

        courses = [
            (c1, user_id, "CS301", "Operating Systems", 4, "#4338ca", "3.8", now, now),
            (c2, user_id, "CS304", "Cybersecurity", 3, "#006c49", "3.9", now, now),
            (c3, user_id, "MATH201", "Applied Linear Algebra", 3, "#8a570e", "3.6", now, now),
            (c4, user_id, "CS308", "Distributed Computing", 4, "#7c3aed", "3.8", now, now)
        ]
        for c in courses:
            await conn.execute("""
                INSERT INTO public.courses (id, user_id, code, name, credits, color, grade, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (id) DO NOTHING
            """, *c)
        print("Seeded Courses into Supabase.")

        # 3. Assignments
        assignments = [
            ("a1111111-1111-1111-1111-111111111111", user_id, c1, "Kernel Memory Allocator Lab", "Implement buddy memory allocator in C with fragmentation tests", datetime.fromisoformat("2026-10-27T23:59:00+00:00"), "in_progress", "urgent", 15.0, None, now, now),
            ("a2222222-2222-2222-2222-222222222222", user_id, c2, "Vulnerability Assessment Report", "Analyze OWASP top 10 flaws in target campus portal", datetime.fromisoformat("2026-10-29T18:00:00+00:00"), "pending", "medium", 10.0, None, now, now),
            ("a3333333-3333-3333-3333-333333333333", user_id, c3, "Eigenvalues Problem Set 5", "Solve matrix decomposition problems 1 through 12", datetime.fromisoformat("2026-10-31T23:59:00+00:00"), "pending", "low", 5.0, None, now, now),
            ("a4444444-4444-4444-4444-444444444444", user_id, c4, "Raft Consensus Simulation", "Build 3-node leader election mock in Python/Go", datetime.fromisoformat("2026-11-04T23:59:00+00:00"), "pending", "medium", 20.0, None, now, now),
            ("a5555555-5555-5555-5555-555555555555", user_id, c1, "Process Synchronization Quiz", "Online multiple-choice check", datetime.fromisoformat("2026-10-22T23:59:00+00:00"), "completed", "low", 5.0, now, now, now)
        ]
        for a in assignments:
            await conn.execute("""
                INSERT INTO public.assignments (id, user_id, course_id, title, description, due_date, status, priority, weight_percentage, completed_at, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ON CONFLICT (id) DO NOTHING
            """, *a)
        print("Seeded Assignments into Supabase.")

        # 4. Exams
        exams = [
            ("e1111111-1111-1111-1111-111111111111", user_id, c2, "Midterm: System Security & Cryptography", datetime.fromisoformat("2026-10-28T09:00:00+00:00"), "Auditorium Hall B", 92.0, json.dumps([
                {"name": "Public Key Cryptography & RSA", "covered": True},
                {"name": "Buffer Overflows & ROP Chains", "covered": True},
                {"name": "Zero Trust Architectures", "covered": False}
            ]), "Bring student ID and scientific calculator", now, now),
            ("e2222222-2222-2222-2222-222222222222", user_id, c1, "Final: Advanced Operating Systems", datetime.fromisoformat("2026-11-15T13:30:00+00:00"), "CS Building Room 204", 95.0, json.dumps([
                {"name": "Virtual Memory Management", "covered": True},
                {"name": "File Systems & Journaling", "covered": False},
                {"name": "Device Drivers & Interrupts", "covered": False}
            ]), "Open book, formula sheet allowed", now, now)
        ]
        for e in exams:
            await conn.execute("""
                INSERT INTO public.exams (id, user_id, course_id, title, exam_date, location, target_score, syllabus_units, notes, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9, $10, $11)
                ON CONFLICT (id) DO NOTHING
            """, *e)
        print("Seeded Exams into Supabase.")

        # 5. Study Sessions
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
        print("Seeded Study Sessions into Supabase.")

        # 6. Reminders
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
        print("Seeded Reminders into Supabase.")

        # 7. Learning Resources
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
        print("Seeded Learning Resources into Supabase.")

    await conn.close()
    print("Supabase seed complete!")

if __name__ == "__main__":
    asyncio.run(seed())
