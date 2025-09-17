"""Input validation utilities"""
from pathlib import Path
from typing import Optional
import fitz


class ValidationError(Exception):
    """Custom validation error"""
    pass


class InputValidator:
    """Validates inputs for PDF parsing operations"""
    
    @staticmethod
    def validate_pdf_file(pdf_path: str) -> Path:
        """Validate PDF file exists and is readable"""
        if not pdf_path:
            raise ValidationError("PDF path cannot be empty")
        
        file_path = Path(pdf_path)
        
        if not file_path.exists():
            raise ValidationError(f"PDF file not found: {file_path}")
        
        if not file_path.is_file():
            raise ValidationError(f"Path is not a file: {file_path}")
        
        if file_path.suffix.lower() != '.pdf':
            raise ValidationError(f"File is not a PDF: {file_path}")
        
        # Test if PDF is readable
        try:
            doc = fitz.open(file_path)
            doc.close()
        except Exception as e:
            raise ValidationError(f"Cannot open PDF file: {e}")
        
        return file_path
    
    @staticmethod
    def validate_search_query(query: str) -> str:
        """Validate search query"""
        if not query:
            raise ValidationError("Search query cannot be empty")
        
        if len(query.strip()) < 2:
            raise ValidationError("Search query must be at least 2 characters")
        
        return query.strip()
    
    @staticmethod
    def validate_output_path(output_path: str) -> Path:
        """Validate output file path"""
        if not output_path:
            raise ValidationError("Output path cannot be empty")
        
        file_path = Path(output_path)
        
        # Check if parent directory exists
        if not file_path.parent.exists():
            raise ValidationError(f"Output directory does not exist: {file_path.parent}")
        
        return file_path