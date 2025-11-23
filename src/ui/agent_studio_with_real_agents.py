"""
Agent Studio - Using REAL UX Designer + Gradio Developer agents
with proper planning, CoT, and memory
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from shared_state import PipelineState
from src.agents.ui_orchestrator import UICodeOrchestrator


def main():
    st.set_page_config(
        page_title="Agent Studio (Real Agents)",
        page_icon="🎭",
        layout="wide"
    )

    st.title("🎭 Agent Studio")
    st.caption("Using UX Designer + Gradio Developer with planning, CoT, and memory")

    # Initialize session state
    if 'orchestrator' not in st.session_state:
        with st.spinner("Initializing agents..."):
            st.session_state.orchestrator = UICodeOrchestrator()
        st.success("✅ Agents initialized with planning & CoT capabilities")

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'generated_code' not in st.session_state:
        st.session_state.generated_code = None

    if 'context' not in st.session_state:
        st.session_state.context = None

    # Load pipeline context
    if not st.session_state.context:
        with st.spinner("Loading pipeline context..."):
            context = PipelineState.load_context(check_freshness=False)
            if context:
                st.session_state.context = context

                # Auto-generate initial prompt
                datasets = list(context.get('data_sources', {}).keys())
                total_records = context.get('summary', {}).get('human_readable_records', 'Unknown')
                data_sources = context.get('data_sources', {})

                status_lines = []
                for ds_name, ds_info in data_sources.items():
                    proc_state = ds_info.get('processing_state', {})
                    parsed_info = ds_info.get('parsed', {}) or ds_info.get('parsing_results', {})
                    file_count = parsed_info.get('total_files', 0)
                    record_count = parsed_info.get('total_records', parsed_info.get('total_rows', 0))

                    status_lines.append(
                        f"  - {ds_name}: {proc_state.get('download', 'unknown')} download, "
                        f"{proc_state.get('parsing', 'unknown')} parsing -> "
                        f"{file_count} files, {record_count:,} records"
                    )

                st.session_state.initial_prompt = f"""Design a pipeline monitoring dashboard that shows:

**Pipeline Status Overview:**
{chr(10).join(status_lines)}

**Requirements:**
- Show processing stage status for each dataset (download -> extract -> parse -> validate -> load)
- Display file counts, record counts, and data sizes
- Highlight any errors or warnings in the pipeline
- Show last update timestamps
- Make it easy to see what's complete vs in-progress vs failed
- Include data quality metrics where available
- Professional, clean layout - this is for monitoring ETL pipeline health

