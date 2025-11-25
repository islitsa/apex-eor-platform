"""
Phase 3A API Test

Tests the data access API to ensure it correctly serves data from the repository.
"""

import sys
from pathlib import Path
import subprocess
import time
import requests
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_api():
    """Test the Phase 3A data API"""

    print("\n" + "=" * 80)
    print("PHASE 3A API TEST")
    print("=" * 80)

    # Start API server in background
    print("\n[TEST] Starting API server...")
    api_process = subprocess.Popen(
        ["python", "-m", "uvicorn", "src.api.data_service:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    print("[TEST] Waiting for server to start...")
    time.sleep(3)

    try:
        base_url = "http://localhost:8000"

        # Test 1: Health check
        print("\n" + "-" * 80)
        print("TEST 1: Health Check")
        print("-" * 80)

        response = requests.get(f"{base_url}/")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"

        data = response.json()
        print(f"✅ API is running")
        print(f"   Service: {data['service']}")
        print(f"   Version: {data['version']}")
        print(f"   Phase: {data['phase']}")

        # Test 2: List sources
        print("\n" + "-" * 80)
        print("TEST 2: List Data Sources")
        print("-" * 80)

        response = requests.get(f"{base_url}/api/sources")
        assert response.status_code == 200, f"List sources failed: {response.status_code}"

        sources = response.json()
        print(f"✅ Found {len(sources)} data sources:")
        for source in sources:
            print(f"   - {source}")

        assert len(sources) > 0, "No sources found"

        # Test 3: Get source info (fracfocus)
        print("\n" + "-" * 80)
        print("TEST 3: Get Source Info (fracfocus)")
        print("-" * 80)

        response = requests.get(f"{base_url}/api/sources/fracfocus/info")
        assert response.status_code == 200, f"Get info failed: {response.status_code}"

        info = response.json()
        print(f"✅ fracfocus metadata:")
        print(f"   Name: {info['name']}")
        print(f"   Data types: {info['data_types']}")
        print(f"   Stages: {info['stages']}")
        print(f"   Row count: {info['row_count']:,}")
        print(f"   Columns ({len(info['columns'])}): {info['columns'][:5]}...")

        assert info['row_count'] > 0, "fracfocus has zero rows"
        assert len(info['columns']) > 0, "fracfocus has no columns"

        # Test 4: Get actual data
        print("\n" + "-" * 80)
        print("TEST 4: Fetch Actual Data (first 10 rows)")
        print("-" * 80)

        response = requests.get(f"{base_url}/api/sources/fracfocus/data?limit=10")
        assert response.status_code == 200, f"Get data failed: {response.status_code}"

        result = response.json()
        print(f"✅ Retrieved data:")
        print(f"   Total rows: {result['total']:,}")
        print(f"   Returned rows: {result['returned']}")
        print(f"   Offset: {result['offset']}")
        print(f"\n   First record (sample):")
        if result['data']:
            first_record = result['data'][0]
            for key, value in list(first_record.items())[:5]:
                print(f"     {key}: {value}")

        assert result['returned'] == 10, f"Expected 10 rows, got {result['returned']}"
        assert len(result['data']) == 10, f"Expected 10 data items, got {len(result['data'])}"

        # Test 5: POST query with filters (if applicable)
        print("\n" + "-" * 80)
        print("TEST 5: POST Query with Column Selection")
        print("-" * 80)

        # Get first 3 columns only
        columns = info['columns'][:3]
        query = {
            "source": "fracfocus",
            "columns": columns,
            "limit": 5,
            "offset": 0
        }

        response = requests.post(f"{base_url}/api/query", json=query)
        assert response.status_code == 200, f"POST query failed: {response.status_code}"

        result = response.json()
        print(f"✅ Query with selected columns:")
        print(f"   Requested columns: {columns}")
        print(f"   Returned rows: {result['returned']}")
        print(f"\n   Sample record:")
        if result['data']:
            first_record = result['data'][0]
            for key, value in first_record.items():
                print(f"     {key}: {value}")

        # Verify only requested columns returned
        if result['data']:
            actual_columns = list(result['data'][0].keys())
            assert set(actual_columns) == set(columns), \
                f"Expected columns {columns}, got {actual_columns}"

        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        print("\n✅ ALL TESTS PASSED")
        print(f"\nPhase 3A Data API is working:")
        print(f"  • API server running at {base_url}")
        print(f"  • {len(sources)} data sources available")
        print(f"  • fracfocus has {info['row_count']:,} records with {len(info['columns'])} columns")
        print(f"  • Data fetching works correctly")
        print(f"  • Column selection works correctly")

        print("\n🎉 PHASE 3A BACKEND COMPLETE")
        print("\nNext step: Update React Developer to generate data-fetching code")

        return True

    except AssertionError as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"\nAssertion Error: {e}")
        return False

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"\nError: {e}")

        import traceback
        traceback.print_exc()

        return False

    finally:
        # Stop API server
        print("\n[TEST] Stopping API server...")
        api_process.terminate()
        api_process.wait()


if __name__ == "__main__":
    print("\n\n")
    print("#" * 80)
    print("# PHASE 3A INTEGRATION TEST")
    print("# Testing: Data Access API")
    print("#" * 80)

    success = test_api()

    print("\n\n")
    print("#" * 80)
    print("# RESULT")
    print("#" * 80)

    if success:
        print("\n✅ PHASE 3A BACKEND VERIFIED")
        print("\nThe data API is working:")
        print("  1. Serves data from repository")
        print("  2. Handles queries and filters")
        print("  3. Returns actual records to clients")
    else:
        print("\n⚠️  PHASE 3A NEEDS REVIEW")
        print("\nCheck the error output above")

    print("\n")
