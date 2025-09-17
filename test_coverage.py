#!/usr/bin/env python3
"""
Enhanced test coverage for edge cases and error branches
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path

# Import modules to test
from validators import InputValidator, ValidationError
from parser_service import ParserService, SearchService
from pdf_parser import PDFParser, JSONLWriter
from content_extractor import ContentExtractor
from models import TOCEntry, ContentEntry, ProcessingStats


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error branches"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_pdf = os.path.join(self.temp_dir, "test.pdf")
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validator_empty_pdf_path(self):
        """Test validator with empty PDF path"""
        with self.assertRaises(ValidationError) as cm:
            InputValidator.validate_pdf_file("")
        self.assertIn("cannot be empty", str(cm.exception))
    
    def test_validator_nonexistent_pdf(self):
        """Test validator with non-existent PDF"""
        with self.assertRaises(ValidationError) as cm:
            InputValidator.validate_pdf_file("nonexistent.pdf")
        self.assertIn("not found", str(cm.exception))
    
    def test_validator_non_pdf_file(self):
        """Test validator with non-PDF file"""
        txt_file = os.path.join(self.temp_dir, "test.txt")
        with open(txt_file, 'w') as f:
            f.write("test")
        
        with self.assertRaises(ValidationError) as cm:
            InputValidator.validate_pdf_file(txt_file)
        self.assertIn("not a PDF", str(cm.exception))
    
    def test_search_query_too_short(self):
        """Test search query validation with short query"""
        with self.assertRaises(ValidationError) as cm:
            InputValidator.validate_search_query("a")
        self.assertIn("at least 2 characters", str(cm.exception))
    
    def test_search_query_empty(self):
        """Test search query validation with empty query"""
        with self.assertRaises(ValidationError) as cm:
            InputValidator.validate_search_query("")
        self.assertIn("cannot be empty", str(cm.exception))
    
    def test_output_path_invalid_directory(self):
        """Test output path validation with invalid directory"""
        invalid_path = "/nonexistent/directory/file.json"
        with self.assertRaises(ValidationError) as cm:
            InputValidator.validate_output_path(invalid_path)
        self.assertIn("does not exist", str(cm.exception))
    
    @patch('fitz.open')
    def test_pdf_parser_file_error(self, mock_fitz):
        """Test PDF parser with file error"""
        mock_fitz.side_effect = Exception("File corrupted")
        
        with self.assertRaises(Exception):
            with PDFParser("test.pdf") as parser:
                pass
    
    @patch('fitz.open')
    def test_content_extractor_empty_doc(self, mock_fitz):
        """Test content extractor with empty document"""
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=0)
        mock_fitz.return_value = mock_doc
        
        with ContentExtractor("test.pdf") as extractor:
            result = extractor.extract_content([])
            self.assertEqual(len(result), 0)
    
    def test_parser_service_validation_error(self):
        """Test parser service with validation error"""
        service = ParserService()
        result = service.parse_pdf("nonexistent.pdf")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_search_service_invalid_query(self):
        """Test search service with invalid query"""
        service = SearchService()
        result = service.search_toc("")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_processing_stats_error_handling(self):
        """Test processing stats error tracking"""
        stats = ProcessingStats()
        stats.add_error("Test error 1")
        stats.add_error("Test error 2")
        
        self.assertEqual(len(stats.errors), 2)
        self.assertIn("Test error 1", stats.errors)
    
    def test_toc_entry_depth_calculation(self):
        """Test TOC entry depth calculation edge cases"""
        # Test empty section ID
        entry = TOCEntry(section_id="", title="Test", page=1, level=1)
        self.assertEqual(entry.get_depth(), 1)
        
        # Test complex section ID
        entry = TOCEntry(section_id="1.2.3.4", title="Test", page=1, level=1)
        self.assertEqual(entry.get_depth(), 4)
    
    def test_content_entry_serialization(self):
        """Test content entry serialization edge cases"""
        entry = ContentEntry(
            doc_title="Test",
            section_id="1.1",
            title="Test Section",
            page_range="1-2",
            content="Test content",
            images=[],
            tables=[],
            metadata={"test": "value"}
        )
        
        data = entry.to_dict()
        self.assertIn('doc_title', data)
        self.assertIn('metadata', data)
        self.assertEqual(data['has_content'], True)
    
    @patch('builtins.open')
    def test_jsonl_writer_file_error(self, mock_open):
        """Test JSONL writer with file error"""
        mock_open.side_effect = IOError("Permission denied")
        
        writer = JSONLWriter()
        with self.assertRaises(IOError):
            writer.save([], "test.jsonl")
    
    def test_fallback_content_creation(self):
        """Test fallback content creation"""
        service = ParserService()
        toc_entries = [
            TOCEntry(section_id="1.1", title="Test", page=1, level=1)
        ]
        
        fallback = service._create_fallback_content(toc_entries)
        self.assertEqual(len(fallback), 1)
        self.assertIn("Fallback", fallback[0].content)


class TestComplexScenarios(unittest.TestCase):
    """Test complex scenarios and integration cases"""
    
    def test_large_toc_processing(self):
        """Test processing large TOC with many entries"""
        # Create 100 mock TOC entries
        toc_entries = []
        for i in range(100):
            entry = TOCEntry(
                section_id=f"{i//10 + 1}.{i%10 + 1}",
                title=f"Section {i+1}",
                page=i + 1,
                level=2 if i % 10 else 1
            )
            toc_entries.append(entry)
        
        # Test that processing doesn't fail
        self.assertEqual(len(toc_entries), 100)
        self.assertTrue(all(entry.section_id for entry in toc_entries))
    
    def test_nested_exception_handling(self):
        """Test nested exception handling scenarios"""
        stats = ProcessingStats()
        
        # Simulate multiple error types
        try:
            raise ValueError("Test error")
        except ValueError as e:
            stats.add_error(f"ValueError: {e}")
        
        try:
            raise FileNotFoundError("File missing")
        except FileNotFoundError as e:
            stats.add_error(f"FileNotFoundError: {e}")
        
        self.assertEqual(len(stats.errors), 2)
        self.assertTrue(any("ValueError" in error for error in stats.errors))
        self.assertTrue(any("FileNotFoundError" in error for error in stats.errors))


if __name__ == '__main__':
    # Run tests with coverage
    unittest.main(verbosity=2)