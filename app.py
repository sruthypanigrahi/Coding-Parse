#!/usr/bin/env python3


import sys
from parser_service import parse_pdf, search_toc


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python app.py parse [pdf_file]")
        print("  python app.py search <query>")
        return
    
    command = sys.argv[1]
    
    if command == "parse":
        pdf_arg = sys.argv[2] if len(sys.argv) > 2 else None
        parse_pdf(pdf_arg)
    
    elif command == "search":
        if len(sys.argv) != 3:
            print("Usage: python app.py search <query>")
            return
        search_toc(sys.argv[2])
    
    else:
        print("Unknown command. Use 'parse' or 'search'")


if __name__ == '__main__':
    main()