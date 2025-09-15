USB Power Delivery PDF Parser
=============================

A Python tool to extract Table of Contents and full content from USB Power Delivery 
specification PDFs, outputting structured JSONL files.

INSTALLATION
------------
pip install pymupdf

USAGE
-----
Parse PDF and extract content:
  python app.py parse

Parse specific PDF file:
  python app.py parse "path/to/file.pdf"

Search extracted content:
  python app.py search "power delivery"
  python app.py search "2.1"

OUTPUT FILES
------------
usb_pd_toc.jsonl     - Table of Contents with numbered sections
usb_pd_spec.jsonl    - Full document content including images and tables

FEATURES
--------
- Extracts hierarchical table of contents
- Captures all section and subsection content
- Identifies images and tables in document
- Provides search functionality
- Handles large PDF documents efficiently

REQUIREMENTS
------------
- Python 3.6+
- PyMuPDF library