# Troubleshooting Guide

## Backend Not Responding / Request Timeout

### Symptoms
- Frontend shows "Request timeout" errors
- Dashboard shows "Backend not connected" banner
- All API calls fail

### Solutions

#### 1. Check if Backend is Running
```powershell
.\check_backend.ps1
```

Or manually check:
```powershell
# Check if port 8000 is in use
Get-NetTCPConnection -LocalPort 8000
```

#### 2. Start the Backend
```powershell
.\start_backend.ps1
```

#### 3. Test Backend Directly
Open in browser: `http://localhost:8000/api/v1/stats`

If this doesn't load, the backend is not running.

#### 4. Check Backend Logs
Look at the PowerShell window running the backend for error messages.

### Common Issues

#### Port Already in Use
If you see "Address already in use":
```powershell
# Kill process on port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

#### Python Not Found
If you see "Python was not found":
- Make sure Python 3.11+ is installed
- Try using `py` instead of `python`:
  ```powershell
  py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```

#### Dependencies Not Installed
```powershell
pip install -r requirements.txt
```

## No Websites Being Discovered

### Check Diagnostic Endpoints

1. **Test Search Functionality**
   ```
   http://localhost:8000/api/v1/diagnostic/search-test
   ```
   This will show if DuckDuckGo search is working.

2. **Full Diagnostic Check**
   ```
   http://localhost:8000/api/v1/diagnostic/full-check
   ```
   This shows overall system health.

3. **Check Database Stats**
   ```
   http://localhost:8000/api/v1/debug/stats
   ```
   This shows what's actually in your database.

### Common Causes

1. **DuckDuckGo Search Not Working**
   - Check network/firewall
   - Verify `duckduckgo-search` library is installed
   - Test: `http://localhost:8000/api/v1/discovery/test-search?query=art+gallery`

2. **Quality Filters Too Strict**
   - Already fixed - filters are now lenient
   - Check: `http://localhost:8000/api/v1/debug/websites` to see if websites are being saved

3. **Automation Not Running**
   - Check Settings tab - is automation ON?
   - Check search interval setting
   - Check Activity Feed for job status

4. **Empty Seed File**
   - Check `seed_websites.txt` has URLs
   - Add URLs manually if needed

## Browser Console Errors

### Chrome Extension Errors (Harmless)
These errors are from browser extensions (Grammarly, ad blockers, etc.) and can be ignored:
- `chrome-extension://invalid/`
- `Denying load of <URL>`
- `ERR_BLOCKED_BY_CLIENT`

### Real Errors to Fix
- `Request timeout` = Backend not running
- `Failed to fetch` = Backend not accessible
- `ERR_CONNECTION_REFUSED` = Backend not running

## Still Having Issues?

1. Check backend logs in PowerShell window
2. Visit diagnostic endpoints listed above
3. Check `http://localhost:8000/api/v1/debug/stats` for database contents
4. Verify automation is ON in Settings tab

