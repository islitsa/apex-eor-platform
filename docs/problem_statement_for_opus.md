# Problem Statement: Agent Knowledge Gap

## Context
We have a UX Code Generator agent that's supposed to be a "Gradio expert" but it keeps generating code with `@keyframes` CSS animations that cause Python syntax errors.

## The Problem

### What Happened
The LLM generated this code:
```python
loading_content = f"""
    <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }    # Python error!
            100% { transform: rotate(360deg); }
        }
    </style>
    <div style="animation: spin 1s;">Loading</div>
"""
```

**Result:** `SyntaxError: invalid decimal literal` because Python parses `0%` as invalid syntax inside the f-string.

### Root Cause Analysis

1. **Agent Claims Expertise But Lacks Knowledge**
   - Agent persona says: "Gradio framework component composition and event handling"
   - But agent doesn't know: Gradio's CSS limitations are a KNOWN issue

2. **Knowledge Gap in RAG System**
   - Queried Pinecone for "Gradio CSS limitations inline styles"
   - Found: Material Design patterns, layout patterns
   - Did NOT find: Gradio technical constraints, CSS limitations, framework gotchas

3. **No Gradio-Specific Technical Knowledge**
   - RAG contains: UX patterns (Material Design, navigation, actions)
   - RAG missing: Framework limitations, implementation constraints, known issues

## The Question

**Should we have 2 separate agents?**

### Option A: Single Agent with Better RAG Knowledge
- Keep one agent
- Add Gradio technical constraints to Pinecone:
  - CSS limitations (no @keyframes in gr.HTML)
  - gr.Blocks architecture constraints
  - Event handling patterns
  - Python/CSS integration gotchas
- **Pros:** Simpler architecture, agent has full context
- **Cons:** Mixing UX design concerns with technical implementation

### Option B: Two Specialized Agents
**Agent 1: UI/UX Designer**
- Responsibility: WHAT to build
- Knowledge: User needs, design patterns, flows, accessibility
- Output: Design specification (wireframe, interactions, patterns to use)

**Agent 2: Gradio Developer**
- Responsibility: HOW to build it within framework constraints
- Knowledge: Gradio limitations, Python/CSS integration, gr.HTML gotchas
- Input: Design spec from Agent 1
- Output: Working Gradio Python code

**Pros:** Clear separation of concerns, each expert in their domain
**Cons:** Need coordination layer, handoff protocol, more complex

## Current Agent Architecture

```
UXCodeGenerator (tries to do everything)
├── Queries Pinecone for UX patterns ✅
├── Has UX expert persona ✅
├── Chain of Thought reasoning ✅
├── Planning phase ✅
├── Memory for multi-screen workflows ✅
├── Skills (testing, formatting) ✅
└── Generates Gradio code ✅
    └── But doesn't know Gradio limitations! ❌
```

## What We've Already Fixed

1. ✅ Added prompt constraint: "Do NOT use @keyframes"
2. ✅ Added Skills test to detect @keyframes
3. ✅ Suggested alternatives: Unicode spinners (⏳ 🔄 ⟳)

**But this is REACTIVE** - we're patching symptoms as we discover them.

## The Core Issue

**The agent doesn't have fundamental knowledge about the framework it's coding in.**

This is like having a "React expert" who doesn't know about the Virtual DOM, or a "Django expert" who doesn't know about the ORM.

## Options for Opus to Consider

### Option 1: RAG Enhancement (Quick Fix)
Add Gradio technical documentation to Pinecone:
- Known issues and limitations
- Best practices for gr.HTML and CSS
- Python/CSS integration gotchas
- Framework architecture constraints

**Effort:** Low (add documents)
**Impact:** Medium (still one agent doing two jobs)

### Option 2: Agent Specialization (Architectural Change)
Split into two specialized agents:
```
┌─────────────────────┐
│  UX Designer Agent  │  ← Plans WHAT to build
│  (Design Patterns)  │
└──────────┬──────────┘
           │ Design Spec
           ↓
┌─────────────────────┐
│ Gradio Dev Agent    │  ← Implements HOW within constraints
│ (Framework Expert)  │
└─────────────────────┘
```

**Effort:** High (refactor, coordination layer)
**Impact:** High (clean separation, less likely to repeat this)

### Option 3: Hybrid Approach
Keep one agent but:
- Add comprehensive Gradio knowledge to RAG
- Create "Framework Constraints" category in Pinecone
- Query constraints BEFORE generation
- Skills system validates against constraints

**Effort:** Medium
**Impact:** High (proactive constraint checking)

## Question for Opus

**Which approach should we take?**

1. Do we need 2 agents (UX Designer + Gradio Developer)?
2. Or should we enhance RAG with Gradio technical knowledge?
3. Or something else entirely?

The pattern will repeat: without framework-specific knowledge, the agent will keep violating constraints we haven't discovered yet.

## Additional Context

- We're using Claude Sonnet 4 for generation
- Pinecone for RAG (currently has UX patterns but not framework constraints)
- Target framework: Gradio (Python web UI framework)
- Agent has: CoT, Planning, Memory, Skills
- Agent lacks: Framework-specific technical knowledge

**What's the right architecture to prevent this class of problems?**