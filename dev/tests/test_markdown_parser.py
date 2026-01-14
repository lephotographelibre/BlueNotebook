"""
Tests pour le parser Markdown
"""

import pytest
from core.markdown_parser import MarkdownParser

def test_markdown_parser_basic():
    parser = MarkdownParser()
    
    # Test titre
    result = parser.to_html("# Titre")
    assert "<h1>Titre</h1>" in result
    
    # Test paragraphe
    result = parser.to_html("Un paragraphe simple")
    assert "<p>Un paragraphe simple</p>" in result
    
    # Test code
    result = parser.to_html("`code`")
    assert "<code>code</code>" in result

def test_markdown_parser_table():
    parser = MarkdownParser()
    
    markdown_table = """
| Col1 | Col2 |
|------|------|
| A    | B    |
"""
    
    result = parser.to_html(markdown_table)
    assert "<table>" in result
    assert "<th>Col1</th>" in result
