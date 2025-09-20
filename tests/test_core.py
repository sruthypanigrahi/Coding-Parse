"""
Unit Tests for Core Components
"""

import unittest
from unittest.mock import Mock, patch
from pathlib import Path
from models import TOCEntry, ContentEntry
from validators import ValidationError, InputValidator
from services_pkg import ParserService, SearchService


class TestInputValidator(unittest.TestCase):
    """Test input validation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = InputValidator()
    
    def test_validate_search_query_valid(self):
        """Test valid search query validation"""
        result = self.validator.validate_search_query("test query")
        self.assertEqual(result, "test query")
    
    def test_validate_search_query_empty(self):
        """Test empty search query raises error"""
        with self.assertRaises(ValidationError):
            self.validator.validate_search_query("")
    
    def test_validate_search_query_too_short(self):
        """Test short search query raises error"""
        with self.assertRaises(ValidationError):
            self.validator.validate_search_query("a")


class TestTOCEntry(unittest.TestCase):
    """Test TOC entry model"""
    
    def test_toc_entry_creation(self):
        """Test TOC entry creation with valid data"""
        entry = TOCEntry(
            section_id="1.1",
            title="Test Section",
            page=10,
            level=1
        )
        self.assertEqual(entry.section_id, "1.1")
        self.assertEqual(entry.title, "Test Section")
        self.assertEqual(entry.page, 10)
        self.assertEqual(entry.level, 1)
    
    def test_toc_entry_validation(self):
        """Test TOC entry validation"""
        entry = TOCEntry(section_id="1.2.3", title="Test", page=5)
        self.assertTrue(entry.is_valid_section_id())
        self.assertEqual(entry.get_depth(), 3)


class TestContentEntry(unittest.TestCase):
    """Test content entry model"""
    
    def test_content_entry_word_count(self):
        """Test word count calculation"""
        entry = ContentEntry(
            doc_title="Test Doc",
            section_id="1.1",
            title="Test",
            page_range="1-2",
            content="This is a test content with multiple words"
        )
        self.assertEqual(entry.word_count, 9)
        self.assertTrue(entry.has_content)


if __name__ == '__main__':
    unittest.main()