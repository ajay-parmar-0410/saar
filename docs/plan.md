# Saar — Implementation Plan

> **Status:** Phase 0 Complete
> **Created:** April 3, 2026
> **Reference:** docs/PRD.md

---

## Phase 0: Project Setup & Environment

### 0.1 Repository Setup
- [ ] Initialize git repo
- [ ] Create `.gitignore` (Python, Node, env files, IDE files)
- [ ] Create folder structure: `backend/`, `frontend/`, `docs/`
- [ ] Push initial commit

**Verify:**
- `git status` shows clean repo
- `.gitignore` excludes `node_modules/`, `venv/`, `.env`, `__pycache__/`

### 0.2 Backend Environment
- [ ] Create `backend/` with Python virtual environment
- [ ] Install core dependencies: `fastapi`, `uvicorn`, `langgraph`, `langchain-groq`, `apscheduler`, `supabase-py`, `python-dotenv`, `pydantic`, `httpx`
- [ ] Create `backend/requirements.txt`
- [ ] Create `backend/.env.example` with all required env var names (no values)
- [ ] Create `backend/main.py` with basic FastAPI app

**Verify:**
```bash
cd backend && uvicorn main:app --reload
# Hit http://localhost:8000/health → returns {"status": "ok"}
```

### 0.3 Frontend Environment
- [ ] Create Next.js app in `frontend/` with TypeScript + Tailwind
- [ ] Install shadcn/ui and initialize
- [ ] Install Tremor
- [ ] Install Magic UI (selective components only)
- [ ] Install Framer Motion + AutoAnimate
- [ ] Install Serwist for PWA
- [ ] Create `frontend/.env.example`

**Verify:**
```bash
cd frontend && npm run dev
# Hit http://localhost:3000 → shows Next.js default page
# npm run build → succeeds with no errors
```

### 0.4 Supabase Setup (User Action Required)
- [ ] User creates Supabase project
- [ ] User provides: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- [ ] User enables Google OAuth in Supabase dashboard
- [ ] User provides: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- [ ] Add all keys to `backend/.env` and `frontend/.env.local`

**Verify:**
```bash
# Backend connects to Supabase
python -c "from supabase import create_client; print('connected')"
```

### 0.5 External API Keys (User Action Required)
- [ ] WeatherAPI key → https://www.weatherapi.com/signup.aspx
- [ ] NewsAPI key → https://newsapi.org/register
- [ ] Groq API key → https://console.groq.com/keys
- [ ] GitHub Personal Access Token → https://github.com/settings/tokens
- [ ] Reddit API credentials → https://www.reddit.com/prefs/apps
- [ ] Add all to `backend/.env`

**Verify:**
```bash
# Run a quick test script that pings each API
python scripts/verify_apis.py
# Output: WeatherAPI ✓, NewsAPI ✓, Groq ✓, GitHub ✓, Reddit ✓
```

---

## Phase 1: Database

### 1.1 Create Tables
- [ ] `users` table with RLS policies
- [ ] `user_preferences` table
- [ ] `user_interests` table (watchlist)
- [ ] `briefing_schedules` table
- [ ] `briefings` table
- [ ] `chat_history` table
- [ ] `preference_history` table

**Verify:**
```bash
# Run migration against Supabase
supabase db push
# Check all 7 tables exist in Supabase dashboard
# Run: SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
# → shows all 7 tables
```

### 1.2 Row-Level Security (RLS)
- [ ] Enable RLS on all tables
- [ ] Policy: users can only read/write their own rows
- [ ] Policy: service role can access all rows (for briefing generation)

**Verify:**
```bash
# Create a test user via Supabase Auth
# Try to read another user's data with anon key → should return empty
# Try to read own data → should return data
```

### 1.3 Database Helper Functions
- [ ] Create `backend/db/client.py` — Supabase client initialization
- [ ] Create `backend/db/users.py` — CRUD for users
- [ ] Create `backend/db/preferences.py` — CRUD for preferences + history logging
- [ ] Create `backend/db/interests.py` — CRUD for watchlist items
- [ ] Create `backend/db/schedules.py` — CRUD for schedules
- [ ] Create `backend/db/briefings.py` — CRUD for briefings
- [ ] Create `backend/db/chat.py` — CRUD for chat history

