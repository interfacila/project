const API = '';
const pages = ['files','ai','knowledge','universities','academics','publications','openalex','stats'];

function switchPage(page) {
    pages.forEach(p => {
        const el = document.getElementById('page-' + p);
        if (el) { el.classList.remove('active-page'); el.style.display = 'none'; }
    });
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
    const target = document.getElementById('page-' + page);
    if (target) { target.style.display = 'block'; target.classList.add('active-page'); }
    const navBtn = document.querySelector(`.nav-item[data-page="${page}"]`);
    if (navBtn) navBtn.classList.add('active');

    if (page === 'universities') loadUniversities();
    else if (page === 'academics') loadAcademics();
    else if (page === 'publications') loadPublications();
    else if (page === 'stats') loadStats();
    else if (page === 'knowledge') loadKnowledge();
}

function toggleSidebar() {
    const sb = document.getElementById('sidebar');
    const mc = document.getElementById('mainContent');
    sb.classList.toggle('collapsed');
    sb.classList.toggle('open');
    mc.classList.toggle('expanded');
}

// ─── Files ──────────────────────────────────────────────────────────────────

async function loadFiles() {
    try {
        const res = await fetch(`${API}/api/files`);
        const files = await res.json();
        renderFiles(files);
        updateStorage(files);
    } catch (err) {
        console.error('Dosyalar yuklenemedi:', err);
    }
}

function renderFiles(files) {
    const container = document.getElementById('filesList');
    const empty = document.getElementById('filesEmpty');
    if (!files.length) {
        container.innerHTML = '';
        if (empty) empty.style.display = 'flex';
        return;
    }
    if (empty) empty.style.display = 'none';
    container.innerHTML = files.map(f => {
        const iconClass = getFileIconClass(f.file_type || '');
        const iconName = getFileIconName(f.file_type || '');
        return `<div class="file-card">
            <div class="file-card-actions">
                <button class="file-action-btn" onclick="event.stopPropagation();downloadFile(${f.id})" title="Indir"><span class="material-icons-outlined">download</span></button>
                <button class="file-action-btn" onclick="event.stopPropagation();askAIAboutFile(${f.id},'${escapeHtml(f.original_filename)}')" title="AI Sor"><span class="material-icons-outlined">smart_toy</span></button>
                <button class="file-action-btn" onclick="event.stopPropagation();deleteFile(${f.id})" title="Sil"><span class="material-icons-outlined">delete</span></button>
            </div>
            <div class="file-card-icon ${iconClass}"><span class="material-icons-outlined">${iconName}</span></div>
            <div class="file-card-name" title="${escapeHtml(f.original_filename)}">${escapeHtml(f.original_filename)}</div>
            <div class="file-card-meta">${formatFileSize(f.file_size)} &middot; ${formatDate(f.created_at)}</div>
        </div>`;
    }).join('');
}

function getFileIconClass(type) {
    if (type.includes('pdf')) return 'pdf';
    if (type.includes('word') || type.includes('document')) return 'doc';
    if (type.includes('image')) return 'img';
    return 'default';
}

function getFileIconName(type) {
    if (type.includes('pdf')) return 'picture_as_pdf';
    if (type.includes('word') || type.includes('document')) return 'description';
    if (type.includes('image')) return 'image';
    if (type.includes('spreadsheet') || type.includes('excel')) return 'table_chart';
    if (type.includes('presentation') || type.includes('powerpoint')) return 'slideshow';
    return 'insert_drive_file';
}

function formatFileSize(bytes) {
    if (!bytes) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    let i = 0;
    while (bytes >= 1024 && i < units.length - 1) { bytes /= 1024; i++; }
    return bytes.toFixed(i ? 1 : 0) + ' ' + units[i];
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', year: 'numeric' });
}

function updateStorage(files) {
    const total = files.reduce((sum, f) => sum + (f.file_size || 0), 0);
    const maxStorage = 1024 * 1024 * 1024;
    const pct = Math.min((total / maxStorage) * 100, 100);
    document.getElementById('storageText').textContent = `${formatFileSize(total)} / 1 GB kullanildi`;
    document.getElementById('storageBar').style.width = pct + '%';
}

