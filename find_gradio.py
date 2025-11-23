"""Find running Gradio processes and their ports"""

import psutil
import re

print("Searching for Gradio processes...\n")

found = False

for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmdline = proc.info.get('cmdline')
        if cmdline:
            cmdline_str = ' '.join(str(arg) for arg in cmdline)

            # Look for python processes running gradio apps
            if 'python' in str(proc.info['name']).lower() and 'generated' in cmdline_str.lower():
                found = True
                print(f"Found Gradio process:")
                print(f"  PID: {proc.info['pid']}")
                print(f"  Command: {cmdline_str}")

                # Try to get network connections to find port
                try:
                    connections = proc.connections()
                    for conn in connections:
                        if conn.status == 'LISTEN':
                            print(f"  Listening on: {conn.laddr.ip}:{conn.laddr.port}")
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    print(f"  (Cannot access connection info)")
                print()

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

if not found:
    print("No Gradio processes found")
    print("\nHint: Click the 'Launch' button in Agent Studio (http://localhost:8502) to start Gradio")
