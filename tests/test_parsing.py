"""Test parsing correctness"""
import pytest
from pathlib import Path
from components.pdf_processor import PDFProcessor
from components.toc_parser import TOCParser


class TestParsing:
    """Test parsing correctness"""
    
    def test_pdf_processor_context_manager(self):
        """Test PDF processor context manager"""
        pdf_path = Path("assets/USB_PD_R3_2 V1.1 2024-10.pdf")
        if not pdf_path.exists():
            pytest.skip("PDF file not found")
        
        with PDFProcessor(str(pdf_path)) as processor:
            assert processor.page_count > 0
            assert processor.document is not None
    
    def test_toc_parser_structure(self):
        """Test TOC parser produces valid structure"""
        pdf_path = Path("assets/USB_PD_R3_2 V1.1 2024-10.pdf")
        if not pdf_path.exists():
            pytest.skip("PDF file not found")
        
        with PDFProcessor(str(pdf_path)) as processor:
            parser = TOCParser(processor)
            entries = parser.parse()
            
            assert entries, "No TOC entries found"
            
            # Check structure
            for entry in entries[:10]:  # Check first 10
                assert hasattr(entry, 'section_id')
                assert hasattr(entry, 'title')
                assert hasattr(entry, 'page')
                assert hasattr(entry, 'level')
                assert entry.page > 0
                assert entry.level >= 0
    
    def test_section_id_format(self):
        """Test section ID format validation"""
        pdf_path = Path("assets/USB_PD_R3_2 V1.1 2024-10.pdf")
        if not pdf_path.exists():
            pytest.skip("PDF file not found")
        
        with PDFProcessor(str(pdf_path)) as processor:
            parser = TOCParser(processor)
            entries = parser.parse()
            
            valid_entries = [e for e in entries if e.section_id]
            assert valid_entries, "No valid section IDs found"
            
            # Check format (should be numeric like 1.2.3)
            for entry in valid_entries[:5]:
                if entry.section_id:
                    parts = entry.section_id.split('.')
                    for part in parts:
                        assert part.isdigit(), f"Invalid section ID: {entry.section_id}"