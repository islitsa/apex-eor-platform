"""
USGS Produced Waters Database Downloader

Downloads and processes USGS Produced Waters Database v2.3
Contains ~114,000 produced water samples with chemistry data.

Source: U.S. Geological Survey
URL: https://www.sciencebase.gov/catalog/item/5d3c2d0de4b01d82ce8d7738
"""

import requests
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class USGSProducedWaterDownloader:
    """
    Download and process USGS Produced Waters Database v2.3

    Features:
    - Downloads ~114k produced water samples
    - Parses chemistry data for EOR applications
    - Creates Texas-specific subsets
    - Generates basin summaries
    """

    def __init__(self, base_path=None):
        if base_path is None:
            base_path = PROJECT_ROOT / "data" / "raw" / "usgs" / "produced_water"

        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # USGS ScienceBase URLs - try alternative download link
        # Main catalog page: https://www.sciencebase.gov/catalog/item/5d3c2d0de4b01d82ce8d7738
        self.catalog_id = "5d3c2d0de4b01d82ce8d7738"
        self.csv_url = f"https://www.sciencebase.gov/catalog/file/get/{self.catalog_id}"

    def download(self):
        """
        Download the produced water database

        Returns:
            Path to downloaded CSV file
        """

        # Create folders
        downloads_path = self.base_path / "downloads"
        downloads_path.mkdir(exist_ok=True)

        csv_file = downloads_path / "PWDB_v2.3.csv"

        # Skip if already downloaded
        if csv_file.exists():
            print(f"[OK] Already downloaded: {csv_file}")
            print(f"  Size: {csv_file.stat().st_size / (1024*1024):.2f} MB")
            return csv_file

        print("\n" + "="*70)
        print("DOWNLOADING USGS PRODUCED WATERS DATABASE v2.3")
        print("="*70)
        print("Source: U.S. Geological Survey")
        print("Records: ~114,000 produced water samples")
        print("="*70 + "\n")

        try:
            response = requests.get(self.csv_url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(csv_file, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}%", end='')

            print(f"\n\n[OK] Downloaded successfully")
            print(f"  File: {csv_file}")
            print(f"  Size: {csv_file.stat().st_size / (1024*1024):.2f} MB")

            # Create metadata
            self.create_metadata(csv_file)

            return csv_file

        except Exception as e:
            print(f"\n[ERROR] Error downloading: {e}")
            if csv_file.exists():
                csv_file.unlink()
            raise

    def extract_and_parse(self, csv_file):
        """
        Parse the produced water data into EOR-relevant subsets

        Args:
            csv_file: Path to downloaded CSV

        Returns:
            Path to parsed data folder
        """

        print("\n" + "="*70)
        print("PARSING PRODUCED WATER CHEMISTRY DATA")
        print("="*70 + "\n")

        # Create parsed folder
        parsed_path = self.base_path / "parsed"
        parsed_path.mkdir(exist_ok=True)

        # Read the CSV
        print("Loading CSV...")
        df = pd.read_csv(csv_file, low_memory=False)

        print(f"[OK] Loaded {len(df):,} records")
        print(f"  Columns: {len(df.columns)}")
        print()

        # 1. EOR chemistry subset
        print("Creating EOR chemistry subset...")
        eor_cols = [
            'PWDB_ID', 'State', 'County', 'Basin', 'Formation',
            'TDS_Calculated_mg_L', 'pH', 'Temperature_C',
            'Calcium_mg_L', 'Magnesium_mg_L', 'Sodium_mg_L',
            'Chloride_mg_L', 'Sulfate_mg_L', 'Bicarbonate_mg_L'
        ]

        # Only include columns that exist
        eor_cols = [col for col in eor_cols if col in df.columns]

        eor_chemistry = df[eor_cols].dropna(subset=['TDS_Calculated_mg_L'] if 'TDS_Calculated_mg_L' in df.columns else [])
        eor_chemistry.to_parquet(parsed_path / "eor_chemistry.parquet", index=False)
        print(f"  [OK] EOR chemistry: {len(eor_chemistry):,} samples")

        # 2. Texas data only (for RRC integration)
        print("Extracting Texas samples...")
        if 'State' in df.columns:
            texas_data = df[df['State'] == 'Texas'].copy()
            if len(texas_data) > 0:
                texas_data.to_parquet(parsed_path / "texas_produced_water.parquet", index=False)
                print(f"  [OK] Texas: {len(texas_data):,} samples")

        # 3. High TDS samples (important for chemical EOR)
        print("Filtering high TDS samples...")
        if 'TDS_Calculated_mg_L' in df.columns:
            high_tds = df[df['TDS_Calculated_mg_L'] > 100000].copy()
            if len(high_tds) > 0:
                high_tds.to_parquet(parsed_path / "high_tds_samples.parquet", index=False)
                print(f"  [OK] High TDS (>100k ppm): {len(high_tds):,} samples")

        # 4. Basin summary statistics
        print("Generating basin summaries...")
        if 'Basin' in df.columns and 'TDS_Calculated_mg_L' in df.columns:
            basin_summary = df.groupby('Basin').agg({
                'TDS_Calculated_mg_L': ['mean', 'min', 'max', 'count'],
                'pH': 'mean' if 'pH' in df.columns else lambda x: None,
                'Temperature_C': 'mean' if 'Temperature_C' in df.columns else lambda x: None
            }).round(2)

            basin_summary.to_csv(parsed_path / "basin_summary.csv")
            print(f"  [OK] Basin summaries: {len(basin_summary)} basins")

        # 5. Key formations for EOR
        print("Extracting key formation data...")
        if 'Formation' in df.columns:
            key_formations = ['Wolfcamp', 'Spraberry', 'Bone Spring', 'Eagle Ford',
                             'Bakken', 'Marcellus', 'Permian']

            formation_data = df[df['Formation'].str.contains(
                '|'.join(key_formations), case=False, na=False
            )]

            if len(formation_data) > 0:
                formation_data.to_parquet(parsed_path / "key_formations_water.parquet", index=False)
                print(f"  [OK] Key formations: {len(formation_data):,} samples")

        print(f"\n[OK] Parsing complete")
        print(f"  Output: {parsed_path}")

        # Update metadata with parsing results
        self.update_metadata_with_parsing(parsed_path, df)

        return parsed_path

    def create_metadata(self, csv_file):
        """Create initial metadata.json"""

        metadata = {
            "dataset": "usgs_produced_water_chemistry",
            "version": "v2.3",
            "source": {
                "provider": "U.S. Geological Survey",
                "url": "https://www.sciencebase.gov/catalog/item/5d3c2d0de4b01d82ce8d7738",
                "license": "Public Domain",
                "citation": "Blondes, M.S., et al., 2019, U.S. Geological Survey National Produced Waters Geochemical Database v2.3"
            },
            "description": "Geochemical data from ~114,000 produced water samples",
            "download_timestamp": datetime.now().isoformat(),
            "processing_state": {
                "download": "complete",
                "extraction": "not_started",
                "parsing": "not_started"
            },
            "files": {
                "downloads": {
                    "original": "PWDB_v2.3.csv",
                    "size_mb": round(csv_file.stat().st_size / (1024*1024), 2)
                }
            },
            "relevance_to_eor": {
                "use_cases": [
                    "Chemical compatibility analysis",
                    "Scale prediction",
                    "Clay swelling assessment",
                    "Surfactant design",
                    "Water treatment requirements"
                ],
                "key_parameters": [
                    "TDS (Total Dissolved Solids)",
                    "Ionic composition",
                    "pH",
                    "Temperature",
                    "Hardness (Ca/Mg)"
                ]
            }
        }

        metadata_file = self.base_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"[OK] Metadata created: {metadata_file}")

    def update_metadata_with_parsing(self, parsed_path, df):
        """Update metadata with parsing results"""

        metadata_file = self.base_path / "metadata.json"

        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        # Calculate total size of parsed files
        total_size = sum(
            f.stat().st_size
            for f in parsed_path.glob("*.parquet")
        )

        metadata["processing_state"]["parsing"] = "complete"
        metadata["processing_state"]["parsing_date"] = datetime.now().isoformat()

        metadata["parsed"] = {
            "total_records": len(df),
            "total_columns": len(df.columns),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024*1024), 2),
            "output_files": len(list(parsed_path.glob("*.parquet")))
        }

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"[OK] Metadata updated with parsing results")


def main():
    """Download and parse USGS Produced Waters database"""

    downloader = USGSProducedWaterDownloader()

    # Download
    csv_file = downloader.download()

    # Parse
    parsed_path = downloader.extract_and_parse(csv_file)

    print("\n" + "="*70)
    print("USGS PRODUCED WATERS - DOWNLOAD COMPLETE")
    print("="*70)
    print(f"Location: {downloader.base_path}")
    print(f"Parsed data: {parsed_path}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
