"""Kill all processes on port 8000"""
import subprocess
import time

# Get all PIDs on port 8000
result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
lines = result.stdout.split('\n')

pids = set()
for line in lines:
    if ':8000' in line and 'LISTENING' in line:
        parts = line.split()
        if parts:
            pid = parts[-1]
            if pid.isdigit():
                pids.add(pid)

print(f"Found {len(pids)} processes on port 8000: {pids}")

for pid in pids:
    try:
        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
        print(f"Killed PID {pid}")
    except Exception as e:
        print(f"Failed to kill PID {pid}: {e}")

time.sleep(2)

# Verify
result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
still_there = [line for line in result.stdout.split('\n') if ':8000' in line and 'LISTENING' in line]

if still_there:
    print(f"\n⚠️  WARNING: {len(still_there)} processes still on port 8000!")
else:
    print("\n✅ Port 8000 is now free!")
