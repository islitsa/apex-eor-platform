# Execution Flow: `python scripts/pipeline/run_ingestion.py --ui`

## Complete File-by-File Execution Trace

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Entry Point                                                         │
│ File: scripts/pipeline/run_ingestion.py                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Line 560: parser.add_argument('--ui', ...)                                  │
│ Line 593: if args.ui:                                                       │
│ Line 594:     pipeline.launch_ui()                                          │
│                                                                              │
│ ▼                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Launch UI Method                                                    │
│ File: scripts/pipeline/run_ingestion.py                                     │
│ Method: IngestionPipeline.launch_ui()                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Line 301: project_root = Path(__file__).parent.parent.parent               │
│ Line 303: streamlit_file = project_root / "src" / "ui" / "agent_studio.py" │
│ Line 307: subprocess.run([                                                  │
│               sys.executable, "-m", "streamlit", "run",                     │
│               str(streamlit_file), "--",                                    │
│               "--auto-start"                                                │
│           ])                                                                │
│                                                                              │
│ ▼ Launches new process                                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: Streamlit App Initialization                                        │
│ File: src/ui/agent_studio.py                                                │
│ Class: AgentStudio                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Line 41: from src.agents.ui_orchestrator import UICodeOrchestrator         │
│ Line 42: from src.utils.context_extractor import PipelineContextExtractor  │
│                                                                              │
│ Line 45: class AgentStudio:                                                 │
│ Line 48:     def __init__(self):                                            │
│ Line 49:         st.set_page_config(...)                                    │
│ Line 56-73:  Initialize session state                                       │
│                                                                              │
│ Line 764: if __name__ == "__main__":                                        │
│ Line 765:     studio = AgentStudio()                                        │
│ Line 766:     studio.run()                                                  │
│                                                                              │
│ ▼                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Auto-Start Detection                                                │
│ File: src/ui/agent_studio.py                                                │
│ Method: AgentStudio.run()                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Line 607: def run(self):                                                    │
│ Line 616:     with st.sidebar:                                              │
│ Line 631:         if '--auto-start' in sys.argv and st.session_state.context:│
│ Line 632:             self.generate_dashboard()                             │
│                                                                              │
│ ▼ User clicks "Generate Dashboard" OR auto-start triggers                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: Generate Dashboard Method                                           │
│ File: src/ui/agent_studio.py                                                │
│ Method: AgentStudio.generate_dashboard()                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Line 319: def generate_dashboard(self):                                     │
│                                                                              │
│ Line 324: if not st.session_state.orchestrator:                             │
│ Line 327:     use_hybrid = '--no-hybrid' not in sys.argv                    │
│                                                                              │
│ Line 329:     if use_hybrid:  # DEFAULT PATH (NEW!)                         │
│ Line 330:         orchestrator = HybridStudioWrapper(...)                   │
│ Line 334:         print("[Agent Studio] Using Hybrid Code Generator")       │
│                                                                              │
│ Line 335:     else:  # FALLBACK (if --no-hybrid flag)                       │
│ Line 336:         orchestrator = StudioOrchestrator(...)                    │
│ Line 340:         print("[Agent Studio] Using Standard Two-Agent System")   │
│                                                                              │
│ Line 342:     st.session_state.orchestrator = orchestrator                  │
│                                                                              │
│ Line 344: requirements = {                                                  │
│ Line 345:     'screen_type': 'dashboard_navigation',                        │
│ Line 346:     'intent': 'Navigate through data pipeline',                   │
│           }                                                                  │
│                                                                              │
│ Line 339: code = st.session_state.orchestrator.generate_ui_code(            │
│               requirements,                                                  │
│               st.session_state.context                                       │
│           )                                                                  │
│                                                                              │
│ ▼ Calls orchestrator (Hybrid by default)                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 6A: Hybrid Path (DEFAULT - 99.3% token savings)                        │
│ File: src/ui/agent_studio.py                                                │
│ Class: HybridStudioWrapper                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Line 700: class HybridStudioWrapper:                                        │
│                                                                              │
│ Line 711: def __init__(self, user_callback, agent_callback):                │
│ Line 712:     from src.agents.hybrid_code_generator import HybridCodeGenerator│
│ Line 714:     self.hybrid_generator = HybridCodeGenerator()                 │
│                                                                              │
│     ▼ Loads from: src/agents/hybrid_code_generator.py                       │
│     ├─────────────────────────────────────────────────────────────────────┐ │
│     │ File: src/agents/hybrid_code_generator.py                           │ │
│     │ Class: HybridCodeGenerator                                          │ │
│     │                                                                      │ │
│     │ Line 52: def __init__(self):                                        │ │
│     │ Line 54:     from src.templates.gradio_snippets import SnippetAssembler│
│     │ Line 57:     from src.agents.ui_orchestrator import UICodeOrchestrator│
│     │ Line 54:     self.snippet_assembler = SnippetAssembler()            │ │
│     │ Line 57:     self.orchestrator = UICodeOrchestrator()               │ │
│     │                                                                      │ │
│     │     ▼ Loads snippet library                                         │ │
│     │     ├───────────────────────────────────────────────────────────┐  │ │
│     │     │ File: src/templates/gradio_snippets.py                    │  │ │
│     │     │ Class: SnippetAssembler                                    │  │ │
│     │     │                                                            │  │ │
│     │     │ PATTERNS = {                                               │  │ │
│     │     │     "pipeline_navigation": """...""",  # 63k chars        │  │ │
│     │     │     "data_grid_with_filter": """...""",                   │  │ │
│     │     │     "master_detail_view": """..."""                       │  │ │
│     │     │ }                                                          │  │ │
│     │     │                                                            │  │ │
│     │     │ COMPONENTS = { ... }  # Pre-validated snippets             │  │ │
│     │     │ INTERACTIONS = { ... } # Event handler patterns            │  │ │
│     │     └───────────────────────────────────────────────────────────┘  │ │
│     │                                                                      │ │
│     │     ▼ Also loads two-agent system as fallback                       │ │
│     │     ├───────────────────────────────────────────────────────────┐  │ │
│     │     │ File: src/agents/ui_orchestrator.py                       │  │ │
│     │     │ Class: UICodeOrchestrator                                 │  │ │
│     │     │                                                            │  │ │
│     │     │ Line 38: def __init__(self):                              │  │ │
│     │     │ Line 39:     self.ux_designer = UXDesignerAgent()         │  │ │
│     │     │ Line 40:     self.gradio_developer = GradioImplementationAgent()│
│     │     │ Line 41:     self.design_kb = DesignKnowledgeBasePinecone()│  │ │
│     │     └───────────────────────────────────────────────────────────┘  │ │
│     └─────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│ Line 724: def generate_ui_code(self, requirements, context):                │
│ Line 736:     code = self.hybrid_generator.generate(requirements, context)  │
│                                                                              │
│     ▼ Back to: src/agents/hybrid_code_generator.py                          │
│     ├─────────────────────────────────────────────────────────────────────┐ │
│     │ File: src/agents/hybrid_code_generator.py                           │ │
│     │ Method: HybridCodeGenerator.generate()                              │ │
│     │                                                                      │ │
│     │ Line 80: def generate(self, requirements, context, force_llm=False):│ │
│     │                                                                      │ │
│     │ ═══════════════════════════════════════════════════════════════════ │ │
│     │ PHASE 0: PATTERN MATCHING                                           │ │
│     │ ═══════════════════════════════════════════════════════════════════ │ │
│     │                                                                      │ │
│     │ Line 96: pattern_id, tokens = self._match_pattern(requirements, ctx)│ │
│     │                                                                      │ │
│     │     ▼ Pattern matching (100 tokens via lightweight LLM)             │ │
│     │     ├───────────────────────────────────────────────────────────┐  │ │
│     │     │ Method: _match_pattern()                                  │  │ │
│     │     │                                                            │  │ │
│     │     │ Line 140: Check cache first (0 tokens if hit)             │  │ │
│     │     │ Line 163: Build lightweight prompt                        │  │ │
│     │     │ Line 178: self.client.messages.create(                    │  │ │
│     │     │               model="claude-sonnet-4-20250514",           │  │ │
│     │     │               max_tokens=50  # Just pattern ID!           │  │ │
│     │     │           )                                               │  │ │
│     │     │                                                            │  │ │
│     │     │ Returns: ("pipeline_navigation", 277 tokens)              │  │ │
│     │     └───────────────────────────────────────────────────────────┘  │ │
│     │                                                                      │ │
│     │ Line 98: if pattern_id:  # SNIPPET PATH                             │ │
│     │ Line 102:     code = self._assemble_from_snippet(pattern_id, ctx)   │ │
│     │                                                                      │ │
│     │     ▼ Snippet assembly (0 tokens - just string substitution!)       │ │
│     │     ├───────────────────────────────────────────────────────────┐  │ │
│     │     │ Method: _assemble_from_snippet()                          │  │ │
│     │     │                                                            │  │ │
│     │     │ Line 233: template = PATTERNS[pattern_id]                 │  │ │
│     │     │ Line 236: code = template.replace(                        │  │ │
│     │     │               '{pipeline_data}',                           │  │ │
│     │     │               json.dumps(data_sources)                     │  │ │
│     │     │           )                                                │  │ │
│     │     │                                                            │  │ │
│     │     │ Returns: 63,200 chars of validated Gradio code            │  │ │
│     │     └───────────────────────────────────────────────────────────┘  │ │
│     │                                                                      │ │
│     │ Line 105: is_valid, tokens = self._validate_snippet(code, reqs)     │ │
│     │                                                                      │ │
│     │     ▼ Validation (0 tokens - syntax check only)                     │ │
│     │     ├───────────────────────────────────────────────────────────┐  │ │
│     │     │ Method: _validate_snippet()                               │  │ │
│     │     │                                                            │  │ │
│     │     │ Line 254: compile(code, '<string>', 'exec')               │  │ │
│     │     │                                                            │  │ │
│     │     │ Returns: (True, 0)  # No LLM validation needed            │  │ │
│     │     └───────────────────────────────────────────────────────────┘  │ │
│     │                                                                      │ │
│     │ Line 107: if is_valid:                                              │ │
│     │ Line 108:     self.snippet_hits += 1                                │ │
│     │ Line 117:     return code  # DONE! 277 tokens total                 │ │
│     │                                                                      │ │
│     │ ═══════════════════════════════════════════════════════════════════ │ │
│     │ RESULT: 63,200 chars generated with 277 tokens                      │ │
│     │ ═══════════════════════════════════════════════════════════════════ │ │
│     └─────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│ Line 738: stats = self.hybrid_generator.get_stats()                         │
│ Line 744: msg = f"[Hybrid] Complete! Used {tokens} tokens (snippet hit!)"  │
│                                                                              │
│ Returns: 63,200 chars of working Gradio code                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 6B: LLM Fallback Path (Only if pattern match fails)                    │
│ File: src/agents/hybrid_code_generator.py                                   │
│ Method: HybridCodeGenerator.generate()                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Line 123: # PHASE 1: LLM Fallback                                           │
│ Line 129: code = self.orchestrator.generate_ui_code(requirements, context)  │
│                                                                              │
│     ▼ Calls: src/agents/ui_orchestrator.py                                  │
│     ├─────────────────────────────────────────────────────────────────────┐ │
│     │ File: src/agents/ui_orchestrator.py                                 │ │
│     │ Method: UICodeOrchestrator.generate_ui_code()                       │ │
│     │                                                                      │ │
│     │ ═══════════════════════════════════════════════════════════════════ │ │
│     │ PHASE 0: KNOWLEDGE RETRIEVAL                                        │ │
│     │ ═══════════════════════════════════════════════════════════════════ │ │
│     │                                                                      │ │
│     │ Line 192: knowledge = self._retrieve_all_knowledge()                │ │
│     │                                                                      │ │
│     │     ▼ Queries Pinecone once for all knowledge                       │ │
│     │     ├───────────────────────────────────────────────────────────┐  │ │
│     │     │ File: src/knowledge/design_kb_pinecone.py                 │  │ │
│     │     │ Class: DesignKnowledgeBasePinecone                        │  │ │
│     │     │                                                            │  │ │
│     │     │ Queries for:                                               │  │ │
│     │     │ - UX patterns (master-detail, progressive disclosure)     │  │ │
│     │     │ - Design principles (Material Design typography, colors)  │  │ │
│     │     │ - Gradio constraints (CSS limitations, gr.State)          │  │ │
│     │     │                                                            │  │ │
│     │     │ Returns: Dict with 6 knowledge items                      │  │ │
│     │     └───────────────────────────────────────────────────────────┘  │ │
│     │                                                                      │ │
│     │ ═══════════════════════════════════════════════════════════════════ │ │
│     │ PHASE 1: UX DESIGNER                                                │ │
│     │ ═══════════════════════════════════════════════════════════════════ │ │
│     │                                                                      │ │
│     │ Line 199: design_knowledge = {                                      │ │
│     │               'ux_patterns': knowledge['ux_patterns'],              │ │
│     │               'design_principles': knowledge['design_principles']   │ │
│     │           }                                                          │ │
│     │ Line 203: design_spec = self.ux_designer.design(reqs, design_knowledge)│
│     │                                                                      │ │
│     │     ▼ Calls: src/agents/ux_designer.py                              │ │
│     │     ├───────────────────────────────────────────────────────────┐  │ │
│     │     │ File: src/agents/ux_designer.py                           │  │ │
│     │     │ Class: UXDesignerAgent                                    │  │ │
│     │     │ Method: design()                                          │  │ │
│     │     │                                                            │  │ │
│     │     │ Line 160: def design(self, requirements, knowledge):      │  │ │
│     │     │ Line 172: ux_patterns = knowledge['ux_patterns']          │  │ │
│     │     │ Line 181: design_reasoning = self._design_with_cot(...)   │  │ │
│     │     │                                                            │  │ │
│     │     │     ▼ Chain of Thought reasoning                          │  │ │
│     │     │     API Call: claude-sonnet-4-20250514                    │  │ │
│     │     │     max_tokens: 2,048 (reduced from 3,072)                │  │ │
│     │     │     Prompt: "Think through UX decisions..."               │  │ │
│     │     │     Output: ~1,480 tokens (design reasoning)              │  │ │
│     │     │                                                            │  │ │
│     │     │ Line 184: design_spec = self._create_design_spec(...)     │  │ │
│     │     │                                                            │  │ │
│     │     │ Returns: DesignSpec object                                │  │ │
│     │     │          - screen_type                                    │  │ │
│     │     │          - components                                     │  │ │
│     │     │          - interactions                                   │  │ │
│     │     │          - patterns                                       │  │ │
│     │     └───────────────────────────────────────────────────────────┘  │ │
│     │                                                                      │ │
│     │ ═══════════════════════════════════════════════════════════════════ │ │
│     │ PHASE 2: GRADIO DEVELOPER                                           │ │
│     │ ═══════════════════════════════════════════════════════════════════ │ │
│     │                                                                      │ │
│     │ Line 217: enhanced_context['knowledge'] = {                         │ │
│     │               'gradio_constraints': knowledge['gradio_constraints'],│ │
│     │               'design_principles': knowledge['design_principles']   │ │
│     │           }                                                          │ │
│     │ Line 224: code = self.gradio_developer.build(design_spec, context)  │ │
│     │                                                                      │ │
│     │     ▼ Calls: src/agents/gradio_developer.py                         │ │
│     │     ├───────────────────────────────────────────────────────────┐  │ │
│     │     │ File: src/agents/gradio_developer.py                      │  │ │
│     │     │ Class: GradioImplementationAgent                          │  │ │
│     │     │ Method: build()                                           │  │ │
│     │     │                                                            │  │ │
│     │     │ Line 62: def build(self, design_spec, context):           │  │ │
│     │     │                                                            │  │ │
│     │     │ Step 1: Extract knowledge from context                    │  │ │
│     │     │ Line 73: knowledge = context.get('knowledge', {})         │  │ │
│     │     │ Line 76: constraints = knowledge['gradio_constraints']    │  │ │
│     │     │                                                            │  │ │
│     │     │ Step 2: Create implementation plan                        │  │ │
│     │     │ Line 85: impl_plan = self._plan_implementation(...)       │  │ │
│     │     │                                                            │  │ │
│     │     │     ▼ Planning API call                                   │  │ │
│     │     │     API Call: claude-sonnet-4-20250514                    │  │ │
│     │     │     max_tokens: 1,024 (reduced from 2,048)                │  │ │
│     │     │     Prompt: "Create implementation plan..."               │  │ │
│     │     │     Output: ~1,247 tokens                                 │  │ │
│     │     │                                                            │  │ │
│     │     │ Step 3: Generate Gradio code                              │  │ │
│     │     │ Line 88: code = self._generate_gradio_code(...)           │  │ │
│     │     │                                                            │  │ │
│     │     │     ▼ Code generation API call                            │  │ │
│     │     │     API Call: claude-sonnet-4-20250514                    │  │ │
│     │     │     max_tokens: 8,192 (reduced from 16,384)               │  │ │
│     │     │     Prompt includes:                                      │  │ │
│     │     │     - design_spec.to_summary() (200 tokens vs 2000!)     │  │ │
│     │     │     - Implementation plan                                 │  │ │
│     │     │     - Gradio constraints                                  │  │ │
│     │     │     - Memory context (last 2 versions)                    │  │ │
│     │     │     Output: ~6,601 tokens                                 │  │ │
│     │     │                                                            │  │ │
│     │     │ Step 4: Validate code                                     │  │ │
│     │     │ Line 91: validated_code, ux_issues = self._validate_code(...)│
│     │     │                                                            │  │ │
│     │     │     Tests:                                                 │  │ │
│     │     │     - Python syntax                                       │  │ │
│     │     │     - @keyframes check                                    │  │ │
│     │     │     - gr.State usage                                      │  │ │
│     │     │     - False affordance (buttons without handlers)         │  │ │
│     │     │     - Data navigation                                     │  │ │
│     │     │     - Progressive disclosure                              │  │ │
│     │     │     - Empty event handlers                                │  │ │
│     │     │                                                            │  │ │
│     │     │ Step 5: Self-correct if needed                            │  │ │
│     │     │ Line 94: if ux_issues:                                    │  │ │
│     │     │ Line 96:     code = self._self_correct_ux_issues(...)     │  │ │
│     │     │                                                            │  │ │
│     │     │     ▼ Self-correction API call (if triggered)             │  │ │
│     │     │     API Call: claude-sonnet-4-20250514                    │  │ │
│     │     │     max_tokens: 4,096 (reduced from 8,192)                │  │ │
│     │     │     Prompt: "Fix UX violations..."                        │  │ │
│     │     │                                                            │  │ │
│     │     │ Step 6: Add to memory                                     │  │ │
│     │     │ Line 103: self._add_to_memory(...)                        │  │ │
│     │     │                                                            │  │ │
│     │     │ Returns: ~12,741 chars of validated Gradio code           │  │ │
│     │     └───────────────────────────────────────────────────────────┘  │ │
│     │                                                                      │ │
│     │ ═══════════════════════════════════════════════════════════════════ │ │
│     │ TOKEN REPORTING                                                     │ │
│     │ ═══════════════════════════════════════════════════════════════════ │ │
│     │                                                                      │ │
│     │ Line 230: ux_tokens = self.ux_designer.total_tokens_used            │ │
│     │ Line 231: dev_tokens = self.gradio_developer.total_tokens_used      │ │
│     │ Line 232: total = ux_tokens + dev_tokens                            │ │
│     │                                                                      │ │
│     │ Line 237: print(f"UX Designer: {ux_tokens:,} tokens")               │ │
│     │ Line 238: print(f"Gradio Developer: {dev_tokens:,} tokens")         │ │
│     │ Line 239: print(f"TOTAL: {total:,} tokens")                         │ │
│     │                                                                      │ │
│     │ Returns: Generated code                                             │ │
│     │                                                                      │ │
│     │ ═══════════════════════════════════════════════════════════════════ │ │
│     │ RESULT: ~9,328 tokens for novel dashboards                          │ │
│     │ ═══════════════════════════════════════════════════════════════════ │ │
│     └─────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│ Line 143: return code                                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 7: Display Results                                                     │
│ File: src/ui/agent_studio.py                                                │
│ Method: AgentStudio.generate_dashboard() (continued)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Line 342: st.session_state.generated_code = code                            │
│ Line 345: with open(project_root / "generated_pipeline_dashboard.py", "w") as f:│
│ Line 346:     f.write(code)                                                 │
│                                                                              │
│ Line 349: self.add_user_message('system', f"Generated {len(code):,} chars") │
│                                                                              │
│ UI displays:                                                                 │
│ - Generated code in middle column                                           │
│ - Token usage stats                                                         │
│ - Download button                                                           │
│ - Preview button                                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Performance Summary

