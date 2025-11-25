# test_what_actually_exists.py

from src.knowledge.repository_index import RepositoryIndex

print("DISCOVERING: What methods actually exist?")
print("="*60)

# Check what RepositoryIndex actually has
index = RepositoryIndex()

print("\n[1] RepositoryIndex methods:")
methods = [m for m in dir(index) if not m.startswith('_')]
for method in methods:
    print(f"  - {method}")

# Try to find where file counts come from
print("\n[2] Looking for anything that counts files...")

# Check if there's a discovery tools method
from src.agents.context.discovery_tools_instrumented import DiscoveryTools
tools = DiscoveryTools()

print("\nDiscoveryTools methods:")
methods = [m for m in dir(tools) if not m.startswith('_')]
for method in methods:
    print(f"  - {method}")
    
# Try the ones that look promising
if hasattr(tools, 'get_status'):
    print(f"\nget_status('fracfocus'): {tools.get_status('fracfocus')}")

if hasattr(tools, 'check_status'):
    print(f"\ncheck_status('fracfocus'): {tools.check_status('fracfocus')}")

# Check the actual pipeline state file
import json
from pathlib import Path

print("\n[3] Raw pipeline_state.json content:")
pipeline_path = Path.home() / '.apex_eor' / 'pipeline_state.json'
if pipeline_path.exists():
    with open(pipeline_path) as f:
        data = json.load(f)
    print(json.dumps(data, indent=2)[:500])  # First 500 chars