"""
UX Designer Agent - The Visionary (Tarkovsky)

Responsibility: Design WHAT to build
- Focuses on user needs, not implementation details
- Queries UX patterns from Pinecone
- Creates design specifications
- Framework-agnostic

This agent knows nothing about Gradio, Python, or CSS constraints.
It only knows about user experience, design patterns, and interaction flows.
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
import sys
import anthropic
import os
import re
import json

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone
from src.agents.context.discovery_tools import DiscoveryTools
from src.agents.context.protocol import SessionContext, ContextAware, TaskType
from src.agents.ux_autonomous import AutonomousUXMixin, Plan, UXEvaluationResult


class DesignSpec:
    """
    Design Specification - Output from UX Designer Agent
    This is the handoff format between UX Designer and Implementation Agent
    """
    def __init__(
        self,
        screen_type: str,
        intent: str,
        components: List[Dict],
        interactions: List[Dict],
        patterns: List[str],
        styling: Dict,
        recommended_pattern: str = None,
        design_reasoning: str = None,
        data_sources: Dict[str, Any] = None,  # Phase 2: Include discovered metadata
        interaction_model: List[Dict] = None  # Behavioral state machines from Pinecone
    ):
        self.screen_type = screen_type
        self.intent = intent
        self.components = components
        self.interactions = interactions
        self.patterns = patterns
        self.styling = styling
        self.design_reasoning = design_reasoning
        self.recommended_pattern = recommended_pattern  # UX agent's pattern recommendation
        self.data_sources = data_sources or {}  # Phase 2: Discovered data with schemas/statuses
        self.interaction_model = interaction_model or []  # Behavioral state machines for React

    def to_dict(self) -> Dict:
        """Full serialization (for debugging, logging)"""
        return {
            "screen_type": self.screen_type,
            "intent": self.intent,
            "components": self.components,
            "interactions": self.interactions,
            "patterns": self.patterns,
            "styling": self.styling,
            "data_sources": self.data_sources,  # Include discovered metadata
            "interaction_model": self.interaction_model  # Behavioral state machines for React
        }

    def to_compact(self) -> Dict:
        """
        Ultra-compact format for inter-agent message passing (Opus approach)
        Reduces token usage by 90-95% vs to_dict()
        """
        return {
            "v": "1.0",  # version
            "c": [  # components (abbreviated)
                {
                    "t": self._abbreviate_type(comp.get("type", "")),
                    "id": comp.get("id", f"c{i}"),
                    "a": comp.get("actions", [])[:3]  # Limit to 3 actions
                }
                for i, comp in enumerate(self.components)
            ],
            "i": [  # interactions (simplified)
                {
                    "on": inter.get("trigger", "")[:20],  # Limit length
                    "do": inter.get("action", "")[:20],
                    "to": inter.get("target", "")[:20]
                }
                for inter in self.interactions
            ],
            "p": [self._abbreviate_pattern(p) for p in self.patterns[:5]]  # Limit to 5 patterns
        }

    def to_summary(self) -> str:
        """
        Human-readable summary for prompts (more readable than compact, smaller than to_dict)
        Use this when agents need to understand, not just process
        """
        comp_types = [c.get("type", "unknown") for c in self.components]
        intent_preview = self.intent[:100] + "..." if len(self.intent) > 100 else self.intent

        return f"""Screen: {self.screen_type}
