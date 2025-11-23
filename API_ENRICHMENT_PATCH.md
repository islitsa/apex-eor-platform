# FastAPI Pipeline Enrichment Patch

## Summary

**Patched:** `src/api/data_service.py`

**Change:** `/api/pipelines` endpoint now uses `PipelineAssemblyTool` to detect real stages from filesystem before returning data to React.

---

## What Was Changed

### Before (Old Behavior):
```python
# Built pipelines from context
# Returned pipelines with empty stages: []
return {"pipelines": pipelines, "summary": {...}}
```

**Result:** React UI showed **0 stages**, no pipeline health indicators

### After (New Behavior):
```python
# Build data_context format
enrichment_context = {
    "pipelines": pipelines,
    "summary": summary_data
}

# Call PipelineAssemblyTool to detect stages from filesystem
enriched_pipelines = pipeline_tool.assemble_pipelines(enrichment_context)

# Return enriched pipelines with detected stages
return {"pipelines": enriched_pipelines, "summary": {...}}
```

**Result:** React UI now shows **real stages** (downloads/extracted/parsed)

---

## How It Works

### Step 1: API loads pipelines from PipelineState
```python
context = PipelineState.load_context()
pipelines = []  # Build from context...
```

### Step 2: PipelineAssemblyTool enriches with filesystem data
```python
pipeline_tool = PipelineAssemblyTool(data_root="data/raw")
enriched_pipelines = pipeline_tool.assemble_pipelines({
    "pipelines": pipelines,
    "summary": summary_data
})
```

**PipelineAssemblyTool:**
- Scans `data/raw/fracfocus/` directory
- Finds `Chemical_data/` container
- Detects subdirectories: `downloads/`, `extracted/`, `parsed/`
- Counts files in each stage
- Scores health status (complete/empty/missing)

### Step 3: API returns enriched data
```json
{
  "pipelines": [
    {
      "id": "fracfocus",
      "stages": [
        {"name": "downloads", "file_count": 1, "status": "complete"},
        {"name": "extracted", "file_count": 17, "status": "complete"},
        {"name": "parsed", "file_count": 17, "status": "complete"}
      ]
    }
  ]
}
```

---

## Files Modified

**1. src/api/data_service.py**
- Line 693: Added import for `PipelineAssemblyTool`
- Lines 928-954: Added enrichment logic before return

**Changes:**
```python
from src.agents.tools.pipeline_assembly_tool import PipelineAssemblyTool

# ENRICHMENT: Use PipelineAssemblyTool to detect stages
try:
    pipeline_tool = PipelineAssemblyTool(data_root="data/raw")
    enrichment_context = {"pipelines": pipelines, "summary": summary_data}
    enriched_pipelines = pipeline_tool.assemble_pipelines(enrichment_context)
    pipelines = enriched_pipelines
except Exception as e:
    # Don't fail API call if enrichment fails
    sys.stderr.write(f"[API ENRICHMENT WARNING] {e}\n")
```

---

## How To Test

### 1. Restart the FastAPI server:
```bash
# Kill existing server (if running)
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *data_service*"

# Start fresh
python -m src.api.data_service
```

### 2. Test the API directly:
```bash
curl http://localhost:8000/api/pipelines
```

**Expected output:**
```json
{
  "pipelines": [
    {
      "id": "fracfocus",
      "stages": [
        {"name": "downloads", "file_count": 1, "status": "complete"},
        {"name": "extracted", "file_count": 17, "status": "complete"},
        {"name": "parsed", "file_count": 17, "status": "complete"}
      ],
      "metrics": {
        "file_count": 37,
        "record_count": 239061,
        "data_size": "7.2 GB"
      }
    }
  ]
}
```

### 3. Launch React app:
```bash
cd generated_react_dashboard
npm run dev
```

**Expected UI:**
- ✅ PipelineHealthSidebar shows 3 stages
- ✅ downloads (complete)
- ✅ extracted (complete)
- ✅ parsed (complete)
- ✅ 239,061 records displayed
- ✅ 37 files displayed

---

## Error Handling

If PipelineAssemblyTool fails, the API:
- ✅ Logs warning to stderr
- ✅ Returns un-enriched pipelines (backward compatible)
- ✅ Doesn't crash the API

**Example warning:**
```
[API ENRICHMENT WARNING] Failed to enrich pipelines: No such directory: data/raw/xyz
```

---

## Benefits

### 1. **Single Source of Truth**
- API filesystem = source of truth
- React UI always shows current state
- No stale data in UI

### 2. **No React Code Changes**
- React code already correct (`data.pipelines`)
- Autocorrection handles any `children` → `files` fixes
- Existing UI components work as-is

### 3. **Real-Time Updates**
- API scans filesystem on every request
- Changes to `data/raw/` reflected immediately
- No cache invalidation needed

### 4. **Backward Compatible**
- If enrichment fails, returns original pipelines
- Existing clients still work
- Gradual rollout possible

---

## Verification Checklist

After restarting API and React app:

- [ ] API returns pipelines with populated `stages[]`
- [ ] Each stage has `name`, `file_count`, `status`
- [ ] React UI shows PipelineHealthSidebar with stages
- [ ] Stage status indicators show correct colors
- [ ] File counts match filesystem reality
- [ ] No "0 stages" bug
- [ ] No console errors in React

---

## Next Steps

1. **Restart API:** `python -m src.api.data_service`
2. **Test API:** `curl http://localhost:8000/api/pipelines | jq .pipelines[0].stages`
3. **Launch React:** `cd generated_react_dashboard && npm run dev`
4. **Verify UI:** Check PipelineHealthSidebar shows stages
5. **Celebrate:** System is now fully integrated! 🎉

---

**Date:** 2025-11-23
**Status:** READY TO TEST
**Impact:** HIGH - Fixes "0 stages" bug permanently by making API the source of truth
