# Phase 5 Step 3: React Agent Upgrade Specification

## Current State Analysis

**File:** `src/agents/react_developer.py` (1511 lines)

### What React Agent Has (Phase 3.1):
- ✅ `build()` method - Generates React code from design spec
- ✅ Memory system - `implementation_history`
- ✅ ContextAware protocol - `with_context()`, `execute()`
- ✅ Validation - `_validate_no_mock_data()`, `_validate_file_completeness()`, `_validate_type_safety()`
- ✅ Token tracking
- ✅ Trace collection

### What's Missing for Phase 5:
- ❌ Autonomous mode flag (`use_autonomous_mode`)
- ❌ Planning loop (iterative plan → execute → evaluate)
- ❌ Skill registry (8-10 skills)
- ❌ Self-evaluation (ReactEvaluationResult)
- ❌ Component-level regeneration (key innovation!)
- ❌ Conflict detection (check against UX spec)
- ❌ SharedMemory integration

**Readiness Score:** 6.2/10 (Good foundations, needs autonomous loop)

---

## Architecture for Phase 5 React Agent

### Autonomous Planning Loop

```python
def run(self, shared_memory: SharedSessionMemory, max_steps: int = 3):
    """
    Autonomous planning loop for Phase 5.

    Returns:
        Generated React files (from shared_memory.react_files)
    """
    print(f"\n[React Agent] Starting autonomous mode (max {max_steps} steps)...")
    shared_memory.react_status = "planning"

    for step in range(max_steps):
        # 1. Plan next action (LLM reasoning)
        plan = self._plan_next_action(shared_memory)

        # 2. Execute skill
        result = self._execute_skill(plan, shared_memory)

        # 3. Evaluate implementation
        evaluation = self._evaluate_implementation(shared_memory)

        # 4. Terminate if satisfactory
        if evaluation.satisfactory or plan.skill == "finish":
            shared_memory.react_satisfactory = True
            shared_memory.react_status = "done"
            return shared_memory.react_files

    return shared_memory.react_files
```

---

## Skill Registry (10 Skills)

### 1. generate_initial_implementation
- **What:** Generate React code from UX spec
- **When:** No React files exist
- **Implementation:** Call existing `build()` method

### 2. fix_type_errors
- **What:** Fix TypeScript type errors
- **When:** Type errors detected in evaluation
- **Implementation:** LLM analyzes errors and generates fixes

### 3. fix_import_errors
- **What:** Fix import paths and missing imports
- **When:** Import errors detected
- **Implementation:** Add `.tsx` extensions, fix relative paths

### 4. regenerate_component
- **What:** Regenerate a specific component (KEY INNOVATION!)
- **When:** Feedback targets a specific component
- **Implementation:**
  ```python
  def _regenerate_component(self, component_name: str, reason: str, shared_memory):
      # Extract current component code
      # Generate replacement using LLM
      # Integrate back into full codebase
  ```

### 5. fix_data_filtering
- **What:** Fix source filtering issues
- **When:** Wrong sources displayed
- **Implementation:** Update filtering logic in App.tsx

### 6. adjust_styling
- **What:** Modify Tailwind classes/styling
- **When:** Styling feedback received
- **Implementation:** Targeted styling changes

### 7. optimize_code
- **What:** Optimize performance/structure
- **When:** Code quality issues detected
- **Implementation:** Refactor for better performance

### 8. resolve_conflicts
- **What:** Resolve conflicts with UX spec
- **When:** Conflicts detected in shared memory
- **Implementation:** Modify implementation to match UX spec

### 9. validate_implementation
- **What:** Run validation checks
- **When:** After generation or fixes
- **Implementation:** Call existing validation methods

### 10. finish
- **What:** Mark implementation as complete
- **When:** All checks pass
- **Implementation:** Set status flags

---

## Evaluation Structure

