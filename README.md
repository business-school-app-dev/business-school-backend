# 💰 Financial Wellness Center — Backend Setup Guide

Welcome to the **UMD Financial Wellness Center Backend**!  
This guide walks you through setting up the backend and local database on your own laptop. SQLite is used for simplicity — no Docker or database server needed.

---

## 🧠 Overview

**Tech stack:**
- Python (Flask)
- SQLite (embedded database)
- SQLAlchemy ORM
- Alembic for schema migrations

**Goal:**  
Get the backend + database running locally with one command, and be able to run migrations and test endpoints.

---

## ⚙️ Prerequisites

Before you start, make sure you have:

1. **Python 3.9 or 3.10**  
   - Check with:
     ```bash
     python --version
     ```
   - [Download Python](https://www.python.org/downloads/) if needed, and check "Add to PATH" during installation.

> 💡 No Docker or database server installation needed — SQLite is built into Python!

---

##  1. Clone and Set Up Virtual Environment

```bash
git clone <repo-url>
cd business-school-backend
```

### Create and activate virtual environment

```bash
python -m venv .venv
```

**On Windows (PowerShell):**
```
.\.venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure Environment Variables

Create a `.env` file in the project root (same folder as `alembic.ini`):

```
DATABASE_URL=sqlite:///./dev.db
```

We include a `.env.example` in the repo — copy it as a template:

```bash
cp .env.example .env
```

## 3. Apply Database Migrations

Alembic creates your tables automatically.
Make sure your venv is active (`(.venv)` in prompt) and run:

```bash
alembic upgrade head
```

You should see logs like:

```
INFO  [alembic.runtime.migration] Running upgrade  -> <revision_id>, add users table
```

This creates all your tables (like users) in the SQLite database file (`dev.db`).

To verify the tables were created:

```bash
sqlite3 dev.db ".tables"
```

## 4. Run the Flask Backend

Set your Flask environment variables and start the server:

**Windows PowerShell:**
```
$env:FLASK_APP="wsgi.py"
$env:FLASK_ENV="development"
flask run --debug
```

**macOS/Linux:**
```bash
export FLASK_APP="wsgi.py"
export FLASK_ENV="development"
flask run --debug
```

Flask should start at: http://127.0.0.1:5000

## 5. Test Your Setup

Visit: http://127.0.0.1:5000/api/v1/health

If you see:
```json
{ "status": "ok" }
```

You're officially up and running 🎉

---

### Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| ❌ `database.db is locked` | Close any other connections or processes using SQLite. SQLite doesn't support concurrent writes. |
| ❌ `ModuleNotFoundError: No module named 'app'` | Make sure you run Alembic from the project root (where `alembic.ini` lives), and `app/__init__.py` exists. |
| ❌ `No such table: users` | Run `alembic upgrade head` to create the tables. |
| ❌ Port 5000 already in use | Run on a different port: `flask run --port=5001` |

---

## Quick Commands Cheat Sheet

### Run migrations
```bash
alembic upgrade head
```

### Create new migration after model change
```bash
alembic revision --autogenerate -m "add new table"
```

### Check SQLite tables
```bash
sqlite3 dev.db ".tables"
```

### Reset database (delete and recreate)
```bash
rm dev.db
alembic upgrade head
```

### Run Flask API
```bash
flask run --debug
```

---

### Developer Notes

- All models live in `app/models.py`
- Migrations live in `migrations/versions/`
- Database URL standard: `sqlite:///./dev.db`
- Don't commit your local `.env` file — it's in `.gitignore`
- Everyone's DB setup is reproducible via SQLite + Alembic

---

## RENDER URL 

https://business-school-backend.onrender.com/
