import json
import fitz
from concurrent.futures import ThreadPoolExecutor
from ..models import TOCEntry, ContentEntry
from ..utils import SecurePathValidator
from ..config import config

class ParserService:
    """PDF parsing service with image counting and security."""
    
    def __init__(self):
        self.validator = SecurePathValidator()
        self.max_pages = config.parser.get('max_pages')
        self.max_text_length = config.parser.get('max_text_length', 300)
        self.doc_title = config.parser.get('doc_title', 'USB PD')
    
    def parse_pdf(self, pdf_path):
        """Parse PDF extracting TOC, content, and image statistics."""
        try:
            safe_path = self.validator.validate_and_resolve(pdf_path)
            doc = fitz.open(str(safe_path))
            
            try:
                toc_data = self._extract_toc(doc)
                content_data = self._extract_content(doc)
                files_created = self._export_files(toc_data, content_data)
                
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
        """Extract table of contents from PDF document."""
        toc_data = []
        for level, title, page in doc.get_toc():
            entry = TOCEntry(self.doc_title, f"{len(toc_data) + 1}.0", title.strip(), page, level)
            toc_data.append(entry.to_dict())
        return toc_data
    
    def _extract_content(self, doc):
        """Extract content and count images from PDF pages."""
        content_data = []
        pages_to_process = len(doc) if self.max_pages is None else min(self.max_pages, len(doc))
        
        for page_num in range(pages_to_process):
            page = doc[page_num]
            text = page.get_text().strip()
            if len(text) > self.max_text_length:
                text = text[:self.max_text_length]
            
            if text:
                image_count = len(page.get_images())
                entry = ContentEntry(self.doc_title, page_num + 1, text, image_count)
                content_data.append(entry.to_dict())
        
        return content_data
    
    def _export_files(self, toc_data, content_data):
        files_created = []
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self._write_file, config.files['toc_output'], toc_data): config.files['toc_output'],
                executor.submit(self._write_file, config.files['content_output'], content_data): config.files['content_output']
            }
            
            for future in futures:
                try:
                    if future.result():
                        files_created.append(futures[future])
                except:
                    pass
        
        return files_created
    
    def _write_file(self, filename, data):
        try:
            safe_path = self.validator.validate_and_resolve(filename)
            with open(safe_path, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            return True
        except:
            return False