```python
@dataclass
class ReactEvaluationResult:
    """
    Structured evaluation result from React Agent.

    Phase 5: React agent evaluates its own work.
    """
    satisfactory: bool
    issues: List[str] = field(default_factory=list)
    next_action: str = "finish"  # "fix_types", "fix_imports", "regenerate_component", "finish"
    type_errors: List[str] = field(default_factory=list)
    import_errors: List[str] = field(default_factory=list)
    conflicts_detected: List[Any] = field(default_factory=list)
    reasoning: str = ""


def _evaluate_implementation(self, shared_memory) -> ReactEvaluationResult:
    """
    Evaluate current implementation and determine next action.
    """
    issues = []

    # Check if files exist
    if not shared_memory.react_files:
        return ReactEvaluationResult(
            satisfactory=False,
            issues=["No React files generated yet"],
            next_action="generate_initial_implementation"
        )

    # Check for conflicts with UX spec
    if shared_memory.implementation_conflicts:
        issues.append(f"{len(shared_memory.implementation_conflicts)} conflicts detected")
        return ReactEvaluationResult(
            satisfactory=False,
            issues=issues,
            next_action="resolve_conflicts",
            conflicts_detected=shared_memory.implementation_conflicts
        )

    # Validate code quality
    validation_issues = self._detect_code_issues(shared_memory.react_files)
    if validation_issues:
        return ReactEvaluationResult(
            satisfactory=False,
            issues=validation_issues,
            next_action="fix_type_errors" if "type error" in str(validation_issues) else "optimize_code"
        )

    # All checks pass
    return ReactEvaluationResult(
        satisfactory=True,
        issues=[],
        next_action="finish",
        reasoning="Implementation is complete with no issues"
    )
```

---

## Key Innovation: Component-Level Regeneration

**Current Problem:** React agent regenerates entire codebase for small changes (wasteful, loses working code)

**Phase 5 Solution:** Regenerate individual components

```python
def _skill_regenerate_component(self, shared_memory, args: Dict) -> Dict[str, Any]:
    """
    Skill: Regenerate a specific component.

    Phase 5 KEY INNOVATION: Component-level regeneration, not full codebase regeneration.
    """
    print("[React Agent] Executing: regenerate_component")

    component_name = args.get('component_name', '')
    reason = args.get('reason', '')

    if not component_name:
        return {"success": False, "error": "No component specified"}

    # Extract current component
    current_files = shared_memory.react_files
    component_file = f"components/{component_name}.tsx"

    if component_file not in current_files:
        return {"success": False, "error": f"Component {component_name} not found"}

    # Generate replacement using LLM
    prompt = f"""Regenerate the {component_name} React component.

REASON FOR REGENERATION:
{reason}

CURRENT COMPONENT:
{current_files[component_file]}

UX SPEC:
{shared_memory.ux_spec.to_summary() if shared_memory.ux_spec else 'N/A'}

Generate ONLY the {component_name}.tsx file, improved based on the reason above.
"""

    response = self.client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}]
    )

    new_component_code = self._extract_component_code(response.content[0].text)

    # Update in shared memory
    updated_files = current_files.copy()
    updated_files[component_file] = new_component_code

    shared_memory.update_react_files(
        updated_files,
        reasoning=f"Regenerated {component_name}: {reason}"
    )

    return {
        "success": True,
        "component": component_name,
        "reason": reason
    }
```

