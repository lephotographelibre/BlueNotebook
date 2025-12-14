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
from PyQt5.QtCore import QObject


class MarkdownParser(QObject):
    # Héritage de QObject uniquement pour avoir accès à self.tr()
    def __init__(self):
        super().__init__()
        self.md = markdown.Markdown(
            extensions=["tables", "fenced_code", "toc", "codehilite"],
            extension_configs={"codehilite": {"css_class": "highlight"}},
        )

    def to_html(self, markdown_text):
        """Convertir Markdown vers HTML"""
        try:
            return self.md.convert(markdown_text)
        except Exception as e:
            # → ENCAPSULATION UNIQUEMENT (français conservé)
            error_msg = self.tr(
                "Erreur de conversion: {error}"
            ).format(error=str(e))
            return f"<p>{error_msg}</p>"

    def reset(self):
        """Réinitialiser le parser"""
        self.md.reset()