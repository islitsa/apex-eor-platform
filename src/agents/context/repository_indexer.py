"""
Repository Indexer

Scans repository artifacts (data sources, primitives, patterns)
and indexes them into Pinecone for gradient-based discovery.
"""

import os
from pathlib import Path
import pandas as pd
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from gradient_context import GradientContextEngine


class RepositoryIndexer:
    """
    Index repository artifacts into Pinecone.
    
    Creates the semantic field that agents swim through.
    Indexes:
    - Data sources (/data directory)
    - Component primitives (your primitive library)
    - Design patterns (UI/UX patterns)
    """
    
    def __init__(self, gradient_engine: GradientContextEngine, namespace: str = "repo-artifacts"):
        self.engine = gradient_engine
        self.namespace = namespace
        self.indexed_count = 0
        
    def index_data_directory(
        self,
        data_path: str,
        batch_size: int = 100
    ) -> int:
        """
        Index all data sources in /data directory.
        
        Scans directory structure, extracts metadata, creates
        searchable embeddings for each dataset.
        
        Args:
            data_path: Path to data directory
            batch_size: Number of vectors to upsert at once
        
        Returns:
            Number of datasets indexed
        """
        data_path = Path(data_path)
        
        if not data_path.exists():
            print(f"⚠️  Data directory not found: {data_path}")
            return 0
        
        print(f"\n{'='*60}")
        print(f"📚 INDEXING DATA DIRECTORY: {data_path}")
        print(f"{'='*60}\n")
        
        vectors_to_upsert = []
        count = 0
        
        for dataset_dir in data_path.iterdir():
            if not dataset_dir.is_dir():
                continue
            
            # Skip hidden directories
            if dataset_dir.name.startswith('.'):
                continue
            
            print(f"  📂 Indexing: {dataset_dir.name}")
            
            try:
                # Extract metadata
                metadata = self._extract_dataset_metadata(dataset_dir)
                
                # Create searchable content
                content = self._create_dataset_description(dataset_dir.name, metadata)
                
                # Generate embedding
                embedding = self.engine.embed(content)
                
                # Prepare vector for upsert
                vectors_to_upsert.append({
                    'id': f"data-{dataset_dir.name}",
                    'values': embedding.tolist(),
                    'metadata': {
                        'type': 'data-source',
                        'name': dataset_dir.name,
                        'path': str(dataset_dir),
                        'indexed_at': datetime.utcnow().isoformat(),
                        **metadata
                    }
                })
                
                count += 1
                
                # Batch upsert
                if len(vectors_to_upsert) >= batch_size:
                    self._upsert_batch(vectors_to_upsert)
                    vectors_to_upsert = []
                    
            except Exception as e:
                print(f"    ⚠️  Error indexing {dataset_dir.name}: {e}")
        
        # Upsert remaining vectors
        if vectors_to_upsert:
            self._upsert_batch(vectors_to_upsert)
        
        self.indexed_count += count
        print(f"\n✅ Indexed {count} datasets")
        print(f"{'='*60}\n")
        
        return count
    
    def _extract_dataset_metadata(self, dataset_dir: Path) -> Dict[str, Any]:
        """
        Extract metadata about a dataset.
        
        Checks:
        - Processing status (complete/incomplete)
        - File counts
        - Record counts
        - Directory structure
        - Schema info
        """
        metadata = {
            'status': 'not_processed',
            'file_count': 0,
            'record_count': 0,
            'size_bytes': 0,
            'subdirectories': [],
            'schema': []
        }
        
        # Check subdirectories
        subdirs = [d.name for d in dataset_dir.iterdir() if d.is_dir()]
        metadata['subdirectories'] = subdirs
        
        # Check for processed data in parsed/ directory
        parsed_dir = dataset_dir / 'parsed'
        if parsed_dir.exists():
            files = list(parsed_dir.glob('*.csv')) + list(parsed_dir.glob('*.parquet'))
            metadata['file_count'] = len(files)
            
            if files:
                metadata['status'] = 'complete'
                
                # Try to get record count and schema from first file
                try:
                    first_file = files[0]
                    
                    if first_file.suffix == '.csv':
                        # Read CSV
                        df_sample = pd.read_csv(first_file, nrows=0)  # Just schema
                        metadata['schema'] = list(df_sample.columns)
                        
                        # Get full count (this can be slow for large files)
                        try:
                            df_full = pd.read_csv(first_file)
                            metadata['record_count'] = len(df_full)
                        except:
                            # If too large, estimate from file size
                            metadata['record_count'] = -1  # Unknown
                            
                    elif first_file.suffix == '.parquet':
                        # Read Parquet
                        df = pd.read_parquet(first_file)
                        metadata['schema'] = list(df.columns)
                        metadata['record_count'] = len(df)
                        
                    # Get total size
                    metadata['size_bytes'] = sum(f.stat().st_size for f in files)
                    
                except Exception as e:
                    print(f"      ⚠️  Could not read file metadata: {e}")
        
        return metadata
    
    def _create_dataset_description(self, name: str, metadata: Dict) -> str:
        """
        Create searchable text description of dataset.
        
        This is what gets embedded and searched against.
        Make it rich with context that agents would search for.
        """
        status = metadata.get('status', 'unknown')
        file_count = metadata.get('file_count', 0)
        record_count = metadata.get('record_count', 0)
        subdirs = metadata.get('subdirectories', [])
        schema = metadata.get('schema', [])
        
        # Build rich description
        parts = [
            f"Dataset: {name}",
            f"Status: {status}",
        ]
        
        if file_count > 0:
            parts.append(f"Contains {file_count} files with {record_count:,} records")
        
        if subdirs:
            parts.append(f"Directory structure: {' / '.join(subdirs)}")
        
        if schema:
            # Include first 10 columns for searchability
            schema_preview = ', '.join(schema[:10])
            parts.append(f"Data columns: {schema_preview}")
            
            # Add common petroleum terms for better matching
            if any(term in schema_preview.lower() for term in ['api', 'well', 'production', 'chemical']):
                parts.append("Contains petroleum production and chemical data")
        
        description = '\n'.join(parts)
        return description
    
    def index_primitive_library(
        self,
        primitives_path: str,
        batch_size: int = 100
    ) -> int:
        """
        Index React primitive components.
        
        Args:
            primitives_path: Path to primitive library directory
            batch_size: Number of vectors to upsert at once
        
        Returns:
            Number of primitives indexed
        """
        primitives_path = Path(primitives_path)
        
        if not primitives_path.exists():
            print(f"⚠️  Primitives directory not found: {primitives_path}")
            return 0
        
        print(f"\n{'='*60}")
        print(f"📚 INDEXING PRIMITIVE LIBRARY: {primitives_path}")
        print(f"{'='*60}\n")
        
        vectors_to_upsert = []
        count = 0
        
        # Index JSON primitive definitions
        for primitive_file in primitives_path.glob('**/*.json'):
            print(f"  🧩 Indexing: {primitive_file.stem}")
            
            try:
                # Load primitive definition
                with primitive_file.open() as f:
                    primitive_def = json.load(f)
                
                # Create searchable description
                content = self._create_primitive_description(
                    primitive_file.stem,
                    primitive_def
                )
                
                # Generate embedding
                embedding = self.engine.embed(content)
                
                # Prepare vector
                vectors_to_upsert.append({
                    'id': f"primitive-{primitive_file.stem}",
                    'values': embedding.tolist(),
                    'metadata': {
                        'type': 'primitive',
                        'name': primitive_file.stem,
                        'path': str(primitive_file),
                        'indexed_at': datetime.utcnow().isoformat(),
                        'category': primitive_def.get('category', 'unknown'),
                        'description': primitive_def.get('description', '')
                    }
                })
                
                count += 1
                
                # Batch upsert
                if len(vectors_to_upsert) >= batch_size:
                    self._upsert_batch(vectors_to_upsert)
                    vectors_to_upsert = []
                    
            except Exception as e:
                print(f"    ⚠️  Error indexing {primitive_file.stem}: {e}")
        
        # Upsert remaining
        if vectors_to_upsert:
            self._upsert_batch(vectors_to_upsert)
        
        self.indexed_count += count
        print(f"\n✅ Indexed {count} primitives")
        print(f"{'='*60}\n")
        
        return count
    
    def _create_primitive_description(self, name: str, definition: Dict) -> str:
        """Create searchable description of primitive component"""
        parts = [
            f"Component: {name}",
            f"Category: {definition.get('category', 'unknown')}",
        ]
        
        if 'description' in definition:
            parts.append(f"Description: {definition['description']}")
        
        if 'props' in definition:
            props = ', '.join(definition['props'].keys())
            parts.append(f"Props: {props}")
        
        if 'use_cases' in definition:
            use_cases = ', '.join(definition['use_cases'])
            parts.append(f"Use cases: {use_cases}")
        
        return '\n'.join(parts)
    
    def index_design_patterns(
        self,
        patterns: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> int:
        """
        Index design patterns.
        
        Args:
            patterns: List of pattern dicts with 'id', 'name', 'description', etc.
            batch_size: Number of vectors to upsert at once
        
        Returns:
            Number of patterns indexed
        """
        print(f"\n{'='*60}")
        print(f"📚 INDEXING DESIGN PATTERNS")
        print(f"{'='*60}\n")
        
        vectors_to_upsert = []
        count = 0
        
        for pattern in patterns:
            pattern_id = pattern.get('id')
            if not pattern_id:
                continue
            
            print(f"  🎨 Indexing: {pattern.get('name', pattern_id)}")
            
            try:
                # Create searchable description
                content = self._create_pattern_description(pattern)
                
                # Generate embedding
                embedding = self.engine.embed(content)
                
                # Prepare vector
                vectors_to_upsert.append({
                    'id': f"pattern-{pattern_id}",
                    'values': embedding.tolist(),
                    'metadata': {
                        'type': 'pattern',
                        'name': pattern.get('name', pattern_id),
                        'indexed_at': datetime.utcnow().isoformat(),
                        'category': pattern.get('category', 'unknown'),
                        'description': pattern.get('description', '')
                    }
                })
                
                count += 1
                
                # Batch upsert
                if len(vectors_to_upsert) >= batch_size:
                    self._upsert_batch(vectors_to_upsert)
                    vectors_to_upsert = []
                    
            except Exception as e:
                print(f"    ⚠️  Error indexing pattern {pattern_id}: {e}")
        
        # Upsert remaining
        if vectors_to_upsert:
            self._upsert_batch(vectors_to_upsert)
        
        self.indexed_count += count
        print(f"\n✅ Indexed {count} patterns")
        print(f"{'='*60}\n")
        
        return count
    
    def _create_pattern_description(self, pattern: Dict) -> str:
        """Create searchable description of design pattern"""
        parts = [
            f"Pattern: {pattern.get('name', pattern.get('id'))}",
            f"Category: {pattern.get('category', 'unknown')}",
        ]
        
        if 'description' in pattern:
            parts.append(f"Description: {pattern['description']}")
        
        if 'use_cases' in pattern:
            parts.append(f"Use cases: {', '.join(pattern['use_cases'])}")
        
        if 'components' in pattern:
            parts.append(f"Components: {', '.join(pattern['components'])}")
        
        return '\n'.join(parts)
    
    def _upsert_batch(self, vectors: List[Dict]):
        """Upsert a batch of vectors to Pinecone"""
        try:
            self.engine.index.upsert(
                vectors=vectors,
                namespace=self.namespace
            )
            print(f"    ✅ Upserted {len(vectors)} vectors")
        except Exception as e:
            print(f"    ⚠️  Upsert failed: {e}")
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the index"""
        try:
            stats = self.engine.index.describe_index_stats()
            return {
                'total_vectors': stats.get('total_vector_count', 0),
                'dimension': stats.get('dimension', 0),
                'namespaces': stats.get('namespaces', {})
            }
        except Exception as e:
            print(f"⚠️  Could not get index stats: {e}")
            return {}


def create_sample_patterns() -> List[Dict]:
    """
    Create sample design patterns for indexing.
    
    Replace this with your actual design pattern definitions.
    """
    return [
        {
            'id': 'master-detail',
            'name': 'Master-Detail Layout',
            'category': 'layout',
            'description': 'Split view with list/table on left, detail panel on right',
            'use_cases': ['data exploration', 'file browsers', 'email clients'],
            'components': ['list', 'detail-panel', 'splitter']
        },
        {
            'id': 'dashboard-grid',
            'name': 'Dashboard Grid Layout',
            'category': 'layout',
            'description': 'Grid of cards/widgets for monitoring data',
            'use_cases': ['monitoring', 'analytics', 'dashboards'],
            'components': ['grid', 'card', 'chart', 'stat-widget']
        },
        {
            'id': 'data-table-filters',
            'name': 'Filterable Data Table',
            'category': 'data-display',
            'description': 'Table with column filters, sorting, pagination',
            'use_cases': ['data exploration', 'admin panels', 'reports'],
            'components': ['table', 'filter', 'pagination', 'sort-header']
        },
        {
            'id': 'file-explorer',
            'name': 'File Explorer Tree',
            'category': 'navigation',
            'description': 'Collapsible tree for browsing hierarchical data',
            'use_cases': ['file systems', 'folder navigation', 'taxonomies'],
            'components': ['tree', 'tree-item', 'collapse-icon']
        },
        {
            'id': 'pipeline-status',
            'name': 'Pipeline Status View',
            'category': 'monitoring',
            'description': 'Visual representation of pipeline stages and status',
            'use_cases': ['ETL monitoring', 'CI/CD pipelines', 'data flows'],
            'components': ['status-badge', 'progress-bar', 'timeline']
        }
    ]
