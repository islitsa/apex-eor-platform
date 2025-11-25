"""
Debug why gradient traces don't appear in Agent Studio logs
"""
import sys
import io

# Fix Unicode encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.agents.ui_orchestrator import UICodeOrchestrator
from src.ui.trace_collector import UniversalTraceCollector

print("="*80)
print("DEBUGGING GRADIENT IN PRODUCTION-LIKE ENVIRONMENT")
print("="*80)

# Simulate Agent Studio environment
trace_collector = UniversalTraceCollector()
orchestrator = UICodeOrchestrator(
    trace_collector=trace_collector,
    enable_gradient=True
)

print(f"\n✓ Orchestrator created")
print(f"  - enable_gradient: {orchestrator.enable_gradient}")
print(f"  - gradient_system: {orchestrator.gradient_system}")
print(f"  - gradient_system is None: {orchestrator.gradient_system is None}")

# Fetch real data from API (same as production)
print(f"\n📡 Fetching data from API...")
data_context = orchestrator._fetch_data_context(api_url="http://localhost:8000")

print(f"\n✓ Data fetched:")
print(f"  - success: {data_context.get('success')}")
print(f"  - pipelines: {len(data_context.get('pipelines', []))}")
print(f"  - data_context is None: {data_context is None}")
print(f"  - data_context is truthy: {bool(data_context)}")

# Now call _retrieve_all_knowledge with data_context (EXACTLY like production does)
print(f"\n🧠 Calling _retrieve_all_knowledge with data_context...")
print(f"  - Condition check:")
print(f"    - self.enable_gradient: {orchestrator.enable_gradient}")
print(f"    - self.gradient_system: {orchestrator.gradient_system is not None}")
print(f"    - data_context: {data_context is not None}")
print(f"    - ALL conditions: {orchestrator.enable_gradient and orchestrator.gradient_system and data_context}")

knowledge = orchestrator._retrieve_all_knowledge(data_context=data_context)

print(f"\n✓ Knowledge retrieved:")
print(f"  - Keys: {list(knowledge.keys())}")
print(f"  - Has gradient_context: {'gradient_context' in knowledge}")

if 'gradient_context' in knowledge:
    gc = knowledge['gradient_context']
    print(f"\n✅ GRADIENT CONTEXT FOUND:")
    print(f"  - Domain: {gc['domain_signals']['domain']}")
    print(f"  - Structure: {gc['domain_signals']['structure']}")
    print(f"  - Boost hierarchical nav: {gc['boost_hierarchical_navigation']}")
    print(f"  - Boost tree views: {gc['boost_tree_views']}")
    print(f"  - Boost drill-down: {gc['boost_data_drill_down']}")
else:
    print(f"\n❌ NO GRADIENT CONTEXT - Check why condition failed!")

print(f"\n📝 Traces emitted: {len(trace_collector.traces)}")
gradient_traces = [
    t for t in trace_collector.traces
    if 'gradient' in str(t.data).lower() or
       (t.reasoning and 'gradient' in t.reasoning.lower())
]
print(f"📝 Gradient traces: {len(gradient_traces)}")
for trace in gradient_traces[:3]:
    print(f"  - {trace.agent}/{trace.method}: {trace.trace_type.value}")

print("\n" + "="*80)
print("✅ DEBUG COMPLETE")
print("="*80)
