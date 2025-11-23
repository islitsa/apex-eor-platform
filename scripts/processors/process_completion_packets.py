"""
RRC Completion Packet Processor - TARGETED EXTRACTION
Extracts only the specific record types needed for merging with production data

Extracts:
  - PACKET (lease/API identifiers)
  - W-2 Formation Data (landing zones)
  - W-2 Casing/Tubing/Liner Data (completion details)

Usage:
    python scripts/process_completion_packets.py
"""

import os
from pathlib import Path
import pandas as pd
from collections import defaultdict

def parse_dat_file(file_path):
    """
    Parse RRC .dat file with { delimiter.
    
    Returns:
        Dictionary of dataframes, one for each record type
    """
    records = defaultdict(list)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Split by { delimiter
                fields = line.split('{')
                
                # First field is the record type
                record_type = fields[0] if fields else 'UNKNOWN'
                
                # Store all fields
                records[record_type].append(fields)
        
        # Convert to dataframes
        dataframes = {}
        for record_type, data in records.items():
            if data:
                # Create dataframe with numbered columns
                max_cols = max(len(row) for row in data)
                df_data = []
                
                for row in data:
                    # Pad row to max_cols length
                    padded_row = row + [''] * (max_cols - len(row))
                    df_data.append(padded_row)
                
                # Create column names
                col_names = ['record_type'] + [f'field_{i}' for i in range(1, max_cols)]
                df = pd.DataFrame(df_data, columns=col_names)
                dataframes[record_type] = df
        
        return dataframes
    
    except Exception as e:
        print(f"Error parsing {file_path.name}: {str(e)}")
        return {}


def scan_extracted_structure(extracted_dir):
    """
    Scan the extracted directory and catalog all .dat files.
    Structure: extracted/date/district/trackingNo/file.dat
    """
    extracted_path = Path(extracted_dir)
    file_catalog = []
    
    # Level 1: Date folders (01-01-2022, etc.)
    for date_folder in sorted(extracted_path.iterdir()):
        if not date_folder.is_dir():
            continue
        
        date_name = date_folder.name
        
        # Level 2: District folders (8A, 09, 08, 7C, etc.)
        for district_folder in date_folder.iterdir():
            if not district_folder.is_dir():
                continue
            
            district_name = district_folder.name
            
            # Level 3: Tracking folders (trackingNo_260662, etc.)
            for tracking_folder in district_folder.iterdir():
                if not tracking_folder.is_dir():
                    continue
                
                tracking_name = tracking_folder.name
                
                # Level 4: .dat files
                for dat_file in tracking_folder.glob("*.dat"):
                    file_catalog.append({
                        'date': date_name,
                        'district': district_name,
                        'tracking_folder': tracking_name,
                        'filename': dat_file.name,
                        'full_path': dat_file,
                        'size': dat_file.stat().st_size
                    })
    
    return file_catalog


def export_by_record_type(extracted_dir, output_dir, record_types=None):
    """
    Export specific record types only.
    
    Args:
        extracted_dir: Source directory
        output_dir: Output directory
        record_types: List of record types to export (None = all)
    """
    file_catalog = scan_extracted_structure(extracted_dir)
    all_records = defaultdict(list)
    
    print(f"Processing {len(file_catalog):,} files...")
    
    for idx, item in enumerate(file_catalog, 1):
        if idx % 1000 == 0:
            print(f"  Processed {idx:,}/{len(file_catalog):,} files...")
        
        dataframes = parse_dat_file(item['full_path'])
        
        for record_type, df in dataframes.items():
            if record_types is None or record_type in record_types:
                df['source_date'] = item['date']
                df['district'] = item['district']
                df['tracking_folder'] = item['tracking_folder']
                df['source_file'] = item['filename']
                all_records[record_type].append(df)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 70)
    print("SAVING RECORD TYPES")
    print("=" * 70 + "\n")
    
    for record_type, df_list in all_records.items():
        combined_df = pd.concat(df_list, ignore_index=True)
        safe_name = record_type.replace(' ', '_').replace('/', '_')
        output_file = output_path / f"{safe_name}.parquet"
        combined_df.to_parquet(output_file, index=False, engine='pyarrow')
        print(f"✓ {safe_name}.parquet")
        print(f"    Rows: {len(combined_df):,} | Columns: {len(combined_df.columns)}")
    
    print(f"\n✓ Saved {len(all_records)} record types to: {output_path}")


# Main workflow
if __name__ == "__main__":
    # Define paths
    project_root = Path(__file__).parent.parent
    extracted_dir = project_root / "data" / "raw" / "rrc" / "extracted"
    interim_dir = project_root / "data" / "interim" / "rrc"
    
    # ONLY export the record types we actually need for merging
    record_types_needed = [
        'PACKET',
        'W-2',
        'W-2 Formation Data',
        'W-2 Casing Data',
        'W-2 Tubing Data',
        'W-2 Production Interval Data',
        'W-2 Liner Data'
    ]
    
    print("=" * 70)
    print("EXTRACTING ONLY REQUIRED RECORD TYPES")
    print("=" * 70)
    print(f"\nRecord types to extract:")
    for rt in record_types_needed:
        print(f"  - {rt}")
    print()
    
    # Process only these specific record types
    export_by_record_type(
        extracted_dir, 
        interim_dir,
        record_types=record_types_needed
    )