async function downloadFile(id) {
    window.open(`${API}/api/files/${id}/download`, '_blank');
}

async function deleteFile(id) {
    if (!confirm('Bu dosyayi silmek istediginize emin misiniz?')) return;
    try {
        await fetch(`${API}/api/files/${id}`, { method: 'DELETE' });
        showToast('Dosya silindi');
        loadFiles();
    } catch (err) {
        showToast('Dosya silinemedi');
    }
}

// Upload Modal
function openUploadModal() {
    document.getElementById('uploadModal').style.display = 'flex';
    document.getElementById('selectedFiles').innerHTML = '';
    document.getElementById('uploadDesc').value = '';
}

function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
}

function handleFileSelect(files) {
    const container = document.getElementById('selectedFiles');
    container.innerHTML = Array.from(files).map(f =>
        `<div class="selected-file"><span class="material-icons-outlined" style="font-size:16px;color:var(--primary)">insert_drive_file</span>${escapeHtml(f.name)} (${formatFileSize(f.size)})</div>`
    ).join('');
}

async function uploadFiles() {
    const input = document.getElementById('fileInput');
    if (!input.files.length) { showToast('Lutfen dosya secin'); return; }
    const btn = document.getElementById('uploadBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Yukleniyor...';
    try {
        for (const file of input.files) {
            const fd = new FormData();
            fd.append('file', file);
            fd.append('description', document.getElementById('uploadDesc').value);
            fd.append('category', document.getElementById('uploadCategory').value);
            await fetch(`${API}/api/files`, { method: 'POST', body: fd });
        }
        showToast(`${input.files.length} dosya yuklendi`);
        closeUploadModal();
        loadFiles();
    } catch (err) {
        showToast('Yukleme hatasi');
    }
    btn.disabled = false;
    btn.innerHTML = '<span class="material-icons-outlined">upload</span> Yukle';
    input.value = '';
}

// Drag & Drop
const dropZone = document.getElementById('dropZone');
if (dropZone) {
    ['dragenter','dragover'].forEach(ev => dropZone.addEventListener(ev, e => { e.preventDefault(); dropZone.style.borderColor = 'var(--primary)'; dropZone.style.background = 'var(--primary-light)'; }));
    ['dragleave','drop'].forEach(ev => dropZone.addEventListener(ev, e => { e.preventDefault(); dropZone.style.borderColor = ''; dropZone.style.background = ''; }));
    dropZone.addEventListener('drop', e => { document.getElementById('fileInput').files = e.dataTransfer.files; handleFileSelect(e.dataTransfer.files); });
}

// ─── AI Chat ────────────────────────────────────────────────────────────────

async function sendAIQuery() {
    const input = document.getElementById('aiInput');
    const query = input.value.trim();
    if (!query) return;
    const messages = document.getElementById('aiMessages');
    messages.innerHTML += `<div class="ai-msg user"><span class="material-icons-outlined msg-avatar">person</span><div class="msg-content">${escapeHtml(query)}</div></div>`;
    input.value = '';
    messages.innerHTML += `<div class="ai-msg assistant" id="aiLoading"><span class="material-icons-outlined msg-avatar">smart_toy</span><div class="msg-content"><span class="spinner"></span> Dusunuyor...</div></div>`;
    messages.scrollTop = messages.scrollHeight;
    try {
        const res = await fetch(`${API}/api/ai/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        const data = await res.json();
        const loading = document.getElementById('aiLoading');
        if (loading) loading.remove();
        messages.innerHTML += `<div class="ai-msg assistant"><span class="material-icons-outlined msg-avatar">smart_toy</span><div class="msg-content">${escapeHtml(data.response_text || data.detail || 'Yanit alinamadi')}</div></div>`;
    } catch (err) {
        const loading = document.getElementById('aiLoading');
        if (loading) loading.remove();
        messages.innerHTML += `<div class="ai-msg assistant"><span class="material-icons-outlined msg-avatar">smart_toy</span><div class="msg-content">Bir hata olustu. Lutfen tekrar deneyin.</div></div>`;
    }
    messages.scrollTop = messages.scrollHeight;
}

function askAIAboutFile(fileId, fileName) {
    switchPage('ai');
    const input = document.getElementById('aiInput');
    input.value = `"${fileName}" dosyasi hakkinda bilgi ver`;
    input.focus();
}

// ─── Knowledge Base ─────────────────────────────────────────────────────────

async function loadKnowledge() {
    try {
        const res = await fetch(`${API}/api/knowledge`);
        const entries = await res.json();
        renderKnowledge(entries);
    } catch (err) {
        console.error('Bilgi tabani yuklenemedi:', err);
    }
}

function renderKnowledge(entries) {
    const container = document.getElementById('kbList');
    if (!entries.length) {
        container.innerHTML = '<div class="empty-state" style="padding:40px"><span class="material-icons-outlined empty-icon">menu_book</span><h3>Henuz bilgi kaydedilmemis</h3></div>';
        return;
    }
    container.innerHTML = entries.map(entry => `
        <div class="kb-card">
            <div class="kb-card-title">${escapeHtml(entry.title)}</div>
            <div class="kb-card-content">${escapeHtml(entry.content)}</div>
            <div class="kb-card-footer">
                <div class="kb-card-meta">
                    <span class="tag">${escapeHtml(entry.category || 'Genel')}</span>
                    ${entry.source ? `<span style="margin-left:8px">${escapeHtml(entry.source)}</span>` : ''}
                </div>
                <button class="btn-danger" onclick="deleteKnowledge(${entry.id})">Sil</button>
            </div>
        </div>
    `).join('');
}

async function addKnowledge() {
    const title = document.getElementById('kbTitle').value.trim();
    const content = document.getElementById('kbContent').value.trim();
    if (!title || !content) { showToast('Baslik ve icerik zorunludur'); return; }
    try {
        await fetch(`${API}/api/knowledge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title, content,
                source: document.getElementById('kbSource').value,
                category: document.getElementById('kbCategory').value
            })
        });
        document.getElementById('kbTitle').value = '';
        document.getElementById('kbContent').value = '';
        document.getElementById('kbSource').value = '';
        showToast('Bilgi eklendi');
        loadKnowledge();
    } catch (err) {
        showToast('Bilgi eklenemedi');
    }
}

