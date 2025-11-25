# Phase 5: Multi-Agent Collaboration

## 🌟 Overview

**Phase 5 transforms UX and React agents into autonomous reasoners with internal planning loops, enabling true multi-agent collaboration and conflict resolution.**

**Current State:**
- ✅ Phase 4 COMPLETE: OrchestratorAgent with LLM-backed reasoning
- 🔄 Phase 3.1: UX Agent (good foundations, needs internal loop)
- 🔄 Phase 3.1: React Agent (good foundations, needs internal loop)

**Phase 5 Goal:**
Each agent becomes autonomous with its own:
- Planning loop (like OrchestratorAgent)
- Skill registry
- Self-evaluation
- Conflict detection
- Shared memory communication

---

## 🎯 What Phase 5 Delivers

### 1. **Autonomous UX Agent**
- Internal reasoning loop
- Can refine its own specs
- Detects conflicts with React output
- Responds to feedback autonomously

### 2. **Autonomous React Agent**
- Internal reasoning loop
- Can fix specific components
- Detects type/import errors
- Regenerates parts, not just full code

### 3. **Shared Memory Bus**
- All agents communicate via SharedSessionMemory
- Conflicts written to shared memory
- Questions asked through memory
- Negotiation audit trail

### 4. **Multi-Agent Negotiation**
- UX and React negotiate design changes
- Orchestrator mediates when needed
- Agents resolve conflicts autonomously

---

## 🏗️ Architecture

### Before Phase 5 (Current):
```
OrchestratorAgent (autonomous)
    ├── UX Designer (procedural)
    └── React Developer (procedural)
```

### After Phase 5:
```
OrchestratorAgent (autonomous meta-agent)
    ├── Shared Memory Bus
    │   ├── UX spec & history
    │   ├── React files & history
    │   ├── Conflicts
    │   ├── Questions
    │   └── Negotiation log
    │
    ├── Autonomous UX Agent
    │   ├── Planning loop
    │   ├── Skill registry
    │   ├── Self-evaluation
    │   └── Conflict detection
    │
    └── Autonomous React Agent
        ├── Planning loop
        ├── Skill registry
        ├── Self-evaluation
        └── Conflict detection
```

---

## 🛠️ Implementation Steps

### ✅ Step 1: SharedSessionMemory (COMPLETE)

**File:** [src/agents/shared_memory.py](src/agents/shared_memory.py)

**Features:**
- Shared state for all agents
- Conflict tracking (design + implementation)
- Inter-agent questions
- Version tracking (ux_spec_version, react_version)
- Negotiation log
- Agent status tracking

**Key Classes:**
- `SharedSessionMemory` - Main memory bus
- `Conflict` - Represents detected conflicts
- `Question` - Inter-agent questions
- `ConflictType` - Enum of conflict types

### 🔄 Step 2: Upgrade UX Agent (IN PROGRESS)

**What's needed:**

#### A. Internal Planning Loop
```python
def run(self, shared_memory: SharedSessionMemory):
    while steps < MAX_STEPS:
        plan = self._plan_next_step(shared_memory)
        result = self._execute_design_skill(plan, shared_memory)
        evaluation = self._evaluate_design(result, shared_memory)
        if evaluation.satisfactory:
            return result
```

#### B. Skill Registry
```python
self.skills = {
    "generate_initial_spec": self._skill_generate_spec,
    "refine_spec": self._skill_refine_spec,
    "address_schema_conflicts": self._skill_address_conflicts,
    "redesign_after_feedback": self._skill_redesign,
    "expand_component_set": self._skill_expand_components,
    "apply_domain_signals": self._skill_apply_signals,
    "resolve_conflicts": self._skill_resolve_conflicts,
    "finish": self._skill_finish
}
```

#### C. Partial Refinement
```python
def refine_spec(self, existing_spec, feedback, shared_memory):
    """Refine existing spec, don't regenerate from scratch"""
    # Modify specific parts based on feedback
    # Write refinement reasoning to shared memory
```

#### D. Conflict Detection
```python
def detect_conflicts(self, shared_memory):
    """Detect conflicts with React implementation"""
    conflicts = []

    if shared_memory.react_files:
        # Check for schema mismatches
        # Check for missing fields
        # Check for data source mismatches

        for conflict in conflicts:
            shared_memory.add_conflict(conflict, is_design=True)
```

