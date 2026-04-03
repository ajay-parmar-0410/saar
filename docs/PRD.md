# PLOS — Product Requirements Document

> **Version:** 1.0
> **Date:** April 3, 2026
> **Status:** Draft

---

## 1. Problem Statement

The world is changing fast. Users open 3-4 apps every morning — weather, stocks, news, Reddit — and still miss what matters. Information overload is real:

- Too many sources, too much noise
- No single app filters information **per user's actual needs**
- Generic news apps show the same feed to everyone
- Users waste 30+ minutes daily just catching up

**The noise-to-signal ratio is broken.** Users need a personal filter — not more content.

---

## 2. Solution

**PLOS** is a personalized daily briefing app that delivers only what matters to you.

- Pick your interests, sources, and schedule
- Get a clean, filtered briefing at your chosen time
- Ask follow-up questions in chat with source links
- Every piece of information passes a relevance + quality filter before reaching you

**One app. Your world. No noise.**

---

## 3. User Personas (MVP)

### Persona 1: AI / Tech Follower

| Attribute | Detail |
|-----------|--------|
| **Who** | Developer, AI enthusiast, tech professional |
| **Goal** | Stay on top of AI breakthroughs, new tools, trending repos, research |
| **Pain** | Information scattered across GitHub, HN, Reddit, arxiv, Twitter |
| **Briefing** | Top AI story, new papers, trending repos, product launches, community buzz |

**Data Sources:**

| Source | API | Cost | What It Provides |
|--------|-----|------|-----------------|
| GitHub Trending | GitHub REST API | Free | Trending AI/tech repos, stars, descriptions |
| Hacker News | HN Algolia API | Free | Top stories, discussions, launches |
| Reddit | Reddit API | Free | r/MachineLearning, r/LocalLLaMA, r/technology |
| Arxiv | Arxiv API | Free | Latest AI/ML research papers |
| Product Hunt | PH API | Free | New tool/product launches |
| TechCrunch | RSS Feed | Free | Funding news, product announcements |
| HuggingFace | HF API | Free | New models, trending spaces |

### Persona 2: General / Casual User

| Attribute | Detail |
|-----------|--------|
| **Who** | Anyone who wants a quick daily catch-up |
| **Goal** | Know what's happening in the world in 2 minutes |
| **Pain** | Too many news apps, notifications, clickbait |
| **Briefing** | Top headlines, weather, currency rates, trending topics |

**Data Sources:**

| Source | API | Cost | What It Provides |
|--------|-----|------|-----------------|
| Weather | WeatherAPI | Free tier | Temperature, condition, forecast |
| Google News | Google News RSS | Free | Top headlines by country/topic |
| NewsAPI | newsapi.org | Free (100 req/day) | Headlines from multiple outlets |
| Reddit Trending | Reddit API | Free | What's viral today |
| Currency Rates | ExchangeRate API | Free | USD/INR, EUR/INR etc. |

### Persona 3: Stock Trader (Indian Market)

| Attribute | Detail |
|-----------|--------|
| **Who** | Retail investor, trader, finance professional |
| **Goal** | Pre-market prep, track watchlist, catch market-moving news |
| **Pain** | MoneyControl is noisy, multiple apps for stocks + news + alerts |
| **Briefing** | Index movement, watchlist performance, market news, economic policy updates |

**Data Sources:**

| Source | API | Cost | What It Provides |
|--------|-----|------|-----------------|
| NSE/BSE Data | Yahoo Finance API / yfinance | Free | Nifty, Sensex, individual stocks |
| MoneyControl | RSS Feed | Free | Market news, earnings, IPOs |
| Economic Times | RSS Feed | Free | Economy, policy, RBI updates |
| Currency/Gold | ExchangeRate API / Gold API | Free | USD/INR, gold price |
| Reddit | Reddit API | Free | r/IndianStreetBets, r/IndianStockMarket |

---

## 4. Core Features (MVP)

### 4.1 Smart Onboarding

- **Step 1:** "What describes you best?" — pick user type cards (can pick multiple)
- **Step 2:** Suggest a starter pack of topics + sources based on selection
- **Step 3:** Optionally add specific watchlist items (stocks, repos, subreddits, keywords)
- **Step 4:** Set briefing schedule (time, frequency, depth, timezone)
- **Goal:** User gets value in under 60 seconds

### 4.2 Personalized Daily Briefing

