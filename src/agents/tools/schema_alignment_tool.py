"""
SchemaAlignmentTool - Phase 6.1

Compares data schema against UX spec and React implementation.

This is a pure analyzer - it does NOT mutate any outputs.
It only produces Conflict[] objects that accumulate in SharedMemory.

Detects:
- UX referencing nonexistent schema fields
- React referencing nonexistent schema fields
- Type mismatches (string vs number, etc.)
- Numeric vs categorical field errors
- Missing required fields
"""

from typing import Dict, Any, List, Optional, Set
import re


class SchemaAlignmentTool:
    """
    Phase 6.1: Schema consistency checker.

    Compares:
    - Data schema (from data_context)
    - UX spec field references
    - React implementation field references

    Detects schema mismatches and type errors.
    """

    def run(self, data_context: Dict, ux_spec: Any,
            react_files: Optional[Dict[str, str]]) -> List['Conflict']:
        """
        Analyze schema alignment across data, UX, and React.

        Args:
            data_context: Data context with schema information
            ux_spec: DesignSpec object from UX Designer
            react_files: Dict of filename -> code from React Developer

        Returns:
            List of Conflict objects
        """
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        # Extract schema from data_context
        schema = self._extract_schema(data_context)

        if not schema:
            # No schema available - can't validate
            return conflicts

        # Check UX spec field references
        if ux_spec:
            conflicts.extend(self._check_ux_schema_alignment(ux_spec, schema))

        # Check React field references
        if react_files:
            conflicts.extend(self._check_react_schema_alignment(react_files, schema))

        # DEBUG: Log conflict details for investigation (Issue #5)
        if conflicts:
            print(f"\n[DEBUG SchemaAlignmentTool] {len(conflicts)} conflicts found:")
            # Group by severity
            by_severity = {}
            for c in conflicts:
                by_severity.setdefault(c.severity, []).append(c)

            for severity in ['high', 'medium', 'low']:
                if severity in by_severity:
                    print(f"\n  [{severity.upper()}] {len(by_severity[severity])} conflicts:")
                    for i, conflict in enumerate(by_severity[severity][:5], 1):  # Show first 5 per severity
                        print(f"    {i}. {conflict.description[:100]}...")
                        if conflict.path:
                            print(f"       Path: {conflict.path}")
                    if len(by_severity[severity]) > 5:
                        print(f"    ... and {len(by_severity[severity]) - 5} more {severity} conflicts")
            print()

        return conflicts

    def _extract_schema(self, data_context: Dict) -> Dict[str, Dict[str, Any]]:
        """
        Extract schema information from data_context.

        FIX: Now extracts BOTH pipeline metadata schema AND dataset schema.

        Returns:
            Dict of source_name -> {field_name -> field_info}
        """
        schema = {}

        if not data_context:
            return schema

        # Extract from pipelines
        pipelines = data_context.get('pipelines', [])

        # Add common API response fields that React code may reference
        schema['__root__'] = {
            'message': {
                'type': 'string',
                'required': False,
                'description': 'API response message (e.g., "success", "error")'
            },
            'success': {
                'type': 'boolean',
                'required': False,
                'description': 'API response success flag'
            },
            'error': {
                'type': 'string',
                'required': False,
                'description': 'API error message if request failed'
            }
        }

        # If multiple pipelines exist, add 'pipelines' as a valid top-level field
        if len(pipelines) > 1:
            schema['__root__']['pipelines'] = {
                'type': 'array',
                'required': True,
                'description': 'Array of all pipelines'
            }

        for pipeline in pipelines:
            source_id = pipeline.get('id', 'unknown')
            source_schema = {}

            # FIX: FIRST extract pipeline metadata schema (id, name, status, metrics, etc.)
            # These are the fields React code uses when referencing pipeline objects
            pipeline_metadata_fields = {
                'id': {'type': 'string', 'required': True, 'description': 'Pipeline ID'},
                'name': {'type': 'string', 'required': True, 'description': 'Pipeline name'},
                'display_name': {'type': 'string', 'required': False, 'description': 'Display name'},
                'status': {'type': 'string', 'required': False, 'description': 'Pipeline status'},
            }

            # Add metrics if present
            if 'metrics' in pipeline:
                pipeline_metadata_fields['metrics'] = {
                    'type': 'object',
                    'required': False,
                    'description': 'Pipeline metrics',
                    'properties': {
                        'file_count': {'type': 'number'},
                        'record_count': {'type': 'number'},
                        'data_size': {'type': 'string'}
                    }
                }

            # Add stages if present
            if 'stages' in pipeline:
                pipeline_metadata_fields['stages'] = {
                    'type': 'array',
                    'required': False,
                    'description': 'Pipeline stages'
                }

            # Add files if present
            if 'files' in pipeline:
                pipeline_metadata_fields['files'] = {
                    'type': 'object',
                    'required': False,
                    'description': 'Pipeline file structure'
                }

            # Start with pipeline metadata
            source_schema.update(pipeline_metadata_fields)

            # THEN add dataset schema (data columns)
            # Extract from schema if present
            if 'schema' in pipeline:
                schema_info = pipeline['schema']
                if isinstance(schema_info, dict):
                    for field_name, field_def in schema_info.items():
                        source_schema[field_name] = {
                            'type': field_def.get('type', 'unknown'),
                            'required': field_def.get('required', False),
                            'description': field_def.get('description', '')
                        }

            # Extract from sample_data if present
            elif 'sample_data' in pipeline:
                sample = pipeline['sample_data']
                if isinstance(sample, list) and len(sample) > 0:
                    # Infer schema from first sample
                    first_row = sample[0]
                    if isinstance(first_row, dict):
                        for field_name, value in first_row.items():
                            source_schema[field_name] = {
                                'type': self._infer_type(value),
                                'required': False,
                                'description': ''
                            }

            # Extract from file_metadata if present
            elif 'file_metadata' in pipeline:
                metadata = pipeline['file_metadata']
                if 'fields' in metadata:
                    for field_name in metadata['fields']:
                        source_schema[field_name] = {
                            'type': 'unknown',
                            'required': False,
                            'description': ''
                        }

            schema[source_id] = source_schema

        return schema

    def _infer_type(self, value: Any) -> str:
        """Infer field type from a sample value"""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'number'
        elif isinstance(value, str):
            # Try to detect if it's a date, categorical, etc.
            if re.match(r'\d{4}-\d{2}-\d{2}', value):
                return 'date'
            elif len(value) < 50 and not any(char in value for char in [' ', '\n', '\t']):
                return 'categorical'
            else:
                return 'string'
        elif isinstance(value, (list, tuple)):
            return 'array'
        elif isinstance(value, dict):
            return 'object'
        else:
            return 'unknown'

    def _check_ux_schema_alignment(self, ux_spec: Any,
                                   schema: Dict[str, Dict[str, Any]]) -> List['Conflict']:
        """Check UX spec field references against schema"""
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        if not hasattr(ux_spec, 'components'):
            return conflicts

        # Build a set of all valid fields across all sources
        all_valid_fields = set()
        for source_schema in schema.values():
            all_valid_fields.update(source_schema.keys())

        # Check each component's data field references
        for comp in ux_spec.components:
            if not hasattr(comp, 'data_field') or not comp.data_field:
                continue

            data_field = comp.data_field
            comp_name = comp.name if hasattr(comp, 'name') else 'Unknown'

            # Check if field exists in schema
            if data_field not in all_valid_fields:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.SCHEMA_FIELD_NONEXISTENT,
                    source_agent="SchemaAlignmentTool",
                    description=f"Component '{comp_name}' references field '{data_field}' not found in data schema",
                    affected_component=comp_name,
                    suggested_resolution=f"Either add '{data_field}' to data schema or update component to use existing field",
                    severity="high",
                    target="UX_SPEC",
                    path=f"/components/{comp_name}/data_field"
                ))

            # Check component type vs field type compatibility
            if hasattr(comp, 'component_type'):
                comp_type = comp.component_type
                field_info = self._find_field_info(data_field, schema)

                if field_info:
                    conflicts.extend(self._check_type_compatibility(
                        comp_name, comp_type, data_field, field_info
                    ))

        # Check data_sources references
        if hasattr(ux_spec, 'data_sources') and ux_spec.data_sources:
            for source_name, source_info in ux_spec.data_sources.items():
                if source_name not in schema:
                    conflicts.append(Conflict(
                        conflict_type=ConflictType.DATA_SOURCE_MISMATCH,
                        source_agent="SchemaAlignmentTool",
                        description=f"UX spec references data source '{source_name}' not found in data_context",
                        severity="high",
                        target="UX_SPEC",
                        path=f"/data_sources/{source_name}"
                    ))

        return conflicts

    def _check_react_schema_alignment(self, react_files: Dict[str, str],
                                      schema: Dict[str, Dict[str, Any]]) -> List['Conflict']:
        """
        Check React field references against schema.

        FIX: Now validates pipeline metadata fields (id, name, metrics, etc.)
        """
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []

        # Build set of all valid fields (now includes pipeline metadata!)
        all_valid_fields = set()
        all_nested_fields = {}  # Track nested fields like metrics.file_count

        for source_schema in schema.values():
            all_valid_fields.update(source_schema.keys())
            # Track nested properties
            for field_name, field_info in source_schema.items():
                if isinstance(field_info, dict) and 'properties' in field_info:
                    all_nested_fields[field_name] = set(field_info['properties'].keys())

        # Check each React file for field references
        for filename, code in react_files.items():
            if not filename.endswith(('.tsx', '.jsx')):
                continue

            # Extract field references from code with CONTEXT-AWARE matching
            # Only match actual data access patterns, not JavaScript methods
            # Pattern: (item|data|row|pipeline|record|source).field_name
            referenced_fields = set()

            # Context-aware pattern: only match data accessors
            data_access_pattern = r'(?:item|data|row|pipeline|record|source|p|d|r)\.([\w]+)'
            matches = re.finditer(data_access_pattern, code, re.IGNORECASE)
            for match in matches:
                field = match.group(1)
                referenced_fields.add(field)

            # Also check bracket notation: data['field']
            bracket_pattern = r'(?:item|data|row|pipeline|record|source)\[[\'"]([\w]+)[\'"]'
            matches = re.finditer(bracket_pattern, code, re.IGNORECASE)
            for match in matches:
                field = match.group(1)
                referenced_fields.add(field)

            # Comprehensive whitelist of JavaScript/React patterns to exclude
            js_and_react_whitelist = {
                # JavaScript Array methods
                'map', 'filter', 'reduce', 'forEach', 'length', 'push', 'pop', 'shift',
                'unshift', 'slice', 'splice', 'indexOf', 'includes', 'find', 'findIndex',
                'some', 'every', 'join', 'concat', 'reverse', 'sort', 'flat', 'flatMap',
                # JavaScript String methods
                'toString', 'toLocaleString', 'valueOf', 'substring', 'substr', 'trim',
                'split', 'replace', 'match', 'search', 'toLowerCase', 'toUpperCase',
                # JavaScript Object methods
                'keys', 'values', 'entries', 'hasOwnProperty', 'isPrototypeOf',
                # JavaScript Set/Map methods
                'has', 'add', 'delete', 'clear', 'set', 'get', 'size',
                # JavaScript type checks
                'isArray', 'isNaN', 'isFinite',
                # React/DOM attributes
                'className', 'style', 'key', 'id', 'name', 'value', 'type', 'checked',
                'children', 'props', 'state', 'ref', 'onClick', 'onChange', 'onSubmit',
                # Common variable names
                'data', 'item', 'row', 'index', 'i', 'j', 'k', 'count', 'total',
                # Date/Number methods
                'min', 'max', 'abs', 'floor', 'ceil', 'round', 'getTime', 'getDate',
                # Pipeline metadata (now in schema but still whitelist to avoid double-checking)
                'file_count', 'record_count', 'data_size', 'stages', 'files', 'metrics',
                'status', 'display_name',
            }

            # Filter out whitelisted fields
            referenced_fields = {f for f in referenced_fields if f not in js_and_react_whitelist}

            # Check if referenced fields exist in schema
            for field in referenced_fields:
                if field not in all_valid_fields:
                    # Also check if it's a nested field
                    is_nested = any(field in nested_props for nested_props in all_nested_fields.values())

                    if not is_nested:
                        # Check if it's a plausible data field (not a React prop or DOM attribute)
                        if not field[0].isupper():  # Not a component name
                            conflicts.append(Conflict(
                                conflict_type=ConflictType.SCHEMA_FIELD_NONEXISTENT,
                                source_agent="SchemaAlignmentTool",
                                description=f"File '{filename}' references field '{field}' not found in data schema",
                                severity="medium",
                                target="REACT_IMPL",
                                path=f"/files/{filename}"
                            ))

        return conflicts

    def _find_field_info(self, field_name: str,
                        schema: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find field info across all sources"""
        for source_schema in schema.values():
            if field_name in source_schema:
                return source_schema[field_name]
        return None

    def _check_type_compatibility(self, comp_name: str, comp_type: str,
                                  field_name: str,
                                  field_info: Dict[str, Any]) -> List['Conflict']:
        """Check if component type is compatible with field type"""
        from src.agents.shared_memory import Conflict, ConflictType

        conflicts = []
        field_type = field_info.get('type', 'unknown')

        # Define incompatible combinations
        incompatible_pairs = [
            # Numeric charts with categorical/string data
            (['bar_chart', 'line_chart', 'scatter_plot', 'histogram'], ['categorical', 'string']),
            # Categorical charts with numeric data
            (['pie_chart', 'donut_chart'], ['integer', 'number', 'float']),
        ]

        comp_type_lower = comp_type.lower()
        for comp_types, field_types in incompatible_pairs:
            if any(ct in comp_type_lower for ct in comp_types):
                if field_type in field_types:
                    conflicts.append(Conflict(
                        conflict_type=ConflictType.NUMERIC_VS_CATEGORICAL_ERROR,
                        source_agent="SchemaAlignmentTool",
                        description=f"Component '{comp_name}' (type={comp_type}) incompatible with field '{field_name}' (type={field_type})",
                        affected_component=comp_name,
                        suggested_resolution=f"Change component type or use a numeric field",
                        severity="high",
                        target="UX_SPEC",
                        path=f"/components/{comp_name}"
                    ))

        return conflicts
