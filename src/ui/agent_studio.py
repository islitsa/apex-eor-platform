"""
Agent Studio - UI Generation with Material Design 3

Your agents are GENERIC UI/UX agents with Material Design 3 expertise.
The domain context (petroleum, EOR, etc.) comes from the data, not the agents.

This uses:
1. UICodeOrchestrator (generic UI coordination)
2. UXDesignerAgent (M3 design patterns from Pinecone)
3. ReactDeveloperAgent (React + TypeScript expertise)
"""

import streamlit as st
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

# Add project root
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Your GENERIC UI agents
from src.agents.ui_orchestrator import UICodeOrchestrator
from src.agents.ux_designer import UXDesignerAgent, DesignSpec
from src.agents.react_developer import ReactDeveloperAgent

from src.shared_state import PipelineState, FavoritesManager


class AgentStudio:
    """
    Agent Studio for UI generation with Material Design 3

    Uses:
    - UICodeOrchestrator (coordinates the generation process)
    - UXDesignerAgent (M3 design patterns from Pinecone)
    - ReactDeveloperAgent (React + TypeScript implementation)
    - UniversalTraceCollector (captures agent reasoning)
    - Real-time streaming to UI
    """

    def __init__(self, enable_gradient=False):
        # Initialize trace collector
        from src.ui.trace_collector import UniversalTraceCollector
        self.trace_collector = UniversalTraceCollector()

        # Initialize YOUR generic UI orchestrator WITH trace collector
        st.info("Initializing UI Agent System with Material Design 3 knowledge...")
        self.orchestrator = UICodeOrchestrator(
            trace_collector=self.trace_collector,
            enable_gradient=enable_gradient
        )

        # Store current work for iteration
        self.current_design_spec = None
        self.current_code = None
        self.iteration_count = 0

        # Save original print
        import builtins
        self.original_print = builtins.print

    def generate_ui(self, requirements: str, context: Dict, stream_container=None, trace_container=None) -> Dict:
        """
        Use YOUR ACTUAL AGENTS to generate UI code

        Args:
            requirements: User requirements
            context: Pipeline context
            stream_container: Container for agent chatter streaming
            trace_container: Container for live trace streaming (debug mode)
        """

        # Clear previous traces for new generation
        self.trace_collector.clear()

        # Set trace streaming container for live updates
        self.trace_collector.stream_container = trace_container

        if stream_container:
            with stream_container:
                st.markdown("### 🚀 Starting UI Generation")
                st.info("Using Material Design 3 patterns from Pinecone...")
        
        # Capture orchestrator output
        captured = []
        
        def capture_orchestrator_output(*args, **kwargs):
            text = ' '.join(str(a) for a in args)
            captured.append(text)
            
            if stream_container and text.strip():
                with stream_container:
                    # Stream orchestrator phases
                    if "KNOWLEDGE RETRIEVAL" in text:
                        st.markdown("#### 📚 Phase 1: Retrieving M3 Patterns from Pinecone")
                    elif "UX DESIGN" in text:
                        st.markdown("#### 🎨 Phase 2: Creating Design Specification")
                    elif "REACT IMPLEMENTATION" in text:
                        st.markdown("#### ⚙️ Phase 3: Implementing with React + TypeScript")
                    elif "TOKEN USAGE" in text:
                        st.success(text)
                    elif "[KB]" in text:
                        st.caption(text)  # Knowledge base queries
                    elif "[Orchestrator]" in text:
                        st.write(text)
                    elif "[UX Designer]" in text or "[React Developer]" in text or "[Protocol]" in text:
                        st.write(text)  # Protocol layer trace messages
                    elif "Retrieved" in text and "items" in text:
                        st.info(text)
            
            # Still print to console (with Unicode error handling for Windows)
            try:
                self.original_print(*args, **kwargs)
            except UnicodeEncodeError:
                # Fallback: replace Unicode with ASCII
                safe_args = []
                for arg in args:
                    if isinstance(arg, str):
                        safe_args.append(arg.encode('ascii', 'replace').decode('ascii'))
                    else:
                        safe_args.append(arg)
                self.original_print(*safe_args, **kwargs)
        
        # Monkey-patch for streaming
        import builtins
        builtins.print = capture_orchestrator_output
        
        try:
            # Convert to requirements format
            req_dict = {
                'screen_type': self._detect_screen_type(requirements),
                'intent': requirements,
                'user_goals': self._extract_goals(requirements),
                'data_sources': context.get('data_sources', {})  # CRITICAL: Pass discovered sources!
            }

            # Add iteration feedback if this is an update
            if self.current_code and self.iteration_count > 0:
                req_dict['user_feedback'] = requirements

            # USE YOUR ACTUAL ORCHESTRATOR!
            code = self.orchestrator.generate_ui_code(req_dict, context)
            
            # Store for iteration
            self.current_code = code
            self.iteration_count += 1
            
            # Get the design spec if available
            design_spec = getattr(self.orchestrator.ux_designer, 'last_design_spec', None)
            self.current_design_spec = design_spec
            
            if stream_container:
                with stream_container:
                    st.success(f"✅ Generation complete! (Iteration {self.iteration_count})")
            
        finally:
            # Restore print
            builtins.print = self.original_print
        
        # Get traces from trace collector
        traces = self.trace_collector.traces.copy()  # Copy to preserve snapshot
        reasoning_traces = self.trace_collector.get_reasoning_traces()

        return {
            'code': code,
            'design_spec': design_spec,
            'captured_output': captured,
            'iteration': self.iteration_count,
            'traces': traces,
            'reasoning_traces': reasoning_traces,
            'trace_collector': self.trace_collector  # Add trace_collector for chat feature
        }
    
    
    def _detect_screen_type(self, requirements: str) -> str:
        """Detect screen type from requirements"""
        req_lower = requirements.lower()
        if 'dashboard' in req_lower:
            return 'dashboard'
        elif 'form' in req_lower:
            return 'form'
        elif 'report' in req_lower:
            return 'report'
        else:
            return 'dashboard'  # default
    
    def _extract_goals(self, requirements: str) -> List[str]:
        """Extract user goals from requirements"""
        goals = []
        req_lower = requirements.lower()
        
        if 'monitor' in req_lower or 'view' in req_lower:
            goals.append('view data')
        if 'filter' in req_lower or 'search' in req_lower:
            goals.append('filter data')
        if 'export' in req_lower:
            goals.append('export data')
        if 'drill' in req_lower or 'detail' in req_lower:
            goals.append('drill down')
        
        return goals if goals else ['view data', 'interact with data']


