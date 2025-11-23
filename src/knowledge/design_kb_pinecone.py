"""
Gradio Design Knowledge Base with Pinecone RAG

Stores and retrieves Gradio-specific design guidelines, best practices,
and accessibility standards using Pinecone vector database.
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from pinecone import Pinecone, ServerlessSpec
from anthropic import Anthropic
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DesignKnowledgeBasePinecone:
    """
    Gradio Design Knowledge Base using Pinecone for RAG

    Features:
    - Stores Gradio design guidelines and best practices
    - Vector search for relevant design patterns
    - Accessibility standards (WCAG, ARIA)
    - Component-specific guidance
    """

    def __init__(
        self,
        index_name: str = "gradio-design-kb",
        dimension: int = 1024,  # Claude embeddings dimension
        namespace: str = "gradio-guidelines"
    ):
        """
        Initialize Pinecone knowledge base

        Args:
            index_name: Pinecone index name
            dimension: Embedding vector dimension (Claude uses 1024)
            namespace: Namespace for organizing vectors
        """
        self.index_name = index_name
        self.dimension = dimension
        self.namespace = namespace

        # Initialize Pinecone
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")

        self.pc = Pinecone(api_key=api_key)

        # Initialize Anthropic for embeddings
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.anthropic = Anthropic(api_key=anthropic_key)

        # Create or connect to index
        self._setup_index()
        self.index = self.pc.Index(self.index_name)

    def _setup_index(self):
        """Create Pinecone index if it doesn't exist"""
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]

        if self.index_name not in existing_indexes:
            print(f"Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            print(f"[OK] Index created: {self.index_name}")
        else:
            print(f"[OK] Using existing index: {self.index_name}")

    def _get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using sentence-transformers (local, no API needed!)

        Priority:
        1. sentence-transformers (PRIMARY - local, free, good quality)
        2. OpenAI (FALLBACK - if sentence-transformers fails)
        3. Hash (LAST RESORT - development only)

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # PRIMARY: Use sentence-transformers (local, free, good quality)
        try:
            from sentence_transformers import SentenceTransformer

            # Cache model instance (one-time download ~90MB)
            if not hasattr(self, '_st_model'):
                print("[INFO] Loading sentence-transformers model (one-time, ~90MB download)...")
                self._st_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("[INFO] Model loaded successfully!")

            # Generate embedding
            embedding = self._st_model.encode(text).tolist()

            # Pad or truncate to match dimension
            if len(embedding) < self.dimension:
                embedding.extend([0.0] * (self.dimension - len(embedding)))
            elif len(embedding) > self.dimension:
                embedding = embedding[:self.dimension]

            return embedding

        except ImportError as e:
            # Import error - module not installed or DLL issue
            if not hasattr(self, '_st_import_error_logged'):
                print(f"[INFO] sentence-transformers not available (expected on Windows), using OpenAI fallback")
                self._st_import_error_logged = True
        except Exception as e:
            # Other error during embedding generation
            if not hasattr(self, '_st_error_logged'):
                error_msg = str(e)
                if len(error_msg) > 100:
                    error_msg = error_msg[:100] + "..."
                print(f"[WARNING] sentence-transformers failed: {error_msg}, trying OpenAI...")
                self._st_error_logged = True

        # FALLBACK: Try OpenAI (if sentence-transformers fails)
        try:
            import openai
            openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response = openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            embedding = response.data[0].embedding

            # OpenAI returns 1536 dimensions, pad or truncate to match our index
            if len(embedding) < self.dimension:
                embedding.extend([0.0] * (self.dimension - len(embedding)))
            elif len(embedding) > self.dimension:
                embedding = embedding[:self.dimension]

            # Only print this message once per session
            if not hasattr(self, '_openai_logged'):
                print("[INFO] Using OpenAI embeddings (sentence-transformers not available)")
                self._openai_logged = True
            return embedding

        except ImportError as e:
            print(f"[WARNING] OpenAI module not installed: {e}, using hash fallback")
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            print(f"[WARNING] OpenAI embedding failed ({error_type}): {error_msg}, using hash fallback")

        # LAST RESORT: Hash-based embedding (poor quality, development only)
        print("[ERROR] Both sentence-transformers and OpenAI failed!")
        print("[ERROR] Using hash-based fallback - search quality will be POOR")

        import hashlib
        import struct

        # Generate deterministic embedding from text hash
        hash_obj = hashlib.sha512(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to normalized float vector
        embedding = []
        for i in range(0, min(len(hash_bytes), self.dimension * 4), 4):
            chunk = hash_bytes[i:i+4]
            if len(chunk) == 4:
                # Normalize to [-1, 1] range
                val = struct.unpack('I', chunk)[0] / (2**32) * 2 - 1
                embedding.append(float(val))

        # Pad to correct dimension
        while len(embedding) < self.dimension:
            embedding.append(0.0)

        # Normalize vector for cosine similarity
        embedding = embedding[:self.dimension]
        norm = sum(x*x for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]

        return embedding

    def add_guideline(
        self,
        guideline_id: str,
        title: str,
        content: str,
        category: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a design guideline to the knowledge base

        Args:
            guideline_id: Unique ID for the guideline
            title: Guideline title
            content: Full guideline text
            category: Category (e.g., "accessibility", "layout", "components")
            metadata: Additional metadata

        Returns:
            Success status
        """
        try:
            # Generate embedding
            embedding = self._get_embedding(content)

            # Prepare metadata
            meta = {
                "title": title,
                "content": content,
                "category": category,
                "added_at": datetime.now().isoformat()
            }
            if metadata:
                meta.update(metadata)

            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(guideline_id, embedding, meta)],
                namespace=self.namespace
            )

            print(f"[OK] Added guideline: {title}")
            return True

        except Exception as e:
            print(f"[FAIL] Error adding guideline: {e}")
            return False

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query the knowledge base for relevant guidelines

        Args:
            query_text: Search query
            top_k: Number of results to return
            category: Optional category filter

        Returns:
            List of matching guidelines with scores
        """
        try:
            # Generate query embedding
            query_embedding = self._get_embedding(query_text)

            # Build filter
            filter_dict = {}
            if category:
                filter_dict["category"] = category

            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=self.namespace,
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )

            # Format results
            formatted = []
            for match in results.matches:
                formatted.append({
                    "id": match.id,
                    "score": match.score,
                    "title": match.metadata.get("title", ""),
                    "content": match.metadata.get("content", ""),
                    "category": match.metadata.get("category", "")
                })

            return formatted

        except Exception as e:
            print(f"[FAIL] Error querying knowledge base: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "namespaces": stats.namespaces,
                "dimension": self.dimension
            }
        except Exception as e:
            print(f"[FAIL] Error getting stats: {e}")
            return {}

    def clear(self):
        """Clear all vectors from the knowledge base"""
        try:
            self.index.delete(delete_all=True, namespace=self.namespace)
            print(f"[OK] Cleared namespace: {self.namespace}")
        except Exception as e:
            print(f"[FAIL] Error clearing knowledge base: {e}")
