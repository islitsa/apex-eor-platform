"""
Launch Dashboard with Dynamic Port Selection
Fixes port conflicts by automatically finding an available port
"""

import sys
import socket
import subprocess
from pathlib import Path

def find_free_port(start_port=7860, max_tries=50):
    """Find an available port"""
    for port in range(start_port, start_port + max_tries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', port))
            sock.close()
            return port
        except OSError:
            continue
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/launch_dashboard.py <dashboard_file.py>")
        sys.exit(1)

    dashboard_file = Path(sys.argv[1])

    if not dashboard_file.exists():
        print(f"ERROR: Dashboard file not found: {dashboard_file}")
        sys.exit(1)

    # Find available port
    port = find_free_port()
    if not port:
        print("ERROR: Could not find available port (tried 7860-7910)")
        sys.exit(1)

    print(f"Found available port: {port}")

    # Read dashboard code
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        code = f.read()

    # Replace port
    import re
    code = re.sub(r'server_port=\d+', f'server_port={port}', code)

    # Write back
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(code)

    print(f"\nLaunching dashboard on http://localhost:{port}")
    print("Opening browser...")
    print("Press Ctrl+C to stop\n")

    # Open browser automatically
    import webbrowser
    import threading
    import time

    def open_browser():
        """Open browser after dashboard starts"""
        time.sleep(3)  # Wait for dashboard to start
        webbrowser.open(f'http://localhost:{port}')
        print(f"Browser opened to http://localhost:{port}")

    # Start browser opener in background thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Launch dashboard (blocking)
    subprocess.run(['python', str(dashboard_file)])
