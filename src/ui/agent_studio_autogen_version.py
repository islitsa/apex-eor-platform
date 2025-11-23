"""
Agent Studio - Fixed Version with Preserved Chat History
No recursion errors and full agent conversation history preserved
"""

import streamlit as st
import os
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

# AutoGen imports
try:
    import autogen
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
    AUTOGEN_VERSION = autogen.__version__
except ImportError as e:
    AUTOGEN_AVAILABLE = False
    AUTOGEN_ERROR = str(e)

from shared_state import PipelineState
from src.agents.ui_orchestrator import UICodeOrchestrator
from src.agents.ux_designer import UXDesignerAgent, DesignSpec
from src.agents.gradio_developer import GradioImplementationAgent


class AgentStudio:
    """
    Interactive Agent Studio with preserved chat history
    """
    
    def __init__(self):
        # Get API keys
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not self.openai_key and not self.anthropic_key:
            raise ValueError("Need OPENAI_API_KEY or ANTHROPIC_API_KEY")
        
        # Setup config
        self.config_list = self._get_config()
        
        # Create agents
        self._create_studio_agents()
        
        # Initialize orchestrator for knowledge access
        self.orchestrator = UICodeOrchestrator()
        
        # Store the original print function BEFORE any monkey-patching
        import builtins
        self.original_print = builtins.print
        
    def _get_config(self):
        """Get LLM configuration"""
        if self.openai_key:
            return [{
                "model": "gpt-4o",
                "api_key": self.openai_key,
            }]
        else:
            # For Claude via litellm proxy
            return [{
                "model": "gpt-4",
                "api_base": "http://localhost:8000",
                "api_key": "dummy"
            }]
    
    def _create_studio_agents(self):
        """Create interactive studio agents"""
        
        llm_config = {
            "config_list": self.config_list,
            "temperature": 0.7,
        }
        
        # UX Designer - Interactive version with planning
        self.ux_designer = AssistantAgent(
            name="UX_Designer",
            llm_config=llm_config,
            system_message="""You are a Senior UX Designer in an interactive studio session.

CRITICAL: You MUST use step-by-step reasoning and planning before designing:

1. ANALYZE THE REQUEST (Chain-of-Thought):
   - What is the primary purpose? (monitoring, analysis, data entry, etc.)
   - Who are the users? (data engineers, analysts, operators, etc.)
   - What are the key metrics/data they need to see?
   - What actions do they need to perform?

2. PLAN THE DESIGN (Show your thinking):
   - List 3-4 design approaches you considered
   - Explain trade-offs of each approach
   - State which approach you recommend and WHY
   - Break down the layout into logical sections

3. DESIGN THE SOLUTION:
   - Provide detailed UI specification
   - Explain each design decision
   - Consider edge cases and error states

ALWAYS show your reasoning process. Start with "Let me think through this..." and walk through your analysis.

When users give feedback:
- Acknowledge the feedback
- Re-analyze with the new constraint
- Explain how you'll incorporate it
- Update your design specification

Be conversational and collaborative. This is an interactive session!"""
        )
        
        # Gradio Developer - Interactive version with planning
        self.gradio_developer = AssistantAgent(
            name="Gradio_Developer",
            llm_config=llm_config,
            system_message="""You are a Gradio Developer in an interactive studio session.

CRITICAL: You MUST plan and reason through implementation before coding:

1. ANALYZE THE DESIGN (Chain-of-Thought):
   - What Gradio components best fit each UI element?
   - What state management is needed?
   - What data flow patterns are required?
   - What edge cases need handling?

2. PLAN THE IMPLEMENTATION (Show your thinking):
   - Break down the design into logical components
   - Identify dependencies and data flow
   - Consider performance implications (e.g., 200M+ records)
   - List potential issues and how you'll handle them

3. IMPLEMENT THE SOLUTION:
   - Write clean, well-documented code
   - Include error handling
   - Add comments explaining complex logic
   - Make it production-ready

ALWAYS start with "Let me plan the implementation..." and show your reasoning.

When users report issues or request changes:
- Acknowledge the issue/request
- Analyze the root cause
- Explain your fix approach
- Provide updated code with explanation

Always output complete, runnable code in ```python blocks.
Be helpful and responsive to user needs."""
        )
        
        # Studio Assistant - Helps coordinate with planning
        self.studio_assistant = AssistantAgent(
            name="Studio_Assistant",
            llm_config=llm_config,
            system_message="""You are the Studio Assistant helping coordinate the session.

Your role:
1. Interpret user requests and break them down
2. Ensure agents follow proper planning/CoT process
3. Direct questions to the right agent
4. Summarize discussions and decisions
5. Keep the session productive and focused

IMPORTANT: If an agent jumps to solution without showing their reasoning:
- Ask them to "show your thinking process"
- Request they analyze the problem first
- Ensure they explain their design/implementation choices

You help facilitate communication between the user and the specialized agents."""
        )
        
        # User proxy for the studio
        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config=False
        )
    
    def process_user_message(self, message: str, context: Dict) -> Dict:
        """
        Process user message and capture ALL agent conversation
        Returns complete conversation history
        """
        
        # Determine message type
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['design', 'layout', 'ui', 'interface', 'screen']):
            message_type = 'design'
        elif any(word in message_lower for word in ['implement', 'code', 'build', 'create']):
            message_type = 'code'
        elif any(word in message_lower for word in ['fix', 'change', 'update', 'modify', 'add', 'remove']):
            message_type = 'feedback'
        elif '?' in message:
            message_type = 'question'
        else:
            message_type = 'general'
        
        # Create appropriate group chat based on message type
        if message_type in ['design', 'feedback']:
            agents = [self.user_proxy, self.ux_designer, self.gradio_developer]
        elif message_type == 'code':
            agents = [self.user_proxy, self.gradio_developer]
        else:
            agents = [self.user_proxy, self.studio_assistant, self.ux_designer, self.gradio_developer]
        
        # Setup group chat
        groupchat = GroupChat(
            agents=agents,
            messages=[],
            max_round=6,
            speaker_selection_method="auto"
        )
        
        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config={"config_list": self.config_list}
        )
        
        # Add context to message
        enhanced_message = f"""{message}

Context:
- Data Sources: {list(context.get('data_sources', {}).keys())}
- Total Records: {context.get('summary', {}).get('human_readable_records', 'Unknown')}
"""
        
        # Capture ALL output including agent chatter
        captured_conversation = []
        
        def capture_print(*args, **kwargs):
            """Capture everything without causing recursion"""
            text = ' '.join(str(a) for a in args)
            captured_conversation.append(text)
            # Use the ORIGINAL print to avoid recursion
            # Handle Unicode by encoding as UTF-8 with error replacement for Windows console
            try:
                self.original_print(*args, **kwargs)
            except UnicodeEncodeError:
                # Fallback: replace problematic Unicode characters with ASCII equivalents
                safe_args = []
                for arg in args:
                    s = str(arg)
                    # Replace common Unicode characters with ASCII
                    s = s.replace('\u2192', '->')  # →
                    s = s.replace('\u2190', '<-')  # ←
                    s = s.replace('\u2713', '[OK]')  # ✓
                    s = s.replace('\u2717', '[X]')  # ✗
                    s = s.replace('\u2022', '*')  # •
                    # Remove any remaining non-ASCII characters
                    s = s.encode('ascii', 'replace').decode('ascii')
                    safe_args.append(s)
                self.original_print(*safe_args, **kwargs)
        
        # Monkey-patch print to capture output
        import builtins
        builtins.print = capture_print
        
        try:
            # Process message
            self.user_proxy.initiate_chat(manager, message=enhanced_message)
        finally:
            # Restore original print
            builtins.print = self.original_print
        
        # Extract code if any
        code = self._extract_code(groupchat.messages)
        
        # Parse the captured conversation for display
        parsed_messages = self._parse_conversation(captured_conversation)
        
        return {
            'type': message_type,
            'responses': groupchat.messages,
            'code': code if code != "# No code generated" else None,
            'captured_conversation': captured_conversation,
            'parsed_messages': parsed_messages
        }
    
    def _parse_conversation(self, conversation: List[str]) -> List[Dict]:
        """Parse captured conversation into structured messages"""
        parsed = []
        current_speaker = None
        current_content = []
        
        for line in conversation:
            # Check for agent speaking
            if "UX_Designer" in line and "(to" in line:
                # Save previous message if exists
                if current_speaker and current_content:
                    parsed.append({
                        'speaker': current_speaker,
                        'content': '\n'.join(current_content)
                    })
                current_speaker = "UX_Designer"
                current_content = []
            elif "Gradio_Developer" in line and "(to" in line:
                if current_speaker and current_content:
                    parsed.append({
                        'speaker': current_speaker,
                        'content': '\n'.join(current_content)
                    })
                current_speaker = "Gradio_Developer"
                current_content = []
            elif "Studio_Assistant" in line and "(to" in line:
                if current_speaker and current_content:
                    parsed.append({
                        'speaker': current_speaker,
                        'content': '\n'.join(current_content)
                    })
                current_speaker = "Studio_Assistant"
                current_content = []
            elif current_speaker and line.strip() and "-----" not in line and "user_proxy" not in line:
                # Add to current speaker's content
                current_content.append(line)
        
        # Save last message
        if current_speaker and current_content:
            parsed.append({
                'speaker': current_speaker,
                'content': '\n'.join(current_content)
            })
        
        return parsed
    
    def _extract_code(self, messages: List[Dict]) -> str:
        """Extract code from messages"""
        for message in reversed(messages):
            if message.get("name") == "Gradio_Developer":
                content = message.get("content", "")
                code_blocks = re.findall(r"```python\n(.*?)\n```", content, re.DOTALL)
                if code_blocks:
                    return code_blocks[-1]
        return "# No code generated"


