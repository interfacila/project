const API = '';
const pages = ['files','ai','knowledge','universities','academics','publications','openalex','stats'];

// ─── i18n (Multi-language) ──────────────────────────────────────────────────

const translations = {
    tr: {
        // Header & Nav
        searchPlaceholder: 'Dosya, akademisyen veya yayin ara...',
        notifications: 'Bildirimler',
        settings: 'Ayarlar',
        newBtn: 'Yeni',
        myFiles: 'Dosyalarim',
        aiAssistant: 'AI Asistan',
        knowledgeBase: 'Bilgi Tabani',
        academicData: 'Akademik Veri',
        universities: 'Universiteler',
        academics: 'Akademisyenler',
        publications: 'Yayinlar',
        openalexNav: 'Veri Cek',
        openalexTitle: 'OpenAlex',
        stats: 'Istatistikler',
        storageUsed: 'kullanildi',
        // Files
        filesTitle: 'Dosyalarim',
        refresh: 'Yenile',
        upload: 'Yukle',
        noFiles: 'Henuz dosya yok',
        noFilesDesc: 'Dosya yuklemek icin Yukle butonuna tiklayin',
        download: 'Indir',
        aiAsk: 'AI Sor',
        deleteBtn: 'Sil',
        deleteConfirm: 'Bu dosyayi silmek istediginize emin misiniz?',
        fileDeleted: 'Dosya silindi',
        fileDeleteFail: 'Dosya silinemedi',
        uploadModal: 'Dosya Yukle',
        dropText: 'Dosyayi surukleyin veya tiklayin',
        dropHint: 'Tum dosya turleri desteklenir',
        description: 'Aciklama',
        descPlaceholder: 'Dosya aciklamasi (opsiyonel)',
        category: 'Kategori',
        cancel: 'Iptal',
        selectFile: 'Lutfen dosya secin',
        uploading: 'Yukleniyor...',
        filesUploaded: 'dosya yuklendi',
        uploadError: 'Yukleme hatasi',
        // Categories
        catGeneral: 'Genel',
        catAcademic: 'Akademik',
        catResearch: 'Arastirma',
        catNotes: 'Ders Notu',
        catArticle: 'Makale',
        catThesis: 'Tez',
        catReport: 'Rapor',
        catPresentation: 'Sunum',
        catOther: 'Diger',
        // AI
        aiTitle: 'AI Asistan',
        aiDesc: 'Veritabanindaki dosyalar ve bilgi tabani hakkinda sorular sorun.',
        aiWelcome: 'Merhaba! Ben akademik AI asistaniyim. Dosyalariniz ve bilgi tabaniniz hakkinda sorular sorabilirsiniz.',
        aiPlaceholder: 'Bir soru sorun...',
        aiThinking: 'Dusunuyor...',
        aiError: 'Bir hata olustu. Lutfen tekrar deneyin.',
        aiNoResponse: 'Yanit alinamadi',
        aiAboutFile: 'dosyasi hakkinda bilgi ver',
        // Knowledge
        knowledgeTitle: 'Bilgi Tabani',
        addKnowledge: 'Yeni Bilgi Ekle',
        kbTitleLabel: 'Baslik',
        kbTitlePlaceholder: 'Bilgi basligi',
        kbContentLabel: 'Icerik',
        kbContentPlaceholder: 'Bilgi icerigi...',
        kbSource: 'Kaynak',
        kbSourcePlaceholder: 'Kaynak (opsiyonel)',
        kbRequired: 'Baslik ve icerik zorunludur',
        kbAdded: 'Bilgi eklendi',
        kbAddFail: 'Bilgi eklenemedi',
        kbEmpty: 'Henuz bilgi kaydedilmemis',
        kbDeleteConfirm: 'Bu bilgiyi silmek istediginize emin misiniz?',
        kbDeleted: 'Bilgi silindi',
        kbDeleteFail: 'Silinemedi',
        add: 'Ekle',
        // Universities
        uniTitle: 'Universiteler',
        uniSearchPlaceholder: 'Universite ara...',
        allRegions: 'Tum Bolgeler',
        allTypes: 'Tum Turler',
        uniCount: 'universite',
        city: 'Sehir',
        region: 'Bolge',
        type: 'Tur',
        established: 'Kurulus',
        web: 'Web',
        academicsLabel: 'Akademisyenler',
        noAcademics: 'Bu universitede kayitli akademisyen yok.',
        uniDetail: 'Universite Detayi',
        // Academics
        acadTitle: 'Akademisyenler',
        acadSearchPlaceholder: 'Akademisyen, bolum veya arastirma alani ara...',
        allTitles: 'Tum Unvanlar',
        acadCount: 'akademisyen',
        university: 'Universite',
        faculty: 'Fakulte',
        department: 'Bolum',
        email: 'E-posta',
        researchAreas: 'Arastirma Alanlari',
        publicationsLabel: 'Yayinlar',
        noPublications: 'Kayitli yayin yok.',
        loadingPublications: 'OpenAlex\'ten yayinlar yukleniyor...',
        openalexPublications: 'OpenAlex Yayinlari',
        citations: 'atif',
        hIndex: 'H-Index',
        i10Index: 'i10-Index',
        totalCitations: 'Toplam Atif',
        totalWorks: 'Toplam Eser',
        authorMetrics: 'Akademik Metrikler',
        acadDetail: 'Akademisyen Detayi',
        sourceOpenAlex: 'OpenAlex',
        sourceScholar: 'Google Scholar',
        sourceYok: 'YÖK Akademik',
        loadingScholar: 'Google Scholar\'dan veriler yukleniyor...',
        loadingYok: 'YÖK Akademik\'ten veriler yukleniyor...',
        scholarPublications: 'Google Scholar Yayinlari',
        yokPublications: 'YÖK Akademik Yayinlari',
        scholarError: 'Google Scholar verileri alinamadi.',
        yokError: 'YÖK Akademik verileri alinamadi.',
        articleType: 'Makale',
        proceedingType: 'Bildiri',
        bookType: 'Kitap',
        affiliationInfo: 'Kurum Bilgileri',
        fieldLabel: 'Alan',
        subfieldLabel: 'Alt Alan',
        domainLabel: 'Domain',
        countryLabel: 'Ulke',
        affiliationHistory: 'Kurum Gecmisi',
        // Publications
        pubTitle: 'Yayinlar',
        pubSearchPlaceholder: 'Yayin, yazar veya dergi ara...',
        allYears: 'Tum Yillar',
        pubCount: 'yayin',
        academicLabel: 'Akademisyen',
        // OpenAlex
        openalexDataTitle: 'OpenAlex Veri Cekme',
        autoSync: 'Otomatik Senkronizasyon',
        autoSyncDesc: 'OpenAlex\'ten universite, akademisyen ve yayin verilerini otomatik olarak cekin.',
        countryCode: 'Ulke Kodu',
        searchOptional: 'Arama (opsiyonel)',
        keyword: 'Anahtar kelime',
        startSync: 'Senkronizasyonu Baslat',
        syncStarted: 'Senkronizasyon baslatildi... Tum veriler cekilecek, bu islem uzun surebilir.',
        syncFailed: 'Senkronizasyon baslatilamadi: ',
        syncRunning: 'Senkronize ediliyor...',
        syncCompleted: 'Senkronizasyon tamamlandi!',
        liveSearch: 'OpenAlex Canli Arama',
        liveSearchDesc: 'OpenAlex veritabaninda canli arama yapin.',
        worksOption: 'Yayinlar',
        authorsOption: 'Yazarlar',
        institutionsOption: 'Kurumlar',
        searchTermPlaceholder: 'Arama terimi girin...',
        search: 'Ara',
        enterSearchTerm: 'Arama terimi girin',
        noResults: 'Sonuc bulunamadi.',
        resultsFound: 'sonuc bulundu',
        searchError: 'Arama hatasi: ',
        saved: 'kaydedildi',
        fetched: 'cekildi',
        openAccess: 'Acik Erisim',
        works: 'eser',
        // Stats
        statsTitle: 'Istatistikler',
        statFiles: 'Dosya',
        statKnowledge: 'Bilgi Kaydi',
        statQueries: 'AI Sorgu',
        statUni: 'Universite',
        statAcademic: 'Akademisyen',
        statPub: 'Yayin',
        statUsers: 'Kullanici',
        // Sync phases
        phaseStarting: 'Baslatiliyor...',
        phaseInstitutions: 'Universiteler',
        phaseAuthors: 'Akademisyenler',
        phaseWorks: 'Yayinlar',
        phaseCompleted: 'Tamamlandi',
        phaseError: 'Hata',
        // Sync banner
        bannerLoading: 'Turkiye akademik verileri yukleniyor...',
        bannerInstLoading: 'Universiteler yukleniyor',
        bannerAuthLoading: 'Akademisyenler yukleniyor',
        bannerWorksLoading: 'Yayinlar yukleniyor',
        bannerCompleted: 'Tamamlandi!',
        dataLoaded: 'Veriler yuklendi! Sayfayi yenileyebilirsiniz.',
        syncDone: 'OpenAlex senkronizasyonu tamamlandi!',
    },
    en: {
        searchPlaceholder: 'Search files, academics or publications...',
        notifications: 'Notifications',
        settings: 'Settings',
        newBtn: 'New',
        myFiles: 'My Files',
        aiAssistant: 'AI Assistant',
        knowledgeBase: 'Knowledge Base',
        academicData: 'Academic Data',
        universities: 'Universities',
        academics: 'Academics',
        publications: 'Publications',
        openalexNav: 'Fetch Data',
        openalexTitle: 'OpenAlex',
        stats: 'Statistics',
        storageUsed: 'used',
        filesTitle: 'My Files',
        refresh: 'Refresh',
        upload: 'Upload',
        noFiles: 'No files yet',
        noFilesDesc: 'Click Upload button to upload files',
        download: 'Download',
        aiAsk: 'Ask AI',
        deleteBtn: 'Delete',
        deleteConfirm: 'Are you sure you want to delete this file?',
        fileDeleted: 'File deleted',
        fileDeleteFail: 'Could not delete file',
        uploadModal: 'Upload File',
        dropText: 'Drag files here or click',
        dropHint: 'All file types are supported',
        description: 'Description',
        descPlaceholder: 'File description (optional)',
        category: 'Category',
        cancel: 'Cancel',
        selectFile: 'Please select a file',
        uploading: 'Uploading...',
        filesUploaded: 'file(s) uploaded',
        uploadError: 'Upload error',
        catGeneral: 'General',
        catAcademic: 'Academic',
        catResearch: 'Research',
        catNotes: 'Lecture Notes',
        catArticle: 'Article',
        catThesis: 'Thesis',
        catReport: 'Report',
        catPresentation: 'Presentation',
        catOther: 'Other',
        aiTitle: 'AI Assistant',
        aiDesc: 'Ask questions about files and knowledge base in the database.',
        aiWelcome: 'Hello! I am the academic AI assistant. You can ask questions about your files and knowledge base.',
        aiPlaceholder: 'Ask a question...',
        aiThinking: 'Thinking...',
        aiError: 'An error occurred. Please try again.',
        aiNoResponse: 'No response received',
        aiAboutFile: 'Give information about the file',
        knowledgeTitle: 'Knowledge Base',
        addKnowledge: 'Add New Knowledge',
        kbTitleLabel: 'Title',
        kbTitlePlaceholder: 'Knowledge title',
        kbContentLabel: 'Content',
        kbContentPlaceholder: 'Knowledge content...',
        kbSource: 'Source',
        kbSourcePlaceholder: 'Source (optional)',
        kbRequired: 'Title and content are required',
        kbAdded: 'Knowledge added',
        kbAddFail: 'Could not add knowledge',
        kbEmpty: 'No knowledge recorded yet',
        kbDeleteConfirm: 'Are you sure you want to delete this knowledge?',
        kbDeleted: 'Knowledge deleted',
        kbDeleteFail: 'Could not delete',
        add: 'Add',
        uniTitle: 'Universities',
        uniSearchPlaceholder: 'Search universities...',
        allRegions: 'All Regions',
        allTypes: 'All Types',
        uniCount: 'universities',
        city: 'City',
        region: 'Region',
        type: 'Type',
        established: 'Established',
        web: 'Web',
        academicsLabel: 'Academics',
        noAcademics: 'No registered academics at this university.',
        uniDetail: 'University Detail',
        acadTitle: 'Academics',
        acadSearchPlaceholder: 'Search academic, department or research area...',
        allTitles: 'All Titles',
        acadCount: 'academics',
        university: 'University',
        faculty: 'Faculty',
        department: 'Department',
        email: 'Email',
        researchAreas: 'Research Areas',
        publicationsLabel: 'Publications',
        noPublications: 'No registered publications.',
        loadingPublications: 'Loading publications from OpenAlex...',
        openalexPublications: 'OpenAlex Publications',
        citations: 'citations',
        hIndex: 'H-Index',
        i10Index: 'i10-Index',
        totalCitations: 'Total Citations',
        totalWorks: 'Total Works',
        authorMetrics: 'Academic Metrics',
        acadDetail: 'Academic Detail',
        sourceOpenAlex: 'OpenAlex',
        sourceScholar: 'Google Scholar',
        sourceYok: 'YÖK Academic',
        loadingScholar: 'Loading data from Google Scholar...',
        loadingYok: 'Loading data from YÖK Academic...',
        scholarPublications: 'Google Scholar Publications',
        yokPublications: 'YÖK Academic Publications',
        scholarError: 'Could not fetch Google Scholar data.',
        yokError: 'Could not fetch YÖK Academic data.',
        articleType: 'Article',
        proceedingType: 'Proceeding',
        bookType: 'Book',
        affiliationInfo: 'Affiliation Info',
        fieldLabel: 'Field',
        subfieldLabel: 'Subfield',
        domainLabel: 'Domain',
        countryLabel: 'Country',
        affiliationHistory: 'Affiliation History',
        pubTitle: 'Publications',
        pubSearchPlaceholder: 'Search publication, author or journal...',
        allYears: 'All Years',
        pubCount: 'publications',
        academicLabel: 'Academic',
        openalexDataTitle: 'OpenAlex Data Fetch',
        autoSync: 'Auto Sync',
        autoSyncDesc: 'Automatically fetch university, academic and publication data from OpenAlex.',
        countryCode: 'Country Code',
        searchOptional: 'Search (optional)',
        keyword: 'Keyword',
        startSync: 'Start Sync',
        syncStarted: 'Sync started... All data will be fetched, this may take a while.',
        syncFailed: 'Sync could not be started: ',
        syncRunning: 'Syncing...',
        syncCompleted: 'Sync completed!',
        liveSearch: 'OpenAlex Live Search',
        liveSearchDesc: 'Search the OpenAlex database live.',
        worksOption: 'Publications',
        authorsOption: 'Authors',
        institutionsOption: 'Institutions',
        searchTermPlaceholder: 'Enter search term...',
        search: 'Search',
        enterSearchTerm: 'Enter a search term',
        noResults: 'No results found.',
        resultsFound: 'results found',
        searchError: 'Search error: ',
        saved: 'saved',
        fetched: 'fetched',
        openAccess: 'Open Access',
        works: 'works',
        statsTitle: 'Statistics',
        statFiles: 'Files',
        statKnowledge: 'Knowledge Records',
        statQueries: 'AI Queries',
        statUni: 'Universities',
        statAcademic: 'Academics',
        statPub: 'Publications',
        statUsers: 'Users',
        phaseStarting: 'Starting...',
        phaseInstitutions: 'Universities',
        phaseAuthors: 'Academics',
        phaseWorks: 'Publications',
        phaseCompleted: 'Completed',
        phaseError: 'Error',
        bannerLoading: 'Loading Turkey academic data...',
        bannerInstLoading: 'Loading universities',
        bannerAuthLoading: 'Loading academics',
        bannerWorksLoading: 'Loading publications',
        bannerCompleted: 'Completed!',
        dataLoaded: 'Data loaded! You can refresh the page.',
        syncDone: 'OpenAlex sync completed!',
    }
};