async function deleteKnowledge(id) {
    if (!confirm('Bu bilgiyi silmek istediginize emin misiniz?')) return;
    try {
        await fetch(`${API}/api/knowledge/${id}`, { method: 'DELETE' });
        showToast('Bilgi silindi');
        loadKnowledge();
    } catch (err) {
        showToast('Silinemedi');
    }
}

// ─── Universities ───────────────────────────────────────────────────────────

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
            document.getElementById('uniCount').textContent = `${unis.length} universite`;
            document.getElementById('uniList').innerHTML = unis.map(u => `
                <div class="card-item" onclick="showUniversityDetail(${u.id})">
                    <div class="card-header">
                        <div class="card-icon"><span class="material-icons-outlined">account_balance</span></div>
                        <div class="card-title">${escapeHtml(u.name)}</div>
                    </div>
                    <div class="card-meta">
                        <span>${escapeHtml(u.city || '')}</span>
                        <span>${escapeHtml(u.region || '')}</span>
                        <span>${escapeHtml(u.type || '')}</span>
                        ${u.established ? `<span>${u.established}</span>` : ''}
                        ${u.academic_count ? `<span>${u.academic_count} akademisyen</span>` : ''}
                    </div>
                </div>
            `).join('');
        } catch (err) {
            console.error('Universiteler yuklenemedi:', err);
        }
    }, 250);
}

