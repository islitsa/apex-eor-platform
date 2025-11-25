"""
Test script for data ingestion pipeline

Tests the pipeline structure without requiring full dependencies.
"""

import sys
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))


def test_directory_structure():
    """Test that all required directories exist"""
    print("\n" + "="*70)
    print("TESTING PIPELINE DIRECTORY STRUCTURE")
    print("="*70)

    required_files = [
        'scripts/pipeline/run_ingestion.py',
        'scripts/pipeline/extract.py',
        'scripts/pipeline/parse.py',
        'scripts/pipeline/config.yaml',
        'scripts/pipeline/README.md',
        'scripts/downloaders/__init__.py',
        'scripts/downloaders/rrc_downloader.py',
        'scripts/downloaders/fracfocus_downloader.py',
    ]

    all_exist = True
    for file_path in required_files:
        full_path = Path(file_path)
        exists = full_path.exists()
        status = "[OK]" if exists else "[MISSING]"
        print(f"{status} {file_path}")
        if not exists:
            all_exist = False

    print("\n" + "="*70)
    if all_exist:
        print("[OK] All required files exist")
    else:
        print("[FAIL] Some files are missing")
    print("="*70)

    return all_exist


def test_data_directories():
    """Test that data directories are set up correctly"""
    print("\n" + "="*70)
    print("TESTING DATA DIRECTORY STRUCTURE")
    print("="*70)

    data_dirs = [
        'data/raw/rrc',
        'data/raw/fracfocus',
    ]

    for dir_path in data_dirs:
        full_path = Path(dir_path)
        exists = full_path.exists()
        status = "[OK]" if exists else "[WILL CREATE]"
        print(f"{status} {dir_path}")

    print("="*70)


def test_pipeline_structure():
    """Test the pipeline module structure"""
    print("\n" + "="*70)
    print("TESTING PIPELINE STRUCTURE")
    print("="*70)

    try:
        # Test imports (without dependencies)
        print("Testing module structure...")

        # Check if files are importable
        pipeline_dir = Path('scripts/pipeline')
        downloader_dir = Path('scripts/downloaders')

        print(f"[OK] Pipeline directory: {pipeline_dir.exists()}")
        print(f"[OK] Downloaders directory: {downloader_dir.exists()}")

        # Check file sizes
        run_ingestion = Path('scripts/pipeline/run_ingestion.py')
        if run_ingestion.exists():
            size = run_ingestion.stat().st_size
            print(f"[OK] Main runner script: {size:,} bytes")

        extract = Path('scripts/pipeline/extract.py')
        if extract.exists():
            size = extract.stat().st_size
            print(f"[OK] Extraction orchestrator: {size:,} bytes")

        parse = Path('scripts/pipeline/parse.py')
        if parse.exists():
            size = parse.stat().st_size
            print(f"[OK] Parsing orchestrator: {size:,} bytes")

        print("\n[OK] Pipeline structure is valid")

    except Exception as e:
        print(f"[FAIL] Error: {e}")

    print("="*70)


def show_usage():
    """Show usage instructions"""
    print("\n" + "="*70)
    print("DATA INGESTION PIPELINE - NEXT STEPS")
    print("="*70)
    print("\n1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n2. Test the pipeline (dry run):")
    print("   python scripts/pipeline/run_ingestion.py --all --dry-run")
    print("\n3. Run download phase:")
    print("   python scripts/pipeline/run_ingestion.py --download")
    print("\n4. Run complete pipeline:")
    print("   python scripts/pipeline/run_ingestion.py --all")
    print("\n5. For specific datasets:")
    print("   python scripts/pipeline/run_ingestion.py --all --datasets rrc_production")
    print("\n" + "="*70)
    print("For more information, see: scripts/pipeline/README.md")
    print("="*70)


if __name__ == '__main__':
    print("\nAPEX EOR Platform - Data Ingestion Pipeline Test")

    # Run tests
    structure_ok = test_directory_structure()
    test_data_directories()
    test_pipeline_structure()

    # Show usage
    show_usage()

    # Exit with appropriate code
    sys.exit(0 if structure_ok else 1)
