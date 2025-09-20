"""
PDF File Validation
"""

import fitz
from pathlib import Path
from constants import ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from .exceptions import ValidationError
from .security import SecurityValidator
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['PDFValidator']


class PDFValidator:
    """PDF-specific validation"""
    
    def __init__(self):
        self._security = SecurityValidator()
    
    def validate_pdf_file(self, pdf_path: str) -> Path:
        """
        Validate PDF file with comprehensive security and integrity checks
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Path: Validated and resolved path
            
        Raises:
            ValidationError: If validation fails
        """
        if not pdf_path:
            raise ValidationError("PDF path cannot be empty", "EMPTY_PATH")
        
        if not isinstance(pdf_path, str):
            raise ValidationError("PDF path must be a string", "INVALID_TYPE")
        
        # Security validation
        if not self._security.is_safe_path(pdf_path):
            raise ValidationError("Invalid file path - security violation", "SECURITY_VIOLATION")
        
        try:
            file_path = Path(pdf_path).resolve()
            
            # Existence check
            if not file_path.exists():
                raise ValidationError(f"PDF file not found: {pdf_path}", "FILE_NOT_FOUND")
            
            # File type check
            if not file_path.is_file():
                raise ValidationError(f"Path is not a file: {pdf_path}", "NOT_A_FILE")
            
            # Extension validation
            if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                raise ValidationError(f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}", "INVALID_EXTENSION")
            
            # Size validation
            if not self._security.validate_file_size(file_path):
                raise ValidationError(f"File too large. Maximum size: {MAX_FILE_SIZE} bytes", "FILE_TOO_LARGE")
            
            # PDF integrity validation
            try:
                with fitz.open(file_path) as doc:
                    if doc.page_count == 0:
                        raise ValidationError("PDF file is empty", "EMPTY_PDF")
                    
                    # Basic PDF structure validation
                    if doc.is_encrypted:
                        raise ValidationError("Encrypted PDFs are not supported", "ENCRYPTED_PDF")
                        
            except (fitz.FileNotFoundError, fitz.FileDataError) as e:
                raise ValidationError(f"Invalid or corrupted PDF file: {str(e)}", "CORRUPTED_PDF")
            
            return file_path
            
        except (OSError, ValueError) as e:
            raise ValidationError(f"Path validation failed", "PATH_ERROR")