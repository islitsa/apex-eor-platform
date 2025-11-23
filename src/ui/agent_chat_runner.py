"""
Agent Chat Runner V2 - ACTUALLY captures output to Streamlit

Key Fix: Monkey-patch print() and sys.stdout BEFORE importing agents.
This ensures ALL agent chatter appears in Streamlit's terminal pane.
"""

import streamlit as st
import sys
import io
import builtins
import threading
import queue
from pathlib import Path
from typing import Dict, Any, Optional
import time
import subprocess
import webbrowser
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class StreamlitOutputCapture:
    """Global output capture that actually works"""

    def __init__(self):
        self.original_print = builtins.print
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.buffer = []
        self.queue = queue.Queue()
        self.capturing = False

    def start_capture(self):
        """Start capturing ALL output"""
        self.capturing = True

        # Create custom print function
        def captured_print(*args, **kwargs):
            output = io.StringIO()
            kwargs['file'] = output
            self.original_print(*args, **kwargs)
            text = output.getvalue()

            # Send to original stdout (terminal)
            self.original_stdout.write(text)

            # Capture if active
            if self.capturing:
                self.buffer.append(text)
                self.queue.put(('print', text))

        # Create custom stdout
        class StdoutCapture:
            def __init__(self, parent):
                self.parent = parent

            def write(self, text):
                # Send to original stdout
                self.parent.original_stdout.write(text)
                # Capture if active
                if self.parent.capturing:
                    self.parent.buffer.append(text)
                    self.parent.queue.put(('stdout', text))

            def flush(self):
                self.parent.original_stdout.flush()

        # Monkey-patch globally
        builtins.print = captured_print
        sys.stdout = StdoutCapture(self)

    def get_output(self):
        """Get all captured output"""
        output = []
        while not self.queue.empty():
            try:
                output.append(self.queue.get_nowait())
            except queue.Empty:
                break
        return output

    def get_buffer(self):
        """Get all buffered output"""
        return ''.join(self.buffer)


# CRITICAL: Set up output capture BEFORE importing agents
OUTPUT_CAPTURE = StreamlitOutputCapture()
OUTPUT_CAPTURE.start_capture()  # Start capturing immediately

# NOW import agents (they will use our patched print)
from src.agents.ui_orchestrator import UICodeOrchestrator
from src.builders.dashboard_builder import DashboardBuilder
from shared_state import PipelineState, SessionState


class AgentChatRunnerV2:
    """Enhanced auto-running agent chat with REAL output capture"""

    def __init__(self):
        st.set_page_config(
            page_title="Agent UI Generator",
            page_icon="[AI]",
            layout="wide"
        )

        # Initialize session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'status' not in st.session_state:
            st.session_state.status = 'initializing'
        if 'generation_started' not in st.session_state:
            st.session_state.generation_started = False
        if 'dashboard_code' not in st.session_state:
            st.session_state.dashboard_code = None
        if 'dashboard_file' not in st.session_state:
            st.session_state.dashboard_file = None
        if 'context' not in st.session_state:
            st.session_state.context = None
        if 'auto_started' not in st.session_state:
            st.session_state.auto_started = False
        if 'prompt' not in st.session_state:
            st.session_state.prompt = None
        if 'terminal_output' not in st.session_state:
            st.session_state.terminal_output = []

    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add a message to the chat"""
        message = {
            'role': role,
            'content': content,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.messages.append(message)

    def render_message(self, msg: Dict):
        """Render a chat message"""
        role = msg['role']
        content = msg['content']

        # Role to display name mapping (no avatars to avoid encoding issues)
        role_names = {
            'system': 'System',
            'ux_designer': 'UX Designer',
            'gradio_developer': 'Gradio Developer',
            'orchestrator': 'Orchestrator',
            'builder': 'Dashboard Builder',
            'prompt': 'Prompt',
        }

        name = role_names.get(role, role.title())

        # Use chat_message without avatar parameter
        with st.chat_message(name):
            if '**' in content or '\n' in content or '```' in content:
                st.markdown(content)
            else:
                st.write(content)

            # Show metadata if present
            if msg.get('metadata') and len(msg['metadata']) > 0:
                with st.expander("Details", expanded=False):
                    st.json(msg['metadata'])

    def generate_prompt_from_context(self, context: Dict) -> str:
        """Generate an intelligent prompt based on context"""
        datasets = list(context.get('data_sources', {}).keys())
        total_records = context.get('summary', {}).get('human_readable_records', 'Unknown')

        # Determine UI type based on data
        if 'production' in str(datasets).lower():
            ui_type = "production monitoring dashboard"
        elif 'permits' in str(datasets).lower():
            ui_type = "permit tracking interface"
        elif 'completions' in str(datasets).lower():
            ui_type = "well completion analyzer"
        else:
            ui_type = "data exploration dashboard"

        prompt = f"""Create a {ui_type} with the following requirements:

