# Step-by-Step Deployment to agent.liquidcanvas.art

Follow these steps in order to deploy your app to the subdomain.

## Step 1: Get a Server (VPS)

You need a Linux server to host the application. Recommended options:

### Option A: DigitalOcean (Recommended - Simple)
1. Sign up at https://www.digitalocean.com
2. Create a Droplet:
   - **OS**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($6/month minimum, $12/month recommended)
   - **Region**: Choose closest to you
   - **Authentication**: SSH keys (recommended) or password
3. Note your server IP address (e.g., `123.45.67.89`)

### Option B: AWS EC2
1. Sign up at https://aws.amazon.com
2. Launch EC2 instance:
   - **AMI**: Ubuntu Server 22.04 LTS
   - **Instance Type**: t2.micro (free tier) or t2.small
   - **Security Group**: Allow HTTP (80), HTTPS (443), SSH (22)
3. Note your server's public IP

### Option C: Other Providers
- Linode
- Vultr
- Hetzner
- Google Cloud Platform

**Minimum Requirements:**
- 1-2 GB RAM
- 1 CPU core
- 20 GB storage
- Ubuntu 20.04+ or similar Linux

## Step 2: Configure DNS in Wix

**Before deploying, set up DNS so the subdomain points to your server:**

1. **Get your server IP** (from Step 1)
2. **Log in to Wix**:
   - Go to https://www.wix.com
   - Sign in to your account
3. **Navigate to Domains**:
   - Click your profile → **Domains**
   - Find and click on `liquidcanvas.art`
4. **Add DNS Record**:
   - Click **Manage DNS** or **DNS Settings**
   - Click **Add Record** or **+**
   - Select **A Record**
   - Fill in:
     - **Name/Host**: `agent` (just "agent")
     - **Type**: A
     - **Value/IP**: Your server IP (e.g., `123.45.67.89`)
     - **TTL**: 3600
   - Click **Save**
5. **Wait 5-30 minutes** for DNS propagation
6. **Verify DNS**:
   ```bash
   # On your local computer
   nslookup agent.liquidcanvas.art
   # Should return your server IP
   ```

**See WIX_DNS_SETUP.md if you have issues.**

## Step 3: Connect to Your Server

### On Windows (PowerShell):

```powershell
# SSH into your server
ssh root@YOUR_SERVER_IP
# or
ssh username@YOUR_SERVER_IP

# If using password, enter it when prompted
# If using SSH key, it should connect automatically
```

### First Time Setup:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Create app user (recommended)
sudo adduser appuser
sudo usermod -aG sudo appuser
su - appuser
```

## Step 4: Install Required Software

```bash
# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Nginx
sudo apt install -y nginx

# Install Certbot (for SSL)
sudo apt install -y certbot python3-certbot-nginx

# Install Git (if using git)
sudo apt install -y git

# Verify installations
python3.11 --version
node --version
nginx -v
```

## Step 5: Upload Your Code

### Option A: Using SCP (from Windows PowerShell)

```powershell
# From your local machine (in project directory)
scp -r . appuser@YOUR_SERVER_IP:/var/www/agent.liquidcanvas.art

# Or upload specific files
scp -r * appuser@YOUR_SERVER_IP:/var/www/agent.liquidcanvas.art
```

### Option B: Using Git (Recommended)

```bash
# On server
sudo mkdir -p /var/www/agent.liquidcanvas.art
sudo chown $USER:$USER /var/www/agent.liquidcanvas.art
cd /var/www/agent.liquidcanvas.art

# Clone your repository
git clone YOUR_REPO_URL .

# Or if you have a private repo, set up SSH keys first
```

### Option C: Using FTP/SFTP Client

- Use FileZilla, WinSCP, or similar
- Connect to your server
- Upload all files to `/var/www/agent.liquidcanvas.art`

## Step 6: Setup Backend

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

**Add to `.env`** (copy from `.env.production.example` and fill in):
```env
DEBUG=False
HOST=127.0.0.1
PORT=8000
CORS_ORIGINS=["https://agent.liquidcanvas.art","https://www.liquidcanvas.art"]
DATABASE_URL=sqlite:///./art_outreach.db
GEMINI_API_KEY=your_key_here
# ... add other API keys
```

## Step 7: Setup Frontend

```bash
cd /var/www/agent.liquidcanvas.art/frontend

# Install dependencies
npm install

# Create production env file
echo "NEXT_PUBLIC_API_BASE_URL=https://agent.liquidcanvas.art/api/v1" > .env.production

