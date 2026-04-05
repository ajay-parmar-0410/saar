# Environment Secrets Setup

## GitHub Secrets (Settings → Secrets and variables → Actions)

Add these secrets to enable CI/CD pipelines:

### Required for Integration Tests
| Secret | Where to find |
|--------|---------------|
| `SUPABASE_URL` | Supabase Dashboard → Settings → API |
| `SUPABASE_ANON_KEY` | Supabase Dashboard → Settings → API |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Dashboard → Settings → API |
| `SUPABASE_JWT_SECRET` | Supabase Dashboard → Settings → API → JWT Secret |
| `GROQ_API_KEY` | console.groq.com → API Keys |
| `NEWS_API_KEY` | newsapi.org → Account |
| `WEATHER_API_KEY` | weatherapi.com → Account |

### Required for Deploy Pipeline
| Secret | Where to find |
|--------|---------------|
| `VERCEL_TOKEN` | Vercel → Settings → Tokens → Create |
| `RAILWAY_TOKEN` | Railway → Account → Tokens → Create |
| `RAILWAY_SERVICE_ID` | Railway → Project → Service → Settings → Service ID |

### Optional (Post-deploy health check)
| Secret | Value |
|--------|-------|
| `BACKEND_URL` | Your Railway backend URL (e.g., `https://saar-api.up.railway.app`) |
| `FRONTEND_URL` | Your Vercel frontend URL (e.g., `https://saar.vercel.app`) |

### Also set as GitHub Variables (not secrets)
| Variable | Value |
|----------|-------|
| `RUN_INTEGRATION_TESTS` | `true` (set this after adding Supabase secrets) |

---

## Vercel Environment Variables

Add in Vercel Dashboard → Project → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Your Supabase anon key |
| `NEXT_PUBLIC_API_URL` | Your Railway backend URL |

---

## Railway Environment Variables

Add in Railway Dashboard → Service → Variables:

| Variable | Value |
|----------|-------|
| `SUPABASE_URL` | Your Supabase URL |
| `SUPABASE_ANON_KEY` | Your Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Your Supabase service role key |
| `SUPABASE_JWT_SECRET` | Your Supabase JWT secret |
| `GROQ_API_KEY` | Your Groq API key |
| `NEWS_API_KEY` | Your NewsAPI key |
| `WEATHER_API_KEY` | Your WeatherAPI key |
| `TAVILY_API_KEY` | Your Tavily API key |
| `FRONTEND_URL` | Your Vercel frontend URL (for CORS) |
