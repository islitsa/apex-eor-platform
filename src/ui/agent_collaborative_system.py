"""
FIXED AutoGen Agent Collaboration System

Uses standard AutoGen (pyautogen) without async complexity.
This WILL work with Streamlit!
"""

import streamlit as st
import os
import json
import threading
import time
from typing import Dict, List, Any
from pathlib import Path
import sys

# Add project root
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load .env file for API keys
from dotenv import load_dotenv
load_dotenv()

# STANDARD AutoGen imports (not the new v0.10+ structure)
try:
    import autogen
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
    AUTOGEN_VERSION = autogen.__version__
except ImportError as e:
    AUTOGEN_AVAILABLE = False
    AUTOGEN_ERROR = str(e)

from shared_state import PipelineState


class CollaborativeUIGenerator:
    """
    Agent system using STANDARD AutoGen - no async needed!
    """

    def __init__(self, chat_container, terminal_container):
        self.chat_container = chat_container
        self.terminal_container = terminal_container

        # Try OpenAI first (AutoGen's native support), fallback to Claude
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.openai_key and not self.anthropic_key:
            raise ValueError("Neither OPENAI_API_KEY nor ANTHROPIC_API_KEY is set")

        # Create config
        self.config_list = self._get_llm_config()

        # Create agents
        self._create_collaborative_agents()

    def _get_llm_config(self):
        """
        Get LLM config for AutoGen - use OpenAI if available
        """
        if self.openai_key:
            # Use GPT-4o (latest and most capable model)
            st.info("Using OpenAI GPT-4o for agent collaboration")
            config = [{
                "model": "gpt-4o",  # Latest and best OpenAI model
                "api_key": self.openai_key,
            }]
        else:
            # Fallback to Claude (requires litellm bridge - not implemented yet)
            st.warning("OpenAI key not found, Claude support incomplete")
            config = [{
                "model": "gpt-4o",
                "api_key": "sk-placeholder"
            }]

        return config

    def _create_collaborative_agents(self):
        """Create agents using STANDARD AutoGen API"""

        llm_config = {
            "config_list": self.config_list,
            "temperature": 0.7,
        }

        # UX Designer Agent
        self.ux_designer = AssistantAgent(
            name="UX_Designer",
            llm_config=llm_config,
            system_message="""You are a Senior UX Designer specializing in Material Design 3.

When designing:
1. Analyze requirements and user needs
2. Propose specific component hierarchy
3. Define layouts (tabs, columns, rows, accordions)
4. Specify interactions and user flows
5. Consider responsive design

Be specific about:
- Component types (cards, tables, charts, buttons)
- Layout structure (grid, flex, columns)
- Navigation patterns
- Color scheme and styling
- User interactions

Respond to technical constraints from the developer constructively."""
        )

        # Gradio Developer Agent
        self.gradio_developer = AssistantAgent(
            name="Gradio_Developer",
            llm_config=llm_config,
            system_message="""You are a Gradio Framework Expert.

Your responsibilities:
1. Review UX designs for technical feasibility
2. Point out Gradio limitations and suggest alternatives
3. Implement the agreed design in complete, working code
4. Use gr.Blocks() for layout control
5. Include proper event handlers and state management

Known Gradio constraints:
- No nested modals
- Tab performance issues with >5 tabs
- Use gr.Accordion for many sections
- gr.State for navigation history
- CSS limitations for styling

Always output COMPLETE, RUNNABLE code wrapped in ```python blocks.
End your final code message with: COLLABORATION_COMPLETE"""
        )

        # User Proxy (for managing the conversation)
        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            is_termination_msg=lambda x: "COLLABORATION_COMPLETE" in x.get("content", ""),
            code_execution_config=False  # Don't execute code
        )

    def generate_with_collaboration(self, requirements: Dict, context: Dict) -> str:
        """
        Generation with real-time updates using session state
        """

        # Initialize session state for messages
        if 'agent_messages' not in st.session_state:
            st.session_state.agent_messages = []
        if 'generation_complete' not in st.session_state:
            st.session_state.generation_complete = False

        # Create group chat
        groupchat = GroupChat(
            agents=[self.user_proxy, self.ux_designer, self.gradio_developer],
            messages=[],
            max_round=10,
            speaker_selection_method="auto"
        )

        # Create manager
        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config={"config_list": self.config_list}
        )

        # Initial message
        initial_message = f"""Create a UI application with these requirements:

REQUIREMENTS:
{json.dumps(requirements, indent=2)}

CONTEXT:
- Data Sources: {list(context.get('data_sources', {}).keys())}
- Total Records: {context.get('summary', {}).get('human_readable_records', 'Unknown')}

PROCESS:
1. UX_Designer: Create a detailed design specification
2. Gradio_Developer: Review for feasibility and provide feedback
3. UX_Designer: Adjust if needed based on constraints
4. Gradio_Developer: Implement the final design in complete code
5. End with COLLABORATION_COMPLETE when code is ready

Start with the UX_Designer creating the design."""

        # Monkey-patch to capture messages
        original_append = groupchat.append

        def append_with_capture(message, speaker=None):
            result = original_append(message, speaker)
            # Store in session state
            st.session_state.agent_messages = list(groupchat.messages)
            return result

        groupchat.append = append_with_capture

        # Run chat
        self.user_proxy.initiate_chat(manager, message=initial_message)

        # Mark complete
        st.session_state.generation_complete = True
        st.session_state.agent_messages = list(groupchat.messages)

        # Extract code
        return self._extract_code(groupchat.messages)

    def _extract_code(self, messages: List[Dict]) -> str:
        """Extract the final code from messages"""
        import re

        # Look for code blocks from Gradio Developer
        for message in reversed(messages):
            if message.get("name") == "Gradio_Developer":
                content = message.get("content", "")

                # Find Python code blocks
                code_blocks = re.findall(r"```python\n(.*?)\n```", content, re.DOTALL)

                if code_blocks:
                    return code_blocks[-1]

        return "# No code generated"


