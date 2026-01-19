"""
Configuration settings for the RAG Chatbot application.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    LLM_MODEL = os.getenv('LLM_MODEL', 'llama-3.3-70b-versatile')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    TOP_K_CHUNKS = int(os.getenv('TOP_K_CHUNKS', 5))
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 800))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 150))
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    FAISS_INDEX_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'faiss_index')
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    @staticmethod
    def init_app():
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.FAISS_INDEX_FOLDER, exist_ok=True)

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
