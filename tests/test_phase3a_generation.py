"""
Phase 3A Generation Test

Tests that React Developer generates code with data hooks.
"""

import sys
from pathlib import Path
import io

# Fix Windows console encoding for emoji
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.react_developer import ReactDeveloperAgent
from agents.ux_designer import DesignSpec

print("\n" + "="*80)
print("PHASE 3A CODE GENERATION TEST")
print("="*80)

print("\n[TEST] Creating React Developer instance...")
react_dev = ReactDeveloperAgent()

print("[TEST] Creating mock design spec...")
design_spec = DesignSpec(
    screen_type="dashboard",
    intent="Display fracfocus chemical data in a dashboard",
    components=[],
    interactions=[],
    patterns=["data-table", "loading-state"],
    styling={"framework": "tailwind", "theme": "light"},
    design_reasoning="Simple dashboard to display chemical data from fracfocus dataset"
)

print("[TEST] Creating mock data sources (discovered by UX Designer)...")
data_sources = {
    'fracfocus': {
        'row_count': 239061,
        'columns': ['DisclosureId', 'JobStartDate', 'JobEndDate', 'APINumber', 'StateName',
                    'CountyName', 'OperatorName', 'WellName', 'Latitude', 'Longitude'],
        'status': 'complete',
        'stages': ['downloads', 'extracted', 'parsed']
    }
}

print("\n[TEST] Generating React code with Phase 3A data fetching...")
print("-"*80)

try:
    # Phase 2 integration: Attach data sources to design_spec
    design_spec.data_sources = data_sources

    # Build with context containing user prompt
    generated_files = react_dev.build(
        design_spec=design_spec,
        context={'user_prompt': "Create a dashboard showing fracfocus chemical data"}
    )

    print(f"\n✅ Generated {len(generated_files)} files:")
    for filename in generated_files.keys():
        print(f"   - {filename}")

    # Check if dataHooks.tsx is included
    print("\n" + "="*80)
    print("PHASE 3A VERIFICATION")
    print("="*80)

    if 'dataHooks.tsx' in generated_files:
        print("\n✅ dataHooks.tsx is included in generated code")
        hooks_content = generated_files['dataHooks.tsx']
        print(f"   Size: {len(hooks_content)} characters")

        # Check for required hooks
        required_hooks = ['useDataSources', 'useDataSourceInfo', 'useDataSource', 'useDataQuery']
        for hook in required_hooks:
            if hook in hooks_content:
                print(f"   ✅ {hook}() hook present")
            else:
                print(f"   ❌ {hook}() hook MISSING")
    else:
        print("\n❌ dataHooks.tsx is NOT included in generated code")
        print("   Phase 3A integration FAILED")

    # Check if App.tsx uses data hooks
    print("\n" + "-"*80)
    print("Checking App.tsx for data fetching...")
    print("-"*80)

    if 'App.tsx' in generated_files:
        app_content = generated_files['App.tsx']

        # Check for imports
        if "from './dataHooks" in app_content or 'from "./dataHooks' in app_content:
            print("✅ App.tsx imports data hooks")
        else:
            print("❌ App.tsx does NOT import data hooks")

        # Check for hook usage
        if 'useDataSource(' in app_content:
            print("✅ App.tsx uses useDataSource() hook")
        else:
            print("⚠️  App.tsx does NOT use useDataSource() hook")

        # Check for loading state
        if 'loading' in app_content.lower():
            print("✅ App.tsx handles loading state")
        else:
            print("⚠️  App.tsx does NOT handle loading state")

        # Check for error handling
        if 'error' in app_content.lower():
            print("✅ App.tsx handles errors")
        else:
            print("⚠️  App.tsx does NOT handle errors")

        # Check for hardcoded data (BAD)
        if 'const data = [' in app_content:
            print("❌ App.tsx contains hardcoded data arrays (Phase 3A violation!)")
        else:
            print("✅ App.tsx does NOT contain hardcoded data arrays")

    print("\n" + "="*80)
    print("PHASE 3A TEST SUMMARY")
    print("="*80)

    if 'dataHooks.tsx' in generated_files:
        print("\n✅ PHASE 3A INTEGRATION WORKING")
        print("   - Data hooks template is included")
        print("   - Generated code should fetch real data at runtime")
        print("\nNext step: Run the generated dashboard with backend API")
    else:
        print("\n❌ PHASE 3A INTEGRATION FAILED")
        print("   - Data hooks template is missing")
        print("   - Generated code will use hardcoded data")

except Exception as e:
    print(f"\n❌ ERROR during code generation:")
    print(f"   {e}")
    import traceback
    traceback.print_exc()

print("\n")
