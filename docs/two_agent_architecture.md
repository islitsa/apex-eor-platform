# Two-Agent Architecture: UX Designer + Gradio Developer

## Decision: Follow Opus's Recommendation

Opus analogy: "That's like you claiming to solve reservoir problems without knowing about permeability."

We're splitting into **two specialized agents** with clear boundaries:

## Architecture

```
User Request
     ↓
┌─────────────────────────────┐
│   UX Designer Agent         │  ← The Visionary (Tarkovsky)
│   "WHAT to build"           │
│                             │
│   Knowledge:                │
│   - User needs & patterns   │
│   - Material Design 3       │
│   - Navigation flows        │
│   - Accessibility           │
│   - Action patterns         │
│                             │
│   Output: Design Spec       │
│   {                         │
│     "component": "loading", │
│     "intent": "show work",  │
│     "pattern": "spinner",   │
│     "style": "M3 colors"    │
│   }                         │
└──────────┬──────────────────┘
           │
           │ Design Spec (intent + patterns)
           ↓
┌─────────────────────────────┐
│   Gradio Developer Agent    │  ← The Implementer (Camera Operator)
│   "HOW to build in Gradio"  │
│                             │
│   Knowledge:                │
│   - Gradio constraints      │
│   - Python/CSS integration  │
│   - gr.HTML limitations     │
│   - Event handling          │
│   - Framework gotchas       │
│                             │
│   Constraints Check:        │
│   - No @keyframes ❌        │
│   - Use unicode spinners ✅ │
│                             │
│   Output: Working Python    │
└─────────────────────────────┘
           ↓
     Working Gradio Code
```

## Why This Works (Opus's Insight)

### 1. Separation of Concerns
- **UX Agent** thinks: "User needs feedback during processing"
- **Gradio Agent** thinks: "Can't use @keyframes, use ⏳ instead"

Just like physics validators don't need to know SQL injection prevention!

### 2. Focused Knowledge Domains
- **UX Agent RAG**: Material Design, UX patterns, accessibility
- **Gradio Agent RAG**: Framework constraints, Python gotchas, gr.HTML limitations

Each agent is an expert in ONE thing.

### 3. Easy to Update
When we discover new Gradio gotcha:
- ✅ Update Gradio Agent's knowledge
- ❌ Don't contaminate UX Agent with framework hacks

### 4. Mirrors Existing Architecture
We already do this with RAG multi-agent validation!

## Implementation Plan

### Phase 1: Create UX Designer Agent
```python
class UXDesignerAgent:
    """
    The Visionary - designs WHAT to build

    - Queries UX patterns from Pinecone
    - Creates design specification
    - Focuses on user needs, not implementation
    """

    def design(self, requirements: Dict) -> DesignSpec:
        # Query UX patterns
        patterns = self.query_ux_patterns(requirements)

        # Create spec with intent
        return DesignSpec(
            components=[...],
            interactions=[...],
            patterns_to_use=[...],
            intent="Show loading state for pipeline execution"
        )
```

### Phase 2: Create Gradio Developer Agent
```python
class GradioImplementationAgent:
    """
    The Implementer - builds HOW within Gradio constraints

    - Queries Gradio constraints from Pinecone
    - Validates against framework limitations
    - Generates working Python code
    """

    def build(self, design_spec: DesignSpec) -> str:
        # Query framework constraints
        constraints = self.query_gradio_constraints()

        # Check design against constraints
        violations = self.check_constraints(design_spec, constraints)

        # Generate code with workarounds
        return self.generate_code(design_spec, constraints)
```

### Phase 3: Coordination Layer
```python
class UICodeOrchestrator:
    """Coordinates UX Designer + Gradio Developer"""

    def __init__(self):
        self.ux_designer = UXDesignerAgent()
        self.gradio_dev = GradioImplementationAgent()

    def generate(self, requirements: Dict) -> str:
        # Step 1: UX designs WHAT
        design_spec = self.ux_designer.design(requirements)

        # Step 2: Gradio implements HOW
        code = self.gradio_dev.build(design_spec)

        return code
```

## Message Format: Design Spec

```python
DesignSpec = {
    "screen_type": "dashboard",
    "intent": "Monitor petroleum data pipeline status",

    "components": [
        {
            "type": "loading_indicator",
            "intent": "Show pipeline is executing",
            "pattern": "spinner",
            "context": "Long-running operation (minutes)"
        },
        {
            "type": "navigation",
            "intent": "Drill down into data sources",
            "pattern": "master-detail",
            "levels": ["source", "dataset", "stage", "file"]
        }
    ],

    "interactions": [
        {
            "trigger": "button_click",
            "action": "navigate_to_detail",
            "pattern": "view_action"
        }
    ],

    "styling": {
        "design_system": "Material Design 3",
        "colors": "from_pinecone",
        "typography": "from_pinecone"
    }
}
```

## Benefits

### 1. Each Agent Has ONE Job
- UX Agent: Be a great designer
- Gradio Agent: Be a great implementer

### 2. Knowledge Doesn't Cross-Contaminate
- UX Agent never learns about `@keyframes` bugs
- Gradio Agent never makes UX decisions

### 3. Testable Independently
- Test UX Agent: Does it create good design specs?
- Test Gradio Agent: Does it handle all constraints?

### 4. Reusable Components
- UX Agent could work with React, Vue, etc.
- Gradio Agent is framework-specific

### 5. Future-Proof
When Gradio v5 comes with different constraints:
- ✅ Swap Gradio Agent
- ✅ Keep UX Agent unchanged

## Comparison to Current Architecture

### Before (One Agent Doing Everything)
```
UXCodeGenerator
├── Knows UX patterns ✅
├── Knows Material Design ✅
├── Generates Gradio code ✅
└── Knows Gradio constraints? ❌ (kept forgetting)
```

### After (Two Specialized Agents)
```
UXDesignerAgent          GradioImplementationAgent
├── Knows UX ✅          ├── Knows Gradio ✅
├── Design patterns ✅   ├── Constraints ✅
└── Pure intent ✅       └── Workarounds ✅
```

## Next Steps

1. ✅ Added Gradio constraints to Pinecone
2. ⏭️ Create `UXDesignerAgent` class
3. ⏭️ Create `GradioImplementationAgent` class
4. ⏭️ Create `UICodeOrchestrator` coordination layer
5. ⏭️ Migrate existing `UXCodeGenerator` logic to appropriate agents
6. ⏭️ Test with existing dashboard generation

## Opus's Key Insight

"This mirrors how you solved the washout problem - multiple specialized agents validating each other, not one agent trying to know everything."

**We already know this pattern works!** Apply it here.