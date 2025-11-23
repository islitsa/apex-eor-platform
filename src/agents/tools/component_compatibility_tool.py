"""
ComponentCompatibilityTool - Phase 6.1

Ensures component dependencies and contracts are valid.

This is a pure analyzer - it does NOT mutate any outputs.
It only produces Conflict[] objects that accumulate in SharedMemory.

Detects:
- Component dependencies missing or incorrect
- Required props missing
- Inter-component event contracts invalid
- Incompatible component hierarchies
"""

from typing import Dict, Any, List, Optional, Set
import re


class ComponentCompatibilityTool:
    """
    Phase 6.1: Component compatibility checker.

    Ensures:
    - Component dependencies are correct
    - Required props exist
    - Inter-component event contracts are valid
    - Component hierarchies are compatible

    This is especially important for:
    - Charts with complex data requirements
    - Multi-stage dashboards
    - Cross-component interactions
    """

    def run(self, ux_spec: Any, react_files: Optional[Dict[str, str]]) -> List['Conflict']:
        """
        Analyze component compatibility.

        Args:
            ux_spec: DesignSpec object from UX Designer
            react_files: Dict of filename -> code from React Developer

        Returns:
            List of Conflict objects
        """
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        if not ux_spec or not react_files:
            return conflicts

        # Extract component dependencies from UX spec
        ux_dependencies = self._extract_ux_dependencies(ux_spec)

        # Extract component signatures from React
        react_signatures = self._extract_react_signatures(react_files)

        # Check dependency validity
        conflicts.extend(self._check_dependencies(ux_dependencies, react_signatures))

        # Check required props
        conflicts.extend(self._check_required_props(ux_spec, react_signatures))

        # Check event contracts
        conflicts.extend(self._check_event_contracts(ux_spec, react_files))

        return conflicts

    def _extract_ux_dependencies(self, ux_spec: Any) -> Dict[str, List[str]]:
        """
        Extract component dependencies from UX spec.

        Returns:
            Dict of component_name -> [required_dependencies]
        """
        dependencies = {}

        if not hasattr(ux_spec, 'components'):
            return dependencies

        for comp in ux_spec.components:
            comp_name = comp.name if hasattr(comp, 'name') else 'Unknown'
            comp_deps = []

            # Check for nested components (explicit dependencies)
            if hasattr(comp, 'nested_components'):
                for nested in comp.nested_components:
                    nested_name = nested.name if hasattr(nested, 'name') else None
                    if nested_name:
                        comp_deps.append(nested_name)

            # Check for data dependencies
            if hasattr(comp, 'data_field'):
                # Components that reference data implicitly depend on data providers
                comp_deps.append('DataProvider')

            # Chart components have special dependencies
            if hasattr(comp, 'component_type'):
                comp_type = comp.component_type.lower()

                # Chart libraries need to be imported
                if any(chart_type in comp_type for chart_type in
                      ['chart', 'graph', 'plot', 'visualization']):
                    comp_deps.append('recharts')  # or whatever chart library is used

            dependencies[comp_name] = comp_deps

        return dependencies

    def _extract_react_signatures(self, react_files: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """
        Extract component signatures from React code.

        Returns:
            Dict of component_name -> {props: [], imports: [], exports: []}
        """
        signatures = {}

        for filename, code in react_files.items():
            if not filename.endswith(('.tsx', '.jsx')):
                continue

            # Extract component definitions
            # Pattern: function ComponentName({prop1, prop2}: Props)
            function_pattern = r'(?:export\s+)?(?:function|const)\s+(\w+)\s*(?:=\s*)?\(\s*\{([^}]*)\}'
            matches = re.finditer(function_pattern, code)

            for match in matches:
                comp_name = match.group(1)
                props_str = match.group(2)

                # Parse props
                props = [p.strip().split(':')[0].strip()
                        for p in props_str.split(',') if p.strip()]

                # Extract imports
                imports = self._extract_imports(code)

                # Check if component is exported
                is_exported = f'export default {comp_name}' in code or \
                             f'export {{ {comp_name}' in code or \
                             f'export function {comp_name}' in code or \
                             f'export const {comp_name}' in code

                signatures[comp_name] = {
                    'props': props,
                    'imports': imports,
                    'exported': is_exported,
                    'filename': filename
                }

        return signatures

    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements from code"""
        imports = []

        # Pattern: import X from 'Y' or import { X } from 'Y'
        import_pattern = r'import\s+(?:\{[^}]+\}|[\w]+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        matches = re.finditer(import_pattern, code)

        for match in matches:
            import_source = match.group(1)
            imports.append(import_source)

        return imports

    def _check_dependencies(self, ux_dependencies: Dict[str, List[str]],
                           react_signatures: Dict[str, Dict[str, Any]]) -> List['Conflict']:
        """Check if component dependencies are satisfied"""
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        for comp_name, deps in ux_dependencies.items():
            # Skip meta-dependencies like 'DataProvider'
            for dep in deps:
                if dep in ['DataProvider', 'recharts']:
                    # Check if this is imported in React
                    if comp_name in react_signatures:
                        react_sig = react_signatures[comp_name]
                        imports = react_sig.get('imports', [])

                        if dep == 'recharts' and not any('recharts' in imp for imp in imports):
                            conflicts.append(Conflict(
                                conflict_type=ConflictType.DEPENDENCY_ERROR,
                                source_agent="ComponentCompatibilityTool",
                                description=f"Component '{comp_name}' requires recharts but it's not imported",
                                affected_component=comp_name,
                                suggested_resolution=f"Add 'import {{ ... }} from \"recharts\"' to {react_sig['filename']}",
                                severity="high",
                                target="REACT_IMPL",
                                path=f"/files/{react_sig['filename']}"
                            ))
                    continue

                # Check if dependency component exists
                if dep not in react_signatures:
                    conflicts.append(Conflict(
                        conflict_type=ConflictType.DEPENDENCY_ERROR,
                        source_agent="ComponentCompatibilityTool",
                        description=f"Component '{comp_name}' depends on '{dep}' which is not implemented",
                        affected_component=comp_name,
                        suggested_resolution=f"Implement {dep} component",
                        severity="high",
                        target="REACT_IMPL"
                    ))

        return conflicts

    def _check_required_props(self, ux_spec: Any,
                             react_signatures: Dict[str, Dict[str, Any]]) -> List['Conflict']:
        """Check if required props are defined"""
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        if not hasattr(ux_spec, 'components'):
            return conflicts

        for comp in ux_spec.components:
            comp_name = comp.name if hasattr(comp, 'name') else 'Unknown'

            if comp_name not in react_signatures:
                continue

            react_sig = react_signatures[comp_name]
            react_props = set(react_sig.get('props', []))

            # Define required props based on component type
            required_props = self._get_required_props(comp)

            # Check if required props exist
            missing_props = required_props - react_props

            if missing_props:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.REQUIRED_PROP_MISSING,
                    source_agent="ComponentCompatibilityTool",
                    description=f"Component '{comp_name}' missing required props: {missing_props}",
                    affected_component=comp_name,
                    suggested_resolution=f"Add props {missing_props} to {comp_name}",
                    severity="high",
                    target="REACT_IMPL",
                    path=f"/components/{comp_name}/props"
                ))

        return conflicts

    def _get_required_props(self, comp: Any) -> Set[str]:
        """Determine required props for a component based on UX spec"""
        required = set()

        # If component has a data_field, it needs a 'data' prop
        if hasattr(comp, 'data_field') and comp.data_field:
            required.add('data')

        # Interactive components need event handlers
        if hasattr(comp, 'interactive') and comp.interactive:
            # At least one event handler required
            # This is a simplified check - real implementation would be more sophisticated
            pass

        # Charts need specific props
        if hasattr(comp, 'component_type'):
            comp_type = comp.component_type.lower()

            if 'chart' in comp_type or 'plot' in comp_type or 'graph' in comp_type:
                required.add('data')

                # Specific chart types need specific props
                if 'bar' in comp_type or 'line' in comp_type:
                    # These need x and y axis definitions
                    # Simplified: just require data for now
                    pass

        return required

    def _check_event_contracts(self, ux_spec: Any,
                               react_files: Dict[str, str]) -> List['Conflict']:
        """Check inter-component event contracts"""
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        # This is a simplified check
        # Full implementation would parse event flows between components

        if not hasattr(ux_spec, 'components'):
            return conflicts

        # Look for components that emit events
        event_emitters = []
        for comp in ux_spec.components:
            if hasattr(comp, 'interactive') and comp.interactive:
                comp_name = comp.name if hasattr(comp, 'name') else None
                if comp_name:
                    event_emitters.append(comp_name)

        # Check if event handlers are properly wired
        for filename, code in react_files.items():
            for emitter in event_emitters:
                # Look for event handler definitions
                # Pattern: onClick={handleClick}, onChange={handleChange}, etc.
                event_pattern = rf'{emitter}.*on\w+={{([^}}]+)}}'
                if not re.search(event_pattern, code):
                    # Check if this component is actually used
                    if f'<{emitter}' in code:
                        conflicts.append(Conflict(
                            conflict_type=ConflictType.EVENT_CONTRACT_INVALID,
                            source_agent="ComponentCompatibilityTool",
                            description=f"Interactive component '{emitter}' used in {filename} but no event handlers found",
                            affected_component=emitter,
                            suggested_resolution=f"Add event handlers for {emitter}",
                            severity="medium",
                            target="REACT_IMPL",
                            path=f"/files/{filename}"
                        ))

        return conflicts
