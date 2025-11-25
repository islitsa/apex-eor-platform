# Phase 5 Step 2: UX Agent Upgrade Specification

## 🎯 Goal

Transform UXDesignerAgent from a procedural executor into an autonomous agent with:
- Internal planning loop (like OrchestratorAgent)
- Skill registry (8 design skills)
- Partial refinement capability
- Conflict detection
- SharedMemory integration

---

## 📊 Current State Analysis

### ✅ What UX Agent Already Has (Phase 3.1)

**Strengths:**
1. **CoT Reasoning** - `_design_with_cot()` method already exists
2. **Design Memory** - `self.design_history` tracks previous designs
3. **SessionContext Support** - `with_context()` method works
4. **DesignSpec Output** - Clean structured output format
5. **Discovery Tools** - Can query data sources

**Current Flow:**
```
design(requirements, knowledge)
  → _design_with_cot(prompt)
  → return DesignSpec
```

### ❌ What's Missing for Phase 5

**Major Gaps:**
1. **No planning loop** - Just one-shot design generation
2. **No skill registry** - Can't choose between actions
3. **No partial refinement** - Always full regeneration
4. **No conflict detection** - Doesn't check React output
5. **No structured evaluation** - Doesn't evaluate its own work
6. **No SharedMemory integration** - Uses local memory only

---

## 🏗️ Architecture for Phase 5 UX Agent

### New Components to Add

```
UXDesignerAgent
├── Autonomous Mode Flag (use_autonomous_mode)
├── Planning Loop (run method)
├── Skill Registry (8 skills)
│   ├── generate_initial_spec
│   ├── refine_spec
│   ├── address_schema_conflicts
│   ├── redesign_after_feedback
│   ├── expand_component_set
│   ├── apply_domain_signals
│   ├── resolve_conflicts
│   └── finish
├── Evaluation Module
│   ├── _evaluate_design()
│   └── _plan_next_step()
├── Conflict Detection
│   └── detect_conflicts()
└── SharedMemory Integration
    ├── Read from shared_memory
    └── Write to shared_memory
```

---

## 🔧 Implementation Blueprint

### 1. Add Autonomous Mode Flag

```python
class UXDesignerAgent:
    def __init__(self, trace_collector=None, use_autonomous_mode=False):
        # Existing initialization...

        # Phase 5: Autonomous mode flag
        self.use_autonomous_mode = use_autonomous_mode

        if use_autonomous_mode:
            self._build_skill_registry()
            print("[UX Agent] Initialized in AUTONOMOUS MODE")
```

### 2. Build Skill Registry

```python
def _build_skill_registry(self):
    """Build registry of design skills for autonomous operation"""
    self.skills = {
        "generate_initial_spec": {
            "fn": self._skill_generate_initial_spec,
            "description": "Generate initial design specification from requirements"
        },
        "refine_spec": {
            "fn": self._skill_refine_spec,
            "description": "Refine existing spec based on feedback (partial)"
        },
        "address_schema_conflicts": {
            "fn": self._skill_address_schema_conflicts,
            "description": "Fix schema mismatches with React implementation"
        },
        "redesign_after_feedback": {
            "fn": self._skill_redesign_after_feedback,
            "description": "Redesign components based on user/React feedback"
        },
        "expand_component_set": {
            "fn": self._skill_expand_component_set,
            "description": "Add new components to existing design"
        },
        "apply_domain_signals": {
            "fn": self._skill_apply_domain_signals,
            "description": "Apply domain-specific design patterns (gradient)"
        },
        "resolve_conflicts": {
            "fn": self._skill_resolve_conflicts,
            "description": "Resolve conflicts reported by React agent"
        },
        "finish": {
            "fn": self._skill_finish,
            "description": "Mark design as complete"
        }
    }
```

### 3. Add Planning Loop (Main Entry Point)

