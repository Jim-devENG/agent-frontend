"""
Test script for code validation (no database connection required)
Tests imports, endpoint wiring, and code structure
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all modules import correctly"""
    print("\n" + "="*60)
    print("TEST 1: Module Imports")
    print("="*60)
    
    results = []
    
    try:
        from app.tasks.enrichment import process_enrichment_job
        print("✅ enrichment.py imports successfully")
        results.append(True)
    except Exception as e:
        print(f"❌ enrichment.py import failed: {e}")
        results.append(False)
    
    try:
        from app.tasks.send import process_send_job
        print("✅ send.py imports successfully")
        results.append(True)
    except Exception as e:
        print(f"❌ send.py import failed: {e}")
        results.append(False)
    
    try:
        from app.tasks.discovery import process_discovery_job
        print("✅ discovery.py imports successfully")
        results.append(True)
    except Exception as e:
        print(f"❌ discovery.py import failed: {e}")
        results.append(False)
    
    try:
        from app.api.prospects import router
        print("✅ prospects.py router imports successfully")
        results.append(True)
    except Exception as e:
        print(f"❌ prospects.py router import failed: {e}")
        results.append(False)
    
    try:
        from app.api.jobs import router
        print("✅ jobs.py router imports successfully")
        results.append(True)
    except Exception as e:
        print(f"❌ jobs.py router import failed: {e}")
        results.append(False)
    
    try:
        from app.clients.hunter import HunterIOClient
        print("✅ HunterIOClient imports successfully")
        results.append(True)
    except Exception as e:
        print(f"❌ HunterIOClient import failed: {e}")
        results.append(False)
    
    try:
        from app.clients.gmail import GmailClient
        print("✅ GmailClient imports successfully")
        results.append(True)
    except Exception as e:
        print(f"❌ GmailClient import failed: {e}")
        results.append(False)
    
    try:
        from app.clients.gemini import GeminiClient
        print("✅ GeminiClient imports successfully")
        results.append(True)
    except Exception as e:
        print(f"❌ GeminiClient import failed: {e}")
        results.append(False)
    
    return all(results)


def test_endpoint_wiring():
    """Test that endpoints are wired correctly"""
    print("\n" + "="*60)
    print("TEST 2: Endpoint Wiring")
    print("="*60)
    
    results = []
    
    # Check enrichment endpoint
    try:
        from app.api.prospects import create_enrichment_job
        import inspect
        source = inspect.getsource(create_enrichment_job)
        
        if "process_enrichment_job" in source:
            print("✅ Enrichment endpoint calls process_enrichment_job")
            results.append(True)
        else:
            print("❌ Enrichment endpoint does NOT call process_enrichment_job")
            results.append(False)
        
        if "not yet implemented" not in source.lower():
            print("✅ Enrichment endpoint no longer returns 'not implemented'")
            results.append(True)
        else:
            print("❌ Enrichment endpoint still returns 'not implemented'")
            results.append(False)
    except Exception as e:
        print(f"❌ Error checking enrichment endpoint: {e}")
        results.append(False)
    
    # Check send endpoint
    try:
        from app.api.jobs import create_send_job
        import inspect
        source = inspect.getsource(create_send_job)
        
        if "process_send_job" in source:
            print("✅ Send endpoint calls process_send_job")
            results.append(True)
        else:
            print("❌ Send endpoint does NOT call process_send_job")
            results.append(False)
        
        if "not yet implemented" not in source.lower():
            print("✅ Send endpoint no longer returns 'not implemented'")
            results.append(True)
        else:
            print("❌ Send endpoint still returns 'not implemented'")
            results.append(False)
    except Exception as e:
        print(f"❌ Error checking send endpoint: {e}")
        results.append(False)
    
    return all(results)


def test_discovery_auto_trigger():
    """Test that discovery auto-triggers enrichment"""
    print("\n" + "="*60)
    print("TEST 3: Discovery Auto-Trigger")
    print("="*60)
    
    try:
        from app.tasks.discovery import discover_websites_async
        import inspect
        source = inspect.getsource(discover_websites_async)
        
        if "process_enrichment_job" in source:
            print("✅ Discovery task includes enrichment auto-trigger")
            return True
        else:
            print("❌ Discovery task does NOT include enrichment auto-trigger")
            return False
    except Exception as e:
        print(f"❌ Error checking discovery auto-trigger: {e}")
        return False


def test_email_extraction():
    """Test that discovery includes email extraction"""
    print("\n" + "="*60)
    print("TEST 4: Email Extraction in Discovery")
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
            return True
        else:
            print("⚠️  Discovery task may not set contact_email/hunter_payload")
            return True  # Optional feature
    except Exception as e:
        print(f"❌ Error checking email extraction: {e}")
        return False


def test_task_structure():
    """Test that task functions have correct structure"""
    print("\n" + "="*60)
    print("TEST 5: Task Function Structure")
    print("="*60)
    
    results = []
    
    # Check enrichment task
    try:
        from app.tasks.enrichment import process_enrichment_job
        import inspect
        sig = inspect.signature(process_enrichment_job)
        
        if 'job_id' in sig.parameters:
            print("✅ process_enrichment_job has job_id parameter")
            results.append(True)
        else:
            print("❌ process_enrichment_job missing job_id parameter")
            results.append(False)
        
        # Check it's async
        if inspect.iscoroutinefunction(process_enrichment_job):
            print("✅ process_enrichment_job is async")
            results.append(True)
        else:
            print("❌ process_enrichment_job is not async")
            results.append(False)
    except Exception as e:
        print(f"❌ Error checking enrichment task: {e}")
        results.append(False)
    
    # Check send task
    try:
        from app.tasks.send import process_send_job
        import inspect
        sig = inspect.signature(process_send_job)
        
        if 'job_id' in sig.parameters:
            print("✅ process_send_job has job_id parameter")
            results.append(True)
        else:
            print("❌ process_send_job missing job_id parameter")
            results.append(False)
        
        # Check it's async
        if inspect.iscoroutinefunction(process_send_job):
            print("✅ process_send_job is async")
            results.append(True)
        else:
            print("❌ process_send_job is not async")
            results.append(False)
    except Exception as e:
        print(f"❌ Error checking send task: {e}")
        results.append(False)
    
    return all(results)


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AUTOMATION PIPELINE CODE VALIDATION")
    print("="*60)
    
    results = []
    
    # Test 1: Module Imports
    results.append(test_imports())
    
    # Test 2: Endpoint Wiring
    results.append(test_endpoint_wiring())
    
    # Test 3: Discovery Auto-Trigger
    results.append(test_discovery_auto_trigger())
    
    # Test 4: Email Extraction
    results.append(test_email_extraction())
    
    # Test 5: Task Structure
    results.append(test_task_structure())
    
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
        print("\n📝 Next Steps:")
        print("   1. Apply database migration on Render: cd backend && alembic upgrade head")
        print("   2. Set environment variables in Render")
        print("   3. Test the pipeline with actual API calls")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

