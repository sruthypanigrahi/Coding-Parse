USB Power Delivery PDF Parser
=============================

This tool extracts the Table of Contents from USB Power Delivery specification PDFs 
and outputs clean, machine-readable JSONL files containing only numbered sections.

INSTALLATION
------------
pip install pymupdf

USAGE
-----
1. Extract all TOC entries from PDF:
   python usb_pd_parser.py "USB_PD_R3_2 V1.1 2024-10.pdf" --out usb_pd_spec.jsonl

2. Filter to keep only numbered sections:
   python filter_toc.py usb_pd_spec.jsonl usb_pd_spec_clean.jsonl

COMPLETE WORKFLOW
-----------------
pip install pymupdf
python usb_pd_parser.py "USB_PD_R3_2 V1.1 2024-10.pdf" --out usb_pd_spec.jsonl
python filter_toc.py usb_pd_spec.jsonl usb_pd_spec_clean.jsonl

OUTPUT FORMAT
-------------
Each line in the JSONL file contains:
- doc_title: Document title
- section_id: Numeric section ID (e.g., "2.1.3")
- title: Section title
- page: Starting page number (integer)
- level: Section depth (integer, based on dots in section_id)
- parent_id: Parent section ID (or null for top-level)
- full_path: Complete section identifier with title

REQUIREMENTS
------------
- Python 3.6+
- pymupdf (PyMuPDF) library