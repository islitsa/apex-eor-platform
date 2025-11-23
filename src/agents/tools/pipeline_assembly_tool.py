"""
PipelineAssemblyTool - MANDATORY PIPELINE ASSEMBLY

This is the CRITICAL tool that must run BEFORE React Developer.

Responsibility:
1. Create pipelines[] from data_sources
2. Detect stages from raw filesystem
3. Score stage health (complete/empty/missing/unknown)
4. Compute metrics (file_count, record_count, data_size)
5. Ensure every pipeline has stages[] and files[]

This tool prevents "0 stages" bugs and hallucinated fields.

STRICT SCHEMA ENFORCEMENT (as per Sonnet Master Instructions):

Pipeline Schema:
{
  id: string,
  name: string,
  display_name: string,
  status: string,
  metrics: {
    file_count: number,
    record_count: number,
    data_size: number
  },
  stages: Stage[],
  files: Array<{ name: string, size_bytes: number }>
}

Stage Schema:
{
  name: string,
  file_count: number,
  total_size_bytes: number,
  status: "complete" | "empty" | "missing" | "unknown"
}

FORBIDDEN FIELDS:
- metrics.total_records (use record_count)
- pipeline.children
- pipeline.subdirectories
- pipeline.records
- pipeline.total_files
- pipeline.total_records
"""

from typing import Dict, List, Any, Optional
import os
from pathlib import Path


