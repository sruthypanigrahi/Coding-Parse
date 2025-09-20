"""Query processing for search operations"""
import json
from pathlib import Path
from typing import List, Dict, Any, Set
from .indexer import SearchIndexer
from .file_finder import FileFinder


class QueryProcessor:
    """Handles different types of search queries"""
    
    def __init__(self, indexer: SearchIndexer):
        self.indexer = indexer
    
    def search_by_section_id(self, query: str) -> List[Dict[str, Any]]:
        """Search by section ID"""
        results = []
        exact_matches = set()
        
        # Exact match
        if query in self.indexer.section_index:
            entry = self.indexer.entries[self.indexer.section_index[query]]
            results.append(self._format_result(entry, 'exact_section'))
            exact_matches.add(entry.get('section_id', ''))
        
        # Partial matches - limited for performance
        query_lower = query.lower()
        for section_id_lower, index in list(self.indexer.section_index_lower.items())[:50]:
            section_id = self.indexer.entries[index].get('section_id', '')
            if query_lower in section_id_lower and section_id not in exact_matches:
                entry = self.indexer.entries[index]
                results.append(self._format_result(entry, 'partial_section'))
        
        return results
    
    def search_by_text(self, query: str) -> List[Dict[str, Any]]:
        """Search by text content"""
        query_words = self.indexer._tokenize(query)
        if not query_words:
            return []
        
        candidate_indices = set()
        for word in query_words:
            if word in self.indexer.word_index:
                candidate_indices.update(self.indexer.word_index[word])
        
        results = []
        for index in candidate_indices:
            entry = self.indexer.entries[index]
            results.append(self._format_result(entry, 'text_match'))
        
        return results
    
    def search_content_file(self, query: str, content_filename: str) -> List[Dict[str, Any]]:
        """Search in content file"""
        content_file = FileFinder.find_content_file(content_filename)
        if not content_file:
            return []
        
        results = []
        query_lower = query.lower()
        
        try:
            # Validate file path for security
            from validators.security import SecurityValidator
            if not SecurityValidator.validate_file_path(str(content_file)):
                logger.error(f"Security violation: Invalid file path {content_file}")
                return []
            
            with open(content_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        content = entry.get('content', '').lower()
                        if query_lower in content:
                            results.append(self._format_result(entry, 'content_match'))
                    except json.JSONDecodeError:
                        continue
        except (FileNotFoundError, PermissionError):
            pass
        
        return results
    
    def batch_search(self, query: str, content_filename: str) -> List[Dict[str, Any]]:
        """Optimized batch search - single pass through all data sources"""
        results = []
        
        # Search TOC data (section ID and text)
        results.extend(self.search_by_section_id(query))
        results.extend(self.search_by_text(query))
        
        # Search content file
        results.extend(self.search_content_file(query, content_filename))
        
        return results
    
    def _format_result(self, entry: Dict, match_type: str) -> Dict[str, Any]:
        """Format search result"""
        return {
            'section_id': entry.get('section_id', ''),
            'title': entry.get('title', ''),
            'page': entry.get('page', 0),
            'match_type': match_type
        }