1. Display data from {len(datasets)} sources: {', '.join(datasets)}
2. Handle {total_records} total records efficiently
3. Include interactive filtering and drill-down capabilities
4. Use Material Design 3 patterns for modern UX
5. Implement real-time data refresh capabilities
6. Add export functionality for reports

Focus on usability and performance for petroleum engineering workflows."""

        return prompt

    def load_and_start(self):
        """Load context and immediately start generation"""
        # Load context from shared state
        try:
            context = PipelineState.load_context(check_freshness=True)

            if context is None:
                self.add_message('system', "[ERROR] No pipeline context found. Please run pipeline first.")
                st.session_state.status = 'error'
                return False

            st.session_state.context = context

            # Generate prompt from context
            prompt = self.generate_prompt_from_context(context)
            st.session_state.prompt = prompt

            # Show what we're doing
            sources = len(context.get('data_sources', {}))
            total_records = context.get('summary', {}).get('human_readable_records', 'Unknown')

            self.add_message('system', "[OK] Context loaded from pipeline", {
                'data_sources': sources,
                'total_records': total_records,
                'datasets': list(context.get('data_sources', {}).keys())
            })

            self.add_message('prompt', f"**Generated Prompt:**\n\n{prompt}")

            return True

        except Exception as e:
            self.add_message('system', f"[ERROR] Error loading context: {e}")
            st.session_state.status = 'error'
            return False

    def update_terminal_display(self, placeholder):
        """Update terminal display with captured output"""
        # Get new output from capture
        new_output = OUTPUT_CAPTURE.get_output()

        for output_type, text in new_output:
            if text.strip():
                st.session_state.terminal_output.append(text)

        # Display in terminal (last 100 lines)
        if st.session_state.terminal_output:
            terminal_text = ''.join(st.session_state.terminal_output[-100:])
            placeholder.code(terminal_text, language='text')
        else:
            placeholder.code("Waiting for output...", language='text')

    def live_update_terminal(self, placeholder, stop_event):
        """Continuously update terminal in background thread"""
        while not stop_event.is_set():
            self.update_terminal_display(placeholder)
            time.sleep(0.1)  # Update every 100ms

    def generate_with_capture(self):
        """Generate dashboard with full output capture"""
        context = st.session_state.context
        prompt = st.session_state.prompt

        # Step 1: Build base dashboard
        self.add_message('builder', "**Step 1/3:** Building base dashboard...")

        try:
            builder = DashboardBuilder()
            base_code = builder.build(context)
            self.add_message('builder', f"[OK] Base dashboard generated: {len(base_code)} characters")

        except Exception as e:
            self.add_message('builder', f"[ERROR] Error: {e}")
            st.session_state.status = 'error'
            return

        # Step 2: Generate with agents (with LIVE output capture)
        self.add_message('orchestrator', "**Step 2/3:** Launching two-agent system...")

        try:
            # Create orchestrator (this prints immediately)
            orchestrator = UICodeOrchestrator()

            # Build requirements from prompt
            requirements = {
                'screen_type': 'dynamic_dashboard',
                'intent': prompt,
                'data_sources': context.get('data_sources', {})
            }

            # Generate (output automatically captured by monkey-patch)
            navigation_code = orchestrator.generate_ui_code(requirements, context)

            # Combine codes
            final_code = self.inject_navigation(base_code, navigation_code)

            self.add_message('orchestrator', f"[OK] Complete! Generated {len(final_code)} characters")

        except Exception as e:
            self.add_message('orchestrator', f"[ERROR] Error: {e}")
            final_code = base_code

        # Step 3: Save and prepare launch
        self.add_message('system', "**Step 3/3:** Saving generated code...")

        try:
            output_file = project_root / "generated_ui.py"
            output_file.write_text(final_code, encoding='utf-8')

            st.session_state.dashboard_code = final_code
            st.session_state.dashboard_file = str(output_file)

            self.add_message('system', f"[OK] **Saved to:** `{output_file.name}`", {
                'file_path': str(output_file),
                'file_size': len(final_code)
            })

            # Save to session
            SessionState.update_session(
                last_dashboard_file=str(output_file),
                last_generation_time=datetime.now().isoformat(),
                last_prompt=prompt
            )

            st.session_state.status = 'complete'

        except Exception as e:
            self.add_message('system', f"[ERROR] Error saving: {e}")
            st.session_state.status = 'error'

    def inject_navigation(self, base_code: str, navigation_code: str) -> str:
        """Inject navigation code into base dashboard"""
        placeholder = "# NAVIGATION_HANDLER_PLACEHOLDER"
        if placeholder in base_code:
            return base_code.replace(placeholder, navigation_code)
        return base_code + "\n\n" + navigation_code

    def launch_gradio(self):
        """Launch the generated Gradio dashboard"""
        if not st.session_state.dashboard_file:
            st.error("No dashboard file to launch!")
            return

        try:
            dashboard_file = st.session_state.dashboard_file
            process = subprocess.Popen(
                ['python', dashboard_file],
                cwd=str(project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(2)
            webbrowser.open('http://127.0.0.1:7860')
            self.add_message('system', "[OK] Dashboard launched at http://127.0.0.1:7860")
        except Exception as e:
            self.add_message('system', f"[ERROR] Error launching: {e}")

    def run(self):
        """Main render loop"""

        # Header
        st.title("[AI] AI-Powered UI Generator")
        st.markdown("**Watch as AI agents collaborate to build your interface!**")

        # Status bar
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            if st.session_state.status == 'initializing':
                st.info("[...] Loading context and preparing prompt...")
            elif st.session_state.status == 'generating':
                st.warning("[...] Agents are working on your UI...")
            elif st.session_state.status == 'complete':
                st.success("[OK] UI generation complete!")
            elif st.session_state.status == 'error':
                st.error("[X] Generation failed - check messages")

        with col2:
            if st.session_state.status == 'complete' and st.session_state.dashboard_file:
                if st.button("[>>] Launch UI", type="primary"):
                    self.launch_gradio()

        with col3:
            if st.button("[R] Regenerate"):
                st.session_state.messages = []
                st.session_state.status = 'initializing'
                st.session_state.generation_started = False
                st.session_state.auto_started = False
                st.session_state.terminal_output = []
                st.rerun()

        st.markdown("---")

        # Two-column layout: Chat and Terminal
        col_chat, col_terminal = st.columns([1, 1])

        with col_chat:
            st.subheader("[C] Agent Conversation")

            # Chat container with messages
            chat_container = st.container(height=600)
            with chat_container:
                for msg in st.session_state.messages:
                    self.render_message(msg)

        with col_terminal:
            st.subheader("[T] Terminal Output")

            # Terminal-style output with continuous updates
            terminal_container = st.container(height=600)
            with terminal_container:
                # Pull latest output from capture
                new_output = OUTPUT_CAPTURE.get_output()
                for output_type, text in new_output:
                    if text.strip():
                        st.session_state.terminal_output.append(text)

                # Display all captured output
                if st.session_state.terminal_output:
                    terminal_text = ''.join(st.session_state.terminal_output)
                    st.code(terminal_text, language='text')
                else:
                    st.code("Waiting for output...", language='text')

                # Auto-refresh during generation
                if st.session_state.status == 'generating':
                    time.sleep(0.5)
                    st.rerun()

        # AUTO-START GENERATION (only once)
        if not st.session_state.auto_started:
            st.session_state.auto_started = True

            # Load context first
            if self.load_and_start():
                st.session_state.status = 'generating'
                st.rerun()

        # Start generation if ready
        elif st.session_state.status == 'generating' and not st.session_state.generation_started:
            st.session_state.generation_started = True
            self.generate_with_capture()
            st.rerun()


# Entry point
if __name__ == "__main__":
    runner = AgentChatRunnerV2()
    runner.run()
