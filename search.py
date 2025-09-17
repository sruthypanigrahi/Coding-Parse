"""Search functionality for TOC entries"""
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import defaultdict

from models import TOCEntry
from constants import TOC_OUTPUT_FILE
from logger_config import setup_logger

logger = setup_logger(__name__)


class TOCSearcher:
    """Search engine for TOC entries"""
    
    def __init__(self):
        self.entries: List[Dict] = []
        self.word_index: Dict[str, Set[int]] = defaultdict(set)
        self.section_index: Dict[str, int] = {}
        self._index_built = False
    
    def search_with_results(self, query: str) -> List[Dict[str, Any]]:
        """Search TOC and return formatted results"""
        if not self._index_built:
            self._build_index()
        
        if not query.strip():
            return []
        
        # Search by section ID first
        section_matches = self._search_by_section_id(query)
        if section_matches:
            return section_matches
        
        # Then search by text
        return self._search_by_text(query)
    
    def _build_index(self):
        """Build search index from TOC file"""
        try:
            toc_file = Path(TOC_OUTPUT_FILE)
            if not toc_file.exists():
                logger.warning(f"TOC file not found: {TOC_OUTPUT_FILE}")
                return
            
            self.entries = []
            with open(toc_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        entry = json.loads(line.strip())
                        self.entries.append(entry)
                        
                        # Index words from title
                        words = self._tokenize(entry.get('title', ''))
                        for word in words:
                            self.word_index[word.lower()].add(len(self.entries) - 1)
                        
                        # Index section ID
                        section_id = entry.get('section_id', '')
                        if section_id:
                            self.section_index[section_id] = len(self.entries) - 1
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"Skipping malformed JSON on line {line_num}: {e}")
                        continue
            
            self._index_built = True
            logger.info(f"Rebuilt search index with {len(self.entries)} entries")
            
        except Exception as e:
            logger.error(f"Failed to build search index: {e}")
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable words"""
        if not text:
            return []
        
        # Split on non-alphanumeric characters and filter short words
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if len(word) >= 2]
    
    def _search_by_section_id(self, query: str) -> List[Dict[str, Any]]:
        """Search by section ID"""
        results = []
        
        # Exact match
        if query in self.section_index:
            entry = self.entries[self.section_index[query]]
            results.append(self._format_result(entry, 'exact_section'))
        
        # Partial matches
        for section_id, index in self.section_index.items():
            if query.lower() in section_id.lower() and query not in section_id:
                entry = self.entries[index]
                results.append(self._format_result(entry, 'partial_section'))
        
        return results[:10]  # Limit results
    
    def _search_by_text(self, query: str) -> List[Dict[str, Any]]:
        """Search by text content"""
        query_words = self._tokenize(query)
        if not query_words:
            return []
        
        # Find entries containing query words
        candidate_indices = set()
        for word in query_words:
            if word in self.word_index:
                candidate_indices.update(self.word_index[word])
        
        results = []
        for index in candidate_indices:
            entry = self.entries[index]
            results.append(self._format_result(entry, 'text_match'))
        
        return results[:10]  # Limit results
    
    def _format_result(self, entry: Dict, match_type: str) -> Dict[str, Any]:
        """Format search result"""
        return {
            'section_id': entry.get('section_id', ''),
            'title': entry.get('title', ''),
            'page': entry.get('page', 0),
            'match_type': match_type
        }