# Phase 7 Complete - Follow-ups and Reply Handling

## ✅ What's Been Built

### 1. Follow-up Task (`worker/tasks/followup.py`)
- RQ task that processes follow-up jobs
- Finds prospects that need follow-ups:
  - Status is "sent"
  - Last sent > X days ago (default: 7 days)
  - Follow-ups sent < max (default: 3)
- Composes follow-up email using Gemini
- Sends via Gmail API
- Updates prospect followup count and last_sent

### 2. Reply Handler (`worker/tasks/reply_handler.py`)
- Task to check for email replies
- Updates prospect status to "replied" when reply detected
- Placeholder for Gmail webhook integration
- Can be called manually or scheduled

### 3. Scheduler (`backend/app/scheduler.py`)
- APScheduler for periodic tasks
- Daily follow-up emails (9 AM)
- Reply checks every 6 hours
- Automatic job queuing

### 4. Backend Integration
- New endpoint: `POST /api/jobs/followup` to queue follow-up jobs
- New endpoint: `POST /api/jobs/check-replies` to manually check replies
- Webhook endpoint: `POST /api/gmail/webhook` for Gmail push notifications
- Scheduler starts automatically on backend startup

### 5. Worker Updates
- Worker now listens to `discovery`, `enrichment`, `scoring`, `send`, and `followup` queues

## 🔄 How It Works

### Follow-up Emails
```
Scheduler (daily 9 AM) → Queue follow-up job
  ↓
Worker picks up task
  ↓
Finds prospects needing follow-ups
  ↓
Composes follow-up using Gemini
  ↓
Sends via Gmail
  ↓
Updates prospect (followups_sent++, last_sent)
```

### Reply Handling
```
Scheduler (every 6 hours) → Queue reply check
  ↓
Worker picks up task
  ↓
Checks Gmail for replies
  ↓
Updates prospect status to "replied"
```

### Gmail Webhook (Future)
```
Gmail → POST /api/gmail/webhook
  ↓
Backend processes notification
  ↓
Identifies prospect by email
  ↓
Updates status to "replied"
```

## 📧 Follow-up Logic

- **Timing**: Sends follow-up X days after last email (default: 7 days)
- **Limit**: Maximum N follow-ups per prospect (default: 3)
- **Composition**: Uses Gemini to generate personalized follow-up
- **Subject**: Adds "Re:" prefix to indicate follow-up
- **Body**: Includes follow-up context and original message

## 📁 Project Structure

```
worker/
├── tasks/
│   ├── discovery.py      ✅
│   ├── enrichment.py     ✅
│   ├── scoring.py        ✅
│   ├── send.py           ✅
│   ├── followup.py       ✅ NEW
│   └── reply_handler.py ✅ NEW
└── worker.py            ✅ Updated

backend/
├── app/
│   ├── scheduler.py      ✅ NEW
│   └── api/
│       └── webhooks.py   ✅ NEW
└── main.py              ✅ Updated
```

## 🚀 Next Steps

**Phase 8**: Build Next.js frontend dashboard
- Dashboard with job controls
- Prospect list with filters
- Email composition interface
- Job status monitoring

## ⚙️ Configuration

Scheduler jobs can be configured in `backend/app/scheduler.py`:
- Follow-up schedule: `CronTrigger(hour=9, minute=0)` (9 AM daily)
- Reply check: `IntervalTrigger(hours=6)` (every 6 hours)

## 🧪 Testing

To test locally:
1. Ensure prospects with "sent" status exist
2. Wait 7+ days or manually update `last_sent` to past date
3. Create follow-up job: `POST /api/jobs/followup?days_since_sent=0`
4. Watch worker process the job
5. Check prospects: `GET /api/prospects?status=sent`

## 📝 Notes

- **Gmail Webhook**: Currently placeholder - requires Gmail Cloud Pub/Sub setup
- **Reply Detection**: Simplified version - in production, implement proper Gmail thread checking
- **Scheduler**: Runs in backend process - consider separate scheduler service for production

