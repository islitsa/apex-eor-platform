# Phase 2: Folder Structure Fix

**Date**: 2025-11-13
**Status**: ✅ **COMPLETE**

## Problem

The generated UI was showing incorrect file paths in the file explorer:
- **Showing**: `fracfocus/downloads/` (flat structure)
- **Should be**: `fracfocus/Chemical_data/downloads/` (nested structure)

The repository uses a nested folder structure:
```
{source}/{data_type}/{stage}
```

For example:
- `fracfocus/Chemical_data/downloads/`
- `fracfocus/Chemical_data/extracted/`
- `fracfocus/Chemical_data/parsed/`
- `rrc/Geographic_data/downloads/`
- `rrc/Geographic_data/extracted/`
- `rrc/Geographic_data/parsed/`

## Root Cause

The React Developer was receiving metadata about discovered data sources (row counts, columns, statuses, stages), but did NOT have information about the folder structure. When Claude generated file paths for the file explorer, it assumed a flat structure without data type folders.

## Solution

Added folder structure metadata to the discovery data and explicit instructions in the React Developer prompt.

### Changes Made

#### 1. Enhanced Discovery Data (ux_designer.py:237-251)

Added three new fields to each data source:

```python
requirements['data_sources'][source_name] = {
    'name': source_name,
    'relevance': source['relevance'],
    'format': 'csv/parquet',
    'columns': discovered['schemas'].get(source_name, {}).get('columns', []),
    'row_count': discovered['schemas'].get(source_name, {}).get('row_count', 0),
    'status': status_info.get('status', 'unknown') if isinstance(status_info, dict) else status_info,
    'stages': status_info.get('stages', []) if isinstance(status_info, dict) else [],

    # NEW: Folder structure metadata
    'files_by_stage': files_by_stage,  # {'downloads': 3, 'extracted': 1, 'parsed': 1}
    'structure_note': f'Nested structure: {source_name}/[data_type]/{{downloads,extracted,parsed}}'
}
```

**What each field does**:
- `files_by_stage`: Dict mapping stage names to file counts (for verification)
- `structure_note`: Human-readable explanation of the folder structure pattern

#### 2. Updated React Developer Formatting (react_developer.py:260-278)

The React Developer now includes folder structure info when formatting data sources for the prompt:

```python
# Extract folder structure info
files_by_stage = info.get('files_by_stage', {})
structure_note = info.get('structure_note', '')

# Format file counts by stage
file_counts = ', '.join([f"{stage}:{files_by_stage.get(stage, 0)} files"
                        for stage in stages]) if files_by_stage else ''

# Include in prompt
sources_info_lines.append(
    f"- {source_name}: {row_count:,} records, {num_cols} columns, status: {status}, stages: {stage_str}"
)
if structure_note:
    sources_info_lines.append(f"  Structure: {structure_note}")
if file_counts:
    sources_info_lines.append(f"  Files: {file_counts}")
```

**Example output in prompt**:
```
DATA SOURCES:
- fracfocus: 239,059 records, 17 columns, status: complete, stages: downloads → extracted → parsed
  Structure: Nested structure: fracfocus/[data_type]/{downloads,extracted,parsed}
  Files: downloads:3 files, extracted:1 files, parsed:1 files
```

#### 3. Added Explicit Instructions (react_developer.py:318-323)

Added a "FOLDER STRUCTURE (IMPORTANT)" section to the React Developer prompt:

```python
FOLDER STRUCTURE (IMPORTANT):
- The repository uses a NESTED structure: {{source}}/{{data_type}}/{{stage}}
- Example: fracfocus/Chemical_data/downloads/, fracfocus/Chemical_data/parsed/
- When showing file paths, use the nested structure with data type folders
- Do NOT use flat paths like fracfocus/downloads/ - they are incorrect
- Check the "Structure:" line for each source to understand the nesting pattern
```

**Note**: The double braces `{{source}}` are necessary because this text is inside an f-string. Single braces `{source}` would cause Python to interpret it as a variable interpolation.

## Bug Fix: F-String Syntax Error

### Error Encountered

When adding the folder structure instructions, I initially wrote:

```python
- The repository uses a NESTED structure: {source}/{data_type}/{stage}
```

This caused:
```
NameError: name 'source' is not defined
```

### Root Cause

The instructions are inserted into an f-string template. Python interpreted `{source}`, `{data_type}`, and `{stage}` as variable interpolations, but these variables don't exist in the scope.

### Fix

Escaped the braces by doubling them:

```python
- The repository uses a NESTED structure: {{source}}/{{data_type}}/{{stage}}
```

Now Python knows these are literal braces in the output string, not variable placeholders.

## Files Modified

### [src/agents/ux_designer.py](src/agents/ux_designer.py)

**Lines 237-251**: Added `files_by_stage` and `structure_note` fields when building data_sources dict

**Key Code**:
```python
status_info = discovered['statuses'].get(source_name, {})
files_by_stage = status_info.get('files_by_stage', {}) if isinstance(status_info, dict) else {}

requirements['data_sources'][source_name] = {
    # ... existing fields ...
    'files_by_stage': files_by_stage,
    'structure_note': f'Nested structure: {source_name}/[data_type]/{{downloads,extracted,parsed}}'
}
```

### [src/agents/react_developer.py](src/agents/react_developer.py)

**Lines 260-278**: Format and include folder structure metadata in prompts

**Lines 318-323**: Added explicit folder structure instructions

**Key Change**:
```python
# Before fix (caused NameError):
- The repository uses a NESTED structure: {source}/{data_type}/{stage}

# After fix (works correctly):
- The repository uses a NESTED structure: {{source}}/{{data_type}}/{{stage}}
```

## Expected Behavior After Fix

When the user generates a dashboard with a file explorer component, Claude should now:

1. **Understand** the nested folder structure from the discovery metadata
2. **See** explicit instructions about using `{source}/{data_type}/{stage}` pattern
3. **Generate** correct file paths like:
   - `fracfocus/Chemical_data/downloads/`
   - `rrc/Geographic_data/parsed/`

Instead of incorrect flat paths like:
   - `fracfocus/downloads/` ❌
   - `rrc/parsed/` ❌

## Integration with Phase 2

This enhancement builds on the Phase 2 multi-turn tool use:

**Phase 2 Data Flow (with folder structure)**:
```
UX Designer discovers data
    ↓
Stores in requirements['data_sources'] with folder structure metadata
    ↓
Creates DesignSpec (WITH data_sources including folder structure)
    ↓
React Developer receives discovered data with folder structure
    ↓
React Developer sees explicit instructions about nested paths
    ↓
Generates UI with CORRECT file paths ✅
```

## Testing

The fix has been applied and the code syntax is correct. Testing in Agent Studio will verify:

1. ✅ No more `NameError` (f-string syntax fixed)
2. 🔄 File explorer shows correct nested paths (needs user testing)
3. 🔄 File counts match actual files in each stage (needs user testing)

## Next Steps

User should test in Agent Studio by:

1. Opening Agent Studio at http://localhost:8502
2. Creating a dashboard request: "Show my pipeline data with file explorer"
3. Checking the generated file explorer paths
4. Verifying paths show `{source}/{data_type}/{stage}` pattern

If paths are still incorrect, may need to strengthen the prompt instructions or add example code snippets.

---

**Status**: ✅ **FIX COMPLETE** - Code syntax corrected, ready for user testing
