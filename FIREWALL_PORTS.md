# Firewall Ports Configuration

This document outlines all firewall ports required for the Financial Wellness Center Backend application to function properly.

---

## 🔴 Production (Render Deployment)

### Inbound Ports

| Port | Protocol | Purpose | Status |
|------|----------|---------|--------|
| **443** | HTTPS | Web application traffic | ✅ Required (Primary) |
| **80** | HTTP | HTTP to HTTPS redirect | ✅ Required |

**How it works on Render:**
- Render acts as a reverse proxy with built-in SSL/TLS termination
- All HTTPS traffic comes through port 443
- Gunicorn runs internally on a dynamic port assigned by Render (`$PORT` env var)
- Render automatically handles certificate renewal and HTTPS

### Outbound Ports

| Port | Destination | Protocol | Purpose | Status |
|------|-------------|----------|---------|--------|
| **443** | rhsmith.umd.edu | HTTPS | Web scraping (events) | ✅ Required |
| **53** | DNS servers | DNS | Domain name resolution | ✅ Required |

**External Services Called:**
- `https://www.rhsmith.umd.edu/events` - Event scraping (uses HTTPS/443)

---

## 🟡 Development (Local Machine)

### Inbound Ports

| Port | Protocol | Purpose | Status | Notes |
|------|----------|---------|--------|-------|
| **5000** | HTTP | Flask dev server | ✅ Development Only | Not exposed to internet |
| **6379** | TCP | Redis (optional) | ⚠️ If using Redis | Local development only |

**How to run:**
```bash
# Development - Flask runs on port 5000 locally
export FLASK_ENV=development
flask run --debug
# App available at: http://localhost:5000
```

### Testing the Endpoints

```bash
# Health check
curl http://127.0.0.1:5000/api/v1/health

# Get users (example)
curl http://127.0.0.1:5000/api/v1/users
```

---

## 📊 Summary by Deployment Environment

### Local Development (.env)
```
- Database: SQLite (file-based, no network)
- Redis: localhost:6379 (optional for async tasks)
- Flask: http://localhost:5000
```

### Production (Render)
```
- HTTPS: Auto-configured on port 443
- Database: Postgres (Render Managed Database)
- Redis: Render Redis instance (if configured)
- Health: https://business-school-backend.onrender.com/api/v1/health
```

---

## 🔒 Security Recommendations

### Firewall Rules for Production

**Allow inbound:**
```
- 0.0.0.0/0 on port 443 (HTTPS)
- 0.0.0.0/0 on port 80  (HTTP → HTTPS redirect)
```

**Allow outbound:**
```
- 0.0.0.0/0 on port 443 (HTTPS for external APIs)
- 0.0.0.0/0 on port 53  (DNS)
```

**Block inbound:**
```
- Port 5000, 6379, and all other non-standard ports
- No SSH access from internet (use Render's deployment methods)
```

### Network Policy on Render

- ✅ Render provides automatic DDoS protection
- ✅ Automatic SSL/TLS certificates (Let's Encrypt)
- ✅ No manual port configuration needed
- ✅ Render handles certificate renewal

---

## 🚀 API Endpoints (All HTTPS/443 in Production)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/auth/*` | POST | Authentication |
| `/api/v1/users` | GET/POST | User management |
| `/api/v1/simulations` | GET/POST | Financial simulations |
| `/api/v1/quiz_store/*` | GET | Quiz data |
| `/api/v1/events` | GET | Scraped events |
| `/api/v1/jobs` | GET | Job market data |

---

## 📋 Network Requirements Checklist

### For Development
- [ ] Port 5000 is not already in use (`lsof -i :5000`)
- [ ] (Optional) Redis running on 6379 for async tasks
- [ ] Internet access for external API calls (rhsmith.umd.edu)

### For Production (Render)
- [ ] Render project configured
- [ ] Environment variables set in Render dashboard
- [ ] Database connection string configured
- [ ] Outbound HTTPS (port 443) allowed to rhsmith.umd.edu
- [ ] DNS resolution working

---

## 🔧 Environment Variables (Port Configuration)

```bash
# Development (.env)
FLASK_ENV=development              # Dev mode
DATABASE_URL=sqlite:///./dev.db    # Local SQLite
REDIS_URL=redis://localhost:6379/0 # Optional, local Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Production (Render)
# → Render auto-assigns PORT env var
# → HTTPS auto-enabled
# → DATABASE_URL provided by Render panel
```

---

## ❓ Troubleshooting

### "Port 5000 already in use" (Development)
```bash
# Find what's using port 5000
lsof -i :5000

# Run on different port
flask run --port=5001
```

### "Connection refused to Redis" (Development)
```bash
# Redis is optional. Check if it's needed:
grep -r "redis\|celery" requirements.txt

# If not needed, ignore. If needed:
# Install and start Redis
brew install redis
redis-server
```

### "Cannot reach external API" (Production)
- Check firewall allows outbound HTTPS (443)
- Verify rhsmith.umd.edu is not blocked
- Check internet connectivity on Render instance

---

## 📞 Related Files

- `render.yaml` - Production deployment config
- `.env` - Development configuration
- `requirements.txt` - Dependencies (includes redis, celery)
- `wsgi.py` - Flask app entry point
