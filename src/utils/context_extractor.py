"""
Pipeline Context Extractor
Uses AutoContextGenerator to automatically discover and extract context
NO HARDCODING - everything discovered dynamically (Opus recommendation)
"""

from typing import Dict, Any
from src.utils.auto_context_generator import AutoContextGenerator

class PipelineContextExtractor:
    """
    Extract UI context using automatic filesystem scanning
    Replaces hardcoded metadata paths with dynamic discovery
    """

    def __init__(self):
        self.auto_generator = AutoContextGenerator()

    def extract_from_metadata(self, metadata_path: str = None) -> Dict[str, Any]:
        """
        Extract process context by AUTO-DISCOVERING all data sources
        NO HARDCODING - scans filesystem and metadata files automatically

        Args:
            metadata_path: Deprecated, kept for backwards compatibility

        Returns:
            Process context dictionary containing:
            - screen_type: Type of UI needed
            - data_type: Domain data type
            - metadata_files: List of ALL discovered metadata files
            - total_records: Total across all sources
            - total_size: Total size across all sources
            - active_sources: Count of active sources
            - data_sources: Detailed info about each source
            - operations: Pipeline operations
            - user_needs: What user wants to do
        """

        # Use automatic context generator (Opus pattern)
        print("[PipelineContextExtractor] Auto-generating context from filesystem...")
        context = self.auto_generator.generate_context_from_filesystem()

        # Add additional fields for backwards compatibility
        context["data_type"] = "multi_sor_petroleum_data"
        context["operations"] = ["download", "extract", "parse"]
        context["user_needs"] = "monitor_multi_sor_pipeline_status"

        # Extract sources in old format for backwards compatibility
        sources = {}
        for source_name, source_data in context.get("data_sources", {}).items():
            for dataset_name, dataset in source_data.get("datasets", {}).items():
                if "parsed" in dataset.get("pipeline_stages", {}):
                    parsed = dataset["pipeline_stages"]["parsed"]
                    key = f"{source_name}_{dataset_name}".replace(" ", "_").lower()

                    sources[key] = {
                        'records': parsed.get('total_rows', 0),
                        'size_bytes': parsed.get('total_size_bytes', 0),
                        'status': dataset.get('status', 'unknown').title(),
                        'last_updated': parsed.get('last_updated', 'Unknown')
                    }

        context["sources"] = sources
        context["total_records"] = context["metrics"]["total_records"]
        context["total_size"] = context["metrics"]["total_size_bytes"]
        context["active_sources"] = context["metrics"]["active_sources"]

        print(f"[PipelineContextExtractor] Discovered {context['active_sources']} sources, "
              f"{context['total_records']:,} records")

        return context
