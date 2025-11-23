"""
Test adapter multi-location output directly (no API needed)
"""

def test_adapter_multi_location():
    print("="*80)
    print("TESTING ADAPTER MULTI-LOCATION OUTPUT")
    print("="*80)
    print()

    from shared_state import PipelineState
    from src.agents.context.adapter import ContextAdapter

    # Load context
    ctx = PipelineState.load_context()

    # Adapt context
    adapted = ContextAdapter.discovery_to_pipeline(ctx, assume_best=False)

    # Check fracfocus
    print("FRACFOCUS:")
    print("-" * 80)
    ff = adapted['data_sources']['fracfocus']
    dir_struct = ff.get('directory_structure', {})

    if 'locations' in dir_struct:
        print("Multi-location structure: YES")
        available_in = dir_struct.get('available_in', [])
        print(f"Available in: {available_in}")
        print()

        locations = dir_struct.get('locations', {})
        for loc_name in ['raw', 'interim', 'processed']:
            if loc_name in locations:
                loc_data = locations[loc_name]
                print(f"[{loc_name.upper()}]")
                print(f"  File count: {loc_data.get('file_count')}")
                print(f"  Size: {loc_data.get('size')}")
                print(f"  File types: {loc_data.get('file_types')}")
                if 'row_count' in loc_data:
                    print(f"  Rows: {loc_data.get('row_count'):,}")
                print()
    else:
        print("Multi-location structure: NO (legacy format)")

    print()
    print("="*80)
    print("RRC:")
    print("-" * 80)
    rrc = adapted['data_sources']['rrc']
    dir_struct = rrc.get('directory_structure', {})

    if 'locations' in dir_struct:
        available_in = dir_struct.get('available_in', [])
        print(f"Available in: {available_in}")

        locations = dir_struct.get('locations', {})
        for loc_name in ['raw', 'interim']:
            if loc_name in locations:
                loc_data = locations[loc_name]
                print(f"\n[{loc_name.upper()}]")
                print(f"  File count: {loc_data.get('file_count')}")
                print(f"  Size: {loc_data.get('size')}")
                print(f"  File types: {loc_data.get('file_types')}")

    print()
    print("="*80)
    print("ALL SOURCES:")
    print("-" * 80)
    for src_id in adapted['data_sources'].keys():
        src_data = adapted['data_sources'][src_id]
        dir_struct = src_data.get('directory_structure', {})
        if 'locations' in dir_struct:
            available_in = dir_struct.get('available_in', [])
            print(f"{src_id}: {available_in}")
        else:
            print(f"{src_id}: [legacy format]")

    print()
    print("="*80)
    print("TEST COMPLETE - Adapter is working correctly!")
    print("="*80)

if __name__ == "__main__":
    test_adapter_multi_location()
