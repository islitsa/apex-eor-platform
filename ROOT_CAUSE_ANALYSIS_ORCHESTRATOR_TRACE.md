# Root Cause Analysis: Missing Orchestrator Data Trace

## Problem Statement
After running Agent Studio (VBS) with a prompt, the orchestrator data sources trace is no longer showing up.

---

## Root Cause

**PRIMARY ISSUE:** Adapter performance bottleneck causing API timeouts

### The Problem Chain:
1. **Adapter was scanning ALL files** (25,451 files for RRC)
   - `_enumerate_location_files()` + `_scan_directory_files()` using `rglob('*')`
   - Taking **8.69 seconds** per request

2. **API endpoint timing out**
   - Default timeout: 5 seconds
   - Actual time: 8-11 seconds
   - Result: Connection timeout before trace can be generated

3. **Orchestrator trace not appearing**
   - Trace generated AFTER successful data fetch
   - Timeout means no trace is emitted

---

## Fix Implemented

### Performance Optimization ([adapter.py](src/agents/context/adapter.py) lines 147-158)

**BEFORE:**
```python
# Enumerate actual files for this location
files = ContextAdapter._enumerate_location_files(
    location_path, file_count, location_type
)

# Count file types
file_types = {}
for file_info in files:
    ext = Path(file_info['name']).suffix.lower()
    if ext:
        file_types[ext] = file_types.get(ext, 0) + 1
```

**AFTER:**
```python
# Use file type information from all_locations (already computed)
# NO need to scan directories - that's too slow!
file_types = loc_info.get('types', {})

locations_data[location_type] = {
    'files': [],  # Don't enumerate files - too slow
    'file_count': file_count,
    'file_types': file_types
}
```

### Performance Improvement
- **Before:** 8.69 seconds
- **After:** 0.056 seconds
- **Speedup:** 155x faster!

---

## Why This Happened

The multi-location adapter implementation was **over-engineering** the solution:
1. Tried to enumerate every single file to count types
2. Didn't realize `all_locations` already had `types` field
3. Used slow recursive `rglob('*')` scan

**Key Insight:** The discovery process already computes file types and stores them in `all_locations.types` - we should reuse that data!

---

## Current Status

### ✅ Fixed
- Adapter performance (155x improvement)
- Multi-location structure working correctly
- File counts accurate
- File types displayed correctly

### ⚠️ Remaining Issue
- API server still slow (11 seconds) even after adapter fix
- Suggests another bottleneck in `/api/pipelines` endpoint
- Needs further investigation

### 🔍 Next Steps
1. **Profile `/api/pipelines` endpoint** to find remaining bottleneck
2. **Restart API server completely** (not just reload)
3. **Verify orchestrator trace appears** after full restart
4. **Check if data_service.py has other slow operations**

---

## How to Verify the Fix

### Test 1: Adapter Performance
```bash
python -c "import time; start = time.time(); from shared_state import PipelineState; from src.agents.context.adapter import ContextAdapter; ctx = PipelineState.load_context(); adapted = ContextAdapter.discovery_to_pipeline(ctx); print(f'Adapter: {time.time() - start:.3f}s')"
```
**Expected:** < 0.1 seconds

### Test 2: API Performance
```bash
python -c "import time, requests; start = time.time(); r = requests.get('http://localhost:8000/api/pipelines', timeout=30); print(f'API: {time.time() - start:.2f}s')"
```
**Expected:** < 2 seconds (currently 11 seconds - ISSUE REMAINS)

### Test 3: Orchestrator Trace
```bash
python test_orchestrator_trace_fixed.py
```
**Expected:** Trace with multi-location data appears

---

## Prevention

### Design Principle Violated
**"Don't scan what's already known"**

The discovery process already:
- Counts files
- Detects file types
- Calculates sizes
- Scans directories

The adapter should **reuse** this information, not **recompute** it.

### Future Safeguard
Always check if data exists in the context before:
- Scanning directories
- Reading files
- Computing statistics
- Enumerating lists

**Ask:** "Has this already been computed?"

---

## Summary

**Root Cause:** Adapter scanning 25K+ files unnecessarily
**Fix:** Use existing `types` data from `all_locations`
**Result:** 155x performance improvement (8.69s → 0.056s)
**Status:** Adapter fixed, but API endpoint has another bottleneck
**Action:** User needs to fully restart API server and verify trace appears
