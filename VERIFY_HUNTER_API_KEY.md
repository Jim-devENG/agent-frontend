# How to Verify Your Hunter.io API Key is Working

## ✅ Quick Verification Steps

### Method 1: Test via Settings Page (Easiest)

1. **Open your app** in the browser
2. **Navigate to Settings page** (usually at `/settings` or click Settings in the menu)
3. **Find "Hunter.io" service card**
4. **Click the "Test" button**
5. **Check the result:**
   - ✅ **Success**: "Hunter.io is working. Found X emails for test domain."
   - ❌ **Not Configured**: "Hunter.io API key not configured"
   - ❌ **Error**: Shows error message

### Method 2: Check API Key Status

1. **Go to Settings page**
2. **Look at the Hunter.io service card**
3. **Status indicators:**
   - 🟢 **Configured**: Green checkmark or "connected" status
   - 🔴 **Not Configured**: Red X or "not_configured" status

### Method 3: Check Backend Logs (Advanced)

If you have access to Render logs:

1. Go to **Render Dashboard** → Your backend service → **Logs**
2. Look for messages like:
   - ✅ `Hunter.io client initialized`
   - ✅ `Hunter.io is working`
   - ❌ `Hunter.io API key not configured`

## 🔍 What to Look For

### ✅ Success Indicators:
- Settings page shows "connected" or "configured"
- Test button returns "Hunter.io is working"
- No more 429 rate limit errors in logs
- Discovery jobs start saving prospects with emails

### ❌ Problem Indicators:
- Settings shows "not_configured"
- Test returns "API key not configured"
- Still getting 429 errors
- Discovery jobs still saving 0 prospects

## 🛠️ Troubleshooting

### If API Key Shows "Not Configured":

1. **Verify in Render:**
   - Go to Render Dashboard → Your backend service → Environment
   - Check that `HUNTER_IO_API_KEY` exists
   - Verify the value is exactly: `b8b197dff80f8cc991db92a6a37653c467c8b952`
   - Make sure there are no extra spaces

2. **Restart the Service:**
   - Render should auto-restart after env var changes
   - If not, manually restart: Render Dashboard → Your service → Manual Deploy → Clear build cache & deploy

3. **Wait a Few Minutes:**
   - Sometimes it takes 1-2 minutes for changes to propagate

### If Test Fails with Error:

1. **Check the error message:**
   - "API key not configured" → See above
   - "Rate limit exceeded" → Old key might still be cached, wait 5 minutes
   - "Invalid API key" → Double-check the key value in Render

2. **Verify the Key:**
   - Go to https://hunter.io → Settings → API
   - Make sure the key matches what you put in Render

## 📊 Expected Behavior After Update

Once the new Pro account key is active:

1. **No More 429 Errors:**
   - You should stop seeing "too_many_requests" errors in logs
   - Discovery jobs should process more domains successfully

2. **More Prospects Saved:**
   - Discovery jobs should save more prospects (not 0)
   - More emails should be found and saved

3. **Higher Rate Limits:**
   - Pro account: 50,000 searches/month
   - Much higher than free tier (25/month)

## 🧪 Test It Now

**Quick Test:**
1. Go to your app's Settings page
2. Click "Test" on Hunter.io service
3. Should see: "Hunter.io is working. Found X emails for test domain."

If you see that message, **your API key is integrated and working!** ✅

