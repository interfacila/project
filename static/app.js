const API = '';
let currentPage = 'files';
let selectedFiles = [];

// ─── Page Navigation ─────────────────────────────────────────────────────────

function switchPage(page) {
    currentPage = page;

    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });

    const pages = ['files', 'ai', 'knowledge', 'stats', 'universities', 'academics', 'publications'];
    pages.forEach(p => {
        const el = document.getElementById('page-' + p);
        if (!el) return;
        if (p === 'ai' || p === 'knowledge') {
            el.classList.toggle('active', p === page);
        } else {
            el.style.display = p === page ? 'block' : 'none';
        }
    });
    // hide ai/knowledge when switching to other pages
    if (page !== 'ai') document.getElementById('page-ai').classList.remove('active');
    if (page !== 'knowledge') document.getElementById('page-knowledge').classList.remove('active');

    if (page === 'files') loadFiles();
    if (page === 'knowledge') loadKnowledge();
    if (page === 'stats') loadStats();
    if (page === 'universities') loadUniversities();
    if (page === 'academics') loadAcademics();
    if (page === 'publications') loadPublications();
}

// ─── File Operations ─────────────────────────────────────────────────────────

async function loadFiles(search) {
    const params = new URLSearchParams();
    if (search) params.set('search', search);

    try {
        const res = await fetch(`${API}/api/files?${params}`);
        const files = await res.json();
        renderFiles(files);
        updateStorage(files);
    } catch (err) {
        console.error('Dosyalar yüklenemedi:', err);
    }
}

