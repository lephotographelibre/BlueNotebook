/**
 * BlueNotebook Web Clipper — Bookmarklet
 *
 * Capture tout ou partie d'une page web et copie le résultat en Markdown
 * formaté pour BlueNotebook dans le presse-papier.
 *
 * INSTALLATION
 * ============
 * 1. Ouvrir le fichier bluenotebook_webclipper.min.js (généré à côté de ce fichier)
 * 2. Copier le contenu complet (une seule ligne commençant par "javascript:")
 * 3. Dans votre navigateur, créer un nouveau marque-page / favori
 * 4. Coller le contenu dans le champ "URL" du marque-page
 * 5. Donner un nom au marque-page (ex: "BlueNotebook Clip")
 *
 * UTILISATION
 * ===========
 * 1. Sur n'importe quelle page web, sélectionner éventuellement du texte
 * 2. Cliquer sur le marque-page "BlueNotebook Clip"
 * 3. Un panneau s'ouvre : ajuster le titre, l'auteur, les tags
 * 4. Cliquer "Copier & Fermer" → le Markdown est dans le presse-papier
 * 5. Dans BlueNotebook, coller (Ctrl+V) à l'endroit souhaité
 *
 * FORMAT DE LA NOTE GÉNÉRÉE
 * ==========================
 * # Titre de l'article
 *
 * > **Source :** [url](url)
 * > **Auteur :** Nom
 * > **Capturé le :** 2026-02-19
 *
 * @@clipping @@tag1
 *
 * ---
 *
 * Contenu en Markdown...
 *
 * GÉNÉRATION DU BOOKMARKLET MINIFIÉ
 * ==================================
 * Utiliser un outil en ligne comme https://jscompress.com ou :
 *   npx terser bluenotebook_webclipper.js -c -m -o bluenotebook_webclipper.min.js
 * Puis préfixer le résultat avec "javascript:" pour obtenir le bookmarklet.
 *
 * Copyright (C) 2026 Jean-Marc DIGNE
 * Licence : GNU GPL v3 — https://www.gnu.org/licenses/
 */

