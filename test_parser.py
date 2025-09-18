"""Unit tests for parser functionality"""
import unittest
from unittest.mock import Mock, patch
from components import TOCParser, ContentExtractor, NumericFilter
from models import TOCEntry, ContentEntry
from services import ParserService


class TestTOCParser(unittest.TestCase):
    """Test TOC parser functionality"""
    
    def setUp(self):
        self.mock_processor = Mock()
        self.parser = TOCParser(self.mock_processor)
    
    def test_create_entry_with_section_id(self):
        """Test creating entry with section ID"""
        entry = self.parser._create_entry(1, "1.1 Introduction", 5)
        self.assertEqual(entry.section_id, "1.1")
        self.assertEqual(entry.title, "Introduction")
        self.assertEqual(entry.page, 5)
        self.assertEqual(entry.level, 1)
    
    def test_create_entry_without_section_id(self):
        """Test creating entry without section ID"""
        entry = self.parser._create_entry(1, "Introduction", 5)
        self.assertEqual(entry.section_id, "")
        self.assertEqual(entry.title, "Introduction")


class TestNumericFilter(unittest.TestCase):
    """Test numeric filter functionality"""
    
    def setUp(self):
        self.filter = NumericFilter()
    
    def test_filter_numeric_sections(self):
        """Test filtering numeric sections"""
        entries = [
            TOCEntry(section_id="1", title="Section 1", page=1, level=1),
            TOCEntry(section_id="1.1", title="Subsection", page=2, level=2),
            TOCEntry(section_id="", title="No ID", page=3, level=1),
            TOCEntry(section_id="A.1", title="Appendix", page=4, level=1)
        ]
        
        filtered = self.filter.apply(entries)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].section_id, "1")
        self.assertEqual(filtered[1].section_id, "1.1")


class TestParserService(unittest.TestCase):
    """Test parser service functionality"""
    
    def setUp(self):
        self.service = ParserService()
    
    def test_resolve_path_default(self):
        """Test resolving default PDF path"""
        path = self.service._resolve_path(None)
        self.assertTrue(str(path).endswith("USB_PD_R3_2 V1.1 2024-10.pdf"))
    
    @patch('pathlib.Path.exists')
    def test_resolve_path_existing_file(self, mock_exists):
        """Test resolving existing file path"""
        mock_exists.return_value = True
        path = self.service._resolve_path("test.pdf")
        self.assertEqual(str(path), "test.pdf")


if __name__ == '__main__':
    unittest.main()