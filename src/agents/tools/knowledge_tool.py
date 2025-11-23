"""
KnowledgeTool - Phase 1.6

Encapsulates knowledge retrieval logic for fetching design patterns from Pinecone.

This tool isolates all knowledge base queries, making it:
- Testable without running full orchestrator
- Mock-able for unit tests
- Reusable across different orchestration strategies
"""

from typing import Dict, List, Optional, Any


class KnowledgeTool:
    """
    Handles knowledge retrieval by querying Pinecone design knowledge base.

    Phase 1.6: Extracted from orchestrator to centralize knowledge queries.
    """

    def __init__(self, design_kb=None, gradient_system=None, trace_collector=None):
        """
        Initialize KnowledgeTool.

        Args:
            design_kb: DesignKnowledgeBasePinecone instance for querying Pinecone
            gradient_system: Optional GradientContext for domain-aware boosting
            trace_collector: Optional trace collector for observability
        """
        self.design_kb = design_kb
        self.gradient_system = gradient_system
        self.trace_collector = trace_collector

    def retrieve_all_knowledge(
        self,
        data_context: Optional[Dict] = None,
        enable_gradient: bool = False
    ) -> Dict[str, Any]:
        """
        Query Pinecone ONCE for all design knowledge, optionally boosted by gradient context.

        This method performs batched queries for:
        - UX patterns (master-detail, progressive disclosure, card grid)
        - Design principles (typography, colors, spacing)
        - Gradio constraints (CSS, state, events)

        Args:
            data_context: Optional real data from API for gradient boosting
            enable_gradient: Whether to apply gradient context boosting

        Returns:
            {
                'ux_patterns': {...},        # UX patterns for UX Designer
                'design_principles': {...},  # Design principles for both agents
                'gradio_constraints': {...}, # Gradio constraints for React Developer
                'gradient_context': {...}    # Domain signals and boosting (if enabled)
            }
        """
        if not self.design_kb:
            print("[KnowledgeTool] WARNING: No design_kb provided, returning empty knowledge")
            return self._empty_knowledge()

        print("[KnowledgeTool] Retrieving design knowledge (single query batch)...")

        knowledge = {
            'ux_patterns': {},
            'design_principles': {},
            'gradio_constraints': {},
        }

        # ========================================
        # UX PATTERNS (for UX Designer)
        # ========================================
        print("  [KB] Querying UX patterns...")

        master_detail = self.design_kb.query(
            "master-detail navigation pattern",
            category="ux_patterns",
            top_k=1
        )
        if master_detail:
            knowledge['ux_patterns']['master_detail'] = master_detail[0]

        progressive = self.design_kb.query(
            "progressive disclosure hierarchy drill-down",
            category="ux_patterns",
            top_k=1
        )
        if progressive:
            knowledge['ux_patterns']['progressive_disclosure'] = progressive[0]

        card_grid = self.design_kb.query(
            "card grid layout data display",
            category="ux_patterns",
            top_k=1
        )
        if card_grid:
            knowledge['ux_patterns']['card_grid'] = card_grid[0]

        # ========================================
        # DESIGN PRINCIPLES (for both agents!)
        # ========================================
        print("  [KB] Querying design principles...")

        typography = self.design_kb.query(
            "Material Design type scale font sizes",
            category="typography",
            top_k=2
        )
        if typography:
            knowledge['design_principles']['typography'] = typography[0]

        colors = self.design_kb.query(
            "Material Design color tokens palette",
            category="colors",
            top_k=2
        )
        if colors:
            knowledge['design_principles']['colors'] = colors[0]

        spacing = self.design_kb.query(
            "Material Design 8px spacing grid",
            category="spacing",
            top_k=2
        )
        if spacing:
            knowledge['design_principles']['spacing'] = spacing[0]

        # ========================================
        # GRADIO CONSTRAINTS (for React Developer)
        # ========================================
        print("  [KB] Querying Gradio constraints...")

        css = self.design_kb.query(
            "@keyframes CSS Gradio limitations",
            category="framework",
            top_k=3
        )
        if css:
            knowledge['gradio_constraints']['css'] = css

        state = self.design_kb.query(
            "gr.State Gradio navigation state",
            category="framework",
            top_k=2
        )
        if state:
            knowledge['gradio_constraints']['state'] = state

        events = self.design_kb.query(
            "Gradio click event handler",
            category="framework",
            top_k=2
        )
        if events:
            knowledge['gradio_constraints']['events'] = events

        total_items = (
            len(knowledge['ux_patterns']) +
            len(knowledge['design_principles']) +
            len(knowledge['gradio_constraints'])
        )
        print(f"  [KB] Retrieved {total_items} knowledge items")
        print(f"       - UX patterns: {len(knowledge['ux_patterns'])}")
        print(f"       - Design principles: {len(knowledge['design_principles'])}")
        print(f"       - Gradio constraints: {len(knowledge['gradio_constraints'])}")

        # Apply gradient context boosting if enabled and data available
        if enable_gradient and self.gradient_system and data_context:
            try:
                # Extract domain signals from real data
                domain_signals = self.extract_domain_signals(data_context)

                # Emit trace: Domain extraction
                if self.trace_collector:
                    self.trace_collector.trace_thinking(
                        agent="KnowledgeTool",
                        method="retrieve_all_knowledge",
                        thought=f"🧭 Applying Gradient Context:\n  Domain: {domain_signals['domain']}\n  Structure: {domain_signals['structure']}\n  Max Depth: {domain_signals['metrics']['max_depth']}\n  Total Files: {domain_signals['metrics']['total_files']}\n  Data Types: {', '.join(domain_signals['data_types'][:3])}"
                    )

                # Build boosting context based on domain signals
                knowledge['gradient_context'] = {
                    'domain_signals': domain_signals,
                    'boost_hierarchical_navigation': domain_signals['structure'] in ['nested_directories', 'deeply_nested_directories'],
                    'boost_tree_views': domain_signals['structure'] == 'deeply_nested_directories',
                    'boost_data_drill_down': len(domain_signals['data_types']) > 0
                }

                # Emit trace: Boosting applied
                if self.trace_collector:
                    gc = knowledge['gradient_context']
                    boost_list = []
                    if gc.get('boost_hierarchical_navigation'):
                        boost_list.append("Hierarchical Navigation")
                    if gc.get('boost_tree_views'):
                        boost_list.append("Tree/Accordion Views")
                    if gc.get('boost_data_drill_down'):
                        boost_list.append("Data Drill-Down")

                    boost_msg = "\n".join([f"  ✓ {item}" for item in boost_list]) if boost_list else "  (none)"

                    self.trace_collector.trace_reasoning(
                        agent="KnowledgeTool",
                        method="retrieve_all_knowledge",
                        reasoning=f"✨ Gradient Boosting Applied:\n\n{boost_msg}\n\nThese UI patterns will be emphasized to match the {domain_signals['domain']} domain with {domain_signals['structure']} structure."
                    )

                print(f"  [Gradient] Applied domain-aware boosting: {domain_signals['domain']}")

            except Exception as e:
                print(f"[KnowledgeTool] Gradient context failed: {e}")
                # Continue without gradient - graceful degradation

        return knowledge

    def extract_domain_signals(self, data_context: Dict) -> Dict[str, Any]:
        """
        Extract domain signals from real data context for gradient navigation.

        Analyzes pipeline metadata to understand:
        - Domain (petroleum, medical, financial, etc.)
        - Data structure complexity (flat, nested, hierarchical)
        - Data types (chemical, geological, production, etc.)

        Args:
            data_context: Real data from API (DataDiscoveryTool result)

        Returns:
            {
                'domain': str,           # e.g., "petroleum_energy"
                'keywords': List[str],   # e.g., ["fracfocus", "chemical", "well"]
                'structure': str,        # e.g., "deeply_nested_directories"
                'data_types': List[str], # e.g., ["chemical_data", "completion_data"]
                'metrics': Dict          # {max_depth, total_files}
            }
        """
        if not data_context.get('success') or not data_context.get('pipelines'):
            return {
                'domain': 'generic',
                'keywords': [],
                'structure': 'flat',
                'data_types': [],
                'metrics': {'max_depth': 0, 'total_files': 0}
            }

        pipelines = data_context['pipelines']

        # Extract keywords from pipeline names
        keywords = []
        data_types = []
        for pipeline in pipelines:
            name = pipeline.get('display_name', '').lower()
            keywords.extend(name.split())

            # Identify data types
            if 'chemical' in name:
                data_types.append('chemical_data')
            if 'completion' in name or 'production' in name:
                data_types.append('operational_data')
            if 'permit' in name or 'drilling' in name:
                data_types.append('regulatory_data')

        # Detect domain from keywords
        domain = 'generic'
        if any(kw in keywords for kw in ['fracfocus', 'petroleum', 'oil', 'gas', 'well', 'rrc']):
            domain = 'petroleum_energy'
        elif any(kw in keywords for kw in ['medical', 'patient', 'clinical']):
            domain = 'healthcare'
        elif any(kw in keywords for kw in ['financial', 'transaction', 'payment']):
            domain = 'financial'

        # Analyze structure complexity
        structure = 'flat'
        total_files = 0
        max_depth = 0

        sample_pipeline = pipelines[0] if pipelines else {}
        files_obj = sample_pipeline.get('files', {})

        if isinstance(files_obj, dict):
            # Check for nested subdirs with enhanced file counting
            subdirs = files_obj.get('subdirs', {})
            if subdirs:
                def check_depth(node, depth=0):
                    nonlocal max_depth, total_files
                    max_depth = max(max_depth, depth)

                    # Count files at this level
                    if 'files' in node and isinstance(node['files'], list):
                        total_files += len(node['files'])

                    # Recurse into subdirs
                    if isinstance(node, dict) and 'subdirs' in node:
                        for subdir in node['subdirs'].values():
                            check_depth(subdir, depth + 1)

                check_depth(files_obj)

                # Classify structure based on depth AND file count
                if max_depth >= 3 and total_files > 10:
                    structure = 'deeply_nested_directories'
                elif max_depth >= 2:
                    structure = 'nested_directories'
                else:
                    structure = 'single_level_directories'

        return {
            'domain': domain,
            'keywords': list(set(keywords)),  # Remove duplicates
            'structure': structure,
            'data_types': list(set(data_types)),
            'metrics': {
                'max_depth': max_depth,
                'total_files': total_files
            }
        }

    def _empty_knowledge(self) -> Dict[str, Any]:
        """Return empty knowledge structure when design_kb is not available"""
        return {
            'ux_patterns': {},
            'design_principles': {},
            'gradio_constraints': {},
        }
