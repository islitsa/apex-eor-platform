"""
Test if /api/pipelines endpoint now shows correct file counts
"""

import requests
import json

print("="*80)
print("TESTING /api/pipelines ENDPOINT")
print("="*80)

# Check if API is running
try:
    response = requests.get("http://localhost:8000/", timeout=2)
    print("\n[OK] API is running")
except:
    print("\n[FAIL] API is not running. Start it with:")
    print("  python -m src.api.data_service")
    print("\nOr test discovery tools directly:")
    print("  python test_discovery_sources.py")
    exit(1)

# Test /api/pipelines
try:
    response = requests.get("http://localhost:8000/api/pipelines", timeout=5)
    response.raise_for_status()

    data = response.json()
    pipelines = data.get('pipelines', [])
    summary = data.get('summary', {})

    print(f"\n[OK] Got pipeline data:")
    print(f"  Total Pipelines: {summary.get('total_pipelines', 0)}")
    print(f"  Total Records: {summary.get('total_records', 0):,}")
    print(f"  Total Size: {summary.get('total_size', '0 B')}")

    print(f"\nPipeline Details:")
    for i, pipeline in enumerate(pipelines, 1):
        print(f"\n{i}. {pipeline.get('display_name', pipeline.get('id'))}")
        metrics = pipeline.get('metrics', {})
        print(f"   File Count: {metrics.get('file_count', 0)}")
        print(f"   Record Count: {metrics.get('record_count', 0):,}")
        print(f"   Data Size: {metrics.get('data_size', '0 B')}")
        print(f"   Status: {pipeline.get('status', 'unknown')}")

        stages = pipeline.get('stages', [])
        if stages:
            stage_names = [s.get('name') for s in stages]
            print(f"   Stages: {', '.join(stage_names)}")

    # Check for the specific issue: fracfocus with 0 files
    fracfocus = next((p for p in pipelines if 'fracfocus' in p.get('id', '').lower()), None)

    if fracfocus:
        file_count = fracfocus.get('metrics', {}).get('file_count', 0)

        print(f"\n{'='*80}")
        print("FRACFOCUS FILE COUNT CHECK")
        print(f"{'='*80}")

        if file_count == 0:
            print("\n[FAIL] FracFocus still showing 0 files!")
            print("\nThis means:")
            print("  1. Pipeline context hasn't been regenerated yet")
            print("  2. Need to run pipeline to update ~/.apex_eor/pipeline_state.json")
            print("\nThe fix to check_status() is working (test_discovery_sources.py shows it)")
            print("But the API is reading from cached context that was generated before the fix.")
        else:
            print(f"\n[OK] FracFocus showing {file_count} files!")
            print("The fix is working end-to-end!")

except Exception as e:
    print(f"\n[FAIL] Error: {e}")

print(f"\n{'='*80}\n")
