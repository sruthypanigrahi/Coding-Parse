# USB Power Delivery PDF Parser

A production-ready Python tool for extracting Table of Contents and full content from USB Power Delivery specification PDFs, with comprehensive logging, validation, and testing.

## Features

- **Hierarchical TOC Extraction**: Extracts structured table of contents with parent-child relationships
- **Full Content Parsing**: Captures all section text, images, and tables
- **Validation Reports**: Generates Excel/JSON reports comparing parsed vs source TOC
- **Robust Error Handling**: Comprehensive validation and logging
- **Performance Optimized**: Memory-efficient processing with optimizations
- **Production Ready**: Enterprise-grade code quality and architecture

## Prerequisites

```bash
# Required Python packages
pip install PyMuPDF PyYAML pandas openpyxl
```

## Quick Start

```bash
# 1. Parse PDF and extract content
python app.py parse

# 2. Search extracted content
python app.py search "power delivery"

# 3. Generate validation report
python validation_report.py
```

## Environment Variables

Create `.env` file (optional):
```bash
PDF_PATH=assets/USB_PD_R3_2 V1.1 2024-10.pdf
LOG_LEVEL=INFO
OUTPUT_DIR=output
```

## Commands

### Parse PDF
```bash
# Parse default PDF
python app.py parse

# Parse specific file
python app.py parse "path/to/file.pdf"

# Parse with custom output
python app.py parse --output custom_output.jsonl
```

### Search Content
```bash
# Basic search
python app.py search "USB"
python app.py search "2.1.3"
python app.py search "cable assembly"
```

### Search Content
```bash
# Search parsed content
python app.py search "power delivery"
python app.py search "2.1.3"
```

## Output Files

- **`usb_pd_toc.jsonl`**: Structured table of contents
- **`usb_pd_spec.jsonl`**: Complete document content
- **`validation_report.xlsx`**: TOC validation report
- **`validation_report.json`**: JSON validation data
- **`pdf_parser.log`**: Application logs

## Testing & Quality

```bash
# Basic functionality test
python app.py parse
python app.py search "USB"

# Code quality checks
flake8 . --max-line-length=88
black . --check
```

## Architecture

```
├── app.py                    # CLI entry point
├── parser_service.py         # Core business logic
├── pdf_parser.py            # PDF TOC extraction
├── content_extractor.py     # Content parsing
├── validation_report.py     # Report generation
├── performance_optimizer.py # Performance utilities
├── filter.py               # Section filtering
├── search.py               # Search functionality
├── models.py               # Data models
├── validators.py           # Input validation
├── logger_config.py        # Logging configuration
└── constants.py            # Configuration
```

## Configuration

Edit `application.yml`:
```yaml
folders:
  assets: "assets"
  output: "output"

files:
  toc_output: "usb_pd_toc.jsonl"
  content_output: "usb_pd_spec.jsonl"
  default_pdf: "USB_PD_R3_2 V1.1 2024-10.pdf"

parser:
  doc_title: "USB Power Delivery Specification"
  progress_interval: 200
  content_limit: 10000
  max_workers: 4

performance:
  enable_caching: true
  batch_size: 100
  memory_limit: "1GB"
```

## Performance Optimizations

- **String Operations**: Uses list joining instead of concatenation
- **Batch Processing**: Processes large documents in chunks
- **Memory Management**: Efficient resource cleanup
- **Parallel Processing**: Multi-threaded content extraction
- **Caching**: LRU cache for repeated operations

## Error Handling

- **Input Validation**: PDF file validation and search query checks
- **Exception Handling**: Specific exception types with proper logging
- **Resource Management**: Context managers for file operations
- **Fallback Strategies**: Graceful degradation on errors
- **Comprehensive Logging**: Detailed error tracking and statistics

## Deliverables

1. **Parsed TOC**: `usb_pd_toc.jsonl` - Structured table of contents
2. **Full Content**: `usb_pd_spec.jsonl` - Complete document content
3. **Validation Report**: `validation_report.xlsx` - TOC accuracy analysis
4. **Performance Metrics**: Processing time and success rates
5. **Error Logs**: Comprehensive logging for debugging

## Requirements

- Python 3.7+
- PyMuPDF (fitz) >= 1.23.0
- PyYAML >= 6.0
- pandas >= 1.3.0 (for reports)
- openpyxl >= 3.0.0 (for Excel output)

## License

MIT License