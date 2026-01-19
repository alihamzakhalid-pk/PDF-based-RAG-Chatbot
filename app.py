"""PDF-based RAG Chatbot - Flask Application."""

import os
import uuid
import numpy as np
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename

from config import Config
from rag import (PDFLoader, TextCleaner, TextChunker, EmbeddingGenerator, 
                 FAISSVectorStore, Retriever, AnswerGenerator)

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
Config.init_app()

user_sessions = {}


def get_user_session():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    
    if user_id not in user_sessions:
        embed_gen = EmbeddingGenerator(Config.EMBEDDING_MODEL)
        vector_store = FAISSVectorStore(dimension=embed_gen.get_embedding_dimension())
        
        user_sessions[user_id] = {
            'pdf_loader': PDFLoader(),
            'text_cleaner': TextCleaner(),
            'chunker': TextChunker(chunk_size=Config.CHUNK_SIZE, chunk_overlap=Config.CHUNK_OVERLAP),
            'embedding_gen': embed_gen,
            'vector_store': vector_store,
            'retriever': Retriever(embed_gen, vector_store, top_k=Config.TOP_K_CHUNKS),
            'answer_gen': AnswerGenerator(api_key=Config.GROQ_API_KEY, model=Config.LLM_MODEL),
            'documents': [],
            'chat_history': []
        }
    
    return user_sessions[user_id]


@app.route('/')
def index():
    user_session = get_user_session()
    return render_template('index.html', documents=user_session.get('documents', []))


@app.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
    user_session = get_user_session()
    user_upload_dir = os.path.join(Config.UPLOAD_FOLDER, session['user_id'])
    os.makedirs(user_upload_dir, exist_ok=True)
    
    uploaded_files = []
    for file in files:
        if file and Config.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(user_upload_dir, filename)
            file.save(filepath)
            uploaded_files.append(filepath)
    
    if not uploaded_files:
        return jsonify({'error': 'No valid PDF files'}), 400
    
    try:
        documents = user_session['pdf_loader'].load_multiple_pdfs(uploaded_files)
        cleaned_docs = user_session['text_cleaner'].clean_documents(documents)
        chunks = user_session['chunker'].chunk_documents(cleaned_docs)
        chunks_with_emb = user_session['embedding_gen'].generate_embeddings_for_chunks(chunks)
        embeddings = np.array([c['embedding'] for c in chunks_with_emb])
        user_session['vector_store'].add_embeddings(embeddings, chunks_with_emb)
        
        for doc in documents:
            user_session['documents'].append({'filename': doc['filename'], 'pages': doc['total_pages']})
        
        return jsonify({
            'success': True,
            'message': f'Processed {len(documents)} document(s) with {len(chunks)} chunks',
            'documents': user_session['documents']
        })
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/chat')
def chat():
    user_session = get_user_session()
    if not user_session['documents']:
        return redirect(url_for('index'))
    return render_template('chat.html', documents=user_session['documents'], 
                          chat_history=user_session['chat_history'])


@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({'error': 'No question provided'}), 400
    
    question = data['question'].strip()
    if not question:
        return jsonify({'error': 'Question cannot be empty'}), 400
    
    user_session = get_user_session()
    if user_session['vector_store'].index.ntotal == 0:
        return jsonify({'error': 'No documents uploaded'}), 400
    
    try:
        clean_q = user_session['text_cleaner'].clean_query(question)
        context, chunks = user_session['retriever'].retrieve_with_context(clean_q, top_k=Config.TOP_K_CHUNKS)
        result = user_session['answer_gen'].generate_with_sources(clean_q, chunks)
        
        chat_entry = {
            'question': question,
            'answer': result['answer'],
            'sources': result.get('sources', []),
            'context': [{'text': c['text'][:200] + '...' if len(c['text']) > 200 else c['text'],
                        'source': c.get('source', 'Unknown'),
                        'score': round(c.get('similarity_score', 0), 3)} for c in chunks]
        }
        user_session['chat_history'].append(chat_entry)
        
        return jsonify({
            'success': True, 'answer': result['answer'], 'sources': result.get('sources', []),
            'context': chat_entry['context'], 'model': result.get('model', 'unknown')
        })
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/clear', methods=['POST'])
def clear():
    if 'user_id' in session:
        user_id = session['user_id']
        import shutil
        user_dir = os.path.join(Config.UPLOAD_FOLDER, user_id)
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)
        if user_id in user_sessions:
            del user_sessions[user_id]
        session.clear()
    return jsonify({'success': True})


@app.route('/stats')
def stats():
    user_session = get_user_session()
    return jsonify({
        'documents': len(user_session['documents']),
        'chunks': user_session['vector_store'].index.ntotal,
        'chat_history': len(user_session['chat_history'])
    })


if __name__ == '__main__':
    print("\n" + "="*50)
    print("  PDF-based RAG Chatbot")
    print("  Open http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