### Hybrid Path (Default - 99.3% savings)
```
PHASE 0: Pattern Matching
  └─ src/agents/hybrid_code_generator.py:_match_pattern()
     └─ API call: 277 tokens

PHASE 1: Snippet Assembly
  └─ src/templates/gradio_snippets.py:PATTERNS
     └─ String substitution: 0 tokens

PHASE 2: Validation
  └─ src/agents/hybrid_code_generator.py:_validate_snippet()
     └─ Syntax check: 0 tokens

TOTAL: 277 tokens, 63,200 chars generated
```

### LLM Fallback Path (78% savings)
```
PHASE 0: Knowledge Retrieval
  └─ src/agents/ui_orchestrator.py:_retrieve_all_knowledge()
     └─ Pinecone: 6 queries (0 LLM tokens)

PHASE 1: UX Designer
  └─ src/agents/ux_designer.py:design()
     └─ API call: 1,480 tokens

PHASE 2: Gradio Developer
  ├─ Planning: 1,247 tokens
  ├─ Code Gen: 6,601 tokens
  └─ Self-Correction: 0-4,096 tokens (if needed)

TOTAL: 9,328 tokens, 12,741 chars generated
```

## File Dependencies

```
scripts/pipeline/run_ingestion.py
  └─ src/ui/agent_studio.py
       ├─ src/agents/hybrid_code_generator.py (NEW - DEFAULT)
       │    ├─ src/templates/gradio_snippets.py (NEW - Snippet library)
       │    └─ src/agents/ui_orchestrator.py (Fallback)
       │         ├─ src/agents/ux_designer.py
       │         ├─ src/agents/gradio_developer.py
       │         └─ src/knowledge/design_kb_pinecone.py
       │
       └─ src/utils/context_extractor.py
```

## Command Line Options

```bash
# Use hybrid system (default - 99.3% savings)
python scripts/pipeline/run_ingestion.py --ui

# Use standard two-agent system (78% savings)
python scripts/pipeline/run_ingestion.py --ui --no-hybrid

# Auto-start generation
python scripts/pipeline/run_ingestion.py --ui --auto-start
```

---

**Current Default:** Hybrid system with snippet-first approach
**Token Usage:** 277 tokens for pipeline dashboards (99.3% savings vs 40,000 baseline)
**Fallback:** Full two-agent generation for novel dashboards (9,328 tokens)