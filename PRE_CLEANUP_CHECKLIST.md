# Pre-Cleanup Safety Checklist

> **Created:** 2025-11-25
> **Purpose:** Document the working state BEFORE any cleanup operations

---

## 1. Git Safety

Before ANY changes:

```bash
# Create safety branch
git checkout -b pre-cleanup-backup
git add -A
git commit -m "Snapshot before cleanup - $(date +%Y%m%d)"
git push origin pre-cleanup-backup

# Return to main and create working branch
git checkout main
git checkout -b cleanup-phase-1
```

---

## 2. What "Working" Means

### 2.1 Core Entry Points

| Command | What it does | Success criteria |
|---------|--------------|------------------|
| `python launch.py` | Interactive menu | Menu displays, no import errors |
| `python launch.py status` | Show platform status | Prints status without crashing |
| `streamlit run src/ui/agent_studio.py` | Launch Agent Studio | Opens in browser at localhost:8501 |
| `python shared_state.py` | Print state info | Shows state directory info |

### 2.2 Core Module Imports

These imports MUST work after cleanup:

```python
# Run this to verify core imports
python -c "
import sys
sys.path.insert(0, '.')

from shared_state import PipelineState, FavoritesManager, SessionState
from src.agents.shared_memory import SharedSessionMemory
from src.agents.ui_orchestrator import UICodeOrchestrator
from src.agents.ux_designer import UXDesignerAgent, DesignSpec
from src.agents.react_developer import ReactDeveloperAgent
from src.agents.context.protocol import SessionContext
from src.agents.tools.discovery_tool import DataDiscoveryTool
from src.agents.tools.filter_tool import DataFilterTool
from src.agents.tools.knowledge_tool import KnowledgeTool

print('All core imports OK')
"
```

### 2.3 Key File Dependencies

**DO NOT DELETE these files** (they are imported by other modules):

```
shared_state.py                          # Used by launch.py, agent_studio.py
src/agents/__init__.py
src/agents/ui_orchestrator.py            # Main orchestrator
src/agents/ux_designer.py                # UX agent
src/agents/react_developer.py            # React agent
src/agents/shared_memory.py              # Agent coordination
src/agents/orchestrator_agent.py         # Lower-level orchestrator
src/agents/context/protocol.py           # Session/context protocol
src/agents/context/adapter.py            # Context adaptation
src/agents/context/gradient_context.py   # Gradient field system
src/agents/tools/discovery_tool.py       # Data discovery
src/agents/tools/filter_tool.py          # Data filtering
src/agents/tools/knowledge_tool.py       # Knowledge queries
src/ui/agent_studio.py                   # Main UI
src/ui/trace_collector.py                # Trace collection
src/knowledge/design_kb_pinecone.py      # Pinecone integration
src/templates/gradio_snippets.py         # UI templates
```

---

## 3. Verification Commands

Run these AFTER each cleanup phase:

### 3.1 Quick Smoke Test

```bash
# Should complete without errors
python -c "from shared_state import PipelineState; print('OK')"
python -c "from src.agents.ui_orchestrator import UICodeOrchestrator; print('OK')"
python launch.py status
```

### 3.2 Import Test (All Core Modules)

```bash
python -c "
import sys
sys.path.insert(0, '.')

modules = [
    'shared_state',
    'src.agents.shared_memory',
    'src.agents.ui_orchestrator', 
    'src.agents.ux_designer',
    'src.agents.react_developer',
    'src.agents.context.protocol',
    'src.agents.context.adapter',
    'src.agents.tools.discovery_tool',
    'src.agents.tools.filter_tool',
    'src.agents.tools.knowledge_tool',
    'src.knowledge.design_kb_pinecone',
]

failed = []
for mod in modules:
    try:
        __import__(mod)
    except Exception as e:
        failed.append((mod, str(e)[:50]))

if failed:
    print('FAILED IMPORTS:')
    for mod, err in failed:
        print(f'  {mod}: {err}')
    exit(1)
else:
    print(f'All {len(modules)} core modules import OK')
"
```

### 3.3 UI Launch Test

```bash
# Should open browser without Python errors
# (May show warnings about missing API keys - that's OK)
timeout 10 streamlit run src/ui/agent_studio.py --server.headless true 2>&1 | head -20
```

---

## 4. Files Safe to Delete

These are confirmed safe to remove (backups, duplicates, artifacts):

### 4.1 Backup Files in src/ui/