**Benefits:**
- ✅ Faster (only regenerate what's needed)
- ✅ Preserves working code
- ✅ More precise fixes
- ✅ Lower token cost

---

## Conflict Detection

```python
def detect_conflicts(self, shared_memory) -> List[Conflict]:
    """
    Detect conflicts between React implementation and UX spec.

    Phase 5: React agent proactively checks for mismatches.

    Returns:
        List of Conflict objects
    """
    conflicts = []

    if not shared_memory.ux_spec or not shared_memory.react_files:
        return conflicts

    from src.agents.shared_memory import Conflict, ConflictType

    ux_components = shared_memory.ux_spec.components
    react_files = shared_memory.react_files

    # Check 1: Are all UX components implemented?
    for component in ux_components:
        component_name = component.get('name', '')
        component_file = f"components/{component_name}.tsx"

        if component_file not in react_files:
            conflicts.append(Conflict(
                conflict_type=ConflictType.MISSING_COMPONENT,
                source_agent="React Developer",
                description=f"UX spec requires {component_name}, but component not implemented",
                affected_component=component_name,
                suggested_resolution=f"Generate {component_name}.tsx component",
                severity="high"
            ))

    # Check 2: Type mismatches (simplified)
    # In production: parse TypeScript, check interfaces

    # Check 3: Invalid imports
    app_file = react_files.get('App.tsx', '')
    if app_file:
        # Check for imports without .tsx extensions
        if "from './components/" in app_file and not "from './components/" + ".tsx" in app_file:
            conflicts.append(Conflict(
                conflict_type=ConflictType.INVALID_IMPORT,
                source_agent="React Developer",
                description="Import statements missing .tsx file extensions",
                suggested_resolution="Add .tsx extensions to all imports",
                severity="medium"
            ))

    return conflicts
```

---

## Integration Points

### With SharedMemory

```python
# Read from shared memory
ux_spec = shared_memory.ux_spec
data_context = shared_memory.data_context
knowledge = shared_memory.knowledge

# Write to shared memory
shared_memory.update_react_files(
    files,
    reasoning="Initial React implementation generated"
)

# Track reasoning
shared_memory.react_reasoning_trace.append("Fixed type errors in DataTable component")

# Check conflicts
conflicts = shared_memory.implementation_conflicts
```

### With UX Agent

The React Agent can:
1. **Read UX spec** from `shared_memory.ux_spec`
2. **Detect conflicts** when UX spec changes (`ux_spec_version` increments)
3. **Ask questions** via `shared_memory.ask_question()`
4. **Report issues** via `shared_memory.add_conflict()`

**Example:**
```python
# Detect UX spec update
if shared_memory.ux_spec_version > self.last_ux_version:
    print("[React Agent] UX spec updated, checking for changes...")
    conflicts = self.detect_conflicts(shared_memory)
    for conflict in conflicts:
        shared_memory.add_conflict(conflict, is_design=False)
```

---

## Changes Required

### 1. Add Dataclasses (at top of file)

```python
from dataclasses import dataclass, field

@dataclass
class ReactEvaluationResult:
    satisfactory: bool
    issues: List[str] = field(default_factory=list)
    next_action: str = "finish"
    type_errors: List[str] = field(default_factory=list)
    import_errors: List[str] = field(default_factory=list)
    conflicts_detected: List[Any] = field(default_factory=list)
    reasoning: str = ""

@dataclass
class Plan:
    skill: str
    reasoning: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    expected_outcome: str = ""
```

### 2. Update `__init__` Method

```python
def __init__(self, trace_collector=None, styling_framework="tailwind", use_autonomous_mode=False):
    # ... existing code ...

    # Phase 5: Autonomous mode flag
    self.use_autonomous_mode = use_autonomous_mode

    # Phase 5: Skill registry
    self.skills = {}
    if use_autonomous_mode:
        self._build_skill_registry()
        print("[React Developer Agent] Initialized in AUTONOMOUS mode with internal planning loop")
    else:
        print(f"[React Developer Agent] Initialized - Styling: {styling_framework}")
```

### 3. Update `execute()` Method

```python
def execute(self) -> Dict[str, Any]:
    if not self.ctx:
        raise ValueError("Context not provided")

    # Phase 5: Route to autonomous mode if enabled
    if self.use_autonomous_mode:
        from src.agents.shared_memory import SharedSessionMemory

        # Build shared memory from context
        shared_memory = SharedSessionMemory(session_id=self.ctx.session_id)
        shared_memory.ux_spec = None  # Orchestrator will populate
        shared_memory.knowledge = {}  # Orchestrator will populate

        # Run autonomous agent
        files = self.run(shared_memory, max_steps=3)
        return files

    # Phase 3.1: Procedural mode (backward compatible)
    # ... existing code ...
```

### 4. Add Phase 5 Methods

```python
# === Phase 5 Methods ===

def _build_skill_registry(self):
    """Build skill registry for autonomous mode."""
    self.skills = {
        "generate_initial_implementation": {
            "fn": self._skill_generate_initial_implementation,
            "description": "Generate React code from UX spec"
        },
        "fix_type_errors": {
            "fn": self._skill_fix_type_errors,
            "description": "Fix TypeScript type errors"
        },
        # ... 8 more skills ...
    }

def run(self, shared_memory, max_steps=3):
    """Autonomous planning loop."""
    # Plan → Execute → Evaluate → Iterate

def _plan_next_action(self, shared_memory) -> Plan:
    """LLM-backed planning for next action."""
    # Similar to UX Agent's _plan_next_step

def _execute_skill(self, plan, shared_memory) -> Dict:
    """Execute planned skill."""
    # Similar to UX Agent

def _evaluate_implementation(self, shared_memory) -> ReactEvaluationResult:
    """Evaluate implementation and determine next action."""
    # Check for conflicts, type errors, etc.

def detect_conflicts(self, shared_memory) -> List[Conflict]:
    """Detect conflicts with UX spec."""
    # Check component mismatches, type errors, etc.

# === Skill Implementations ===

def _skill_generate_initial_implementation(self, shared_memory, args):
    """Generate initial React code."""
    # Call existing build() method

def _skill_fix_type_errors(self, shared_memory, args):
    """Fix TypeScript type errors."""
    # LLM-based type error fixing

def _skill_regenerate_component(self, shared_memory, args):
    """Regenerate specific component (KEY INNOVATION!)."""
    # Component-level regeneration

# ... 7 more skill methods ...
```

---

## Testing Plan

**File:** `test_react_agent_phase5.py`

```python
def test_react_agent_autonomous_mode_initialization():
    """Test React Agent initializes correctly in autonomous mode"""
    agent = ReactDeveloperAgent(use_autonomous_mode=True)
    assert agent.use_autonomous_mode == True
    assert len(agent.skills) == 10

def test_react_agent_run():
    """Test autonomous run() method"""
    agent = ReactDeveloperAgent(use_autonomous_mode=True)
    shared_memory = SharedSessionMemory(session_id="test")
    # ... populate shared memory ...
    files = agent.run(shared_memory, max_steps=1)
    assert files is not None

def test_component_level_regeneration():
    """Test component-level regeneration"""
    # ... test that only target component is regenerated ...

def test_conflict_detection():
    """Test conflict detection with UX spec"""
    # ... test that conflicts are detected ...

def test_backward_compatibility():
    """Test that Phase 3.1 still works"""
    agent = ReactDeveloperAgent(use_autonomous_mode=False)
    # ... test existing build() method ...
```

---

## Implementation Metrics

**Estimated additions:**
- Dataclasses: ~50 lines
- `__init__` update: ~10 lines
- `execute()` update: ~20 lines
- `run()` method: ~50 lines
- `_plan_next_action()`: ~80 lines
- `_execute_skill()`: ~15 lines
- `_evaluate_implementation()`: ~60 lines
- `_build_skill_registry()`: ~40 lines
- 10 skill methods: ~200 lines (20 per skill)
- `detect_conflicts()`: ~80 lines
- Helper methods: ~50 lines

**Total:** ~655 lines

**New file size:** ~2166 lines (current 1511 + 655)

---

## Success Criteria

- ✅ React Agent has autonomous planning loop
- ✅ 10 skills registered and functional
- ✅ Component-level regeneration works (key innovation!)
- ✅ Conflict detection implemented
- ✅ SharedMemory integration complete
- ✅ Self-evaluation working
- ✅ All tests passing
- ✅ Backward compatibility maintained

---

## Next Steps

1. **Implement Phase 5 methods** (~655 lines)
2. **Create test file** (~300 lines)
3. **Run tests** to verify
4. **Document fixes** (similar to UX Agent fixes)
5. **Proceed to Step 4** (Orchestrator integration)

---

**Status:** Specification complete, ready for implementation
**Complexity:** High (major refactor, ~655 lines)
**Key Innovation:** Component-level regeneration (not full codebase regeneration)
