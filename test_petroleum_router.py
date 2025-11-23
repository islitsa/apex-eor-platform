"""
Test script for petroleum intent router integration.

This script tests various query types to ensure the petroleum router
correctly identifies petroleum context and routes to RRC appropriately.
"""

from src.agents.domain.petroleum_intent_router import (
    PetroleumIntentRouter,
    route_petroleum_query
)


def test_petroleum_router():
    """Test the petroleum intent router with various query types."""

    router = PetroleumIntentRouter()

    # Mock data sources (similar to what orchestrator provides)
    available_sources = [
        {'id': 'rrc'},
        {'id': 'Chemical_data'},
        {'id': 'fracfocus'}
    ]

    print("=" * 80)
    print("PETROLEUM INTENT ROUTER TEST")
    print("=" * 80)
    print(f"\nAvailable sources: {[s['id'] for s in available_sources]}")
    print("\n" + "-" * 80)

    # Test cases
    test_cases = [
        # Should route to RRC (petroleum context present)
        {
            'query': 'Show me production data from wells',
            'expected_route': 'rrc',
            'should_route': True
        },
        {
            'query': 'What is the oil production in the Permian basin?',
            'expected_route': 'rrc',
            'should_route': True
        },
        {
            'query': 'Give me RRC well data',
            'expected_route': 'rrc',
            'should_route': True
        },
        {
            'query': 'Show me drilling permits for horizontal wells',
            'expected_route': 'rrc',
            'should_route': True
        },
        {
            'query': 'Natural gas production statistics',
            'expected_route': 'rrc',
            'should_route': True
        },

        # Should NOT route to RRC (no petroleum context)
        {
            'query': 'Show me production data',
            'expected_route': None,
            'should_route': False
        },
        {
            'query': 'What are the production metrics?',
            'expected_route': None,
            'should_route': False
        },
        {
            'query': 'Display chemical data',
            'expected_route': None,
            'should_route': False
        },
        {
            'query': 'Software production environment status',
            'expected_route': None,
            'should_route': False
        },

        # Edge cases
        {
            'query': 'Show me all data',
            'expected_route': None,
            'should_route': False
        },
        {
            'query': 'FracFocus well completion data',
            'expected_route': 'rrc',  # "well" is a petroleum keyword
            'should_route': True
        }
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases, 1):
        query = test_case['query']
        expected_route = test_case['expected_route']
        should_route = test_case['should_route']

        print(f"\nTest {i}: {query}")
        print(f"  Expected: {'RRC routing' if should_route else 'LLM fallback'}")

        # Test routing
        result = route_petroleum_query(query, available_sources)

        if result is None:
            actual_route = None
            print(f"  Actual:   LLM fallback")
        else:
            actual_route = [s['id'] for s in result]
            print(f"  Actual:   Routed to {actual_route}")

        # Check if result matches expectation
        if should_route:
            if result is not None and expected_route in [s['id'] for s in result]:
                print(f"  Status:   [PASS]")
                passed += 1
            else:
                print(f"  Status:   [FAIL] - Expected RRC routing but got {actual_route}")
                failed += 1
        else:
            if result is None:
                print(f"  Status:   [PASS]")
                passed += 1
            else:
                print(f"  Status:   [FAIL] - Expected LLM fallback but got {actual_route}")
                failed += 1

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Passed: {passed}/{len(test_cases)}")
    print(f"Failed: {failed}/{len(test_cases)}")

    # Display router statistics
    stats = router.get_stats()
    print(f"\nRouter Statistics:")
    print(f"  Total routes: {stats['total_routes']}")
    print(f"  RRC routes: {stats['rrc_routes']} ({stats['rrc_percentage']}%)")
    print(f"  LLM fallback: {stats['llm_fallback_routes']}")

    print("\n" + "=" * 80)

    return passed == len(test_cases)


def test_validation():
    """Test the validation functionality."""

    router = PetroleumIntentRouter()

    print("\n" + "=" * 80)
    print("VALIDATION TEST")
    print("=" * 80)

    test_cases = [
        {
            'prompt': 'Show me oil production data',
            'sources': ['rrc'],
            'should_be_correct': True
        },
        {
            'prompt': 'Show me production data',
            'sources': ['rrc'],
            'should_be_correct': False  # Ambiguous without petroleum context
        },
        {
            'prompt': 'Chemical data analysis',
            'sources': ['Chemical_data'],
            'should_be_correct': True
        }
    ]

    for i, test in enumerate(test_cases, 1):
        result = router.validate_routing_decision(test['prompt'], test['sources'])
        print(f"\nTest {i}: {test['prompt']}")
        print(f"  Routed to: {test['sources']}")
        print(f"  Validation: {'[CORRECT]' if result['correct'] else '[INCORRECT]'}")
        if result['issues']:
            print(f"  Issues: {', '.join(result['issues'])}")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    print("\n")

    # Run main routing tests
    all_passed = test_petroleum_router()

    # Run validation tests
    test_validation()

    # Final result
    print("\n" + "=" * 80)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED - Router integration successful!")
    else:
        print("[FAILED] SOME TESTS FAILED - Review router logic")
    print("=" * 80 + "\n")
