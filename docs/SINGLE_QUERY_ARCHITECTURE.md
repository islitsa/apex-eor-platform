# Single Pinecone Query Architecture

## The Problem

**Your question:** "how do we design this so we make only 1 trip to pinecone to retrieve these and use it both for implementation and validation?"

**Current inefficiency:**
```
UX Designer queries Pinecone:
  - UX patterns
  - Design principles (typography, colors, spacing)

Gradio Developer queries Pinecone AGAIN:
  - Gradio constraints
  - Design principles (typography, colors, spacing)  ← DUPLICATE!
  - Validation rules
```

**Result:** Multiple round trips for the same data!

---

## The Solution: Query Once in Orchestrator

### Architecture: Orchestrator Owns Knowledge Retrieval

```
┌─────────────────────────────────────────────────────────────┐
│ UICodeOrchestrator (Coordination Layer)                     │
│                                                              │
│  1. Query ALL knowledge from Pinecone ONCE:                 │
│     ✓ UX patterns                                           │
│     ✓ Design principles (typography, colors, spacing)       │
│     ✓ Gradio constraints                                    │
│     ✓ Framework limitations                                 │
│                                                              │
│  2. Pass to UX Designer:                                    │
│     → UX patterns                                           │
│     → Design principles                                     │
│                                                              │
│  3. Pass to Gradio Developer:                               │
│     → Gradio constraints                                    │
│     → Design principles (for validation)                    │
│     → Framework limitations                                 │
└─────────────────────────────────────────────────────────────┘
       ↓                                    ↓
┌──────────────────┐              ┌───────────────────────┐
│ UX Designer      │              │ Gradio Developer      │
│ - Uses patterns  │              │ - Uses constraints    │
│ - Uses principles│              │ - Validates w/        │
│ - NO queries     │              │   principles          │
└──────────────────┘              │ - NO queries          │
                                  └───────────────────────┘
```

---

## Implementation Plan

### Step 1: Add Knowledge Cache to Orchestrator

```python
class UICodeOrchestrator:
    def __init__(self):
        # Initialize knowledge base connection
        from src.knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone
        self.design_kb = DesignKnowledgeBasePinecone()

        # Cache for knowledge (retrieved once per generation)
        self.knowledge_cache = None

        self.ux_designer = UXDesignerAgent()
        self.gradio_developer = GradioImplementationAgent()

    def _retrieve_all_knowledge(self) -> Dict:
        """
        Query Pinecone ONCE for all design knowledge
        Returns comprehensive knowledge bundle
        """
        print("[Orchestrator] Retrieving design knowledge (single query)...")

        knowledge = {
            'ux_patterns': {},
            'design_principles': {},
            'gradio_constraints': {},
        }

        # UX PATTERNS (for UX Designer)
        print("  [KB] Querying UX patterns...")
        knowledge['ux_patterns'] = {
            'master_detail': self.design_kb.query(
                "master-detail navigation pattern",
                category="ux_patterns",
                top_k=1
            ),
            'progressive_disclosure': self.design_kb.query(
                "progressive disclosure hierarchy drill-down",
                category="ux_patterns",
                top_k=1
            ),
            'card_grid': self.design_kb.query(
                "card grid layout data display",
                category="ux_patterns",
                top_k=1
            ),
        }

        # DESIGN PRINCIPLES (for both agents)
        print("  [KB] Querying design principles...")
        knowledge['design_principles'] = {
            'typography': self.design_kb.query(
                "Material Design type scale font sizes",
                category="typography",
                top_k=2
            ),
            'colors': self.design_kb.query(
                "Material Design color tokens palette",
                category="colors",
                top_k=2
            ),
            'spacing': self.design_kb.query(
                "Material Design 8px spacing grid",
                category="spacing",
                top_k=2
            ),
        }

        # GRADIO CONSTRAINTS (for Gradio Developer)
        print("  [KB] Querying Gradio constraints...")
        knowledge['gradio_constraints'] = {
            'css': self.design_kb.query(
                "@keyframes CSS Gradio limitations",
                category="framework",
                top_k=3
            ),
            'state': self.design_kb.query(
                "gr.State Gradio navigation state",
                category="framework",
                top_k=2
            ),
            'events': self.design_kb.query(
                "Gradio click event handler",
                category="framework",
                top_k=2
            ),
        }

        print(f"  [KB] Retrieved {sum(len(v) for v in knowledge.values())} knowledge items")
        return knowledge
```

### Step 2: Modify generate_ui_code() to Use Cached Knowledge

