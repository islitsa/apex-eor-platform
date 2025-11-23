# Streamlit Agent Studio Fixes

## Issues Fixed

### 1. Prompt Not Passing Through CLI
**Problem:** `run_ingestion.py` passes `--prompt` via CLI, but `agent_studio.py` doesn't read it.

**Fix:** Added CLI argument parsing in `AgentStudio.__init__()`:
- Parses `--prompt` argument from `sys.argv`
- Stores in `st.session_state.initial_prompt`
- Sets `auto_generate` flag when prompt provided

### 2. Agent Chatter Goes to Terminal Instead of Streamlit
**Problem:** All agent print output (token usage, phases, etc.) goes to terminal, not visible in UI.

**Fix:** Added output capture in `HybridStudioWrapper`:
- New method `generate_code_with_capture()` uses `redirect_stdout` and `redirect_stderr`
- Captures all console output during generation
- Returns tuple `(code, chatter)` instead of just code
- Stored in `st.session_state.agent_chatter`

### 3. No Auto-Generation When Launched with Prompt
**Problem:** Even with prompt passed, user still needs to click "Generate Dashboard" button.

**Fix:** Added auto-generation logic in `AgentStudio.run()`:
- Checks `st.session_state.auto_generate` flag
- Auto-loads context on first run
- Auto-generates dashboard if prompt provided
- Adds initial prompt to user chat
- Only triggers once (prevents re-generation on every rerun)

## Changes Made

### src/ui/agent_studio.py

1. **Added imports** (lines 32-34):
```python
import argparse
import io
from contextlib import redirect_stdout, redirect_stderr
```

2. **Modified `__init__()`** (lines 59-76):
- Added CLI argument parsing
- Stores `initial_prompt` and `auto_generate` in session state
- Added `agent_chatter` to session state

3. **New method in `HybridStudioWrapper`** (lines 740-797):
- `generate_code_with_capture()`: Captures stdout/stderr during generation
- `generate_ui_code()`: Backwards-compatible wrapper

4. **Modified `generate_dashboard()`** (lines 376-383):
- Checks for `generate_code_with_capture()` method
- Stores captured chatter in session state
- Falls back to regular generation for non-Hybrid orchestrators

5. **Modified `run()`** (lines 664-672):
- Auto-loads context on first run
- Auto-generates when `auto_generate` flag set
- Adds initial prompt message to chat

6. **Modified `render_right_column()`** (lines 252-260):
- Added "Agent Output" section
- Displays captured chatter in expandable code block
- Shows helpful message when no chatter yet

## Testing

### Test 1: CLI Prompt Passing
```bash
python scripts/pipeline/run_ingestion.py --ui
```

**Expected:**
- Streamlit launches
- Agent Studio UI appears
- Chatter section shows "Agent console output will appear here"

### Test 2: With Prompt Auto-Generation
```bash
# In run_ingestion.py, prompt is passed via:
subprocess.run([
    sys.executable, "-m", "streamlit", "run",
    str(agent_studio_path),
    "--", "--prompt", "Generate pipeline navigation dashboard"
])
```

**Expected:**
- Streamlit launches
- Context auto-loads
- Dashboard auto-generates
- Initial prompt appears in user chat
- Agent chatter appears in right column
- Generated code saved to `generated_pipeline_dashboard.py`

### Test 3: Chatter Capture
After generation completes, right column should show:
```
💭 Agent Output
▼ View captured agent output

[Hybrid Generator] Initialized
  - Snippet patterns available: 3
  - Strategy: Snippet first (300 tokens), LLM fallback (8,000 tokens)

================================================================================
HYBRID CODE GENERATION (Opus Extreme Optimization)
================================================================================

PHASE 0: PATTERN MATCHING (Snippet Path)
--------------------------------------------------------------------------------
  [Pattern Matcher] Tokens: input=271, output=6, total=277
  [Pattern Matcher] Response: 'pipeline_navigation'
  [Hybrid] Pattern matched: 'pipeline_navigation'
  [Hybrid] Using snippet assembly (0 additional tokens!)
  [Validator] Snippet validated successfully

[Hybrid] [OK] Snippet path successful!
  - Pattern: pipeline_navigation
  - Code length: 215,951 chars
  - Tokens used: 277 (pattern matching + validation)
  - Snippet hit rate: 1/1 (100.0%)
```

## Key Benefits

1. **Better UX**: User sees what agents are doing in real-time
2. **Debugging**: Easy to see token usage, phases, and errors
3. **Transparency**: All agent thinking visible in UI, not hidden in terminal
4. **Auto-flow**: Seamless experience when launched from `run_ingestion.py`

## Technical Notes

- `redirect_stdout` and `redirect_stderr` capture ALL print statements during generation
- Context managers ensure output is properly captured and restored
- Backwards compatible: Works with both `HybridStudioWrapper` and `StudioOrchestrator`
- Session state prevents re-parsing CLI args on every Streamlit rerun
- `auto_generate` flag ensures only one auto-generation per launch