"""PDF processor with context manager pattern"""
try:
    import fitz  # PyMuPDF
except ImportError:
    raise ImportError("PyMuPDF is required. Install with: pip install PyMuPDF")

from pathlib import Path
from typing import Optional, Any
from interfaces import Processable
from logger_config import setup_logger


class PDFProcessor(Processable):
    """PDF processor with comprehensive resource management"""
    
    def __init__(self, file_path: str):
        """Initialize PDF processor with security validation"""
        # Security validation - path traversal protection with cached resolution
        resolved_path = Path(file_path).resolve()
        cwd = Path.cwd().resolve()
        try:
            resolved_path.relative_to(cwd)
        except ValueError:
            raise ValueError("Path traversal not allowed - path outside working directory")
        
        # Cache resolved path to avoid duplicate resolution
        self._file_path = resolved_path
        self._doc: Optional[fitz.Document] = None
        self._logger = setup_logger(self.__class__.__name__)
    
    def __enter__(self) -> 'PDFProcessor':
        """Enter context manager with error handling"""
        try:
            if self._file_path.suffix.lower() != '.pdf':
                raise ValueError("Only PDF files are supported")
            
            if not self._file_path.exists():
                raise FileNotFoundError(f"PDF file not found: {self._file_path}")
            if not self._file_path.is_file():
                raise ValueError(f"Path is not a file: {self._file_path}")
            
            self._doc = fitz.open(self._file_path)
            self._logger.debug(f"Opened PDF: {self._file_path.name}")
            return self
        except (FileNotFoundError, PermissionError, OSError, RuntimeError, ValueError) as e:
            self._logger.error(f"Failed to open PDF {self._file_path.name}: {e}")
            raise
        except Exception as e:
            self._logger.error(f"PDF processing error: {type(e).__name__}")
            raise ValueError(f"Invalid or corrupted PDF file") from e
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager with cleanup"""
        if self._doc:
            try:
                self._doc.close()
                self._logger.debug(f"Closed PDF: {self._file_path.name}")
            except (RuntimeError, OSError) as e:
                self._logger.warning(f"Error closing PDF: {e}")
            except Exception as e:
                self._logger.error(f"Unexpected error closing PDF: {e}")
        return None  # Ensure exceptions are not suppressed
    
    @property
    def document(self) -> fitz.Document:
        """Get document with validation"""
        if self._doc is None:
            raise RuntimeError("PDF not opened. Use within context manager.")
        return self._doc
    
    @property
    def page_count(self) -> int:
        """Get total page count with validation"""
        if self._doc is None:
            raise RuntimeError("PDF not opened. Use within context manager.")
        return len(self._doc)