# USB Power Delivery PDF Parser

A production-ready Python tool for extracting Table of Contents and full content from USB Power Delivery specification PDFs, with comprehensive logging, validation, and testing.

## Features

- **Hierarchical TOC Extraction**: Extracts structured table of contents with parent-child relationships
- **Full Content Parsing**: Captures all section text, images, and tables
- **Robust Error Handling**: Comprehensive validation and logging
- **Performance Optimized**: Memory-efficient processing with context managers
- **Production Ready**: Follows best practices with proper OOP design

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m pytest test_parser.py -v
```

## Usage

### Parse PDF
```bash
# Parse default PDF from assets folder
python app.py parse

# Parse specific PDF file
python app.py parse "path/to/your/file.pdf"

# Parse PDF from assets folder by name
python app.py parse "USB_PD_R3_2 V1.1 2024-10.pdf"
```

### Search Content
```bash
# Search in extracted TOC
python app.py search "power delivery"
python app.py search "2.1"
python app.py search "cable"
```

## Output Files

- **`usb_pd_toc.jsonl`**: Table of Contents with numbered sections only
- **`usb_pd_spec.jsonl`**: Complete document content including images and tables
- **`pdf_parser.log`**: Application logs for debugging

## Configuration

Edit `application.yml` to customize:

```yaml
folders:
  assets: "assets"

files:
  toc_output: "usb_pd_toc.jsonl"
  content_output: "usb_pd_spec.jsonl"
  default_pdf: "USB_PD_R3_2 V1.1 2024-10.pdf"

parser:
  doc_title: "USB Power Delivery Specification"
  progress_interval: 200
  content_limit: 10000
```

## Architecture

```
├── app.py                 # Main entry point
├── parser_service.py      # Business logic
├── pdf_parser.py         # PDF TOC extraction
├── content_extractor.py  # Content parsing
├── filter.py             # Section filtering
├── search.py             # Search functionality
├── models.py             # Data models
├── validators.py         # Input validation
├── logger_config.py      # Logging setup
├── constants.py          # Configuration loader
└── test_parser.py        # Unit tests
```

## Testing

```bash
# Run all tests
python -m pytest test_parser.py -v

# Run specific test class
python -m pytest test_parser.py::TestInputValidator -v

# Run with coverage
python -m pytest test_parser.py --cov=. --cov-report=html
```

## Error Handling

The application includes comprehensive error handling:

- **Input Validation**: Validates PDF files, search queries, and output paths
- **Logging**: Centralized logging to console and file
- **Custom Exceptions**: Clear error messages for different failure modes
- **Resource Management**: Proper cleanup with context managers

## Performance Features

- **Memory Efficient**: Uses generators and context managers
- **Batch Processing**: Processes content in configurable batches
- **Optimized Parsing**: Compiled regex patterns and efficient data structures
- **Resource Cleanup**: Automatic PDF document closure

## Requirements

- Python 3.7+
- PyMuPDF (fitz) >= 1.23.0
- PyYAML >= 6.0

## Changelog

### v2.0.0 - Production Release
- Added comprehensive logging system
- Implemented input validation with custom exceptions
- Refactored to proper OOP design with classes
- Added unit tests for critical functionality
- Improved error handling and resource management
- Performance optimizations with context managers
- Added detailed documentation and configuration

### v1.0.0 - Initial Release
- Basic PDF parsing functionality
- TOC extraction and content parsing
- Simple command-line interface

## License

MIT License - see LICENSE file for details.