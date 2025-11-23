"""
Agent Chat Runner with AutoGen - Based on Official Microsoft Examples
References:
- https://github.com/microsoft/autogen/blob/main/python/samples/agentchat_streamlit/main.py
- https://github.com/microsoft/autogen/discussions/6411

This implementation properly streams GroupChat responses to Streamlit.
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import time
import json
import subprocess
import webbrowser
from datetime import datetime
from io import StringIO
import threading
from queue import Queue

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# AutoGen imports
from autogen import (
    AssistantAgent,
    UserProxyAgent,
    GroupChat,
    GroupChatManager,
    ConversableAgent
)
import autogen

from shared_state import PipelineState, SessionState


class StreamlitAgentChat:
    """
    Manages AutoGen agent chat with proper Streamlit streaming.
    Based on official AutoGen Streamlit example.
    """

    def __init__(self):
        """Initialize the agent chat system"""
        self.chat_messages = []
        self.message_queue = Queue()
        self.agents_created = False

    def create_agents(self) -> tuple:
        """
        Create the UX Designer and Gradio Developer agents.
        Returns tuple of (agents_list, group_chat_manager)
        """

        # Get API key
        import os
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            st.error("Please set ANTHROPIC_API_KEY environment variable")
            return None, None

        # Configure LLM
        llm_config = {
            "config_list": [{
                "model": "claude-3-sonnet-20240229",
                "api_key": api_key,
                "api_type": "anthropic"
            }],
            "temperature": 0.7,
        }

        # Create UX Designer Agent
        ux_designer = AssistantAgent(
            name="UX_Designer",
            system_message="""You are a Senior UX Designer specializing in Material Design 3.

Your responsibilities:
1. Analyze requirements and create detailed design specifications
2. Define component hierarchy, layout structure, and color scheme
3. Specify interaction patterns and user flows
4. Provide clear design rationale

Output a structured design specification with:
- Layout structure (tabs, columns, rows)
- Component list with descriptions
- Interaction patterns
- Visual styling guidelines""",
            llm_config=llm_config,
        )

        # Create Gradio Developer Agent
        gradio_developer = AssistantAgent(
            name="Gradio_Developer",
            system_message="""You are a Gradio Framework Expert.

Your responsibilities:
1. Convert UX designs into working Gradio code
2. Implement all components and interactions
3. Handle data bindings and event handlers
4. Generate complete, runnable Python code

