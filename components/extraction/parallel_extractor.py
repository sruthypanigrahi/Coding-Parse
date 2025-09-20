"""Parallel extraction implementation"""
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from models import TOCEntry, ContentEntry
from constants import MAX_WORKERS
from logger_config import setup_logger

logger = setup_logger(__name__)

class ParallelExtractor:
    """Handles parallel content extraction"""
    
    def __init__(self, extract_func):
        self.extract_func = extract_func
    
    def extract_parallel(self, entries: List[TOCEntry]) -> List[ContentEntry]:
        """Parallel extraction with error handling"""
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_index = {
                executor.submit(self.extract_func, entries[i], entries, i): i 
                for i in range(len(entries))
            }
            ordered_results = [None] * len(entries)
            
            try:
                for future in as_completed(future_to_index):
                    try:
                        result = future.result(timeout=30)
                        if result:
                            index = future_to_index[future]
                            ordered_results[index] = result
                    except (TimeoutError, Exception) as e:
                        logger.error(f"Parallel extraction failed: {e}")
                
                results = [r for r in ordered_results if r is not None]
                logger.info(f"Parallel extraction completed: {len(results)} entries")
                return results
                
            except Exception as e:
                logger.error(f"Parallel processing failed: {e}")
                return []