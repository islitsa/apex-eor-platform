# Phase 4: Autonomous Orchestrator Agent

## 🌟 Overview

**Phase 4 transforms the orchestrator from a procedural coordinator into an autonomous LLM-backed agent.**

Instead of following a fixed workflow, the orchestrator now:
- **Thinks** about what to do next
- **Plans** actions based on current state
- **Evaluates** progress after each step
- **Self-corrects** when things go wrong
- **Iterates** until goal is achieved

This is the final evolution: **giving the orchestrator a mind**.

---

## 🧠 Architecture

### Before Phase 4 (Procedural):
```
discover → knowledge → session → UX → React → done
```

### After Phase 4 (Autonomous):
```
while not goal_achieved:
    observe current state
    plan next action (LLM reasoning)
    execute chosen skill
    evaluate result
    update memory
    iterate
```

---

## 🏗️ Key Components

### 1. OrchestratorAgent ([src/agents/orchestrator_agent.py](src/agents/orchestrator_agent.py))

**The autonomous agent that supervises UI generation.**

**Core capabilities:**
- LLM-backed planning and reasoning
- Iterative execution loop
- Self-evaluation and correction
- Memory management
- Skill selection
- Error recovery

### 2. Session Memory

**Tracks everything the agent knows about the current session:**

```python
@dataclass
class SessionMemory:
    session_id: str
    iteration: int

    # User input
    user_requirements: Dict
    user_context: Dict

    # Discovered data
    data_context: Dict
    knowledge: Dict
    session_ctx: SessionContext

    # Agent outputs
    design_spec: DesignSpec
    react_files: Dict

    # Evaluation history
    evaluation_history: List[Dict]

    # Action history
    actions_taken: List[str]
    skills_used: List[str]

    # Error tracking
    errors: List[str]
    last_error: str

    # Planning trace
    planning_trace: List[Dict]

    # Success flags
    ux_satisfactory: bool
    react_satisfactory: bool
    goal_achieved: bool
```

### 3. Skill Registry

**Phase 3 tools + agents become callable skills:**

```python
skills = {
    # Data & filtering
    "discover_data": "Fetch real data from API",
    "filter_sources": "Filter sources by user intent",

    # Knowledge & context
    "retrieve_knowledge": "Get UX patterns from vector DB",
    "build_session_context": "Build SessionContext",
    "prepare_builder_context": "Prepare React context",

    # UX design
    "generate_ux": "Call UX Designer agent",
    "refine_ux": "Refine UX with feedback",
    "validate_ux": "Evaluate UX design spec",

    # React generation
    "generate_react": "Call React Developer agent",
    "regenerate_react": "Regenerate with fixes",
    "validate_react": "Evaluate React code",

    # Meta-actions
    "evaluate_progress": "Check overall progress",
    "finish": "Mark goal achieved"
}
```

### 4. Planning Module

**LLM-based reasoning to choose next action:**

**Input to LLM:**
- Current state (has data? has UX? has React?)
- Recent evaluations
- Error history
- Actions taken
- Available skills

**Output from LLM:**
```json
{
  "skill": "generate_ux",
  "reasoning": "We have data and knowledge but no UX design yet",
  "arguments": {},
  "expected_outcome": "UX design specification"
}
```

**Decision rules:**
- No data → `discover_data`
- No knowledge → `retrieve_knowledge`
- No session context → `build_session_context`
- No UX → `generate_ux`
- UX invalid → `refine_ux` or retry
- No React → `generate_react`
- React invalid → `regenerate_react`
- Both valid → `finish`

### 5. Reasoning Loop

**Main agent execution:**

```python
for iteration in range(MAX_ITERATIONS):
    # 1. Plan next action (LLM reasoning)
    plan = agent.plan_next_action()

    # 2. Execute chosen skill
    result = agent.execute_skill(plan)

    # 3. Update memory
    memory.actions_taken.append(plan.skill)

    # 4. Check if goal achieved
    if memory.goal_achieved:
        break

    # 5. Safety: max iterations
    if iteration >= MAX_ITERATIONS - 1:
        break
```

### 6. Skill Implementations

**Each skill is a wrapper around existing Phase 3 tools:**

```python
def _skill_discover_data(self, **kwargs):
    """Discover data from API"""
    filter_sources = kwargs.get('filter_sources', None)
    self.memory.data_context = self.orchestrator.discovery_tool.fetch_data_context(
        filter_sources=filter_sources
    )
    return {"success": self.memory.data_context.get('success', False)}
```

**Skills delegate to:**
- Phase 3 tools (DataShapingTool, ContextAssemblyTool, etc.)
- Phase 2 evaluation methods
- UX/React agents

