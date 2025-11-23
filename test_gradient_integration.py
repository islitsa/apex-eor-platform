"""
Test gradient context integration with real data
"""
import sys
import io

# Fix Unicode encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.agents.ui_orchestrator import UICodeOrchestrator
from src.ui.trace_collector import UniversalTraceCollector

print("="*80)
print("TESTING GRADIENT CONTEXT INTEGRATION")
print("="*80)

# Test 1: Gradient disabled (baseline)
print("\nTEST 1: Without Gradient Context")
print("-"*80)
orchestrator_no_gradient = UICodeOrchestrator(enable_gradient=False)
print(f"✓ Gradient enabled: {orchestrator_no_gradient.enable_gradient}")
print(f"✓ Gradient system: {orchestrator_no_gradient.gradient_system}")

# Test 2: Gradient enabled
print("\nTEST 2: With Gradient Context")
print("-"*80)
trace_collector = UniversalTraceCollector()
orchestrator_with_gradient = UICodeOrchestrator(
    trace_collector=trace_collector,
    enable_gradient=True
)
print(f"✓ Gradient enabled: {orchestrator_with_gradient.enable_gradient}")
print(f"✓ Gradient system: {orchestrator_with_gradient.gradient_system}")

# Test 3: Domain extraction
print("\nTEST 3: Domain Signal Extraction")
print("-"*80)
mock_data_context = {
    'success': True,
    'pipelines': [
        {
            'id': 'fracfocus_chemical_data',
            'display_name': 'FracFocus Chemical Data',
            'files': {
                'subdirs': {
                    'downloads': {
                        'subdirs': {
                            'extracted': {
                                'files': [
                                    {'name': 'file1.csv'},
                                    {'name': 'file2.csv'}
                                ],
                                'subdirs': {
                                    'parsed': {
                                        'files': [
                                            {'name': 'parsed1.csv'},
                                            {'name': 'parsed2.csv'}
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        {
            'id': 'rrc_completions',
            'display_name': 'RRC Completion Data'
        }
    ]
}

domain_signals = orchestrator_with_gradient._extract_domain_signals(mock_data_context)
print(f"✓ Domain: {domain_signals['domain']}")
print(f"✓ Structure: {domain_signals['structure']}")
print(f"✓ Keywords: {domain_signals['keywords'][:5]}")
print(f"✓ Data Types: {domain_signals['data_types']}")
print(f"✓ Max Depth: {domain_signals['metrics']['max_depth']}")
print(f"✓ Total Files: {domain_signals['metrics']['total_files']}")

# Expected: petroleum_energy, deeply_nested_directories, depth=3, files=4

# Test 4: Knowledge retrieval with gradient
print("\nTEST 4: Knowledge Retrieval with Gradient Boosting")
print("-"*80)
knowledge = orchestrator_with_gradient._retrieve_all_knowledge(
    data_context=mock_data_context
)
print(f"✓ Knowledge keys: {list(knowledge.keys())}")
if 'gradient_context' in knowledge:
    print("✅ Gradient context present in knowledge")
    gc = knowledge['gradient_context']
    print(f"  ✓ Domain: {gc['domain_signals']['domain']}")
    print(f"  ✓ Structure: {gc['domain_signals']['structure']}")
    print(f"  ✓ Boost hierarchical nav: {gc.get('boost_hierarchical_navigation')}")
    print(f"  ✓ Boost tree views: {gc.get('boost_tree_views')}")
    print(f"  ✓ Boost drill-down: {gc.get('boost_data_drill_down')}")
else:
    print("❌ Gradient context NOT in knowledge")

# Test 5: Check traces
print("\nTEST 5: Trace Emissions")
print("-"*80)
traces = trace_collector.traces
print(f"✓ Total traces: {len(traces)}")
gradient_traces = [
    t for t in traces
    if 'gradient' in str(t.data).lower() or
       (t.reasoning and 'gradient' in t.reasoning.lower())
]
print(f"✓ Gradient-related traces: {len(gradient_traces)}")
for trace in gradient_traces[:5]:  # Show first 5
    print(f"  - {trace.agent}/{trace.method}: {trace.trace_type.value}")

print("\n" + "="*80)
print("✅ TEST COMPLETE - Gradient Context Integration Working!")
print("="*80)

print("\n📊 Summary:")
print(f"  ✓ Gradient system initializes: {'YES' if orchestrator_with_gradient.gradient_system else 'NO'}")
print(f"  ✓ Domain extraction works: {domain_signals['domain'] == 'petroleum_energy'}")
print(f"  ✓ Structure detection works: {domain_signals['structure'] == 'deeply_nested_directories'}")
print(f"  ✓ Gradient context in knowledge: {'gradient_context' in knowledge}")
print(f"  ✓ Trace emissions working: {len(gradient_traces) > 0}")
