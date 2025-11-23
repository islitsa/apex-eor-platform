"""
Discovery Tools - Clean interface for agents to explore repository context

This module provides agent-friendly methods for discovering:
- Data sources (what datasets exist)
- Schemas (what columns/types are available)
- Directory structure (what files are present)
- Processing status (what data is ready to use)

Agents use these tools for "context swimming" - autonomous discovery
rather than receiving pre-assembled context in prompts.

Usage:
    tools = DiscoveryTools()

    # Find relevant data sources
    sources = tools.find_data_sources("chemical data for EOR analysis")

    # Get schema for a source
    schema = tools.get_schema("fracfocus")

    # Check processing status
    status = tools.check_status("rrc")
"""

from typing import List, Dict, Optional, Any
from pathlib import Path
import sys

# Add src to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.knowledge.repository_index import RepositoryIndex


class DiscoveryTools:
    """
    Agent-friendly interface for repository discovery.

    This wrapper provides clean, simple methods that agents can call
    to discover context without needing to understand the underlying
    Pinecone/indexing implementation.
    """

    def __init__(self):
        """Initialize discovery tools with repository indexer."""
        self.indexer = RepositoryIndex()
        print("[Discovery Tools] Initialized")

    def find_data_sources(
        self,
        query: str,
        top_k: int = 10,
        min_relevance: float = 0.5,
        source_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find data sources relevant to a query.

        Uses semantic search to find datasets that match the intent.

        Args:
            query: Natural language query (e.g., "chemical data for EOR")
            top_k: Maximum number of results to return
            min_relevance: Minimum relevance score (0-1) to include
            source_filter: Optional source name filter (e.g., "fracfocus")
                          If provided, only returns sources matching this name

        Returns:
            List of data source dicts with:
            - id: Unique identifier
            - name: Source name (e.g., "fracfocus")
            - relevance: Relevance score (0-1)
            - description: Brief description

        Example:
            tools = DiscoveryTools()
            sources = tools.find_data_sources("production data")

            for source in sources:
                print(f"{source['name']}: {source['relevance']:.2f}")
        """
        print(f"[Discovery] Finding data sources for: '{query}'")
        if source_filter:
            print(f"[Discovery] 🎯 Applying source filter: '{source_filter}'")

        results = self.indexer.query_data_sources(query, top_k=top_k)

        # Filter by relevance and format for agents
        filtered = []
        for result in results:
            relevance = result.get('score', 0)

            if relevance >= min_relevance:
                # Extract name from metadata or title
                if 'metadata' in result:
                    name = result['metadata'].get('name', 'Unknown')
                else:
                    # Parse from title "Data Source: fracfocus"
                    title = result.get('title', '')
                    name = title.replace('Data Source:', '').strip() if 'Data Source:' in title else 'Unknown'

                # Apply source filter BEFORE adding to results
                if source_filter:
                    # Check if source name contains the filter (case-insensitive)
                    if source_filter.lower() not in name.lower():
                        continue  # Skip this source

                filtered.append({
                    'id': result.get('id', name),
                    'name': name,
                    'relevance': relevance,
                    'description': result.get('content', '')[:200]  # Truncate description
                })

        print(f"[Discovery] Found {len(filtered)} relevant sources (threshold: {min_relevance})")
        return filtered

    def get_schema(
        self,
        source_name: str,
        file_path: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get schema (columns, types, sample data) for a data source.

        Reads the actual parsed file to extract schema information.
        Useful for agents to verify what columns are available before
        generating code.

        Args:
            source_name: Name of data source (e.g., "fracfocus", "rrc")
            file_path: Optional specific file path (if None, finds first parsed file)

        Returns:
            Schema dict with:
            - source: Source name
            - file: Path to file
            - columns: List of column names
            - dtypes: Dict mapping column -> data type
            - row_count: Number of rows
            - sample: Sample data (first 5 rows)

        Example:
            tools = DiscoveryTools()
            schema = tools.get_schema("fracfocus")

            print(f"Columns: {schema['columns']}")
            print(f"Types: {schema['dtypes']}")
        """
        print(f"[Discovery] Getting schema for: '{source_name}'")

        schema = self.indexer.get_schema(source_name, file_path=file_path)

        if schema:
            print(f"[Discovery] Schema found: {len(schema['columns'])} columns, {schema['row_count']:,} rows")
        else:
            print(f"[Discovery] No schema found for: '{source_name}'")

        return schema

    def check_status(self, source_name: str) -> Optional[Dict[str, Any]]:
        """
        Check processing status of a data source.

        Determines which pipeline stages are complete:
        - downloads: Raw files downloaded
        - extracted: Archives extracted
        - parsed: Data parsed and ready to use

        Args:
            source_name: Name of data source (e.g., "fracfocus")

        Returns:
            Status dict with:
            - source: Source name
            - status: Overall status ("complete", "in_progress", "not_started")
            - has_downloads: Bool
            - has_extracted: Bool
            - has_parsed: Bool
            - stages: List of present stages
            - files_by_stage: Dict mapping stage -> file count

        Example:
            tools = DiscoveryTools()
            status = tools.check_status("rrc")

            if status['has_parsed']:
                print("Data is ready to use!")
        """
        print(f"[Discovery] Checking status for: '{source_name}'")

        status = self.indexer.get_processing_status(source_name)

        if status:
            print(f"[Discovery] Status: {status['status']} - stages: {', '.join(status['stages'])}")
        else:
            print(f"[Discovery] Source not found: '{source_name}'")

        return status

    def explore_directory(self, source_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete directory structure for a data source.

        Returns hierarchical file tree with sizes, types, and metadata.
        Useful for understanding what files are available.

        Args:
            source_name: Name of data source

        Returns:
            Directory structure dict with:
            - name: Directory name
            - path: Full path
            - type: 'directory' or 'file'
            - children: List of child nodes (for directories)
            - file_count: Total number of files
            - total_size_mb: Total size in MB
            - extension: File extension (for files)
            - size_mb: Size in MB (for files)

        Example:
            tools = DiscoveryTools()
            structure = tools.explore_directory("fracfocus")

            print(f"Total files: {structure['file_count']}")
            print(f"Total size: {structure['total_size_mb']:.1f} MB")
        """
        print(f"[Discovery] Exploring directory: '{source_name}'")

        structure = self.indexer.get_directory_structure(source_name)

        if structure:
            print(f"[Discovery] Found {structure.get('file_count', 0)} files, {structure.get('total_size_mb', 0):.1f} MB")
        else:
            print(f"[Discovery] Directory not found: '{source_name}'")

        return structure

    def discover_all(
        self,
        query: str,
        top_k: int = 5,
        get_schemas: bool = True
    ) -> Dict[str, Any]:
        """
        One-shot discovery: Find sources, get schemas, check status.

        Convenience method that performs complete discovery in one call.
        Useful for agents that need full context quickly.

        Args:
            query: Natural language query
            top_k: Number of data sources to explore
            get_schemas: Whether to fetch schemas for each source

        Returns:
            Discovery results dict with:
            - query: Original query
            - sources: List of data sources with relevance scores
            - schemas: Dict mapping source_name -> schema (if get_schemas=True)
            - statuses: Dict mapping source_name -> status

        Example:
            tools = DiscoveryTools()
            results = tools.discover_all("oil production data")

            for source in results['sources']:
                name = source['name']
                schema = results['schemas'].get(name)
                status = results['statuses'].get(name)

                print(f"{name}: {schema['row_count']:,} rows, status: {status['status']}")
        """
        print(f"\n{'='*60}")
        print(f"[Discovery] Starting full discovery for: '{query}'")
        print(f"{'='*60}")

        # Find relevant sources
        sources = self.find_data_sources(query, top_k=top_k, min_relevance=0.5)

        # Get schemas and statuses
        schemas = {}
        statuses = {}

        for source in sources:
            name = source['name']

            # Get schema
            if get_schemas:
                schema = self.get_schema(name)
                if schema:
                    schemas[name] = schema

            # Get status
            status = self.check_status(name)
            if status:
                statuses[name] = status

        print(f"\n[Discovery] Complete: {len(sources)} sources, {len(schemas)} schemas, {len(statuses)} statuses")
        print(f"{'='*60}\n")

        return {
            'query': query,
            'sources': sources,
            'schemas': schemas,
            'statuses': statuses
        }


# Convenience function for quick testing
def test_discovery_tools():
    """Quick test of discovery tools"""
    tools = DiscoveryTools()

    print("\n" + "="*80)
    print("TESTING DISCOVERY TOOLS")
    print("="*80 + "\n")

    # Test 1: Find data sources
    print("[TEST 1] Find chemical data sources")
    sources = tools.find_data_sources("chemical data", top_k=3)
    for source in sources:
        print(f"  - {source['name']} (relevance: {source['relevance']:.2f})")

    # Test 2: Get schema
    if sources:
        test_source = sources[0]['name']
        print(f"\n[TEST 2] Get schema for '{test_source}'")
        schema = tools.get_schema(test_source)
        if schema:
            print(f"  Columns: {len(schema['columns'])}")
            print(f"  First 5: {schema['columns'][:5]}")

    # Test 3: Check status
    if sources:
        print(f"\n[TEST 3] Check status for '{test_source}'")
        status = tools.check_status(test_source)
        if status:
            print(f"  Status: {status['status']}")
            print(f"  Stages: {', '.join(status['stages'])}")

    # Test 4: Full discovery
    print(f"\n[TEST 4] Full discovery")
    results = tools.discover_all("production data", top_k=2, get_schemas=False)
    print(f"  Found {len(results['sources'])} sources")
    print(f"  Statuses: {len(results['statuses'])}")

    print("\n" + "="*80)
    print("TESTS COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_discovery_tools()
