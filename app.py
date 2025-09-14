import sys
from pathlib import Path
from pdf_parser import USBPDParser
from filter import filter_numbered_sections
from search import search_toc
from constants import RAW_OUTPUT_FILE, CLEAN_OUTPUT_FILE, ASSETS_FOLDER, DEFAULT_PDF_FILE


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python app.py parse <pdf_file>")
        print("  python app.py search <query>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "parse":
        if len(sys.argv) == 2:
            # Use default PDF from assets folder
            pdf_file = Path(ASSETS_FOLDER) / DEFAULT_PDF_FILE
        elif len(sys.argv) == 3:
            # Check if it's just filename (look in assets) or full path
            pdf_arg = sys.argv[2]
            if Path(pdf_arg).exists():
                pdf_file = Path(pdf_arg)
            else:
                pdf_file = Path(ASSETS_FOLDER) / pdf_arg
        else:
            print("Usage: python app.py parse [pdf_file]")
            sys.exit(1)
        
        if not pdf_file.exists():
            print(f"Error: PDF file not found: {pdf_file}")
            sys.exit(1)
        
        parser = USBPDParser(str(pdf_file))
        entries = parser.parse()
        
        if entries:
            parser.save_jsonl(entries, RAW_OUTPUT_FILE)
            count = filter_numbered_sections(RAW_OUTPUT_FILE, CLEAN_OUTPUT_FILE)
            
            print(f"\nParsing complete!")
            print(f"Clean output: {CLEAN_OUTPUT_FILE} ({count} sections)")
            
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
        clean_file = CLEAN_OUTPUT_FILE
        
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