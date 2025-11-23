"""Kill all processes listening on port 8000"""
import subprocess
import re

# Get all processes on port 8000
result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
lines = result.stdout.split('\n')

pids = set()
for line in lines:
    if ':8000' in line and 'LISTENING' in line:
        # Extract PID from end of line
        parts = line.split()
        if parts:
            pid = parts[-1]
            if pid.isdigit():
                pids.add(pid)

print(f"Found {len(pids)} processes on port 8000")
for pid in pids:
    print(f"Killing PID {pid}...")
    subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)

print("Done!")
