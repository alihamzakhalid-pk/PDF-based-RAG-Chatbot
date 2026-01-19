"""Answer Generator - Uses Groq API with LLaMA for grounded answers."""

import os
from typing import List, Dict, Optional
from groq import Groq


class AnswerGenerator:
    SYSTEM_PROMPT = """You are a helpful assistant. Answer questions using ONLY the provided context.
If the answer is not in the context, say "I cannot find this information in the uploaded documents."
Do NOT make up information. Be accurate and concise."""

    USER_PROMPT = """Context:
---
{context}
---

Question: {question}

Answer using ONLY the context above:"""

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY required")
        self.model = model
        self.client = Groq(api_key=self.api_key)
        self.available_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", 
                                  "mixtral-8x7b-32768", "gemma2-9b-it"]

    def generate(self, question: str, context: str, temperature: float = 0.1) -> Dict:
        if not context.strip():
            return {'answer': "No documents uploaded. Please upload PDFs first.", 
                    'model': self.model, 'usage': None}
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": self.USER_PROMPT.format(context=context, question=question)}
                ],
                temperature=temperature,
                max_tokens=1024
            )
            return {
                'answer': response.choices[0].message.content,
                'model': self.model,
                'usage': {'total_tokens': response.usage.total_tokens}
            }
        except Exception as e:
            return {'answer': f"Error: {str(e)}", 'model': self.model, 'error': str(e), 'usage': None}

    def generate_with_sources(self, question: str, chunks: List[Dict], temperature: float = 0.1) -> Dict:
        context = "\n\n".join([f"[{c.get('source', 'Doc')}]\n{c['text']}" for c in chunks])
        sources = list(set([c.get('source', 'Unknown') for c in chunks]))
        result = self.generate(question, context, temperature)
        result['sources'] = sources
        result['chunks_used'] = len(chunks)
        return result

    def set_model(self, model: str) -> bool:
        if model in self.available_models:
            self.model = model
            return True
        return False
