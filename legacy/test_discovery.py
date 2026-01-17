"""
Test script to verify website discovery is working
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from jobs.website_discovery import WebsiteDiscovery
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_discovery():
    """Test website discovery functionality"""
    print("=" * 60)
    print("Testing Website Discovery")
    print("=" * 60)
    
    discovery = WebsiteDiscovery()
    
    # Test 1: DuckDuckGo search
    print("\n1. Testing DuckDuckGo search...")
    try:
        results = discovery.search_duckduckgo("art gallery", num_results=5)
        print(f"   ✅ Found {len(results)} results")
        for i, url in enumerate(results[:3], 1):
            print(f"      {i}. {url}")
        if len(results) == 0:
            print("   ⚠️  WARNING: No results found! This might be the issue.")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Seed file
    print("\n2. Testing seed file...")
    try:
        seed_urls = discovery.fetch_from_seed_list()
        print(f"   ✅ Found {len(seed_urls)} URLs in seed file")
        for i, url in enumerate(seed_urls[:3], 1):
            print(f"      {i}. {url}")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    # Test 3: Full discovery
    print("\n3. Testing full discovery (limited to 2 queries)...")
    try:
        # Temporarily modify to test with fewer queries
        original_discover = discovery.discover_art_websites
        def limited_discover():
            all_urls = set()
            queries = ["art gallery", "interior design blog"]
            for query in queries:
                try:
                    urls = discovery.search_duckduckgo(query, num_results=3)
                    all_urls.update(urls)
                    print(f"      Query '{query}': {len(urls)} results")
                except Exception as e:
                    print(f"      Query '{query}': ERROR - {str(e)}")
            seed_urls = discovery.fetch_from_seed_list()
            all_urls.update(seed_urls)
            return list(all_urls)
        
        urls = limited_discover()
        print(f"   ✅ Total discovered: {len(urls)} URLs")
        if len(urls) == 0:
            print("   ⚠️  WARNING: No URLs discovered! This is the problem.")
        else:
            print(f"   Sample URLs:")
            for i, url in enumerate(urls[:5], 1):
                print(f"      {i}. {url}")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_discovery()

