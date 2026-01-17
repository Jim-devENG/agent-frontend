# Phase 6 Complete - Gmail Send Functionality

## ✅ What's Been Built

### 1. Gmail Client (`worker/clients/gmail.py`)
- Async HTTP client for Gmail API
- OAuth2 token management (access + refresh tokens)
- Automatic token refresh on 401 errors
- Email sending via Gmail API
- User profile retrieval

### 2. Send Task (`worker/tasks/send.py`)
- RQ task that processes send jobs
- Sends emails to prospects with drafts
- Creates email log entries
- Updates prospect status to "sent"
- Rate limiting (1 second between sends)
- Error handling and retry logic

### 3. Backend Integration
- `POST /api/prospects/{id}/send` now fully functional
- Uses Gmail API to send emails
- Creates email log entries
- Updates prospect status
- New endpoint: `POST /api/jobs/send` for bulk sending

### 4. Worker Updates
- Worker now listens to `discovery`, `enrichment`, `scoring`, and `send` queues

## 🔄 How It Works

### Single Email Send
```
User → POST /api/prospects/{id}/send
  ↓
Backend fetches prospect
  ↓
Calls Gmail API to send email
  ↓
Creates email log entry
  ↓
Updates prospect status to "sent"
  ↓
Returns send result
```

### Bulk Email Send
```
User → POST /api/jobs/send
  ↓
Backend creates Job record
  ↓
Queues RQ task to Redis
  ↓
Worker picks up task
  ↓
Finds prospects with drafts
  ↓
Sends emails via Gmail API
  ↓
Creates email logs
  ↓
Updates prospect statuses
  ↓
Updates Job status
```

## 📧 Email Sending Features

- **OAuth2 Authentication**: Uses access token or refresh token
- **Automatic Token Refresh**: Refreshes expired tokens automatically
- **Rate Limiting**: 1 second delay between sends
- **Error Handling**: Continues processing even if one email fails
- **Email Logging**: All sent emails logged with Gmail message IDs
- **Status Updates**: Prospect status updated to "sent"

## 📁 Project Structure

```
worker/
├── clients/
│   ├── dataforseo.py    ✅
│   ├── hunter.py        ✅
│   ├── gemini.py        ✅
│   └── gmail.py         ✅ NEW
├── tasks/
│   ├── discovery.py      ✅
│   ├── enrichment.py    ✅
│   ├── scoring.py       ✅
│   └── send.py          ✅ NEW
└── worker.py            ✅ Updated
```

## 🚀 Next Steps

**Phase 7**: Implement follow-ups and reply handling
- Scheduled follow-up emails
- Gmail webhook/polling for replies
- Update prospect status on reply

## ⚙️ Configuration

Required environment variables:
- `GMAIL_ACCESS_TOKEN` - OAuth2 access token (or)
- `GMAIL_REFRESH_TOKEN` - OAuth2 refresh token
- `GMAIL_CLIENT_ID` - OAuth2 client ID (for refresh)
- `GMAIL_CLIENT_SECRET` - OAuth2 client secret (for refresh)

## 🔐 OAuth2 Setup

To get Gmail credentials:
1. Go to Google Cloud Console
2. Create OAuth2 credentials
3. Authorize application
4. Get access token and refresh token
5. Set in environment variables

## 🧪 Testing

To test locally:
1. Set Gmail OAuth2 credentials in environment
2. Ensure prospect has email and draft
3. Send email: `POST /api/prospects/{id}/send`
4. Check email log: `GET /api/prospects/{id}`
5. Verify email in Gmail sent folder

## 📊 Bulk Sending

To send to multiple prospects:
```bash
POST /api/jobs/send?max_prospects=50&auto_send=true
```

This will:
- Find top 50 prospects with drafts
- Send emails automatically
- Create email logs
- Update all statuses

