"""Diagnose what's spawning processes on port 8000"""
import psutil
import time
import subprocess

def diagnose_port_8000():
    print("=== PORT 8000 DIAGNOSTIC ===\n")

    # 1. Find what's on port 8000
    print("1. Current processes on port 8000:")
    found_any = False
    for conn in psutil.net_connections():
        if hasattr(conn.laddr, 'port') and conn.laddr.port == 8000:
            found_any = True
            try:
                proc = psutil.Process(conn.pid)
                print(f"   PID {conn.pid}: {proc.name()}")
                print(f"   Started: {time.ctime(proc.create_time())}")
                cmdline = ' '.join(proc.cmdline())
                print(f"   Command: {cmdline[:100]}")  # First 100 chars

                # Get parent
                try:
                    parent = psutil.Process(proc.ppid())
                    print(f"   Parent PID {proc.ppid()}: {parent.name()}")
                    parent_cmd = ' '.join(parent.cmdline())
                    print(f"   Parent Command: {parent_cmd[:100]}")
                except:
                    print(f"   Parent: <unknown>")
                print()
            except Exception as e:
                print(f"   Error reading process: {e}\n")

    if not found_any:
        print("   ✅ Port 8000 is FREE!\n")
        return

    # 2. Kill all python processes
    print("\n2. Killing all Python processes on port 8000...")
    for conn in psutil.net_connections():
        if hasattr(conn.laddr, 'port') and conn.laddr.port == 8000:
            try:
                proc = psutil.Process(conn.pid)
                print(f"   Killing PID {conn.pid} ({proc.name()})...")
                proc.kill()
            except Exception as e:
                print(f"   Failed to kill PID {conn.pid}: {e}")

    time.sleep(3)

    # 3. Check if it respawned
    print("\n3. After killing - checking for respawn:")
    respawned = False
    for conn in psutil.net_connections():
        if hasattr(conn.laddr, 'port') and conn.laddr.port == 8000:
            respawned = True
            try:
                proc = psutil.Process(conn.pid)
                parent = psutil.Process(proc.ppid())
                print(f"   ⚠️ PORT 8000 RESPAWNED! PID: {conn.pid}")
                print(f"   Process: {proc.name()}")
                print(f"   Parent process: {parent.name()} (PID: {parent.pid})")
                parent_cmd = ' '.join(parent.cmdline())
                print(f"   Parent command: {parent_cmd}")
            except Exception as e:
                print(f"   Error reading respawned process: {e}")

    if not respawned:
        print("   ✅ Port 8000 is now FREE!")
    else:
        print("\n   🚨 PROBLEM: Something is auto-restarting the server!")
        print("   You need to kill the PARENT process to stop the respawning.")

if __name__ == "__main__":
    diagnose_port_8000()
