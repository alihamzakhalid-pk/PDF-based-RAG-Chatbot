"""Retriever - Finds relevant chunks for a query."""

from typing import List, Dict, Tuple, Optional
from .embeddings import EmbeddingGenerator
from .vector_store import FAISSVectorStore


class Retriever:
    def __init__(self, embedding_generator: EmbeddingGenerator, 
                 vector_store: FAISSVectorStore, top_k: int = 5):
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        k = top_k or self.top_k
        query_embedding = self.embedding_generator.generate_embedding(query)
        results = self.vector_store.search(query_embedding, top_k=k)
        return [{**meta, 'similarity_score': score} for meta, score in results]

    def retrieve_with_context(self, query: str, top_k: Optional[int] = None) -> Tuple[str, List[Dict]]:
        chunks = self.retrieve(query, top_k)
        context_parts = []
        for c in chunks:
            context_parts.append(f"[{c.get('source', 'Doc')}] (Score: {c['similarity_score']:.2f})\n{c['text']}")
        return "\n\n---\n\n".join(context_parts), chunks

    def get_stats(self) -> Dict:
        return {
            'model': self.embedding_generator.model_name,
            'dimension': self.embedding_generator.embedding_dimension,
            'vectors': self.vector_store.get_stats(),
            'top_k': self.top_k
        }
