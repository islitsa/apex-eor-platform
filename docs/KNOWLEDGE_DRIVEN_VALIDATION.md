# Knowledge-Driven Validation (Not Hardcoded!)

## The Problem You Identified

**Your observation:** "wait is this all hardcoded?"

**YES!** I was about to add hardcoded visual design validation:
- Hardcoded Material Design font sizes: `[11, 12, 14, 16, 22, 24...]`
- Hardcoded 8px grid assumption
- Hardcoded color limits: `if len(hardcoded_colors) > 5`
- Hardcoded font families: checking for "Roboto"

**This is wrong for the same reason the Gradio rules were wrong!**

---

## Why Hardcoding is Bad

### 1. **Duplication**
- Design knowledge already in Pinecone
- Validation rules hardcoded in Python
- Two sources of truth = maintenance nightmare

### 2. **Inflexibility**
- What if design system changes?
- What if user wants different design system (not Material Design)?
- What if new font sizes added to type scale?
- **Answer:** Have to change Python code every time!

### 3. **Inconsistency**
- UX Designer queries Pinecone for typography rules
- Gradio Developer validates against hardcoded rules
- They might not match!

---

## The Right Approach: Knowledge-Driven Validation

### Principle: Single Source of Truth

**All design rules live in Pinecone, validation queries them dynamically**

```
┌─────────────────────────────────────────┐
│ Pinecone Knowledge Base                 │
│                                         │
│  Typography:                            │
│   - Type scale: 11,12,14,16,22,24...   │
│   - Font family: Roboto, sans-serif     │
│   - Line height: 1.5                    │
│                                         │
│  Colors:                                │
│   - Primary: #6200EE                    │
│   - Surface: #FFFFFF                    │
│   - Token-based system                  │
│                                         │
│  Spacing:                               │
│   - Grid: 8px                           │
│   - Valid values: 4,8,16,24,32,40...   │
└─────────────────────────────────────────┘
           ↓                    ↓
    UX Designer          Gradio Developer
    queries for          queries for
    design rules         validation rules
           ↓                    ↓
    Designs with         Validates against
    type scale           type scale
```

---

## Implementation Approach

### Instead of Hardcoded Validation:

```python
# ❌ BAD: Hardcoded
valid_sizes = [11, 12, 14, 16, 22, 24, 28, 32, 36, 45, 57]
font_sizes = re.findall(r'font-size:\s*(\d+)px', code)
invalid_sizes = []
for size in font_sizes:
    if int(size) not in valid_sizes:
        invalid_sizes.append(size)
```

### Use Knowledge-Driven Validation:

```python
# ✅ GOOD: Query knowledge base
def _query_visual_design_rules(self) -> Dict:
    """Query design system rules from Pinecone"""
    rules = {}

    # Get typography rules
    typo_results = self.design_kb.query(
        "Material Design type scale font sizes",
        category="typography",
        top_k=1
    )
    if typo_results:
        rules['typography'] = typo_results[0]

    # Get color system rules
    color_results = self.design_kb.query(
        "Material Design color tokens palette",
        category="colors",
        top_k=1
    )
    if color_results:
        rules['colors'] = color_results[0]

    # Get spacing rules
    spacing_results = self.design_kb.query(
        "Material Design spacing 8px grid system",
        category="spacing",
        top_k=1
    )
    if spacing_results:
        rules['spacing'] = spacing_results[0]

    return rules

def _validate_visual_design(self, code: str, design_rules: Dict) -> List[str]:
    """Validate code against design rules from knowledge base"""
    violations = []

    # Extract what the knowledge base says about typography
    typo_rule = design_rules.get('typography', {})
    # Parse the rule content to extract valid font sizes
    # Then validate code against those values

    # Same for colors, spacing, etc.
    return violations
```

---

## Better Yet: Use Claude to Validate

Instead of regex + hardcoded logic, **ask Claude to validate based on design rules**:

