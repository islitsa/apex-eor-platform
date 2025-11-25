# Protocol + Gradient Architecture: Execution Plan

**Status:** Ready to implement
**Estimated Time:** Phase 1 (2-3 hours), Phase 2 (3-4 hours)
**Priority:** HIGH - Fixes immediate bugs + prevents future drift

---

## Overview

Two-layer architecture that adds:
1. **Protocol Layer** (Week 1): Type-safe context passing between agents
2. **Gradient Field** (Week 2): Semantic stability validation with auto-correction

---

## Phase 1: Protocol Layer (Ship Today)

### Goals
- ✅ Fix missing context bugs (agents don't know what sources were discovered)
- ✅ Fix wrong sources bug (React uses undiscovered data)
- ✅ Fix type errors (mixed types in stages array)
- ✅ Add compile-time safety (can't execute without context)

### Task 1.1: Create Core Protocol Types
**File:** `src/agents/context/protocol.py`
**Lines:** ~100 lines

**Code to write:**
```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Protocol, Optional, Any

class TaskType(str, Enum):
    DASHBOARD = "dashboard"
    ANALYSIS = "analysis"
    REPORT = "report"

class OutputFormat(str, Enum):
    REACT = "react"
    STREAMLIT = "streamlit"
    JUPYTER = "jupyter"

@dataclass
class DiscoveryContext:
    """What was discovered"""
    sources: List[str]                  # ["fracfocus", "rrc"]
    record_counts: Dict[str, int]       # {"fracfocus": 239059, "rrc": 18200}
    discovery_confidence: float         # 0.0-1.0
    rationale: str                      # Why these sources
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class UserIntent:
    """What user wants"""
    original_query: str                 # "show fracfocus data"
    parsed_intent: str                  # "generate_dashboard"
    scope: List[str]                    # ["fracfocus"] - CRITICAL for filtering
    task_type: TaskType                 # DASHBOARD
    output_format: OutputFormat         # REACT
    filters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionContext:
    """How agents behave"""
    max_iterations: int = 5
    require_validation: bool = True
    trace_decisions: bool = True

@dataclass
class SessionContext:
    """Complete context for agent execution"""
    session_id: str
    discovery: DiscoveryContext
    intent: UserIntent
    execution: ExecutionContext

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for logging/debugging"""
        return {
            "session_id": self.session_id,
            "discovery": {
                "sources": self.discovery.sources,
                "record_counts": self.discovery.record_counts,
                "confidence": self.discovery.discovery_confidence
            },
            "intent": {
                "query": self.intent.original_query,
                "scope": self.intent.scope,
                "task_type": self.intent.task_type.value,
                "output_format": self.intent.output_format.value
            }
        }

class ContextAware(Protocol):
    """Protocol that all agents must implement"""

    def with_context(self, ctx: SessionContext) -> "ContextAware":
        """Inject context before execution"""
        ...

    def execute(self) -> Dict[str, Any]:
        """Execute with injected context"""
        ...
```

**Testing:**
```python
# Test instantiation
ctx = SessionContext(
    session_id="test-123",
    discovery=DiscoveryContext(
        sources=["fracfocus"],
        record_counts={"fracfocus": 239059},
        discovery_confidence=0.95,
        rationale="User asked for fracfocus data"
    ),
    intent=UserIntent(
        original_query="show fracfocus chemical data",
        parsed_intent="generate_dashboard",
        scope=["fracfocus"],
        task_type=TaskType.DASHBOARD,
        output_format=OutputFormat.REACT
    ),
    execution=ExecutionContext()
)
assert len(ctx.discovery.sources) == 1
assert ctx.intent.scope == ["fracfocus"]
```

**Time:** 30 minutes

---

### Task 1.2: Update ReactDeveloperAgent
**File:** `src/agents/react_developer.py`
**Changes:** Add ContextAware implementation

**Current signature:**
```python
def build(self, design_spec: DesignSpec, context: Dict[str, Any]) -> Dict[str, str]:
```

**New implementation:**
```python
class ReactDeveloperAgent(ContextAware):
    def __init__(self, trace_collector=None, styling_framework="tailwind"):
        # ... existing init ...
        self.ctx: Optional[SessionContext] = None  # NEW

    def with_context(self, ctx: SessionContext) -> "ReactDeveloperAgent":
        """Inject context before execution"""
        self.ctx = ctx
        return self

    def execute(self) -> Dict[str, Any]:
        """Execute with context - wrapper for build()"""
        if not self.ctx:
            raise ValueError("Context not provided. Call with_context() first.")

        # Build design spec from context
        design_spec = self._build_design_spec_from_context()

        # Use ONLY discovered sources from context
        sources = self.ctx.discovery.sources

        # Call existing build method
        return self.build(design_spec, self._context_to_legacy_dict())

    def _context_to_legacy_dict(self) -> Dict[str, Any]:
        """Convert SessionContext to legacy dict format for backward compat"""
        return {
            "data_sources": {
                source: {"name": source, "row_count": count}
                for source, count in self.ctx.discovery.record_counts.items()
            },
            "user_prompt": self.ctx.intent.original_query,
            "scope": self.ctx.intent.scope  # NEW: explicit scope
        }

    # Keep existing build() method for backward compatibility
    def build(self, design_spec: DesignSpec, context: Dict[str, Any]) -> Dict[str, str]:
        # ... existing implementation ...

        # CRITICAL FIX: Filter sources to match context scope
        if self.ctx and self.ctx.intent.scope:
            # Only use sources in scope
            filtered_sources = {
                k: v for k, v in data_sources.items()
                if k in self.ctx.intent.scope
            }
            data_sources = filtered_sources

        # ... rest of existing code ...
```

**Key changes:**
1. Add `self.ctx: Optional[SessionContext]` attribute
2. Implement `with_context()` and `execute()` methods
3. Add scope filtering using `self.ctx.intent.scope`
4. Add defensive type coercion in output (see Task 1.5)

**Testing:**
```python
def test_react_agent_requires_context():
    agent = ReactDeveloperAgent()
    with pytest.raises(ValueError, match="Context not provided"):
        agent.execute()

def test_react_agent_uses_discovered_sources():
    agent = ReactDeveloperAgent()
    ctx = SessionContext(
        discovery=DiscoveryContext(sources=["fracfocus"], ...),
        intent=UserIntent(scope=["fracfocus"], ...)
    )
    agent.with_context(ctx)
    result = agent.execute()
    # Should only use fracfocus, not all sources
    assert "fracfocus" in result["sources"]
    assert "rrc" not in result["sources"]
```

**Time:** 45 minutes

---

### Task 1.3: Update UXDesignerAgent
**File:** `src/agents/ux_designer.py`
**Changes:** Similar to ReactDeveloper

**Implementation:**
```python
class UXDesignerAgent(ContextAware):
    def __init__(self, trace_collector=None):
        # ... existing init ...
        self.ctx: Optional[SessionContext] = None  # NEW

    def with_context(self, ctx: SessionContext) -> "UXDesignerAgent":
        self.ctx = ctx
        return self

    def execute(self) -> Dict[str, Any]:
        if not self.ctx:
            raise ValueError("Context not provided. Call with_context() first.")

        # Build requirements from context
        requirements = {
            "intent": self.ctx.intent.original_query,
            "screen_type": self._infer_screen_type(self.ctx.intent.task_type),
            "data_sources": {
                source: {"name": source, "row_count": count}
                for source, count in self.ctx.discovery.record_counts.items()
            }
        }

        # Call existing design method
        design_spec = self.design(requirements)

        # Return as dict
        return design_spec.to_dict()

    def _infer_screen_type(self, task_type: TaskType) -> str:
        mapping = {
            TaskType.DASHBOARD: "data_dashboard",
            TaskType.ANALYSIS: "analysis_view",
            TaskType.REPORT: "report_view"
        }
        return mapping.get(task_type, "data_dashboard")
```

**Time:** 30 minutes

---

### Task 1.4: Update UICodeOrchestrator
**File:** `src/agents/ui_orchestrator.py`
**Changes:** Build SessionContext and thread through agents

**Current code:**
```python
def generate_ui_code(self, requirements: Dict[str, Any], context: Dict[str, Any]) -> str:
    # ... fetch data, retrieve knowledge ...
    design_spec = self.ux_designer.design(requirements, design_knowledge)
    react_files = self.react_developer.build(design_spec, enhanced_context)
```

**New code:**
```python
def generate_ui_code(self, requirements: Dict[str, Any], context: Dict[str, Any]) -> str:
    print("\n[Orchestrator] Building SessionContext...")

    # Phase 0A: Fetch real data (existing)
    data_context = self._fetch_data_context()

    # Phase 0B: Retrieve knowledge (existing)
    knowledge = self._retrieve_all_knowledge(data_context=data_context)

    # NEW: Build structured SessionContext
    ctx = self._build_session_context(requirements, data_context, knowledge)

    print(f"[Orchestrator] SessionContext created:")
    print(f"  - Session ID: {ctx.session_id}")
    print(f"  - Discovered sources: {ctx.discovery.sources}")
    print(f"  - Intent scope: {ctx.intent.scope}")
    print(f"  - Task type: {ctx.intent.task_type.value}")

    # Phase 1: UX Design with context
    print("\nPHASE 1: UX DESIGN (with SessionContext)")
    design = self.ux_designer.with_context(ctx).execute()

    # Phase 2: React Implementation with context
    print("\nPHASE 2: REACT IMPLEMENTATION (with SessionContext)")
    code = self.react_developer.with_context(ctx).execute()

    return code

def _build_session_context(
    self,
    requirements: Dict[str, Any],
    data_context: Dict,
    knowledge: Dict
) -> SessionContext:
    """Build SessionContext from requirements and discovered data"""
    import uuid

    # Extract discovered sources
    data_sources = requirements.get('data_sources', {})
    sources = list(data_sources.keys())
    record_counts = {
        name: info.get('row_count', 0)
        for name, info in data_sources.items()
    }

    # Parse user intent
    user_query = requirements.get('intent', 'Generate dashboard')
    task_type = self._infer_task_type(requirements.get('screen_type', 'dashboard'))

    # Build context
    ctx = SessionContext(
        session_id=str(uuid.uuid4()),
        discovery=DiscoveryContext(
            sources=sources,
            record_counts=record_counts,
            discovery_confidence=0.95,  # High confidence from discovery tools
            rationale=user_query
        ),
        intent=UserIntent(
            original_query=user_query,
            parsed_intent="generate_dashboard",
            scope=sources,  # CRITICAL: Scope = discovered sources
            task_type=task_type,
            output_format=OutputFormat.REACT
        ),
        execution=ExecutionContext(
            trace_decisions=self.trace_collector is not None
        )
    )

    return ctx

def _infer_task_type(self, screen_type: str) -> TaskType:
    """Map screen_type to TaskType enum"""
    if 'dashboard' in screen_type.lower():
        return TaskType.DASHBOARD
    elif 'analysis' in screen_type.lower():
        return TaskType.ANALYSIS
    elif 'report' in screen_type.lower():
        return TaskType.REPORT
    return TaskType.DASHBOARD
```

**Key changes:**
1. Add `_build_session_context()` method
2. Replace dict-based context with SessionContext
3. Use `.with_context(ctx).execute()` pattern for agents
4. Log context details for debugging

**Time:** 45 minutes

---

### Task 1.5: Add Defensive Type Coercion
**File:** `src/agents/react_developer.py`
**Location:** In `_create_react_prompt()` method

**Add to prompt:**
```python
⚠️ DEFENSIVE CODING - TYPE COERCION:

API responses may contain mixed types. ALWAYS coerce to expected types when rendering:

```typescript
// ✅ CORRECT - Safe type coercion:
{String(stage.status || 'unknown').replace(/_/g, ' ')}
{Number(metric.value || 0).toLocaleString()}

// ❌ WRONG - Assumes types:
{stage.status.replace(/_/g, ' ')}  // TypeError if status is number!
```

CRITICAL: The stages array may contain metadata fields (dates, counts).
Always use String() coercion when rendering stage.status.
```

**Also add validation in parser:**
```python
def _validate_type_safety(self, files: Dict[str, str]):
    """Check for missing String() coercion in TypeScript files"""
    for filename, content in files.items():
        if not filename.endswith(('.tsx', '.ts')):
            continue

        # Look for .replace() calls without String() coercion
        import re
        pattern = r'{\s*(\w+\.\w+)\.replace\('
        matches = re.findall(pattern, content)

        for match in matches:
            if 'String(' not in content[:content.index(match)]:
                print(f"  ⚠️  {filename}: Missing String() coercion for {match}.replace()")
```

**Time:** 20 minutes

---

### Task 1.6: Write Tests
**File:** `tests/test_protocol.py`
**Lines:** ~150 lines

**Tests to write:**
```python
import pytest
from src.agents.context.protocol import (
    SessionContext, DiscoveryContext, UserIntent,
    ExecutionContext, TaskType, OutputFormat
)
from src.agents.react_developer import ReactDeveloperAgent
from src.agents.ux_designer import UXDesignerAgent

class TestProtocolTypes:
    def test_discovery_context_creation(self):
        ctx = DiscoveryContext(
            sources=["fracfocus", "rrc"],
            record_counts={"fracfocus": 239059, "rrc": 18200},
            discovery_confidence=0.95,
            rationale="User requested petroleum data"
        )
        assert len(ctx.sources) == 2
        assert ctx.record_counts["fracfocus"] == 239059
        assert ctx.discovery_confidence == 0.95

    def test_user_intent_with_scope(self):
        intent = UserIntent(
            original_query="show fracfocus data",
            parsed_intent="generate_dashboard",
            scope=["fracfocus"],  # Only fracfocus!
            task_type=TaskType.DASHBOARD,
            output_format=OutputFormat.REACT
        )
        assert intent.scope == ["fracfocus"]
        assert intent.task_type == TaskType.DASHBOARD

    def test_session_context_serialization(self):
        ctx = SessionContext(
            session_id="test-123",
            discovery=DiscoveryContext(
                sources=["fracfocus"],
                record_counts={"fracfocus": 239059},
                discovery_confidence=0.95,
                rationale="Test"
            ),
            intent=UserIntent(
                original_query="test",
                parsed_intent="test",
                scope=["fracfocus"],
                task_type=TaskType.DASHBOARD,
                output_format=OutputFormat.REACT
            ),
            execution=ExecutionContext()
        )

        serialized = ctx.to_dict()
        assert serialized["session_id"] == "test-123"
        assert "fracfocus" in serialized["discovery"]["sources"]
        assert serialized["intent"]["scope"] == ["fracfocus"]

class TestContextAwareAgents:
    def test_react_agent_requires_context(self):
        """Protocol prevents execution without context"""
        agent = ReactDeveloperAgent()

        with pytest.raises(ValueError, match="Context not provided"):
            agent.execute()

    def test_ux_agent_requires_context(self):
        """UX agent also requires context"""
        agent = UXDesignerAgent()

        with pytest.raises(ValueError, match="Context not provided"):
            agent.execute()

    def test_react_agent_filters_by_scope(self):
        """Agent only uses sources in scope"""
        agent = ReactDeveloperAgent()

        ctx = SessionContext(
            session_id="test",
            discovery=DiscoveryContext(
                sources=["fracfocus", "rrc"],  # Discovered both
                record_counts={"fracfocus": 1000, "rrc": 2000},
                discovery_confidence=0.95,
                rationale="Test"
            ),
            intent=UserIntent(
                original_query="show fracfocus data",
                parsed_intent="generate_dashboard",
                scope=["fracfocus"],  # But scope is only fracfocus!
                task_type=TaskType.DASHBOARD,
                output_format=OutputFormat.REACT
            ),
            execution=ExecutionContext()
        )

        agent.with_context(ctx)
        # Agent should only use fracfocus, not rrc
        legacy_dict = agent._context_to_legacy_dict()
        assert "fracfocus" in legacy_dict["scope"]
        assert len(legacy_dict["scope"]) == 1

class TestOrchestrator:
    def test_orchestrator_builds_context(self):
        """Orchestrator creates valid SessionContext"""
        from src.agents.ui_orchestrator import UICodeOrchestrator

        orch = UICodeOrchestrator()

        requirements = {
            "intent": "show fracfocus data",
            "screen_type": "dashboard",
            "data_sources": {
                "fracfocus": {"row_count": 239059}
            }
        }

        ctx = orch._build_session_context(requirements, {}, {})

        assert ctx.discovery.sources == ["fracfocus"]
        assert ctx.intent.scope == ["fracfocus"]
        assert ctx.intent.task_type == TaskType.DASHBOARD

def test_type_coercion_in_output():
    """Test that type coercion is applied to mixed-type data"""
    # This would be integration test with actual LLM generation
    # For now, just verify prompt includes type coercion guidance
    agent = ReactDeveloperAgent()
    prompt = agent._create_react_prompt(
        design_spec=...,
        data_sources={"test": {"row_count": 100}},
        user_prompt="test"
    )

    assert "String(" in prompt
    assert "DEFENSIVE CODING" in prompt
    assert "type coercion" in prompt.lower()
```

**Run tests:**
```bash
pytest tests/test_protocol.py -v
```

**Time:** 1 hour

---

## Phase 1 Summary

**Total Time:** ~4 hours
**Files Created:** 1 (protocol.py)
**Files Modified:** 3 (react_developer.py, ux_designer.py, ui_orchestrator.py)
**Tests Written:** ~10 tests

**Bugs Fixed:**
- ✅ Missing context (agents get SessionContext)
- ✅ Wrong sources (filtered by scope)
- ✅ Type errors (defensive coercion)

**Deploy:** Commit, test, merge to main

---

## Phase 2: Gradient Field (Week 2)

### Goals
- ✅ Detect source drift (using undiscovered sources)
- ✅ Detect type mismatches (mixed types in arrays)
- ✅ Detect semantic drift (scope creep during execution)
- ✅ Auto-correct violations (modify agent output)
- ✅ Block hard violations (prevent execution)

### Task 2.1: Create GradientField Class
**File:** `src/agents/context/gradient_field.py`
**Lines:** ~200 lines

**Code structure:**
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

from src.agents.context.protocol import SessionContext

@dataclass
class ProposedAction:
    """Action an agent wants to take"""
    agent_name: str
    action_type: str  # "build_ui", "run_query", "generate_code"
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class GradientSignal:
    """Evaluation result from gradient field"""
    score: float  # -1.0 (bad) to 1.0 (good)
    reasons: List[str]
    corrections: Dict[str, Any]
    hard_block: bool = False

@dataclass
class ArchitectureMetrics:
    """Metrics for monitoring architecture health"""
    # Protocol metrics
    context_handoff_failures: int = 0

    # Gradient metrics
    corrections_applied: int = 0
    hard_blocks_triggered: int = 0

    # Combined
    total_agent_failures: int = 0

class GradientField:
    """
    Semantic stability layer for agent system.

    Validates agent actions against SessionContext to detect:
    - Source consistency violations (using undiscovered sources)
    - Type safety issues (mixed types)
    - Semantic drift (scope creep)
    """

    def __init__(self):
        self.drift_correction = 0.0
        self.decision_history: List[Tuple[SessionContext, ProposedAction, GradientSignal]] = []
        self.original_context: Optional[SessionContext] = None

    def evaluate(self, ctx: SessionContext, action: ProposedAction) -> GradientSignal:
        """
        Evaluate action against context.

        Returns:
            GradientSignal with score, reasons, and corrections
        """
        score = 0.0
        reasons = []
        corrections = {}

        # Store first context (drift baseline)
        if not self.original_context:
            self.original_context = ctx

        # Check 1: Source consistency
        source_check = self._check_source_consistency(ctx, action)
        score += source_check["score"]
        reasons.extend(source_check["reasons"])
        corrections.update(source_check["corrections"])

        # Check 2: Type safety
        type_check = self._check_type_safety(ctx, action)
        score += type_check["score"]
        reasons.extend(type_check["reasons"])
        corrections.update(type_check["corrections"])

        # Check 3: Drift detection
        drift_check = self._check_drift(ctx, action)
        score += drift_check["score"]
        reasons.extend(drift_check["reasons"])

        # Build signal
        signal = GradientSignal(
            score=score,
            reasons=reasons,
            corrections=corrections,
            hard_block=(score < -0.7)  # Block if very bad
        )

        # Record history
        self.decision_history.append((ctx, action, signal))

        return signal

    def _check_source_consistency(self, ctx: SessionContext, action: ProposedAction) -> Dict:
        """Check if action uses only discovered sources"""
        # Implementation in Task 2.2
        pass

    def _check_type_safety(self, ctx: SessionContext, action: ProposedAction) -> Dict:
        """Check for mixed types in action payload"""
        # Implementation in Task 2.3
        pass

    def _check_drift(self, ctx: SessionContext, action: ProposedAction) -> Dict:
        """Check if action drifts from original intent"""
        # Implementation in Task 2.4
        pass
```

**Time:** 30 minutes

---

### Task 2.2: Implement Source Consistency Check
**File:** `src/agents/context/gradient_field.py`
**Method:** `_check_source_consistency()`

**Implementation:**
```python
def _check_source_consistency(self, ctx: SessionContext, action: ProposedAction) -> Dict:
    """
    Check if action uses only discovered sources.

    Example violation:
    - Discovered: ["fracfocus"]
    - Action uses: ["fracfocus", "rrc"]  ← RRC not discovered!
    """
    result = {"score": 0.0, "reasons": [], "corrections": {}}

    # Only check actions that involve data sources
    if action.action_type not in ["build_ui", "run_query", "fetch_data"]:
        return result

    # Get discovered sources from context
    discovered = set(ctx.discovery.sources)

    # Get sources used in action
    used_sources = set()
    if "sources" in action.payload:
        used_sources = set(action.payload["sources"])
    elif "data_sources" in action.payload:
        used_sources = set(action.payload["data_sources"].keys())

    if not used_sources:
        return result  # No sources to check

    # Check for undiscovered sources
    undiscovered = used_sources - discovered

    if undiscovered:
        result["score"] = -0.7  # Severe violation
        result["reasons"].append(
            f"Using undiscovered sources: {undiscovered}. "
            f"Discovered sources: {discovered}"
        )
        result["corrections"]["sources"] = list(discovered)
        print(f"  🚨 [Gradient] Source violation: {undiscovered} not in {discovered}")
    else:
        result["score"] = 0.1  # Small positive for correct behavior
        print(f"  ✅ [Gradient] Source consistency OK: {used_sources} ⊆ {discovered}")

    return result
```

**Testing:**
```python
def test_gradient_catches_undiscovered_sources():
    gradient = GradientField()

    ctx = SessionContext(
        discovery=DiscoveryContext(
            sources=["fracfocus"],  # Only fracfocus discovered
            ...
        ),
        ...
    )

    action = ProposedAction(
        agent_name="ReactDev",
        action_type="build_ui",
        payload={"sources": ["fracfocus", "rrc"]}  # Using RRC!
    )

    signal = gradient.evaluate(ctx, action)

    assert signal.score < 0  # Negative score
    assert "undiscovered sources" in signal.reasons[0].lower()
    assert signal.corrections["sources"] == ["fracfocus"]
```

**Time:** 30 minutes

---

### Task 2.3: Implement Type Safety Check
**File:** `src/agents/context/gradient_field.py`
**Method:** `_check_type_safety()`

**Implementation:**
```python
def _check_type_safety(self, ctx: SessionContext, action: ProposedAction) -> Dict:
    """
    Check for mixed types in action payload.

    Example violation:
    stages = [
        {"status": "complete"},  ← dict
        29,                      ← int!
        "2025-10-24"            ← string!
    ]
    """
    result = {"score": 0.0, "reasons": [], "corrections": {}}

    # Check stages array (known issue)
    if "stages" in action.payload:
        stages = action.payload["stages"]
        if self._has_mixed_types(stages):
            result["score"] = -0.3
            result["reasons"].append(
                f"Mixed types in stages array. Found types: "
                f"{set(type(s).__name__ for s in stages)}"
            )
            result["corrections"]["add_type_coercion"] = True
            print(f"  ⚠️  [Gradient] Type safety violation in stages")

    # Check other arrays
    for key, value in action.payload.items():
        if isinstance(value, list) and value:
            if self._has_mixed_types(value):
                result["score"] -= 0.2
                result["reasons"].append(f"Mixed types in {key}")

    return result

def _has_mixed_types(self, data: List) -> bool:
    """Check if list contains mixed types"""
    if not data:
        return False

    types = set(type(item) for item in data)
    return len(types) > 1
```

**Testing:**
```python
def test_gradient_detects_mixed_types():
    gradient = GradientField()

    action = ProposedAction(
        agent_name="ReactDev",
        action_type="render_ui",
        payload={
            "stages": [
                {"status": "ok"},  # dict
                29,                # int
                "2025-10-24"       # string
            ]
        }
    )

    signal = gradient.evaluate(ctx, action)

    assert signal.score < 0
    assert "mixed types" in signal.reasons[0].lower()
    assert signal.corrections["add_type_coercion"] == True
```

**Time:** 30 minutes

---

### Task 2.4: Implement Drift Detection
**File:** `src/agents/context/gradient_field.py`
**Method:** `_check_drift()`

**Implementation:**
```python
def _check_drift(self, ctx: SessionContext, action: ProposedAction) -> Dict:
    """
    Check if action drifts from original intent.

    Drift = scope creep during execution.
    Example: Started with ["fracfocus"], now using ["fracfocus", "rrc", "usgs"]
    """
    result = {"score": 0.0, "reasons": []}

    if not self.original_context:
        return result  # First action, no drift yet

    # Get original scope
    original_scope = set(self.original_context.intent.scope)

    # Get current scope from action
    current_scope = set()
    if "sources" in action.payload:
        current_scope = set(action.payload["sources"])

    if not current_scope:
        return result

    # Calculate drift (overlap with original scope)
    if original_scope:
        overlap = len(original_scope & current_scope) / len(original_scope)

        if overlap < 0.5:  # Less than 50% overlap = drifting
            self.drift_correction += 0.1
            result["score"] = -self.drift_correction
            result["reasons"].append(
                f"Drifting from original scope. "
                f"Original: {original_scope}, Current: {current_scope}, "
                f"Overlap: {overlap:.1%}, Drift score: {self.drift_correction:.2f}"
            )
            print(f"  ⚠️  [Gradient] Drift detected: {overlap:.1%} overlap")
        else:
            print(f"  ✅ [Gradient] No drift: {overlap:.1%} overlap with original")

    return result
```

**Testing:**
```python
def test_gradient_detects_drift():
    gradient = GradientField()

    # First action (baseline)
    ctx1 = SessionContext(
        intent=UserIntent(scope=["fracfocus"], ...)
    )
    action1 = ProposedAction(
        payload={"sources": ["fracfocus"]}
    )
    signal1 = gradient.evaluate(ctx1, action1)
    assert signal1.score >= 0  # No drift yet

    # Second action (drifting)
    ctx2 = SessionContext(
        intent=UserIntent(scope=["fracfocus", "rrc", "usgs"], ...)  # Expanded!
    )
    action2 = ProposedAction(
        payload={"sources": ["fracfocus", "rrc", "usgs"]}
    )
    signal2 = gradient.evaluate(ctx2, action2)

    assert signal2.score < 0  # Negative for drift
    assert "drift" in signal2.reasons[0].lower()
```

**Time:** 45 minutes

---

### Task 2.5: Integrate into Orchestrator
**File:** `src/agents/ui_orchestrator.py`
**Changes:** Add gradient evaluation

**Implementation:**
```python
from src.agents.context.gradient_field import GradientField, ProposedAction, ArchitectureMetrics

class UICodeOrchestrator:
    def __init__(self, trace_collector=None, enable_gradient=False):
        # ... existing init ...

        # NEW: Gradient system
        self.gradient = GradientField() if enable_gradient else None
        self.metrics = ArchitectureMetrics()

        if enable_gradient:
            print("[Orchestrator] Gradient Field enabled (validation + correction)")

    def generate_ui_code(self, requirements: Dict[str, Any], context: Dict[str, Any]) -> str:
        # ... build context ...
        ctx = self._build_session_context(requirements, data_context, knowledge)

        # Phase 1: UX Design
        design_result = self.ux_designer.with_context(ctx).execute()

        if self.gradient:
            # Evaluate UX agent's output
            ux_action = ProposedAction(
                agent_name="UXDesigner",
                action_type="design_ui",
                payload=design_result
            )
            ux_signal = self.gradient.evaluate(ctx, ux_action)

            if ux_signal.corrections:
                print(f"  🔧 [Gradient] Applying {len(ux_signal.corrections)} corrections to UX output")
                design_result.update(ux_signal.corrections)
                self.metrics.corrections_applied += len(ux_signal.corrections)

            if ux_signal.hard_block:
                print(f"  🚨 [Gradient] BLOCKED UX action: {ux_signal.reasons}")
                self.metrics.hard_blocks_triggered += 1
                raise ValueError(f"UX action blocked: {ux_signal.reasons}")

        # Phase 2: React Implementation
        code_result = self.react_developer.with_context(ctx).execute()

        if self.gradient:
            # Evaluate React agent's output
            react_action = ProposedAction(
                agent_name="ReactDeveloper",
                action_type="build_ui",
                payload=code_result
            )
            react_signal = self.gradient.evaluate(ctx, react_action)

            if react_signal.corrections:
                print(f"  🔧 [Gradient] Applying {len(react_signal.corrections)} corrections to React output")
                code_result.update(react_signal.corrections)
                self.metrics.corrections_applied += len(react_signal.corrections)

            if react_signal.hard_block:
                print(f"  🚨 [Gradient] BLOCKED React action: {react_signal.reasons}")
                self.metrics.hard_blocks_triggered += 1
                raise ValueError(f"React action blocked: {react_signal.reasons}")

        # Print metrics
        if self.gradient:
            print("\n" + "="*80)
            print("GRADIENT FIELD METRICS")
            print("="*80)
            print(f"Corrections Applied:    {self.metrics.corrections_applied}")
            print(f"Hard Blocks Triggered:  {self.metrics.hard_blocks_triggered}")
            print(f"Context Handoffs:       {2}")  # UX + React
            print("="*80 + "\n")

        return code_result
```

**Usage:**
```python
# Enable gradient validation
orchestrator = UICodeOrchestrator(enable_gradient=True)
```

**Time:** 45 minutes

---

### Task 2.6: Write Tests
**File:** `tests/test_gradient_field.py`
**Lines:** ~200 lines

**Full test suite:**
```python
import pytest
from src.agents.context.protocol import SessionContext, DiscoveryContext, UserIntent, TaskType, OutputFormat
from src.agents.context.gradient_field import GradientField, ProposedAction, GradientSignal

class TestSourceConsistency:
    def test_detects_undiscovered_sources(self):
        """Gradient catches using undiscovered sources"""
        gradient = GradientField()

        ctx = SessionContext(
            session_id="test",
            discovery=DiscoveryContext(
                sources=["fracfocus"],
                record_counts={"fracfocus": 1000},
                discovery_confidence=0.95,
                rationale="Test"
            ),
            intent=UserIntent(
                original_query="test",
                parsed_intent="test",
                scope=["fracfocus"],
                task_type=TaskType.DASHBOARD,
                output_format=OutputFormat.REACT
            ),
            execution=ExecutionContext()
        )

        action = ProposedAction(
            agent_name="ReactDev",
            action_type="build_ui",
            payload={"sources": ["fracfocus", "rrc"]}  # RRC not discovered!
        )

        signal = gradient.evaluate(ctx, action)

        assert signal.score < 0
        assert "undiscovered" in signal.reasons[0].lower()
        assert signal.corrections["sources"] == ["fracfocus"]

    def test_allows_discovered_sources(self):
        """Gradient allows using only discovered sources"""
        gradient = GradientField()

        ctx = SessionContext(
            discovery=DiscoveryContext(sources=["fracfocus", "rrc"], ...),
            ...
        )

        action = ProposedAction(
            agent_name="ReactDev",
            action_type="build_ui",
            payload={"sources": ["fracfocus"]}  # Subset of discovered
        )

        signal = gradient.evaluate(ctx, action)

        assert signal.score >= 0  # Positive or neutral

class TestTypeSafety:
    def test_detects_mixed_types(self):
        """Gradient catches mixed types in arrays"""
        gradient = GradientField()

        action = ProposedAction(
            agent_name="ReactDev",
            action_type="render_ui",
            payload={
                "stages": [
                    {"status": "complete"},  # dict
                    29,                      # int
                    "2025-10-24"            # string
                ]
            }
        )

        signal = gradient.evaluate(ctx, action)

        assert signal.score < 0
        assert "mixed types" in signal.reasons[0].lower()
        assert signal.corrections["add_type_coercion"] == True

    def test_allows_homogeneous_types(self):
        """Gradient allows arrays with single type"""
        gradient = GradientField()

        action = ProposedAction(
            payload={
                "stages": [
                    {"status": "complete"},
                    {"status": "in_progress"},
                    {"status": "pending"}
                ]
            }
        )

        signal = gradient.evaluate(ctx, action)
        assert signal.score >= 0

class TestDriftDetection:
    def test_detects_scope_drift(self):
        """Gradient catches scope creep"""
        gradient = GradientField()

        # First action (baseline)
        ctx1 = SessionContext(
            intent=UserIntent(scope=["fracfocus"], ...)
        )
        action1 = ProposedAction(payload={"sources": ["fracfocus"]})
        signal1 = gradient.evaluate(ctx1, action1)

        # Second action (drifted)
        ctx2 = SessionContext(
            intent=UserIntent(scope=["fracfocus", "rrc", "usgs"], ...)
        )
        action2 = ProposedAction(payload={"sources": ["fracfocus", "rrc", "usgs"]})
        signal2 = gradient.evaluate(ctx2, action2)

        assert signal2.score < 0
        assert "drift" in signal2.reasons[0].lower()

    def test_no_drift_within_scope(self):
        """Gradient allows actions within original scope"""
        gradient = GradientField()

        ctx1 = SessionContext(intent=UserIntent(scope=["fracfocus", "rrc"], ...))
        action1 = ProposedAction(payload={"sources": ["fracfocus", "rrc"]})
        gradient.evaluate(ctx1, action1)

        ctx2 = SessionContext(intent=UserIntent(scope=["fracfocus"], ...))
        action2 = ProposedAction(payload={"sources": ["fracfocus"]})
        signal2 = gradient.evaluate(ctx2, action2)

        assert signal2.score >= -0.2  # Small drift OK

class TestHardBlocks:
    def test_blocks_severe_violations(self):
        """Gradient blocks actions with score < -0.7"""
        gradient = GradientField()

        ctx = SessionContext(
            discovery=DiscoveryContext(sources=["fracfocus"], ...)
        )

        action = ProposedAction(
            payload={"sources": ["rrc", "usgs", "completely_unknown"]}  # All wrong!
        )

        signal = gradient.evaluate(ctx, action)

        assert signal.hard_block == True
        assert signal.score < -0.7

class TestOrchestrationIntegration:
    def test_orchestrator_applies_corrections(self):
        """Orchestrator applies gradient corrections"""
        from src.agents.ui_orchestrator import UICodeOrchestrator

        orch = UICodeOrchestrator(enable_gradient=True)

        # Simulate agent returning wrong sources
        # Orchestrator should correct via gradient

        assert orch.gradient is not None
        assert orch.metrics.corrections_applied >= 0
```

**Run tests:**
```bash
pytest tests/test_gradient_field.py -v
```

**Time:** 1.5 hours

---

## Phase 2 Summary

**Total Time:** ~4-5 hours
**Files Created:** 1 (gradient_field.py)
**Files Modified:** 1 (ui_orchestrator.py)
**Tests Written:** ~15 tests

**Features Added:**
- ✅ Source consistency validation
- ✅ Type safety checking
- ✅ Drift detection
- ✅ Auto-correction
- ✅ Hard blocking
- ✅ Metrics tracking

**Deploy:** Commit, test, merge to main

---

## Complete Migration Timeline

| Week | Phase | Deliverables | Status |
|------|-------|--------------|--------|
| Week 1 | Protocol Layer | Types, agents, orchestrator, tests | Ready to start |
| Week 2 | Gradient Field | Validation, correction, metrics | Ready after Week 1 |
| Week 3 | Enable Blocking | Turn on hard blocks for violations | After Week 2 |
| Month 2+ | APEX Physics | Domain constraints (petroleum engineering) | Future |

---

## Success Metrics

**Protocol Layer (Week 1):**
- ✅ All agents require context to execute
- ✅ Zero "wrong sources" bugs
- ✅ Zero type errors from mixed arrays
- ✅ 100% test coverage for protocol

**Gradient Field (Week 2):**
- ✅ Detects 100% of source violations
- ✅ Detects 100% of type violations
- ✅ Drift score < 0.3 for valid actions
- ✅ < 5% false positive rate

**Combined (Week 3):**
- ✅ Context handoff failures → 0
- ✅ Corrections applied: track trend
- ✅ Hard blocks: < 1% of executions
- ✅ Agent failures: decrease by 80%

---

## Next Steps

1. **Review this plan** - Confirm approach
2. **Start Phase 1.1** - Create protocol.py
3. **Run tests continuously** - Ensure no regressions
4. **Deploy incrementally** - Don't break existing code
5. **Monitor metrics** - Track improvements

Ready to start implementation? I can begin with Task 1.1 (creating protocol.py).
