# Hunter.io API Setup Guide

This guide explains how to set up and use Hunter.io API for enhanced email extraction.

## What is Hunter.io?

Hunter.io is a professional email finder service that:
- Finds emails associated with domains
- Verifies email addresses
- Provides email patterns (e.g., `{first}.{last}@domain.com`)
- Includes metadata (names, positions, social links)

## Getting Your API Key

1. **Sign up for Hunter.io**
   - Go to https://hunter.io
   - Create a free account (25 searches/month) or paid plan

2. **Get Your API Key**
   - Log in to your Hunter.io account
   - Go to Settings → API
   - Copy your API key

3. **Add to Environment Variables**
   - Open your `.env` file
   - Add: `HUNTER_IO_API_KEY=your_api_key_here`
   - Save the file

## Features Enabled

Once configured, the system will:

1. **Domain Search**: Automatically search for all emails associated with a domain
2. **Email Verification**: Verify found emails are deliverable
3. **Pattern Discovery**: Learn email patterns (e.g., `firstname.lastname@domain.com`)
4. **Metadata Enrichment**: Get names, positions, LinkedIn profiles

## Usage

The enhanced email extractor automatically uses Hunter.io when:
- A website is scraped
- Contact extraction runs
- The API key is configured

## API Limits

- **Free Plan**: 25 searches/month
- **Starter Plan**: 500 searches/month ($49/month)
- **Growth Plan**: 5,000 searches/month ($149/month)
- **Pro Plan**: 50,000 searches/month ($499/month)

## Cost Optimization

The system uses Hunter.io intelligently:
- Only searches domains that haven't been searched recently
- Caches results to avoid duplicate API calls
- Falls back to standard extraction if API fails

## Troubleshooting

**"Hunter.io API key not configured"**
- Check that `HUNTER_IO_API_KEY` is in your `.env` file
- Restart the backend server after adding the key

**"API request failed"**
- Check your API key is correct
- Verify you haven't exceeded your monthly limit
- Check your internet connection

**No emails found via Hunter.io**
- Some domains may not have emails in Hunter.io's database
- The system will still use standard extraction methods
- Try searching the domain manually on hunter.io to verify

## Example

After adding your API key, when scraping `liquidcanvas.art`:
1. System extracts emails from HTML (standard method)
2. System queries Hunter.io for `liquidcanvas.art`
3. Hunter.io returns: `info@liquidcanvas.art`, `contact@liquidcanvas.art`
4. All emails are combined and saved

## Benefits

- **More Emails**: Finds emails not visible on the website
- **Verified**: Only returns deliverable emails
- **Enriched**: Includes names, positions, social links
- **Patterns**: Learns email patterns for future searches

