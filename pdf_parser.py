import json
import re
import fitz
from pathlib import Path
from constants import DOC_TITLE, SECTION_TITLE_PATTERN


class PDFParser:
    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)
        self.doc_title = DOC_TITLE
    
    def extract_toc(self):
        """Extract table of contents from PDF bookmarks"""
        try:
            doc = fitz.open(self.pdf_path)
            outline = doc.get_toc()
            doc.close()
            
            if not outline:
                return []
            
            entries = []
            for level, title, page in outline:
                title = title.strip()
                match = re.match(SECTION_TITLE_PATTERN, title)
                
                if match:
                    section_id = match.group(1)
                    section_title = match.group(2)
                else:
                    section_id = ""
                    section_title = title
                
                entries.append({
                    'section_id': section_id,
                    'title': section_title,
                    'page': page,
                    'level': level,
                    'raw_title': title
                })
            
            return entries
        except Exception as e:
            print(f"Error extracting TOC: {e}")
            return []
    
    def build_hierarchy(self, entries):
        """Build parent-child relationships for TOC entries"""
        result = []
        parent_stack = []
        
        for entry in entries:
            section_id = entry['section_id']
            if not section_id:
                continue
            
            level = len(section_id.split('.'))
            
            while len(parent_stack) >= level:
                parent_stack.pop()
            
            parent_id = parent_stack[-1] if parent_stack else None
            full_path = f"{section_id} {entry['title']}"
            
            toc_entry = {
                'doc_title': self.doc_title,
                'section_id': section_id,
                'title': entry['title'],
                'page': entry['page'],
                'level': level,
                'parent_id': parent_id,
                'full_path': full_path
            }
            
            result.append(toc_entry)
            parent_stack.append(section_id)
        
        return result
    
    def save_jsonl(self, entries, filename):
        """Save entries to JSONL file"""
        with open(filename, 'w', encoding='utf-8') as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        print(f"Saved {len(entries)} entries to {filename}")