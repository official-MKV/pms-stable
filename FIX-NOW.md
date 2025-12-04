# IMMEDIATE FIX REQUIRED - Database Migration Issue

## Current Problem
```
sqlalchemy.exc.ProgrammingError: column users.onboarding_token_expires_at does not exist
```

Your backend is failing because the database schema is outdated. Migrations were not applied.

---

## QUICK FIX (Do This Now on Remote Server)

### Step 1: Stop the Backend
```powershell
pm2 stop pms-backend
```

### Step 2: Apply Migrations
```powershell
cd C:\Users\vem\pms-stable\backend
python -m alembic upgrade head
```

You should see output like:
```
INFO  [alembic.runtime.migration] Running upgrade 9af49871a6c8 -> b3d53f692103, add_onboarding_token_expiration
INFO  [alembic.runtime.migration] Running upgrade b3d53f692103 -> cc7410bd0a08, add PENDING_ACTIVATION status
```

### Step 3: Restart Backend
```powershell
pm2 restart pms-backend
```

### Step 4: Verify It's Working
```powershell
pm2 logs pms-backend --lines 20
```

You should see the backend start successfully without the column error.

---

## PERMANENT FIX (Prevent This From Happening Again)

### What Changed

I've updated your `ecosystem.config.js` to automatically run migrations before starting the backend. Now it uses a wrapper script (`start_with_migrations.py`) that:

1. Runs `alembic upgrade head` (migrations)
2. Only starts the backend if migrations succeed
3. Exits with error if migrations fail

### Deploy the Fix

1. **On your development machine**, commit and push the changes:
```bash
git add .
git commit -m "Add automatic database migrations on backend startup"
git push
```

2. **On your remote server**, pull the changes:
```bash
cd C:\Users\vem\pms-stable
git pull
```

3. **Restart PM2** (migrations will now run automatically):
```powershell
pm2 restart pms-backend
```

4. **Check the logs** to see migrations running:
```powershell
pm2 logs pms-backend --lines 30
```

You should see:
```
=== Starting PMS Backend with Migrations ===
Running database migrations...
✓ Migrations completed successfully
Starting uvicorn server...
```

---

## Files That Were Changed/Added

### Modified:
- `backend/ecosystem.config.js` - Now uses `start_with_migrations.py` instead of calling uvicorn directly

### New Files:
- `backend/start_with_migrations.py` - Main wrapper script (runs migrations then starts server)
- `backend/start-with-migrations.sh` - Bash version for Linux
- `backend/start-with-migrations.ps1` - PowerShell standalone version
- `backend/run-migrations.ps1` - Manual migration management tool (Windows)
- `backend/run-migrations.sh` - Manual migration management tool (Linux)
- `backend/fix-migrations.ps1` - Diagnostic and fix tool
- `DEPLOYMENT.md` - Complete deployment guide
- `MIGRATION-FIX-GUIDE.md` - Troubleshooting guide
- `FIX-NOW.md` - This file

---

## How It Works Now

### Automatic (Recommended)
Every time PM2 starts or restarts the backend:
```
1. start_with_migrations.py runs
2. Checks for pending migrations
3. Applies them automatically
4. Starts uvicorn
```

If migrations fail, the backend won't start (fail-safe).

### Manual (When Needed)
Use the migration scripts for manual control:

**Windows:**
```powershell
cd backend
.\run-migrations.ps1 -Status     # Check status
.\run-migrations.ps1              # Apply migrations
.\fix-migrations.ps1              # Diagnose and fix issues
```

**Linux:**
```bash
cd backend
./run-migrations.sh status     # Check status
./run-migrations.sh            # Apply migrations
```

---

## Future Deployments

Your deployment workflow is now simpler:

```bash
# 1. Pull latest code
git pull

# 2. Restart PM2 (migrations run automatically)
pm2 restart all

# That's it! Migrations happen automatically.
```

Or use the startup script:
```powershell
.\pm2-startup.ps1  # Handles migrations + starts everything
```

---

## Verification Checklist

After applying the fix, verify:

- [ ] Backend starts without errors: `pm2 logs pms-backend`
- [ ] Migrations run automatically (check logs for "Running database migrations...")
- [ ] Database has the missing column:
  ```powershell
  python -m alembic current
  # Should show: cc7410bd0a08 (head)
  ```
- [ ] Application is accessible at your URL

---

## If Something Goes Wrong

### Migrations Fail
Check the logs:
```powershell
pm2 logs pms-backend --err --lines 50
```

Common issues:
- **Database not reachable**: Check DATABASE_URL in ecosystem.config.js
- **Wrong migration state**: Run `.\fix-migrations.ps1` to diagnose
- **Permission issues**: Ensure database user has proper permissions

### Backend Won't Start
1. Check PM2 status: `pm2 status`
2. Check error logs: `pm2 logs pms-backend --err`
3. Test migrations manually: `python -m alembic upgrade head`
4. If needed, downgrade: `python -m alembic downgrade -1`

### Need Help
Run the diagnostic tool:
```powershell
cd backend
.\fix-migrations.ps1 -DiagnoseOnly
```

This will show you:
- Current migration version
- Missing migrations
- Missing database columns
- Suggested fixes

---

## Summary

**Right Now:** Run the 3 commands in "QUICK FIX" section above

**After That:** Push changes to git, pull on server, restart PM2

**From Now On:** Just `git pull && pm2 restart all` - migrations are automatic!