Total: {len(datasets)} datasets, {total_records} records processed"""

                st.success(f"✅ Context loaded: {len(datasets)} data sources")
            else:
                st.warning("No pipeline context found")
                st.session_state.context = {'data_sources': {}, 'summary': {}}

    # Sidebar
    with st.sidebar:
        st.header("🎨 Design Studio")

        if st.session_state.context:
            st.success(f"✅ Context: {len(st.session_state.context.get('data_sources', {}))} sources")

        st.divider()

        st.subheader("Quick Actions")
        if st.button("🚀 Start with Pipeline Dashboard"):
            if hasattr(st.session_state, 'initial_prompt'):
                st.session_state.current_request = st.session_state.initial_prompt
                st.rerun()

        if st.session_state.generated_code:
            st.divider()
            st.subheader("Generated Code")
            if st.button("💾 Save & Launch"):
                save_and_launch_code(st.session_state.generated_code)

    # Main chat interface
    st.header("💬 Chat with Agents")

    # Show agent capabilities
    with st.expander("🧠 Agent Capabilities", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **UX Designer Agent:**
            - 🧠 Chain-of-Thought reasoning
            - 📋 6-step design planning process
            - 💾 Session memory
            - 🎯 Pinecone knowledge base
            - 📝 User feedback integration
            """)
        with col2:
            st.markdown("""
            **Gradio Developer Agent:**
            - 📐 Implementation planning
            - ✅ Skills-based validation
            - 🔧 Self-correction system
            - 🚨 UX violation detection
            - 💾 Implementation memory
            """)

    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])

    # Handle user input
    if 'current_request' in st.session_state:
        user_input = st.session_state.current_request
        del st.session_state.current_request
    else:
        user_input = st.chat_input("Ask agents to design a UI...")

    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Process with agents
        with st.chat_message("assistant"):
            with st.spinner("🎨 UX Designer is analyzing requirements..."):
                status_placeholder = st.empty()
                code_placeholder = st.empty()

                try:
                    # Build requirements from user input and context
                    requirements = {
                        'screen_type': 'dashboard',
                        'intent': user_input,
                        'data_sources': st.session_state.context.get('data_sources', {}),
                    }

                    # Create output container for agent logs with REAL-TIME streaming
                    log_container = st.expander("📋 Agent Activity Log", expanded=True)
                    log_display = log_container.empty()

                    # Capture agent output with REAL-TIME streaming
                    import builtins
                    original_print = builtins.print
                    captured_logs = []

                    def streaming_print(*args, **kwargs):
                        """Print to both console AND Streamlit in real-time"""
                        text = ' '.join(str(arg) for arg in args)
                        captured_logs.append(text)

                        # Update Streamlit display immediately
                        log_display.code('\n'.join(captured_logs), language="text")

                        # Also print to console (for debugging)
                        try:
                            original_print(*args, **kwargs)
                        except UnicodeEncodeError:
                            # Handle Windows encoding issues
                            safe_text = text.encode('ascii', 'replace').decode('ascii')
                            original_print(safe_text, **kwargs)

                    # Monkey-patch print for real-time streaming
                    builtins.print = streaming_print

                    try:
                        # Call orchestrator - this triggers both agents with full CoT!
                        status_placeholder.info("🎨 UX Designer: Analyzing requirements with Chain-of-Thought...")
                        code = st.session_state.orchestrator.generate_ui_code(
                            requirements=requirements,
                            context={
                                'data_sources': st.session_state.context.get('data_sources', {}),
                                'pipeline_status': st.session_state.context.get('pipeline_status', {})
                            }
                        )
                    finally:
                        # Restore original print
                        builtins.print = original_print

                    # Store generated code
                    st.session_state.generated_code = code

                    # Show success and code in collapsible section
                    status_placeholder.success("✅ Code generated successfully!")

                    with st.expander("📄 Generated Code", expanded=False):
                        st.code(code, language="python")

                    # Add assistant message
                    response = f"✅ Generated Gradio dashboard with planning and validation!\n\n**Agent Process:**\n- UX Designer used Chain-of-Thought reasoning\n- Created design specification\n- Gradio Developer planned implementation\n- Code validated with Skills system\n- Self-corrected any UX violations\n\nCheck the 'Agent Activity Log' above to see the full planning process.\n\nClick 'Save & Launch' in sidebar to run it!"
                    st.session_state.messages.append({"role": "assistant", "content": response})

                except Exception as e:
                    status_placeholder.error(f"❌ Error: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Sorry, I encountered an error: {str(e)}"
                    })


def save_and_launch_code(code: str):
    """Save generated code and launch it"""
    import subprocess
    from pathlib import Path

    output_file = Path("generated_dashboard.py")

    # Save with UTF-8 encoding to handle any characters
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(code)

    st.success(f"✅ Saved to {output_file}")

    # Find available port
    import socket
    def find_free_port(start_port=7860):
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        return None

    port = find_free_port()
    if port:
        # Launch in background
        try:
            venv_python = Path("venv/Scripts/python.exe")
            if venv_python.exists():
                subprocess.Popen([str(venv_python), str(output_file)],
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(["python", str(output_file)],
                               creationflags=subprocess.CREATE_NEW_CONSOLE)

            st.success(f"🚀 Launching dashboard on port {port}...")
            st.info(f"Dashboard will open at: http://localhost:{port}")
            st.caption("Check your terminal for the exact URL")
        except Exception as e:
            st.error(f"Failed to launch: {e}")
            st.info(f"Launch manually with: `python {output_file}`")
    else:
        st.warning("No free ports available")
        st.info(f"Launch manually with: `python {output_file}`")


if __name__ == "__main__":
    main()
