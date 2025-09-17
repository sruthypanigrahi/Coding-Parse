"""Search functionality with performance optimizations"""
import json
from pathlib import Path
from typing import List, Dict, Generator
from constants import TOC_OUTPUT_FILE


class TOCSearcher:
    def __init__(self, toc_file: str = TOC_OUTPUT_FILE):
        self.toc_file = Path(toc_file)
    
    def search(self, query: str) -> None:
        """Search TOC entries and display results"""
        if not self.toc_file.exists():
            print(f"Error: {self.toc_file} not found. Run parse first.")
            return
        
        matches = list(self._find_matches(query))
        self._display_results(query, matches)
    
    def _find_matches(self, query: str) -> Generator[Dict, None, None]:
        """Find matching entries using generator for memory efficiency"""
        query_lower = query.lower()
        
        with open(self.toc_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if self._matches_query(entry, query_lower):
                        yield entry
                except json.JSONDecodeError:
                    continue
    
    def _matches_query(self, entry: Dict, query_lower: str) -> bool:
        """Check if entry matches search query"""
        return (query_lower in entry.get('title', '').lower() or 
                query_lower in entry.get('section_id', ''))
    
    def _display_results(self, query: str, matches: List[Dict]) -> None:
        """Display search results"""
        if matches:
            print(f"Found {len(matches)} matches for '{query}':\n")
            for match in matches:
                print(f"{match['section_id']} {match['title']} "
                      f"(page {match['page']})")
        else:
            print(f"No matches found for '{query}'")