Always output COMPLETE working code using gr.Blocks() that can be run immediately.
Include all imports, event handlers, and sample data.""",
            llm_config=llm_config,
        )

        # Create User Proxy (non-executing)
        user_proxy = UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
        )

        # Create Group Chat
        groupchat = GroupChat(
            agents=[user_proxy, ux_designer, gradio_developer],
            messages=[],
            max_round=8,
            speaker_selection_method="auto",
            enable_clear_history=True
        )

        # Create Group Chat Manager
        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config=llm_config,
        )

        return [user_proxy, ux_designer, gradio_developer, manager], manager

    def print_messages(self, recipient, messages, sender, config):
        """
        Callback function to capture and display messages in Streamlit.
        This is called by AutoGen for each message exchange.
        """

        # Extract the actual message content
        if messages:
            for message in messages if isinstance(messages, list) else [messages]:
                if isinstance(message, dict):
                    content = message.get("content", "")
                    name = message.get("name", sender.name if hasattr(sender, 'name') else "Unknown")
                else:
                    content = str(message)
                    name = sender.name if hasattr(sender, 'name') else "Unknown"

                # Add to our message list
                self.chat_messages.append({
                    "name": name,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })

                # Also add to queue for streaming display
                self.message_queue.put({
                    "name": name,
                    "content": content
                })

        return False, None  # Don't stop the conversation

    def run_chat(self, message: str, agents: list, manager) -> str:
        """
        Run the agent chat with proper streaming to Streamlit.

        Args:
            message: Initial message to start the conversation
            agents: List of agents
            manager: Group chat manager

        Returns:
            Generated code as string
        """

        # Clear previous messages
        self.chat_messages = []

        # Get the user proxy (first agent)
        user_proxy = agents[0]

        # Register the print callback for streaming
        for agent in agents:
            agent.register_reply(
                [autogen.Agent, None],
                reply_func=self.print_messages,
                config={"callback": None},
            )

        # Create a placeholder for streaming messages
        message_placeholder = st.empty()

        # Function to update display
        def update_display():
            while True:
                if not self.message_queue.empty():
                    msg = self.message_queue.get()

                    # Update the placeholder with new message
                    with message_placeholder.container():
                        # Display all messages so far
                        for chat_msg in self.chat_messages:
                            name = chat_msg["name"]
                            content = chat_msg["content"]

                            # Style based on agent
                            if name == "UX_Designer":
                                st.markdown(f"**UX Designer:**")
                            elif name == "Gradio_Developer":
                                st.markdown(f"**Gradio Developer:**")
                            else:
                                st.markdown(f"**{name}:**")

                            st.write(content)
                            st.divider()

                time.sleep(0.1)

        # Start the display updater in a thread
        display_thread = threading.Thread(target=update_display, daemon=True)
        display_thread.start()

        # Initiate the chat
        with st.spinner("Agents are collaborating..."):
            user_proxy.initiate_chat(
                manager,
                message=message,
                clear_history=True
            )

        # Extract code from the conversation
        return self.extract_code_from_messages()

    def extract_code_from_messages(self) -> str:
        """Extract generated code from agent messages"""

        code_blocks = []

        for msg in self.chat_messages:
            if msg["name"] == "Gradio_Developer":
                content = msg["content"]

                # Look for code blocks
                import re

                # Try to find Python code blocks
                pattern = r"```python\n(.*?)\n```"
                matches = re.findall(pattern, content, re.DOTALL)
                if matches:
                    code_blocks.extend(matches)
                else:
                    # Try generic code blocks
                    pattern = r"```\n(.*?)\n```"
                    matches = re.findall(pattern, content, re.DOTALL)
                    if matches:
                        code_blocks.extend(matches)

        # Return the most complete code block (usually the last one)
        for code in reversed(code_blocks):
            if "import gradio" in code and "gr.Blocks" in code:
                return code

        # If no complete code block, try to extract from content
        for msg in reversed(self.chat_messages):
            if msg["name"] == "Gradio_Developer":
                content = msg["content"]
                if "import gradio" in content:
                    return content

        return ""


def main():
    """Main Streamlit application"""

    st.set_page_config(
        page_title="Agent UI Generator (AutoGen Official Pattern)",
        page_icon="AI",
        layout="wide"
    )

    st.title("AI Agent UI Generator")
    st.markdown("**Using Microsoft AutoGen with proper streaming**")

    # Initialize session state
    if 'agent_chat' not in st.session_state:
        st.session_state.agent_chat = StreamlitAgentChat()
    if 'status' not in st.session_state:
        st.session_state.status = 'ready'
    if 'generated_code' not in st.session_state:
        st.session_state.generated_code = None
    if 'context' not in st.session_state:
        st.session_state.context = None
    if 'agents' not in st.session_state:
        st.session_state.agents = None
    if 'manager' not in st.session_state:
        st.session_state.manager = None

    # Load context
    if st.session_state.context is None:
        with st.spinner("Loading pipeline context..."):
            try:
                context = PipelineState.load_context(check_freshness=False)
                if context:
                    st.session_state.context = context
                    st.success(f"Loaded {len(context.get('data_sources', {}))} data sources")
                else:
                    st.error("No context found. Please run: `python run_ingestion.py --all`")
                    st.stop()
            except Exception as e:
                st.error(f"Error loading context: {e}")
                st.stop()

    # Create agents if not already created
    if st.session_state.agents is None:
        with st.spinner("Creating AI agents..."):
            agents, manager = st.session_state.agent_chat.create_agents()
            if agents:
                st.session_state.agents = agents
                st.session_state.manager = manager
                st.success("Agents created successfully")
            else:
                st.error("Failed to create agents")
                st.stop()

    # Generate prompt from context
    context = st.session_state.context
    datasets = list(context.get('data_sources', {}).keys())
    total_records = context.get('summary', {}).get('human_readable_records', 'Unknown')

    prompt = f"""Create a Gradio dashboard application with these requirements:

