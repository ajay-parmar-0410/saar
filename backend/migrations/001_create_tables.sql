-- Saar: Phase 1 — Database Migration
-- Creates all 7 tables with RLS policies

-- ============================================================
-- 1. Users table
-- Uses Supabase Auth's auth.users as the source of truth.
-- This table extends it with app-specific fields.
-- ============================================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    name TEXT,
    avatar_url TEXT,
    user_type TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_active_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_select_own" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "users_insert_own" ON public.users
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "users_update_own" ON public.users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "users_delete_own" ON public.users
    FOR DELETE USING (auth.uid() = id);

-- Service role bypass (for backend operations)
CREATE POLICY "users_service_all" ON public.users
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================================
-- 2. User Preferences
-- ============================================================
CREATE TABLE IF NOT EXISTS public.user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    topics TEXT[] DEFAULT '{}',
    sources TEXT[] DEFAULT '{}',
    briefing_depth TEXT NOT NULL DEFAULT 'detailed'
        CHECK (briefing_depth IN ('headlines', 'detailed')),
    location TEXT DEFAULT 'Mumbai',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id)
);

ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;

CREATE POLICY "prefs_select_own" ON public.user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "prefs_insert_own" ON public.user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "prefs_update_own" ON public.user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "prefs_delete_own" ON public.user_preferences
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "prefs_service_all" ON public.user_preferences
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================================
-- 3. User Interests (Watchlist)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.user_interests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('stock', 'repo', 'subreddit', 'keyword', 'team')),
    value TEXT NOT NULL,
    added_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.user_interests ENABLE ROW LEVEL SECURITY;

CREATE POLICY "interests_select_own" ON public.user_interests
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "interests_insert_own" ON public.user_interests
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "interests_update_own" ON public.user_interests
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "interests_delete_own" ON public.user_interests
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "interests_service_all" ON public.user_interests
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================================
-- 4. Briefing Schedules
-- ============================================================
CREATE TABLE IF NOT EXISTS public.briefing_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    times TEXT[] DEFAULT '{"07:00"}',
    timezone TEXT NOT NULL DEFAULT 'Asia/Kolkata',
    enabled BOOLEAN NOT NULL DEFAULT true,
    UNIQUE(user_id)
);

ALTER TABLE public.briefing_schedules ENABLE ROW LEVEL SECURITY;

CREATE POLICY "schedules_select_own" ON public.briefing_schedules
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "schedules_insert_own" ON public.briefing_schedules
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "schedules_update_own" ON public.briefing_schedules
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "schedules_delete_own" ON public.briefing_schedules
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "schedules_service_all" ON public.briefing_schedules
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================================
-- 5. Briefings
-- ============================================================
CREATE TABLE IF NOT EXISTS public.briefings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    content TEXT,
    sections JSONB DEFAULT '[]',
    top_story TEXT,
    item_count INTEGER DEFAULT 0,
    alert_count INTEGER DEFAULT 0,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    read BOOLEAN NOT NULL DEFAULT false,
    read_at TIMESTAMPTZ
);

CREATE INDEX idx_briefings_user_id ON public.briefings(user_id);
CREATE INDEX idx_briefings_generated_at ON public.briefings(generated_at DESC);

ALTER TABLE public.briefings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "briefings_select_own" ON public.briefings
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "briefings_insert_own" ON public.briefings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "briefings_update_own" ON public.briefings
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "briefings_service_all" ON public.briefings
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================================
-- 6. Chat History
-- ============================================================
CREATE TABLE IF NOT EXISTS public.chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    sources JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_chat_history_user_id ON public.chat_history(user_id);
CREATE INDEX idx_chat_history_created_at ON public.chat_history(created_at DESC);

ALTER TABLE public.chat_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "chat_select_own" ON public.chat_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "chat_insert_own" ON public.chat_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "chat_service_all" ON public.chat_history
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================================
-- 7. Preference History (Changelog)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.preference_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    action TEXT NOT NULL CHECK (action IN ('added', 'removed')),
    field TEXT NOT NULL,
    value TEXT NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_pref_history_user_id ON public.preference_history(user_id);

ALTER TABLE public.preference_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "pref_history_select_own" ON public.preference_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "pref_history_insert_own" ON public.preference_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "pref_history_service_all" ON public.preference_history
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================================
-- Auto-create user profile on signup (trigger)
-- ============================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', ''),
        COALESCE(NEW.raw_user_meta_data->>'avatar_url', '')
    );

    INSERT INTO public.user_preferences (user_id)
    VALUES (NEW.id);

    INSERT INTO public.briefing_schedules (user_id)
    VALUES (NEW.id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
