"""
AutoGen + Streamlit with REAL Real-Time Streaming

This version actually streams agent output to Streamlit as it happens!
No waiting until the end - you see it live!
"""

import streamlit as st
import os
import json
import sys
from typing import Dict, List, Any
from pathlib import Path

# Add project root
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Standard AutoGen imports
try:
    import autogen
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
    AUTOGEN_VERSION = autogen.__version__
except ImportError as e:
    AUTOGEN_AVAILABLE = False
    AUTOGEN_ERROR = str(e)

from shared_state import PipelineState


class RealTimeStreamingGenerator:
    """
    This ACTUALLY streams to Streamlit in real-time!
    The secret: Write directly to containers during execution.
    """

    def __init__(self, chat_container, terminal_container):
        self.chat_container = chat_container
        self.terminal_container = terminal_container
        self.message_count = 0

        # Check for API keys
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.openai_key and not self.anthropic_key:
            raise ValueError("Need either OPENAI_API_KEY or ANTHROPIC_API_KEY")

        # Setup config
        self.config_list = self._get_config()

        # Create agents
        self._create_agents()

    def _get_config(self):
        """Get LLM config"""
        if self.openai_key:
            return [{
                "model": "gpt-4o",
                "api_key": self.openai_key,
            }]
        else:
            # For Claude, need litellm proxy
            return [{
                "model": "gpt-4",
                "api_base": "http://localhost:8000",
                "api_key": "dummy"
            }]

    def _create_agents(self):
        """Create the collaborative agents"""

        llm_config = {
            "config_list": self.config_list,
            "temperature": 0.7,
        }

        self.ux_designer = AssistantAgent(
            name="UX_Designer",
            llm_config=llm_config,
            system_message="""You are a Senior UX Designer specializing in Material Design 3 and data visualization.

Your responsibilities:
1. Analyze requirements and create detailed design specifications
2. Define component hierarchy and layout structure
3. Specify interaction patterns and user flows
4. Consider responsive design and accessibility

When creating designs:
- List all UI components needed
- Specify layout (tabs, columns, rows)
- Define color scheme and styling
- Describe interactions and transitions

Be specific and detailed. Your design will be implemented by the Gradio Developer."""
        )

        self.gradio_developer = AssistantAgent(
            name="Gradio_Developer",
            llm_config=llm_config,
            system_message="""You are a Gradio Framework Expert who implements UX designs into working code.

Your responsibilities:
1. Review UX designs for technical feasibility
2. Point out any Gradio limitations
3. Suggest alternatives if needed
4. Implement the agreed design in complete, working code

Known Gradio constraints:
- No nested modals
- Tab performance issues with >5 tabs
- Use gr.Accordion for many sections
- Use gr.State for navigation state
- CSS limitations

Always output COMPLETE, RUNNABLE code wrapped in ```python blocks.
When code is final, end with: COLLABORATION_COMPLETE"""
        )

        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            is_termination_msg=lambda x: "COLLABORATION_COMPLETE" in x.get("content", ""),
            code_execution_config=False
        )

    def generate(self, requirements: Dict, context: Dict) -> str:
        """
        Generate with REAL streaming to Streamlit

        The magic: We monkey-patch print to write directly to containers!
        """

        # Setup group chat
        groupchat = GroupChat(
            agents=[self.user_proxy, self.ux_designer, self.gradio_developer],
            messages=[],
            max_round=10,
            speaker_selection_method="auto"
        )

        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config={"config_list": self.config_list}
        )

        # Build initial message
        initial_message = f"""Create a UI application with these requirements:

REQUIREMENTS:
{json.dumps(requirements, indent=2)}

CONTEXT:
- Data Sources: {list(context.get('data_sources', {}).keys())}
- Total Records: {context.get('summary', {}).get('human_readable_records', 'Unknown')}

PROCESS:
1. UX_Designer: Create your design specification
2. Gradio_Developer: Review and provide feedback
3. Both: Iterate if needed
4. Gradio_Developer: Implement final code
5. End with COLLABORATION_COMPLETE

Begin with UX_Designer."""

        # THE MAGIC: Capture print and stream to Streamlit!
        original_print = print

        def stream_to_streamlit(*args, **kwargs):
            """This function streams output to Streamlit IN REAL TIME!"""
            text = ' '.join(str(arg) for arg in args)

            # Skip empty lines
            if not text.strip():
                return original_print(*args, **kwargs)

            # Parse agent output and display in Streamlit IMMEDIATELY
            if self.chat_container:
                with self.chat_container:
                    # Check for agent names
                    if "UX_Designer" in text and "to" in text:
                        self.message_count += 1
                        st.markdown(f"### 🎨 UX Designer (Message {self.message_count})")
                        st.divider()
                    elif "Gradio_Developer" in text and "to" in text:
                        self.message_count += 1
                        st.markdown(f"### ⚙️ Gradio Developer (Message {self.message_count})")
                        st.divider()
                    elif "user_proxy" in text:
                        # Skip orchestrator messages
                        pass
                    elif "----------------" in text:
                        st.divider()
                    else:
                        # Display the actual content
                        if "```" in text:
                            # Code block - show as code
                            st.text(text)
                        else:
                            # Regular text
                            st.write(text)

            # Also update terminal
            if self.terminal_container:
                with self.terminal_container:
                    short_text = text[:150] + "..." if len(text) > 150 else text
                    st.text(f"[{self.message_count}] {short_text}")

            # Still print to console
            return original_print(*args, **kwargs)

        # Apply the monkey-patch
        import builtins
        builtins.print = stream_to_streamlit

        try:
            # Start the chat - THIS WILL STREAM IN REAL TIME!
            st.info("🚀 Starting agent collaboration...")
            self.user_proxy.initiate_chat(manager, message=initial_message)
            st.success("✅ Collaboration complete!")
        finally:
            # Restore original print
            builtins.print = original_print

        # Extract the generated code
        return self._extract_code(groupchat.messages)

    def _extract_code(self, messages: List[Dict]) -> str:
        """Extract the final code from agent messages"""
        import re

        for message in reversed(messages):
            if message.get("name") == "Gradio_Developer":
                content = message.get("content", "")
                code_blocks = re.findall(r"```python\n(.*?)\n```", content, re.DOTALL)
                if code_blocks:
                    return code_blocks[-1]

        return "# No code generated"


