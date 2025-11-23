"""
Parse RRC completion data from delimited .dat files into structured CSV tables.

This script:
1. Reads all .dat files from extracted/ folder (25,106 files)
2. Parses delimited format (delimiter: {)
3. Identifies record types (PACKET, G-1, W-2, P-4, etc.)
4. Flattens nested folder structure
5. Outputs separate CSV files per record type in parsed/ folder
"""

import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import sys

def parse_delimited_line(line, delimiter='{'):
    """Parse a delimited line into fields."""
    return line.strip().split(delimiter)

def identify_record_type(fields):
    """Identify the record type from the first field."""
    if not fields:
        return None

    record_type = fields[0].strip()

    # Only keep known structured record types (filter out comments/remarks)
    valid_types = {
        'PACKET', 'PACKET_WORKOVER',
        'G-1', 'G-1 Measurement Data', 'G-1 Field Data', 'G-1 Amount And Material Data',
        'G-1 Multi-Completion Data', 'G-1 Casing Data', 'G-1 Liner Data', 'G-1 Tubing Data',
        'G-1 Production Interval Data', 'G-1 Formation Data',
        'W-2', 'W-2 Amount And Material Data', 'W-2 Multi-Completion Data',
        'W-2 Casing Data', 'W-2 Liner Data', 'W-2 Tubing Data',
        'W-2 Production Interval Data', 'W-2 Formation Data',
        'P-4', 'P-4 Gas Gatherer Data', 'P-4 Oil Gatherer Data',
        'P-15', 'G-5', 'G-10', 'W-12', 'L-1'
    }

    if record_type in valid_types:
        return record_type

    return None  # Ignore unstructured comments/remarks

def parse_dat_file(file_path):
    """
    Parse a single .dat file and extract all records.

    Returns dict of record_type -> list of records
    """
    records_by_type = defaultdict(list)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                fields = parse_delimited_line(line)
                record_type = identify_record_type(fields)

                if record_type:
                    records_by_type[record_type].append(fields)

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

    return records_by_type

def process_all_dat_files(extracted_dir, parsed_dir):
    """
    Process all .dat files in extracted directory.

    Args:
        extracted_dir: Path to extracted/ folder with nested structure
        parsed_dir: Path to parsed/ output folder
    """
    extracted_path = Path(extracted_dir)
    parsed_path = Path(parsed_dir)
    parsed_path.mkdir(parents=True, exist_ok=True)

    # Find all .dat files
    dat_files = list(extracted_path.rglob("*.dat"))
    total_files = len(dat_files)

    print(f"Found {total_files} .dat files to parse")
    print(f"Output directory: {parsed_path}\n")

    # Accumulate all records by type
    all_records = defaultdict(list)

    # Process each file
    for i, dat_file in enumerate(dat_files, 1):
        if i % 1000 == 0 or i == 1:
            print(f"Processing file {i}/{total_files}...")

        records = parse_dat_file(dat_file)

        if records:
            # Extract metadata from path: date/district/trackingNo
            parts = dat_file.relative_to(extracted_path).parts
            if len(parts) >= 3:
                date_folder = parts[0]  # e.g., "01-01-2022"
                district = parts[1]     # e.g., "09"
                tracking_folder = parts[2]  # e.g., "trackingNo_260663"

                # Add metadata to each record
                for record_type, record_list in records.items():
                    for record_fields in record_list:
                        # Prepend metadata columns
                        enriched_record = [date_folder, district, tracking_folder] + record_fields
                        all_records[record_type].append(enriched_record)

    print(f"\nParsing complete! Processed {total_files} files")
    print(f"\nRecord types found:")
    for record_type, records in sorted(all_records.items()):
        print(f"  {record_type}: {len(records):,} records")

    # Write each record type to a separate CSV
    print(f"\nWriting CSV files to {parsed_path}...")

    for record_type, records in all_records.items():
        if not records:
            continue

        # Create safe filename from record type
        safe_filename = record_type.replace(' ', '_').replace('-', '_').lower()
        output_file = parsed_path / f"{safe_filename}.csv"

        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Write header: metadata columns + data columns
                max_fields = max(len(record) for record in records)
                header = ['submission_date', 'district', 'tracking_folder'] + \
                         [f'field_{i}' for i in range(max_fields - 3)]
                writer.writerow(header)

                # Write all records
                for record in records:
                    # Pad with empty strings if needed
                    padded_record = record + [''] * (max_fields - len(record))
                    writer.writerow(padded_record)

            file_size = output_file.stat().st_size / (1024 * 1024)  # MB
            print(f"  [OK] {output_file.name}: {len(records):,} rows ({file_size:.1f} MB)")

        except Exception as e:
            print(f"  [ERROR] Error writing {output_file.name}: {e}")

    return all_records

def generate_summary(all_records, parsed_dir):
    """Generate a summary file of the parsing results."""
    parsed_path = Path(parsed_dir)
    summary_file = parsed_path / "_parsing_summary.txt"

    with open(summary_file, 'w') as f:
        f.write("RRC Completion Data Parsing Summary\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("Record Types and Counts:\n")
        f.write("-" * 60 + "\n")

        total_records = 0
        for record_type, records in sorted(all_records.items()):
            count = len(records)
            total_records += count
            f.write(f"{record_type:40} {count:>10,} records\n")

        f.write("-" * 60 + "\n")
        f.write(f"{'TOTAL':40} {total_records:>10,} records\n\n")

        f.write("Output Files:\n")
        f.write("-" * 60 + "\n")
        for csv_file in sorted(parsed_path.glob("*.csv")):
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            f.write(f"{csv_file.name:40} {size_mb:>10.1f} MB\n")

    print(f"\n[OK] Summary written to: {summary_file}")

if __name__ == "__main__":
    # Define paths
    project_root = Path(__file__).parent.parent.parent
    extracted_dir = project_root / "data" / "raw" / "rrc" / "completions_data" / "extracted"
    parsed_dir = project_root / "data" / "raw" / "rrc" / "completions_data" / "parsed"

    print("=" * 60)
    print("RRC COMPLETION DATA PARSER")
    print("=" * 60)
    print(f"Source: {extracted_dir}")
    print(f"Output: {parsed_dir}")
    print("=" * 60 + "\n")

    # Check if extracted directory exists
    if not extracted_dir.exists():
        print(f"Error: Extracted directory not found: {extracted_dir}")
        sys.exit(1)

    # Process all files
    all_records = process_all_dat_files(extracted_dir, parsed_dir)

    # Generate summary
    generate_summary(all_records, parsed_dir)

    print("\n" + "=" * 60)
    print("PARSING COMPLETE!")
    print("=" * 60)
    print(f"\nParsed data available in: {parsed_dir}")
    print("\nNext steps:")
    print("  1. Review _parsing_summary.txt for statistics")
    print("  2. Examine CSV files for data quality")
    print("  3. Map field names using data dictionaries")
    print("  4. Load into database or analysis tool")
