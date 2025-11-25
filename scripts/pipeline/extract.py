"""
Extraction Orchestrator

Handles extraction of all downloaded data sources:
- ZIP files (single and nested)
- Compressed archives
- Direct file copies

Usage:
    orchestrator = ExtractionOrchestrator()
    orchestrator.extract_all()
"""

import os
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from tqdm import tqdm


class ExtractionOrchestrator:
    """Orchestrates extraction of all downloaded data"""

    def __init__(self, base_data_dir: str = 'data/raw'):
        """
        Initialize extraction orchestrator

        Args:
            base_data_dir: Base directory containing raw data
        """
        self.base_data_dir = Path(base_data_dir)
        self.rrc_dir = self.base_data_dir / 'rrc'
        self.fracfocus_dir = self.base_data_dir / 'fracfocus'

    def _extract_zip(self, zip_path: Path, extract_to: Path, description: str = "") -> bool:
        """
        Extract a ZIP file with progress tracking

        Args:
            zip_path: Path to ZIP file
            extract_to: Directory to extract to
            description: Description for progress bar

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\nExtracting {description}...")
            print(f"From: {zip_path}")
            print(f"To: {extract_to}")

            extract_to.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                members = zip_ref.namelist()
                print(f"Files to extract: {len(members)}")

                for member in tqdm(members, desc=description):
                    try:
                        zip_ref.extract(member, extract_to)
                    except Exception as e:
                        print(f"Warning: Failed to extract {member}: {e}")

            print(f"✓ Extraction complete")
            return True

        except zipfile.BadZipFile as e:
            print(f"✗ Invalid ZIP file: {e}")
            return False
        except Exception as e:
            print(f"✗ Extraction failed: {e}")
            return False

    def _extract_nested_zips(self, downloads_dir: Path, extract_to: Path, description: str = "") -> bool:
        """
        Extract nested ZIP files (for RRC completion packets)

        Args:
            downloads_dir: Directory containing ZIP files
            extract_to: Directory to extract to
            description: Description for progress

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\nExtracting nested ZIPs: {description}...")
            print(f"From: {downloads_dir}")
            print(f"To: {extract_to}")

            # Find all ZIP files
            zip_files = list(downloads_dir.glob('**/*.zip'))
            print(f"Found {len(zip_files)} ZIP files")

            if not zip_files:
                print("No ZIP files found to extract")
                return True

            extract_to.mkdir(parents=True, exist_ok=True)
            extracted_count = 0

            for zip_file in tqdm(zip_files, desc="Extracting nested ZIPs"):
                try:
                    # Create subdirectory based on ZIP name
                    subdir = extract_to / zip_file.stem
                    subdir.mkdir(parents=True, exist_ok=True)

                    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                        zip_ref.extractall(subdir)
                        extracted_count += 1

                except Exception as e:
                    print(f"Warning: Failed to extract {zip_file.name}: {e}")

            print(f"✓ Extracted {extracted_count}/{len(zip_files)} ZIP files")
            return True

        except Exception as e:
            print(f"✗ Nested extraction failed: {e}")
            return False

    def _update_metadata(self, dataset_path: Path, status: str, step: str):
        """Update metadata.json with extraction status"""
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

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def extract_rrc_production(self) -> bool:
        """Extract RRC production data (PDQ_DSV.zip)"""
        zip_file = self.rrc_dir / 'production' / 'downloads' / 'PDQ_DSV.zip'
        extract_to = self.rrc_dir / 'production' / 'extracted'

        if not zip_file.exists():
            print(f"Production ZIP not found: {zip_file}")
            return False

        success = self._extract_zip(
            zip_file,
            extract_to,
            "RRC Production Data (PDQ_DSV.zip)"
        )

        if success:
            self._update_metadata(self.rrc_dir / 'production', 'complete', 'extraction')

        return success

    def extract_rrc_permits(self) -> bool:
        """
        Extract RRC horizontal drilling permits

        Note: DAF318.txt is already in usable format, just copy to extracted/
        """
        source_file = self.rrc_dir / 'horizontal_drilling_permits' / 'downloads' / 'daf318.txt'
        extract_to = self.rrc_dir / 'horizontal_drilling_permits' / 'extracted'

        if not source_file.exists():
            print(f"Permits file not found: {source_file}")
            return False

        print(f"\nCopying permits file (already in text format)...")
        print(f"From: {source_file}")
        print(f"To: {extract_to}")

        extract_to.mkdir(parents=True, exist_ok=True)
        dest_file = extract_to / 'daf318.txt'

        try:
            shutil.copy2(source_file, dest_file)
            print(f"✓ File copied successfully")

            self._update_metadata(
                self.rrc_dir / 'horizontal_drilling_permits',
                'complete',
                'extraction'
            )
            return True

        except Exception as e:
            print(f"✗ Copy failed: {e}")
            return False

    def extract_rrc_completions(self) -> bool:
        """Extract RRC completion packets (nested ZIPs)"""
        downloads_dir = self.rrc_dir / 'completions_data' / 'downloads'
        extract_to = self.rrc_dir / 'completions_data' / 'extracted'

        if not downloads_dir.exists():
            print(f"Completions directory not found: {downloads_dir}")
            return False

        success = self._extract_nested_zips(
            downloads_dir,
            extract_to,
            "RRC Completion Packets"
        )

        if success:
            self._update_metadata(
                self.rrc_dir / 'completions_data',
                'complete',
                'extraction'
            )

        return success

    def extract_fracfocus(self) -> bool:
        """Extract FracFocus CSV data"""
        zip_file = self.fracfocus_dir / 'downloads' / 'FracFocusCSV.zip'
        extract_to = self.fracfocus_dir / 'extracted'

        if not zip_file.exists():
            print(f"FracFocus ZIP not found: {zip_file}")
            return False

        success = self._extract_zip(
            zip_file,
            extract_to,
            "FracFocus CSV Data"
        )

        if success:
            self._update_metadata(self.fracfocus_dir, 'complete', 'extraction')

        return success

    def extract_all(self) -> Dict[str, bool]:
        """
        Extract all downloaded datasets

        Returns:
            Dictionary with extraction status for each dataset
        """
        print("\n" + "="*70)
        print("EXTRACTION ORCHESTRATOR")
        print("="*70)

        results = {
            'rrc_production': self.extract_rrc_production(),
            'rrc_permits': self.extract_rrc_permits(),
            'rrc_completions': self.extract_rrc_completions(),
            'fracfocus': self.extract_fracfocus()
        }

        print("\n" + "="*70)
        print("EXTRACTION SUMMARY")
        print("="*70)
        for dataset, success in results.items():
            status = "✓" if success else "✗"
            print(f"{status} {dataset}: {'Success' if success else 'Failed'}")
        print("="*70)

        return results


if __name__ == '__main__':
    # Example usage
    orchestrator = ExtractionOrchestrator()
    orchestrator.extract_all()
