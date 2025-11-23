"""
FracFocus Chemical Disclosure Data Downloader

Downloads FracFocus CSV data from the public registry.

Data includes:
- FracFocusRegistry (chemical disclosure records)
- DisclosureList (well-level metadata)
- WaterSource (water source information)

Usage:
    downloader = FracFocusDownloader(base_dir='data/raw/fracfocus')
    downloader.download_all()
"""

import os
import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from tqdm import tqdm


class FracFocusDownloader:
    """Automated downloader for FracFocus chemical disclosure data"""

    # FracFocus Data URLs
    URLS = {
        'csv_data': 'https://fracfocus.org/data-download',
        'direct_csv': 'https://fracfocusdata.org/DigitalDownload/FracFocusCSV.zip',
        'api_bulk': 'https://fracfocusdata.org/api/v1/data'
    }

    def __init__(self, base_dir: str = 'data/raw/fracfocus'):
        """
        Initialize FracFocus downloader

        Args:
            base_dir: Base directory for FracFocus data storage
        """
        self.base_dir = Path(base_dir)
        self.downloads_dir = self.base_dir / 'downloads'
        self.downloads_dir.mkdir(parents=True, exist_ok=True)

    def _download_file(self, url: str, output_path: Path, description: str = "") -> bool:
        """
        Download a file with progress bar

        Args:
            url: URL to download from
            output_path: Path to save file
            description: Description for progress bar

        Returns:
            True if download successful, False otherwise
        """
        try:
            print(f"\nDownloading {description}...")
            print(f"URL: {url}")
            print(f"Output: {output_path}")

            # Set headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, stream=True, headers=headers, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(output_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=description) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            # Calculate checksum
            checksum = self._calculate_checksum(output_path)
            print(f"✓ Downloaded successfully (MD5: {checksum[:8]}...)")

            return True

        except requests.RequestException as e:
            print(f"✗ Download failed: {e}")
            if output_path.exists():
                output_path.unlink()
            return False
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            if output_path.exists():
                output_path.unlink()
            return False

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file"""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def _save_metadata(self, file_path: Path, url: str, checksum: str):
        """Save download metadata"""
        metadata = {
            'dataset': 'fracfocus',
            'download_date': datetime.now().isoformat(),
            'source_url': url,
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size,
            'md5_checksum': checksum,
            'status': 'downloaded',
            'license': 'Public Domain',
            'update_frequency': 'Quarterly'
        }

        metadata_file = self.base_dir / 'metadata.json'

        # Load existing metadata if it exists
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                existing_metadata = json.load(f)
        else:
            existing_metadata = {}

        # Update with new download info
        existing_metadata['last_download'] = metadata
        existing_metadata['processing_state'] = existing_metadata.get('processing_state', {})
        existing_metadata['processing_state']['download'] = 'complete'

        with open(metadata_file, 'w') as f:
            json.dump(existing_metadata, f, indent=2)

        print(f"✓ Metadata saved to {metadata_file}")

    def download_csv_bulk(self, force: bool = False) -> bool:
        """
        Download FracFocus CSV bulk data (FracFocusCSV.zip)

        Args:
            force: Force download even if file exists

        Returns:
            True if successful, False otherwise
        """
        output_file = self.downloads_dir / 'FracFocusCSV.zip'

        if output_file.exists() and not force:
            print(f"FracFocus CSV data already exists at {output_file}")
            print("Use force=True to re-download")
            return True

        success = self._download_file(
            self.URLS['direct_csv'],
            output_file,
            "FracFocus CSV Bulk Download"
        )

        if success:
            checksum = self._calculate_checksum(output_file)
            self._save_metadata(output_file, self.URLS['direct_csv'], checksum)

        return success

    def download_all(self, force: bool = False) -> Dict[str, bool]:
        """
        Download all FracFocus datasets

        Args:
            force: Force download even if files exist

        Returns:
            Dictionary with download status for each dataset
        """
        results = {
            'csv_bulk': self.download_csv_bulk(force)
        }

        print("\n" + "="*70)
        print("FRACFOCUS DOWNLOAD SUMMARY")
        print("="*70)
        for dataset, success in results.items():
            status = "✓" if success else "✗"
            print(f"{status} {dataset}: {'Success' if success else 'Failed'}")
        print("="*70)

        return results


if __name__ == '__main__':
    # Example usage
    downloader = FracFocusDownloader()
    downloader.download_all()
