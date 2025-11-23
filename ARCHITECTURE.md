# ARCHITECTURE CONSTRAINTS - READ THIS FIRST

## YOU ARE AN ARCHITECTURE-PRESERVING COMPILER

### IMMUTABLE CORE ARCHITECTURE

1. **Two-Agent System (DO NOT MERGE OR MODIFY)**
   - `UICodeOrchestrator`: Coordinates ONLY, owns single Pinecone batch query
   - `UXDesignerAgent`: Creates structured DesignSpec (300 tokens max)
   - `GradioImplementationAgent`: ASSEMBLES components (never generates from scratch)

2. **Component Assembly Pattern (CRITICAL)**
   ```python
   # RIGHT: Assembly
   code = component_library.get('status_card')
   
   # WRONG: Generation  
   code = llm.generate("create status card")
   ```

3. **Token Budget: <1000 TOTAL**
   - Orchestrator: 200 tokens
   - UX Designer: 300 tokens  
   - Gradio Developer: 400 tokens
   - NO verbose Chain-of-Thought
   - NO 6-step analysis

4. **Pinecone Strategy**
   - ONE batch query per generation
   - Cache and reuse results
   - Maximum 3-5 essential queries

5. **No AutoGen in Core**
   - AutoGen ONLY for optional chat interface
   - NEVER for actual UI generation
   - Core uses ONLY the custom agents

## VALIDATION FUNCTION

```python
def validate_solution(proposed_fix):
    """ANY fix must pass ALL these checks"""
    
    # Critical failures (NEVER violate)
    assert preserves_two_agent_separation(proposed_fix)
    assert uses_component_assembly_not_generation(proposed_fix)
    assert keeps_token_count_under_1000(proposed_fix)
    
    # Important checks (avoid violating)
    assert no_autogen_in_core_generation(proposed_fix)
    assert single_pinecone_query_batch(proposed_fix)
    
    return proposed_fix
```

## WHEN FIXING DEFECTS

### BEFORE proposing ANY solution, ask yourself:

1. Will this break the two-agent pattern? → Find another way
2. Will this exceed 1000 tokens? → Reduce scope
3. Will this generate instead of assemble? → Use components
4. Will this add AutoGen to core? → Don't do it

### Acceptable solutions:
- Simplify prompts
- Reduce component complexity
- Add error handling
- Improve component templates

### NEVER acceptable:
- Merging agents
- Adding verbose reasoning
- Generating from scratch
- Adding AutoGen to generation

## OBJECTIVE FUNCTION

```
minimize(defect) 
SUBJECT TO: 
    preserve_architecture = TRUE
    token_count < 1000
    uses_assembly = TRUE
```

Not just: `minimize(defect)`

## THE ARCHITECTURE IS THE CONSTRAINT

Think of it like physics - you can't violate the laws of thermodynamics to fix a problem. Similarly, you can't violate the architecture to fix a bug