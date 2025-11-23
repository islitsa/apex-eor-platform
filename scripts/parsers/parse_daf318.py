"""
parse_daf318.py - Horizontal Drilling Permits Parser

Parses DAF318 format files containing horizontal drilling permit data
from the Texas Railroad Commission.

DAF318 Format:
- Fixed-width sequential file (360 characters per record)
- Contains information on every application to drill for a horizontal well
- Based on official RRC documentation: horizontaldrillingpermits.pdf

Author: Data Engineering Team
Date: 2025-10-24
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List


class DAF318Parser:
    """Parser for DAF318 (Horizontal Drilling Permits) fixed-width format files."""

    # Field specifications based on official RRC documentation
    FIELD_SPECS = [
        ('permit_number', 1, 7, 'int'),
        ('permit_sequence', 8, 9, 'int'),
        ('permit_district', 10, 11, 'int'),
        ('county_name', 12, 24, 'str'),
        ('api_county', 25, 27, 'int'),
        ('api_unique_number', 28, 32, 'int'),
        ('permit_operator_number', 33, 38, 'int'),
        ('operator_name', 39, 70, 'str'),
        ('permit_lease_name', 71, 102, 'str'),
        ('permit_issued_date', 103, 110, 'date'),
        ('permit_total_depth', 111, 115, 'int'),
        ('permit_section', 116, 123, 'str'),
        ('permit_block', 124, 133, 'str'),
        ('permit_abstract', 134, 139, 'str'),
        ('permit_survey', 140, 194, 'str'),
        ('permit_well_number', 195, 200, 'str'),
        ('field_name', 201, 232, 'str'),
        ('validated_field_name', 233, 264, 'str'),
        ('validated_well_date', 265, 272, 'date'),
        ('validated_operator_name', 273, 304, 'str'),
        ('oil_or_gas', 305, 305, 'str'),
        ('validated_lease_number', 306, 311, 'str'),
        ('validated_lease_name', 312, 343, 'str'),
        ('validated_well_number', 344, 349, 'str'),
        ('val_off_schedule_flag', 350, 350, 'str'),
        ('total_permitted_fields', 351, 352, 'int'),
        ('total_validated_fields', 353, 354, 'int'),
        ('filler', 355, 360, 'str'),
    ]

    def __init__(self, metadata_path: Optional[str] = None):
        """
        Initialize parser.

        Args:
            metadata_path: Optional path to data dictionary JSON file
                          (e.g., data/raw/rrc/metadata/data_dictionaries/daf318.json)
        """
        self.metadata = None
        if metadata_path:
            self.load_metadata(metadata_path)

    def load_metadata(self, metadata_path: str) -> None:
        """Load metadata JSON file."""
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)

    @staticmethod
    def parse_date(date_str: str) -> Optional[str]:
        """
        Parse date from CCYYMMDD or YYYYMMDD format.

        Args:
            date_str: Date string to parse

        Returns:
            ISO formatted date string (YYYY-MM-DD) or None if invalid
        """
        date_str = date_str.strip()
        if not date_str or date_str == '0' * len(date_str):
            return None

        try:
            if len(date_str) == 8:
                # CCYYMMDD or YYYYMMDD format
                year = int(date_str[:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])

                if year == 0 or month == 0 or day == 0:
                    return None

                date_obj = datetime(year, month, day)
                return date_obj.strftime('%Y-%m-%d')
        except (ValueError, IndexError):
            return None

        return None

    @staticmethod
    def parse_field(value: str, field_type: str) -> any:
        """
        Parse individual field based on type.

        Args:
            value: Raw field value
            field_type: Type of field ('str', 'int', 'date')

        Returns:
            Parsed value
        """
        value = value.strip()

        if field_type == 'str':
            return value if value else None
        elif field_type == 'int':
            try:
                return int(value) if value and value != '0' * len(value) else None
            except ValueError:
                return None
        elif field_type == 'date':
            return DAF318Parser.parse_date(value)

        return value

    def parse_line(self, line: str) -> Dict:
        """
        Parse a single line from DAF318 file.

        Args:
            line: Single line from file

        Returns:
            Dictionary with parsed fields
        """
        record = {}

        for field_name, start, end, field_type in self.FIELD_SPECS:
            # Convert to 0-based indexing
            value = line[start-1:end]
            parsed_value = self.parse_field(value, field_type)
            record[field_name] = parsed_value

        # Add computed fields
        if record['api_county'] and record['api_unique_number']:
            record['api_number'] = f"{record['api_county']:03d}{record['api_unique_number']:05d}"
        else:
            record['api_number'] = None

        return record

    def parse_file(self, file_path: str, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Parse entire DAF318 file into DataFrame.

        Args:
            file_path: Path to DAF318 file
            limit: Optional limit on number of records to parse

        Returns:
            DataFrame with parsed records
        """
        records = []

        with open(file_path, 'r', encoding='latin-1') as f:
            for i, line in enumerate(f):
                if limit and i >= limit:
                    break

                try:
                    record = self.parse_line(line)
                    records.append(record)
                except Exception as e:
                    print(f"Error parsing line {i+1}: {e}")
                    continue

        df = pd.DataFrame(records)
        return df

    def export_to_csv(self, input_path: str, output_path: str,
                      limit: Optional[int] = None) -> None:
        """
        Parse DAF318 file and export to CSV.

        Args:
            input_path: Path to DAF318 file
            output_path: Path for output CSV file
            limit: Optional limit on number of records
        """
        df = self.parse_file(input_path, limit=limit)
        df.to_csv(output_path, index=False)
        print(f"Exported {len(df)} records to {output_path}")

    def export_to_parquet(self, input_path: str, output_path: str,
                          limit: Optional[int] = None) -> None:
        """
        Parse DAF318 file and export to Parquet.

        Args:
            input_path: Path to DAF318 file
            output_path: Path for output Parquet file
            limit: Optional limit on number of records
        """
        df = self.parse_file(input_path, limit=limit)
        df.to_parquet(output_path, index=False, engine='pyarrow')
        print(f"Exported {len(df)} records to {output_path}")


def main():
    """Example usage of DAF318Parser."""

    # Initialize parser
    parser = DAF318Parser()

    # Define paths
    input_file = "data/raw/rrc/downloads/horizontal_drilling_permits/daf318"
    output_csv = "data/processed/rrc/daf318_horizontal_permits.csv"
    output_parquet = "data/processed/rrc/daf318_horizontal_permits.parquet"

    # Parse first 1000 records as a test
    print("Parsing DAF318 file (first 1000 records)...")
    df = parser.parse_file(input_file, limit=1000)

    # Display info
    print(f"\nParsed {len(df)} records")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst record:")
    print(df.iloc[0].to_dict())

    # Display summary statistics
    print(f"\nSummary:")
    print(f"  Unique permits: {df['permit_number'].nunique()}")
    print(f"  Date range: {df['permit_issued_date'].min()} to {df['permit_issued_date'].max()}")
    print(f"  Counties: {df['county_name'].nunique()}")
    print(f"  Oil vs Gas: {df['oil_or_gas'].value_counts().to_dict()}")

    # Optionally export to CSV
    # parser.export_to_csv(input_file, output_csv)

    # Optionally export to Parquet
    # parser.export_to_parquet(input_file, output_parquet)


if __name__ == "__main__":
    main()
