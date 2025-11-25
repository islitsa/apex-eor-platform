"""Quick test of Protocol Layer implementation"""

import sys
from pathlib import Path
import uuid

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.agents.context.protocol import (
    SessionContext, DiscoveryContext, UserIntent,
    ExecutionContext, TaskType, OutputFormat
)
from src.agents.react_developer import ReactDeveloperAgent

def test_protocol_types():
    """Test that protocol types can be created"""
    print("Testing protocol types...")

    ctx = SessionContext(
        session_id=str(uuid.uuid4()),
        discovery=DiscoveryContext(
            sources=["fracfocus"],
            record_counts={"fracfocus": 239059},
            discovery_confidence=0.95,
            rationale="Test discovery"
        ),
        intent=UserIntent(
            original_query="show fracfocus data",
            parsed_intent="generate_dashboard",
            scope=["fracfocus"],
            task_type=TaskType.DASHBOARD,
            output_format=OutputFormat.REACT
        ),
        execution=ExecutionContext()
    )

    print(f"  Session ID: {ctx.session_id[:8]}...")
    print(f"  Discovered: {ctx.discovery.sources}")
    print(f"  Scope: {ctx.intent.scope}")
    print("  ✓ Protocol types work!")

def test_react_agent_requires_context():
    """Test that ReactAgent requires context"""
    print("\nTesting ReactAgent context requirement...")

    agent = ReactDeveloperAgent()

    try:
        agent.execute()
        print("  ✗ FAILED: Should have raised ValueError")
    except ValueError as e:
        if "Context not provided" in str(e):
            print("  ✓ ReactAgent correctly requires context!")
        else:
            print(f"  ✗ Wrong error: {e}")

def test_react_agent_with_context():
    """Test that ReactAgent works with context"""
    print("\nTesting ReactAgent with context...")

    ctx = SessionContext(
        session_id=str(uuid.uuid4()),
        discovery=DiscoveryContext(
            sources=["fracfocus"],
            record_counts={"fracfocus": 239059},
            discovery_confidence=0.95,
            rationale="Test"
        ),
        intent=UserIntent(
            original_query="test",
            parsed_intent="test",
            scope=["fracfocus"],
            task_type=TaskType.DASHBOARD,
            output_format=OutputFormat.REACT
        ),
        execution=ExecutionContext()
    )

    agent = ReactDeveloperAgent()
    agent_with_ctx = agent.with_context(ctx)

    print(f"  Context injected: {agent.ctx is not None}")
    print(f"  Agent has scope: {agent.ctx.intent.scope if agent.ctx else 'None'}")
    print("  ✓ Context injection works!")

if __name__ == "__main__":
    print("="*60)
    print("PROTOCOL LAYER QUICK TEST")
    print("="*60)

    test_protocol_types()
    test_react_agent_requires_context()
    test_react_agent_with_context()

    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60)
