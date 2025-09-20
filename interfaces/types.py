"""Type definitions for interfaces"""
from typing import Dict, Any, Optional, TypedDict


class ValidationReport(TypedDict):
    """Typed dictionary for validation reports"""
    total_entries: int
    valid_entries: int
    coverage_percentage: float
    generated_at: str


class ProcessingResult(TypedDict):
    """Typed dictionary for processing results"""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]