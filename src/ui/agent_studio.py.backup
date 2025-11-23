"""
Agent Studio - 3-Column Chat Interface

Layout:
┌──────────────┬──────────────────┬──────────────────┐
│              │                  │                  │
│  LEFT        │   MIDDLE         │   RIGHT          │
│  User        │   Your Chat      │   Agent Chat     │
│  Profile     │   with Agents    │   (Watch Them)   │
│              │                  │                  │
│  - Name      │   You: Generate  │   🎨 UX: I'll    │
│  - Save      │   dashboard      │   design...      │
│  - History   │                  │                  │
│  - Settings  │   🎨 UX: Done!   │   ⚙️ Dev: I'll   │
│              │                  │   implement...   │
│              │   You: Why card  │                  │
│              │   layout?        │   🎨->⚙️: Here's │
│              │                  │   the spec       │
│              │   🎨 UX: Because │                  │
│              │   ...            │                  │
└──────────────┴──────────────────┴──────────────────┘
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Dict, Any, List
import time
import json
from datetime import datetime
from dotenv import load_dotenv
import argparse
import io
from contextlib import redirect_stdout, redirect_stderr

# Load environment variables FIRST
load_dotenv()

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents.ui_orchestrator import UICodeOrchestrator
from shared_state import PipelineState, SessionState


class AgentStudio:
    """3-column agent chat studio"""

    def __init__(self):
        st.set_page_config(
            page_title="Agent Studio",
            page_icon="🎨",
            layout="wide",
            initial_sidebar_state="collapsed"
        )

        # Parse CLI arguments for initial prompt
        if 'cli_args_parsed' not in st.session_state:
            parser = argparse.ArgumentParser()
            parser.add_argument("--prompt", type=str, default="", help="Initial prompt to populate")

            # Streamlit passes args after --, so handle that
            try:
                if "--" in sys.argv:
                    idx = sys.argv.index("--")
                    args = parser.parse_args(sys.argv[idx+1:])
                else:
                    args = parser.parse_args([])
            except:
                args = parser.parse_args([])  # Default if parsing fails

            st.session_state.cli_args_parsed = True
            st.session_state.initial_prompt = args.prompt
            st.session_state.auto_generate = bool(args.prompt)  # Auto-generate if prompt provided

            # Check for --force-llm flag
            st.session_state.force_llm = '--force-llm' in sys.argv

        # Initialize session state
        if 'user_name' not in st.session_state:
            st.session_state.user_name = "You"
        if 'user_messages' not in st.session_state:
            st.session_state.user_messages = []  # User <-> Agent conversation
        if 'agent_messages' not in st.session_state:
            st.session_state.agent_messages = []  # Agent <-> Agent conversation
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []  # Saved chat sessions
        if 'orchestrator' not in st.session_state:
            st.session_state.orchestrator = None
        if 'context' not in st.session_state:
            st.session_state.context = None
        if 'auto_start' not in st.session_state:
            st.session_state.auto_start = False  # Auto-load context and generate
        if 'initialized' not in st.session_state:
            st.session_state.initialized = False
        if 'agent_chatter' not in st.session_state:
            st.session_state.agent_chatter = ""  # Captured agent output

    def add_user_message(self, role: str, content: str, metadata: Dict = None):
        """Add message to user chat (middle column)"""
        st.session_state.user_messages.append({
            'role': role,
            'content': content,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        })

    def add_agent_message(self, from_agent: str, to_agent: str, content: str, metadata: Dict = None):
        """Add message to agent chat (right column)"""
        st.session_state.agent_messages.append({
            'from': from_agent,
            'to': to_agent,
            'content': content,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        })

    def render_left_column(self):
        """Left column: User profile and chat management"""
        st.header("👤 Profile")

        # User name
        user_name = st.text_input(
            "Your Name",
            value=st.session_state.user_name,
            key="user_name_input"
        )
        if user_name != st.session_state.user_name:
            st.session_state.user_name = user_name

        st.markdown("---")

        # Current session info
        st.subheader("📊 Current Session")
        st.metric("User Messages", len(st.session_state.user_messages))
        st.metric("Agent Messages", len(st.session_state.agent_messages))

        # Context status
        if st.session_state.context:
            st.success("✅ Context Loaded")
            sources = len(st.session_state.context.get('data_sources', {}))
            st.caption(f"{sources} data sources")
        else:
            if st.button("🔍 Load Context", use_container_width=True):
                self.load_context()

        st.markdown("---")

        # Save current chat
        st.subheader("💾 Save Chat")

        session_name = st.text_input(
            "Session Name",
            value=f"Session {len(st.session_state.chat_history) + 1}"
        )

        if st.button("💾 Save Current Chat", use_container_width=True):
            self.save_chat(session_name)

        # Clear chat
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.user_messages = []
            st.session_state.agent_messages = []
            st.rerun()

        st.markdown("---")

        # Chat history
        st.subheader("📚 Saved Chats")

        if st.session_state.chat_history:
            for i, saved_chat in enumerate(reversed(st.session_state.chat_history)):
                with st.expander(f"📝 {saved_chat['name']}", expanded=False):
                    st.caption(f"Saved: {saved_chat['timestamp']}")
                    st.caption(f"Messages: {saved_chat['user_msg_count']} user, {saved_chat['agent_msg_count']} agent")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📂 Load", key=f"load_{i}"):
                            self.load_chat(saved_chat)
                    with col2:
                        if st.button("⬇️ Export", key=f"export_{i}"):
                            self.export_chat(saved_chat)
        else:
            st.caption("No saved chats yet")

    def render_middle_column(self):
        """Middle column: User conversation with agents"""
        st.header("💬 Chat with Agents")

        # Quick actions
        with st.expander("🚀 Quick Actions", expanded=True):
            # Show different actions based on state
            if 'generated_code' in st.session_state and st.session_state.generated_code:
                # After generation - show launch and regenerate buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Regenerate", use_container_width=True):
                        # Set flag to trigger regeneration on next run
                        st.session_state.regenerate_requested = True
                        # Force LLM generation on regenerate to incorporate feedback
                        st.session_state.force_llm = True
                        st.rerun()
                with col2:
                    if st.button("🚀 Launch Dashboard", use_container_width=True, type="primary"):
                        self.launch_gradio()
            else:
                # Before generation - show generate button
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("🎨 Generate Dashboard", use_container_width=True):
                        if not st.session_state.context:
                            st.error("Load context first!")
                        else:
                            self.generate_dashboard()

                with col2:
                    if st.button("❓ Ask Design Question", use_container_width=True):
                        self.add_user_message('system', "💡 Tip: Ask about design patterns, UX decisions, or implementation details!")

        st.markdown("---")

        # Chat messages
        chat_container = st.container(height=500)

        with chat_container:
            if not st.session_state.user_messages:
                st.info("👋 Start chatting! Click 'Generate Dashboard' or type a message below.")
            else:
                for msg in st.session_state.user_messages:
                    self.render_user_chat_message(msg)

        # Chat input
        user_input = st.chat_input("Ask agents anything or give them instructions...")

        if user_input:
            # Add user message
            self.add_user_message('user', user_input)

            # Process with agents
            self.handle_user_input(user_input)

            st.rerun()

    def render_right_column(self):
        """Right column: Agent-to-agent conversation"""
        st.header("🤖 Agent Conversation")

        st.caption("Watch UX Designer and Gradio Developer collaborate")

        # Agent chat
        agent_chat_container = st.container(height=500)

        with agent_chat_container:
            if not st.session_state.agent_messages:
                st.info("🔇 Agents haven't started talking yet. Generate a dashboard to see their conversation!")
            else:
                for msg in st.session_state.agent_messages:
                    self.render_agent_chat_message(msg)

        # Agent chatter output
        st.markdown("---")
        st.subheader("💭 Agent Output")

        if st.session_state.agent_chatter:
            with st.expander("View captured agent output", expanded=True):
                st.code(st.session_state.agent_chatter, language="text")
        else:
            st.caption("Agent console output will appear here during generation")

        # Agent status
        st.markdown("---")
        st.subheader("🎭 Agent Status")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🎨 UX Designer**")
            if st.session_state.orchestrator:
                designs = len(st.session_state.orchestrator.ux_designer.design_history)
                st.caption(f"{designs} designs created")
            else:
                st.caption("Idle")

        with col2:
            st.markdown("**⚙️ Gradio Developer**")
            if st.session_state.orchestrator:
                impls = len(st.session_state.orchestrator.gradio_developer.implementation_history)
                st.caption(f"{impls} implementations")
            else:
                st.caption("Idle")

    def render_user_chat_message(self, msg: Dict):
        """Render a message in the user chat (middle column)"""
        role = msg['role']
        content = msg['content']

        if role == 'user':
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"**{st.session_state.user_name}**")
                st.write(content)
        elif role == 'ux_designer':
            with st.chat_message("assistant", avatar="🎨"):
                st.markdown("**UX Designer**")
                st.write(content)
                if msg.get('metadata'):
                    with st.expander("Details"):
                        st.json(msg['metadata'])
        elif role == 'gradio_developer':
            with st.chat_message("assistant", avatar="⚙️"):
                st.markdown("**Gradio Developer**")
                st.write(content)
                if msg.get('metadata'):
                    with st.expander("Details"):
                        st.json(msg['metadata'])
        else:
            with st.chat_message("assistant", avatar="🎭"):
                st.markdown(f"**{role.title()}**")
                st.write(content)

    def render_agent_chat_message(self, msg: Dict):
        """Render a message in the agent chat (right column)"""
        from_agent = msg['from']
        to_agent = msg['to']
        content = msg['content']

        # Agent icons
        agent_icons = {
            'ux_designer': '🎨',
            'gradio_developer': '⚙️',
            'orchestrator': '🎭',
            'system': '⚙️'
        }

        from_icon = agent_icons.get(from_agent, '🤖')
        to_icon = agent_icons.get(to_agent, '🤖')

        # Show as agent-to-agent message
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <strong>{from_icon} → {to_icon}</strong>
            <p style="margin: 5px 0;">{content}</p>
        </div>
        """, unsafe_allow_html=True)

        if msg.get('metadata'):
            with st.expander("📊 Data"):
                st.json(msg['metadata'])

    def load_context(self):
        """Load pipeline context from shared state"""
        try:
            context = PipelineState.load_context(check_freshness=True)
            if context is None:
                st.error("❌ No pipeline context found. Run: python run_ingestion.py --generate-context")
                self.add_user_message('system', "❌ No pipeline context found. Please run the ingestion pipeline first.")
            else:
                st.session_state.context = context
                self.add_user_message('system', f"✅ Loaded {len(context.get('data_sources', {}))} data sources from shared state")
                st.rerun()
        except Exception as e:
            st.error(f"Failed to load context: {e}")

    def generate_dashboard(self, user_feedback=None):
        """Generate dashboard with agent collaboration

        Args:
            user_feedback: Optional user feedback from chat to incorporate into design
        """
        # Add message only if it's the first generation
        if not user_feedback:
            self.add_user_message('user', "Generate a dashboard with navigation")

        # Create orchestrator if needed
        if not st.session_state.orchestrator:
            # Use Hybrid system (92% token savings vs baseline)
            # Fallback to StudioOrchestrator if --no-hybrid flag present
            use_hybrid = '--no-hybrid' not in sys.argv

            if use_hybrid:
                orchestrator = HybridStudioWrapper(
                    user_callback=self.add_user_message,
                    agent_callback=self.add_agent_message
                )
                print("[Agent Studio] Using Hybrid Code Generator (92% token savings)")
            else:
                orchestrator = StudioOrchestrator(
                    user_callback=self.add_user_message,
                    agent_callback=self.add_agent_message
                )
                print("[Agent Studio] Using Standard Two-Agent System (78% token savings)")

            st.session_state.orchestrator = orchestrator

        # Build intent from base requirements + chat history
        base_intent = '''Navigate through data pipeline with modern Material Design 3 aesthetics.

GRADIO API CONSTRAINTS (CRITICAL - DO NOT DEVIATE):
Theme:
- Use: gr.themes.Soft() - DO NOT customize colors
- Soft theme provides clean, modern aesthetic similar to M3
- NO custom theme.set() calls - causes errors
- Focus on layout and component design, not theme customization

Components:
- Button: gr.Button("text", variant="primary") - NO 'label' parameter!
  CORRECT: gr.Button("Click Me", variant="primary")
  WRONG: gr.Button(label="Click Me", variant="primary")
- All other components (Dropdown, Textbox, etc.) DO use 'label' parameter'''

        # Incorporate user feedback from chat if regenerating
        if user_feedback or (st.session_state.user_messages and len(st.session_state.user_messages) > 1):
            # Extract recent user feedback from chat
            recent_feedback = []
            for msg in st.session_state.user_messages[-5:]:  # Last 5 messages
                if msg['role'] == 'user' and msg['content'] not in ['Generate a dashboard with navigation']:
                    recent_feedback.append(msg['content'])

            if recent_feedback or user_feedback:
                feedback_text = user_feedback if user_feedback else '\n'.join(recent_feedback)
                base_intent += f"\n\nUSER FEEDBACK TO INCORPORATE:\n{feedback_text}"
                print(f"[Agent Studio] Incorporating user feedback: {feedback_text[:100]}...")

        # Generate
        requirements = {
            'screen_type': 'dashboard_navigation',
            'intent': base_intent,
            'data_sources': st.session_state.context.get('data_sources', {})
        }

        try:
            # Check for --force-llm flag to skip snippets (from session state)
            force_llm = st.session_state.get('force_llm', False)

            # Use st.status for live progress updates
            with st.status("Generating dashboard...", expanded=True) as status:
                # Store status messages for the chatter column
                chatter_messages = []

                if force_llm:
                    status.write("🎨 Using FULL AGENT GENERATION (skipping snippets)")
                    chatter_messages.append("[Mode] Force LLM - agents will design from scratch")
                else:
                    status.write("🔍 Step 1: Pattern matching (snippet path)...")
                    chatter_messages.append("[Hybrid] Starting pattern matching...")

                # Check if orchestrator has capture method (HybridStudioWrapper does)
                if hasattr(st.session_state.orchestrator, 'generate_code_with_capture'):
                    # Pass force_llm to the generator
                    if hasattr(st.session_state.orchestrator.hybrid_generator, 'generate'):
                        # Directly call generate with force_llm
                        code = st.session_state.orchestrator.hybrid_generator.generate(
                            requirements,
                            st.session_state.context,
                            force_llm=force_llm
                        )
                        chatter = "Agent generation - check terminal for details"
                    else:
                        code, chatter = st.session_state.orchestrator.generate_code_with_capture(requirements, st.session_state.context)
                    chatter_messages.append(chatter)
                else:
                    # Fallback for StudioOrchestrator (no capture)
                    status.write("⚙️ Step 2: Running two-agent generation...")
                    code = st.session_state.orchestrator.generate_ui_code(requirements, st.session_state.context)
                    chatter_messages.append("[Standard] Two-agent generation (no detailed chatter)")

                status.write(f"✅ Step 3: Code generated ({len(code):,} chars)")

                # Save to session state
                st.session_state.agent_chatter = "\n\n".join(chatter_messages)

                # Save generated code to session state and file
                st.session_state.generated_code = code

                # Save to file
                output_file = project_root / "generated_pipeline_dashboard.py"
                output_file.write_text(code, encoding='utf-8')
                st.session_state.dashboard_file = str(output_file)

                status.write(f"💾 Step 4: Saved to {output_file.name}")
                status.update(label="✅ Dashboard generated!", state="complete")

            self.add_user_message('system', f"✅ Generated {len(code)} chars of code\n📁 Saved to: {output_file.name}")
            st.rerun()

        except Exception as e:
            self.add_user_message('system', f"❌ Error: {e}")
            import traceback
            st.session_state.agent_chatter = f"ERROR:\n{str(e)}\n\n{traceback.format_exc()}"
            st.rerun()

    def launch_gradio(self):
        """Launch Gradio dashboard in new browser tab"""
        import subprocess
        import webbrowser

        if 'dashboard_file' not in st.session_state or not st.session_state.dashboard_file:
            st.error("No dashboard file to launch!")
            return

        dashboard_file = st.session_state.dashboard_file

        self.add_user_message('system', "🚀 Launching Gradio dashboard...")

        try:
            # Launch Gradio in background process
            subprocess.Popen(
                ['python', dashboard_file],
                cwd=str(project_root)
            )

            # Wait a moment then open browser
            import time
            time.sleep(2)
            webbrowser.open('http://127.0.0.1:7860')

            self.add_user_message('system', "✅ Gradio dashboard launched at http://127.0.0.1:7860")
            st.rerun()

        except Exception as e:
            self.add_user_message('system', f"❌ Error launching Gradio: {e}")
            st.rerun()

    def handle_user_input(self, user_input: str):
        """Handle user questions/commands - routes to actual agents"""
        import anthropic
        import os

        # Ensure orchestrator exists
        if not st.session_state.orchestrator:
            self.add_user_message('system', "⚠️ Please generate a dashboard first so agents are initialized!")
            return

        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

        # Route to appropriate agent based on keywords
        if any(word in user_input.lower() for word in ['design', 'ux', 'layout', 'pattern', 'user', 'why', 'card', 'show', 'display']):
            # UX Designer question - BUILD RICH CONTEXT
            self.add_agent_message('user', 'ux_designer', user_input)

            # Build comprehensive context
            context_lines = []

            # 1. DATA SOURCE CONTEXT (critical for "why show 1 dataset" question)
            if 'context' in st.session_state:
                data_sources = st.session_state.context.get('data_sources', {})
                if data_sources:
                    context_lines.append("DATA SOURCES AVAILABLE:")
                    for source_name, source_info in data_sources.items():
                        datasets = source_info.get('datasets', {})  # It's a dict, not a list!
                        context_lines.append(f"  - {source_name.upper()}: {len(datasets)} datasets")
                        # Get first 5 dataset names from dict
                        for i, (ds_name, ds_info) in enumerate(list(datasets.items())[:5], 1):
                            context_lines.append(f"      {i}. {ds_name}")

            # 2. DESIGN SPEC CONTEXT (what you actually designed)
            design_history = st.session_state.orchestrator.ux_designer.design_history
            if design_history:
                last_design = design_history[-1]
                context_lines.append("\nDESIGN SPECIFICATION YOU CREATED:")
                context_lines.append(f"  Screen Type: {last_design.screen_type}")
                context_lines.append(f"  Intent: {last_design.intent}")
                context_lines.append(f"  Components: {len(last_design.components)}")
                for comp in last_design.components:
                    context_lines.append(f"    - {comp.get('type')}: {comp.get('intent', 'N/A')}")
                context_lines.append(f"  Patterns Used: {', '.join(last_design.patterns)}")

            # 3. GENERATED CODE CONTEXT (what Gradio Developer built)
            if 'generated_code' in st.session_state and st.session_state.generated_code:
                code = st.session_state.generated_code
                context_lines.append(f"\nGRADIO CODE THAT WAS GENERATED: {len(code)} chars")

                # Extract theme line
                import re
                theme_match = re.search(r'theme=([^\)]+)\)', code)
                if theme_match:
                    context_lines.append(f"  - Theme: {theme_match.group(1)}")

                # Extract any color definitions in the code
                color_matches = re.findall(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}', code)
                if color_matches:
                    unique_colors = list(set(color_matches))[:5]  # First 5 unique colors
                    context_lines.append(f"  - Colors used: {', '.join(unique_colors)}")

                # Include first 50 lines of actual code for context
                code_lines = code.split('\n')[:50]
                context_lines.append(f"\nFIRST 50 LINES OF ACTUAL GENERATED CODE:")
                context_lines.append("```python")
                context_lines.extend(code_lines)
                context_lines.append("```")

                if 'gr.Button' in code:
                    button_count = code.count('gr.Button')
                    context_lines.append(f"  - Contains {button_count} buttons")
                if 'gr.Dropdown' in code:
                    context_lines.append(f"  - Contains dropdown navigation")
                if 'gr.Tabs' in code:
                    context_lines.append(f"  - Uses tabbed interface")

            context_text = "\n".join(context_lines) if context_lines else "No context available yet"

            prompt = f"""You are the UX Designer agent who created this dashboard design.

THE USER'S QUESTION:
{user_input}

YOUR CONTEXT (what you have access to):
{context_text}

IMPORTANT:
- You designed this specific dashboard
- Answer based on what you actually created
- Reference specific components and data sources by name
- If asked about implementation details, you can see what Gradio Developer built
- If the card shows "1 dataset" but the source has multiple datasets, that's a bug in implementation
- Be honest if something was designed incorrectly or implemented incorrectly

Please answer the user's question with specific details from your design."""

            try:
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                response = message.content[0].text
                self.add_user_message('ux_designer', response)
                self.add_agent_message('ux_designer', 'user', f"Answered: {user_input[:30]}...")
            except Exception as e:
                self.add_user_message('system', f"❌ Error: {e}")

        elif any(word in user_input.lower() for word in ['code', 'gradio', 'implement', 'how', 'error', 'dataset', 'many', 'available']):
            # Gradio Developer question - BUILD RICH CONTEXT
            self.add_agent_message('user', 'gradio_developer', user_input)

            # Build comprehensive context
            context_lines = []

            # 1. DATA SOURCE CONTEXT (critical for "how many datasets" question)
            if 'context' in st.session_state:
                data_sources = st.session_state.context.get('data_sources', {})
                if data_sources:
                    context_lines.append("DATA SOURCES YOU'RE WORKING WITH:")
                    for source_name, source_info in data_sources.items():
                        datasets = source_info.get('datasets', {})  # It's a dict, not a list!
                        context_lines.append(f"  - {source_name.upper()}: {len(datasets)} datasets")
                        # Get first 5 dataset names from dict
                        for i, (ds_name, ds_info) in enumerate(list(datasets.items())[:5], 1):
                            context_lines.append(f"      {i}. {ds_name}")

            # 2. DESIGN SPEC CONTEXT (what UX Designer gave you)
            design_history = st.session_state.orchestrator.ux_designer.design_history
            if design_history:
                last_design = design_history[-1]
                context_lines.append("\nDESIGN SPEC YOU RECEIVED:")
                context_lines.append(f"  Screen Type: {last_design.screen_type}")
                context_lines.append(f"  Components to implement: {len(last_design.components)}")
                for comp in last_design.components:
                    context_lines.append(f"    - {comp.get('type')}: {comp.get('intent', 'N/A')}")

            # 3. YOUR GENERATED CODE (FULL, not just 500 chars!)
            if 'generated_code' in st.session_state and st.session_state.generated_code:
                code = st.session_state.generated_code
                context_lines.append(f"\nCODE YOU GENERATED: {len(code)} chars")
                context_lines.append("=" * 60)
                context_lines.append(code)  # FULL CODE!
                context_lines.append("=" * 60)

            # 4. IMPLEMENTATION DETAILS
            impl_history = st.session_state.orchestrator.gradio_developer.implementation_history
            if impl_history:
                last_impl = impl_history[-1]
                context_lines.append("\nYOUR IMPLEMENTATION DETAILS:")
                context_lines.append(f"  Components used: {last_impl.get('code_summary', 'N/A')}")
                if 'constraints_applied' in last_impl:
                    context_lines.append(f"  Constraints applied: {', '.join(last_impl.get('constraints_applied', []))}")

            context_text = "\n".join(context_lines) if context_lines else "No context available yet"

            prompt = f"""You are the Gradio Developer agent who implemented this dashboard.

THE USER'S QUESTION:
{user_input}

YOUR CONTEXT (what you have access to):
{context_text}

IMPORTANT:
- You wrote this specific Gradio code
- You can see the FULL code above
- You know exactly what data sources exist and how many datasets
- Answer based on what you actually implemented
- Reference specific code lines or components
- If you see a bug or issue in your code, acknowledge it honestly
- If the code shows "1 dataset" but the source has multiple datasets, that's your bug

Please answer the user's question with specific technical details from your implementation."""

            try:
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2048,  # More tokens for technical answers with full code
                    messages=[{"role": "user", "content": prompt}]
                )
                response = message.content[0].text
                self.add_user_message('gradio_developer', response)
                self.add_agent_message('gradio_developer', 'user', f"Answered: {user_input[:30]}...")
            except Exception as e:
                self.add_user_message('system', f"❌ Error: {e}")

        elif any(word in user_input.lower() for word in ['fix', 'regenerate', 'change', 'update', 'modify', 'improve']):
            # User wants to fix/regenerate code
            self.add_user_message('system', f"🔄 Regenerating with your feedback: '{user_input}'")

            # Add feedback to requirements
            requirements = {
                'screen_type': 'dashboard_navigation',
                'intent': 'Navigate through data pipeline',
                'data_sources': st.session_state.context.get('data_sources', {}),
                'user_feedback': user_input  # Include user feedback!
            }

            try:
                # Regenerate with feedback
                code = st.session_state.orchestrator.generate_ui_code(requirements, st.session_state.context)

                # Save updated code
                st.session_state.generated_code = code
                output_file = project_root / "generated_pipeline_dashboard.py"
                output_file.write_text(code, encoding='utf-8')
                st.session_state.dashboard_file = str(output_file)

                self.add_user_message('system', f"✅ Regenerated {len(code)} chars of code with your feedback!")
                self.add_user_message('system', "💡 Click 'Launch Gradio Dashboard' to see the updated version")
            except Exception as e:
                self.add_user_message('system', f"❌ Error regenerating: {e}")

        else:
            # General feedback
            response = f"I've noted your feedback: '{user_input}'"
            self.add_user_message('system', response)

    def save_chat(self, name: str):
        """Save current chat session"""
        saved = {
            'name': name,
            'timestamp': datetime.now().isoformat(),
            'user_messages': st.session_state.user_messages.copy(),
            'agent_messages': st.session_state.agent_messages.copy(),
            'user_msg_count': len(st.session_state.user_messages),
            'agent_msg_count': len(st.session_state.agent_messages)
        }
        st.session_state.chat_history.append(saved)
        st.success(f"💾 Saved: {name}")
        st.rerun()

    def load_chat(self, saved_chat: Dict):
        """Load a saved chat session"""
        st.session_state.user_messages = saved_chat['user_messages']
        st.session_state.agent_messages = saved_chat['agent_messages']
        st.success(f"📂 Loaded: {saved_chat['name']}")
        st.rerun()

    def export_chat(self, saved_chat: Dict):
        """Export chat as JSON"""
        json_str = json.dumps(saved_chat, indent=2)
        st.download_button(
            label="⬇️ Download JSON",
            data=json_str,
            file_name=f"{saved_chat['name']}.json",
            mime="application/json"
        )

    def run(self):
        """Main render loop"""

        # Auto-start if launched from run_ingestion.py
        if not st.session_state.initialized:
            st.session_state.initialized = True
            # Auto-load context on first run
            if not st.session_state.context:
                self.load_context()
            # Auto-generate if prompt was passed via CLI
            if st.session_state.get('auto_generate') and st.session_state.context:
                if 'generated_code' not in st.session_state:
                    # Add initial prompt message to user chat
                    if st.session_state.get('initial_prompt'):
                        self.add_user_message('user', st.session_state.initial_prompt)
                    # Generate dashboard
                    self.generate_dashboard()
                    st.session_state.auto_generate = False  # Only auto-generate once

        # Handle regenerate request
        if st.session_state.get('regenerate_requested'):
            st.session_state.regenerate_requested = False  # Clear flag
            # Clear previous generation
            if 'generated_code' in st.session_state:
                del st.session_state.generated_code
            if 'dashboard_file' in st.session_state:
                del st.session_state.dashboard_file
            # Trigger regeneration
            self.generate_dashboard()
            return  # Exit early since generate_dashboard calls st.rerun()

        # Title
        st.title("🎨 Agent Studio")
        st.caption("Collaborative AI Dashboard Generator")
        st.markdown("---")

        # 3-column layout
        col1, col2, col3 = st.columns([1, 2, 2])

        with col1:
            self.render_left_column()

        with col2:
            self.render_middle_column()

        with col3:
            self.render_right_column()


