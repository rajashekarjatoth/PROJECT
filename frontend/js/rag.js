/**
 * COGNITIVE ASSISTANCE & INTERVIEW PREPARATION BOT
 * RAG Knowledge Base, Document Ingestion & Performance Analytics
 */

let selectedFile = null;

document.addEventListener('DOMContentLoaded', () => {
  initDropzoneEvents();
});

// -------------------------------------------------------------
// DOCUMENT INGESTION & DROPZONE
// -------------------------------------------------------------
function initDropzoneEvents() {
  const dropzone = document.getElementById('fileDropzone');
  if (!dropzone) return;

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      handleFiles(files[0]);
    }
  });
}

function handleFileSelected(event) {
  const files = event.target.files;
  if (files.length > 0) {
    handleFiles(files[0]);
  }
}

function handleFiles(file) {
  selectedFile = file;
  const dropzone = document.getElementById('fileDropzone');
  dropzone.innerHTML = `
    <i class="fa-solid fa-file-check" style="font-size: 2.25rem; color: var(--accent-emerald); margin-bottom: 0.5rem;"></i>
    <h4 style="font-size: 0.95rem; color: #fff;">Selected: ${file.name}</h4>
    <p style="font-size: 0.75rem; color: var(--text-dim);">${(file.size / 1024).toFixed(1)} KB • Ready for Embedding</p>
  `;

  // Auto-fill title
  const titleInput = document.getElementById('docTitleInput');
  if (titleInput && !titleInput.value) {
    titleInput.value = file.name.replace(/\.[^/.]+$/, "").replace(/_/g, ' ');
  }
}

async function uploadSelectedFile() {
  if (!selectedFile) {
    showToast('Please select or drop a document to ingest first.', 'warning');
    return;
  }

  const uploadBtn = document.getElementById('uploadFileBtn');
  uploadBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Embeddings...';
  uploadBtn.disabled = true;

  const title = document.getElementById('docTitleInput').value.trim();
  const formData = new FormData();
  formData.append('file', selectedFile);
  if (title) formData.append('title', title);
  formData.append('category', 'Technical Prep Notes');

  try {
    const res = await apiRequest('/documents/upload', 'POST', formData, true);
    showToast(res.message, 'success');

    // Reset UI
    selectedFile = null;
    document.getElementById('fileDropzone').innerHTML = `
      <input type="file" id="fileUploadInput" style="display: none;" accept=".pdf,.txt,.md,.json,.py,.sql" onchange="handleFileSelected(event)">
      <i class="fa-solid fa-file-arrow-up" style="font-size: 2.25rem; color: var(--accent-primary); margin-bottom: 0.75rem;"></i>
      <h4 style="font-family: var(--font-heading); font-size: 1rem; color: #fff;">Click or Drag &amp; Drop Documents</h4>
      <p style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.25rem;">Supports PDF notes, Markdown guides, Python &amp; SQL scripts</p>
    `;
    document.getElementById('docTitleInput').value = '';

    // Reload documents list
    loadIngestedDocuments();
    fetchSystemStats();
  } catch (err) {
    showToast('Upload error: ' + err.message, 'error');
  } finally {
    uploadBtn.innerHTML = '<i class="fa-solid fa-upload"></i> Ingest &amp; Embed';
    uploadBtn.disabled = false;
  }
}

async function loadIngestedDocuments() {
  const tbody = document.getElementById('docsTableBody');
  if (!tbody) return;

  try {
    const docs = await apiRequest('/documents/list');
    tbody.innerHTML = '';

    if (docs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-dim); padding: 1.5rem;">No documents uploaded yet. Default knowledge base is active.</td></tr>';
      return;
    }

    docs.forEach(doc => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-weight: 600; color: #fff;">
          <i class="fa-regular fa-file-lines text-cyan" style="margin-right: 0.4rem;"></i>
          ${doc.title}
        </td>
        <td><span class="badge badge-purple">${doc.file_type}</span></td>
        <td><span class="badge badge-cyan">${doc.num_chunks} chunks</span></td>
        <td style="color: var(--text-dim); font-size: 0.78rem;">${doc.uploaded_at}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('Failed to load documents:', err);
  }
}

