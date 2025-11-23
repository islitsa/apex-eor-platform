"""
Parse RRC horizontal drilling permits (DAF318) from fixed-width format to CSV.

This script:
1. Reads the daf318 fixed-width file (360 chars per line)
2. Uses the data dictionary to extract fields by position
3. Outputs a single CSV file with all permits

Fixed-width format: 360 characters per record
"""

import csv
import json
from pathlib import Path
from datetime import datetime
import sys

def load_data_dictionary(dict_path):
    """Load the DAF318 data dictionary."""
    with open(dict_path, 'r') as f:
        return json.load(f)

def parse_fixed_width_line(line, fields):
    """
    Parse a fixed-width line using field definitions.

    Args:
        line: The fixed-width line (360 chars)
        fields: List of field definitions from data dictionary

    Returns:
        Dictionary of field_name: value
    """
    record = {}

    for field in fields:
        field_name = field['field_name']
        start = field['position_start'] - 1  # Convert to 0-indexed
        end = field['position_end']

        # Extract the value
        value = line[start:end].strip() if len(line) >= end else ''

        record[field_name] = value

    return record

def parse_daf318(input_file, output_file, data_dict):
    """
    Parse the entire DAF318 file.

    Args:
        input_file: Path to daf318 file
        output_file: Path to output CSV
        data_dict: Data dictionary with field definitions
    """
    fields = data_dict['fields']
    field_names = [f['field_name'] for f in fields]

    print(f"Parsing: {input_file}")
    print(f"Output: {output_file}")
    print(f"Fields: {len(field_names)}")
    print(f"Expected record length: {data_dict['record_length']}\n")

    records_parsed = 0
    records_skipped = 0

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=field_names)
            writer.writeheader()

            for line_num, line in enumerate(infile, 1):
                # Remove line ending
                line = line.rstrip('\n\r')

                # Skip empty lines
                if not line.strip():
                    records_skipped += 1
                    continue

                # Check length
                if len(line) != data_dict['record_length']:
                    if line_num <= 5 or records_parsed % 10000 == 0:
                        print(f"Warning: Line {line_num} has length {len(line)}, expected {data_dict['record_length']}")

                # Parse the line
                try:
                    record = parse_fixed_width_line(line, fields)
                    writer.writerow(record)
                    records_parsed += 1

                    if records_parsed % 10000 == 0:
                        print(f"Parsed {records_parsed:,} records...")

                except Exception as e:
                    print(f"Error parsing line {line_num}: {e}")
                    records_skipped += 1

    return records_parsed, records_skipped

def generate_summary(output_file, records_parsed, records_skipped, data_dict):
    """Generate a summary file."""
    output_path = Path(output_file)
    summary_file = output_path.parent / f"{output_path.stem}_summary.txt"

    file_size_mb = output_path.stat().st_size / (1024 * 1024)

    with open(summary_file, 'w') as f:
        f.write("DAF318 Horizontal Drilling Permits Parsing Summary\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("Input File:\n")
        f.write("-" * 60 + "\n")
        f.write(f"Source: {data_dict.get('file_path', 'N/A')}\n")
        f.write(f"Format: Fixed-width, {data_dict['record_length']} chars/record\n")
        f.write(f"Total expected records: {data_dict.get('total_records', 'Unknown'):,}\n\n")

        f.write("Parsing Results:\n")
        f.write("-" * 60 + "\n")
        f.write(f"Records parsed:    {records_parsed:>10,}\n")
        f.write(f"Records skipped:   {records_skipped:>10,}\n")
        f.write(f"Total processed:   {records_parsed + records_skipped:>10,}\n\n")

        f.write("Output File:\n")
        f.write("-" * 60 + "\n")
        f.write(f"File: {output_path.name}\n")
        f.write(f"Size: {file_size_mb:.1f} MB\n")
        f.write(f"Fields: {len(data_dict['fields'])}\n\n")

        f.write("Field Names:\n")
        f.write("-" * 60 + "\n")
        for i, field in enumerate(data_dict['fields'][:10], 1):
            f.write(f"  {i}. {field['field_name']}\n")
        if len(data_dict['fields']) > 10:
            f.write(f"  ... and {len(data_dict['fields']) - 10} more\n")

    print(f"\n[OK] Summary written to: {summary_file}")

if __name__ == "__main__":
    # Define paths
    project_root = Path(__file__).parent.parent.parent

    # Input files
    input_file = project_root / "data" / "raw" / "rrc" / "horizontal_drilling_permits" / "downloads" / "daf318"
    data_dict_file = project_root / "data" / "raw" / "rrc" / "metadata" / "data_dictionaries" / "daf318.json"

    # Output directory and file
    output_dir = project_root / "data" / "raw" / "rrc" / "horizontal_drilling_permits" / "parsed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "horizontal_permits.csv"

    print("=" * 60)
    print("DAF318 HORIZONTAL DRILLING PERMITS PARSER")
    print("=" * 60)
    print(f"Input: {input_file}")
    print(f"Dict: {data_dict_file}")
    print(f"Output: {output_file}")
    print("=" * 60 + "\n")

    # Check files exist
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    if not data_dict_file.exists():
        print(f"Error: Data dictionary not found: {data_dict_file}")
        sys.exit(1)

    # Load data dictionary
    print("Loading data dictionary...")
    data_dict = load_data_dictionary(data_dict_file)
    print(f"Loaded {len(data_dict['fields'])} field definitions\n")

    # Parse the file
    records_parsed, records_skipped = parse_daf318(input_file, output_file, data_dict)

    # Print results
    print("\n" + "=" * 60)
    print("PARSING COMPLETE!")
    print("=" * 60)
    print(f"Records parsed:  {records_parsed:,}")
    print(f"Records skipped: {records_skipped:,}")
    print(f"Output file:     {output_file}")

    # Generate summary
    generate_summary(output_file, records_parsed, records_skipped, data_dict)

    print("\nNext steps:")
    print("  1. Review horizontal_permits_summary.txt")
    print("  2. Examine CSV for data quality")
    print("  3. Link to completion data via API numbers")
    print("  4. Load into database for analysis")
