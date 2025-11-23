# Prompt Filtering Fix

## Problem
When user asks for "production data from rrc", the orchestrator trace shows ALL 6 data sources:
- fracfocus
- rrc ✓ (requested)
- attribution
- completions
- production
- treatments

This is misleading and wastes tokens/context.

## Root Cause

**The real issue:** Agent Studio loads discovery context at startup with ALL 6 sources. This context is stored in `st.session_state.context` and reused for every prompt. When building `requirements['data_sources']`, it always contains all 6 sources - not just the ones mentioned in the user's prompt.

The filtering was extracting sources from `requirements['data_sources']` (which always had all 6), instead of parsing the user's actual prompt text to find which sources were mentioned.

## Solution Implemented

### Changes to `ui_orchestrator.py`

**1. Added `filter_sources` parameter to `_fetch_data_context()`** (line 257)
```python
def _fetch_data_context(self, api_url: str = "http://localhost:8000", filter_sources: list = None) -> Dict:
```

**2. Added filtering logic** (lines 296-309)
```python
# Filter pipelines if filter_sources is provided
if filter_sources:
    original_count = len(pipelines)
    pipelines = [p for p in pipelines if p.get('id') in filter_sources]
    filtered_count = len(pipelines)

    if filtered_count < original_count:
        print(f"  [API] FILTERED: {filtered_count}/{original_count} pipelines match prompt scope: {filter_sources}")
```

**3. Parse user's prompt to detect mentioned sources** (lines 697-713)
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

## Expected Behavior (After Fix)

### Prompt: "pls generate a dashboard of production data from rrc"

**Console output (debug):**
```
[DEBUG] User intent: pls generate a dashboard of production data from rrc
[DEBUG] All available sources: ['fracfocus', 'rrc', 'attribution', 'completions', 'production', 'treatments']
[DEBUG] Detected sources from prompt: ['rrc', 'production']
[Orchestrator] Filtering trace to show only: ['rrc', 'production']

[DEBUG _fetch_data_context] filter_sources parameter: ['rrc', 'production']
[DEBUG _fetch_data_context] Total pipelines before filter: 6
[DEBUG _fetch_data_context] Pipelines after filter: 2
[DEBUG _fetch_data_context] Pipeline IDs kept: ['rrc', 'production']
[API] FILTERED: 2/6 pipelines match prompt scope: ['rrc', 'production']
```

**Trace will show:**
```
Successfully fetched REAL DATA from API:

SUMMARY:
- Total Pipelines: 2  # Only RRC and production!
- Total Records: ~80M
- Total Size: ~70 GB

PIPELINE BREAKDOWN (by stage):
  >> rrc
     📁 raw       25451 files (...) - 63.78 GB
     📁 interim   12 files (12 .parquet) - 1.36 GB - 79,637,354 records

     Available in 2 location(s)

  >> production
     📁 interim   5 files (5 .parquet) - 5.16 GB - 8,583,292 records

     Available in 1 location(s)

✨ Only relevant data passed to agents!
```

**Note:** The prompt mentions both "production" and "rrc", so both are shown. If you only want RRC, say "rrc data" without mentioning "production".

## Benefits

1. **Clearer traces** - Only shows what's relevant to the prompt
2. **Reduced token usage** - Doesn't pass irrelevant data to agents
3. **Better agent focus** - Agents only see data they need to work with
4. **Accurate summaries** - Totals reflect only the filtered sources

## Testing

To test, run Agent Studio with a prompt like:
```
"generate a dashboard showing fracfocus chemical data"
```

Expected: Trace should only show `fracfocus`, not all 6 sources.

## Note

The API still returns all 6 sources - filtering happens in the orchestrator BEFORE creating the trace and passing to agents. This is the right layer for filtering since:
- API is generic (serves all data)
- Orchestrator is prompt-aware (knows what user wants)
- Agents receive only relevant context
