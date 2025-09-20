"""Query processing for search operations"""
import json
from pathlib import Path
from typing import List, Dict, Any, Set
from .indexer import SearchIndexer
from .file_finder import FileFinder
from logger_config import setup_logger

logger = setup_logger(__name__)


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
        import itertools
        for section_id_lower, index in itertools.islice(self.indexer.section_index_lower.items(), 50):
            section_id = self.indexer.entries[index].get('section_id', '')
            if query_lower in section_id_lower and section_id not in exact_matches:
                entry = self.indexer.entries[index]
                results.append(self._format_result(entry, 'partial_section'))
        
        return results
    
    def search_by_text(self, query: str) -> List[Dict[str, Any]]:
        """Search by text content"""
        query_words = self._tokenize_query(query)
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
        """Optimized batch search with deduplication"""
        results = []
        seen_ids = set()
        
        # Search TOC data (section ID and text) with memory efficiency
        import itertools
        for result in itertools.chain(self.search_by_section_id(query), self.search_by_text(query)):
            section_id = result.get('section_id')
            if section_id not in seen_ids:
                seen_ids.add(section_id)
                results.append(result)
        
        # Search content file
        for result in self.search_content_file(query, content_filename):
            section_id = result.get('section_id')
            if section_id not in seen_ids:
                seen_ids.add(section_id)
                results.append(result)
        
        return results
    
    def _tokenize_query(self, query: str) -> List[str]:
        """Tokenize query using public interface"""
        import re
        if not query:
            return []
        return re.findall(r'\b\w{2,}\b', query.lower())
    
    def _format_result(self, entry: Dict, match_type: str) -> Dict[str, Any]:
        """Format search result"""
        return {
            'section_id': entry.get('section_id', ''),
            'title': entry.get('title', ''),
            'page': entry.get('page', 0),
            'match_type': match_type
        }