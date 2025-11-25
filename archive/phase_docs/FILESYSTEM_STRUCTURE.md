# Actual Filesystem Structure

## Issue Analysis

### What API Returns:
```json
"stages": []  // ALL pipelines have empty stages
```

### What Filesystem Has:

#### fracfocus:
```
data/raw/fracfocus/
  ├── Chemical_data/  (detected as 1 stage by PipelineAssemblyTool)
  └── metadata.json
```

#### rrc:
```
data/raw/rrc/
  ├── completions_data/  (should be stage)
  ├── horizontal_drilling_permits/  (should be stage)
  ├── metadata/  (should be stage)
  ├── production/  (should be stage)
  ├── DATA_SUMMARY.md
  ├── QUICK_START.md
  └── README.md
```

### What PipelineAssemblyTool Detected (from logs):
```
[Pipeline] Enhancing: fracfocus
  [Detect] No stages found, detecting from filesystem...
  [OK] Detected 1 stages  ← Found "Chemical_data"
```

## The Problem:

**API returns `stages: []` for ALL pipelines**, but:
1. PipelineAssemblyTool IS detecting stages (saw 1 stage for fracfocus)
2. The enhanced pipelines with stages are NOT persisting
3. Either:
   - Enhanced pipelines aren't being returned correctly
   - OR data_context isn't being updated with enhanced pipelines
   - OR API is being called again and returns original empty stages

## Key Issues:

1. **data_size is STRING not number** → Should be bytes integer
2. **stages always empty** → Stage detection works but doesn't persist
3. **Some files[] are populated, some empty** → Inconsistent

## What Should Happen:

After PipelineAssemblyTool enhancement, fracfocus should have:
```json
{
  "id": "fracfocus",
  "metrics": {
    "data_size": 7730941132  // bytes, not "7.2 GB"
  },
  "stages": [
    {
      "name": "Chemical_data",
      "file_count": X,
      "total_size_bytes": Y,
      "status": "complete"
    }
  ]
}
```
