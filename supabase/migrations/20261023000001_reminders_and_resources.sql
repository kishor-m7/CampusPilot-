-- CampusPilot Database Migration: Reminders & Learning Resources
-- Migration ID: 20261023000001_reminders_and_resources.sql

-- 1. Reminders Table
CREATE TABLE IF NOT EXISTS public.reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    course_id UUID REFERENCES public.courses(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    due_date TIMESTAMPTZ,
    priority TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'urgent')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 2. Learning Resources Table
CREATE TABLE IF NOT EXISTS public.learning_resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES public.courses(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    topic TEXT NOT NULL,
    url TEXT NOT NULL DEFAULT '',
    resource_type TEXT NOT NULL DEFAULT 'notes' CHECK (resource_type IN ('notes', 'article', 'video', 'practice_quiz', 'official_docs')),
    summary TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Indices
CREATE INDEX IF NOT EXISTS idx_reminders_user_status ON public.reminders(user_id, status);
CREATE INDEX IF NOT EXISTS idx_resources_topic ON public.learning_resources(topic);

-- Row Level Security
ALTER TABLE public.reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_resources ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own reminders"
    ON public.reminders
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Authenticated users can read learning resources"
    ON public.learning_resources
    FOR SELECT
    USING (auth.role() = 'authenticated' OR auth.role() = 'anon');