function renderFiles(files) {
    const container = document.getElementById('filesList');

    if (files.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📂</div>
                <h3>Henüz dosya yok</h3>
                <p>"Yeni" butonuna tıklayarak dosya yükleyebilirsiniz.</p>
            </div>
        `;
        return;
    }

    let html = `
        <table class="file-list">
            <thead>
                <tr>
                    <th>Ad</th>
                    <th>Kategori</th>
                    <th>Boyut</th>
                    <th>Tarih</th>
                    <th>İşlemler</th>
                </tr>
            </thead>
            <tbody>
    `;

    for (const file of files) {
        const icon = getFileIcon(file.file_type);
        const size = formatFileSize(file.file_size);
        const date = formatDate(file.created_at);

        html += `
            <tr>
                <td>
                    <div class="file-name-cell">
                        <span class="file-icon-sm">${icon}</span>
                        <span>${escapeHtml(file.original_filename)}</span>
                    </div>
                </td>
                <td>${escapeHtml(file.category)}</td>
                <td>${size}</td>
                <td>${date}</td>
                <td>
                    <div class="file-actions-cell">
                        <button onclick="downloadFile(${file.id}, '${escapeHtml(file.original_filename)}')" title="İndir">⬇️</button>
                        <button onclick="askAIAboutFile(${file.id}, '${escapeHtml(file.original_filename)}')" title="AI'a Sor">🤖</button>
                        <button class="delete-btn" onclick="deleteFile(${file.id})" title="Sil">🗑️</button>
                    </div>
                </td>
            </tr>
        `;
    }

    html += '</tbody></table>';
    container.innerHTML = html;
}

function getFileIcon(mimeType) {
    if (!mimeType) return '📄';
    if (mimeType.includes('pdf')) return '📕';
    if (mimeType.includes('word') || mimeType.includes('document')) return '📝';
    if (mimeType.includes('sheet') || mimeType.includes('excel')) return '📊';
    if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) return '📙';
    if (mimeType.includes('image')) return '🖼️';
    if (mimeType.includes('video')) return '🎬';
    if (mimeType.includes('audio')) return '🎵';
    if (mimeType.includes('zip') || mimeType.includes('rar') || mimeType.includes('archive')) return '📦';
    if (mimeType.includes('text')) return '📄';
    return '📄';
}

function formatFileSize(bytes) {
    if (!bytes) return '-';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    const months = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'];
    return `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`;
}

function updateStorage(files) {
    const totalSize = files.reduce((sum, f) => sum + (f.file_size || 0), 0);
    const maxStorage = 1024 * 1024 * 1024; // 1 GB
    const percent = Math.min((totalSize / maxStorage) * 100, 100);

    document.getElementById('storageText').textContent =
        `${formatFileSize(totalSize)} / 1 GB kullanılıyor`;
    document.getElementById('storageBar').style.width = percent + '%';
}

async function downloadFile(fileId, filename) {
    try {
        const res = await fetch(`${API}/api/files/${fileId}/download`);
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
        showToast('Dosya indiriliyor...');
    } catch (err) {
        showToast('İndirme hatası!');
    }
}

async function deleteFile(fileId) {
    if (!confirm('Bu dosyayı silmek istediğinize emin misiniz?')) return;

    try {
        await fetch(`${API}/api/files/${fileId}`, { method: 'DELETE' });
        showToast('Dosya silindi');
        loadFiles();
    } catch (err) {
        showToast('Silme hatası!');
    }
}

// ─── Upload ──────────────────────────────────────────────────────────────────

function openUploadModal() {
    document.getElementById('uploadModal').classList.add('active');
    selectedFiles = [];
    document.getElementById('selectedFiles').innerHTML = '';
    document.getElementById('uploadDesc').value = '';
}

function closeUploadModal() {
    document.getElementById('uploadModal').classList.remove('active');
    selectedFiles = [];
}

function handleFileSelect(files) {
    selectedFiles = Array.from(files);
    const container = document.getElementById('selectedFiles');
    container.innerHTML = selectedFiles.map(f =>
        `<div style="padding: 6px 0; font-size: 13px;">${getFileIcon(f.type)} ${f.name} (${formatFileSize(f.size)})</div>`
    ).join('');
}

// Drag & drop
const dropZone = document.getElementById('dropZone');
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});
dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    handleFileSelect(e.dataTransfer.files);
});

async function uploadFiles() {
    if (selectedFiles.length === 0) {
        showToast('Lütfen dosya seçin');
        return;
    }

    const btn = document.getElementById('uploadBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Yükleniyor...';

    const description = document.getElementById('uploadDesc').value;
    const category = document.getElementById('uploadCategory').value;

    for (const file of selectedFiles) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('description', description);
        formData.append('category', category);

        try {
            await fetch(`${API}/api/files`, {
                method: 'POST',
                body: formData,
            });
        } catch (err) {
            showToast(`Hata: ${file.name} yüklenemedi`);
        }
    }

    btn.disabled = false;
    btn.textContent = 'Yükle';
    closeUploadModal();
    showToast(`${selectedFiles.length} dosya yüklendi`);
    loadFiles();
}

// ─── AI Chat ─────────────────────────────────────────────────────────────────

async function sendAIQuery() {
    const input = document.getElementById('aiInput');
    const query = input.value.trim();
    if (!query) return;

    const messages = document.getElementById('aiMessages');
    messages.innerHTML += `<div class="ai-message user">${escapeHtml(query)}</div>`;
    input.value = '';

    const sendBtn = document.getElementById('aiSendBtn');
    sendBtn.disabled = true;

    messages.innerHTML += `<div class="ai-message assistant" id="aiLoading"><span class="spinner"></span> Düşünüyorum...</div>`;
    messages.scrollTop = messages.scrollHeight;

    try {
        const res = await fetch(`${API}/api/ai/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query }),
        });
        const data = await res.json();

        document.getElementById('aiLoading').remove();
        messages.innerHTML += `<div class="ai-message assistant">${escapeHtml(data.response_text || 'Yanıt alınamadı.')}</div>`;
    } catch (err) {
        document.getElementById('aiLoading').remove();
        messages.innerHTML += `<div class="ai-message assistant">Hata oluştu. Lütfen tekrar deneyin.</div>`;
    }

    sendBtn.disabled = false;
    messages.scrollTop = messages.scrollHeight;
}

function askAIAboutFile(fileId, filename) {
    switchPage('ai');
    const input = document.getElementById('aiInput');
    input.value = `"${filename}" dosyası hakkında bilgi ver.`;
    input.focus();
}

// ─── Knowledge Base ──────────────────────────────────────────────────────────

