# Saar — Personalized Daily Briefing App

## What Is This
**Saar** (meaning "essence" in Hindi) — a personalized daily briefing web app (PWA). Users pick interests, get filtered news/weather/market briefings, and can ask follow-up questions in chat.

## Tech Stack
- **Backend:** FastAPI + LangGraph + Groq (Llama 3.1)
- **Frontend:** Next.js + shadcn/ui + Tremor + Magic UI + Tailwind
- **Database/Auth:** Supabase (PostgreSQL + Auth)
- **Scheduler:** APScheduler
- **Deploy:** Vercel (frontend) + Railway (backend)

## Project Structure
```
backend/          # FastAPI + LangGraph pipeline
frontend/         # Next.js PWA (mobile-first)
docs/             # PRD, plan, architecture docs
```

## Commands
```bash
# Backend
cd backend && uvicorn main:app --reload

# Frontend
cd frontend && npm run dev

# Tests
pytest tests/                  # Backend
npm run test                   # Frontend
npm run test:e2e               # Playwright
```

## Rules
- Mobile-first design (bottom nav, 44px touch targets, single column)
- All API keys server-side only, never in frontend
- Immutable data patterns — never mutate, always return new
- Type annotations on all Python functions
- pydantic for all API request/response models
- Small files (< 400 lines), small functions (< 50 lines)
- Handle errors explicitly, never swallow silently
- No hardcoded secrets — env variables only
- Test before commit — minimum 80% coverage

## Key Docs
- `docs/PRD.md` — Full product requirements
- `docs/plan.md` — Implementation roadmap
