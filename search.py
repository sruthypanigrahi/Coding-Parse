"""Advanced search system with indexing and optimization"""
import json
from pathlib import Path
from typing import List, Dict, Generator, Optional, Set
import re
from collections import defaultdict

from constants import TOC_OUTPUT_FILE
from logger_config import setup_logger
from performance_cache import cached

logger = setup_logger(__name__)


class SearchIndex:
    """In-memory search index for fast lookups"""
    
    def __init__(self):
        self.word_index: Dict[str, Set[int]] = defaultdict(set)
        self.entries: List[Dict] = []
        self.is_built = False
    
    def build_index(self, entries: List[Dict]) -> None:
        """Build search index from entries"""
        self.entries = entries
        self.word_index.clear()
        
        for idx, entry in enumerate(entries):
            # Index section ID
            if entry.get('section_id'):
                self._add_to_index(entry['section_id'], idx)
            
            # Index title words
            if entry.get('title'):
                words = self._tokenize(entry['title'])
                for word in words:
                    self._add_to_index(word, idx)
        
        self.is_built = True
        logger.debug(f"Built search index with {len(self.word_index)} terms")
    
    def _add_to_index(self, term: str, entry_idx: int) -> None:
        """Add term to index"""
        normalized_term = term.lower().strip()
        if normalized_term:
            self.word_index[normalized_term].add(entry_idx)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable words"""
        # Split on whitespace and punctuation, keep alphanumeric
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if len(word) > 1]
    
    def search(self, query: str) -> Set[int]:
        """Search index for matching entry indices"""
        if not self.is_built:
            return set()
        
        query_lower = query.lower().strip()
        
        # Direct section ID match
        if query_lower in self.word_index:
            return self.word_index[query_lower].copy()
        
        # Word-based search
        query_words = self._tokenize(query)
        if not query_words:
            return set()
        
        # Find entries containing all query words (AND search)
        result_sets = [self.word_index.get(word, set()) for word in query_words]
        if result_sets:
            return set.intersection(*result_sets)
        
        return set()


class TOCSearcher:
    """High-performance TOC searcher with indexing"""
    
    def __init__(self, toc_file: str = TOC_OUTPUT_FILE):
        self.toc_file = Path(toc_file)
        self.index = SearchIndex()
        self._last_modified = 0
    
    def _ensure_index_current(self) -> bool:
        """Ensure search index is current"""
        if not self.toc_file.exists():
            return False
        
        current_modified = self.toc_file.stat().st_mtime
        
        if current_modified > self._last_modified or not self.index.is_built:
            try:
                entries = list(self._load_entries())
                self.index.build_index(entries)
                self._last_modified = current_modified
                logger.info(
                    f"Rebuilt search index with {len(entries)} entries"
                )
                return True
            except Exception as e:
                logger.error(f"Failed to build search index: {e}")
                return False
        
        return True
    
    @cached(ttl=300)
    def _load_entries(self) -> Generator[Dict, None, None]:
        """Load entries from JSONL file with caching"""
        with open(self.toc_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    yield entry
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping malformed JSON on line {line_num}: {e}")
                    continue
    
    def search(self, query: str) -> None:
        """Search and display results (legacy interface)"""
        result = self.search_with_results(query)
        
        if result['success']:
            matches = result['matches']
            if matches:
                print(f"Found {len(matches)} matches for '{query}':\n")
                for match in matches:
                    print(f"{match['section_id']} {match['title']} "
                          f"(page {match['page']})")
            else:
                print(f"No matches found for '{query}'")
        else:
            print(f"Search error: {result['error']}")
    
    def search_with_results(self, query: str) -> Dict:
        """Search and return structured results"""
        if not self.toc_file.exists():
            return {
                'success': False,
                'error': f"{self.toc_file} not found. Run parse first.",
                'matches': []
            }
        
        try:
            # Ensure index is current
            if not self._ensure_index_current():
                # Fallback to linear search
                return self._linear_search(query)
            
            # Use indexed search
            return self._indexed_search(query)
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                'success': False,
                'error': f"Search failed: {e}",
                'matches': []
            }
    
    def _indexed_search(self, query: str) -> Dict:
        """Perform indexed search for better performance"""
        matching_indices = self.index.search(query)
        
        matches = []
        for idx in sorted(matching_indices):
            if idx < len(self.index.entries):
                matches.append(self.index.entries[idx])
        
        # Sort by section ID for consistent ordering
        matches.sort(key=lambda x: self._sort_key(x.get('section_id', '')))
        
        return {
            'success': True,
            'matches': matches,
            'search_type': 'indexed',
            'query': query
        }
    
    def _linear_search(self, query: str) -> Dict:
        """Fallback linear search"""
        logger.warning("Using fallback linear search")
        
        matches = []
        query_lower = query.lower()
        
        for entry in self._load_entries():
            if self._matches_query(entry, query_lower):
                matches.append(entry)
        
        # Sort results
        matches.sort(key=lambda x: self._sort_key(x.get('section_id', '')))
        
        return {
            'success': True,
            'matches': matches,
            'search_type': 'linear',
            'query': query
        }
    
    def _matches_query(self, entry: Dict, query_lower: str) -> bool:
        """Check if entry matches search query"""
        # Check section ID
        section_id = entry.get('section_id', '').lower()
        if query_lower in section_id:
            return True
        
        # Check title
        title = entry.get('title', '').lower()
        if query_lower in title:
            return True
        
        return False
    
    def _sort_key(self, section_id: str) -> tuple:
        """Generate sort key for section ID"""
        if not section_id:
            return (float('inf'),)
        
        try:
            # Split section ID into numeric parts for proper sorting
            parts = section_id.split('.')
            return tuple(int(part) for part in parts)
        except ValueError:
            # Fallback to string sorting
            return (float('inf'), section_id)
    
    def get_statistics(self) -> Dict:
        """Get search index statistics"""
        return {
            'index_built': self.index.is_built,
            'total_entries': len(self.index.entries),
            'index_terms': len(self.index.word_index),
            'file_exists': self.toc_file.exists(),
            'last_modified': self._last_modified
        }


class AdvancedSearcher(TOCSearcher):
    """Advanced searcher with fuzzy matching and ranking"""
    
    def __init__(self, toc_file: str = TOC_OUTPUT_FILE):
        super().__init__(toc_file)
        self.enable_fuzzy = True
        self.fuzzy_threshold = 0.8
    
    def search_fuzzy(self, query: str, max_results: int = 20) -> Dict:
        """Perform fuzzy search with ranking"""
        try:
            if not self._ensure_index_current():
                return self._linear_search(query)
            
            # Get exact matches first
            exact_matches = self._indexed_search(query)['matches']
            
            # Add fuzzy matches if enabled
            if self.enable_fuzzy and len(exact_matches) < max_results:
                fuzzy_matches = self._fuzzy_search(query, max_results - len(exact_matches))
                
                # Combine and deduplicate
                all_matches = exact_matches + fuzzy_matches
                seen_ids = set()
                unique_matches = []
                
                for match in all_matches:
                    match_id = match.get('section_id', '')
                    if match_id not in seen_ids:
                        seen_ids.add(match_id)
                        unique_matches.append(match)
                
                return {
                    'success': True,
                    'matches': unique_matches[:max_results],
                    'search_type': 'fuzzy',
                    'query': query
                }
            
            return exact_matches
            
        except Exception as e:
            logger.error(f"Fuzzy search failed: {e}")
            return self._linear_search(query)
    
    def _fuzzy_search(self, query: str, max_results: int) -> List[Dict]:
        """Perform fuzzy matching"""
        import difflib
        
        query_lower = query.lower()
        candidates = []
        
        for entry in self.index.entries:
            # Calculate similarity scores
            title_similarity = difflib.SequenceMatcher(
                None, query_lower, entry.get('title', '').lower()
            ).ratio()
            
            section_similarity = difflib.SequenceMatcher(
                None, query_lower, entry.get('section_id', '').lower()
            ).ratio()
            
            # Use best similarity score
            best_score = max(title_similarity, section_similarity)
            
            if best_score >= self.fuzzy_threshold:
                candidates.append((best_score, entry))
        
        # Sort by similarity score (descending)
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        return [entry for score, entry in candidates[:max_results]]