const API = '';
const pages = ['files','ai','knowledge','universities','academics','publications','openalex','stats'];

// `t(key, vars)` is provided globally by /static/i18n.js. If the script
// failed to load (e.g. offline), fall back to a no-op that returns the key
// so the UI degrades gracefully rather than blowing up.
if (typeof window.t !== 'function') {
    window.t = (key) => key;
}

// Switch UI language at runtime. Called from the header TR/EN buttons.
// Re-renders the currently visible list page so dynamic strings update too.
function switchLanguage(code) {
    if (window.I18N && typeof I18N.setLang === 'function') {
        I18N.setLang(code);
    }
}

// ─── Performance helpers ────────────────────────────────────────────────────
// Default page size — kept aligned with the backend default to keep responses
// small and rendering fast even with large datasets.
const PAGE_SIZE = 50;

// Generic debouncer. Returns a function that delays invocation of `fn` until
// `delay` ms have elapsed since the last call.
function debounce(fn, delay = 300) {
    let t;
    return function debounced(...args) {
        clearTimeout(t);
        t = setTimeout(() => fn.apply(this, args), delay);
    };
}

// Per-loader AbortControllers so a fast-typing user cancels the previous
// in-flight fetch before issuing a new one. This prevents stale (and slow)
// responses from overwriting fresh ones and from competing for main-thread
// time during JSON parsing + render.
const _inFlight = {};
function getAbortSignal(key) {
    if (_inFlight[key]) _inFlight[key].abort();
    const ctrl = new AbortController();
    _inFlight[key] = ctrl;
    return ctrl.signal;
}

// Pagination state for each list view. `total` is the server-reported total
// matching the current filters; `offset` is the next page's offset.
const pageState = {
    universities: { offset: 0, total: 0 },
    academics:    { offset: 0, total: 0 },
    publications: { offset: 0, total: 0 },
    files:        { offset: 0, total: 0 },
    knowledge:    { offset: 0, total: 0 },
};

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

    if (page === 'files') loadFiles();
    else if (page === 'universities') loadUniversities();
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

async function loadFiles({ append = false } = {}) {
    try {
        const searchVal = document.getElementById('searchInput')?.value || '';
        const params = new URLSearchParams();
        if (searchVal.trim()) params.set('search', searchVal.trim());
        if (!append) pageState.files.offset = 0;
        params.set('limit', PAGE_SIZE);
        params.set('offset', pageState.files.offset);
        const signal = getAbortSignal('files');
        const res = await fetch(`${API}/api/files?${params}`, { signal });
        const data = await res.json();
        const items = Array.isArray(data) ? data : (data.items || []);
        const total = Array.isArray(data) ? items.length : (data.total || 0);
        pageState.files.total = total;
        pageState.files.offset += items.length;
        renderFiles(items, { append });
        updateStorage(items);
        renderLoadMore('files', 'filesList', () => loadFiles({ append: true }));
    } catch (err) {
        if (err.name === 'AbortError') return;
        console.error(t('files.load_failed') + ':', err);
    }
}

function renderFiles(files, { append = false } = {}) {
    const container = document.getElementById('filesList');
    const empty = document.getElementById('filesEmpty');
    const html = files.map(f => {
        const iconClass = getFileIconClass(f.file_type || '');
        const iconName = getFileIconName(f.file_type || '');
        return `<div class="file-card">
            <div class="file-card-actions">
                <button class="file-action-btn" onclick="event.stopPropagation();downloadFile(${f.id})" title="${escapeHtml(t('files.download'))}"><span class="material-icons-outlined">download</span></button>
                <button class="file-action-btn" onclick="event.stopPropagation();askAIAboutFile(${f.id},'${escapeHtml(f.original_filename)}')" title="${escapeHtml(t('files.ask_ai'))}"><span class="material-icons-outlined">smart_toy</span></button>
                <button class="file-action-btn" onclick="event.stopPropagation();deleteFile(${f.id})" title="${escapeHtml(t('files.delete'))}"><span class="material-icons-outlined">delete</span></button>
            </div>
            <div class="file-card-icon ${iconClass}"><span class="material-icons-outlined">${iconName}</span></div>
            <div class="file-card-name" title="${escapeHtml(f.original_filename)}">${escapeHtml(f.original_filename)}</div>
            <div class="file-card-meta">${formatFileSize(f.file_size)} &middot; ${formatDate(f.created_at)}</div>
        </div>`;
    }).join('');
    if (append) {
        container.insertAdjacentHTML('beforeend', html);
    } else {
        container.innerHTML = html;
    }
    if (!container.children.length) {
        if (empty) empty.style.display = 'flex';
    } else if (empty) {
        empty.style.display = 'none';
    }
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
    const lang = (window.I18N && I18N.lang && I18N.lang()) || 'tr';
    return d.toLocaleDateString(lang === 'en' ? 'en-US' : 'tr-TR', { day: 'numeric', month: 'short', year: 'numeric' });
}

