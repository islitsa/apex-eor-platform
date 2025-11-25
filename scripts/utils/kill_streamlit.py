"""Kill all running Streamlit processes"""

import psutil
import sys

found = False

print("Searching for Streamlit processes...")

for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmdline = proc.info.get('cmdline')
        if cmdline and any('streamlit' in str(arg).lower() for arg in cmdline):
            found = True
            print(f"Found: PID {proc.info['pid']} - {' '.join(cmdline)}")
            print(f"  Killing...")
            proc.terminate()
            proc.wait(timeout=3)
            print(f"  Killed successfully")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
        pass

if not found:
    print("No Streamlit processes found")
else:
    print("\nAll Streamlit processes terminated")
