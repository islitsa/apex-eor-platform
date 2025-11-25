"""
Quick test script to verify collaborative agent system is ready
"""

import os
import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load .env file
from dotenv import load_dotenv
load_dotenv()

print("="*70)
print("COLLABORATIVE AGENT SYSTEM - SETUP TEST")
print("="*70)

# Test 1: Check API Key
print("\n[1/5] Checking API Key...")
api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key:
    print(f"  [OK] ANTHROPIC_API_KEY is set (starts with: {api_key[:10]}...)")
else:
    print("  [ERROR] ANTHROPIC_API_KEY not set!")
    print("  Set it: set ANTHROPIC_API_KEY=your-key-here")
    sys.exit(1)

# Test 2: Check AutoGen imports
print("\n[2/5] Checking AutoGen installation...")
try:
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
    from autogen_ext.models.anthropic import AnthropicChatCompletionClient
    print("  [OK] AutoGen v0.10+ is properly installed")
except ImportError as e:
    print(f"  [ERROR] AutoGen import failed: {e}")
    print("  Install: pip install pyautogen autogen-ext[anthropic]")
    sys.exit(1)

# Test 3: Check context
print("\n[3/5] Checking pipeline context...")
try:
    from shared_state import PipelineState
    context = PipelineState.load_context(check_freshness=False)
    if context:
        sources = len(context.get('data_sources', {}))
        records = context.get('summary', {}).get('human_readable_records', 'Unknown')
        print(f"  [OK] Context loaded: {sources} data sources, {records} records")
    else:
        print("  [WARNING] No context found")
        print("  Generate it: python scripts/pipeline/run_ingestion.py --generate-context")
except Exception as e:
    print(f"  [ERROR] Context check failed: {e}")
    sys.exit(1)

# Test 4: Test Anthropic client creation
print("\n[4/5] Testing Anthropic client...")
try:
    client = AnthropicChatCompletionClient(
        model="claude-3-5-sonnet-20241022",
        api_key=api_key
    )
    print("  [OK] Anthropic client created successfully")
except Exception as e:
    print(f"  [ERROR] Client creation failed: {e}")
    sys.exit(1)

# Test 5: Test collaborative system import
print("\n[5/5] Testing collaborative system...")
try:
    from src.ui.agent_collaborative_system import CollaborativeUIGenerator, EnhancedAgentRunner
    print("  [OK] Collaborative system imports successfully")
except Exception as e:
    print(f"  [ERROR] Import failed: {e}")
    sys.exit(1)

# All tests passed!
print("\n" + "="*70)
print("SUCCESS! All tests passed!")
print("="*70)
print("\nYou're ready to run the collaborative agent system!")
print("\nLaunch with:")
print("  python scripts/pipeline/run_ingestion.py --generate-context --launch-ui collaborate")
print("\nOr:")
print("  start_collaborative_ui.bat")
print("\n" + "="*70)
