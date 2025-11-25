"""
Test discovery directly without cached state
This shows REAL current file counts
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.context.discovery_tools import DiscoveryTools

print("="*80)
print("REAL-TIME DISCOVERY (No Cache)")
print("="*80)

tools = DiscoveryTools()

# Get all sources
sources = tools.find_data_sources("", top_k=20, min_relevance=0.0)

print(f"\nFound {len(sources)} sources:\n")

for i, source in enumerate(sources, 1):
    source_name = source['name']

    # Get real-time status
    status = tools.check_status(source_name)

    if status:
        print(f"{i}. {source_name}")
        print(f"   Status: {status['status']}")
        print(f"   Files by stage:")

        total_files = 0
        for stage, count in status.get('files_by_stage', {}).items():
            print(f"     - {stage}: {count} files")
            total_files += count

        print(f"   TOTAL FILES: {total_files}")
    else:
        print(f"{i}. {source_name} - No status")

    print()

print("="*80)
print("\nThis shows ACTUAL current file counts.")
print("Compare this to what /api/pipelines shows (cached data).")
print("="*80 + "\n")