class StudioOrchestrator(UICodeOrchestrator):
    """Orchestrator that emits to both user and agent chats"""

    def __init__(self, user_callback=None, agent_callback=None):
        super().__init__()
        self.user_callback = user_callback  # For user chat (middle)
        self.agent_callback = agent_callback  # For agent chat (right)

    def generate_ui_code(self, requirements: Dict, context: Dict) -> str:
        """Generate with dual chat emissions"""

        # Notify user
        if self.user_callback:
            self.user_callback('system', "🎭 Starting two-agent generation...")

        # PHASE 1: UX DESIGNER
        if self.agent_callback:
            self.agent_callback('orchestrator', 'ux_designer', "PHASE 1: Please design the UI")

        design_spec = self.ux_designer.design(requirements)

        if self.agent_callback:
            self.agent_callback('ux_designer', 'orchestrator', f"Design complete: {design_spec.screen_type}", {
                'components': len(design_spec.components),
                'patterns': design_spec.patterns
            })

        if self.user_callback:
            self.user_callback('ux_designer', f"✅ Design complete!")

        # PHASE 2: GRADIO DEVELOPER
        if self.agent_callback:
            self.agent_callback('orchestrator', 'gradio_developer', "PHASE 2: Please implement this design", {
                'design_spec': design_spec.to_dict()
            })

        gradio_code = self.gradio_developer.build(design_spec, context)

        if self.agent_callback:
            self.agent_callback('gradio_developer', 'orchestrator', f"Implementation complete: {len(gradio_code)} chars")

        if self.user_callback:
            self.user_callback('gradio_developer', f"✅ Implementation complete!")

        return gradio_code


