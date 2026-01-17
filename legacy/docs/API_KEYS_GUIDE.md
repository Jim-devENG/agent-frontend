# API Keys Guide - When You Need Them

## 🎯 Quick Answer

**You need API keys when you want to:**
1. **Generate AI emails** → Need Gemini or OpenAI API key
2. **Send emails** → Need Gmail API credentials OR SMTP credentials
3. **Automatically discover websites** → Need Google/Bing Search API keys (optional)

**You DON'T need API keys for:**
- ✅ Scraping websites (uses Requests/Playwright - free)
- ✅ Extracting contacts (uses regex/BeautifulSoup - free)
- ✅ Using email templates (no API needed)
- ✅ Viewing dashboard data (no API needed)
- ✅ Manual URL scraping (no API needed)

---

## 📋 Detailed Breakdown

### 1. **Gemini API Key** (Priority: HIGH if using AI emails)

**When you need it:**
- When you want to generate personalized emails using AI
- When automation runs the "generate_ai_email" job
- When you use the `/api/v1/emails/generate` endpoint with `use_ai=true`

**What happens without it:**
- ✅ System still works - you can use email templates instead
- ✅ Scraping and contact extraction still work
- ❌ AI email generation will fail (but templates work as fallback)
- ⚠️ You'll see warnings in logs: "GEMINI_API_KEY not configured"

**How to get it:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

**Where to add it:**
```bash
# Create .env file in project root
GEMINI_API_KEY=your_api_key_here
```

**Alternative:** Use OpenAI API key instead (set `OPENAI_API_KEY` and `AI_MODEL=gpt-4`)

---

### 2. **Gmail API Credentials** (Priority: HIGH if sending emails)

**When you need it:**
- When you want to send emails automatically
- When automation runs the "send_email_if_not_sent" job
- When you use the `/api/v1/emails/send` endpoint

**What happens without it:**
- ✅ System still works - emails are generated but not sent
- ✅ You can manually review emails in dashboard
- ❌ Automatic email sending will fail
- ⚠️ You can use SMTP instead (see below)

**How to get it:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Get Client ID, Client Secret, and Refresh Token

**Where to add it:**
```bash
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token
```

**Alternative:** Use SMTP instead (simpler setup, see below)

---

### 3. **SMTP Credentials** (Priority: HIGH - Alternative to Gmail API)

**When you need it:**
- When you prefer SMTP over Gmail API (simpler setup)
- When you want to send emails from any email provider

**What happens without it:**
- ✅ System still works - emails are generated but not sent
- ❌ Email sending will fail

**How to get it:**
- For Gmail: Use App Password (not regular password)
  1. Go to Google Account → Security
  2. Enable 2-Step Verification
  3. Generate App Password
  4. Use that as SMTP_PASSWORD

**Where to add it:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

---

### 4. **Search API Keys** (Priority: LOW - Optional)

**When you need it:**
- When you want automatic website discovery via search engines
- When automation runs the "fetch_new_art_websites" job

**What happens without it:**
- ✅ System still works - you can manually add URLs
- ✅ You can use seed_websites.txt file
- ❌ Automatic website discovery via Google/Bing won't work
- ⚠️ You'll see warnings but system continues

