"""Search service implementation"""
from typing import Optional, Dict, Any
from interfaces import Executable
from search import TOCSearcher
from validators import InputValidator, ValidationError
from logger_config import setup_logger


class SearchService(Executable):
    """Search service with proper dependency injection"""
    
    def __init__(self, searcher: Optional[TOCSearcher] = None, 
                 validator: Optional[InputValidator] = None):
        self._searcher = searcher or TOCSearcher()
        self._validator = validator or InputValidator()
        self._logger = setup_logger(self.__class__.__name__)
    
    def execute(self, query: str) -> Dict[str, Any]:
        """Execute search with comprehensive error handling"""
        try:
            validated_query = self._validator.validate_search_query(query)
            matches = self._searcher.search(validated_query)
            
            self._logger.info(f"Search for '{validated_query}' returned {len(matches)} results")
            
            return {
                'success': True, 
                'matches': matches, 
                'count': len(matches),
                'query': validated_query
            }
            
        except ValidationError as e:
            self._logger.warning(f"Search validation failed: {e}")
            return {'success': False, 'error': str(e), 'matches': []}
        except FileNotFoundError as e:
            self._logger.error(f"Search index not found: {e}")
            return {'success': False, 'error': 'Search index not available', 'matches': []}
        except Exception as e:
            self._logger.error(f"Search failed: {e}")
            return {'success': False, 'error': 'Internal search error occurred', 'matches': []}