"""FAISS Vector Store - Stores and searches embeddings."""

import os
import json
import numpy as np
import faiss
from typing import List, Dict, Tuple, Optional


class FAISSVectorStore:
    def __init__(self, dimension: int, index_path: Optional[str] = None):
        self.dimension = dimension
        self.index_path = index_path
        self.index = faiss.IndexFlatIP(dimension)
        self.metadata = []

    def add_embeddings(self, embeddings: np.ndarray, chunks_metadata: List[Dict]) -> None:
        if len(embeddings) == 0:
            return
        embeddings = embeddings.astype(np.float32)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        for meta in chunks_metadata:
            self.metadata.append({k: v for k, v in meta.items() if k != 'embedding'})

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[Dict, float]]:
        if self.index.ntotal == 0:
            return []
        query = query_embedding.astype(np.float32).reshape(1, -1)
        faiss.normalize_L2(query)
        top_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query, top_k)
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if 0 <= idx < len(self.metadata):
                results.append((self.metadata[idx], float(score)))
        return results

    def save(self, path: Optional[str] = None) -> None:
        save_path = path or self.index_path
        if not save_path:
            return
        os.makedirs(save_path, exist_ok=True)
        faiss.write_index(self.index, os.path.join(save_path, "index.faiss"))
        with open(os.path.join(save_path, "metadata.json"), 'w') as f:
            json.dump(self.metadata, f)

    def load(self, path: Optional[str] = None) -> bool:
        load_path = path or self.index_path
        if not load_path:
            return False
        try:
            self.index = faiss.read_index(os.path.join(load_path, "index.faiss"))
            with open(os.path.join(load_path, "metadata.json")) as f:
                self.metadata = json.load(f)
            return True
        except:
            return False

    def clear(self) -> None:
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []

    def get_stats(self) -> Dict:
        return {'total_vectors': self.index.ntotal, 'dimension': self.dimension}
