"""Search indexing functionality"""
import json
import re
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict
from logger_config import setup_logger

logger = setup_logger(__name__)


class SearchIndexer:
    """Handles search index building and management"""
    
    def __init__(self):
        self.entries: List[Dict] = []
        self.word_index: Dict[str, Set[int]] = defaultdict(set)
        self.section_index: Dict[str, int] = {}
        self.section_index_lower: Dict[str, int] = {}
    
    def build_index(self, toc_file: Path) -> bool:
        """Build search index with secure validation"""
        from utils.security import SecurePathValidator
        
        # Explicit path traversal check
        toc_str = str(toc_file)
        if '..' in toc_str or (not toc_str.endswith('.jsonl')):
            logger.error("Invalid file path or type")
            return False
        
        # Secure path validation with explicit checks
        try:
            toc_str = str(toc_file)
            # Only allow .jsonl files and prevent path traversal
            if not toc_str.endswith('.jsonl') or '/' in toc_str or '\\' in toc_str:
                raise ValueError("Only .jsonl files allowed")
            resolved_path = SecurePathValidator.validate_and_resolve(toc_str)
            SecurePathValidator.validate_file_access(resolved_path)
        except (ValueError, FileNotFoundError) as e:
            logger.error(f"Path validation failed: {e}")
            return False
            
        self.entries = []
        
        try:
            entry_counter = 0
            with open(toc_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    entry_counter = self._process_line(line, line_num, entry_counter)
            
            logger.info(f"Built search index with {len(self.entries)} entries")
            return True
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            logger.error(f"Failed to build search index: {e}")
            return False
    
    def _process_line(self, line: str, line_num: int, entry_counter: int) -> int:
        """Process a single line from TOC file with counter for efficiency"""
        try:
            entry = json.loads(line.strip())
            
            # Use streaming processing for large datasets to avoid memory issues
            if len(self.entries) > 10000:  # Batch processing threshold
                self._process_batch()
            
            self.entries.append(entry)
            self._index_entry(entry, entry_counter)
            return entry_counter + 1
            
        except json.JSONDecodeError as e:
            logger.warning(f"Skipping malformed JSON on line {line_num}: {e}")
            return entry_counter
    
    def _process_batch(self):
        """Process batch with consistent index mapping"""
        if len(self.entries) > 5000:
            # Clear all indices to maintain consistency
            self.word_index.clear()
            self.section_index.clear()
            self.section_index_lower.clear()
            # Keep recent entries and rebuild indices
            self.entries = self.entries[-5000:]
            # Rebuild indices for remaining entries
            for i, entry in enumerate(self.entries):
                self._index_entry(entry, i)
    
    def _index_entry(self, entry: Dict, entry_index: int):
        """Index a single entry for search"""
        # Index words from title
        words = self._tokenize(entry.get('title', ''))
        for word in words:
            self.word_index[word].add(entry_index)
        
        # Index section ID
        section_id = entry.get('section_id', '')
        if section_id:
            self.section_index[section_id] = entry_index
            self.section_index_lower[section_id.lower()] = entry_index
    

    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text with optimized performance"""
        if not text:
            return []
        from utils.performance import PerformanceOptimizer
        return PerformanceOptimizer.WORD_PATTERN.findall(text.lower())