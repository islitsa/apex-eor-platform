"""
React Implementation Agent - The Implementer (True Lovable Approach)

Responsibility: Implement HOW to build with React + TypeScript
- Generates production-ready React components
- Uses modern React patterns (hooks, functional components)
- Integrates Tailwind CSS + Material Symbols for styling
- True interactivity with working event handlers
- Framework-specific expert for React ecosystem

This agent generates actual working React code like Lovable does.
It takes design specs and implements them as React + TypeScript components.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
import sys
import anthropic
import os
import json
import re

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents.ux_designer import DesignSpec
from src.agents.context.protocol import SessionContext, ContextAware


# === Phase 5: Dataclasses for Autonomous Mode ===

@dataclass
class ReactEvaluationResult:
    """
    Structured evaluation result from React Agent.

    Phase 5: React agent evaluates its own work and determines next action.
    """
    satisfactory: bool
    issues: List[str] = field(default_factory=list)
    next_action: str = "finish"  # "fix_types", "fix_imports", "regenerate_component", "finish"
    type_errors: List[str] = field(default_factory=list)
    import_errors: List[str] = field(default_factory=list)
    conflicts_detected: List[Any] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class Plan:
    """
    Plan for next action in autonomous mode.

    Phase 5: LLM-backed planning for React implementation.
    """
    skill: str
    reasoning: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    expected_outcome: str = ""


@dataclass
class SkillOutput:
    """
    Structured output from skill execution.

    Phase 5 Refactoring: Skills return structured output instead of raw Dict.
    This enforces contracts, prevents hidden side effects, and enables proper error handling.
    """
    success: bool
    updated_files: Dict[str, str] = field(default_factory=dict)
    new_issues: List[str] = field(default_factory=list)
    requires_replan: bool = False
    message: str = ""
    error: str = ""


class ReactDeveloperAgent:
    """
    React Developer Agent - Generates production-ready React + TypeScript code

    ARCHITECTURE (Pure Lovable Approach):
    - Generates React functional components with hooks
    - Uses Tailwind CSS for styling (or Material UI if specified)
    - Material Symbols for icons
    - TypeScript for type safety
    - Working event handlers and state management
    - Component composition from primitives

    Token Budget: ~400-800 tokens (component + types + handlers)
    No pre-built patterns - generates fresh code based on design spec
    """

    def __init__(self, trace_collector=None, styling_framework="tailwind", use_autonomous_mode=False):
        """
        Initialize React Developer Agent

        Args:
            trace_collector: Optional trace collector for debugging
            styling_framework: "tailwind" or "mui" (Material UI)
            use_autonomous_mode: Enable Phase 5 autonomous mode with internal planning loop
        """
        # Initialize Claude API
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=api_key)

        self.styling_framework = styling_framework
        self.trace_collector = trace_collector

        # MEMORY: Track implementations across session
        self.implementation_history = []
        self.memory_enabled = True

        # Token tracking
        self.total_tokens_used = 0

        # Protocol: Context-aware execution
        self.ctx: Optional[SessionContext] = None

        # Phase 5: Autonomous mode flag
        self.use_autonomous_mode = use_autonomous_mode

        # Phase 5: Skill registry
        self.skills = {}
        if use_autonomous_mode:
            self._build_skill_registry()
            print("[React Developer Agent] Initialized in AUTONOMOUS mode with internal planning loop")
            print(f"  [React Agent] {len(self.skills)} skills registered")
        else:
            print(f"[React Developer Agent] Initialized - Styling: {styling_framework}")
            print("[React Developer] Using PURE LOVABLE APPROACH")
            print("[React Developer] Generating React + TypeScript components")

    def with_context(self, ctx: SessionContext) -> "ReactDeveloperAgent":
        """
        Inject context before execution (ContextAware protocol).

        Args:
            ctx: Session context with discovery, intent, execution settings

        Returns:
            Self for method chaining
        """
        self.ctx = ctx
        print(f"[React Developer] Context injected - Session: {ctx.session_id[:8]}...")
        print(f"  Discovered sources: {ctx.discovery.sources}")
        print(f"  Intent scope: {ctx.intent.scope}")
        return self

    def execute(self, shared_memory: Optional['SharedSessionMemory'] = None, design_spec: Optional['DesignSpec'] = None) -> Dict[str, Any]:
        """
        Execute with context (ContextAware protocol).

        Phase 5: Routes to autonomous mode if enabled, otherwise uses Phase 3.1 procedural mode.
        Phase 6.2: Accepts external shared_memory for orchestrator integration.

        Args:
            shared_memory: Optional SharedSessionMemory instance from orchestrator
            design_spec: Optional design spec (fallback if shared_memory.ux_spec not available)

        Returns:
            Generated files dict

        Raises:
            ValueError: If context not provided
        """
        if not self.ctx:
            raise ValueError(
                "Context not provided. Call with_context() first.\n"
                "Usage: agent.with_context(ctx).execute()"
            )

        # Phase 5: Route to autonomous mode if enabled
        if self.use_autonomous_mode:
            from src.agents.shared_memory import SharedSessionMemory

            print("\n[React Developer] Executing in AUTONOMOUS mode...")

            # Phase 6.2: Use orchestrator's shared_memory if provided
            if shared_memory is None:
                # Fallback: create local shared_memory for standalone use
                shared_memory = SharedSessionMemory(session_id=self.ctx.session_id)
                shared_memory.ux_spec = None  # Orchestrator will provide
                shared_memory.data_context = {
                    "sources": self.ctx.discovery.sources,
                    "record_counts": self.ctx.discovery.record_counts
                }
                shared_memory.knowledge = {}  # Orchestrator will provide

            # Store for use in skills
            self.current_shared_memory = shared_memory

            # Phase 6.2: Read ux_spec from shared_memory
            if shared_memory.ux_spec is None and design_spec:
                # Fallback: use provided design_spec
                shared_memory.ux_spec = design_spec

            # Check if we have a UX spec
            if shared_memory.ux_spec is None:
                self._report_conflict(
                    shared_memory,
                    conflict_type="missing_design",
                    description="No UX spec available in shared memory",
                    severity="high"
                )
                return {}

            # Run autonomous agent
            files = self.run(shared_memory, max_steps=3)

            # Phase 6.2: Write files to shared memory before returning
            if files and shared_memory:
                shared_memory.update_react_files(files, "Generated by React Developer")

            return files

        # Phase 3.1: Procedural mode (backward compatible)
        print("\n[React Developer] Executing with SessionContext (Phase 3.1 mode)...")

        # Phase 6.2: Read design_spec from shared_memory if available
        if shared_memory and shared_memory.ux_spec:
            print("[Phase 6.2] Using UX spec from shared memory")
            design_spec = shared_memory.ux_spec
        elif design_spec is None:
            # Build minimal design spec from context as fallback
            from src.agents.ux_designer import DesignSpec
            design_spec = DesignSpec(
                screen_type=self.ctx.intent.task_type.value,
                intent=self.ctx.intent.original_query,
                components=[],
                interactions=[],
                patterns=[],
                styling={},
                data_sources={
                    source: {"name": source, "row_count": count}
                    for source, count in self.ctx.discovery.record_counts.items()
                }
            )

        # Convert context to legacy dict format
        legacy_context = self._context_to_legacy_dict()

        # Call existing build method
        files = self.build(design_spec, legacy_context)

        # Phase 6.2: Write files to shared memory if provided
        if files and shared_memory:
            shared_memory.update_react_files(files, "Generated by React Developer")

        return files

    def _context_to_legacy_dict(self) -> Dict[str, Any]:
        """
        Convert SessionContext to legacy dict format for backward compatibility.

        Returns:
            Dict compatible with existing build() method
        """
        if not self.ctx:
            return {}

        return {
            "data_sources": {
                source: {
                    "name": source,
                    "row_count": self.ctx.discovery.record_counts.get(source, 0)
                }
                for source in self.ctx.discovery.sources
            },
            "user_prompt": self.ctx.intent.original_query,
            "scope": self.ctx.intent.scope,  # NEW: explicit scope filtering
            "data_context": {},  # Placeholder for real data
            "gradient_context": {}  # Placeholder for gradient hints
        }

    def _load_data_hooks_template(self) -> str:
        """
        Load the Phase 3A data hooks template.

        Returns:
            Content of dataHooks.tsx template, or empty string if not found
        """
        template_path = Path(__file__).parent.parent / "templates" / "data_hooks.tsx"
        if template_path.exists():
            return template_path.read_text()
        return ""  # Fallback if template not found

    def build(self, design_spec: DesignSpec, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Build React + TypeScript code from design spec

        Args:
            design_spec: Design from UX Designer Agent
            context: Additional context (data sources, etc.)

        Returns:
            Dictionary with generated files:
            {
                'App.tsx': '...',
                'types.ts': '...',
                'components/DataSourceCard.tsx': '...',
                'package.json': '...'
            }
        """
        print("\n[React Developer] Starting React component generation...")

        # Emit trace: Starting
        if self.trace_collector:
            intent = design_spec.intent if hasattr(design_spec, 'intent') else str(design_spec)
            self.trace_collector.trace_thinking(
                agent="React Developer",
                method="build",
                thought=f"🚀 Starting React + TypeScript implementation for: {intent}"
            )

        # Extract context
        # Phase 2: Prioritize data_sources from design_spec (discovered data)
        data_sources = getattr(design_spec, 'data_sources', {}) or context.get('data_sources', {})
        user_prompt = context.get('user_prompt', '')

        # PROTOCOL: Filter sources by scope (CRITICAL FIX for "wrong sources" bug)
        scope = context.get('scope', [])
        if self.ctx and self.ctx.intent.scope:
            # If context is injected, use its scope
            scope = self.ctx.intent.scope

        if scope:
            # Filter data_sources to only include items in scope
            original_count = len(data_sources)
            data_sources = {
                k: v for k, v in data_sources.items()
                if k in scope
            }
            filtered_count = len(data_sources)

            if original_count != filtered_count:
                print(f"  [Protocol] Filtered sources by scope: {original_count} → {filtered_count}")
                print(f"  [Protocol] Scope: {scope}")
                print(f"  [Protocol] Using sources: {list(data_sources.keys())}")

        # Phase 3A: Extract REAL DATA context from API (fetched by Orchestrator)
        data_context = context.get('data_context', {})

        # Phase 3B: Extract GRADIENT CONTEXT for domain-aware pattern boosting
        gradient_context = context.get('gradient_context', {})

        # Emit trace: Discovery
        if self.trace_collector:
            # Show REAL data if available
            if data_context.get('success'):
                pipelines = data_context.get('pipelines', [])
                summary = data_context.get('summary', {})
                self.trace_collector.trace_thinking(
                    agent="React Developer",
                    method="build",
                    thought=f"📊 REAL DATA from API: {len(pipelines)} pipelines, {summary.get('total_records', 0):,} records, {summary.get('total_size', '0 B')}"
                )
            else:
                sources_list = ', '.join(list(data_sources.keys())[:3])
                if len(data_sources) > 3:
                    sources_list += f" (+ {len(data_sources) - 3} more)"
                self.trace_collector.trace_thinking(
                    agent="React Developer",
                    method="build",
                    thought=f"📊 Analyzing {len(data_sources)} data sources: {sources_list}"
                )

        # Build prompt for LLM (with REAL DATA context AND GRADIENT hints!)
        prompt = self._create_react_prompt(design_spec, data_sources, user_prompt, data_context, gradient_context)

        # Emit trace: Reasoning
        if self.trace_collector:
            # Extract design details
            screen_type = getattr(design_spec, 'screen_type', 'unknown')
            components = getattr(design_spec, 'components', [])
            component_names = [c.get('name', 'Unknown') for c in components] if components else []

            # Calculate total records - handle both 'row_count' (from discovery) and 'records' (legacy)
            total_records = sum(
                ds.get('row_count', ds.get('records', 0))
                for ds in data_sources.values()
            )

            # Build source details for trace
            source_details = []
            for name, ds in list(data_sources.items())[:3]:
                count = ds.get('row_count', ds.get('records', 0))
                source_details.append(f"{name}({count:,})")
            if len(data_sources) > 3:
                source_details.append(f"+ {len(data_sources) - 3} more")

            reasoning = f"""Planning React component architecture:

DESIGN SPEC ANALYSIS:
- Screen Type: {screen_type}
- Components to Build: {len(component_names)} ({', '.join(component_names[:5])}{', ...' if len(component_names) > 5 else ''})
- Data Sources: {len(data_sources)} sources with {total_records:,} total records [{', '.join(source_details)}]

TECHNICAL APPROACH:
Styling Framework: {self.styling_framework}
- Using Tailwind CSS utility classes
- Material Design 3 elevation patterns
- Material Symbols for icons

Component Architecture:
- Lovable-style functional components with hooks
- TypeScript for type safety
- Proper state management with useState/useMemo
- Real interactivity with working event handlers

File Structure:
- App.tsx (main component)
- types.ts (TypeScript interfaces)
- components/ ({len(component_names)} reusable components)
- package.json (dependencies)
- Config files (tailwind, vite, postcss)

Estimated Output: {len(component_names) + 5}+ files
"""
            self.trace_collector.trace_reasoning(
                agent="React Developer",
                method="build",
                reasoning=reasoning
            )

        # Generate React code via Claude
        print("  [React Developer] Calling Claude API for React generation...")

        # Emit trace: Generation start
        if self.trace_collector:
            self.trace_collector.trace_thinking(
                agent="React Developer",
                method="build",
                thought="⚡ Calling Claude API to generate React components (model: claude-sonnet-4-5, max_tokens: 16000)"
            )

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=16000,  # Increased from 8000 to prevent truncation
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Track token usage
        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        self.total_tokens_used += tokens_used
        print(f"  [React Developer] Tokens used: {tokens_used} (Total: {self.total_tokens_used})")

        # Extract code from response
        generated_code = response.content[0].text

        # Parse into separate files
        files = self._parse_generated_files(generated_code)

        # Validate: no mock data allowed
        self._validate_no_mock_data(files)

        # Emit trace: Files parsed
        if self.trace_collector:
            files_summary = '\n'.join([f"  - {name}" for name in list(files.keys())[:10]])
            if len(files) > 10:
                files_summary += f"\n  ... and {len(files) - 10} more"

            self.trace_collector.trace_thinking(
                agent="React Developer",
                method="build",
                thought=f"📦 Generated {len(files)} React + TypeScript files:\n{files_summary}\n\nTokens used: {tokens_used:,} (input: {response.usage.input_tokens:,}, output: {response.usage.output_tokens:,})"
            )

        # Store in memory
        if self.memory_enabled:
            self.implementation_history.append({
                'design_spec': design_spec.to_compact(),
                'context': {
                    'data_sources_count': len(data_sources),
                    'user_prompt': user_prompt[:100]  # Truncate for storage
                },
                'files_generated': list(files.keys()),
                'tokens_used': tokens_used
            })

        print(f"  [React Developer] Generated {len(files)} files")

        # Emit trace: Complete
        if self.trace_collector:
            self.trace_collector.trace_thinking(
                agent="React Developer",
                method="build",
                thought=f"✅ React implementation complete! Generated {len(files)} files, total tokens: {self.total_tokens_used:,}"
            )

        return files

    def _create_react_prompt(self, design_spec: DesignSpec, data_sources: Dict, user_prompt: str, data_context: Dict = None, gradient_context: Dict = None) -> str:
        """
        Create prompt for React code generation

        Args:
            design_spec: Design specification from UX Agent
            data_sources: Data sources dictionary (legacy)
            user_prompt: Original user request
            data_context: REAL DATA from API (fetched by Orchestrator) - Phase 3A
            gradient_context: Domain-aware pattern boosting hints - Phase 3B
        """
        if data_context is None:
            data_context = {}
        if gradient_context is None:
            gradient_context = {}

        # Get styling imports based on framework
        if self.styling_framework == "tailwind":
            styling_setup = """
STYLING: Tailwind CSS
- Use Tailwind utility classes for all styling
- Follow Material Design 3 color system
- Use these Tailwind classes for M3 elevation:
  * elevation-1: shadow-sm
  * elevation-2: shadow-md
  * elevation-3: shadow-lg
"""
        else:  # mui
            styling_setup = """
STYLING: Material UI (MUI)
- Import components from @mui/material
- Use MUI's sx prop for custom styling
- Follow Material Design 3 principles
"""

        # Build data sources info
        # Phase 2: Handle discovered data format (row_count, columns, status, stages) and legacy format (type, records)
        sources_info_lines = []
        discovered_source_names = []  # Track discovered source names for filtering

        for name, info in list(data_sources.items()):  # Process ALL sources (RRC was being excluded!)
            discovered_source_names.append(name)  # Add to discovered list

            # Check if this is discovered data (has row_count) or legacy format (has records)
            if 'row_count' in info:
                # Discovered data format
                row_count = info.get('row_count', 0)
                num_cols = len(info.get('columns', []))
                status = info.get('status', 'unknown')
                stages = info.get('stages', [])  # Phase 2 fix: Include actual pipeline stages!

                # Format stage info: ['downloads', 'extracted', 'parsed'] -> "downloads → extracted → parsed"
                stage_str = ' → '.join(stages) if stages else 'no stages'

                # Phase 2 enhancement: Include folder structure and file counts
                files_by_stage = info.get('files_by_stage', {})
                structure_note = info.get('structure_note', '')

                file_counts = ', '.join([f"{stage}:{files_by_stage.get(stage, 0)} files"
                                        for stage in stages]) if files_by_stage else ''

                sources_info_lines.append(
                    f"- {name}: {row_count:,} records, {num_cols} columns, status: {status}, stages: {stage_str}"
                )
                if structure_note:
                    sources_info_lines.append(f"  Structure: {structure_note}")
                if file_counts:
                    sources_info_lines.append(f"  Files: {file_counts}")
            else:
                # Legacy format (backward compatibility)
                data_type = info.get('type', 'Unknown')
                records = info.get('records', 0)
                sources_info_lines.append(
                    f"- {name}: {data_type} ({records:,} records)"
                )
        sources_info = "\n".join(sources_info_lines)

        # Build discovered sources JSON for filtering
        import json
        discovered_sources_json = json.dumps(discovered_source_names)

        # TOKEN OPTIMIZATION: Use compressed implementation guidance instead of full reasoning
        # Full design_reasoning is ~1000 tokens, implementation_guidance is ~300-400 tokens (60-70% reduction)
        # Keeps: layout, components, styling, icons | Drops: UX philosophy, rationale
        if hasattr(design_spec, 'to_implementation_guidance'):
            design_summary = design_spec.to_implementation_guidance()
        elif hasattr(design_spec, 'to_summary'):
            design_summary = design_spec.to_summary()
        else:
            design_summary = str(design_spec.design_reasoning)[:500]

        # FIX: Extract exact component names from UX spec for naming enforcement
        required_components = []
        if hasattr(design_spec, 'components') and design_spec.components:
            required_components = [
                comp.get('name') if isinstance(comp, dict) else getattr(comp, 'name', None)
                for comp in design_spec.components
            ]
            # Filter out None values
            required_components = [name for name in required_components if name]

        # Build component naming enforcement section
        component_naming_section = ""
        if required_components:
            component_list = "\n".join([f"  - {name}" for name in required_components])
            component_naming_section = f"""

🎯 CRITICAL: EXACT COMPONENT NAMING REQUIREMENT

The UX specification defines {len(required_components)} components with EXACT names.
You MUST use these names EXACTLY as specified - do not rename or simplify them.

REQUIRED COMPONENT NAMES (use these EXACTLY):
{component_list}

NAMING RULES:
1. Use the EXACT name from the list above for each component
2. Convert spaces to PascalCase for file/component names (e.g., "Hero Metrics Card" → HeroMetricsCard)
3. Create component files as: components/HeroMetricsCard.tsx
4. Export component with PascalCase name: export default function HeroMetricsCard()
5. DO NOT invent alternative names like "DatasetCard" for "Dataset Accordion Card"
6. DO NOT simplify names like "DataTable" for "Data Table"

EXAMPLE:
UX Spec says: "Hero Metrics Card"
✅ CORRECT:
  - File: components/HeroMetricsCard.tsx
  - Component: export default function HeroMetricsCard()
  - Usage: <HeroMetricsCard pipeline={{pipeline}} />

❌ WRONG:
  - File: components/MetricsCard.tsx (simplified name)
  - Component: export default function MetricsWidget() (different name)
"""

        # Build REAL DATA context section
        real_data_section = ""
        if data_context.get('success'):
            pipelines = data_context.get('pipelines', [])
            summary = data_context.get('summary', {})

            real_data_section = f"""
🔥🔥🔥 ATTENTION: REAL DATA IS AVAILABLE FROM API! 🔥🔥🔥

The Orchestrator has ALREADY FETCHED real data from http://localhost:8000/api/pipelines:

REAL DATA SUMMARY:
- Total Pipelines: {len(pipelines)}
- Total Records: {summary.get('total_records', 0):,}
- Total Size: {summary.get('total_size', '0 B')}

REAL PIPELINES (first 3):"""

            for i, pipeline in enumerate(pipelines[:3], 1):
                stages_str = ', '.join([f"{s['name']}({s['status']})" for s in pipeline.get('stages', [])])
                real_data_section += f"""
{i}. {pipeline.get('display_name', pipeline.get('id'))}
   - ID: {pipeline['id']}
   - Status: {pipeline['status']}
   - Files: {pipeline['metrics']['file_count']}
   - Data Size: {pipeline['metrics']['data_size']}
   - Stages: {stages_str or 'none'}"""

            if len(pipelines) > 3:
                real_data_section += f"\n... and {len(pipelines) - 3} more pipelines"

            real_data_section += """

This data is REAL and CURRENT. Use usePipelines() hook to fetch it - NO EXCUSES for mock data!
"""
        else:
            error_msg = data_context.get('error', 'Unknown error')
            real_data_section = f"""
⚠️ WARNING: Could not fetch real data from API: {error_msg}

You MUST still use usePipelines() hook and handle the loading/error states properly.
DO NOT generate mock data as a fallback!
"""

        prompt = f"""You are a React + TypeScript expert generating production-ready code.

USER REQUEST:
{user_prompt}

DESIGN GUIDANCE:
{design_summary}
{component_naming_section}

DATA SOURCES (Discovered via Context Swimming):
{sources_info or "None"}

🎯 DISCOVERED SOURCES TO DISPLAY: {discovered_sources_json}

⚠️ CRITICAL FILTERING REQUIREMENT:
The discovery system identified specific data sources for this dashboard.
You MUST filter the API response to ONLY show these discovered sources: {discovered_sources_json}

DO NOT display all pipelines from the API - only the ones that match discovered sources!

{real_data_section}

PHASE 3A - REAL DATA FETCHING WITH DISCOVERY FILTERING:

🚨 CRITICAL RULE: ABSOLUTELY NEVER GENERATE MOCK DATA 🚨

Mock data in production dashboards is UNACCEPTABLE and considered a BUG. The backend API at http://localhost:8000 provides real data. You MUST use it.

❌ FORBIDDEN - DO NOT DO THIS:
```typescript
// ❌ MOCK DATA - This will cause production failures!
const MOCK_DATASETS = [
  {{ id: 'fracfocus', name: 'FracFocus', records: 45200000 }},  // FAKE DATA!
  {{ id: 'rrc', name: 'RRC', records: 18200000 }}  // FAKE DATA!
];
const [datasets, setDatasets] = useState(MOCK_DATASETS);  // WRONG!
```

✅ REQUIRED - DO THIS INSTEAD:
```typescript
// ✅ REAL DATA from backend API
import {{ useDataSources }} from './dataHooks.tsx';

function App() {{
  const {{ data: pipelines, loading, error }} = useDataSources();  // CORRECT!
  // ...
}}
```

The application MUST fetch real data from the backend API at http://localhost:8000, not use hardcoded values.

You have access to these data-fetching hooks (already included in dataHooks.tsx):

// FOR PIPELINE METADATA (pipeline stages, health, file structure):
```typescript
// Fetch pipeline metadata from /api/pipelines
const {{ data, loading, error }} = usePipelines();
```

{self._inject_actual_schema_for_prompt(data_context)}


⚠️ DEFENSIVE CODING REQUIREMENTS (CRITICAL FOR TYPE SAFETY):

API responses may contain unexpected types or null values. ALWAYS code defensively:

1. **Never assume field types** - API may return mixed types (strings, numbers, dates)
2. **Always coerce to expected types** when rendering - THIS IS MANDATORY:
   ```typescript
   // ✅ CORRECT - Safe type coercion:
   {{String(stage.status || 'unknown').replace(/_/g, ' ')}}         // String() before .replace()
   {{String(stageName || '').replace(/_/g, ' ')}}                   // String() before any string method
   {{String(pipeline.name || 'Unknown').toLowerCase()}}             // String() before .toLowerCase()
   {{Number(metric.value || 0).toFixed(2)}}                         // Number() before .toFixed()
   {{Number(sizeInGB || 0).toFixed(2)}} GB                          // Number() before .toFixed()
   {{Number(metric.value || 0).toLocaleString()}}                   // Number() before .toLocaleString()

   // ❌ WRONG - Assumes types without coercion (WILL CAUSE TypeErrors):
   {{stage.status.replace(/_/g, ' ')}}      // TypeError if status is a number or null!
   {{stageName.replace(/_/g, ' ')}}         // TypeError if stageName is undefined!
   {{sizeInGB.toFixed(2)}}                  // TypeError if sizeInGB is a string!
   {{metric.value.toLocaleString()}}        // TypeError if value is a string!
   ```

   RULE: Before calling ANY type-specific method:
   - `.replace()`, `.split()`, `.trim()`, `.toLowerCase()`, `.toUpperCase()` → Wrap in `String()`
   - `.toFixed()`, `.toPrecision()`, `.toLocaleString()` → Wrap in `Number()`

3. **Handle null/undefined gracefully**:
   ```typescript
   // ✅ CORRECT:
   {{pipeline.metrics?.file_count || 0}}
   {{pipeline.name ?? 'Unknown'}}

   // ❌ WRONG:
   {{pipeline.metrics.file_count}}  // TypeError if metrics is undefined
   ```

4. **For array operations, check existence first**:
   ```typescript
   // ✅ CORRECT:
   {{pipeline.stages?.map(stage => ...) ?? []}}

   // ❌ WRONG:
   {{pipeline.stages.map(stage => ...)}}  // TypeError if stages is undefined
   ```

CRITICAL: The stages array may contain metadata fields (dates, counts) mixed with actual stages.
Always use String() coercion when rendering stage.status to prevent TypeErrors.

🎯 DISCOVERY FILTERING - CRITICAL IMPLEMENTATION:

The discovery system found these specific sources: {discovered_sources_json}

*** CRITICAL SCHEMA RULE (Phase 1.6) ***

The usePipelines() hook returns:
  {{ data: PipelinesResponse, loading, error }}

Where PipelinesResponse is:
  {{ pipelines: Pipeline[], summary: {{...}} }}

Therefore you MUST access data.pipelines, NEVER data directly!

WRONG:  if (!data || !Array.isArray(data))
WRONG:  data.filter(...)
WRONG:  data.map(...)

CORRECT: if (!data?.pipelines || !Array.isArray(data.pipelines))
CORRECT: data.pipelines.filter(...)
CORRECT: data.pipelines.map(...)

Violating this rule causes: 0 records, 0 files, empty dashboard (filteredPipelines always returns [])

You MUST filter pipelines to only show discovered sources. Generate code like this:

```typescript
export default function App() {{
  const {{ data, loading, error }} = usePipelines();

  // CRITICAL: Filter to only discovered sources
  const DISCOVERED_SOURCES = {discovered_sources_json};

  const filteredPipelines = useMemo(() => {{
    if (!data?.pipelines || !Array.isArray(data.pipelines)) return [];  // CORRECT

    return data.pipelines.filter(pipeline => {{  // CORRECT
      // Match by pipeline ID or name against discovered sources
      return DISCOVERED_SOURCES.some(source =>
        pipeline.id.toLowerCase().includes(source.toLowerCase()) ||
        pipeline.name.toLowerCase().includes(source.toLowerCase())
      );
    }});
  }}, [data]);

  // Use filteredPipelines everywhere, NOT data.pipelines!
  const totalFiles = filteredPipelines.reduce((sum, p) => sum + (p.metrics?.file_count || 0), 0);

  return (
    <div>
      <h1>{{DISCOVERED_SOURCES.length}} Data Sources</h1>
      <p>{{totalFiles}} Total Files</p>
      {{filteredPipelines.map(pipeline => (
        <PipelineCard key={{pipeline.id}} pipeline={{pipeline}} />
      ))}}
    </div>
  );
}}
```

⚠️ KEY POINTS:
1. Define DISCOVERED_SOURCES constant with the exact list: {discovered_sources_json}
2. Create filteredPipelines using .filter() on data.pipelines
3. Use filteredPipelines everywhere in the component, NOT data.pipelines
4. The filter checks if pipeline ID/name contains any discovered source name
5. Calculate totals (file counts, sizes) from filteredPipelines only

❌ DO NOT generate code that uses data.pipelines directly - always filter first!

*** 🚨 CRITICAL: FILE EXPLORER COMPONENTS - MANDATORY SCHEMA NORMALIZATION 🚨 ***

⚠️ THE API RETURNS FILES IN TWO DIFFERENT FORMATS - YOU MUST HANDLE BOTH!

Format 1 (Current API): {{ type: "folder", children: [...] }}
Format 2 (Backend):     {{ type: "directory", subdirs: {{}}, files: [...] }}

🔧 MANDATORY FOR ALL FileExplorer/FileBrowser/FileTree COMPONENTS:

STEP 1: Define FileNode interface with ALL three fields:
```typescript
export interface FileNode {{
  name: string;
  path: string;
  type: 'file' | 'directory' | 'folder';
  subdirs?: Record<string, FileNode>;  // Backend format
  files?: FileNode[];                   // Backend format
  children?: FileNode[];                // API format (or normalized)
  size?: number;
  file_count?: number;
}}
```

STEP 2: Include this normalizeNode function (COPY EXACTLY):
```typescript
const normalizeNode = (node: any): FileNode => {{
  let children: FileNode[] = [];

  if (node.children && Array.isArray(node.children)) {{
    children = node.children.map((child: any) => normalizeNode(child));
  }} else {{
    if (node.subdirs && typeof node.subdirs === 'object') {{
      Object.values(node.subdirs).forEach((subdir: any) => {{
        children.push(normalizeNode(subdir));
      }});
    }}
    if (node.files && Array.isArray(node.files)) {{
      node.files.forEach((file: any) => {{
        children.push({{
          ...file,
          type: file.type || 'file',
          path: file.path || `${{node.path}}/${{file.name}}`,
          children: [],
        }});
      }});
    }}
  }}

  const normalizedType = node.type === 'folder' ? 'directory' : (node.type || 'directory');

  return {{
    name: node.name,
    path: node.path,
    type: normalizedType as 'file' | 'directory',
    children,
    file_count: node.file_count,
    size: node.size_bytes || node.size,
  }};
}};
```

STEP 3: Use normalization BEFORE rendering:
```typescript
const normalizedFiles = pipeline.files.map(node => normalizeNode(node));
return <div>{{normalizedFiles.map(node => renderNode(node))}}</div>;
```

⚠️ FAILURE TO INCLUDE normalizeNode() WILL CAUSE NON-EXPANDABLE FOLDERS!

✅ CORRECT pattern for FileExplorerTree:
```typescript
export default function FileExplorerTree({{ pipeline }}: Props) {{
  const normalizeNode = (node: any): FileNode => {{ /* ... copy from above ... */ }};

  const normalizedFiles = pipeline.files.map(node => normalizeNode(node));

  return (
    <div>
      {{normalizedFiles.map(node => renderNode(node, 0))}}
    </div>
  );
}}
```

❌ WRONG - Using pipeline.files directly WITHOUT normalization:
```typescript
// ❌ This will NOT work - folders won't expand!
{{pipeline.files.map(file => renderNode(file))}}  // Missing normalizeNode!
```

⚠️ NOTE: Pipeline objects use `pipeline.files` and `pipeline.stages`, NOT `pipeline.children`.
The `children` field is ONLY for FileNode objects AFTER normalization.
```

// FOR DATA SOURCE RECORDS (fracfocus chemical data, etc.):

```typescript
import {{ useDataSources, useDataSourceInfo, useDataSource, useDataQuery }} from './dataHooks.tsx';

// List all sources
const {{ sources, loading, error }} = useDataSources();

// Get source metadata
const {{ info, loading, error }} = useDataSourceInfo('fracfocus');

// Fetch data with pagination
const {{ data, total, loading, error }} = useDataSource('fracfocus', {{ limit: 1000 }});

// Advanced queries with filters
const {{ data, total, loading, error }} = useDataQuery({{
  source: 'fracfocus',
  columns: ['Well', 'Chemical'],
  filters: {{ State: 'TX' }},
  limit: 100
}});
```

CRITICAL RULES FOR DATA FETCHING:
1. ❌ NEVER hardcode data arrays like `const data = [...]`
2. ✅ ALWAYS use hooks to fetch data: `const {{ data, loading }} = useDataSource('fracfocus')`
3. ✅ ALWAYS handle loading states: `if (loading) return <div>Loading...</div>`
4. ✅ ALWAYS handle errors: `if (error) return <div>Error: {{error}}</div>`
5. ✅ Use the EXACT source names from DATA SOURCES section (e.g., 'fracfocus', 'rrc')
6. ✅ Display the `total` count from the hook response (e.g., "{{total:,}} total records")

Example of CORRECT data fetching:
```typescript
import {{ useDataSource }} from './dataHooks.tsx';

export default function Dashboard() {{
  const {{ data, total, loading, error }} = useDataSource('fracfocus', {{
    limit: 100
  }});

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {{error}}</div>;

  return (
    <div>
      <h1>FracFocus Data ({{total:,}} total records)</h1>
      {{data.map((row, i) => (
        <div key={{i}}>{{JSON.stringify(row)}}</div>
      ))}}
    </div>
  );
}}
```

Example of WRONG (hardcoded) data - DO NOT DO THIS:
```typescript
// ❌ DON'T DO THIS!
const data = [
  {{ source: 'fracfocus', records: 239059 }}  // Hardcoded
];
```

CRITICAL - USE ACTUAL DATA:
- The DATA SOURCES section above contains REAL metadata from the repository
- Use the EXACT row counts shown (e.g., "239,059 records" not "0 records")
- Use the EXACT status values shown (e.g., "complete" not generic statuses)
- Use the EXACT stage names shown (e.g., "downloads → extracted → parsed" NOT "Download → Transform → Validate")
- Display these actual values in the UI, not placeholder/mock data
- When showing pipeline stages, use the stage names EXACTLY as provided (downloads, extracted, parsed)
- Do NOT rename stages to generic names like "Download", "Transform", "Code", "Validate", etc.

FOLDER STRUCTURE (IMPORTANT):
- The repository uses a NESTED structure: {{source}}/{{data_type}}/{{stage}}
- Example: fracfocus/Chemical_data/downloads/, fracfocus/Chemical_data/parsed/
- When showing file paths, use the nested structure with data type folders
- Do NOT use flat paths like fracfocus/downloads/ - they are incorrect
- Check the "Structure:" line for each source to understand the nesting pattern

{self._build_gradient_hints(gradient_context)}

{styling_setup}

⚠️ CRITICAL - DEFENSIVE TYPE COERCION:

API responses may contain mixed types (strings, numbers, dates). ALWAYS use type coercion when rendering dynamic data:

✅ CORRECT - Safe type coercion:
```typescript
// String coercion for string methods
{{String(stage.status || 'unknown').replace(/_/g, ' ')}}

// Number coercion for numeric operations
{{Number(metric.value || 0).toLocaleString()}}

// Null-safe rendering
{{pipeline?.name ?? 'Unknown'}}
{{pipeline.stages?.length ?? 0}}
```

❌ WRONG - Assumes types (causes TypeError):
```typescript
// TypeError if status is a number or date!
{{stage.status.replace(/_/g, ' ')}}

// TypeError if value is not a number!
{{metric.value.toFixed(2)}}
```

**Why this matters:**
- The `stages` array may contain metadata fields (dates, file counts) as objects
- API responses may include computed fields with different types
- Without String() coercion, `.replace()` will fail on non-string values
- Without Number() coercion, numeric methods will fail on string values

**Required coercions:**
- `String(value)` before: `.replace()`, `.split()`, `.toLowerCase()`, `.substring()`, template literals
- `Number(value)` before: `.toFixed()`, `.toLocaleString()`, math operations
- `Array.from(value ?? [])` before: `.map()`, `.filter()`, `.length` on possibly-undefined arrays

TECHNICAL REQUIREMENTS:

1. **Component Structure:**
   - Generate React 18+ functional components
   - Use TypeScript for all files
   - Use hooks (useState, useEffect, useMemo, useCallback)
   - Compose small, reusable components
   - ⚠️ **MANDATORY**: FileExplorer/FileBrowser/FileTree components MUST include normalizeNode() function (see schema normalization section above)

2. **File Organization:**
   Generate these files (use comments to separate):
   ```
   // === FILE: App.tsx ===
   // === FILE: types.ts ===
   // === FILE: components/DataSourceCard.tsx ===
   // === FILE: package.json ===
   // === FILE: README.md ===
   ```

3. **Icons:**
   - Use Material Symbols Rounded font
   - REQUIRED: Add this link to index.html: <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
   - REQUIRED: Add this CSS class definition to index.css IMMEDIATELY after @tailwind directives:
     ```css
     .material-symbols-rounded {{{{
       font-family: 'Material Symbols Rounded';
       font-weight: normal;
       font-style: normal;
       font-size: 24px;
       line-height: 1;
       letter-spacing: normal;
       text-transform: none;
       display: inline-block;
       white-space: nowrap;
       word-wrap: normal;
       direction: ltr;
       -webkit-font-smoothing: antialiased;
       -moz-osx-font-smoothing: grayscale;
       font-feature-settings: 'liga';
     }}}}
     ```
   - Use icons like: <span className="material-symbols-rounded">delete</span>

4. **Interactivity:**
   - All onClick handlers must work
   - Proper state management with useState
   - Type-safe event handlers
   - Real-time updates when user interacts

5. **Code Quality:**
   - Total code: 400-800 lines across all files
   - Helper functions for repeated logic
   - TypeScript interfaces for all data types
   - Proper prop types and return types
   - No duplication - use .map() for lists
   - **CRITICAL**: All import statements MUST include file extensions (.tsx, .ts, .jsx, .js)
     Example: `import {{ MyComponent }} from './components/MyComponent.tsx'`
     Example: `import {{ MyType }} from './types.ts'`
     This is required for Vite + TypeScript with allowImportingTsExtensions

6. **Material Design 3:**
   - Follow M3 color system
   - Use elevation (shadows) appropriately
   - Rounded corners (8px-16px)
   - Proper spacing and padding

ANTI-PATTERNS (DO NOT DO):
❌ Class components
❌ Inline styles everywhere (use Tailwind or MUI)
❌ Repeated component code (use .map())
❌ Missing TypeScript types
❌ Non-working event handlers

*** CRITICAL: STRICT CANONICAL SCHEMA (DO NOT DEVIATE) ***

interface Pipeline {{
  id: string;
  name: string;
  display_name: string;
  status: string;
  metrics: {{
    file_count: number;       // ✅ CORRECT field name
    record_count: number;     // ✅ CORRECT field name (NOT total_records!)
    data_size: string;
  }};
  stages: {{ name: string; status: string }}[];
  files: any;
}}

interface DataContext {{
  summary: {{
    total_files: number;
    total_records: number;
    total_size_mb: number;
  }};
  pipelines: Pipeline[];
}}

CRITICAL CONSTRAINTS - THESE CAUSE "0 RECORDS" BUGS:
❌ NEVER use pipeline.metrics.total_records (DOES NOT EXIST!)
❌ NEVER use pipeline.metrics.records (DOES NOT EXIST!)
❌ NEVER use pipeline.total_files (DOES NOT EXIST!)
❌ NEVER use pipeline.total_records (DOES NOT EXIST!)
❌ NEVER use pipeline.fileCount or pipeline.recordCount (DOES NOT EXIST!)
❌ NEVER use pipeline.filesCount or pipeline.recordsCount (DOES NOT EXIST!)
❌ NEVER use pipeline.children (DOES NOT EXIST!)
❌ NEVER use pipeline.subdirectories or pipeline.tree (DOES NOT EXIST!)

✅ ALWAYS use pipeline.metrics.file_count (correct!)
✅ ALWAYS use pipeline.metrics.record_count (correct!)
✅ ALWAYS use pipeline.metrics.data_size (correct!)
✅ ALWAYS use pipeline.stages for stage info (correct!)
✅ ALWAYS use pipeline.files for file structure (correct!)

FORBIDDEN OPERATIONS:
❌ DO NOT invent fields not in the canonical schema above
❌ DO NOT create onClick handlers for modifying data (data is READ-ONLY)
❌ DO NOT build file tree navigation from scratch
❌ DO NOT reference nested.field.paths not explicitly in schema

REQUIRED RULES:
✅ FileExplorer/FileBrowser components are READ-ONLY displays
✅ Only use fields explicitly defined in canonical schema above
✅ Use defensive access with optional chaining: data?.field
✅ Check schema carefully before using any field name

Violating these rules causes: "0 records", "0 files", "Unknown", empty dashboards.
If a component needs data not in the schema, SKIP that component entirely.
Better to omit a feature than hallucinate non-existent fields.

Generate complete, working React + TypeScript code that can be immediately run with `npm install && npm start`.

OUTPUT FORMAT - CRITICAL:
- Separate EVERY file (TypeScript, CSS, JSON, etc.) with: // === FILE: filename.ext ===
- Use // (double slash) for ALL file types, even CSS files
- Do NOT use /* */ style comments for file markers
- Do NOT use markdown code fences (```) around file content
- Do NOT wrap files in ```typescript, ```json, or ```css blocks
- Output raw file content directly after the marker

✅ CORRECT Examples:
// === FILE: App.tsx ===
import React from 'react';
...

// === FILE: index.css ===
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Material Symbols Icons */
.material-symbols-rounded {{
  font-family: 'Material Symbols Rounded';
  font-weight: normal;
  font-style: normal;
  font-size: 24px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-smoothing: antialiased;
  font-feature-settings: 'liga';
}}

body {{
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', ...
}}

// === FILE: package.json ===
{{
  "name": "dashboard"
}}

❌ WRONG - Never do this:
/* === FILE: index.css === */   ← NO! Use // not /* */
```css                           ← NO! No markdown fences
@tailwind base;
```
"""

        return prompt

    def _build_gradient_hints(self, gradient_context: Dict) -> str:
        """
        Build domain-aware UI pattern hints from gradient context

        Args:
            gradient_context: {
                'domain_signals': { 'domain', 'structure', 'keywords', 'data_types', 'metrics' },
                'boost_hierarchical_navigation': bool,
                'boost_tree_views': bool,
                'boost_data_drill_down': bool
            }

        Returns:
            Formatted hint section for the prompt
        """
        if not gradient_context or not gradient_context.get('domain_signals'):
            return ""  # No gradient hints if not available

        domain_signals = gradient_context['domain_signals']
        domain = domain_signals.get('domain', 'generic')
        structure = domain_signals.get('structure', 'flat')
        max_depth = domain_signals.get('metrics', {}).get('max_depth', 0)
        total_files = domain_signals.get('metrics', {}).get('total_files', 0)
        data_types = domain_signals.get('data_types', [])

        hints = []
        hints.append("🧭 GRADIENT CONTEXT - DOMAIN-AWARE PATTERNS:")
        hints.append("")
        hints.append(f"The data analysis shows: {domain} domain with {structure} ({max_depth} levels deep, {total_files} total files)")
        hints.append("")

        # Add specific hints based on boosting flags
        if gradient_context.get('boost_hierarchical_navigation'):
            hints.append("✓ HIERARCHICAL NAVIGATION BOOSTED:")
            hints.append("  - Use expandable/collapsible folder tree components")
            hints.append("  - Show breadcrumb navigation for current path")
            hints.append("  - Display parent → child relationships clearly")
            hints.append(f"  - Data has {max_depth}-level nesting: pipeline.files.subdirs.*.subdirs.*.files")
            hints.append("  - CRITICAL: Files are in ARRAYS at leaf nodes, NOT objects!")
            hints.append("  - Example: pipeline.files.subdirs['downloads'].files = [{name: 'file1.csv'}, ...]")
            hints.append("")

        if gradient_context.get('boost_tree_views'):
            hints.append("✓ TREE/ACCORDION VIEWS BOOSTED:")
            hints.append("  - Deeply nested structure detected - use tree/accordion UI")
            hints.append("  - Implement expand/collapse for each directory level")
            hints.append("  - Show file counts at each level")
            hints.append("  - Use indentation to show hierarchy depth")
            hints.append("")

        if gradient_context.get('boost_data_drill_down'):
            hints.append("✓ DATA DRILL-DOWN BOOSTED:")
            if data_types:
                hints.append(f"  - Multiple data types detected: {', '.join(data_types[:3])}")
            hints.append("  - Enable clicking into nested data structures")
            hints.append("  - Show detail views when user selects items")
            hints.append("  - Display metadata at each level (file counts, sizes, statuses)")
            hints.append("")

        hints.append("CRITICAL - NESTED DATA HANDLING:")
        hints.append("  The API returns files in this nested structure:")
        hints.append("  ```typescript")
        hints.append("  pipeline.files = {")
        hints.append("    subdirs: {")
        hints.append("      'Chemical_data': {")
        hints.append("        subdirs: {")
        hints.append("          'downloads': { files: [{name, size_bytes, size_human}], file_count: 2 },")
        hints.append("          'extracted': { files: [{...}], file_count: 17 }")
        hints.append("        }")
        hints.append("      }")
        hints.append("    }")
        hints.append("  }")
        hints.append("  ```")
        hints.append("")
        hints.append("  DO NOT access files like: pipeline.files[0].name  ❌")
        hints.append("  DO access files like: pipeline.files.subdirs['dir_name'].files[0].name  ✅")
        hints.append("")
        hints.append("  To display files, you MUST:")
        hints.append("  1. Recursively traverse subdirs object")
        hints.append("  2. Extract files arrays at each level")
        hints.append("  3. Map over the arrays to display individual files")
        hints.append("")

        return "\n".join(hints)

    def _validate_no_mock_data(self, files: Dict[str, str]):
        """
        Validate that generated files don't contain forbidden patterns:
        1. Mock data patterns
        2. CSS code in TypeScript files

        Raises:
            ValueError: If violations are detected
        """
        mock_patterns = [
            'MOCK_DATA',
            'MOCK_DATASETS',
            'MOCK_PIPELINES',
            'const mockData =',
            'const MOCK_',
            'const data = [',  # Hardcoded arrays
        ]

        css_patterns = [
            '@tailwind',
            '@apply',
            '@layer',
            '/* === FILE:',  # CSS file marker inside TS file
        ]

        violations = []

        for filename, content in files.items():
            # Skip non-code files
            if not (filename.endswith('.tsx') or filename.endswith('.ts') or filename.endswith('.jsx') or filename.endswith('.js')):
                continue

            # Skip dataHooks.tsx which legitimately might have example patterns in comments
            if 'dataHooks' in filename or 'hooks' in filename.lower():
                continue

            # Check for CSS in TypeScript files
            for pattern in css_patterns:
                if pattern in content:
                    lines_with_pattern = [i+1 for i, line in enumerate(content.split('\n')) if pattern in line]
                    violations.append(
                        f"{filename}: Contains CSS code ('{pattern}') on line(s) {lines_with_pattern}. "
                        f"CSS should be in a separate .css file, not embedded in .tsx files."
                    )

            # Check for mock data patterns
            for pattern in mock_patterns:
                if pattern in content:
                    # Check if it's in a comment (allow warnings about mock data)
                    lines_with_pattern = [line for line in content.split('\n') if pattern in line]
                    for line in lines_with_pattern:
                        stripped = line.strip()
                        # Allow if it's in a comment or string explaining what NOT to do
                        if not (stripped.startswith('//') or stripped.startswith('*') or 'DO NOT' in line or 'NEVER' in line):
                            violations.append(f"{filename}: Found '{pattern}' on line: {line.strip()[:80]}")

        if violations:
            violation_msg = "\n".join(violations)
            warning = f"""
⚠️ WARNING: Mock data patterns detected in generated code!

{violation_msg}

The system is configured to NEVER generate mock data. These patterns violate the
"ABSOLUTELY NEVER GENERATE MOCK DATA" rule in the React Developer prompt.

This is a code quality issue that should be investigated.
"""
            print(warning)
            # For now, just warn - could make this a hard error with raise ValueError(warning)

    def _validate_file_completeness(self, files: Dict[str, str]):
        """
        Validate that generated files are complete and not truncated.

        Checks for:
        1. Truncated CSS files (ending with incomplete properties)
        2. Truncated code files (unclosed braces, parentheses)
        3. Files that are suspiciously short
        4. Incomplete JSON files

        Args:
            files: Dict of filename -> content
        """
        truncation_warnings = []

        for filename, content in files.items():
            # Skip empty or very small files
            if not content or len(content.strip()) < 10:
                truncation_warnings.append(f"{filename}: File is empty or too short ({len(content)} chars)")
                continue

            lines = content.split('\n')
            last_line = lines[-1] if lines else ""
            last_few_lines = '\n'.join(lines[-3:]) if len(lines) >= 3 else content

            # Check CSS files
            if filename.endswith('.css'):
                stripped_content = content.rstrip()

                # Check for incomplete CSS properties
                if stripped_content.endswith('-') or stripped_content.endswith(':'):
                    truncation_warnings.append(
                        f"{filename}: CSS appears truncated (ends with '{stripped_content[-5:]}')"
                    )

                # Check for unclosed CSS blocks
                open_braces = content.count('{')
                close_braces = content.count('}')
                if open_braces != close_braces:
                    truncation_warnings.append(
                        f"{filename}: Unbalanced braces ({open_braces} open, {close_braces} close)"
                    )

            # Check TypeScript/JavaScript files
            elif filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
                # Check for unclosed braces/brackets/parens
                open_braces = content.count('{') - content.count('}')
                open_brackets = content.count('[') - content.count(']')
                open_parens = content.count('(') - content.count(')')

                if open_braces > 2:  # Allow small imbalance for template literals
                    truncation_warnings.append(
                        f"{filename}: {open_braces} unclosed braces - likely truncated"
                    )
                if open_brackets > 1:
                    truncation_warnings.append(
                        f"{filename}: {open_brackets} unclosed brackets - likely truncated"
                    )
                if open_parens > 1:
                    truncation_warnings.append(
                        f"{filename}: {open_parens} unclosed parentheses - likely truncated"
                    )

                # Check for incomplete statements
                if last_line.strip() and not last_line.strip().endswith((';', '}', ')', ']', ',', '>')):
                    # Could be truncated mid-statement
                    if len(last_line.strip()) < 50:  # Short incomplete line
                        truncation_warnings.append(
                            f"{filename}: Possibly truncated (last line: '{last_line.strip()[:50]}')"
                        )

            # Check JSON files
            elif filename.endswith('.json'):
                try:
                    import json
                    json.loads(content)
                except json.JSONDecodeError as e:
                    truncation_warnings.append(
                        f"{filename}: Invalid JSON - {str(e)}"
                    )

            # Check config files
            elif filename in ['package.json', 'tsconfig.json', 'vite.config.ts', 'tailwind.config.js']:
                if len(content) < 50:
                    truncation_warnings.append(
                        f"{filename}: Config file is suspiciously short ({len(content)} chars)"
                    )

        # Report warnings
        if truncation_warnings:
            warning_msg = "\n".join([f"  ⚠️  {w}" for w in truncation_warnings])
            print(f"\n⚠️  TRUNCATION WARNINGS DETECTED:")
            print(warning_msg)
            print(f"\n💡 Suggestion: Files may be incomplete due to token limit.")
            print(f"   Current max_tokens: 16000. Consider generating fewer files or increasing limit.\n")
        else:
            print("  [Parser] ✅ All files appear complete (no truncation detected)")

    def _validate_type_safety(self, files: Dict[str, str]):
        """
        Validate that generated code uses defensive type coercion.

        Checks for:
        1. .replace() calls without String() coercion
        2. .toFixed() calls without Number() coercion
        3. .map() calls on possibly undefined arrays

        Args:
            files: Dict of filename -> content
        """
        import re

        type_safety_warnings = []

        for filename, content in files.items():
            if not filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
                continue

            # Check for .replace() without String() coercion
            # Pattern: something.replace( but not String(something).replace(
            replace_pattern = r'(?<!String\()([a-zA-Z_][a-zA-Z0-9_\.]*?)\.replace\('
            matches = re.findall(replace_pattern, content)

            for match in matches:
                # Exclude safe cases like literal strings
                if match not in ['str', 'text', 'String']:
                    type_safety_warnings.append(
                        f"{filename}: '{match}.replace()' missing String() coercion"
                    )

            # Check for .toFixed() without Number() coercion
            tofixed_pattern = r'(?<!Number\()([a-zA-Z_][a-zA-Z0-9_\.]*?)\.toFixed\('
            matches = re.findall(tofixed_pattern, content)

            for match in matches:
                if match not in ['num', 'number', 'Number']:
                    type_safety_warnings.append(
                        f"{filename}: '{match}.toFixed()' missing Number() coercion"
                    )

        # Report warnings (informational, not blocking)
        if type_safety_warnings:
            warning_msg = "\n".join([f"  ℹ️  {w}" for w in type_safety_warnings[:5]])  # Limit to 5
            print(f"\nℹ️  TYPE SAFETY SUGGESTIONS:")
            print(warning_msg)
            if len(type_safety_warnings) > 5:
                print(f"  ... and {len(type_safety_warnings) - 5} more suggestions")
            print(f"\n💡 Consider adding String() or Number() coercion for safety.\n")
        else:
            print("  [Parser] ✅ Type safety looks good (coercion detected)")

    def _validate_data_hooks_schema_consistency(self, files: Dict[str, str]):
        """
        CRITICAL VALIDATION (Phase 1.6):
        Ensure App.tsx uses data.pipelines, NOT data directly.

        If dataHooks.tsx defines:
          PipelinesResponse { pipelines: Pipeline[] }
        Then App.tsx MUST access:
          data.pipelines (NEVER data)

        This prevents the "0 records, 0 files" bug where schema mismatch
        causes filteredPipelines to always be empty.

        Args:
            files: Dict of filename -> content
        """
        import re

        # Check if dataHooks.tsx defines PipelinesResponse with pipelines property
        if 'dataHooks.tsx' not in files or 'App.tsx' not in files:
            return

        data_hooks_content = files['dataHooks.tsx']
        app_tsx_content = files['App.tsx']

        # Check if PipelinesResponse is defined with pipelines property
        pipelines_response_pattern = r'interface\s+PipelinesResponse\s*\{[^}]*pipelines:\s*Pipeline\[\]'
        has_pipelines_response = re.search(pipelines_response_pattern, data_hooks_content, re.DOTALL)

        if not has_pipelines_response:
            return  # No PipelinesResponse structure, skip validation

        # Check if App.tsx incorrectly uses data as array instead of data.pipelines
        # Pattern: if (!data || !Array.isArray(data))
        incorrect_data_check = re.search(r'Array\.isArray\(data\)', app_tsx_content)

        # Pattern: data.filter( instead of data.pipelines.filter(
        incorrect_data_filter = re.search(r'\bdata\.filter\s*\(', app_tsx_content)

        if incorrect_data_check or incorrect_data_filter:
            print("\n" + "="*70)
            print("CRITICAL SCHEMA ERROR DETECTED")
            print("="*70)
            print("\ndataHooks.tsx defines:")
            print("   PipelinesResponse { pipelines: Pipeline[] }")
            print("\nBut App.tsx uses:")
            if incorrect_data_check:
                print("   Array.isArray(data)  <- WRONG!")
            if incorrect_data_filter:
                print("   data.filter(...)  <- WRONG!")
            print("\nMUST use:")
            print("   Array.isArray(data.pipelines)")
            print("   data.pipelines.filter(...)")
            print("\nThis will cause: 0 records, 0 files, empty dashboard")
            print("="*70 + "\n")

            # This is a critical error, so we should raise it
            raise ValueError(
                "Schema mismatch: App.tsx must use data.pipelines, not data directly. "
                "See console output above for details."
            )

        print("  [Parser] Schema consistency: App.tsx correctly uses data.pipelines")

    def _validate_canonical_schema_fields(self, files: Dict[str, str]):
        """
        CRITICAL VALIDATION: Check for hallucinated metric fields.

        Detects usage of non-existent fields that cause "0 records" bugs:
        - pipeline.metrics.total_records (WRONG - should be record_count)
        - pipeline.total_files (WRONG - should be metrics.file_count)
        - pipeline.children, pipeline.subdirectories, etc. (WRONG - don't exist)

        Args:
            files: Dict of filename -> content
        """
        import re

        HALLUCINATED_FIELDS = [
            (r'\.metrics\.total_records', 'metrics.total_records', 'metrics.record_count'),
            (r'\.metrics\.records\b', 'metrics.records', 'metrics.record_count'),
            (r'\.total_files\b', 'total_files', 'metrics.file_count'),
            (r'\.total_records\b(?!.*metrics)', 'total_records', 'metrics.record_count'),
            (r'\.fileCount\b', 'fileCount', 'metrics.file_count'),
            (r'\.recordCount\b', 'recordCount', 'metrics.record_count'),
            (r'\.filesCount\b', 'filesCount', 'metrics.file_count'),
            (r'\.recordsCount\b', 'recordsCount', 'metrics.record_count'),
            # REMOVED: (r'\.children\b', 'children', 'files') - children is now correct field from API
            (r'\.subdirectories\b', 'subdirectories', 'files'),
            (r'\.tree\b', 'tree', 'files'),
        ]

        errors = []
        autocorrected = []

        for filename, content in files.items():
            if not filename.endswith(('.tsx', '.ts')):
                continue

            # Skip type definitions
            if 'types.ts' in filename:
                continue

            original_content = content
            for pattern, wrong_field, correct_field in HALLUCINATED_FIELDS:
                if re.search(pattern, content):
                    # AUTOCORRECT: Replace hallucinated field with canonical field
                    content = re.sub(pattern, f'.{correct_field}', content)
                    autocorrected.append(f"{filename}: Auto-corrected '{wrong_field}' -> '{correct_field}'")

            # Update files dict with corrected content
            if content != original_content:
                files[filename] = content

        # Report autocorrections (info only, don't block)
        if autocorrected:
            print("\n" + "="*70)
            print("SCHEMA AUTOCORRECTION APPLIED")
            print("="*70)
            print("\nFixed hallucinated fields automatically:")
            for fix in autocorrected:
                print(f"  [AUTO-FIX] {fix}")
            print("\nCanonical schema enforced:")
            print("  [OK] pipeline.metrics.file_count")
            print("  [OK] pipeline.metrics.record_count")
            print("  [OK] pipeline.metrics.data_size")
            print("  [OK] pipeline.stages")
            print("  [OK] pipeline.files")
            print("="*70 + "\n")

        # Re-scan for any remaining errors (shouldn't happen after autocorrect)
        for filename, content in files.items():
            if not filename.endswith(('.tsx', '.ts')):
                continue
            if 'types.ts' in filename:
                continue
            for pattern, wrong_field, correct_field in HALLUCINATED_FIELDS:
                if re.search(pattern, content):
                    errors.append(f"{filename}: Uses '{wrong_field}' (should be '{correct_field}')")

        if errors:
            print("\n" + "="*70)
            print("CRITICAL: HALLUCINATED SCHEMA FIELDS DETECTED")
            print("="*70)
            print("\nThese fields DO NOT EXIST and cause '0 records' bugs:")
            for error in errors:
                print(f"  [X] {error}")
            print("\nCanonical schema:")
            print("  [OK] pipeline.metrics.file_count")
            print("  [OK] pipeline.metrics.record_count")
            print("  [OK] pipeline.metrics.data_size")
            print("  [OK] pipeline.stages")
            print("  [OK] pipeline.files")
            print("="*70 + "\n")

            raise ValueError(
                f"Hallucinated schema fields detected: {', '.join([e.split(':')[1].strip() for e in errors[:3]])}. "
                "See console output for details."
            )

        print("  [Parser] [OK] Canonical schema fields validated - no hallucinations")

    def _parse_generated_files(self, generated_code: str) -> Dict[str, str]:
        """
        Parse generated code into separate files

        Supports formats:
        // === FILE: App.tsx ===        (standard)
        /* === FILE: index.css === */  (CSS/fallback)
        // ===FILE:App.tsx===           (no spaces - robustness)

        Phase 5 Refactoring: Improved regex to handle edge cases
        """
        files = {}
        current_file = None
        current_content = []
        in_markdown_fence = False  # Track if we're inside a markdown code fence

        # Phase 5 Refactoring: Robust regex pattern for file markers
        # Handles: // === FILE: App.tsx ===, /* === FILE: foo.ts === */, //===FILE:bar.tsx===
        file_marker_pattern = re.compile(
            r'^[/\*\s]*===+\s*FILE:\s*(.+?)\s*===+',
            re.IGNORECASE
        )

        for line in generated_code.split('\n'):
            # Check for file markers using robust regex
            marker_match = file_marker_pattern.match(line.strip())

            if marker_match:
                marker_filename = marker_match.group(1).strip()

                # FIX: Remove markdown formatting from filenames (**, *, `, etc.)
                # LLM may generate: components/**DatasetCard**.tsx or `DataTable`.tsx
                marker_filename = marker_filename.replace('**', '').replace('*', '').replace('`', '').strip()

                # Phase 5 Refactoring: Safety checks
                # Prevent path traversal attacks and excessive files
                if len(files) >= 50:
                    print(f"  [Parser] Warning: Max file limit (50) reached, ignoring: {marker_filename}")
                    continue

                if '..' in marker_filename or marker_filename.startswith('/'):
                    print(f"  [Parser] Warning: Invalid path detected, ignoring: {marker_filename}")
                    continue

                # Save previous file
                if current_file:
                    # Clean up content: remove trailing markdown syntax
                    content = '\n'.join(current_content).rstrip()
                    # Remove trailing markdown fences (handles both ``` and ```language)
                    lines = content.split('\n')
                    while lines and lines[-1].strip().startswith('```'):
                        lines.pop()
                        print(f"  [Parser] Removed trailing markdown fence from {current_file}")
                    content = '\n'.join(lines).rstrip()
                    files[current_file] = content

                # Start new file
                current_file = marker_filename
                current_content = []
                in_markdown_fence = False  # Reset fence state for new file
                seen_closing_fence = False  # Track if we've seen a closing fence
                skip_rest_of_file = False  # Flag to skip markdown docs after code
            else:
                if current_file and not skip_rest_of_file:
                    # Check if this line is a markdown fence marker
                    if line.strip().startswith('```'):
                        # Toggle fence state (handles both opening and closing)
                        was_in_fence = in_markdown_fence
                        in_markdown_fence = not in_markdown_fence
                        # If we just closed a fence, mark it
                        if was_in_fence and not in_markdown_fence:
                            seen_closing_fence = True
                        continue  # Skip the fence line itself

                    # After a closing fence, stop if we see markdown documentation
                    if seen_closing_fence and not in_markdown_fence:
                        stripped = line.strip()
                        # Detect markdown headers (##, ###) or numbered lists (1., 2., etc.)
                        if (stripped.startswith('#') or
                            (stripped and stripped[0].isdigit() and '.' in stripped[:4])):
                            print(f"  [Parser] Detected markdown documentation after code in {current_file}, skipping rest")
                            skip_rest_of_file = True
                            continue  # Skip this line and subsequent ones

                    # Only append content if we're NOT inside a markdown fence
                    if not in_markdown_fence:
                        current_content.append(line)

        # Save last file
        if current_file:
            content = '\n'.join(current_content).rstrip()
            # Remove trailing markdown fences (handles both ``` and ```language)
            # This catches cases where Claude adds markdown fences at end of last file
            lines = content.split('\n')
            while lines and lines[-1].strip().startswith('```'):
                lines.pop()
                print(f"  [Parser] Removed trailing markdown fence from {current_file}")
            content = '\n'.join(lines).rstrip()
            files[current_file] = content

        # If no file markers found, treat entire output as App.tsx
        if not files:
            files['App.tsx'] = generated_code

        # Phase 3A: Always include data hooks for real data fetching
        data_hooks_content = self._load_data_hooks_template()
        if data_hooks_content:
            files['dataHooks.tsx'] = data_hooks_content
            print(f"  [React Developer] Added dataHooks.tsx ({len(data_hooks_content)} chars)")

        # Validate files for truncation
        self._validate_file_completeness(files)

        # Validate type safety (defensive coercion)
        self._validate_type_safety(files)

        # Validate schema consistency (Phase 1.6 - CRITICAL)
        self._validate_data_hooks_schema_consistency(files)

        # Validate canonical schema fields - NO HALLUCINATIONS (Phase 1.6)
        self._validate_canonical_schema_fields(files)

        return files

    def get_setup_instructions(self) -> str:
        """Get instructions for setting up and running the generated React app"""

        if self.styling_framework == "tailwind":
            return """
# Setup Instructions

1. Create React app:
   ```bash
   npx create-react-app pipeline-dashboard --template typescript
   cd pipeline-dashboard
   ```

2. Install Tailwind CSS:
   ```bash
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   ```

3. Configure Tailwind (tailwind.config.js):
   ```js
   module.exports = {
     content: ["./src/**/*.{js,jsx,ts,tsx}"],
     theme: { extend: {} },
     plugins: [],
   }
   ```

4. Add Tailwind to src/index.css:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

5. Replace src/App.tsx with generated code

6. Add Material Symbols to public/index.html:
   ```html
   <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded" rel="stylesheet">
   ```

7. Run:
   ```bash
   npm start
   ```
"""
        else:  # mui
            return """
# Setup Instructions

1. Create React app:
   ```bash
   npx create-react-app pipeline-dashboard --template typescript
   cd pipeline-dashboard
   ```

2. Install Material UI:
   ```bash
   npm install @mui/material @emotion/react @emotion/styled
   npm install @mui/icons-material
   ```

3. Replace src/App.tsx with generated code

4. Run:
   ```bash
   npm start
   ```
"""

    def save_files(self, files: Dict[str, str], output_dir: Path):
        """
        Save generated files to disk

        Args:
            files: Dictionary of filename -> content
            output_dir: Directory to save files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Vite/React source files should go in src/ directory
        src_extensions = {'.tsx', '.ts', '.jsx', '.js', '.css'}
        config_files = {'package.json', 'tsconfig.json', 'vite.config.ts', 'tailwind.config.js', 'postcss.config.js'}

        for filename, content in files.items():
            # Determine if file should go in src/ directory
            file_ext = Path(filename).suffix
            file_basename = Path(filename).name

            # FIX #12: Skip component files without proper extensions
            # This prevents writing extensionless duplicates that cause Vite parse errors
            if 'components/' in filename and file_ext not in src_extensions:
                print(f"  [React Developer] ⚠️ Skipping invalid component file (no extension): {filename}")
                continue

            # Check if it's a source file (has source extension and not a config file)
            is_source_file = file_ext in src_extensions and file_basename not in config_files

            # Components folder files always go in src/
            if 'components/' in filename or is_source_file:
                # For Vite, React source files go in src/
                file_path = output_dir / 'src' / filename
            else:
                # Config files stay in root
                file_path = output_dir / filename

            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"  [React Developer] Saved: {file_path}")

        # Fix vite.config.ts to use port 3001 to avoid conflict with Streamlit (port 3000)
        vite_config_path = output_dir / "vite.config.ts"
        if vite_config_path.exists():
            vite_content = vite_config_path.read_text(encoding='utf-8')
            # Replace port 3000 with 3001, and add host: '0.0.0.0'
            vite_content = vite_content.replace('port: 3000', 'port: 3001')
            # Add host if not present
            if 'host:' not in vite_content:
                vite_content = vite_content.replace('port: 3001', "port: 3001,\n    host: '0.0.0.0'")
            vite_config_path.write_text(vite_content, encoding='utf-8')
            print(f"  [React Developer] Fixed vite.config.ts to use port 3001")

        # Save setup instructions
        setup_file = output_dir / "SETUP.md"
        with open(setup_file, 'w', encoding='utf-8') as f:
            f.write(self.get_setup_instructions())

        print(f"  [React Developer] Saved: {setup_file}")
        print(f"\n[React Developer] All files saved to: {output_dir}")

    # === Phase 5: Autonomous Mode Methods ===

    def run(self, shared_memory, max_steps: int = 3) -> Dict[str, str]:
        """
        Autonomous planning loop for Phase 5.

        Args:
            shared_memory: SharedSessionMemory instance
            max_steps: Maximum planning iterations (default: 3)

        Returns:
            Generated React files (from shared_memory.react_files)
        """
        print(f"\n[React Agent] Starting autonomous mode (max {max_steps} steps)...")
        shared_memory.react_status = "planning"

        for step in range(max_steps):
            print(f"\n[React Agent] Step {step + 1}/{max_steps}")

            # 1. Plan next action (LLM reasoning)
            plan = self._plan_next_action(shared_memory)
            print(f"[React Agent] Planned: {plan.skill}")
            print(f"[React Agent] Reasoning: {plan.reasoning}")

            # 2. Execute skill
            print(f"[React Agent] Executing: {plan.skill}")
            result = self._execute_skill(plan, shared_memory)

            # 3. Evaluate implementation
            evaluation = self._evaluate_implementation(shared_memory)
            print(f"[React Agent] Evaluation: {'SATISFACTORY' if evaluation.satisfactory else 'NEEDS WORK'}")

            if evaluation.issues:
                print(f"[React Agent] Issues: {', '.join(evaluation.issues[:3])}")

            # BUGFIX: Save evaluation to shared_memory so next iteration can see it
            shared_memory.react_evaluations.append({
                "step": step + 1,
                "satisfactory": evaluation.satisfactory,
                "issues": evaluation.issues,
                "next_action": evaluation.next_action,
                "reasoning": evaluation.reasoning
            })

            # 4. Terminate ONLY if evaluation is satisfactory
            # FIX: Don't allow LLM to override evaluation by planning "finish" when there are still conflicts
            # The evaluation is deterministic code logic we can trust, the plan is LLM reasoning that can be wrong
            if evaluation.satisfactory:
                shared_memory.react_satisfactory = True
                shared_memory.react_status = "done"
                print(f"[React Agent] Implementation complete after {step + 1} step(s)!")
                return shared_memory.react_files
            elif plan.skill == "finish" and not evaluation.satisfactory:
                # LLM tried to finish but evaluation says there are issues - override and continue
                print(f"[React Agent] ⚠️ LLM planned 'finish' but evaluation found {len(evaluation.issues)} issues - continuing to fix")
                print(f"[React Agent] Next action from evaluation: {evaluation.next_action}")
                # Continue loop to address issues

        # Max steps reached
        print(f"[React Agent] Max steps reached ({max_steps}), returning current implementation")
        shared_memory.react_status = "max_steps_reached"
        return shared_memory.react_files

    def _plan_next_action(self, shared_memory) -> Plan:
        """
        Plan next action using LLM reasoning.

        Args:
            shared_memory: SharedSessionMemory instance

        Returns:
            Plan object with skill, reasoning, and arguments
        """
        # Build context for planning
        ux_spec_summary = shared_memory.ux_spec.to_summary() if shared_memory.ux_spec else "No UX spec available"
        react_files_count = len(shared_memory.react_files) if shared_memory.react_files else 0
        conflicts_count = len(shared_memory.implementation_conflicts)

        # BUGFIX Issue #4: Include conflict DETAILS, not just count
        conflict_details = ""
        if shared_memory.implementation_conflicts:
            # Show first 10 conflicts with details
            conflict_list = []
            for i, conflict in enumerate(shared_memory.implementation_conflicts[:10], 1):
                conflict_list.append(f"{i}. [{conflict.severity.upper()}] {conflict.description}")
            if len(shared_memory.implementation_conflicts) > 10:
                conflict_list.append(f"... and {len(shared_memory.implementation_conflicts) - 10} more conflicts")
            conflict_details = f"""
