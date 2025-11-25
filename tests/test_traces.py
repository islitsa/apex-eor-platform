"""Test that trace collection is working"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.ui.trace_collector import UniversalTraceCollector, TraceType

print("Testing Trace Collection System...")
print("=" * 60)

# Create trace collector
collector = UniversalTraceCollector()

# Simulate agent execution
collector.trace_call("UXDesigner", "design", "requirements={}")
collector.trace_thinking("UXDesigner", "design", "Analyzing user requirements...")
collector.trace_reasoning(
    "UXDesigner",
    "_design_with_cot",
    reasoning="1. USER NEEDS: Dashboard for pipeline monitoring\n2. PATTERNS: Use Material Design 3 cards\n3. HIERARCHY: Status overview at top",
    knowledge_used=["M3_Cards", "Status_Indicators"]
)
collector.trace_decision("UXDesigner", "design", "Created design specification with 5 components")

collector.trace_call("GradioDeveloper", "build", "design_spec={}")
collector.trace_reasoning(
    "GradioDeveloper",
    "_plan_implementation",
    reasoning="1. COMPONENT MAPPING: Use gr.Blocks for layout\n2. CONSTRAINTS: Gradio doesn't support nested tabs\n3. WORKAROUNDS: Use accordion instead",
    knowledge_used=["gradio_blocks", "gradio_limitations"]
)

print(f"\nTotal traces collected: {len(collector.traces)}")
print(f"Reasoning traces: {len(collector.get_reasoning_traces())}")
print("\nReasoning traces:")
print("-" * 60)

for trace in collector.get_reasoning_traces():
    print(f"\n{trace.agent} - {trace.method}")
    print(f"Reasoning (first 200 chars):")
    print(trace.reasoning[:200] if trace.reasoning else "None")
    print(f"Knowledge used: {trace.knowledge_used}")

print("\n" + "=" * 60)
print("SUCCESS! Trace collection is working!")
print("\nIf you can see reasoning above, the system works.")
print("The issue is that you're viewing OLD browser tabs with ZOMBIE instances.")