let currentLang = localStorage.getItem('lang') || 'tr';

function t(key) {
    return (translations[currentLang] && translations[currentLang][key]) || translations.tr[key] || key;
}

function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    applyTranslations();
    const activePage = document.querySelector('.page.active-page');
    if (activePage) {
        const id = activePage.id.replace('page-', '');
        if (id === 'files') loadFiles();
        else if (id === 'universities') loadUniversities();
        else if (id === 'academics') loadAcademics();
        else if (id === 'publications') loadPublications();
        else if (id === 'stats') loadStats();
        else if (id === 'knowledge') loadKnowledge();
    }
}

function applyTranslations() {
    // Header
    const searchInput = document.getElementById('searchInput');
    if (searchInput) searchInput.placeholder = t('searchPlaceholder');

    // Language toggle button text
    const langBtn = document.getElementById('langToggleBtn');
    if (langBtn) langBtn.textContent = currentLang === 'tr' ? 'EN' : 'TR';

    // Sidebar
    const sidebarNew = document.querySelector('.sidebar-new-btn');
    if (sidebarNew) sidebarNew.innerHTML = `<span class="material-icons-outlined">add</span> ${t('newBtn')}`;

    document.querySelectorAll('.nav-item[data-page]').forEach(btn => {
        const page = btn.dataset.page;
        const iconEl = btn.querySelector('.material-icons-outlined');
        const icon = iconEl ? iconEl.outerHTML : '';
        const map = {
            files: 'myFiles', ai: 'aiAssistant', knowledge: 'knowledgeBase',
            universities: 'universities', academics: 'academics',
            publications: 'publications', openalex: 'openalexNav', stats: 'stats'
        };
        if (map[page]) btn.innerHTML = `${icon} ${t(map[page])}`;
    });

    const acadDataTitle = document.querySelector('.nav-section-title');
    if (acadDataTitle) acadDataTitle.textContent = t('academicData');

    const sectionTitles = document.querySelectorAll('.nav-section-title');
    if (sectionTitles[0]) sectionTitles[0].textContent = t('academicData');
    if (sectionTitles[1]) sectionTitles[1].textContent = t('openalexTitle');

    // Page headers
    const pageHeaders = {
        'page-files': 'filesTitle',
        'page-universities': 'uniTitle',
        'page-academics': 'acadTitle',
        'page-publications': 'pubTitle',
        'page-stats': 'statsTitle',
        'page-knowledge': 'knowledgeTitle',
        'page-openalex': 'openalexDataTitle',
    };
    for (const [pageId, key] of Object.entries(pageHeaders)) {
        const el = document.querySelector(`#${pageId} .page-header h1`);
        if (el) el.textContent = t(key);
    }

    // Files page buttons
    const refreshBtn = document.querySelector('#page-files .btn-outlined');
    if (refreshBtn) refreshBtn.innerHTML = `<span class="material-icons-outlined">refresh</span> ${t('refresh')}`;
    const uploadBtn = document.querySelector('#page-files .btn-primary');
    if (uploadBtn) uploadBtn.innerHTML = `<span class="material-icons-outlined">upload_file</span> ${t('upload')}`;

    // Empty state
    const emptyH3 = document.querySelector('#filesEmpty h3');
    if (emptyH3) emptyH3.textContent = t('noFiles');
    const emptyP = document.querySelector('#filesEmpty p');
    if (emptyP) emptyP.textContent = t('noFilesDesc');

    // AI page
    const aiH2 = document.querySelector('.ai-header h2');
    if (aiH2) aiH2.textContent = t('aiTitle');
    const aiP = document.querySelector('.ai-header p');
    if (aiP) aiP.textContent = t('aiDesc');
    const aiInput = document.getElementById('aiInput');
    if (aiInput) aiInput.placeholder = t('aiPlaceholder');

    // Knowledge page
    const kbFormH3 = document.querySelector('.kb-form-card h3');
    if (kbFormH3) kbFormH3.textContent = t('addKnowledge');

    // Filter placeholders
    const uniSearch = document.getElementById('uniSearch');
    if (uniSearch) uniSearch.placeholder = t('uniSearchPlaceholder');
    const acadSearch = document.getElementById('acadSearch');
    if (acadSearch) acadSearch.placeholder = t('acadSearchPlaceholder');
    const pubSearch = document.getElementById('pubSearch');
    if (pubSearch) pubSearch.placeholder = t('pubSearchPlaceholder');

    // Upload modal
    const uploadModalH2 = document.querySelector('#uploadModal .modal-header h2');
    if (uploadModalH2) uploadModalH2.textContent = t('uploadModal');
    const dropZoneP = document.querySelector('.drop-zone p');
    if (dropZoneP) dropZoneP.textContent = t('dropText');
    const dropHint = document.querySelector('.drop-hint');
    if (dropHint) dropHint.textContent = t('dropHint');

    // Modal titles
    const uniModalH2 = document.querySelector('#universityModal .modal-header h2');
    if (uniModalH2) uniModalH2.textContent = t('uniDetail');
    const acadModalH2 = document.querySelector('#academicModal .modal-header h2');
    if (acadModalH2) acadModalH2.textContent = t('acadDetail');

    // OpenAlex page
    const syncH3 = document.querySelector('.sync-card .panel-card-header h3');
    if (syncH3) syncH3.textContent = t('autoSync');
    const syncDesc = document.querySelector('.sync-card .panel-desc');
    if (syncDesc) syncDesc.textContent = t('autoSyncDesc');
    const searchH3 = document.querySelector('.search-card .panel-card-header h3');
    if (searchH3) searchH3.textContent = t('liveSearch');
    const searchDesc = document.querySelector('.search-card .panel-desc');
    if (searchDesc) searchDesc.textContent = t('liveSearchDesc');

    const oaSearchQuery = document.getElementById('oaSearchQuery');
    if (oaSearchQuery) oaSearchQuery.placeholder = t('searchTermPlaceholder');

    // Select options for OpenAlex search type
    const oaSearchType = document.getElementById('oaSearchType');
    if (oaSearchType) {
        oaSearchType.options[0].text = t('worksOption');
        oaSearchType.options[1].text = t('authorsOption');
        oaSearchType.options[2].text = t('institutionsOption');
    }

    // Filter selects
    const uniRegion = document.getElementById('uniRegion');
    if (uniRegion && uniRegion.options[0]) uniRegion.options[0].text = t('allRegions');
    const uniType = document.getElementById('uniType');
    if (uniType && uniType.options[0]) uniType.options[0].text = t('allTypes');
    const acadTitleSelect = document.getElementById('acadTitle');
    if (acadTitleSelect && acadTitleSelect.options[0]) acadTitleSelect.options[0].text = t('allTitles');
    const pubYear = document.getElementById('pubYear');
    if (pubYear && pubYear.options[0]) pubYear.options[0].text = t('allYears');

    // Sync button
    const syncBtn = document.getElementById('syncBtn');
    if (syncBtn && !syncBtn.disabled) {
        syncBtn.innerHTML = `<span class="material-icons-outlined">cloud_download</span> ${t('startSync')}`;
    }
}

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

