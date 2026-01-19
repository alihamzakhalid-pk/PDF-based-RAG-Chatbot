"""PDF Loader - Extracts text from PDF files using pdfplumber."""

import pdfplumber
import os
from typing import List, Dict


class PDFLoader:
    def __init__(self):
        self.extracted_documents = []

    def load_single_pdf(self, file_path: str) -> Dict:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF not found: {file_path}")

        filename = os.path.basename(file_path)
        pages_text = []
        full_text = []

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                pages_text.append({'page_number': page_num, 'text': text})
                full_text.append(text)

        return {
            'filename': filename,
            'file_path': file_path,
            'total_pages': len(pages_text),
            'pages': pages_text,
            'full_text': '\n\n'.join(full_text)
        }

    def load_multiple_pdfs(self, file_paths: List[str]) -> List[Dict]:
        documents = []
        for file_path in file_paths:
            try:
                doc = self.load_single_pdf(file_path)
                documents.append(doc)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        self.extracted_documents = documents
        return documents

    def get_combined_text(self, documents: List[Dict] = None) -> str:
        docs = documents or self.extracted_documents
        return '\n\n'.join([f"--- {d['filename']} ---\n{d['full_text']}" for d in docs])