async function showUniversityDetail(id) {
    try {
        const res = await fetch(`${API}/api/universities/${id}`);
        const uni = await res.json();
        document.getElementById('universityDetail').innerHTML = `
            <h3 style="margin-bottom:16px">${escapeHtml(uni.name)}</h3>
            <div class="detail-grid">
                <div class="detail-item"><strong>Sehir</strong>${escapeHtml(uni.city || '-')}</div>
                <div class="detail-item"><strong>Bolge</strong>${escapeHtml(uni.region || '-')}</div>
                <div class="detail-item"><strong>Tur</strong>${escapeHtml(uni.type || '-')}</div>
                ${uni.established ? `<div class="detail-item"><strong>Kurulus</strong>${uni.established}</div>` : ''}
                ${uni.website ? `<div class="detail-item"><strong>Web</strong><a href="${uni.website}" target="_blank">${uni.website}</a></div>` : ''}
            </div>
            ${uni.academics && uni.academics.length > 0 ? `
                <h4 style="margin-top:20px;margin-bottom:8px">Akademisyenler (${uni.academics.length})</h4>
                <div class="detail-list">
                    ${uni.academics.map(a => `<div class="detail-list-item" onclick="showAcademicDetail(${a.id});document.getElementById('universityModal').style.display='none'"><strong>${escapeHtml(a.title || '')} ${escapeHtml(a.name)}</strong><span style="color:var(--text-secondary);font-size:13px">${escapeHtml(a.department || '')}</span></div>`).join('')}
                </div>
            ` : '<p style="color:var(--text-secondary);margin-top:16px">Bu universitede kayitli akademisyen yok.</p>'}
        `;
        document.getElementById('universityModal').style.display = 'flex';
    } catch (err) {
        console.error('Universite detayi yuklenemedi:', err);
    }
}

// ─── Academics ──────────────────────────────────────────────────────────────

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
            document.getElementById('acadCount').textContent = `${acads.length} akademisyen`;
            document.getElementById('acadList').innerHTML = acads.map(a => `
                <div class="card-item" onclick="showAcademicDetail(${a.id})">
                    <div class="card-header">
                        <div class="card-icon"><span class="material-icons-outlined">person</span></div>
                        <div class="card-title">${escapeHtml(a.title || '')} ${escapeHtml(a.name)}</div>
                    </div>
                    <div class="card-meta">
                        <span>${escapeHtml(a.university || '')}</span>
                        <span>${escapeHtml(a.department || '')}</span>
                        ${a.source ? `<span class="tag">${escapeHtml(a.source)}</span>` : ''}
                    </div>
                    <div class="card-tags">
                        ${(a.research_areas || '').split(',').filter(x=>x.trim()).slice(0,4).map(area => `<span class="tag">${escapeHtml(area.trim())}</span>`).join('')}
                    </div>
                </div>
            `).join('');
        } catch (err) {
            console.error('Akademisyenler yuklenemedi:', err);
        }
    }, 250);
}

async function showAcademicDetail(id) {
    try {
        const res = await fetch(`${API}/api/academics/${id}`);
        const a = await res.json();
        document.getElementById('academicDetail').innerHTML = `
            <h3 style="margin-bottom:16px">${escapeHtml(a.title || '')} ${escapeHtml(a.name)}</h3>
            <div class="detail-grid">
                <div class="detail-item"><strong>Universite</strong>${escapeHtml(a.university || '-')}</div>
                <div class="detail-item"><strong>Fakulte</strong>${escapeHtml(a.faculty || '-')}</div>
                <div class="detail-item"><strong>Bolum</strong>${escapeHtml(a.department || '-')}</div>
                ${a.email ? `<div class="detail-item"><strong>E-posta</strong>${escapeHtml(a.email)}</div>` : ''}
            </div>
            <div style="margin-top:16px"><strong style="font-size:13px;color:var(--text-secondary)">Arastirma Alanlari</strong>
                <div class="card-tags" style="margin-top:8px">${(a.research_areas || '').split(',').filter(x=>x.trim()).map(area => `<span class="tag">${escapeHtml(area.trim())}</span>`).join('')}</div>
            </div>
            ${a.publications && a.publications.length > 0 ? `
                <h4 style="margin-top:20px;margin-bottom:8px">Yayinlar (${a.publications.length})</h4>
                <div class="detail-list">
                    ${a.publications.map(p => `<div class="detail-list-item"><strong>${escapeHtml(p.title)}</strong><span style="color:var(--text-secondary);font-size:13px">${escapeHtml(p.journal || '')} ${p.year ? '(' + p.year + ')' : ''}</span></div>`).join('')}
                </div>
            ` : '<p style="color:var(--text-secondary);margin-top:16px">Kayitli yayin yok.</p>'}
        `;
        document.getElementById('academicModal').style.display = 'flex';
    } catch (err) {
        console.error('Akademisyen detayi yuklenemedi:', err);
    }
}

