import time
import requests

print("Waiting for API server...")
time.sleep(8)

try:
    r = requests.get('http://localhost:8000/api/pipelines', timeout=30)
    data = r.json()

    s = data['summary']

    if s['total_size'] != '0 B':
        print("\n" + "="*60)
        print("SUCCESS! Total size is now calculated correctly!")
        print("="*60)
    else:
        print("\nStill showing 0 B")

    print(f"\nSUMMARY:")
    print(f"  Total Size: {s['total_size']}")
    print(f"  Total Records: {s['total_records']:,}")
    print(f"  Total Pipelines: {s['total_pipelines']}")

    print(f"\nFRACFOCUS:")
    ff = [p for p in data['pipelines'] if p['id']=='fracfocus'][0]
    print(f"  Files: {ff['metrics']['file_count']}")
    print(f"  Size: {ff['metrics']['data_size']}")
    print(f"  Records: {ff['metrics']['record_count']:,}")

except Exception as e:
    print(f"Error: {e}")
