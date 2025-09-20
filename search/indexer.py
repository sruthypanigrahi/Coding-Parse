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
        """Build search index from TOC file"""
        # Enhanced security check - prevent path traversal
        try:
            resolved_path = toc_file.resolve()
            cwd = Path.cwd().resolve()
            resolved_path.relative_to(cwd)
            
            # Additional security: check for dangerous path components
            if any(part in str(toc_file) for part in ['..',  '~', '//', '\\\\']):
                logger.error(f"Dangerous path components detected: {toc_file}")
                return False
        except ValueError:
            logger.error(f"Path traversal detected: {toc_file}")
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
    
    def _process_line(self, line: str, line_num: int, entry_counter: int):
        """Process a single line from TOC file with counter for efficiency"""
        try:
            entry = json.loads(line.strip())
            self.entries.append(entry)
            self._index_entry(entry, entry_counter)
            return entry_counter + 1
        except json.JSONDecodeError as e:
            logger.warning(f"Skipping malformed JSON on line {line_num}: {e}")
            return entry_counter
    
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
        """Tokenize text into searchable words with optimized regex"""
        if not text:
            return []
        return re.findall(r'\b\w{2,}\b', text.lower())