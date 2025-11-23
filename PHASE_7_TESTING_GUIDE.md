# Phase 7 Testing Guide - Agent Studio

**Date:** 2025-11-22
**Purpose:** Test the Phase 7 refactored architecture end-to-end

---

## Quick Launch

### Option 1: Using the Batch File
```bash
TEST_PHASE_7.bat
```

### Option 2: Manual Launch
```bash
# Activate venv
call venv\Scripts\activate

# Launch Agent Studio
streamlit run src\ui\agent_studio.py --server.port 8501
```

Then open: **http://localhost:8501**

---

## What to Test

### Test 1: Basic UI Generation (Procedural Mode)

**Steps:**
1. Open Agent Studio
2. Enter requirements:
   ```
   Create a data dashboard showing petroleum pipeline status with drill-down capability
   ```
3. Click **"Generate UI"**

**What to Watch For:**

✅ **Phase 7 Initialization (Console Output):**
```
================================================================================
TWO-AGENT UI CODE GENERATION SYSTEM
================================================================================
Architecture: UX Designer (Visionary) + React Developer (Implementer)
Mode: Procedural Coordination (Phase 3)
================================================================================

[Phase 7.1] OrchestratorTools bundle created and validated
[Phase 7.2] Using consistency tools from OrchestratorTools bundle
[Orchestrator] PROCEDURAL MODE (fixed sequence via agent.run())
```

✅ **Procedural Orchestrator Execution:**
```
================================================================================
PROCEDURAL ORCHESTRATOR (Phase 7.3)
================================================================================
Fixed sequence: Discovery → Knowledge → UX → React → Consistency
================================================================================

[Step 1/5] Discovering data...
[Step 2/5] Retrieving knowledge...
[Step 3/5] Building session context...
[Step 4/5] Generating UX design...
[Step 5/5] Generating React code...
```

✅ **Real Tools Being Used:**
```
[Discovery] Fetching data context from API...
[Discovery] Found 3 sources: fracfocus, rrc, usgs
[Knowledge] Querying Pinecone for design patterns...
[Knowledge] Retrieved 15 M3 design patterns
```

✅ **SharedMemory Flow:**
```
[Phase 6.2] UX spec written to shared memory (version 1)
[Phase 6.2] React agent reading UX spec from shared memory (version 1)
[Phase 6.2] React files written to shared memory (version 1)
```

✅ **Consistency Checks:**
```
[Phase 6.1] Running consistency checks...
  [1/4] DesignCodeConsistencyTool...
        Found 0 conflicts
  [2/4] SchemaAlignmentTool...
        Found 0 conflicts
  [3/4] KnowledgeConflictTool...
        Found 0 conflicts
  [4/4] ComponentCompatibilityTool...
        Found 0 conflicts
[Phase 6.1] Total conflicts detected: 0
```

✅ **Final Output:**
```
================================================================================
PROCEDURAL ORCHESTRATOR COMPLETE
================================================================================
  React files generated: True
  UX spec version: 1
  React version: 1
================================================================================
```

---

### Test 2: Verify Real Data (Not Stubs!)

**What to Check:**

1. **In Console Output:**
   - Look for `[Discovery] Fetching data context from API...`
   - Should see REAL source names (fracfocus, rrc, usgs, etc.)
   - Should see REAL record counts (not fake numbers like 1000)

2. **In Agent Studio UI:**
   - Check "Agent Chatter" tab
   - Should see knowledge retrieval messages
   - Should see M3 design patterns being loaded

3. **In Generated Code:**
   - Look at the React code
   - Should reference ACTUAL data fields from your API
   - Should have REAL component names (not generic placeholders)

---

### Test 3: Test Autonomous Mode (Optional)

**Steps:**
1. Stop Agent Studio
2. Edit `src/ui/agent_studio.py` line 56:
   ```python
   # Change from:
   self.orchestrator = UICodeOrchestrator(
       trace_collector=self.trace_collector,
       enable_gradient=enable_gradient
   )

   # To:
   self.orchestrator = UICodeOrchestrator(
       trace_collector=self.trace_collector,
       enable_gradient=enable_gradient,
       use_agent_mode=True  # ← ADD THIS
   )
   ```

3. Restart Agent Studio
4. Generate UI again

**Expected Output:**
```
Mode: AUTONOMOUS AGENT (Phase 4 - LLM-backed reasoning)

[Orchestrator] AUTONOMOUS AGENT MODE enabled (LLM-backed planning)
```

