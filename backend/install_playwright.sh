#!/bin/bash
# Install Playwright browsers for social media scraping

echo "Installing Playwright browsers..."
pip install playwright
playwright install chromium
playwright install-deps chromium

echo "✅ Playwright installation complete!"

