import json
import re
from pathlib import Path
from typing import List, Dict, Optional

try:
    import fitz  
except ImportError:
    raise ImportError("Required packages not installed. Run: pip install pymupdf")


class USBPDParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.doc_title = "USB Power Delivery Specification"
        
    def extract_outline_bookmarks(self) -> List[Dict]:
        try:
            doc = fitz.open(self.pdf_path)
            outline = doc.get_toc()
            doc.close()
            
            if not outline:
                return []
                
            entries = []
            for level, title, page in outline:
                clean_title = title.strip()
                section_match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)', clean_title)
                
                if section_match:
                    section_id = section_match.group(1)
                    title_text = section_match.group(2)
                else:
                    section_id = ""
                    title_text = clean_title
                
                entries.append({
                    'section_id': section_id,
                    'title': title_text,
                    'page': page,
                    'level': level,
                    'raw_title': clean_title
                })
            
            return entries
            
        except Exception as e:
            print(f"Bookmark extraction failed: {e}")
            return []
    
    def _calculate_hierarchy(self, entries: List[Dict]) -> List[Dict]:
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
            
            processed_entry = {
                'doc_title': self.doc_title,
                'section_id': section_id,
                'title': entry['title'],
                'page': entry['page'],
                'level': level,
                'parent_id': parent_id,
                'full_path': full_path
            }
            
            result.append(processed_entry)
            parent_stack.append(section_id)
        
        return result
    
    def parse(self) -> List[Dict]:
        print(f"Parsing {self.pdf_path.name}...")
        entries = self.extract_outline_bookmarks()
        
        if entries:
            print(f"Extracted {len(entries)} entries from bookmarks")
            processed = self._calculate_hierarchy(entries)
            return processed
        else:
            print("No ToC found in document")
            return []
    
    def save_jsonl(self, entries: List[Dict], output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        print(f"Saved {len(entries)} entries to {output_path}")


def filter_numbered_sections(input_file: str, output_file: str):
    section_pattern = re.compile(r'^\d+(\.\d+)*$')
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        filtered_count = 0
        for line in infile:
            try:
                entry = json.loads(line.strip())
                section_id = entry.get('section_id', '')
                
                if section_id and section_pattern.match(section_id):
                    if not entry.get('parent_id'):
                        entry['parent_id'] = None
                    outfile.write(json.dumps(entry, ensure_ascii=False) + '\n')
                    filtered_count += 1
            except json.JSONDecodeError:
                continue
    
    print(f"Filtered {filtered_count} numbered sections")
    return filtered_count


def search_toc(jsonl_file: str, query: str) -> List[Dict]:
    matches = []
    query_lower = query.lower()
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line.strip())
            if (query_lower in entry['title'].lower() or 
                query_lower in entry.get('section_id', '')):
                matches.append(entry)
    
    return matches