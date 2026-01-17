"""
Verification script to check if the application is set up correctly
"""
import sys
import os

def check_imports():
    """Check if all required modules can be imported"""
    print("Checking imports...")
    try:
        from fastapi import FastAPI
        from sqlalchemy import create_engine
        from db.database import Base, engine
        from db.models import ScrapedWebsite, Contact, OutreachEmail
        from scraper.scraper_service import ScraperService
        from extractor.contact_extraction_service import ContactExtractionService
        from ai.email_generator import EmailGenerator
        from emailer.outreach_email_sender import OutreachEmailSender
        from jobs.scheduler import start_scheduler
        from jobs.automation_jobs import fetch_new_art_websites
        from api.dashboard_routes import router
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False

def check_config():
    """Check configuration"""
    print("\nChecking configuration...")
    try:
        from utils.config import settings
        print(f"✅ Configuration loaded")
        print(f"   - Database: {settings.DATABASE_URL}")
        print(f"   - Scheduler enabled: {settings.SCHEDULER_ENABLED}")
        print(f"   - Gemini API key: {'Set' if settings.GEMINI_API_KEY else 'Not set'}")
        print(f"   - OpenAI API key: {'Set' if settings.OPENAI_API_KEY else 'Not set'}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return False

def check_files():
    """Check if required files exist"""
    print("\nChecking required files...")
    files = [
        "main.py",
        "requirements.txt",
        "seed_websites.txt",
        ".env.example"
    ]
    all_exist = True
    for file in files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"⚠️  {file} (not found)")
            all_exist = False
    return all_exist

def main():
    """Run all checks"""
    print("=" * 60)
    print("Autonomous Art Outreach Scraper - Setup Verification")
    print("=" * 60)
    
    checks = [
        check_imports(),
        check_config(),
        check_files()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ Setup verification PASSED")
        print("\nYou can now run: python main.py")
    else:
        print("⚠️  Setup verification found some issues")
        print("Please check the errors above")
    print("=" * 60)

if __name__ == "__main__":
    main()