```python
def run(self, shared_memory: SharedSessionMemory, max_steps: int = 3):
    """
    Phase 5: Autonomous design loop with planning.

    Replaces the procedural design() method when in autonomous mode.

    Args:
        shared_memory: SharedSessionMemory instance
        max_steps: Maximum planning iterations

    Returns:
        DesignSpec
    """
    print(f"\n[UX Agent] Starting autonomous design loop (max {max_steps} steps)")

    # Update status
    shared_memory.ux_status = "planning"

    for step in range(max_steps):
        print(f"\n[UX Agent] Planning iteration {step + 1}/{max_steps}")

        # 1. Plan next action based on current state
        plan = self._plan_next_step(shared_memory)

        print(f"[UX Agent] Plan: {plan.skill}")
        print(f"[UX Agent] Reasoning: {plan.reasoning}")

        # 2. Execute planned skill
        result = self._execute_skill(plan, shared_memory)

        # 3. Evaluate result
        evaluation = self._evaluate_design(shared_memory)

        # 4. Log to shared memory
        shared_memory.ux_reasoning_trace.append(
            f"Step {step + 1}: {plan.skill} - {plan.reasoning}"
        )

        # 5. Check if design is satisfactory
        if evaluation.satisfactory or plan.skill == "finish":
            shared_memory.ux_status = "done"
            shared_memory.ux_satisfactory = True
            print(f"\n[UX Agent] Design complete after {step + 1} steps")
            return shared_memory.ux_spec

        # 6. Continue iterating
        shared_memory.iteration += 1

    # Return whatever we have after max steps
    shared_memory.ux_status = "done"
    print(f"\n[UX Agent] Reached max steps, returning current design")
    return shared_memory.ux_spec
```

### 4. Add Planning Function

```python
def _plan_next_step(self, shared_memory: SharedSessionMemory):
    """
    Plan next design action based on current state.

    Uses LLM to decide what to do next.
    """
    # Get current state
    state = shared_memory.get_current_state_summary()

    # Build planning prompt
    prompt = f"""You are the UX Designer Agent. Your goal is to create a complete design specification.

**Current State:**
- Has UX spec: {state['has_ux_spec']}
- UX version: {state['ux_version']}
- Design conflicts: {state['design_conflicts']}
- React status: {state['react_status']}
- Unanswered questions: {state['unanswered_questions']}

**Available Skills:**
{self._format_skills()}

**Recent Actions:**
{shared_memory.ux_reasoning_trace[-3:] if shared_memory.ux_reasoning_trace else 'None'}

**Conflicts to Address:**
{self._format_conflicts(shared_memory)}

**Decision Rules:**
- If no UX spec exists: use "generate_initial_spec"
- If React reported conflicts: use "address_schema_conflicts" or "resolve_conflicts"
- If user feedback exists: use "refine_spec" or "redesign_after_feedback"
- If React questions exist: answer them first
- If design is complete and validated: use "finish"

Return JSON:
{{
  "skill": "<skill_name>",
  "reasoning": "<why this skill now>",
  "arguments": {{}}
}}
"""

    # Call LLM for planning
    response = self.client.messages.create(
        model=self.model,
        max_tokens=1000,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse plan
    plan_text = response.content[0].text
    plan = self._parse_plan(plan_text)

    return plan
```

### 5. Skill Implementations

#### Skill: generate_initial_spec

```python
def _skill_generate_initial_spec(self, shared_memory: SharedSessionMemory, **kwargs):
    """Generate initial design specification"""
    print("[UX Agent] Generating initial design spec...")

    # Use existing _design_with_cot logic
    requirements = shared_memory.user_requirements
    knowledge = shared_memory.knowledge or {}

    # Generate design
    design_spec = self.design(requirements, knowledge)

    # Write to shared memory
    shared_memory.update_ux_spec(
        design_spec,
        reasoning="Initial design specification generated"
    )

    return {"success": True, "spec": design_spec}
```

#### Skill: refine_spec

```python
def _skill_refine_spec(self, shared_memory: SharedSessionMemory, **kwargs):
    """Refine existing spec based on feedback (PARTIAL, not full regeneration)"""
    print("[UX Agent] Refining existing design spec...")

    current_spec = shared_memory.ux_spec
    if not current_spec:
        return {"success": False, "error": "No spec to refine"}

    # Get feedback from user or React agent
    feedback = kwargs.get('feedback') or self._extract_feedback(shared_memory)

    # Refine specific parts (NOT full regeneration)
    refined_spec = self._refine_design_partial(current_spec, feedback, shared_memory)

    # Update in shared memory
    shared_memory.update_ux_spec(
        refined_spec,
        reasoning=f"Refined based on: {feedback[:100]}"
    )

    return {"success": True, "spec": refined_spec}
```

#### Skill: address_schema_conflicts

