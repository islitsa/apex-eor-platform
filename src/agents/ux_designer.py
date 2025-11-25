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

from typing import Dict, Any, List, Optional
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
        data_sources: Dict[str, Any] = None  # Phase 2: Include discovered metadata
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

    def to_dict(self) -> Dict:
        """Full serialization (for debugging, logging)"""
        return {
            "screen_type": self.screen_type,
            "intent": self.intent,
            "components": self.components,
            "interactions": self.interactions,
            "patterns": self.patterns,
            "styling": self.styling,
            "data_sources": self.data_sources  # Include discovered metadata
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

    def __init__(self, trace_collector=None, use_autonomous_mode=False):
        self.design_kb = DesignKnowledgeBasePinecone()

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

        # Step 3: Use CoT to reason through UX decisions WITH real data and gradient hints
        design_reasoning = self._design_with_cot(requirements, ux_patterns, design_principles, data_context, gradient_context)

        # Step 4: Create design specification (with gradient-aware component injection)
        design_spec = self._create_design_spec(design_reasoning, requirements, ux_patterns, gradient_context)

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

    def _design_with_cot(
        self,
        requirements: Dict,
        ux_patterns: Dict,
        design_principles: Dict,
        data_context: Dict = None,
        gradient_context: Dict = None
    ) -> str:
        """
        Chain of Thought: Reason through UX design decisions

        Args:
            requirements: User requirements with discovered data sources
            ux_patterns: UX patterns from KB
            design_principles: Design principles from KB
            data_context: REAL DATA from API (pipelines with actual metrics)
            gradient_context: Domain-aware pattern boosts from gradient system

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

        # BOLD, CONFIDENT DESIGN MODE
        prompt = f"""You are a senior product designer who previously led design at Stripe/Linear/Vercel.

Design a {screen_type} for: {user_intent}

Data: {len(data_sources)} datasets{data_section}{real_data_section}{gradient_hints}{feedback_section}

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

INTERACTIONS: [list 3-5 interactions with visual feedback]

VISUAL HIERARCHY: [describe how to guide the eye - what's bold, what's large, what's emphasized]

Design confident, opinionated interfaces. M3 is your foundation, not your ceiling.
"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,  # Increased for detailed styling + icon guidance
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
                # Extract which patterns were referenced
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

    def _create_design_spec(
        self,
        design_reasoning: str,
        requirements: Dict,
        ux_patterns: Dict,
        gradient_context: Dict = None
    ) -> DesignSpec:
        """
        Create design specification from reasoning

        Args:
            design_reasoning: CoT reasoning from design process
            requirements: User requirements
            ux_patterns: UX patterns from KB
            gradient_context: Domain-aware pattern boost flags
        """
        print("  [UX Designer] Creating design specification...")

        # Extract from requirements
        screen_type = requirements.get('screen_type', 'dashboard')
        user_intent = requirements.get('intent', 'view and manage data')
        data_sources = requirements.get('data_sources', {})

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

        return DesignSpec(
            screen_type=screen_type,
            intent=user_intent,
            components=components,
            interactions=interactions,
            patterns=pattern_list,
            styling=styling,
            recommended_pattern=None,  # Not used in Pure Lovable approach
            design_reasoning=design_reasoning,  # Pass full design reasoning (includes ICONS)
            data_sources=data_sources  # Phase 2: Pass discovered metadata to React Developer
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
