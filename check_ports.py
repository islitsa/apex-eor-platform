"""Check which ports are listening for HTTP traffic"""

import psutil

print("Ports in LISTEN state:\n")

# Get all listening connections
connections = psutil.net_connections(kind='inet')

gradio_ports = []

for conn in connections:
    if conn.status == 'LISTEN' and conn.laddr.port >= 7860 and conn.laddr.port <= 7870:
        try:
            proc = psutil.Process(conn.pid) if conn.pid else None
            proc_name = proc.name() if proc else "unknown"
            cmdline = ' '.join(proc.cmdline()) if proc else ""

            if 'generated_ui' in cmdline:
                print(f"Port {conn.laddr.port} - Gradio (PID {conn.pid})")
                gradio_ports.append(conn.laddr.port)
            else:
                print(f"Port {conn.laddr.port} - {proc_name} (PID {conn.pid})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            print(f"Port {conn.laddr.port} - (unknown process)")

if gradio_ports:
    print(f"\nGradio is running on: http://localhost:{gradio_ports[0]}")
    if len(gradio_ports) > 1:
        print(f"  (Note: Multiple instances found on ports {gradio_ports})")
else:
    print("\nNo Gradio processes found listening on ports 7860-7870")