def main():
    st.set_page_config(
        page_title="Agent Studio",
        page_icon="🎭",
        layout="wide"
    )
    
    # Header
    st.title("🎭 Agent Studio")
    st.markdown("**Interactive AI Development Environment**")
    
    # Check dependencies
    if not AUTOGEN_AVAILABLE:
        st.error(f"AutoGen not installed: {AUTOGEN_ERROR}")
        st.stop()
    
    # Initialize session state
    if 'studio' not in st.session_state:
        st.session_state.studio = AgentStudio()
    if 'context' not in st.session_state:
        st.session_state.context = None
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []  # Full history with agent chatter
    if 'generated_code' not in st.session_state:
        st.session_state.generated_code = None
    if 'initial_prompt' not in st.session_state:
        st.session_state.initial_prompt = None
    
    # Load context from pipeline
    if not st.session_state.context:
        with st.spinner("Loading pipeline context..."):
            context = PipelineState.load_context(check_freshness=False)
            if context:
                st.session_state.context = context
                
                # Auto-generate initial prompt from context
                datasets = list(context.get('data_sources', {}).keys())
                total_records = context.get('summary', {}).get('human_readable_records', 'Unknown')

                # Build processing status summary
                data_sources = context.get('data_sources', {})

                status_lines = []
                for ds_name, ds_info in data_sources.items():
                    proc_state = ds_info.get('processing_state', {})
                    parsed_info = ds_info.get('parsed', {}) or ds_info.get('parsing_results', {})

                    # Get file/table counts
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
                st.warning("No pipeline context found. Starting with blank slate.")
                st.session_state.context = {'data_sources': {}, 'summary': {}}
                st.session_state.initial_prompt = "Design a modern data dashboard"
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📋 Quick Actions")
        
        if st.button("🎨 Request Initial Design"):
            prompt = st.session_state.initial_prompt
            # Process and add to history
            with st.spinner("Agents collaborating..."):
                result = st.session_state.studio.process_user_message(prompt, st.session_state.context)
                st.session_state.conversation_history.append({
                    'role': 'user',
                    'content': prompt,
                    'agent_conversation': result['parsed_messages'],
                    'timestamp': datetime.now()
                })
                if result['code']:
                    st.session_state.generated_code = result['code']
                st.rerun()
        
        if st.button("💻 Generate Implementation"):
            prompt = "Implement the current design in Gradio"
            with st.spinner("Generating code..."):
                result = st.session_state.studio.process_user_message(prompt, st.session_state.context)
                st.session_state.conversation_history.append({
                    'role': 'user',
                    'content': prompt,
                    'agent_conversation': result['parsed_messages'],
                    'timestamp': datetime.now()
                })
                if result['code']:
                    st.session_state.generated_code = result['code']
                st.rerun()
        
        if st.button("🔄 Clear Chat"):
            st.session_state.conversation_history = []
            st.session_state.generated_code = None
            st.rerun()
        
        if st.button("💾 Save Chat History"):
            # Save complete conversation history
            history_file = project_root / f"agent_studio_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(history_file, 'w') as f:
                json.dump(st.session_state.conversation_history, f, indent=2, default=str)
            st.success(f"Saved to {history_file.name}")
        
        st.markdown("### 💡 Example Prompts")
        example_prompts = [
            "Make the charts bigger and more prominent",
            "Add date range filters to all data views",
            "Change the color scheme to dark mode",
            "Add export buttons for each chart",
            "Explain how the navigation works",
            "Why did you choose tabs over sidebar?",
            "Can you add real-time updates?",
            "Fix the layout - it's too cramped",
        ]
        
        for prompt in example_prompts:
            if st.button(f"_{prompt}_", key=prompt):
                with st.spinner("Processing..."):
                    result = st.session_state.studio.process_user_message(prompt, st.session_state.context)
                    st.session_state.conversation_history.append({
                        'role': 'user',
                        'content': prompt,
                        'agent_conversation': result['parsed_messages'],
                        'timestamp': datetime.now()
                    })
                    if result['code']:
                        st.session_state.generated_code = result['code']
                    st.rerun()
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Studio Chat")
        
        # Display conversation history with agent chatter preserved
        chat_container = st.container(height=500)
        with chat_container:
            for entry in st.session_state.conversation_history:
                # Show user message
                st.chat_message("user").write(entry['content'])
                
                # Show agent conversation
                if entry.get('agent_conversation'):
                    for msg in entry['agent_conversation']:
                        speaker = msg['speaker']
                        content = msg['content']
                        
                        if speaker == "UX_Designer":
                            with st.chat_message("assistant", avatar="🎨"):
                                st.markdown(f"**UX Designer:**")
                                st.write(content)
                        elif speaker == "Gradio_Developer":
                            with st.chat_message("assistant", avatar="⚙️"):
                                st.markdown(f"**Developer:**")
                                if "```python" in content:
                                    # Extract and display code properly
                                    parts = content.split("```python")
                                    st.write(parts[0])
                                    if len(parts) > 1:
                                        code_parts = parts[1].split("```")
                                        st.code(code_parts[0], language="python")
                                else:
                                    st.write(content)
                        elif speaker == "Studio_Assistant":
                            with st.chat_message("assistant", avatar="🎭"):
                                st.markdown(f"**Assistant:**")
                                st.write(content)
        
        # Chat input
        user_input = st.chat_input("Ask agents anything about the UI...")
        
        if user_input:
            # Process with agents
            with st.spinner("Agents are thinking..."):
                result = st.session_state.studio.process_user_message(
                    user_input, 
                    st.session_state.context
                )
                
                # Add to history with full agent conversation
                st.session_state.conversation_history.append({
                    'role': 'user',
                    'content': user_input,
                    'agent_conversation': result['parsed_messages'],
                    'timestamp': datetime.now()
                })
                
                # Update code if generated
                if result['code']:
                    st.session_state.generated_code = result['code']
            
            st.rerun()
    
    with col2:
        st.markdown("### 🎯 Current Context")
        
        # Show loaded context
        if st.session_state.context:
            datasets = st.session_state.context.get('data_sources', {})
            st.info(f"**Data Sources:** {len(datasets)}")
            for ds in list(datasets)[:5]:
                st.write(f"• {ds}")
            if len(datasets) > 5:
                st.write(f"• ...and {len(datasets)-5} more")
            
            summary = st.session_state.context.get('summary', {})
            if summary:
                st.write(f"**Records:** {summary.get('human_readable_records', 'N/A')}")
                st.write(f"**Size:** {summary.get('human_readable_size', 'N/A')}")
        
        st.markdown("### 📊 Session Stats")
        st.metric("Messages", len(st.session_state.conversation_history))
        
        total_agent_messages = sum(
            len(entry.get('agent_conversation', [])) 
            for entry in st.session_state.conversation_history
        )
        st.metric("Agent Responses", total_agent_messages)
    
    # Generated code section
    if st.session_state.generated_code:
        st.markdown("---")
        st.markdown("### 📄 Generated Code")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Save Code", type="primary"):
                path = project_root / "studio_generated_ui.py"
                path.write_text(st.session_state.generated_code)
                st.success(f"Saved to {path}")
        
        with col2:
            if st.button("🚀 Launch UI"):
                # Save and launch
                path = project_root / "studio_generated_ui.py"
                path.write_text(st.session_state.generated_code)
                import subprocess
                subprocess.Popen(["python", str(path)])
                st.success("UI launched! Check http://localhost:7860")
        
        with col3:
            if st.button("📋 Copy Code"):
                st.code(st.session_state.generated_code, language="python")
        
        # Show code
        with st.expander("View Code", expanded=False):
            st.code(st.session_state.generated_code, language="python")


if __name__ == "__main__":
    main()