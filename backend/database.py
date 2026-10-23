import os
import sqlite3
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from backend.config import settings

logger = logging.getLogger("campuspilot.database")

# Check if PostgreSQL is configured
USE_POSTGRES = bool(settings.DATABASE_URL and ("postgres" in settings.DATABASE_URL))

pg_pool = None

# ---------------------------------------------------------------------------
# SQLite Local Helper Functions
# ---------------------------------------------------------------------------
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "campuspilot_dev.db")

def get_sqlite_conn():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_sqlite_tables():
    conn = get_sqlite_conn()
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_profiles (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        full_name TEXT NOT NULL,
        major TEXT,
        semester TEXT,
        current_gpa REAL,
        target_gpa REAL,
        weekly_target_hours REAL,
        ai_preferences TEXT,
        alexa_sync_enabled INTEGER,
        created_at TEXT,
        updated_at TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        code TEXT NOT NULL,
        name TEXT NOT NULL,
        credits INTEGER,
        color TEXT,
        grade TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(user_id) REFERENCES user_profiles(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        course_id TEXT,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT NOT NULL,
        status TEXT NOT NULL,
        priority TEXT NOT NULL,
        weight_percentage REAL,
        completed_at TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(user_id) REFERENCES user_profiles(id),
        FOREIGN KEY(course_id) REFERENCES courses(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS exams (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        course_id TEXT,
        title TEXT NOT NULL,
        exam_date TEXT NOT NULL,
        location TEXT,
        target_score REAL,
        syllabus_units TEXT,
        notes TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(user_id) REFERENCES user_profiles(id),
        FOREIGN KEY(course_id) REFERENCES courses(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS study_sessions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        course_id TEXT,
        title TEXT NOT NULL,
        session_type TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        duration_minutes INTEGER,
        completed INTEGER,
        alexa_synced INTEGER,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(user_id) REFERENCES user_profiles(id),
        FOREIGN KEY(course_id) REFERENCES courses(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS assistant_messages (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        action_type TEXT,
        metadata TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES user_profiles(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        course_id TEXT,
        title TEXT NOT NULL,
        due_date TEXT,
        priority TEXT NOT NULL DEFAULT 'medium',
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(user_id) REFERENCES user_profiles(id),
        FOREIGN KEY(course_id) REFERENCES courses(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS learning_resources (
        id TEXT PRIMARY KEY,
        course_id TEXT,
        title TEXT NOT NULL,
        topic TEXT NOT NULL,
        url TEXT NOT NULL DEFAULT '',
        resource_type TEXT NOT NULL DEFAULT 'notes',
        summary TEXT,
        created_at TEXT,
        FOREIGN KEY(course_id) REFERENCES courses(id)
    );
    """)

    conn.commit()
    conn.close()

def seed_demo_data(user_id: str):
    conn = get_sqlite_conn()
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    cur.execute("SELECT id FROM user_profiles WHERE id = ?", (user_id,))
    if not cur.fetchone():
        # 1. Profile
        prefs = json.dumps({"response_style": "concise", "syllabus_parsing": True, "voice_confirmations": True})
        cur.execute("""
        INSERT INTO user_profiles (id, email, full_name, major, semester, current_gpa, target_gpa, weekly_target_hours, ai_preferences, alexa_sync_enabled, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, "kishor@campus.edu", "Kishor", "B.Tech CS", "Sem 6", 3.78, 3.90, 24.0, prefs, 1, now, now))

        # 2. Courses
        courses = [
            ("c1", user_id, "CS301", "Operating Systems", 4, "#4338ca", "3.8", now, now),
            ("c2", user_id, "CS304", "Cybersecurity", 3, "#006c49", "3.9", now, now),
            ("c3", user_id, "MATH201", "Applied Linear Algebra", 3, "#8a570e", "3.6", now, now),
            ("c4", user_id, "CS308", "Distributed Computing", 4, "#7c3aed", "3.8", now, now)
        ]
        cur.executemany("""
        INSERT INTO courses (id, user_id, code, name, credits, color, grade, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, courses)

        # 3. Assignments
        assignments = [
            ("a1", user_id, "c1", "Kernel Memory Allocator Lab", "Implement buddy memory allocator in C with fragmentation tests", "2026-10-27T23:59:00Z", "in_progress", "urgent", 15.0, None, now, now),
            ("a2", user_id, "c2", "Vulnerability Assessment Report", "Analyze OWASP top 10 flaws in target campus portal", "2026-10-29T18:00:00Z", "pending", "medium", 10.0, None, now, now),
            ("a3", user_id, "c3", "Eigenvalues Problem Set 5", "Solve matrix decomposition problems 1 through 12", "2026-10-31T23:59:00Z", "pending", "low", 5.0, None, now, now),
            ("a4", user_id, "c4", "Raft Consensus Simulation", "Build 3-node leader election mock in Python/Go", "2026-11-04T23:59:00Z", "pending", "medium", 20.0, None, now, now),
            ("a5", user_id, "c1", "Process Synchronization Quiz", "Online multiple-choice check", "2026-10-22T23:59:00Z", "completed", "low", 5.0, now, now, now)
        ]
        cur.executemany("""
        INSERT INTO assignments (id, user_id, course_id, title, description, due_date, status, priority, weight_percentage, completed_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, assignments)

        # 4. Exams
        exams = [
            ("e1", user_id, "c2", "Midterm: System Security & Cryptography", "2026-10-28T09:00:00Z", "Auditorium Hall B", 92.0, json.dumps([
                {"name": "Public Key Cryptography & RSA", "covered": True},
                {"name": "Buffer Overflows & ROP Chains", "covered": True},
                {"name": "Zero Trust Architectures", "covered": False}
            ]), "Bring student ID and scientific calculator", now, now),
            ("e2", user_id, "c1", "Final: Advanced Operating Systems", "2026-11-15T13:30:00Z", "CS Building Room 204", 95.0, json.dumps([
                {"name": "Virtual Memory Management", "covered": True},
                {"name": "File Systems & Journaling", "covered": False},
                {"name": "Device Drivers & Interrupts", "covered": False}
            ]), "Open book, formula sheet allowed", now, now)
        ]
        cur.executemany("""
        INSERT INTO exams (id, user_id, course_id, title, exam_date, location, target_score, syllabus_units, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, exams)

        # 5. Study Sessions
        sessions = [
            ("s1", user_id, "c1", "Deep Work: Memory Allocator C Implementation", "deep_work", "2026-10-24T10:00:00Z", "2026-10-24T12:00:00Z", 120, 0, 1, now, now),
            ("s2", user_id, "c2", "Revision: Cryptography Drill with Alexa", "revision", "2026-10-24T14:30:00Z", "2026-10-24T16:00:00Z", 90, 0, 1, now, now),
            ("s3", user_id, "c4", "Lecture: Distributed Consensus & Paxos", "lecture", "2026-10-25T09:00:00Z", "2026-10-25T10:30:00Z", 90, 0, 0, now, now),
            ("s4", user_id, "c3", "Linear Algebra Problem Set Deep Focus", "deep_work", "2026-10-25T11:00:00Z", "2026-10-25T12:30:00Z", 90, 0, 0, now, now)
        ]
        cur.executemany("""
        INSERT INTO study_sessions (id, user_id, course_id, title, session_type, start_time, end_time, duration_minutes, completed, alexa_synced, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sessions)

        # 6. Assistant Messages
        messages = [
            ("m1", user_id, "user", "Can you draft a 3-day revision plan for Cybersecurity before the midterm?", "plan_day", json.dumps({}), now),
            ("m2", user_id, "assistant", "Here is your high-yield 3-day revision plan for Cybersecurity:\n- Day 1: RSA & Elliptic Curve Cryptography\n- Day 2: Buffer Overflows & Stack Protection\n- Day 3: Zero Trust & Past Year Exam Drills\n\nI've scheduled these slots into your Study Planner and can sync reminders to your connected Alexa devices.", "plan_day", json.dumps({"citations": ["Syllabus Unit 3", "Cybersecurity Midterm Notice"]}), now)
        ]
        cur.executemany("""
        INSERT INTO assistant_messages (id, user_id, role, content, action_type, metadata, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, messages)

    # 7. Seed reminders if empty
    cur.execute("SELECT count(*) FROM reminders WHERE user_id = ?", (user_id,))
    if cur.fetchone()[0] == 0:
        reminders = [
            ("r1", user_id, "c2", "Review RSA Public Key proof before morning quiz", "2026-10-25T08:30:00Z", "urgent", "pending", now, now),
            ("r2", user_id, "c1", "Submit kernel lab partner selection", "2026-10-26T17:00:00Z", "medium", "pending", now, now),
            ("r3", user_id, "c3", "Pick up Linear Algebra recommended textbook from campus library", "2026-10-27T12:00:00Z", "low", "completed", now, now)
        ]
        cur.executemany("""
        INSERT INTO reminders (id, user_id, course_id, title, due_date, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, reminders)

    # 8. Seed learning resources if empty
    cur.execute("SELECT count(*) FROM learning_resources")
    if cur.fetchone()[0] == 0:
        resources = [
            ("lr1", "c1", "Buddy Allocator Internals & Memory Fragmentation", "Operating Systems", "https://campus.edu/resources/buddy-allocator", "notes", "Step-by-step guide to power-of-two block allocation and coalescing", now),
            ("lr2", "c2", "Zero Trust Architecture & Perimeter Security", "Cybersecurity", "https://campus.edu/resources/zero-trust", "article", "NIST SP 800-207 guidelines summarized for undergrad coursework", now),
            ("lr3", "c3", "Eigenvalues & Spectral Theorem Visualizations", "Applied Linear Algebra", "https://campus.edu/resources/eigen-visuals", "video", "Interactive 3D geometric interpretation of transformations", now),
            ("lr4", "c4", "Raft Consensus Algorithm Paper & Lecture Slides", "Distributed Computing", "https://campus.edu/resources/raft-guide", "official_docs", "In Search of an Understandable Consensus Algorithm (Ongaro & Ousterhout)", now)
        ]
        cur.executemany("""
        INSERT INTO learning_resources (id, course_id, title, topic, url, resource_type, summary, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, resources)

    conn.commit()
    conn.close()
    logger.info("Local SQLite seed data verified and loaded for student: %s", user_id)


# ---------------------------------------------------------------------------
# Database Lifecycle & Abstract Query Interface
# ---------------------------------------------------------------------------
async def init_db():
    global pg_pool, USE_POSTGRES
    
    if USE_POSTGRES:
        try:
            import asyncpg
            logger.info("Attempting connection to Supabase PostgreSQL at: %s", settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else "configured URL")
            pg_pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL, min_size=1, max_size=5)
            logger.info("Connected to Supabase PostgreSQL database.")
            return
        except Exception as e:
            logger.warning("Could not connect to PostgreSQL (%s). Falling back to local SQLite.", str(e))
            USE_POSTGRES = False

    # Initialize SQLite
    init_sqlite_tables()
    seed_demo_data(settings.DEFAULT_DEV_USER_ID)
    logger.info("Initialized local SQLite database at: %s", SQLITE_DB_PATH)

async def close_db():
    global pg_pool
    if pg_pool:
        await pg_pool.close()
        logger.info("PostgreSQL connection pool closed.")

async def fetch_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    if USE_POSTGRES and pg_pool:
        # Convert ? to $1, $2 for postgres
        pg_query = query
        parts = query.split('?')
        if len(parts) > 1:
            pg_query = ""
            for i, part in enumerate(parts[:-1]):
                pg_query += f"{part}${i+1}"
            pg_query += parts[-1]
            
        async with pg_pool.acquire() as conn:
            records = await conn.fetch(pg_query, *params)
            return [dict(r) for r in records]
    else:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute(query, params)
        rows = [dict(row) for row in cur.fetchall()]
        conn.close()
        return rows

async def fetch_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    rows = await fetch_all(query, params)
    return rows[0] if rows else None

async def execute(query: str, params: tuple = ()) -> None:
    if USE_POSTGRES and pg_pool:
        pg_query = query
        parts = query.split('?')
        if len(parts) > 1:
            pg_query = ""
            for i, part in enumerate(parts[:-1]):
                pg_query += f"{part}${i+1}"
            pg_query += parts[-1]
            
        async with pg_pool.acquire() as conn:
            await conn.execute(pg_query, *params)
    else:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        conn.close()
