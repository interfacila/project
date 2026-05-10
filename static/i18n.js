// ─── i18n / Locale ──────────────────────────────────────────────────────────
// Lightweight client-side internationalization for Akademik AI.
//
//   * Locale is auto-detected from `localStorage.lang` (user override) or
//     `navigator.language` ("tr-TR" => Turkish, anything else => English).
//   * Translations live in /static/i18n/<lang>.json.
//   * `t('a.b.c', { name: 'X' })` returns the translated string with {placeholders}
//     interpolated.
//   * On DOMContentLoaded, all elements with `data-i18n="..."` get their
//     textContent replaced; `data-i18n-placeholder="..."` updates `placeholder`;
//     `data-i18n-title="..."` updates `title`; `data-i18n-html="..."` sets
//     innerHTML (use carefully, only with trusted i18n strings).
//   * `setLang(code)` switches at runtime, updates localStorage, re-applies
//     translations and dispatches a `lang-change` CustomEvent on `document`
//     so that app.js can re-render dynamic content.
const I18N = (() => {
    const SUPPORTED = ['tr', 'en'];
    const FALLBACK = 'en';
    let current = 'tr';
    let dict = {};
    const cache = {}; // { tr: {...}, en: {...} }
    const ready = []; // resolvers for whenReady()

    function detectInitial() {
        const stored = (typeof localStorage !== 'undefined') && localStorage.getItem('lang');
        if (stored && SUPPORTED.includes(stored)) return stored;
        const nav = (navigator.language || navigator.userLanguage || 'en').toLowerCase();
        if (nav.startsWith('tr')) return 'tr';
        return FALLBACK;
    }

    async function fetchLang(code) {
        if (cache[code]) return cache[code];
        const res = await fetch(`/static/i18n/${code}.json`, { cache: 'force-cache' });
        if (!res.ok) throw new Error(`i18n load failed: ${code}`);
        cache[code] = await res.json();
        return cache[code];
    }

    function get(key) {
        if (!key) return '';
        const parts = key.split('.');
        let cur = dict;
        for (const p of parts) {
            if (cur && typeof cur === 'object' && p in cur) cur = cur[p];
            else return key; // fallback: show the key so missing translations are obvious
        }
        return typeof cur === 'string' ? cur : key;
    }

    function interpolate(str, vars) {
        if (!vars || typeof str !== 'string') return str;
        return str.replace(/\{(\w+)\}/g, (_, name) =>
            (name in vars) ? String(vars[name]) : `{${name}}`
        );
    }

    function t(key, vars) {
        return interpolate(get(key), vars);
    }

    function applyToDom(root) {
        const scope = root || document;
        scope.querySelectorAll('[data-i18n]').forEach(el => {
            el.textContent = t(el.getAttribute('data-i18n'));
        });
        scope.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            el.setAttribute('placeholder', t(el.getAttribute('data-i18n-placeholder')));
        });
        scope.querySelectorAll('[data-i18n-title]').forEach(el => {
            el.setAttribute('title', t(el.getAttribute('data-i18n-title')));
        });
        scope.querySelectorAll('[data-i18n-html]').forEach(el => {
            el.innerHTML = t(el.getAttribute('data-i18n-html'));
        });
        // Update <html lang="..."> for accessibility / spellcheck behavior.
        document.documentElement.setAttribute('lang', current);
        // Update <title> if marked.
        const titleKey = document.querySelector('title')?.getAttribute('data-i18n');
        if (titleKey) document.title = t(titleKey);
    }

    async function setLang(code) {
        if (!SUPPORTED.includes(code)) code = FALLBACK;
        try {
            dict = await fetchLang(code);
        } catch {
            // Last-ditch fallback: use whatever's in cache or empty object.
            dict = cache[FALLBACK] || cache[current] || {};
        }
        current = code;
        try { localStorage.setItem('lang', code); } catch {}
        applyToDom();
        document.dispatchEvent(new CustomEvent('lang-change', { detail: { lang: code } }));
    }

    function lang() { return current; }

    function whenReady() {
        return new Promise(resolve => {
            if (Object.keys(dict).length) resolve();
            else ready.push(resolve);
        });
    }

    async function init() {
        const initial = detectInitial();
        try {
            dict = await fetchLang(initial);
            current = initial;
        } catch {
            try {
                dict = await fetchLang(FALLBACK);
                current = FALLBACK;
            } catch {
                dict = {};
            }
        }
        applyToDom();
        ready.splice(0).forEach(fn => fn());
        document.dispatchEvent(new CustomEvent('lang-ready', { detail: { lang: current } }));
    }

    // Kick off the initial fetch as soon as the script loads.
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init, { once: true });
    } else {
        init();
    }

    return { t, setLang, lang, applyToDom, whenReady, SUPPORTED };
})();

// Convenience global so templates and app.js can call `t('header.search_placeholder')`.
const t = (key, vars) => I18N.t(key, vars);
