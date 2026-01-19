"""Embeddings Generator - Creates vector embeddings using Sentence-Transformers."""

import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Dimension: {self.embedding_dimension}")

    def generate_embedding(self, text: str) -> np.ndarray:
        if not text.strip():
            return np.zeros(self.embedding_dimension)
        return self.model.encode([text], convert_to_numpy=True, normalize_embeddings=True)[0]

    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        if not texts:
            return np.array([])
        return self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True, 
                                  normalize_embeddings=True, show_progress_bar=True)

    def generate_embeddings_for_chunks(self, chunks: List[Dict], batch_size: int = 32) -> List[Dict]:
        if not chunks:
            return []
        texts = [c.get('text', '') for c in chunks]
        embeddings = self.generate_embeddings(texts, batch_size)
        for i, chunk in enumerate(chunks):
            chunk['embedding'] = embeddings[i]
        return chunks

    def get_embedding_dimension(self) -> int:
        return self.embedding_dimension
