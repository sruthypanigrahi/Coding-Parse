#!/usr/bin/env python3
"""
USB Power Delivery PDF Parser
Main application entry point
"""

import sys
from pathlib import Path
from pdf_parser import PDFParser
from content_extractor import ContentExtractor
from filter import filter_numbered_sections
from search import search_toc
from constants import ASSETS_FOLDER, DEFAULT_PDF_FILE, TOC_OUTPUT_FILE, CONTENT_OUTPUT_FILE


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python app.py parse [pdf_file]")
        print("  python app.py search <query>")
        return
    
    command = sys.argv[1]
    
    if command == "parse":
        if len(sys.argv) == 2:
            pdf_file = Path(ASSETS_FOLDER) / DEFAULT_PDF_FILE
        elif len(sys.argv) == 3:
            pdf_arg = sys.argv[2]
            if Path(pdf_arg).exists():
                pdf_file = Path(pdf_arg)
            else:
                pdf_file = Path(ASSETS_FOLDER) / pdf_arg
        else:
            print("Usage: python app.py parse [pdf_file]")
            return
        
        if not pdf_file.exists():
            print(f"Error: PDF file not found: {pdf_file}")
            return
        
        parser = PDFParser(str(pdf_file))
        
        raw_toc = parser.extract_toc()
        if not raw_toc:
            print("No TOC found in PDF")
            return
        
        structured_toc = parser.build_hierarchy(raw_toc)
        filtered_toc = filter_numbered_sections(structured_toc)
        
        parser.save_jsonl(filtered_toc, TOC_OUTPUT_FILE)
        print(f"TOC output: {TOC_OUTPUT_FILE} ({len(filtered_toc)} sections)")
        
        extractor = ContentExtractor(str(pdf_file))
        content_entries = extractor.extract_content(filtered_toc)
        parser.save_jsonl(content_entries, CONTENT_OUTPUT_FILE)
        print(f"Content output: {CONTENT_OUTPUT_FILE} ({len(content_entries)} entries)")
    
    elif command == "search":
        if len(sys.argv) != 3:
            print("Usage: python app.py search <query>")
            return
        
        query = sys.argv[2]
        search_toc(query)
    
    else:
        print("Unknown command. Use 'parse' or 'search'")


if __name__ == '__main__':
    main()