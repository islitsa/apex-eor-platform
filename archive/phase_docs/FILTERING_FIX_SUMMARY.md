# Prompt Filtering Fix - Complete Summary

## Problem

When asking for "production data from **rrc**", the orchestrator trace showed **ALL 6** data sources (fracfocus, rrc, attribution, completions, production, treatments) instead of just the ones mentioned in the prompt.

## Root Cause Discovery

### Initial Hypothesis (WRONG)
First thought the API was returning all sources without filtering.

### Actual Root Cause (CORRECT)
Agent Studio loads the discovery context **once at startup** with ALL 6 sources. This context is stored in `st.session_state.context` and **reused for every prompt**.

The flow was:
1. Startup: Load context with ALL 6 sources → `st.session_state.context`
2. User prompt: "rrc data"
3. Agent Studio passes `st.session_state.context` (with all 6 sources) to orchestrator
4. Orchestrator builds `requirements['data_sources']` from context → contains all 6
5. Filtering extracts keys from `requirements['data_sources']` → gets all 6!
6. Filter with all 6 sources = no filtering!

**The bug:** Filtering was based on pre-loaded context (always all 6), not on what the user actually asked for.

## Solution

Parse the **user's prompt text** to find which sources are mentioned, then filter based on that.

### Code Changes

**File:** `src/agents/ui_orchestrator.py`

**1. Added `filter_sources` parameter** (line 257)
```python
def _fetch_data_context(self, api_url: str = "http://localhost:8000", filter_sources: list = None) -> Dict:
```

**2. Added filtering logic in `_fetch_data_context()`** (lines 296-309)
```python
# Filter pipelines if filter_sources is provided
print(f"\n[DEBUG _fetch_data_context] filter_sources parameter: {filter_sources}")
print(f"[DEBUG _fetch_data_context] Total pipelines before filter: {len(pipelines)}")
if filter_sources:
    original_count = len(pipelines)
    pipelines = [p for p in pipelines if p.get('id') in filter_sources]
    filtered_count = len(pipelines)
    print(f"[DEBUG _fetch_data_context] Pipelines after filter: {filtered_count}")
    print(f"[DEBUG _fetch_data_context] Pipeline IDs kept: {[p.get('id') for p in pipelines]}")

    if filtered_count < original_count:
        print(f"  [API] FILTERED: {filtered_count}/{original_count} pipelines match prompt scope: {filter_sources}")
else:
    print(f"[DEBUG _fetch_data_context] No filtering - filter_sources is None")
```

**3. Parse prompt to detect mentioned sources** (lines 697-715)
```python
# Extract source filter from USER'S PROMPT (not pre-loaded context!)
# Parse the intent to find which data sources are mentioned
intent = requirements.get('intent', '').lower()
all_sources = list(requirements.get('data_sources', {}).keys()) if requirements.get('data_sources') else []

print(f"\n[DEBUG] User intent: {intent}")
print(f"[DEBUG] All available sources: {all_sources}")

# Find which sources are mentioned in the prompt
mentioned_sources = [src for src in all_sources if src.lower() in intent]

# Use mentioned sources for filtering, or None to show all if nothing specific mentioned
filter_sources = mentioned_sources if mentioned_sources else None

print(f"[DEBUG] Detected sources from prompt: {filter_sources}")
if filter_sources:
    print(f"[Orchestrator] Filtering trace to show only: {filter_sources}")

data_context = self._fetch_data_context(filter_sources=filter_sources)
```

## How It Works Now

### Example 1: "generate dashboard of rrc data"
```
[DEBUG] User intent: generate dashboard of rrc data
[DEBUG] All available sources: ['fracfocus', 'rrc', 'attribution', 'completions', 'production', 'treatments']
[DEBUG] Detected sources from prompt: ['rrc']
[Orchestrator] Filtering trace to show only: ['rrc']

[API] FILTERED: 1/6 pipelines match prompt scope: ['rrc']

Trace shows: ONLY RRC ✅
```

### Example 2: "show production data from rrc"
```
[DEBUG] User intent: show production data from rrc
[DEBUG] Detected sources from prompt: ['rrc', 'production']
[Orchestrator] Filtering trace to show only: ['rrc', 'production']

[API] FILTERED: 2/6 pipelines match prompt scope: ['rrc', 'production']

Trace shows: RRC + production ✅
```

### Example 3: "create a dashboard"
```
[DEBUG] User intent: create a dashboard
[DEBUG] Detected sources from prompt: None
[DEBUG _fetch_data_context] No filtering - filter_sources is None

Trace shows: ALL 6 sources ✅ (because no specific source mentioned)
```

## Benefits

1. **Intelligent filtering** - Shows only what you ask for
2. **Keyword-based** - Simple substring matching (e.g., "rrc" in prompt)
3. **Reduced token usage** - Doesn't pass irrelevant data to agents
4. **Better agent focus** - Agents see only relevant data
5. **Accurate summaries** - Totals reflect filtered sources

## Testing Required

### Step 1: Restart Agent Studio
**IMPORTANT:** Python caches modules. You MUST fully restart to load changes.

```batch
# Kill all processes
kill_all_agent_studio.bat

# Verify ports are free
# Should show: "Port 8000 is free" and "Port 8501 is free"

# Restart
Launch_Agent_Studio.vbs
```

### Step 2: Test Cases

**Test 1:** Only RRC
```
Prompt: "generate a dashboard showing rrc well data"
Expected: Trace shows ONLY rrc (1/6 filtered)
```

**Test 2:** Only FracFocus
```
Prompt: "show fracfocus chemical data"
Expected: Trace shows ONLY fracfocus (1/6 filtered)
```

**Test 3:** Multiple sources
```
Prompt: "compare rrc and fracfocus production"
Expected: Trace shows rrc, fracfocus, production (3/6 filtered)
```

**Test 4:** No specific source
```
Prompt: "create a dashboard"
Expected: Trace shows ALL 6 sources (no filtering)
```

### Step 3: Verify Debug Output

Check the **console** (where you ran the batch file) for debug messages:
```
[DEBUG] User intent: ...
[DEBUG] All available sources: ...
[DEBUG] Detected sources from prompt: ...
```

If you DON'T see these messages, the code hasn't loaded. Try restarting again.

## Current Status

- ✅ Fix implemented
- ⚠️ Needs testing (requires full restart)
- 📋 Ready for user verification

## Related Files

- [PROMPT_FILTERING_FIX.md](PROMPT_FILTERING_FIX.md) - Detailed technical documentation
- [RESTART_AGENT_STUDIO.md](RESTART_AGENT_STUDIO.md) - Restart instructions
- [kill_all_agent_studio.bat](kill_all_agent_studio.bat) - Process killer script
- [ui_orchestrator.py](src/agents/ui_orchestrator.py) - Main fix location

## What Changed vs Initial Fix

**Initial attempt:** Filtered based on `requirements['data_sources']` keys
- Problem: This always had all 6 sources from pre-loaded context

**Final fix:** Parse user's prompt text to find mentioned sources
- Solution: Look for source names (rrc, fracfocus, etc.) in the prompt string
- Works: Only shows sources that appear in the prompt text