- Generated at user's scheduled time
- Newsletter format (clean, scannable, mobile-optimized)
- Sections ordered by user's priorities
- **Top Story** always first — highest impact item across all sources
- Each item shows: title, 1-2 line summary, impact level, source link
- 2-3 minute read maximum
- Previous briefings accessible from history

### 4.3 Noise Filtering Pipeline

Every piece of content passes through before reaching the user:

```
Raw data from APIs
    |
    v
Deduplication (same story from multiple sources)
    |
    v
Relevance scoring (does it match user's interests?)
    |
    v
Quality filtering (minimum upvotes, reputable source, not clickbait)
    |
    v
Impact scoring (major event vs minor update)
    |
    v
LLM ranking + summarization
    |
    v
Final briefing (only high-signal items)
```

**Reddit-specific filtering:**
- Only top posts by upvotes from curated subreddits
- Filter by time window (last 24h)
- Minimum upvote threshold per subreddit
- LLM filters out meme/low-quality posts

**This filtering applies to ALL sources, not just Reddit.**

### 4.4 Configurable Schedule

- User picks time(s): "7:00 AM", "7:00 AM + 6:00 PM", or custom
- User picks timezone
- User picks depth: "Headlines only" vs "Detailed summaries"
- Can pause/resume without losing preferences
- Can change anytime from settings

### 4.5 Chat (Ask Anything)

- Conversational interface
- User asks: "What's happening with RBI policy?"
- App responds with summarized answer + source article links
- Context-aware: knows user's interests, can reference today's or past briefings
- Example interactions:
  - "Summarize the Llama 4 paper"
  - "Compare Nifty performance this week vs last"
  - "Any new AI tools launched today?"
  - "Explain today's market drop"

### 4.6 Briefing History

- All past briefings stored and accessible
- Browse by date
- Each entry shows: date, top story, item count, alert count
- Click to open full briefing

### 4.7 Settings

- Update user type, topics, sources anytime
- Manage watchlist (add/remove stocks, repos, keywords)
- Change schedule, depth, timezone
- Update location (for weather)
- Delete account

---

## 5. User Flows

### 5.1 Onboarding Flow

```
Open app (first time)
    |
    v
Landing page --> "Get Started"
    |
    v
Login (Google OAuth or Magic Link)
    |
    v
Step 1: Pick user type(s)
    |
    v
Step 2: Review suggested starter pack (toggle on/off)
    |
    v
Step 3: Add watchlist items (optional, can skip)
    |
    v
Step 4: Set schedule + depth + timezone
    |
    v
"Your first briefing is being prepared..."
    |
    v
Redirect to Home (briefing tab)
```

### 5.2 Daily Briefing Flow (System)

```
Cron triggers at user's scheduled time
    |
    v
Load user preferences (topics, sources, watchlist, depth)
    |
    v
Fetch data from user's sources (parallel)
    |
    v
Noise filtering pipeline (dedup, relevance, quality, impact)
    |
    v
LLM summarization + ranking
    |
    v
Generate personalized briefing
    |
    v
Store in database
    |
    v
Push notification: "Your briefing is ready"
    |
    v
User opens app --> sees briefing
```

### 5.3 Chat Flow

```
User types question in chat tab
    |
    v
Identify intent (news lookup, comparison, explanation, deep dive)
    |
    v
Search relevant sources based on user's question + their interests
    |
    v
LLM summarizes findings
    |
    v
Return answer + source links
    |
    v
User can ask follow-ups (context preserved)
```

### 5.4 Preference Update Flow

```
User goes to Settings
    |
    v
Changes topic / source / watchlist item
    |
    v
Current preferences updated
    |
    v
Change logged in preference_history table
    |
    v
Next briefing uses new preferences
```

---

## 6. Screens (MVP)

**Total: 7 screens**

### Screen 1: Landing Page

- App name + one-line pitch
- 3 bullet points explaining value
- Preview/demo of a sample briefing
- "Get Started" button

### Screen 2: Login

- Google OAuth button
- Email magic link input
- No passwords, no forms

### Screen 3: Onboarding (4 steps)

- Step 1: User type selection (cards)
- Step 2: Starter pack review (toggles)
- Step 3: Watchlist items (optional)
- Step 4: Schedule configuration

### Screen 4: Home — Briefing Tab

