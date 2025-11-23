# debug_api_issue.py
import json
from pathlib import Path
from src.agents.context.discovery_instrumentation import DiscoveryTools

print("DEBUGGING: Why API shows 0 files\n")
print("="*60)

# 1. Check what discovery tools returns
print("\n[1] LIVE Discovery Tools check_status():")
tools = DiscoveryTools()
status = tools.check_status('fracfocus')
live_count = sum(status.get('files_by_stage', {}).values())
print(f"FracFocus live count: {live_count} files")
print(f"Files by stage: {status.get('files_by_stage', {})}")

# 2. Check what's in the cached JSON
print("\n[2] CACHED pipeline_state.json:")
pipeline_path = Path.home() / '.apex_eor' / 'pipeline_state.json'
if pipeline_path.exists():
    with open(pipeline_path) as f:
        data = json.load(f)
    
    # Look for fracfocus in different places
    if 'pipelines' in data:
        fracfocus = data['pipelines'].get('fracfocus', {})
        print(f"Found in pipelines: {fracfocus.get('metrics', {}).get('file_count', 'NOT FOUND')}")
    
    if 'context' in data:
        if 'pipelines' in data['context']:
            fracfocus = data['context']['pipelines'].get('fracfocus', {})
            print(f"Found in context.pipelines: {fracfocus}")
    
    # Show the actual structure
    print(f"\nActual JSON structure keys: {data.keys()}")
    if 'context' in data:
        print(f"context keys: {data['context'].keys()}")

# 3. Check what the API endpoint actually returns
print("\n[3] API RESPONSE:")
import requests
try:
    response = requests.get('http://localhost:8000/api/pipelines')
    pipelines = response.json().get('pipelines', [])
    for p in pipelines:
        if 'fracfocus' in p.get('name', '').lower():
            print(f"FracFocus from API: {p}")
            break
except:
    print("API not running or error connecting")

print("\n" + "="*60)
print("\nDIAGNOSIS:")
if live_count > 0:
    print(f"✅ Discovery tools returns {live_count} files")
else:
    print("❌ Discovery tools returns 0 files")

print("\nThe issue is likely:")
print("1. The cached JSON doesn't have the right structure")
print("2. The API is reading from the wrong place in the JSON")
print("3. The cache regeneration didn't actually update the file")