def main():
    st.set_page_config(
        page_title="Real-Time Agent Collaboration",
        page_icon="🤖",
        layout="wide"
    )

    st.title("🤖 Real-Time Agent Collaboration")
    st.markdown("**Watch agents collaborate in real-time - no waiting!**")

    # Check AutoGen
    if not AUTOGEN_AVAILABLE:
        st.error(f"""
        AutoGen not installed! Error: {AUTOGEN_ERROR}

        Install: `pip install pyautogen<0.3`
        """)
        st.stop()

    st.success(f"✅ AutoGen {AUTOGEN_VERSION} ready")

    # Initialize session state
    if 'context' not in st.session_state:
        st.session_state.context = None
    if 'generated_code' not in st.session_state:
        st.session_state.generated_code = None
    if 'status' not in st.session_state:
        st.session_state.status = 'ready'

    # Load context
    if not st.session_state.context:
        with st.spinner("Loading context..."):
            context = PipelineState.load_context(check_freshness=False)
            if context:
                st.session_state.context = context
                datasets = list(context.get('data_sources', {}).keys())
                st.success(f"✅ Loaded {len(datasets)} data sources")
            else:
                st.error("No context found. Run pipeline first!")
                st.stop()

    # Controls
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💬 Start Generation", type="primary", disabled=st.session_state.status == 'generating'):
            st.session_state.status = 'generating'
            st.rerun()

    with col2:
        if st.session_state.generated_code:
            if st.button("💾 Save Code"):
                path = Path("generated_ui.py")
                path.write_text(st.session_state.generated_code)
                st.success(f"Saved to {path}")

    with col3:
        if st.button("🔄 Reset"):
            st.session_state.status = 'ready'
            st.session_state.generated_code = None
            st.rerun()

    st.divider()

    # Create display areas
    col_chat, col_terminal = st.columns([2, 1])

    with col_chat:
        st.subheader("💬 Agent Conversation")
        chat_container = st.container(height=600)

    with col_terminal:
        st.subheader("📟 Terminal")
        terminal_container = st.container(height=600)

    # Generate if requested
    if st.session_state.status == 'generating':
        try:
            # Create generator with containers
            generator = RealTimeStreamingGenerator(chat_container, terminal_container)

            # Build requirements
            datasets = list(st.session_state.context.get('data_sources', {}).keys())
            requirements = {
                'screen_type': 'dashboard',
                'intent': f"Monitor {', '.join(datasets)} data",
                'data_sources': st.session_state.context.get('data_sources', {})
            }

            # Generate - THIS WILL STREAM IN REAL TIME!
            code = generator.generate(requirements, st.session_state.context)

            # Save result
            st.session_state.generated_code = code
            st.session_state.status = 'complete'

            # Save to file
            output_path = Path("generated_ui.py")
            output_path.write_text(code)
            st.success(f"💾 Saved to {output_path}")

            # Show code
            with st.expander("📝 Generated Code", expanded=True):
                st.code(code, language='python')

            # Auto-launch Gradio UI
            st.info("🚀 Launching Gradio UI in background...")
            import subprocess
            gradio_process = subprocess.Popen(
                [sys.executable, str(output_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            st.success("✅ Gradio UI launched! Check http://localhost:7860")

        except Exception as e:
            st.error(f"Error: {e}")
            st.session_state.status = 'ready'


if __name__ == "__main__":
    main()
