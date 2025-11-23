"""
Test script to generate debug files for pipeline assembly verification.

This runs the procedural orchestrator workflow to generate:
- debug_discovery.json (pre-assembly)
- debug_post_assembly.json (post-assembly)
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents.ui_orchestrator import UICodeOrchestrator


def test_debug_file_generation():
    """Run procedural workflow to generate debug files."""
    print("\n" + "="*80)
    print("DEBUG FILE GENERATION TEST")
    print("="*80)
    print("Purpose: Verify PipelineAssemblyTool is running and producing stages")
    print("="*80 + "\n")

    # Initialize orchestrator
    print("[1/3] Initializing orchestrator...")
    orchestrator = UICodeOrchestrator(use_agent_mode=False)

    print("\n[2/3] Running procedural workflow...")
    print("  This will generate debug_discovery.json and debug_post_assembly.json\n")

    # Define minimal requirements
    requirements = {
        "screen_type": "dashboard",
        "intent": "Show me an overview of all pipeline data",
        "components": ["data grid", "metrics cards"]
    }

    # Define minimal context
    context = {
        "data_sources": {},  # Will be auto-discovered
        "selected_sources": None  # Will auto-discover
    }

    try:
        # Run procedural workflow (will generate debug files)
        result = orchestrator.generate_ui_code(
            requirements=requirements,
            context=context
        )

        print("\n[3/3] Checking debug files...")

        debug_discovery = Path("debug_discovery.json")
        debug_post_assembly = Path("debug_post_assembly.json")

        if debug_discovery.exists():
            print(f"  [OK] {debug_discovery.resolve()} generated")
            print(f"       Size: {debug_discovery.stat().st_size:,} bytes")
        else:
            print(f"  [FAIL] {debug_discovery} not found!")

        if debug_post_assembly.exists():
            print(f"  [OK] {debug_post_assembly.resolve()} generated")
            print(f"       Size: {debug_post_assembly.stat().st_size:,} bytes")
        else:
            print(f"  [FAIL] {debug_post_assembly} not found!")

        print("\n" + "="*80)
        print("DEBUG FILES GENERATED")
        print("="*80)
        print("\nNext steps:")
        print("1. Review debug_discovery.json - Check if stages are empty")
        print("2. Review debug_post_assembly.json - Check if stages are populated")
        print("3. Compare the two files to verify pipeline assembly worked")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(test_debug_file_generation())
