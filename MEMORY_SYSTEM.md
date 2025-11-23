# Memory System - Iterative Learning

## Overview

The Gradio Developer agent now has an **active memory system** that learns from previous generations within a session. This enables iterative refinement where the agent remembers what it tried before and what feedback it received.

## How It Works

### Automatic Recording
Every time the agent generates code, it automatically records:
- **Screen type** and **intent**
- **Generated code** (first 2000 chars)
- **Components used** (gr.Button, gr.Textbox, etc.)
- **User feedback** (if provided)

### Memory Injection
When generating a new iteration, the agent:
1. **Retrieves memory** from previous attempts
2. **Injects context** into the LLM prompt
3. **Shows user feedback** explicitly
4. **Includes code snippets** from past versions

### Learning from Mistakes
The memory context tells the LLM:
```
PREVIOUS IMPLEMENTATIONS IN THIS SESSION:
==========================================================

Initial version: dashboard
   Components used: gr.Button, gr.Markdown
   Code length: 1500 chars

Version 2: dashboard
   Components used: gr.Button, gr.Markdown, gr.Textbox
   ⚠️  USER SAID: "make the button bigger"
   This version was created in response to that feedback

LEARNING FROM HISTORY:
- Review previous versions and what feedback they received
- If user complained about something, DON'T repeat that mistake
- Build incrementally on what worked
- Address the specific issues mentioned in feedback
```

## Usage in Agent Studio

### Passing User Feedback

To trigger memory-based refinement, pass `user_feedback` in the context:

```python
context = {
    'data_sources': {...},
    'user_feedback': "Make cards bigger and add more spacing"
}

code = agent.build(design_spec, context)
```

The agent will:
1. Remember all previous versions in this session
2. See your feedback explicitly
3. Avoid repeating mistakes you complained about
4. Build incrementally on what worked

### Session Lifecycle

**Memory persists for:**
- ✅ Multiple generations within same agent instance
- ✅ Entire Studio session

**Memory is lost when:**
- ❌ Agent instance is recreated
- ❌ Studio is restarted
- ❌ New session begins

**Note:** This is different from **Favorites** (which persist across sessions to disk).

## Example Workflow

```python
# Generation 1: Initial dashboard
context_v1 = {'data_sources': data, 'user_feedback': None}
code_v1 = agent.build(design_spec, context_v1)
# Memory: 1 entry

# Generation 2: User wants bigger cards
context_v2 = {'data_sources': data, 'user_feedback': "Make cards bigger"}
code_v2 = agent.build(design_spec, context_v2)
# Memory: 2 entries, LLM sees feedback from v1

# Generation 3: User wants different colors
context_v3 = {'data_sources': data, 'user_feedback': "Use blue instead of green"}
code_v3 = agent.build(design_spec, context_v3)
# Memory: 3 entries, LLM sees all previous feedback
```

Each generation sees the full history and learns from it.

## Technical Details

### Memory Storage
Location: `GradioImplementationAgent.implementation_history` (in-memory list)

Structure per entry:
```python
{
    "screen_type": "dashboard",
    "intent": "create a pipeline dashboard",
    "code_length": 2500,
    "constraints_applied": [],
    "code_summary": "gr.Button, gr.Markdown, .click() handler",
    "full_code": "import gradio...",  # First 2000 chars
    "user_feedback": "make buttons bigger"  # Optional
}
```

### Key Methods

**`_add_to_memory(design_spec, code, constraints, user_feedback)`**
- Called automatically after each generation
- Stores implementation details
- Located at [gradio_developer.py:496-516](src/agents/gradio_developer.py#L496-L516)

**`_get_memory_context()`**
- Formats memory for injection into prompts
- Returns formatted string with history + learning instructions
- Located at [gradio_developer.py:569-602](src/agents/gradio_developer.py#L569-L602)

### Activation Points

Memory is now active at:

1. **[gradio_developer.py:107-113](src/agents/gradio_developer.py#L107-L113)** - Records after generation
2. **[gradio_developer.py:210](src/agents/gradio_developer.py#L210)** - Retrieves memory context
3. **[gradio_developer.py:244-257](src/agents/gradio_developer.py#L244-L257)** - Injects into prompt

## Differences from Favorites

| Feature | Memory System | Favorites |
|---------|---------------|-----------|
| **Scope** | Session-only | Persistent across sessions |
| **Storage** | RAM | Disk (JSON) |
| **Purpose** | Iterative learning | Bookmarking good designs |
| **Trigger** | Automatic | Manual save |
| **Data** | Component summaries + feedback | Complete code |
| **Lifespan** | Until agent restarts | Forever |

## Benefits

1. **Avoid Repetition**: Agent won't make the same mistake twice
2. **Incremental Refinement**: Builds on what worked before
3. **Feedback Awareness**: Explicitly addresses user complaints
4. **Session Context**: Understands the conversation flow
5. **Zero Manual Work**: Happens automatically

## Limitations

1. **Session-Scoped**: Lost when agent instance is destroyed
2. **No Persistence**: Doesn't survive Studio restart
3. **Memory Size**: Only stores first 2000 chars of code
4. **No Cross-Session**: Can't learn from yesterday's session

For persistent storage of favorite designs, use the **Favorites system** instead.

## Future Enhancements

Potential improvements:
- **Persistent memory**: Save to disk like Favorites
- **Cross-session learning**: Load memory from previous sessions
- **Pattern extraction**: Identify common feedback themes
- **Automatic suggestions**: "Based on past feedback, should I...?"
- **Memory limits**: Cap history size for performance
