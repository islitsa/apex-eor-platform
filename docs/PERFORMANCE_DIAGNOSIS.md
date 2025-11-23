# Two-Agent System Performance Diagnosis

## User Complaint
> "two agent system doesn't work well yet, the results are terrible for some reason, also eats a lot of tokens and is slow"

---

## Root Causes Identified

### 1. EXCESSIVE TOKEN USAGE (CRITICAL)

**Problem:** Four separate Claude API calls per generation with massive token allocations

#### API Call Breakdown:

| Phase | File:Line | max_tokens | Purpose |
|-------|-----------|------------|---------|
| 1. UX Design | [ux_designer.py:261](../src/agents/ux_designer.py#L261) | 3,072 | Design reasoning (CoT) |
| 2. Implementation Plan | [gradio_developer.py:182](../src/agents/gradio_developer.py#L182) | 2,048 | Planning phase |
| 3. Code Generation | [gradio_developer.py:269](../src/agents/gradio_developer.py#L269) | **16,384** | Generate Gradio code |
| 4. Self-Correction | [gradio_developer.py:503](../src/agents/gradio_developer.py#L503) | 8,192 | Fix UX violations |
| **TOTAL per generation** | | **29,696 tokens** | |

**If self-correction triggers:** 29,696 tokens allocated **per generation**

**Cost Impact:**
- Input tokens: ~5,000-10,000 per call (prompts + context)
- Output tokens: Up to 29,696 allocated
- Total per dashboard: **~40,000-50,000 tokens**

**This is excessive for generating a simple dashboard!**

---

### 2. PROMPT BLOAT (HIGH IMPACT)

#### Issue: Design Spec Serialization

[gradio_developer.py:243](../src/agents/gradio_developer.py#L243):
```python
DESIGN SPECIFICATION (from UX Designer):
{design_spec.to_dict()}  # This serializes ENTIRE design spec
```

**Problem:** `to_dict()` includes:
- All components with full details
- All interactions
- All patterns
- All styling metadata
- Potentially large data structures

**Estimate:** 2,000-5,000 tokens just for design spec

---

#### Issue: Memory Context Duplication

[gradio_developer.py:216](../src/agents/gradio_developer.py#L216):
```python
memory_context = self._get_memory_context()
```

This includes:
- Previous code attempts (2,000 chars each × N versions)
- User feedback
- Component summaries
- All past versions

**On iteration 3:** Memory context could be 6,000-10,000 chars = 1,500-2,500 tokens

---

#### Issue: Constraints Text

[gradio_developer.py:208](../src/agents/gradio_developer.py#L208):
```python
constraints_text = self._build_constraints_text(constraints)
```

This retrieves from Pinecone and formats 3 constraint categories with content.

**Estimate:** 1,000-2,000 tokens for constraints

---

### 3. REDUNDANT PINECONE QUERIES (MEDIUM IMPACT)

**Expected with Single-Query Architecture:**
```
[Orchestrator] Retrieving design knowledge (single query batch)...
[UX Designer] Using provided knowledge (no queries)
[Gradio Developer] Using provided knowledge (no queries)
```

**What might actually be happening:**

If `knowledge` dict from orchestrator is not properly structured, agents fall back to direct queries:

[gradio_developer.py:78-82](../src/agents/gradio_developer.py#L78-L82):
```python
if knowledge:
    constraints = knowledge.get('gradio_constraints', {})
    design_principles = knowledge.get('design_principles', {})
else:
    # Fallback: query directly
    constraints = self._query_gradio_constraints()  # 3 Pinecone queries!
```

**Result:** Could be 10+ Pinecone queries instead of 1 batch if knowledge not passed correctly.

---

### 4. NO TOKEN USAGE LOGGING

**Problem:** We have no visibility into actual token consumption

**Missing:**
- No logging of API response usage
- No tracking of input vs output tokens
- No cumulative totals

**Cannot measure:**
- Which phase uses most tokens
- How much memory context contributes
- If optimizations are working

---

### 5. POTENTIAL QUALITY ISSUES

#### Issue: Over-Engineering

The system has **multiple reasoning phases**:

1. UX Designer CoT (3,072 tokens)
2. Implementation Planning (2,048 tokens)
3. Code Generation CoT (16,384 tokens)

**Total reasoning budget:** 21,504 tokens

**Question:** Do we need THREE separate reasoning phases?

#### Issue: Large Code Generation Budget

16,384 tokens for code generation = ~12,000 chars of Python code

**Generated dashboard:** ~600-1,000 lines typically

**Question:** Is 16k tokens excessive? Could we use 8k?

---

## Comparison: Two-Agent vs Old UXCodeGenerator

### Old System (UXCodeGenerator)
- **API Calls:** 3 (Planning → Generation → Review)
- **Token Allocation:**
  - Planning: 4,096
  - Generation: 8,192
  - Review: 2,048
  - **Total: 14,336 tokens**
- **Pinecone Queries:** ~5-7 direct queries
- **Speed:** Moderate

### New System (Two-Agent)
- **API Calls:** 4 (potentially 5 with self-correction)
- **Token Allocation:**
  - UX Design: 3,072
  - Implementation Plan: 2,048
  - Code Generation: 16,384
  - Self-Correction: 8,192 (if triggered)
  - **Total: 29,696 tokens** (or 37,888 with self-correction)
- **Pinecone Queries:** 1 batch (if working) or 10+ (if falling back)
- **Speed:** Slower (more API calls, more reasoning)

**Result:** New system uses **2-2.6x more tokens** than old system!

---

## Why Results Might Be "Terrible"

### Hypothesis 1: Over-Specification Leading to Complexity

**UX Designer creates elaborate design spec →**
**Gradio Developer tries to implement ALL details →**
**Result: Overly complex code with bugs**

### Hypothesis 2: Self-Correction Introduces Errors

If validation triggers self-correction frequently:
- Agent regenerates entire code
- May lose working parts
- May introduce new bugs while fixing old ones

### Hypothesis 3: Memory Context Confusion

As implementation history grows:
- Memory context becomes large (10k+ tokens)
- Agent sees contradictory patterns
- Gets confused about what worked vs didn't work

### Hypothesis 4: Missing Cross-Agent Communication

**UX Designer designs features →**
**Gradio Developer doesn't understand full intent →**
**Result: Misaligned implementation**

The design spec might not capture enough detail for implementation.

---

## Recommendations

### Immediate Fixes (High Impact, Low Effort)

#### 1. Add Token Usage Logging

```python
# In gradio_developer.py and ux_designer.py
message = self.client.messages.create(...)

# Log usage
usage = message.usage
print(f"  [Agent] Tokens: input={usage.input_tokens}, output={usage.output_tokens}, total={usage.input_tokens + usage.output_tokens}")
```

#### 2. Reduce max_tokens Allocations

```python
# UX Designer: 3,072 → 2,048 (still plenty for reasoning)
# Implementation Plan: 2,048 → 1,024 (plan doesn't need to be huge)
# Code Generation: 16,384 → 8,192 (600 lines = ~4,000 tokens)
# Self-Correction: 8,192 → 4,096 (focused fixes)

# New total: 15,360 tokens (48% reduction!)
```

#### 3. Limit Memory Context Size

```python
def _get_memory_context(self) -> str:
    # Only show last 2 versions, not all history
    recent = self.implementation_history[-2:]
    # Limit code snippet to 300 chars instead of 500
    # Result: 600-1,000 tokens instead of 2,000-4,000
```

#### 4. Compress Design Spec Serialization

```python
# Instead of: design_spec.to_dict()
# Use: design_spec.to_summary()

def to_summary(self) -> str:
    """Compressed summary for prompts"""
    return f"""
    Screen: {self.screen_type}
    Intent: {self.intent}
    Components: {len(self.components)} ({', '.join([c['type'] for c in self.components])})
    Interactions: {len(self.interactions)}
    Patterns: {', '.join(self.patterns)}
    """
    # Result: 200-500 tokens instead of 2,000-5,000
```

---

### Architectural Improvements (High Impact, Medium Effort)

#### 1. Consider Single-Agent Architecture

**Question:** Do we need UX Designer + Gradio Developer separation?

**Alternative:** Single agent with better prompting:
- One API call instead of 4
- 8,192 tokens instead of 29,696
- Faster execution
- Simpler architecture

**Trade-off:** Lose explicit design phase

#### 2. Implement Opus's 3-Agent Suggestion Differently

Instead of:
- UX Designer (designs)
- Gradio Developer (implements)
- Assembly Agent (wires events)

Consider:
- **Design Agent** (creates component spec)
- **Code Generator** (writes Gradio code from templates)
- **Validator** (checks and fixes issues)

**Key difference:** Code Generator uses templates/patterns, not full reasoning

#### 3. Hybrid Approach: Templates + LLM

```python
# 90% of dashboards follow patterns:
# - Card grid for data sources
# - Dropdown navigation
# - Detail panels

# Use templates for common patterns
if screen_type == "dashboard_navigation":
    code = DASHBOARD_NAVIGATION_TEMPLATE.format(
        data_sources=data_sources,
        # ...
    )
    # Only use LLM for customizations
    code = refine_with_llm(code, user_requirements)

# Result: 2,000 tokens instead of 20,000
```

---

### Debugging Steps (Next Actions)

#### 1. Measure Current Token Usage

```bash
# Add logging and run generation
python scripts/pipeline/run_ingestion.py --ui

# Check console for token usage per phase
# Expected output:
# [UX Designer] Tokens: input=X, output=Y, total=Z
# [Gradio Developer] Tokens: input=X, output=Y, total=Z
```

#### 2. Verify Single-Query Architecture

```bash
# Check if agents are using provided knowledge
# Look for:
# "[UX Designer] Using provided knowledge (no queries)"
# "[Gradio Developer] Using provided knowledge (no queries)"

# If you see:
# "[UX Designer] WARNING: No knowledge provided, querying directly"
# Then single-query architecture is NOT working
```

#### 3. Inspect Generated Code Quality

```python
# Check generated_pipeline_dashboard.py:
# - Is it overly complex?
# - Are interactions working?
# - Are there obvious bugs?
# - How many lines? (expected: 600-1000)
```

#### 4. Profile Execution Time

```python
import time

# In ui_orchestrator.py
start = time.time()
knowledge = self._retrieve_all_knowledge()
print(f"Knowledge retrieval: {time.time() - start:.2f}s")

start = time.time()
design_spec = self.ux_designer.design(...)
print(f"UX Design: {time.time() - start:.2f}s")

start = time.time()
code = self.gradio_developer.build(...)
print(f"Gradio Development: {time.time() - start:.2f}s")
```

---

## Expected Performance After Fixes

### Token Reduction:

| Phase | Current | Optimized | Reduction |
|-------|---------|-----------|-----------|
| UX Design | 3,072 | 2,048 | -33% |
| Impl Plan | 2,048 | 1,024 | -50% |
| Code Gen | 16,384 | 8,192 | -50% |
| Self-Correct | 8,192 | 4,096 | -50% |
| **Total** | **29,696** | **15,360** | **-48%** |

### Additional Savings from Prompt Compression:

- Design spec: 2,000 → 500 tokens (-75%)
- Memory context: 2,000 → 800 tokens (-60%)
- Constraints: 1,500 → 1,000 tokens (-33%)

**Total input token reduction: ~3,000 tokens saved**

### Combined Result:

**Current:** ~40,000-50,000 total tokens per generation

**Optimized:** ~20,000-25,000 total tokens per generation

**Savings: 50% reduction in token usage**

---

## Next Steps

1. **Immediate:** Add token usage logging to all API calls
2. **Quick Win:** Reduce max_tokens allocations by 50%
3. **Important:** Verify single-query architecture is actually working
4. **Test:** Generate dashboard and measure tokens/time/quality
5. **Decide:** After measurements, decide if architecture needs rethinking

**Goal:** Get actual data before making architectural changes.