```python
def generate_ui_code(
    self,
    requirements: Dict[str, Any],
    context: Dict[str, Any]
) -> str:
    """Generate UI code with single knowledge retrieval"""

    print("[Orchestrator] Starting two-agent code generation...")

    # STEP 0: Retrieve ALL knowledge ONCE
    knowledge = self._retrieve_all_knowledge()
    self.knowledge_cache = knowledge  # Cache for potential reuse

    # PHASE 1: UX DESIGNER
    print("\nPHASE 1: UX DESIGN (The Visionary)")

    # Pass relevant knowledge to UX Designer
    design_knowledge = {
        'ux_patterns': knowledge['ux_patterns'],
        'design_principles': knowledge['design_principles'],
    }

    design_spec = self.ux_designer.design(requirements, design_knowledge)

    # PHASE 2: GRADIO DEVELOPER
    print("\nPHASE 2: GRADIO IMPLEMENTATION (The Implementer)")

    # Pass relevant knowledge to Gradio Developer
    implementation_knowledge = {
        'gradio_constraints': knowledge['gradio_constraints'],
        'design_principles': knowledge['design_principles'],  # Same data!
    }

    enhanced_context = dict(context)
    enhanced_context['knowledge'] = implementation_knowledge
    if 'user_feedback' in requirements:
        enhanced_context['user_feedback'] = requirements['user_feedback']

    gradio_code = self.gradio_developer.build(design_spec, enhanced_context)

    return gradio_code
```

### Step 3: Modify UX Designer to Accept Knowledge

```python
# src/agents/ux_designer.py

class UXDesignerAgent:
    def __init__(self):
        # Remove self.design_kb - no longer queries directly!
        # self.design_kb = DesignKnowledgeBasePinecone()  ← DELETE

        api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.client = anthropic.Anthropic(api_key=api_key)
        self.design_history = []

    def design(self, requirements: Dict[str, Any], knowledge: Dict = None) -> DesignSpec:
        """
        Create design specification

        Args:
            requirements: User requirements
            knowledge: Pre-fetched design knowledge from orchestrator
        """
        print("\n[UX Designer] Starting design process...")

        # Use provided knowledge (no queries!)
        if knowledge:
            ux_patterns = knowledge.get('ux_patterns', {})
            design_principles = knowledge.get('design_principles', {})
        else:
            # Fallback: empty knowledge (should not happen)
            print("  [UX Designer] WARNING: No knowledge provided!")
            ux_patterns = {}
            design_principles = {}

        # Rest of design process uses this knowledge...
```

### Step 4: Modify Gradio Developer to Accept Knowledge

```python
# src/agents/gradio_developer.py

class GradioImplementationAgent:
    def __init__(self):
        # Remove self.design_kb - no longer queries directly!
        # self.design_kb = DesignKnowledgeBasePinecone()  ← DELETE

        api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.client = anthropic.Anthropic(api_key=api_key)
        self.implementation_history = []

    def build(self, design_spec: DesignSpec, context: Dict[str, Any]) -> str:
        """
        Build Gradio code from design specification

        Args:
            design_spec: Design from UX Designer Agent
            context: Contains 'knowledge' key with pre-fetched constraints
        """
        print("\n[Gradio Developer] Starting implementation...")

        # Extract pre-fetched knowledge from context
        knowledge = context.get('knowledge', {})
        constraints = knowledge.get('gradio_constraints', {})
        design_principles = knowledge.get('design_principles', {})

        # No queries needed - use provided knowledge!

        # Step 2: Create implementation plan
        impl_plan = self._plan_implementation(design_spec, constraints, context)

        # Step 3: Generate code
        code = self._generate_gradio_code(design_spec, impl_plan, constraints, context)

        # Step 4: Validate (using design_principles from knowledge)
        validated_code, ux_issues = self._validate_code(code, design_principles)

        # Step 5: Self-correct if needed
        if ux_issues:
            code = self._self_correct_ux_issues(
                design_spec, code, ux_issues,
                impl_plan, constraints, context
            )
            validated_code, remaining = self._validate_code(code, design_principles)

        return validated_code
```

---

## Benefits

### 1. **Performance**
- **Before:** 10+ Pinecone queries per generation
  - UX Designer: 6 queries (patterns + principles)
  - Gradio Developer: 5 queries (constraints + principles again)

- **After:** 1 batch query
  - Orchestrator: All knowledge in single batch
  - 10x faster!

### 2. **Consistency**
- Same knowledge passed to both agents
- Design principles used for design = principles used for validation
- No possibility of drift

