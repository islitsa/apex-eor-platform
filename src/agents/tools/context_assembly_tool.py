"""
Context Assembly Tool - Phase 3 Step 2

Responsibility: Session context building and scope determination.
Depends on: DataShapingTool (for pipeline normalization and record counts)

This tool handles:
1. Building SessionContext from requirements and discovered data
2. Parsing user intent and inferring task types
3. Determining scope from filtered pipelines
4. Creating DiscoveryContext, UserIntent, and ExecutionContext components
"""

from typing import Dict, Any, List
import uuid

from src.agents.context.protocol import (
    SessionContext, DiscoveryContext, UserIntent,
    ExecutionContext, TaskType, OutputFormat
)
from src.agents.tools.data_shaping_tool import DataShapingTool


class ContextAssemblyTool:
    """
    Phase 3: Extract session context assembly logic from orchestrator.

    This tool builds SessionContext from requirements and discovered data,
    making it easier to test and reuse context building logic.
    """

    def __init__(self, shaping_tool: DataShapingTool = None):
        """
        Initialize the context assembly tool.

        Args:
            shaping_tool: DataShapingTool instance (or create new one)
        """
        self.shaping_tool = shaping_tool or DataShapingTool()

    def build_session_context(
        self,
        requirements: Dict[str, Any],
        data_context: Dict,
        knowledge: Dict
    ) -> SessionContext:
        """
        Build SessionContext from requirements and discovered data.

        This is the critical method that transforms legacy dict-based context
        into type-safe SessionContext for protocol-aware execution.

        Args:
            requirements: User requirements dict
            data_context: Real data from API (with filtered pipelines)
            knowledge: Retrieved knowledge

        Returns:
            SessionContext with discovery, intent, execution settings
        """
        print("\n[ContextAssemblyTool] Building SessionContext...")

        # Extract discovered sources from FILTERED data_context (not requirements!)
        # This ensures session_ctx uses the filtered sources, not all discovered sources
        if data_context.get('success') and data_context.get('pipelines'):
            # Use filtered pipelines from data_context
            filtered_pipelines = data_context.get('pipelines', [])

            # Use shaping tool to extract sources and record counts
            sources = self.shaping_tool.extract_sources_list(filtered_pipelines)
            record_counts = self.shaping_tool.extract_record_counts(filtered_pipelines)

            print(f"  [SessionContext] Using FILTERED sources from data_context: {sources}")
        else:
            # Fallback: use requirements (legacy)
            data_sources = requirements.get('data_sources', {})
            sources = list(data_sources.keys())
            record_counts = {
                name: info.get('row_count', 0)
                for name, info in data_sources.items()
            }
            print(f"  [SessionContext] Fallback to requirements sources: {sources}")

        print(f"  Record counts: {record_counts}")

        # Parse user intent
        user_query = requirements.get('intent', 'Generate dashboard')
        task_type = self.infer_task_type(requirements.get('screen_type', 'dashboard'))

        # Build SessionContext
        ctx = SessionContext(
            session_id=str(uuid.uuid4()),
            discovery=DiscoveryContext(
                sources=sources,
                record_counts=record_counts,
                discovery_confidence=0.95,  # High confidence from discovery tools
                rationale=user_query
            ),
            intent=UserIntent(
                original_query=user_query,
                parsed_intent="generate_dashboard",
                scope=sources,  # CRITICAL: Scope = discovered sources
                task_type=task_type,
                output_format=OutputFormat.REACT
            ),
            execution=ExecutionContext(
                trace_decisions=False  # Will be set by orchestrator based on trace_collector
            )
        )

        print(f"  Session ID: {ctx.session_id[:8]}...")
        print(f"  Intent scope: {ctx.intent.scope}")
        print(f"  Task type: {ctx.intent.task_type.value}")

        return ctx

    def infer_task_type(self, screen_type: str) -> TaskType:
        """
        Map screen_type string to TaskType enum.

        Args:
            screen_type: Screen type from requirements

        Returns:
            TaskType enum value
        """
        screen_lower = screen_type.lower()

        if 'dashboard' in screen_lower:
            return TaskType.DASHBOARD
        elif 'analysis' in screen_lower:
            return TaskType.ANALYSIS
        elif 'report' in screen_lower:
            return TaskType.REPORT

        # Default to dashboard
        return TaskType.DASHBOARD

    def update_execution_context(
        self,
        session_ctx: SessionContext,
        trace_decisions: bool = False
    ) -> SessionContext:
        """
        Update execution context settings.

        Args:
            session_ctx: Existing SessionContext
            trace_decisions: Whether to trace decisions

        Returns:
            Updated SessionContext
        """
        session_ctx.execution.trace_decisions = trace_decisions
        return session_ctx

    def prepare_builder_context(
        self,
        requirements: Dict[str, Any],
        context: Dict[str, Any],
        data_context: Dict,
        filter_tool=None
    ) -> Dict[str, Any]:
        """
        Prepare enhanced context for React Developer (builder context shaping).

        This method:
        1. Copies base context
        2. Ensures user_prompt is present (fallback to intent)
        3. Adds user_feedback if available
        4. Filters data_sources to match filtered data_context

        Args:
            requirements: User requirements with intent and feedback
            context: Base context dict
            data_context: Filtered data context from discovery
            filter_tool: DataFilterTool instance for filtering sources

        Returns:
            Enhanced context dict ready for React Developer
        """
        print("\n[ContextAssemblyTool] Preparing builder context...")

        # Start with copy of base context
        enhanced_context = dict(context)

        # Ensure user_prompt is always present (fallback to intent if missing)
        if 'user_prompt' not in enhanced_context:
            enhanced_context['user_prompt'] = requirements.get('intent', 'Generate a data UI')
            print(f"  Added user_prompt from intent")

        # Add user_feedback if present in requirements
        if 'user_feedback' in requirements:
            enhanced_context['user_feedback'] = requirements['user_feedback']
            print(f"  Added user_feedback")

        # Filter data_sources to match filtered data_context
        if data_context.get('success') and data_context.get('pipelines') and filter_tool:
            filtered_pipeline_ids = [p.get('id') for p in data_context.get('pipelines', [])]
            original_data_sources = enhanced_context.get('data_sources', {})

            enhanced_context = filter_tool.filter_context_sources(
                enhanced_context,
                filtered_pipeline_ids
            )

            new_data_sources = enhanced_context.get('data_sources', {})
            if len(new_data_sources) != len(original_data_sources):
                print(f"  Filtered data_sources: {len(original_data_sources)} -> {len(new_data_sources)}")
                print(f"  Builder will see: {list(new_data_sources.keys())}")

        return enhanced_context