IMPLEMENTATION CONFLICTS ({conflicts_count} total):
{chr(10).join(conflict_list)}

ACTION REQUIRED: Use "resolve_conflicts" skill to fix these issues!
"""

        # BUGFIX: Include previous evaluation results in planning context
        previous_evaluation = ""
        if shared_memory.react_evaluations:
            last_eval = shared_memory.react_evaluations[-1]
            previous_evaluation = f"""
PREVIOUS STEP EVALUATION:
- Satisfactory: {last_eval['satisfactory']}
- Issues Found: {', '.join(last_eval['issues']) if last_eval['issues'] else 'None'}
- Suggested Next Action: {last_eval['next_action']}
- Reasoning: {last_eval['reasoning']}
"""

        prompt = f"""You are a React Developer Agent planning your next implementation step.

CURRENT STATE:
- UX Spec Version: {shared_memory.ux_spec_version}
- React Files Generated: {react_files_count}
- React Status: {shared_memory.react_status}
{conflict_details}{previous_evaluation}
UX SPECIFICATION:
{ux_spec_summary}

AVAILABLE SKILLS:
{self._format_available_skills()}

YOUR TASK:
Decide what skill to execute next to complete the React implementation.

DECISION LOGIC (in order of priority):
1. If React files count is 0, use "generate_initial_implementation"
2. If IMPLEMENTATION CONFLICTS section shows conflicts above, use "resolve_conflicts" (CRITICAL!)
3. If import errors exist (missing .tsx/.ts extensions), use "fix_import_errors"
4. If type errors exist, use "fix_type_errors"
5. If previous evaluation suggested a next action, strongly consider using it
6. If implementation is complete with no issues, use "finish"

