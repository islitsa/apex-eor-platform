# Quick Start: Collaborative Agent UI Generator

## 🚀 Get Started in 3 Steps

### Step 1: Install (if not already done)

```bash
pip install pyautogen autogen-ext[anthropic] streamlit
```

### Step 2: Set Your API Key

```bash
set ANTHROPIC_API_KEY=your-api-key-here
```

### Step 3: Run!

```bash
# Easy way
run_collaborative_agents.bat

# Or direct
streamlit run src\ui\agent_collaborative_system.py
```

## 🎯 What You'll See

A Streamlit interface with two panels:

### Left Panel: Agent Collaboration
Watch the agents have REAL conversations:

```
UX Designer
I propose a 3-tab layout with master-detail pattern...

Gradio Developer
Good idea, but Gradio tabs have performance issues beyond 5 tabs.
Let me suggest using an accordion instead...

UX Designer
Excellent point! Let's use accordion for the main navigation...

[continues iterating]

Gradio Developer
Here's the final implementation:
```python
import gradio as gr
...
```

UX Critic
The implementation looks good. I'd suggest adding...

Code Reviewer
Code is complete and production-ready!

COLLABORATION_COMPLETE
```

### Right Panel: Terminal
Raw conversation flow with message counts

## ✅ Success Indicators

You'll know it's working when you see:

1. ✅ "Loaded X data sources" at the top
2. ✅ "Start Collaboration" button is clickable
3. ✅ After clicking, agents start conversing in real-time
4. ✅ Final code appears in the "Generated Code" expander

## ❌ Common Issues & Fixes

### "ANTHROPIC_API_KEY not set"
```bash
# Check if set
echo %ANTHROPIC_API_KEY%

# Set it
set ANTHROPIC_API_KEY=sk-ant-...
```

### "No context found"
```bash
# Generate context from your data first
python scripts\pipeline\run_ingestion.py --generate-context
```

### "AutoGen not installed"
```bash
pip install pyautogen autogen-ext[anthropic]
```

### Agents not responding
- Check your API key is valid
- Ensure you have API credits
- Try using Claude 3 Haiku (cheaper/faster) for testing

## 🎓 What Makes This Special

### vs. Your Old Sequential System

| Old Way | New Way |
|---------|---------|
| Designer generates → Done | Designer ↔ Developer iterate |
| No feedback loop | Multiple critique rounds |
| Single pass | Refinement until optimal |
| Can't adapt to constraints | Adapts to technical reality |

### Real Collaboration Example

**Old Way:**
```
1. UX Designer: Here's a design [done]
2. Developer: Here's code for that design [done]
```

**New Way:**
```
1. UX Designer: How about this design?
2. Developer: Good, but constraint X means we need to...
3. UX Designer: Ah! Then let's adjust to...
4. Developer: Perfect! Implementing...
5. UX Critic: Implementation looks good but...
6. Developer: Fixed! Here's final code.
```

## 🎨 Customization

### Change AI Model

Edit `agent_collaborative_system.py`:

```python
return AnthropicChatCompletionClient(
    model="claude-3-haiku-20240307",  # Faster, cheaper
    # or
    model="claude-3-opus-20240229",   # More capable
    api_key=self.api_key
)
```

### Adjust Collaboration Rounds

```python
termination = TextMentionTermination("COLLABORATION_COMPLETE") | MaxMessageTermination(30)
# Allow up to 30 messages instead of 20
```

### Add More Agents

```python
self.security_expert = AssistantAgent(
    name="Security_Expert",
    model_client=model_client,
    system_message="You review code for security vulnerabilities..."
)
```

## 📊 Monitoring API Usage

The system shows:
- Message count in terminal panel
- Each agent's contributions
- Total collaboration rounds

Typical session:
- Messages: 10-15
- Tokens: ~20-30K total
- Cost: ~$0.50-1.00 (with Sonnet)
- Time: 2-3 minutes

## 🔥 Pro Tips

1. **Let it finish**: Don't interrupt - collaboration improves with each round
2. **Watch the dialogue**: You'll learn about Gradio constraints
3. **Read the critiques**: UX and Code reviewers catch real issues
4. **Save good conversations**: The collaboration log is valuable
5. **Iterate on prompts**: Adjust requirements in the initial message

## 📚 Next Steps

Once it's working:

1. **Read [COLLABORATIVE_AGENTS_README.md](COLLABORATIVE_AGENTS_README.md)** for deep dive
2. **Experiment with agent personalities** by editing system messages
3. **Try different data contexts** (production, permits, completions)
4. **Compare outputs** to your old sequential system
5. **Integrate with your pipeline** using the existing orchestrator interface

## 🆘 Need Help?

1. Check [COLLABORATIVE_AGENTS_README.md](COLLABORATIVE_AGENTS_README.md)
2. Look at AutoGen docs: https://microsoft.github.io/autogen/
3. Test with simple example first (fewer data sources)
4. Enable debug mode in code

## 🎉 You're Ready!

Run `run_collaborative_agents.bat` and watch the magic happen!

The first time you see agents negotiating design trade-offs in real-time will blow your mind. 🤯
