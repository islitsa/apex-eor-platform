"""
Streamlit Agent Chat Interface - Watch Agents Work in Real-Time

This interface shows the conversation between UX Designer and Gradio Developer agents
as they collaborate to generate UI code.

Left pane: User inputs (requirements, context)
Right pane: Agent conversation and reasoning
Bottom: Generated code output
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Dict, Any, List
import time

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents.ui_orchestrator import UICodeOrchestrator
from shared_state import PipelineState


class AgentChatInterface:
    """Streamlit interface for watching agents collaborate"""

    def __init__(self):
        st.set_page_config(
            page_title="Agent Chat - UI Code Generator",
            page_icon="🤖",
            layout="wide"
        )

        # Initialize session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'generated_code' not in st.session_state:
            st.session_state.generated_code = None
        if 'orchestrator' not in st.session_state:
            st.session_state.orchestrator = None

    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add a message to the chat"""
        st.session_state.messages.append({
            'role': role,
            'content': content,
            'metadata': metadata or {},
            'timestamp': time.time()
        })

    def render_chat_message(self, msg: Dict):
        """Render a single chat message"""
        role = msg['role']
        content = msg['content']

        # Choose icon and color based on role
        if role == 'ux_designer':
            icon = "🎨"
            color = "#1E88E5"  # Blue
            name = "UX Designer (The Visionary)"
        elif role == 'gradio_developer':
            icon = "⚙️"
            color = "#43A047"  # Green
            name = "Gradio Developer (The Implementer)"
        elif role == 'orchestrator':
            icon = "🎭"
            color = "#8E24AA"  # Purple
            name = "Orchestrator"
        elif role == 'user':
            icon = "👤"
            color = "#757575"  # Gray
            name = "You"
        else:
            icon = "ℹ️"
            color = "#999999"
            name = role.title()

        # Render message
        with st.chat_message(name, avatar=icon):
            st.markdown(f"**{name}**")
            st.markdown(content)

            # Show metadata if available
            if msg.get('metadata'):
                with st.expander("Details"):
                    st.json(msg['metadata'])

    def render(self):
        """Render the main interface"""

        # Title
        st.title("🤖 Agent Chat Interface")
        st.markdown("**Watch UX Designer and Gradio Developer agents collaborate in real-time**")

        # Layout: Left pane (inputs) | Right pane (chat)
        col1, col2 = st.columns([1, 2])

        with col1:
            st.header("📝 Requirements")

            # Screen type
            screen_type = st.selectbox(
                "Screen Type",
                ["data_dashboard", "dashboard_navigation", "settings_screen", "data_viewer", "custom"]
            )

            # User intent
            intent = st.text_area(
                "User Intent",
                value="Monitor petroleum pipeline status and drill down into data hierarchy",
                height=100
            )

            # Load context button
            if st.button("🔍 Load Pipeline Context"):
                with st.spinner("Loading context..."):
                    try:
                        context = PipelineState.load_context(check_freshness=True)
                        if context is None:
                            st.error("❌ No pipeline context found. Run: python run_ingestion.py --generate-context")
                        else:
                            st.session_state.context = context
                            st.success(f"✅ Loaded {len(context.get('data_sources', {}))} data sources")
                    except Exception as e:
                        st.error(f"❌ Error loading context: {e}")

            # Show context if loaded
            if 'context' in st.session_state:
                with st.expander("📊 Context Details"):
                    st.json({
                        'sources': len(st.session_state.context.get('data_sources', {})),
                        'datasets': len(st.session_state.context.get('datasets', {}))
                    })

            st.markdown("---")

            # Generate button
            if st.button("🚀 Generate UI Code", type="primary"):
                if 'context' not in st.session_state:
                    st.error("⚠️ Please load context first")
                else:
                    self.generate_code(screen_type, intent, st.session_state.context)

        with col2:
            st.header("💬 Agent Conversation")

            # Chat container
            chat_container = st.container()

            with chat_container:
                if not st.session_state.messages:
                    st.info("👋 Click 'Generate UI Code' to watch the agents collaborate!")
                else:
                    for msg in st.session_state.messages:
                        self.render_chat_message(msg)

            # Chat input for questions and feedback
            st.markdown("---")
            user_message = st.chat_input("Ask agents a question or provide feedback...")

            if user_message:
                # Add user message
                self.add_message('user', user_message)

                # Process user message
                self.handle_user_message(user_message)

                # Trigger rerun to show new messages
                st.rerun()

        # Bottom: Generated code
        if st.session_state.generated_code:
            st.markdown("---")
            st.header("📄 Generated Code")
            st.code(st.session_state.generated_code, language="python", line_numbers=True)

            # Download button
            st.download_button(
                label="⬇️ Download Code",
                data=st.session_state.generated_code,
                file_name=f"generated_{screen_type}.py",
                mime="text/x-python"
            )

    def generate_code(self, screen_type: str, intent: str, context: Dict):
        """Generate code and stream agent messages"""

        # Clear previous messages
        st.session_state.messages = []
        st.session_state.generated_code = None

        # Add user message
        self.add_message('user', f"Generate a {screen_type} screen", {
            'screen_type': screen_type,
            'intent': intent
        })

        # Create orchestrator with message callback
        self.add_message('orchestrator', "Initializing two-agent system...")

        try:
            # Create orchestrator
            if not st.session_state.orchestrator:
                st.session_state.orchestrator = AgentChatOrchestrator(
                    message_callback=self.add_message
                )

            orchestrator = st.session_state.orchestrator

            # Build requirements (no data_sources - agent will discover)
            requirements = {
                'screen_type': screen_type,
                'intent': intent
                # Note: data_sources NOT passed - UX Designer will discover autonomously
            }

            # Generate code (agents will emit messages via callback)
            self.add_message('orchestrator', "Starting two-agent code generation...")

            code = orchestrator.generate_ui_code(requirements, context)

            # Store generated code
            st.session_state.generated_code = code

            self.add_message('orchestrator', f"✅ Code generation complete! Generated {len(code)} characters", {
                'code_length': len(code)
            })

            # Trigger rerun to show results
            st.rerun()

        except Exception as e:
            self.add_message('orchestrator', f"❌ Error: {e}", {'error': str(e)})
            st.error(f"Error generating code: {e}")

    def handle_user_message(self, message: str):
        """Handle user questions and feedback"""

        # Check if orchestrator exists
        if not st.session_state.orchestrator:
            self.add_message('orchestrator', "Please generate code first before asking questions")
            return

        orchestrator = st.session_state.orchestrator

        # Route message to appropriate agent based on content
        if any(word in message.lower() for word in ['design', 'ux', 'layout', 'pattern', 'user']):
            # UX Designer question
            self.add_message('ux_designer', "Let me think about your design question...")
            response = self.ask_ux_designer(message, orchestrator)
            self.add_message('ux_designer', response)

        elif any(word in message.lower() for word in ['gradio', 'code', 'implement', 'component', 'error']):
            # Gradio Developer question
            self.add_message('gradio_developer', "Let me check the implementation...")
            response = self.ask_gradio_developer(message, orchestrator)
            self.add_message('gradio_developer', response)

        else:
            # General question - orchestrator handles
            self.add_message('orchestrator', "Let me address your question...")
            response = f"Your feedback: '{message}' has been noted. Both agents will consider this in future generations."
            self.add_message('orchestrator', response)

    def ask_ux_designer(self, question: str, orchestrator) -> str:
        """Ask UX Designer agent a question"""
        import anthropic
        import os

        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

        # Get design history
        design_history = orchestrator.ux_designer.get_design_history()

        prompt = f"""You are the UX Designer agent. You specialize in Material Design 3, user experience patterns, and design thinking.

The user has a question about the design:

USER QUESTION: {question}

DESIGN HISTORY:
{design_history if design_history else "No designs created yet"}

GENERATED CODE:
{st.session_state.generated_code[:500] if st.session_state.generated_code else "No code generated yet"}

Please answer the user's question from a UX design perspective. Be helpful and explain your design decisions.

Answer in 2-3 paragraphs."""

        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Sorry, I encountered an error: {e}"

    def ask_gradio_developer(self, question: str, orchestrator) -> str:
        """Ask Gradio Developer agent a question"""
        import anthropic
        import os

        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

        # Get implementation history
        impl_history = orchestrator.gradio_developer.implementation_history

        prompt = f"""You are the Gradio Developer agent. You specialize in Gradio framework, Python implementation, and solving technical constraints.

The user has a question about the implementation:

USER QUESTION: {question}

IMPLEMENTATION HISTORY:
{impl_history if impl_history else "No implementations created yet"}

GENERATED CODE:
{st.session_state.generated_code[:500] if st.session_state.generated_code else "No code generated yet"}

Please answer the user's question from a technical Gradio implementation perspective. Be specific about constraints and workarounds.

Answer in 2-3 paragraphs."""

        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Sorry, I encountered an error: {e}"


