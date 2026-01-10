# Test Database Connection - Do This Now

## Quick Tests

### Test 1: Health Endpoint
Visit this URL in your browser:
```
https://agent-liquidcanvas.onrender.com/health/ready
```

**What to expect:**
- ✅ `{"status":"ready","database":"connected"}` → Database is connected!
- ⚠️ `{"status":"ready","database":"checking","warning":"..."}` → Connection issue
- ❌ Any error page → Backend might have issues

### Test 2: Database Query Endpoint
Visit this URL:
```
https://agent-liquidcanvas.onrender.com/api/prospects?limit=10
```

**What to expect:**
- ✅ `{"data":[...],"total":X}` → Database works! Migrations completed!
- ✅ `{"data":[],"total":0}` → Database works! Just no data yet (empty database is fine)
- ❌ `"relation does not exist"` or `"table does not exist"` → Migrations didn't complete
- ❌ `"column does not exist"` → Migrations didn't complete fully

---

## What to Do Based on Results

### If Health Endpoint Returns `{"database":"connected"}`:
✅ **Connection works!** Now check if tables exist:

1. Try the prospects endpoint above
2. If it works → Migrations completed! You're done! 🎉
3. If it returns "table does not exist" → Run migrations manually (see below)

### If Health Endpoint Shows Errors:
⚠️ **Connection issue** - Check logs for:
- Password authentication failed
- Database does not exist
- Connection refused

**Fixes:**
- Verify `DATABASE_URL` is correct
- Check database is actually running on Render
- Verify connection string format

### If Prospects Endpoint Shows "relation does not exist":
❌ **Migrations didn't complete** - Run them manually:

**Steps:**
1. Go to backend service → "Shell" tab
2. Wait for shell to connect
3. Run:
   ```bash
   cd backend
   alembic upgrade head
   ```
4. Watch for migration output
5. Verify it says "Running upgrade ... -> ..."
6. Check for errors

---

## Quick Diagnostic

Run this in your browser's console (on your frontend) or use curl:

```javascript
// In browser console:
fetch('https://agent-liquidcanvas.onrender.com/health/ready')
  .then(r => r.json())
  .then(console.log)

fetch('https://agent-liquidcanvas.onrender.com/api/prospects?limit=10')
  .then(r => r.json())
  .then(console.log)
```

Or use curl:
```bash
curl https://agent-liquidcanvas.onrender.com/health/ready
curl https://agent-liquidcanvas.onrender.com/api/prospects?limit=10
```

---

**Please test these endpoints and share the results!** This will tell us exactly what's happening. 🚀

