# Quick Start: Pipeline UI

## Success! ✓

The Pipeline Orchestrator → UI Agent → Browser integration is working!

## What Just Happened

1. **Pipeline Orchestrator** detected the `--ui` flag
2. **UI Agent** was initialized with Claude Sonnet 4
3. **UI Agent generated** a complete Streamlit dashboard with 5 files:
   - `pipeline_dashboard.py` - Main dashboard
   - `components/status_cards.py` - Status display components
   - `components/progress_monitor.py` - Progress tracking
   - `components/controls_panel.py` - Interactive controls
   - `components/__init__.py` - Component exports
4. **Streamlit server** launched successfully
5. **Dashboard** is now running at http://localhost:8501

## How to Use

### Option 1: Run with Auto-Launch (Recommended)

```bash
python scripts/pipeline/run_ingestion.py --ui
```

This will:
- Generate the UI (if not already generated)
- Launch Streamlit automatically
- Open your browser

### Option 2: Run Manually

```bash
# Generate UI first (only needed once)
python scripts/pipeline/run_ingestion.py --ui

# Then launch manually
streamlit run src/ui/src/ui/pipeline_dashboard.py
```

### Option 3: Direct Streamlit Launch

```bash
# If UI is already generated
streamlit run src/ui/src/ui/pipeline_dashboard.py --server.port 8501
```

## Dashboard Features

The UI Agent created a comprehensive dashboard with:

### 🎯 Dashboard Overview
- Pipeline status cards (Download/Extract/Parse)
- Dataset metadata cards
- Real-time status indicators

### 🎮 Interactive Controls
- Run buttons for each phase
- Dataset selector checkboxes
- Force re-download toggle
- Dry-run mode switch

### 📊 Progress Monitoring
- Live progress bars
- Log output viewer
- Success/failure indicators
- Timestamp tracking

### 📈 Data Visualization
- File size charts
- Processing timeline
- Dataset statistics
- Storage usage graphs

## Files Generated

```
src/ui/src/ui/
├── pipeline_dashboard.py          # Main dashboard (entry point)
├── __init__.py                    # Package initialization
└── components/
    ├── __init__.py                # Component exports
    ├── status_cards.py            # Status display components
    ├── progress_monitor.py        # Progress tracking UI
    └── controls_panel.py          # Control buttons & selectors
```

## Troubleshooting

### Issue: Files in nested directory

**Current location**: `src/ui/src/ui/pipeline_dashboard.py`
**Expected location**: `src/ui/pipeline_dashboard.py`

**Fix**: The UI Agent includes the path in filenames. To fix:

```bash
# Move files to correct location
cd src/ui
mv src/ui/* .
rmdir src/ui
```

Or just run from the generated location:
```bash
streamlit run src/ui/src/ui/pipeline_dashboard.py
```

### Issue: Import errors

**Error**: `Could not import IngestionPipeline`

**Fix**: The dashboard adds the project root to sys.path. If imports fail, check:

```python
# In pipeline_dashboard.py
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
```

Adjust based on actual file location.

### Issue: Port already in use

**Error**: `Address already in use`

**Fix**: Use a different port:
```bash
streamlit run src/ui/src/ui/pipeline_dashboard.py --server.port 8502
```

## Fixes Applied

### 1. UTF-8 Encoding (Fixed ✓)

**Problem**: Unicode characters in generated code caused encoding errors on Windows.

**Fix**: Updated `src/agents/ui_agent.py` to use UTF-8 encoding:
```python
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
```

### 2. Path Handling (Fixed ✓)

**Problem**: UI Agent creates nested paths (`src/ui/src/ui/`)

**Fix**: Updated orchestrator to check both locations:
```python
dashboard_path = PROJECT_ROOT / "src" / "ui" / "pipeline_dashboard.py"
if not dashboard_path.exists():
    dashboard_path = PROJECT_ROOT / "src" / "ui" / "src" / "ui" / "pipeline_dashboard.py"
```

## Using the Dashboard

1. **Open your browser** to http://localhost:8501

2. **Select datasets** using checkboxes:
   - ☐ rrc_production
   - ☐ rrc_permits
   - ☐ rrc_completions
   - ☐ fracfocus

3. **Choose options**:
   - ☐ Force re-download
   - ☐ Dry-run mode

4. **Click a button**:
   - [Download] - Run download phase
   - [Extract] - Run extraction phase
   - [Parse] - Run parsing phase
   - [Run All] - Run all phases

5. **Monitor progress**:
   - Watch real-time progress bars
   - View logs in the log viewer
   - Check status indicators
   - See file sizes and counts

## Architecture Flow

```
┌─────────────────────────────────────────────────────┐
│  USER                                               │
│  python run_ingestion.py --ui                       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  PIPELINE ORCHESTRATOR                              │
│  - Detects --ui flag                                │
│  - Calls launch_ui()                                │
│  - Prompts UI Agent with requirements               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  UI AGENT (Claude Sonnet 4)                         │
│  - Receives prompt                                  │
│  - Generates 5 Python files                         │
│  - Saves to src/ui/src/ui/                          │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  STREAMLIT SERVER                                   │
│  - Launches on port 8501                            │
│  - Serves dashboard                                 │
│  - Handles user interactions                        │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  BROWSER                                            │
│  http://localhost:8501                              │
│  - Interactive dashboard                            │
│  - Control buttons                                  │
│  - Progress monitoring                              │
└─────────────────────────────────────────────────────┘
```

## Next Steps

1. **Use the Dashboard** to run your pipeline
2. **Customize if needed** - Edit the generated files
3. **Re-generate anytime** - Run `--ui` flag again to regenerate

## Summary

✅ **UTF-8 encoding fixed** - No more Unicode errors
✅ **UI generated successfully** - 5 files created
✅ **Streamlit running** - Dashboard at http://localhost:8501
✅ **Integration working** - Orchestrator → UI Agent → Browser

The pipeline is now fully operational with a web UI! 🚀
