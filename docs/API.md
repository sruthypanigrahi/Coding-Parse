# API Documentation

## Core Services

### ParserService
Main service for PDF parsing with security and performance optimization.

```python
from src.core import ParserService

parser = ParserService()
result = parser.parse_pdf("document.pdf")
```

**Methods:**
- `parse_pdf(pdf_path: str) -> Dict`: Parse PDF and export to JSONL files

### SearchService
Search functionality with input validation and efficient indexing.

```python
from src.core import SearchService

searcher = SearchService()
results = searcher.search("USB power")
```

**Methods:**
- `search(query: str) -> Dict`: Search parsed content with validation

## Data Models

### TOCEntry
Table of contents entry with validation.

**Fields:**
- `doc_title: str` - Document title
- `section_id: str` - Section identifier
- `title: str` - Section title
- `page: int` - Page number
- `level: int` - Heading level

### ContentEntry
Content entry with comprehensive validation.

**Fields:**
- `doc_title: str` - Document title
- `section_id: str` - Section identifier
- `title: str` - Section title
- `page_range: str` - Page range
- `content: str` - Text content

## Security

### SecurePathValidator
Comprehensive path validation preventing CWE-22 vulnerabilities.

```python
from src.utils import SecurePathValidator

validator = SecurePathValidator()
safe_path = validator.validate_and_resolve("filename.pdf")
```

**Methods:**
- `validate_and_resolve(filename) -> Path`: Validate and resolve secure path
- `validate_file_access(filepath) -> Path`: Validate file exists and is accessible