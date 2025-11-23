"""
Diagnostic Agent Chat Runner - Figure out why terminal output isn't captured

This version will help us understand:
1. WHEN agents are printing
2. HOW they're printing
3. WHY we're not catching it
"""

import streamlit as st
import sys
import io
import os
import builtins
import threading
import logging
from pathlib import Path
from typing import Dict, Any
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# ============================================================================
# DIAGNOSTIC OUTPUT CAPTURE - Track ALL output methods
# ============================================================================

class DiagnosticCapture:
    """Diagnostic capture to understand output patterns"""

    def __init__(self):
        self.captured = []
        self.original_print = builtins.print
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.original_write = None

    def start_capture(self):
        """Start comprehensive capture"""
        print("[DIAGNOSTIC] Setting up capture...")

        # 1. Capture print()
        def diagnostic_print(*args, **kwargs):
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            source = "PRINT"

            # Get the actual output
            output = io.StringIO()
            kwargs['file'] = output
            self.original_print(*args, **kwargs)
            text = output.getvalue()

            # Log it
            self.captured.append(f"[{timestamp}] [{source}] {text}")

            # Still print to terminal
            self.original_stdout.write(f"[CAPTURED-PRINT] {text}")
            self.original_stdout.flush()

        builtins.print = diagnostic_print

        # 2. Capture sys.stdout.write()
        class StdoutDiagnostic:
            def __init__(self, parent):
                self.parent = parent

            def write(self, text):
                if text and text != '\n':
                    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    self.parent.captured.append(f"[{timestamp}] [STDOUT] {text}")

                # Still write to terminal
                self.parent.original_stdout.write(f"[CAPTURED-STDOUT] {text}")
                self.parent.original_stdout.flush()

            def flush(self):
                self.parent.original_stdout.flush()

        sys.stdout = StdoutDiagnostic(self)

        # 3. Capture sys.stderr.write()
        class StderrDiagnostic:
            def __init__(self, parent):
                self.parent = parent

            def write(self, text):
                if text and text != '\n':
                    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    self.parent.captured.append(f"[{timestamp}] [STDERR] {text}")

                # Still write to terminal
                self.parent.original_stderr.write(f"[CAPTURED-STDERR] {text}")
                self.parent.original_stderr.flush()

            def flush(self):
                self.parent.original_stderr.flush()

        sys.stderr = StderrDiagnostic(self)

        # 4. Capture logging
        class LogCapture(logging.Handler):
            def __init__(self, parent):
                super().__init__()
                self.parent = parent

            def emit(self, record):
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                msg = self.format(record)
                self.parent.captured.append(f"[{timestamp}] [LOG-{record.levelname}] {msg}")

                # Still log to terminal
                self.parent.original_stdout.write(f"[CAPTURED-LOG] {msg}\n")
                self.parent.original_stdout.flush()

        # Add our handler to root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(LogCapture(self))

        # 5. Monitor file descriptors directly
        self.monitor_fd()

        print("[DIAGNOSTIC] Capture setup complete!")

    def monitor_fd(self):
        """Monitor file descriptors directly"""
        # This is where output might be sneaking through
        try:
            # Save original file descriptors
            self.original_fd_1 = os.dup(1)  # stdout
            self.original_fd_2 = os.dup(2)  # stderr

            # Create pipes to intercept
            r1, w1 = os.pipe()
            r2, w2 = os.pipe()

            # We'd redirect here, but it's complex and might break Streamlit
            # Just note that this is a possible escape route

        except Exception as e:
            print(f"[DIAGNOSTIC] FD monitoring failed: {e}")


# Set up diagnostic capture BEFORE any imports
DIAGNOSTIC = DiagnosticCapture()
DIAGNOSTIC.start_capture()

# Test our capture
print("TEST: Can we capture this print?")
sys.stdout.write("TEST: Can we capture this stdout.write?\n")
sys.stderr.write("TEST: Can we capture this stderr.write?\n")
logging.info("TEST: Can we capture this logging.info?")

# NOW import agents - let's see what they output during import
print("\n[DIAGNOSTIC] About to import agents...")
print("[DIAGNOSTIC] Watch for any output that appears WITHOUT [CAPTURED-*] prefix")
print("[DIAGNOSTIC] That output is escaping our capture!\n")

from src.agents.ui_orchestrator import UICodeOrchestrator
from src.builders.dashboard_builder import DashboardBuilder
from shared_state import PipelineState

print("\n[DIAGNOSTIC] Agent import complete")
print(f"[DIAGNOSTIC] Captured {len(DIAGNOSTIC.captured)} outputs so far")


