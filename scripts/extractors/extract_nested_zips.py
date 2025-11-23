import zipfile
import os
from pathlib import Path
import io

def process_nested_zips(main_zip_path, extract_to='extracted_files'):
    """
    Process a zip file containing other zip files.
    
    Args:
        main_zip_path: Path to the main zip file
        extract_to: Directory where files should be extracted
    """
    extract_path = Path(extract_to)
    extract_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Processing: {main_zip_path.name}")
    
    with zipfile.ZipFile(main_zip_path, 'r') as main_zip:
        zip_files = [f for f in main_zip.namelist() if f.endswith('.zip')]
        
        print(f"  Found {len(zip_files)} nested zip files")
        
        for zip_name in zip_files:
            # Read the nested zip file into memory
            nested_zip_data = main_zip.read(zip_name)
            
            # Create a subdirectory for this nested zip
            zip_base_name = Path(zip_name).stem
            nested_extract_path = extract_path / zip_base_name
            nested_extract_path.mkdir(parents=True, exist_ok=True)
            
            # Open and extract the nested zip
            with zipfile.ZipFile(io.BytesIO(nested_zip_data), 'r') as nested_zip:
                file_list = nested_zip.namelist()
                
                # Extract all files
                nested_zip.extractall(nested_extract_path)
                print(f"    {zip_name}: {len(file_list)} files -> {nested_extract_path}")
        
        print()
    
    return extract_path

def list_nested_zip_contents(main_zip_path):
    """
    List contents of nested zips without extracting.
    """
    print(f"\n{main_zip_path.name}:")
    
    with zipfile.ZipFile(main_zip_path, 'r') as main_zip:
        zip_files = [f for f in main_zip.namelist() if f.endswith('.zip')]
        
        print(f"  Contains {len(zip_files)} nested zip files")
        
        total_files = 0
        for zip_name in zip_files:
            nested_zip_data = main_zip.read(zip_name)
            
            with zipfile.ZipFile(io.BytesIO(nested_zip_data), 'r') as nested_zip:
                file_count = len(nested_zip.namelist())
                total_files += file_count
                print(f"    {zip_name}: {file_count} files")
        
        print(f"  Total files across all nested zips: {total_files}")

def process_all_zips_in_downloads(downloads_dir, extract_to):
    """
    Process all zip files in the downloads directory.
    
    Args:
        downloads_dir: Path to downloads folder
        extract_to: Path to extraction folder
    """
    downloads_path = Path(downloads_dir)
    extract_path = Path(extract_to)
    
    # Find all zip files
    zip_files = list(downloads_path.glob("*.zip"))
    
    if not zip_files:
        print(f"No zip files found in {downloads_path}")
        return
    
    print(f"Found {len(zip_files)} zip file(s) in downloads folder:\n")
    
    for zip_file in sorted(zip_files):
        process_nested_zips(zip_file, extract_to=extract_path)
    
    print(f"✓ All extractions complete! Files saved to: {extract_path}")

def list_all_zips_in_downloads(downloads_dir):
    """
    List contents of all zip files in downloads without extracting.
    """
    downloads_path = Path(downloads_dir)
    zip_files = list(downloads_path.glob("*.zip"))
    
    if not zip_files:
        print(f"No zip files found in {downloads_path}")
        return
    
    print(f"Found {len(zip_files)} zip file(s) in downloads folder:")
    
    for zip_file in sorted(zip_files):
        list_nested_zip_contents(zip_file)

def search_files_in_all_zips(downloads_dir, file_extension=None, search_term=None):
    """
    Search for specific files across all zip files in downloads.
    
    Args:
        downloads_dir: Path to downloads folder
        file_extension: File extension to search for (e.g., '.csv', '.xlsx')
        search_term: Text to search for in filenames
    """
    downloads_path = Path(downloads_dir)
    zip_files = list(downloads_path.glob("*.zip"))
    
    all_results = []
    
    for main_zip_path in zip_files:
        with zipfile.ZipFile(main_zip_path, 'r') as main_zip:
            nested_zips = [f for f in main_zip.namelist() if f.endswith('.zip')]
            
            for zip_name in nested_zips:
                nested_zip_data = main_zip.read(zip_name)
                
                with zipfile.ZipFile(io.BytesIO(nested_zip_data), 'r') as nested_zip:
                    for file_name in nested_zip.namelist():
                        match = True
                        
                        if file_extension and not file_name.endswith(file_extension):
                            match = False
                        
                        if search_term and search_term.lower() not in file_name.lower():
                            match = False
                        
                        if match:
                            all_results.append({
                                'main_zip': main_zip_path.name,
                                'container': zip_name,
                                'file': file_name,
                                'size': nested_zip.getinfo(file_name).file_size
                            })
    
    return all_results

# Main workflow for your project structure
if __name__ == "__main__":
    # Define paths based on your project structure
    project_root = Path(__file__).parent.parent
    downloads_dir = project_root / "data" / "raw" / "rrc" / "downloads"
    extract_dir = project_root / "data" / "raw" / "rrc" / "extracted"
    
    # Ensure directories exist
    downloads_dir.mkdir(parents=True, exist_ok=True)
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("RRC ZIP PROCESSOR")
    print("=" * 60)
    
    # Option 1: List all contents (quick overview)
    print("\n=== LISTING ALL ZIP CONTENTS ===")
    list_all_zips_in_downloads(downloads_dir)
    
    # Option 2: Extract all zip files
    print("\n" + "=" * 60)
    print("=== EXTRACTING ALL ZIP FILES ===")
    print("=" * 60 + "\n")
    process_all_zips_in_downloads(downloads_dir, extract_dir)
    
    # Option 3: Search for specific file types (example)
    print("\n" + "=" * 60)
    print("=== SEARCHING FOR CSV FILES ===")
    print("=" * 60 + "\n")
    csv_files = search_files_in_all_zips(downloads_dir, file_extension='.csv')
    if csv_files:
        print(f"Found {len(csv_files)} CSV files:")
        for item in csv_files[:10]:
            print(f"  {item['main_zip']} > {item['container']} > {item['file']}")
        if len(csv_files) > 10:
            print(f"  ... and {len(csv_files) - 10} more")
    else:
        print("No CSV files found.")