```python
def _validate_visual_design_with_llm(self, code: str, design_rules: Dict) -> List[str]:
    """
    Use Claude to validate visual design against knowledge base rules
    """

    # Format design rules from knowledge base
    rules_text = self._format_design_rules(design_rules)

    prompt = f"""You are a design system validator.

DESIGN SYSTEM RULES (from knowledge base):
{rules_text}

CODE TO VALIDATE:
```python
{code[:2000]}
```

YOUR TASK: Identify visual design violations in the code.

Check for:
1. Font sizes not from the type scale
2. Colors not from the design tokens
3. Spacing not on the grid system
4. Font families not from the approved list
5. Contrast issues

OUTPUT FORMAT:
List each violation as:
- VIOLATION: [description]

If no violations found, output:
- NO VIOLATIONS
"""

    try:
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        response = message.content[0].text

        # Parse violations from response
        violations = []
        for line in response.split('\n'):
            if line.strip().startswith('- VIOLATION:'):
                violations.append(line.strip().replace('- VIOLATION: ', 'VISUAL VIOLATION: '))

        return violations

    except Exception as e:
        print(f"  [Validation] Error: {e}")
        return []
```

---

## Why This is Better

### 1. **Dynamic**
- Design system changes in Pinecone
- Validation automatically uses new rules
- No code changes needed

### 2. **Intelligent**
- Claude understands context
- Can detect subtle violations
- Not just pattern matching

### 3. **Single Source of Truth**
- UX Designer uses Pinecone rules
- Gradio Developer validates against same rules
- Guaranteed consistency

### 4. **Flexible**
- Works with any design system (not just Material Design)
- User can customize rules in Pinecone
- Validation adapts automatically

---

## Example Flow

### Generate Code with Knowledge-Driven Validation

```
1. UX Designer queries Pinecone:
   "Material Design type scale font sizes"
   → Gets: "11px, 12px, 14px, 16px, 22px, 24px..."

2. UX Designer creates spec:
   styling = {
       "typography": "Use type scale from knowledge base",
       "font_sizes": [11, 12, 14, 16, 22, 24, ...]  # From Pinecone
   }

3. Gradio Developer generates code:
   css = """
   .title { font-size: 24px; }  /* Uses type scale */
   .body { font-size: 18px; }   /* NOT in type scale! */
   """

4. Gradio Developer validates:
   - Queries SAME Pinecone rules
   - Finds font-size: 18px
   - Checks against type scale from Pinecone
   - Detects: "18px not in type scale [11,12,14,16,22,24...]"

5. Self-corrects:
   - Regenerates with violation context
   - Uses 16px instead (closest valid size)
```

---

## Current State vs Proposed State

### Current (After My Changes)

```python
# Gradio Developer - _validate_code()
# ❌ Hardcoded validation
if "@keyframes" in code:
    errors.append("Found @keyframes")  # Framework rule

# ❌ Would have added hardcoded visual validation
valid_sizes = [11, 12, 14, 16, ...]  # Hardcoded!
```

### Proposed (Knowledge-Driven)

```python
# Gradio Developer - _validate_code()
# ✅ Query framework rules from Pinecone
constraints = self._query_gradio_constraints()  # Already does this!

# ✅ Query design rules from Pinecone
design_rules = self._query_visual_design_rules()  # Add this!

# ✅ Validate code against queried rules
ux_violations = self._validate_visual_design_with_llm(code, design_rules)
```

---

## What to Implement

### Option 1: Simple (Regex + KB Query)
Query design rules from Pinecone, parse them, use regex to validate

**Pros:**
- Fast
- Deterministic

**Cons:**
- Still requires parsing logic
- Limited to pattern matching

### Option 2: Smart (LLM + KB Query)
Query design rules from Pinecone, ask Claude to validate

**Pros:**
- Understands context
- Can detect subtle issues
- No parsing logic needed

**Cons:**
- Slower (extra LLM call)
- Non-deterministic

