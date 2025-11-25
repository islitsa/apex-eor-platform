# Agents Folder Archival Recommendations

**Date**: 2025-11-22
**Purpose**: Identify obsolete/experimental files for archival

---

## CATEGORY 1: ALREADY DEPRECATED (Ready for Archive)

### 1. **component_assembler.py** ❌ ARCHIVE
- **Status**: ALREADY MARKED DEPRECATED in code
- **Reason**: "Incorrectly categorized as an 'agent' but it's actually a template-based builder"
- **Moved to**: `src.builders.dashboard_builder`
- **Usage**: Only exists for backwards compatibility
- **Recommendation**: **ARCHIVE IMMEDIATELY** (already deprecated with warnings)

---

## CATEGORY 2: SUPERSEDED BY NEWER ARCHITECTURE (Gradio → React Migration)

### 2. **gradio_developer.py** ❌ ARCHIVE
- **What**: Gradio-specific implementation agent
- **Superseded by**: `react_developer.py` (React + TypeScript)
- **Architecture**: Phase 1 two-agent system (Gradio era)
- **Current**: Phase 5+ uses React, not Gradio
- **Recommendation**: **ARCHIVE** (project migrated to React)

### 3. **ux_code_generator.py** ❌ ARCHIVE
- **What**: Generic UI code generator for Gradio
- **Superseded by**: `ux_designer.py` (design spec generator, framework-agnostic)
- **Architecture**: Old monolithic UX generator
- **Current**: Phase 5 uses ux_designer.py for specs, react_developer.py for implementation
- **Recommendation**: **ARCHIVE** (replaced by two-agent separation)

---

## CATEGORY 3: EXPERIMENTAL OPTIMIZATIONS (Token Reduction Experiments)

### 4. **hybrid_code_generator.py** ⚠️ REVIEW
- **What**: "Snippet first, LLM fallback" optimization
- **Purpose**: 95% token reduction via template reuse
- **Status**: Experimental, not in main pipeline
- **Architecture**: Uses ui_orchestrator internally
- **Recommendation**: **ARCHIVE or MOVE to /experiments** (interesting but not production)

### 5. **snippet_modifier.py** ⚠️ REVIEW
- **What**: Modifies existing snippets instead of generating from scratch
- **Purpose**: 87% token reduction
- **Status**: Experimental optimization
- **Used by**: hybrid_code_generator.py
- **Recommendation**: **ARCHIVE or MOVE to /experiments** (paired with hybrid_code_generator)

---

## CATEGORY 4: EXAMPLE/DEMO FILES

### 6. **context/integration_example.py** ⚠️ MOVE
- **What**: "Complete end-to-end demo" of context-swimming agents
- **Purpose**: Example/tutorial file
- **Location**: Should NOT be in production src/agents/context/
- **Recommendation**: **MOVE to /examples or /docs/tutorials**

---

## CATEGORY 5: INSTRUMENTATION/DEBUGGING

### 7. **context/discovery_tools_instrumented.py** ⚠️ REVIEW
- **What**: Instrumented version of discovery_tools.py
- **Purpose**: Debugging/performance tracking
- **Status**: Likely a temporary debug version
- **Recommendation**: **ARCHIVE** if discovery_tools.py works, or **MERGE** instrumentation features

### 8. **context/discovery_instrumentation.py** ⚠️ REVIEW
- **What**: Performance tracking and bottleneck detection
- **Purpose**: Development/debugging tool
- **Status**: May still be useful for profiling
- **Recommendation**: **MOVE to /tools or /dev_utils** (not production code)

### 9. **context/discovery_instrumentation_fixed.py** ❌ ARCHIVE
- **What**: Fixed version of discovery_instrumentation.py
- **Implication**: Original discovery_instrumentation.py had bugs, this is the fix
- **Recommendation**:
  - **ARCHIVE discovery_instrumentation.py** (broken version)
  - **RENAME discovery_instrumentation_fixed.py → discovery_instrumentation.py** (keep fixed version)

---

## CATEGORY 6: EXPERIMENTAL ARCHITECTURE (Context Swimming)

### 10. **context/context_swimming_agents.py** ⚠️ REVIEW
- **What**: Autonomous context-discovery agents
- **Status**: Experimental architecture (context swimming)
- **Current**: Not used in main pipeline (Phase 5 uses protocol.py)
- **Recommendation**: **ARCHIVE or MOVE to /experiments** (interesting concept, not production)

---

## PRODUCTION FILES (KEEP - DO NOT ARCHIVE)

### ✅ **ui_orchestrator.py** - KEEP
- **Status**: PRODUCTION - Main orchestrator used by Agent Studio
- **Phase**: 3, 4, 5, 6.1, 6.2 implemented
- **Usage**: Primary entry point