**How to get it:**
- **Google Search API:**
  1. Go to [Google Cloud Console](https://console.cloud.google.com/)
  2. Enable Custom Search API
  3. Create API key
  4. Create Search Engine ID

- **Bing Search API:**
  1. Go to [Azure Portal](https://portal.azure.com/)
  2. Create Bing Search resource
  3. Get API key

**Where to add it:**
```bash
# Google Search (optional)
GOOGLE_SEARCH_API_KEY=your_key
GOOGLE_SEARCH_ENGINE_ID=your_engine_id

# Bing Search (optional)
BING_SEARCH_API_KEY=your_key
```

---

## 🚀 Recommended Setup Order

### Phase 1: Basic Testing (No API Keys Needed)
1. ✅ Test scraping websites manually
2. ✅ Test contact extraction
3. ✅ View dashboard and data

### Phase 2: Email Templates (No API Keys Needed)
1. ✅ Create email templates in Settings tab
2. ✅ Test template-based email generation
3. ✅ Review generated emails

### Phase 3: AI Email Generation (Need Gemini/OpenAI)
1. 🔑 Add `GEMINI_API_KEY` to `.env`
2. ✅ Test AI email generation
3. ✅ Compare AI vs template emails

### Phase 4: Email Sending (Need Gmail API or SMTP)
1. 🔑 Add Gmail API credentials OR SMTP credentials
2. ✅ Test sending emails
3. ✅ Enable automatic email sending

### Phase 5: Full Automation (Optional Search APIs)
1. 🔑 Add search API keys (optional)
2. ✅ Enable automatic website discovery
3. ✅ Let system run 24/7

---

## 📝 Example .env File

```bash
# ============================================
# REQUIRED FOR AI EMAIL GENERATION
# ============================================
GEMINI_API_KEY=your_gemini_api_key_here
# OR use OpenAI instead:
# OPENAI_API_KEY=your_openai_api_key_here
# AI_MODEL=gpt-4

# ============================================
# REQUIRED FOR SENDING EMAILS
# Choose ONE: Gmail API OR SMTP
# ============================================

# Option 1: Gmail API (more features)
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token

# Option 2: SMTP (simpler, works with any email)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your_email@gmail.com
# SMTP_PASSWORD=your_app_password

# ============================================
# OPTIONAL: Website Discovery
# ============================================
# GOOGLE_SEARCH_API_KEY=your_key
# GOOGLE_SEARCH_ENGINE_ID=your_engine_id
# BING_SEARCH_API_KEY=your_key

# ============================================
# OTHER SETTINGS (Optional)
# ============================================
DEBUG=False
SCHEDULER_ENABLED=True
MIN_QUALITY_SCORE=50
```

---

## ⚠️ Important Notes

1. **Never commit `.env` file to Git** - It's already in `.gitignore`
2. **API keys are loaded from `.env` file** - Create it in project root
3. **System gracefully handles missing keys** - Won't crash, just won't use that feature
4. **You can mix and match** - Use templates without AI, or AI without sending
5. **Test incrementally** - Add one API key at a time and test

---

## 🔍 How to Check if API Keys Are Working

### Test Gemini API:
```bash
# In Python shell or test script
from ai.gemini_client import GeminiClient
client = GeminiClient()
if client.model:
    print("✅ Gemini API is configured!")
else:
    print("❌ Gemini API key missing")
```

### Test Email Sending:
```bash
# Use the dashboard to generate and send a test email
# Or use the API endpoint:
POST /api/v1/emails/send
```

### Check Logs:
```bash
# Look for these messages in backend logs:
# ✅ "Gemini API initialized successfully"
# ❌ "GEMINI_API_KEY not configured"
```

---

## 💡 Pro Tips

1. **Start with templates** - They work without any API keys
2. **Add Gemini key when ready** - For personalized AI emails
3. **Use SMTP for simplicity** - Easier than Gmail API setup
4. **Search APIs are optional** - Manual URL entry works fine
5. **Test in manual mode first** - Before enabling automation

---

## 🆘 Troubleshooting

**"GEMINI_API_KEY not configured" warning:**
- ✅ This is normal if you haven't added the key yet
- ✅ System will use templates instead
- 🔑 Add key to `.env` when ready for AI emails

**Email sending fails:**
- Check if Gmail API credentials are correct
- OR check if SMTP credentials are correct
- Make sure you're using App Password (not regular password) for Gmail SMTP

**API key not loading:**
- Make sure `.env` file is in project root (same folder as `main.py`)
- Restart the backend after adding keys
- Check for typos in variable names (must be exact: `GEMINI_API_KEY`)

---

## 📞 When to Provide API Keys

**You can provide them:**
- ✅ **Right now** - If you want to test AI email generation
- ✅ **After testing scraping** - Once you've verified basic functionality
- ✅ **When ready to send emails** - Before enabling automatic sending
- ✅ **Anytime** - System adapts to what's available

**You DON'T need to provide them:**
- ❌ To test scraping (works without keys)
- ❌ To test contact extraction (works without keys)
- ❌ To use email templates (works without keys)
- ❌ To view dashboard (works without keys)

**Best practice:** Start without keys, test everything, then add keys incrementally as you need each feature.

