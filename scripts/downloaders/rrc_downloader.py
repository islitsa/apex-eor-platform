"""
Texas Railroad Commission (RRC) Data Downloader

Downloads three primary RRC datasets:
1. Production Data (PDQ_DSV.zip) - ~3.4GB
2. Horizontal Drilling Permits (DAF318.txt) - ~58MB
3. Completion Packets (nested ZIPs) - ~1.1GB

Usage:
    downloader = RRCDownloader(base_dir='data/raw/rrc')
    downloader.download_all()
    # Or download specific datasets:
    downloader.download_production()
    downloader.download_permits()
    downloader.download_completions()
"""

import os
import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from tqdm import tqdm


class RRCDownloader:
    """Automated downloader for Texas RRC data"""

    # RRC Data URLs
    URLS = {
        'production': 'https://www.rrc.texas.gov/media/vkijhgem/pdq_dsv.zip',
        'permits': 'https://www.rrc.texas.gov/media/k0jdyqrb/daf318.txt',
        'completions_base': 'https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/completion-data-packets/'
    }

    def __init__(self, base_dir: str = 'data/raw/rrc'):
        """
        Initialize RRC downloader

        Args:
            base_dir: Base directory for RRC data storage
        """
        self.base_dir = Path(base_dir)
        self.production_dir = self.base_dir / 'production' / 'downloads'
        self.permits_dir = self.base_dir / 'horizontal_drilling_permits' / 'downloads'
        self.completions_dir = self.base_dir / 'completions_data' / 'downloads'

        # Create directories
        for dir_path in [self.production_dir, self.permits_dir, self.completions_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

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

            response = requests.get(url, stream=True, timeout=30)
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

    def _save_metadata(self, dataset_type: str, file_path: Path, url: str, checksum: str):
        """Save download metadata"""
        metadata_dir = self.base_dir / 'metadata' / 'provenance'
        metadata_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            'dataset': dataset_type,
            'download_date': datetime.now().isoformat(),
            'source_url': url,
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size,
            'md5_checksum': checksum,
            'status': 'downloaded'
        }

        metadata_file = metadata_dir / f'{dataset_type}_download_{datetime.now().strftime("%Y%m%d")}.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Metadata saved to {metadata_file}")

    def download_production(self, force: bool = False) -> bool:
        """
        Download RRC production data (PDQ_DSV.zip)

        Args:
            force: Force download even if file exists

        Returns:
            True if successful, False otherwise
        """
        output_file = self.production_dir / 'PDQ_DSV.zip'

        if output_file.exists() and not force:
            print(f"Production data already exists at {output_file}")
            print("Use force=True to re-download")
            return True

        success = self._download_file(
            self.URLS['production'],
            output_file,
            "RRC Production Data (PDQ_DSV.zip)"
        )

        if success:
            checksum = self._calculate_checksum(output_file)
            self._save_metadata('production', output_file, self.URLS['production'], checksum)

        return success

    def download_permits(self, force: bool = False) -> bool:
        """
        Download horizontal drilling permits (DAF318.txt)

        Args:
            force: Force download even if file exists

        Returns:
            True if successful, False otherwise
        """
        output_file = self.permits_dir / 'daf318.txt'

        if output_file.exists() and not force:
            print(f"Permits data already exists at {output_file}")
            print("Use force=True to re-download")
            return True

        success = self._download_file(
            self.URLS['permits'],
            output_file,
            "RRC Horizontal Drilling Permits (DAF318.txt)"
        )

        if success:
            checksum = self._calculate_checksum(output_file)
            self._save_metadata('horizontal_permits', output_file, self.URLS['permits'], checksum)

        return success

    def download_completions(self, force: bool = False) -> bool:
        """
        Download completion packets

        Note: This requires web scraping the RRC completions page
        to get the list of available ZIP files. Currently returns
        a message to download manually.

        Args:
            force: Force download even if files exist

        Returns:
            True if successful, False otherwise
        """
        print("\n" + "="*70)
        print("COMPLETION PACKETS DOWNLOAD")
        print("="*70)
        print("\nCompletion packets are distributed as nested ZIP files by date/district.")
        print("They require scraping the RRC website to discover available files.")
        print("\nManual download instructions:")
        print(f"1. Visit: {self.URLS['completions_base']}")
        print("2. Download completion packet ZIP files")
        print(f"3. Save to: {self.completions_dir}")
        print("\nFor automated download, we would need to:")
        print("  - Use Selenium to navigate the page")
        print("  - Parse the available date ranges and districts")
        print("  - Download each ZIP file individually")
        print("\nThis functionality can be added if needed.")
        print("="*70)

        return False

    def download_all(self, force: bool = False) -> Dict[str, bool]:
        """
        Download all RRC datasets

        Args:
            force: Force download even if files exist

        Returns:
            Dictionary with download status for each dataset
        """
        results = {
            'production': self.download_production(force),
            'permits': self.download_permits(force),
            'completions': self.download_completions(force)
        }

        print("\n" + "="*70)
        print("DOWNLOAD SUMMARY")
        print("="*70)
        for dataset, success in results.items():
            status = "✓" if success else "✗"
            print(f"{status} {dataset}: {'Success' if success else 'Failed/Manual'}")
        print("="*70)

        return results


if __name__ == '__main__':
    # Example usage
    downloader = RRCDownloader()
    downloader.download_all()
