# Server Setup Checklist

Use this checklist to track your deployment progress.

## Pre-Deployment

- [ ] **Server/VPS purchased** (DigitalOcean, AWS, etc.)
- [ ] **Server IP address noted**
- [ ] **SSH access working** (can connect to server)
- [ ] **DNS configured in Wix**:
  - [ ] Logged into Wix
  - [ ] Added A record: `agent` → Server IP
  - [ ] Waited 5-30 minutes
  - [ ] Verified DNS: `nslookup agent.liquidcanvas.art`

## Server Setup

- [ ] **System updated**: `sudo apt update && sudo apt upgrade -y`
- [ ] **Python 3.11 installed**: `python3.11 --version`
- [ ] **Node.js 18+ installed**: `node --version`
- [ ] **Nginx installed**: `nginx -v`
- [ ] **Certbot installed**: `certbot --version`
- [ ] **Git installed** (if using): `git --version`

## Code Deployment

- [ ] **Code uploaded to server** (`/var/www/agent.liquidcanvas.art`)
- [ ] **Backend virtual environment created**
- [ ] **Backend dependencies installed**: `pip install -r requirements.txt`
- [ ] **Playwright browsers installed**: `playwright install chromium`
- [ ] **Backend .env file created** with API keys
- [ ] **Frontend dependencies installed**: `npm install`
- [ ] **Frontend built**: `npm run build`
- [ ] **Frontend .env.production created**

## Configuration

- [ ] **Nginx config copied** to `/etc/nginx/sites-available/`
- [ ] **Nginx site enabled**: symlink created
- [ ] **Nginx config tested**: `sudo nginx -t`
- [ ] **Nginx reloaded**: `sudo systemctl reload nginx`
- [ ] **Systemd service files copied** to `/etc/systemd/system/`
- [ ] **Service files edited** (paths verified)
- [ ] **Systemd reloaded**: `sudo systemctl daemon-reload`

## Services

- [ ] **Backend service enabled**: `sudo systemctl enable art-outreach-backend`
- [ ] **Backend service started**: `sudo systemctl start art-outreach-backend`
- [ ] **Backend service status**: `sudo systemctl status art-outreach-backend` (running)
- [ ] **Frontend service enabled**: `sudo systemctl enable art-outreach-frontend`
- [ ] **Frontend service started**: `sudo systemctl start art-outreach-frontend`
- [ ] **Frontend service status**: `sudo systemctl status art-outreach-frontend` (running)

## SSL Certificate

- [ ] **DNS fully propagated** (verified with nslookup)
- [ ] **SSL certificate obtained**: `sudo certbot --nginx -d agent.liquidcanvas.art`
- [ ] **Auto-renewal tested**: `sudo certbot renew --dry-run`
- [ ] **HTTPS working**: https://agent.liquidcanvas.art

## Firewall

- [ ] **Port 80 allowed**: `sudo ufw allow 80/tcp`
- [ ] **Port 443 allowed**: `sudo ufw allow 443/tcp`
- [ ] **Port 22 allowed**: `sudo ufw allow 22/tcp`
- [ ] **Firewall enabled**: `sudo ufw enable`

## Permissions

- [ ] **Ownership set**: `sudo chown -R www-data:www-data /var/www/agent.liquidcanvas.art`
- [ ] **Permissions set**: `sudo chmod -R 755 /var/www/agent.liquidcanvas.art`

## Testing

- [ ] **Backend health check**: `curl http://localhost:8000/health`
- [ ] **Backend API**: `curl http://localhost:8000/api/v1/stats`
- [ ] **Frontend local**: `curl http://localhost:3000`
- [ ] **HTTPS frontend**: https://agent.liquidcanvas.art (opens in browser)
- [ ] **HTTPS API**: https://agent.liquidcanvas.art/api/v1/stats (returns JSON)
- [ ] **Scraping test**: Try scraping a URL from the dashboard
- [ ] **No CORS errors** in browser console

## Post-Deployment

- [ ] **Application fully functional**
- [ ] **Logs monitored** (no critical errors)
- [ ] **Backup strategy planned** (optional)
- [ ] **Monitoring set up** (optional)

## Quick Test Commands

```bash
# Test backend
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/stats

# Test frontend
curl http://localhost:3000

# Test from outside (after DNS/SSL)
curl https://agent.liquidcanvas.art/health
curl https://agent.liquidcanvas.art/api/v1/stats

# Check services
sudo systemctl status art-outreach-backend
sudo systemctl status art-outreach-frontend

# Check logs
sudo journalctl -u art-outreach-backend -n 20
sudo journalctl -u art-outreach-frontend -n 20
```

