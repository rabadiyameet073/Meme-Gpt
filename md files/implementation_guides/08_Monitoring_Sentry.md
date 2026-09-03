# 08 — Monitoring: Sentry + UptimeRobot
> **Priority:** 🟡 Medium — Know immediately when something breaks in production
> **Time Needed:** ~1 hour
> **Result:** Error alerts in your inbox, uptime monitoring every 5 minutes

---

## 🔍 What Gets Monitored

| Tool | What It Does | Alert When |
|---|---|---|
| **Sentry** | Catches Python exceptions in FastAPI | Any unhandled error |
| **Sentry** | Captures frontend JS errors | React component crash |
| **UptimeRobot** | Pings `/health` every 5 min | Backend goes down |
| **Railway Metrics** | CPU/Memory/Request graphs | Resource spike |
| **Vercel Analytics** | Web vitals + visitor stats | Traffic patterns |

---

## PART A — Sentry (Error Tracking)

### Step A1 — Create Sentry Account + Project

```
1. Go to: https://sentry.io
2. Sign up (free: 5,000 errors/month)
3. Create a new Project:
   - Platform: FastAPI / Python
   - Name: memegpt-backend
4. Copy the DSN:
   - Looks like: https://abc123@o123456.ingest.sentry.io/123456
```

### Step A2 — Add SENTRY_DSN to .env

```env
# d:\Meme GPT\.env
SENTRY_DSN=https://YOUR_KEY@o000000.ingest.sentry.io/000000
```

The backend `main.py` already has this initialization code:
```python
# This is already in backend/app/main.py — just needs SENTRY_DSN set
sentry_dsn = getattr(settings, "SENTRY_DSN", "")
if sentry_dsn:
    import sentry_sdk
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=0.1,
        environment=getattr(settings, "APP_ENV", "development"),
    )
```

### Step A3 — Test Sentry is Working

```powershell
cd "d:\Meme GPT\backend"
uvicorn app.main:app --reload --port 8000
```

Look for in logs:
```
✅ Sentry initialized
```

Create a test error endpoint to verify (temporary, remove after testing):
```powershell
# Trigger a test error
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health/sentry-test" -Method GET
```

Or send a test event from Python:
```python
import sentry_sdk
sentry_sdk.init(dsn="YOUR_DSN")
sentry_sdk.capture_message("MemeGPT Sentry test", level="info")
```

Check Sentry dashboard — you should see the event appear within 30 seconds.

### Step A4 — Add Frontend Sentry (Optional but Recommended)

```powershell
cd "d:\Meme GPT\frontend"
npm install @sentry/react
```

Add to `d:\Meme GPT\frontend\src\main.tsx`:

```typescript
import * as Sentry from "@sentry/react";

// Add BEFORE ReactDOM.createRoot()
if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.VITE_APP_ENV || "development",
    tracesSampleRate: 0.1,
    replaysSessionSampleRate: 0.05,
  });
}
```

Add to Vercel environment variables:
```env
VITE_SENTRY_DSN=https://YOUR_FRONTEND_KEY@sentry.io/xxx
```

Create a separate Sentry project for the frontend (React) to get separate error streams.

### Step A5 — Set Up Sentry Alerts

In Sentry → Alerts → Create Alert:

```
Alert Rule 1: First Occurrence
  Condition: A new issue is created
  Action: Send email to your@email.com
  Frequency: Once per issue

Alert Rule 2: High Volume
  Condition: Issue count > 10 in 1 hour
  Action: Send email
  Frequency: Every hour

Alert Rule 3: Unresolved Issues
  Condition: Issue is unresolved for > 24 hours
  Action: Send email
```

---

## PART B — UptimeRobot (Availability Monitoring)

### Step B1 — Create UptimeRobot Account

```
1. Go to: https://uptimerobot.com
2. Sign up (free: 50 monitors, 5-min intervals)
3. Click "Add New Monitor"
```

### Step B2 — Create Backend Health Monitor

```
Monitor Type: HTTP(s)
Friendly Name: MemeGPT Backend
URL: https://your-app.railway.app/api/v1/health
Monitoring Interval: Every 5 minutes
Alert When: Down (send email)
```

### Step B3 — Create Frontend Monitor

```
Monitor Type: HTTP(s)
Friendly Name: MemeGPT Frontend
URL: https://memegpt-xyz.vercel.app
Monitoring Interval: Every 5 minutes
Alert When: Down
```

### Step B4 — Add Keyword Check

Also add a keyword monitor to catch cases where the page loads but is broken:

```
Monitor Type: Keyword
URL: https://your-app.railway.app/api/v1/health
Keyword: healthy
Alert When: Keyword NOT found
```

---

## PART C — Railway Native Metrics (No Setup Needed)

Railway automatically provides:
- CPU/Memory graphs → Go to: Railway Dashboard → Your Service → Metrics
- Request logs → Railway Dashboard → Your Service → Logs
- Restart history

Set up Railway alerts:
```
Railway Dashboard → Your Service → Settings → Notifications
  Enable: Deployment failures
  Enable: Service restarts
  Email: your@email.com
```

---

## PART D — Vercel Analytics (Frontend)

Vercel provides free web analytics:

```
Vercel Dashboard → Your Project → Analytics
  Enable: Web Analytics
  Enable: Speed Insights
```

This shows:
- Page views, unique visitors
- Core Web Vitals (LCP, FID, CLS)
- Country/device breakdown

No code changes needed — Vercel injects analytics automatically.

---

## 📊 Monitoring Dashboard Summary

After setup, you'll have:

| What | Where | Check Frequency |
|---|---|---|
| Backend errors | Sentry dashboard + email | Real-time |
| Frontend errors | Sentry (React project) + email | Real-time |
| Backend uptime | UptimeRobot dashboard + email | Every 5 min |
| Frontend uptime | UptimeRobot | Every 5 min |
| Resource usage | Railway Metrics | Continuous |
| Web traffic | Vercel Analytics | Daily |

---

## ✅ Done When

- [ ] SENTRY_DSN set in .env and in Railway environment
- [ ] Backend logs show `✅ Sentry initialized`
- [ ] A test error appears in Sentry dashboard
- [ ] UptimeRobot shows backend as "Up" (green)
- [ ] UptimeRobot alert email received when you temporarily stop backend
- [ ] Vercel Analytics shows data after first page view

**You are now FULLY deployed with monitoring! 🎉**
