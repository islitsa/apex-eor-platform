"""
Test Memory System for Iterative Refinement
"""
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.agents.gradio_developer import GradioImplementationAgent
from src.agents.ux_designer import DesignSpec

print("=" * 80)
print("TESTING: Memory System for Iterative Learning")
print("=" * 80)
print()

# Create agent
print("1. Creating Gradio Developer agent with memory enabled...")
agent = GradioImplementationAgent()
print(f"   Memory enabled: {agent.memory_enabled}")
print(f"   Memory history: {len(agent.implementation_history)} entries")
print()

# First generation
print("2. Generating initial UI (no history yet)...")
design_spec_v1 = DesignSpec(
    screen_type="dashboard",
    intent="create a simple dashboard with a title and button",
    design_reasoning="Use clean layout with Material Symbols"
)

context_v1 = {
    'data_sources': {},
    'user_feedback': None
}

code_v1 = agent.build(design_spec_v1, context_v1)
print(f"   ✅ Generated v1: {len(code_v1)} chars")
print(f"   Memory history: {len(agent.implementation_history)} entries")
print()

# Check memory
if agent.implementation_history:
    entry = agent.implementation_history[0]
    print("   Memory entry 0:")
    print(f"     - Screen type: {entry['screen_type']}")
    print(f"     - Intent: {entry['intent'][:50]}...")
    print(f"     - Code length: {entry['code_length']}")
    print(f"     - Components: {entry['code_summary']}")
    print(f"     - Feedback: {entry.get('user_feedback', 'None')}")
    print()

# Second generation with feedback
print("3. Generating refined UI with user feedback...")
design_spec_v2 = DesignSpec(
    screen_type="dashboard",
    intent="create a simple dashboard with a title and button",
    design_reasoning="Use clean layout with Material Symbols"
)

context_v2 = {
    'data_sources': {},
    'user_feedback': "Make the button bigger and change the title to 48px"
}

code_v2 = agent.build(design_spec_v2, context_v2)
print(f"   ✅ Generated v2: {len(code_v2)} chars")
print(f"   Memory history: {len(agent.implementation_history)} entries")
print()

# Check memory again
if len(agent.implementation_history) >= 2:
    entry = agent.implementation_history[1]
    print("   Memory entry 1:")
    print(f"     - Screen type: {entry['screen_type']}")
    print(f"     - Intent: {entry['intent'][:50]}...")
    print(f"     - Code length: {entry['code_length']}")
    print(f"     - Components: {entry['code_summary']}")
    print(f"     - Feedback: {entry.get('user_feedback', 'None')}")
    print()

# Third generation with different feedback
print("4. Generating another refinement...")
context_v3 = {
    'data_sources': {},
    'user_feedback': "Add a second button that says 'Cancel'"
}

code_v3 = agent.build(design_spec_v2, context_v3)
print(f"   ✅ Generated v3: {len(code_v3)} chars")
print(f"   Memory history: {len(agent.implementation_history)} entries")
print()

# Show full memory context
print("5. Getting memory context for next generation...")
memory_context = agent._get_memory_context()
if memory_context:
    print("   Memory context preview (first 500 chars):")
    print("   " + "-" * 76)
    print("   " + memory_context[:500].replace('\n', '\n   '))
    print("   " + "-" * 76)
else:
    print("   No memory context (empty history)")
print()

print("=" * 80)
print("MEMORY SYSTEM TEST COMPLETE!")
print()
print("Summary:")
print(f"  - Total implementations tracked: {len(agent.implementation_history)}")
print(f"  - Memory system working: {'✅ YES' if agent.implementation_history else '❌ NO'}")
print(f"  - Feedback captured: {'✅ YES' if any(e.get('user_feedback') for e in agent.implementation_history) else '❌ NO'}")
print()
print("The agent will now remember:")
print("  1. What components were used in each version")
print("  2. What feedback users provided")
print("  3. Code snippets from previous attempts")
print("  4. This helps avoid repeating mistakes in future iterations!")
print("=" * 80)
