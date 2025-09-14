#!/usr/bin/env python3
"""
USB Power Delivery PDF Parser Application
Main application to parse PDF and provide search functionality
"""

import sys
from pathlib import Path
from parser_module import USBPDParser, filter_numbered_sections, search_toc


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python app.py parse <pdf_file>")
        print("  python app.py search <query>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "parse":
        if len(sys.argv) != 3:
            print("Usage: python app.py parse <pdf_file>")
            sys.exit(1)
        
        pdf_file = sys.argv[2]
        if not Path(pdf_file).exists():
            print(f"Error: PDF file not found: {pdf_file}")
            sys.exit(1)
        
        # Parse PDF
        parser = USBPDParser(pdf_file)
        entries = parser.parse()
        
        if entries:
            # Save raw output
            parser.save_jsonl(entries, "usb_pd_spec.jsonl")
            
            # Filter numbered sections
            count = filter_numbered_sections("usb_pd_spec.jsonl", "usb_pd_spec_clean.jsonl")
            
            print(f"\nParsing complete!")
            print(f"Clean output: usb_pd_spec_clean.jsonl ({count} sections)")
            
            # Show sample
            print(f"\nSample entries:")
            for entry in entries[:3]:
                if entry.get('section_id'):
                    print(f"  {entry['section_id']} {entry['title']} (p.{entry['page']})")
        else:
            print("No ToC entries found")
    
    elif command == "search":
        if len(sys.argv) != 3:
            print("Usage: python app.py search <query>")
            sys.exit(1)
        
        query = sys.argv[2]
        clean_file = "usb_pd_spec_clean.jsonl"
        
        if not Path(clean_file).exists():
            print(f"Error: {clean_file} not found. Run 'python app.py parse <pdf_file>' first.")
            sys.exit(1)
        
        matches = search_toc(clean_file, query)
        
        if matches:
            print(f"Found {len(matches)} matches for '{query}':\n")
            for match in matches:
                print(f"{match['section_id']} {match['title']} (page {match['page']})")
        else:
            print(f"No matches found for '{query}'")
    
    else:
        print("Unknown command. Use 'parse' or 'search'")


if __name__ == '__main__':
    main()