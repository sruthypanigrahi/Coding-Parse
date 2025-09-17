#!/usr/bin/env python3
"""
USB Power Delivery PDF Parser - Command Line Interface

Minimal CLI entry point that only calls service functions.
No business logic - pure delegation to service layer.

Usage:
    python app.py parse [pdf_file]  # Parse PDF
    python app.py search <query>    # Search TOC
"""

import sys
from parser_service import get_parser_service, get_search_service


def main() -> int:
    """Application entry point - delegates to services.
    
    Returns:
        Exit code
    """
    if len(sys.argv) < 2:
        print("Usage: python app.py [parse|search] [args]")
        return 1
    
    command = sys.argv[1]
    
    if command == "parse":
        pdf_file = sys.argv[2] if len(sys.argv) > 2 else None
        result = get_parser_service().parse_pdf(pdf_file)
        return 0 if result['success'] else 1
    
    elif command == "search":
        if len(sys.argv) != 3:
            print("Usage: python app.py search <query>")
            return 1
        result = get_search_service().search_toc(sys.argv[2])
        return 0 if result['success'] else 1
    
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())