async function loadFiles() {
    try {
        const searchVal = document.getElementById('searchInput')?.value || '';
        const params = new URLSearchParams();
        if (searchVal.trim()) params.set('search', searchVal.trim());
        const res = await fetch(`${API}/api/files?${params}`);
        const files = await res.json();
        renderFiles(files);
        updateStorage(files);
    } catch (err) {
        console.error('Files load error:', err);
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
                <button class="file-action-btn" onclick="event.stopPropagation();downloadFile(${f.id})" title="${t('download')}"><span class="material-icons-outlined">download</span></button>
                <button class="file-action-btn" onclick="event.stopPropagation();askAIAboutFile(${f.id},'${escapeHtml(f.original_filename)}')" title="${t('aiAsk')}"><span class="material-icons-outlined">smart_toy</span></button>
                <button class="file-action-btn" onclick="event.stopPropagation();deleteFile(${f.id})" title="${t('deleteBtn')}"><span class="material-icons-outlined">delete</span></button>
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
    const locale = currentLang === 'tr' ? 'tr-TR' : 'en-US';
    return d.toLocaleDateString(locale, { day: 'numeric', month: 'short', year: 'numeric' });
}

function updateStorage(files) {
    const total = files.reduce((sum, f) => sum + (f.file_size || 0), 0);
    const maxStorage = 1024 * 1024 * 1024;
    const pct = Math.min((total / maxStorage) * 100, 100);
    document.getElementById('storageText').textContent = `${formatFileSize(total)} / 1 GB ${t('storageUsed')}`;
    document.getElementById('storageBar').style.width = pct + '%';
}

async function downloadFile(id) {
    window.open(`${API}/api/files/${id}/download`, '_blank');
}

async function deleteFile(id) {
    if (!confirm(t('deleteConfirm'))) return;
    try {
        await fetch(`${API}/api/files/${id}`, { method: 'DELETE' });
        showToast(t('fileDeleted'));
        loadFiles();
    } catch (err) {
        showToast(t('fileDeleteFail'));
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
    if (!input.files.length) { showToast(t('selectFile')); return; }
    const btn = document.getElementById('uploadBtn');
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> ${t('uploading')}`;
    try {
        for (const file of input.files) {
            const fd = new FormData();
            fd.append('file', file);
            fd.append('description', document.getElementById('uploadDesc').value);
            fd.append('category', document.getElementById('uploadCategory').value);
            await fetch(`${API}/api/files`, { method: 'POST', body: fd });
        }
        showToast(`${input.files.length} ${t('filesUploaded')}`);
        closeUploadModal();
        loadFiles();
    } catch (err) {
        showToast(t('uploadError'));
    }
    btn.disabled = false;
    btn.innerHTML = `<span class="material-icons-outlined">upload</span> ${t('upload')}`;
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
    messages.innerHTML += `<div class="ai-msg assistant" id="aiLoading"><span class="material-icons-outlined msg-avatar">smart_toy</span><div class="msg-content"><span class="spinner"></span> ${t('aiThinking')}</div></div>`;
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
        messages.innerHTML += `<div class="ai-msg assistant"><span class="material-icons-outlined msg-avatar">smart_toy</span><div class="msg-content">${escapeHtml(data.response_text || data.detail || t('aiNoResponse'))}</div></div>`;
    } catch (err) {
        const loading = document.getElementById('aiLoading');
        if (loading) loading.remove();
        messages.innerHTML += `<div class="ai-msg assistant"><span class="material-icons-outlined msg-avatar">smart_toy</span><div class="msg-content">${t('aiError')}</div></div>`;
    }
    messages.scrollTop = messages.scrollHeight;
}

function askAIAboutFile(fileId, fileName) {
    switchPage('ai');
    const input = document.getElementById('aiInput');
    input.value = `"${fileName}" ${t('aiAboutFile')}`;
    input.focus();
}

// ─── Knowledge Base ─────────────────────────────────────────────────────────

async function loadKnowledge() {
    try {
        const res = await fetch(`${API}/api/knowledge`);
        const entries = await res.json();
        renderKnowledge(entries);
    } catch (err) {
        console.error('Knowledge load error:', err);
    }
}

function renderKnowledge(entries) {
    const container = document.getElementById('kbList');
    if (!entries.length) {
        container.innerHTML = `<div class="empty-state" style="padding:40px"><span class="material-icons-outlined empty-icon">menu_book</span><h3>${t('kbEmpty')}</h3></div>`;
        return;
    }
    container.innerHTML = entries.map(entry => `
        <div class="kb-card">
            <div class="kb-card-title">${escapeHtml(entry.title)}</div>
            <div class="kb-card-content">${escapeHtml(entry.content)}</div>
            <div class="kb-card-footer">
                <div class="kb-card-meta">
                    <span class="tag">${escapeHtml(entry.category || t('catGeneral'))}</span>
                    ${entry.source ? `<span style="margin-left:8px">${escapeHtml(entry.source)}</span>` : ''}
                </div>
                <button class="btn-danger" onclick="deleteKnowledge(${entry.id})">${t('deleteBtn')}</button>
            </div>
        </div>
    `).join('');
}

async function addKnowledge() {
    const title = document.getElementById('kbTitle').value.trim();
    const content = document.getElementById('kbContent').value.trim();
    if (!title || !content) { showToast(t('kbRequired')); return; }
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
        showToast(t('kbAdded'));
        loadKnowledge();
    } catch (err) {
        showToast(t('kbAddFail'));
    }
}

async function deleteKnowledge(id) {
    if (!confirm(t('kbDeleteConfirm'))) return;
    try {
        await fetch(`${API}/api/knowledge/${id}`, { method: 'DELETE' });
        showToast(t('kbDeleted'));
        loadKnowledge();
    } catch (err) {
        showToast(t('kbDeleteFail'));
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
            document.getElementById('uniCount').textContent = `${unis.length} ${t('uniCount')}`;
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
                        ${u.academic_count ? `<span>${u.academic_count} ${t('acadCount')}</span>` : ''}
                    </div>
                </div>
            `).join('');
        } catch (err) {
            console.error('Universities load error:', err);
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
                <div class="detail-item"><strong>${t('city')}</strong>${escapeHtml(uni.city || '-')}</div>
                <div class="detail-item"><strong>${t('region')}</strong>${escapeHtml(uni.region || '-')}</div>
                <div class="detail-item"><strong>${t('type')}</strong>${escapeHtml(uni.type || '-')}</div>
                ${uni.established ? `<div class="detail-item"><strong>${t('established')}</strong>${uni.established}</div>` : ''}
                ${uni.website ? `<div class="detail-item"><strong>${t('web')}</strong><a href="${uni.website}" target="_blank">${uni.website}</a></div>` : ''}
            </div>
            ${uni.academics && uni.academics.length > 0 ? `
                <h4 style="margin-top:20px;margin-bottom:8px">${t('academicsLabel')} (${uni.academics.length})</h4>
                <div class="detail-list">
                    ${uni.academics.map(a => `<div class="detail-list-item" onclick="showAcademicDetail(${a.id});document.getElementById('universityModal').style.display='none'"><strong>${escapeHtml(a.title || '')} ${escapeHtml(a.name)}</strong><span style="color:var(--text-secondary);font-size:13px">${escapeHtml(a.department || '')}</span></div>`).join('')}
                </div>
            ` : `<p style="color:var(--text-secondary);margin-top:16px">${t('noAcademics')}</p>`}
        `;
        document.getElementById('universityModal').style.display = 'flex';
    } catch (err) {
        console.error('University detail error:', err);
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
            document.getElementById('acadCount').textContent = `${acads.length} ${t('acadCount')}`;
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
            console.error('Academics load error:', err);
        }
    }, 250);
}

async function showAcademicDetail(id) {
    try {
        const res = await fetch(`${API}/api/academics/${id}`);
        const a = await res.json();

        const hasDbPubs = a.publications && a.publications.length > 0;
        let dbPubsHtml = '';
        if (hasDbPubs) {
            dbPubsHtml = `
                <h4 style="margin-top:12px;margin-bottom:8px">${t('publicationsLabel')} (${a.publications.length})</h4>
                <div class="detail-list">
                    ${a.publications.map(p => `<div class="detail-list-item"><strong>${escapeHtml(p.title)}</strong><span style="color:var(--text-secondary);font-size:13px">${escapeHtml(p.journal || '')} ${p.year ? '(' + p.year + ')' : ''}</span></div>`).join('')}
                </div>
            `;
        }

        const spinnerHtml = '<span class="spinner" style="width:14px;height:14px;border-width:2px;vertical-align:middle;margin-right:8px"></span>';

        document.getElementById('academicDetail').innerHTML = `
            <h3 style="margin-bottom:16px">${escapeHtml(a.title || '')} ${escapeHtml(a.name)}</h3>
            <div class="detail-grid">
                <div class="detail-item"><strong>${t('university')}</strong>${escapeHtml(a.university || '-')}</div>
                <div class="detail-item"><strong>${t('faculty')}</strong>${escapeHtml(a.faculty || '-')}</div>
                <div class="detail-item"><strong>${t('department')}</strong>${escapeHtml(a.department || '-')}</div>
                ${a.email ? `<div class="detail-item"><strong>${t('email')}</strong>${escapeHtml(a.email)}</div>` : ''}
            </div>
            <div style="margin-top:16px"><strong style="font-size:13px;color:var(--text-secondary)">${t('researchAreas')}</strong>
                <div class="card-tags" style="margin-top:8px">${(a.research_areas || '').split(',').filter(x=>x.trim()).map(area => `<span class="tag">${escapeHtml(area.trim())}</span>`).join('')}</div>
            </div>
            <div id="openalex-metrics-${id}" style="margin-top:16px"></div>
            ${dbPubsHtml}
            <div style="margin-top:20px">
                <div class="source-tabs" style="display:flex;gap:0;border-bottom:2px solid var(--border);margin-bottom:16px">
                    <button class="source-tab active" onclick="switchSourceTab(${id},'openalex')" id="tab-openalex-${id}" style="padding:8px 16px;border:none;background:none;cursor:pointer;font-size:13px;font-weight:600;color:var(--primary);border-bottom:2px solid var(--primary);margin-bottom:-2px">${t('sourceOpenAlex')}</button>
                    <button class="source-tab" onclick="switchSourceTab(${id},'scholar')" id="tab-scholar-${id}" style="padding:8px 16px;border:none;background:none;cursor:pointer;font-size:13px;font-weight:500;color:var(--text-secondary);border-bottom:2px solid transparent;margin-bottom:-2px">${t('sourceScholar')}</button>
                    <button class="source-tab" onclick="switchSourceTab(${id},'yok')" id="tab-yok-${id}" style="padding:8px 16px;border:none;background:none;cursor:pointer;font-size:13px;font-weight:500;color:var(--text-secondary);border-bottom:2px solid transparent;margin-bottom:-2px">${t('sourceYok')}</button>
                </div>
                <div id="source-openalex-${id}" style="display:block">
                    <p style="color:var(--text-secondary)">${spinnerHtml}${t('loadingPublications')}</p>
                </div>
                <div id="source-scholar-${id}" style="display:none">
                    <p style="color:var(--text-secondary)">${spinnerHtml}${t('loadingScholar')}</p>
                </div>
                <div id="source-yok-${id}" style="display:none">
                    <p style="color:var(--text-secondary)">${spinnerHtml}${t('loadingYok')}</p>
                </div>
            </div>
        `;
        document.getElementById('academicModal').style.display = 'flex';

        fetchOpenAlexData(id, hasDbPubs);
        fetchScholarData(id);
        fetchYokData(id);
    } catch (err) {
        console.error('Academic detail error:', err);
    }
}

function switchSourceTab(academicId, source) {
    ['openalex', 'scholar', 'yok'].forEach(s => {
        const tab = document.getElementById(`tab-${s}-${academicId}`);
        const content = document.getElementById(`source-${s}-${academicId}`);
        if (tab && content) {
            if (s === source) {
                tab.style.color = 'var(--primary)';
                tab.style.fontWeight = '600';
                tab.style.borderBottom = '2px solid var(--primary)';
                content.style.display = 'block';
            } else {
                tab.style.color = 'var(--text-secondary)';
                tab.style.fontWeight = '500';
                tab.style.borderBottom = '2px solid transparent';
                content.style.display = 'none';
            }
        }
    });
}

function renderMetricsCards(stats, prefix) {
    if (!stats || (!stats.h_index && !stats.i10_index && !stats.cited_by_count)) return '';
    const s = stats;
    return `
        <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px">
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px 20px;text-align:center;min-width:100px">
                <div style="font-size:24px;font-weight:700;color:var(--primary)">${s.h_index || 0}</div>
                <div style="font-size:12px;color:var(--text-secondary);margin-top:2px">${t('hIndex')}</div>
            </div>
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px 20px;text-align:center;min-width:100px">
                <div style="font-size:24px;font-weight:700;color:var(--primary)">${s.i10_index || 0}</div>
                <div style="font-size:12px;color:var(--text-secondary);margin-top:2px">${t('i10Index')}</div>
            </div>
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px 20px;text-align:center;min-width:100px">
                <div style="font-size:24px;font-weight:700;color:var(--primary)">${(s.cited_by_count || 0).toLocaleString()}</div>
                <div style="font-size:12px;color:var(--text-secondary);margin-top:2px">${t('totalCitations')}</div>
            </div>
            ${s.works_count !== undefined ? `<div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px 20px;text-align:center;min-width:100px">
                <div style="font-size:24px;font-weight:700;color:var(--primary)">${(s.works_count || 0).toLocaleString()}</div>
                <div style="font-size:12px;color:var(--text-secondary);margin-top:2px">${t('totalWorks')}</div>
            </div>` : ''}
        </div>
    `;
}

function renderPubList(pubs, titleKey) {
    if (!pubs || pubs.length === 0) return `<p style="color:var(--text-secondary)">${t('noPublications')}</p>`;
    return `
        <h4 style="margin-bottom:8px">${t(titleKey)} (${pubs.length})</h4>
        <div class="detail-list">
            ${pubs.map(p => `
                <div class="detail-list-item">
                    <strong>${escapeHtml(p.title || '')}</strong>
                    <span style="color:var(--text-secondary);font-size:13px">
                        ${escapeHtml(p.journal || p.type || '')} ${p.year ? '(' + p.year + ')' : ''}
                        ${p.citations ? ' | ' + p.citations + ' ' + t('citations') : ''}
                    </span>
                    ${p.doi ? `<a href="${p.doi}" target="_blank" style="font-size:12px;color:var(--primary);margin-top:2px">DOI</a>` : ''}
                    ${p.url && !p.doi ? `<a href="${p.url}" target="_blank" style="font-size:12px;color:var(--primary);margin-top:2px">Link</a>` : ''}
                </div>
            `).join('')}
        </div>
    `;
}

function renderAffiliationInfo(info) {
    if (!info || (!info.university && !info.field)) return '';
    let rows = '';
    if (info.university) rows += `<tr><td style="font-weight:600;padding:4px 12px 4px 0;white-space:nowrap">${t('university')}</td><td style="padding:4px 0">${escapeHtml(info.university)}${info.country ? ' <span style="color:var(--text-secondary)">(' + escapeHtml(info.country) + ')</span>' : ''}</td></tr>`;
    if (info.field) rows += `<tr><td style="font-weight:600;padding:4px 12px 4px 0;white-space:nowrap">${t('fieldLabel')}</td><td style="padding:4px 0">${escapeHtml(info.field)}</td></tr>`;
    if (info.subfield) rows += `<tr><td style="font-weight:600;padding:4px 12px 4px 0;white-space:nowrap">${t('subfieldLabel')}</td><td style="padding:4px 0">${escapeHtml(info.subfield)}</td></tr>`;
    if (info.domain) rows += `<tr><td style="font-weight:600;padding:4px 12px 4px 0;white-space:nowrap">${t('domainLabel')}</td><td style="padding:4px 0">${escapeHtml(info.domain)}</td></tr>`;

    let affHistory = '';
    if (info.affiliations && info.affiliations.length > 0) {
        affHistory = `<details style="margin-top:8px"><summary style="cursor:pointer;font-size:12px;color:var(--primary)">${t('affiliationHistory')} (${info.affiliations.length})</summary>
            <div style="margin-top:6px;font-size:12px">
                ${info.affiliations.map(a => `<div style="padding:3px 0;border-bottom:1px solid var(--border)"><strong>${escapeHtml(a.institution)}</strong> ${a.country ? '<span style="color:var(--text-secondary)">(' + escapeHtml(a.country) + ')</span>' : ''} ${a.years && a.years.length ? '<span style="color:var(--text-secondary);font-size:11px"> ' + a.years.join(', ') + '</span>' : ''}</div>`).join('')}
            </div>
        </details>`;
    }

    return `<div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 16px;margin-bottom:16px">
        <h4 style="margin:0 0 8px 0;font-size:14px">${t('affiliationInfo')}</h4>
        <table style="font-size:13px;border-collapse:collapse">${rows}</table>
        ${affHistory}
    </div>`;
}

function updateDetailFields(academicId, info) {
    if (!info) return;
    const detailEl = document.getElementById('academicDetail');
    if (!detailEl) return;
    const items = detailEl.querySelectorAll('.detail-item');
    items.forEach(item => {
        const strong = item.querySelector('strong');
        if (!strong) return;
        const label = strong.textContent.trim();
        const valueNode = item.childNodes[item.childNodes.length - 1];
        if (valueNode && valueNode.textContent.trim() === '-') {
            if ((label === t('university') || label === 'Universite' || label === 'University') && info.university) {
                valueNode.textContent = info.university;
            }
            if ((label === t('faculty') || label === 'Fakulte' || label === 'Faculty') && info.field) {
                valueNode.textContent = info.field;
            }
            if ((label === t('department') || label === 'Bolum' || label === 'Department') && info.subfield) {
                valueNode.textContent = info.subfield;
            }
        }
    });
}

async function fetchOpenAlexData(academicId, hasDbPubs) {
    const metricsContainer = document.getElementById(`openalex-metrics-${academicId}`);
    const container = document.getElementById(`source-openalex-${academicId}`);
    try {
        const res = await fetch(`${API}/api/academics/${academicId}/publications/openalex`);
        const data = await res.json();

        if (metricsContainer && data.author_stats) {
            metricsContainer.innerHTML = renderMetricsCards(data.author_stats, 'openalex');
        }

        // Update university/faculty/department fields from OpenAlex data
        if (data.affiliation_info) {
            updateDetailFields(academicId, data.affiliation_info);
        }

        if (container) {
            let html = '';
            if (data.affiliation_info) {
                html += renderAffiliationInfo(data.affiliation_info);
            }
            if (data.author_stats && (data.author_stats.h_index || data.author_stats.i10_index || data.author_stats.cited_by_count)) {
                html += renderMetricsCards(data.author_stats, 'openalex');
            }
            if (data.results && data.results.length > 0) {
                html += renderPubList(data.results, 'openalexPublications');
            } else {
                html += `<p style="color:var(--text-secondary)">${t('noPublications')}</p>`;
            }
            container.innerHTML = html;
        }
    } catch (err) {
        if (container) {
            container.innerHTML = `<p style="color:var(--text-secondary)">${t('noPublications')}</p>`;
        }
    }
}

async function fetchScholarData(academicId) {
    const container = document.getElementById(`source-scholar-${academicId}`);
    if (!container) return;
    try {
        const res = await fetch(`${API}/api/academics/${academicId}/publications/scholar`);
        const data = await res.json();

        if (data.error) {
            container.innerHTML = `<p style="color:var(--text-secondary)">${t('scholarError')} <span style="font-size:12px">(${escapeHtml(data.error)})</span></p>`;
            return;
        }

        let html = '';
        // Show affiliation from Google Scholar
        if (data.author_stats && data.author_stats.affiliation) {
            html += `<div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 16px;margin-bottom:16px">
                <h4 style="margin:0 0 8px 0;font-size:14px">${t('affiliationInfo')}</h4>
                <table style="font-size:13px;border-collapse:collapse">
                    <tr><td style="font-weight:600;padding:4px 12px 4px 0">${t('university')}</td><td style="padding:4px 0">${escapeHtml(data.author_stats.affiliation)}</td></tr>
                    ${data.author_stats.interests && data.author_stats.interests.length ? '<tr><td style="font-weight:600;padding:4px 12px 4px 0">' + t('researchAreas') + '</td><td style="padding:4px 0">' + escapeHtml(data.author_stats.interests.join(', ')) + '</td></tr>' : ''}
                </table>
            </div>`;
        }
        if (data.author_stats) {
            html += renderMetricsCards(data.author_stats, 'scholar');
        }
        if (data.publications && data.publications.length > 0) {
            html += renderPubList(data.publications, 'scholarPublications');
        } else {
            html += `<p style="color:var(--text-secondary)">${t('noPublications')}</p>`;
        }
        container.innerHTML = html;
    } catch (err) {
        container.innerHTML = `<p style="color:var(--text-secondary)">${t('scholarError')}</p>`;
    }
}

async function fetchYokData(academicId) {
    const container = document.getElementById(`source-yok-${academicId}`);
    if (!container) return;
    try {
        const res = await fetch(`${API}/api/academics/${academicId}/publications/yok`);
        const data = await res.json();

        if (data.error) {
            container.innerHTML = `<p style="color:var(--text-secondary)">${t('yokError')} <span style="font-size:12px">(${escapeHtml(data.error)})</span></p>`;
            return;
        }

        let html = '';
        // Show YÖK profile info (university, faculty, department)
        if (data.profile && (data.profile.university || data.profile.faculty || data.profile.department)) {
            let rows = '';
            if (data.profile.university) rows += `<tr><td style="font-weight:600;padding:4px 12px 4px 0">${t('university')}</td><td style="padding:4px 0">${escapeHtml(data.profile.university)}</td></tr>`;
            if (data.profile.faculty) rows += `<tr><td style="font-weight:600;padding:4px 12px 4px 0">${t('faculty')}</td><td style="padding:4px 0">${escapeHtml(data.profile.faculty)}</td></tr>`;
            if (data.profile.department) rows += `<tr><td style="font-weight:600;padding:4px 12px 4px 0">${t('department')}</td><td style="padding:4px 0">${escapeHtml(data.profile.department)}</td></tr>`;
            if (data.profile.title) rows += `<tr><td style="font-weight:600;padding:4px 12px 4px 0">${t('allTitles').replace('Tum ','').replace('All ','')}</td><td style="padding:4px 0">${escapeHtml(data.profile.title)}</td></tr>`;
            html += `<div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 16px;margin-bottom:16px">
                <h4 style="margin:0 0 8px 0;font-size:14px">${t('affiliationInfo')}</h4>
                <table style="font-size:13px;border-collapse:collapse">${rows}</table>
                ${data.profile.yok_url ? '<a href="' + escapeHtml(data.profile.yok_url) + '" target="_blank" style="font-size:12px;color:var(--primary);margin-top:6px;display:inline-block">YÖK Akademik Profil →</a>' : ''}
            </div>`;

            // Also update header detail fields from YÖK data
            updateDetailFields(academicId, {
                university: data.profile.university,
                field: data.profile.faculty,
                subfield: data.profile.department,
            });
        }
        if (data.publications && data.publications.length > 0) {
            html += renderPubList(data.publications, 'yokPublications');
        } else {
            html += `<p style="color:var(--text-secondary)">${t('noPublications')}</p>`;
        }
        container.innerHTML = html;
    } catch (err) {
        container.innerHTML = `<p style="color:var(--text-secondary)">${t('yokError')}</p>`;
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
            document.getElementById('pubCount').textContent = `${pubs.length} ${t('pubCount')}`;
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
                        ${p.citations ? `<span>${p.citations} ${t('citations')}</span>` : ''}
                        <span>${escapeHtml(p.type || t('catArticle'))}</span>
                    </div>
                    ${p.academic ? `<div style="font-size:12px;color:var(--text-secondary);margin-top:4px">${t('academicLabel')}: ${escapeHtml(p.academic)}</div>` : ''}
                </div>
            `).join('');
        } catch (err) {
            console.error('Publications load error:', err);
        }
    }, 250);
}