class DiagnosticRunner:
    """Diagnostic runner to trace output issues"""

    def __init__(self):
        st.set_page_config(
            page_title="Diagnostic Runner",
            page_icon="D",
            layout="wide"
        )

        if 'status' not in st.session_state:
            st.session_state.status = 'ready'
        if 'context' not in st.session_state:
            st.session_state.context = None

    def run_diagnostic_generation(self):
        """Run generation with detailed diagnostics"""

        st.write("### Starting Diagnostic Generation")
        st.write("Check your VS Code terminal for output patterns!")

        # Load context
        print("\n" + "="*60)
        print("[DIAGNOSTIC] Loading context...")
        context = PipelineState.load_context(check_freshness=False)

        if not context:
            st.error("No context found")
            return

        st.success(f"Loaded {len(context.get('data_sources', {}))} data sources")

        # Create orchestrator
        print("\n[DIAGNOSTIC] Creating orchestrator...")
        orchestrator = UICodeOrchestrator()
        print(f"[DIAGNOSTIC] Orchestrator type: {type(orchestrator)}")
        print(f"[DIAGNOSTIC] Has ux_designer: {hasattr(orchestrator, 'ux_designer')}")
        print(f"[DIAGNOSTIC] Has gradio_developer: {hasattr(orchestrator, 'gradio_developer')}")

        # Build requirements
        requirements = {
            'screen_type': 'test_dashboard',
            'intent': 'Test generation for diagnostic purposes',
            'data_sources': context.get('data_sources', {})
        }

        # THE KEY MOMENT - Call generate_ui_code and watch for output
        print("\n" + "="*60)
        print("[DIAGNOSTIC] CALLING orchestrator.generate_ui_code()")
        print("[DIAGNOSTIC] Any output below WITHOUT [CAPTURED-*] is escaping!")
        print("="*60 + "\n")

        try:
            # This is where agent chatter should appear
            result = orchestrator.generate_ui_code(requirements, context)

            print("\n" + "="*60)
            print(f"[DIAGNOSTIC] Generation complete: {len(result)} chars")
            print("="*60)

        except Exception as e:
            print(f"\n[DIAGNOSTIC] Error during generation: {e}")
            st.error(f"Generation failed: {e}")

        # Show what we captured
        st.write("### Captured Output")
        st.write(f"Total captured: {len(DIAGNOSTIC.captured)} lines")

        if DIAGNOSTIC.captured:
            # Show last 50 captured outputs
            st.code('\n'.join(DIAGNOSTIC.captured[-50:]), language='text')
        else:
            st.warning("Nothing captured! Check terminal for uncaptured output.")

        # Analysis
        st.write("### Diagnostic Analysis")

        # Check for different output types
        print_count = sum(1 for c in DIAGNOSTIC.captured if '[PRINT]' in c)
        stdout_count = sum(1 for c in DIAGNOSTIC.captured if '[STDOUT]' in c)
        stderr_count = sum(1 for c in DIAGNOSTIC.captured if '[STDERR]' in c)
        log_count = sum(1 for c in DIAGNOSTIC.captured if '[LOG-' in c)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Print()", print_count)
        col2.metric("Stdout", stdout_count)
        col3.metric("Stderr", stderr_count)
        col4.metric("Logging", log_count)

        st.info("""
        **How to interpret:**
        1. Check VS Code terminal
        2. Look for output WITHOUT [CAPTURED-*] prefix
        3. That's the output escaping our capture!
        4. Note WHEN it appears (during import? during generation?)
        """)

    def run(self):
        """Main diagnostic interface"""

        st.title("D Agent Output Diagnostic Tool")
        st.markdown("This tool helps identify why agent output isn't appearing in Streamlit")

        st.markdown("---")

        # Instructions
        st.warning("""
        **Instructions:**
        1. Keep VS Code terminal visible
        2. Click 'Run Diagnostic' below
        3. Watch terminal for output patterns
        4. Look for output WITHOUT [CAPTURED-*] prefix - that's escaping!
        """)

        if st.button("Run Diagnostic", type="primary"):
            self.run_diagnostic_generation()

        # Manual check
        if st.button("Show Current Captures"):
            st.write(f"Total captured so far: {len(DIAGNOSTIC.captured)}")
            if DIAGNOSTIC.captured:
                st.code('\n'.join(DIAGNOSTIC.captured[-20:]), language='text')


if __name__ == "__main__":
    runner = DiagnosticRunner()
    runner.run()