- Today's date
- Top Story card (highest impact)
- Section cards based on user's interests
- Each item: title, summary, impact badge, source link
- Previous briefings link at bottom
- Pull-to-refresh on mobile

### Screen 5: Home — Chat Tab

- Chat interface
- User message bubbles
- App response with formatted answer + source links
- "Ask anything..." input at bottom

### Screen 6: Briefing History

- List of past briefings by date
- Each entry: date, top story title, item count, alert count
- Click to open full briefing

### Screen 7: Settings

- Profile (name, email, avatar)
- Interest management (user types, topics, sources)
- Watchlist management (add/remove)
- Schedule configuration
- Location
- Delete account

### Mobile Navigation

Bottom tab bar (thumb-friendly, always visible):

```
[ Briefing ] [ Chat ] [ History ] [ Settings ]
```

---

## 7. Data Model

### 7.1 Users

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| email | string | Login identity |
| name | string | Display name |
| avatar_url | string | From OAuth provider |
| user_type | string[] | ["ai_tech", "trader", "general"] |
| created_at | timestamp | Account creation |
| last_active_at | timestamp | Last app open |

### 7.2 User Preferences

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| topics | string[] | ["ai", "markets", "weather"] |
| sources | string[] | ["github", "hackernews", "reddit"] |
| briefing_depth | enum | "headlines" or "detailed" |
| location | string | City for weather + local news |
| updated_at | timestamp | Last preference change |

### 7.3 User Interests (Watchlist)

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| type | string | "stock", "repo", "subreddit", "keyword", "team" |
| value | string | "RELIANCE", "langchain-ai/langchain", "r/LocalLLaMA" |
| added_at | timestamp | When added |

### 7.4 Briefing Schedule

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| times | string[] | ["07:00", "18:00"] |
| timezone | string | "Asia/Kolkata" |
| enabled | boolean | Can pause without deleting |

### 7.5 Briefings

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| content | text | Rendered HTML/markdown briefing |
| sections | jsonb | Structured data per section |
| top_story | string | Headline of top story |
| item_count | int | Total items in briefing |
| alert_count | int | Number of alerts |
| generated_at | timestamp | When created |
| read | boolean | Did user open it |
| read_at | timestamp | When user opened it |

### 7.6 Chat History

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| query | text | User's question |
| response | text | App's answer |
| sources | jsonb | [{title, url, source}] |
| created_at | timestamp | When asked |

### 7.7 Preference History (Changelog)

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| action | enum | "added" or "removed" |
| field | string | "topic", "source", "interest", "schedule" |
| value | string | The actual value changed |
| changed_at | timestamp | When changed |

### 7.8 Relationships

```
User
 |-- has one --> Preferences
 |-- has one --> Schedule
 |-- has many --> Interests (watchlist)
 |-- has many --> Briefings
 |-- has many --> Chat History
 |-- has many --> Preference History
```

### 7.9 Storage Policy

- **Store all briefings permanently** (optimize later at scale)
- **Store all chat history permanently**
- **Store all preference history permanently**
- No raw API responses stored — fetch fresh every time
- No full article content — only links (avoid copyright issues)

---

## 8. Tech Stack

### Backend

| Layer | Technology | Why |
|-------|-----------|-----|
| API Framework | FastAPI (Python) | Async, existing codebase, LangGraph compatible |
| Agent Pipeline | LangGraph | Already built, parallel fetching, easy to extend |
| LLM | Groq (Llama 3.1 8B) | Free tier, fast inference, already integrated |
| Task Scheduler | APScheduler | Lightweight, Python-native, no extra infra for MVP |
| Database | Supabase (PostgreSQL) | Auth + DB + real-time, generous free tier |
| Auth | Supabase Auth | Google OAuth + Magic Link, free |

### Frontend

| Layer | Technology | Why |
|-------|-----------|-----|
| Framework | Next.js (React) | SSR, PWA support, mobile-first |
| Components | shadcn/ui | Full ownership, dark mode, accessible, industry standard |
| Dashboard/Charts | Tremor | Built for data visualization, same Tailwind stack |
| Animations | Magic UI + Motion (Framer Motion) | Premium feel, smooth transitions |
| Feed Animations | AutoAnimate | Zero-config list animations for news feed |
| Styling | Tailwind CSS | Utility-first, mobile-first by default |
| PWA | Serwist (next-pwa) | Service workers, offline support, installable |

