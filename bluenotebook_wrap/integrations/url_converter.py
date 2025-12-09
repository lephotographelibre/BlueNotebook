# urltomarkdown.py (version améliorée pour tables larges)
# pip install requests beautifulsoup4 readability-lxml markdownify validators

import re
import html
import json
from urllib.parse import urljoin, urlparse
from typing import Optional

import requests
from bs4 import BeautifulSoup
from readability import Document
from markdownify import markdownify
from validators import url as valid_url


class UrlToMarkdown:
    """
    Convertisseur autonome URL → Markdown propre
    Support complet : Apple Developer, StackOverflow, tables intelligentes
    """

    def __init__(self, timeout: int = 15, user_agent: str = None):
        self.timeout = timeout
        # En-têtes complets pour simuler un vrai navigateur et éviter les blocages
        self.headers = {
            self.tr("User-Agent"): user_agent
            or self.tr("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"),
            self.tr("Accept"): self.tr("text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"),
            self.tr("Accept-Language"): self.tr("fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7"),
            self.tr("Accept-Encoding"): self.tr("gzip, deflate, br, zstd"),
            self.tr("DNT"): self.tr("1"),  # Do Not Track
            self.tr("Upgrade-Insecure-Requests"): self.tr("1"),
        }

        # Détection sites spéciaux
        self.apple_regex = re.compile(
            self.tr(r"^https?://developer\.apple\.com/"), re.IGNORECASE
        )
        self.so_regex = re.compile(
            self.tr(r"^https?://stackoverflow\.com/questions/\d+"), re.IGNORECASE
        )

    def convert(
        self,
        url: str,
        title: bool = True,
        links: bool = True,
        clean: bool = True,
        html_content: Optional[str] = None,  # Pour forcer du HTML directement
    ) -> str:
        """
        Convertit une URL (ou du HTML) en Markdown propre.

        Args:
            url: URL de la page
            title: Ajouter # Titre en haut
            links: Garder les liens Markdown
            clean: Utiliser Readability pour nettoyer
            html_content: Optionnel – fournir du HTML directement

        Returns:
            Markdown propre
        """
        if not url and not html_content:
            raise ValueError(self.tr("url ou html_content requis"))

        base_url = url or self.tr("http://example.com")
        ignore_links = not links

        # 1. Apple Developer → JSON officiel
        if self.apple_regex.match(base_url):
            json_url = self._apple_json_url(base_url)
            if json_url:
                try:
                    data = json.loads(self._fetch(json_url))
                    return self._parse_apple_json(data, title, ignore_links)
                except:
                    pass  # fallback

        # 2. StackOverflow spécial
        if self.so_regex.match(base_url):
            html = html_content or self._fetch(base_url)
            html = self._clean_html(html)
            return self._convert_stackoverflow(html, base_url, title, ignore_links)

        # 3. Conversion classique
        html = html_content or self._fetch(base_url)
        html = self._clean_html(html)

        page_title = self.tr("")
        if clean:
            html, page_title = self._extract_readable(html, base_url)
        else:
            soup = BeautifulSoup(html, self.tr("html.parser"))
            page_title = soup.title.string.strip() if soup.title else self.tr("")

        # Tables intelligentes (améliorées)
        html = self._enhance_tables(html)

        # Conversion finale
        md = markdownify(html, heading_style=self.tr("ATX"))
        md = self._postprocess(md, base_url, ignore_links)

        if title and page_title:
            md = self.tr("# %1\n\n%2").arg(page_title).arg(md)

        return md.strip() + self.tr("\n")

    # ————————————————————————————————————————
    # Méthodes privées
    # ————————————————————————————————————————

    def _fetch(self, url: str) -> str:
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text

    def _clean_html(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, self.tr("html.parser"))
        for tag in soup([self.tr("script"), self.tr("style"), self.tr("noscript")]):
            tag.decompose()
        return str(soup)

    def _extract_readable(self, html_content: str, base_url: str):
        doc = Document(html_content)
        content = doc.summary()
        title = doc.title().strip()
        soup = BeautifulSoup(content, self.tr("html.parser"))
        for tag in soup.find_all(src=True):
            tag[self.tr("src")] = urljoin(base_url, tag[self.tr("src")])
        for tag in soup.find_all(href=True):
            tag[self.tr("href")] = urljoin(base_url, tag[self.tr("href")])
        return str(soup), title

    def _apple_json_url(self, web_url: str) -> str | None:
        parsed = urlparse(web_url)
        parts = [p for p in parsed.path.strip(self.tr("/")).split(self.tr("/")) if p]
        if not parts:
            return None
        if parts[0] == self.tr("documentation"):
            parts = parts[1:]
        return self.tr("https://developer.apple.com/tutorials/data/%1.json").arg('/'.join(parts))

    def _parse_apple_json(self, data: dict, title: bool, ignore_links: bool) -> str:
        md = self.tr("")
        refs = data.get(self.tr("references"), {})

        if title and data.get(self.tr("metadata"), {}).get(self.tr("title")):
            md += self.tr("# %1\n\n").arg(data[self.tr('metadata')][self.tr('title')])

        def inline(items):
            text = self.tr("")
            for it in items:
                t = it.get(self.tr("type"))
                if t == self.tr("text"):
                    text += it[self.tr("text")]
                elif t == self.tr("codeVoice"):
                    text += self.tr("`%1`").arg(it.get(self.tr('code'), self.tr('')))
                elif t == self.tr("link") and not ignore_links:
                    text += self.tr("%1)").arg(it.get(self.tr('title'), self.tr('Lien')))
                elif t == self.tr("reference") and it.get(self.tr("identifier")) in refs:
                    text += refs[it[self.tr("identifier")]].get(self.tr("title"), self.tr("Référence"))
            return text

        def section(sec):
            text = self.tr("")
            if sec.get(self.tr("title")):
                level = 1 if sec.get(self.tr("kind")) == self.tr("hero") else 2
                text += self.tr("%1 %2\n\n").arg(self.tr('#') * level).arg(sec[self.tr('title')])

            for c in sec.get(self.tr("content"), []):
                ct = c.get(self.tr("type"))
                if ct == self.tr("paragraph"):
                    text += inline(c.get(self.tr("inlineContent"), [])) + self.tr("\n\n")
                elif ct == self.tr("codeListing"):
                    code = self.tr("\n").join(c.get(self.tr("code"), []))
                    text += self.tr("```\n%1\n```\n\n").arg(code)
                elif ct == self.tr("heading"):
                    text += self.tr("%1 %2\n\n").arg(self.tr('#') * c.get(self.tr('level'), 2)).arg(c.get(self.tr('text'), self.tr('')))
            return text

        for s in data.get(self.tr("primaryContentSections")) or data.get(self.tr("sections"), []):
            md += section(s)

        return md

    def _enhance_tables(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, self.tr("html.parser"))
        for table in soup.find_all(self.tr("table")):
            md_table = self._table_to_markdown(table)
            div = soup.new_tag(self.tr("div"))
            div.string = self.tr("\n") + md_table + self.tr("\n")
            table.replace_with(div)
        return str(soup)

    def _table_to_markdown(self, table) -> str:
        def clean(text):
            if not text:
                return self.tr("")
            text = re.sub(r"<[^>]+>", "", str(text))
            return re.sub(r"\s+", " ", html.unescape(text)).strip()

        caption = table.find(self.tr("caption"))
        caption_md = clean(caption) + self.tr("\n\n") if caption else self.tr("")

        rows = []
        for tr in table.find_all(self.tr("tr")):
            row = [clean(cell) for cell in tr.find_all([self.tr("td"), self.tr("th")])]
            rows.append(row if row else [self.tr("")])

        if len(rows) < 2:
            return self.tr("")

        n_cols = max(len(r) for r in rows)
        for r in rows:
            r.extend([self.tr("")] * (n_cols - len(r)))

        col_widths = [
            max(len(r[i]) for r in rows) if any(r[i] for r in rows) else 3
            for i in range(n_cols)
        ]  # Min 3 si vide
        total = sum(col_widths) + 3 * (n_cols - 1) + n_cols + 1  # | sep |

        md = self.tr("\n") + caption_md

        # Amélioration : seuil plus haut pour forcer table plus souvent (mieux pour viewers MD)
        MAX_TABLE_WIDTH = 300  # Au lieu de 96 – testé pour Wikipedia larges

        # Option : si >80% cellules courtes (<10 chars), force table
        all_cells = [cell for row in rows for cell in row if cell]
        short_ratio = (
            sum(len(c) < 10 for c in all_cells) / len(all_cells) if all_cells else 0
        )
        if short_ratio > 0.8:
            total = 95  # Force table si majoritairement court (comme Yes/No)

        if total <= MAX_TABLE_WIDTH:
            # Mode table (amélioré : alignement left par défaut)
            header = rows[0]
            md += (
                self.tr("| ")
                + self.tr(" | ").join(c.ljust(col_widths[i]) for i, c in enumerate(header))
                + self.tr(" |\n")
            )
            md += self.tr("| ") + self.tr(" | ").join(self.tr("-") * col_widths[i] for i in range(n_cols)) + self.tr(" |\n")
            for row in rows[1:]:
                md += (
                    self.tr("| ")
                    + self.tr(" | ").join(c.ljust(col_widths[i]) for i, c in enumerate(row))
                    + self.tr(" |\n")
                )
        else:
            # Mode liste (amélioré : skip si clé vide, et wrap long text si besoin – mais MD gère)
            headers = rows[0]
            for row in rows[1:]:
                md += self.tr("* %1\n").arg(row[0]) if row[0] else self.tr("")  # Bibliothèque en bold bullet
                for i in range(1, n_cols):
                    if headers[i] and row[i]:
                        md += self.tr("  * **%1**: %2\n").arg(headers[i]).arg(row[i])  # Bold clé pour meilleure lisibilité
                md += self.tr("\n")
        return md + self.tr("\n")

    def _convert_stackoverflow(
        self, html_content: str, base_url: str, title: bool, ignore_links: bool
    ) -> str:
        soup = BeautifulSoup(html_content, self.tr("html.parser"))
        page_title = (
            soup.find(self.tr("h1")).get_text(strip=True) if soup.find(self.tr("h1")) else self.tr("Question")
        )

        q = soup.find(self.tr("div"), id=self.tr("question"))
        a = soup.find(self.tr("div"), id=self.tr("answers"))

        md = markdownify(str(q), heading_style=self.tr("ATX")) if q else self.tr("")
        if a and not str(a).strip().endswith("Your Answer"):
            md += self.tr("\n\n## Réponses\n\n") + markdownify(str(a), heading_style=self.tr("ATX"))

        md = self._postprocess(md, base_url, ignore_links)
        if title:
            md = self.tr("# %1\n\n%2").arg(page_title).arg(md)
        return md

    def _postprocess(self, md: str, base_url: str, ignore_links: bool) -> str:
        md = re.sub(
            self.tr(r"\]\((?!https?:|/|#)([^)]+)\)"),
            lambda m: self.tr("](%1)").arg(urljoin(base_url, m.group(1))),
            md,
        )
        md = re.sub(r"\[¶\]\(#.*?\)", "", md)
        md = re.sub(r"\)\[", ")\n[", md)
        if ignore_links:
            md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
        return md.strip() + self.tr("\n")


# ————————————————————————————————————————
# Utilisation simple (optionnel)
# ————————————————————————————————————————
if __name__ == "__main__":
    converter = UrlToMarkdown()
    md = converter.convert(
        url=self.tr("https://developer.apple.com/documentation/swift/string"),
        title=True,
        links=True,
        clean=True,
    )
    print(md)