class AgentChatOrchestrator(UICodeOrchestrator):
    """
    Extended orchestrator that emits messages to chat interface
    """

    def __init__(self, message_callback=None):
        super().__init__()
        self.message_callback = message_callback

    def emit(self, role: str, content: str, metadata: Dict = None):
        """Emit a message to the chat"""
        if self.message_callback:
            self.message_callback(role, content, metadata)

    def generate_ui_code(self, requirements: Dict, context: Dict) -> str:
        """Generate UI code with chat emissions"""

        self.emit('orchestrator', "Starting PHASE 1: UX Design")

        # PHASE 1: UX DESIGNER
        self.emit('ux_designer', "Starting design process...", {
            'phase': 'design',
            'screen_type': requirements.get('screen_type')
        })

        self.emit('ux_designer', "Querying UX patterns from Pinecone...")
        design_spec = self.ux_designer.design(requirements)

        self.emit('ux_designer', f"Design complete!", {
            'components': len(design_spec.components),
            'interactions': len(design_spec.interactions),
            'patterns': design_spec.patterns
        })

        # Show design reasoning if available
        if hasattr(self.ux_designer, '_last_reasoning'):
            self.emit('ux_designer', "**Chain of Thought Reasoning:**\n\n" + self.ux_designer._last_reasoning[:500] + "...")

        self.emit('orchestrator', "Starting PHASE 2: Gradio Implementation")

        # PHASE 2: GRADIO DEVELOPER
        self.emit('gradio_developer', "Starting implementation...", {
            'phase': 'implementation'
        })

        self.emit('gradio_developer', "Querying Gradio constraints from Pinecone...")
        gradio_code = self.gradio_developer.build(design_spec, context)

        self.emit('gradio_developer', f"Implementation complete!", {
            'code_length': len(gradio_code)
        })

        # Show implementation plan if available
        if hasattr(self.gradio_developer, '_last_plan'):
            self.emit('gradio_developer', "**Implementation Plan:**\n\n" + self.gradio_developer._last_plan[:500] + "...")

        return gradio_code


# Entry point
if __name__ == "__main__":
    interface = AgentChatInterface()
    interface.render()