IMPORTANT: When conflicts are listed above, you MUST use "resolve_conflicts", NOT "finish"!

IMPORTANT: Respond with ONLY valid JSON. No prose before or after.

Output format:
{{
  "skill": "skill_name",
  "reasoning": "why this skill is needed now",
  "arguments": {{}},
  "expected_outcome": "what this will achieve"
}}
"""

        # Call LLM for planning
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1000,
            temperature=0.0,  # Deterministic planning
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text

        # Robust JSON parsing: Try multiple strategies
        plan_data = None

        # Strategy 1: Direct JSON parse
        try:
            plan_data = json.loads(response_text.strip())
        except:
            # Strategy 2: Extract from code block
            import re
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if code_block_match:
                try:
                    plan_data = json.loads(code_block_match.group(1))
                except:
                    pass

            # Strategy 3: Find first JSON object
            if not plan_data:
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        plan_data = json.loads(json_match.group(0))
                    except:
                        pass

        if plan_data and isinstance(plan_data, dict):
            return Plan(
                skill=plan_data.get('skill', 'generate_initial_implementation'),
                reasoning=plan_data.get('reasoning', 'No reasoning provided'),
                arguments=plan_data.get('arguments', {}),
                expected_outcome=plan_data.get('expected_outcome', '')
            )
        else:
            # Fallback: Default plan
            print(f"[React Agent] JSON parsing failed, using fallback plan")
            if react_files_count == 0:
                return Plan(
                    skill="generate_initial_implementation",
                    reasoning="No React files exist yet",
                    arguments={},
                    expected_outcome="Initial React implementation generated"
                )
            else:
                return Plan(
                    skill="finish",
                    reasoning="Implementation appears complete",
                    arguments={},
                    expected_outcome="Mark implementation as done"
                )

    def _format_available_skills(self) -> str:
        """Format available skills for prompt"""
        if not self.skills:
            return "No skills available"

        lines = []
        for skill_name, skill_info in self.skills.items():
            lines.append(f"- {skill_name}: {skill_info['description']}")
        return "\n".join(lines)

    def _normalize_skill_output(self, result: Dict[str, Any]) -> SkillOutput:
        """
        Normalize skill result Dict to SkillOutput dataclass.

        Phase 5 Refactoring: Enforce skill contracts by normalizing outputs.
        Skills can still return Dict for backward compatibility.

        Args:
            result: Skill result dict (legacy format)

        Returns:
            SkillOutput with normalized structure
        """
        if isinstance(result, SkillOutput):
            return result

        return SkillOutput(
            success=result.get("success", True),
            updated_files=result.get("updated_files", {}),
            new_issues=result.get("new_issues", []),
            requires_replan=result.get("requires_replan", False),
            message=result.get("message", ""),
            error=result.get("error", "")
        )

    def _execute_skill(self, plan: Plan, shared_memory) -> Dict[str, Any]:
        """
        Execute planned skill.

        Args:
            plan: Plan object with skill name and arguments
            shared_memory: SharedSessionMemory instance

        Returns:
            Skill execution result dict

        Phase 5 Refactoring: Normalizes skill outputs to SkillOutput for validation
        """
        skill_name = plan.skill

        if skill_name not in self.skills:
            print(f"[React Agent] Unknown skill: {skill_name}, using 'finish'")
            skill_name = "finish"

        skill_fn = self.skills[skill_name]["fn"]
        result = skill_fn(shared_memory, plan.arguments)

        # Phase 5 Refactoring: Normalize and validate skill output
        normalized = self._normalize_skill_output(result)

        # Log issues if any
        if not normalized.success:
            print(f"  [React Agent] Skill failed: {normalized.error}")
        if normalized.new_issues:
            print(f"  [React Agent] New issues detected: {len(normalized.new_issues)}")

        # Record reasoning in trace
        shared_memory.react_reasoning_trace.append(
            f"Step: {skill_name} - {plan.reasoning}"
        )

        # Return original dict for backward compatibility
        return result

    def _build_skill_registry(self):
        """Build skill registry for autonomous mode."""
        self.skills = {
            "generate_initial_implementation": {
                "fn": self._skill_generate_initial_implementation,
                "description": "Generate React code from UX spec"
            },
            "fix_type_errors": {
                "fn": self._skill_fix_type_errors,
                "description": "Fix TypeScript type errors"
            },
            "fix_import_errors": {
                "fn": self._skill_fix_import_errors,
                "description": "Fix import paths and missing imports"
            },
            "regenerate_component": {
                "fn": self._skill_regenerate_component,
                "description": "Regenerate a specific component (KEY INNOVATION!)"
            },
            "fix_data_filtering": {
                "fn": self._skill_fix_data_filtering,
                "description": "Fix source filtering issues"
            },
            "adjust_styling": {
                "fn": self._skill_adjust_styling,
                "description": "Modify Tailwind classes/styling"
            },
            "optimize_code": {
                "fn": self._skill_optimize_code,
                "description": "Optimize performance/structure"
            },
            "resolve_conflicts": {
                "fn": self._skill_resolve_conflicts,
                "description": "Resolve conflicts with UX spec"
            },
            "validate_implementation": {
                "fn": self._skill_validate_implementation,
                "description": "Run validation checks"
            },
            "finish": {
                "fn": self._skill_finish,
                "description": "Mark implementation as complete"
            }
        }

    # ========================================
    # PHASE 6.2: CONFLICT REPORTING
    # ========================================

    def _report_conflict(self, shared_memory, conflict_type: str, description: str,
                        affected_component: str = None, severity: str = "medium"):
        """
        Phase 6.2: Report a conflict to shared memory.

        Agents use this when they detect issues with UX spec or their own implementation.

        Args:
            shared_memory: SharedSessionMemory instance
            conflict_type: Type of conflict (from ConflictType enum)
            description: Clear description of the issue
            affected_component: Component name if applicable
            severity: "low", "medium", "high", or "critical"
        """
        from src.agents.shared_memory import Conflict, ConflictType

        # Map string to ConflictType enum
        conflict_type_map = {
            "missing_component": ConflictType.MISSING_COMPONENT,
            "prop_mismatch": ConflictType.PROP_LIST_MISMATCH,
            "type_error": ConflictType.IMPLEMENTATION_TYPE_ERROR,
            "import_error": ConflictType.INVALID_IMPORT,
            "schema_mismatch": ConflictType.DESIGN_SCHEMA_MISMATCH,
            "data_source_mismatch": ConflictType.DATA_SOURCE_MISMATCH,
        }

        conflict = Conflict(
            conflict_type=conflict_type_map.get(conflict_type, ConflictType.IMPLEMENTATION_TYPE_ERROR),
            source_agent="ReactDeveloper",
            description=description,
            affected_component=affected_component,
            severity=severity,
            target="REACT_IMPL"  # React agent reports implementation conflicts
        )

        shared_memory.implementation_conflicts.append(conflict)
        print(f"[Phase 6.2] React agent reported conflict: {description}")

    def _evaluate_implementation(self, shared_memory) -> ReactEvaluationResult:
        """
        Evaluate current implementation and determine next action.

        FIX: Now checks BOTH design AND implementation conflicts.

        Args:
            shared_memory: SharedSessionMemory instance

        Returns:
            ReactEvaluationResult with evaluation details
        """
        issues = []

        # Check if files exist
        if not shared_memory.react_files:
            return ReactEvaluationResult(
                satisfactory=False,
                issues=["No React files generated yet"],
                next_action="generate_initial_implementation",
                reasoning="No implementation exists"
            )

        # FIX: Check BOTH conflict lists, not just implementation_conflicts
        all_conflicts = (
            (shared_memory.design_conflicts or []) +
            (shared_memory.implementation_conflicts or [])
        )

        if all_conflicts:
            conflicts_desc = [c.description for c in all_conflicts[:3]]
            issues.append(f"{len(all_conflicts)} total conflicts detected (design + implementation)")

            # Categorize by severity
            high_severity = sum(1 for c in all_conflicts if c.severity == "high")
            medium_severity = sum(1 for c in all_conflicts if c.severity == "medium")

            print(f"  [React Evaluation] Found {len(all_conflicts)} conflicts: {high_severity} high, {medium_severity} medium")

            return ReactEvaluationResult(
                satisfactory=False,
                issues=issues,
                next_action="resolve_conflicts",
                conflicts_detected=all_conflicts,
                reasoning=f"Cannot mark satisfactory with {len(all_conflicts)} unresolved conflicts: {', '.join(conflicts_desc)}"
            )

        # Validate code quality (basic checks)
        validation_issues = self._detect_code_issues(shared_memory.react_files)
        if validation_issues:
            # BUGFIX: Properly determine next_action based on issue type
            issues_str = str(validation_issues).lower()

            if "import" in issues_str or "extension" in issues_str or ".tsx" in issues_str:
                next_action = "fix_import_errors"
                reasoning_prefix = "Import errors detected"
            elif "type" in issues_str or "typescript" in issues_str:
                next_action = "fix_type_errors"
                reasoning_prefix = "Type errors detected"
            elif "mock" in issues_str or "placeholder" in issues_str:
                next_action = "regenerate_component"
                reasoning_prefix = "Mock data detected"
            else:
                next_action = "optimize_code"
                reasoning_prefix = "Code quality issues"

            return ReactEvaluationResult(
                satisfactory=False,
                issues=validation_issues,
                next_action=next_action,
                reasoning=f"{reasoning_prefix}: {', '.join(validation_issues[:2])}"
            )

        # All checks pass
        return ReactEvaluationResult(
            satisfactory=True,
            issues=[],
            next_action="finish",
            reasoning="Implementation is complete with no issues"
        )

    def _detect_code_issues(self, files: Dict[str, str]) -> List[str]:
        """
        Detect basic code quality issues.

        Args:
            files: Dictionary of filename -> content

        Returns:
            List of issue descriptions

        Phase 5 Refactoring: Smarter mock data detection - avoids false positives
        """
        issues = []

        for filename, content in files.items():
            if not filename.endswith(('.tsx', '.ts')):
                continue

            # Check for missing imports with extensions
            if "import" in content and "from './" in content:
                imports_without_ext = re.findall(r"from '\./(?!.*\.tsx|.*\.ts)[^']+", content)
                if imports_without_ext:
                    issues.append(f"{filename}: Missing .tsx extensions in imports")

            # Phase 5 Refactoring: Smarter mock data detection
            # Only flag if it looks like a dataset (>5 items, used as data source)
            if filename.endswith('.tsx'):
                # Check for explicit MOCK_DATA markers
                if "MOCK_DATA" in content or "PLACEHOLDER_DATA" in content:
                    issues.append(f"{filename}: Contains explicit mock data markers")
                    continue

                # Check for suspicious large arrays in TSX files
                # Pattern: const foo = [{...}, {...}, {...}, ...] with 5+ objects
                array_pattern = r'const\s+(\w+)\s*=\s*\[([\s\S]*?)\]'
                matches = re.findall(array_pattern, content)

                for var_name, array_content in matches:
                    # Count number of objects in array (look for {)
                    object_count = array_content.count('{')

                    # If array has 5+ objects AND is used in a data context
                    if object_count >= 5:
                        # Check if variable is used in a data-fetching context
                        # Look for: data={varName}, items={varName}, rows={varName}
                        data_usage_pattern = rf'(data|items|rows|tableData)\s*=\s*\{{\s*{var_name}'
                        if re.search(data_usage_pattern, content):
                            issues.append(f"{filename}: Potential mock data - array '{var_name}' with {object_count} objects used as data source")

        return issues

    def detect_conflicts(self, shared_memory) -> List:
        """
        Detect conflicts between React implementation and UX spec.

        Args:
            shared_memory: SharedSessionMemory instance

        Returns:
            List of Conflict objects
        """
        conflicts = []

        if not shared_memory.ux_spec or not shared_memory.react_files:
            return conflicts

        from src.agents.shared_memory import Conflict, ConflictType

        ux_components = shared_memory.ux_spec.components
        react_files = shared_memory.react_files

        # Check 1: Are all UX components implemented?
        for component in ux_components:
            component_name = component.get('name', '')
            component_file = f"components/{component_name}.tsx"

            if component_file not in react_files:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.MISSING_COMPONENT,
                    source_agent="React Developer",
                    description=f"UX spec requires {component_name}, but component not implemented",
                    affected_component=component_name,
                    suggested_resolution=f"Generate {component_name}.tsx component",
                    severity="high"
                ))

        # Check 2: Invalid imports (missing .tsx extensions)
        app_file = react_files.get('App.tsx', '')
        if app_file:
            if "from './components/" in app_file:
                import re
                imports_without_ext = re.findall(r"from '\./components/([^']+)'", app_file)
                for imp in imports_without_ext:
                    if not imp.endswith('.tsx'):
                        conflicts.append(Conflict(
                            conflict_type=ConflictType.INVALID_IMPORT,
                            source_agent="React Developer",
                            description=f"Import missing .tsx extension: {imp}",
                            suggested_resolution=f"Change to: from './components/{imp}.tsx'",
                            severity="medium"
                        ))

        return conflicts

    # === Skill Implementations ===

    def _skill_generate_initial_implementation(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Generate initial React code from UX spec."""
        print("[React Agent] Executing: generate_initial_implementation")

        if not shared_memory.ux_spec:
            return {"success": False, "error": "No UX spec available"}

        # Convert UX spec to DesignSpec object
        from src.agents.ux_designer import DesignSpec
        ux_spec = shared_memory.ux_spec

        # Build context from shared memory
        context = {
            "data_sources": shared_memory.data_context.get("sources", {}),
            "user_prompt": shared_memory.user_requirements.get("intent", ""),
            "scope": [],
            "data_context": {},
            "gradient_context": {}
        }

        # Call existing build() method
        files = self.build(ux_spec, context)

        # Update shared memory
        shared_memory.update_react_files(
            files,
            reasoning="Initial React implementation generated from UX spec"
        )

        return {"success": True, "files_generated": len(files)}

    def _skill_fix_type_errors(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Fix TypeScript type errors."""
        print("[React Agent] Executing: fix_type_errors")

        # In production, this would analyze errors and fix them
        # For now, return success (placeholder)
        return {"success": True, "errors_fixed": 0}

    def _skill_fix_import_errors(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Fix import paths and missing imports."""
        print("[React Agent] Executing: fix_import_errors")

        if not shared_memory.react_files:
            return {"success": False, "error": "No React files to fix"}

        fixed_count = 0
        updated_files = shared_memory.react_files.copy()

        # Fix missing .tsx and .ts extensions
        for filename, content in updated_files.items():
            if not filename.endswith(('.tsx', '.ts')):
                continue

            import re
            original_content = content

            # Comprehensive pattern: Match imports without extensions
            # Pattern matches: from './path/to/file' or from "./path/to/file"
            # With optional semicolon and whitespace
            def fix_import(match):
                """Determine correct extension based on file naming convention"""
                full_match = match.group(0)
                import_path = match.group(1)

                # Extract just the filename (after last /)
                parts = import_path.split('/')
                file_name = parts[-1] if parts else import_path

                # Determine extension:
                # - Known .ts files (types, utils, constants, config)
                if file_name in ['types', 'interfaces', 'constants', 'config']:
                    new_path = import_path + '.ts'
                # - Everything else gets .tsx (components, pages, main, etc.)
                else:
                    new_path = import_path + '.tsx'

                # Replace the path in the original match
                return full_match.replace(import_path + "'", new_path + "'")

            # Match all relative imports without extensions
            # This pattern handles:
            # - from './foo' OR from "./foo"
            # - With or without semicolon
            # - Nested paths like './components/Foo' or './utils/helper'
            # CRITICAL: Must NOT match imports that already have extensions
            content = re.sub(
                r'''from\s+['"](\.\/[^'"]+?)(?<!\.tsx)(?<!\.ts)(?<!\.jsx)(?<!\.js)(?<!\.json)(?<!\.css)['"]''',
                fix_import,
                content
            )

            if content != original_content:
                updated_files[filename] = content
                fixed_count += 1

                # BUGFIX Issue #3: Count imports that MATCHED the fix pattern (needed extensions)
                # Use the same pattern as re.sub to count what actually got fixed
                imports_fixed = len(re.findall(
                    r'''from\s+['"](\.\/[^'"]+?)(?<!\.tsx)(?<!\.ts)(?<!\.jsx)(?<!\.js)(?<!\.json)(?<!\.css)['"]''',
                    original_content
                ))

                print(f"  [fix_import_errors] Fixed {imports_fixed} import(s) in {filename}")

        if fixed_count > 0:
            shared_memory.update_react_files(
                updated_files,
                reasoning=f"Fixed {fixed_count} files with import extensions"
            )
            print(f"  [fix_import_errors] Total files fixed: {fixed_count}")
        else:
            print(f"  [fix_import_errors] No import errors found to fix")

        return {"success": True, "fixes_applied": fixed_count}

    def _skill_regenerate_component(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """
        Regenerate a specific component (KEY INNOVATION!).

        Phase 5 KEY INNOVATION: Component-level regeneration, not full codebase regeneration.
        """
        print("[React Agent] Executing: regenerate_component")

        component_name = args.get('component_name', '')
        reason = args.get('reason', '')

        if not component_name:
            return {"success": False, "error": "No component specified"}

        # Extract current component
        current_files = shared_memory.react_files
        component_file = f"components/{component_name}.tsx"

        if component_file not in current_files:
            return {"success": False, "error": f"Component {component_name} not found"}

        # Generate replacement using LLM
        prompt = f"""Regenerate the {component_name} React component.

REASON FOR REGENERATION:
{reason}

CURRENT COMPONENT:
{current_files[component_file][:500]}...

UX SPEC:
{shared_memory.ux_spec.to_summary() if shared_memory.ux_spec else 'N/A'}

Generate ONLY the {component_name}.tsx file, improved based on the reason above.
Use TypeScript, Tailwind CSS, and Material Symbols icons.
"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        new_component_code = response.content[0].text

        # Update in shared memory
        updated_files = current_files.copy()
        updated_files[component_file] = new_component_code

        shared_memory.update_react_files(
            updated_files,
            reasoning=f"Regenerated {component_name}: {reason}"
        )

        return {"success": True, "component": component_name, "reason": reason}

    def _skill_fix_data_filtering(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Fix source filtering issues."""
        print("[React Agent] Executing: fix_data_filtering")
        # Placeholder - would implement filtering fixes
        return {"success": True, "filters_fixed": 0}

    def _skill_adjust_styling(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Modify Tailwind classes/styling."""
        print("[React Agent] Executing: adjust_styling")
        # Placeholder - would implement styling adjustments
        return {"success": True, "styling_updated": False}

    def _skill_optimize_code(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Optimize performance/structure."""
        print("[React Agent] Executing: optimize_code")
        # Placeholder - would implement code optimization
        return {"success": True, "optimizations_applied": 0}

    def _skill_resolve_conflicts(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """
        Skill: Resolve conflicts with UX spec by actually regenerating files.

        FIX: Actually modifies React code instead of just marking resolved.

        Args:
            shared_memory: SharedSessionMemory
            args: Empty dict (no args needed)

        Returns:
            Dict with success status and conflicts_resolved count
        """
        print("[React Agent] Executing: resolve_conflicts")

        conflicts = shared_memory.implementation_conflicts
        if not conflicts:
            print("  [resolve_conflicts] No conflicts to resolve")
            return {"success": True, "conflicts_resolved": 0, "files_updated": 0}

        # Group conflicts by affected file
        conflicts_by_file = {}
        for conflict in conflicts:
            # Extract file path from conflict (default to App.tsx)
            file_path = getattr(conflict, 'path', None)
            if not file_path:
                file_path = 'App.tsx'  # Default

            # Normalize path (remove leading / or /files/)
            file_path = file_path.lstrip('/')
            if file_path.startswith('files/'):
                file_path = file_path[6:]  # Remove 'files/' prefix

            if file_path not in conflicts_by_file:
                conflicts_by_file[file_path] = []
            conflicts_by_file[file_path].append(conflict)

        print(f"  [resolve_conflicts] Grouped {len(conflicts)} conflicts across {len(conflicts_by_file)} files")

        # Regenerate each affected file with conflict context
        updated_files = dict(shared_memory.react_files or {})
        files_updated = 0

        for filename, file_conflicts in conflicts_by_file.items():
            # Build conflict description for LLM
            conflict_desc = "\n".join([
                f"- [{c.severity.upper()}] {c.description}"
                for c in file_conflicts
            ])

            print(f"  [resolve_conflicts] Regenerating {filename} ({len(file_conflicts)} conflicts)")

            # Get current code
            current_code = updated_files.get(filename, "// File not found")

            # Build regeneration prompt
            prompt = f"""You are a senior React + TypeScript engineer fixing implementation conflicts.

Fix the following issues in {filename}:

CONFLICTS TO RESOLVE:
{conflict_desc}

CURRENT CODE for {filename}:
```tsx
{current_code}
```

UX SPECIFICATION (summary):
{shared_memory.ux_spec.to_summary() if shared_memory.ux_spec else "N/A"}

DATA SCHEMA:
{self._format_data_schema(shared_memory)}

REQUIREMENTS:
1. Fix ALL listed conflicts
2. Preserve working functionality
3. Maintain TypeScript type safety
4. Use Tailwind CSS for styling
5. Return ONLY the full, corrected contents of {filename}

Generate the fixed {filename} file:"""

            try:
                # Call LLM to regenerate file
                response = self.client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=4000,
                    messages=[{"role": "user", "content": prompt}]
                )

                new_code = response.content[0].text.strip()

                # Remove markdown fences if present
                if new_code.startswith('```'):
                    lines = new_code.split('\n')
                    if lines[0].startswith('```'):
                        lines = lines[1:]  # Remove opening fence
                    if lines and lines[-1].startswith('```'):
                        lines = lines[:-1]  # Remove closing fence
                    new_code = '\n'.join(lines)

                updated_files[filename] = new_code
                files_updated += 1
                print(f"  [resolve_conflicts] ✅ Regenerated {filename} ({len(new_code)} chars)")

            except Exception as e:
                print(f"  [resolve_conflicts] ❌ Failed to regenerate {filename}: {e}")
                continue

        if files_updated > 0:
            # CRITICAL (Phase 1.6): Validate regenerated files
            # The schema validator MUST run on regenerated files to prevent
            # the "0 records, 0 files" bug from reappearing
            try:
                print(f"  [resolve_conflicts] Running schema validation on {files_updated} regenerated files...")
                self._validate_data_hooks_schema_consistency(updated_files)
                self._validate_canonical_schema_fields(updated_files)
                print(f"  [resolve_conflicts] Schema validation passed")
            except ValueError as e:
                print(f"  [resolve_conflicts] ❌ SCHEMA VALIDATION FAILED: {e}")
                # This is a critical error - the regenerated code has the same bug we're trying to prevent
                # We should NOT update shared memory with broken code
                return {
                    "success": False,
                    "conflicts_resolved": 0,
                    "files_updated": 0,
                    "error": f"Regenerated files failed schema validation: {e}"
                }

            # Update shared memory with fixed files
            shared_memory.update_react_files(
                updated_files,
                reasoning=f"Resolved {len(conflicts)} conflicts across {files_updated} files (schema validated)"
            )
            print(f"  [resolve_conflicts] Updated {files_updated} files in shared memory")

        # DON'T clear conflicts - let mediator re-run consistency checks
        # The conflicts will naturally disappear if fixes worked

        return {
            "success": True,
            "conflicts_resolved": len(conflicts),
            "files_updated": files_updated
        }

    def _skill_validate_implementation(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Run validation checks."""
        print("[React Agent] Executing: validate_implementation")

        if not shared_memory.react_files:
            return {"success": False, "error": "No files to validate"}

        # Run existing validation methods
        self._validate_no_mock_data(shared_memory.react_files)
        self._validate_file_completeness(shared_memory.react_files)
        self._validate_type_safety(shared_memory.react_files)

        return {"success": True, "validation_passed": True}

    def _inject_actual_schema_for_prompt(self, data_context: Dict) -> str:
        """
        Inject ACTUAL API schema into prompt for initial generation.

        FIX: Prevents React from hallucinating fields by showing exact API structure.

        Args:
            data_context: Real data from API

        Returns:
            Formatted schema documentation for prompt
        """
        if not data_context or not data_context.get('success'):
            return """
// ⚠️ WARNING: No real data available from API
// Use usePipelines() hook and handle loading/error states
"""

        pipelines = data_context.get('pipelines', [])
        if not pipelines:
            return "// No pipelines available in API response"

        # Extract actual schema from first pipeline
        pipeline = pipelines[0]

        import json

        def extract_schema(obj, depth=0, max_depth=2):
            """Recursively extract schema from object"""
            if depth > max_depth:
                return "{ ... }"

            if isinstance(obj, dict):
                schema = {}
                for key, value in obj.items():
                    if isinstance(value, dict):
                        schema[key] = extract_schema(value, depth+1, max_depth)
                    elif isinstance(value, list):
                        if value and len(value) > 0:
                            schema[key] = [extract_schema(value[0], depth+1, max_depth)]
                        else:
                            schema[key] = "[]"
                    elif isinstance(value, str):
                        schema[key] = "string"
                    elif isinstance(value, (int, float)):
                        schema[key] = "number"
                    elif isinstance(value, bool):
                        schema[key] = "boolean"
                    else:
                        schema[key] = type(value).__name__
                return schema
            else:
                return type(obj).__name__

        # Extract schemas
        pipeline_schema = extract_schema(pipeline, max_depth=3)

        # Format as TypeScript types
        schema_json = json.dumps(pipeline_schema, indent=2)

        return f"""
// 🔥 ACTUAL API SCHEMA (from real response):

// Response structure from usePipelines():
// {{
//   pipelines: Pipeline[],
//   summary: {{
//     total_pipelines: number,
//     total_records: number,
//     total_size: string
//   }}
// }}

// ACTUAL Pipeline object structure (from API):
{schema_json}

// 🚨 CRITICAL RULES - ZERO TOLERANCE FOR SCHEMA VIOLATIONS:
// 1. Use ONLY fields that exist in the schema above
// 2. DO NOT invent, infer, or reference ANY field not explicitly listed
// 3. If a field is not in the schema, DO NOT CREATE IT in your types or components
// 4. Always use optional chaining (?.) for nested fields

// 🚫 ABSOLUTELY FORBIDDEN - DO NOT HALLUCINATE THESE COMMON MISTAKES:
// ❌ pipeline.structure         // Does NOT exist! Files are flat arrays, not trees
// ❌ pipeline.tree              // Does NOT exist! No tree structure in schema
// ❌ pipeline.children          // Does NOT exist! Files don't have children property
// ❌ pipeline.file_count        // WRONG! It's pipeline.metrics.file_count
// ❌ pipeline.pipelines         // Nonsense field
// ❌ pipeline.tsx               // Nonsense field
// ❌ pipeline.message           // Only in error responses, not in data

// ✅ CORRECT examples (fields that ACTUALLY exist in schema):
// pipeline.metrics?.file_count    // ✓ Correct path
// pipeline.metrics?.data_size     // ✓ Correct path
// pipeline.status                 // ✓ Exists at root
// pipeline.id                     // ✓ Exists at root
// pipeline.stages?.[0]?.name      // ✓ If stages array exists

// 📋 FOR FILE EXPLORERS - CRITICAL SCHEMA NORMALIZATION REQUIRED:
//
// ⚠️ THE API RETURNS FILES IN "subdirs + files" FORMAT, NOT "children" FORMAT!
//
// Correct API structure:
// {{
//   name: "folder_name",
//   path: "path/to/folder",
//   type: "folder",  // or "directory"
//   subdirs: {{      // OBJECT (dictionary), NOT array!
//     "subfolder1": {{
//       subdirs: {{}},
//       files: [...]
//     }}
//   }},
//   files: [       // ARRAY of file objects
//     {{ name: "file.csv", size: 12345, type: "file" }}
//   ]
// }}
//
// 🚨 CRITICAL: FileNode Interface Definition:
//
// export interface FileNode {{
//   name: string;
//   path: string;
//   type: 'file' | 'directory' | 'folder';  // API may return 'folder' or 'directory'
//   size?: number;
//   size_bytes?: number;
//   file_count?: number;
//   subdirs?: Record<string, FileNode>;  // Backend format (object/dictionary)
//   files?: FileNode[];                   // Backend format (array)
//   children?: FileNode[];                // UI format (derived from subdirs + files)
// }}
//
// 🔧 MANDATORY: Schema Normalization Function
//
// EVERY FileExplorer component MUST include this normalizeNode function:
//
// ```typescript
// const normalizeNode = (node: any): FileNode => {{
//   let children: FileNode[] = [];
//
//   // If API already provides children array, use it recursively
//   if (node.children && Array.isArray(node.children)) {{
//     children = node.children.map((child: any) => normalizeNode(child));
//   }} else {{
//     // Convert subdirs dictionary into children[]
//     if (node.subdirs && typeof node.subdirs === 'object') {{
//       Object.values(node.subdirs).forEach((subdir: any) => {{
//         children.push(normalizeNode(subdir));
//       }});
//     }}
//
//     // Convert files array into children[]
//     if (node.files && Array.isArray(node.files)) {{
//       node.files.forEach((file: any) => {{
//         children.push({{
//           ...file,
//           type: file.type || 'file',
//           path: file.path || `${{node.path}}/${{file.name}}`,
//           children: [],
//         }});
//       }});
//     }}
//   }}
//
//   // Normalize type: "folder" -> "directory" for UI consistency
//   const normalizedType = node.type === 'folder' ? 'directory' : (node.type || 'directory');
//
//   return {{
//     name: node.name,
//     path: node.path,
//     type: normalizedType as 'file' | 'directory',
//     children,
//     file_count: node.file_count,
//     size: node.size_bytes || node.size,
//   }};
// }};
// ```
//
// 📍 USAGE IN COMPONENT:
//
// ```typescript
// export default function FileExplorerTree({{ pipeline }}: Props) {{
//   // Normalize API data before rendering
//   const normalizedFiles = pipeline.files.map(node => normalizeNode(node));
//
//   return (
//     <div>
//       {{normalizedFiles.map(node => renderNode(node, 0))}}
//     </div>
//   );
// }}
// ```
//
// ✅ REQUIRED: Use this pattern in ALL file explorer components:
//   - FileExplorerTree.tsx
//   - FileExplorerPanel.tsx
//   - FileBrowser.tsx
//   - Any component that displays file hierarchies
//
// ❌ DO NOT:
//   - Access node.children directly without normalization
//   - Assume children array exists in API response
//   - Ignore subdirs/files format from backend
"""

    def _format_data_schema(self, shared_memory) -> str:
        """
        Format ACTUAL data schema from API response for prompts.

        FIX: Uses actual API response structure instead of hardcoded template.
        This prevents React from hallucinating fields that don't exist.

        Args:
            shared_memory: SharedSessionMemory with data_context

        Returns:
            JSON schema string showing actual API response structure
        """
        if not hasattr(shared_memory, 'data_context') or not shared_memory.data_context:
            return "No schema available"

        data_context = shared_memory.data_context
        if not data_context.get('pipelines'):
            return "No pipelines in schema"

        # FIX: Extract ACTUAL schema from API response, not a hardcoded template
        # Take first pipeline and introspect its structure
        pipeline = data_context['pipelines'][0]

        import json

        def extract_schema(obj, depth=0, max_depth=3):
            """Recursively extract schema from object"""
            if depth > max_depth:
                return "..."

            if isinstance(obj, dict):
                schema = {}
                for key, value in obj.items():
                    if isinstance(value, dict):
                        schema[key] = extract_schema(value, depth+1, max_depth)
                    elif isinstance(value, list):
                        if value and len(value) > 0:
                            schema[key] = [extract_schema(value[0], depth+1, max_depth)]
                        else:
                            schema[key] = []
                    elif isinstance(value, str):
                        schema[key] = f"string (e.g., '{value[:30]}')"
                    elif isinstance(value, (int, float)):
                        schema[key] = f"number (e.g., {value})"
                    elif isinstance(value, bool):
                        schema[key] = f"boolean (e.g., {value})"
                    else:
                        schema[key] = type(value).__name__
                return schema
            else:
                return type(obj).__name__

        # Extract schema from actual pipeline object
        pipeline_schema = extract_schema(pipeline)

        # Format as readable JSON
        schema_json = json.dumps(pipeline_schema, indent=2)

        return f"""ACTUAL API SCHEMA (from real response):

Pipeline object structure:
{schema_json}

🚨 STRICT SCHEMA BINDING - ZERO TOLERANCE FOR VIOLATIONS:
1. Use ONLY fields that exist in the schema above
2. DO NOT invent, infer, or hallucinate ANY field not explicitly listed
3. If a field is missing from schema, DO NOT CREATE IT

🚫 FORBIDDEN HALLUCINATIONS (these fields DO NOT EXIST):
❌ pipeline.structure     // Does NOT exist - use actual file fields from schema
❌ pipeline.tree          // Does NOT exist - files are not trees
❌ pipeline.children      // Does NOT exist - files don't have children
❌ pipeline.file_count    // WRONG path - it's pipeline.metrics.file_count
❌ pipeline.tsx           // Nonsense field
❌ pipeline.message       // Only in errors, not data

✅ CORRECT (fields that ACTUALLY exist):
✓ pipeline.metrics.file_count
✓ pipeline.status
✓ pipeline.id
✓ pipeline.stages[0].name (if stages exists)"""

    def _skill_finish(self, shared_memory, args: Dict) -> Dict[str, Any]:
        """Mark implementation as complete."""
        print("[React Agent] Executing: finish")

        shared_memory.react_status = "done"
        shared_memory.react_satisfactory = True

        return {"success": True, "status": "done"}


# Example usage
if __name__ == "__main__":
    from src.agents.ux_designer import UXDesignerAgent

    # Example: Generate React dashboard
    ux_agent = UXDesignerAgent()
    react_agent = ReactDeveloperAgent(styling_framework="tailwind")

    # Mock context
    context = {
        'user_prompt': "Create a pipeline monitoring dashboard with data source cards",
        'data_sources': {
            'fracfocus': {
                'type': 'Chemical Data',
                'records': 7255562,
                'status': 'success'
            },
            'rrc/production': {
                'type': 'Production Data',
                'records': 216079924,
                'status': 'success'
            }
        }
    }

    # Generate design spec
    print("Generating design spec...")
    requirements = {
        'user_intent': "Show pipeline data sources with status",
        'screen_type': "data_list",
        **context
    }
    design_spec = ux_agent.design(requirements=requirements)

    # Generate React code
    print("\nGenerating React code...")
    files = react_agent.build(design_spec, context)

    # Save to disk
    output_dir = Path(__file__).parent.parent.parent / "generated_react_dashboard"
    react_agent.save_files(files, output_dir)

    print(f"\n✅ React dashboard generated at: {output_dir}")
    print("📖 See SETUP.md for installation instructions")
