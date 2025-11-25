"""
Quick verification script for DataFilterTool

Run this to verify the filter tool works correctly without starting Agent Studio.
"""

from src.agents.tools.filter_tool import DataFilterTool


def test_filter_by_prompt():
    """Test prompt-based source detection"""
    print("=" * 80)
    print("TEST 1: filter_by_prompt")
    print("=" * 80)

    tool = DataFilterTool()

    # Test 1: Basic detection
    intent = "generate dashboard of production data from rrc"
    all_sources = ["fracfocus", "rrc", "attribution", "completions", "production", "treatments"]

    print(f"Intent: '{intent}'")
    print(f"All sources: {all_sources}")

    result = tool.filter_by_prompt(intent, all_sources)
    print(f"Detected sources: {result}")

    expected = ["rrc", "production"]
    if set(result) == set(expected):
        print("[PASS] PASS: Correctly detected 'rrc' and 'production'")
    else:
        print(f"[FAIL] FAIL: Expected {expected}, got {result}")

    print()

    # Test 2: Single source
    intent2 = "show rrc data"
    result2 = tool.filter_by_prompt(intent2, all_sources)
    print(f"Intent: '{intent2}'")
    print(f"Detected sources: {result2}")

    if result2 == ["rrc"]:
        print("[PASS] PASS: Correctly detected single source 'rrc'")
    else:
        print(f"[FAIL] FAIL: Expected ['rrc'], got {result2}")

    print()

    # Test 3: No specific sources
    intent3 = "create a dashboard"
    result3 = tool.filter_by_prompt(intent3, all_sources)
    print(f"Intent: '{intent3}'")
    print(f"Detected sources: {result3}")

    if result3 is None:
        print("[PASS] PASS: Correctly returned None (no specific sources)")
    else:
        print(f"[FAIL] FAIL: Expected None, got {result3}")

    print()


def test_filter_pipelines():
    """Test pipeline filtering"""
    print("=" * 80)
    print("TEST 2: filter_pipelines")
    print("=" * 80)

    tool = DataFilterTool()

    pipelines = [
        {"id": "fracfocus", "metrics": {"file_count": 39}},
        {"id": "rrc", "metrics": {"file_count": 25451}},
        {"id": "attribution", "metrics": {"file_count": 15}},
        {"id": "completions", "metrics": {"file_count": 20}},
        {"id": "production", "metrics": {"file_count": 5}},
        {"id": "treatments", "metrics": {"file_count": 10}},
    ]

    selected = ["rrc", "production"]

    print(f"Total pipelines: {len(pipelines)}")
    print(f"Selected sources: {selected}")

    filtered = tool.filter_pipelines(pipelines, selected)
    filtered_ids = [p["id"] for p in filtered]

    print(f"Filtered pipelines: {len(filtered)}")
    print(f"Filtered IDs: {filtered_ids}")

    if set(filtered_ids) == {"rrc", "production"}:
        print("[PASS] PASS: Correctly filtered to 'rrc' and 'production'")
    else:
        print(f"[FAIL] FAIL: Expected ['rrc', 'production'], got {filtered_ids}")

    print()


def test_filter_design_spec():
    """Test design spec filtering"""
    print("=" * 80)
    print("TEST 3: filter_design_spec")
    print("=" * 80)

    tool = DataFilterTool()

    class DummySpec:
        def __init__(self):
            self.data_sources = {
                "fracfocus": {"records": 13907094},
                "rrc": {"records": 79637354},
                "attribution": {"records": 40624002},
                "completions": {"records": 25989646},
                "production": {"records": 8561948},
                "treatments": {"records": 10000},
            }

    spec = DummySpec()
    print(f"Original sources: {list(spec.data_sources.keys())}")

    pipeline_ids = ["rrc", "production"]
    print(f"Pipeline IDs to keep: {pipeline_ids}")

    tool.filter_design_spec(spec, pipeline_ids)
    print(f"Filtered sources: {list(spec.data_sources.keys())}")

    if set(spec.data_sources.keys()) == {"rrc", "production"}:
        print("[PASS] PASS: Correctly filtered design_spec.data_sources")
    else:
        print(f"[FAIL] FAIL: Expected ['rrc', 'production'], got {list(spec.data_sources.keys())}")

    print()


