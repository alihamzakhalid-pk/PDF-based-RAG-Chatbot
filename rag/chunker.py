"""Text Chunker - Splits text into overlapping chunks."""

import re
from typing import List, Dict
from transformers import AutoTokenizer


class TextChunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150,
                 tokenizer_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        except:
            self.tokenizer = None

    def count_tokens(self, text: str) -> int:
        if self.tokenizer:
            return len(self.tokenizer.encode(text, add_special_tokens=False))
        return len(text.split())

    def chunk_text(self, text: str, source: str = "document") -> List[Dict]:
        if not text.strip():
            return []

        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_id = 0

        for sentence in sentences:
            tokens = self.count_tokens(sentence)

            if tokens > self.chunk_size:
                if current_chunk:
                    chunks.append(self._make_chunk(' '.join(current_chunk), chunk_id, source))
                    chunk_id += 1
                    current_chunk = []
                    current_tokens = 0
                
                words = sentence.split()
                temp = []
                temp_tokens = 0
                for word in words:
                    wt = self.count_tokens(word)
                    if temp_tokens + wt > self.chunk_size:
                        chunks.append(self._make_chunk(' '.join(temp), chunk_id, source))
                        chunk_id += 1
                        temp = [word]
                        temp_tokens = wt
                    else:
                        temp.append(word)
                        temp_tokens += wt
                if temp:
                    current_chunk = temp
                    current_tokens = temp_tokens
                continue

            if current_tokens + tokens > self.chunk_size:
                if current_chunk:
                    chunks.append(self._make_chunk(' '.join(current_chunk), chunk_id, source))
                    chunk_id += 1
                    
                    overlap = []
                    overlap_tokens = 0
                    for s in reversed(current_chunk):
                        st = self.count_tokens(s)
                        if overlap_tokens + st <= self.chunk_overlap:
                            overlap.insert(0, s)
                            overlap_tokens += st
                        else:
                            break
                    current_chunk = overlap + [sentence]
                    current_tokens = self.count_tokens(' '.join(current_chunk))
                else:
                    current_chunk = [sentence]
                    current_tokens = tokens
            else:
                current_chunk.append(sentence)
                current_tokens += tokens

        if current_chunk:
            chunks.append(self._make_chunk(' '.join(current_chunk), chunk_id, source))

        return chunks

    def _make_chunk(self, text: str, chunk_id: int, source: str) -> Dict:
        return {
            'chunk_id': chunk_id,
            'text': text,
            'source': source,
            'token_count': self.count_tokens(text)
        }

    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        all_chunks = []
        gid = 0
        for doc in documents:
            chunks = self.chunk_text(doc.get('full_text', ''), doc.get('filename', 'unknown'))
            for c in chunks:
                c['global_chunk_id'] = gid
                gid += 1
            all_chunks.extend(chunks)
        return all_chunks
