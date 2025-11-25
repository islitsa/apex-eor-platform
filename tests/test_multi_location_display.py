"""
Test multi-location display in orchestrator trace
"""

def test_multi_location_display():
    print("="*80)
    print("TESTING MULTI-LOCATION DISPLAY")
    print("="*80)
    print()

    from src.agents.ui_orchestrator import UICodeOrchestrator

    # Initialize orchestrator
    orch = UICodeOrchestrator(trace_collector=None)

    # Fetch data context (this will trigger the adapter and formatting)
    data_context = orch._fetch_data_context()

    if data_context.get('success'):
        print("SUCCESS: Data fetched from API")
        print()

        pipelines = data_context.get('pipelines', [])
        print(f"Total pipelines: {len(pipelines)}")
        print()

        # Check fracfocus specifically
        fracfocus = next((p for p in pipelines if p.get('id') == 'fracfocus'), None)
        if fracfocus:
            print("FracFocus pipeline structure:")
            print(f"  ID: {fracfocus.get('id')}")
            print(f"  Display Name: {fracfocus.get('display_name')}")

            files_info = fracfocus.get('files', {})
            if 'locations' in files_info:
                print(f"  Multi-location structure: YES")
                locations = files_info.get('locations', {})
                available_in = files_info.get('available_in', [])

                print(f"  Available in: {available_in}")
                print()

                for loc_name in ['raw', 'interim', 'processed']:
                    if loc_name in locations:
                        loc_data = locations[loc_name]
                        print(f"  [{loc_name}]")
                        print(f"    File count: {loc_data.get('file_count')}")
                        print(f"    Size: {loc_data.get('size')}")
                        print(f"    File types: {loc_data.get('file_types')}")
                        if 'row_count' in loc_data:
                            print(f"    Rows: {loc_data.get('row_count'):,}")
                        print()
            else:
                print(f"  Multi-location structure: NO")
                print(f"  Legacy structure detected")
        else:
            print("FracFocus pipeline NOT FOUND")

        print()
        print("-" * 80)
        print("CHECKING RRC:")
        rrc = next((p for p in pipelines if p.get('id') == 'rrc'), None)
        if rrc:
            files_info = rrc.get('files', {})
            if 'locations' in files_info:
                available_in = files_info.get('available_in', [])
                print(f"  RRC available in: {available_in}")
            else:
                print(f"  RRC using legacy structure")

    else:
        print(f"FAILED: {data_context.get('error')}")

    print()
    print("="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_multi_location_display()
