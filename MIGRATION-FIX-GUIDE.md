# Quick Migration Fix Guide

## Problem
Backend error: `column users.onboarding_token_expires_at does not exist`

This means migrations were not applied to the database.

---

## Quick Fix (3 Steps)

### Step 1: Stop the Backend
```powershell
pm2 stop pms-backend
```

### Step 2: Run Migrations Manually
```powershell
cd C:\Users\vem\pms-stable\backend

# Check current status
python -m alembic current

# Apply all pending migrations
python -m alembic upgrade head
```

### Step 3: Start the Backend
```powershell
pm2 restart pms-backend

# Check if it's working
pm2 logs pms-backend --lines 20
```

---

## Alternative: Use the Fix Script

```powershell
cd C:\Users\vem\pms-stable\backend

# Diagnose the issue
.\fix-migrations.ps1 -DiagnoseOnly

# Apply fixes automatically
.\fix-migrations.ps1
```

---

## Why This Happened

The `pm2-startup.ps1` script should run migrations automatically, but it likely:
1. Wasn't run this time
2. Or the migration step failed silently
3. Or PM2 started the backend directly without running the startup script

---

## Ensure Migrations Run Automatically

### Option A: Always Use pm2-startup.ps1
```powershell
# Instead of running PM2 commands directly, use:
cd C:\Users\vem\pms-stable
.\pm2-startup.ps1
```

### Option B: Modify PM2 Ecosystem to Run Migrations
Update `backend/ecosystem.config.js` to add a pre-start script:

```javascript
module.exports = {
  apps: [{
    name: 'pms-backend',
    script: 'uvicorn',
    args: 'main:app --host 0.0.0.0 --port 8000',
    interpreter: 'python',
    cwd: 'C:/Users/vem/pms-stable/backend',
    // Add this:
    pre_start: 'python -m alembic upgrade head',
    env: {
      // ... existing env vars
    },
    autorestart: true,
    watch: false,
    max_memory_restart: '500M'
  }]
};
```

### Option C: Create PM2 Process File
```javascript
// backend/process.json
{
  "apps": [{
    "name": "pms-migrations",
    "script": "python",
    "args": "-m alembic upgrade head",
    "cwd": "C:/Users/vem/pms-stable/backend",
    "autorestart": false,
    "watch": false
  }, {
    "name": "pms-backend",
    "script": "uvicorn",
    "args": "main:app --host 0.0.0.0 --port 8000",
    "interpreter": "python",
    "cwd": "C:/Users/vem/pms-stable/backend",
    "wait_ready": true,
    "listen_timeout": 10000,
    "env": {
      // ... your env vars
    }
  }]
}

// Then start with:
// pm2 start process.json
```

---

## Verification

After running migrations, verify they worked:

```powershell
# Check migration status
cd C:\Users\vem\pms-stable\backend
python -m alembic current

# Should show: cc7410bd0a08 (head)

# Check the column exists in database
# Connect to your database and run:
# SELECT column_name FROM information_schema.columns
# WHERE table_name='users' AND column_name='onboarding_token_expires_at';
```

---

## Prevention

Add this to your deployment checklist:
1. Pull latest code
2. **Run migrations**: `python -m alembic upgrade head`
3. Restart PM2: `pm2 restart all`

Or use the startup script which does all this automatically:
```powershell
.\pm2-startup.ps1
```