#### E. Structured Evaluation
```python
@dataclass
class UXEvaluationResult:
    satisfactory: bool
    issues: List[str]
    next_action: str  # "refine_spec", "regenerate", "address_conflicts", "finish"
    conflicts_detected: List[Conflict]
```

### 🔄 Step 3: Upgrade React Agent (IN PROGRESS)

**What's needed:**

#### A. Internal Planning Loop
```python
def run(self, shared_memory: SharedSessionMemory):
    while steps < MAX_STEPS:
        plan = self._plan_next_action(shared_memory)
        result = self._execute_implementation_skill(plan, shared_memory)
        evaluation = self._evaluate_implementation(result, shared_memory)
        if evaluation.satisfactory:
            return result
```

#### B. Skill Registry
```python
self.skills = {
    "generate_initial_implementation": self._skill_generate_impl,
    "fix_type_errors": self._skill_fix_types,
    "adjust_imports": self._skill_adjust_imports,
    "fix_source_filtering": self._skill_fix_filtering,
    "regenerate_component": self._skill_regenerate_component,
    "validate_implementation": self._skill_validate,
    "resolve_conflicts": self._skill_resolve_conflicts,
    "finish": self._skill_finish
}
```

#### C. Component-Level Regeneration
```python
def regenerate_component(self, component_name: str, shared_memory):
    """Regenerate specific component, not entire codebase"""
    # Extract component code
    # Regenerate just that component
    # Integrate back into full implementation
```

#### D. Conflict Detection
```python
def detect_conflicts(self, shared_memory):
    """Detect implementation issues"""
    conflicts = []

    # Type errors
    # Invalid imports
    # Missing props
    # Incorrect filtering

    for conflict in conflicts:
        shared_memory.add_conflict(conflict, is_design=False)
```

#### E. Respond to UX Changes
```python
def detect_ux_modifications(self, shared_memory):
    """Check if UX spec changed since last implementation"""
    if shared_memory.ux_spec_version > self.last_ux_version:
        # UX refined the spec
        # Determine what changed
        # Update implementation accordingly
```

### 🔄 Step 4: Multi-Agent Negotiation (IN PROGRESS)

**Orchestrator mediates:**

```python
# UX detects conflict
shared_memory.add_conflict(Conflict(
    conflict_type=ConflictType.DATA_SOURCE_MISMATCH,
    source_agent="UX Designer",
    description="React implementation uses wrong data source",
    suggested_resolution="Update React to use 'fracfocus' not 'frac_focus'"
))

# React agent sees conflict in shared memory
# React agent addresses it
# React agent marks conflict resolved
shared_memory.resolve_conflict(conflict)
```

**Agents can also ask questions:**

```python
# React asks UX a question
shared_memory.ask_question(
    asking_agent="React Developer",
    target_agent="UX Designer",
    question="Should the PipelineCard component be collapsible?",
    context={"component": "PipelineCard"}
)

# UX agent sees question
# UX agent answers
shared_memory.answer_question(question, "Yes, all cards should be collapsible")

# React agent sees answer
# React agent updates implementation
```

### 🔄 Step 5: Integration & Testing (PENDING)

- Update OrchestratorAgent to use SharedSessionMemory
- Update skill executions to pass shared memory
- Test multi-agent negotiation scenarios
- Verify conflict resolution works
- Test partial refinement paths

### 🔄 Step 6: Documentation & Examples (PENDING)

- Multi-agent conversation examples
- Conflict resolution scenarios
- Performance comparison vs Phase 4

---

## 📊 Current Status

### ✅ Completed:
1. **SharedSessionMemory** - Communication bus created
   - Conflict tracking ✅
   - Question system ✅
   - Version tracking ✅
   - Negotiation log ✅

### 🔄 In Progress:
2. **UX Agent Upgrade** - Needs implementation
3. **React Agent Upgrade** - Needs implementation
4. **Multi-Agent Integration** - Needs implementation
5. **Testing** - Needs implementation

---

## 🎨 Example Multi-Agent Conversation

