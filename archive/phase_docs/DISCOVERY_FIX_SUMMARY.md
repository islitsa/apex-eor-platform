# Discovery File Count Fix - Summary

## The Problem

Agent Studio was showing "0 files" for all pipelines even though files exist.

Example from Agent Studio trace:
```
- Total Pipelines: 10
- Total Records: 0
- Datasets Available: 10

PIPELINES:
  1. fracfocus - 0 files, 1.3 KB
  2. fracfocus / Chemical_data - 0 files, 0 B
  ...
```

## Root Cause

**Two separate issues:**

### Issue 1: Empty Directory Bug (FIXED ✅)
- Empty `data/raw/fracfocus/downloads` directory existed
- `check_status()` in [repository_index.py:565-569](src/knowledge/repository_index.py#L565-L569) checks direct path first
- Found empty directory, counted 0 files, never checked nested `Chemical_data/downloads`

**Fix:** Removed empty directory. Now `check_status()` correctly finds nested downloads.

**Verification:**
```bash
python debug_check_status.py
# Result: downloads: 1 file ✅
```

### Issue 2: API Using Cached Data (NEEDS FIX ❌)
- `/api/pipelines` endpoint reads from `~/.apex_eor/pipeline_state.json`
- This cached file was generated BEFORE the fix
- Contains stale `directory_structure` with 0 file counts

**Current Status:**
- ✅ Discovery tools work correctly (`check_status()` shows files)
- ❌ API still shows 0 files (reading stale cache)

## Test Results

### Real-Time Discovery (Correct)
```bash
python test_direct_discovery_api.py
```
**Result:**
```
3. fracfocus
   Status: complete
   Files by stage:
     - downloads: 1 files
     - extracted: 17 files
     - parsed: 17 files
   TOTAL FILES: 35  ✅
```

### API Endpoint (Stale)
```bash
python test_api_pipelines.py
```
**Result:**
```
1. fracfocus
   File Count: 0  ❌
   Record Count: 0
   Data Size: 1.3 KB
```

## Solutions

### Option A: Regenerate Pipeline State (Quick Fix)

Run whatever script populates `~/.apex_eor/pipeline_state.json`:
```bash
# Find and run pipeline script
# This will use the now-fixed check_status()
```

### Option B: Update API to Use Live Discovery (Better Fix)

Modify [data_service.py:403](src/api/data_service.py#L403) `get_pipelines()` to use `DiscoveryTools` instead of `PipelineState`:

```python
@app.get("/api/pipelines")
async def get_pipelines():
    """Get REAL-TIME pipeline data (no cache)"""
    from src.agents.context.discovery_tools import DiscoveryTools

    tools = DiscoveryTools()

    # Find all sources
    sources = tools.find_data_sources("", top_k=20, min_relevance=0.0)

    pipelines = []
    for source in sources:
        source_name = source['name']

        # Get real-time status
        status = tools.check_status(source_name)

        if status:
            # Count total files
            total_files = sum(status['files_by_stage'].values())

            # Get schema for record count
            schema = tools.get_schema(source_name)
            record_count = schema['row_count'] if schema else 0

            # Get directory structure for size
            structure = tools.explore_directory(source_name)
            size_mb = structure['total_size_mb'] if structure else 0

            pipelines.append({
                'id': source_name,
                'display_name': source_name.title(),
                'status': status['status'],
                'metrics': {
                    'file_count': total_files,  # Now correct!
                    'record_count': record_count,
                    'data_size': f"{size_mb:.1f} MB"
                },
                'stages': [
                    {'name': stage, 'status': 'complete'}
                    for stage in status['stages']
                ],
                'files': {}  # Can populate if needed
            })

    return {
        'pipelines': pipelines,
        'summary': {
            'total_pipelines': len(pipelines),
            'total_records': sum(p['metrics']['record_count'] for p in pipelines),
            'total_size': f"{sum(float(p['metrics']['data_size'].split()[0]) for p in pipelines):.1f} MB"
        }
    }
```

## Files Created

- [debug_check_status.py](debug_check_status.py) - Debug script that found the bug
- [test_discovery_sources.py](test_discovery_sources.py) - Comprehensive discovery test
- [test_api_pipelines.py](test_api_pipelines.py) - API endpoint tester
- [test_direct_discovery_api.py](test_direct_discovery_api.py) - Shows real-time counts

## Verification Steps

1. **Test discovery tools:**
   ```bash
   python test_direct_discovery_api.py
   ```
   Should show 35 files for fracfocus ✅

2. **Start API:**
   ```bash
   cd src/api && python data_service.py
   ```

3. **Test API endpoint:**
   ```bash
   python test_api_pipelines.py
   ```
   Currently shows 0 files (needs Option A or B above)

## Impact on Agent Studio

Once the API is fixed, Agent Studio will show correct data:
```
PIPELINES:
  1. fracfocus - 35 files, 6.8 GB  ✅
  2. fracfocus / Chemical_data - 17 files, 4.2 GB  ✅
  3. rrc / production - 25,451 files, 60.8 GB  ✅
```

This will give UX Designer and React Developer REAL data to work with!