Intent: {intent_preview}
Components: {len(self.components)} ({', '.join(comp_types[:3])})
Interactions: {len(self.interactions)}
Patterns: {', '.join(self.patterns)}""".strip()

    def to_implementation_guidance(self) -> str:
        """
        Compressed design guidance for implementation agents (React/Gradio developers)
        Extracts only actionable implementation details from design_reasoning

        Token reduction: ~1000 tokens → ~300-400 tokens (60-70% savings)
        Keeps: layout, components, styling, icons
        Drops: UX philosophy, rationale, Material Design theory
        """
        if not self.design_reasoning:
            return self.to_summary()

        # Extract key sections that implementers need
        reasoning_lines = self.design_reasoning.split('\n')
        implementation_lines = []

        # Keep lines that contain actionable implementation details
        keep_keywords = [
            'LAYOUT:', 'COMPONENTS:', 'ICONS:', 'VISUAL', 'INTERACTIONS:',
            'component', 'icon:', 'card', 'button', 'header', 'grid', 'flex',
            'Material Symbols', 'spacing', 'padding', 'margin', 'color',
            'typography', 'font', 'shadow', 'elevation', 'rounded'
        ]

        for line in reasoning_lines:
            # Keep section headers and lines with implementation keywords
            if any(keyword.lower() in line.lower() for keyword in keep_keywords):
                implementation_lines.append(line)
            # Stop if we hit anti-patterns or philosophy sections
            elif 'anti-pattern' in line.lower() or 'principle' in line.lower():
                continue

        # If we filtered too much, return first 400 chars of reasoning
        if len(implementation_lines) < 5:
            return self.design_reasoning[:400] + "..."

        return '\n'.join(implementation_lines[:15])  # Limit to ~15 key lines

    @staticmethod
    def _abbreviate_type(type_name: str) -> str:
        """Abbreviate component types for compact format"""
        abbrevs = {
            "card_grid": "cg",
            "navigation_dropdown": "nav_dd",
            "file_browser": "fb",
            "button": "btn",
            "detail_panel": "dp",
            "data_table": "dt",
            "filter_bar": "flt",
            "search_box": "srch"
        }
        return abbrevs.get(type_name, type_name[:3])

    @staticmethod
    def _abbreviate_pattern(pattern: str) -> str:
        """Abbreviate pattern names for compact format"""
        abbrevs = {
            "master-detail": "md",
            "progressive-disclosure": "pd",
            "breadcrumb-navigation": "bc",
            "card-grid": "cg",
            "hierarchical-navigation": "hn"
        }
        return abbrevs.get(pattern, pattern[:2])


class UXDesignerAgent(AutonomousUXMixin):
    """
    UX Designer Agent - Designs WHAT to build

    This agent is a UX expert who:
    - Understands user needs
    - Knows design patterns (Material Design, navigation, accessibility)
    - Creates design specifications
    - Is framework-agnostic (doesn't know about Gradio)

    Architecture Enhancements:
    - Chain of Thought (CoT): Reasons through UX decisions
    - Planning: Creates structured design plan
    - Memory: Remembers previous designs in session
    """

    def __init__(self, trace_collector=None, use_autonomous_mode=False, use_json_mode=False):
        self.design_kb = DesignKnowledgeBasePinecone()

        # Phase 6: JSON structured output mode (v2 prompt)
        self.use_json_mode = use_json_mode

        # Initialize Discovery Tools for context swimming
        self.discovery_tools = DiscoveryTools()

        # Initialize Claude API
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=api_key)

        # Memory: Track designs across session
        self.design_history = []

        # Token tracking (for optimization monitoring)
        self.total_tokens_used = 0

        # Trace collector (optional - for capturing reasoning)
        self.trace_collector = trace_collector

        # Protocol: Context-aware execution
        self.ctx: Optional[SessionContext] = None

        # Phase 5: Autonomous mode flag
        self.use_autonomous_mode = use_autonomous_mode

        # Phase 5: Skill registry (only in autonomous mode)
        self.skills = {}
        if use_autonomous_mode:
            self._build_skill_registry()
            print("[UX Designer Agent] Initialized in AUTONOMOUS mode with internal planning loop")
        else:
            print("[UX Designer Agent] Initialized with Discovery Tools - Ready to design user experiences")

    def with_context(self, ctx: SessionContext) -> "UXDesignerAgent":
        """
        Inject context before execution (ContextAware protocol).

        Args:
            ctx: Session context with discovery, intent, execution settings

        Returns:
            Self for method chaining
        """
        self.ctx = ctx
        print(f"[UX Designer] Context injected - Session: {ctx.session_id[:8]}...")
        print(f"  Discovered sources: {ctx.discovery.sources}")
        print(f"  Intent scope: {ctx.intent.scope}")
        return self

    def execute(self, shared_memory: Optional['SharedSessionMemory'] = None) -> Dict[str, Any]:
        """
        Execute with context (ContextAware protocol).

        Phase 5: Routes to autonomous run() if use_autonomous_mode=True,
        otherwise uses procedural design() method.

        Phase 6.2: Accepts external shared_memory for orchestrator integration.

        Args:
            shared_memory: Optional SharedSessionMemory instance from orchestrator

        Returns:
            Design specification as dict

        Raises:
            ValueError: If context not provided
        """
        if not self.ctx:
            raise ValueError(
                "Context not provided. Call with_context() first.\n"
                "Usage: agent.with_context(ctx).execute()"
            )

        print("\n[UX Designer] Executing with SessionContext...")

        # Phase 5: Route to autonomous mode if enabled
        if self.use_autonomous_mode:
            # Import SharedSessionMemory
            from src.agents.shared_memory import SharedSessionMemory

            # Phase 6.2: Use orchestrator's shared_memory if provided
            if shared_memory is None:
                # Fallback: create local shared_memory for standalone use
                shared_memory = SharedSessionMemory(session_id=self.ctx.session_id)
                shared_memory.user_requirements = {
                    "intent": self.ctx.intent.original_query
                }
                shared_memory.user_context = {
                    "data_sources": {
                        source: {
                            "name": source,
                            "row_count": self.ctx.discovery.record_counts.get(source, 0)
                        }
                        for source in self.ctx.discovery.sources
                    }
                }
                shared_memory.knowledge = {}  # Will be populated by orchestrator

            # Store for use in skills
            self.current_shared_memory = shared_memory

            # Run autonomous agent
            design_spec = self.run(shared_memory, max_steps=3)

            # Phase 6.2: Write design_spec to shared memory before returning
            if design_spec and shared_memory:
                shared_memory.update_ux_spec(design_spec, "Generated by UX Designer")

            # Return as dict
            return design_spec.to_dict() if design_spec else {}

        # Phase 3.1: Procedural mode (backward compatible)
        # Build requirements from context
        requirements = {
            "intent": self.ctx.intent.original_query,
            "screen_type": self._infer_screen_type(self.ctx.intent.task_type),
            "data_sources": {
                source: {
                    "name": source,
                    "row_count": self.ctx.discovery.record_counts.get(source, 0)
                }
                for source in self.ctx.discovery.sources
            }
        }

        # Call existing design method
        design_spec = self.design(requirements)

        # Phase 6.2: Write design_spec to shared memory if provided (procedural mode)
        if design_spec and shared_memory:
            shared_memory.update_ux_spec(design_spec, "Generated by UX Designer")

        # Return as dict
        return design_spec.to_dict()

    def _infer_screen_type(self, task_type: TaskType) -> str:
        """
        Convert TaskType enum to screen_type string.

        Args:
            task_type: TaskType enum

        Returns:
            Screen type string for design method
        """
        mapping = {
            TaskType.DASHBOARD: "data_dashboard",
            TaskType.ANALYSIS: "analysis_view",
            TaskType.REPORT: "report_view"
        }
        return mapping.get(task_type, "data_dashboard")

    def _parse_query_constraints(self, prompt: str) -> Dict[str, Any]:
        """
        Extract explicit constraints from user prompt.

        This is generic NLP pattern matching - works for any domain/source.

        Args:
            prompt: User's natural language prompt

        Returns:
            Dict with extracted constraints:
            {
                'source_filter': Optional[str],  # e.g., 'fracfocus'
                'intent': str,  # 'data_analysis' or 'pipeline_monitoring'
                'exclusivity': bool  # True if 'only' keyword present
            }
        """
        constraints = {}

        # Source filtering patterns (generic - works for any source name)
        source_patterns = [
            r'from\s+(\w+)',           # "from fracfocus"
            r'only\s+(\w+)',           # "only medical_data"
            r'(\w+)\s+data(?:\s|$)',   # "fracfocus data" or "chemical data"
            r'(\w+)\s+dataset'         # "fracfocus dataset"
        ]

        for pattern in source_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                source_name = match.group(1).lower()
                # Filter out generic terms that aren't source names
                if source_name not in ['chemical', 'pipeline', 'data', 'monitoring', 'dashboard']:
                    constraints['source_filter'] = source_name
                    # Check for exclusivity
                    if 'only' in prompt.lower():
                        constraints['exclusivity'] = True
                    break

        # Intent classification (data analysis vs infrastructure monitoring)
        analysis_keywords = ['show', 'display', 'visualize', 'analyze', 'explore', 'view', 'chart']
        monitoring_keywords = ['monitor', 'status', 'pipeline', 'health', 'track']

        prompt_lower = prompt.lower()
        if any(kw in prompt_lower for kw in analysis_keywords):
            constraints['intent'] = 'data_analysis'
        elif any(kw in prompt_lower for kw in monitoring_keywords):
            constraints['intent'] = 'pipeline_monitoring'
        else:
            # Default to data analysis if ambiguous
            constraints['intent'] = 'data_analysis'

        return constraints

    def design(self, requirements: Dict[str, Any], knowledge: Dict = None) -> DesignSpec:
        """
        Design WHAT to build based on requirements

        Args:
            requirements: Dict with user needs, context, data sources
            knowledge: Pre-fetched design knowledge from orchestrator (optional)
                      If provided, skip querying Pinecone

        Returns:
            DesignSpec: Framework-agnostic design specification
        """
        print("\n[UX Designer] Starting design process...")

        # Step 1: Parse query constraints (NEW: Query Understanding Layer)
        user_prompt = requirements.get('intent', 'data visualization dashboard')
        query_constraints = self._parse_query_constraints(user_prompt)

        if query_constraints.get('source_filter'):
            print(f"  [UX Designer] 🎯 Detected source filter: '{query_constraints['source_filter']}'")

        # Step 2: Discover data sources if not provided (CONTEXT SWIMMING)
        if 'data_sources' not in requirements or not requirements['data_sources']:
            print("  [UX Designer] No data sources provided - discovering autonomously...")
            discovered = self.discover_data_sources(user_prompt, top_k=10, constraints=query_constraints)

            # Format discovered sources for requirements
            requirements['data_sources'] = {}
            for source in discovered['sources']:
                source_name = source['name']
                status_info = discovered['statuses'].get(source_name, {})

                # Phase 2 fix: Include BOTH status string AND stages list for React Developer
                # Phase 2 enhancement: Include folder structure info for correct file paths
                files_by_stage = status_info.get('files_by_stage', {}) if isinstance(status_info, dict) else {}

                requirements['data_sources'][source_name] = {
                    'name': source_name,
                    'relevance': source['relevance'],
                    'format': 'csv/parquet',  # Discovered sources are parsed data
                    'columns': discovered['schemas'].get(source_name, {}).get('columns', []),
                    'row_count': discovered['schemas'].get(source_name, {}).get('row_count', 0),
                    'status': status_info.get('status', 'unknown') if isinstance(status_info, dict) else status_info,
                    'stages': status_info.get('stages', []) if isinstance(status_info, dict) else [],  # Include stages!
                    'files_by_stage': files_by_stage,  # File counts per stage
                    'structure_note': f'Nested structure: {source_name}/[data_type]/{{downloads,extracted,parsed}}'  # Explain nesting
                }

            print(f"  [UX Designer] Discovered {len(requirements['data_sources'])} data sources")
        else:
            print(f"  [UX Designer] Using provided data sources: {len(requirements['data_sources'])}")

        # Step 2: Use provided knowledge (from orchestrator) or query if not provided
        if knowledge:
            print("  [UX Designer] Using provided knowledge (no queries)")
            ux_patterns = knowledge.get('ux_patterns', {})
            design_principles = knowledge.get('design_principles', {})
            # Extract REAL DATA and GRADIENT CONTEXT from orchestrator
            data_context = knowledge.get('data_context')
            gradient_context = knowledge.get('gradient_context')
        else:
            # Fallback: query directly (for backward compatibility)
            print("  [UX Designer] WARNING: No knowledge provided, querying directly")
            ux_patterns = self._query_ux_patterns(requirements)
            design_principles = self._query_design_principles()
            data_context = None
            gradient_context = None

        # Step 2.5: Query INTERACTION PATTERNS from Pinecone (behavioral state machines)
        # This gives UX Designer behavioral memory for how UI should respond to events
        interaction_patterns = self._query_interaction_patterns(user_prompt)

        # Step 3: Use CoT to reason through UX decisions WITH real data, gradient hints, AND interaction patterns
        design_reasoning = self._design_with_cot(
            requirements, ux_patterns, design_principles,
            data_context, gradient_context, interaction_patterns
        )

        # Step 4: Create design specification (with gradient-aware component injection)
        design_spec = self._create_design_spec(
            design_reasoning, requirements, ux_patterns, gradient_context, interaction_patterns
        )

        # Step 5: Add to memory
        self._add_to_memory(design_spec)

        print(f"[UX Designer] Design complete: {design_spec.screen_type}")
        return design_spec

    def discover_data_sources(self, intent: str, top_k: int = 10, constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Autonomously discover data sources relevant to the user's intent.

        This is the "context swimming" behavior - the agent explores the repository
        to find what data exists rather than being told.

        Args:
            intent: User's intent (e.g., "dashboard for chemical analysis")
            top_k: Maximum number of sources to discover
            constraints: Optional query constraints (from _parse_query_constraints)

        Returns:
            Dict with discovered sources and their schemas:
            {
                'sources': [{name, relevance, ...}, ...],
                'schemas': {source_name: schema, ...},
                'statuses': {source_name: status, ...}
            }
        """
        print(f"\n[UX Designer] Discovering data sources for: '{intent}'")

        # Trace: Discovery start
        if self.trace_collector:
            self.trace_collector.trace_thinking(
                agent="UXDesigner",
                method="discover_data_sources",
                thought=f"🔍 Starting autonomous discovery for: '{intent[:80]}...'" if len(intent) > 80 else f"🔍 Starting autonomous discovery for: '{intent}'"
            )

        # Use discovery tools to find relevant sources
        # Pass source_filter to discovery tools for constraint-based filtering
        sources = self.discovery_tools.find_data_sources(
            query=intent,
            top_k=top_k,
            min_relevance=0.6,  # Only high-relevance sources
            source_filter=constraints.get('source_filter') if constraints else None
        )

        print(f"[UX Designer] Discovered {len(sources)} relevant sources")

        # Trace: Sources found
        if self.trace_collector:
            source_names = [s['name'] for s in sources[:5]]
            if len(sources) > 5:
                source_names.append(f"+ {len(sources) - 5} more")
            self.trace_collector.trace_thinking(
                agent="UXDesigner",
                method="discover_data_sources",
                thought=f"📊 Found {len(sources)} relevant data sources: {', '.join(source_names)}"
            )

        # Get schemas for all discovered sources (Phase 2 fix: include ALL sources, not just top 5)
        schemas = {}
        statuses = {}
        for source in sources:  # Process ALL discovered sources (RRC was being excluded!)
            source_name = source['name']

            # Trace: Starting schema retrieval
            if self.trace_collector:
                self.trace_collector.trace_thinking(
                    agent="UXDesigner",
                    method="discover_data_sources",
                    thought=f"📋 Getting schema for '{source_name}'..."
                )

            # Get schema
            schema = self.discovery_tools.get_schema(source_name)
            if schema:
                schemas[source_name] = {
                    'columns': schema['columns'],
                    'dtypes': schema['dtypes'],
                    'row_count': schema['row_count']
                }

                # Trace: Schema found
                if self.trace_collector:
                    self.trace_collector.trace_thinking(
                        agent="UXDesigner",
                        method="discover_data_sources",
                        thought=f"✅ {source_name}: {len(schema['columns'])} columns, {schema['row_count']:,} rows"
                    )
            else:
                # Trace: No schema
                if self.trace_collector:
                    self.trace_collector.trace_thinking(
                        agent="UXDesigner",
                        method="discover_data_sources",
                        thought=f"⚠️  {source_name}: No parsed data available"
                    )

            # Get status (Phase 2 fix: Store ENTIRE status dict including stages!)
            status = self.discovery_tools.check_status(source_name)
            if status:
                statuses[source_name] = status  # Store full dict {status: 'complete', stages: [...], ...}

                # Trace: Status found
                if self.trace_collector:
                    status_emoji = {
                        'complete': '✅',
                        'in_progress': '⏳',
                        'not_started': '⭕'
                    }.get(status['status'], '❓')

                    stages = status.get('stages', [])
                    stage_info = f" (stages: {', '.join(stages)})" if stages else ""

                    self.trace_collector.trace_thinking(
                        agent="UXDesigner",
                        method="discover_data_sources",
                        thought=f"{status_emoji} {source_name}: {status['status']}{stage_info}"
                    )

        # Trace: Discovery summary
        if self.trace_collector:
            # Count sources with data
            sources_with_data = len([s for s in schemas.values() if s.get('row_count', 0) > 0])

            # Build detailed source list with record counts
            source_details = []
            for source in sources[:5]:  # Show top 5 sources
                source_name = source['name']
                relevance = source['relevance']
                schema = schemas.get(source_name, {})
                row_count = schema.get('row_count', 0)
                status = statuses.get(source_name, {})
                status_str = status.get('status', 'unknown') if isinstance(status, dict) else status

                if row_count > 0:
                    source_details.append(f"  • {source_name}: {relevance:.1%} relevant | {row_count:,} records | {status_str}")
                else:
                    source_details.append(f"  • {source_name}: {relevance:.1%} relevant | No parsed data yet | {status_str}")

            if len(sources) > 5:
                source_details.append(f"  ... and {len(sources) - 5} more sources")

            reasoning = f"""Discovery Complete - Context Swimming Results:

📊 Total Sources Found: {len(sources)}
✅ Sources with Parsed Data: {sources_with_data}/{len(sources)}
📋 Schemas Retrieved: {len(schemas)}
⚙️  Statuses Checked: {len(statuses)}

Discovered Sources (with data):
{chr(10).join(source_details)}

Ready to design with discovered context."""

            self.trace_collector.trace_reasoning(
                agent="UXDesigner",
                method="discover_data_sources",
                reasoning=reasoning,
                knowledge_used=[s['name'] for s in sources[:5]]
            )

        return {
            'sources': sources,
            'schemas': schemas,
            'statuses': statuses
        }

    def _query_ux_patterns(self, requirements: Dict) -> Dict:
        """Query Pinecone for relevant UX patterns (BATCHED)"""
        print("  [UX Designer] Querying UX patterns...")

        screen_type = requirements.get('screen_type', 'dashboard')

        # SINGLE BATCHED QUERY: Combine all pattern needs into one query
        query_text = "navigation master-detail drill-down hierarchy actions buttons layout"

        results = self.design_kb.query(
            query_text,
            category="pattern",
            top_k=5  # Get top 5 patterns in one call
        )

        # Cache and organize results
        patterns = {}
        if results:
            patterns['all_patterns'] = results[:5]

        print(f"  [UX Designer] Retrieved {len(results) if results else 0} patterns (1 batched query)")
        return patterns

    def _query_design_principles(self) -> Dict:
        """Query Material Design 3 principles"""
        print("  [UX Designer] Querying design principles...")

        # BATCH QUERY: Single Pinecone call for all design principles
        results = self.design_kb.query(
            "color palette typography spacing layout",
            top_k=3  # Get top 3 most relevant principles
        )

        # Cache results
        principles = {}
        if results:
            for i, result in enumerate(results[:3]):
                principles[f'principle_{i+1}'] = result

        print(f"  [UX Designer] Retrieved {len(principles)} principles (1 batched query)")
        return principles

    def _query_interaction_patterns(self, user_intent: str) -> Dict[str, Any]:
        """
        Query INTERACTION PATTERNS from Pinecone (behavioral state machines)

        This retrieves:
        1. Patterns relevant to the user's intent
        2. Canonical patterns: file selection, drilldown, async, pagination

        These patterns define HOW the UI should behave - state changes, data fetches,
        UI feedback, and dependency rules that React must implement.

        Args:
            user_intent: User's intent string

        Returns:
            Dict with categorized interaction patterns
        """
        print("  [UX Designer] Querying interaction patterns (behavioral state machines)...")

        interaction_patterns = {
            'intent_patterns': [],
            'file_selection': [],
            'pagination': [],
            'async_loading': [],
            'drilldown': []
        }

        try:
            # 1. Query patterns relevant to user's intent
            intent_results = self.design_kb.query_interaction_patterns(
                query_text=user_intent,
                top_k=3
            )
            interaction_patterns['intent_patterns'] = intent_results
            print(f"    [OK] Intent patterns: {len(intent_results)}")

            # 2. Query canonical file selection pattern (CRITICAL for file explorers)
            file_results = self.design_kb.query_interaction_patterns(
                query_text="file selection data fetch refresh when file changes",
                top_k=2,
                category="navigation"
            )
            interaction_patterns['file_selection'] = file_results
            print(f"    [OK] File selection patterns: {len(file_results)}")

            # 3. Query pagination pattern
            pagination_results = self.design_kb.query_interaction_patterns(
                query_text="pagination page change data fetch",
                top_k=1,
                category="data-display"
            )
            interaction_patterns['pagination'] = pagination_results
            print(f"    [OK] Pagination patterns: {len(pagination_results)}")

            # 4. Query async loading pattern (skeletons, loading states)
            async_results = self.design_kb.query_interaction_patterns(
                query_text="async loading skeleton error empty state",
                top_k=2,
                category="feedback"
            )
            interaction_patterns['async_loading'] = async_results
            print(f"    [OK] Async loading patterns: {len(async_results)}")

            # 5. Query drilldown/expand pattern
            drilldown_results = self.design_kb.query_interaction_patterns(
                query_text="drilldown expand collapse progressive disclosure",
                top_k=2,
                category="navigation"
            )
            interaction_patterns['drilldown'] = drilldown_results
            print(f"    [OK] Drilldown patterns: {len(drilldown_results)}")

            # Count total patterns retrieved
            total = sum(len(v) for v in interaction_patterns.values())
            print(f"  [UX Designer] Retrieved {total} interaction patterns total")

            # Trace
            if self.trace_collector:
                pattern_summary = [
                    f"intent:{len(interaction_patterns['intent_patterns'])}",
                    f"file:{len(interaction_patterns['file_selection'])}",
                    f"page:{len(interaction_patterns['pagination'])}",
                    f"async:{len(interaction_patterns['async_loading'])}",
                    f"drill:{len(interaction_patterns['drilldown'])}"
                ]
                self.trace_collector.trace_thinking(
                    agent="UXDesigner",
                    method="_query_interaction_patterns",
                    thought=f"🔄 Loaded behavioral patterns: {', '.join(pattern_summary)}"
                )

        except Exception as e:
            print(f"  [UX Designer] WARNING: Could not query interaction patterns: {e}")
            # Continue without patterns - graceful degradation

        return interaction_patterns

    def _design_with_cot(
        self,
        requirements: Dict,
        ux_patterns: Dict,
        design_principles: Dict,
        data_context: Dict = None,
        gradient_context: Dict = None,
        interaction_patterns: Dict = None
    ) -> str:
        """
        Chain of Thought: Reason through UX design decisions

        Args:
            requirements: User requirements with discovered data sources
            ux_patterns: UX patterns from KB
            design_principles: Design principles from KB
            data_context: REAL DATA from API (pipelines with actual metrics)
            gradient_context: Domain-aware pattern boosts from gradient system
            interaction_patterns: Behavioral state machines from Pinecone

        Returns design reasoning as structured text
        """
        print("  [UX Designer] Applying Chain of Thought reasoning...")

        # Extract context
        screen_type = requirements.get('screen_type', 'dashboard')
        user_intent = requirements.get('intent', 'view and manage data')
        data_sources = requirements.get('data_sources', {})
        user_feedback = requirements.get('user_feedback', None)

        # Build feedback section if provided
        feedback_section = ""
        if user_feedback:
            feedback_section = f"""

IMPORTANT - USER FEEDBACK ON PREVIOUS DESIGN:
"{user_feedback}"

This is critical feedback about issues with the previous design. You MUST address these concerns in your new design.
Think carefully about what the user is asking for and incorporate those improvements.
"""

        # Build rich data source section (discovered metadata + real API data)
        data_section = ""
        if data_sources:
            ds_lines = []
            for name, info in list(data_sources.items())[:3]:  # Show first 3 with details
                row_count = info.get('row_count', 0)
                cols = info.get('columns', [])
                status = info.get('status', 'unknown')
                stages = info.get('stages', [])

                ds_lines.append(
                    f"- {name}: {row_count:,} rows, {len(cols)} columns "
                    f"({', '.join(cols[:3])}{'...' if len(cols) > 3 else ''}), "
                    f"status: {status}, stages: {' → '.join(stages) or 'none'}"
                )

            if len(data_sources) > 3:
                ds_lines.append(f"... and {len(data_sources) - 3} more sources")

            data_section = "\n\nDATA SOURCES (discovered):\n" + "\n".join(ds_lines)

        # Build real data section from API context
        real_data_section = ""
        if data_context and data_context.get('success'):
            pipelines = data_context.get('pipelines', [])
            real_data_lines = []
            for pipeline in pipelines[:3]:  # Show first 3 pipelines
                metrics = pipeline.get('metrics', {})
                stages = ', '.join([s['name'] for s in pipeline.get('stages', [])])
                real_data_lines.append(
                    f"- {pipeline.get('display_name', pipeline['id'])}: "
                    f"{metrics.get('file_count', 0)} files, "
                    f"{metrics.get('data_size', '0 B')}, "
                    f"stages: {stages or 'none'}"
                )
            if len(pipelines) > 3:
                real_data_lines.append(f"... and {len(pipelines) - 3} more pipelines")

            real_data_section = "\n\nREAL PIPELINE DATA (from API):\n" + "\n".join(real_data_lines)

        # Build gradient hints section
        gradient_hints = ""
        if gradient_context and gradient_context.get('domain_signals'):
            domain_signals = gradient_context['domain_signals']
            domain = domain_signals.get('domain', 'generic')
            structure = domain_signals.get('structure', 'flat')
            max_depth = domain_signals.get('metrics', {}).get('max_depth', 0)

            hints = ["\n\n🧭 DOMAIN-AWARE DESIGN HINTS:"]
            hints.append(f"- Data domain: {domain}")
            hints.append(f"- Folder structure: {structure} ({max_depth} levels deep)")

            if gradient_context.get('boost_hierarchical_navigation'):
                hints.append("- ✓ BOOST: Hierarchical navigation (use breadcrumbs, expandable trees)")
            if gradient_context.get('boost_tree_views'):
                hints.append("- ✓ BOOST: Tree/accordion views (deep nesting detected)")
            if gradient_context.get('boost_data_drill_down'):
                hints.append("- ✓ BOOST: Data drill-down (enable clicking into nested data)")

            gradient_hints = "\n".join(hints)

        # Build INTERACTION PATTERNS section (behavioral state machines)
        interaction_section = ""
        if interaction_patterns:
            interaction_lines = ["\n\n🔄 BEHAVIORAL PATTERNS (from knowledge base):"]
            interaction_lines.append("These patterns define HOW the UI must behave. Include them in your INTERACTIONS section.")
            interaction_lines.append("")

            # Add file selection pattern (CRITICAL)
            file_patterns = interaction_patterns.get('file_selection', [])
            if file_patterns:
                fp = file_patterns[0]  # Use first/best match
                interaction_lines.append("FILE SELECTION BEHAVIOR:")
                interaction_lines.append(f"  Event: {fp.get('event', 'onFileSelect')}")
                interaction_lines.append(f"  State Changes: {', '.join(fp.get('state_changes', []))}")
                dep_rules = fp.get('dependency_rules', [])
                if dep_rules:
                    interaction_lines.append(f"  Dependency Rules: {', '.join(dep_rules[:3])}")
                interaction_lines.append("")

            # Add pagination pattern
            page_patterns = interaction_patterns.get('pagination', [])
            if page_patterns:
                pp = page_patterns[0]
                interaction_lines.append("PAGINATION BEHAVIOR:")
                interaction_lines.append(f"  Event: {pp.get('event', 'onPageChange')}")
                interaction_lines.append(f"  State Changes: {', '.join(pp.get('state_changes', []))}")
                dep_rules = pp.get('dependency_rules', [])
                if dep_rules:
                    interaction_lines.append(f"  Dependency Rules: {', '.join(dep_rules[:2])}")
                interaction_lines.append("")

            # Add async loading pattern
            async_patterns = interaction_patterns.get('async_loading', [])
            if async_patterns:
                ap = async_patterns[0]
                interaction_lines.append("ASYNC LOADING BEHAVIOR:")
                ui_feedback = ap.get('ui_feedback', [])
                if ui_feedback:
                    interaction_lines.append(f"  UI Feedback: {', '.join(ui_feedback[:4])}")
                interaction_lines.append("")

            # Add drilldown pattern
            drill_patterns = interaction_patterns.get('drilldown', [])
            if drill_patterns:
                dp = drill_patterns[0]
                interaction_lines.append("DRILLDOWN/EXPAND BEHAVIOR:")
                interaction_lines.append(f"  Event: {dp.get('event', 'onExpandToggle')}")
                interaction_lines.append(f"  State Changes: {', '.join(dp.get('state_changes', []))}")
                interaction_lines.append("")

            interaction_section = "\n".join(interaction_lines)

        # ================================================================
        # DUAL-MODE PROMPT: JSON (v3 compressed) vs Legacy (v1) text output
        # ================================================================
        if self.use_json_mode:
            # Use v3 compressed prompt (70% smaller, same functionality)
            prompt = self._build_v3_compressed_prompt(
                screen_type=screen_type,
                user_intent=user_intent,
                data_section=data_section,
                real_data_section=real_data_section,
                gradient_hints=gradient_hints,
                interaction_section=interaction_section,
                feedback_section=feedback_section
            )
            print("  [UX Designer] Using JSON mode (v3 compressed prompt)")
        else:
            # BOLD, CONFIDENT DESIGN MODE (legacy v1)
            prompt = self._build_v1_legacy_prompt(
                screen_type=screen_type,
                user_intent=user_intent,
                data_sources=data_sources,
                data_section=data_section,
                real_data_section=real_data_section,
                gradient_hints=gradient_hints,
                interaction_section=interaction_section,
                feedback_section=feedback_section
            )

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500 if self.use_json_mode else 1000,
                messages=[{"role": "user", "content": prompt}]
            )

            reasoning = message.content[0].text

            # Token usage logging (Opus optimization)
            usage = message.usage
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
            total_tokens = input_tokens + output_tokens
            self.total_tokens_used += total_tokens
            print(f"  [UX Designer] Tokens: input={input_tokens}, output={output_tokens}, total={total_tokens}")
            print(f"  [UX Designer] Generated {len(reasoning)} chars of design reasoning")

            # Emit trace with actual reasoning
            if self.trace_collector:
                pattern_names = [p for p in ux_patterns.keys() if p.lower() in reasoning.lower()]
                self.trace_collector.trace_reasoning(
                    agent="UXDesigner",
                    method="_design_with_cot",
                    reasoning=reasoning,
                    knowledge_used=pattern_names
                )

            return reasoning

        except Exception as e:
            print(f"  [UX Designer] CoT failed: {e}")
            return "Design reasoning unavailable - proceeding with pattern-based design"

    def _build_v1_legacy_prompt(
        self,
        screen_type: str,
        user_intent: str,
        data_sources: Dict,
        data_section: str,
        real_data_section: str,
        gradient_hints: str,
        interaction_section: str,
        feedback_section: str
    ) -> str:
        """
        Build v1 legacy prompt for text-based output (backward compatibility).
        """
        prompt = f"""You are a senior product designer who previously led design at Stripe/Linear/Vercel.

Design a {screen_type} for: {user_intent}

Data: {len(data_sources)} datasets{data_section}{real_data_section}{gradient_hints}{interaction_section}{feedback_section}

DESIGN PRINCIPLES (apply rigorously):
- Visual hierarchy is EVERYTHING - use contrast, size, and whitespace decisively
- Color is communication, not decoration - every color choice has semantic meaning
- Icons aren't optional - they're cognitive shortcuts that reduce reading time (use Material Symbols)
- White space is a feature, not wasted space
- Typography scale: headlines should be 2-3x body text size
- Shadows and elevation create depth and focus
- Default to bold for labels, regular for values

PROGRESSIVE DISCLOSURE & SPATIAL GROUPING (CRITICAL for drilldown UIs):
- Related content stays together - file explorer appears INSIDE the dataset card, not in a separate section
- Expand in context - when user clicks "fracfocus", the fracfocus card expands to show files (not scroll to different section)
- Vertical proximity = relationship - drilling down should expand the card vertically, revealing nested content
- Use Accordion pattern: collapsed card → click to expand → reveals file tree inside same card
- DON'T separate navigation from content - if user selects dataset A, content for A appears adjacent/within, not far away
- Example: Dataset card with "Show Files" button → expands card → file explorer appears below in same card

LEFT/RIGHT LAYOUT ALIGNMENT (when progressive disclosure isn't possible):
- If using side-by-side layout (left: cards, right: file browser), ensure visual connection:
  * Match card titles with selector options (same text, same icons)
  * Use equal heights: left cards column should match right browser column height
  * Add visual indicator: highlight selected card when it matches right-side selection
  * Use consistent spacing: card gaps should match browser section spacing
  * Add connecting element: arrow, line, or shared color to show relationship

ANTI-PATTERNS TO AVOID:
- Timid, uniform text weights (everything regular)
- Monotone color schemes
- Missing visual hierarchy
- Cluttered layouts with no breathing room
- Generic, unstyled boxes

MATERIAL SYMBOLS ICON CATEGORIES (choose appropriate icons):
- Completion states: check_circle, done, task_alt, pending, cancel, error, warning
- Data & storage: database (for data source headers), storage, folder, cloud_download
- Pipeline stages: download, transform, code (use inside stage circles)
- Data types: science (chemistry), biotech (lab), factory (industrial), water_drop (fluids), oil_barrel (oil & gas)
- Navigation: arrow_forward, expand_more

ICON USAGE GUIDANCE:
- Headers/sections: Use database icon for "Data Sources" section
- Data type labels: Use domain icon (science, biotech, etc.) NEXT TO the data type text, NOT in header
- Stage indicators: Use completion icons (check_circle, done) inside circular badges
- Example: "Data Sources" header gets database icon, but "Chemical Data" label gets science icon

Your output should look production-ready for a $20M Series A fundraise deck.

🔒 CRITICAL: MACHINE-PARSABLE OUTPUT FORMAT REQUIRED

Output structured design spec (max 1000 tokens) using EXACT format below.
DO NOT deviate from this format or the build will FAIL.

LAYOUT: [describe layout with emphasis on hierarchy and whitespace]

COMPONENTS:
- COMPONENT: ComponentName
  DESCRIPTION: [SPECIFIC styling guidance - sizes, weights, colors, behavior]
- COMPONENT: SecondComponent
  DESCRIPTION: [SPECIFIC styling guidance]

🚨 COMPONENT FORMAT RULES (CRITICAL - MUST FOLLOW EXACTLY):
1. Each component MUST start with "- COMPONENT: " followed by the component name ONLY
2. Component name must be 2-4 words maximum, in Title Case (e.g., "Hero Metrics Card", "Data Table")
3. NO markdown formatting in component names (no **, no *, no `)
4. Description MUST be on the next line starting with "  DESCRIPTION: "
5. Keep descriptions to 1-2 sentences of styling/behavior guidance
6. List 3-7 components total
7. NEVER put description on the same line as component name
8. NEVER use bullets like "• **Name**: description" - ALWAYS use the two-line format

CORRECT FORMAT EXAMPLE:
- COMPONENT: Pipeline Health Card
  DESCRIPTION: 400px width, 16px rounded corners, elevated shadow (4dp). Header shows pipeline name with status badge.
- COMPONENT: File Explorer Tree
  DESCRIPTION: Expandable tree with 48px row height, indent 24px per level. Folder icons use expand_more/expand_less.

WRONG FORMAT (DO NOT USE):
- **Pipeline Card**: 400px width... (NO - mixing name and description)
- Pipeline Card (NO - missing COMPONENT: prefix and description)
• **Name**: description (NO - wrong bullet style)

ICONS: [specify EXACTLY which Material Symbols icons to use where - be specific about headers vs labels]

INTERACTIONS (CRITICAL - Use behavioral patterns from above):
List 3-5 interactions using this format:
- EVENT: [event name like onFileSelect, onPageChange]
  TRIGGERS: [what user does]
  STATE_CHANGES: [what state updates]
  DATA_FETCH: [what data to fetch and when]
  UI_FEEDBACK: [loading skeleton, highlight, scroll, etc.]

Example:
- EVENT: onFileSelect
  TRIGGERS: User clicks a file in the tree
  STATE_CHANGES: selectedFile = filePath, currentPage = 1
  DATA_FETCH: Fetch file preview when filePath changes
  UI_FEEDBACK: Show loading skeleton, highlight selected file

VISUAL HIERARCHY: [describe how to guide the eye - what's bold, what's large, what's emphasized]

Design confident, opinionated interfaces. M3 is your foundation, not your ceiling.
"""
        return prompt

    def _build_v2_json_prompt(
        self,
        screen_type: str,
        user_intent: str,
        data_section: str,
        real_data_section: str,
        gradient_hints: str,
        interaction_section: str,
        feedback_section: str
    ) -> str:
        """
        Build v2 JSON prompt for deterministic, machine-parsable output.

        This prompt produces valid JSON that can be directly parsed without regex.
        Includes all context injections for full behavioral state machine support.
        """
        prompt = f"""You are a senior product designer who outputs ONLY valid JSON.

Design a {screen_type} for: {user_intent}
{data_section}{real_data_section}{gradient_hints}{interaction_section}{feedback_section}

OUTPUT REQUIREMENTS:
You MUST output ONLY a valid JSON object. No explanations, no markdown, no code fences.
The JSON must be parseable by json.loads() directly.

REQUIRED JSON STRUCTURE:
{{
  "screen_type": "{screen_type}",
  "components": [
    {{
      "name": "ComponentName",
      "type": "Card|List|Tree|Table|Chart|Form|Modal|Container",
      "purpose": "Brief description of what this component does",
      "props": {{
        "width": "400px",
        "elevation": "4dp",
        "cornerRadius": "16px"
      }},
      "data_binding": "source_name or null",
      "children": []
    }}
  ],
  "layout": {{
    "type": "flex|grid",
    "direction": "row|column",
    "gap": "24px",
    "responsive": true
  }},
  "data_model": {{
    "sources": ["list of data source names"],
    "primary_entity": "main data type being displayed",
    "relationships": ["entity A -> entity B"]
  }},
  "interaction_model": [
    {{
      "event": "onFileSelect",
      "source_component": "FileExplorerTree",
      "target_component": "DataPreviewTable",
      "state_changes": ["selectedFile = filePath", "currentPage = 1"],
      "data_fetch": {{
        "endpoint": "/api/pipelines/{{pipelineId}}/files/preview",
        "params": ["file_path", "page", "page_size"],
        "trigger": "when filePath changes"
      }},
      "ui_feedback": ["show skeleton", "highlight selected", "scroll to preview"],
      "dependency_rules": ["refetch when filePath changes", "refetch when page changes"],
      "react_pattern": "useFilePreview(pipelineId, selectedFile, currentPage, pageSize)"
    }}
  ],
  "styling": {{
    "theme": "material3",
    "elevation": {{
      "card": "4dp",
      "modal": "8dp"
    }},
    "typography": {{
      "heading": "24px bold",
      "body": "14px regular",
      "caption": "12px medium"
    }},
    "icons": {{
      "header": "database",
      "folder": "folder",
      "file": "description",
      "status": "check_circle"
    }}
  }}
}}

COMPONENT NAMING RULES:
- Use PascalCase: "DataPreviewTable", "PipelineCard", "FileExplorer"
- Be specific: "WellDataTable" not "DataTable"
- Include purpose: "PaginationControls", "LoadingSkeletons"

INTERACTION MODEL RULES (CRITICAL):
- Every user action needs an event
- Every event must specify state_changes
- Every data-dependent component needs data_fetch
- Every async operation needs ui_feedback
- Include react_pattern for each interaction showing the exact hook call

REQUIRED INTERACTIONS (include these if applicable):
1. File/item selection: onFileSelect, onRowSelect, onItemSelect
2. Pagination: onPageChange with currentPage state
3. Loading states: onDataFetchStart, onDataFetchError, onDataEmpty
4. Expansion: onExpandToggle, onFolderToggle for tree/accordion

Output ONLY the JSON object. Start with {{ and end with }}."""

        return prompt

    def _build_v3_compressed_prompt(
        self,
        screen_type: str,
        user_intent: str,
        data_section: str,
        real_data_section: str,
        gradient_hints: str,
        interaction_section: str,
        feedback_section: str
    ) -> str:
        """
        Build v3 COMPRESSED prompt for UX Designer.

        70% smaller than v2 while maintaining all functionality.
        Produces valid JSON design spec.
        """
        prompt = f"""You are the UX DESIGNER AGENT for an autonomous multi-agent system.
Your job: produce a **single JSON design spec** for a React application UI.

OUTPUT MUST BE VALID JSON. No commentary. No markdown fences.

========================================================
DESIGN SPEC JSON SCHEMA (MANDATORY)
========================================================
{{
  "screen_type": "string",
  "components": [
    {{
      "name": "string",
      "type": "canonical_component",
      "data_source": "string|null",
      "props": {{}},
      "interactive": true|false
    }}
  ],
  "layout": {{
    "type": "layout_type",
    "children": ["component_names"]
  }},
  "data_model": {{
    "pipelines": ["ids"],
    "files": true|false,
    "metrics": true|false
  }},
  "interaction_model": [
    {{
      "event": "onEventName",
      "state_changes": ["state = value"],
      "data_fetch": {{"endpoint": "...", "params": []}},
      "ui_feedback": ["skeleton", "highlight"],
      "dependency_rules": ["refetch when X changes"],
      "react_pattern": "hook signature"
    }}
  ],
  "styling": {{
    "icons": {{"header": "icon_name"}},
    "typography": "body|title|label",
    "elevation": "none|low|medium|high"
  }}
}}

========================================================
CANONICAL COMPONENT TYPES
========================================================
FileTree, DatasetCard, DataPreviewTable, PipelineMetrics,
PaginationControls, FilterBar, DetailPanel, StageProgress, Tabs

========================================================
CANONICAL LAYOUT TYPES
========================================================
"two_column", "three_column", "stacked", "master_detail"

========================================================
CANONICAL EVENTS
========================================================
onFileSelect, onPageChange, onFilterChange, onRowSelect,
onBreadcrumbClick, onDatasetCardClick, onSearchInput, onModalToggle

========================================================
BEHAVIORAL PATTERNS FROM KNOWLEDGE BASE
========================================================
{interaction_section}

You MUST integrate these into interaction_model.
If a required pattern is missing, infer using:

INFERENCE RULES:
1. File selection: selectedFile = filePath, currentPage = 1, fetch preview
2. Pagination: refetch on page change
3. Show skeleton on data_fetch start
4. Show error/empty states if applicable
5. Every interactive component needs at least one event

========================================================
MANDATORY INTERACTION WIRING (CRITICAL)
========================================================
When a FileTree/FileExplorer component exists:
1. MUST have onFileSelect event that:
   - Sets selectedFile state to the clicked file path
   - Resets currentPage to 1
   - Triggers data_fetch for file preview

2. MUST wire to DataPreviewTable/DataTable using:
   - react_pattern: "useFilePreview(pipelineId, selectedFile, page, pageSize)"
   - data_fetch.endpoint: "/api/pipelines/{{pipelineId}}/files/preview"
   - data_fetch.params: ["file_path", "page", "page_size"]

3. MUST specify these hooks in interaction_model:
   - "usePipelines()" for listing pipelines
   - "useFilePreview(pipelineId, filePath, page, pageSize)" for file data

Example interaction_model entry for file selection:
{{
  "event": "onFileSelect",
  "source_component": "FileExplorerTree",
  "target_component": "DataPreviewTable",
  "state_changes": ["selectedFile = filePath", "currentPage = 1"],
  "data_fetch": {{
    "endpoint": "/api/pipelines/{{pipelineId}}/files/preview",
    "params": ["file_path", "page", "page_size"]
  }},
  "react_pattern": "useFilePreview(pipelineId, selectedFile, currentPage, pageSize)"
}}

========================================================
CONTEXT PROVIDED
========================================================
DATA CONTEXT:
{data_section}

REAL DATA EXAMPLES:
{real_data_section}

GRADIENT CONTEXT (domain-aware):
{gradient_hints}

USER REQUEST:
{user_intent}

SCREEN TYPE: {screen_type}

========================================================
RULES
========================================================
1. Output MUST be valid JSON
2. MUST include ALL required keys
3. MUST populate interaction_model using patterns + inference
4. MUST assign components to layout
5. MUST keep all naming canonical
6. DO NOT output React code - only JSON design spec

========================================================
BEGIN JSON OUTPUT:
========================================================
"""
        return prompt

    def _extract_components_block(self, design_reasoning: str) -> Optional[str]:
        """
        Extract COMPONENTS section with robust pattern matching.

        Handles multiple formats:
        - ## COMPONENTS: (markdown header)
        - **COMPONENTS:** (markdown bold)
        - COMPONENTS: (plain text)

        Returns:
            Extracted components text, or None if not found
        """
        patterns = [
            # Markdown header style
            r'##\s*COMPONENTS:?\s*\n(.*?)(?=\n##|\Z)',
            # Bold markdown style like **COMPONENTS:**
            r'\*\*COMPONENTS:?\*\*\s*\n(.*?)(?=\n\*\*[A-Z]|\Z)',
            # Plain text
            r'\bCOMPONENTS:?\s*\n(.*?)(?=\n[A-Z][A-Z ]+\:|\Z)',
        ]

        for i, pattern in enumerate(patterns, 1):
            match = re.search(pattern, design_reasoning, re.DOTALL | re.IGNORECASE)
            if match:
                print(f"  [UX Designer] ✅ COMPONENTS block found with pattern #{i}")
                return match.group(1)

        return None

    @staticmethod
    def _canonicalize_component_name(name: str) -> str:
        """
        Canonicalize component name to PascalCase for consistent matching.

        Converts:
        - "Dataset Overview Card" → "DatasetOverviewCard"
        - "Pipeline Health!" → "PipelineHealth"
        - "Data-Table" → "DataTable"

        This ensures:
        1. All non-alphanumeric characters are removed (except spaces for word splitting)
        2. Result is always PascalCase
        3. React and UX can match components reliably

        Args:
            name: Raw component name from LLM

        Returns:
            Canonicalized PascalCase name
        """
        if not name:
            return ""

        # Remove emojis, formatting, markdown, punctuation
        name = re.sub(r'[\*\_`~]', '', name)
        name = re.sub(r'[^a-zA-Z0-9 ]+', '', name)

        # Convert to PascalCase: "Dataset Overview Card" → "DatasetOverviewCard"
        parts = name.strip().split()
        return ''.join(word.capitalize() for word in parts)

    def _parse_components_from_reasoning(self, design_reasoning: str) -> List[Dict]:
        """
        Parse component definitions from LLM's design reasoning.

        Extracts the COMPONENTS: section and converts it into structured component dicts.

        FIX: Now enforces strict machine-parsable format:
        - COMPONENT: ComponentName
          DESCRIPTION: description

        FIX 2: Canonicalizes component names to PascalCase for reliable matching

        Args:
            design_reasoning: CoT reasoning text with COMPONENTS section

        Returns:
            List of component dicts with name, type, intent, pattern, features
        """
        if not design_reasoning:
            return []

        # Step 1: Extract COMPONENTS block with robust pattern matching
        components_text = self._extract_components_block(design_reasoning)

        if not components_text:
            print("  [UX Designer] ⚠️ No COMPONENTS section found in reasoning")
            # Debug: print first 500 chars to see what format Claude used
            print(f"  [UX Designer] DEBUG: Reasoning preview:\n{design_reasoning[:500]}...")
            return []

        # Step 2: Parse components using strict machine-parsable format
        # Expected format:
        # - COMPONENT: ComponentName
        #   DESCRIPTION: description text

        components = []
        lines = components_text.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Match component line: "- COMPONENT: Name"
            comp_match = re.match(r'^\-\s*COMPONENT:\s*(.+)$', line, re.IGNORECASE)
            if comp_match:
                raw_name = comp_match.group(1).strip()

                # Strip any markdown formatting that might have snuck in
                raw_name = raw_name.replace('**', '').replace('*', '').replace('`', '').strip()

                # FIX: Canonicalize component name to PascalCase
                # "Dataset Overview Card" → "DatasetOverviewCard"
                # This ensures React can match it reliably
                canonical_name = self._canonicalize_component_name(raw_name)

                # Look for description on next line
                desc = ""
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    desc_match = re.match(r'^DESCRIPTION:\s*(.+)$', next_line, re.IGNORECASE)
                    if desc_match:
                        desc = desc_match.group(1).strip()
                        i += 1  # Skip the description line

                if not canonical_name:
                    i += 1
                    continue

                # Infer component type from name/description
                comp_type = self._infer_component_type(canonical_name, desc)

                # Extract features from description
                features = self._extract_features(desc)

                components.append({
                    "name": canonical_name,  # Store canonicalized PascalCase name
                    "display_name": raw_name,  # Keep original for display if needed
                    "type": comp_type,
                    "intent": desc[:100] if desc else canonical_name,
                    "pattern": self._infer_pattern(desc),
                    "features": features
                })

                print(f"  [UX Designer] Canonicalized: '{raw_name}' → '{canonical_name}'")

            i += 1

        if components:
            print(f"  [UX Designer] ✅ Parsed {len(components)} components from reasoning")
        else:
            print("  [UX Designer] ⚠️ No components matched strict format")
            print("  [UX Designer] Expected format: '- COMPONENT: Name' followed by '  DESCRIPTION: ...'")

        return components

    def _infer_component_type(self, name: str, description: str) -> str:
        """Infer component type from name and description"""
        text = (name + " " + description).lower()

        if any(kw in text for kw in ['nav', 'breadcrumb', 'hierarchy', 'menu', 'sidebar']):
            return "navigation"
        elif any(kw in text for kw in ['file', 'browser', 'tree', 'folder', 'explorer']):
            return "file_browser"
        elif any(kw in text for kw in ['button', 'action', 'toolbar']):
            return "action_buttons"
        elif any(kw in text for kw in ['card', 'grid', 'list', 'table', 'data', 'display']):
            return "data_display"
        elif any(kw in text for kw in ['expand', 'accordion', 'collaps', 'dropdown']):
            return "expandable_navigation"
        elif any(kw in text for kw in ['filter', 'search', 'sort']):
            return "filter_bar"
        else:
            return "data_display"  # Default

    def _infer_pattern(self, description: str) -> str:
        """Infer UX pattern from description"""
        desc = description.lower()

        if 'tree' in desc or 'accordion' in desc:
            return "tree-accordion"
        elif 'master' in desc or 'detail' in desc:
            return "master-detail"
        elif 'expand' in desc or 'collapse' in desc:
            return "progressive-disclosure"
        elif 'card' in desc:
            return "card-grid"
        else:
            return "default"

    def _extract_features(self, description: str) -> List[str]:
        """Extract feature keywords from description"""
        features = []
        desc = description.lower()

        feature_keywords = [
            'expand', 'collapse', 'breadcrumb', 'search', 'filter', 'sort',
            'click', 'hover', 'drill-down', 'navigation', 'tree', 'accordion'
        ]

        for keyword in feature_keywords:
            if keyword in desc:
                features.append(keyword)

        return features[:5]  # Limit to 5 features

    def _get_fallback_components(self, ux_patterns: Dict, gradient_context: Dict = None) -> List[Dict]:
        """
        Generate minimal fallback components (ONLY if parsing completely fails).

        FIX: Returns empty list instead of 'Unknown' to avoid unfixable conflicts.

        This should rarely be used - the robust parsing above should handle most cases.

        Args:
            ux_patterns: UX patterns from KB
            gradient_context: Domain-aware pattern boost flags

        Returns:
            Empty list (no fallback components)
        """
        print("  [UX Designer] ⚠️ Using empty fallback (parsing failed)")
        # FIX: Return empty list instead of creating "Unknown" or template components
        # This prevents unfixable HIGH severity conflicts
        return []

    # ========================================================================
    # JSON STRUCTURED OUTPUT LAYER - Phase 6 (v2 Prompt)
    # Enables deterministic, machine-parsable JSON output from UX Designer
    # ========================================================================

    def _detect_json_output(self, text: str) -> bool:
        """
        Detect if LLM output is in JSON format (v2 mode).

        Args:
            text: Raw LLM response text

        Returns:
            True if output appears to be JSON, False otherwise
        """
        if not text:
            return False

        stripped = text.strip()

        # Check for code fence with json
        if stripped.startswith("```json") or stripped.startswith("```JSON"):
            return True

        # Check for raw JSON object
        if stripped.startswith("{") and stripped.endswith("}"):
            # Quick validation - try to find key JSON markers
            json_markers = ['"screen_type"', '"components"', '"interaction_model"']
            return any(marker in stripped for marker in json_markers)

        return False

    def _extract_json_from_response(self, text: str) -> str:
        """
        Extract JSON content from LLM response, handling code fences.

        Args:
            text: Raw LLM response text

        Returns:
            Clean JSON string ready for parsing
        """
        if not text:
            return ""

        stripped = text.strip()

        # Handle ```json ... ``` code fence
        if stripped.startswith("```json") or stripped.startswith("```JSON"):
            # Find the closing fence
            start_idx = stripped.find("\n") + 1
            end_idx = stripped.rfind("```")
            if end_idx > start_idx:
                return stripped[start_idx:end_idx].strip()

        # Handle ``` ... ``` generic code fence
        if stripped.startswith("```"):
            start_idx = stripped.find("\n") + 1
            end_idx = stripped.rfind("```")
            if end_idx > start_idx:
                return stripped[start_idx:end_idx].strip()

        # Already clean JSON
        if stripped.startswith("{"):
            return stripped

        return stripped

    def _parse_json_design(self, json_text: str) -> Dict[str, Any]:
        """
        Parse JSON design spec into structured components, interactions, and styling.

        This is the v2 structured parser that replaces regex-based extraction
        when the LLM outputs deterministic JSON.

        Args:
            json_text: JSON string from _extract_json_from_response()

        Returns:
            Dict with keys: screen_type, components, layout, data_model,
                           interaction_model, styling, raw_json
        """
        result = {
            "screen_type": "unknown",
            "components": [],
            "layout": {},
            "data_model": {},
            "interaction_model": [],
            "styling": {},
            "raw_json": None,
            "parse_success": False
        }

        if not json_text:
            print("  [UX Designer] ⚠️ JSON parse: Empty input")
            return result

        try:
            parsed = json.loads(json_text)
            result["raw_json"] = parsed
            result["parse_success"] = True

            # Extract screen_type
            result["screen_type"] = parsed.get("screen_type", "dashboard")

            # Extract components with normalization
            raw_components = parsed.get("components", [])
            normalized_components = []
            for comp in raw_components:
                if isinstance(comp, dict):
                    normalized_comp = {
                        "name": comp.get("name", comp.get("component_name", "UnknownComponent")),
                        "type": comp.get("type", comp.get("component_type", "Container")),
                        "purpose": comp.get("purpose", comp.get("description", "")),
                        "props": comp.get("props", comp.get("properties", {})),
                        "children": comp.get("children", []),
                        "data_binding": comp.get("data_binding", comp.get("data", None)),
                    }
                    normalized_components.append(normalized_comp)
            result["components"] = normalized_components

            # Extract layout
            result["layout"] = parsed.get("layout", {
                "type": "flex",
                "direction": "column",
                "responsive": True
            })

            # Extract data_model
            result["data_model"] = parsed.get("data_model", {})

            # Extract and normalize interaction_model (critical for Phase 4)
            raw_interactions = parsed.get("interaction_model", [])
            normalized_interactions = []
            for interaction in raw_interactions:
                if isinstance(interaction, dict):
                    norm_interaction = {
                        "event": self._canonicalize_event_name(interaction.get("event", "")),
                        "state_changes": interaction.get("state_changes", []),
                        "data_fetch": interaction.get("data_fetch", None),
                        "ui_feedback": interaction.get("ui_feedback", []),
                        "dependency_rules": interaction.get("dependency_rules", []),
                    }
                    # Add react_pattern if present
                    if "react_pattern" in interaction:
                        norm_interaction["react_pattern"] = interaction["react_pattern"]
                    normalized_interactions.append(norm_interaction)
            result["interaction_model"] = normalized_interactions

            # Extract styling with M3 defaults
            result["styling"] = parsed.get("styling", {
                "theme": "material3",
                "elevation": {},
                "typography": {},
                "icons": {}
            })

            print(f"  [UX Designer] ✅ JSON parse successful: {len(normalized_components)} components, {len(normalized_interactions)} interactions")

        except json.JSONDecodeError as e:
            print(f"  [UX Designer] ⚠️ JSON parse error: {e}")
            result["parse_success"] = False

        return result

    def _convert_json_to_legacy_format(self, json_result: Dict[str, Any]) -> Tuple[List[Dict], str]:
        """
        Convert parsed JSON design to legacy format for backward compatibility.

        This enables dual-mode operation where JSON output can still flow
        through existing _create_design_spec() logic.

        Args:
            json_result: Output from _parse_json_design()

        Returns:
            Tuple of (components_list, raw_response_for_fallback)
        """
        if not json_result.get("parse_success"):
            return [], ""

        components = []
        for comp in json_result.get("components", []):
            legacy_comp = {
                "name": comp.get("name", "Component"),
                "type": comp.get("type", "Container"),
                "purpose": comp.get("purpose", ""),
                "props": comp.get("props", {}),
            }
            # Map data_binding to props if present
            if comp.get("data_binding"):
                legacy_comp["props"]["data_source"] = comp["data_binding"]

            components.append(legacy_comp)

        # Build a minimal raw response for any fallback parsing
        raw_response = f"Screen Type: {json_result.get('screen_type', 'dashboard')}\n"
        raw_response += "Components:\n"
        for comp in components:
            raw_response += f"- {comp['name']} ({comp['type']}): {comp['purpose']}\n"

        return components, raw_response

    # ========================================================================
    # INTERACTION BEHAVIOR LAYER - Enhancement C
    # Merges Pinecone canonical patterns + LLM-generated behavior + context
    # ========================================================================

    # Canonical event names for consistency
    CANONICAL_EVENTS = {
        'onfileselect': 'onFileSelect',
        'onpagechange': 'onPageChange',
        'ondatasetselect': 'onDatasetSelect',
        'onpipelineselect': 'onPipelineSelect',
        'onexpandtoggle': 'onExpandToggle',
        'onfoldertoggle': 'onFolderToggle',
        'onfilterchange': 'onFilterChange',
        'onrowselect': 'onRowSelect',
        'onsearchinput': 'onSearchInput',
        'onmodalopen': 'onModalOpen',
        'onmodalclose': 'onModalClose',
        'ondatafetchstart': 'onDataFetchStart',
        'ondatafetcherror': 'onDataFetchError',
        'ondataempty': 'onDataEmpty',
    }

    def _canonicalize_event_name(self, event: str) -> str:
        """
        Canonicalize event name to consistent camelCase format.

        Args:
            event: Raw event name from LLM or pattern

        Returns:
            Canonicalized event name (e.g., 'onFileSelect')
        """
        if not event:
            return ""

        # Normalize: remove spaces, lowercase for lookup
        normalized = event.replace(' ', '').replace('_', '').replace('-', '').lower()

        # Check canonical mapping
        if normalized in self.CANONICAL_EVENTS:
            return self.CANONICAL_EVENTS[normalized]

        # If not in mapping, return as-is with proper camelCase
        # Ensure it starts with 'on' if it doesn't
        if not event.lower().startswith('on'):
            event = 'on' + event

        return event

    def _parse_interactions_from_reasoning(self, design_reasoning: str) -> List[Dict]:
        """
        Parse INTERACTIONS section from LLM's design reasoning.

        Expected format:
        - EVENT: onFileSelect
          TRIGGERS: User clicks a file in the tree
          STATE_CHANGES: selectedFile = filePath, currentPage = 1
          DATA_FETCH: Fetch file preview when filePath changes
          UI_FEEDBACK: Show loading skeleton, highlight selected file

        Args:
            design_reasoning: Full CoT reasoning text

        Returns:
            List of parsed interaction dicts
        """
        if not design_reasoning:
            return []

        interactions = []

        # Extract INTERACTIONS block
        interactions_match = re.search(
            r'INTERACTIONS.*?:(.*?)(?=\n[A-Z][A-Z ]+:|$)',
            design_reasoning,
            re.DOTALL | re.IGNORECASE
        )

        if not interactions_match:
            print("  [UX Designer] No INTERACTIONS block found in reasoning")
            return []

        interactions_text = interactions_match.group(1)

        # Parse individual events
        # Pattern: "- EVENT: eventName" followed by indented fields
        event_pattern = re.compile(
            r'-\s*EVENT:\s*(\w+)\s*\n'
            r'(?:\s+TRIGGERS?:\s*(.+?)\n)?'
            r'(?:\s+STATE_CHANGES?:\s*(.+?)\n)?'
            r'(?:\s+DATA_FETCH:\s*(.+?)\n)?'
            r'(?:\s+UI_FEEDBACK:\s*(.+?)(?:\n|$))?',
            re.IGNORECASE
        )

        for match in event_pattern.finditer(interactions_text):
            event_name = self._canonicalize_event_name(match.group(1))
            triggers = match.group(2).strip() if match.group(2) else ""
            state_changes_raw = match.group(3).strip() if match.group(3) else ""
            data_fetch_raw = match.group(4).strip() if match.group(4) else ""
            ui_feedback_raw = match.group(5).strip() if match.group(5) else ""

            # Parse state changes (comma-separated)
            state_changes = []
            if state_changes_raw:
                state_changes = [s.strip() for s in state_changes_raw.split(',') if s.strip()]

            # Parse UI feedback (comma-separated)
            ui_feedback = []
            if ui_feedback_raw:
                ui_feedback = [f.strip() for f in ui_feedback_raw.split(',') if f.strip()]

            interactions.append({
                'event': event_name,
                'triggers': triggers,
                'state_changes': state_changes,
                'data_fetch_description': data_fetch_raw,
                'ui_feedback': ui_feedback,
                'source': 'llm'
            })

        print(f"  [UX Designer] Parsed {len(interactions)} interactions from LLM reasoning")
        return interactions

    def _merge_interaction_behaviors(
        self,
        pinecone_patterns: Dict[str, List[Dict]],
        llm_interactions: List[Dict],
        components: List[Dict],
        requirements: Dict
    ) -> List[Dict]:
        """
        Merge interaction behaviors from multiple sources:
        1. Pinecone canonical patterns (authoritative for React implementation details)
        2. LLM-generated interactions (context-specific behavior)
        3. Context-based inference (fill in gaps)

        Merge rules:
        - If LLM specifies an event → trust LLM for triggers/feedback
        - If Pinecone has React implementation details → use those
        - If neither has it → infer from context
        - Deduplicate and validate

        Args:
            pinecone_patterns: Patterns from Pinecone by category
            llm_interactions: Parsed interactions from LLM reasoning
            components: List of components in the design
            requirements: User requirements dict

        Returns:
            Merged, deduplicated list of interaction behaviors
        """
        merged = {}  # Key by event name

        # Step 1: Load Pinecone patterns as base (authoritative React details)
        for category, patterns in pinecone_patterns.items():
            if category == 'intent_patterns':
                continue  # Skip intent patterns, use specific ones

            for pattern in patterns:
                event = self._canonicalize_event_name(pattern.get('event', ''))
                if not event:
                    continue

                if event not in merged:
                    merged[event] = {
                        'event': event,
                        'state_changes': pattern.get('state_changes', []),
                        'data_fetch': pattern.get('data_fetch', {}),
                        'ui_feedback': pattern.get('ui_feedback', []),
                        'dependency_rules': pattern.get('dependency_rules', []),
                        'react_pattern': pattern.get('react_pattern', ''),
                        'source': 'pinecone'
                    }

        # Step 2: Overlay LLM-generated interactions
        for llm_int in llm_interactions:
            event = llm_int.get('event', '')
            if not event:
                continue

            if event in merged:
                # Merge: LLM provides context, Pinecone provides React details
                existing = merged[event]

                # Merge state_changes (union, dedupe)
                existing_states = set(existing.get('state_changes', []))
                llm_states = set(llm_int.get('state_changes', []))
                existing['state_changes'] = list(existing_states | llm_states)

                # Merge ui_feedback (union, dedupe)
                existing_feedback = set(existing.get('ui_feedback', []))
                llm_feedback = set(llm_int.get('ui_feedback', []))
                existing['ui_feedback'] = list(existing_feedback | llm_feedback)

                # LLM triggers override if provided
                if llm_int.get('triggers'):
                    existing['triggers'] = llm_int['triggers']

                existing['source'] = 'merged'
            else:
                # New event from LLM - add it
                merged[event] = {
                    'event': event,
                    'triggers': llm_int.get('triggers', ''),
                    'state_changes': llm_int.get('state_changes', []),
                    'data_fetch': {'description': llm_int.get('data_fetch_description', '')},
                    'ui_feedback': llm_int.get('ui_feedback', []),
                    'dependency_rules': [],
                    'react_pattern': '',
                    'source': 'llm'
                }

        # Step 3: Context-aware inference (fill gaps)
        merged = self._infer_missing_behaviors(merged, components, requirements)

        # Step 4: Context-aware pruning (remove irrelevant)
        merged = self._prune_irrelevant_behaviors(merged, components, requirements)

        # Step 5: Deduplicate and validate
        final_list = self._deduplicate_and_validate(merged)

        print(f"  [UX Designer] Merged interaction_model: {len(final_list)} behaviors")
        return final_list

    def _infer_missing_behaviors(
        self,
        merged: Dict[str, Dict],
        components: List[Dict],
        requirements: Dict
    ) -> Dict[str, Dict]:
        """
        Infer missing behaviors that LLM often forgets.

        Common gaps:
        - Loading skeleton during async fetch
        - Error state handling
        - Empty state handling
        - Scroll behavior after selection

        Args:
            merged: Current merged behaviors
            components: Components in design
            requirements: User requirements

        Returns:
            Updated merged dict with inferred behaviors
        """
        component_types = [c.get('type', '').lower() for c in components]
        component_names = [c.get('name', '').lower() for c in components]

        # Infer: If file browser exists, ensure onFileSelect has proper feedback
        has_file_browser = any('file' in t or 'tree' in t or 'explorer' in t
                              for t in component_types + component_names)

        # CRITICAL FIX: CREATE onFileSelect if missing but file browser exists
        # This was the "smoking gun" bug - only enhanced existing patterns, never created them
        if has_file_browser and 'onFileSelect' not in merged:
            print("  [UX Designer] Inferring onFileSelect behavior (Pinecone pattern missing)")
            merged['onFileSelect'] = {
                'event': 'onFileSelect',
                'state_changes': ['selectedFile = filePath', 'currentPage = 1'],
                'data_fetch': {
                    'endpoint': '/api/files/preview',
                    'params': ['filePath', 'page', 'pageSize'],
                    'method': 'GET',
                    'trigger': 'on_file_selection'
                },
                'ui_feedback': [
                    'show loading skeleton in preview panel',
                    'highlight selected file in tree',
                    'scroll preview panel to top'
                ],
                'dependency_rules': [
                    'refetch when filePath changes',
                    'refetch when currentPage changes',
                    'reset currentPage to 1 when filePath changes'
                ],
                'react_pattern': 'const { data, loading, error, totalRows } = useFilePreview(selectedFile, { page: currentPage, pageSize });',
                'source': 'inferred'
            }

        if has_file_browser and 'onFileSelect' in merged:
            fb = merged['onFileSelect']
            # Ensure loading skeleton
            if not any('skeleton' in f.lower() for f in fb.get('ui_feedback', [])):
                fb.setdefault('ui_feedback', []).append('show loading skeleton in preview panel')
            # Ensure highlight
            if not any('highlight' in f.lower() for f in fb.get('ui_feedback', [])):
                fb['ui_feedback'].append('highlight selected file in tree')
            # Ensure scroll
            if not any('scroll' in f.lower() for f in fb.get('ui_feedback', [])):
                fb['ui_feedback'].append('scroll preview panel to top')

        # Infer: If data table/preview exists, ensure pagination has feedback
        has_table = any('table' in t or 'preview' in t or 'data' in t
                       for t in component_types + component_names)

        # CRITICAL FIX: CREATE onPageChange if missing but table/preview exists
        if has_table and 'onPageChange' not in merged:
            print("  [UX Designer] Inferring onPageChange behavior (Pinecone pattern missing)")
            merged['onPageChange'] = {
                'event': 'onPageChange',
                'state_changes': ['currentPage = newPage'],
                'data_fetch': {
                    'endpoint': '/api/files/preview',
                    'params': ['filePath', 'page', 'pageSize'],
                    'method': 'GET',
                    'trigger': 'on_page_change'
                },
                'ui_feedback': [
                    'show loading state on table',
                    'scroll to top of table',
                    'update pagination controls'
                ],
                'dependency_rules': [
                    'refetch when currentPage changes',
                    'maintain filePath selection'
                ],
                'react_pattern': 'const handlePageChange = (newPage: number) => setCurrentPage(newPage);',
                'source': 'inferred'
            }

        if has_table and 'onPageChange' in merged:
            pb = merged['onPageChange']
            if not any('skeleton' in f.lower() for f in pb.get('ui_feedback', [])):
                pb.setdefault('ui_feedback', []).append('show loading state on table')
            if not any('scroll' in f.lower() for f in pb.get('ui_feedback', [])):
                pb['ui_feedback'].append('scroll to top of table')

        # Infer: Add async loading behavior if not present
        if 'onDataFetchStart' not in merged and (has_file_browser or has_table):
            merged['onDataFetchStart'] = {
                'event': 'onDataFetchStart',
                'state_changes': ['loading = true', 'error = null'],
                'data_fetch': {},
                'ui_feedback': [
                    'show skeleton matching content shape',
                    'disable interactive elements during load'
                ],
                'dependency_rules': ['automatic when any fetch starts'],
                'react_pattern': 'if (loading) return <Skeleton />',
                'source': 'inferred'
            }

        # Infer: Add error state if not present
        if 'onDataFetchError' not in merged and (has_file_browser or has_table):
            merged['onDataFetchError'] = {
                'event': 'onDataFetchError',
                'state_changes': ['loading = false', 'error = errorMessage'],
                'data_fetch': {},
                'ui_feedback': [
                    'show error message with retry button',
                    'preserve previous data if available'
                ],
                'dependency_rules': ['trigger on fetch failure'],
                'react_pattern': 'if (error) return <ErrorState message={error} onRetry={refetch} />',
                'source': 'inferred'
            }

        # Infer: Add empty state if not present
        if 'onDataEmpty' not in merged and has_table:
            merged['onDataEmpty'] = {
                'event': 'onDataEmpty',
                'state_changes': ['loading = false', 'data = []'],
                'data_fetch': {},
                'ui_feedback': [
                    'show empty state message',
                    'suggest action if applicable'
                ],
                'dependency_rules': ['show when loading=false and data.length=0'],
                'react_pattern': "if (!loading && data.length === 0) return <EmptyState message='No data found' />",
                'source': 'inferred'
            }

        return merged

    def _prune_irrelevant_behaviors(
        self,
        merged: Dict[str, Dict],
        components: List[Dict],
        requirements: Dict
    ) -> Dict[str, Dict]:
        """
        Remove behaviors that don't apply to the current design context.

        Examples:
        - No file browser → remove onFileSelect, onFolderToggle
        - No pagination → remove onPageChange
        - No filters → remove onFilterChange
        - Intent is "overview only" → remove detailed interactions

        Args:
            merged: Current merged behaviors
            components: Components in design
            requirements: User requirements

        Returns:
            Pruned merged dict
        """
        component_types = [c.get('type', '').lower() for c in components]
        component_names = [c.get('name', '').lower() for c in components]
        all_comp_text = ' '.join(component_types + component_names)

        user_intent = requirements.get('intent', '').lower()

        # Prune: No file browser → remove file-related events
        has_file_browser = 'file' in all_comp_text or 'tree' in all_comp_text or 'explorer' in all_comp_text
        if not has_file_browser:
            merged.pop('onFileSelect', None)
            merged.pop('onFolderToggle', None)

        # Prune: No pagination component → remove pagination event
        has_pagination = 'pagination' in all_comp_text or 'page' in all_comp_text
        if not has_pagination:
            merged.pop('onPageChange', None)

        # Prune: No filter component → remove filter event
        has_filters = 'filter' in all_comp_text or 'search' in all_comp_text
        if not has_filters:
            merged.pop('onFilterChange', None)
            merged.pop('onSearchInput', None)

        # Prune: No expandable/accordion → remove expand events
        has_expandable = 'expand' in all_comp_text or 'accordion' in all_comp_text or 'collapse' in all_comp_text
        if not has_expandable:
            merged.pop('onExpandToggle', None)

        # Prune: Overview/summary intent → minimize interactions
        if 'overview' in user_intent or 'summary' in user_intent:
            # Keep only essential events for overview
            keep_events = {'onDatasetSelect', 'onPipelineSelect', 'onDataFetchStart', 'onDataFetchError'}
            merged = {k: v for k, v in merged.items() if k in keep_events}

        return merged

    def _deduplicate_and_validate(self, merged: Dict[str, Dict]) -> List[Dict]:
        """
        Deduplicate rules within each behavior and validate structure.

        Args:
            merged: Merged behaviors dict

        Returns:
            Clean list of validated interaction behaviors
        """
        final_list = []

        for event, behavior in merged.items():
            # Dedupe state_changes
            state_changes = list(dict.fromkeys(behavior.get('state_changes', [])))

            # Dedupe ui_feedback
            ui_feedback = list(dict.fromkeys(behavior.get('ui_feedback', [])))

            # Dedupe dependency_rules
            dependency_rules = list(dict.fromkeys(behavior.get('dependency_rules', [])))

            # Build clean behavior object
            clean_behavior = {
                'event': behavior.get('event', event),
                'state_changes': state_changes[:5],  # Limit to 5
                'data_fetch': behavior.get('data_fetch', {}),
                'ui_feedback': ui_feedback[:5],  # Limit to 5
                'dependency_rules': dependency_rules[:3],  # Limit to 3
            }

            # Add react_pattern if present
            if behavior.get('react_pattern'):
                clean_behavior['react_pattern'] = behavior['react_pattern']

            # Add triggers if present
            if behavior.get('triggers'):
                clean_behavior['triggers'] = behavior['triggers']

            final_list.append(clean_behavior)

        # Sort by event name for consistency
        final_list.sort(key=lambda x: x.get('event', ''))

        # Limit total to 12 behaviors
        if len(final_list) > 12:
            print(f"  [UX Designer] Trimming interaction_model from {len(final_list)} to 12")
            final_list = final_list[:12]

        return final_list

    def _create_design_spec(
        self,
        design_reasoning: str,
        requirements: Dict,
        ux_patterns: Dict,
        gradient_context: Dict = None,
        interaction_patterns: Dict = None
    ) -> DesignSpec:
        """
        Create design specification from reasoning

        Args:
            design_reasoning: CoT reasoning from design process
            requirements: User requirements
            ux_patterns: UX patterns from KB
            gradient_context: Domain-aware pattern boost flags
            interaction_patterns: Behavioral state machines from Pinecone
        """
        print("  [UX Designer] Creating design specification...")

        # Extract from requirements
        screen_type = requirements.get('screen_type', 'dashboard')
        user_intent = requirements.get('intent', 'view and manage data')
        data_sources = requirements.get('data_sources', {})

        # ================================================================
        # DUAL-MODE ROUTING: JSON (v2) vs Legacy (v1) parsing
        # ================================================================
        if self._detect_json_output(design_reasoning):
            print("  [UX Designer] Detected JSON output - using v2 parser")
            json_text = self._extract_json_from_response(design_reasoning)
            json_result = self._parse_json_design(json_text)

            if json_result.get("parse_success"):
                # JSON mode: Extract all data directly from parsed JSON
                components = json_result.get("components", [])
                interaction_model = json_result.get("interaction_model", [])
                styling = json_result.get("styling", {
                    "design_system": "Material Design 3",
                    "typography": "from_knowledge_base",
                    "colors": "from_knowledge_base",
                    "spacing": "8dp_grid"
                })

                # Override screen_type if JSON provided it
                if json_result.get("screen_type") and json_result["screen_type"] != "unknown":
                    screen_type = json_result["screen_type"]

                print(f"  [UX Designer] ✅ JSON parsed: {len(components)} components, {len(interaction_model)} interactions")

                # Still apply gradient enhancements to JSON-parsed components
                if gradient_context:
                    component_types = [c.get('type', '') for c in components]
                    if gradient_context.get('boost_tree_views') and 'Tree' not in component_types:
                        components.append({
                            "name": "FileBrowser",
                            "type": "Tree",
                            "purpose": "Navigate deeply nested directory structure",
                            "props": {"expandable": True, "showBreadcrumbs": True}
                        })

                # Merge with Pinecone patterns for completeness
                if interaction_patterns:
                    interaction_model = self._merge_interaction_behaviors(
                        pinecone_patterns=interaction_patterns,
                        llm_interactions=interaction_model,  # JSON interactions as LLM source
                        components=components,
                        requirements=requirements
                    )

                # Define basic interactions for legacy compatibility
                interactions = [
                    {"trigger": "button_click", "action": "navigate_to_detail", "pattern": "master-detail"},
                    {"trigger": "action_button", "action": "execute_on_item", "pattern": "context-action"}
                ]

                return DesignSpec(
                    screen_type=screen_type,
                    intent=user_intent,
                    components=components,
                    interactions=interactions,
                    patterns=list(ux_patterns.keys()),
                    styling=styling,
                    recommended_pattern=None,
                    design_reasoning=design_reasoning,
                    data_sources=data_sources,
                    interaction_model=interaction_model
                )
            else:
                print("  [UX Designer] ⚠️ JSON parse failed - falling back to legacy parser")

        # ================================================================
        # LEGACY MODE (v1): Regex-based parsing
        # ================================================================

        # PARSE components from design_reasoning instead of using templates
        components = self._parse_components_from_reasoning(design_reasoning)

        if not components:
            # FIX: Use empty list instead of fallback to avoid "Unknown" component
            print("  [UX Designer] ⚠️ Failed to parse components from reasoning, using empty list")
            components = []  # Changed from _get_fallback_components()
        else:
            print(f"  [UX Designer] ✅ Parsed {len(components)} components from reasoning")

            # GRADIENT-AWARE ENHANCEMENT
            # Add gradient-suggested components if not already present
            if gradient_context:
                component_types = [c.get('type', '') for c in components]

                if gradient_context.get('boost_tree_views') and 'file_browser' not in component_types:
                    print("  [UX Designer] 🧭 Gradient: Adding tree/accordion component")
                    components.append({
                        "name": "FileBrowser",
                        "type": "file_browser",
                        "intent": "Navigate deeply nested directory structure",
                        "pattern": "tree-accordion",
                        "features": ["expand-collapse", "breadcrumbs", "depth-indication"]
                    })

                if gradient_context.get('boost_hierarchical_navigation') and 'expandable_navigation' not in component_types and 'navigation' not in component_types:
                    print("  [UX Designer] 🧭 Gradient: Adding expandable navigation")
                    components.append({
                        "name": "ExpandableNavigation",
                        "type": "expandable_navigation",
                        "intent": "Navigate nested data hierarchy",
                        "pattern": "expandable-cards",
                        "features": ["click-to-expand", "breadcrumbs"]
                    })

        # Define interactions
        interactions = [
            {
                "trigger": "button_click",
                "action": "navigate_to_detail",
                "pattern": "master-detail"
            },
            {
                "trigger": "action_button",
                "action": "execute_on_item",
                "pattern": "context-action"
            }
        ]

        # Styling from design principles
        styling = {
            "design_system": "Material Design 3",
            "typography": "from_knowledge_base",
            "colors": "from_knowledge_base",
            "spacing": "8dp_grid"
        }

        # Patterns to use
        pattern_list = list(ux_patterns.keys())

        # GRADIENT-AWARE PATTERN INJECTION
        if gradient_context:
            if gradient_context.get('boost_hierarchical_navigation'):
                if 'breadcrumb-navigation' not in pattern_list:
                    pattern_list.append('breadcrumb-navigation')
                    print("  [UX Designer] 🧭 Gradient: Added breadcrumb-navigation pattern")

        # PURE LOVABLE: No pattern selection needed - Gradio agent composes from primitives
        # The design_reasoning contains all guidance needed (visual hierarchy, icons, etc.)

        # ================================================================
        # ENHANCEMENT C: Build interaction_model via 3-layer merge
        # 1. Pinecone canonical patterns (React implementation details)
        # 2. LLM-generated interactions (context-specific behavior)
        # 3. Inferred behaviors (fill gaps, add error/empty states)
        # ================================================================

        # Step 1: Parse LLM-generated interactions from design reasoning
        llm_interactions = self._parse_interactions_from_reasoning(design_reasoning)

        # Step 2: Merge all three sources
        interaction_model = self._merge_interaction_behaviors(
            pinecone_patterns=interaction_patterns or {},
            llm_interactions=llm_interactions,
            components=components,
            requirements=requirements
        )

        return DesignSpec(
            screen_type=screen_type,
            intent=user_intent,
            components=components,
            interactions=interactions,
            patterns=pattern_list,
            styling=styling,
            recommended_pattern=None,  # Not used in Pure Lovable approach
            design_reasoning=design_reasoning,  # Pass full design reasoning (includes ICONS)
            data_sources=data_sources,  # Phase 2: Pass discovered metadata to React Developer
            interaction_model=interaction_model  # Behavioral state machines for React
        )

    def _add_to_memory(self, design_spec: DesignSpec):
        """Add design to memory for session continuity"""
        memory_entry = {
            "screen_type": design_spec.screen_type,
            "intent": design_spec.intent,
            "components": len(design_spec.components),
            "patterns_used": design_spec.patterns
        }
        self.design_history.append(memory_entry)
        print(f"  [UX Designer] Added to memory ({len(self.design_history)} designs)")

    def get_design_history(self) -> str:
        """Format design history for context"""
        if not self.design_history:
            return ""

        lines = ["PREVIOUS DESIGNS IN SESSION:"]
        for i, entry in enumerate(self.design_history, 1):
            lines.append(f"{i}. {entry['screen_type']}: {entry['intent']}")
            lines.append(f"   Patterns: {', '.join(entry['patterns_used'])}")

        return "\n".join(lines)
