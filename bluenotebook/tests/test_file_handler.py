"""
Tests pour le gestionnaire de fichiers
"""

import pytest
import tempfile
import os
from core.file_handler import FileHandler

def test_file_handler_read_write():
    content = "# Test\n\nContenu de test"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        # Test lecture
        read_content = FileHandler.read_file(temp_path)
        assert read_content == content
        
        # Test écriture
        new_content = "# Nouveau contenu"
        FileHandler.write_file(temp_path, new_content)
        
        read_new = FileHandler.read_file(temp_path)
        assert read_new == new_content
        
    finally:
        os.unlink(temp_path)

def test_is_markdown_file():
    assert FileHandler.is_markdown_file("test.md") == True
    assert FileHandler.is_markdown_file("test.markdown") == True
    assert FileHandler.is_markdown_file("test.txt") == True
    assert FileHandler.is_markdown_file("test.py") == False