javascript:(async function () {

    // ─── GARDE : empêcher le double-chargement ──────────────────────────────
    if (document.getElementById('bn-clip-overlay')) return;

    // ─── TRADUCTIONS ────────────────────────────────────────────────────────
    const lang = (navigator.language || 'fr').toLowerCase().startsWith('fr') ? 'fr' : 'en';

    const i18n = {
        fr: {
            dialogTitle  : 'BlueNotebook Web Clipper',
            lblTitle     : 'Titre',
            lblAuthor    : 'Auteur',
            lblTags      : 'Tags (séparés par des espaces)',
            lblSource    : 'Source',
            lblPreview   : 'Aperçu Markdown (modifiable)',
            btnCancel    : 'Annuler',
            btnCopy      : 'Copier & Fermer',
            btnCopied    : '✓ Copié dans le presse-papier !',
            fieldSource  : 'Source',
            fieldAuthor  : 'Auteur',
            fieldClipped : 'Capturé le',
        },
        en: {
            dialogTitle  : 'BlueNotebook Web Clipper',
            lblTitle     : 'Title',
            lblAuthor    : 'Author',
            lblTags      : 'Tags (space separated)',
            lblSource    : 'Source',
            lblPreview   : 'Markdown Preview (editable)',
            btnCancel    : 'Cancel',
            btnCopy      : 'Copy & Close',
            btnCopied    : '✓ Copied to clipboard!',
            fieldSource  : 'Source',
            fieldAuthor  : 'Author',
            fieldClipped : 'Clipped on',
        }
    };

    const T = i18n[lang];

    // ─── CHARGEMENT DES DÉPENDANCES ─────────────────────────────────────────
    let Turndown, Readability;
    try {
        [{ default: Turndown }, { default: Readability }] = await Promise.all([
            import('https://unpkg.com/turndown@6.0.0?module'),
            import('https://unpkg.com/@tehshrike/readability@0.2.0')
        ]);
    } catch (e) {
        alert('BlueNotebook Clipper : impossible de charger les dépendances.\n' + e.message);
        return;
    }

    // ─── RÉCUPÉRATION DE LA SÉLECTION UTILISATEUR ──────────────────────────
    function getSelectionHtml() {
        if (typeof window.getSelection !== 'undefined') {
            const sel = window.getSelection();
            if (sel && sel.rangeCount) {
                const container = document.createElement('div');
                for (let i = 0; i < sel.rangeCount; i++) {
                    container.appendChild(sel.getRangeAt(i).cloneContents());
                }
                return container.innerHTML;
            }
        }
        return '';
    }

    const selectionHtml = getSelectionHtml();

    // ─── EXTRACTION DE L'ARTICLE VIA READABILITY ───────────────────────────
    let articleTitle  = document.title || '';
    let articleByline = '';
    let articleHtml   = '';

    try {
        const parsed = new Readability(document.cloneNode(true)).parse();
        if (parsed) {
            articleTitle  = parsed.title   || document.title || '';
            articleByline = parsed.byline  || '';
            articleHtml   = parsed.content || '';
        }
    } catch (e) {
        // Fallback : contenu brut de la page
        articleHtml = document.body ? document.body.innerHTML : '';
    }

    // Priorité : sélection utilisateur → article Readability
    const htmlToConvert = selectionHtml || articleHtml;

    // ─── CONVERSION EN MARKDOWN ─────────────────────────────────────────────
    const td = new Turndown({
        headingStyle    : 'atx',
        hr              : '---',
        bulletListMarker: '-',
        codeBlockStyle  : 'fenced',
        emDelimiter     : '*'
    });

    const markdownBody = td.turndown(htmlToConvert);

    // ─── EXTRACTION DES MÉTADONNÉES ─────────────────────────────────────────
    function getMeta(attr, value) {
        const el = document.querySelector(`meta[${attr}="${value}"]`);
        return el ? el.getAttribute('content').trim() : '';
    }

    const author = articleByline
        || getMeta('name',     'author')
        || getMeta('property', 'author')
        || getMeta('property', 'og:site_name')
        || '';

    function formatDate(date) {
        const y = date.getFullYear();
        const m = String(date.getMonth() + 1).padStart(2, '0');
        const d = String(date.getDate()).padStart(2, '0');
        return `${y}-${m}-${d}`;
    }

    const today   = formatDate(new Date());
    const pageUrl = document.URL;

    // ─── CONSTRUCTION DU MARKDOWN FINAL ────────────────────────────────────
    /**
     * Génère le Markdown BlueNotebook à partir des valeurs des champs.
     * @param {string} title      - Titre de l'article
     * @param {string} authorVal  - Auteur
     * @param {string} tagsVal    - Tags séparés par des espaces
     * @returns {string} Markdown complet prêt à coller dans BlueNotebook
     */
    function buildMarkdown(title, authorVal, tagsVal) {
        // Normalise les tags : ajoute @@ si absent, supprime les doublons
        const tagsList = tagsVal.trim()
            .split(/\s+/)
            .filter(Boolean)
            .map(tag => '@@' + tag.replace(/^@@/, ''))
            .join(' ');

        let header = `# ${title}\n\n`;
        header += `> **${T.fieldSource} :** [${pageUrl}](${pageUrl})  \n`;
        if (authorVal) {
            header += `> **${T.fieldAuthor} :** ${authorVal}  \n`;
        }
        header += `> **${T.fieldClipped} :** ${today}  \n`;
        header += `\n${tagsList}\n\n---\n\n`;

        return header + markdownBody;
    }

    // ─── CSS DE L'OVERLAY ───────────────────────────────────────────────────
    const CSS = `
        #bn-clip-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.65);
            z-index: 2147483647;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
        }
        #bn-clip-dialog {
            background: #1e1e2e;
            color: #cdd6f4;
            border-radius: 12px;
            padding: 24px 28px;
            width: 90%;
            max-width: 640px;
            max-height: 92vh;
            overflow-y: auto;
            box-shadow: 0 24px 64px rgba(0, 0, 0, 0.55);
            box-sizing: border-box;
        }
        #bn-clip-dialog h2 {
            margin: 0 0 18px;
            font-size: 15px;
            font-weight: 600;
            color: #89b4fa;
            letter-spacing: 0.02em;
        }
        #bn-clip-dialog label {
            display: block;
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #7f849c;
            margin: 14px 0 5px;
        }
        #bn-clip-dialog input[type="text"] {
            width: 100%;
            box-sizing: border-box;
            background: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 7px;
            padding: 8px 11px;
            font-size: 13px;
            outline: none;
            transition: border-color 0.15s;
        }
        #bn-clip-dialog input[type="text"]:focus {
            border-color: #89b4fa;
            background: #363649;
        }
        #bn-clip-dialog .bn-source-url {
            font-size: 11px;
            color: #6c7086;
            margin-top: 3px;
            word-break: break-all;
            line-height: 1.5;
        }
        #bn-clip-dialog textarea {
            width: 100%;
            box-sizing: border-box;
            background: #181825;
            color: #a6adc8;
            border: 1px solid #313244;
            border-radius: 7px;
            padding: 10px 12px;
            font-family: 'Consolas', 'Fira Code', 'Monaco', monospace;
            font-size: 11px;
            line-height: 1.6;
            height: 200px;
            resize: vertical;
            outline: none;
            transition: border-color 0.15s;
            margin-top: 5px;
        }
        #bn-clip-dialog textarea:focus {
            border-color: #45475a;
        }
        #bn-clip-dialog .bn-btn-row {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 20px;
        }
        #bn-clip-dialog button {
            padding: 9px 20px;
            border: none;
            border-radius: 7px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: background 0.15s, transform 0.1s;
        }
        #bn-clip-dialog button:active {
            transform: scale(0.97);
        }
        #bn-btn-cancel {
            background: #45475a;
            color: #cdd6f4;
        }
        #bn-btn-cancel:hover { background: #585b70; }
        #bn-btn-copy {
            background: #89b4fa;
            color: #1e1e2e;
        }
        #bn-btn-copy:hover { background: #b4d0ff; }
        #bn-btn-copy.bn-copied {
            background: #a6e3a1;
            color: #1e1e2e;
            cursor: default;
        }
    `;

    // ─── CONSTRUCTION DE L'OVERLAY ──────────────────────────────────────────
    function escAttr(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    const initialMarkdown = buildMarkdown(articleTitle, author, 'clipping');

    const styleEl = document.createElement('style');
    styleEl.id = 'bn-clip-style';
    styleEl.textContent = CSS;
    document.head.appendChild(styleEl);

    const overlay = document.createElement('div');
    overlay.id = 'bn-clip-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', T.dialogTitle);

    overlay.innerHTML = `
        <div id="bn-clip-dialog">
            <h2>📋 ${escAttr(T.dialogTitle)}</h2>

            <label for="bn-f-title">${escAttr(T.lblTitle)}</label>
            <input type="text" id="bn-f-title" value="${escAttr(articleTitle)}">

            <label for="bn-f-author">${escAttr(T.lblAuthor)}</label>
            <input type="text" id="bn-f-author" value="${escAttr(author)}">

            <label for="bn-f-tags">${escAttr(T.lblTags)}</label>
            <input type="text" id="bn-f-tags" value="clipping">

            <label>${escAttr(T.lblSource)}</label>
            <div class="bn-source-url">${escAttr(pageUrl)}</div>

            <label for="bn-f-preview">${escAttr(T.lblPreview)}</label>
            <textarea id="bn-f-preview">${escAttr(initialMarkdown)}</textarea>

            <div class="bn-btn-row">
                <button id="bn-btn-cancel">${escAttr(T.btnCancel)}</button>
                <button id="bn-btn-copy">${escAttr(T.btnCopy)}</button>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    // ─── MISE À JOUR DE L'APERÇU ────────────────────────────────────────────
    function updatePreview() {
        const title     = document.getElementById('bn-f-title').value;
        const authorVal = document.getElementById('bn-f-author').value;
        const tagsVal   = document.getElementById('bn-f-tags').value;
        document.getElementById('bn-f-preview').value = buildMarkdown(title, authorVal, tagsVal);
    }

    document.getElementById('bn-f-title').addEventListener('input', updatePreview);
    document.getElementById('bn-f-author').addEventListener('input', updatePreview);
    document.getElementById('bn-f-tags').addEventListener('input', updatePreview);

    // ─── FERMETURE DE L'OVERLAY ─────────────────────────────────────────────
    function closeOverlay() {
        overlay.remove();
        styleEl.remove();
    }

    document.getElementById('bn-btn-cancel').addEventListener('click', closeOverlay);

    // Fermeture au clic sur le fond
    overlay.addEventListener('click', function (e) {
        if (e.target === overlay) closeOverlay();
    });

    // Fermeture à la touche Échap
    function escHandler(e) {
        if (e.key === 'Escape') {
            closeOverlay();
            document.removeEventListener('keydown', escHandler);
        }
    }
    document.addEventListener('keydown', escHandler);

    // ─── COPIE DANS LE PRESSE-PAPIER ────────────────────────────────────────
    document.getElementById('bn-btn-copy').addEventListener('click', async function () {
        const markdown = document.getElementById('bn-f-preview').value;

        async function doCopy() {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(markdown);
            } else {
                // Fallback pour les navigateurs sans API Clipboard moderne
                const ta = document.createElement('textarea');
                ta.value = markdown;
                ta.style.cssText = 'position:fixed;top:-9999px;left:-9999px;opacity:0;';
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                ta.remove();
            }
        }

        try {
            await doCopy();
            const btn = document.getElementById('bn-btn-copy');
            if (btn) {
                btn.textContent = T.btnCopied;
                btn.classList.add('bn-copied');
                btn.disabled = true;
            }
            setTimeout(closeOverlay, 900);
        } catch (err) {
            alert('BlueNotebook Clipper : échec de la copie.\n' + err.message);
        }
    });

    // Mise au point sur le champ titre
    setTimeout(function () {
        const titleField = document.getElementById('bn-f-title');
        if (titleField) {
            titleField.focus();
            titleField.select();
        }
    }, 80);

})();