### Recommended: Hybrid
- Use regex for obvious violations (syntax, presence checks)
- Use LLM for nuanced violations (visual design, semantics)

---

## Implementation Plan

### Step 1: Add Visual Design Rule Queries

```python
def _query_visual_design_rules(self) -> Dict:
    """Query visual design rules from knowledge base"""
    print("  [Gradio Developer] Querying visual design rules...")

    rules = {}

    # Typography
    typo_results = self.design_kb.query(
        "Material Design type scale font sizes",
        category="typography",
        top_k=1
    )
    if typo_results:
        rules['typography'] = typo_results[0]

    # Colors
    color_results = self.design_kb.query(
        "Material Design color tokens system",
        category="colors",
        top_k=1
    )
    if color_results:
        rules['colors'] = color_results[0]

    # Spacing
    spacing_results = self.design_kb.query(
        "Material Design 8px spacing grid",
        category="spacing",
        top_k=1
    )
    if spacing_results:
        rules['spacing'] = spacing_results[0]

    print(f"  [Gradio Developer] Retrieved {len(rules)} visual design rules")
    return rules
```

### Step 2: Add LLM-Based Visual Validation

```python
def _validate_visual_design(self, code: str, design_rules: Dict) -> List[str]:
    """Use Claude to validate visual design against design rules"""

    if not design_rules:
        print("    [Skill: Visual Design] SKIP - No design rules available")
        return []

    # Format rules for prompt
    rules_text = []
    for category, rule in design_rules.items():
        rules_text.append(f"{category.upper()}:")
        rules_text.append(f"  {rule.get('content', 'N/A')}")
    rules_formatted = "\n".join(rules_text)

    prompt = f"""Validate this code against design system rules.

DESIGN SYSTEM RULES:
{rules_formatted}

CODE TO VALIDATE:
```python
{code[:2000]}
```

Check for:
1. Font sizes not from approved type scale
2. Colors not using design tokens
3. Spacing not on grid system
4. Non-standard font families

List violations or "NO VIOLATIONS"
"""

    try:
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        response = message.content[0].text

        # Parse violations
        violations = []
        if "NO VIOLATIONS" not in response.upper():
            for line in response.split('\n'):
                if 'violation' in line.lower() or 'issue' in line.lower():
                    violations.append(f"VISUAL VIOLATION: {line.strip()}")

        if violations:
            print(f"    [Skill: Visual Design] FAIL - {len(violations)} violations")
        else:
            print("    [Skill: Visual Design] PASS")

        return violations

    except Exception as e:
        print(f"    [Skill: Visual Design] ERROR - {e}")
        return []
```

### Step 3: Integrate into Validation Flow

```python
def _validate_code(self, code: str) -> tuple:
    """Validate code with knowledge-driven checks"""

    # ... existing technical validation ...

    # ========================================
    # VISUAL DESIGN VALIDATION (KNOWLEDGE-DRIVEN)
    # ========================================

    # Query design rules from knowledge base
    design_rules = self._query_visual_design_rules()

    # Validate using LLM + design rules
    visual_violations = self._validate_visual_design(code, design_rules)

    # Add to overall violations
    ux_violations.extend(visual_violations)

    # ... rest of validation ...
```

---

## Summary

**Your question:** "wait is this all hardcoded?"

**Answer:** YES, and you caught it before I made the same mistake twice!

**The fix:**
1. ✅ Don't hardcode design rules
2. ✅ Query from Pinecone (single source of truth)
3. ✅ Use Claude to validate against queried rules
4. ✅ Same approach as UX Designer already uses

**Result:**
- Validation rules match design rules automatically
- Change design system in one place (Pinecone)
- Everything adapts dynamically
- No hardcoded magic numbers!

---

## Next Steps

1. Implement `_query_visual_design_rules()` method
2. Implement `_validate_visual_design()` method with LLM
3. Integrate into main validation flow
4. Test with actual generated code
5. Verify validation catches real visual issues

Want me to implement this knowledge-driven validation system?