// ─── Publications ───────────────────────────────────────────────────────────

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
            document.getElementById('pubCount').textContent = `${pubs.length} yayin`;
            document.getElementById('pubList').innerHTML = pubs.map(p => `
                <div class="card-item">
                    <div class="card-header">
                        <div class="card-icon"><span class="material-icons-outlined">article</span></div>
                        <div class="card-title">${escapeHtml(p.title)}</div>
                    </div>
                    <div class="card-meta">
                        <span>${escapeHtml(p.authors || '')}</span>
                        <span>${escapeHtml(p.journal || '')}</span>
                        ${p.year ? `<span>${p.year}</span>` : ''}
                        ${p.citations ? `<span>${p.citations} atif</span>` : ''}
                        <span>${escapeHtml(p.type || 'Makale')}</span>
                    </div>
                    ${p.academic ? `<div style="font-size:12px;color:var(--text-secondary);margin-top:4px">Akademisyen: ${escapeHtml(p.academic)}</div>` : ''}
                </div>
            `).join('');
        } catch (err) {
            console.error('Yayinlar yuklenemedi:', err);
        }
    }, 250);
}

// ─── Stats ──────────────────────────────────────────────────────────────────

async function loadStats() {
    try {
        const res = await fetch(`${API}/api/stats`);
        const stats = await res.json();
        document.getElementById('statsGrid').innerHTML = `
            <div class="stat-card"><span class="material-icons-outlined">folder</span><div class="stat-number">${stats.total_files || 0}</div><div class="stat-label">Dosya</div></div>
            <div class="stat-card"><span class="material-icons-outlined">menu_book</span><div class="stat-number">${stats.total_knowledge || 0}</div><div class="stat-label">Bilgi Kaydi</div></div>
            <div class="stat-card"><span class="material-icons-outlined">smart_toy</span><div class="stat-number">${stats.total_queries || 0}</div><div class="stat-label">AI Sorgu</div></div>
            <div class="stat-card"><span class="material-icons-outlined">account_balance</span><div class="stat-number">${stats.total_universities || 0}</div><div class="stat-label">Universite</div></div>
            <div class="stat-card"><span class="material-icons-outlined">person</span><div class="stat-number">${stats.total_academics || 0}</div><div class="stat-label">Akademisyen</div></div>
            <div class="stat-card"><span class="material-icons-outlined">article</span><div class="stat-number">${stats.total_publications || 0}</div><div class="stat-label">Yayin</div></div>
            <div class="stat-card"><span class="material-icons-outlined">people</span><div class="stat-number">${stats.total_users || 0}</div><div class="stat-label">Kullanici</div></div>
        `;
    } catch (err) {
        console.error('Istatistikler yuklenemedi:', err);
    }
}

// ─── OpenAlex ───────────────────────────────────────────────────────────────

async function startSync() {
    const btn = document.getElementById('syncBtn');
    const statusEl = document.getElementById('syncStatus');
    const country = document.getElementById('syncCountry').value || 'TR';
    const search = document.getElementById('syncSearch').value;
    const pages = document.getElementById('syncPages').value || 3;

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Senkronize ediliyor...';
    statusEl.style.display = 'block';
    statusEl.className = 'sync-status syncing';
    statusEl.innerHTML = 'Senkronizasyon baslatildi... Bu islem biraz zaman alabilir.';

    try {
        const params = new URLSearchParams({ country_code: country, max_pages: pages });
        if (search) params.set('search', search);
        await fetch(`${API}/api/openalex/sync?${params}`, { method: 'POST' });
        pollSyncStatus(statusEl, btn);
    } catch (err) {
        statusEl.className = 'sync-status error';
        statusEl.innerHTML = 'Senkronizasyon baslatilamadi: ' + err.message;
        btn.disabled = false;
        btn.innerHTML = '<span class="material-icons-outlined">cloud_download</span> Senkronizasyonu Baslat';
    }
}