### Infrastructure

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend Hosting | Vercel | Free tier, built for Next.js |
| Backend Hosting | Railway | Free tier, easy Python deploy |
| Database | Supabase | Free tier PostgreSQL |
| CI/CD | GitHub Actions | Free for public repos |

---

## 9. Mobile-First Design Constraints

| Constraint | Requirement |
|------------|-------------|
| Layout | Single column, no sidebars on mobile |
| Navigation | Bottom tab bar (Briefing, Chat, History, Settings) |
| Touch targets | Minimum 44x44px for all interactive elements |
| Typography | 16px minimum font size, high contrast |
| Animations | Subtle on mobile, no heavy effects on low-end devices |
| Offline | PWA caches last briefing for offline reading |
| Gestures | Pull-to-refresh, swipe between briefings |
| Performance | Tree-shake aggressively, lazy load non-critical components |
| Bundle size | Target < 200KB initial JS bundle |
| Hover states | Replaced with tap/press states |
| Data tables | Replaced with card-based layouts |
| Modals | Replaced with bottom sheets |
| Images | Lazy loaded, responsive sizes, WebP format |

---

## 10. Noise Filtering Strategy

### Global Rules (All Sources)

1. **Deduplication** — same story from 3 sources = 1 entry with "3 sources agree"
2. **Relevance score** — LLM scores 0-10 against user's topics/interests, threshold: 6+
3. **Quality score** — source reputation, engagement metrics, content length
4. **Impact score** — HIGH (affects many people), MEDIUM (niche but significant), LOW (minor update)
5. **Recency** — prioritize last 24 hours, deprioritize older content
6. **Max items per briefing** — cap at 15-20 items for "detailed", 8-10 for "headlines"

### Reddit-Specific Filtering

- Curated subreddit list per user type (not all of Reddit)
- Minimum upvote threshold: 50+ for niche subs, 200+ for large subs
- Time filter: last 24 hours only
- Exclude: memes, shitposts, questions, low-effort content
- LLM pass: verify post is informational/newsworthy before including

### News-Specific Filtering

- Exclude clickbait (LLM detection)
- Exclude duplicate rewrites of same story
- Prefer primary sources over aggregators
- Exclude opinion pieces unless explicitly followed

---

## 11. Testing Strategy

### 11.1 Test Levels

| Level | What | Tools | Coverage Target |
|-------|------|-------|----------------|
| **Unit Tests** | Individual functions: filters, parsers, scoring, formatters, utils | pytest (backend), Jest (frontend) | 80%+ |
| **Integration Tests** | API endpoints, DB operations, external API calls, auth flow | pytest + httpx + Supabase test DB | All endpoints |
| **Component Tests** | React components in isolation: cards, tabs, chat bubbles | Jest + React Testing Library | All components |
| **API Contract Tests** | Request/response schema validation between frontend and backend | pydantic (backend) + zod (frontend) | All API routes |
| **E2E Tests** | Full user flows: onboarding, briefing view, chat, settings | Playwright | All critical flows |
| **Load Tests** | Concurrent briefing generation, scheduler under load | Locust | 1000 concurrent users |
| **LLM Output Tests** | Summary quality, relevance to user topics, hallucination detection | Custom assertions + LLM-as-judge | All LLM outputs |

### 11.2 What To Test Per Feature

**Onboarding:**
- User type selection saves correctly
- Starter pack populates based on user type
- Schedule saves with correct timezone
- Preferences stored in DB
- Preference history logged

**Briefing Generation:**
- Correct sources fetched per user type
- Noise filter removes low-quality content
- Deduplication works across sources
- LLM summarization produces valid output
- Briefing stored in DB with correct structure
- Item count respects max limits

**Chat:**
- Query processed and response returned
- Source links are valid URLs
- Chat history saved
- Context maintained across follow-ups
- Handles empty/no-result queries gracefully

**Settings:**
- Preference changes update DB
- Preference history logged on every change
- Schedule changes take effect on next briefing
- Delete account removes all user data

**Auth:**
- Google OAuth flow completes
- Magic link sent and validates
- JWT token refresh works
- Expired tokens rejected
- Unauthorized routes protected

### 11.3 Test Commands

```bash
# Backend
pytest tests/unit/                    # Unit tests
pytest tests/integration/             # Integration tests
pytest tests/llm/                     # LLM output tests
locust -f tests/load/locustfile.py    # Load tests

# Frontend
npm run test                          # Jest + RTL
npm run test:e2e                      # Playwright

# All
npm run test:all                      # Everything
```