// ─── Stats ──────────────────────────────────────────────────────────────────

async function loadStats() {
    try {
        const res = await fetch(`${API}/api/stats`);
        const stats = await res.json();
        document.getElementById('statsGrid').innerHTML = `
            <div class="stat-card"><span class="material-icons-outlined">folder</span><div class="stat-number">${stats.total_files || 0}</div><div class="stat-label">${t('statFiles')}</div></div>
            <div class="stat-card"><span class="material-icons-outlined">menu_book</span><div class="stat-number">${stats.total_knowledge || 0}</div><div class="stat-label">${t('statKnowledge')}</div></div>
            <div class="stat-card"><span class="material-icons-outlined">smart_toy</span><div class="stat-number">${stats.total_queries || 0}</div><div class="stat-label">${t('statQueries')}</div></div>
            <div class="stat-card"><span class="material-icons-outlined">account_balance</span><div class="stat-number">${stats.total_universities || 0}</div><div class="stat-label">${t('statUni')}</div></div>
            <div class="stat-card"><span class="material-icons-outlined">person</span><div class="stat-number">${stats.total_academics || 0}</div><div class="stat-label">${t('statAcademic')}</div></div>
            <div class="stat-card"><span class="material-icons-outlined">article</span><div class="stat-number">${stats.total_publications || 0}</div><div class="stat-label">${t('statPub')}</div></div>
            <div class="stat-card"><span class="material-icons-outlined">people</span><div class="stat-number">${stats.total_users || 0}</div><div class="stat-label">${t('statUsers')}</div></div>
        `;
    } catch (err) {
        console.error('Stats load error:', err);
    }
}

