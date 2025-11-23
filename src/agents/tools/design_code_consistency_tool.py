"""
DesignCodeConsistencyTool - Phase 6.1

Compares UX spec against React implementation to detect inconsistencies.

This is a pure analyzer - it does NOT mutate any outputs.
It only produces Conflict[] objects that accumulate in SharedMemory.

Detects:
- Missing components
- Component name mismatches
- Prop list mismatches
- Attribute mismatches
- Incorrect data bindings
- Interactive behavior mismatches
- Nested component inconsistencies
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import re
import ast


@dataclass
class ComponentSignature:
    """Extracted signature of a React component"""
    name: str
    props: List[str]
    data_sources: List[str]
    interactive: bool
    nested_components: List[str]


class DesignCodeConsistencyTool:
    """
    Phase 6.1: Consistency checker for UX spec vs React implementation.

    This tool compares:
    - UX spec component definitions
    - React implementation component signatures

    And produces Conflict[] objects for any inconsistencies.
    """

    @staticmethod
    def _normalize_component_name(name: str) -> str:
        """
        Normalize component name to PascalCase for comparison.

        Converts "Hero Metrics Card" → "HeroMetricsCard"
        Converts "Data Table" → "DataTable"
        Leaves "HeroMetricsCard" unchanged (already PascalCase)

        This allows matching UX spec names (with spaces) against React component names (PascalCase).
        """
        if not name:
            return ""

        # FIX: If already no spaces/separators (already PascalCase), return as-is
        # This prevents "DatasetOverviewCard" → "Datasetoverviewcard" bug
        if ' ' not in name and '-' not in name and '_' not in name:
            return name

        # Otherwise, convert to PascalCase by splitting on separators
        words = name.replace('-', ' ').replace('_', ' ').split()

        # Capitalize first letter of each word and join
        pascal_case = ''.join(word.capitalize() for word in words)

        return pascal_case

    def run(self, ux_spec: Any, react_files: Optional[Dict[str, str]]) -> List['Conflict']:
        """
        Analyze UX spec and React files for inconsistencies.

        Args:
            ux_spec: DesignSpec object from UX Designer
            react_files: Dict of filename -> code from React Developer

        Returns:
            List of Conflict objects
        """
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        # Early exit if inputs are missing
        if not ux_spec:
            return []

        if not react_files:
            return [Conflict(
                conflict_type=ConflictType.MISSING_COMPONENT,
                source_agent="DesignCodeConsistencyTool",
                description="No React implementation found",
                severity="critical",
                target="REACT_IMPL"
            )]

        # Extract component definitions from UX spec
        ux_components = self._extract_ux_components(ux_spec)

        # Extract component signatures from React files
        react_components = self._extract_react_components(react_files)

        # Compare components
        conflicts.extend(self._compare_components(ux_components, react_components))

        # Check data binding consistency
        conflicts.extend(self._check_data_bindings(ux_spec, react_files))

        # DEBUG: Log conflict details for investigation (Issue #6)
        if conflicts:
            print(f"\n[DEBUG DesignCodeConsistencyTool] {len(conflicts)} conflicts found:")
            for i, conflict in enumerate(conflicts[:10], 1):  # Show first 10
                print(f"  {i}. [{conflict.severity.upper()}] {conflict.description}")
                if conflict.affected_component:
                    print(f"      Component: {conflict.affected_component}")
                if conflict.suggested_resolution:
                    print(f"      Fix: {conflict.suggested_resolution}")
            if len(conflicts) > 10:
                print(f"  ... and {len(conflicts) - 10} more conflicts")
            print()

        return conflicts

    def _extract_ux_components(self, ux_spec: Any) -> Dict[str, Dict[str, Any]]:
        """
        Extract component definitions from UX spec.

        Returns:
            Dict of component_name -> component_info
        """
        components = {}

        if not hasattr(ux_spec, 'components'):
            return components

        for comp in ux_spec.components:
            # FIX: Components are dicts, not objects - use dict.get() not hasattr()
            # This was creating "Unknown" components when comp.name didn't exist as attribute
            comp_info = {
                'name': comp.get('name') if isinstance(comp, dict) else getattr(comp, 'name', None),
                'component_type': comp.get('type') if isinstance(comp, dict) else getattr(comp, 'component_type', None),
                'props': comp.get('props', {}) if isinstance(comp, dict) else getattr(comp, 'props', {}),
                'data_field': comp.get('data_field') if isinstance(comp, dict) else getattr(comp, 'data_field', None),
                'interactive': comp.get('interactive', False) if isinstance(comp, dict) else getattr(comp, 'interactive', False),
                'nested': []
            }

            # Skip components without names
            if not comp_info['name']:
                continue

            # Extract nested components if present
            nested_comps = comp.get('nested_components', []) if isinstance(comp, dict) else getattr(comp, 'nested_components', [])
            if nested_comps:
                comp_info['nested'] = [
                    nc.get('name') if isinstance(nc, dict) else getattr(nc, 'name', None)
                    for nc in nested_comps
                    if (nc.get('name') if isinstance(nc, dict) else getattr(nc, 'name', None))
                ]

            components[comp_info['name']] = comp_info

        return components

    def _extract_react_components(self, react_files: Dict[str, str]) -> Dict[str, ComponentSignature]:
        """
        Extract component signatures from React code.

        Returns:
            Dict of component_name -> ComponentSignature
        """
        components = {}

        for filename, code in react_files.items():
            if not filename.endswith(('.tsx', '.jsx')):
                continue

            # Extract function components with regex
            # Pattern: function ComponentName({prop1, prop2}: Props) or const ComponentName = ({props}) =>
            function_pattern = r'(?:function|const)\s+(\w+)\s*(?:=\s*)?\(\s*\{([^}]*)\}'
            matches = re.finditer(function_pattern, code)

            for match in matches:
                comp_name = match.group(1)
                props_str = match.group(2)

                # Parse props
                props = [p.strip() for p in props_str.split(',') if p.strip()]

                # Detect data sources (look for data references in the code)
                data_sources = self._extract_data_sources(code, comp_name)

                # Detect interactivity (presence of event handlers)
                interactive = self._detect_interactivity(code, comp_name)

                # Detect nested components
                nested = self._detect_nested_components(code, comp_name, components.keys())

                components[comp_name] = ComponentSignature(
                    name=comp_name,
                    props=props,
                    data_sources=data_sources,
                    interactive=interactive,
                    nested_components=nested
                )

        return components

    def _extract_data_sources(self, code: str, component_name: str) -> List[str]:
        """Extract data source references from component code"""
        sources = []

        # Look for common data patterns
        patterns = [
            r'data\[[\'"]([\w]+)[\'"]',  # data['source']
            r'dataContext\.(\w+)',         # dataContext.source
            r'\.map\((\w+)\s*=>',          # array.map patterns
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                source = match.group(1)
                if source and source not in sources:
                    sources.append(source)

        return sources

    def _detect_interactivity(self, code: str, component_name: str) -> bool:
        """Detect if component has interactive elements"""
        interactive_patterns = [
            r'onClick',
            r'onChange',
            r'onSubmit',
            r'onHover',
            r'useState',
            r'useCallback',
        ]

        for pattern in interactive_patterns:
            if re.search(pattern, code):
                return True

        return False

    def _detect_nested_components(self, code: str, component_name: str,
                                   known_components: List[str]) -> List[str]:
        """Detect nested component usage"""
        nested = []

        for known_comp in known_components:
            # Look for component usage: <ComponentName ... />
            if re.search(rf'<{known_comp}[\s/>]', code):
                nested.append(known_comp)

        return nested

    def _compare_components(self, ux_components: Dict[str, Dict],
                           react_components: Dict[str, ComponentSignature]) -> List['Conflict']:
        """
        Compare UX and React components for inconsistencies.

        FIX: Now uses normalized names (PascalCase) for matching to handle:
        - UX spec: "Hero Metrics Card"
        - React impl: "HeroMetricsCard"
        """
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        # Build mapping of normalized names to React components
        react_normalized = {}
        for react_name, react_comp in react_components.items():
            normalized = self._normalize_component_name(react_name)
            react_normalized[normalized] = (react_name, react_comp)

        # Check for missing components
        for ux_name, ux_comp in ux_components.items():
            # Normalize UX name for comparison
            ux_normalized = self._normalize_component_name(ux_name)

            # Try to find matching React component by normalized name
            if ux_normalized not in react_normalized:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.MISSING_COMPONENT,
                    source_agent="DesignCodeConsistencyTool",
                    description=f"Component '{ux_name}' defined in UX spec but missing in React implementation",
                    affected_component=ux_name,
                    suggested_resolution=f"Implement {ux_name} component in React (as {ux_normalized}.tsx)",
                    severity="high",
                    target="REACT_IMPL",
                    path=f"/components/{ux_normalized}"
                ))
                continue

            react_name, react_comp = react_normalized[ux_normalized]

            # Names match (normalized), no need to check for exact match since
            # UX spec uses "Hero Metrics Card" and React uses "HeroMetricsCard" (both valid)

            # Check props consistency
            ux_props = set(ux_comp.get('props', {}).keys())
            react_props = set(react_comp.props)

            missing_props = ux_props - react_props
            if missing_props:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.PROP_LIST_MISMATCH,
                    source_agent="DesignCodeConsistencyTool",
                    description=f"Component '{ux_name}' missing props in React: {missing_props}",
                    affected_component=ux_name,
                    suggested_resolution=f"Add props {missing_props} to {ux_name}",
                    severity="medium",
                    target="REACT_IMPL",
                    path=f"/components/{ux_name}/props"
                ))

            # Check interactivity consistency
            ux_interactive = ux_comp.get('interactive', False)
            if ux_interactive and not react_comp.interactive:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.INTERACTIVE_MISMATCH,
                    source_agent="DesignCodeConsistencyTool",
                    description=f"Component '{ux_name}' marked interactive in UX but has no event handlers in React",
                    affected_component=ux_name,
                    suggested_resolution=f"Add event handlers to {ux_name}",
                    severity="medium",
                    target="REACT_IMPL"
                ))

            # Check nested components
            ux_nested = set(ux_comp.get('nested', []))
            react_nested = set(react_comp.nested_components)

            missing_nested = ux_nested - react_nested
            if missing_nested:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.NESTED_COMPONENT_INCONSISTENCY,
                    source_agent="DesignCodeConsistencyTool",
                    description=f"Component '{ux_name}' missing nested components in React: {missing_nested}",
                    affected_component=ux_name,
                    severity="low",
                    target="REACT_IMPL"
                ))

        # Check for extra components in React not in UX spec
        # Build normalized UX component names set
        ux_normalized_names = {self._normalize_component_name(name) for name in ux_components.keys()}

        for react_name in react_components:
            react_normalized = self._normalize_component_name(react_name)

            # Check if React component exists in UX spec (by normalized name)
            if react_normalized not in ux_normalized_names:
                # Only warn about this if it looks like a main component (starts with capital)
                if react_name[0].isupper():
                    conflicts.append(Conflict(
                        conflict_type=ConflictType.MISSING_COMPONENT,
                        source_agent="DesignCodeConsistencyTool",
                        description=f"Component '{react_name}' exists in React but not defined in UX spec",
                        affected_component=react_name,
                        severity="low",
                        target="UX_SPEC"
                    ))

        return conflicts

    def _check_data_bindings(self, ux_spec: Any, react_files: Dict[str, str]) -> List['Conflict']:
        """Check that data bindings in React match UX spec"""
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        if not hasattr(ux_spec, 'data_sources'):
            return conflicts

        # Extract data source names from UX spec
        ux_data_sources = set(ux_spec.data_sources.keys()) if ux_spec.data_sources else set()

        # Check each React file for data references
        for filename, code in react_files.items():
            # Look for data references that don't match UX spec
            data_refs = re.findall(r'data\[[\'"]([\w]+)[\'"]', code)

            for ref in data_refs:
                if ref not in ux_data_sources:
                    conflicts.append(Conflict(
                        conflict_type=ConflictType.DATA_BINDING_INCORRECT,
                        source_agent="DesignCodeConsistencyTool",
                        description=f"Data reference '{ref}' in {filename} not found in UX spec data_sources",
                        severity="high",
                        target="BOTH",
                        suggested_resolution=f"Either add '{ref}' to UX spec or update React code"
                    ))

        return conflicts