class PipelineAssemblyTool:
    """
    MANDATORY pipeline assembly tool that MUST run before UX/React generation.

    This tool bridges the gap between data_sources (from API) and pipelines (for UI).
    Without this tool, React Developer will receive incomplete data and generate broken UIs.
    """

    def __init__(self, data_root: str = "data/raw", trace_collector=None):
        """
        Initialize Pipeline Assembly Tool.

        Args:
            data_root: Root directory for data files (default: data/raw)
            trace_collector: Optional trace collector for debugging
        """
        self.data_root = Path(data_root)
        self.trace_collector = trace_collector

    def assemble_pipelines(self, data_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Assemble pipelines from data_context with stage detection.

        This is the MAIN ENTRY POINT that orchestrator must call.

        Args:
            data_context: Data context from DataDiscoveryTool containing EITHER:
                1. API format (already has pipelines):
                   {
                       'pipelines': [...],
                       'summary': {...}
                   }
                2. Legacy format (has data_sources):
                   {
                       'data_sources': {...},
                       'summary': {...}
                   }

        Returns:
            List of Pipeline objects with detected stages and computed metrics
        """
        print("\n[PipelineAssemblyTool] Assembling pipelines with stage detection...")

        # CASE 1: API already returned pipelines - enhance/validate them
        if 'pipelines' in data_context and data_context['pipelines']:
            print("  [Mode] Enhancing existing pipelines from API")
            existing_pipelines = data_context['pipelines']
            return self._enhance_existing_pipelines(existing_pipelines)

        # CASE 2: Legacy format with data_sources - build from scratch
        data_sources = data_context.get('data_sources', {})
        if not data_sources:
            print("  [WARN] No pipelines or data_sources in data_context")
            return []

        print("  [Mode] Building pipelines from data_sources")
        pipelines = []

        for source_name, source_data in data_sources.items():
            print(f"\n  [Pipeline] Processing: {source_name}")

            # Create pipeline object with STRICT schema
            pipeline = self._create_pipeline_from_source(source_name, source_data)

            # Detect stages from filesystem
            stages = self._detect_stages_from_filesystem(source_name, source_data)
            pipeline['stages'] = stages

            # Compute metrics from stages (if not already present)
            self._compute_pipeline_metrics(pipeline, stages, source_data)

            # Extract files list (if not already present)
            if not pipeline.get('files'):
                pipeline['files'] = self._extract_files_list(source_data)

            # Validate pipeline schema
            self._validate_pipeline_schema(pipeline)

            pipelines.append(pipeline)

            print(f"    [OK] Created pipeline with {len(stages)} stages")
            for stage in stages:
                print(f"      - {stage['name']}: {stage['status']} ({stage['file_count']} files)")

        print(f"\n[PipelineAssemblyTool] Assembly complete: {len(pipelines)} pipelines created")

        # Emit trace
        if self.trace_collector:
            self.trace_collector.trace_thinking(
                agent="PipelineAssemblyTool",
                method="assemble_pipelines",
                thought=f"Assembled {len(pipelines)} pipelines with stage detection"
            )

        return pipelines

    def _enhance_existing_pipelines(self, existing_pipelines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance and validate pipelines that already exist from API.

        This method:
        1. Validates schema compliance
        2. Ensures canonical fields exist
        3. Adds missing stages[] if needed
        4. Adds missing files[] if needed
        5. Detects stages from filesystem if not present

        Args:
            existing_pipelines: Pipelines from API

        Returns:
            Enhanced and validated pipelines
        """
        enhanced = []

        for pipeline in existing_pipelines:
            pipeline_id = pipeline.get('id', 'unknown')
            print(f"\n  [Pipeline] Enhancing: {pipeline_id}")

            # Ensure metrics use canonical fields
            if 'metrics' in pipeline:
                metrics = pipeline['metrics']

                # Fix: total_records → record_count
                if 'total_records' in metrics and 'record_count' not in metrics:
                    metrics['record_count'] = metrics.pop('total_records')
                    print(f"    [FIX] Renamed total_records → record_count")

                # Ensure record_count exists
                if 'record_count' not in metrics:
                    metrics['record_count'] = 0

                # Ensure file_count exists
                if 'file_count' not in metrics:
                    metrics['file_count'] = 0

                # Ensure data_size exists
                if 'data_size' not in metrics:
                    metrics['data_size'] = 0

            # Ensure stages exist
            if 'stages' not in pipeline or not pipeline['stages']:
                print(f"    [Detect] No stages found, detecting from filesystem...")
                stages = self._detect_stages_from_filesystem(
                    pipeline_id,
                    {'location': f'data/raw/{pipeline_id}'}
                )
                pipeline['stages'] = stages
                print(f"    [OK] Detected {len(stages)} stages")
            else:
                stages = pipeline['stages']
                print(f"    [OK] Found {len(stages)} existing stages")

            # Ensure files exist
            if 'files' not in pipeline:
                pipeline['files'] = []

            # Validate schema
            try:
                self._validate_pipeline_schema(pipeline)
                print(f"    [OK] Schema validation passed")
            except Exception as e:
                print(f"    [ERROR] Schema validation failed: {e}")
                # Continue anyway but log the error

            enhanced.append(pipeline)

        print(f"\n[PipelineAssemblyTool] Enhanced {len(enhanced)} pipelines")
        return enhanced

    def _create_pipeline_from_source(
        self,
        source_name: str,
        source_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create pipeline object from source data with STRICT schema.

        ONLY uses canonical fields - no hallucination allowed.
        """
        return {
            'id': source_name,
            'name': source_name,
            'display_name': source_data.get('name', source_name),
            'status': 'active',  # Default status
            'metrics': {
                'file_count': source_data.get('file_count', 0),
                'record_count': source_data.get('row_count', 0),  # CANONICAL FIELD
                'data_size': source_data.get('total_size_bytes', 0)
            },
            'stages': [],  # Will be populated by stage detection
            'files': []    # Will be populated by file extraction
        }

    def _detect_stages_from_filesystem(
        self,
        source_name: str,
        source_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Detect pipeline stages from filesystem.

        DETECTION RULES (as per specification):

        For a dataset located at:
            data/raw/<source_name>/<dataset_name>/

        Every DIRECTORY under <dataset_name> is a pipeline stage.

        Example:
            Chemical_data/
                downloads/      <- stage
                extracted/      <- stage
                parsed/         <- stage
                metadata.json   <- ignored

        STAGE SCORING RULES:
            if folder does not exist → status="missing"
            if folder exists but has 0 files → status="empty"
            if folder exists and has >=1 files → status="complete"
            if exception → status="unknown"

        Returns:
            List of Stage objects with health scores
        """
        stages = []

        # Build path: data/raw/<source_name>/
        # NOTE: Discovery may return location pointing to interim/processed
        # We need to scan raw directory for stage detection
        source_path = self.data_root / source_name

        print(f"    [Stages] Scanning filesystem: {source_path}")

        # Check if source directory exists
        if not source_path.exists():
            print(f"    [WARN] Source directory does not exist: {source_path}")
            return stages

        # Scan for subdirectories (each is a stage)
        try:
            subdirs = [item for item in source_path.iterdir() if item.is_dir()]

            # Special case: If there's only ONE subdirectory and it looks like a dataset container
            # (e.g., Chemical_data), scan INSIDE it for actual pipeline stages
            if len(subdirs) == 1 and not any(stage in subdirs[0].name.lower()
                                             for stage in ['downloads', 'extracted', 'parsed',
                                                          'raw', 'interim', 'processed']):
                # This subdirectory is likely a dataset container, scan inside it
                container = subdirs[0]
                print(f"    [Detect] Found dataset container: {container.name}")
                scan_path = container
            else:
                scan_path = source_path

            # Scan for stage directories
            for item in scan_path.iterdir():
                if item.is_dir():
                    stage_name = item.name
                    # Skip hidden directories and non-stage folders
                    if not stage_name.startswith('.') and not stage_name.startswith('_'):
                        stage = self._score_stage_health(stage_name, item)
                        stages.append(stage)

        except Exception as e:
            print(f"    [ERROR] Failed to scan directory: {e}")
            return stages

        # If still no stages found, check common stage names at source_path
        if not stages:
            common_stages = ['downloads', 'extracted', 'parsed', 'raw', 'interim', 'processed']
            for stage_name in common_stages:
                stage_path = source_path / stage_name
                if stage_path.exists():
                    stage = self._score_stage_health(stage_name, stage_path)
                    stages.append(stage)

        return stages

    def _score_stage_health(self, stage_name: str, stage_path: Path) -> Dict[str, Any]:
        """
        Score stage health based on filesystem state.

        SCORING RULES:
            if folder does not exist → status="missing"
            if folder exists but has 0 files → status="empty"
            if folder exists and has >=1 files → status="complete"
            if exception → status="unknown"

        Returns:
            Stage object with health score
        """
        try:
            if not stage_path.exists():
                return {
                    'name': stage_name,
                    'file_count': 0,
                    'total_size_bytes': 0,
                    'status': 'missing'
                }

            # Count files in this stage
            files = list(stage_path.glob('*'))
            file_count = sum(1 for f in files if f.is_file())

            # Compute total size
            total_size = sum(f.stat().st_size for f in files if f.is_file())

            # Determine status
            if file_count == 0:
                status = 'empty'
            else:
                status = 'complete'

            return {
                'name': stage_name,
                'file_count': file_count,
                'total_size_bytes': total_size,
                'status': status
            }

        except Exception as e:
            print(f"      [ERROR] Failed to score stage {stage_name}: {e}")
            return {
                'name': stage_name,
                'file_count': 0,
                'total_size_bytes': 0,
                'status': 'unknown'
            }

    def _compute_pipeline_metrics(
        self,
        pipeline: Dict[str, Any],
        stages: List[Dict[str, Any]],
        source_data: Dict[str, Any]
    ):
        """
        Compute pipeline metrics from stages.

        If metrics are already in source_data, use those.
        Otherwise, compute from stages.

        CANONICAL FIELDS ONLY:
        - file_count (NOT total_files)
        - record_count (NOT total_records)
        - data_size (NOT size)
        """
        metrics = pipeline['metrics']

        # If source_data already has metrics, use those
        if 'file_count' in source_data and metrics['file_count'] == 0:
            metrics['file_count'] = source_data['file_count']

        if 'row_count' in source_data and metrics['record_count'] == 0:
            metrics['record_count'] = source_data['row_count']

        if 'total_size_bytes' in source_data and metrics['data_size'] == 0:
            metrics['data_size'] = source_data['total_size_bytes']

        # If still zero, compute from stages
        if metrics['file_count'] == 0 and stages:
            metrics['file_count'] = sum(s['file_count'] for s in stages)

        if metrics['data_size'] == 0 and stages:
            metrics['data_size'] = sum(s['total_size_bytes'] for s in stages)

    def _extract_files_list(self, source_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract files list from source_data.

        Returns list in format:
        [
            { name: string, size_bytes: number },
            ...
        ]
        """
        file_list = source_data.get('file_list', [])

        # Normalize to canonical format
        normalized = []
        for file_info in file_list:
            if isinstance(file_info, dict):
                normalized.append({
                    'name': file_info.get('name', 'unknown'),
                    'size_bytes': file_info.get('size_bytes', 0)
                })
            elif isinstance(file_info, str):
                normalized.append({
                    'name': file_info,
                    'size_bytes': 0
                })

        return normalized

    def _validate_pipeline_schema(self, pipeline: Dict[str, Any]):
        """
        Validate pipeline schema to ensure no forbidden fields.

        REQUIRED FIELDS:
        - id, name, display_name, status
        - metrics.file_count, metrics.record_count, metrics.data_size
        - stages, files

        FORBIDDEN FIELDS:
        - metrics.total_records (use record_count)
        - pipeline.children
        - pipeline.subdirectories
        - pipeline.records
        - pipeline.total_files
        - pipeline.total_records
        """
        required_fields = ['id', 'name', 'display_name', 'status', 'metrics', 'stages', 'files']
        for field in required_fields:
            if field not in pipeline:
                raise ValueError(f"Pipeline missing required field: {field}")

        required_metrics = ['file_count', 'record_count', 'data_size']
        for metric in required_metrics:
            if metric not in pipeline['metrics']:
                raise ValueError(f"Pipeline metrics missing required field: {metric}")

        # Check for forbidden fields
        forbidden_fields = ['children', 'subdirectories', 'records', 'total_files', 'total_records']
        for field in forbidden_fields:
            if field in pipeline:
                raise ValueError(f"Pipeline contains FORBIDDEN field: {field}")

        forbidden_metrics = ['total_records', 'records']
        for metric in forbidden_metrics:
            if metric in pipeline['metrics']:
                raise ValueError(f"Pipeline metrics contains FORBIDDEN field: {metric}")

        # Validate stages
        if not isinstance(pipeline['stages'], list):
            raise ValueError("Pipeline stages must be a list")

        for stage in pipeline['stages']:
            required_stage_fields = ['name', 'file_count', 'total_size_bytes', 'status']
            for field in required_stage_fields:
                if field not in stage:
                    raise ValueError(f"Stage missing required field: {field}")

            if stage['status'] not in ['complete', 'empty', 'missing', 'unknown']:
                raise ValueError(f"Invalid stage status: {stage['status']}")

        # Validate files
        if not isinstance(pipeline['files'], list):
            raise ValueError("Pipeline files must be a list")

    def update_data_context_with_pipelines(
        self,
        data_context: Dict[str, Any],
        pipelines: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update data_context with assembled pipelines.

        This MUST be called by orchestrator before UX/React generation.

        Args:
            data_context: Original data context from DataDiscoveryTool
            pipelines: Assembled pipelines from assemble_pipelines()

        Returns:
            Updated data_context with 'pipelines' field
        """
        data_context['pipelines'] = pipelines

        print(f"\n[PipelineAssemblyTool] Updated data_context with {len(pipelines)} pipelines")

        # Emit trace
        if self.trace_collector:
            self.trace_collector.trace_thinking(
                agent="PipelineAssemblyTool",
                method="update_data_context_with_pipelines",
                thought=f"Updated data_context with {len(pipelines)} pipelines (ready for React Developer)"
            )

        return data_context