---

## 12. CI/CD Pipeline

### 12.1 Pipeline Architecture

```
Developer pushes code to GitHub
         |
         v
GitHub Actions triggers automatically
         |
    +-----------+-----------+-----------+
    |           |           |           |
    v           v           v           v
  Lint       Type Check   Unit Tests  Security
  (ruff +    (mypy +      (pytest +   (bandit +
  eslint)    TypeScript)   jest)       Snyk)
    |           |           |           |
    +-----------+-----------+-----------+
                    |
                    v
            Integration Tests
            (Supabase test DB + mocked external APIs)
                    |
                    v
              Build Check
              (Next.js build + FastAPI startup)
                    |
                    v
               E2E Tests
               (Playwright against staging)
                    |
                    v
              All Passed?
              /          \
           Yes            No
            |              |
            v              v
      Deploy to        Block merge
       Staging         Notify dev
            |
            v
      Manual Approval
            |
            v
      Deploy to
      Production
```

### 12.2 Pipeline Stages

**Stage 1: Quality Gates (Parallel)**

| Check | Tool | Fails If |
|-------|------|----------|
| Python lint | ruff | Any lint error |
| JS/TS lint | eslint | Any lint error |
| Python types | mypy | Type errors |
| TypeScript | tsc --noEmit | Type errors |
| Python security | bandit | HIGH/CRITICAL findings |
| Dependency scan | Snyk / Dependabot | Known vulnerabilities |

**Stage 2: Unit + Component Tests (Parallel)**

| Suite | Tool | Fails If |
|-------|------|----------|
| Backend unit tests | pytest tests/unit/ | Any failure or < 80% coverage |
| Frontend component tests | jest | Any failure |
| API contract tests | pydantic + zod | Schema mismatch |

**Stage 3: Integration Tests**

| Suite | Tool | Fails If |
|-------|------|----------|
| API endpoint tests | pytest + httpx | Any failure |
| Database tests | pytest + Supabase test DB | Any failure |
| Auth flow tests | pytest | Any failure |

**Stage 4: Build + E2E**

| Step | What |
|------|------|
| Next.js build | `next build` succeeds |
| FastAPI startup | App starts without errors |
| E2E tests | Playwright runs critical user flows against staging |

**Stage 5: Deploy**

| Environment | When | How |
|-------------|------|-----|
| Staging | All tests pass on PR | Auto-deploy |
| Production | Manual approval after staging | One-click deploy |

### 12.3 Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code |
| `develop` | Integration branch |
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `release/*` | Release preparation |

### 12.4 Deploy Targets

| Service | Platform | Deploy Method |
|---------|----------|--------------|
| Frontend (Next.js) | Vercel | Git push auto-deploy |
| Backend (FastAPI) | Railway | Git push auto-deploy |
| Database | Supabase | Migrations via CLI |

---

## 13. Security

### 13.1 Authentication & Authorization

| Practice | Implementation |
|----------|---------------|
| Auth provider | Supabase Auth (Google OAuth + Magic Link) |
| Token type | JWT with short expiry (1 hour) + refresh tokens (7 days) |
| Session management | Refresh tokens rotated on each use |
| Route protection | All API routes require valid JWT except login/signup |
| Role-based access | Users can only access their own data |
| Account deletion | Hard delete all user data on request (GDPR-style) |

### 13.2 API Security

| Practice | Implementation |
|----------|---------------|
| Rate limiting | Per-user limits on all endpoints (e.g., 60 req/min) |
| CORS | Whitelist only our frontend domain |
| Input validation | pydantic models on every endpoint, reject malformed requests |
| Request size | Limit payload size (1MB max) |
| API versioning | /api/v1/ prefix for future-proofing |

### 13.3 Data Security

| Practice | Implementation |
|----------|---------------|
| Encryption at rest | Supabase default (AES-256) |
| Encryption in transit | HTTPS everywhere (TLS 1.3) |
| No plain text secrets | All secrets in environment variables |
| Database access | Row-Level Security (RLS) in Supabase — users see only their data |
| Backup | Supabase automatic daily backups |

### 13.4 Code Security

