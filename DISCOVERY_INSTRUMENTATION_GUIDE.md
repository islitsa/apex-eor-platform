# Discovery Instrumentation Framework - User Guide

## Overview

This framework tracks discovery tool performance to identify bottlenecks and validate whether gradient context improvements (like path coordinates) actually help.

## Quick Start

### 1. Run the Validation Test

```bash
cd C:\Users\irina\apex-eor-platform
python test_discovery_validation.py
```

This will:
- Test 3 scenarios (no context, topology hints, path coordinates)
- Run multiple discovery operations per scenario
- Save detailed logs to `logs/discovery/`
- Print comparison results

**Expected output:**
```
VALIDATION RESULTS
==================
1. No Context:
  Success rate: 100.0%
  Total duration: 12345ms
  ...

2. Topology Hints:
  Success rate: 100.0%
  ...

3. Path Coordinates:
  Success rate: 100.0%
  ...

KEY FINDINGS
============
✗ Path coordinates did NOT make a measurable difference
```

### 2. Analyze the Results

```bash
python analyze_discovery_results.py
```

This reads all the JSON logs and provides detailed analysis:
- Location tracking (where discovery searched)
- Performance breakdown
- Key insights about bottlenecks

## Using the Instrumentation in Your Code

### Basic Usage

```python
from src.agents.context.discovery_tools_instrumented import InstrumentedDiscoveryTools

# Create instrumented tools with your gradient context
gradient_context = {
    'structure': 'deeply_nested_directories',
    'data_root': 'data/raw'
}

tools = InstrumentedDiscoveryTools(gradient_context=gradient_context)

# Start a session
tools.start_session("my_test")

# Use discovery tools normally
sources = tools.find_data_sources("chemical data")
schema = tools.get_schema("fracfocus")
status = tools.check_status("fracfocus")

# End session and get metrics
session = tools.end_session()

print(f"Success rate: {session.success_rate}")
print(f"Avg duration: {session.avg_duration_ms}ms")
print(f"Missing hints: {session.missing_path_hints}")
```

### Testing Specific Hypotheses

#### Hypothesis: "Path coordinates will speed up discovery"

```python
# Test WITHOUT path coordinates
tools_baseline = InstrumentedDiscoveryTools(gradient_context={})
tools_baseline.start_session("baseline")

sources = tools_baseline.find_data_sources("production data")
session_baseline = tools_baseline.end_session()

# Test WITH path coordinates
gradient_with_paths = {
    'data_paths': {
        'rrc': {'root_path': 'data/raw/rrc/production'}
    }
}

tools_with_paths = InstrumentedDiscoveryTools(gradient_context=gradient_with_paths)
tools_with_paths.start_session("with_paths")

sources = tools_with_paths.find_data_sources("production data")
session_with_paths = tools_with_paths.end_session()

# Compare
print(f"Baseline: {session_baseline.avg_duration_ms:.1f}ms")
print(f"With paths: {session_with_paths.avg_duration_ms:.1f}ms")

if session_with_paths.avg_duration_ms < session_baseline.avg_duration_ms:
    print("✓ Path coordinates helped!")
else:
    print("✗ Path coordinates didn't help")
```

#### Hypothesis: "Discovery fails when searching for non-existent sources"

```python
tools = InstrumentedDiscoveryTools()
tools.start_session("failure_test")

# Try to find something that doesn't exist
sources = tools.find_data_sources("unicorn data that doesn't exist")
schema = tools.get_schema("nonexistent_source")

session = tools.end_session()

print(f"Failed operations: {session.failed_attempts}")
print(f"Missing path hints: {session.missing_path_hints}")

# If missing_path_hints > 0, then path coordinates WOULD help
if session.missing_path_hints > 0:
    print("✓ Path coordinates would help with failures")
```

## Understanding the Metrics

### Session Metrics

```python
session = tools.end_session()

session.success_rate          # 0.0-1.0 (1.0 = 100% success)
session.avg_duration_ms       # Average time per operation
session.failed_attempts       # Number of failed operations
session.navigation_errors     # Searched wrong places
session.missing_path_hints    # Times path coordinates would have helped
session.missing_structure_hints  # Times directory structure would have helped
```

### Attempt Metrics

Each discovery operation is tracked:

```python
for attempt in session.attempts:
    print(f"Method: {attempt.method}")
    print(f"Query: {attempt.query}")
    print(f"Success: {attempt.success}")
    print(f"Duration: {attempt.duration_ms}ms")
    print(f"Searched: {attempt.searched_locations}")
    print(f"Found at: {attempt.actual_location}")
    print(f"Missing hint: {attempt.missing_hint_type}")
```

## Interpreting Results

### Scenario 1: Path Coordinates Help

```
Success rate: 75.0% → 100.0%
Missing path hints: 3 → 0
Navigation errors: 2 → 0
```

**Interpretation:** Discovery was failing or searching wrong places. Path coordinates fixed it.

**Action:** Add path coordinates to gradient context!

### Scenario 2: Path Coordinates Don't Help (Current Finding)

```
Success rate: 100.0% → 100.0%
Avg duration: 4500ms → 4500ms
Navigation errors: 0 → 0
Missing path hints: 0 → 0
```

**Interpretation:** Discovery already works. Path coordinates don't change anything.

**Action:** Focus on caching/performance instead of path coordinates.

### Scenario 3: Performance Bottleneck Identified

```
Slowest operations:
  1. find_data_sources: 4500ms
  2. get_schema: 1600ms
  3. check_status: 10ms
```

**Interpretation:** Semantic search (4500ms) and schema loading (1600ms) are slow.

