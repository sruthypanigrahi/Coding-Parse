#!/usr/bin/env python3
"""
USB Power Delivery PDF Parser - Perfect CLI Interface
Minimal, clean CLI following Single Responsibility Principle
"""

import sys
from typing import List
from services_pkg import ParserService, SearchService


def main(args: List[str] = None) -> int:
    """
    Perfect CLI entry point with comprehensive error handling
    
    Args:
        args: Command line arguments (defaults to sys.argv)
        
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    if args is None:
        args = sys.argv
    
    if len(args) < 2:
        print("Usage: python app.py [parse|search|validate] [args]")
        return 1
    
    command = args[1]
    
    try:
        if command == "parse":
            pdf_file = args[2] if len(args) > 2 else None
            service = ParserService()
            result = service.execute(pdf_file)
            return 0 if result['success'] else 1
        
        elif command == "search":
            if len(args) != 3:
                print("Usage: python app.py search <query>")
                return 1
            service = SearchService()
            result = service.execute(args[2])
            
            if result['success']:
                matches = result.get('matches', [])
                if matches:
                    print(f"\nFound {len(matches)} results for '{result['query']}':")
                    print("-" * 60)
                    for match in matches:
                        print(f"Section: {match['section_id']}")
                        print(f"Title: {match['title']}")
                        print(f"Page: {match['page']}")
                        print(f"Match Type: {match['match_type']}")
                        print("-" * 60)
                    print(f"\nTotal matches found: {len(matches)}")
                else:
                    print(f"No results found for '{result['query']}'")
                return 0
            else:
                print(f"Search failed: {result.get('error', 'Unknown error')}")
                return 1
        
        elif command == "validate":
            # Validation is handled by parse command
            service = ParserService()
            result = service.execute()
            return 0 if result['success'] else 1
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: parse, search, validate")
            return 1
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())