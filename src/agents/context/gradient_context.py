"""
Gradient Context System - Semantic field navigation for repository exploration

This module implements gradient-based navigation through repository context:
- Treats context as a CONTINUOUS semantic field (not discrete retrieval)
- Computes relevance gradients for navigation
- Enables agents to "follow the gradient" to high-relevance regions
- Integrates with existing Pinecone/vector systems

Architecture:
- Semantic embeddings for all repository artifacts
- Gradient computation: direction of increasing relevance
- Multi-dimensional relevance scoring
- Adaptive exploration based on gradient strength

This is the "water" that agents swim in - the continuous semantic field
that guides exploration from query → relevant artifacts.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class GradientScore:
    """
    Gradient score for an artifact relative to a query.
    
    Represents both the magnitude (relevance) and direction (semantic relationship)
    of the gradient at this point in semantic space.
    """
    artifact_id: str
    relevance: float  # 0-1 scale
    gradient_magnitude: float  # How "steep" the gradient is
    semantic_distance: float  # Distance in embedding space
    gradient_direction: Optional[np.ndarray] = None  # Vector pointing toward higher relevance
    
    def __repr__(self):
        return f"<Gradient: {self.artifact_id} relevance={self.relevance:.3f} magnitude={self.gradient_magnitude:.3f}>"


class GradientContextSystem:
    """
    Gradient Context System for semantic navigation.
    
    This system enables agents to navigate through repository context
    using gradient-guided exploration rather than discrete queries.
    
    Key Concepts:
    - Context as a continuous field (not discrete items)
    - Relevance gradients point toward more relevant regions
    - Agents "follow the gradient" to discover relevant artifacts
    - Multi-hop exploration builds semantic chains
    
    Integration Points:
    - Connects to Pinecone for embeddings
    - Integrates with DesignKnowledgeBasePinecone
    - Provides gradient-guided navigation layer
    """
    
    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        """
        Initialize gradient context system.
        
        Args:
            embedding_model: Model to use for embeddings (OpenAI, HuggingFace, etc.)
        """
        self.embedding_model = embedding_model
        
        # Cache for embeddings (avoid recomputing)
        self.embedding_cache: Dict[str, np.ndarray] = {}
        
        # Gradient computation parameters
        self.gradient_smoothing = 0.1  # Smoothing factor for gradient computation
        self.relevance_threshold = 0.3  # Minimum relevance to follow gradient
        
        print(f"[Gradient Context] Initialized with model: {embedding_model}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        
        TODO: Integrate with your actual embedding system (OpenAI, HuggingFace, etc.)
        For now: placeholder that returns random vector for testing.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (numpy array)
        """
        # Check cache
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        # TODO: Replace with actual embedding call
        # embedding = openai.embeddings.create(model=self.embedding_model, input=text)
        # vector = np.array(embedding.data[0].embedding)
        
        # Placeholder: random vector (replace with real embeddings)
        vector = np.random.randn(1536)  # OpenAI embedding dimension
        vector = vector / np.linalg.norm(vector)  # Normalize
        
        # Cache
        self.embedding_cache[text] = vector
        
        return vector
    
    def compute_relevance_field(
        self,
        query_embedding: np.ndarray,
        artifact_embeddings: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """
        Compute continuous relevance field over all artifacts.
        
        This creates a "semantic landscape" where:
        - High values = very relevant to query
        - Low values = not relevant
        - Gradients point toward more relevant regions
        
        Args:
            query_embedding: Embedding of user's query/intent
            artifact_embeddings: Dict mapping artifact_id -> embedding
            
        Returns:
            Dict mapping artifact_id -> relevance score (0-1)
        """
        relevance_field = {}
        
        for artifact_id, artifact_emb in artifact_embeddings.items():
            # Cosine similarity as base relevance
            similarity = np.dot(query_embedding, artifact_emb)
            
            # Normalize to 0-1 range (cosine is -1 to 1)
            relevance = (similarity + 1) / 2
            
            relevance_field[artifact_id] = float(relevance)
        
        return relevance_field
    
    def compute_gradient_scores(
        self,
        query_embedding: np.ndarray,
        artifact_embeddings: Dict[str, np.ndarray],
        top_k: int = 20
    ) -> List[GradientScore]:
        """
        Compute gradient scores for all artifacts.
        
        Returns not just relevance, but also gradient information:
        - Magnitude: How strongly relevant
        - Direction: Semantic relationship
        - Distance: How far in embedding space
        
        Args:
            query_embedding: Query embedding
            artifact_embeddings: Artifact embeddings
            top_k: Return top-k by gradient magnitude
            
        Returns:
            List of GradientScore objects, sorted by relevance
        """
        scores = []
        
        for artifact_id, artifact_emb in artifact_embeddings.items():
            # Compute relevance (cosine similarity)
            similarity = np.dot(query_embedding, artifact_emb)
            relevance = (similarity + 1) / 2
            
            # Compute semantic distance (Euclidean)
            distance = np.linalg.norm(query_embedding - artifact_emb)
            
            # Compute gradient magnitude (rate of change of relevance)
            # Higher magnitude = steeper gradient = stronger relevance signal
            gradient_magnitude = relevance / (distance + 1e-6)
            
            # Gradient direction (points toward this artifact)
            gradient_direction = (artifact_emb - query_embedding)
            if np.linalg.norm(gradient_direction) > 0:
                gradient_direction = gradient_direction / np.linalg.norm(gradient_direction)
            
            score = GradientScore(
                artifact_id=artifact_id,
                relevance=float(relevance),
                gradient_magnitude=float(gradient_magnitude),
                semantic_distance=float(distance),
                gradient_direction=gradient_direction
            )
            
            scores.append(score)
        
        # Sort by relevance (primary) and gradient magnitude (secondary)
        scores.sort(key=lambda s: (s.relevance, s.gradient_magnitude), reverse=True)
        
        return scores[:top_k]
    
    def find_gradient_peaks(
        self,
        query_embedding: np.ndarray,
        artifact_embeddings: Dict[str, np.ndarray],
        top_k: int = 10
    ) -> List[str]:
        """
        Find "peaks" in the gradient field - regions of highest relevance.
        
        These are the artifacts where the relevance gradient is steepest,
        indicating strong semantic relationship to the query.
        
        Args:
            query_embedding: Query embedding
            artifact_embeddings: Artifact embeddings
            top_k: Number of peaks to return
            
        Returns:
            List of artifact IDs at gradient peaks
        """
        gradient_scores = self.compute_gradient_scores(
            query_embedding,
            artifact_embeddings,
            top_k=top_k
        )
        
        return [score.artifact_id for score in gradient_scores]
    
    def navigate_gradient(
        self,
        start_embedding: np.ndarray,
        artifact_embeddings: Dict[str, np.ndarray],
        steps: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Navigate through semantic space by following the gradient.
        
        Starting from a query, take multiple steps following the direction
        of increasing relevance. This enables multi-hop exploration.
        
        Args:
            start_embedding: Starting point (query embedding)
            artifact_embeddings: Artifact embeddings
            steps: Number of gradient steps to take
            
        Returns:
            List of (artifact_id, relevance) tuples along gradient path
        """
        path = []
        current_position = start_embedding.copy()
        visited = set()
        
        for step in range(steps):
            # Find nearest unvisited artifact
            best_artifact = None
            best_relevance = -1.0
            
            for artifact_id, artifact_emb in artifact_embeddings.items():
                if artifact_id in visited:
                    continue
                
                # Compute relevance from current position
                similarity = np.dot(current_position, artifact_emb)
                relevance = (similarity + 1) / 2
                
                if relevance > best_relevance:
                    best_relevance = relevance
                    best_artifact = artifact_id
                    best_embedding = artifact_emb
            
            if best_artifact is None or best_relevance < self.relevance_threshold:
                break  # No more relevant artifacts
            
            # Add to path
            path.append((best_artifact, float(best_relevance)))
            visited.add(best_artifact)
            
            # Move toward this artifact (follow gradient)
            direction = best_embedding - current_position
            direction = direction / np.linalg.norm(direction)
            current_position = current_position + direction * 0.5  # Step size
            current_position = current_position / np.linalg.norm(current_position)  # Normalize
        
        return path
    
    def compute_semantic_neighborhood(
        self,
        artifact_id: str,
        artifact_embeddings: Dict[str, np.ndarray],
        radius: float = 0.5,
        max_neighbors: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Find semantic neighbors of an artifact.
        
        Useful for discovering related artifacts - if you found one relevant
        data source, what else is nearby in semantic space?
        
        Args:
            artifact_id: Artifact to find neighbors for
            artifact_embeddings: All artifact embeddings
            radius: Maximum semantic distance for neighbors
            max_neighbors: Maximum number of neighbors
            
        Returns:
            List of (neighbor_id, similarity) tuples
        """
        if artifact_id not in artifact_embeddings:
            return []
        
        target_emb = artifact_embeddings[artifact_id]
        neighbors = []
        
        for other_id, other_emb in artifact_embeddings.items():
            if other_id == artifact_id:
                continue
            
            # Compute distance
            distance = np.linalg.norm(target_emb - other_emb)
            
            if distance <= radius:
                similarity = 1.0 - (distance / radius)  # Convert distance to similarity
                neighbors.append((other_id, float(similarity)))
        
        # Sort by similarity
        neighbors.sort(key=lambda x: x[1], reverse=True)
        
        return neighbors[:max_neighbors]
    
    def interpolate_path(
        self,
        artifact_a: str,
        artifact_b: str,
        artifact_embeddings: Dict[str, np.ndarray],
        num_points: int = 5
    ) -> List[np.ndarray]:
        """
        Interpolate path between two artifacts in semantic space.
        
        Useful for understanding the semantic relationship between two concepts.
        What lies "between" FracFocus data and production data in semantic space?
        
        Args:
            artifact_a: First artifact ID
            artifact_b: Second artifact ID
            artifact_embeddings: All embeddings
            num_points: Number of interpolation points
            
        Returns:
            List of embedding vectors along the path
        """
        if artifact_a not in artifact_embeddings or artifact_b not in artifact_embeddings:
            return []
        
        emb_a = artifact_embeddings[artifact_a]
        emb_b = artifact_embeddings[artifact_b]
        
        path = []
        for i in range(num_points):
            t = i / (num_points - 1)  # 0 to 1
            interpolated = (1 - t) * emb_a + t * emb_b
            interpolated = interpolated / np.linalg.norm(interpolated)  # Normalize
            path.append(interpolated)
        
        return path
    
    def compute_gradient_strength(
        self,
        query_embedding: np.ndarray,
        artifact_embeddings: Dict[str, np.ndarray]
    ) -> float:
        """
        Compute overall gradient strength in the semantic field.
        
        High gradient strength = strong, clear relevance signals
        Low gradient strength = weak, ambiguous relevance
        
        This helps agents decide whether to explore further or stop.
        
        Args:
            query_embedding: Query embedding
            artifact_embeddings: Artifact embeddings
            
        Returns:
            Overall gradient strength (0-1)
        """
        scores = self.compute_gradient_scores(query_embedding, artifact_embeddings, top_k=10)
        
        if not scores:
            return 0.0
        
        # Average gradient magnitude of top results
        avg_magnitude = np.mean([s.gradient_magnitude for s in scores])
        
        # Normalize to 0-1 range
        strength = np.tanh(avg_magnitude)  # Squash to 0-1
        
        return float(strength)


class GradientNavigator:
    """
    High-level interface for gradient-guided navigation.
    
    This class provides agent-friendly methods for exploring semantic space
    using the gradient context system.
    """
    
    def __init__(self, gradient_system: GradientContextSystem):
        self.gradient = gradient_system
        self.navigation_history = []
    
    def explore_from_query(
        self,
        query: str,
        artifacts: Dict[str, str],  # artifact_id -> text content
        exploration_strategy: str = "peaks"
    ) -> List[str]:
        """
        Explore semantic space starting from a query.
        
        Args:
            query: User's query/intent
            artifacts: Available artifacts (id -> text)
            exploration_strategy: "peaks" (highest relevance) or "gradient" (follow gradient)
            
        Returns:
            List of artifact IDs to explore, ordered by relevance
        """
        print(f"[Gradient Navigator] Exploring from query: '{query}'")
        print(f"  Strategy: {exploration_strategy}")
        print(f"  Artifacts available: {len(artifacts)}")
        
        # Generate embeddings
        query_emb = self.gradient.embed_text(query)
        artifact_embeddings = {
            aid: self.gradient.embed_text(text)
            for aid, text in artifacts.items()
        }
        
        # Choose exploration strategy
        if exploration_strategy == "peaks":
            # Find gradient peaks (highest relevance)
            results = self.gradient.find_gradient_peaks(
                query_emb,
                artifact_embeddings,
                top_k=10
            )
        elif exploration_strategy == "gradient":
            # Navigate by following gradient
            path = self.gradient.navigate_gradient(
                query_emb,
                artifact_embeddings,
                steps=5
            )
            results = [aid for aid, _ in path]
        else:
            raise ValueError(f"Unknown strategy: {exploration_strategy}")
        
        # Record navigation
        self.navigation_history.append({
            'query': query,
            'strategy': exploration_strategy,
            'results': results
        })
        
        print(f"  → Found {len(results)} relevant artifacts")
        
        return results
    
    def get_semantic_neighbors(
        self,
        artifact_id: str,
        artifacts: Dict[str, str],
        radius: float = 0.5
    ) -> List[str]:
        """
        Find semantically related artifacts.
        
        Args:
            artifact_id: Artifact to find neighbors for
            artifacts: All artifacts
            radius: Search radius in semantic space
            
        Returns:
            List of neighbor artifact IDs
        """
        # Generate embeddings
        artifact_embeddings = {
            aid: self.gradient.embed_text(text)
            for aid, text in artifacts.items()
        }
        
        neighbors = self.gradient.compute_semantic_neighborhood(
            artifact_id,
            artifact_embeddings,
            radius=radius
        )
        
        return [nid for nid, _ in neighbors]


class RepositoryStructureInterpreter:
    """
    Interprets repository paths using structure.yaml schema.
    
    Instead of hardcoding dataset paths, this reads a semantic schema
    that defines what each level in the folder hierarchy means.
    
    Usage:
        interpreter = RepositoryStructureInterpreter("data/structure.yaml")
        context = interpreter.interpret_path("data/raw/FracFocus/Chemical_Data/Parsed")
        # Returns: {
        #   'completeness': 'raw',
        #   'source': 'FracFocus', 
        #   'dataset': 'Chemical_Data',
        #   'etl_stage': 'Parsed',
        #   'domain': 'chemistry',
        #   'join_key': 'APINumber',
        #   'ready_for_use': True
        # }
    """
    
    def __init__(self, structure_path: str = "data/structure.yaml"):
        self.structure_path = Path(structure_path)
        self.schema = self._load_schema()
        
    def _load_schema(self) -> Dict[str, Any]:
        """Load structure.yaml schema."""
        if not self.structure_path.exists():
            print(f"[RepositoryStructure] Warning: {self.structure_path} not found, using defaults")
            return self._default_schema()
        
        try:
            import yaml
            with open(self.structure_path, 'r') as f:
                schema = yaml.safe_load(f)
            print(f"[RepositoryStructure] Loaded schema from {self.structure_path}")
            return schema
        except ImportError:
            print("[RepositoryStructure] PyYAML not installed, trying JSON fallback")
            # Try JSON if YAML not available
            json_path = self.structure_path.with_suffix('.json')
            if json_path.exists():
                with open(json_path, 'r') as f:
                    return json.load(f)
            return self._default_schema()
        except Exception as e:
            print(f"[RepositoryStructure] Error loading schema: {e}")
            return self._default_schema()
    
    def _default_schema(self) -> Dict[str, Any]:
        """Default schema if structure.yaml not found."""
        return {
            "levels": {
                "0": {"name": "root", "value": "data"},
                "1": {"name": "completeness", "possible_values": {"raw": "Original data"}},
                "2": {"name": "source", "dynamic": True},
                "3": {"name": "dataset", "dynamic": True},
                "4": {"name": "etl_stage", "possible_values": {
                    "Downloads": {"ready_for_use": False},
                    "Extracted": {"ready_for_use": False},
                    "Parsed": {"ready_for_use": True}
                }}
            },
            "domain_hints": {}
        }
    
    def interpret_path(self, path: str) -> Dict[str, Any]:
        """
        Interpret a path using the structure schema.
        
        Args:
            path: File or folder path (e.g., "data/raw/FracFocus/Chemical_Data/Parsed")
            
        Returns:
            Dict with semantic interpretation of each path component
        """
        parts = Path(path).parts
        result = {
            'path': path,
            'levels': {},
            'domain': None,
            'join_key': None,
            'ready_for_use': False,
            'status': 'unknown'
        }
        
        levels = self.schema.get('levels', {})
        domain_hints = self.schema.get('domain_hints', {})
        
        for i, part in enumerate(parts):
            level_def = levels.get(str(i), {})
            level_name = level_def.get('name', f'level_{i}')
            
            result['levels'][level_name] = part
            
            # Check for known values
            possible_values = level_def.get('possible_values', {})
            if part in possible_values:
                value_info = possible_values[part]
                if isinstance(value_info, dict):
                    if 'ready_for_use' in value_info:
                        result['ready_for_use'] = value_info['ready_for_use']
                    if 'intent' in value_info:
                        result[f'{level_name}_intent'] = value_info['intent']
                else:
                    result[f'{level_name}_intent'] = value_info
            
            # Check domain hints
            if part in domain_hints:
                hint = domain_hints[part]
                result['domain'] = hint.get('domain')
                join_keys = hint.get('join_keys', [])
                if join_keys:
                    result['join_key'] = join_keys[0].get('field') if isinstance(join_keys[0], dict) else join_keys[0]
                result['source_description'] = hint.get('description')
        
        # Determine status from ETL stage
        etl_stage = result['levels'].get('etl_stage')
        if etl_stage == 'Parsed':
            result['status'] = 'complete'
        elif etl_stage == 'Extracted':
            result['status'] = 'extracted'
        elif etl_stage == 'Downloads':
            result['status'] = 'downloads_only'
        
        return result
    
    def discover_datasets(self, base_path: str = "data/raw") -> List[Dict[str, Any]]:
        """
        Dynamically discover all datasets by scanning directories.
        
        Uses structure schema to interpret what's found.
        
        Returns:
            List of dataset contexts with semantic interpretation
        """
        base = Path(base_path)
        datasets = []
        
        if not base.exists():
            print(f"[RepositoryStructure] Base path not found: {base}")
            return datasets
        
        # Level 2: sources
        for source in base.iterdir():
            if not source.is_dir() or source.name.startswith('.'):
                continue
            
            # Level 3: datasets
            for dataset in source.iterdir():
                if not dataset.is_dir() or dataset.name.startswith('.'):
                    continue
                
                # Find ETL stages present
                stages = []
                for stage in ['Downloads', 'Extracted', 'Parsed']:
                    stage_path = dataset / stage
                    if stage_path.exists():
                        file_count = len(list(stage_path.glob('*')))
                        if file_count > 0:
                            stages.append({'name': stage, 'files': file_count})
                
                # Interpret the path
                context = self.interpret_path(str(dataset))
                context['stages'] = stages
                context['id'] = f"{source.name.lower()}_{dataset.name.lower()}"
                
                datasets.append(context)
        
        print(f"[RepositoryStructure] Discovered {len(datasets)} datasets")
        return datasets
    
    def get_domain_for_source(self, source_name: str) -> Optional[Dict[str, Any]]:
        """Get domain hints for a source."""
        return self.schema.get('domain_hints', {}).get(source_name)
    
    def get_join_relationships(self) -> List[Dict[str, Any]]:
        """Get all defined join relationships."""
        return self.schema.get('join_patterns', [])


# Integration example with AgentStudio
def integrate_gradient_with_agent_studio(agent_studio, gradient_system):
    """
    Integration point: Connect gradient system with AgentStudio.
    
    This enables AgentStudio's semantic index to use gradient-guided navigation.
    """
    # Build artifact text corpus from semantic index
    artifacts = {}
    for artifact in agent_studio.semantic_index.artifacts:
        # Create searchable text from artifact
        text_parts = [
            artifact.name,
            str(artifact.path),
            json.dumps(artifact.metadata)
        ]
        
        if isinstance(artifact.content, str):
            text_parts.append(artifact.content[:500])
        elif isinstance(artifact.content, dict):
            text_parts.append(json.dumps(artifact.content))
        
        artifacts[str(artifact.path)] = " ".join(text_parts)
    
    # Create navigator
    navigator = GradientNavigator(gradient_system)
    
    return artifacts, navigator


# Example usage
if __name__ == "__main__":
    # Initialize gradient system
    gradient = GradientContextSystem()
    
    # Example: Navigate from query
    artifacts = {
        "fracfocus_chemicals.parquet": "chemical data fracfocus cas number concentration",
        "texas_rrc_production.csv": "oil gas production well performance barrels",
        "lab_results.xlsx": "chemical analysis laboratory test results ph viscosity"
    }
    
    navigator = GradientNavigator(gradient)
    
    # Explore using gradient peaks
    results = navigator.explore_from_query(
        query="chemical data for EOR analysis",
        artifacts=artifacts,
        exploration_strategy="peaks"
    )
    
    print(f"\nTop results: {results[:3]}")
    
    # Find semantic neighbors
    if results:
        neighbors = navigator.get_semantic_neighbors(
            artifact_id=results[0],
            artifacts=artifacts,
            radius=0.6
        )
        print(f"Neighbors of {results[0]}: {neighbors}")
