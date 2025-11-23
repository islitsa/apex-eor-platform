# Complete File Count Fix Plan
## Following Opus's Guidance: Show Everything, Assume Nothing

## Problem Summary

**Current Behavior:**
```
>> fracfocus
   └─ Total: 2 files, 970.9 MB
```

**Reality:**
- `raw/`: 37 files (32 CSV, 2 JSON, 1 ZIP, 2 TXT) - 7.16 GB
- `interim/`: 2 files (2 parquet) - 970.9 MB - 13.9M records

**What Went Wrong:**
The system made an assumption that "interim is best" and only showed that. This is fundamentally wrong.

---

## Opus's Core Principle

> **"NEVER assume which data directory is 'best' or 'ready to use'.**
> **Show me ALL locations where data exists.**
> **Let ME decide which to use.**
> **The system should report facts, not make quality judgments."**

---

## Expected Output (After Fix)

```
>> fracfocus
   📁 raw/      37 files (32 CSV, 2 JSON, 1 ZIP, 2 TXT) - 7.16 GB
   📁 interim/   2 files (2 parquet) - 970.9 MB - 13.9M records

   Available in 2 locations

>> rrc
   📁 raw/      [X files] - [size]
   📁 interim/  [Y files] - [size]

   Available in 2 locations

>> attribution
   📁 interim/  2 files - 325.0 MB

   Available in 1 location
```

---

## Implementation Plan

### Phase 1: Adapter Changes (src/agents/context/adapter.py)

**Current Problem:**
- Lines 111-140: Makes assumption about "best" location
- Lines 117-121: Prioritizes raw over interim (WRONG!)
- Line 136: Overwrites file_count (WRONG!)

**Required Changes:**

1. **Build Multi-Location Structure**
   - Don't pick a "winner"
   - Create `directory_structure` with ALL locations
   - Use `all_locations` data to enumerate each location separately

2. **New Structure:**
```python
adapted['directory_structure'] = {
    'locations': {
        'raw': {
            'files': [...],  # 37 files for fracfocus
            'subdirs': {},
            'file_count': 37,
            'size': '7.16 GB',
            'file_types': {'.csv': 32, '.json': 2, ...}
        },
        'interim': {
            'files': [...],  # 2 files for fracfocus
            'subdirs': {},
            'file_count': 2,
            'size': '970.9 MB',
            'row_count': 13907094
        }
    },
    'available_in': ['raw', 'interim']  # List of locations
}
```

3. **Implementation Steps:**
   - Read `all_locations` from source_data
   - For each location (raw, interim, processed):
     - If file_count > 0, enumerate those files
     - Build proper path (data/{location}/{source_id})
     - Scan actual directory structure
     - Collect file metadata (name, size, type)
   - DO NOT set a "primary" or "default" location
   - DO NOT overwrite top-level file_count

---

### Phase 2: Data Service Changes (src/api/data_service.py)

**Current Problem:**
- Line 547: Uses `p['metrics']['file_count']` which is ambiguous
- Lines 306-349: `format_pipeline_detail()` expects single location

**Required Changes:**

1. **Update format_pipeline_detail() function (lines 306-349):**

```python
def format_pipeline_detail(p):
    """Format pipeline with ALL locations shown"""
    lines = [f"  >> {p.get('display_name', p.get('id'))}"]

    # Check new multi-location structure
    files_info = p.get('files', {})
    if files_info and isinstance(files_info, dict) and 'locations' in files_info:
        locations_data = files_info['locations']
        available_in = files_info.get('available_in', [])

        # Show each location
        for location in ['raw', 'interim', 'processed']:
            if location in locations_data:
                loc_data = locations_data[location]
                file_count = loc_data.get('file_count', 0)
                size = loc_data.get('size', '0 B')

                # Build file type breakdown
                file_types = loc_data.get('file_types', {})
                type_str = ', '.join([f"{count} {ext}" for ext, count in file_types.items()])
                if type_str:
                    type_str = f" ({type_str})"
                else:
                    type_str = ""

                # Add row count if available
                rows = loc_data.get('row_count', 0)
                row_str = f" - {rows:,} records" if rows else ""

                lines.append(f"     📁 {location:<9} {file_count} files{type_str} - {size}{row_str}")

        # Show summary
        lines.append(f"     ")
        lines.append(f"     Available in {len(available_in)} location(s)")
    else:
        # Fallback for old format
        lines.append(f"     └─ Total: {p['metrics']['file_count']} files, {p['metrics']['data_size']}")

    return "\n".join(lines)
```