```
src/ui/agent_studio.py.backup
src/ui/agent_studio.py.old  
src/ui/agent_studio_OLD_BACKUP.py
src/ui/agent_chat_runner.py.backup
src/ui/agent_chat_runner.py.backup2
src/ui/agent_chat_runner.py.backup3
src/ui/agent_chat_interface.py.backup
src/ui/agent_collaborative_system.py.broken
src/ui/agent_collaborative_system.py.broken_async
```

### 4.2 Backup Files at Root

```
generated_ui_BROKEN_BACKUP.py
generated_ui_OLD_FALLBACK_BACKUP.py
src/templates/gradio_snippets.py.backup
scripts/pipeline/run_ingestion.py.backup
scripts/pipeline/run_ingestion.py.backup2
```

### 4.3 Temporary/Debug Files at Root

```
temp_prompt.txt
temp_ui.py
studio_generated_ui.py (empty file)
debug_discovery.json
debug_post_assembly.json
api_response.json (254KB - generated output)
```

---

## 5. Files to ARCHIVE (not delete)

Move these to `archive/` folder - they contain design history:

### 5.1 Phase Documentation (36 files)

```bash
mkdir -p archive/phase_docs
mv PHASE_*.md archive/phase_docs/
```

### 5.2 Fix/Complete Documentation

```bash
mv *_FIX*.md *_COMPLETE*.md *_SUMMARY.md archive/phase_docs/
```

### 5.3 Agent Chat Logs

```bash
mkdir -p archive/chat_logs
mv agent_chat_*.txt archive/chat_logs/
mv agent_traces_*.txt archive/chat_logs/
mv agent_studio_history_*.json archive/chat_logs/
```

---

## 6. Rollback Procedure

If something breaks:

```bash
# Option 1: Revert to backup branch
git checkout pre-cleanup-backup
git checkout -b main-restored
git push origin main-restored --force

# Option 2: Restore specific file from backup
git checkout pre-cleanup-backup -- path/to/file.py

# Option 3: Full reset (nuclear option)
git reset --hard pre-cleanup-backup
```

---

## 7. Cleanup Order

Execute in this order to minimize risk:

1. **Phase 1.1:** Move test files to tests/ (LOW RISK)
2. **Phase 1.2:** Archive phase documentation (LOW RISK)  
3. **Phase 1.3:** Delete backup files (LOW RISK)
4. **Phase 1.4:** Consolidate generated outputs (MEDIUM RISK)
5. **Phase 2:** Fix React dashboard structure (MEDIUM RISK)
6. **Phase 3:** Analyze large files (ANALYSIS ONLY)

**Run verification after EACH phase.**

---

## 8. Current Test Baseline

### Test Files Status

| File | Status | Notes |
|------|--------|-------|
| tests/test_context_adapter.py | RUNS | 4 failures (version mismatch, missing keys) |
| tests/test_design_system_consistency.py | RUNS | Needs PINECONE_API_KEY |
| tests/test_discovery_tool.py | RUNS | Passes |
| tests/test_filter_tool.py | RUNS | 2 failures |
| tests/test_knowledge_tool.py | RUNS | Passes |
| tests/test_m3_dashboard.py | BROKEN | Imports `agents.component_assembler` (doesn't exist) |
| tests/test_protocol.py | RUNS | Needs API keys |
| tests/unit/test_ui_agent_enhanced.py | BROKEN | Imports `src.agents.ui_agent_enhanced` (doesn't exist) |

### Baseline Results (2025-11-25)

```
93 passed
13 failed  
2 skipped
7 errors
2 test files broken (can't import)
```

**Failures are expected** - most require API keys (ANTHROPIC_API_KEY, PINECONE_API_KEY)

### Run Baseline Command

```bash
# Exclude broken test files
pytest tests/ -v --tb=line \
  --ignore=tests/test_m3_dashboard.py \
  --ignore=tests/unit/test_ui_agent_enhanced.py \
  2>&1 | tee test_baseline.txt
```

### Tests That Should Always Pass (No API Keys Needed)

```bash
pytest tests/test_discovery_tool.py tests/test_knowledge_tool.py -v
```

---

## Checklist Before Starting

- [ ] Created `pre-cleanup-backup` branch
- [ ] Pushed backup branch to GitHub  
- [ ] Ran verification commands (Section 3)
- [ ] Saved test baseline output
- [ ] Read this entire document

**Ready to proceed with Phase 1.1**
