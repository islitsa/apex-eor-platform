"""Kill all zombie Streamlit processes"""
import subprocess
import sys

print("Killing all Streamlit processes...")
try:
    result = subprocess.run(
        ['taskkill', '/F', '/IM', 'streamlit.exe'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("[OK] All Streamlit processes killed")
    else:
        print("[OK] No Streamlit processes found")
except Exception as e:
    print(f"Error: {e}")

print("\nYou can now run:")
print("python scripts/pipeline/run_ingestion.py --generate-context --launch-ui collaborate")
