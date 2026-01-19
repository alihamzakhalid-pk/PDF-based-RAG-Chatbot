# 🔮 PDF-based RAG Chatbot

A **Retrieval Augmented Generation (RAG)** chatbot that answers questions exclusively from your uploaded PDF documents.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-2.3+-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

## ✨ Features

- 📄 **Multi-PDF Upload** - Process multiple documents
- 🔍 **Semantic Search** - FAISS vector similarity
- 🎯 **Grounded Answers** - Only from document content
- 🚫 **No Hallucination** - Refuses if info not found
- 💬 **Modern UI** - Clean dark theme

## 🏗️ Architecture

```
PDF → Extract → Clean → Chunk → Embed → FAISS Index
                                            ↓
Query → Embed → Search → Top-K → LLaMA 3 → Answer
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python, Flask |
| PDF | pdfplumber |
| Embeddings | Sentence-Transformers |
| Vector DB | FAISS |
| LLM | LLaMA 3 (Groq API) |
| Frontend | HTML, CSS, JS |

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
# Copy .env.example to .env and add your GROQ_API_KEY

# 3. Run
python app.py

# 4. Open http://localhost:5000
```

## ⚙️ Configuration

Edit `.env` file:

```env
GROQ_API_KEY=your_key_here
LLM_MODEL=llama-3.3-70b-versatile
CHUNK_SIZE=800
TOP_K_CHUNKS=5
```

## 📁 Project Structure

```
├── app.py              # Flask app
├── config.py           # Settings
├── requirements.txt    # Dependencies
├── rag/                # RAG pipeline
│   ├── pdf_loader.py
│   ├── text_cleaner.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│   └── generator.py
├── templates/          # HTML
└── static/             # CSS, JS
```

## 📄 License

MIT License

---

**Built with Flask, FAISS, Sentence-Transformers & Groq**