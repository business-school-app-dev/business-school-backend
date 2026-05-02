# App Store Backend Issues - Deployment Fix Guide

## Summary
Your backend has **THREE CRITICAL ISSUES** preventing the App Store version from working:

### ✅ **FIXED in Code:**
1. ✅ **CORS Headers** - Added flask-cors configuration
2. ✅ **Error Handling** - Improved error messages for debugging
3. ✅ **Database Diagnostic Endpoint** - Added `/api/v1/health/db-status`

### 🔴 **STILL REQUIRED ON UNIVERSITY SERVER:**
1. 🔴 **Install Dependencies** - Install `flask-cors` 
2. 🔴 **Seed Database** - Run the seed scripts to populate questions and events
3. 🔴 **Configure Environment Variables** - Ensure DATABASE_URL is set

---

## What's Wrong?

### Issue #1: CORS Blocking Requests (PRIMARY ISSUE) ✅ FIXED
**Problem:**
- The App Store frontend is from a different domain than your university server
- Browser CORS policy blocks cross-origin requests without proper headers
- This causes: "Failed to load questions", events not showing, leaderboard not loading

**Solution:**
- ✅ Added `flask-cors` to `requirements.txt`
- ✅ Configured CORS in `app/__init__.py` to allow all `/api/*` requests

### Issue #2: Database Not Seeded (LIKELY CAUSE) ⚠️ MANUAL ACTION NEEDED
**Problem:**
- If you haven't run the seed scripts on the university server, the questions and events tables are EMPTY
- This causes empty responses from quiz and events endpoints
- Frontend then shows "Failed to load" errors

**Solution - Run These Commands on University Server:**
```bash
# 1. Install dependencies (if not already done)
pip install -r requirements.txt

# 2. Run database migrations
alembic upgrade head

# 3. Seed the database with questions and events
python scripts/seed_db.py

# 4. Verify data was loaded
python -c "
from app import create_app
from app.models import Questions, Event

app = create_app()
with app.app_context():
    q = app.session.query(Questions).count()
    e = app.session.query(Event).count()
    print(f'Questions: {q}')
    print(f'Events: {e}')
    print('✅ Database is seeded!' if q > 0 and e > 0 else '❌ Database is empty!')
"
```

### Issue #3: Environment Variables Not Configured ⚠️ CHECK
**Problem:**
- `DATABASE_URL` environment variable might not be set correctly
- `SECRET_KEY` needs to be set

**Solution:**
Create a `.env` file on the university server:
```
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/your_db_name
SECRET_KEY=your-secret-key-here
```

---

## Diagnostic Endpoint

After deploying, test these endpoints:

```bash
# 1. Check basic health
curl https://your-server/api/v1/health

# 2. Check database status and data population
curl https://your-server/api/v1/health/db-status

# Expected output when database is properly seeded:
{
  "status": "ok",
  "database": "connected",
  "questions_loaded": true,
  "questions_count": 42,
  "events_loaded": true,
  "events_count": 12,
  "message": "✅ All systems operational"
}
```

If `questions_loaded` or `events_loaded` are `false`, the seed scripts haven't been run.

---

## Endpoints Reference

All endpoints are now CORS-enabled and should work from the App Store frontend:

### Quiz/Challenges
- `GET /api/v1/challenges/can-play?username=NAME` - Check if user can play today
- `GET /api/v1/challenges/questions` - Get 3 random questions (Easy, Medium, Hard)
- `POST /api/v1/challenges/submit-batch` - Submit answers and get score
- `GET /api/v1/topten` - Get leaderboard top 10

### Events
- `GET /api/v1/scraping/events?days=60` - Get upcoming events (next 60 days)

### Leaderboard (if needed)
- `GET /api/v1/topten` - Top 10 scorers

### Diagnostics
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/db-status` - Database status and data count

---

## Deployment Checklist

- [ ] Pull latest code (includes CORS fix)
- [ ] Update `requirements.txt` with `flask-cors`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run migrations: `alembic upgrade head`
- [ ] Run seed scripts: `python scripts/seed_db.py`
- [ ] Verify with diagnostic endpoint: `curl https://your-server/api/v1/health/db-status`
- [ ] Restart Flask/Gunicorn server
- [ ] Test from App Store frontend

---

## Expected Behavior After Fix

✅ Daily Quiz will load questions  
✅ Leaderboard will show top 10 scores  
✅ Upcoming campus events will display  
✅ Monte Carlo simulation will continue to work (already working)  
✅ Course recommender will continue to work (already working)  

---

## Need Help?

If issues persist after following this guide:

1. **Check logs** on university server for error messages
2. **Run diagnostic endpoint**: `curl https://your-server/api/v1/health/db-status`
3. **Verify DATABASE_URL** is correctly set and database is accessible
4. **Check that seed scripts ran successfully** without errors
5. **Look at Flask server logs** for any 500 errors
