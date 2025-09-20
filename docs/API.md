# API Documentation

## Core Classes

### ParserService
Main service for PDF parsing operations.

**Methods:**
- `execute(pdf_path: Optional[str] = None) -> Dict[str, Any]`
  - Parses PDF and generates all required output files
  - Returns: Success/failure status with metrics

### SearchService  
Service for searching parsed content.

**Methods:**
- `execute(query: str) -> Dict[str, Any]`
  - Searches TOC and content for query terms
  - Returns: Search results with match types

### FileExporter
Handles export of all output formats.

**Methods:**
- `export_toc(entries, filename) -> bool`
- `export_content(entries, filename) -> bool` 
- `export_validation_excel(entries, filename) -> bool`
- `export_validation_json(entries, filename) -> bool`

## Data Models

### TOCEntry
Represents table of contents entry.

**Fields:**
- `doc_title: str` - Document title
- `section_id: str` - Section identifier
- `title: str` - Section title
- `page: int` - Page number
- `level: int` - Nesting level

### ContentEntry
Represents extracted content.

**Fields:**
- `doc_title: str` - Document title
- `section_id: str` - Section identifier
- `content: str` - Extracted text content
- `images: List[ImageInfo]` - Associated images
- `tables: List[TableInfo]` - Associated tables