Then you should see LLM-backed planning instead of fixed sequence.

---

### Test 4: Test Convergence Loop

**Trigger Conflicts:**
1. Generate a complex UI with many features
2. Look for consistency check output
3. If conflicts detected, should see:
   ```
   [Phase 6.2] MEDIATOR CONVERGENCE LOOP
   ================================================================================

   [Phase 6.2] Convergence iteration 1/2
     Current state: 5 total conflicts, 2 high-severity
     Re-running React generation with conflict context...
     React regenerated (version 2)

   [Phase 6.2] Convergence iteration 2/2
     Current state: 1 total conflicts, 0 high-severity
   [Phase 6.2] CONVERGED: Only low-severity conflicts remain
   ```

---

## Success Criteria

### ✅ Phase 7 Complete If You See:

1. **Tools Bundle Validated:**
   ```
   [OrchestratorTools] All 11 tools validated successfully
   ```

2. **Real Data Discovery:**
   ```
   [Discovery] Found N sources: <real source names>
   ```

3. **Real Knowledge Retrieval:**
   ```
   [Knowledge] Retrieved N M3 design patterns
   ```

4. **SharedMemory Communication:**
   ```
   [Phase 6.2] UX spec written to shared memory (version X)
   [Phase 6.2] React agent reading UX spec from shared memory (version X)
   ```

5. **Consistency Checks Running:**
   ```
   [Phase 6.1] Running consistency checks...
   ```

6. **Working React Code Generated:**
   - Preview shows actual UI
   - Code has real data fields
   - No placeholder text

---

## Troubleshooting

### Issue: "Tools bundle not found"
**Fix:** Run `python -c "from src.agents.orchestrator_tools_bundle import OrchestratorTools"`

### Issue: "Stub data being used"
**Check:** Look for `[Discovery] Fetching data context from API...` in console
**If missing:** Tools bundle not wired - recheck Phase 7.2

### Issue: "No convergence loop"
**Check:** Look for `[Phase 6.2] MEDIATOR CONVERGENCE LOOP`
**If missing:** Convergence only runs when conflicts detected

### Issue: "Import errors"
**Fix:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## Performance Metrics to Collect

Track these for before/after comparison:

| Metric | How to Measure |
|--------|----------------|
| **Generation Time** | Time from click to code displayed |
| **Code Quality** | Does preview work? Any errors? |
| **Token Usage** | Check console for `[TOKEN USAGE]` |
| **Conflict Count** | Number from consistency checks |
| **Convergence Iterations** | How many iterations to converge? |

---

## What Success Looks Like

### Console Output Example:
```
================================================================================
TWO-AGENT UI CODE GENERATION SYSTEM
================================================================================
[Phase 7.1] OrchestratorTools bundle created and validated
[Orchestrator] PROCEDURAL MODE (fixed sequence via agent.run())

[Step 1/5] Discovering data...
[Discovery] Fetching data context from API...
[Discovery] Found 3 sources: fracfocus, rrc, usgs

[Step 2/5] Retrieving knowledge...
[Knowledge] Querying Pinecone for design patterns...
[Knowledge] Retrieved 15 M3 design patterns

[Step 3/5] Building session context...
[Context] Session context built successfully

[Step 4/5] Generating UX design...
[Phase 6.2] UX spec written to shared memory (version 1)

[Step 5/5] Generating React code...
[Phase 6.2] React agent reading UX spec from shared memory (version 1)
[Phase 6.1] Running consistency checks...
        Found 0 conflicts
[Phase 6.2] React files written to shared memory (version 1)

PROCEDURAL ORCHESTRATOR COMPLETE
  React files generated: True
```

### Agent Studio UI:
- ✅ Preview shows working dashboard
- ✅ Code tab has complete React + TypeScript
- ✅ Design Spec tab shows M3 components
- ✅ Agent Chatter shows real API calls
- ✅ Traces show tool execution

---

## Next Steps After Successful Test

1. **Document performance:** Note generation time, token usage
2. **Compare with old version:** Is it faster? Better quality?
3. **Test edge cases:** Empty data, API errors, complex UIs
4. **Production deployment:** If all tests pass, ready to ship!

---

**Phase 7 Testing Complete When:**
- ✅ All 4 tests pass
- ✅ Real tools confirmed (no stubs)
- ✅ SharedMemory flowing correctly
- ✅ Generated code works in preview
- ✅ No import errors or crashes

**Good luck testing! 🚀**