### Iteration 1: UX Generates Initial Spec
```
[UX Agent] Planning: generate_initial_spec
[UX Agent] Generated design spec v1
[SharedMemory] ux_spec_version = 1
```

### Iteration 2: React Generates Implementation
```
[React Agent] Planning: generate_initial_implementation
[React Agent] Generated React files v1
[SharedMemory] react_version = 1
```

### Iteration 3: React Detects Conflict
```
[React Agent] Conflict detected: Type error in PipelineCard
[SharedMemory] implementation_conflicts += TypeErrorConflict
[React Agent] Planning: fix_type_errors
[React Agent] Fixed types
[SharedMemory] react_version = 2
[SharedMemory] Conflict resolved
```

### Iteration 4: UX Refines Based on Feedback
```
[Orchestrator] Feedback: Add filtering controls
[UX Agent] Planning: refine_spec
[UX Agent] Refined spec to add FilterPanel component
[SharedMemory] ux_spec_version = 2
[SharedMemory] Negotiation log: UX -> React "Added FilterPanel component"
```

### Iteration 5: React Adapts to UX Change
```
[React Agent] Detected UX modification (v1 -> v2)
[React Agent] Planning: regenerate_component("FilterPanel")
[React Agent] Generated new FilterPanel component
[SharedMemory] react_version = 3
[SharedMemory] Negotiation log: React -> UX "FilterPanel implemented"
```

### Iteration 6: Completion
```
[UX Agent] Evaluation: satisfactory ✅
[React Agent] Evaluation: satisfactory ✅
[Orchestrator] Goal achieved!
```

---

## 🔍 Key Differences: Phase 4 vs Phase 5

| Aspect | Phase 4 | Phase 5 |
|--------|---------|---------|
| **Orchestrator** | Autonomous with planning loop | Same + mediates multi-agent negotiation |
| **UX Agent** | Procedural executor | Autonomous reasoner with skills |
| **React Agent** | Procedural executor | Autonomous reasoner with skills |
| **Communication** | Method calls | Shared memory bus |
| **Conflict Resolution** | Orchestrator decides | Agents negotiate autonomously |
| **Refinement** | Full regeneration only | Partial refinement supported |
| **Questions** | N/A | Agents can ask each other questions |
| **Observability** | Agent traces | + Negotiation log + Conflict tracking |

---

## 📁 Files

### Created:
1. **[src/agents/shared_memory.py](src/agents/shared_memory.py)** ✅
   - SharedSessionMemory class
   - Conflict class
   - Question class
   - ConflictType enum

### To Modify:
2. **src/agents/ux_designer.py** - Add internal loop + skills
3. **src/agents/react_developer.py** - Add internal loop + skills
4. **src/agents/orchestrator_agent.py** - Integrate shared memory

### Documentation:
5. **[PHASE_5_MULTI_AGENT_COLLABORATION.md](PHASE_5_MULTI_AGENT_COLLABORATION.md)** - This file

---

## 🚧 Next Steps

To complete Phase 5, we need to:

1. ✅ **Create SharedSessionMemory** - DONE
2. 🔄 **Upgrade UX Agent** - Add planning loop, skills, conflict detection
3. 🔄 **Upgrade React Agent** - Add planning loop, skills, component regeneration
4. 🔄 **Integrate with Orchestrator** - Use shared memory instead of direct calls
5. 🔄 **Test Multi-Agent Scenarios** - Verify negotiation works
6. 🔄 **Document Examples** - Show real multi-agent conversations

---

## ✨ What Phase 5 Achieves

**True multi-agent collaboration where:**
- ✅ Each agent thinks for itself
- ✅ Agents negotiate through shared memory
- ✅ Conflicts detected and resolved autonomously
- ✅ Agents can refine parts, not just regenerate everything
- ✅ Full audit trail of multi-agent communication
- ✅ Orchestrator mediates when needed, but agents are autonomous

**This is the vision:** A system where agents collaborate like a team, not just execute in sequence.

---

**Status:** Step 1 complete (SharedSessionMemory)
**Next:** Upgrade UX Agent with internal planning loop
**Timeline:** Multi-session implementation
**Complexity:** High (major agent refactoring)