class EnhancedAgentRunner:
    """Runner with WORKING collaborative agent system"""

    def __init__(self):
        st.set_page_config(
            page_title="Collaborative Agent UI Generator",
            page_icon="AI",
            layout="wide"
        )

        # Session state
        if 'status' not in st.session_state:
            st.session_state.status = 'initializing'
        if 'generated_code' not in st.session_state:
            st.session_state.generated_code = None
        if 'context' not in st.session_state:
            st.session_state.context = None
        if 'prompt' not in st.session_state:
            st.session_state.prompt = None

    def run(self):
        st.title("Collaborative Agent UI Generator (FIXED)")
        st.markdown("**Using standard AutoGen - no async complexity!**")

        # Check AutoGen
        if not AUTOGEN_AVAILABLE:
            st.error(f"""
            AutoGen not installed! Error: {AUTOGEN_ERROR}

            Install with:
            ```bash
            pip install pyautogen
            ```

            For Claude support, also run:
            ```bash
            pip install litellm
            litellm --model claude-3-sonnet-20240229
            ```
            """)
            st.stop()
        else:
            st.success(f"AutoGen {AUTOGEN_VERSION} available")

        # Load context AUTO-MAGICALLY
        if not st.session_state.context:
            with st.spinner("Loading context..."):
                context = PipelineState.load_context(check_freshness=False)
                if context:
                    st.session_state.context = context

                    # Generate prompt
                    datasets = list(context.get('data_sources', {}).keys())
                    total_records = context.get('summary', {}).get('human_readable_records', 'Unknown')

                    st.session_state.prompt = f"""Create a dashboard for:
- {len(datasets)} data sources: {', '.join(datasets)}
- {total_records} total records
- Interactive filtering and drill-down
- Material Design 3 interface
- Real-time updates"""

                    st.success(f"Context loaded: {len(datasets)} sources")

                    # AUTO-START!
                    st.session_state.status = 'generating'
                    st.rerun()
                else:
                    st.error("No context found. Run pipeline first!")
                    st.stop()

        # Status
        status_container = st.container()
        with status_container:
            if st.session_state.status == 'generating':
                st.warning("Agents collaborating...")
            elif st.session_state.status == 'complete':
                st.success("Complete!")

        # Controls
        col1, col2 = st.columns(2)

        with col1:
            if st.session_state.generated_code:
                if st.button("Save Code", type="primary"):
                    path = project_root / "generated_ui.py"
                    path.write_text(st.session_state.generated_code)
                    st.success(f"Saved to {path}")

        with col2:
            if st.button("Regenerate"):
                st.session_state.status = 'initializing'
                st.session_state.generated_code = None
                st.session_state.context = None
                st.rerun()

        st.markdown("---")

        # Display areas
        col_chat, col_terminal = st.columns([2, 1])

        with col_chat:
            st.subheader("Agent Conversation")
            chat_container = st.container(height=600)

            # Display messages from session state
            if 'agent_messages' in st.session_state and st.session_state.agent_messages:
                with chat_container:
                    for msg in st.session_state.agent_messages:
                        speaker = msg.get("name", "Unknown")
                        content = msg.get("content", "")

                        if speaker == "UX_Designer":
                            st.markdown("### 🎨 UX Designer")
                        elif speaker == "Gradio_Developer":
                            st.markdown("### 💻 Gradio Developer")
                        else:
                            st.markdown(f"### {speaker}")

                        st.markdown(content)
                        st.markdown("---")

        with col_terminal:
            st.subheader("Terminal")
            terminal_container = st.container(height=600)

            # Show message count
            if 'agent_messages' in st.session_state:
                with terminal_container:
                    st.info(f"Messages: {len(st.session_state.agent_messages)}")

        # SYNCHRONOUS generation (no async!)
        if st.session_state.status == 'generating':
            try:
                generator = CollaborativeUIGenerator(chat_container, terminal_container)

                requirements = {
                    'screen_type': 'dashboard',
                    'intent': st.session_state.prompt,
                    'data_sources': st.session_state.context.get('data_sources', {})
                }

                # NO asyncio.run() - just call it directly!
                code = generator.generate_with_collaboration(
                    requirements,
                    st.session_state.context
                )

                st.session_state.generated_code = code
                st.session_state.status = 'complete'
                st.rerun()

            except Exception as e:
                st.error(f"Generation failed: {e}")
                st.info("""
                If AutoGen can't connect to Claude, try:
                1. Run: `litellm --model claude-3-sonnet-20240229`
                2. This creates a local proxy
                3. Then retry generation
                """)
                st.session_state.status = 'error'

        # Show code
        if st.session_state.generated_code:
            with st.expander("Generated Code", expanded=True):
                st.code(st.session_state.generated_code, language='python')


if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.error("Set ANTHROPIC_API_KEY environment variable")
        st.stop()

    runner = EnhancedAgentRunner()
    runner.run()