```python
def _skill_address_schema_conflicts(self, shared_memory: SharedSessionMemory, **kwargs):
    """Fix schema mismatches reported by React agent"""
    print("[UX Agent] Addressing schema conflicts...")

    conflicts = shared_memory.get_unresolved_conflicts(is_design=True)
    if not conflicts:
        return {"success": True, "message": "No conflicts to address"}

    current_spec = shared_memory.ux_spec

    for conflict in conflicts:
        if conflict.conflict_type == ConflictType.DESIGN_SCHEMA_MISMATCH:
            # Fix the schema issue
            current_spec = self._fix_schema_mismatch(
                current_spec,
                conflict.description,
                conflict.suggested_resolution
            )

            # Mark conflict as resolved
            shared_memory.resolve_conflict(conflict)

            # Log negotiation
            shared_memory.log_negotiation(
                from_agent="UX Designer",
                to_agent="React Developer",
                message=f"Fixed schema conflict: {conflict.description}",
                metadata={"conflict_type": conflict.conflict_type.value}
            )

    # Update spec
    shared_memory.update_ux_spec(
        current_spec,
        reasoning="Fixed schema conflicts"
    )

    return {"success": True, "conflicts_resolved": len(conflicts)}
```

#### Skill: resolve_conflicts

```python
def _skill_resolve_conflicts(self, shared_memory: SharedSessionMemory, **kwargs):
    """Resolve conflicts reported by React agent (general)"""
    print("[UX Agent] Resolving conflicts with React...")

    conflicts = shared_memory.get_unresolved_conflicts(is_design=True)

    for conflict in conflicts:
        # Handle different conflict types
        if conflict.conflict_type == ConflictType.MISSING_DESIGN_FIELD:
            self._add_missing_field(shared_memory.ux_spec, conflict)
        elif conflict.conflict_type == ConflictType.DATA_SOURCE_MISMATCH:
            self._fix_data_source(shared_memory.ux_spec, conflict)

        # Resolve
        shared_memory.resolve_conflict(conflict)

    return {"success": True}
```

#### Skill: finish

```python
def _skill_finish(self, shared_memory: SharedSessionMemory, **kwargs):
    """Mark design as complete"""
    print("[UX Agent] Marking design as complete...")

    shared_memory.ux_status = "done"
    shared_memory.ux_satisfactory = True

    return {"finished": True}
```

### 6. Evaluation Function

```python
@dataclass
class UXEvaluationResult:
    """Structured evaluation of UX design"""
    satisfactory: bool
    issues: List[str]
    next_action: str  # "refine_spec", "address_conflicts", "finish"
    conflicts_detected: List[Conflict]

def _evaluate_design(self, shared_memory: SharedSessionMemory) -> UXEvaluationResult:
    """Evaluate current design specification"""
    issues = []
    conflicts_detected = []

    spec = shared_memory.ux_spec

    if not spec:
        return UXEvaluationResult(
            satisfactory=False,
            issues=["No design spec exists"],
            next_action="generate_initial_spec",
            conflicts_detected=[]
        )

    # Check 1: Has components
    if not spec.components or len(spec.components) == 0:
        issues.append("Design has no components")

    # Check 2: Has data sources
    if not spec.data_sources:
        issues.append("Design has no data sources")

    # Check 3: Check for unresolved conflicts
    unresolved = shared_memory.get_unresolved_conflicts(is_design=True)
    if unresolved:
        issues.append(f"{len(unresolved)} unresolved conflicts")
        conflicts_detected = unresolved

    # Determine satisfactory
    satisfactory = len(issues) == 0

    # Determine next action
    if conflicts_detected:
        next_action = "address_schema_conflicts"
    elif not satisfactory:
        next_action = "refine_spec"
    else:
        next_action = "finish"

    return UXEvaluationResult(
        satisfactory=satisfactory,
        issues=issues,
        next_action=next_action,
        conflicts_detected=conflicts_detected
    )
```

### 7. Conflict Detection

```python
def detect_conflicts(self, shared_memory: SharedSessionMemory):
    """
    Detect conflicts between UX design and React implementation.

    This is called AFTER React generates code, to check for mismatches.
    """
    conflicts = []

    if not shared_memory.react_files:
        return []  # No React code to compare against

    spec = shared_memory.ux_spec
    react_code = shared_memory.react_files

    # Check 1: Missing components in React
    for component in spec.components:
        component_name = component.get('type', '').replace('_', '').title()

        # Search for component in React files
        found = any(component_name in code for code in react_code.values())

        if not found:
            conflicts.append(Conflict(
                conflict_type=ConflictType.MISSING_COMPONENT,
                source_agent="UX Designer",
                description=f"Component '{component_name}' missing in React implementation",
                affected_component=component_name,
                suggested_resolution=f"Add {component_name} component to implementation",
                severity="high"
            ))

    # Check 2: Data source mismatches
    # (Additional checks...)

    # Write conflicts to shared memory
    for conflict in conflicts:
        shared_memory.add_conflict(conflict, is_design=True)

    return conflicts
```