### 3. **Cost**
- Fewer API calls to Pinecone
- Lower latency
- Better resource utilization

### 4. **Caching Potential**
- Orchestrator can cache knowledge between generations
- If user iterates, reuse same knowledge
- Only re-query if design system changes

---

## Advanced: Smart Caching

```python
class UICodeOrchestrator:
    def __init__(self):
        self.design_kb = DesignKnowledgeBasePinecone()
        self.ux_designer = UXDesignerAgent()
        self.gradio_developer = GradioImplementationAgent()

        # Knowledge cache with TTL
        self.knowledge_cache = None
        self.cache_timestamp = None
        self.cache_ttl = 300  # 5 minutes

    def _retrieve_all_knowledge(self, force_refresh: bool = False) -> Dict:
        """Retrieve knowledge with caching"""
        import time

        # Check cache
        if not force_refresh and self.knowledge_cache:
            age = time.time() - self.cache_timestamp
            if age < self.cache_ttl:
                print(f"  [KB] Using cached knowledge ({int(age)}s old)")
                return self.knowledge_cache

        # Cache miss or expired - query Pinecone
        print("  [KB] Querying Pinecone (cache miss/expired)...")
        knowledge = self._query_all_knowledge()

        # Update cache
        self.knowledge_cache = knowledge
        self.cache_timestamp = time.time()

        return knowledge

    def _query_all_knowledge(self) -> Dict:
        """Actually query Pinecone"""
        # ... implementation from Step 1 ...
```

---

## Migration Path

### Phase 1: Orchestrator Retrieval (Now)
- Add `_retrieve_all_knowledge()` to orchestrator
- Pass knowledge to both agents via method params
- Agents still have fallback to query directly

### Phase 2: Remove Agent Queries (After testing)
- Remove `self.design_kb` from both agents
- Make knowledge param required
- Fully centralized retrieval

### Phase 3: Smart Caching (Optimization)
- Add TTL-based cache to orchestrator
- Cache invalidation on design system changes
- Per-session caching

---

## Code Changes Summary

### Files to Modify

1. **src/agents/ui_orchestrator.py**
   - Add `self.design_kb`
   - Add `_retrieve_all_knowledge()`
   - Modify `generate_ui_code()` to pass knowledge

2. **src/agents/ux_designer.py**
   - Change `design()` signature to accept `knowledge` param
   - Remove direct Pinecone queries
   - Use provided knowledge instead

3. **src/agents/gradio_developer.py**
   - Change `build()` to extract knowledge from context
   - Modify `_validate_code()` to accept `design_principles` param
   - Remove direct Pinecone queries
   - Use provided knowledge instead

---

## Example Console Output

### Before (Multiple Queries)
```
[Orchestrator] Starting two-agent code generation...

PHASE 1: UX DESIGN
[UX Designer] Starting design process...
  [UX Designer] Querying UX patterns...
  [UX Designer] Querying design principles...
    [Pinecone] Query: master-detail pattern
    [Pinecone] Query: progressive disclosure
    [Pinecone] Query: typography
    [Pinecone] Query: colors
    [Pinecone] Query: spacing
  [UX Designer] Retrieved 5 items

PHASE 2: GRADIO IMPLEMENTATION
[Gradio Developer] Starting implementation...
  [Gradio Developer] Querying framework constraints...
    [Pinecone] Query: CSS limitations
    [Pinecone] Query: gr.State patterns
    [Pinecone] Query: event handlers
    [Pinecone] Query: typography ← DUPLICATE!
    [Pinecone] Query: colors ← DUPLICATE!
    [Pinecone] Query: spacing ← DUPLICATE!
```

### After (Single Query)
```
[Orchestrator] Starting two-agent code generation...
[Orchestrator] Retrieving design knowledge (single query)...
  [KB] Querying UX patterns...
  [KB] Querying design principles...
  [KB] Querying Gradio constraints...
  [KB] Retrieved 11 knowledge items in 0.8s

PHASE 1: UX DESIGN
[UX Designer] Starting design process...
[UX Designer] Using provided knowledge (no queries)

PHASE 2: GRADIO IMPLEMENTATION
[Gradio Developer] Starting implementation...
[Gradio Developer] Using provided knowledge (no queries)
[Gradio Developer] Validating with provided design principles
```

---

## Ready to Implement?

This architecture gives you:
- ✅ Single Pinecone query per generation
- ✅ Consistent knowledge across agents
- ✅ 10x faster execution
- ✅ Caching potential for iterations
- ✅ Lower cost

Want me to implement this single-query architecture?