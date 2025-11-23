# Collaborative Agent UI Generator

## Overview

This system uses **Microsoft AutoGen v0.10+** to enable **real multi-agent collaboration** for UI generation. Unlike sequential agent calls, this system allows agents to:

- **Critique** each other's work
- **Iterate** on designs and implementations
- **Refine** through multiple feedback rounds
- **Collaborate** naturally to reach better solutions

## Architecture

### The Four-Agent Team

1. **UX Designer** (Visionary)
   - Proposes initial designs
   - Adapts based on technical constraints
   - Explains design decisions
   - Critiques implementations for UX issues

2. **Gradio Developer** (Realist)
   - Evaluates design feasibility
   - Provides technical constraints feedback
   - Suggests alternatives when needed
   - Implements final designs with best practices

3. **UX Critic** (Quality Reviewer)
   - Reviews implementations for UX standards
   - Identifies missing UX elements
   - Validates accessibility and user workflows
   - Suggests improvements

4. **Code Reviewer** (Quality Assurance)
   - Checks code for errors and completeness
   - Ensures best practices
   - Validates functionality
   - Verifies production-readiness

### Collaboration Flow

```
1. UX Designer proposes design
   ↓
2. Gradio Developer reviews feasibility
   ↓
3. They iterate until agreement
   ↓
4. Developer implements design
   ↓
5. UX Critic reviews implementation
   ↓
6. Code Reviewer ensures quality
   ↓
7. Developer addresses concerns
   ↓
8. Final refined code delivered
```

## Installation

### 1. Install Dependencies

```bash
# Install AutoGen v0.10+ with Anthropic support
pip install pyautogen autogen-ext[anthropic]

# Other dependencies
pip install streamlit python-dotenv
```

### 2. Set API Key

```bash
# Windows
set ANTHROPIC_API_KEY=your-key-here

# Linux/Mac
export ANTHROPIC_API_KEY=your-key-here
```

### 3. Run the System

**Option 1: Use the launcher**
```bash
run_collaborative_agents.bat
```

**Option 2: Direct command**
```bash
streamlit run src\ui\agent_collaborative_system.py
```

## How It Works

### AutoGen v0.10+ Features Used

1. **RoundRobinGroupChat**: Agents take turns speaking in order
2. **TextMentionTermination**: Conversation ends when "COLLABORATION_COMPLETE" appears
3. **MaxMessageTermination**: Safety limit of 20 messages
4. **AnthropicClient**: Direct Claude 3.5 Sonnet integration
5. **async/await**: Streaming output to Streamlit in real-time

### Output Streaming

The system streams agent conversations to two panels:

- **Chat Panel** (Left): Formatted agent messages with context
- **Terminal Panel** (Right): Raw conversation flow

You see the ACTUAL agent-to-agent communication happening live!

## Why This Is Better

### vs. Sequential Agents (Your Original System)

| Feature | Sequential | Collaborative |
|---------|-----------|---------------|
| Agent interaction | None | Full dialogue |
| Critique rounds | No | Yes (multiple) |
| Design iteration | No | Yes (adaptive) |
| Code refinement | No | Yes (reviewer feedback) |
| Quality assurance | Manual | Built-in (2 reviewers) |
| Output quality | Good | Excellent |

### vs. Monkey-Patching print()

| Approach | Complexity | Reliability | Coverage |
|----------|-----------|-------------|----------|
| Monkey-patch | High | Medium | Partial |
| AutoGen streams | Low | High | Complete |

AutoGen **handles all output streaming natively** - no need to intercept print statements!

## Benefits of Real Collaboration

### 1. Better Designs
UX Designer proposes, Developer provides constraints, they iterate to find optimal solutions.

### 2. Fewer Bugs
Code Reviewer catches issues before code is finalized.

### 3. Better UX
UX Critic ensures implementations meet accessibility and usability standards.

### 4. Learning Opportunity
Watch agents negotiate trade-offs between ideal designs and technical limitations.

## Configuration

### Changing Models

Edit `_create_model_client()` in `agent_collaborative_system.py`:

```python
return AnthropicClient(
    model="claude-3-5-sonnet-20241022",  # Change this
    api_key=self.api_key
)
```

Available models:
- `claude-3-5-sonnet-20241022` (Best balance)
- `claude-3-opus-20240229` (Most capable, slower)
- `claude-3-haiku-20240307` (Fastest, cheaper)

### Adjusting Conversation Length

Edit termination conditions:

```python
termination = TextMentionTermination("COLLABORATION_COMPLETE") | MaxMessageTermination(20)
# Change 20 to allow more/fewer messages
```

### Changing Agent Behavior

Edit system messages in `_create_collaborative_agents()` to adjust:
- Tone and style
- Focus areas
- Critique strictness
- Implementation preferences

## Troubleshooting

### "AutoGen not installed"
```bash
pip install pyautogen autogen-ext[anthropic]
```

### "ANTHROPIC_API_KEY not set"
```bash
# Check if set
echo %ANTHROPIC_API_KEY%

# Set it
set ANTHROPIC_API_KEY=your-key-here
```

### "No context found"
```bash
# Generate context first
python scripts\pipeline\run_ingestion.py --generate-context
```

### Agents not collaborating properly

Check the system messages - they should:
- Encourage dialogue
- Request feedback
- Specify when to critique
- Define collaboration style

### Output not streaming

AutoGen v0.10+ uses async streaming. Make sure:
- Using `async def generate_with_collaboration()`
- Using `async for message in team.run_stream()`
- Running with `asyncio.run()` from synchronous context

## Advanced Usage

### Custom Agent Teams

Add more specialists:

```python
# Add a performance specialist
self.performance_expert = AssistantAgent(
    name="Performance_Expert",
    model_client=model_client,
    system_message="You optimize code for performance..."
)
```

### Custom Termination Conditions

```python
# End when specific criteria met
def custom_termination(message):
    return (
        "```python" in message.content and
        "TESTED" in message.content and
        len(message.content) > 500
    )
```

### Saving Conversation History

```python
# After generation
conversation_log = result.messages
with open("conversation.json", "w") as f:
    json.dump([str(m) for m in conversation_log], f, indent=2)
```

## What's Next

### Potential Enhancements

1. **Memory System**: Agents remember past projects
2. **User Feedback**: Incorporate user critique into iteration
3. **Visual Preview**: Show UI mockups before implementation
4. **A/B Testing**: Generate multiple variants, agents vote
5. **Deployment**: Agents help deploy and monitor

### Integration with Existing System

This collaborative system can replace the orchestrator in your pipeline:

```python
# In run_ingestion.py
from src.ui.agent_collaborative_system import CollaborativeUIGenerator

generator = CollaborativeUIGenerator(chat_container, terminal_container)
code = await generator.generate_with_collaboration(requirements, context)
```

## Credits

- **Microsoft AutoGen**: Multi-agent framework
- **Anthropic Claude**: AI reasoning engine
- **Streamlit**: Real-time UI framework
- **Opus (Claude)**: Architecture design

## License

Same as parent project.

---

**Ready to see REAL agent collaboration?**

Run: `run_collaborative_agents.bat`

Watch as agents negotiate, critique, and refine their way to exceptional UI code!
