# Wix DNS Setup for agent.liquidcanvas.art

Since your main domain `liquidcanvas.art` is hosted on Wix, you need to configure the subdomain `agent.liquidcanvas.art` to point to your server.

## Step-by-Step: Adding Subdomain in Wix

### Method 1: Wix Dashboard

1. **Log in to Wix**
   - Go to https://www.wix.com
   - Sign in to your account

2. **Navigate to Domains**
   - Click on your profile/account menu
   - Go to **Domains** or **My Domains**
   - Find and select `liquidcanvas.art`

3. **Access DNS Settings**
   - Click **Manage DNS** or **DNS Settings**
   - Look for **DNS Records** or **Advanced DNS Settings**

4. **Add A Record**
   - Click **Add Record** or **+ Add**
   - Select **A Record** (or **A**)
   - Fill in:
     - **Host/Name**: `agent` (just "agent", not "agent.liquidcanvas.art")
     - **Points to/Value**: Your server's IP address (e.g., `123.45.67.89`)
     - **TTL**: `3600` (or leave default)
   - Click **Save** or **Add Record**

5. **Verify**
   - The record should appear in your DNS records list
   - Wait 5-30 minutes for DNS propagation

### Method 2: If Wix Doesn't Allow Subdomain DNS

If Wix doesn't allow you to add subdomain DNS records directly, you have two options:

#### Option A: Use External DNS (Recommended)

1. **Transfer DNS Management to External Provider**
   - Use a DNS provider like:
     - Cloudflare (free)
     - AWS Route 53
     - Google Cloud DNS
     - Namecheap DNS
   
2. **Point Domain to External DNS**
   - In Wix, change nameservers to your DNS provider
   - Add A record for `agent.liquidcanvas.art` in the external DNS provider
   - Keep main domain on Wix (if possible) or move entirely

#### Option B: Use Cloudflare (Easiest)

1. **Sign up for Cloudflare** (free)
2. **Add Domain**
   - Add `liquidcanvas.art` to Cloudflare
3. **Update Nameservers in Wix**
   - Cloudflare will provide nameservers
   - Update nameservers in Wix to point to Cloudflare
4. **Add DNS Records in Cloudflare**
   - Add A record: `agent` → Your server IP
   - Keep existing records for main domain
5. **Wix Integration**
   - Configure Cloudflare to proxy main domain to Wix (if needed)
   - Or keep main domain on Wix and only manage subdomain in Cloudflare

## Verify DNS Propagation

After adding the DNS record, verify it's working:

```bash
# Check DNS resolution
nslookup agent.liquidcanvas.art
# or
dig agent.liquidcanvas.art

# Should return your server IP address
```

**Online Tools:**
- https://dnschecker.org
- https://www.whatsmydns.net
- Enter: `agent.liquidcanvas.art`
- Should show your server IP globally

## Testing Locally

Once DNS is configured:

```bash
# Test from your server
curl -I http://agent.liquidcanvas.art
curl -I https://agent.liquidcanvas.art
```

## Important Notes

1. **DNS Propagation**: Can take 5 minutes to 48 hours (usually 5-30 minutes)
2. **SSL Certificate**: Can only be issued after DNS is fully propagated
3. **Main Domain**: Stays on Wix, only subdomain points to your server
4. **Wix Limitations**: Some Wix plans may not allow custom DNS records - check your plan

## Troubleshooting

**Subdomain not resolving:**
- Wait longer for DNS propagation
- Check DNS record is correct in Wix
- Verify server IP is correct
- Use `nslookup` or `dig` to check DNS

**Can't add DNS record in Wix:**
- Your Wix plan may not support custom DNS
- Consider using Cloudflare (free) for DNS management
- Contact Wix support for assistance

**SSL certificate fails:**
- DNS must be fully propagated first
- Wait 30+ minutes after DNS setup
- Run `certbot` again after DNS is ready

## Next Steps

Once DNS is configured and propagated:

1. Verify DNS: `nslookup agent.liquidcanvas.art`
2. Deploy application to server
3. Configure Nginx
4. Get SSL certificate: `sudo certbot --nginx -d agent.liquidcanvas.art`
5. Test: https://agent.liquidcanvas.art