def test_filter_context_sources():
    """Test context source filtering"""
    print("=" * 80)
    print("TEST 4: filter_context_sources")
    print("=" * 80)

    tool = DataFilterTool()

    context = {
        "data_sources": {
            "fracfocus": {"records": 13907094},
            "rrc": {"records": 79637354},
            "attribution": {"records": 40624002},
            "completions": {"records": 25989646},
            "production": {"records": 8561948},
            "treatments": {"records": 10000},
        },
        "user_prompt": "generate dashboard",
        "gradient_context": {},
    }

    print(f"Original sources: {list(context['data_sources'].keys())}")

    pipeline_ids = ["rrc", "production"]
    print(f"Pipeline IDs to keep: {pipeline_ids}")

    tool.filter_context_sources(context, pipeline_ids)
    print(f"Filtered sources: {list(context['data_sources'].keys())}")

    if set(context["data_sources"].keys()) == {"rrc", "production"}:
        print("[PASS] PASS: Correctly filtered context['data_sources']")

        # Verify other fields preserved
        if "user_prompt" in context and "gradient_context" in context:
            print("[PASS] PASS: Other context fields preserved")
        else:
            print("[FAIL] FAIL: Other context fields lost")
    else:
        print(f"[FAIL] FAIL: Expected ['rrc', 'production'], got {list(context['data_sources'].keys())}")

    print()


def test_integration():
    """Test complete workflow"""
    print("=" * 80)
    print("TEST 5: INTEGRATION - Full Workflow")
    print("=" * 80)

    tool = DataFilterTool()

    # Simulate orchestrator workflow
    print("Simulating: 'generate dashboard of production data from rrc'\n")

    # Step 1: Parse prompt
    intent = "generate dashboard of production data from rrc"
    all_sources = ["fracfocus", "rrc", "attribution", "completions", "production", "treatments"]

    filter_sources = tool.filter_by_prompt(intent, all_sources)
    print(f"Step 1 - Prompt parsing: {intent}")
    print(f"         Detected sources: {filter_sources}")

    # Step 2: Filter pipelines
    pipelines = [
        {"id": src, "metrics": {"file_count": 100}} for src in all_sources
    ]

    filtered_pipelines = tool.filter_pipelines(pipelines, filter_sources)
    print(f"Step 2 - Pipeline filtering: {len(pipelines)} -> {len(filtered_pipelines)}")
    print(f"         Kept: {[p['id'] for p in filtered_pipelines]}")

    # Step 3: Build SessionContext (not using tool - just list comprehension)
    sources_for_session = [p.get('id') for p in filtered_pipelines]
    print(f"Step 3 - SessionContext building: {sources_for_session}")

    # Step 4: Filter design spec
    class DummySpec:
        def __init__(self):
            self.data_sources = {src: {} for src in all_sources}

    spec = DummySpec()
    pipeline_ids = [p["id"] for p in filtered_pipelines]
    tool.filter_design_spec(spec, pipeline_ids)
    print(f"Step 4 - Design spec filtering: {len(all_sources)} -> {len(spec.data_sources)}")
    print(f"         Kept: {list(spec.data_sources.keys())}")

    # Step 5: Filter context
    context = {
        "data_sources": {src: {} for src in all_sources}
    }
    tool.filter_context_sources(context, pipeline_ids)
    print(f"Step 5 - Context filtering: {len(all_sources)} -> {len(context['data_sources'])}")
    print(f"         Kept: {list(context['data_sources'].keys())}")

    # Verify all steps produced consistent results
    expected = {"rrc", "production"}
    if (set(filter_sources) == expected and
        set([p["id"] for p in filtered_pipelines]) == expected and
        set(sources_for_session) == expected and
        set(spec.data_sources.keys()) == expected and
        set(context["data_sources"].keys()) == expected):
        print("\n[PASS] PASS: All steps produced consistent filtering!")
        print("         Only 'rrc' and 'production' throughout the workflow")
        return True
    else:
        print("\n[FAIL] FAIL: Inconsistent filtering across steps")
        return False


def main():
    """Run all verification tests"""
    print("\n")
    print("+" + "=" * 78 + "+")
    print("|" + " " * 20 + "DataFilterTool Verification" + " " * 31 + "|")
    print("+" + "=" * 78 + "+")
    print()

    try:
        test_filter_by_prompt()
        test_filter_pipelines()
        test_filter_design_spec()
        test_filter_context_sources()
        success = test_integration()

        print("=" * 80)
        if success:
            print("[PASS] ALL TESTS PASSED")
            print("   DataFilterTool is working correctly!")
            print("   Ready for Agent Studio integration.")
        else:
            print("[FAIL] SOME TESTS FAILED")
            print("   Review output above for details.")
        print("=" * 80)

    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
