# Regenerate Workflow Fix

## Problem Statement

The chat-to-regeneration workflow was fundamentally broken:

1. User generates initial dashboard (uses snippet path - fast, 277 tokens)
2. User chats with agents: "fix M3 colors"
3. Agent responds with proposed changes in chat
4. User clicks "Regenerate" button
5. **PROBLEM**: System regenerates using snippets again, ignoring chat feedback
6. Nothing changes - user frustrated

## Root Causes

### Issue 1: Regenerate Always Used Snippets
The regenerate button cleared generated code and called `generate_dashboard()`, but didn't force LLM generation. The hybrid system would pattern-match and use snippets again, producing identical output.

### Issue 2: Chat Feedback Not Incorporated
The `generate_dashboard()` method used static requirements. Chat history wasn't extracted or passed to generation, so agents never saw user feedback.

### Issue 3: force_llm Flag Not Persisting
The `--force-llm` CLI flag was checked from `sys.argv` during generation, but Streamlit consumes CLI args so they're not available at runtime.

## The Fix

### 1. Store force_llm in Session State
**File**: [src/ui/agent_studio.py:79](src/ui/agent_studio.py#L79)

```python
# In __init__ (lines 59-79):
if 'cli_args_parsed' not in st.session_state:
    # ... parse args ...

    # Check for --force-llm flag
    st.session_state.force_llm = '--force-llm' in sys.argv
```

This stores the flag during initialization, before Streamlit consumes the args.

### 2. Regenerate Button Forces LLM Generation
**File**: [src/ui/agent_studio.py:200-207](src/ui/agent_studio.py#L200-L207)

```python
if st.button("Regenerate", use_container_width=True):
    # Clear generated code to trigger fresh generation
    del st.session_state.generated_code
    if 'dashboard_file' in st.session_state:
        del st.session_state.dashboard_file
    # Force LLM generation on regenerate to incorporate feedback
    st.session_state.force_llm = True
    self.generate_dashboard()
```

**Key Change**: Added `st.session_state.force_llm = True` before regenerating.

This ensures regeneration ALWAYS uses full LLM generation (not snippets), allowing agents to incorporate feedback and make design changes.

### 3. Extract Chat Feedback from History
**File**: [src/ui/agent_studio.py:405-416](src/ui/agent_studio.py#L405-L416)

```python
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
```

This extracts the last 5 user messages from chat history and appends them to the requirements intent as "USER FEEDBACK TO INCORPORATE".

### 4. Read force_llm from Session State
**File**: [src/ui/agent_studio.py:427](src/ui/agent_studio.py#L427)

```python
# Check for --force-llm flag to skip snippets (from session state)
force_llm = st.session_state.get('force_llm', False)
```

Changed from checking `sys.argv` directly to reading from session state.

## How It Works Now

### Workflow 1: Initial Generation (Snippet Path)
```
1. User clicks "Generate Dashboard"
2. generate_dashboard() called with no feedback
3. force_llm = False (not set yet)
4. Hybrid system pattern matches → snippet assembly
5. Result: 277 tokens, fast generation
```

### Workflow 2: Regenerate with Feedback (LLM Path)
```
1. User chats: "make header bigger and use M3 colors"
2. Agent responds in chat (visible to user)
3. User clicks "Regenerate"
4. Regenerate button sets force_llm = True
5. generate_dashboard() called
6. Extracts last 5 user messages from chat
7. Appends to intent: "USER FEEDBACK TO INCORPORATE: make header bigger..."
8. force_llm = True bypasses snippet pattern matching
9. Full LLM generation with feedback
10. Result: 8,000-15,000 tokens, incorporates changes
```

## Token Usage

- **First generation** (snippet): ~277 tokens
- **Regeneration** (LLM with feedback): ~8,000-15,000 tokens
- **Total for iteration**: ~8,277-15,277 tokens

Compare to:
- **Always-LLM approach**: 40,000+ tokens (2x generations)
- **Savings**: ~79% token savings while enabling iteration

## Testing

### Unit Test
Run: `python test_poc_simple.py`

Validates:
- First generation uses snippet path (<1000 tokens)
- Regeneration with feedback uses LLM path (>5000 tokens)
- force_llm flag works correctly

### Integration Test
Run: `python test_regenerate_workflow.py`

Validates complete workflow:
- Initial generation
- User feedback simulation
- Regeneration with feedback
- Code changes verification

### Manual Test in UI
```bash
python scripts/pipeline/run_ingestion.py --ui
```

Steps:
1. Click "Generate Dashboard"
2. Verify snippet path used (check "Agent Output" section)
3. Chat with agents: "make the header bigger and use more colorful buttons"
4. Click "Regenerate"
5. Verify LLM path used with "FULL AGENT GENERATION" message
6. Verify dashboard code changed

## Files Modified

1. **src/ui/agent_studio.py**
   - Line 79: Store force_llm in session state
   - Lines 200-207: Regenerate button sets force_llm=True
   - Lines 405-416: Extract chat feedback
   - Line 427: Read force_llm from session state

## Benefits

1. **Fast Initial Generation**: Snippet path for first generation (99.3% token savings)
2. **Iterative Design**: User can provide feedback and regenerate with changes
3. **Transparent**: User sees agent thinking in "Agent Output" section
4. **Token Efficient**: Only use expensive LLM when feedback requires it
5. **No Lost Context**: Chat history flows into regeneration

## Limitations

- Regeneration always uses LLM (can't detect if feedback is minor)
- Limited to last 5 user messages (to avoid context bloat)
- Agents may still hallucinate APIs despite constraints
- No streaming during LLM generation (could add in future)

## Next Steps

1. Test with real users
2. Add streaming for LLM generation progress
3. Add detection for "minor" vs "major" feedback (smart force_llm)
4. Expand chat history context window if needed
5. Add validation to catch API hallucination before execution