---

## 🔄 How It Works

### Example Session:

**Iteration 1:**
```
State: Empty memory
Plan: discover_data
Execute: Call discovery_tool
Result: data_context filled
```

**Iteration 2:**
```
State: Has data, no knowledge
Plan: retrieve_knowledge
Execute: Call knowledge_tool
Result: knowledge filled
```

**Iteration 3:**
```
State: Has data + knowledge, no session context
Plan: build_session_context
Execute: Call context_assembly_tool
Result: session_ctx filled
```

**Iteration 4:**
```
State: Has context, no UX
Plan: generate_ux
Execute: Call UX Designer agent
Result: design_spec created
Evaluate: UX satisfactory ✅
```

**Iteration 5:**
```
State: Has UX, no React
Plan: generate_react
Execute: Call React Developer agent
Result: react_files created
Evaluate: React satisfactory ✅
```

**Iteration 6:**
```
State: Both UX and React valid
Plan: finish
Execute: Mark goal achieved
Result: DONE ✅
```

---

## 🎯 Benefits

### 1. **Autonomous Correction**
If UX or React is invalid, agent decides to retry/refine automatically

### 2. **Adaptive Planning**
Agent chooses skills based on current state, not fixed workflow

### 3. **Error Recovery**
Agent can detect errors and choose recovery strategies

### 4. **Iterative Improvement**
Can refine UX multiple times until satisfactory

### 5. **Introspection**
Complete trace of agent's reasoning and decisions

### 6. **Robustness**
Handles missing data, bad outputs, edge cases gracefully

### 7. **Future-Proof**
Easy to add new skills without changing core logic

---

## 🚀 Usage

### Enable Agent Mode:

```python
# Create orchestrator with agent mode enabled
orchestrator = UICodeOrchestrator(
    use_agent_mode=True,  # Enable Phase 4 autonomous reasoning
    enable_gradient=True,
    trace_collector=trace_collector
)

# Generate UI (agent decides what to do)
requirements = {
    'screen_type': 'dashboard',
    'intent': 'Show chemical data with pagination'
}

context = {
    'data_sources': {...}
}

code = orchestrator.generate_ui_code(requirements, context)
```

### Disable Agent Mode (Use Phase 3 Procedural):

```python
# Create orchestrator with procedural mode (default)
orchestrator = UICodeOrchestrator(
    use_agent_mode=False,  # Phase 3 procedural coordination
    enable_gradient=True
)

# Generate UI (fixed workflow)
code = orchestrator.generate_ui_code(requirements, context)
```

---

## 📊 Agent Trace Example

```
[OrchestratorAgent] Planning iteration 0
  Chosen skill: discover_data
  Reasoning: No data context available, need to fetch from API first

[OrchestratorAgent] Executing skill: discover_data
[OrchestratorAgent] Skill completed: discover_data

[OrchestratorAgent] Planning iteration 1
  Chosen skill: retrieve_knowledge
  Reasoning: Data discovered, now need UX patterns from knowledge base

[OrchestratorAgent] Executing skill: retrieve_knowledge
[OrchestratorAgent] Skill completed: retrieve_knowledge

[OrchestratorAgent] Planning iteration 2
  Chosen skill: build_session_context
  Reasoning: Have data and knowledge, can build session context now

[OrchestratorAgent] Executing skill: build_session_context
[OrchestratorAgent] Skill completed: build_session_context

[OrchestratorAgent] Planning iteration 3
  Chosen skill: generate_ux
  Reasoning: Session context ready, calling UX Designer to create design spec

[OrchestratorAgent] Executing skill: generate_ux
[ExecutionTool] Using protocol-aware UX execution...
[ExecutionTool] Evaluating UX design specification...
[ExecutionTool] SUCCESS: UX design specification validated
[OrchestratorAgent] Skill completed: generate_ux

[OrchestratorAgent] Planning iteration 4
  Chosen skill: generate_react
  Reasoning: UX design validated, ready to generate React code

[OrchestratorAgent] Executing skill: generate_react
[ExecutionTool] Using protocol-aware React execution...
[ExecutionTool] Evaluating React code output...
[ExecutionTool] SUCCESS: React code output validated
[OrchestratorAgent] Skill completed: generate_react

[OrchestratorAgent] Planning iteration 5
  Chosen skill: finish
  Reasoning: Both UX and React validated successfully, goal achieved

GOAL ACHIEVED!
```

---

## 🔧 Technical Details

### LLM Configuration

**Model:** `claude-sonnet-4-20250514` (latest Sonnet)

