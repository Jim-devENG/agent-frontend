#!/bin/bash
# Deployment script for agent.liquidcanvas.art

set -e

APP_DIR="/var/www/agent.liquidcanvas.art"
DOMAIN="agent.liquidcanvas.art"

echo "=========================================="
echo "Deploying to $DOMAIN"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Step 1: Update code
echo "Step 1: Updating code..."
cd $APP_DIR
# git pull  # Uncomment if using git
# Or copy files manually

# Step 2: Backend setup
echo "Step 2: Setting up backend..."
cd $APP_DIR
source venv/bin/activate
pip install -r requirements.txt --quiet
playwright install chromium --quiet

# Step 3: Frontend setup
echo "Step 3: Setting up frontend..."
cd $APP_DIR/frontend
npm install --production
npm run build

# Step 4: Set permissions
echo "Step 4: Setting permissions..."
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

# Step 5: Restart services
echo "Step 5: Restarting services..."
systemctl restart art-outreach-backend
systemctl restart art-outreach-frontend
systemctl reload nginx

echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
echo "Backend: https://$DOMAIN/api/v1"
echo "Frontend: https://$DOMAIN"
echo ""
echo "Check status:"
echo "  systemctl status art-outreach-backend"
echo "  systemctl status art-outreach-frontend"