**Verify:**
```bash
pytest tests/unit/test_db.py -v
# All CRUD operations pass: create, read, update, delete for each table
# Preference history auto-logged on every preference change
```

---

## Phase 2: Authentication

### 2.1 Backend Auth
- [ ] Create `backend/auth/middleware.py` — JWT verification middleware
- [ ] Create `backend/auth/routes.py` — login callback, token refresh, logout
- [ ] Protect all API routes with auth middleware (except /health, /auth/*)

**Verify:**
```bash
# Call protected endpoint without token → 401 Unauthorized
# Call with valid token → 200 OK
# Call with expired token → 401 Unauthorized
# Call /health without token → 200 OK
pytest tests/unit/test_auth.py -v
```

### 2.2 Frontend Auth
- [ ] Create auth context provider
- [ ] Create login page with Google OAuth button + Magic Link input
- [ ] Handle OAuth callback redirect
- [ ] Store session token securely (httpOnly cookie or Supabase client)
- [ ] Create auth guard — redirect unauthenticated users to login
- [ ] Create logout functionality

**Verify:**
```
# Manual test:
# 1. Open app → redirected to login
# 2. Click Google login → OAuth flow completes → redirected to app
# 3. Refresh page → still logged in (session persists)
# 4. Click logout → redirected to login
# 5. Try accessing /briefing directly → redirected to login
```

---

## Phase 3: Onboarding

### 3.1 Backend — Onboarding API
- [ ] `POST /api/v1/onboarding/complete` — accepts user type, topics, sources, interests, schedule
- [ ] Creates entries in: user_preferences, user_interests, briefing_schedules
- [ ] Logs initial preferences in preference_history
- [ ] Returns success with user profile

**Verify:**
```bash
pytest tests/integration/test_onboarding.py -v
# Send complete onboarding payload → all tables populated correctly
# Send partial payload (skip optional fields) → defaults applied
# Send invalid payload → 422 validation error with clear message
```

### 3.2 Frontend — Onboarding Screens
- [ ] Step 1: User type selection (card grid, multi-select)
- [ ] Step 2: Starter pack display (pre-selected based on user type, toggleable)
- [ ] Step 3: Watchlist input (optional, skip button)
- [ ] Step 4: Schedule picker (time, frequency, depth, timezone)
- [ ] Progress indicator (step 1 of 4, step 2 of 4, etc.)
- [ ] "Back" button on each step
- [ ] Final submit → calls onboarding API → redirects to home

**Verify:**
```
# Manual test:
# 1. Complete all 4 steps → lands on home page
# 2. Check Supabase → all tables have correct data
# 3. Go back on step 3 → step 2 data preserved
# 4. Skip step 3 → still works
# 5. Pick multiple user types → starter pack combines sources
# Playwright E2E:
npm run test:e2e -- --grep "onboarding"
```

### 3.3 Starter Pack Logic
- [ ] Create `backend/config/starter_packs.py` — defines default topics + sources per user type
- [ ] AI/Tech: github, hackernews, reddit, arxiv, producthunt, techcrunch, huggingface
- [ ] General: weather, google_news, newsapi, reddit_trending, currency
- [ ] Trader: yahoo_finance, moneycontrol, economic_times, currency_gold, reddit_finance
- [ ] Combined packs when user picks multiple types (deduplicated)

**Verify:**
```bash
pytest tests/unit/test_starter_packs.py -v
# Single type → correct sources
# Multiple types → combined, no duplicates
# Unknown type → returns empty with error
```

---

## Phase 4: Data Source Integrations

### 4.1 Create Source Fetchers
Each fetcher: takes parameters, returns standardized format `{title, summary, url, source, timestamp, raw}`

- [ ] `backend/sources/weather.py` — WeatherAPI
- [ ] `backend/sources/news_google.py` — Google News RSS
- [ ] `backend/sources/news_api.py` — NewsAPI.org
- [ ] `backend/sources/reddit.py` — Reddit API (configurable subreddits)
- [ ] `backend/sources/github_trending.py` — GitHub API
- [ ] `backend/sources/hackernews.py` — HN Algolia API
- [ ] `backend/sources/arxiv.py` — Arxiv API
- [ ] `backend/sources/producthunt.py` — Product Hunt API
- [ ] `backend/sources/huggingface.py` — HuggingFace API
- [ ] `backend/sources/yahoo_finance.py` — yfinance
- [ ] `backend/sources/rss_feed.py` — Generic RSS fetcher (MoneyControl, Economic Times, TechCrunch)
- [ ] `backend/sources/currency.py` — ExchangeRate API

**Verify (per source):**
```bash
pytest tests/integration/test_sources.py -v
# Each source:
# 1. Returns data in standardized format
# 2. Handles API errors gracefully (returns empty, not crash)
# 3. Handles rate limits (backs off, retries)
# 4. Handles empty responses
# 5. Respects timeout (5s max per source)
```

### 4.2 Source Registry
- [ ] Create `backend/sources/registry.py` — maps source names to fetcher functions
- [ ] `get_sources_for_user(preferences)` → returns list of fetcher functions to call
- [ ] Parallel execution of all fetchers using `asyncio.gather`

**Verify:**
```bash
pytest tests/unit/test_registry.py -v
# AI/Tech user → returns 7 fetchers
# General user → returns 5 fetchers
# Trader user → returns 5 fetchers
# Unknown source name → skipped with warning log
# All fetchers run in parallel, total time ≈ slowest single fetcher (not sum)
```

### 4.3 Retry & Error Handling
- [ ] Create `backend/sources/retry.py` — retry wrapper with exponential backoff
- [ ] Max 3 retries, 1s/2s/4s delays
- [ ] If all retries fail → return empty result, log error, don't crash pipeline

**Verify:**
```bash
pytest tests/unit/test_retry.py -v
# Mock API failure → retries 3 times → returns empty
# Mock intermittent failure → succeeds on retry 2
# Mock timeout → retries and handles
```

---

## Phase 5: Noise Filtering Pipeline

### 5.1 Deduplication
- [ ] Create `backend/filters/dedup.py`
- [ ] Compare titles using fuzzy matching (similarity > 0.85 = duplicate)
- [ ] Merge duplicates: keep best summary, list all source URLs, count sources

**Verify:**
```bash
pytest tests/unit/test_dedup.py -v
# "Apple launches iPhone 16" + "Apple unveils new iPhone 16" → merged
# "Apple launches iPhone" + "Google launches Pixel" → not merged
# 5 duplicates → 1 entry with "5 sources agree"
```

### 5.2 Relevance Scoring
- [ ] Create `backend/filters/relevance.py`
- [ ] LLM scores each item 0-10 against user's topics + interests
- [ ] Threshold: 6+ passes, below 6 filtered out
- [ ] Batch scoring (send multiple items in one LLM call for efficiency)

**Verify:**
```bash
pytest tests/unit/test_relevance.py -v
# AI user + "New GPT model" → score 9+ → passes
# AI user + "Cricket match results" → score < 6 → filtered
# Empty topics → all items pass (no filter)
```

### 5.3 Quality Filtering
- [ ] Create `backend/filters/quality.py`
- [ ] Reddit: minimum upvote threshold per subreddit size
- [ ] News: exclude clickbait (LLM detection)
- [ ] All: minimum content length, reputable source check

**Verify:**
```bash
pytest tests/unit/test_quality.py -v
# Reddit post with 5 upvotes → filtered
# Reddit post with 500 upvotes → passes
# Clickbait headline → filtered
# Legitimate headline → passes
```

### 5.4 Impact Scoring
- [ ] Create `backend/filters/impact.py`
- [ ] LLM assigns: HIGH (affects many), MEDIUM (niche but significant), LOW (minor)
- [ ] Sort items by impact within each section

**Verify:**
```bash
pytest tests/unit/test_impact.py -v
# "RBI changes interest rate" → HIGH
# "New VS Code extension" → LOW
# Items sorted: HIGH first, then MEDIUM, then LOW
```

### 5.5 Filter Pipeline Orchestrator
- [ ] Create `backend/filters/pipeline.py`
- [ ] Chains: dedup → relevance → quality → impact → sort → limit
- [ ] Configurable limits: 15-20 items (detailed), 8-10 items (headlines)

**Verify:**
```bash
pytest tests/integration/test_filter_pipeline.py -v
# 50 raw items → pipeline → 12 filtered, scored, sorted items
# All duplicates removed
# All low-relevance items removed
# Items sorted by impact
# Count within limits
# Pipeline handles empty input → returns empty (no crash)
```

---

## Phase 6: Briefing Engine

### 6.1 LLM Summarization
- [ ] Create `backend/briefing/summarizer.py`
- [ ] Summarize items per section (batch)
- [ ] Two modes: "headlines" (1 line each) vs "detailed" (2-3 sentences each)
- [ ] Generate "Top Story" — highest impact item with extended summary
- [ ] Generate cross-domain insights if applicable

**Verify:**
```bash
pytest tests/unit/test_summarizer.py -v
# Headlines mode → each item ≤ 1 sentence
# Detailed mode → each item 2-3 sentences
# Top story → has extended summary
# LLM failure → fallback to raw titles (no crash)
```

### 6.2 Briefing Generator
- [ ] Create `backend/briefing/generator.py`
- [ ] Takes user preferences + filtered items
- [ ] Organizes into sections based on user's topics
- [ ] Orders sections by user's priority (user type determines default order)
- [ ] Generates final briefing: structured JSON + rendered HTML/markdown
- [ ] Stores in briefings table

**Verify:**
```bash
pytest tests/integration/test_generator.py -v
# AI user → sections: Top Story, AI & Tech, Research, Community Buzz
# Trader → sections: Top Story, Markets, Watchlist, Economic News
# General → sections: Top Story, Headlines, Weather, Trending
# Briefing stored in DB with correct user_id, sections, content
# item_count and alert_count match actual content
```

### 6.3 Scheduler
- [ ] Create `backend/briefing/scheduler.py`
- [ ] On app startup: load all enabled schedules from DB
- [ ] APScheduler cron job per user per scheduled time
- [ ] On trigger: fetch → filter → summarize → generate → store → notify
- [ ] Handle new schedules (add job), updated schedules (reschedule), deleted schedules (remove job)
- [ ] Handle timezone correctly

**Verify:**
```bash
pytest tests/integration/test_scheduler.py -v
# Create schedule for 1 minute from now → briefing generated on time
# Disable schedule → job removed, no briefing generated
# Change time → job rescheduled
# Multiple users at same time → all get briefings (parallel)
# Invalid timezone → rejected with error
```

---

## Phase 7: Backend API

### 7.1 API Routes
- [ ] `GET /health` — health check (no auth)
- [ ] `POST /api/v1/auth/callback` — OAuth callback
- [ ] `POST /api/v1/auth/magic-link` — send magic link
- [ ] `POST /api/v1/auth/refresh` — refresh token
- [ ] `POST /api/v1/auth/logout` — logout
- [ ] `GET /api/v1/user/profile` — get user profile
- [ ] `POST /api/v1/onboarding/complete` — complete onboarding
- [ ] `GET /api/v1/preferences` — get current preferences
- [ ] `PUT /api/v1/preferences` — update preferences (logs history)
- [ ] `GET /api/v1/interests` — get watchlist
- [ ] `POST /api/v1/interests` — add watchlist item (logs history)
- [ ] `DELETE /api/v1/interests/{id}` — remove watchlist item (logs history)
- [ ] `GET /api/v1/schedule` — get schedule
- [ ] `PUT /api/v1/schedule` — update schedule
- [ ] `GET /api/v1/briefings` — list briefings (paginated)
- [ ] `GET /api/v1/briefings/{id}` — get single briefing
- [ ] `PUT /api/v1/briefings/{id}/read` — mark as read
- [ ] `POST /api/v1/chat` — send chat message, get response
- [ ] `GET /api/v1/chat/history` — get chat history (paginated)
- [ ] `DELETE /api/v1/user` — delete account + all data

### 7.2 Input Validation
- [ ] Pydantic models for every request/response
- [ ] Create `backend/schemas/` — all request/response models
- [ ] Validate all inputs: types, lengths, allowed values

### 7.3 Rate Limiting
- [ ] Add rate limiting middleware: 60 requests/min per user
- [ ] Chat endpoint: 20 requests/min per user (LLM costs)
- [ ] Return 429 Too Many Requests when exceeded

### 7.4 Error Handling
- [ ] Global exception handler
- [ ] Consistent error response format: `{error: string, detail: string, status: int}`
- [ ] Never leak stack traces or internal details to client

**Verify:**
```bash
pytest tests/integration/test_api.py -v
# Every endpoint:
# 1. Returns correct status code (200, 201, 401, 404, 422, 429)
# 2. Returns correct response schema
# 3. Rejects invalid input with 422
# 4. Rejects unauthenticated requests with 401
# 5. Rate limit works (send 61 requests → 429 on 61st)
# 6. Delete account removes ALL user data from ALL tables
```

---

## Phase 8: Chat Feature

### 8.1 Chat Engine
- [ ] Create `backend/chat/engine.py`
- [ ] Takes user query + user preferences + recent briefing context
- [ ] Searches relevant sources based on query
- [ ] LLM generates answer with source citations
- [ ] Returns: `{response: string, sources: [{title, url, source}]}`

**Verify:**
```bash
pytest tests/integration/test_chat.py -v
# "What's happening with Llama 4?" → response mentions Llama 4 + source links
# "Compare Nifty this week" → response with market data + sources
# Random gibberish → polite "I couldn't find relevant information" response
# Empty query → 422 validation error
# Response always includes at least 1 source link (when available)
```

### 8.2 Chat Context
- [ ] Chat knows user's preferences (topics, interests)
- [ ] Chat can reference today's briefing content
- [ ] Chat maintains conversation context within a session (follow-up questions work)

**Verify:**
```bash
# "Tell me about today's top story" → references actual top story from briefing
# "Tell me more" (follow-up) → continues previous context
# New chat session → fresh context
```

---

## Phase 9: Frontend — All Screens

### 9.1 Layout & Navigation
- [ ] Create mobile-first layout component
- [ ] Bottom tab bar: Briefing, Chat, History, Settings (icons + labels)
- [ ] Active tab indicator
- [ ] Top bar: app logo + user avatar
- [ ] Dark mode support (system default + manual toggle)

**Verify:**
```
# Mobile (375px): bottom nav visible, single column, no horizontal scroll
# Desktop (1440px): responsive layout, content centered
# Tab switching works without page reload
# Dark mode toggles all components correctly
```

### 9.2 Landing Page
- [ ] Hero section: app name + pitch + "Get Started" button
- [ ] 3 value propositions
- [ ] Sample briefing preview (static mockup)
- [ ] Mobile responsive

**Verify:**
```
# Page loads < 2 seconds
# "Get Started" → redirects to login
# Already logged in + visit landing → redirect to home
```

### 9.3 Login Page
- [ ] Google OAuth button (styled)
- [ ] Magic link email input + send button
- [ ] Loading states for both
- [ ] Error messages displayed clearly

**Verify:**
```
# Google login → completes OAuth → redirect to onboarding (first time) or home (returning)
# Magic link → "Check your email" message shown
# Invalid email → validation error shown
```

### 9.4 Onboarding Screens
- [ ] Step 1: User type cards (multi-select, animated)
- [ ] Step 2: Starter pack toggles
- [ ] Step 3: Watchlist input (autocomplete for stocks, repos)
- [ ] Step 4: Schedule picker
- [ ] Progress bar
- [ ] Back/Next buttons
- [ ] Final submission + loading state

**Verify:**
```
# Complete flow → lands on home with briefing
# Back button preserves previous selections
# Skip optional step → works
# Mobile: all steps usable with thumb, no tiny targets
npm run test:e2e -- --grep "onboarding"
```

### 9.5 Briefing Screen (Home)
- [ ] Today's date header
- [ ] Top Story card (prominent, larger)
- [ ] Section cards grouped by topic
- [ ] Each item: title, summary, impact badge, source, tap to open link
- [ ] Pull-to-refresh
- [ ] Loading skeleton while briefing loads
- [ ] Empty state: "Your briefing is being prepared..."
- [ ] Previous briefings link

**Verify:**
```
# Briefing displays all sections from API response
# Tap on item → opens source URL in new tab
# Pull down → refreshes briefing
# No briefing yet → shows "preparing" message
# Loading state → skeleton animation (not blank screen)
# Impact badges: HIGH (red), MEDIUM (yellow), LOW (gray)
npm run test:e2e -- --grep "briefing"
```

### 9.6 Chat Screen
- [ ] Chat message list (scrollable)
- [ ] User message bubble (right aligned)
- [ ] App response bubble (left aligned) with markdown rendering
- [ ] Source links displayed as clickable cards below response
- [ ] Input bar at bottom with send button
- [ ] Loading indicator while waiting for response
- [ ] Auto-scroll to latest message

**Verify:**
```
# Type message → send → response appears with sources
# Source links open in new tab
# Long response renders markdown correctly
# Chat history loads on tab switch
# Loading spinner while waiting
# Empty state: "Ask me anything about today's news"
npm run test:e2e -- --grep "chat"
```

### 9.7 History Screen
- [ ] List of past briefings sorted by date (newest first)
- [ ] Each card: date, top story title, item count, alert count
- [ ] Tap → opens full briefing
- [ ] Infinite scroll or pagination
- [ ] Empty state for new users

**Verify:**
```
# Shows all past briefings
# Tap opens correct briefing content
# Scroll loads more briefings
# New user → "No briefings yet" message
npm run test:e2e -- --grep "history"
```

### 9.8 Settings Screen
- [ ] Profile section (name, email, avatar — read only from OAuth)
- [ ] Interests section (edit topics, sources — toggles)
- [ ] Watchlist section (add/remove items)
- [ ] Schedule section (time picker, frequency, depth, timezone)
- [ ] Location input
- [ ] Dark mode toggle
- [ ] Delete account button (with confirmation dialog)

**Verify:**
```
# Change topic → saved to DB + preference history logged
# Change schedule → next briefing at new time
# Add watchlist item → appears in next briefing
# Delete account → confirmation → all data deleted → redirect to landing
npm run test:e2e -- --grep "settings"
```

---

## Phase 10: PWA Setup

### 10.1 Service Worker
- [ ] Configure Serwist for Next.js
- [ ] Cache last briefing for offline reading
- [ ] Cache static assets (fonts, icons, CSS)
- [ ] Update prompt when new version available

### 10.2 Web App Manifest
- [ ] App name, short name, description
- [ ] Icons (192x192, 512x512)
- [ ] Theme color, background color
- [ ] Display: standalone
- [ ] Start URL: /briefing

### 10.3 Push Notifications
- [ ] Request notification permission on onboarding
- [ ] Send push when briefing is ready
- [ ] Tap notification → opens briefing

### 10.4 Install Prompt
- [ ] Custom "Add to Home Screen" banner for mobile users
- [ ] Show after 2nd visit (not first — avoid annoying new users)

**Verify:**
```
# Mobile Chrome: "Add to Home Screen" prompt appears
# Install → app icon on home screen → opens in standalone mode
# Turn off WiFi → last briefing still readable
# Receive push notification → tap → opens correct briefing
# Lighthouse PWA audit → score 90+
```

---

## Phase 11: Testing (Full Suite)

### 11.1 Backend Unit Tests
- [ ] All DB helpers (CRUD operations)
- [ ] All source fetchers (mocked API responses)
- [ ] All filters (dedup, relevance, quality, impact)
- [ ] Summarizer (mocked LLM)
- [ ] Briefing generator
- [ ] Starter pack logic
- [ ] Auth middleware
- [ ] Input validation schemas

**Verify:**
```bash
pytest tests/unit/ -v --cov=backend --cov-report=term-missing
# All pass, coverage ≥ 80%
```

### 11.2 Backend Integration Tests
- [ ] All API endpoints (with test DB)
- [ ] Onboarding flow end-to-end
- [ ] Briefing generation pipeline
- [ ] Chat engine with real LLM
- [ ] Scheduler creates and triggers jobs
- [ ] Preference update logs history

**Verify:**
```bash
pytest tests/integration/ -v
# All pass against Supabase test project
```

### 11.3 Frontend Component Tests
- [ ] All shared components (cards, buttons, tabs, inputs)
- [ ] Onboarding step components
- [ ] Briefing section components
- [ ] Chat message components
- [ ] Settings form components

**Verify:**
```bash
cd frontend && npm run test -- --coverage
# All pass, coverage ≥ 80%
```

### 11.4 API Contract Tests
- [ ] Frontend zod schemas match backend pydantic schemas
- [ ] Every API call in frontend uses correct request/response types

**Verify:**
```bash
npm run test:contracts
# All schemas match
```

### 11.5 E2E Tests (Playwright)
- [ ] Onboarding complete flow
- [ ] Login → see briefing → tap item → opens link
- [ ] Chat → ask question → get response with sources
- [ ] Settings → change preference → next briefing reflects change
- [ ] History → browse past briefings
- [ ] Offline → last briefing visible
- [ ] Delete account → all data gone

**Verify:**
```bash
cd frontend && npm run test:e2e
# All flows pass on Chrome, Firefox, Safari (mobile viewport)
```

### 11.6 Load Tests
- [ ] 100 concurrent briefing generations
- [ ] 500 concurrent API requests
- [ ] Scheduler handling 1000 users at same time slot

**Verify:**
```bash
locust -f tests/load/locustfile.py --headless -u 500 -r 50 -t 60s
# 95th percentile response time < 2 seconds
# 0 failures
```

### 11.7 LLM Output Tests
- [ ] Summaries are relevant to input
- [ ] No hallucinated URLs
- [ ] Summaries stay within length limits
- [ ] Chat responses include source citations

**Verify:**
```bash
pytest tests/llm/ -v
# All quality assertions pass
```

---

## Phase 12: Security Hardening

### 12.1 Security Headers
- [ ] Add all headers from PRD section 13.5 to Next.js config
- [ ] Add CORS whitelist to FastAPI

**Verify:**
```bash
# Check headers with curl:
curl -I https://your-app.vercel.app
# All security headers present
```

### 12.2 Secret Scanning
- [ ] Add pre-commit hook to block secrets
- [ ] Enable GitHub secret scanning on repo
- [ ] Verify no secrets in codebase

**Verify:**
```bash
# Run bandit on backend
bandit -r backend/ -ll
# 0 HIGH/CRITICAL findings

# Check for hardcoded secrets
grep -r "sk-" backend/ frontend/ --include="*.py" --include="*.ts" --include="*.tsx"
# 0 matches
```

### 12.3 Dependency Audit
- [ ] Run `pip audit` on Python dependencies
- [ ] Run `npm audit` on Node dependencies
- [ ] Fix all HIGH/CRITICAL vulnerabilities

**Verify:**
```bash
cd backend && pip audit
cd frontend && npm audit
# 0 high/critical vulnerabilities
```

### 12.4 RLS Verification
- [ ] Test that User A cannot read User B's data
- [ ] Test that User A cannot modify User B's data
- [ ] Test that unauthenticated requests get no data

**Verify:**
```bash
pytest tests/security/test_rls.py -v
# All cross-user access attempts blocked
```

---

## Phase 13: CI/CD Pipeline

### 13.1 GitHub Actions — PR Pipeline
- [ ] Create `.github/workflows/pr.yml`
- [ ] Stage 1 (parallel): ruff, eslint, mypy, tsc, bandit, npm audit
- [ ] Stage 2 (parallel): pytest unit, jest, contract tests
- [ ] Stage 3: pytest integration
- [ ] Stage 4: next build + fastapi startup check
- [ ] Stage 5: playwright E2E
- [ ] Block merge if any stage fails

**Verify:**
```
# Push a PR with a lint error → pipeline fails at stage 1
# Push a PR with failing test → pipeline fails at stage 2
# Push a clean PR → all stages pass → merge allowed
```

### 13.2 GitHub Actions — Deploy Pipeline
- [ ] Create `.github/workflows/deploy.yml`
- [ ] Trigger: merge to `main`
- [ ] Auto-deploy frontend to Vercel
- [ ] Auto-deploy backend to Railway
- [ ] Run Supabase migrations if changed

**Verify:**
```
# Merge PR to main → both Vercel and Railway deploy automatically
# Visit production URL → app works
# Check Railway logs → backend healthy
# Check Vercel dashboard → frontend deployed
```

### 13.3 Environment Secrets
- [ ] Add all API keys to GitHub Secrets
- [ ] Add all API keys to Vercel environment variables
- [ ] Add all API keys to Railway environment variables
- [ ] Separate staging vs production secrets

**Verify:**
```
# Production app can fetch weather, news, market data
# No secrets visible in build logs
```

---

## Phase 14: Deployment

### 14.1 Staging Deploy
- [ ] Deploy backend to Railway (staging)
- [ ] Deploy frontend to Vercel (preview)
- [ ] Point frontend to staging backend URL
- [ ] Run full E2E suite against staging

**Verify:**
```
# Complete user flow on staging:
# 1. Sign up → onboard → see first briefing
# 2. Chat → get answers
# 3. Change preferences → see updated briefing
# 4. Check history → past briefings visible
# All on mobile device (real phone, not just emulator)
```

### 14.2 Production Deploy
- [ ] Deploy backend to Railway (production)
- [ ] Deploy frontend to Vercel (production)
- [ ] Configure production Supabase
- [ ] DNS setup (if custom domain)
- [ ] Verify all API keys are production keys

**Verify:**
```
# Same flow as staging verification
# Lighthouse audit:
#   Performance: 90+
#   Accessibility: 90+
#   Best Practices: 90+
#   SEO: 90+
#   PWA: 90+
# App installable on mobile
# Push notification works
```

### 14.3 Post-Launch Monitoring
- [ ] Verify Supabase dashboard shows user signups
- [ ] Verify Railway logs show healthy scheduler
- [ ] Verify Vercel analytics show page views
- [ ] Set up uptime monitoring (e.g., UptimeRobot — free)

**Verify:**
```
# Sign up as real user
# Wait for scheduled briefing → arrives on time
# Use chat → works
# Check all monitoring dashboards → green
```

---

## Phase Summary

| Phase | What | Depends On |
|-------|------|-----------|
| 0 | Project setup + environment | Nothing |
| 1 | Database tables + helpers | Phase 0 |
| 2 | Authentication | Phase 0, 1 |
| 3 | Onboarding | Phase 1, 2 |
| 4 | Data source integrations | Phase 0 |
| 5 | Noise filtering pipeline | Phase 4 |
| 6 | Briefing engine | Phase 1, 4, 5 |
| 7 | Backend API (all routes) | Phase 1, 2, 3, 6 |
| 8 | Chat feature | Phase 4, 7 |
| 9 | Frontend (all screens) | Phase 7 |
| 10 | PWA setup | Phase 9 |
| 11 | Full test suite | Phase 1-10 |
| 12 | Security hardening | Phase 1-10 |
| 13 | CI/CD pipeline | Phase 11, 12 |
| 14 | Deployment | Phase 13 |

**Parallel work possible:**
- Phase 4 (data sources) can run parallel with Phase 2-3 (auth + onboarding)
- Phase 9 (frontend) can start as soon as Phase 7 API routes are defined (mock data first)
- Phase 11-12 (testing + security) can overlap