# Entry point
class HybridStudioWrapper:
    """
    Wrapper around HybridCodeGenerator that provides same interface as StudioOrchestrator
    but with 92% token savings via snippet assembly + LLM fallback

    Usage: Drop-in replacement for StudioOrchestrator
    - 80% of requests: Uses snippets (~277 tokens)
    - 20% of requests: Falls back to LLM (~9,000 tokens)
    - Average: ~3,202 tokens (92% savings vs 40,000 baseline)
    """

    def __init__(self, user_callback=None, agent_callback=None):
        from src.agents.hybrid_code_generator import HybridCodeGenerator

        # Create message callback that streams to Streamlit
        self.chatter_lines = []

        def streaming_callback(message):
            """Callback that accumulates messages for streaming display"""
            self.chatter_lines.append(message)
            # Update the chatter placeholder if it exists
            if 'chatter_placeholder' in st.session_state and st.session_state.chatter_placeholder:
                st.session_state.chatter_placeholder.code("\n".join(self.chatter_lines), language="text")

        self.hybrid_generator = HybridCodeGenerator(message_callback=streaming_callback)
        self.user_callback = user_callback
        self.agent_callback = agent_callback

        # Expose agents for Q&A (agent_studio.py needs these for chat)
        self.ux_designer = self.hybrid_generator.orchestrator.ux_designer
        self.gradio_developer = self.hybrid_generator.orchestrator.gradio_developer

        print("[HybridStudioWrapper] Initialized - using snippet-first approach")

    def generate_code_with_capture(self, requirements: Dict, context: Dict) -> tuple[str, str]:
        """
        Generate code while capturing all agent output (stdout/stderr)
        Returns: (code, captured_chatter)
        """
        # Create buffers to capture output
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        # Capture all output during generation
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            try:
                # Notify user
                if self.user_callback:
                    self.user_callback('system', "[Hybrid] Starting generation (snippet-first approach)...")

                # Notify agents
                if self.agent_callback:
                    self.agent_callback('orchestrator', 'pattern_matcher', "PHASE 0: Matching to snippet pattern...")

                # Generate with hybrid system (verbose output will be captured)
                code = self.hybrid_generator.generate(requirements, context)

                # Get stats
                stats = self.hybrid_generator.get_stats()
                total_tokens = stats.get('total_tokens_used', 0)

                # Notify completion with token count
                if self.user_callback:
                    if self.hybrid_generator.snippet_hits > 0:
                        msg = f"[Hybrid] Complete! Used {total_tokens:,} tokens (snippet hit!)"
                    else:
                        msg = f"[Hybrid] Complete! Used {total_tokens:,} tokens (LLM generation)"

                    msg += f" | Hit rate: {stats['hit_rate']:.1f}%"
                    self.user_callback('system', msg)

                # Notify agent chat
                if self.agent_callback:
                    if self.hybrid_generator.snippet_hits > 0:
                        self.agent_callback('pattern_matcher', 'orchestrator',
                            f"Pattern matched! Generated {len(code):,} chars with {total_tokens} tokens")
                    else:
                        self.agent_callback('orchestrator', 'user',
                            f"LLM fallback complete. Generated {len(code):,} chars")

            except Exception as e:
                # Capture any errors too
                print(f"[ERROR] Generation failed: {str(e)}")
                code = f"# Error during generation: {str(e)}"

        # Combine stdout and stderr
        chatter = stdout_buffer.getvalue()
        errors = stderr_buffer.getvalue()
        if errors:
            chatter += f"\n\n{'='*80}\nERRORS\n{'='*80}\n{errors}"

        return code, chatter

    def generate_ui_code(self, requirements: Dict, context: Dict) -> str:
        """Legacy method for backwards compatibility - returns only code"""
        code, chatter = self.generate_code_with_capture(requirements, context)
        return code


if __name__ == "__main__":
    studio = AgentStudio()
    studio.run()