// ─── OpenAlex ───────────────────────────────────────────────────────────────

async function startSync() {
    const btn = document.getElementById('syncBtn');
    const statusEl = document.getElementById('syncStatus');
    const country = document.getElementById('syncCountry').value || 'TR';
    const search = document.getElementById('syncSearch').value;

    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> ${t('syncRunning')}`;
    statusEl.style.display = 'block';
    statusEl.className = 'sync-status syncing';
    statusEl.innerHTML = t('syncStarted');

    try {
        const params = new URLSearchParams({ country_code: country });
        if (search) params.set('search', search);
        await fetch(`${API}/api/openalex/sync?${params}`, { method: 'POST' });
        pollSyncStatus(statusEl, btn);
    } catch (err) {
        statusEl.className = 'sync-status error';
        statusEl.innerHTML = t('syncFailed') + err.message;
        btn.disabled = false;
        btn.innerHTML = `<span class="material-icons-outlined">cloud_download</span> ${t('startSync')}`;
    }
}

function formatNumber(n) {
    const locale = currentLang === 'tr' ? 'tr-TR' : 'en-US';
    return (n || 0).toLocaleString(locale);
}

function buildProgressHTML(data) {
    const phaseLabels = {
        starting: t('phaseStarting'),
        institutions: t('phaseInstitutions'),
        authors: t('phaseAuthors'),
        works: t('phaseWorks'),
        completed: t('phaseCompleted'),
        error: t('phaseError')
    };
    const phase = data.phase || 'starting';
    const fetched = data.phase_fetched || 0;
    const total = data.phase_total || 0;
    const pct = total > 0 ? Math.min(Math.round((fetched / total) * 100), 100) : 0;
    const prog = data.progress || {};

    let html = `<div style="margin-bottom:8px"><strong>${phaseLabels[phase] || phase}</strong>`;
    if (total > 0) html += ` - ${formatNumber(fetched)} / ${formatNumber(total)} (${pct}%)`;
    html += '</div>';
    if (total > 0) html += `<div style="background:#e0e0e0;border-radius:4px;height:6px;margin-bottom:8px"><div style="background:var(--primary);height:100%;border-radius:4px;width:${pct}%;transition:width 0.3s"></div></div>`;

    if (prog.institutions) html += `<div style="font-size:12px">${t('phaseInstitutions')}: ${formatNumber(prog.institutions.total_saved)} ${t('saved')} / ${formatNumber(prog.institutions.total_fetched)} ${t('fetched')}</div>`;
    if (prog.authors) html += `<div style="font-size:12px">${t('phaseAuthors')}: ${formatNumber(prog.authors.total_saved)} ${t('saved')} / ${formatNumber(prog.authors.total_fetched)} ${t('fetched')}</div>`;
    if (prog.works) html += `<div style="font-size:12px">${t('phaseWorks')}: ${formatNumber(prog.works.total_saved)} ${t('saved')} / ${formatNumber(prog.works.total_fetched)} ${t('fetched')}</div>`;
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
                statusEl.innerHTML = t('phaseError') + ': ' + data.error;
                if (btn) { btn.disabled = false; btn.innerHTML = `<span class="material-icons-outlined">cloud_download</span> ${t('startSync')}`; }
            } else if (data.last_result) {
                const r = data.last_result;
                statusEl.className = 'sync-status done';
                statusEl.innerHTML = `${t('syncCompleted')}<br>
                    ${t('phaseInstitutions')}: ${formatNumber(r.institutions?.total_saved)} ${t('saved')} (${formatNumber(r.institutions?.total_fetched)} ${t('fetched')})<br>
                    ${t('phaseAuthors')}: ${formatNumber(r.authors?.total_saved)} ${t('saved')} (${formatNumber(r.authors?.total_fetched)} ${t('fetched')})<br>
                    ${t('phaseWorks')}: ${formatNumber(r.works?.total_saved)} ${t('saved')} (${formatNumber(r.works?.total_fetched)} ${t('fetched')})`;
                if (btn) { btn.disabled = false; btn.innerHTML = `<span class="material-icons-outlined">cloud_download</span> ${t('startSync')}`; }
                showToast(t('syncDone'));
                hideSyncBanner();
            } else {
                statusEl.className = 'sync-status done';
                statusEl.innerHTML = t('syncCompleted');
                if (btn) { btn.disabled = false; btn.innerHTML = `<span class="material-icons-outlined">cloud_download</span> ${t('startSync')}`; }
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
    if (!query) { showToast(t('enterSearchTerm')); return; }
    const resultsEl = document.getElementById('oaResults');
    resultsEl.innerHTML = '<div style="text-align:center;padding:20px"><span class="spinner"></span></div>';
    try {
        const res = await fetch(`${API}/api/openalex/search/${type}?query=${encodeURIComponent(query)}`);
        const data = await res.json();
        if (!data.results || !data.results.length) {
            resultsEl.innerHTML = `<p style="color:var(--text-secondary);padding:16px">${t('noResults')}</p>`;
            return;
        }
        resultsEl.innerHTML = `<div style="font-size:12px;color:var(--text-secondary);margin-bottom:8px">${data.total.toLocaleString()} ${t('resultsFound')}</div>` +
            data.results.map(item => {
                if (type === 'works') {
                    return `<div class="oa-result-item"><div class="oa-result-title">${escapeHtml(item.title || '')}</div><div class="oa-result-meta">${escapeHtml(item.authors || '')} | ${escapeHtml(item.journal || '')} ${item.year ? '(' + item.year + ')' : ''} | ${item.citations || 0} ${t('citations')} ${item.open_access ? '| ' + t('openAccess') : ''}</div></div>`;
                } else if (type === 'authors') {
                    return `<div class="oa-result-item"><div class="oa-result-title">${escapeHtml(item.name || '')}</div><div class="oa-result-meta">${escapeHtml(item.institution || '')} | ${item.works_count || 0} ${t('works')} | ${item.cited_by_count || 0} ${t('citations')}</div></div>`;
                } else {
                    return `<div class="oa-result-item"><div class="oa-result-title">${escapeHtml(item.name || '')}</div><div class="oa-result-meta">${escapeHtml(item.city || '')} ${escapeHtml(item.country || '')} | ${item.works_count || 0} ${t('works')}</div></div>`;
                }
            }).join('');
    } catch (err) {
        resultsEl.innerHTML = `<p style="color:var(--danger);padding:16px">${t('searchError')}${err.message}</p>`;
    }
}

// ─── Search ─────────────────────────────────────────────────────────────────

let searchTimeout;
function handleSearch(query) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        if (!query.trim()) return;
        const activePage = document.querySelector('.page.active-page');
        if (activePage) {
            const id = activePage.id;
            if (id === 'page-files') loadFiles();
            else if (id === 'page-universities') loadUniversities();
            else if (id === 'page-academics') loadAcademics();
            else if (id === 'page-publications') loadPublications();
            else if (id === 'page-mongo') loadMongoStats();
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

function showSyncBanner() {
    let banner = document.getElementById('syncBanner');
    if (!banner) {
        banner = document.createElement('div');
        banner.id = 'syncBanner';
        banner.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:9999;background:linear-gradient(135deg,#1a73e8,#4285f4);color:#fff;padding:12px 24px;font-size:14px;box-shadow:0 2px 8px rgba(0,0,0,.2);display:flex;align-items:center;gap:12px';
        banner.innerHTML = `<span class="spinner" style="border-color:rgba(255,255,255,.3);border-top-color:#fff"></span><div id="syncBannerContent">${t('bannerLoading')}</div><button onclick="hideSyncBanner()" style="background:none;border:none;color:#fff;cursor:pointer;font-size:18px;margin-left:auto">&times;</button>`;
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
        starting: t('phaseStarting'),
        institutions: t('bannerInstLoading'),
        authors: t('bannerAuthLoading'),
        works: t('bannerWorksLoading'),
        completed: t('bannerCompleted')
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
                        if (d2.last_result) showToast(t('dataLoaded'));
                    }
                } catch (e) { setTimeout(poll, 3000); }
            };
            setTimeout(poll, 2000);
        }
    } catch (e) { /* ignore */ }
}

// ─── MongoDB ────────────────────────────────────────────────────────────────

async function loadMongoStats() {
    const el = document.getElementById('mongoSyncInfo');
    if (!el) return;
    try {
        const res = await fetch(`${API}/api/mongo/stats`);
        const d = await res.json();
        if (!d.connected) {
            el.innerHTML = `<span style="color:var(--danger)">MongoDB baglantisi yok: ${escapeHtml(d.error || '')}</span>`;
            return;
        }
        let html = `<div style="display:flex;gap:16px;flex-wrap:wrap">`;
        html += `<div><strong>${formatNumber(d.universities)}</strong> universite</div>`;
        html += `<div><strong>${formatNumber(d.academics)}</strong> akademisyen</div>`;
        html += `</div>`;
        if (d.university_sync) {
            const us = d.university_sync;
            html += `<div style="margin-top:8px;font-size:12px;color:var(--text-secondary)">Universite sync: ${us.completed ? 'Tamamlandi' : 'Devam ediyor'} (${formatNumber(us.total_fetched)}/${formatNumber(us.api_total)})</div>`;
        }
        if (d.academic_sync) {
            const as2 = d.academic_sync;
            html += `<div style="font-size:12px;color:var(--text-secondary)">Akademisyen sync: ${as2.completed ? 'Tamamlandi' : 'Devam ediyor'} (${formatNumber(as2.total_fetched)}/${formatNumber(as2.api_total)})</div>`;
        }
        el.innerHTML = html;
    } catch (err) {
        el.innerHTML = `<span style="color:var(--text-secondary)">MongoDB durumu alinamadi</span>`;
    }
}

async function startMongoSync(syncType) {
    try {
        const res = await fetch(`${API}/api/mongo/sync/start?sync_type=${syncType}`, {method: 'POST'});
        const d = await res.json();
        const statusEl = document.getElementById('mongoSyncStatus');
        if (statusEl) statusEl.innerHTML = `<p style="color:var(--primary)">${escapeHtml(d.detail || 'Baslatildi')}</p>`;
        // Poll status
        const poll = async () => {
            try {
                const r = await fetch(`${API}/api/mongo/sync/status`);
                const s = await r.json();
                let html = '';
                if (s.universities && s.universities.total_fetched) {
                    const u = s.universities;
                    const pct = u.api_total ? (u.total_fetched / u.api_total * 100).toFixed(1) : 0;
                    html += `<div>Universiteler: ${formatNumber(u.total_fetched)}/${formatNumber(u.api_total)} (${pct}%) ${u.completed ? '✓' : '...'}</div>`;
                }
                if (s.academics && s.academics.total_fetched) {
                    const a = s.academics;
                    const pct = a.api_total ? (a.total_fetched / a.api_total * 100).toFixed(1) : 0;
                    html += `<div>Akademisyenler: ${formatNumber(a.total_fetched)}/${formatNumber(a.api_total)} (${pct}%) ${a.completed ? '✓' : '...'}</div>`;
                }
                if (statusEl) statusEl.innerHTML = html;
                const uDone = !s.universities || s.universities.completed || !s.universities.total_fetched;
                const aDone = !s.academics || s.academics.completed || !s.academics.total_fetched;
                if (!uDone || !aDone) setTimeout(poll, 3000);
                else { loadMongoStats(); showToast('MongoDB sync tamamlandi!'); }
            } catch(e) { setTimeout(poll, 5000); }
        };
        setTimeout(poll, 3000);
    } catch (err) {
        showToast('Sync baslatilamadi: ' + err.message);
    }
}

let mongoSearchPage = 1;
async function searchMongo(page) {
    mongoSearchPage = page || 1;
    const type = document.getElementById('mongoSearchType').value;
    const query = document.getElementById('mongoSearchQuery').value;
    const container = document.getElementById('mongoResults');
    if (!container) return;
    if (!query) { container.innerHTML = ''; return; }
    container.innerHTML = '<p style="color:var(--text-secondary)">Araniyor...</p>';
    try {
        const res = await fetch(`${API}/api/mongo/${type}?search=${encodeURIComponent(query)}&page=${mongoSearchPage}&per_page=20`);
        const d = await res.json();
        if (!d.results || d.results.length === 0) {
            container.innerHTML = '<p style="color:var(--text-secondary)">Sonuc bulunamadi.</p>';
            return;
        }
        let html = `<div style="margin-bottom:8px;font-size:13px;color:var(--text-secondary)">${formatNumber(d.total)} sonuc (sayfa ${d.page})</div>`;
        if (type === 'academics') {
            html += d.results.map(a => `
                <div style="padding:10px 12px;border-bottom:1px solid var(--border);font-size:13px">
                    <strong>${escapeHtml(a.name)}</strong>
                    ${a.university_name ? '<span style="color:var(--text-secondary)"> — ' + escapeHtml(a.university_name) + '</span>' : ''}
                    <div style="margin-top:4px;font-size:12px;color:var(--text-secondary)">
                        h-index: ${a.h_index || 0} | i10: ${a.i10_index || 0} | Atif: ${formatNumber(a.cited_by_count || 0)} | Eser: ${formatNumber(a.works_count || 0)}
                        ${a.field ? ' | ' + escapeHtml(a.field) : ''}
                    </div>
                </div>
            `).join('');
        } else {
            html += d.results.map(u => `
                <div style="padding:10px 12px;border-bottom:1px solid var(--border);font-size:13px">
                    <strong>${escapeHtml(u.name)}</strong>
                    ${u.city ? '<span style="color:var(--text-secondary)"> — ' + escapeHtml(u.city) + '</span>' : ''}
                    <div style="margin-top:4px;font-size:12px;color:var(--text-secondary)">
                        Tur: ${escapeHtml(u.university_type || u.type || '')} | Eser: ${formatNumber(u.works_count || 0)} | Atif: ${formatNumber(u.cited_by_count || 0)}
                        ${u.homepage_url ? ' | <a href="' + escapeHtml(u.homepage_url) + '" target="_blank">Web</a>' : ''}
                    </div>
                </div>
            `).join('');
        }
        // Pagination
        const totalPages = Math.ceil(d.total / 20);
        if (totalPages > 1) {
            html += `<div style="display:flex;gap:8px;margin-top:12px;justify-content:center">`;
            if (mongoSearchPage > 1) html += `<button class="btn-outlined" onclick="searchMongo(${mongoSearchPage - 1})">Onceki</button>`;
            html += `<span style="padding:8px;font-size:13px">${mongoSearchPage}/${totalPages}</span>`;
            if (mongoSearchPage < totalPages) html += `<button class="btn-outlined" onclick="searchMongo(${mongoSearchPage + 1})">Sonraki</button>`;
            html += `</div>`;
        }
        container.innerHTML = html;
    } catch (err) {
        container.innerHTML = `<p style="color:var(--danger)">Hata: ${escapeHtml(err.message)}</p>`;
    }
}

// ─── Init ───────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    applyTranslations();
    loadFiles();
    checkAutoSync();
});
