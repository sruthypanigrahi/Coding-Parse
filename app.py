#!/usr/bin/env python3
"""
USB Power Delivery PDF Parser - Command Line Interface

A minimal CLI entry point that delegates all business logic to service layers.
Follows clean architecture principles with proper separation of concerns.

Usage:
    python app.py parse [pdf_file]  # Parse PDF and extract content
    python app.py search <query>    # Search extracted TOC
"""

import sys
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from parser_service import get_parser_service, get_search_service


class CommandHandler(ABC):
    """Abstract base class for command handlers following Command pattern."""
    
    @abstractmethod
    def execute(self, args: List[str]) -> int:
        """Execute the command with given arguments.
        
        Args:
            args: Command line arguments
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        pass


class ParseCommand(CommandHandler):
    """Handles PDF parsing operations."""
    
    def execute(self, args: List[str]) -> int:
        """Parse PDF file and extract TOC and content.
        
        Args:
            args: Command arguments, optional PDF file path at index 2
            
        Returns:
            0 if successful, 1 if failed
        """
        pdf_file = args[2] if len(args) > 2 else None
        result = get_parser_service().parse_pdf(pdf_file)
        print("Success" if result['success'] else f"Error: {result['error']}")
        return 0 if result['success'] else 1


class SearchCommand(CommandHandler):
    """Handles search operations on extracted TOC."""
    
    def execute(self, args: List[str]) -> int:
        """Search TOC for matching entries.
        
        Args:
            args: Command arguments, search query at index 2
            
        Returns:
            0 if successful, 1 if failed or invalid arguments
        """
        if len(args) != 3:
            print("Usage: python app.py search <query>")
            return 1
            
        result = get_search_service().search_toc(args[2])
        if result['success']:
            for match in result['matches']:
                print(f"{match['section_id']} {match['title']} (page {match['page']})")
        return 0 if result['success'] else 1


class CLIApplication:
    """Main CLI application using Command pattern for extensibility."""
    
    def __init__(self):
        """Initialize CLI with available commands."""
        self._commands: Dict[str, CommandHandler] = {
            'parse': ParseCommand(),
            'search': SearchCommand()
        }
    
    def run(self, args: List[str]) -> int:
        """Execute CLI application with given arguments.
        
        Args:
            args: Command line arguments from sys.argv
            
        Returns:
            Exit code for the application
        """
        if len(args) < 2:
            self._show_usage()
            return 1
        
        command_name = args[1].lower()
        command = self._commands.get(command_name)
        
        if command:
            return command.execute(args)
        else:
            print(f"Unknown command: {command_name}")
            self._show_usage()
            return 1
    
    def _show_usage(self) -> None:
        """Display usage information."""
        print("Usage: python app.py [parse|search] [args]")


def main() -> int:
    """Application entry point.
    
    Returns:
        Exit code for the process
    """
    app = CLIApplication()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())