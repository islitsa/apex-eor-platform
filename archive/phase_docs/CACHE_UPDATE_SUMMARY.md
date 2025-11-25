# Cache Update Summary

## What Was Done

### 1. Regenerated Pipeline Context Cache ✅
```bash
python scripts/pipeline/run_ingestion.py --generate-context
```

**Result:**
- Cache file updated: `C:\Users\irina\.apex_eor\pipeline_state.json`
- Contains 10 datasets with 224,044,778 records (36.49 GB)
- Directory structures include correct `file_count` values

**Verification:**
```bash
python debug_api_file_count.py
```
Shows fracfocus has 37 files total (1 downloads + 17 extracted + 17 parsed + 2 metadata)

### 2. Fixed API File Counting Logic ✅
**File:** `src/api/data_service.py` (lines 485-497)

**Changed from:**
```python
# Old broken logic - looked for individual file objects
def count_files(node):
    if 'size' in value and 'type' in value and value.get('type') == 'file':
        file_count += 1
```

**Changed to:**
```python
# New correct logic - sums file_count from each directory
def count_files(node):
    nonlocal file_count
    if isinstance(node, dict):
        if 'file_count' in node:
            file_count += node['file_count']
        if 'subdirs' in node:
            for subdir in node['subdirs'].values():
                count_files(subdir)
```

### 3. Verified Logic Works Locally ✅
```bash
python test_api_direct.py
```

**Result:** Returns 37 files for fracfocus ✅

## Current Problem ❌

The API endpoint **still returns 0 files** despite:
1. Cache being regenerated with correct data
2. API code being fixed with correct counting logic
3. Local testing confirming the logic works

### Evidence

**HTTP API Response:**
```json
{
  "id": "fracfocus",
  "metrics": {
    "file_count": 0  // ❌ WRONG
  },
  "files": {
    "subdirs": {
      "Chemical_data": {
        "downloads": {
          "file_count": 1  // ✅ Data is here!
        },
        "extracted": {
          "file_count": 17  // ✅ Data is here!
        },
        "parsed": {
          "file_count": 17  // ✅ Data is here!
        }
      }
    }
  }
}
```

The correct data IS in the response, but `file_count` in metrics is 0!

## Hypothesis

There might be:
1. **Python bytecode caching** - The .pyc files have old code
2. **Module import caching** - Uvicorn's auto-reload isn't working
3. **Multiple processes** - An old API server still running
4. **Different code path** - The actual running code differs from what's in the file

## What To Try Next

### Option 1: Force Clean Restart
```bash
# Kill ALL Python processes
tasklist | findstr python
# Kill each PID

# Clear all Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# Restart API
cd C:\Users\irina\apex-eor-platform
python -m src.api.data_service
```

### Option 2: Add Debug Logging
Add print statements to the `count_files()` function in data_service.py:

```python
def count_files(node):
    nonlocal file_count
    if isinstance(node, dict):
        if 'file_count' in node:
            fc = node['file_count']
            file_count += fc
            print(f"[DEBUG API] Adding {fc} files, total: {file_count}")  # ADD THIS
        if 'subdirs' in node:
            for subdir in node['subdirs'].values():
                count_files(subdir)
```

Then check the API server logs to see if the function is being called.

### Option 3: Bypass Cache Entirely
Replace the `/api/pipelines` endpoint to use DiscoveryTools directly:

```python
@app.get("/api/pipelines")
async def get_pipelines():
    from src.agents.context.discovery_tools import DiscoveryTools
    tools = DiscoveryTools()

    pipelines = []
    for source in ['fracfocus', 'rrc_production']:
        status = tools.check_status(source)
        if status:
            total_files = sum(status['files_by_stage'].values())
            pipelines.append({
                'id': source,
                'metrics': {'file_count': total_files},
                'status': status['status']
            })

    return {'pipelines': pipelines}
```

## Files Created During Investigation

1. `debug_check_status.py` - Found the empty directory bug
2. `test_discovery_sources.py` - Comprehensive discovery test
3. `test_api_pipelines.py` - API endpoint tester
4. `test_direct_discovery_api.py` - Shows real-time counts
5. `debug_api_file_count.py` - Debug file counting logic
6. `test_api_direct.py` - Test API logic without HTTP

## Summary

**What's Fixed:**
- ✅ Empty directory bug (removed `data/raw/fracfocus/downloads`)
- ✅ Cache regenerated with correct file counts
- ✅ API counting logic fixed
- ✅ Logic verified to work locally

**What's Still Broken:**
- ❌ HTTP API endpoint returns 0 files
- ❌ The fixed code doesn't seem to be executing in the running server

**Most Likely Cause:**
The running API server is using cached bytecode or hasn't properly reloaded the updated code.
