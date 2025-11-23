"""
Example: Agent using discovery tools for context swimming

This demonstrates how an agent would autonomously discover context
rather than receiving pre-assembled context in prompts.

BEFORE (hardcoded context):
    prompt = "Create dashboard for these sources: fracfocus, rrc, NETL EDX"
    # Agent receives context, doesn't discover it

AFTER (context swimming):
    tools = DiscoveryTools()
    sources = tools.find_data_sources("chemical data for EOR")
    # Agent discovers context based on intent
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.context.discovery_tools import DiscoveryTools


def example_agent_workflow():
    """
    Simulate an agent workflow using discovery tools.

    This shows how an agent would:
    1. Start with user intent
    2. Discover relevant data sources
    3. Get schemas to understand what's available
    4. Check processing status
    5. Make decisions based on discovered context
    """

    print("\n" + "="*80)
    print("EXAMPLE: AGENT AUTONOMOUS DISCOVERY WORKFLOW")
    print("="*80)

    # Initialize discovery tools
    tools = DiscoveryTools()

    # === STEP 1: User Intent ===
    user_intent = "I want to analyze chemical additives used in oil production"

    print(f"\n[AGENT] User intent: '{user_intent}'")
    print("[AGENT] I need to discover what data sources are available...")

    # === STEP 2: Discover Data Sources ===
    sources = tools.find_data_sources(
        query=user_intent,
        top_k=5,
        min_relevance=0.6  # Only highly relevant sources
    )

    print(f"\n[AGENT] I discovered {len(sources)} relevant data sources:")
    for source in sources:
        print(f"  - {source['name']}: {source['relevance']:.2%} relevance")

    if not sources:
        print("\n[AGENT] No relevant sources found. Cannot proceed.")
        return

    # === STEP 3: Get Schemas for Top Sources ===
    print(f"\n[AGENT] Let me examine the schemas to understand what columns are available...")

    schemas = {}
    for source in sources[:3]:  # Check top 3
        schema = tools.get_schema(source['name'])
        if schema:
            schemas[source['name']] = schema
            print(f"\n  [AGENT] {source['name']} schema:")
            print(f"    - {len(schema['columns'])} columns")
            print(f"    - {schema['row_count']:,} rows")
            print(f"    - Key columns: {', '.join(schema['columns'][:5])}")

    # === STEP 4: Check Processing Status ===
    print(f"\n[AGENT] Checking which sources are ready to use...")

    ready_sources = []
    for source in sources:
        status = tools.check_status(source['name'])
        if status:
            print(f"\n  [AGENT] {source['name']}: {status['status']}")
            if status['has_parsed']:
                print(f"    [AGENT] [OK] Ready to use (has parsed data)")
                ready_sources.append(source['name'])
            else:
                print(f"    [AGENT] [NOT READY] No parsed data")

    # === STEP 5: Agent Decision ===
    print(f"\n[AGENT] Analysis complete. Decision:")
    print(f"  - Total sources discovered: {len(sources)}")
    print(f"  - Sources with schemas: {len(schemas)}")
    print(f"  - Ready to use: {len(ready_sources)}")

    if ready_sources:
        print(f"\n[AGENT] I can create a dashboard using these sources:")
        for source_name in ready_sources:
            if source_name in schemas:
                schema = schemas[source_name]
                print(f"  - {source_name}: {len(schema['columns'])} columns, {schema['row_count']:,} rows")

        print(f"\n[AGENT] Proceeding with dashboard generation...")
        print(f"[AGENT] (In a real workflow, I would now call the UX Designer agent)")
    else:
        print(f"\n[AGENT] No sources are ready to use. Cannot create dashboard.")
        print(f"[AGENT] The user should run the data pipeline first.")

    print("\n" + "="*80)
    print("AGENT WORKFLOW COMPLETE")
    print("="*80 + "\n")


def example_one_shot_discovery():
    """
    Example using the one-shot discover_all() method.

    This is more convenient for agents that need complete context quickly.
    """

    print("\n" + "="*80)
    print("EXAMPLE: ONE-SHOT DISCOVERY")
    print("="*80)

    tools = DiscoveryTools()

    # One call gets everything
    results = tools.discover_all(
        query="well production data for Texas",
        top_k=3,
        get_schemas=True
    )

    print(f"\n[AGENT] Discovery results:")
    print(f"  - Query: '{results['query']}'")
    print(f"  - Sources found: {len(results['sources'])}")
    print(f"  - Schemas retrieved: {len(results['schemas'])}")
    print(f"  - Statuses checked: {len(results['statuses'])}")

    # Agent can now use this context
    for source in results['sources']:
        name = source['name']
        schema = results['schemas'].get(name)
        status = results['statuses'].get(name)

        print(f"\n  {name}:")
        print(f"    Relevance: {source['relevance']:.2%}")
        if schema:
            print(f"    Columns: {len(schema['columns'])}")
            print(f"    Rows: {schema['row_count']:,}")
        if status:
            print(f"    Status: {status['status']}")

    print("\n" + "="*80 + "\n")


def example_compare_with_without_discovery():
    """
    Compare agent prompts with and without discovery tools.
    """

    print("\n" + "="*80)
    print("COMPARISON: WITH vs WITHOUT DISCOVERY")
    print("="*80)

    print("\n--- WITHOUT DISCOVERY (old approach) ---")
    print("Agent receives hardcoded context in prompt:")
    print("""
  You have these data sources:
  - fracfocus: chemical disclosure data (17 columns)
  - rrc: Railroad Commission production data (6 columns)
  - NETL EDX: Well characteristics (unknown schema)

  Create a dashboard for chemical analysis.
    """)
    print("Issues:")
    print("  [-] Context becomes stale when repository changes")
    print("  [-] Agent can't verify column names")
    print("  [-] Wastes tokens on irrelevant sources")

    print("\n--- WITH DISCOVERY (new approach) ---")
    print("Agent discovers context autonomously:")

    tools = DiscoveryTools()

    # Agent discovers
    sources = tools.find_data_sources("chemical analysis", top_k=2)
    schema = tools.get_schema(sources[0]['name']) if sources else None

    print(f"""
  [Agent discovers]
  sources = tools.find_data_sources("chemical analysis")
  schema = tools.get_schema(sources[0]['name'])

  [Agent now has]
  - Top source: {sources[0]['name']} ({sources[0]['relevance']:.2%} relevant)
  - Verified columns: {schema['columns'][:5] if schema else 'N/A'}
  - Actual row count: {schema['row_count']:,} if schema else 'N/A'
    """)

    print("Benefits:")
    print("  [+] Context is always current")
    print("  [+] Agent verifies actual schemas")
    print("  [+] Only retrieves relevant sources")
    print("  [+] Adapts to repository changes automatically")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    # Run examples
    example_agent_workflow()
    example_one_shot_discovery()
    example_compare_with_without_discovery()

    print("\nKEY INSIGHT:")
    print("Agents don't receive context - they discover it.")
    print("This is 'context swimming' in action.")
    print()
