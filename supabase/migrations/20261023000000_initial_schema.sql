-- CampusPilot Initial PostgreSQL / Supabase Schema Migration
-- Migration ID: 20261023000000_initial_schema.sql

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. User Profiles
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE,
    full_name TEXT NOT NULL DEFAULT 'Student',
    major TEXT DEFAULT 'Computer Science',
    semester TEXT DEFAULT 'Semester 1',
    current_gpa NUMERIC(3, 2) DEFAULT 3.75,
    target_gpa NUMERIC(3, 2) DEFAULT 3.90,
    weekly_target_hours NUMERIC(4, 1) DEFAULT 24.0,
    ai_preferences JSONB DEFAULT '{"response_style": "concise", "syllabus_parsing": true, "voice_confirmations": true}'::jsonb,
    alexa_sync_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 2. Courses
CREATE TABLE IF NOT EXISTS public.courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    credits INT DEFAULT 3,
    color TEXT DEFAULT '#4338ca',
    grade TEXT DEFAULT 'A',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    CONSTRAINT unique_user_course UNIQUE(user_id, code)
);

-- 3. Assignments
CREATE TABLE IF NOT EXISTS public.assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    course_id UUID REFERENCES public.courses(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    due_date TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'overdue')),
    priority TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'urgent')),
    weight_percentage NUMERIC(5, 2) DEFAULT 10.0,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 4. Exams
CREATE TABLE IF NOT EXISTS public.exams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    course_id UUID REFERENCES public.courses(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    exam_date TIMESTAMPTZ NOT NULL,
    location TEXT DEFAULT '',
    target_score NUMERIC(5, 2) DEFAULT 90.0,
    syllabus_units JSONB DEFAULT '[]'::jsonb,
    notes TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 5. Study Sessions
CREATE TABLE IF NOT EXISTS public.study_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    course_id UUID REFERENCES public.courses(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    session_type TEXT NOT NULL DEFAULT 'deep_work' CHECK (session_type IN ('lecture', 'deep_work', 'revision', 'group_study', 'lab')),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    duration_minutes INT NOT NULL DEFAULT 60,
    completed BOOLEAN DEFAULT FALSE,
    alexa_synced BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 6. Assistant Messages
CREATE TABLE IF NOT EXISTS public.assistant_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    action_type TEXT DEFAULT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_courses_user ON public.courses(user_id);
CREATE INDEX IF NOT EXISTS idx_assignments_user_due ON public.assignments(user_id, due_date);
CREATE INDEX IF NOT EXISTS idx_exams_user_date ON public.exams(user_id, exam_date);
CREATE INDEX IF NOT EXISTS idx_sessions_user_time ON public.study_sessions(user_id, start_time);
CREATE INDEX IF NOT EXISTS idx_messages_user_time ON public.assistant_messages(user_id, created_at);

-- Row Level Security (RLS) Configuration
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.exams ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.study_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assistant_messages ENABLE ROW LEVEL SECURITY;

-- Supabase RLS Policies (using auth.uid())
-- 1. User Profiles
CREATE POLICY "Users can manage their own profile"
    ON public.user_profiles
    FOR ALL
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- 2. Courses
CREATE POLICY "Users can manage their own courses"
    ON public.courses
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- 3. Assignments
CREATE POLICY "Users can manage their own assignments"
    ON public.assignments
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- 4. Exams
CREATE POLICY "Users can manage their own exams"
    ON public.exams
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- 5. Study Sessions
CREATE POLICY "Users can manage their own study sessions"
    ON public.study_sessions
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- 6. Assistant Messages
CREATE POLICY "Users can manage their own assistant conversations"
    ON public.assistant_messages
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);
