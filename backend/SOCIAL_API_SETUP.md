# Social Media API Setup Guide

This guide explains how to configure real API access for social media discovery.

## Overview

The social discovery system supports **two methods** for finding profiles:

1. **Official Platform APIs** (Recommended) - Direct API access to each platform
2. **DataForSEO Fallback** - Uses Google search via DataForSEO to find social profiles

## Platform API Setup

### LinkedIn API

**Requirements:**
- LinkedIn Developer account
- LinkedIn app registration
- OAuth 2.0 access token

**Steps:**
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Create a new app
3. Request "People Search" API permission
4. Generate an access token
5. Set environment variable: `LINKEDIN_ACCESS_TOKEN=your_token_here`

**Note:** LinkedIn API has strict access requirements and may require partnership approval for certain endpoints.

### Instagram Graph API (Meta)

**Requirements:**
- Meta Developer account
- Facebook app creation
- Instagram Business account
- App Review approval

**Steps:**
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Instagram Basic Display or Instagram Graph API product
4. Request required permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
5. Complete App Review process
6. Generate access token
7. Set environment variable: `INSTAGRAM_ACCESS_TOKEN=your_token_here`

**Note:** Instagram API requires business accounts and App Review approval.

### Facebook Graph API (Meta)

**Requirements:**
- Meta Developer account
- Facebook app creation
- App Review approval

**Steps:**
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Facebook Login product
4. Request permissions:
   - `pages_read_engagement`
   - `pages_show_list`
5. Complete App Review process
6. Generate access token
7. Set environment variable: `FACEBOOK_ACCESS_TOKEN=your_token_here`

### TikTok API

**Requirements:**
- TikTok Developer account
- App registration
- API access approval

**Steps:**
1. Go to [TikTok for Developers](https://developers.tiktok.com/)
2. Register as a developer
3. Create an application
4. Request API access
5. Get client key and secret
6. Set environment variables:
   - `TIKTOK_CLIENT_KEY=your_key_here`
   - `TIKTOK_CLIENT_SECRET=your_secret_here`

**Note:** TikTok API access is restricted and may require partnership status.

## DataForSEO Fallback (No Platform APIs Required)

If you don't have platform API credentials, the system automatically falls back to using **DataForSEO** to search Google for social profiles.

**Requirements:**
- DataForSEO account (already configured for website discovery)
- `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` environment variables

**How it works:**
- Searches Google with queries like: `site:linkedin.com/in/ [category] [location]`
- Extracts profile URLs from search results
- Creates prospects from discovered profiles

**Advantages:**
- No platform API approval needed
- Works immediately with existing DataForSEO credentials
- Finds public profiles across all platforms

**Limitations:**
- May not find all profiles (limited by Google search results)
- Profile data may be less detailed than direct API access

## Current Behavior

**Without Platform API Credentials:**
- System uses DataForSEO to search for social profiles
- Finds real profiles via Google search
- Works immediately (no additional setup needed)

**With Platform API Credentials:**
- System uses official platform APIs for direct access
- More comprehensive profile data
- Better search capabilities
- Requires API setup and approval

## Environment Variables

Add these to your `.env` file or Render environment variables:

```bash
# Platform API Credentials (Optional - enables direct API access)
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
FACEBOOK_ACCESS_TOKEN=your_facebook_token
TIKTOK_CLIENT_KEY=your_tiktok_key
TIKTOK_CLIENT_SECRET=your_tiktok_secret

# DataForSEO (Required for fallback - already configured)
DATAFORSEO_LOGIN=your_dataforseo_login
DATAFORSEO_PASSWORD=your_dataforseo_password
```

## Testing

After setting up credentials, test each platform in the Settings page:
- Go to Settings → Services
- Click "Test" for each platform
- Verify API connectivity

## Troubleshooting

**"API permissions not granted" errors:**
- Ensure you've requested the correct permissions in your app
- Complete App Review process (for Meta platforms)
- Verify access token is valid and not expired

**"Access token is invalid or expired":**
- Generate a new access token
- For OAuth tokens, implement token refresh logic
- Check token expiration and renew as needed

**DataForSEO fallback not working:**
- Verify `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` are set
- Test DataForSEO connection in Settings
- Check DataForSEO account has sufficient credits

## Next Steps

1. **Start with DataForSEO** - Works immediately, finds real profiles
2. **Add platform APIs gradually** - Set up one platform at a time
3. **Monitor results** - Compare API vs DataForSEO discovery quality
4. **Optimize queries** - Adjust search parameters for better results

