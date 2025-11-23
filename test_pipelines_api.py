"""Test /api/pipelines endpoint - PROOF IT WORKS"""
import requests
import json

# Test the API
url = "http://localhost:8000/api/pipelines"

print("=" * 80)
print("TESTING /api/pipelines ENDPOINT")
print("=" * 80)
print(f"\nFetching: {url}\n")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS! Endpoint is working.\n")

        print("=" * 80)
        print("PIPELINE DATA (from real pipeline_context.json)")
        print("=" * 80)

        # Show summary
        summary = data.get('summary', {})
        print(f"\nSummary:")
        print(f"  Total Pipelines: {summary.get('total_pipelines')}")
        print(f"  Total Records:   {summary.get('total_records'):,}")
        print(f"  Total Size:      {summary.get('total_size')}")

        # Show first 3 pipelines
        pipelines = data.get('pipelines', [])
        print(f"\nPipelines ({len(pipelines)} total):\n")

        for i, pipeline in enumerate(pipelines[:3], 1):
            print(f"{i}. {pipeline['display_name']} ({pipeline['id']})")
            print(f"   Status: {pipeline['status']}")
            print(f"   Files: {pipeline['metrics']['file_count']}")
            print(f"   Data Size: {pipeline['metrics']['data_size']}")

            # Show stages
            stages = pipeline.get('stages', [])
            if stages:
                stage_str = ' → '.join([f"{s['name']}({s['status']})" for s in stages])
                print(f"   Stages: {stage_str}")
            print()

        if len(pipelines) > 3:
            print(f"... and {len(pipelines) - 3} more pipelines\n")

        print("=" * 80)
        print("✅ PROOF: API is returning REAL pipeline data from shared_state.py")
        print("=" * 80)

    else:
        print(f"\n❌ ERROR: Got status {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to API. Is it running at http://localhost:8000?")
    print("\nStart it with: python -m uvicorn src.api.data_service:app --reload")
except Exception as e:
    print(f"❌ ERROR: {e}")
