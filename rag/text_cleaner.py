"""Text Cleaner - Preprocesses and normalizes text."""

import re
import unicodedata
from typing import List, Dict


class TextCleaner:
    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Replace special quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('–', '-').replace('—', '-')
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:\'"()\-\[\]{}@#$%&*+=/<>]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()

    def clean_documents(self, documents: List[Dict]) -> List[Dict]:
        cleaned = []
        for doc in documents:
            cleaned_doc = doc.copy()
            cleaned_doc['full_text'] = self.clean_text(doc['full_text'])
            if 'pages' in doc:
                cleaned_doc['pages'] = [
                    {**p, 'text': self.clean_text(p['text'])} for p in doc['pages']
                ]
            cleaned.append(cleaned_doc)
        return cleaned

    def clean_query(self, query: str) -> str:
        return re.sub(r'\s+', ' ', query.strip())