2. **Update metrics calculation (lines 516-547):**
   - Calculate totals across ALL locations
   - Don't pick a "primary" location
   - Show aggregate stats in summary

---

### Phase 3: Orchestrator Changes (src/agents/ui_orchestrator.py)

**Current Status:**
- Lines 352-354: Calls `format_pipeline_detail()` for each pipeline
- Should work automatically once data_service changes are applied

**Verification Needed:**
- Check trace output format
- Ensure multi-location display works
- Verify summary totals are correct

---

### Phase 4: Discovery Process (discover_real_data.py)

**Current Status:**
- Already populates `all_locations` correctly
- No changes needed

**Verification:**
- Confirm all_locations has complete data
- Check file type breakdown is accurate

---

## Testing Plan

### Test 1: Verify Context Data
```bash
python -c "from shared_state import PipelineState; ctx = PipelineState.load_context(); ff = ctx['data_sources']['fracfocus']; print(ff.get('all_locations'))"
```

**Expected:** Shows both raw (37 files) and interim (2 files)

### Test 2: Test Adapter
```bash
python -c "from shared_state import PipelineState; from src.agents.context.adapter import ContextAdapter; ctx = PipelineState.load_context(); adapted = ContextAdapter.discovery_to_pipeline(ctx); import json; print(json.dumps(adapted['data_sources']['fracfocus']['directory_structure'], indent=2))"
```

**Expected:** Shows locations structure with both raw and interim

### Test 3: Test API
```bash
curl http://localhost:8000/api/pipelines | python -m json.tool
```

**Expected:** Pipeline data shows multi-location structure

### Test 4: Test Orchestrator Trace
```bash
python test_protocol_smoke.py
```

**Expected:** Trace shows:
```
>> fracfocus
   📁 raw/      37 files (32 CSV, ...) - 7.16 GB
   📁 interim/   2 files (parquet) - 970.9 MB - 13.9M records

   Available in 2 locations
```

---

## Key Principles (From Opus)

1. **Show Everything** - All locations where data exists
2. **Assume Nothing** - No quality judgments about which is "best"
3. **Full Transparency** - Complete file counts, sizes, types
4. **User Decides** - Don't filter or prioritize automatically
5. **Report State, Not Quality** - raw/interim/processed are states, not rankings

---

## Why This Matters

**For Your Use Case:**
- You're mid-pipeline processing
- Need to compare raw vs processed
- Need to debug transformations
- Need to validate data quality
- Need to see what exists where

**For Gradient Context:**
- Gradient should understand data STATE
- Not make assumptions about "readiness"
- Provide semantic understanding of pipeline stages
- Support experimental data processing

---

## Implementation Order

1. ✅ **Understand the problem** (DONE)
2. 🔄 **Fix adapter.py** - Build multi-location structure
3. 🔄 **Fix data_service.py** - Update formatting and metrics
4. 🔄 **Test with orchestrator** - Verify trace output
5. 🔄 **Document changes** - Update architecture docs

---

## Files to Modify

1. **src/agents/context/adapter.py** (Lines 111-140)
   - Rewrite `_adapt_sources()` to build multi-location structure
   - Update `_enumerate_files()` to handle location-specific paths

2. **src/api/data_service.py** (Lines 306-349, 516-547)
   - Rewrite `format_pipeline_detail()` to show all locations
   - Update metrics calculation to aggregate across locations

3. **Tests** (New test file)
   - Create `test_multi_location_display.py`
   - Verify all locations are shown
   - Verify no assumptions are made

---

## Success Criteria

✅ Orchestrator trace shows ALL locations for each source
✅ No location is prioritized or marked as "best"
✅ File counts are accurate for each location
✅ File types and sizes are shown for each location
✅ User can see complete data landscape
✅ System makes NO quality judgments

---

## Notes

- This aligns with APEX EOR's experimental nature
- Supports debugging and validation workflows
- Maintains semantic neutrality
- Respects user's data pipeline state
- No breaking changes to discovery process