| Practice | Implementation |
|----------|---------------|
| SQL injection | Parameterized queries via Supabase client, never raw SQL |
| XSS prevention | React auto-escaping + CSP headers + sanitize user content |
| CSRF protection | Token-based on state-changing endpoints |
| Dependency scanning | Snyk / Dependabot in CI, auto-PRs for vulnerabilities |
| Secret scanning | GitHub secret scanning enabled, pre-commit hook to block secrets |

### 13.5 Security Headers

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

### 13.6 API Key Management

| Rule | Detail |
|------|--------|
| Server-side only | All third-party API keys stay on backend, never exposed to frontend |
| Scoped permissions | Each key has minimum required permissions |
| Rotation | Rotate keys quarterly or immediately if exposed |
| Monitoring | Log API key usage, alert on unusual patterns |

### 13.7 Logging & Monitoring

| Rule | Detail |
|------|--------|
| Never log | Tokens, passwords, PII, API keys |
| Always log | Auth attempts, API errors, rate limit hits, unusual access patterns |
| Alert on | Failed auth spikes, API error rate > 5%, rate limit abuse |

---

## 14. Non-Goals (What We Are NOT Building)

| Non-Goal | Why |
|----------|-----|
| Social features (sharing, following users) | Keep it personal first |
| Twitter/X integration | API is paid ($100/month), Reddit covers community pulse |
| Native mobile app | PWA first, native later if demand exists |
| Paid features / monetization | Free first, figure out monetization later |
| Content creation | We aggregate and summarize, we don't create original content |
| Real-time streaming updates | Daily briefing + on-demand chat is enough for MVP |
| Multi-language support | English only for MVP |
| Admin panel | Not needed until significant user base |

---

## 15. Future Scope (Post-MVP)

| Feature | Priority | Description |
|---------|----------|-------------|
| Implicit preference tracking | High | Track what users actually read vs skip, auto-adjust |
| Smart suggestions | High | "Users like you also follow..." |
| Cross-domain correlation | High | "Market dip possibly linked to cyclone alert" |
| Action items | High | "Carry umbrella", "Consider booking profits" |
| Time-aware briefings | Medium | Morning (full), midday (update), evening (recap) |
| Seasonal pattern detection | Medium | Auto-suggest "IPL" every March |
| Voice briefings (TTS) | Medium | Listen during commute |
| Multi-channel delivery | Medium | Telegram, WhatsApp, email digest |
| Weekly/monthly trend reports | Medium | "This week: market up 4%, 3 rain days" |
| Anomaly detection | Medium | "Temperature is highest in 30 days" |
| Twitter/X integration | Low | If API becomes affordable |
| Native mobile app | Low | Only if PWA limitations become a problem |
| Multi-language | Low | Hindi, regional languages |
| Team/shared briefings | Low | Shared workspace briefings |

---

## 16. Success Metrics

| Metric | Target (3 months) | How To Measure |
|--------|-------------------|----------------|
| Daily Active Users | 100+ | Supabase analytics |
| Briefing open rate | > 60% | read field in briefings table |
| Chat usage | > 30% of users use chat weekly | Chat history count |
| Onboarding completion | > 80% | Funnel tracking |
| 7-day retention | > 40% | last_active_at tracking |
| 30-day retention | > 25% | last_active_at tracking |
| Avg briefing read time | 2-3 minutes | Frontend analytics |
| User preference changes | Track trend | Preference history table |

---

## 17. Open Questions

| Question | Status |
|----------|--------|
| Reddit API rate limits — will free tier be enough? | To verify |
| Groq free tier limits for per-user LLM calls at scale | To verify |
| PWA push notification reliability on iOS | To verify |
| Supabase free tier row limits for storing all briefings | To verify |

---

## 18. Appendix: API Rate Limits (Free Tiers)

| API | Free Tier Limit | Enough for MVP? |
|-----|----------------|-----------------|
| WeatherAPI | 1M calls/month | Yes |
| NewsAPI | 100 requests/day | Tight — may need alternative |
| GitHub API | 5000 requests/hour (authenticated) | Yes |
| Reddit API | 100 requests/minute | Yes |
| Arxiv API | No strict limit | Yes |
| HN Algolia API | No strict limit | Yes |
| Product Hunt API | 450 requests/day | Yes |
| HuggingFace API | Varies | Yes |
| Groq (Llama 3.1) | 30 requests/minute, 14.4k/day | Tight at scale |
| Supabase (free) | 500MB DB, 50k auth users | Yes for MVP |
| ExchangeRate API | 1500 requests/month | Yes |