**Action:** Implement caching for embeddings and schemas.

## Testing Different Scenarios

### Test with Real Agent Workflow

```python
# Simulate what UX Designer agent does
tools = InstrumentedDiscoveryTools(gradient_context={
    'current_agent': 'ux_designer',
    'data_root': 'data/raw'
})

tools.start_session("ux_designer_workflow")

# Agent discovers data
results = tools.discover_all("chemical data for visualization")

# Agent explores specific source
for source in results['sources']:
    tools.explore_directory(source['name'])

session = tools.end_session()

# Check if agent needed hints
if session.missing_path_hints > 0:
    print("Agent would benefit from path coordinates!")
```

### Test with Missing Data

```python
# Test what happens when data isn't indexed
tools = InstrumentedDiscoveryTools()
tools.start_session("missing_data_test")

try:
    # Search for source that's not in Pinecone
    schema = tools.get_schema("brand_new_unindexed_source")
except Exception:
    pass

session = tools.end_session()

# Check if gradient context would have helped as fallback
print(f"Missing hints: path={session.missing_path_hints}, "
      f"structure={session.missing_structure_hints}")
```

## Advanced: Custom Instrumentation

### Track Custom Operations

```python
from src.agents.context.discovery_instrumentation import DiscoveryInstrumentor

instrumentor = DiscoveryInstrumentor()
instrumentor.start_session("custom_test")

# Track your own operations
with instrumentor.track_operation('custom_operation', 'my query') as tracker:
    # Do something
    result = my_custom_discovery_function()

    tracker.record_success(
        result,
        searched=['path1', 'path2'],
        actual_location='path2'
    )

session = instrumentor.end_session()
```

### Analyze Logs Programmatically

```python
import json
from pathlib import Path

logs_dir = Path("logs/discovery")

for log_file in logs_dir.glob("*.json"):
    with open(log_file) as f:
        session = json.load(f)

    # Find slow operations
    slow_ops = [a for a in session['attempts']
                if a['duration_ms'] > 1000]

    # Find operations that needed hints
    needed_hints = [a for a in session['attempts']
                    if a['missing_hint_type']]

    print(f"{log_file.name}:")
    print(f"  Slow operations: {len(slow_ops)}")
    print(f"  Needed hints: {len(needed_hints)}")
```

## Expected Findings (Based on Current Results)

### What You'll Probably See

1. **100% success rate** - Discovery works without path coordinates
2. **Semantic search is slow** (~4500ms for `find_data_sources`)
3. **Schema loading is slow** (~1600ms for `get_schema`)
4. **No navigation errors** - Pinecone handles path resolution
5. **Missing hints = 0** - Path coordinates not needed

### What Would Change This

- If you **remove Pinecone** and do filesystem traversal → path coordinates would help
- If you **have unindexed sources** → path coordinates could provide fallback
- If you **add real-time data** → gradient context could hint at new locations

## Validation Checklist

Use this to validate the findings:

- [ ] Run `python test_discovery_validation.py`
- [ ] Confirm all 3 scenarios succeed (success_rate = 100%)
- [ ] Check that path coordinates don't improve success rate
- [ ] Check that path coordinates don't improve performance
- [ ] Check that `missing_path_hints` = 0 for all scenarios
- [ ] Review slowest operations (should be `find_data_sources`)
- [ ] Check JSON logs in `logs/discovery/` for raw data

If all checkboxes are ✓, then the finding is validated:
> **Path coordinates don't help because discovery uses Pinecone, not filesystem traversal**

## Next Steps

### If Path Coordinates Don't Help (Current Finding)

1. **Add caching** to speed up Pinecone queries
2. **Cache schemas** to avoid re-reading CSV files
3. **Pre-load common sources** in gradient context
4. **Use local embeddings** instead of OpenAI API

### If Path Coordinates DO Help (Unexpected)

1. **Add path coordinates to gradient context**
2. **Implement path resolution** in discovery tools
3. **Use gradient hints for filesystem fallback**
4. **Update gradient context generation** to include paths

## Troubleshooting

### "Unicode encoding error"

The instrumentation tries to print summary to console. If you see Unicode errors, results are still saved to JSON. Just run:

```bash
python analyze_discovery_results.py
```

### "No logs found"

Make sure to call `tools.start_session()` and `tools.end_session()`. Logs are only written on `end_session()`.

### "searched_locations is always empty"

This means the instrumentation isn't capturing where discovery looks. To fix:

1. Add deeper tracking in `RepositoryIndex.get_directory_structure()`
2. Track Pinecone query parameters
3. Log filesystem operations in `_analyze_directory()`

## Files Reference

- **[discovery_instrumentation.py](src/agents/context/discovery_instrumentation.py)** - Core instrumentation framework
- **[discovery_tools_instrumented.py](src/agents/context/discovery_tools_instrumented.py)** - Instrumented wrapper
- **[test_discovery_validation.py](test_discovery_validation.py)** - Validation test script
- **[analyze_discovery_results.py](analyze_discovery_results.py)** - Results analyzer
- **[DISCOVERY_INSTRUMENTATION_REPORT.md](DISCOVERY_INSTRUMENTATION_REPORT.md)** - Initial findings report
- **logs/discovery/*.json** - Raw instrumentation data

## Summary

This framework lets you **empirically validate** architectural hypotheses like:
- "Do path coordinates help discovery?"
- "Where is the performance bottleneck?"
- "When does discovery fail?"

The current finding: **Path coordinates don't help** because discovery uses Pinecone semantic search, which already contains path information. The bottleneck is **API performance**, not **navigation**.

Use this framework to test other hypotheses or validate changes to the discovery system!
