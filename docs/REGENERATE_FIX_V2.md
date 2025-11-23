# Regenerate Button Fix - v2 (Streamlit Rerun Issue)

## The Problem

After implementing the initial regenerate workflow fix, clicking the "Regenerate" button still did nothing. The root cause was a **Streamlit rerun paradox**:

### What Was Happening:

1. User clicks "Regenerate" button
2. Code deletes `st.session_state.generated_code` (line 202)
3. Code calls `self.generate_dashboard()` (line 207)
4. `generate_dashboard()` creates new code
5. Saves to `st.session_state.generated_code` (line 469)
6. Calls `st.rerun()` (line 480)
7. **Page reloads** - but `generated_code` exists again!
8. Button renders, but click event is gone
9. **Result: Nothing happens from user's perspective**

### The Core Issue:

The button tried to delete `generated_code` and immediately regenerate it in the same execution. But Streamlit's rerun cycle meant the deletion never persisted - the code was recreated before the rerun completed.

## The Solution: Flag-Based Approach

Instead of trying to delete and regenerate in one step, we use a **two-phase approach** with a flag:

### Phase 1: Button Click
When user clicks "Regenerate":
1. Set `st.session_state.regenerate_requested = True` (flag)
2. Set `st.session_state.force_llm = True` (force LLM generation)
3. Call `st.rerun()` to reload the page
4. **Don't call generate_dashboard() yet!**

### Phase 2: On Page Load
At the start of the `run()` method:
1. Check if `regenerate_requested` flag is set
2. If yes:
   - Clear the flag
   - Delete `generated_code` and `dashboard_file`
   - Call `generate_dashboard()`
   - Exit early (since generate will trigger another rerun)

## Code Changes

### Change 1: Regenerate Button (lines 200-205)

**Before:**
```python
if st.button("🔄 Regenerate", use_container_width=True):
    # Clear generated code to trigger fresh generation
    del st.session_state.generated_code
    if 'dashboard_file' in st.session_state:
        del st.session_state.dashboard_file
    # Force LLM generation on regenerate to incorporate feedback
    st.session_state.force_llm = True
    self.generate_dashboard()
```

**After:**
```python
if st.button("🔄 Regenerate", use_container_width=True):
    # Set flag to trigger regeneration on next run
    st.session_state.regenerate_requested = True
    # Force LLM generation on regenerate to incorporate feedback
    st.session_state.force_llm = True
    st.rerun()
```

**Key Changes:**
- Don't delete `generated_code` immediately
- Don't call `generate_dashboard()` immediately
- Set flag and rerun - let the page load handler do the work

### Change 2: Page Load Handler (lines 787-797)

**Added new block after initialization:**
```python
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
```

**Why This Works:**
- The flag persists through the rerun
- On page load, we check the flag BEFORE rendering anything
- Delete the old code THEN trigger generation
- Exit early to avoid rendering duplicate UI

## How It Works Now

### Complete Workflow:

```
1. User generates dashboard
   → Uses snippet path (277 tokens)
   → Sets st.session_state.generated_code
   → Shows "Regenerate" and "Launch" buttons

2. User chats with agents
   → "make header bigger, use M3 colors"
   → Agent responds (visible in chat)
   → Messages stored in st.session_state.user_messages

3. User clicks "Regenerate" button
   → Sets regenerate_requested = True
   → Sets force_llm = True
   → Calls st.rerun()

4. Page reloads (run() method executes)
   → Checks: regenerate_requested == True?
   → YES: Clear flag
   → Delete generated_code and dashboard_file
   → Call generate_dashboard()

5. generate_dashboard() executes
   → Extracts last 5 user messages from chat
   → Appends to intent: "USER FEEDBACK TO INCORPORATE: ..."
   → Checks force_llm == True
   → Bypasses snippet pattern matching
   → Runs full LLM generation (8,000-15,000 tokens)
   → Creates new code with feedback incorporated
   → Saves to st.session_state.generated_code
   → Calls st.rerun()

6. Page reloads again
   → regenerate_requested == False (cleared in step 4)
   → Renders normal UI
   → Shows new "Regenerate" button (code exists)
   → User sees new dashboard with changes!
```

## Files Modified

### [src/ui/agent_studio.py](src/ui/agent_studio.py)

1. **Lines 200-205**: Regenerate button
   - Changed to flag-based approach
   - Sets `regenerate_requested` and `force_llm` flags
   - Calls `st.rerun()` instead of direct generation

2. **Lines 787-797**: Page load handler
   - Added check for `regenerate_requested` flag
   - Clears old generation when flag is set
   - Triggers `generate_dashboard()` and exits early

## Why The Previous Fix Didn't Work

The original fix had the right idea:
- Store force_llm in session state ✓
- Extract chat feedback ✓
- Force LLM generation on regenerate ✓

But it failed because:
- It tried to do everything in one execution cycle
- Streamlit's rerun model doesn't support this pattern
- The deleted state was recreated before the rerun completed

## Testing

To test this fix:

```bash
python scripts/pipeline/run_ingestion.py --ui
```

Steps:
1. Click "Generate Dashboard"
   - Verify: Console shows "snippet path" and ~277 tokens

2. Chat with agents: "make the header text bigger and use bold colors"
   - Verify: Agent responds in chat

3. Click "Regenerate"
   - Verify: Console shows "FULL AGENT GENERATION (skipping snippets)"
   - Verify: Console shows "Incorporating user feedback: make the header..."
   - Verify: Token count is 8,000-15,000

4. Compare generated_pipeline_dashboard.py
   - Verify: Code changed (different length or content)
   - Verify: Changes reflect your feedback

## Technical Notes

### Why Use A Flag?

Streamlit's execution model requires this approach:
- Each widget interaction (button click) triggers a full script rerun
- State changes must persist across reruns
- Complex operations need to be broken into steps

The flag-based approach:
- Phase 1 (button click): Set flags, trigger rerun
- Phase 2 (page load): Check flags, perform action
- This ensures state changes persist correctly

### Alternative Approaches Considered

**1. Use st.experimental_singleton**
- Doesn't solve the rerun issue
- Just caches the orchestrator

**2. Use callbacks on button click**
- Streamlit callbacks run BEFORE the page reruns
- Still causes the same deletion/recreation paradox

**3. Delete code in button, check for deletion in generate_dashboard()**
- Doesn't work - generate recreates code immediately
- Deletion doesn't persist through rerun

**4. Use st.form to batch operations**
- Over-complicated for this use case
- Still requires rerun handling

The flag-based approach is the cleanest solution for Streamlit's execution model.

## Token Savings

With this fix working correctly:

- **First generation**: 277 tokens (snippet)
- **Regeneration**: 8,000-15,000 tokens (LLM with feedback)
- **Total for one iteration**: ~8,277-15,277 tokens

Compare to always-LLM approach:
- **Two generations**: 40,000+ tokens (2x full LLM)
- **Savings**: ~62-79%

## Next Steps

1. Test with real user feedback in production
2. Add visual indicator when regeneration is in progress
3. Add toast notification "Regenerating with your feedback..."
4. Consider adding "Quick Fix" vs "Full Redesign" buttons
5. Add undo/redo for regenerations