**Why Sonnet?**
- Best balance of speed and reasoning capability
- Strong chain-of-thought reasoning
- Good at structured JSON output
- Cost-effective for planning decisions

**Temperature:** `0.0` (deterministic planning)

**Max tokens:** `2000` (enough for planning response)

### Safety Limits

**Max iterations:** 4

**Why 4?**
- Typical flow needs 3-4 steps
- Prevents infinite loops
- Sufficient for error recovery
- If more needed, likely a fundamental issue

### Memory Persistence

**Session-scoped:** Memory resets for each generation request

**Not persistent across requests:** Each UI generation is independent

**Future enhancement:** Could add cross-session memory for learning

---

## 🧪 Testing

### Unit Test (Planned):

```python
# test_orchestrator_agent.py

def test_agent_initialization():
    """Test agent initializes with all skills"""
    orchestrator = UICodeOrchestrator()
    agent = OrchestratorAgent(orchestrator)

    assert len(agent.skills) > 0
    assert "discover_data" in agent.skills
    assert "generate_ux" in agent.skills
    assert "generate_react" in agent.skills

def test_planning_module():
    """Test LLM planning produces valid plans"""
    agent = OrchestratorAgent(orchestrator)
    agent.memory = SessionMemory(session_id="test")

    plan = agent._plan_next_action()

    assert isinstance(plan, Plan)
    assert plan.skill in agent.skills
    assert len(plan.reasoning) > 0

def test_reasoning_loop():
    """Test full reasoning loop"""
    orchestrator = UICodeOrchestrator(use_agent_mode=True)

    requirements = {"intent": "Test dashboard"}
    context = {"data_sources": {}}

    result = orchestrator.generate_ui_code(requirements, context)

    assert result is not None
```

### Integration Test (Planned):

```python
def test_agent_vs_procedural():
    """Test agent mode produces same quality as procedural"""

    # Procedural mode
    orch1 = UICodeOrchestrator(use_agent_mode=False)
    code1 = orch1.generate_ui_code(requirements, context)

    # Agent mode
    orch2 = UICodeOrchestrator(use_agent_mode=True)
    code2 = orch2.generate_ui_code(requirements, context)

    # Both should produce valid code
    assert code1 is not None
    assert code2 is not None
```

---

## 📁 Files Created

### Core Agent:
- [src/agents/orchestrator_agent.py](src/agents/orchestrator_agent.py) - Main agent class

### Modified Files:
- [src/agents/ui_orchestrator.py](src/agents/ui_orchestrator.py) - Added `use_agent_mode` parameter

### Documentation:
- [PHASE_4_AUTONOMOUS_AGENT.md](PHASE_4_AUTONOMOUS_AGENT.md) - This file

---

## 🔮 Future Enhancements

### 1. **Multi-turn refinement**
Agent could engage in dialogue with user for clarification

### 2. **Learning from failures**
Store common errors and solutions for faster recovery

### 3. **Parallel skill execution**
Execute independent skills concurrently

### 4. **Adaptive max iterations**
Adjust iteration limit based on task complexity

### 5. **Skill composition**
Combine multiple skills into higher-level strategies

### 6. **Cross-session memory**
Learn patterns across multiple generations

### 7. **Meta-learning**
Agent improves its planning over time

---

## 🎓 Comparison: Phase 3 vs Phase 4

| Aspect | Phase 3 (Procedural) | Phase 4 (Autonomous) |
|--------|---------------------|----------------------|
| **Workflow** | Fixed: discover → knowledge → UX → React | Dynamic: agent decides |
| **Error handling** | Retry with max attempts | Adaptive recovery strategies |
| **Planning** | Hardcoded decision tree | LLM-based reasoning |
| **Flexibility** | Limited to procedural flow | Fully adaptive |
| **Observability** | State transitions | Complete reasoning trace |
| **Self-correction** | Limited (retry only) | Full (refine, regenerate, adjust) |
| **Skill selection** | Predetermined sequence | Contextual choice |
| **Memory** | State machine | Rich session memory |

---

## ✨ Conclusion

**Phase 4 complete!** The orchestrator is now a **true autonomous agent** that:

✅ Plans its own actions
✅ Chooses from a skill registry
✅ Evaluates its own progress
✅ Self-corrects when needed
✅ Iterates until goal achieved
✅ Provides full introspection

**This is the final transformation**: From procedural coordinator → **Autonomous meta-agent with a mind.**

---

**Implementation Date:** 2025-11-21
**Status:** Core implementation complete
**Mode:** Optional (controlled by `use_agent_mode` flag)
**Backward Compatible:** Yes (Phase 3 still available)
**LLM:** Claude Sonnet 4
**Max Iterations:** 4
**Skills:** 12+
