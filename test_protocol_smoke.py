# test_protocol_traces.py
import sys
from io import StringIO

def test_protocol_execution():
    """Test if Protocol layer generates trace messages"""
    print("="*60)
    print("TESTING PROTOCOL TRACE MESSAGES")
    print("="*60)
    
    from src.agents.ui_orchestrator import UICodeOrchestrator
    from src.agents.context.protocol import SessionContext
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured = StringIO()
    
    try:
        # Initialize orchestrator
        orch = UICodeOrchestrator(trace_collector=None)
        
        # Create requirements
        requirements = {
            "intent": "Show fracfocus data only",
            "data_sources": {
                "fracfocus": {"row_count": 13907094},
                "rrc": {"row_count": 79637354}
            }
        }
        
        # Build context (should generate traces)
        ctx = orch._build_session_context(requirements, {}, {})
        
        # Check what was captured
        output = captured.getvalue()
        
    finally:
        sys.stdout = old_stdout
    
    # Analyze output
    print("\nCAPTURED OUTPUT:")
    print("-"*40)
    if output:
        print(output)
    else:
        print("(No output captured)")
    
    print("\nTRACE ANALYSIS:")
    print("-"*40)
    
    trace_markers = [
        "[Orchestrator]",
        "[UX Designer]", 
        "[React Developer]",
        "SessionContext",
        "scope:",
        "sources:"
    ]
    
    for marker in trace_markers:
        if marker in output:
            print(f"✅ Found: {marker}")
        else:
            print(f"❌ Missing: {marker}")
    
    print("\nCONTEXT DETAILS:")
    print(f"  Session ID: {ctx.session_id}")
    print(f"  Sources: {ctx.discovery.sources}")
    print(f"  Scope: {ctx.intent.scope}")

if __name__ == "__main__":
    test_protocol_execution()