"""
Debug script to trace why check_status returns 0 files for downloads
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.knowledge.repository_index import RepositoryIndex


# Manual check
print("="*80)
print("MANUAL FILESYSTEM CHECK")
print("="*80)

downloads_path = Path("data/raw/fracfocus/Chemical_data/downloads")
print(f"\nPath: {downloads_path}")
print(f"Exists: {downloads_path.exists()}")
print(f"Is dir: {downloads_path.is_dir()}")

if downloads_path.exists():
    print(f"\nDirect listing:")
    for item in downloads_path.iterdir():
        print(f"  - {item.name} (is_file: {item.is_file()})")

    print(f"\nRecursive rglob('*'):")
    files = list(downloads_path.rglob('*'))
    print(f"  Total items: {len(files)}")
    for f in files:
        print(f"  - {f} (is_file: {f.is_file()})")

    print(f"\nFile count: {sum(1 for f in files if f.is_file())}")

# Now check what check_status returns
print("\n" + "="*80)
print("REPOSITORY INDEX CHECK_STATUS")
print("="*80)

indexer = RepositoryIndex()
status = indexer.get_processing_status('fracfocus')

print(f"\nStatus result:")
print(f"  Status: {status['status']}")
print(f"  Stages: {status['stages']}")
print(f"  Has downloads: {status['has_downloads']}")
print(f"  Files by stage:")
for stage, count in status['files_by_stage'].items():
    print(f"    {stage}: {count} files")

# Debug the actual path check
print("\n" + "="*80)
print("DEBUG PATH RESOLUTION")
print("="*80)

source_path = Path("data/raw/fracfocus")
print(f"\nSource path: {source_path}")
print(f"Exists: {source_path.exists()}")

# Check direct downloads path
direct_path = source_path / 'downloads'
print(f"\nDirect path: {direct_path}")
print(f"Exists: {direct_path.exists()}")

if not direct_path.exists():
    print("\nChecking subdirectories for nested downloads...")
    for subdir in source_path.iterdir():
        if subdir.is_dir() and subdir.name not in ['downloads', 'extracted', 'parsed', 'metadata']:
            print(f"\n  Subdir: {subdir.name}")
            nested_downloads = subdir / 'downloads'
            print(f"    Nested downloads: {nested_downloads}")
            print(f"    Exists: {nested_downloads.exists()}")

            if nested_downloads.exists():
                files = list(nested_downloads.rglob('*'))
                file_count = sum(1 for f in files if f.is_file())
                print(f"    Files: {file_count}")
                for f in files:
                    if f.is_file():
                        print(f"      - {f.name}")

print("\n" + "="*80 + "\n")
