# Quick Deployment Checklist for agent.liquidcanvas.art

## Pre-Deployment Checklist

- [ ] Server with Ubuntu 20.04+ ready
- [ ] **DNS configured in Wix**: A record `agent` → Server IP (see WIX_DNS_SETUP.md)
- [ ] DNS propagated (check with `nslookup agent.liquidcanvas.art`)
- [ ] Server has Python 3.11+, Node.js 18+, Nginx installed
- [ ] API keys ready (Gemini, OpenAI, SMTP, etc.)

**Note**: Since `liquidcanvas.art` is on Wix, add the subdomain DNS record in Wix dashboard.

## Quick Deploy Steps

### 0. Configure DNS in Wix (Do This First!)

**Important**: Since your domain is on Wix, configure DNS before deployment.

1. Log in to Wix → Domains → Select `liquidcanvas.art`
2. Go to DNS Settings
3. Add A Record:
   - Name: `agent`
   - Type: A
   - Value: Your server IP
4. Save and wait 5-30 minutes for propagation
5. Verify: `nslookup agent.liquidcanvas.art`

**See WIX_DNS_SETUP.md for detailed instructions.**

### 1. Upload Code to Server

```bash
# On your local machine
scp -r . user@your-server:/var/www/agent.liquidcanvas.art
```

### 2. On Server - Initial Setup

```bash
# SSH into server
ssh user@your-server

# Navigate to app directory
cd /var/www/agent.liquidcanvas.art

# Make deploy script executable
chmod +x deploy.sh

# Run initial setup
sudo ./deploy.sh
```

### 3. Configure Nginx

```bash
# Copy nginx config
sudo cp nginx/agent.liquidcanvas.art.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/agent.liquidcanvas.art.conf /etc/nginx/sites-enabled/

# Test nginx config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### 4. Setup SSL Certificate

```bash
# Get SSL certificate
sudo certbot --nginx -d agent.liquidcanvas.art

# Test auto-renewal
sudo certbot renew --dry-run
```

### 5. Setup Systemd Services

```bash
# Copy service files
sudo cp systemd/art-outreach-backend.service /etc/systemd/system/
sudo cp systemd/art-outreach-frontend.service /etc/systemd/system/

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable art-outreach-backend
sudo systemctl enable art-outreach-frontend
sudo systemctl start art-outreach-backend
sudo systemctl start art-outreach-frontend
```

### 6. Configure Environment

```bash
# Create production .env
cd /var/www/agent.liquidcanvas.art
cp .env.production.example .env
nano .env  # Edit with your API keys and settings
```

### 7. Verify Deployment

```bash
# Check services
sudo systemctl status art-outreach-backend
sudo systemctl status art-outreach-frontend

# Check logs
sudo journalctl -u art-outreach-backend -f
sudo journalctl -u art-outreach-frontend -f

# Test endpoints
curl https://agent.liquidcanvas.art/health
curl https://agent.liquidcanvas.art/api/v1/stats
```

## Post-Deployment

- [ ] Test frontend: https://agent.liquidcanvas.art
- [ ] Test API: https://agent.liquidcanvas.art/api/v1/stats
- [ ] Verify SSL certificate
- [ ] Check CORS is working
- [ ] Test scraping functionality
- [ ] Monitor logs for errors

## Common Commands

```bash
# Restart services
sudo systemctl restart art-outreach-backend
sudo systemctl restart art-outreach-frontend

# View logs
sudo journalctl -u art-outreach-backend -n 50
sudo journalctl -u art-outreach-frontend -n 50

# Update and redeploy
cd /var/www/agent.liquidcanvas.art
git pull  # or upload new files
sudo ./deploy.sh
```

## Troubleshooting

**502 Bad Gateway**: Services not running
```bash
sudo systemctl status art-outreach-backend
sudo systemctl status art-outreach-frontend
```

**CORS Errors**: Check CORS_ORIGINS in .env
```bash
grep CORS_ORIGINS .env
```

**SSL Issues**: Renew certificate
```bash
sudo certbot renew
```

**Database Issues**: Check PostgreSQL
```bash
sudo systemctl status postgresql
```