# Build for production
npm run build
```

## Step 8: Configure Nginx

```bash
# Copy nginx config
sudo cp /var/www/agent.liquidcanvas.art/nginx/agent.liquidcanvas.art.conf /etc/nginx/sites-available/

# Enable site
sudo ln -s /etc/nginx/sites-available/agent.liquidcanvas.art.conf /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test nginx config
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

## Step 9: Setup Systemd Services

```bash
# Copy service files
sudo cp /var/www/agent.liquidcanvas.art/systemd/art-outreach-backend.service /etc/systemd/system/
sudo cp /var/www/agent.liquidcanvas.art/systemd/art-outreach-frontend.service /etc/systemd/system/

# Update paths in service files if needed
sudo nano /etc/systemd/system/art-outreach-backend.service
sudo nano /etc/systemd/system/art-outreach-frontend.service

# Reload systemd
sudo systemctl daemon-reload

# Enable services (start on boot)
sudo systemctl enable art-outreach-backend
sudo systemctl enable art-outreach-frontend

# Start services
sudo systemctl start art-outreach-backend
sudo systemctl start art-outreach-frontend

# Check status
sudo systemctl status art-outreach-backend
sudo systemctl status art-outreach-frontend
```

## Step 10: Get SSL Certificate

**Important**: DNS must be fully propagated first!

```bash
# Get SSL certificate
sudo certbot --nginx -d agent.liquidcanvas.art

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose redirect HTTP to HTTPS (option 2)

# Test auto-renewal
sudo certbot renew --dry-run
```

## Step 11: Configure Firewall

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH (important!)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## Step 12: Verify Deployment

```bash
# Check services are running
sudo systemctl status art-outreach-backend
sudo systemctl status art-outreach-frontend

# Check logs
sudo journalctl -u art-outreach-backend -n 20
sudo journalctl -u art-outreach-frontend -n 20

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:3000

# Test from browser
# https://agent.liquidcanvas.art
# https://agent.liquidcanvas.art/api/v1/stats
```

## Step 13: Set Permissions

```bash
# Set ownership
sudo chown -R www-data:www-data /var/www/agent.liquidcanvas.art

# Set permissions
sudo chmod -R 755 /var/www/agent.liquidcanvas.art
```

## Troubleshooting

### Backend not starting:
```bash
# Check logs
sudo journalctl -u art-outreach-backend -f

# Common issues:
# - Missing dependencies: pip install -r requirements.txt
# - Wrong Python path: Check service file
# - Port in use: sudo lsof -i :8000
```

### Frontend not starting:
```bash
# Check logs
sudo journalctl -u art-outreach-frontend -f

# Common issues:
# - Not built: npm run build
# - Wrong Node version: node --version
```

### Nginx 502 Bad Gateway:
- Check backend/frontend services are running
- Check nginx error log: `sudo tail -f /var/log/nginx/error.log`
- Verify ports 8000 and 3000 are listening: `sudo netstat -tlnp | grep -E '8000|3000'`

### SSL Certificate fails:
- DNS must be fully propagated (wait 30+ minutes)
- Verify DNS: `nslookup agent.liquidcanvas.art`
- Check firewall allows port 80

## Quick Commands Reference

```bash
# Restart services
sudo systemctl restart art-outreach-backend
sudo systemctl restart art-outreach-frontend
sudo systemctl restart nginx

# View logs
sudo journalctl -u art-outreach-backend -f
sudo journalctl -u art-outreach-frontend -f

# Check service status
sudo systemctl status art-outreach-backend
sudo systemctl status art-outreach-frontend

# Update and redeploy
cd /var/www/agent.liquidcanvas.art
git pull  # or upload new files
source venv/bin/activate
pip install -r requirements.txt
cd frontend
npm install
npm run build
sudo systemctl restart art-outreach-backend
sudo systemctl restart art-outreach-frontend
```

## Next Steps After Deployment

1. ✅ Test the application: https://agent.liquidcanvas.art
2. ✅ Verify API is working: https://agent.liquidcanvas.art/api/v1/stats
3. ✅ Test scraping functionality
4. ✅ Monitor logs for errors
5. ✅ Set up monitoring/alerting (optional)
6. ✅ Configure backups (optional)

## Support

If you encounter issues:
1. Check service logs
2. Check nginx error logs
3. Verify DNS is correct
4. Verify firewall rules
5. Check server resources (RAM, CPU)

