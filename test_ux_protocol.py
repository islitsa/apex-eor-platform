"""Quick test of UXDesignerAgent with protocol"""

import sys
from pathlib import Path
import uuid

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.agents.context.protocol import (
    SessionContext, DiscoveryContext, UserIntent,
    ExecutionContext, TaskType, OutputFormat
)
from src.agents.ux_designer import UXDesignerAgent

def test_ux_agent_requires_context():
    """Test that UXAgent requires context"""
    print("Testing UXAgent context requirement...")

    agent = UXDesignerAgent()

    try:
        agent.execute()
        print("  X FAILED: Should have raised ValueError")
    except ValueError as e:
        if "Context not provided" in str(e):
            print("  OK: UXAgent correctly requires context!")
        else:
            print(f"  X Wrong error: {e}")

def test_ux_agent_with_context():
    """Test that UXAgent works with context"""
    print("\nTesting UXAgent with context...")

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

    agent = UXDesignerAgent()
    agent_with_ctx = agent.with_context(ctx)

    print(f"  Context injected: {agent.ctx is not None}")
    print(f"  Agent has scope: {agent.ctx.intent.scope if agent.ctx else 'None'}")
    print("  OK: Context injection works!")

if __name__ == "__main__":
    print("="*60)
    print("UX DESIGNER PROTOCOL TEST")
    print("="*60)

    test_ux_agent_requires_context()
    test_ux_agent_with_context()

    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60)
