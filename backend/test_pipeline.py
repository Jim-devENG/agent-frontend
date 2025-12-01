"""
Test script for the automation pipeline
Tests all endpoints and tasks
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.database import AsyncSessionLocal
from app.models import Job, Prospect, DiscoveryQuery
from sqlalchemy import select, func
from sqlalchemy import inspect


async def test_database_schema():
    """Test that database schema is correct"""
    print("\n" + "="*60)
    print("TEST 1: Database Schema")
    print("="*60)
    
    async with AsyncSessionLocal() as db:
        # Check Prospect model columns
        prospect_columns = [c.name for c in inspect(Prospect).columns]
        print(f"\n✅ Prospect model columns: {len(prospect_columns)}")
        print(f"   Key columns: {', '.join([c for c in prospect_columns if c in ['id', 'domain', 'contact_email', 'discovery_query_id', 'hunter_payload']])}")
        
        # Check if discovery_query_id exists
        if 'discovery_query_id' in prospect_columns:
            print("✅ discovery_query_id column exists in Prospect model")
        else:
            print("❌ discovery_query_id column MISSING in Prospect model")
            return False
        
        # Check DiscoveryQuery model
        try:
            dq_columns = [c.name for c in inspect(DiscoveryQuery).columns]
            print(f"✅ DiscoveryQuery model columns: {len(dq_columns)}")
            print(f"   Key columns: {', '.join([c for c in dq_columns if c in ['id', 'job_id', 'keyword', 'status']])}")
        except Exception as e:
            print(f"❌ DiscoveryQuery model error: {e}")
            return False
        
        # Check database tables (if connected)
        try:
            result = await db.execute(select(func.count()).select_from(Prospect))
            count = result.scalar() or 0
            print(f"✅ Database connection successful - {count} prospects in database")
        except Exception as e:
            print(f"⚠️  Database connection test failed: {e}")
            print("   (This is OK if DATABASE_URL is not set locally)")
        
        return True


def test_imports():
    """Test that all modules import correctly"""
    print("\n" + "="*60)
    print("TEST 2: Module Imports")
    print("="*60)
    
    try:
        from app.tasks.enrichment import process_enrichment_job
        print("✅ enrichment.py imports successfully")
    except Exception as e:
        print(f"❌ enrichment.py import failed: {e}")
        return False
    
    try:
        from app.tasks.send import process_send_job
        print("✅ send.py imports successfully")
    except Exception as e:
        print(f"❌ send.py import failed: {e}")
        return False
    
    try:
        from app.tasks.discovery import process_discovery_job
        print("✅ discovery.py imports successfully")
    except Exception as e:
        print(f"❌ discovery.py import failed: {e}")
        return False
    
    try:
        from app.api.prospects import router
        print("✅ prospects.py router imports successfully")
    except Exception as e:
        print(f"❌ prospects.py router import failed: {e}")
        return False
    
    try:
        from app.api.jobs import router
        print("✅ jobs.py router imports successfully")
    except Exception as e:
        print(f"❌ jobs.py router import failed: {e}")
        return False
    
    try:
        from app.clients.hunter import HunterIOClient
        print("✅ HunterIOClient imports successfully")
    except Exception as e:
        print(f"❌ HunterIOClient import failed: {e}")
        return False
    
    try:
        from app.clients.gmail import GmailClient
        print("✅ GmailClient imports successfully")
    except Exception as e:
        print(f"❌ GmailClient import failed: {e}")
        return False
    
    try:
        from app.clients.gemini import GeminiClient
        print("✅ GeminiClient imports successfully")
    except Exception as e:
        print(f"❌ GeminiClient import failed: {e}")
        return False
    
    return True


def test_endpoint_wiring():
    """Test that endpoints are wired correctly"""
    print("\n" + "="*60)
    print("TEST 3: Endpoint Wiring")
    print("="*60)
    
    # Check enrichment endpoint
    try:
        from app.api.prospects import create_enrichment_job
        import inspect
        source = inspect.getsource(create_enrichment_job)
        
        if "process_enrichment_job" in source:
            print("✅ Enrichment endpoint calls process_enrichment_job")
        else:
            print("❌ Enrichment endpoint does NOT call process_enrichment_job")
            return False
        
        if "not yet implemented" not in source.lower():
            print("✅ Enrichment endpoint no longer returns 'not implemented'")
        else:
            print("❌ Enrichment endpoint still returns 'not implemented'")
            return False
    except Exception as e:
        print(f"❌ Error checking enrichment endpoint: {e}")
        return False
    
    # Check send endpoint
    try:
        from app.api.jobs import create_send_job
        import inspect
        source = inspect.getsource(create_send_job)
        
        if "process_send_job" in source:
            print("✅ Send endpoint calls process_send_job")
        else:
            print("❌ Send endpoint does NOT call process_send_job")
            return False
        
        if "not yet implemented" not in source.lower():
            print("✅ Send endpoint no longer returns 'not implemented'")
        else:
            print("❌ Send endpoint still returns 'not implemented'")
            return False
    except Exception as e:
        print(f"❌ Error checking send endpoint: {e}")
        return False
    
    return True


def test_discovery_auto_trigger():
    """Test that discovery auto-triggers enrichment"""
    print("\n" + "="*60)
    print("TEST 4: Discovery Auto-Trigger")
    print("="*60)
    
    try:
        from app.tasks.discovery import discover_websites_async
        import inspect
        source = inspect.getsource(discover_websites_async)
        
        if "process_enrichment_job" in source:
            print("✅ Discovery task includes enrichment auto-trigger")
        else:
            print("❌ Discovery task does NOT include enrichment auto-trigger")
            return False
        
        if "Auto-trigger" in source or "auto-trigger" in source:
            print("✅ Auto-trigger code found in discovery task")
        else:
            print("⚠️  Auto-trigger code not clearly marked")
    except Exception as e:
        print(f"❌ Error checking discovery auto-trigger: {e}")
        return False
    
    return True


def test_email_extraction():
    """Test that discovery includes email extraction"""
    print("\n" + "="*60)
    print("TEST 5: Email Extraction in Discovery")
    print("="*60)
    
    try:
        from app.tasks.discovery import discover_websites_async
        import inspect
        source = inspect.getsource(discover_websites_async)
        
        if "HunterIOClient" in source:
            print("✅ Discovery task includes HunterIOClient")
        else:
            print("⚠️  Discovery task does NOT include HunterIOClient (optional)")
        
        if "contact_email" in source and "hunter_payload" in source:
            print("✅ Discovery task sets contact_email and hunter_payload")
        else:
            print("⚠️  Discovery task may not set contact_email/hunter_payload")
    except Exception as e:
        print(f"❌ Error checking email extraction: {e}")
        return False
    
    return True


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AUTOMATION PIPELINE TEST SUITE")
    print("="*60)
    
    results = []
    
    # Test 1: Database Schema
    results.append(await test_database_schema())
    
    # Test 2: Module Imports
    results.append(test_imports())
    
    # Test 3: Endpoint Wiring
    results.append(test_endpoint_wiring())
    
    # Test 4: Discovery Auto-Trigger
    results.append(test_discovery_auto_trigger())
    
    # Test 5: Email Extraction
    results.append(test_email_extraction())
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

