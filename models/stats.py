"""
Processing Statistics Models
"""

from dataclasses import dataclass, field
from typing import List
import html
from .base import BaseModel

__all__ = ['ProcessingStats']


@dataclass
class ProcessingStats(BaseModel):
    """Perfect processing statistics with comprehensive metrics"""
    total_sections: int = 0
    processed_sections: int = 0
    total_pages: int = 0
    total_images: int = 0
    total_tables: int = 0
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    _error_set: set[str] = field(default_factory=set, init=False, repr=False)
    
    def add_error(self, error: str) -> None:
        """Add processing error with validation and XSS protection"""
        if error and isinstance(error, str):
            # Sanitize error message to prevent XSS
            sanitized_error = html.escape(error.strip())
            if sanitized_error not in self._error_set:  # O(1) duplicate check
                self.errors.append(sanitized_error)
                self._error_set.add(sanitized_error)
    
    def get_success_rate(self) -> float:
        """Calculate processing success rate"""
        if self.total_sections == 0:
            return 0.0
        return (self.processed_sections / self.total_sections) * 100
    
    def get_error_count(self) -> int:
        """Get total error count"""
        return len(self.errors)
    
    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return bool(self.errors)
    
    def get_processing_summary(self) -> str:
        """Get formatted processing summary"""
        return (f"Processed {self.processed_sections}/{self.total_sections} sections "
                f"({self.get_success_rate():.1f}% success) in {self.processing_time:.2f}s")