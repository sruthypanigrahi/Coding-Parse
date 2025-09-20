"""Main search orchestrator"""
from typing import List, Dict, Any, Optional
from interfaces import Searchable
from constants import TOC_OUTPUT_FILE, CONTENT_OUTPUT_FILE
from .indexer import SearchIndexer
from .file_finder import FileFinder
from .query_processor import QueryProcessor


class TOCSearcher(Searchable):
    """Main search orchestrator - coordinates all search operations"""
    
    def __init__(self):
        self._indexer = SearchIndexer()
        self._query_processor = QueryProcessor(self._indexer)
        self._index_built = False
        self._last_modified = None
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search TOC and content with optimized batch operations"""
        if not self._index_built:
            self._rebuild_index_if_needed()
        
        if not query.strip():
            return []
        
        # Optimized batch search - single pass through data
        all_results = self._query_processor.batch_search(query, CONTENT_OUTPUT_FILE)
 
        return self._deduplicate_results(all_results)
    
    def _rebuild_index_if_needed(self):
        """Rebuild index if file changed with cached stat call"""
        toc_file = FileFinder.find_toc_file(TOC_OUTPUT_FILE)
        if not toc_file:
            return
        
        # Cache stat call to avoid redundant filesystem operations
        current_mtime = toc_file.stat().st_mtime
        should_rebuild = True
        if self._last_modified is not None:
            if current_mtime == self._last_modified:
                should_rebuild = False
        
        if should_rebuild:
            if self._indexer.build_index(toc_file):
                self._index_built = True
                self._last_modified = current_mtime
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on section_id"""
        seen_dict = {}
        for result in results:
            section_id = result.get('section_id', '')
            if section_id not in seen_dict:
                seen_dict[section_id] = result
        return list(seen_dict.values())