# Copyright (C) 2025 Jean-Marc DIGNE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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

from PyQt5.QtCore import QCoreApplication


class UrlToMarkdownContext:
    @staticmethod
    def tr(text):
        return QCoreApplication.translate("UrlToMarkdownContext", text)


class UrlToMarkdown:
    """
    Convertisseur autonome URL → Markdown propre
    Support complet : Apple Developer, StackOverflow, tables intelligentes
    """

    def __init__(self, timeout: int = 15, user_agent: str = None):
        self.timeout = timeout
        # En-têtes complets pour simuler un vrai navigateur et éviter les blocages
        self.headers = {
            "User-Agent": user_agent
            or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "DNT": "1",  # Do Not Track
            "Upgrade-Insecure-Requests": "1",
        }

        # Détection sites spéciaux
        self.apple_regex = re.compile(
            r"^https?://developer\.apple\.com/", re.IGNORECASE
        )
        self.so_regex = re.compile(
            r"^https?://stackoverflow\.com/questions/\d+", re.IGNORECASE
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
            raise ValueError(UrlToMarkdownContext.tr("❌ Url ou html_content requis"))

        base_url = url or "http://example.com"
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

        page_title = ""
        if clean:
            html, page_title = self._extract_readable(html, base_url)
        else:
            soup = BeautifulSoup(html, "html.parser")
            page_title = soup.title.string.strip() if soup.title else ""

        # Tables intelligentes (améliorées)
        html = self._enhance_tables(html)

        # Conversion finale
        md = markdownify(html, heading_style="ATX")
        md = self._postprocess(md, base_url, ignore_links)

        if title and page_title:
            md = f"# {page_title}\n\n{md}"

        return md.strip() + "\n"

    # ————————————————————————————————————————
    # Méthodes privées
    # ————————————————————————————————————————

    def _fetch(self, url: str) -> str:
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text

    def _clean_html(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return str(soup)

    def _extract_readable(self, html_content: str, base_url: str):
        doc = Document(html_content)
        content = doc.summary()
        title = doc.title().strip()
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup.find_all(src=True):
            tag["src"] = urljoin(base_url, tag["src"])
        for tag in soup.find_all(href=True):
            tag["href"] = urljoin(base_url, tag["href"])
        return str(soup), title

    def _apple_json_url(self, web_url: str) -> str | None:
        parsed = urlparse(web_url)
        parts = [p for p in parsed.path.strip("/").split("/") if p]
        if not parts:
            return None
        if parts[0] == "documentation":
            parts = parts[1:]
        return f"https://developer.apple.com/tutorials/data/{'/'.join(parts)}.json"

    def _parse_apple_json(self, data: dict, title: bool, ignore_links: bool) -> str:
        md = ""
        refs = data.get("references", {})

        if title and data.get("metadata", {}).get("title"):
            md += f"# {data['metadata']['title']}\n\n"

        def inline(items):
            text = ""
            for it in items:
                t = it.get("type")
                if t == "text":
                    text += it["text"]
                elif t == "codeVoice":
                    text += f"`{it.get('code', '')}`"
                elif t == "link" and not ignore_links:
                    link_title = it.get('title', UrlToMarkdownContext.tr("Lien"))
                    text += link_title
                elif t == "reference" and it.get("identifier") in refs:
                    ref_title = refs[it["identifier"]].get("title", UrlToMarkdownContext.tr("Référence"))
                    text += ref_title
            return text

        def section(sec):
            text = ""
            if sec.get("title"):
                level = 1 if sec.get("kind") == "hero" else 2
                text += f"{'#' * level} {sec['title']}\n\n"

            for c in sec.get("content", []):
                ct = c.get("type")
                if ct == "paragraph":
                    text += inline(c.get("inlineContent", [])) + "\n\n"
                elif ct == "codeListing":
                    code = "\n".join(c.get("code", []))
                    text += f"```\n{code}\n```\n\n"
                elif ct == "heading":
                    text += f"{'#' * c.get('level', 2)} {c.get('text', '')}\n\n"
            return text

        for s in data.get("primaryContentSections") or data.get("sections", []):
            md += section(s)

        return md

    def _enhance_tables(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")
        for table in soup.find_all("table"):
            md_table = self._table_to_markdown(table)
            div = soup.new_tag("div")
            div.string = "\n" + md_table + "\n"
            table.replace_with(div)
        return str(soup)

    def _table_to_markdown(self, table) -> str:
        def clean(text):
            if not text:
                return ""
            text = re.sub(r"<[^>]+>", "", str(text))
            return re.sub(r"\s+", " ", html.unescape(text)).strip()

        caption = table.find("caption")
        caption_md = clean(caption) + "\n\n" if caption else ""

        rows = []
        for tr in table.find_all("tr"):
            row = [clean(cell) for cell in tr.find_all(["td", "th"])]
            rows.append(row if row else [""])

        if len(rows) < 2:
            return ""

        n_cols = max(len(r) for r in rows)
        for r in rows:
            r.extend([""] * (n_cols - len(r)))

        col_widths = [
            max(len(r[i]) for r in rows) if any(r[i] for r in rows) else 3
            for i in range(n_cols)
        ]  # Min 3 si vide

        md = "\n" + caption_md

        # Mode table ou liste
        total = sum(col_widths) + 3 * (n_cols - 1) + n_cols + 1  # | sep |

        MAX_TABLE_WIDTH = 300

        all_cells = [cell for row in rows for cell in row if cell]
        short_ratio = (
            sum(len(c) < 10 for c in all_cells) / len(all_cells) if all_cells else 0
        )
        if short_ratio > 0.8:
            total = 95  # Force table si majoritairement court

        if total <= MAX_TABLE_WIDTH:
            # Mode table Markdown classique
            header = rows[0]
            md += (
                "| "
                + " | ".join(c.ljust(col_widths[i]) for i, c in enumerate(header))
                + " |\n"
            )
            md += "| " + " | ".join("-" * col_widths[i] for i in range(n_cols)) + " |\n"
            for row in rows[1:]:
                md += (
                    "| "
                    + " | ".join(c.ljust(col_widths[i]) for i, c in enumerate(row))
                    + " |\n"
                )
        else:
            # Mode liste à puces
            headers = rows[0]
            for row in rows[1:]:
                if row[0]:
                    md += f"* {row[0]}\n"
                for i in range(1, n_cols):
                    if headers[i] and row[i]:
                        header_text = headers[i]
                        value_text = row[i]
                        md += f"  * **{header_text}**: {value_text}\n"
                md += "\n"
        return md + "\n"

    def _convert_stackoverflow(
        self, html_content: str, base_url: str, title: bool, ignore_links: bool
    ) -> str:
        soup = BeautifulSoup(html_content, "html.parser")
        page_title = (
            soup.find("h1").get_text(strip=True) if soup.find("h1") else UrlToMarkdownContext.tr("Question")
        )

        q = soup.find("div", id="question")
        a = soup.find("div", id="answers")

        md = markdownify(str(q), heading_style="ATX") if q else ""
        if a and not str(a).strip().endswith("Your Answer"):
            answers_title = UrlToMarkdownContext.tr("Réponses")
            md += f"\n\n## {answers_title}\n\n" + markdownify(str(a), heading_style="ATX")

        md = self._postprocess(md, base_url, ignore_links)
        if title:
            md = f"# {page_title}\n\n{md}"
        return md

    def _postprocess(self, md: str, base_url: str, ignore_links: bool) -> str:
        md = re.sub(
            r"\]\((?!https?:|/|#)([^)]+)\)",
            lambda m: f"]({urljoin(base_url, m.group(1))})",
            md,
        )
        md = re.sub(r"\[¶\]\(#.*?\)", "", md)
        md = re.sub(r"\)\[", ")\n[", md)
        if ignore_links:
            md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
        return md.strip() + "\n"


# ————————————————————————————————————————
# Utilisation simple (optionnel)
# ————————————————————————————————————————
if __name__ == "__main__":
    converter = UrlToMarkdown()
    md = converter.convert(
        url="https://developer.apple.com/documentation/swift/string",
        title=True,
        links=True,
        clean=True,
    )
    print(md)