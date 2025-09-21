import json
import fitz
from concurrent.futures import ThreadPoolExecutor
from .models import TOCEntry, ContentEntry
from .utils import SecurePathValidator
from .config import config

class ParserService:
    def __init__(self):
        self.validator = SecurePathValidator()
        self.max_pages = config.parser.get('max_pages')
        self.max_text_length = config.parser.get('max_text_length', 300)
        self.doc_title = config.parser.get('doc_title', 'USB PD')
    
    def parse_pdf(self, pdf_path):
        try:
            safe_path = self.validator.validate_and_resolve(pdf_path)
            doc = fitz.open(str(safe_path))
            
            try:
                toc_data = self._extract_toc(doc)
                content_data = self._extract_content(doc)
                files_created = self._export_data_parallel(toc_data, content_data)
                
                return {
                    'success': True,
                    'toc_data': toc_data,
                    'content_data': content_data,
                    'files_created': files_created
                }
            finally:
                doc.close()
                
        except Exception as e:
            return {'success': False, 'error': f'{type(e).__name__}'}
    
    def _extract_toc(self, doc):
        toc_data = []
        for level, title, page in doc.get_toc():
            entry = TOCEntry(
                doc_title=self.doc_title,
                section_id=f"{len(toc_data) + 1}.0",
                title=title.strip(),
                page=page,
                level=level
            )
            toc_data.append(entry.to_dict())
        return toc_data
    
    def _extract_content(self, doc):
        content_data = []
        pages_to_process = len(doc) if self.max_pages is None else min(self.max_pages, len(doc))
        
        for page_num in range(pages_to_process):
            text = doc[page_num].get_text().strip()
            
            if len(text) > self.max_text_length:
                text = text[:self.max_text_length]
            
            if text:
                entry = ContentEntry(
                    doc_title=self.doc_title,
                    page=page_num + 1,
                    content=text
                )
                content_data.append(entry.to_dict())
        
        return content_data
    
    def _export_data_parallel(self, toc_data, content_data):
        files_to_create = [
            (config.files['toc_output'], toc_data),
            (config.files['content_output'], content_data)
        ]
        
        files_created = []
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(self._write_jsonl_file, f, d): f for f, d in files_to_create}
            
            for future in futures:
                try:
                    if future.result():
                        files_created.append(futures[future])
                except:
                    pass
        
        return files_created
    
    def _write_jsonl_file(self, filename, data):
        try:
            safe_path = self.validator.validate_and_resolve(filename)
            with open(safe_path, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            return True
        except:
            return False

class SearchService:
    def __init__(self):
        self.validator = SecurePathValidator()
        self.max_results = config.search.get('max_results', 10)
        self.min_query_length = config.search.get('min_query_length', 2)
    
    def search(self, query):
        try:
            if not query or len(query.strip()) < self.min_query_length:
                return {'success': False, 'error': f'Query must be at least {self.min_query_length} characters'}
            
            matches = self._search_content(query.strip().lower())
            
            return {
                'success': True,
                'matches': matches[:self.max_results],
                'total_found': len(matches)
            }
        except Exception as e:
            return {'success': False, 'error': f'{type(e).__name__}'}
    
    def _search_content(self, query):
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