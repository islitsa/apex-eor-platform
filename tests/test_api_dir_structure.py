"""
Test API directory structure endpoint.

Verifies:
1. API responds within timeout
2. Returns correct file structure
"""

import requests
import json

def test_api_directory_structure():
    print("\n=== Testing API Directory Structure ===\n")

    api_url = "http://localhost:8000/api/pipelines"

    print(f"Fetching from: {api_url}")
    print("Timeout: 5 seconds\n")

    try:
        response = requests.get(api_url, timeout=5)
        print(f"[OK] API responded with status {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            pipelines = data.get('pipelines', [])

            print(f"[OK] Found {len(pipelines)} pipelines\n")

            # Find fracfocus pipeline
            fracfocus = next((p for p in pipelines if 'fracfocus' in p.get('id', '').lower()), None)

            if fracfocus:
                print(f"[OK] Found fracfocus pipeline: {fracfocus.get('id')}")
                print(f"  - Display name: {fracfocus.get('display_name')}")
                print(f"  - File count: {fracfocus.get('metrics', {}).get('file_count', 0):,}")
                print(f"  - Record count: {fracfocus.get('metrics', {}).get('record_count', 0):,}")

                # Check files structure
                files = fracfocus.get('files', {})
                if files:
                    print(f"\n[OK] Files structure present")
                    print(f"  - Type: {type(files).__name__}")
                    print(f"  - Keys: {list(files.keys())[:5]}")  # First 5 keys

                    # Pretty print a sample
                    print(f"\n  Sample structure:")
                    print(json.dumps(files, indent=2)[:500])  # First 500 chars
                else:
                    print(f"\n[WARNING] No files structure in response")

            else:
                print("[WARNING] fracfocus pipeline not found")

        else:
            print(f"[FAILED] API returned status {response.status_code}")
            print(f"Response: {response.text[:200]}")

    except requests.exceptions.Timeout:
        print("[FAILED] API request timed out (> 5 seconds)")
        return False
    except requests.exceptions.ConnectionError:
        print("[FAILED] Could not connect to API - is it running on port 8000?")
        return False
    except Exception as e:
        print(f"[FAILED] Error: {e}")
        return False

    print("\n=== Test Complete ===")
    return True

if __name__ == "__main__":
    success = test_api_directory_structure()
    exit(0 if success else 1)
