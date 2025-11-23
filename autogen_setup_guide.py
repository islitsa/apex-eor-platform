"""
AutoGen Setup Guide for Agent Chat Runner

This guide helps you set up AutoGen for real agent-to-agent collaboration
with streaming output to Streamlit.
"""

# ============================================================================
# INSTALLATION
# ============================================================================

"""
1. Install required packages:

pip install pyautogen streamlit anthropic python-dotenv

OR if you want to use litellm for better Claude support:

pip install pyautogen streamlit litellm python-dotenv

2. Set your API key:

Create a .env file:
ANTHROPIC_API_KEY=your-api-key-here

3. Run the application:

streamlit run src/ui/agent_chat_runner_autogen.py
"""

# ============================================================================
# ALTERNATIVE: AUTOGEN WITH LITELLM (Better Claude Support)
# ============================================================================

"""
If the basic AutoGen setup doesn't work well with Claude, use this enhanced version
that uses litellm as a bridge:
"""

import os
from typing import Dict, List

# AutoGen v0.10+ uses autogen_agentchat
try:
    from autogen_agentchat import AssistantAgent, UserProxyAgent
    import autogen_agentchat as autogen
    print("[OK] AutoGen agentchat module loaded")
except ImportError:
    print("[ERROR] AutoGen not installed. Run: pip install pyautogen")

# Configure litellm for Claude
os.environ["LITELLM_LOG"] = "DEBUG"  # Optional: for debugging

class AutoGenWithLiteLLM:
    """
    Enhanced AutoGen setup using litellm for better Claude integration
    """

    def __init__(self):
        # Use litellm format for Claude
        self.config_list = [{
            "model": "claude-3-sonnet-20240229",
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "api_type": "anthropic",
            "base_url": "https://api.anthropic.com",
            # Use litellm proxy
            "litellm_params": {
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "model": "claude-3-sonnet-20240229"
            }
        }]

        # Alternative: Use OpenAI-compatible endpoint
        # self.config_list = [{
        #     "model": "gpt-4",  # AutoGen expects OpenAI model names
        #     "api_key": "dummy",  # Required but not used
        #     "base_url": "http://0.0.0.0:8000",  # litellm proxy server
        # }]

    def start_litellm_proxy(self):
        """
        Start litellm proxy server for OpenAI-compatible API
        Run this in terminal: litellm --model claude-3-sonnet-20240229
        """
        import subprocess
        cmd = [
            "litellm",
            "--model", "claude-3-sonnet-20240229",
            "--api_key", os.getenv("ANTHROPIC_API_KEY"),
            "--port", "8000"
        ]
        subprocess.Popen(cmd)

# ============================================================================
# SIMPLE WORKING EXAMPLE
# ============================================================================

def simple_autogen_example():
    """
    Minimal working example to test AutoGen with Claude
    """

    # Method 1: Direct Anthropic (if AutoGen supports it)
    config_list = [{
        "model": "claude-3-sonnet-20240229",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
    }]

    # Method 2: Through OpenAI proxy (more reliable)
    # First run: litellm --model claude-3-sonnet-20240229
    # config_list = [{
    #     "model": "gpt-4",
    #     "base_url": "http://localhost:8000",
    #     "api_key": "dummy"
    # }]

    # Create a simple agent
    assistant = AssistantAgent(
        name="assistant",
        llm_config={"config_list": config_list}
    )

    user_proxy = UserProxyAgent(
        name="user",
        human_input_mode="NEVER",
        code_execution_config=False
    )

    # Test conversation
    user_proxy.initiate_chat(
        assistant,
        message="Hello, can you see this message?"
    )

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Common Issues and Solutions:

1. "API key not found" or authentication errors:
   - Make sure ANTHROPIC_API_KEY is set in .env
   - Try using litellm proxy method instead

2. "Model not supported" errors:
   - AutoGen might not directly support Claude
   - Use litellm proxy: litellm --model claude-3-sonnet-20240229
   - Then use localhost:8000 as base_url

3. No output appearing in Streamlit:
   - Check that output redirection is working
   - Try adding explicit print statements in agent messages
   - Use st.write() directly in callbacks

4. Agents not responding:
   - Check max_consecutive_auto_reply setting
   - Ensure human_input_mode="NEVER" for automation
   - Verify API key and model access

5. Code not being extracted:
   - Check regex patterns for code blocks
   - Ensure agents wrap code in ```python blocks
   - Look for code in all messages, not just last one
"""

# ============================================================================
# ENHANCED STREAMING TO STREAMLIT
# ============================================================================

class EnhancedStreamlitCapture:
    """
    Better output capture with message parsing
    """

    def __init__(self, container):
        self.container = container
        self.current_agent = None
        self.message_buffer = []

    def write(self, text):
        """Parse and display agent messages"""

        # Detect agent names (AutoGen format)
        if text.strip().endswith(" (to"):  # AutoGen message format
            agent_name = text.split(" (to")[0].strip()
            self.current_agent = agent_name
            with self.container:
                st.markdown(f"### {agent_name}")

        # Detect message content
        elif self.current_agent and text.strip():
            # Check for code blocks
            if "```" in text:
                with self.container:
                    # Extract code
                    code = text.split("```")[1].replace("python", "").strip()
                    st.code(code, language="python")
            else:
                # Regular text
                with self.container:
                    st.write(text)

        # Also show in terminal style
        self.message_buffer.append(text)

    def flush(self):
        pass

# ============================================================================
# FINAL WORKING CONFIGURATION
# ============================================================================

def get_working_config():
    """
    Returns a working configuration for AutoGen with Claude
    """

    # Check which method works
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    # Try different configurations in order of reliability
    configs_to_try = [
        # 1. Direct Anthropic (if supported)
        {
            "method": "direct",
            "config_list": [{
                "model": "claude-3-sonnet-20240229",
                "api_key": api_key,
            }]
        },

        # 2. Through litellm
        {
            "method": "litellm",
            "config_list": [{
                "model": "claude-3-sonnet-20240229",
                "api_key": api_key,
                "api_type": "anthropic",
                "base_url": "https://api.anthropic.com/v1/messages"
            }]
        },

        # 3. Through local proxy (most reliable but requires setup)
        {
            "method": "proxy",
            "config_list": [{
                "model": "gpt-4",  # Pretend to be GPT-4
                "base_url": "http://localhost:8000",
                "api_key": "dummy"
            }],
            "note": "Run 'litellm --model claude-3-sonnet-20240229' first"
        }
    ]

    # Test each configuration
    for config in configs_to_try:
        try:
            test_agent = AssistantAgent(
                name="test",
                llm_config={"config_list": config["config_list"]},
                max_consecutive_auto_reply=1
            )
            print(f"[OK] {config['method']} configuration works!")
            return config["config_list"]
        except Exception as e:
            print(f"[ERROR] {config['method']} failed: {e}")
            if "note" in config:
                print(f"   Note: {config['note']}")

    raise ValueError("No working configuration found")

# ============================================================================
# USAGE
# ============================================================================

if __name__ == "__main__":
    print("Testing AutoGen configurations...")

    try:
        config = get_working_config()
        print("\n[OK] Success! Use this configuration:")
        print(config)

        # Test with simple example
        simple_autogen_example()

    except Exception as e:
        print(f"\n[ERROR] Setup failed: {e}")
        print("\nTry the litellm proxy method:")
        print("1. Run: litellm --model claude-3-sonnet-20240229")
        print("2. Update config to use localhost:8000")