// -------------------------------------------------------------
// VECTOR SEARCH PLAYGROUND
// -------------------------------------------------------------
async function executeVectorSearch() {
  const queryInput = document.getElementById('vectorSearchInput');
  const query = queryInput.value.trim();
  if (!query) {
    showToast('Enter a search query to test semantic retrieval.', 'info');
    return;
  }

  const container = document.getElementById('vectorSearchResultsContainer');
  container.innerHTML = '<div style="text-align: center; padding: 2rem;"><i class="fa-solid fa-spinner fa-spin text-purple" style="font-size: 1.5rem;"></i><div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">Searching dense vector index...</div></div>';

  try {
    const data = await apiRequest('/documents/search', 'POST', { query, top_k: 4 });
    renderVectorSearchResults(data.results, query);
  } catch (err) {
    container.innerHTML = `<div style="color: var(--accent-rose); font-size: 0.85rem;">Search failed: ${err.message}</div>`;
  }
}

function renderVectorSearchResults(results, query) {
  const container = document.getElementById('vectorSearchResultsContainer');
  container.innerHTML = '';

  if (!results || results.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 2rem; color: var(--text-dim); font-size: 0.85rem;">
        No semantic matches found for "${query}". Try adjusting keywords or uploading notes.
      </div>
    `;
    return;
  }

  results.forEach((r, idx) => {
    const card = document.createElement('div');
    card.style.background = 'rgba(255, 255, 255, 0.02)';
    card.style.border = '1px solid var(--border-glass)';
    card.style.borderRadius = 'var(--radius-md)';
    card.style.padding = '0.85rem 1rem';

    const simPct = Math.round(r.similarity_score * 100);
    const badgeColor = simPct >= 70 ? 'badge-emerald' : (simPct >= 40 ? 'badge-cyan' : 'badge-amber');

    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
        <span style="font-size: 0.85rem; font-weight: 700; color: #fff;">
          <i class="fa-solid fa-bookmark text-purple" style="margin-right: 0.35rem;"></i> ${r.title}
        </span>
        <span class="badge ${badgeColor}">Match: ${simPct}%</span>
      </div>
      <div style="font-size: 0.72rem; color: var(--text-dim); margin-bottom: 0.5rem;">
        Chunk #${r.chunk_index} • File: <code>${r.filename}</code>
      </div>
      <p style="font-size: 0.82rem; color: #d1d5db; line-height: 1.5; background: rgba(0,0,0,0.25); padding: 0.6rem; border-radius: var(--radius-sm); font-family: var(--font-body);">
        ${escapeHtml(r.text.substring(0, 320))}${r.text.length > 320 ? '...' : ''}
      </p>
    `;
    container.appendChild(card);
  });
}

// -------------------------------------------------------------
// PERFORMANCE & HISTORICAL REPORTS
// -------------------------------------------------------------
async function loadUserPerformanceHistory() {
  const tbody = document.getElementById('userHistoryTableBody');
  if (!tbody) return;

  try {
    const history = await apiRequest('/user/history');
    tbody.innerHTML = '';

    if (history.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-dim); padding: 2rem;">No interview simulations completed yet. Start an interview in Tab 1!</td></tr>';
      return;
    }

    // Update summary stats
    const avg = Math.round(history.reduce((acc, h) => acc + (h.score || 0), 0) / history.length);
    const avgScoreEl = document.getElementById('statAverageScore');
    if (avgScoreEl) avgScoreEl.innerText = `${avg}%`;

    const readinessEl = document.getElementById('statReadinessTier');
    if (readinessEl) {
      readinessEl.innerText = avg >= 85 ? 'Senior Ready' : (avg >= 70 ? 'Job-Ready' : 'In Training');
    }

    history.forEach(item => {
      const tr = document.createElement('tr');
      const scoreColor = item.score >= 80 ? 'text-emerald' : (item.score >= 60 ? 'text-amber' : 'text-rose');
      
      tr.innerHTML = `
        <td style="font-weight: 600; color: #fff;">${item.title}</td>
        <td><span class="badge badge-purple">${item.domain}</span></td>
        <td style="text-transform: capitalize;">${item.interview_type}</td>
        <td style="text-transform: capitalize;">${item.difficulty}</td>
        <td style="font-weight: 700;" class="${scoreColor}">${Math.round(item.score || 0)}%</td>
        <td style="color: var(--text-dim); font-size: 0.78rem;">${item.started_at}</td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="viewSessionReport(${item.id})">
            <i class="fa-solid fa-eye"></i> Report
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('Failed to load user history:', err);
  }
}
