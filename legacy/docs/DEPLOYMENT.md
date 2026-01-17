# Deployment Guide for agent.liquidcanvas.art

This guide covers deploying the Autonomous Art Outreach Scraper to `agent.liquidcanvas.art`.

## Architecture

- **Frontend**: Next.js app (port 3000) → served via nginx
- **Backend**: FastAPI app (port 8000) → served via nginx reverse proxy
- **Domain**: `agent.liquidcanvas.art`
- **SSL**: Let's Encrypt (via Certbot)

## Prerequisites

1. **Server Requirements**:
   - Ubuntu 20.04+ or similar Linux server
   - Python 3.11+
   - Node.js 18+
   - Nginx
   - Certbot (for SSL)
   - Domain DNS pointing to server IP

2. **DNS Configuration (Wix)**:
   Since `liquidcanvas.art` is hosted on Wix, you need to add a subdomain A record in Wix:
   
   **Steps to add subdomain in Wix:**
   1. Log in to your Wix account
   2. Go to **Domains** → Select `liquidcanvas.art`
   3. Click **Manage DNS** or **DNS Settings**
   4. Add a new **A Record**:
      - **Name/Host**: `agent` (or `agent.liquidcanvas.art` depending on Wix interface)
      - **Type**: A
      - **Value/IP Address**: Your server's IP address
      - **TTL**: 3600 (or default)
   5. Save the DNS record
   6. Wait 5-30 minutes for DNS propagation
   
   **Note**: The main domain stays on Wix, only the `agent` subdomain points to your server.

## Step 1: Server Setup

### Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, Node.js, Nginx
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm nginx certbot python3-certbot-nginx

# Install PM2 for process management (optional but recommended)
sudo npm install -g pm2
```

## Step 2: Deploy Application

### Clone/Upload Code

```bash
# Create app directory
sudo mkdir -p /var/www/agent.liquidcanvas.art
sudo chown $USER:$USER /var/www/agent.liquidcanvas.art

# Upload your code to /var/www/agent.liquidcanvas.art
# Or clone from git repository
```

### Backend Setup

```bash
cd /var/www/agent.liquidcanvas.art

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create .env file
nano .env
```

**Add to `.env`**:
```env
# Production settings
DEBUG=False
HOST=127.0.0.1
PORT=8000

# CORS - Add your production domain
CORS_ORIGINS=["https://agent.liquidcanvas.art","https://www.liquidcanvas.art"]

# Database (use PostgreSQL for production)
DATABASE_URL=postgresql://user:password@localhost:5432/art_outreach

# Add your API keys
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_password
```

### Frontend Setup

```bash
cd /var/www/agent.liquidcanvas.art/frontend

# Install dependencies
npm install

# Build for production
npm run build

# Create .env.production
nano .env.production
```

**Add to `.env.production`**:
```env
NEXT_PUBLIC_API_BASE_URL=https://agent.liquidcanvas.art/api/v1
```

## Step 3: Nginx Configuration

Create nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/agent.liquidcanvas.art
```

**Configuration**:
```nginx
# Backend API (FastAPI)
upstream backend {
    server 127.0.0.1:8000;
}

# Frontend (Next.js)
upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name agent.liquidcanvas.art;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name agent.liquidcanvas.art;

    # SSL certificates (will be added by Certbot)
    ssl_certificate /etc/letsencrypt/live/agent.liquidcanvas.art/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/agent.liquidcanvas.art/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API endpoints - proxy to FastAPI backend
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Health check
    location /health {
        proxy_pass http://backend;
        access_log off;
    }

    # Frontend - proxy to Next.js
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Static files (if serving directly)
    location /_next/static {
        proxy_pass http://frontend;
        proxy_cache_valid 200 60m;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/agent.liquidcanvas.art /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Step 4: SSL Certificate

```bash
# Get SSL certificate
sudo certbot --nginx -d agent.liquidcanvas.art

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run
```

## Step 5: Process Management

### Option 1: Systemd Services

**Backend Service** (`/etc/systemd/system/art-outreach-backend.service`):
```ini
[Unit]
Description=Art Outreach Scraper Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/agent.liquidcanvas.art
Environment="PATH=/var/www/agent.liquidcanvas.art/venv/bin"
ExecStart=/var/www/agent.liquidcanvas.art/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Frontend Service** (`/etc/systemd/system/art-outreach-frontend.service`):
```ini
[Unit]
Description=Art Outreach Scraper Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/agent.liquidcanvas.art/frontend
Environment="NODE_ENV=production"
Environment="NEXT_PUBLIC_API_BASE_URL=https://agent.liquidcanvas.art/api/v1"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable art-outreach-backend
sudo systemctl enable art-outreach-frontend
sudo systemctl start art-outreach-backend
sudo systemctl start art-outreach-frontend
```

### Option 2: PM2 (Recommended)

**Backend**:
```bash
cd /var/www/agent.liquidcanvas.art
pm2 start venv/bin/uvicorn --name "backend" -- main:app --host 127.0.0.1 --port 8000
pm2 save
```

**Frontend**:
```bash
cd /var/www/agent.liquidcanvas.art/frontend
pm2 start npm --name "frontend" -- start
pm2 save
```

## Step 6: Firewall

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

## Step 7: Database (Production)

For production, use PostgreSQL instead of SQLite:

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE art_outreach;
CREATE USER art_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE art_outreach TO art_user;
\q
```

Update `.env`:
```env
DATABASE_URL=postgresql://art_user:your_secure_password@localhost:5432/art_outreach
```

## Monitoring

```bash
# Check backend logs
sudo journalctl -u art-outreach-backend -f

# Check frontend logs
sudo journalctl -u art-outreach-frontend -f

# Or with PM2
pm2 logs
```

## Troubleshooting

1. **502 Bad Gateway**: Check if backend/frontend services are running
2. **CORS errors**: Verify CORS_ORIGINS in .env includes your domain
3. **SSL errors**: Run `sudo certbot renew`
4. **Database errors**: Check PostgreSQL is running and credentials are correct

## Updates

```bash
# Pull latest code
cd /var/www/agent.liquidcanvas.art
git pull

# Update backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart art-outreach-backend

# Update frontend
cd frontend
npm install
npm run build
sudo systemctl restart art-outreach-frontend
```

