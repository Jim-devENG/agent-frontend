# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your API keys:
# - GEMINI_API_KEY (or OPENAI_API_KEY)
# - GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN
#   OR SMTP_USER, SMTP_PASSWORD
```

### 3. Run the Application

```bash
python main.py
```

The application will:
- ✅ Create database automatically
- ✅ Start 24/7 automation pipeline
- ✅ Launch API server at http://localhost:8000

## 📊 Access Dashboard API

- **API Base**: http://localhost:8000/api/v1
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🎯 Key Endpoints

```bash
# Get statistics
GET http://localhost:8000/api/v1/stats

# Get leads
GET http://localhost:8000/api/v1/leads?skip=0&limit=50

# Get sent emails
GET http://localhost:8000/api/v1/emails/sent

# Get pending emails
GET http://localhost:8000/api/v1/emails/pending

# Scrape a URL
POST http://localhost:8000/api/v1/scrape-url?url=https://example.com

# Get job status
GET http://localhost:8000/api/v1/jobs/latest
```

## 🔄 Automation Running

The system automatically runs these jobs 24/7:

1. **Weekly Discovery** (Monday 3 AM) - Finds new websites
2. **Scraping** (Every 6h) - Processes pending websites
3. **Contact Extraction** (Every 4h) - Extracts contacts
4. **Email Generation** (Every 2h) - Generates AI emails
5. **Email Sending** (Hourly) - Sends outreach emails

## 📝 Add Seed URLs

Edit `seed_websites.txt` to add URLs manually:

```
https://example-art-gallery.com
https://example-interior-design.com
```

## ✅ Verify Setup

Run verification script:

```bash
python verify_setup.py
```

## 🐛 Troubleshooting

**Database not created?**
- Check file permissions
- Ensure SQLite is available

**Scheduler not starting?**
- Check `SCHEDULER_ENABLED=True` in .env
- Check logs for errors

**API not responding?**
- Check port 8000 is available
- Verify all dependencies installed
- Check CORS settings

## 📚 Next Steps

1. **Build Frontend**: Use the API endpoints to build a Next.js dashboard
2. **Monitor Jobs**: Check `/jobs/latest` to see automation status
3. **Add Seed URLs**: Populate `seed_websites.txt` with target websites
4. **Configure Quality**: Adjust quality thresholds in `.env`

## 🎉 You're Ready!

The system is now running 24/7, automatically discovering, scraping, and reaching out to art-related websites!