### 8. Partial Refinement Logic

```python
def _refine_design_partial(self, current_spec: DesignSpec, feedback: str, shared_memory: SharedSessionMemory) -> DesignSpec:
    """
    Refine specific parts of the design WITHOUT full regeneration.

    This is a KEY Phase 5 capability.
    """
    # Create prompt for partial refinement
    prompt = f"""You are refining an existing UX design.

**Current Design:**
- Screen: {current_spec.screen_type}
- Components: {[c.get('type') for c in current_spec.components]}
- Patterns: {current_spec.patterns}

**Feedback to Address:**
{feedback}

**Task:** Modify ONLY the parts mentioned in feedback. Keep everything else unchanged.

Return JSON with ONLY the changes:
{{
  "components_to_add": [...],
  "components_to_modify": [...],
  "components_to_remove": [...],
  "patterns_to_add": [...],
  "styling_updates": {{...}}
}}
"""

    # Call LLM
    response = self.client.messages.create(
        model=self.model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse changes
    changes = json.loads(response.content[0].text)

    # Apply changes to current spec (PARTIAL UPDATE)
    refined_spec = self._apply_design_changes(current_spec, changes)

    return refined_spec
```

---

## 🔗 Integration Points

### 1. Update design() Method to Support Both Modes

```python
def design(self, requirements: Dict, design_knowledge: Dict, shared_memory: SharedSessionMemory = None):
    """
    Generate design specification.

    If autonomous mode + shared_memory provided: Use planning loop
    Otherwise: Use original procedural approach
    """
    if self.use_autonomous_mode and shared_memory:
        # Phase 5: Autonomous planning loop
        return self.run(shared_memory)
    else:
        # Phase 3: Original procedural design
        return self._design_with_cot(requirements, design_knowledge)
```

### 2. Update with_context() for SharedMemory

```python
def with_context(self, session_ctx: SessionContext, shared_memory: SharedSessionMemory = None):
    """Bind context for protocol-aware execution"""
    self.session_ctx = session_ctx
    self.shared_memory = shared_memory  # Phase 5
    return self
```

---

## 📊 Testing Plan

### Test 1: Skill Registry
```python
def test_ux_agent_skill_registry():
    agent = UXDesignerAgent(use_autonomous_mode=True)
    assert len(agent.skills) == 8
    assert "generate_initial_spec" in agent.skills
    assert "refine_spec" in agent.skills
```

### Test 2: Planning Loop
```python
def test_ux_agent_planning_loop():
    agent = UXDesignerAgent(use_autonomous_mode=True)
    memory = SharedSessionMemory(session_id="test")
    memory.user_requirements = {"intent": "Test"}

    spec = agent.run(memory)
    assert spec is not None
    assert memory.ux_spec_version > 0
```

### Test 3: Partial Refinement
```python
def test_ux_agent_partial_refinement():
    agent = UXDesignerAgent(use_autonomous_mode=True)
    memory = SharedSessionMemory(session_id="test")

    # Generate initial
    initial_spec = agent._skill_generate_initial_spec(memory)

    # Refine partially
    refined_spec = agent._skill_refine_spec(memory, feedback="Add filtering")

    # Version should increment
    assert memory.ux_spec_version == 2
```

### Test 4: Conflict Detection
```python
def test_ux_agent_conflict_detection():
    agent = UXDesignerAgent(use_autonomous_mode=True)
    memory = SharedSessionMemory(session_id="test")

    # Set up conflict scenario
    memory.update_ux_spec(mock_spec)
    memory.update_react_files({"App.tsx": "..."})

    conflicts = agent.detect_conflicts(memory)
    assert len(conflicts) > 0
```

---

## 📈 Success Metrics

**Phase 5 UX Agent is complete when:**
- ✅ Has planning loop with max 3 iterations
- ✅ Has 8 working skills
- ✅ Can refine existing spec (not just regenerate)
- ✅ Detects conflicts with React code
- ✅ Writes to SharedSessionMemory
- ✅ Backward compatible (works in both modes)
- ✅ All tests passing

---

## 🚀 Implementation Estimate

**Scope:** ~300-400 lines of new code
**Complexity:** High (major refactor)
**Time:** Multi-session implementation

**Files to Modify:**
1. `src/agents/ux_designer.py` - Add all Phase 5 capabilities

**Files to Create:**
1. `test_ux_agent_phase5.py` - Comprehensive tests

---

**Status:** Specification complete
**Next:** Begin implementation
**Dependency:** Phase 5 Step 1 (SharedSessionMemory) ✅ Complete