function updateStorage(files) {
    const total = files.reduce((sum, f) => sum + (f.file_size || 0), 0);
    const maxStorage = 1024 * 1024 * 1024;
    const pct = Math.min((total / maxStorage) * 100, 100);
    document.getElementById('storageText').textContent = t('files.storage_used', { used: formatFileSize(total) });
    document.getElementById('storageBar').style.width = pct + '%';
}

async function downloadFile(id) {
    window.open(`${API}/api/files/${id}/download`, '_blank');
}

async function deleteFile(id) {
    if (!confirm(t('files.delete_confirm'))) return;
    try {
        await fetch(`${API}/api/files/${id}`, { method: 'DELETE' });
        showToast(t('files.deleted'));
        loadFiles();
    } catch (err) {
        showToast(t('files.delete_failed'));
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
    if (!input.files.length) { showToast(t('files.select_first')); return; }
    const btn = document.getElementById('uploadBtn');
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> ${escapeHtml(t('files.uploading'))}`;
    try {
        for (const file of input.files) {
            const fd = new FormData();
            fd.append('file', file);
            fd.append('description', document.getElementById('uploadDesc').value);
            fd.append('category', document.getElementById('uploadCategory').value);
            await fetch(`${API}/api/files`, { method: 'POST', body: fd });
        }
        showToast(t('files.uploaded_n', { count: input.files.length }));
        closeUploadModal();
        loadFiles();
    } catch (err) {
        showToast(t('files.upload_error'));
    }
    btn.disabled = false;
    btn.innerHTML = `<span class="material-icons-outlined">upload</span> ${escapeHtml(t('files.upload'))}`;
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
    messages.innerHTML += `<div class="ai-msg assistant" id="aiLoading"><span class="material-icons-outlined msg-avatar">smart_toy</span><div class="msg-content"><span class="spinner"></span> ${escapeHtml(t('ai.thinking'))}</div></div>`;
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
        messages.innerHTML += `<div class="ai-msg assistant"><span class="material-icons-outlined msg-avatar">smart_toy</span><div class="msg-content">${escapeHtml(data.response_text || data.detail || t('ai.no_response'))}</div></div>`;
    } catch (err) {
        const loading = document.getElementById('aiLoading');
        if (loading) loading.remove();
        messages.innerHTML += `<div class="ai-msg assistant"><span class="material-icons-outlined msg-avatar">smart_toy</span><div class="msg-content">${escapeHtml(t('ai.error_msg'))}</div></div>`;
    }
    messages.scrollTop = messages.scrollHeight;
}

function askAIAboutFile(fileId, fileName) {
    switchPage('ai');
    const input = document.getElementById('aiInput');
    input.value = t('ai.ask_about_file', { name: fileName });
    input.focus();
}

// ─── Knowledge Base ─────────────────────────────────────────────────────────

async function loadKnowledge({ append = false } = {}) {
    try {
        if (!append) pageState.knowledge.offset = 0;
        const params = new URLSearchParams();
        params.set('limit', PAGE_SIZE);
        params.set('offset', pageState.knowledge.offset);
        const signal = getAbortSignal('knowledge');
        const res = await fetch(`${API}/api/knowledge?${params}`, { signal });
        const data = await res.json();
        const items = Array.isArray(data) ? data : (data.items || []);
        const total = Array.isArray(data) ? items.length : (data.total || 0);
        pageState.knowledge.total = total;
        pageState.knowledge.offset += items.length;
        renderKnowledge(items, { append });
        renderLoadMore('knowledge', 'kbList', () => loadKnowledge({ append: true }));
    } catch (err) {
        if (err.name === 'AbortError') return;
        console.error(t('knowledge.load_failed') + ':', err);
    }
}

function renderKnowledge(entries, { append = false } = {}) {
    const container = document.getElementById('kbList');
    const html = entries.map(entry => `
        <div class="kb-card">
            <div class="kb-card-title">${escapeHtml(entry.title)}</div>
            <div class="kb-card-content">${escapeHtml(entry.content)}</div>
            <div class="kb-card-footer">
                <div class="kb-card-meta">
                    <span class="tag">${escapeHtml(t('categories.' + (entry.category || 'Genel')))}</span>
                    ${entry.source ? `<span style="margin-left:8px">${escapeHtml(entry.source)}</span>` : ''}
                </div>
                <button class="btn-danger" onclick="deleteKnowledge(${entry.id})">${escapeHtml(t('knowledge.delete_btn'))}</button>
            </div>
        </div>
    `).join('');
    if (append) {
        container.insertAdjacentHTML('beforeend', html);
    } else if (!entries.length) {
        container.innerHTML = `<div class="empty-state" style="padding:40px"><span class="material-icons-outlined empty-icon">menu_book</span><h3>${escapeHtml(t('knowledge.empty_title'))}</h3></div>`;
    } else {
        container.innerHTML = html;
    }
}

async function addKnowledge() {
    const title = document.getElementById('kbTitle').value.trim();
    const content = document.getElementById('kbContent').value.trim();
    if (!title || !content) { showToast(t('knowledge.title_required')); return; }
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
        showToast(t('knowledge.added'));
        loadKnowledge();
    } catch (err) {
        showToast(t('knowledge.add_failed'));
    }
}

async function deleteKnowledge(id) {
    if (!confirm(t('knowledge.delete_confirm'))) return;
    try {
        await fetch(`${API}/api/knowledge/${id}`, { method: 'DELETE' });
        showToast(t('knowledge.deleted'));
        loadKnowledge();
    } catch (err) {
        showToast(t('knowledge.delete_failed'));
    }
}

// ─── Universities ───────────────────────────────────────────────────────────

async function loadUniversities({ append = false } = {}) {
    const params = new URLSearchParams();
    const search = document.getElementById('uniSearch')?.value;
    const region = document.getElementById('uniRegion')?.value;
    const type = document.getElementById('uniType')?.value;
    if (search) params.set('search', search);
    if (region) params.set('region', region);
    if (type) params.set('university_type', type);
    if (!append) pageState.universities.offset = 0;
    params.set('limit', PAGE_SIZE);
    params.set('offset', pageState.universities.offset);
    try {
        const signal = getAbortSignal('universities');
        const res = await fetch(`${API}/api/universities?${params}`, { signal });
        const data = await res.json();
        const items = Array.isArray(data) ? data : (data.items || []);
        const total = Array.isArray(data) ? items.length : (data.total || 0);
        pageState.universities.total = total;
        pageState.universities.offset += items.length;
        document.getElementById('uniCount').textContent = t('universities.count', { n: total });
        renderUniversities(items, { append });
        renderLoadMore('universities', 'uniList', () => loadUniversities({ append: true }));
    } catch (err) {
        if (err.name === 'AbortError') return;
        console.error(t('universities.load_failed') + ':', err);
    }
}

function renderUniversities(items, { append = false } = {}) {
    const container = document.getElementById('uniList');
    const html = items.map(u => `
        <div class="card-item" onclick="showUniversityDetail(${u.id})">
            <div class="card-header">
                <div class="card-icon"><span class="material-icons-outlined">account_balance</span></div>
                <div class="card-title">${escapeHtml(u.name)}</div>
            </div>
            <div class="card-meta">
                <span>${escapeHtml(u.city || '')}</span>
                <span>${escapeHtml(u.region ? t('regions.' + u.region) : '')}</span>
                <span>${escapeHtml(u.type ? t('uni_types.' + u.type) : '')}</span>
                ${u.established ? `<span>${u.established}</span>` : ''}
                ${u.academic_count ? `<span>${escapeHtml(t('universities.academic_count', { n: u.academic_count }))}</span>` : ''}
            </div>
        </div>
    `).join('');
    if (append) {
        container.insertAdjacentHTML('beforeend', html);
    } else {
        container.innerHTML = html;
    }
}

// Debounced wrappers used by `oninput`/`onchange` handlers in the markup so
// that fast typing only triggers a single network request per pause.
const loadUniversitiesDebounced = debounce(loadUniversities, 350);

async function showUniversityDetail(id) {
    try {
        const res = await fetch(`${API}/api/universities/${id}`);
        const uni = await res.json();
        document.getElementById('universityDetail').innerHTML = `
            <h3 style="margin-bottom:16px">${escapeHtml(uni.name)}</h3>
            <div class="detail-grid">
                <div class="detail-item"><strong>${escapeHtml(t('universities.city'))}</strong>${escapeHtml(uni.city || '-')}</div>
                <div class="detail-item"><strong>${escapeHtml(t('universities.region'))}</strong>${escapeHtml(uni.region ? t('regions.' + uni.region) : '-')}</div>
                <div class="detail-item"><strong>${escapeHtml(t('universities.type'))}</strong>${escapeHtml(uni.type ? t('uni_types.' + uni.type) : '-')}</div>
                ${uni.established ? `<div class="detail-item"><strong>${escapeHtml(t('universities.established'))}</strong>${uni.established}</div>` : ''}
                ${uni.website ? `<div class="detail-item"><strong>${escapeHtml(t('universities.website'))}</strong><a href="${uni.website}" target="_blank">${uni.website}</a></div>` : ''}
            </div>
            ${uni.academics && uni.academics.length > 0 ? `
                <h4 style="margin-top:20px;margin-bottom:8px">${escapeHtml(t('universities.academics_n', { n: uni.academics.length }))}</h4>
                <div class="detail-list">
                    ${uni.academics.map(a => `<div class="detail-list-item" onclick="showAcademicDetail(${a.id});document.getElementById('universityModal').style.display='none'"><strong>${escapeHtml(a.title || '')} ${escapeHtml(a.name)}</strong><span style="color:var(--text-secondary);font-size:13px">${escapeHtml(a.department || '')}</span></div>`).join('')}
                </div>
            ` : `<p style="color:var(--text-secondary);margin-top:16px">${escapeHtml(t('universities.no_academics'))}</p>`}
        `;
        document.getElementById('universityModal').style.display = 'flex';
    } catch (err) {
        console.error(t('universities.detail_load_failed') + ':', err);
    }
}

// ─── Academics ──────────────────────────────────────────────────────────────

async function loadAcademics({ append = false } = {}) {
    const params = new URLSearchParams();
    const search = document.getElementById('acadSearch')?.value;
    const title = document.getElementById('acadTitle')?.value;
    if (search) params.set('search', search);
    if (title) params.set('title', title);
    if (!append) pageState.academics.offset = 0;
    params.set('limit', PAGE_SIZE);
    params.set('offset', pageState.academics.offset);
    try {
        const signal = getAbortSignal('academics');
        const res = await fetch(`${API}/api/academics?${params}`, { signal });
        const data = await res.json();
        const items = Array.isArray(data) ? data : (data.items || []);
        const total = Array.isArray(data) ? items.length : (data.total || 0);
        pageState.academics.total = total;
        pageState.academics.offset += items.length;
        document.getElementById('acadCount').textContent = t('academics.count', { n: total });
        renderAcademics(items, { append });
        renderLoadMore('academics', 'acadList', () => loadAcademics({ append: true }));
    } catch (err) {
        if (err.name === 'AbortError') return;
        console.error(t('academics.load_failed') + ':', err);
    }
}

function renderAcademics(items, { append = false } = {}) {
    const container = document.getElementById('acadList');
    const html = items.map(a => `
        <div class="card-item" onclick="showAcademicDetail(${a.id})">
            <div class="card-header">
                <div class="card-icon"><span class="material-icons-outlined">person</span></div>
                <div class="card-title">${escapeHtml(translateTitle(a.title))} ${escapeHtml(a.name)}</div>
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
    if (append) {
        container.insertAdjacentHTML('beforeend', html);
    } else {
        container.innerHTML = html;
    }
}

const loadAcademicsDebounced = debounce(loadAcademics, 350);

async function showAcademicDetail(id) {
    try {
        const res = await fetch(`${API}/api/academics/${id}`);
        const a = await res.json();
        document.getElementById('academicDetail').innerHTML = `
            <h3 style="margin-bottom:16px">${escapeHtml(translateTitle(a.title))} ${escapeHtml(a.name)}</h3>
            <div class="detail-grid">
                <div class="detail-item"><strong>${escapeHtml(t('academics.university'))}</strong>${escapeHtml(a.university || '-')}</div>
                <div class="detail-item"><strong>${escapeHtml(t('academics.faculty'))}</strong>${escapeHtml(a.faculty || '-')}</div>
                <div class="detail-item"><strong>${escapeHtml(t('academics.department'))}</strong>${escapeHtml(a.department || '-')}</div>
                ${a.email ? `<div class="detail-item"><strong>${escapeHtml(t('academics.email'))}</strong>${escapeHtml(a.email)}</div>` : ''}
            </div>
            <div style="margin-top:16px"><strong style="font-size:13px;color:var(--text-secondary)">${escapeHtml(t('academics.research_areas'))}</strong>
                <div class="card-tags" style="margin-top:8px">${(a.research_areas || '').split(',').filter(x=>x.trim()).map(area => `<span class="tag">${escapeHtml(area.trim())}</span>`).join('')}</div>
            </div>
            ${a.publications && a.publications.length > 0 ? `
                <h4 style="margin-top:20px;margin-bottom:8px">${escapeHtml(t('academics.publications_n', { n: a.publications.length }))}</h4>
                <div class="detail-list">
                    ${a.publications.map(p => `<div class="detail-list-item"><strong>${escapeHtml(p.title)}</strong><span style="color:var(--text-secondary);font-size:13px">${escapeHtml(p.journal || '')} ${p.year ? '(' + p.year + ')' : ''}</span></div>`).join('')}
                </div>
            ` : `<p style="color:var(--text-secondary);margin-top:16px">${escapeHtml(t('academics.no_publications'))}</p>`}
        `;
        document.getElementById('academicModal').style.display = 'flex';
    } catch (err) {
        console.error(t('academics.detail_load_failed') + ':', err);
    }
}

// ─── Publications ───────────────────────────────────────────────────────────

async function loadPublications({ append = false } = {}) {
    const params = new URLSearchParams();
    const search = document.getElementById('pubSearch')?.value;
    const year = document.getElementById('pubYear')?.value;
    if (search) params.set('search', search);
    if (year) params.set('year', year);
    if (!append) pageState.publications.offset = 0;
    params.set('limit', PAGE_SIZE);
    params.set('offset', pageState.publications.offset);
    try {
        const signal = getAbortSignal('publications');
        const res = await fetch(`${API}/api/publications?${params}`, { signal });
        const data = await res.json();
        const items = Array.isArray(data) ? data : (data.items || []);
        const total = Array.isArray(data) ? items.length : (data.total || 0);
        pageState.publications.total = total;
        pageState.publications.offset += items.length;
        document.getElementById('pubCount').textContent = t('publications.count', { n: total });
        renderPublications(items, { append });
        renderLoadMore('publications', 'pubList', () => loadPublications({ append: true }));
    } catch (err) {
        if (err.name === 'AbortError') return;
        console.error(t('publications.load_failed') + ':', err);
    }
}

function renderPublications(items, { append = false } = {}) {
    const container = document.getElementById('pubList');
    const html = items.map(p => `
        <div class="card-item">
            <div class="card-header">
                <div class="card-icon"><span class="material-icons-outlined">article</span></div>
                <div class="card-title">${escapeHtml(p.title)}</div>
            </div>
            <div class="card-meta">
                <span>${escapeHtml(p.authors || '')}</span>
                <span>${escapeHtml(p.journal || '')}</span>
                ${p.year ? `<span>${p.year}</span>` : ''}
                ${p.citations ? `<span>${escapeHtml(t('publications.citations', { n: p.citations }))}</span>` : ''}
                <span>${escapeHtml(p.type || t('publications.default_type'))}</span>
            </div>
            ${p.academic ? `<div style="font-size:12px;color:var(--text-secondary);margin-top:4px">${escapeHtml(t('publications.academic_label', { name: p.academic }))}</div>` : ''}
        </div>
    `).join('');
    if (append) {
        container.insertAdjacentHTML('beforeend', html);
    } else {
        container.innerHTML = html;
    }
}

const loadPublicationsDebounced = debounce(loadPublications, 350);

// ─── Pagination UI ──────────────────────────────────────────────────────────

// Render or remove a "Load more" button below a list. Uses the page state
// for the given key to decide whether more rows are available on the server.
function renderLoadMore(key, containerId, onClick) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const parent = container.parentElement;
    if (!parent) return;
    const existing = parent.querySelector(`[data-load-more="${key}"]`);
    const state = pageState[key] || { offset: 0, total: 0 };
    const hasMore = state.offset < state.total;
    if (!hasMore) {
        if (existing) existing.remove();
        return;
    }
    const remaining = state.total - state.offset;
    if (existing) {
        existing.querySelector('.load-more-label').textContent =
            t('common.load_more', { n: remaining });
        return;
    }
    const btn = document.createElement('button');
    btn.className = 'btn-outlined';
    btn.dataset.loadMore = key;
    btn.style.cssText = 'margin:16px auto;display:block';
    btn.innerHTML = `<span class="material-icons-outlined">expand_more</span> <span class="load-more-label">${escapeHtml(t('common.load_more', { n: remaining }))}</span>`;
    btn.addEventListener('click', () => {
        btn.disabled = true;
        btn.querySelector('.load-more-label').textContent = t('common.loading');
        Promise.resolve(onClick()).finally(() => { btn.disabled = false; });
    });
    container.insertAdjacentElement('afterend', btn);
}