async function pollSyncStatus(statusEl, btn) {
    const check = async () => {
        try {
            const res = await fetch(`${API}/api/openalex/sync/status`);
            const data = await res.json();
            if (data.running) {
                statusEl.innerHTML = 'Senkronizasyon devam ediyor...';
                setTimeout(check, 2000);
            } else if (data.error) {
                statusEl.className = 'sync-status error';
                statusEl.innerHTML = 'Hata: ' + data.error;
                btn.disabled = false;
                btn.innerHTML = '<span class="material-icons-outlined">cloud_download</span> Senkronizasyonu Baslat';
            } else if (data.last_result) {
                const r = data.last_result;
                statusEl.className = 'sync-status done';
                statusEl.innerHTML = `Senkronizasyon tamamlandi!<br>
                    Kurumlar: ${r.institutions?.total_saved || 0} kaydedildi (${r.institutions?.total_fetched || 0} cekildi)<br>
                    Yazarlar: ${r.authors?.total_saved || 0} kaydedildi (${r.authors?.total_fetched || 0} cekildi)<br>
                    Yayinlar: ${r.works?.total_saved || 0} kaydedildi (${r.works?.total_fetched || 0} cekildi)`;
                btn.disabled = false;
                btn.innerHTML = '<span class="material-icons-outlined">cloud_download</span> Senkronizasyonu Baslat';
                showToast('OpenAlex senkronizasyonu tamamlandi!');
            } else {
                statusEl.className = 'sync-status done';
                statusEl.innerHTML = 'Senkronizasyon tamamlandi.';
                btn.disabled = false;
                btn.innerHTML = '<span class="material-icons-outlined">cloud_download</span> Senkronizasyonu Baslat';
            }
        } catch (err) {
            setTimeout(check, 3000);
        }
    };
    setTimeout(check, 2000);
}

async function searchOpenAlex() {
    const type = document.getElementById('oaSearchType').value;
    const query = document.getElementById('oaSearchQuery').value.trim();
    if (!query) { showToast('Arama terimi girin'); return; }
    const resultsEl = document.getElementById('oaResults');
    resultsEl.innerHTML = '<div style="text-align:center;padding:20px"><span class="spinner"></span></div>';
    try {
        const res = await fetch(`${API}/api/openalex/search/${type}?query=${encodeURIComponent(query)}`);
        const data = await res.json();
        if (!data.results || !data.results.length) {
            resultsEl.innerHTML = '<p style="color:var(--text-secondary);padding:16px">Sonuc bulunamadi.</p>';
            return;
        }
        resultsEl.innerHTML = `<div style="font-size:12px;color:var(--text-secondary);margin-bottom:8px">${data.total.toLocaleString()} sonuc bulundu</div>` +
            data.results.map(item => {
                if (type === 'works') {
                    return `<div class="oa-result-item"><div class="oa-result-title">${escapeHtml(item.title || '')}</div><div class="oa-result-meta">${escapeHtml(item.authors || '')} | ${escapeHtml(item.journal || '')} ${item.year ? '(' + item.year + ')' : ''} | ${item.citations || 0} atif ${item.open_access ? '| Acik Erisim' : ''}</div></div>`;
                } else if (type === 'authors') {
                    return `<div class="oa-result-item"><div class="oa-result-title">${escapeHtml(item.name || '')}</div><div class="oa-result-meta">${escapeHtml(item.institution || '')} | ${item.works_count || 0} eser | ${item.cited_by_count || 0} atif</div></div>`;
                } else {
                    return `<div class="oa-result-item"><div class="oa-result-title">${escapeHtml(item.name || '')}</div><div class="oa-result-meta">${escapeHtml(item.city || '')} ${escapeHtml(item.country || '')} | ${item.works_count || 0} eser</div></div>`;
                }
            }).join('');
    } catch (err) {
        resultsEl.innerHTML = '<p style="color:var(--danger);padding:16px">Arama hatasi: ' + err.message + '</p>';
    }
}

// ─── Search ─────────────────────────────────────────────────────────────────

let searchTimeout;
function handleSearch(query) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        if (!query.trim()) return;
        // Search across current page or default to files
        const activePage = document.querySelector('.page.active-page');
        if (activePage) {
            const id = activePage.id;
            if (id === 'page-files') loadFiles();
            else if (id === 'page-universities') loadUniversities();
            else if (id === 'page-academics') loadAcademics();
            else if (id === 'page-publications') loadPublications();
        }
    }, 300);
}

// ─── Utilities ──────────────────────────────────────────────────────────────

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function showToast(msg) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ─── Init ───────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    loadFiles();
});
