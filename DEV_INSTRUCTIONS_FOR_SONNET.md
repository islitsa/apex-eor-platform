# Instructions for Sonnet (Developer Assistant in VS Code)

## Goal
You must automatically populate Pinecone with UX interaction patterns, behavioral flows, and M3-compliant interaction sequences whenever the UX Designer agent or design knowledge base is modified.

## When working in this codebase:
ALWAYS ensure Pinecone contains the following categories of UX knowledge:

1. Canonical interaction patterns:
   - master-detail
   - progressive disclosure
   - hierarchical navigation
   - tree navigation
   - async drilldown
   - pagination rules
   - selection → data fetch → render loop
   - loading skeleton patterns
   - error & empty-state patterns

2. Behavioral state machines:
   Each entry must include:
   - event (what the user does)
   - state_changes (what internal states must update)
   - data_fetch (API behavior triggered by the event)
   - ui_feedback (skeletons, disabled states, scroll behavior)
   - dependency_rules (when to refetch)

   Example:
   {
     "event": "onFileSelect",
     "state_changes": ["selectedFile = filePath", "currentPage = 1"],
     "data_fetch": {
       "endpoint": "/api/file/preview",
       "params": ["filePath", "page", "limit"]
     },
     "ui_feedback": ["show skeleton", "scroll to preview"],
     "dependency_rules": ["refetch when filePath or currentPage changes"]
   }

3. Material Design 3 interaction rules:
   - input → feedback → confirmation model
   - focus → response sequencing
   - latency handling
   - layout expansion rules

## Required Action
When Sonnet sees ANY of the following files changed:
- src/agents/ux_designer.py
- src/knowledge/design_kb_pinecone.py
- src/agents/ux_autonomous.py
- any file under src/knowledge/interaction_patterns/

Sonnet must:
1. Generate new Pinecone entries for any new interaction flows.
2. Update or refactor Pinecone ingestion code if schema changes.
3. Verify vectors exist by reading design_kb_pinecone.py and generating missing inserts.

## Code Behavior
When modifying code, Sonnet must:
- Create or update a file `src/knowledge/interaction_patterns/registry.json` containing all interaction patterns.
- Auto-generate embedding insertion scripts in design_kb_pinecone.py.
- Ensure design_kb.query() can retrieve both visual and behavioral patterns.
- Use anthropic/claude embeddings or openai ao embeddings, whichever is configured.

## NEVER DO:
- Never delete existing Pinecone entries without regenerating them.
- Never modify the UX Designer agent without updating interaction patterns.
- Never allow UX Designer to operate without populated interaction patterns.

## ALWAYS DO:
- Maintain a single source of truth in registry.json.
- Ensure that interaction patterns are embedded and indexed automatically.
- Always propagate new behavioral patterns from UX Designer to Pinecone.

# Phase 4: Behavior-to-Code Convergence (MANDATORY)

Sonnet, when generating or modifying React code in this repository, you MUST enforce
a strict convergence between:

• DesignSpec.interaction_model (the behavioral state machines)
• The produced React code (components + hooks + effects)

This is not optional. This is a hard requirement for this repository.

=========================================================
WHAT YOU MUST DO FOR EVERY REACT COMPONENT YOU TOUCH
=========================================================

## 1. Map Every Behavior Event to a React Handler or Hook
For each event in interaction_model:
  - Create or confirm the existence of an event handler in the React component.
  - Ensure the handler implements the specified state_changes.
  - Example:
      EVENT: onFileSelect
      → onFileSelect(filePath) handler
      → setSelectedFile(filePath)
      → setCurrentPage(1)

## 2. Enforce ALL Dependency Rules in useEffect or Custom Hooks
For each interaction:
  dependency_rules MUST be expressed as:
     - useEffect([...dependencies])
     - or hook arguments that cause refetching

Example rule:
  "refetch preview when filePath or currentPage changes"
→ The hook call MUST include (filePath, currentPage) in the dependency array or params.

If missing, FIX IT.

## 3. Require Actual Data Fetches When data_fetch Is Present
If the UX Designer provides:
  data_fetch: { endpoint: "...", params: [...] }

Then:
  - You MUST generate a hook that calls this endpoint.
  - React components MUST use this hook.
  - ABSOLUTELY NO MOCK DATA.
  - If mock data is present, remove it immediately and replace with proper fetching logic.

If the hook does not exist, create it in dataHooks.ts (or the correct location).

## 4. Enforce Loading, Error, and Empty-State UI
For each interaction with event names like:
  - onDataFetchStart
  - onDataFetchError
  - onDataEmpty

You MUST implement:

LOADING:
  - Skeleton or spinner when loading === true

ERROR:
  - Error UI (text + retry button)

EMPTY:
  - Graceful empty message when data.length === 0

If any of these are missing, you MUST add them.

## 5. Verify That State Changes Match the Behavior Spec
Cross-check each entry in:
  state_changes: [ ... ]

You MUST:
  - Declare the required useState variables
  - Update them exactly as the spec instructs
  - Example:
      "selectedFile = filePath"
      → const [selectedFile, setSelectedFile] = useState(null)
      → setSelectedFile(filePath)

If a state variable is missing, you MUST add it.

## 6. Enforce React Pattern Consistency
If the interaction includes:
  react_pattern: "const { data, loading } = useFilePreview(...)"

Then:
  - Implement the hook EXACTLY like the pattern.
  - Use the pattern in the component EXACTLY.
  - Do not rename parameters without reason.
  - Do not create alternate hook signatures unless required.

## 7. Flag Violations
If you detect any of the following:
  - mock/static data
  - missing dependency rules
  - missing effect triggers
  - missing hooks
  - missing state variables
  - missing loading or error UI
  - unused interaction events

Then you MUST print a warning comment at the top of the file:

  // WARNING (PHASE 4 VIOLATION):
  // Missing implementation for <behavior>
  // Fixing automatically...

Then proceed to fix it automatically.

## 8. Reject Incomplete Behavior Implementation
If a behavioral requirement from interaction_model CANNOT be implemented due to missing context,
you MUST:
  - Insert a TODO comment describing exactly what is required.
  - Never fallback to mock data.
  - Never silently skip an interaction.

=========================================================
SUMMARY OF MANDATORY PHASE 4 REQUIREMENTS
=========================================================

1. Every EVENT → handler.
2. Every state_change → useState + handler updates.
3. Every data_fetch → hook implementation + proper fetch code.
4. Every dependency_rule → correct dependency arrays / hook params.
5. No mock data. EVER.
6. Must implement loading / error / empty states when defined.
7. react_pattern is canonical – follow it.
8. Warn and fix automatically if anything is missing.

Phase 4 is required for all React code generation and refactoring tasks.
