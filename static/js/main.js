/* RAG Chatbot - JavaScript */
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('uploadForm')) initUpload();
    if (document.getElementById('chatForm')) initChat();
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) clearBtn.addEventListener('click', clearSession);
});

function initUpload() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const selectedFiles = document.getElementById('selectedFiles');
    const status = document.getElementById('uploadStatus');
    let files = [];

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', e => { e.preventDefault(); dropZone.classList.remove('dragover'); });
    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        addFiles(Array.from(e.dataTransfer.files).filter(f => f.name.toLowerCase().endsWith('.pdf')));
    });
    fileInput.addEventListener('change', e => { addFiles(Array.from(e.target.files)); fileInput.value = ''; });
    uploadForm.addEventListener('submit', async e => { e.preventDefault(); if (files.length) await upload(); });

    function addFiles(newFiles) {
        newFiles.forEach(f => { if (!files.some(x => x.name === f.name)) files.push(f); });
        render();
    }
    function render() {
        selectedFiles.innerHTML = files.map(f => `<div class="selected-file"><span>📄 ${f.name}</span><button type="button" class="remove-file" data-name="${f.name}">✕</button></div>`).join('');
        document.querySelectorAll('.remove-file').forEach(btn => btn.addEventListener('click', () => { files = files.filter(f => f.name !== btn.dataset.name); render(); }));
        uploadBtn.disabled = !files.length;
        status.className = 'upload-status';
    }
    async function upload() {
        status.textContent = 'Processing...';
        status.className = 'upload-status loading';
        uploadBtn.disabled = true;
        const formData = new FormData();
        files.forEach(f => formData.append('files', f));
        try {
            const res = await fetch('/upload', { method: 'POST', body: formData });
            const data = await res.json();
            if (res.ok && data.success) {
                status.textContent = '✓ ' + data.message;
                status.className = 'upload-status success';
                setTimeout(() => location.reload(), 1000);
            } else {
                status.textContent = data.error || 'Upload failed';
                status.className = 'upload-status error';
                uploadBtn.disabled = false;
            }
        } catch {
            status.textContent = 'Network error';
            status.className = 'upload-status error';
            uploadBtn.disabled = false;
        }
    }
}

function initChat() {
    const form = document.getElementById('chatForm');
    const input = document.getElementById('questionInput');
    const messages = document.getElementById('chatMessages');
    const loading = document.getElementById('loadingOverlay');
    const contextContent = document.getElementById('contextContent');
    const closeContext = document.getElementById('closeContext');

    document.querySelectorAll('.sample-q').forEach(btn => btn.addEventListener('click', () => { input.value = btn.dataset.question; form.dispatchEvent(new Event('submit')); }));
    if (closeContext) closeContext.addEventListener('click', () => document.querySelector('.chat-container').classList.remove('context-open'));

    form.addEventListener('submit', async e => {
        e.preventDefault();
        const q = input.value.trim();
        if (!q) return;
        input.value = '';
        const welcome = messages.querySelector('.chat-welcome');
        if (welcome) welcome.remove();
        addMsg(q, 'user');
        loading.classList.add('active');
        try {
            const res = await fetch('/query', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: q }) });
            const data = await res.json();
            if (res.ok && data.success) {
                addMsg(data.answer, 'assistant', data.sources);
                showContext(data.context);
            } else {
                addMsg(data.error || 'Error occurred', 'assistant');
            }
        } catch {
            addMsg('Network error', 'assistant');
        } finally {
            loading.classList.remove('active');
            messages.scrollTop = messages.scrollHeight;
            input.focus();
        }
    });

    function addMsg(text, type, sources = []) {
        const avatar = type === 'user' ? '👤' : '🤖';
        const srcHtml = sources.length ? `<div class="message-sources"><span class="sources-label">Sources:</span>${sources.map(s => `<span class="source-tag">${s}</span>`).join('')}</div>` : '';
        const div = document.createElement('div');
        div.className = `message ${type}-message`;
        div.innerHTML = `<div class="message-avatar">${avatar}</div><div class="message-content"><p>${text.replace(/\n/g, '<br>')}</p>${srcHtml}</div>`;
        messages.appendChild(div);
    }
    function showContext(chunks) {
        if (!chunks?.length) { contextContent.innerHTML = '<p class="context-placeholder">No context</p>'; return; }
        document.querySelector('.chat-container').classList.add('context-open');
        contextContent.innerHTML = chunks.map(c => `<div class="context-chunk"><div class="context-chunk-header"><span>📄 ${c.source}</span><span>${(c.score * 100).toFixed(0)}%</span></div><div class="context-chunk-text">${c.text}</div></div>`).join('');
    }
}

async function clearSession() {
    if (!confirm('Clear all documents and chat?')) return;
    try { await fetch('/clear', { method: 'POST' }); location.href = '/'; } catch { alert('Error'); }
}
