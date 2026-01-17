# Gmail OAuth 2.0 Setup Guide

## Overview

This system uses **OAuth 2.0 with offline access** for server-side Gmail sending. This is the recommended approach for backend email automation.

## OAuth Model

**Server-Side OAuth (NOT Browser-Based)**

- Backend sends emails on behalf of a Gmail account
- Uses refresh tokens for long-lived access
- No user interaction required after initial setup
- Tokens stored in environment variables (secure)

## Required Setup Steps

### 1. Create OAuth 2.0 Credentials in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Gmail API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

4. Create OAuth 2.0 Client ID:
   - Navigate to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: **"Web application"** (even for backend)
   - Name: "LiquidCanvas Gmail Sender" (or your choice)
   - **Authorized redirect URIs**: 
     - For testing: `https://developers.google.com/oauthplayground`
     - For production: Your backend callback URL (if using OAuth flow)
     - **Note**: For refresh token generation, OAuth Playground is recommended

### 2. Configure OAuth Consent Screen

1. Navigate to "APIs & Services" > "OAuth consent screen"
2. User Type: **External** (for testing) or **Internal** (for Workspace)
3. Fill in required fields:
   - App name: "LiquidCanvas Outreach"
   - User support email: Your email
   - Developer contact: Your email

4. **Scopes** (CRITICAL):
   - Click "Add or Remove Scopes"
   - Add: `https://www.googleapis.com/auth/gmail.send`
   - **DO NOT** add read scopes unless required
   - Save

5. **Test Users** (if app is in testing mode):
   - Add the Gmail account email that will send emails
   - This account must be added as a test user

6. **Publishing** (for production):
   - If app is in testing mode, only test users can use it
   - For production, submit for verification (or keep in testing with test users)

### 3. Generate Refresh Token

#### Option A: Using OAuth Playground (Recommended)

1. Go to [OAuth 2.0 Playground](https://developers.google.com/oauthplayground)
2. Click gear icon (⚙️) in top right
3. Check "Use your own OAuth credentials"
4. Enter your **Client ID** and **Client Secret** from Google Cloud Console
5. In left panel, find "Gmail API v1"
6. Select scope: `https://www.googleapis.com/auth/gmail.send`
7. Click "Authorize APIs"
8. Sign in with the Gmail account that will send emails
9. Click "Allow" to grant permissions
10. Click "Exchange authorization code for tokens"
11. Copy the **Refresh token** (long string)
12. Copy the **Access token** (optional, expires in 1 hour)

#### Option B: Using Backend OAuth Flow (Advanced)

If you implement a full OAuth flow in your backend:
- Redirect URI must match what's configured in Google Cloud Console
- Must request `access_type=offline` and `prompt=consent` to get refresh token
- Store refresh token securely

### 4. Set Environment Variables

Add these to your `.env` file or deployment environment (e.g., Render.com):

```bash
# Option 1: Using Refresh Token (Recommended - Auto-refreshes)
GMAIL_REFRESH_TOKEN=your_refresh_token_here
GMAIL_CLIENT_ID=your_client_id_here
GMAIL_CLIENT_SECRET=your_client_secret_here

# Option 2: Using Access Token (Temporary - Expires in 1 hour)
# GMAIL_ACCESS_TOKEN=your_access_token_here
```

**Security Notes:**
- Never commit these to git
- Use environment variables in production
- Rotate tokens if compromised
- Consider using a secrets manager for production

### 5. Verify Configuration

Check Gmail configuration status:

```bash
# Via API
GET /api/health/gmail

# Expected response:
{
  "status": "configured",
  "has_refresh_token": true,
  "has_client_id": true,
  "has_client_secret": true,
  "token_refresh_test": "success",
  "ready_to_send": true
}
```

## How Token Refresh Works

1. **Initial State**: System has refresh token, client ID, and secret
2. **On Send**: If access token missing or expired:
   - System calls Google OAuth token endpoint
   - Exchanges refresh token for new access token
   - Stores access token in memory (not persisted)
   - Uses access token for Gmail API calls
3. **On 401 Error**: If Gmail API returns 401:
   - System automatically refreshes token
   - Retries the send request
   - Fails if refresh token is invalid

## Troubleshooting

### Error: "Failed to obtain Gmail access token"

**Causes:**
1. Refresh token missing or invalid
2. Client ID/Secret mismatch
3. Refresh token expired or revoked
4. OAuth consent screen not configured

**Solutions:**
1. Check `/api/health/gmail` endpoint
2. Verify environment variables are set correctly
3. Generate new refresh token from OAuth Playground
4. Ensure test user is added (if app in testing mode)

### Error: "invalid_grant"

**Causes:**
- Refresh token expired or revoked
- User revoked access
- Token was generated for different client ID/Secret

**Solutions:**
- Generate new refresh token
- Ensure client ID/Secret match the ones used to generate token

### Error: "invalid_client"

**Causes:**
- Client ID or Client Secret is incorrect
- Credentials don't match OAuth Playground settings

**Solutions:**
- Verify credentials in Google Cloud Console
- Ensure no extra spaces or characters in env vars

### Error: "403 Forbidden"

**Causes:**
- OAuth scope `gmail.send` not granted
- App not verified (if in production)
- User hasn't granted permission

**Solutions:**
- Verify scope is added in OAuth consent screen
- Ensure test user is added (if in testing mode)
- Re-authorize in OAuth Playground

## Token Storage

**Current Implementation:**
- Tokens stored in environment variables
- Access tokens are in-memory only (not persisted)
- Refresh tokens are long-lived and stored in env vars

**Security Best Practices:**
- Use environment variables (never hardcode)
- Rotate refresh tokens periodically
- Monitor `/api/health/gmail` for token issues
- Use secrets manager in production (AWS Secrets Manager, etc.)

## What Breaks If Tokens Are Revoked?

1. **Refresh Token Revoked**:
   - All sends fail with "Failed to obtain Gmail access token"
   - Must generate new refresh token
   - No data loss, just sending disabled

2. **Access Token Expired** (Normal):
   - System auto-refreshes using refresh token
   - No user action needed
   - Sends continue working

3. **User Revokes Access**:
   - Refresh token becomes invalid
   - Must re-authorize in OAuth Playground
   - Generate new refresh token

## Required Gmail API Scope

**Minimum Required:**
```
https://www.googleapis.com/auth/gmail.send
```

**What This Allows:**
- Send emails via Gmail API
- Does NOT allow reading emails
- Does NOT allow modifying drafts
- Send-only access (secure)

## Testing

1. **Health Check**:
   ```bash
   curl https://your-api.com/api/health/gmail
   ```

2. **Manual Send Test**:
   - Create a draft via compose endpoint
   - Send via `/api/prospects/{id}/send`
   - Check logs for token refresh messages

3. **Pipeline Send Test**:
   - Use Pipeline → Send card
   - Monitor job status
   - Check email logs

## Production Checklist

- [ ] OAuth consent screen configured
- [ ] Required scope (`gmail.send`) added
- [ ] Test users added (if in testing mode)
- [ ] Refresh token generated and stored securely
- [ ] Environment variables set in deployment
- [ ] `/api/health/gmail` returns "ready_to_send": true
- [ ] Test send works end-to-end
- [ ] Monitoring set up for token refresh failures

## Support

If issues persist:
1. Check `/api/health/gmail` for detailed diagnostics
2. Review backend logs for Gmail API errors
3. Verify OAuth credentials in Google Cloud Console
4. Test token refresh manually in OAuth Playground

