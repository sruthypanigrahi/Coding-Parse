import json
from ..utils import SecurePathValidator
from ..config import config

class SearchService:
    """Search service with unlimited results and content preview."""
    
    def __init__(self):
        self.validator = SecurePathValidator()
        self.max_results = config.search.get('max_results')
        self.min_query_length = config.search.get('min_query_length', 2)
    
    def search(self, query):
        """Search through TOC and content files with query validation."""
        try:
            if not query or len(query.strip()) < self.min_query_length:
                return {'success': False, 'error': f'Query must be at least {self.min_query_length} characters'}
            
            matches = self._search_content(query.strip().lower())
            limited_matches = matches[:self.max_results] if self.max_results else matches
            
            return {
                'success': True,
                'matches': limited_matches,
                'total_found': len(matches)
            }
        except Exception as e:
            return {'success': False, 'error': f'{type(e).__name__}'}
    
    def _search_content(self, query):
        """Search content files and return sorted matches by page."""
        matches = []
        
        for filename in [config.files['toc_output'], config.files['content_output']]:
            try:
                safe_path = self.validator.validate_and_resolve(filename)
                if not safe_path.exists():
                    continue
                
                with open(safe_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            searchable_text = ''
                            if 'title' in data:
                                searchable_text += data['title'].lower() + ' '
                            if 'content' in data:
                                searchable_text += data['content'].lower()
                            
                            if query in searchable_text:
                                matches.append({
                                    'title': data.get('title', f"Page {data.get('page', 'Unknown')}"),
                                    'page': data.get('page', 0),
                                    'content': data.get('content', '')[:100] + '...' if data.get('content') else ''
                                })
                        except:
                            continue
            except:
                continue
        
        matches.sort(key=lambda x: x['page'])
        return matches