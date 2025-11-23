"""
KnowledgeConflictTool - Phase 6.1

Compares domain knowledge against UX affordances and React implementations.

This is a pure analyzer - it does NOT mutate any outputs.
It only produces Conflict[] objects that accumulate in SharedMemory.

Detects:
- Invalid domain assumptions
- Dangerous affordances (e.g., mixing stage 1 + stage 2 incorrectly)
- Incorrect labeling
- Out-of-domain patterns
"""

from typing import Dict, Any, List, Optional


class KnowledgeConflictTool:
    """
    Phase 6.1: Knowledge consistency checker.

    Compares:
    - Domain knowledge (from gradient-assembled knowledge)
    - UX design affordances
    - React implementation patterns

    Detects domain-level inconsistencies and dangerous patterns.
    """

    def run(self, knowledge: Dict, ux_spec: Any,
            react_files: Optional[Dict[str, str]]) -> List['Conflict']:
        """
        Analyze knowledge alignment across domain, UX, and React.

        Args:
            knowledge: Domain knowledge from KnowledgeAssemblyTool
            ux_spec: DesignSpec object from UX Designer
            react_files: Dict of filename -> code from React Developer

        Returns:
            List of Conflict objects
        """
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        if not knowledge:
            # No knowledge available - can't validate
            return conflicts

        # Extract domain constraints from knowledge
        domain_rules = self._extract_domain_rules(knowledge)

        # Check UX affordances against domain knowledge
        if ux_spec:
            conflicts.extend(self._check_ux_domain_alignment(ux_spec, domain_rules, knowledge))

        # Check React implementation against domain knowledge
        if react_files:
            conflicts.extend(self._check_react_domain_alignment(react_files, domain_rules, knowledge))

        return conflicts

    def _extract_domain_rules(self, knowledge: Dict) -> Dict[str, Any]:
        """
        Extract domain rules and constraints from knowledge.

        Returns:
            Dict of rule_type -> rules
        """
        rules = {
            'stage_separation': [],
            'required_fields': [],
            'forbidden_combinations': [],
            'labeling_conventions': [],
            'valid_patterns': []
        }

        # Extract from knowledge structure
        if 'design_patterns' in knowledge:
            patterns = knowledge['design_patterns']
            if isinstance(patterns, list):
                for pattern in patterns:
                    if isinstance(pattern, dict):
                        # Extract stage-related rules
                        if 'stage' in pattern:
                            rules['stage_separation'].append(pattern)

                        # Extract field requirements
                        if 'required_fields' in pattern:
                            rules['required_fields'].extend(pattern['required_fields'])

                        # Extract forbidden combinations
                        if 'forbidden' in pattern:
                            rules['forbidden_combinations'].append(pattern['forbidden'])

        # Extract from gradient knowledge if present
        if 'gradient_insights' in knowledge:
            insights = knowledge['gradient_insights']
            if isinstance(insights, dict):
                # Extract labeling conventions
                if 'labeling' in insights:
                    rules['labeling_conventions'] = insights['labeling']

                # Extract valid patterns
                if 'patterns' in insights:
                    rules['valid_patterns'] = insights['patterns']

        return rules

    def _check_ux_domain_alignment(self, ux_spec: Any, domain_rules: Dict,
                                   knowledge: Dict) -> List['Conflict']:
        """Check UX spec against domain knowledge"""
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        # Check for stage mixing (dangerous pattern)
        conflicts.extend(self._check_stage_mixing(ux_spec, domain_rules))

        # Check for invalid field usage
        conflicts.extend(self._check_field_usage(ux_spec, domain_rules))

        # Check labeling conventions
        conflicts.extend(self._check_labeling(ux_spec, domain_rules))

        # Check for out-of-domain patterns
        conflicts.extend(self._check_domain_patterns(ux_spec, domain_rules))

        return conflicts

    def _check_react_domain_alignment(self, react_files: Dict[str, str],
                                     domain_rules: Dict,
                                     knowledge: Dict) -> List['Conflict']:
        """Check React implementation against domain knowledge"""
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        # For now, we focus on UX-level domain checks
        # React-level domain checks would look for anti-patterns in code
        # This can be expanded in future phases

        return conflicts

    def _check_stage_mixing(self, ux_spec: Any, domain_rules: Dict) -> List['Conflict']:
        """
        Check for dangerous stage mixing.

        Example: Combining pre-processing (stage 1) and post-processing (stage 2)
        in a single visualization without clear separation.
        """
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        if not hasattr(ux_spec, 'components'):
            return conflicts

        # Track which stages are used
        stages_used = set()

        for comp in ux_spec.components:
            if hasattr(comp, 'props') and isinstance(comp.props, dict):
                # Check for stage indicators in props
                if 'stage' in comp.props:
                    stage = comp.props['stage']
                    stages_used.add(stage)

                # Check data_field for stage indicators
                if hasattr(comp, 'data_field'):
                    field = comp.data_field
                    if 'stage1' in field.lower() or 'raw' in field.lower():
                        stages_used.add('stage1')
                    elif 'stage2' in field.lower() or 'processed' in field.lower():
                        stages_used.add('stage2')

        # Check for dangerous stage mixing
        if 'stage1' in stages_used and 'stage2' in stages_used:
            # Check if there's proper separation
            has_separation = hasattr(ux_spec, 'layout') and 'tabs' in str(ux_spec.layout).lower()

            if not has_separation:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.DANGEROUS_AFFORDANCE,
                    source_agent="KnowledgeConflictTool",
                    description="UX spec mixes stage 1 (raw) and stage 2 (processed) data without clear separation",
                    suggested_resolution="Use tabs or separate views to clearly distinguish stages",
                    severity="high",
                    target="UX_SPEC",
                    path="/layout"
                ))

        return conflicts

    def _check_field_usage(self, ux_spec: Any, domain_rules: Dict) -> List['Conflict']:
        """Check if required fields are used correctly"""
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        if not hasattr(ux_spec, 'components'):
            return conflicts

        required_fields = domain_rules.get('required_fields', [])

        # Check if any components use required fields
        fields_used = set()
        for comp in ux_spec.components:
            if hasattr(comp, 'data_field') and comp.data_field:
                fields_used.add(comp.data_field)

        # Check for missing critical fields
        for required_field in required_fields:
            if required_field not in fields_used:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.INVALID_DOMAIN_ASSUMPTION,
                    source_agent="KnowledgeConflictTool",
                    description=f"Required domain field '{required_field}' not used in any component",
                    suggested_resolution=f"Add component using '{required_field}'",
                    severity="medium",
                    target="UX_SPEC"
                ))

        return conflicts

    def _check_labeling(self, ux_spec: Any, domain_rules: Dict) -> List['Conflict']:
        """Check labeling conventions"""
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        if not hasattr(ux_spec, 'components'):
            return conflicts

        labeling_conventions = domain_rules.get('labeling_conventions', {})

        if not labeling_conventions:
            return conflicts

        # Check component labels
        for comp in ux_spec.components:
            comp_name = comp.name if hasattr(comp, 'name') else None

            if not comp_name:
                continue

            # Check if label follows conventions
            if hasattr(comp, 'props') and isinstance(comp.props, dict):
                label = comp.props.get('label', comp.props.get('title', ''))

                # Check for common labeling errors
                if label:
                    # Check for technical field names in labels (bad UX)
                    if '_' in label or label.islower() and len(label.split()) == 1:
                        conflicts.append(Conflict(
                            conflict_type=ConflictType.INCORRECT_LABELING,
                            source_agent="KnowledgeConflictTool",
                            description=f"Component '{comp_name}' uses technical field name as label: '{label}'",
                            affected_component=comp_name,
                            suggested_resolution="Use human-readable label",
                            severity="low",
                            target="UX_SPEC",
                            path=f"/components/{comp_name}/props/label"
                        ))

        return conflicts

    def _check_domain_patterns(self, ux_spec: Any, domain_rules: Dict) -> List['Conflict']:
        """Check for out-of-domain patterns"""
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        if not hasattr(ux_spec, 'components'):
            return conflicts

        valid_patterns = domain_rules.get('valid_patterns', [])

        if not valid_patterns:
            return conflicts

        # Check if UX spec uses valid patterns
        # This is a simplified check - can be expanded with more sophisticated pattern matching

        component_types = set()
        for comp in ux_spec.components:
            if hasattr(comp, 'component_type'):
                component_types.add(comp.component_type.lower())

        # Check for unusual combinations
        unusual_combinations = [
            (['pie_chart', 'bar_chart'], 'Multiple aggregate visualizations may confuse users'),
            (['table', 'data_grid', 'list'], 'Multiple tabular components may be redundant'),
        ]

        for combination, message in unusual_combinations:
            matching = [ct for ct in combination if ct in component_types]
            if len(matching) > 1:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.OUT_OF_DOMAIN_PATTERN,
                    source_agent="KnowledgeConflictTool",
                    description=message,
                    suggested_resolution="Consider consolidating similar visualizations",
                    severity="low",
                    target="UX_SPEC"
                ))

        return conflicts