**Data Context:**
- Data Sources: {', '.join(datasets)}
- Total Records: {total_records}

**Requirements:**
1. Create a multi-tab interface for different data views
2. Add filtering controls for each data source
3. Include data visualization components
4. Add export functionality
5. Use Material Design principles
6. Make it responsive and user-friendly

**Process:**
1. UX_Designer: Create a detailed design specification
2. Gradio_Developer: Implement the complete working code
3. Ensure the code is complete and can run immediately

Begin by having the UX_Designer create the design specification."""

    # Display prompt
    with st.expander("Generation Prompt", expanded=False):
        st.info(prompt)

    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Generate UI", type="primary", disabled=st.session_state.status == 'generating'):
            st.session_state.status = 'generating'
            st.rerun()

    with col2:
        if st.session_state.generated_code:
            if st.button("Save Code"):
                output_file = project_root / "generated_ui_autogen.py"
                output_file.write_text(st.session_state.generated_code, encoding='utf-8')
                st.success(f"Saved to {output_file}")

    with col3:
        if st.session_state.generated_code:
            if st.button("Launch Dashboard"):
                output_file = project_root / "generated_ui_autogen.py"
                output_file.write_text(st.session_state.generated_code, encoding='utf-8')
                subprocess.Popen(['python', str(output_file)])
                time.sleep(2)
                webbrowser.open('http://127.0.0.1:7860')
                st.success("Dashboard launched!")

    st.divider()

    # Main content area
    if st.session_state.status == 'generating':
        st.subheader("Agent Collaboration")

        # Create container for agent messages
        chat_container = st.container()

        with chat_container:
            # Run the agent chat
            generated_code = st.session_state.agent_chat.run_chat(
                prompt,
                st.session_state.agents,
                st.session_state.manager
            )

            if generated_code:
                st.session_state.generated_code = generated_code
                st.session_state.status = 'complete'
                st.success("Code generation complete!")
                st.rerun()
            else:
                st.error("Failed to generate code")
                st.session_state.status = 'ready'

    elif st.session_state.status == 'complete' and st.session_state.generated_code:
        # Display the generated code
        st.subheader("Generated Code")

        # Show agent conversation
        with st.expander("Agent Conversation", expanded=False):
            for msg in st.session_state.agent_chat.chat_messages:
                name = msg["name"]
                content = msg["content"]

                if name == "UX_Designer":
                    st.markdown("**UX Designer:**")
                elif name == "Gradio_Developer":
                    st.markdown("**Gradio Developer:**")
                else:
                    st.markdown(f"**{name}:**")

                st.write(content)
                st.divider()

        # Show the code
        st.code(st.session_state.generated_code, language='python')

    else:
        # Ready state
        st.info("Click 'Generate UI' to start the agent collaboration")

        # Show what will be generated
        st.subheader("Available Data Sources")

        for source_name, source_data in context.get('data_sources', {}).items():
            with st.expander(f"{source_name}"):
                if isinstance(source_data, dict):
                    st.json(source_data)
                else:
                    st.write(source_data)


if __name__ == "__main__":
    import os

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.error("""
        ANTHROPIC_API_KEY not found!

        Please set your API key:
        ```bash
        export ANTHROPIC_API_KEY='your-key-here'
        ```
        """)
        st.stop()

    # Check if AutoGen supports Anthropic directly
    # If not, we'll need to use litellm as a bridge
    try:
        import litellm
        st.sidebar.success("LiteLLM available for Anthropic support")
    except ImportError:
        st.sidebar.warning("""
        Install litellm for better Anthropic support:
        ```bash
        pip install litellm
        ```
        """)

    main()
