"""
Knowledge Assembly Tool - Phase 3 Step 3

Responsibility: Knowledge bundle assembly and gradient merging.
Depends on: KnowledgeTool (for Pinecone queries) and DataShapingTool (for data context)

This tool handles:
1. High-level knowledge retrieval orchestration
2. Agent-specific knowledge bundling (UX vs React)
3. Gradient context merging with knowledge
4. Knowledge caching and reuse
"""

from typing import Dict, Any, Optional


class KnowledgeAssemblyTool:
    """
    Phase 3: High-level knowledge assembly and agent-specific bundling.

    This tool wraps KnowledgeTool and provides:
    - Agent-specific knowledge extraction
    - Knowledge caching for iteration reuse
    - Clean interface for orchestrator
    """

    def __init__(self, knowledge_tool=None):
        """
        Initialize the knowledge assembly tool.

        Args:
            knowledge_tool: KnowledgeTool instance for Pinecone queries
        """
        self.knowledge_tool = knowledge_tool
        self.knowledge_cache = None

    def retrieve_and_assemble_knowledge(
        self,
        data_context: Dict,
        enable_gradient: bool = False,
        use_cache: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieve all knowledge and assemble complete knowledge bundle.

        This orchestrates the knowledge retrieval process:
        1. Check cache if enabled
        2. Use KnowledgeTool to query Pinecone
        3. Cache results for potential reuse

        Args:
            data_context: Real data from API for gradient boosting
            enable_gradient: Whether to apply gradient context boosting
            use_cache: Whether to use cached knowledge (for iterations)

        Returns:
            Complete knowledge bundle with all categories
        """
        # Use cache if available and requested
        if use_cache and self.knowledge_cache:
            print("[KnowledgeAssemblyTool] Using cached knowledge")
            return self.knowledge_cache

        # Delegate to KnowledgeTool for actual retrieval
        if not self.knowledge_tool:
            print("[KnowledgeAssemblyTool] WARNING: No knowledge_tool provided")
            return self._empty_knowledge()

        knowledge = self.knowledge_tool.retrieve_all_knowledge(
            data_context=data_context,
            enable_gradient=enable_gradient
        )

        # Cache for potential reuse
        self.knowledge_cache = knowledge

        return knowledge

    def assemble_ux_knowledge(
        self,
        knowledge: Dict[str, Any],
        data_context: Dict
    ) -> Dict[str, Any]:
        """
        Assemble knowledge bundle specifically for UX Designer.

        Includes:
        - UX patterns (master-detail, progressive disclosure, etc.)
        - Design principles (typography, colors, spacing)
        - Real data context
        - Gradient context (if available)

        Args:
            knowledge: Complete knowledge bundle from retrieve_and_assemble_knowledge
            data_context: Real data from API

        Returns:
            Knowledge bundle tailored for UX Designer
        """
        return {
            'ux_patterns': knowledge.get('ux_patterns', {}),
            'design_principles': knowledge.get('design_principles', {}),
            'data_context': data_context,
            'gradient_context': knowledge.get('gradient_context')
        }

    def assemble_react_knowledge(
        self,
        knowledge: Dict[str, Any],
        data_context: Dict,
        enhanced_context: Dict
    ) -> Dict[str, Any]:
        """
        Assemble knowledge for React Developer.

        Includes:
        - Design principles (same as UX Designer)
        - Gradio constraints (framework-specific)
        - Real data context
        - Gradient context (if available)
        - Enhanced context from orchestrator

        Args:
            knowledge: Complete knowledge bundle
            data_context: Real data from API
            enhanced_context: Additional context from orchestrator

        Returns:
            Enhanced context with knowledge for React Developer
        """
        # Build enhanced context with knowledge
        result = dict(enhanced_context)

        result['knowledge'] = {
            'design_principles': knowledge.get('design_principles', {}),
            'gradio_constraints': knowledge.get('gradio_constraints', {})
        }
        result['data_context'] = data_context
        result['gradient_context'] = knowledge.get('gradient_context')

        return result

    def clear_cache(self):
        """Clear knowledge cache (useful when starting new session)"""
        self.knowledge_cache = None
        print("[KnowledgeAssemblyTool] Cache cleared")

    def has_cached_knowledge(self) -> bool:
        """Check if knowledge is cached"""
        return self.knowledge_cache is not None

    def _empty_knowledge(self) -> Dict[str, Any]:
        """Return empty knowledge structure"""
        return {
            'ux_patterns': {},
            'design_principles': {},
            'gradio_constraints': {},
        }
