# Sonnet Guardrails - Make Sonnet Respect Your Architecture

## Quick Setup (2 minutes)

1. **Copy these files to your project root:**
   - `ARCHITECTURE.md` - The main constraints document
   - `ARCHITECTURE_QUICK.md` - Quick reference

2. **Copy the `.vscode` folder to your project:**
   - Contains `architecture.code-snippets` for quick insertion

3. **Test the snippets in VS Code:**
   - Open Claude/Sonnet chat
   - Type `arch` and hit Tab - full architecture context appears
   - Type `fix` and hit Tab - quick fix template appears

## How to Use with Sonnet

### For EVERY conversation, start with:
```
Read ARCHITECTURE.md first.

[Then describe your problem]
```

### Quick snippets (after setup):
- `arch` + Tab → Full architecture context
- `fix` + Tab → Quick fix with constraints  
- `comp` + Tab → Component assembly reminder
- `token` + Tab → Token budget check
- `valid` + Tab → Solution validation checklist

## The Core Constraints Sonnet Must Follow:

1. **Two-agent system** - Never merge agents
2. **Component assembly** - Never generate from scratch
3. **<1000 tokens total** - Stay within budget
4. **No AutoGen in core** - Only for optional chat
5. **Single Pinecone query** - Batch, don't repeat

## Example Conversation Starters:

### For a bug fix:
```
Read ARCHITECTURE.md first.

Problem: Gradio code is truncated
Fix must: Use component assembly, stay under 1000 tokens
```

### For new feature:
```
Read ARCHITECTURE.md first.

Add feature: Dark mode toggle
Constraint: Add to component library, don't generate new code
```

### For debugging:
```
Read ARCHITECTURE.md first.

Debug: Agents not communicating
Preserve: Two-agent separation, use DesignSpec for data passing
```

## If Sonnet Violates Architecture:

Tell it:
```
Your solution violates ARCHITECTURE.md constraints:
- [Specific violation]

Find alternative solution that preserves architecture.
```

## The Key Files:

### ARCHITECTURE.md
- Complete constraints
- Validation function
- Immutable rules

### ARCHITECTURE_QUICK.md  
- Common problems and CORRECT fixes
- Quick copy-paste templates
- The mantra: "Assemble, don't generate"

### .vscode/architecture.code-snippets
- VS Code snippets for quick insertion
- Type trigger + Tab to insert

## Remember:

Every time Sonnet tries to "help" by:
- Adding more tokens
- Generating from scratch
- Merging agents
- Adding AutoGen

Point back to ARCHITECTURE.md and say "Find solution within constraints."

This will save you HOURS of fixing broken architecture!
