# Authentication Troubleshooting Guide

## Issue: Statistics and Status Unavailable

If you're seeing "Statistics and status unavailable" or 401 errors, follow these steps:

### Step 1: Check if You're Logged In

1. **Open Browser DevTools** (Press F12)
2. **Go to Console tab**
3. **Run this command:**
   ```javascript
   localStorage.getItem('auth_token')
   ```

**If it returns `null`**: You're not logged in. Go to Step 2.

**If it returns a token**: The token might be expired or invalid. Go to Step 3.

### Step 2: Log In

1. **Go to**: `https://agent.liquidcanvas.art/login`
2. **Enter credentials**:
   - Username: `admin`
   - Password: Check your Render dashboard → Environment tab → `ADMIN_PASSWORD`
3. **After login**, you should be redirected to the dashboard
4. **Statistics should now load**

### Step 3: Clear and Re-login

If you have a token but still getting 401 errors:

1. **Clear localStorage**:
   - Open DevTools (F12)
   - Console tab
   - Run: `localStorage.clear()`
   - Refresh the page
2. **Log in again** at `/login`

### Step 4: Verify Backend Password

Make sure the password in Render matches what you're using:

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Select your backend service**
3. **Go to "Environment" tab**
4. **Check `ADMIN_PASSWORD`** - this is the password you need to use

### Step 5: Check Backend Logs

If still not working, check Render logs:

1. **Render Dashboard** → Your service → **Logs** tab
2. **Look for**:
   - `401 Unauthorized` errors
   - Authentication-related errors
   - Token validation errors

### Common Issues

#### Issue: "Backend not connected"
- **Cause**: Backend is not responding or authentication failed
- **Fix**: Log in first, then check if backend is running

#### Issue: "Statistics unavailable"
- **Cause**: Not authenticated or token expired
- **Fix**: Log in at `/login`

#### Issue: Token exists but still 401
- **Cause**: Token expired or backend password changed
- **Fix**: Clear localStorage and log in again

### Quick Fix Script

Run this in browser console to check everything:

```javascript
// Check if logged in
const token = localStorage.getItem('auth_token');
console.log('Token exists:', !!token);
console.log('Token value:', token ? token.substring(0, 20) + '...' : 'null');

// Test API call
if (token) {
  fetch('https://agent.liquidcanvas.art/api/v1/stats', {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  .then(r => {
    console.log('Stats API Status:', r.status);
    if (r.status === 401) {
      console.error('❌ Token is invalid or expired. Please log in again.');
      localStorage.clear();
      window.location.href = '/login';
    } else if (r.ok) {
      console.log('✅ Authentication working!');
    }
  });
} else {
  console.error('❌ No token found. Please log in.');
  window.location.href = '/login';
}
```

### Still Not Working?

1. **Check Vercel deployment**: Make sure frontend has latest code
2. **Check Render deployment**: Make sure backend has latest code
3. **Verify environment variables**: `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `JWT_SECRET_KEY` are set in Render
4. **Hard refresh**: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

