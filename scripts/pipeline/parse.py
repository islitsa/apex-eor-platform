"""
Parsing Orchestrator

Handles parsing of all extracted data sources into structured formats:
- DSV to CSV conversion (RRC production)
- Fixed-width parsing (RRC permits)
- Delimited file parsing (RRC completions)
- CSV consolidation (FracFocus)

Usage:
    orchestrator = ParsingOrchestrator()
    orchestrator.parse_all()
"""

import os
import sys
import json
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from tqdm import tqdm

# Add scripts directory to path to import existing parsers
SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))


class ParsingOrchestrator:
    """Orchestrates parsing of all extracted data"""

    def __init__(self, base_data_dir: str = 'data/raw'):
        """
        Initialize parsing orchestrator

        Args:
            base_data_dir: Base directory containing raw data
        """
        self.base_data_dir = Path(base_data_dir)
        self.rrc_dir = self.base_data_dir / 'rrc'
        self.fracfocus_dir = self.base_data_dir / 'fracfocus'

    def _update_metadata(self, dataset_path: Path, status: str, step: str, **kwargs):
        """Update metadata.json with parsing status"""
        metadata_file = dataset_path / 'metadata.json'

        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {}

        if 'processing_state' not in metadata:
            metadata['processing_state'] = {}

        metadata['processing_state'][step] = status
        metadata['processing_state'][f'{step}_date'] = datetime.now().isoformat()

        # Add any additional metadata
        for key, value in kwargs.items():
            metadata['processing_state'][key] = value

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def parse_rrc_production(self) -> bool:
        """
        Parse RRC production data (DSV to CSV)

        Converts pipe/delimiter-separated files to standard CSV format
        """
        extracted_dir = self.rrc_dir / 'production' / 'extracted'
        parsed_dir = self.rrc_dir / 'production' / 'parsed'

        if not extracted_dir.exists():
            print(f"Production extracted directory not found: {extracted_dir}")
            return False

        print("\n" + "="*70)
        print("PARSING RRC PRODUCTION DATA")
        print("="*70)

        parsed_dir.mkdir(parents=True, exist_ok=True)

        # Find all .dsv files
        dsv_files = list(extracted_dir.glob('*.dsv')) + list(extracted_dir.glob('*.DSV'))

        if not dsv_files:
            print("No DSV files found to parse")
            return False

        print(f"Found {len(dsv_files)} DSV files to parse")

        parsed_count = 0
        for dsv_file in tqdm(dsv_files, desc="Parsing DSV files"):
            try:
                output_file = parsed_dir / f"{dsv_file.stem}.csv"

                # Read DSV with } delimiter and convert to CSV
                print(f"\nParsing {dsv_file.name}...")

                # Try to detect the delimiter
                with open(dsv_file, 'r', encoding='utf-8', errors='ignore') as f:
                    first_line = f.readline()
                    if '}' in first_line:
                        delimiter = '}'
                    elif '|' in first_line:
                        delimiter = '|'
                    else:
                        delimiter = ','

                print(f"  Detected delimiter: '{delimiter}'")

                # Read and convert
                df = pd.read_csv(
                    dsv_file,
                    delimiter=delimiter,
                    engine='python',
                    encoding='utf-8',
                    on_bad_lines='warn',
                    low_memory=False
                )

                # Write to CSV
                df.to_csv(output_file, index=False)
                print(f"  ✓ Wrote {len(df):,} rows to {output_file.name}")

                parsed_count += 1

            except Exception as e:
                print(f"  ✗ Failed to parse {dsv_file.name}: {e}")

        print(f"\n✓ Parsed {parsed_count}/{len(dsv_files)} files")

        self._update_metadata(
            self.rrc_dir / 'production',
            'complete',
            'parsing',
            parsed_files=parsed_count,
            total_files=len(dsv_files)
        )

        return parsed_count > 0

    def parse_rrc_permits(self) -> bool:
        """
        Parse RRC horizontal drilling permits (fixed-width format)

        Uses the existing DAF318Parser
        """
        from parsers.parse_daf318 import DAF318Parser

        source_file = self.rrc_dir / 'horizontal_drilling_permits' / 'extracted' / 'daf318.txt'
        parsed_dir = self.rrc_dir / 'horizontal_drilling_permits' / 'parsed'

        if not source_file.exists():
            # Try downloads directory
            source_file = self.rrc_dir / 'horizontal_drilling_permits' / 'downloads' / 'daf318.txt'

        if not source_file.exists():
            print(f"Permits file not found: {source_file}")
            return False

        print("\n" + "="*70)
        print("PARSING RRC HORIZONTAL DRILLING PERMITS")
        print("="*70)

        parsed_dir.mkdir(parents=True, exist_ok=True)

        try:
            parser = DAF318Parser()
            output_file = parsed_dir / 'horizontal_permits.csv'

            print(f"Parsing {source_file.name}...")
            df = parser.parse_file(str(source_file))

            # Save to CSV
            df.to_csv(output_file, index=False)
            print(f"✓ Parsed {len(df):,} permits to {output_file}")

            self._update_metadata(
                self.rrc_dir / 'horizontal_drilling_permits',
                'complete',
                'parsing',
                records_parsed=len(df)
            )

            return True

        except Exception as e:
            print(f"✗ Failed to parse permits: {e}")
            return False

    def parse_rrc_completions(self) -> bool:
        """
        Parse RRC completion packets

        Uses the existing completion packet parser
        """
        extracted_dir = self.rrc_dir / 'completions_data' / 'extracted'
        parsed_dir = self.rrc_dir / 'completions_data' / 'parsed'

        if not extracted_dir.exists():
            print(f"Completions extracted directory not found: {extracted_dir}")
            return False

        print("\n" + "="*70)
        print("PARSING RRC COMPLETION PACKETS")
        print("="*70)

        # Check if parse_completion_data.py exists
        completion_parser = SCRIPTS_DIR / 'extractors' / 'parse_completion_data.py'

        if not completion_parser.exists():
            print(f"Completion parser script not found: {completion_parser}")
            print("Please ensure parse_completion_data.py is in scripts/extractors/")
            return False

        try:
            # Import and run the parser
            from extractors.parse_completion_data import parse_completion_packets

            parsed_dir.mkdir(parents=True, exist_ok=True)

            print(f"Parsing completion packets from {extracted_dir}...")
            result = parse_completion_packets(str(extracted_dir), str(parsed_dir))

            if result:
                print(f"✓ Completion packets parsed successfully")

                self._update_metadata(
                    self.rrc_dir / 'completions_data',
                    'complete',
                    'parsing'
                )

                return True
            else:
                print("✗ Completion parsing returned False")
                return False

        except ImportError as e:
            print(f"✗ Could not import completion parser: {e}")
            print("Skipping completion parsing (requires manual implementation)")
            return False
        except Exception as e:
            print(f"✗ Failed to parse completions: {e}")
            return False

    def parse_fracfocus(self) -> bool:
        """
        Parse FracFocus CSV data

        Consolidates multiple CSV files and organizes them
        """
        extracted_dir = self.fracfocus_dir / 'extracted'
        parsed_dir = self.fracfocus_dir / 'parsed'

        if not extracted_dir.exists():
            print(f"FracFocus extracted directory not found: {extracted_dir}")
            return False

        print("\n" + "="*70)
        print("PARSING FRACFOCUS DATA")
        print("="*70)

        parsed_dir.mkdir(parents=True, exist_ok=True)

        # Find all CSV files
        csv_files = list(extracted_dir.glob('**/*.csv'))

        if not csv_files:
            print("No CSV files found to parse")
            return False

        print(f"Found {len(csv_files)} CSV files")

        try:
            # Group files by type
            registry_files = [f for f in csv_files if 'FracFocusRegistry' in f.name]
            disclosure_files = [f for f in csv_files if 'DisclosureList' in f.name]
            water_files = [f for f in csv_files if 'WaterSource' in f.name]

            print(f"\nFile breakdown:")
            print(f"  - Registry files: {len(registry_files)}")
            print(f"  - Disclosure files: {len(disclosure_files)}")
            print(f"  - Water source files: {len(water_files)}")

            # Simply copy organized files to parsed directory
            for csv_file in tqdm(csv_files, desc="Organizing CSV files"):
                dest_file = parsed_dir / csv_file.name

                # If file doesn't exist in parsed, copy it
                if not dest_file.exists():
                    import shutil
                    shutil.copy2(csv_file, dest_file)

            print(f"\n✓ Organized {len(csv_files)} CSV files to {parsed_dir}")

            self._update_metadata(
                self.fracfocus_dir,
                'complete',
                'parsing',
                csv_files=len(csv_files),
                registry_files=len(registry_files),
                disclosure_files=len(disclosure_files),
                water_files=len(water_files)
            )

            return True

        except Exception as e:
            print(f"✗ Failed to parse FracFocus data: {e}")
            return False

    def parse_all(self) -> Dict[str, bool]:
        """
        Parse all extracted datasets

        Returns:
            Dictionary with parsing status for each dataset
        """
        print("\n" + "="*70)
        print("PARSING ORCHESTRATOR")
        print("="*70)

        results = {
            'rrc_production': self.parse_rrc_production(),
            'rrc_permits': self.parse_rrc_permits(),
            'rrc_completions': self.parse_rrc_completions(),
            'fracfocus': self.parse_fracfocus()
        }

        print("\n" + "="*70)
        print("PARSING SUMMARY")
        print("="*70)
        for dataset, success in results.items():
            status = "✓" if success else "✗"
            print(f"{status} {dataset}: {'Success' if success else 'Failed/Skipped'}")
        print("="*70)

        return results


if __name__ == '__main__':
    # Example usage
    orchestrator = ParsingOrchestrator()
    orchestrator.parse_all()
