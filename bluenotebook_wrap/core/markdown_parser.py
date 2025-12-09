"""
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


Gestionnaire de parsing et conversion Markdown
"""

import markdown
from markdown.extensions import tables, fenced_code, toc


class MarkdownParser:
    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                self.tr("tables"),
                self.tr("fenced_code"),
                self.tr("toc"),
                self.tr("codehilite"),
            ],
            extension_configs={
                self.tr("codehilite"): {self.tr("css_class"): self.tr("highlight")}
            },
        )

    def to_html(self, markdown_text):
        """Convertir Markdown vers HTML"""
        try:
            return self.md.convert(markdown_text)
        except Exception as e:
            return self.tr("<p>Erreur de conversion: %1</p>").arg(e)

    def reset(self):
        """Réinitialiser le parser"""
        self.md.reset()
