"""
Convert production DSV files to CSV format (optional).

The production data is already in a structured format with headers.
This script simply converts the delimiter from } to , (CSV).

NOTE: This is optional - you can load DSV files directly into pandas/database.
Only run this if you need CSV format specifically.
"""

import csv
from pathlib import Path
from datetime import datetime
import sys

def convert_dsv_to_csv(input_file, output_file, delimiter='}'):
    """
    Convert a DSV file to CSV.

    Args:
        input_file: Path to .dsv file
        output_file: Path to output .csv file
        delimiter: Input delimiter (default: })
    """
    print(f"Converting: {input_file.name}")

    rows_converted = 0

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        # Read DSV with } delimiter
        reader = csv.reader(infile, delimiter=delimiter)

        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            # Write CSV with , delimiter
            writer = csv.writer(outfile)

            for row in reader:
                writer.writerow(row)
                rows_converted += 1

                if rows_converted % 100000 == 0:
                    print(f"  {rows_converted:,} rows...")

    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"  Complete: {rows_converted:,} rows ({file_size_mb:.1f} MB)\n")

    return rows_converted

def convert_all_production_dsv(extracted_dir, output_dir):
    """
    Convert all DSV files to CSV.

    Args:
        extracted_dir: Directory with .dsv files
        output_dir: Output directory for .csv files
    """
    extracted_path = Path(extracted_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all .dsv files
    dsv_files = sorted(extracted_path.glob("*.dsv"))

    if not dsv_files:
        print(f"No .dsv files found in {extracted_path}")
        return

    print(f"Found {len(dsv_files)} DSV files\n")

    total_rows = 0
    results = []

    for dsv_file in dsv_files:
        # Output filename: same name but .csv extension
        csv_file = output_path / dsv_file.name.replace('.dsv', '.csv')

        rows = convert_dsv_to_csv(dsv_file, csv_file)
        total_rows += rows

        results.append({
            'file': dsv_file.name,
            'rows': rows,
            'size_mb': csv_file.stat().st_size / (1024 * 1024)
        })

    # Print summary
    print("\n" + "=" * 60)
    print("CONVERSION SUMMARY")
    print("=" * 60)
    print(f"{'File':<45} {'Rows':>10} {'Size':>10}")
    print("-" * 60)

    for result in results:
        print(f"{result['file']:<45} {result['rows']:>10,} {result['size_mb']:>9.1f}M")

    print("-" * 60)
    print(f"{'TOTAL':<45} {total_rows:>10,}")

    return results

if __name__ == "__main__":
    # Define paths
    project_root = Path(__file__).parent.parent.parent
    extracted_dir = project_root / "data" / "raw" / "rrc" / "production" / "extracted"
    output_dir = project_root / "data" / "raw" / "rrc" / "production" / "parsed"

    print("=" * 60)
    print("PRODUCTION DSV TO CSV CONVERTER")
    print("=" * 60)
    print(f"Source: {extracted_dir}")
    print(f"Output: {output_dir}")
    print("=" * 60)
    print("\nNOTE: This is optional - DSV files can be loaded directly!")
    print("Only run this if you specifically need CSV format.\n")
    print("=" * 60 + "\n")

    # Check if directory exists
    if not extracted_dir.exists():
        print(f"Error: Directory not found: {extracted_dir}")
        sys.exit(1)

    # Convert all files
    results = convert_all_production_dsv(extracted_dir, output_dir)

    print("\n" + "=" * 60)
    print("CONVERSION COMPLETE!")
    print("=" * 60)
    print(f"\nCSV files saved to: {output_dir}")
    print("\nYou can now:")
    print("  1. Load CSV files into pandas/Excel")
    print("  2. Import into database")
    print("  3. Use for analysis")
    print("\nOR just use the original DSV files directly:")
    print("  pd.read_csv('file.dsv', sep='}', engine='python')")