// ─── Stats ──────────────────────────────────────────────────────────────────

async function loadStats() {
    try {
        const res = await fetch(`${API}/api/stats`);
        const stats = await res.json();
        document.getElementById('statsGrid').innerHTML = `
            <div class="stat-card"><span class="material-icons-outlined">folder</span><div class="stat-number">${stats.total_files || 0}</div><div class="stat-label">${escapeHtml(t('stats.files'))}</div></div>
            <div class="stat-card"><span class="material-icons-outlined">menu_book</span><div class="stat-number">${stats.total_knowledge || 0}</div><div class="stat-label">${escapeHtml(t('stats.knowledge'))}</div></div>
            <div class="stat-card"><span class="material-icons-outlined">smart_toy</span><div class="stat-number">${stats.total_queries || 0}</div><div class="stat-label">${escapeHtml(t('stats.ai_queries'))}</div></div>
            <div class="stat-card"><span class="material-icons-outlined">account_balance</span><div class="stat-number">${stats.total_universities || 0}</div><div class="stat-label">${escapeHtml(t('stats.universities'))}</div></div>
            <div class="stat-card"><span class="material-icons-outlined">person</span><div class="stat-number">${stats.total_academics || 0}</div><div class="stat-label">${escapeHtml(t('stats.academics'))}</div></div>
            <div class="stat-card"><span class="material-icons-outlined">article</span><div class="stat-number">${stats.total_publications || 0}</div><div class="stat-label">${escapeHtml(t('stats.publications'))}</div></div>
            <div class="stat-card"><span class="material-icons-outlined">people</span><div class="stat-number">${stats.total_users || 0}</div><div class="stat-label">${escapeHtml(t('stats.users'))}</div></div>
        `;
    } catch (err) {
        console.error(t('stats.load_failed') + ':', err);
    }
}

