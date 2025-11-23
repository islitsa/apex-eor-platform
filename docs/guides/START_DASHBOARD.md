# APEX Pipeline Dashboard - Quick Start

## Current Working Dashboards

Dashboards are now located in: `scripts/dashboard/`

### Option 1: Professional Dashboard (Recommended)
**File:** `scripts/dashboard/pipeline_dashboard_v2.py`

**To Launch:**
```bash
python scripts/dashboard/pipeline_dashboard_v2.py
```

**Access:** http://localhost:7861

**Features:**
- Professional charts and visualizations
- Real-time metrics from metadata.json files
- Per-source status cards
- Clean, production-ready design

---

### Option 2: Simple Working Dashboard
**File:** `scripts/dashboard/pipeline_dashboard_working.py`

**To Launch:**
```bash
python scripts/dashboard/pipeline_dashboard_working.py
```

**Access:** http://localhost:7860

**Features:**
- Minimal, guaranteed to work
- Shows real metrics (541K records from RRC Completions)
- No dependencies on AI generation

---

### Option 3: AI-Generated Dashboard
**Via Pipeline:**
```bash
python scripts/pipeline/run_ingestion.py --ui
```

**Features:**
- Claude AI generates dashboard on the fly
- Requires Anthropic API credits
- Customizable based on prompt

---

## Dashboard Metrics

All dashboards read real data from metadata.json files:
- **RRC Production:** Production data
- **RRC Completions:** Completion data (541K+ records)
- **RRC Permits:** Horizontal drilling permits
- **FracFocus:** Chemical disclosures

---

## If You Need to Update Metrics

If you run the pipeline and data changes, sync the metadata:

```bash
python scripts/sync_metadata.py
```

Then restart the dashboard.

---

## System Architecture

**Current Stack:**
- **Framework:** Gradio (Python)
- **AI Model:** Claude Sonnet 4.5 (Anthropic)
- **Knowledge Base:** Pinecone (RAG for design guidelines)
- **Evolutionary UI:** Iterative refinement system for UI quality

**Key Components:**
- [scripts/pipeline/run_ingestion.py](scripts/pipeline/run_ingestion.py) - Main pipeline with `--ui` flag
- [src/agents/ui_agent_gradio_generator.py](src/agents/ui_agent_gradio_generator.py) - AI-powered UI generator
- [src/agents/evolutionary_ui_system.py](src/agents/evolutionary_ui_system.py) - Iterative UI improvement
- [src/knowledge/design_kb_pinecone.py](src/knowledge/design_kb_pinecone.py) - Design knowledge base
