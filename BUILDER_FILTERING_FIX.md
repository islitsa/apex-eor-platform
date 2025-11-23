# Builder Filtering Fix - Why Builder Was Seeing All 6 Sources

## Problem

After implementing prompt filtering, the **orchestrator trace** correctly showed only 2 sources (rrc, production), but the **builder trace** still showed all 6 sources!

```
Orchestrator: Shows 2 sources ✅
Builder: Shows 6 sources ❌
```

## Root Cause

The orchestrator was filtering `data_context['pipelines']` correctly, but passing **unfiltered** data to the builder through multiple channels:

### Three Sources of Unfiltered Data

1. **`design_spec.data_sources`**
   - UX Designer discovers all 6 sources
   - Passed to builder as-is
   - Builder checks this FIRST (line 200 in react_developer.py)

2. **`enhanced_context['data_sources']`**
   - Copied from original context (line 804: `dict(context)`)
   - Contains all 6 sources from startup
   - Builder falls back to this if design_spec doesn't have data_sources

3. **Second filtering step** (lines 785-797)
   - Tried to re-filter pipelines based on `design_spec.data_sources`
   - But `design_spec.data_sources` had all 6 sources!
   - Could add sources back after first filter

## Solution

Filter ALL FOUR sources to match the filtered `data_context['pipelines']`:

### Fix 1: Filter `design_spec.data_sources` (lines 799-808)

```python
# CRITICAL: Also filter design_spec.data_sources to match filtered pipelines
# This ensures design_spec doesn't pass unfiltered sources to builder
if filtered_count < original_count:
    remaining_pipeline_ids = [p.get('id') for p in data_context['pipelines']]
    filtered_design_sources = {
        k: v for k, v in design_spec.data_sources.items()
        if k in remaining_pipeline_ids
    }
    print(f"[Orchestrator] Also filtering design_spec.data_sources: {len(design_spec.data_sources)} → {len(filtered_design_sources)}")
    design_spec.data_sources = filtered_design_sources
```

### Fix 2: Filter `session_ctx` sources (lines 602-627)

**CRITICAL FIX:** This was the missing piece causing "still 6 sources" bug!

```python
# Extract discovered sources from FILTERED data_context (not requirements!)
# This ensures session_ctx uses the filtered sources, not all discovered sources
if data_context.get('success') and data_context.get('pipelines'):
    # Use filtered pipelines from data_context
    filtered_pipelines = data_context.get('pipelines', [])
    sources = [p.get('id') for p in filtered_pipelines]

    # Build record counts from filtered pipelines
    record_counts = {}
    for pipeline in filtered_pipelines:
        pipeline_id = pipeline.get('id')
        metrics = pipeline.get('metrics', {})
        record_counts[pipeline_id] = metrics.get('record_count', 0)

    print(f"  [SessionContext] Using FILTERED sources from data_context: {sources}")
```

This fixes the **protocol-aware execution path** which uses `session_ctx` instead of `enhanced_context`.

### Fix 3: Filter `enhanced_context['data_sources']` (lines 822-834)

```python
# CRITICAL: Filter enhanced_context['data_sources'] to match filtered data_context
# This ensures builder sees same sources as orchestrator trace
if data_context.get('success') and data_context.get('pipelines'):
    filtered_pipeline_ids = [p.get('id') for p in data_context.get('pipelines', [])]
    original_data_sources = enhanced_context.get('data_sources', {})
    filtered_data_sources = {
        k: v for k, v in original_data_sources.items()
        if k in filtered_pipeline_ids
    }
    if len(filtered_data_sources) != len(original_data_sources):
        print(f"\n[Orchestrator] Filtered data_sources for builder: {len(original_data_sources)} → {len(filtered_data_sources)}")
        print(f"[Orchestrator] Builder will see: {list(filtered_data_sources.keys())}")
        enhanced_context['data_sources'] = filtered_data_sources
```

## Complete Filtering Flow

Now the data flows like this:

1. **Prompt parsing** (line 706)
   - Extract sources mentioned in prompt: `['rrc', 'production']`

2. **First filter** (line 715)
   - Filter `data_context['pipelines']`: 6 → 2
   - Orchestrator trace shows: 2 sources ✅

3. **Build SessionContext** (lines 602-627) **← THIS WAS THE BUG!**
   - Extract sources from FILTERED `data_context['pipelines']`: 2 sources
   - Set `intent.scope` to filtered sources: `['rrc', 'production']`
   - Protocol-aware path uses this: 2 sources ✅

4. **Second filter** (lines 785-797)
   - Re-filter `data_context['pipelines']` based on UX discovery
   - Usually doesn't change anything (already filtered)

5. **Filter design_spec** (lines 799-808)
   - Filter `design_spec.data_sources`: 6 → 2
   - Legacy path builder gets: 2 sources from design_spec ✅

6. **Filter enhanced_context** (lines 822-834)
   - Filter `enhanced_context['data_sources']`: 6 → 2
   - Legacy path fallback gets: 2 sources ✅

7. **Builder receives** (react_developer.py line 200)
   - Protocol path: Gets from `session_ctx.discovery.sources`: 2 sources ✅
   - Legacy path: Gets from `design_spec.data_sources` or `context['data_sources']`: 2 sources ✅
   - Builder trace shows: 2 sources ✅

## Expected Console Output

```
[DEBUG] User intent: generate dashboard of production data from rrc
[DEBUG] Detected sources from prompt: ['rrc', 'production']
[Orchestrator] Filtering trace to show only: ['rrc', 'production']

[API] FILTERED: 2/6 pipelines match prompt scope: ['rrc', 'production']

[Orchestrator] Building SessionContext...
[SessionContext] Using FILTERED sources from data_context: ['rrc', 'production']
Record counts: {...}

[Orchestrator] Filtering data context to discovered sources: ['rrc', 'production']
[Orchestrator] Filtered pipelines: 2 → 2
[Orchestrator] Also filtering design_spec.data_sources: 6 → 2

[Orchestrator] Filtered data_sources for builder: 6 → 2
[Orchestrator] Builder will see: ['rrc', 'production']

[Orchestrator] Using protocol-aware execution...
```

## Expected Traces

**Orchestrator Trace:**
```
Successfully fetched REAL DATA from API:

SUMMARY:
- Total Pipelines: 2  ✅
- Total Records: 163,958,119
- Total Size: 3.02 GB

PIPELINE BREAKDOWN:
  >> rrc
  >> production
```

**Builder Trace:**
```
Planning React component architecture:

DESIGN SPEC ANALYSIS:
- Data Sources: 2 sources with 163,958,119 total records [rrc(...), production(...)]  ✅
```

## Files Changed

- [ui_orchestrator.py](src/agents/ui_orchestrator.py)
  - Lines 602-627: Build `session_ctx` from filtered data_context **← KEY FIX!**
  - Lines 799-808: Filter `design_spec.data_sources`
  - Lines 822-834: Filter `enhanced_context['data_sources']`

## Testing

1. Kill all processes: `kill_all_agent_studio.bat`
2. Restart: `Launch_Agent_Studio.vbs`
3. Test prompt: "generate dashboard of rrc well data"
4. Check console for filtering messages (should show 3 filter steps)
5. Check orchestrator trace (should show 1 source)
6. Check builder trace (should show 1 source, NOT 6)

## Status

- ✅ Fix implemented
- ⚠️ Needs testing with full restart