def main():
    st.set_page_config(
        page_title="Hybrid Agent Studio",
        page_icon="🎭",
        layout="wide"
    )
    
    st.title("🎭 Agent Studio")
    st.markdown("**Material Design 3 UI Generation with Pinecone Knowledge**")

    # Initialize
    if 'enable_gradient' not in st.session_state:
        st.session_state.enable_gradient = False  # Default gradient setting
    if 'studio' not in st.session_state:
        st.session_state.studio = AgentStudio(enable_gradient=st.session_state.enable_gradient)
    if 'context' not in st.session_state:
        st.session_state.context = None
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'current_code' not in st.session_state:
        st.session_state.current_code = None
    
    # Load context
    if not st.session_state.context:
        context = PipelineState.load_context(check_freshness=False)
        if context:
            st.session_state.context = context
            st.success(f"✅ Context loaded: {len(context.get('data_sources', {}))} data sources")
        else:
            st.session_state.context = {'data_sources': {}, 'summary': {}}

    # Get initial prompt from pipeline context (generated by pipeline)
    if 'initial_prompt' not in st.session_state:
        # Use prompt from pipeline if available, otherwise create a default
        st.session_state.initial_prompt = st.session_state.context.get(
            'initial_prompt',
            f"Create a dashboard for {len(st.session_state.context.get('data_sources', {}))} data sources"
        )
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Actions")

        # Debug mode selector
        if 'debug_mode' not in st.session_state:
            st.session_state.debug_mode = True  # Default to debug mode

        debug_mode = st.toggle("🐛 Debug Mode (Live Traces)", value=st.session_state.debug_mode)
        if debug_mode != st.session_state.debug_mode:
            st.session_state.debug_mode = debug_mode
            st.rerun()

        # Gradient enhancement toggle
        if 'enable_gradient' not in st.session_state:
            st.session_state.enable_gradient = False  # Default to disabled

        enable_gradient = st.toggle(
            "🎯 Gradient Enhancement (Phase 1)",
            value=st.session_state.enable_gradient,
            help="Enable domain-aware pattern boosting for petroleum engineering contexts"
        )
        if enable_gradient != st.session_state.enable_gradient:
            st.session_state.enable_gradient = enable_gradient
            # Reinitialize studio with new gradient setting
            st.session_state.studio = AgentStudio(enable_gradient=enable_gradient)
            st.info(f"Gradient enhancement {'enabled' if enable_gradient else 'disabled'}")
            st.rerun()

        if debug_mode:
            st.caption("Shows live agent traces during execution")
        else:
            st.caption("Production mode - clean UI only")

        st.divider()

        if st.button("🎨 Generate Initial UI", type="primary", use_container_width=True):
            # Use the prompt generated by the pipeline
            requirements = st.session_state.initial_prompt
            st.session_state.history.append({'type': 'generate', 'content': requirements})
            st.rerun()

        if st.session_state.current_code:
            if st.button("🔧 Request Changes", use_container_width=True):
                feedback = "Make the cards bigger and add more spacing between sections"
                st.session_state.history.append({'type': 'generate', 'content': feedback})
                st.rerun()

        # Save buttons
        if st.session_state.history:
            st.divider()

            # Save Chat History button
            if st.button("💾 Save Chat History", use_container_width=True):
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                chat_file = project_root / f"agent_chat_{timestamp}.txt"

                # Format chat history with full conversation
                chat_content = ["=== Agent Studio Chat History ===\n"]
                chat_content.append(f"Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                chat_content.append("=" * 70 + "\n\n")

                for i, item in enumerate(st.session_state.history, 1):
                    # User prompt
                    chat_content.append(f"[{i}] USER REQUEST:\n")
                    chat_content.append(f"{item['content']}\n")
                    chat_content.append("-" * 70 + "\n\n")

                    # Agent response (if processed)
                    if item.get('processed'):
                        # Show orchestrator output
                        captured_output = item.get('captured_output', [])
                        if captured_output:
                            chat_content.append(f"[{i}] AGENT RESPONSE:\n")
                            for line in captured_output:
                                chat_content.append(f"{line}\n")
                            chat_content.append("\n")

                        # Show generated code preview
                        chat_content.append(f"[{i}] GENERATED CODE:\n")
                        chat_content.append("✅ UI code generated successfully\n")
                        chat_content.append(f"(Full code saved separately in generated_ui.py)\n")
                        chat_content.append("\n")

                        chat_content.append("=" * 70 + "\n\n")

                chat_file.write_text(''.join(chat_content), encoding='utf-8')
                st.success(f"Saved!")
                st.code(str(chat_file), language="text")

            # Save Agent Traces button
            if st.button("🐛 Save Agent Traces", use_container_width=True):
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                trace_file = project_root / f"agent_traces_{timestamp}.txt"

                # Get all traces from trace collector
                traces = st.session_state.studio.trace_collector.traces

                if not traces:
                    st.warning("No traces available to save")
                else:
                    # Format traces
                    trace_content = ["=== Agent Studio Execution Traces ===\n"]
                    trace_content.append(f"Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    trace_content.append(f"Total traces: {len(traces)}\n")
                    trace_content.append("=" * 70 + "\n\n")

                    for i, trace in enumerate(traces, 1):
                        trace_content.append(f"[{i}] {trace.trace_type.value.upper()}\n")
                        trace_content.append(f"Agent: {trace.agent}\n")
                        trace_content.append(f"Method: {trace.method}\n")
                        trace_content.append(f"Time: {trace.timestamp}\n")

                        if trace.reasoning:
                            trace_content.append(f"\nReasoning:\n{trace.reasoning}\n")

                        if trace.knowledge_used:
                            trace_content.append(f"\nKnowledge Used: {', '.join(trace.knowledge_used)}\n")

                        if trace.data:
                            trace_content.append(f"\nData: {trace.data}\n")

                        trace_content.append("-" * 70 + "\n\n")

                    trace_file.write_text(''.join(trace_content), encoding='utf-8')
                    st.success(f"Saved {len(traces)} traces!")
                    st.code(str(trace_file), language="text")

        st.markdown("### 📚 Your Agents")
        st.info("""
        **UICodeOrchestrator**
        Coordinates the design process

        **UXDesignerAgent**
        Creates M3 design specs

        **GradioImplementationAgent**
        Implements in Gradio

        **Pinecone Knowledge**
        Material Design 3 patterns
        """)
    
    # Main area - Split based on debug mode
    if st.session_state.debug_mode:
        # DEBUG MODE: 3 columns - Session | Traces | Code
        session_col, trace_col, code_col = st.columns([1, 1, 1])
    else:
        # PRODUCTION MODE: 2 columns - Session | Code
        session_col, code_col = st.columns([1, 1])

    with session_col:
        st.markdown("### 💬 Studio Session")
        chat_container = st.container(height=600)

        # Display all history (even if processed)
        for item in st.session_state.history:
            with chat_container:
                st.info(f"You: {item['content']}")

            # If not yet processed, generate the UI
            if not item.get('processed'):
                # In debug mode, create trace container
                if st.session_state.debug_mode and 'trace_col' in locals():
                    trace_container = trace_col.container(height=600)
                    trace_container.markdown("### 🐛 Live Agent Traces")
                else:
                    trace_container = None

                response_container = chat_container.container()

                # Use YOUR agents to generate UI - pass trace container for live updates
                result = st.session_state.studio.generate_ui(
                    item['content'],
                    st.session_state.context,
                    response_container,
                    trace_container  # NEW: pass trace container for live streaming
                )
                st.session_state.current_code = result['code']

                # Store all result data with this history item
                item['traces'] = result.get('traces', [])
                item['reasoning_traces'] = result.get('reasoning_traces', [])
                item['captured_output'] = result.get('captured_output', [])
                item['design_spec'] = result.get('design_spec')
                item['trace_collector'] = result.get('trace_collector')  # Store trace_collector reference

                item['processed'] = True
                st.rerun()  # Rerun to properly render buttons in next cycle
            else:
                # Already processed - show completion message
                with chat_container:
                    st.success("✅ Generated")

                # In debug mode, re-display traces for this processed item
                if st.session_state.debug_mode and 'trace_col' in locals():
                    reasoning_traces = item.get('reasoning_traces', [])
                    if reasoning_traces:
                        # Create trace display in the trace column
                        with trace_col:
                            for trace in reasoning_traces:
                                st.markdown(f"**🧠 {trace.agent}** - {trace.method}")
                                # Show full reasoning in expandable text area
                                with st.expander("View Full Reasoning", expanded=False):
                                    st.text_area(
                                        "Reasoning",
                                        trace.reasoning,
                                        height=400,
                                        disabled=True,
                                        label_visibility="collapsed",
                                        key=f"trace_{trace.timestamp}_{id(trace)}"  # Unique key for each trace
                                    )
                                if trace.knowledge_used:
                                    st.caption(f"📚 Knowledge: {', '.join(trace.knowledge_used[:3])}")
                                st.divider()

        # Input
        user_input = st.chat_input("Request UI changes or new generation...")
        if user_input:
            st.session_state.history.append({
                'type': 'generate',
                'content': user_input,
                'processed': False
            })
            st.rerun()
    
    with code_col:
        st.markdown("### 📄 Generated Code")
        if st.session_state.current_code:
            # Handle React files (dictionary) vs old Gradio code (string)
            if isinstance(st.session_state.current_code, dict):
                # Show React files
                st.info(f"✨ Generated {len(st.session_state.current_code)} React + TypeScript files")

                # Show file tree
                for filename in sorted(st.session_state.current_code.keys()):
                    with st.expander(f"📄 {filename}"):
                        file_content = st.session_state.current_code[filename]
                        # Determine language for syntax highlighting
                        if filename.endswith('.tsx') or filename.endswith('.ts'):
                            lang = 'typescript'
                        elif filename.endswith('.json'):
                            lang = 'json'
                        elif filename.endswith('.css'):
                            lang = 'css'
                        elif filename.endswith('.js'):
                            lang = 'javascript'
                        elif filename.endswith('.html'):
                            lang = 'html'
                        else:
                            lang = 'text'

                        preview = file_content[:300] + "..." if len(file_content) > 300 else file_content
                        st.code(preview, language=lang)
            else:
                # Old Gradio code (string)
                st.code(st.session_state.current_code[:500] + "..." if len(st.session_state.current_code) > 500 else st.session_state.current_code, language="python")

            # Optional: Show advanced save button for users who want to save without launching
            show_save_button = st.checkbox("Show advanced Save button", value=False, key="show_save_checkbox",
                                          help="Enable this to save files without launching the dashboard")

            if show_save_button:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save", key="save_code_btn", use_container_width=True):
                        # Handle React files
                        if isinstance(st.session_state.current_code, dict):
                            output_dir = project_root / "generated_react_dashboard"
                            output_dir.mkdir(parents=True, exist_ok=True)

                            # Save all React files
                            from src.agents.react_developer import ReactDeveloperAgent
                            react_agent = ReactDeveloperAgent()
                            react_agent.save_files(st.session_state.current_code, output_dir)

                            st.success(f"Saved {len(st.session_state.current_code)} files to generated_react_dashboard/")
                        else:
                            # Old Gradio code
                            Path("generated_ui.py").write_text(st.session_state.current_code, encoding='utf-8')
                            st.success("Saved!")
                        st.rerun()
                with col2:
                    launch_button = st.button("🚀 Launch", key="launch_code_btn", use_container_width=True)
            else:
                # Single launch button that auto-saves
                launch_button = st.button("🚀 Launch Dashboard (auto-saves)", key="launch_code_btn", use_container_width=True)

            if launch_button:
                # Handle React vs Gradio
                if isinstance(st.session_state.current_code, dict):
                    # React project
                    output_dir = project_root / "generated_react_dashboard"
                    output_dir.mkdir(parents=True, exist_ok=True)

                    # Save all React files first
                    from src.agents.react_developer import ReactDeveloperAgent
                    react_agent = ReactDeveloperAgent()
                    react_agent.save_files(st.session_state.current_code, output_dir)

                    # Launch React dev server
                    import subprocess
                    import webbrowser
                    import time
                    import json
                    try:
                        print(f"[DEBUG Launch React] Starting React dev server...")

                        # Read port from vite.config.ts if it exists
                        dev_port = 3000  # Default port for generated dashboards
                        vite_config_path = output_dir / "vite.config.ts"
                        if vite_config_path.exists():
                            try:
                                config_content = vite_config_path.read_text()
                                # Simple regex to extract port from vite config
                                import re
                                port_match = re.search(r'port:\s*(\d+)', config_content)
                                if port_match:
                                    dev_port = int(port_match.group(1))
                                    print(f"[DEBUG Launch React] Found port {dev_port} in vite.config.ts")
                            except Exception as e:
                                print(f"[DEBUG Launch React] Could not read vite.config.ts, using default port 3000: {e}")

                        npm_command = ["npm", "run", "dev"]

                        print(f"[DEBUG Launch React] Using Vite on port {dev_port}")
                        print(f"[DEBUG Launch React] Using command: {' '.join(npm_command)}")

                        # Start dev server in background
                        react_process = subprocess.Popen(
                            npm_command,
                            cwd=str(output_dir),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            bufsize=0,
                            shell=True  # Need shell=True on Windows for npm
                        )

                        # Store process
                        if 'react_processes' not in st.session_state:
                            st.session_state.react_processes = []
                        st.session_state.react_processes.append(react_process)

                        # Give React a moment to start, then open browser
                        time.sleep(3)
                        webbrowser.open(f'http://localhost:{dev_port}')

                        st.session_state.launch_message = f"success_port_{dev_port}"
                        st.rerun()
                    except Exception as e:
                        print(f"[DEBUG Launch React] Exception: {e}")
                        st.session_state.launch_message = f"error: {e}"
                        st.rerun()
                else:
                    # Old Gradio launch code
                    # Debug: Check what we're about to write
                    print(f"[DEBUG Launch] Code length: {len(st.session_state.current_code)}")
                    print(f"[DEBUG Launch] First 200 chars: {st.session_state.current_code[:200]}")
                    print(f"[DEBUG Launch] Has imports? {'import gradio' in st.session_state.current_code}")
                    print(f"[DEBUG Launch] Has launch? {'.launch()' in st.session_state.current_code}")

                    # Save to project root
                    output_path = project_root / "generated_ui.py"
                    output_path.write_text(st.session_state.current_code, encoding='utf-8')
                    print(f"[DEBUG Launch] Saved to: {output_path}")
                    print(f"[DEBUG Launch] File exists: {output_path.exists()}")
                    print(f"[DEBUG Launch] File size: {output_path.stat().st_size} bytes")

                    # Find venv python
                    venv_python = project_root / "venv" / "Scripts" / "python.exe"
                    python_exe = str(venv_python) if venv_python.exists() else sys.executable
                    print(f"[DEBUG Launch] Python: {python_exe}")

                    # Launch Gradio app in background
                    import subprocess
                    import webbrowser
                    import time
                    import re
                    try:
                        print(f"[DEBUG Launch] Starting subprocess...")
                        # Start Gradio in background - capture output to detect port
                        # Set PYTHONUNBUFFERED to get immediate output
                        import os as os_module
                        env = os_module.environ.copy()
                        env['PYTHONUNBUFFERED'] = '1'

                        gradio_process = subprocess.Popen(
                            [python_exe, "-u", str(output_path)],  # -u for unbuffered
                            cwd=str(project_root),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,  # Merge stderr into stdout
                            text=True,
                            bufsize=0,  # Unbuffered
                            env=env
                        )
                        print(f"[DEBUG Launch] Process started with PID: {gradio_process.pid}")

                        # Store process in session state list
                        if 'gradio_processes' not in st.session_state:
                            st.session_state.gradio_processes = []
                        st.session_state.gradio_processes.append(gradio_process)

                        # Wait for Gradio to start and capture the port from output
                        port = 7860  # Default fallback
                        timeout = 10  # seconds
                        start_time = time.time()

                        while time.time() - start_time < timeout:
                            line = gradio_process.stdout.readline()
                            if line:
                                print(f"[DEBUG Launch] stdout: {line.strip()}")
                                # Look for "Running on local URL:  http://127.0.0.1:XXXX"
                                match = re.search(r'http://(?:127\.0\.0\.1|localhost):(\d+)', line)
                                if match:
                                    port = match.group(1)
                                    print(f"[DEBUG Launch] Found port: {port}")
                                    break
                            if gradio_process.poll() is not None:
                                # Process terminated
                                returncode = gradio_process.returncode
                                # Read remaining output
                                remaining_output = gradio_process.stdout.read()
                                print(f"[DEBUG Launch] Process terminated early! Return code: {returncode}")
                                print(f"[DEBUG Launch] Remaining output: {remaining_output}")
                                st.session_state.launch_message = f"error: Process failed with code {returncode}: {remaining_output[:200]}"
                                st.rerun()
                                return
                            time.sleep(0.1)

                        print(f"[DEBUG Launch] Opening browser on port {port}")
                        # Open browser with actual port
                        webbrowser.open(f'http://localhost:{port}')

                        # Store success message in session state and rerun to show it
                        st.session_state.launch_message = f"success_port_{port}"
                        print(f"[DEBUG Launch] Success! Rerunning...")
                        st.rerun()
                    except Exception as e:
                        print(f"[DEBUG Launch] Exception: {e}")
                        import traceback
                        traceback.print_exc()
                        st.session_state.launch_message = f"error: {e}"
                        st.rerun()

            # Display launch status (persists across reruns)
            if 'launch_message' in st.session_state:
                if st.session_state.launch_message.startswith("success"):
                    # Extract port from message if available
                    if "_port_" in st.session_state.launch_message:
                        port = st.session_state.launch_message.split("_port_")[1]
                        st.success("🚀 Launched! Opening in new browser tab...")
                        st.info(f"Dashboard running on http://localhost:{port}")
                    else:
                        st.success("🚀 Launched! Opening in new browser tab...")
                        st.info("Dashboard running on http://localhost:7860")
                else:
                    error = st.session_state.launch_message.replace("error: ", "")
                    st.error(f"Launch failed: {error}")
                    venv_python = project_root / "venv" / "Scripts" / "python.exe"
                    python_exe = str(venv_python) if venv_python.exists() else sys.executable
                    st.info(f"Try manually: `{python_exe} generated_ui.py`")

            # Favorites Section
            st.markdown("---")
            st.markdown("### ⭐ Favorites")

            # Load favorites list
            favorites_list = FavoritesManager.list_favorites()

            col1, col2 = st.columns([2, 1])

            with col1:
                # Save current code as favorite
                favorite_name = st.text_input(
                    "Save current UI as favorite:",
                    key="favorite_name_input",
                    placeholder="E.g., 'Pipeline Dashboard v1'"
                )

                if st.button("⭐ Save as Favorite", key="save_favorite_btn", disabled=not favorite_name):
                    # Get the original prompt from history
                    current_prompt = ""
                    if st.session_state.history:
                        # Find the most recent user message
                        for msg in reversed(st.session_state.history):
                            if msg.get('role') == 'user':
                                current_prompt = msg.get('content', '')
                                break

                    # Save favorite
                    if FavoritesManager.save_favorite(
                        name=favorite_name,
                        code=st.session_state.current_code,
                        prompt=current_prompt
                    ):
                        st.success(f"✅ Saved '{favorite_name}' to favorites!")
                        st.rerun()
                    else:
                        st.error("Failed to save favorite")

            with col2:
                # Load from favorites
                if favorites_list:
                    selected_favorite = st.selectbox(
                        "Load favorite:",
                        options=["-- Select --"] + favorites_list,
                        key="favorite_selector"
                    )

                    if st.button("📥 Load Favorite", key="load_favorite_btn", disabled=(selected_favorite == "-- Select --")):
                        favorite_data = FavoritesManager.get_favorite(selected_favorite)
                        if favorite_data:
                            # Load code into current session
                            st.session_state.current_code = favorite_data['code']

                            # Add to history
                            st.session_state.history.append({
                                'role': 'user',
                                'content': f"Loaded favorite: {selected_favorite}",
                                'timestamp': datetime.now().isoformat()
                            })
                            st.session_state.history.append({
                                'role': 'assistant',
                                'content': f"Loaded favorite '{selected_favorite}' ({favorite_data['code_length']} chars)\n\nOriginal prompt: {favorite_data.get('prompt', 'N/A')}",
                                'code': favorite_data['code'],
                                'timestamp': datetime.now().isoformat()
                            })

                            st.success(f"✅ Loaded '{selected_favorite}'!")
                            st.rerun()
                        else:
                            st.error("Failed to load favorite")

                    # Delete favorite button
                    if selected_favorite != "-- Select --":
                        if st.button("🗑️ Delete", key="delete_favorite_btn"):
                            if FavoritesManager.delete_favorite(selected_favorite):
                                st.success(f"Deleted '{selected_favorite}'")
                                st.rerun()
                            else:
                                st.error("Failed to delete favorite")
                else:
                    st.info("No favorites saved yet")

            # Chat with Agents Section (0 tokens - searches traces)
            st.markdown("---")
            with st.expander("💬 Chat with Agents", expanded=False):
                st.markdown("Ask questions about design decisions. Answers come from captured traces (0 tokens).")

                # Get trace_collector once at the start (fix for UnboundLocalError)
                trace_collector = item.get('trace_collector')

                col1, col2 = st.columns([3, 1])

                with col1:
                    user_question = st.text_input(
                        "Ask about design decisions:",
                        key="agent_question_input",
                        placeholder="E.g., Why did you choose this layout?"
                    )

                with col2:
                    st.markdown("#### Quick Questions")
                    if st.button("Why this layout?", key="quick_q1"):
                        user_question = "Why did you choose this layout pattern?"
                        st.session_state.agent_question_input = user_question
                    if st.button("Why cards?", key="quick_q2"):
                        user_question = "Why cards instead of a table?"
                        st.session_state.agent_question_input = user_question
                    if st.button("What patterns used?", key="quick_q3"):
                        user_question = "What design patterns were used?"
                        st.session_state.agent_question_input = user_question

                if user_question or st.session_state.get('agent_question_input'):
                    question_to_ask = user_question or st.session_state.agent_question_input

                    # Search traces for answers (0 tokens!)
                    if trace_collector:
                        answers = trace_collector.ask_question(question_to_ask)

                        if answers:
                            st.markdown(f"**Question:** {question_to_ask}")
                            st.markdown("---")

                            for agent, answer in answers.items():
                                with st.chat_message("assistant"):
                                    st.markdown(f"**{agent}:**")
                                    st.text_area(
                                        "Response",
                                        value=answer,
                                        height=200,
                                        disabled=True,
                                        label_visibility="collapsed",
                                        key=f"answer_{agent}"
                                    )
                        else:
                            st.info("No relevant information found in traces. Try a different question or generate a UI first.")
                    else:
                        st.warning("No trace data available. Generate a UI first to capture agent decisions.")

                # Show available design patterns
                if trace_collector:
                    patterns_used = trace_collector.get_design_patterns_used()
                    if patterns_used:
                        st.markdown("---")
                        st.markdown("**Design Patterns Used:**")
                        st.markdown(", ".join(patterns_used[:10]))

            # Design Change Request Section (0 tokens for template swaps)
            st.markdown("---")
            with st.expander("🔧 Request Design Changes", expanded=False):
                st.markdown("Request changes that swap templates (0 tokens) or refine design (minimal tokens).")

                change_type = st.selectbox(
                    "What would you like to change?",
                    [
                        "-- Select a change --",
                        "Make cards bigger",
                        "Switch to table view",
                        "Make more compact",
                        "Add dark theme support",
                        "Increase spacing",
                        "Custom request..."
                    ],
                    key="design_change_selector"
                )

                custom_request = None
                if change_type == "Custom request...":
                    custom_request = st.text_area(
                        "Describe your change:",
                        placeholder="E.g., Add a search box at the top",
                        key="custom_change_request"
                    )

                if st.button("Apply Change", key="apply_change_btn", disabled=(change_type == "-- Select a change --")):
                    with st.spinner("Applying change..."):
                        current_code = st.session_state.current_code

                        # Template swapping (0 tokens)
                        if change_type == "Make cards bigger":
                            # Simple string replacement to swap templates
                            if "status_card_compact" in current_code:
                                new_code = current_code.replace("status_card_compact", "status_card_large")
                                st.session_state.current_code = new_code
                                st.success("Changed to larger cards! (0 tokens)")
                                st.rerun()
                            else:
                                st.info("No compact cards found to enlarge.")

                        elif change_type == "Switch to table view":
                            st.info("Table view swap not yet implemented. This would swap the component template.")

                        elif change_type == "Make more compact":
                            if "scale=" in current_code:
                                # Reduce scale values
                                new_code = current_code.replace("scale=4", "scale=3").replace("scale=2", "scale=1")
                                st.session_state.current_code = new_code
                                st.success("Made layout more compact! (0 tokens)")
                                st.rerun()
                            else:
                                st.info("No scale parameters found to adjust.")

                        elif change_type == "Custom request...":
                            if custom_request:
                                st.warning("Custom changes require LLM generation. This feature preserves architecture by using minimal prompts.")
                                # Could implement minimal LLM call here if needed
                            else:
                                st.error("Please describe your custom change.")

                        else:
                            st.info(f"Change '{change_type}' not yet implemented.")

        else:
            st.info("No code generated yet. Click 'Generate Initial UI' to start!")


if __name__ == "__main__":
    main()