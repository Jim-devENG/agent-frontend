# Autonomous Art Outreach Scraper - Project Summary

## 🎯 Project Overview

A production-grade Python web application that autonomously scrapes art-related websites, extracts contact information, generates personalized outreach emails using AI, and sends them automatically - running 24/7.

## ✅ Completed Phases

### Phase 1: Foundation
- ✅ Complete folder structure
- ✅ FastAPI backend setup
- ✅ SQLAlchemy database models
- ✅ Configuration management
- ✅ All module placeholders

### Phase 2: Scraping Engine
- ✅ Website scraping with JS fallback (Playwright)
- ✅ Social media scraping (Instagram, TikTok, Behance, Pinterest)
- ✅ Art detection with 7 categories
- ✅ Quality filtering (domain authority, traffic, SSL, DNS)
- ✅ Rate limiting and error handling

### Phase 3: Contact Extraction
- ✅ Email extraction (regex + BeautifulSoup)
- ✅ Phone number extraction
- ✅ Social link extraction (10+ platforms)
- ✅ Contact form detection
- ✅ Contact page crawler (/contact, /about, etc.)
- ✅ Database storage

### Phase 4: LLM Integration
- ✅ Gemini API integration
- ✅ OpenAI API integration
- ✅ Business context-aware email generation
- ✅ Personalized outreach emails

### Phase 5: Email Sender
- ✅ Gmail API integration
- ✅ SMTP support
- ✅ HTML email formatting
- ✅ Retry logic (3 attempts with exponential backoff)
- ✅ Database logging

### Phase 6: Automation Pipeline
- ✅ 24/7 automation with APScheduler
- ✅ 5 scheduled jobs:
  1. Fetch new websites (weekly)
  2. Scrape pending websites (every 6h)
  3. Extract contacts (every 4h)
  4. Generate AI emails (every 2h)
  5. Send emails (hourly)
- ✅ Database job logging

### Phase 7: Dashboard API
- ✅ `/leads` - Get leads with pagination
- ✅ `/emails/sent` - Get sent emails
- ✅ `/emails/pending` - Get pending emails
- ✅ `/scrape-url` - Manual URL scraping
- ✅ `/stats` - Comprehensive statistics
- ✅ `/jobs/status` - Job status monitoring
- ✅ `/jobs/latest` - Latest job executions

## 📁 Project Structure

```
.
├── api/                    # REST API endpoints
│   ├── routes.py          # Main API routes
│   └── dashboard_routes.py # Dashboard endpoints
├── ai/                     # LLM integrations
│   ├── gemini_client.py
│   ├── openai_client.py
│   └── email_generator.py
├── db/                     # Database
│   ├── database.py        # SQLAlchemy setup
│   └── models.py           # Data models
├── emailer/                # Email sending
│   ├── gmail_client.py
│   ├── smtp_client.py
│   ├── html_formatter.py
│   ├── outreach_email_sender.py
│   └── email_sender.py
├── extractor/              # Contact extraction
│   ├── email_extractor.py
│   ├── phone_extractor.py
│   ├── social_extractor.py
│   ├── contact_form_extractor.py
│   ├── contact_page_crawler.py
│   └── contact_extraction_service.py
├── jobs/                   # Background jobs
│   ├── scheduler.py        # APScheduler setup
│   ├── automation_jobs.py # 5 automation jobs
│   └── website_discovery.py
├── scraper/                # Web scraping
│   ├── base_scraper.py
│   ├── website_scraper.py
│   ├── social_scraper.py
│   ├── scraper_service.py
│   ├── domain_analyzer.py
│   ├── art_detector.py
│   └── rate_limiter.py
├── utils/                  # Utilities
│   ├── config.py
│   └── logging_config.py
├── main.py                 # FastAPI app
├── requirements.txt
├── seed_websites.txt
└── README.md
```

## 🗄️ Database Models

1. **ScrapedWebsite** - Websites with quality metrics
2. **Contact** - Emails, phones, social links
3. **ContactForm** - Detected contact forms
4. **OutreachEmail** - Generated and sent emails
5. **ScrapingJob** - Background job logs

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

4. **Access API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

## 📊 Dashboard Endpoints

All endpoints at `/api/v1/`:

- `GET /leads` - Leads with pagination
- `GET /emails/sent` - Sent emails
- `GET /emails/pending` - Pending emails
- `POST /scrape-url` - Scrape URL
- `GET /stats` - Statistics
- `GET /jobs/status` - Job status
- `GET /jobs/latest` - Latest jobs

## 🔄 Automation Pipeline

The system runs 24/7 with these scheduled jobs:

1. **Weekly Discovery** (Monday 3 AM)
   - Searches for new art websites
   - Pulls from seed list

2. **Scraping** (Every 6 hours)
   - Processes pending websites
   - Applies quality filters

3. **Contact Extraction** (Every 4 hours)
   - Extracts emails, phones, social links
   - Crawls contact pages

4. **Email Generation** (Every 2 hours)
   - Generates AI emails for contacts
   - Uses business context

5. **Email Sending** (Hourly)
   - Sends draft emails
   - Retry logic included

## 🎨 Target Categories

1. Interior Decor sites
2. Art Gallery sites
3. Home tech sites
4. Mom blogs sites
5. Tech sites for NFTs
6. Editorial media houses
7. Holiday/family oriented sites

## 🔧 Configuration

Key settings in `.env`:

```env
# AI
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key

# Email
GMAIL_CLIENT_ID=your_id
GMAIL_CLIENT_SECRET=your_secret
GMAIL_REFRESH_TOKEN=your_token

# Quality Filtering
MIN_QUALITY_SCORE=50
MIN_DOMAIN_AUTHORITY=30
REQUIRE_SSL=True
```

## 📈 Features

- ✅ Automatic website discovery
- ✅ Quality-based filtering
- ✅ Multi-category detection
- ✅ Comprehensive contact extraction
- ✅ AI-powered email generation
- ✅ Automated email sending
- ✅ 24/7 operation
- ✅ Full database logging
- ✅ Dashboard API ready
- ✅ TypeScript/Next.js compatible

## 🎯 Next Steps

1. **Frontend Development:**
   - Build Next.js dashboard
   - Connect to API endpoints
   - Display stats and leads

2. **Enhancements:**
   - Add Google/Bing search APIs
   - Implement email tracking
   - Add analytics dashboard
   - Create reporting features

3. **Deployment:**
   - Docker containerization
   - Production database (PostgreSQL)
   - Environment setup
   - Monitoring and alerts

## 📝 Notes

- All logs stored in database
- Jobs run automatically 24/7
- Quality filtering ensures high-quality leads
- Retry logic handles failures gracefully
- API ready for TypeScript/Next.js frontend

