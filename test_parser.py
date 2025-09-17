"""Unit tests for PDF parser functionality"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import json

from validators import InputValidator, ValidationError
from models import TOCEntry, ContentEntry
from filter import SectionFilter


class TestInputValidator(unittest.TestCase):
    """Test input validation functionality"""
    
    def test_validate_search_query_valid(self):
        """Test valid search query"""
        result = InputValidator.validate_search_query("  test query  ")
        self.assertEqual(result, "test query")
    
    def test_validate_search_query_empty(self):
        """Test empty search query raises error"""
        with self.assertRaises(ValidationError):
            InputValidator.validate_search_query("")
    
    def test_validate_search_query_too_short(self):
        """Test short search query raises error"""
        with self.assertRaises(ValidationError):
            InputValidator.validate_search_query("a")
    
    def test_validate_output_path_valid(self):
        """Test valid output path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.jsonl"
            result = InputValidator.validate_output_path(str(output_path))
            self.assertEqual(result, output_path)
    
    def test_validate_output_path_invalid_directory(self):
        """Test invalid output directory raises error"""
        with self.assertRaises(ValidationError):
            InputValidator.validate_output_path("/nonexistent/path/file.jsonl")


class TestSectionFilter(unittest.TestCase):
    """Test section filtering functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.filter = SectionFilter()
        self.test_entries = [
            TOCEntry("1", "Introduction", 1, 1),
            TOCEntry("1.1", "Overview", 2, 2, "1"),
            TOCEntry("", "Unnumbered Section", 3, 1),
            TOCEntry("2", "Main Content", 4, 1),
        ]
    
    def test_filter_numbered_sections(self):
        """Test filtering keeps only numbered sections"""
        result = self.filter.filter_numbered_sections(self.test_entries)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].section_id, "1")
        self.assertEqual(result[1].section_id, "1.1")
        self.assertEqual(result[2].section_id, "2")
    
    def test_filter_sets_parent_id_none(self):
        """Test filter sets parent_id to None when needed"""
        entry = TOCEntry("1", "Test", 1, 1, "")
        result = self.filter.filter_numbered_sections([entry])
        
        self.assertIsNone(result[0].parent_id)


class TestTOCEntry(unittest.TestCase):
    """Test TOC entry model"""
    
    def test_toc_entry_creation(self):
        """Test TOC entry creation"""
        entry = TOCEntry("1.1", "Test Title", 5, 2, "1")
        
        self.assertEqual(entry.section_id, "1.1")
        self.assertEqual(entry.title, "Test Title")
        self.assertEqual(entry.page, 5)
        self.assertEqual(entry.level, 2)
        self.assertEqual(entry.parent_id, "1")
        self.assertEqual(entry.full_path, "1.1 Test Title")
    
    def test_toc_entry_auto_full_path(self):
        """Test automatic full_path generation"""
        entry = TOCEntry("2", "Chapter Two", 10, 1)
        self.assertEqual(entry.full_path, "2 Chapter Two")


class TestContentEntry(unittest.TestCase):
    """Test content entry model"""
    
    def test_content_entry_creation(self):
        """Test content entry creation"""
        entry = ContentEntry(
            doc_title="Test Doc",
            section_id="1.1",
            title="Test Section",
            page_range="5-10",
            content="Test content"
        )
        
        self.assertEqual(entry.doc_title, "Test Doc")
        self.assertEqual(entry.section_id, "1.1")
        self.assertEqual(entry.title, "Test Section")
        self.assertEqual(entry.page_range, "5-10")
        self.assertEqual(entry.content, "Test content")
        self.assertTrue(entry.has_content)


if __name__ == '__main__':
    unittest.main()