### ✅ **orchestrator_agent.py** - KEEP
- **Status**: PRODUCTION - Autonomous agent mode (Phase 4)
- **Phase**: 4, 5, 6.1, 6.2 implemented
- **Usage**: Used when use_agent_mode=True

### ✅ **ux_designer.py** - KEEP
- **Status**: PRODUCTION - UX design spec generator
- **Phase**: 5 autonomous agent
- **Usage**: Core UX agent

### ✅ **react_developer.py** - KEEP
- **Status**: PRODUCTION - React + TypeScript implementation
- **Phase**: 5 autonomous agent
- **Usage**: Core React agent

### ✅ **shared_memory.py** - KEEP
- **Status**: PRODUCTION - Phase 6.1/6.2 negotiation layer
- **Usage**: Multi-agent collaboration

### ✅ **context/protocol.py** - KEEP
- **Status**: PRODUCTION - Phase 3 protocol definitions
- **Usage**: SessionContext, DiscoveryContext, ExecutionContext

### ✅ **context/adapter.py** - KEEP
- **Status**: PRODUCTION - Phase 3 protocol adapter
- **Usage**: Converts between old and new data formats

### ✅ **context/gradient_context.py** - KEEP
- **Status**: PRODUCTION - Gradient context system
- **Usage**: Semantic navigation (Phase 1.6+)

### ✅ **context/discovery_tools.py** - KEEP
- **Status**: PRODUCTION - Main discovery tools
- **Usage**: Core data discovery

### ✅ **context/repository_indexer.py** - KEEP
- **Status**: PRODUCTION (if used) - Repository indexing
- **Usage**: Check if still used

### ✅ **tools/*.py** (ALL) - KEEP
- **Status**: PRODUCTION - Phase 3 and Phase 6.1 tools
- **Usage**: Core business logic layer

---

## ARCHIVAL STRUCTURE PROPOSAL

Create an `archive/` directory:

```
archive/
├── legacy_agents/
│   ├── component_assembler.py (DEPRECATED - moved to builders)
│   ├── gradio_developer.py (SUPERSEDED - Gradio → React migration)
│   ├── ux_code_generator.py (SUPERSEDED - monolithic → two-agent)
│
├── experiments/
│   ├── hybrid_code_generator.py (Token optimization experiment)
│   ├── snippet_modifier.py (Template modification approach)
│   ├── context_swimming_agents.py (Autonomous context discovery)
│
├── debugging/
│   ├── discovery_instrumentation.py (BROKEN - replaced by _fixed)
│   ├── discovery_tools_instrumented.py (Debug version)
│
└── examples/
    └── integration_example.py (Tutorial/demo file)
```

---

## IMMEDIATE ACTIONS

### Critical (Do Now)

1. ✅ **ARCHIVE component_assembler.py** (already deprecated)
2. ✅ **ARCHIVE discovery_instrumentation.py** (broken version)
3. ✅ **RENAME discovery_instrumentation_fixed.py → discovery_instrumentation.py**

### High Priority (This Week)

4. ✅ **ARCHIVE gradio_developer.py** (no longer relevant post-React migration)
5. ✅ **ARCHIVE ux_code_generator.py** (superseded by ux_designer.py)

### Medium Priority (Next Sprint)

6. ⚠️ **MOVE TO /experiments**:
   - hybrid_code_generator.py
   - snippet_modifier.py
   - context_swimming_agents.py

7. ⚠️ **MOVE TO /examples**:
   - integration_example.py

8. ⚠️ **MOVE TO /dev_utils**:
   - discovery_tools_instrumented.py
   - discovery_instrumentation.py (if keeping for profiling)

---

## VERIFICATION CHECKLIST

Before archiving each file:

- [ ] Grep entire codebase for imports
- [ ] Check if any UI files reference it
- [ ] Check if any test files depend on it
- [ ] Update any documentation that references it
- [ ] Add deprecation notice if keeping for compatibility

---

## RISK ASSESSMENT

**Low Risk** (safe to archive):
- component_assembler.py (already deprecated)
- discovery_instrumentation.py (broken, have fixed version)

**Medium Risk** (check dependencies first):
- gradio_developer.py (old UI files might import it)
- ux_code_generator.py (old UI files might import it)

**High Risk** (experimental but might be referenced):
- hybrid_code_generator.py (check if any perf tests use it)
- snippet_modifier.py (paired with hybrid)

---

## SUMMARY

**Total Files Reviewed**: 32
**Recommended for Archive**: 9 files
**Recommended for Move**: 4 files
**Production Files (Keep)**: 19 files

**Archival reduces agents/ folder size by ~30%** while preserving all production code.

**Next Step**: Execute immediate actions, then review medium-priority moves.
