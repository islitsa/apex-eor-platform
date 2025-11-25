"""
Test that orchestrator trace now appears with fast adapter
"""

def test_orchestrator_trace():
    print("="*80)
    print("TESTING ORCHESTRATOR TRACE (AFTER PERFORMANCE FIX)")
    print("="*80)
    print()

    from src.agents.ui_orchestrator import UICodeOrchestrator
    from src.agents.trace_collector import TraceCollector
    import time

    # Create trace collector
    trace_collector = TraceCollector()

    # Initialize orchestrator with trace collector
    orch = UICodeOrchestrator(trace_collector=trace_collector)

    print("Fetching data from API...")
    start = time.time()

    # Fetch data context (this will trigger the trace)
    data_context = orch._fetch_data_context()

    elapsed = time.time() - start
    print(f"Data fetch took: {elapsed:.2f} seconds")
    print()

    if data_context.get('success'):
        print("SUCCESS: Data fetched")
        print(f"  Pipelines: {len(data_context.get('pipelines', []))}")
        print()

        # Check if traces were collected
        traces = trace_collector.get_traces()
        print(f"Traces collected: {len(traces)}")

        # Find orchestrator traces
        orch_traces = [t for t in traces if t.get('agent') == 'Orchestrator']
        print(f"Orchestrator traces: {len(orch_traces)}")

        if orch_traces:
            print("\nOrchestrator trace found!")
            for trace in orch_traces:
                if 'Successfully fetched REAL DATA' in str(trace.get('reasoning', '')):
                    print("\nDATA SOURCE TRACE:")
                    print("-" * 80)
                    reasoning = trace.get('reasoning', '')
                    # Print first 1000 chars of trace
                    print(reasoning[:1500])
                    print("\n... (trace continues) ...")
                    break
        else:
            print("\nNO orchestrator traces found!")
    else:
        print(f"FAILED: {data_context.get('error')}")

    print()
    print("="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_orchestrator_trace()
