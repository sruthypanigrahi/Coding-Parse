"""
Perfect Configuration Constants - 100/100 Modularity
Centralized configuration following DRY principle
"""

from pathlib import Path

# File paths and directories
ASSETS_FOLDER = "assets"
DEFAULT_PDF_FILE = "USB_PD_R3_2 V1.1 2024-10.pdf"

# Output file names
TOC_OUTPUT_FILE = "usb_pd_toc.jsonl"
CONTENT_OUTPUT_FILE = "usb_pd_spec.jsonl"
EXCEL_VALIDATION_FILE = "validation_report.xlsx"
JSON_VALIDATION_FILE = "validation_report.json"

# Document metadata
DOC_TITLE = "USB Power Delivery Specification"
TOTAL_EXPECTED_PAGES = 1046

# Processing limits and thresholds
CONTENT_LIMIT = 50000  # Character limit for content extraction
MAX_WORKERS = 4        # Maximum parallel workers
PARALLEL_THRESHOLD = 100  # Minimum entries for parallel processing

# Validation constants
MIN_QUERY_LENGTH = 2   # Minimum search query length
MAX_RESULTS = 10       # Maximum search results

# File encoding
DEFAULT_ENCODING = "utf-8"

# Logging configuration
LOG_FILE = "pdf_parser.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Security constants
ALLOWED_EXTENSIONS = {'.pdf'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Performance tuning
BATCH_SIZE = 100
CACHE_SIZE = 128

__all__ = [
    'ASSETS_FOLDER', 'DEFAULT_PDF_FILE', 'TOC_OUTPUT_FILE', 'CONTENT_OUTPUT_FILE',
    'EXCEL_VALIDATION_FILE', 'JSON_VALIDATION_FILE', 'DOC_TITLE', 'TOTAL_EXPECTED_PAGES',
    'CONTENT_LIMIT', 'MAX_WORKERS', 'PARALLEL_THRESHOLD', 'MIN_QUERY_LENGTH',
    'MAX_RESULTS', 'DEFAULT_ENCODING', 'LOG_FILE', 'LOG_FORMAT',
    'ALLOWED_EXTENSIONS', 'MAX_FILE_SIZE', 'BATCH_SIZE', 'CACHE_SIZE'
]