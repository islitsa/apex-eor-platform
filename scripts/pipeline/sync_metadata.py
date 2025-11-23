"""
Sync Metadata Files with Actual Parsed Data

Scans data/raw/*/parsed/ folders and updates metadata.json files
with accurate statistics from the actual files.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent

def get_parquet_stats(parquet_file):
    """Get row count and size from parquet file"""
    try:
        df = pd.read_parquet(parquet_file)
        return {
            'rows': len(df),
            'size_bytes': parquet_file.stat().st_size,
            'columns': len(df.columns)
        }
    except Exception as e:
        print(f"  [ERROR] Could not read {parquet_file.name}: {e}")
        return None

def get_csv_stats(csv_file):
    """Get row count and size from CSV file"""
    try:
        # Just count lines without loading whole file
        with open(csv_file, 'r', encoding='utf-8') as f:
            rows = sum(1 for _ in f) - 1  # Subtract header
        return {
            'rows': rows,
            'size_bytes': csv_file.stat().st_size
        }
    except Exception as e:
        print(f"  [ERROR] Could not read {csv_file.name}: {e}")
        return None

def sync_dataset_metadata(dataset_path, metadata_file):
    """Sync metadata for a single dataset"""
    print(f"\n{'='*70}")
    print(f"Dataset: {dataset_path.name}")
    print(f"{'='*70}")

    # Check parsed folder
    parsed_dir = dataset_path / 'parsed'
    if not parsed_dir.exists():
        print(f"  [SKIP] No parsed folder found")
        return

    # Find all parsed files
    csv_files = list(parsed_dir.glob('*.csv'))
    parquet_files = list(parsed_dir.glob('*.parquet'))

    if not csv_files and not parquet_files:
        print(f"  [SKIP] No CSV or parquet files in parsed folder")
        return

    print(f"  Found: {len(csv_files)} CSV files, {len(parquet_files)} parquet files")

    # Scan files and collect stats
    total_rows = 0
    total_size_bytes = 0
    file_stats = []

    # Process parquet files (prefer these as they're faster to scan)
    for pq_file in parquet_files:
        print(f"  Scanning: {pq_file.name}...", end=' ')
        stats = get_parquet_stats(pq_file)
        if stats:
            total_rows += stats['rows']
            total_size_bytes += stats['size_bytes']
            file_stats.append({
                'file': pq_file.name,
                'rows': stats['rows'],
                'size_bytes': stats['size_bytes'],
                'format': 'parquet'
            })
            print(f"{stats['rows']:,} rows, {stats['size_bytes']/(1024**2):.1f} MB")

    # Process CSV files (slower)
    for csv_file in csv_files:
        print(f"  Scanning: {csv_file.name}...", end=' ')
        stats = get_csv_stats(csv_file)
        if stats:
            total_rows += stats['rows']
            total_size_bytes += stats['size_bytes']
            file_stats.append({
                'file': csv_file.name,
                'rows': stats['rows'],
                'size_bytes': stats['size_bytes'],
                'format': 'csv'
            })
            print(f"{stats['rows']:,} rows, {stats['size_bytes']/(1024**2):.1f} MB")

    # Update metadata.json
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = {}

    # Update parsed section
    metadata['parsed'] = {
        'path': 'parsed/',
        'status': 'complete',
        'format': 'parquet' if parquet_files else 'csv',
        'total_files': len(csv_files) + len(parquet_files),
        'total_rows': total_rows,
        'total_size_bytes': total_size_bytes,
        'total_size_human': f"{total_size_bytes / (1024**3):.2f} GB" if total_size_bytes > 1024**3 else f"{total_size_bytes / (1024**2):.1f} MB",
        'files': file_stats,
        'last_updated': datetime.now().isoformat()
    }

    # Update processing_state
    if 'processing_state' not in metadata:
        metadata['processing_state'] = {}

    metadata['processing_state'].update({
        'parsing': 'complete',
        'parsing_date': datetime.now().isoformat(),
        'parsed_files': len(csv_files) + len(parquet_files)
    })

    # Save updated metadata
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n  [OK] Updated metadata.json")
    print(f"  Total: {total_rows:,} rows | {total_size_bytes/(1024**3):.2f} GB")

def main():
    """Main sync function"""
    print("\n" + "="*70)
    print("METADATA SYNC - Scanning Actual Parsed Data")
    print("="*70)

    # Define datasets to sync
    datasets = [
        {
            'path': PROJECT_ROOT / 'data/raw/rrc/production',
            'metadata': PROJECT_ROOT / 'data/raw/rrc/production/metadata.json'
        },
        {
            'path': PROJECT_ROOT / 'data/raw/rrc/completions_data',
            'metadata': PROJECT_ROOT / 'data/raw/rrc/completions_data/metadata.json'
        },
        {
            'path': PROJECT_ROOT / 'data/raw/rrc/horizontal_drilling_permits',
            'metadata': PROJECT_ROOT / 'data/raw/rrc/horizontal_drilling_permits/metadata.json'
        },
        {
            'path': PROJECT_ROOT / 'data/raw/fracfocus',
            'metadata': PROJECT_ROOT / 'data/raw/fracfocus/metadata.json'
        }
    ]

    for dataset in datasets:
        sync_dataset_metadata(dataset['path'], dataset['metadata'])

    print("\n" + "="*70)
    print("SYNC COMPLETE!")
    print("="*70)
    print("\nAll metadata.json files updated with accurate statistics.")
    print("You can now run the dashboard and see correct metrics per SOR.")
    print("="*70)

if __name__ == '__main__':
    main()
