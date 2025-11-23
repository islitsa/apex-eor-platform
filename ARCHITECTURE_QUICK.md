# QUICK ARCHITECTURE REFERENCE

## For Every Fix, Paste This First:

```
Read ARCHITECTURE.md before proposing any solution.
Preserve: two-agent system, component assembly, <1000 tokens
```

## Common Issues & CORRECT Fixes:

### ❌ Problem: "Truncated code"
#### WRONG: Add more tokens, generate more code
#### ✅ RIGHT: Simplify components, use assembly pattern

### ❌ Problem: "Missing feature"  
#### WRONG: Add AutoGen agent to handle it
#### ✅ RIGHT: Add to component library, assemble it

### ❌ Problem: "Agents not communicating"
#### WRONG: Merge agents or add AutoGen conversation
#### ✅ RIGHT: Pass structured DesignSpec between them

### ❌ Problem: "Need more context"
#### WRONG: Add verbose Chain-of-Thought
#### ✅ RIGHT: Single Pinecone batch query, cache results

### ❌ Problem: "Complex UI requirements"
#### WRONG: Generate complex code from scratch
#### ✅ RIGHT: Compose from smaller components

## The Mantra:
**"Assemble, don't generate. Structure, don't narrate. Constrain, don't expand."**

## Copy-Paste Templates:

### For Sonnet/Claude:
```
CONTEXT: Two-agent system with component assembly (<1000 tokens)
PROBLEM: [issue]
FIX: Must preserve architecture from ARCHITECTURE.md
```

### For Quick Fixes:
```
Fix [issue] using component assembly only. No generation. <1000 tokens.
```

### For Complex Issues:
```
Read ARCHITECTURE.md first.
Problem: [detailed issue]
Constraints: preserve two-agent, use assembly, stay under 1000 tokens
Find solution within constraints.
```