async function loadKnowledge() {
    try {
        const res = await fetch(`${API}/api/knowledge`);
        const entries = await res.json();
        renderKnowledge(entries);
    } catch (err) {
        console.error('Bilgi tabanı yüklenemedi:', err);
    }
}

function renderKnowledge(entries) {
    const container = document.getElementById('kbList');

    if (entries.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📚</div>
                <h3>Bilgi tabanı boş</h3>
                <p>Yukarıdaki formu kullanarak bilgi ekleyebilirsiniz.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = entries.map(entry => `
        <div class="kb-card">
            <h4>${escapeHtml(entry.title)}</h4>
            <p>${escapeHtml(entry.content.substring(0, 300))}${entry.content.length > 300 ? '...' : ''}</p>
            <div class="kb-meta">
                <span>📂 ${escapeHtml(entry.category)}</span>
                ${entry.source ? `<span>📎 ${escapeHtml(entry.source)}</span>` : ''}
                <span>📅 ${formatDate(entry.created_at)}</span>
            </div>
            <div class="kb-actions">
                <button class="btn-cancel" onclick="deleteKnowledge(${entry.id})">🗑️ Sil</button>
            </div>
        </div>
    `).join('');
}

async function addKnowledge() {
    const title = document.getElementById('kbTitle').value.trim();
    const content = document.getElementById('kbContent').value.trim();
    const source = document.getElementById('kbSource').value.trim();
    const category = document.getElementById('kbCategory').value;

    if (!title || !content) {
        showToast('Başlık ve içerik gereklidir');
        return;
    }

    try {
        await fetch(`${API}/api/knowledge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content, source: source || null, category }),
        });

        document.getElementById('kbTitle').value = '';
        document.getElementById('kbContent').value = '';
        document.getElementById('kbSource').value = '';

        showToast('Bilgi eklendi');
        loadKnowledge();
    } catch (err) {
        showToast('Ekleme hatası!');
    }
}

async function deleteKnowledge(id) {
    if (!confirm('Bu kaydı silmek istediğinize emin misiniz?')) return;

    try {
        await fetch(`${API}/api/knowledge/${id}`, { method: 'DELETE' });
        showToast('Bilgi silindi');
        loadKnowledge();
    } catch (err) {
        showToast('Silme hatası!');
    }
}

// ─── Stats ───────────────────────────────────────────────────────────────────

async function loadStats() {
    try {
        const res = await fetch(`${API}/api/stats`);
        const stats = await res.json();

        document.getElementById('statsGrid').innerHTML = `
            <div class="stat-card">
                <div class="stat-number">${stats.total_files}</div>
                <div class="stat-label">📁 Toplam Dosya</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.total_knowledge}</div>
                <div class="stat-label">📚 Bilgi Kaydı</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.total_queries}</div>
                <div class="stat-label">🤖 AI Sorgusu</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.total_universities || 0}</div>
                <div class="stat-label">🏛️ Üniversite</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.total_academics || 0}</div>
                <div class="stat-label">👨‍🏫 Akademisyen</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.total_publications || 0}</div>
                <div class="stat-label">📄 Yayın</div>
            </div>
        `;
    } catch (err) {
        console.error('İstatistikler yüklenemedi:', err);
    }
}

// ─── Search ──────────────────────────────────────────────────────────────────

let searchTimeout;
function handleSearch(value) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        if (currentPage === 'files') {
            loadFiles(value);
        }
    }, 300);
}

// ─── Utilities ───────────────────────────────────────────────────────────────

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ─── Universities ────────────────────────────────────────────────────────────

let uniSearchTimeout;
async function loadUniversities() {
    clearTimeout(uniSearchTimeout);
    uniSearchTimeout = setTimeout(async () => {
        const params = new URLSearchParams();
        const search = document.getElementById('uniSearch')?.value;
        const region = document.getElementById('uniRegion')?.value;
        const type = document.getElementById('uniType')?.value;
        if (search) params.set('search', search);
        if (region) params.set('region', region);
        if (type) params.set('university_type', type);
        try {
            const res = await fetch(`${API}/api/universities?${params}`);
            const unis = await res.json();
            document.getElementById('uniCount').textContent = `${unis.length} üniversite bulundu`;
            document.getElementById('uniList').innerHTML = unis.map(u => `
                <div class="card-item" onclick="showUniversityDetail(${u.id})">
                    <div class="card-header">
                        <span class="card-icon">🏛️</span>
                        <div class="card-title">${escapeHtml(u.name)}</div>
                    </div>
                    <div class="card-meta">
                        <span>📍 ${escapeHtml(u.city || '')}</span>
                        <span>🌍 ${escapeHtml(u.region || '')}</span>
                        <span>🏢 ${escapeHtml(u.type || '')}</span>
                        ${u.established ? `<span>📅 ${u.established}</span>` : ''}
                        <span>👨‍🏫 ${u.academic_count} akademisyen</span>
                    </div>
                    ${u.website ? `<div class="card-link"><a href="${u.website}" target="_blank" onclick="event.stopPropagation()">🔗 Web Sitesi</a></div>` : ''}
                </div>
            `).join('');
        } catch (err) {
            console.error('Üniversiteler yüklenemedi:', err);
        }
    }, 250);
}

async function showUniversityDetail(id) {
    try {
        const res = await fetch(`${API}/api/universities/${id}`);
        const uni = await res.json();
        document.getElementById('universityDetail').innerHTML = `
            <h2>🏛️ ${escapeHtml(uni.name)}</h2>
            <div class="detail-grid">
                <div class="detail-item"><strong>📍 Şehir:</strong> ${escapeHtml(uni.city || '-')}</div>
                <div class="detail-item"><strong>🌍 Bölge:</strong> ${escapeHtml(uni.region || '-')}</div>
                <div class="detail-item"><strong>🏢 Tür:</strong> ${escapeHtml(uni.type || '-')}</div>
                ${uni.established ? `<div class="detail-item"><strong>📅 Kuruluş:</strong> ${uni.established}</div>` : ''}
                ${uni.website ? `<div class="detail-item"><strong>🔗 Web:</strong> <a href="${uni.website}" target="_blank">${uni.website}</a></div>` : ''}
            </div>
            ${uni.academics.length > 0 ? `
                <h3 style="margin-top:20px;">👨‍🏫 Akademisyenler (${uni.academics.length})</h3>
                <div class="detail-list">
                    ${uni.academics.map(a => `
                        <div class="detail-list-item" onclick="showAcademicDetail(${a.id}); document.getElementById('universityModal').style.display='none';">
                            <strong>${escapeHtml(a.title || '')} ${escapeHtml(a.name)}</strong>
                            <span style="color:var(--text-secondary);font-size:13px;">${escapeHtml(a.department || '')}</span>
                        </div>
                    `).join('')}
                </div>
            ` : '<p style="color:var(--text-secondary);margin-top:16px;">Henüz bu üniversitede kayıtlı akademisyen yok.</p>'}
        `;
        document.getElementById('universityModal').style.display = 'flex';
    } catch (err) {
        console.error('Üniversite detayı yüklenemedi:', err);
    }
}

// ─── Academics ───────────────────────────────────────────────────────────────

let acadSearchTimeout;
async function loadAcademics() {
    clearTimeout(acadSearchTimeout);
    acadSearchTimeout = setTimeout(async () => {
        const params = new URLSearchParams();
        const search = document.getElementById('acadSearch')?.value;
        const title = document.getElementById('acadTitle')?.value;
        if (search) params.set('search', search);
        if (title) params.set('title', title);
        try {
            const res = await fetch(`${API}/api/academics?${params}`);
            const acads = await res.json();
            document.getElementById('acadCount').textContent = `${acads.length} akademisyen bulundu`;
            document.getElementById('acadList').innerHTML = acads.map(a => `
                <div class="card-item" onclick="showAcademicDetail(${a.id})">
                    <div class="card-header">
                        <span class="card-icon">👨‍🏫</span>
                        <div class="card-title">${escapeHtml(a.title || '')} ${escapeHtml(a.name)}</div>
                    </div>
                    <div class="card-meta">
                        <span>🏛️ ${escapeHtml(a.university || 'Bilinmeyen')}</span>
                        <span>🏫 ${escapeHtml(a.department || '')}</span>
                    </div>
                    <div class="card-tags">
                        ${(a.research_areas || '').split(',').map(area => 
                            `<span class="tag">${escapeHtml(area.trim())}</span>`
                        ).join('')}
                    </div>
                </div>
            `).join('');
        } catch (err) {
            console.error('Akademisyenler yüklenemedi:', err);
        }
    }, 250);
}

async function showAcademicDetail(id) {
    try {
        const res = await fetch(`${API}/api/academics/${id}`);
        const a = await res.json();
        document.getElementById('academicDetail').innerHTML = `
            <h2>👨‍🏫 ${escapeHtml(a.title || '')} ${escapeHtml(a.name)}</h2>
            <div class="detail-grid">
                <div class="detail-item"><strong>🏛️ Üniversite:</strong> ${escapeHtml(a.university || '-')}</div>
                <div class="detail-item"><strong>🏫 Fakülte:</strong> ${escapeHtml(a.faculty || '-')}</div>
                <div class="detail-item"><strong>💼 Bölüm:</strong> ${escapeHtml(a.department || '-')}</div>
                ${a.email ? `<div class="detail-item"><strong>📧 E-posta:</strong> ${escapeHtml(a.email)}</div>` : ''}
            </div>
            <div style="margin-top:16px;">
                <strong>🔬 Araştırma Alanları:</strong>
                <div class="card-tags" style="margin-top:8px;">
                    ${(a.research_areas || '').split(',').map(area => 
                        `<span class="tag">${escapeHtml(area.trim())}</span>`
                    ).join('')}
                </div>
            </div>
            ${a.publications && a.publications.length > 0 ? `
                <h3 style="margin-top:20px;">📄 Yayınlar (${a.publications.length})</h3>
                <div class="detail-list">
                    ${a.publications.map(p => `
                        <div class="detail-list-item">
                            <strong>${escapeHtml(p.title)}</strong>
                            <span style="color:var(--text-secondary);font-size:13px;">${escapeHtml(p.journal || '')} ${p.year ? '(' + p.year + ')' : ''}</span>
                        </div>
                    `).join('')}
                </div>
            ` : '<p style="color:var(--text-secondary);margin-top:16px;">Kayıtlı yayın bulunmamaktadır.</p>'}
        `;
        document.getElementById('academicModal').style.display = 'flex';
    } catch (err) {
        console.error('Akademisyen detayı yüklenemedi:', err);
    }
}

// ─── Publications ────────────────────────────────────────────────────────────

let pubSearchTimeout;
async function loadPublications() {
    clearTimeout(pubSearchTimeout);
    pubSearchTimeout = setTimeout(async () => {
        const params = new URLSearchParams();
        const search = document.getElementById('pubSearch')?.value;
        const year = document.getElementById('pubYear')?.value;
        if (search) params.set('search', search);
        if (year) params.set('year', year);
        try {
            const res = await fetch(`${API}/api/publications?${params}`);
            const pubs = await res.json();
            document.getElementById('pubCount').textContent = `${pubs.length} yayın bulundu`;
            document.getElementById('pubList').innerHTML = pubs.map(p => `
                <div class="card-item">
                    <div class="card-header">
                        <span class="card-icon">📄</span>
                        <div class="card-title">${escapeHtml(p.title)}</div>
                    </div>
                    <div class="card-meta">
                        <span>👤 ${escapeHtml(p.authors || 'Bilinmeyen')}</span>
                        <span>📖 ${escapeHtml(p.journal || '')}</span>
                        ${p.year ? `<span>📅 ${p.year}</span>` : ''}
                        ${p.citations ? `<span>📈 ${p.citations} atıf</span>` : ''}
                        <span>🏷️ ${escapeHtml(p.type || 'Makale')}</span>
                    </div>
                    ${p.academic ? `<div style="font-size:13px;color:var(--text-secondary);margin-top:4px;">🏛️ Akademisyen: ${escapeHtml(p.academic)}</div>` : ''}
                </div>
            `).join('');
        } catch (err) {
            console.error('Yayınlar yüklenemedi:', err);
        }
    }, 250);
}

// ─── Init ────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    loadFiles();
});
