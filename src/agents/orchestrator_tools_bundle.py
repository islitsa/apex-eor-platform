"""
Orchestrator Tools Bundle - Phase 7.1

This module defines the OrchestratorTools dataclass that bundles all tools
used by the orchestrator agent. This provides:

1. Explicit dependency injection (no hidden coupling)
2. Clear interface of what tools the agent can use
3. Easy testing (can mock the entire bundle)
4. Prevents agent from reimplementing tools

The orchestrator agent operates on this bundle instead of accessing
UICodeOrchestrator's internal state.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OrchestratorTools:
    """
    Bundle of all tools available to the orchestrator agent.

    These tools represent the "what" - the capabilities available.
    The agent decides "when" and "how" to use them.

    Phase 1-2 Tools:
    - data_discovery: Fetches real data from API
    - data_filter: Filters data sources based on user intent
    - data_shaping: Shapes data into usable format
    - pipeline_assembly: Assembles pipelines with stage detection (MANDATORY before UX/React)

    Phase 3 Tools:
    - context_assembly: Builds SessionContext and builder context
    - knowledge: Retrieves knowledge from Pinecone
    - knowledge_assembly: Assembles knowledge for UX/React
    - execution: Executes UX/React agents with retry logic

    Phase 6.1 Tools (Consistency Checking):
    - design_code_consistency: Checks UX spec vs React implementation
    - schema_alignment: Validates data schema alignment
    - knowledge_conflict: Checks domain knowledge consistency
    - component_compatibility: Validates component dependencies
    """

    # Phase 1-2: Data discovery and filtering
    data_discovery: 'DataDiscoveryTool'
    data_filter: 'DataFilterTool'
    data_shaping: 'DataShapingTool'
    pipeline_assembly: 'PipelineAssemblyTool'

    # Phase 3: Context and knowledge assembly
    context_assembly: 'ContextAssemblyTool'
    knowledge: 'KnowledgeTool'
    knowledge_assembly: 'KnowledgeAssemblyTool'
    execution: 'ExecutionTool'

    # Phase 6.1: Consistency checking (observe-only)
    design_code_consistency: 'DesignCodeConsistencyTool'
    schema_alignment: 'SchemaAlignmentTool'
    knowledge_conflict: 'KnowledgeConflictTool'
    component_compatibility: 'ComponentCompatibilityTool'

    # Optional: trace collector for debugging
    trace_collector: Optional[any] = None

    def __post_init__(self):
        """Validate that all required tools are present."""
        required_tools = [
            'data_discovery',
            'data_filter',
            'data_shaping',
            'pipeline_assembly',
            'context_assembly',
            'knowledge',
            'knowledge_assembly',
            'execution',
            'design_code_consistency',
            'schema_alignment',
            'knowledge_conflict',
            'component_compatibility',
        ]

        for tool_name in required_tools:
            tool = getattr(self, tool_name)
            if tool is None:
                raise ValueError(f"Required tool '{tool_name}' is None")

    def validate(self):
        """
        Validate that all tools are properly initialized.

        Raises:
            ValueError: If any required tool is missing or invalid
        """
        self.__post_init__()
        print("[OrchestratorTools] All 12 tools validated successfully")