// ─── OpenAlex ───────────────────────────────────────────────────────────────

async function startSync() {
    const btn = document.getElementById('syncBtn');
    const statusEl = document.getElementById('syncStatus');
    const country = document.getElementById('syncCountry').value || 'TR';
    const search = document.getElementById('syncSearch').value;

    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> ${escapeHtml(t('openalex.syncing'))}`;
    statusEl.style.display = 'block';
    statusEl.className = 'sync-status syncing';
    statusEl.innerHTML = escapeHtml(t('openalex.sync_started'));

    try {
        const params = new URLSearchParams({ country_code: country });
        if (search) params.set('search', search);
        await fetch(`${API}/api/openalex/sync?${params}`, { method: 'POST' });
        pollSyncStatus(statusEl, btn);
    } catch (err) {
        statusEl.className = 'sync-status error';
        statusEl.innerHTML = escapeHtml(t('openalex.sync_failed', { err: err.message }));
        btn.disabled = false;
        btn.innerHTML = `<span class="material-icons-outlined">cloud_download</span> ${escapeHtml(t('openalex.start_sync'))}`;
    }
}

function formatNumber(n) {
    const lang = (window.I18N && I18N.lang && I18N.lang()) || 'tr';
    return (n || 0).toLocaleString(lang === 'en' ? 'en-US' : 'tr-TR');
}

// Translate academic title prefix ("Prof.", "Doc.", "Dr. Ogr.") to current
// locale. Returns the original string if no translation key matches.
function translateTitle(title) {
    if (!title) return '';
    const trimmed = title.trim();
    const known = ['Prof.', 'Doc.', 'Dr. Ogr.'];
    if (known.includes(trimmed)) {
        const translated = t('titles.' + trimmed);
        // If t() returned the key unchanged, fallback to the original.
        return translated && !translated.startsWith('titles.') ? translated : trimmed;
    }
    return trimmed;
}

function buildProgressHTML(data) {
    const phaseLabels = {
        starting: t('openalex.phase_starting'),
        institutions: t('openalex.phase_institutions'),
        authors: t('openalex.phase_authors'),
        works: t('openalex.phase_works'),
        completed: t('openalex.phase_completed'),
        error: t('openalex.phase_error'),
    };
    const phase = data.phase || 'starting';
    const fetched = data.phase_fetched || 0;
    const total = data.phase_total || 0;
    const pct = total > 0 ? Math.min(Math.round((fetched / total) * 100), 100) : 0;
    const prog = data.progress || {};

    let html = `<div style="margin-bottom:8px"><strong>${escapeHtml(phaseLabels[phase] || phase)}</strong>`;
    if (total > 0) html += ` - ${formatNumber(fetched)} / ${formatNumber(total)} (${pct}%)`;
    html += '</div>';
    if (total > 0) html += `<div style="background:#e0e0e0;border-radius:4px;height:6px;margin-bottom:8px"><div style="background:var(--primary);height:100%;border-radius:4px;width:${pct}%;transition:width 0.3s"></div></div>`;

    if (prog.institutions) html += `<div style="font-size:12px">${escapeHtml(t('openalex.progress_uni', { saved: formatNumber(prog.institutions.total_saved), fetched: formatNumber(prog.institutions.total_fetched) }))}</div>`;
    if (prog.authors) html += `<div style="font-size:12px">${escapeHtml(t('openalex.progress_authors', { saved: formatNumber(prog.authors.total_saved), fetched: formatNumber(prog.authors.total_fetched) }))}</div>`;
    if (prog.works) html += `<div style="font-size:12px">${escapeHtml(t('openalex.progress_works', { saved: formatNumber(prog.works.total_saved), fetched: formatNumber(prog.works.total_fetched) }))}</div>`;
    return html;
}

async function pollSyncStatus(statusEl, btn) {
    const check = async () => {
        try {
            const res = await fetch(`${API}/api/openalex/sync/status`);
            const data = await res.json();
            if (data.running) {
                statusEl.innerHTML = buildProgressHTML(data);
                setTimeout(check, 2000);
            } else if (data.error) {
                statusEl.className = 'sync-status error';
                statusEl.innerHTML = escapeHtml(t('openalex.phase_error') + ': ' + data.error);
                if (btn) { btn.disabled = false; btn.innerHTML = `<span class="material-icons-outlined">cloud_download</span> ${escapeHtml(t('openalex.start_sync'))}`; }
            } else if (data.last_result) {
                const r = data.last_result;
                statusEl.className = 'sync-status done';
                statusEl.innerHTML = `${escapeHtml(t('openalex.sync_done'))}<br>
                    ${escapeHtml(t('openalex.saved_summary_uni', { saved: formatNumber(r.institutions?.total_saved), fetched: formatNumber(r.institutions?.total_fetched) }))}<br>
                    ${escapeHtml(t('openalex.saved_summary_authors', { saved: formatNumber(r.authors?.total_saved), fetched: formatNumber(r.authors?.total_fetched) }))}<br>
                    ${escapeHtml(t('openalex.saved_summary_works', { saved: formatNumber(r.works?.total_saved), fetched: formatNumber(r.works?.total_fetched) }))}`;
                if (btn) { btn.disabled = false; btn.innerHTML = `<span class="material-icons-outlined">cloud_download</span> ${escapeHtml(t('openalex.start_sync'))}`; }
                showToast(t('openalex.sync_completed_toast'));
                hideSyncBanner();
            } else {
                statusEl.className = 'sync-status done';
                statusEl.innerHTML = escapeHtml(t('openalex.sync_done_simple'));
                if (btn) { btn.disabled = false; btn.innerHTML = `<span class="material-icons-outlined">cloud_download</span> ${escapeHtml(t('openalex.start_sync'))}`; }
                hideSyncBanner();
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
    if (!query) { showToast(t('openalex.search_term_required')); return; }
    const resultsEl = document.getElementById('oaResults');
    resultsEl.innerHTML = '<div style="text-align:center;padding:20px"><span class="spinner"></span></div>';
    try {
        const res = await fetch(`${API}/api/openalex/search/${type}?query=${encodeURIComponent(query)}`);
        const data = await res.json();
        if (!data.results || !data.results.length) {
            resultsEl.innerHTML = `<p style="color:var(--text-secondary);padding:16px">${escapeHtml(t('openalex.no_results'))}</p>`;
            return;
        }
        resultsEl.innerHTML = `<div style="font-size:12px;color:var(--text-secondary);margin-bottom:8px">${escapeHtml(t('openalex.results_found', { n: formatNumber(data.total) }))}</div>` +
            data.results.map(item => {
                if (type === 'works') {
                    return `<div class="oa-result-item"><div class="oa-result-title">${escapeHtml(item.title || '')}</div><div class="oa-result-meta">${escapeHtml(item.authors || '')} | ${escapeHtml(item.journal || '')} ${item.year ? '(' + item.year + ')' : ''} | ${item.citations || 0} ${escapeHtml(t('openalex.citations_word'))} ${item.open_access ? '| ' + escapeHtml(t('openalex.open_access')) : ''}</div></div>`;
                } else if (type === 'authors') {
                    return `<div class="oa-result-item"><div class="oa-result-title">${escapeHtml(item.name || '')}</div><div class="oa-result-meta">${escapeHtml(item.institution || '')} | ${item.works_count || 0} ${escapeHtml(t('openalex.works_word'))} | ${item.cited_by_count || 0} ${escapeHtml(t('openalex.citations_word'))}</div></div>`;
                } else {
                    return `<div class="oa-result-item"><div class="oa-result-title">${escapeHtml(item.name || '')}</div><div class="oa-result-meta">${escapeHtml(item.city || '')} ${escapeHtml(item.country || '')} | ${item.works_count || 0} ${escapeHtml(t('openalex.works_word'))}</div></div>`;
                }
            }).join('');
    } catch (err) {
        resultsEl.innerHTML = `<p style="color:var(--danger);padding:16px">${escapeHtml(t('openalex.search_error', { err: err.message }))}</p>`;
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
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

function showToast(msg) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ─── Auto-Sync Banner ───────────────────────────────────────────────────────

// ─── Locale change handling ─────────────────────────────────────────────────
// When the user toggles TR/EN, re-render the active list page so dynamic
// strings (counts, button labels, card metadata) update without a reload.
// We also keep the highlighted .lang-btn in sync with the current locale.
function _refreshActivePage() {
    const active = document.querySelector('.page.active-page');
    if (!active) return;
    const id = active.id;
    if (id === 'page-files') loadFiles();
    else if (id === 'page-universities') loadUniversities();
    else if (id === 'page-academics') loadAcademics();
    else if (id === 'page-publications') loadPublications();
    else if (id === 'page-stats') loadStats();
    else if (id === 'page-knowledge') loadKnowledge();
    // Storage label uses formatFileSize; refresh by reloading files when on files page.
}

function _syncLangButtons(code) {
    document.querySelectorAll('#langSwitch .lang-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.lang === code);
    });
}

document.addEventListener('lang-ready', (e) => {
    _syncLangButtons(e.detail?.lang);
});
document.addEventListener('lang-change', (e) => {
    _syncLangButtons(e.detail?.lang);
    _refreshActivePage();
});

function showSyncBanner() {
    let banner = document.getElementById('syncBanner');
    if (!banner) {
        banner = document.createElement('div');
        banner.id = 'syncBanner';
        banner.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:9999;background:linear-gradient(135deg,#1a73e8,#4285f4);color:#fff;padding:12px 24px;font-size:14px;box-shadow:0 2px 8px rgba(0,0,0,.2);display:flex;align-items:center;gap:12px';
        banner.innerHTML = `<span class="spinner" style="border-color:rgba(255,255,255,.3);border-top-color:#fff"></span><div id="syncBannerContent">${escapeHtml(t('common.sync_banner'))}</div><button onclick="hideSyncBanner()" style="background:none;border:none;color:#fff;cursor:pointer;font-size:18px;margin-left:auto">&times;</button>`;
        document.body.prepend(banner);
    }
    banner.style.display = 'flex';
}

function hideSyncBanner() {
    const banner = document.getElementById('syncBanner');
    if (banner) banner.style.display = 'none';
}

function updateSyncBanner(data) {
    const content = document.getElementById('syncBannerContent');
    if (!content) return;
    const phaseLabels = {
        starting: t('openalex.phase_starting'),
        institutions: t('openalex.phase_institutions_loading'),
        authors: t('openalex.phase_authors_loading'),
        works: t('openalex.phase_works_loading'),
        completed: t('openalex.phase_completed_excl'),
    };
    const phase = data.phase || 'starting';
    const fetched = data.phase_fetched || 0;
    const total = data.phase_total || 0;
    let text = phaseLabels[phase] || phase;
    if (total > 0) text += ` (${formatNumber(fetched)} / ${formatNumber(total)})`;
    content.textContent = text;
}

async function checkAutoSync() {
    try {
        const res = await fetch(`${API}/api/openalex/sync/status`);
        const data = await res.json();
        if (data.running) {
            showSyncBanner();
            const poll = async () => {
                try {
                    const r2 = await fetch(`${API}/api/openalex/sync/status`);
                    const d2 = await r2.json();
                    if (d2.running) {
                        updateSyncBanner(d2);
                        setTimeout(poll, 2000);
                    } else {
                        hideSyncBanner();
                        if (d2.last_result) showToast('Veriler yuklendi! Sayfayi yenileyebilirsiniz.');
                    }
                } catch (e) { setTimeout(poll, 3000); }
            };
            setTimeout(poll, 2000);
        }
    } catch (e) { /* ignore */ }
}

// ─── Init ───────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    loadFiles();
    checkAutoSync();
});
