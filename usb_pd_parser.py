import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import argparse

try:
    import fitz  
except ImportError:
    print("Required packages not installed. Run: pip install pymupdf")
    sys.exit(1)


class USBPDParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.doc_title = "USB Power Delivery Specification"
        self.toc_entries = []
        
    def extract_outline_bookmarks(self) -> List[Dict]:
        
        try:
            doc = fitz.open(self.pdf_path)
            outline = doc.get_toc()
            doc.close()
            
            if not outline:
                return []
                
            entries = []
            for level, title, page in outline:
                # Clean title and extract section ID
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
    
    def extract_printed_toc(self) -> List[Dict]:
        """Fallback: Parse printed Table of Contents pages"""
        try:
            doc = fitz.open(self.pdf_path)
            entries = []
            
            # Search for ToC pages (typically in first 20 pages)
            for page_num in range(min(20, len(doc))):
                page = doc[page_num]
                text = page.get_text()
                
                # Look for ToC indicators
                if any(indicator in text.lower() for indicator in ['table of contents', 'contents']):
                    entries.extend(self._parse_toc_text(text, page_num + 1))
            
            doc.close()
            return entries
            
        except Exception as e:
            print(f"Printed ToC extraction failed: {e}")
            return []
    
    def _parse_toc_text(self, text: str, source_page: int) -> List[Dict]:
        """Parse ToC text and extract entries"""
        entries = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Match patterns like "2.1.3 Section Title ... 45"
            pattern = r'^(\d+(?:\.\d+)*)\s+(.+?)\s+\.{2,}\s*(\d+)$'
            match = re.match(pattern, line)
            
            if match:
                section_id = match.group(1)
                title = match.group(2).strip()
                page = int(match.group(3))
                level = len(section_id.split('.'))
                
                entries.append({
                    'section_id': section_id,
                    'title': title,
                    'page': page,
                    'level': level,
                    'raw_title': f"{section_id} {title}"
                })
        
        return entries
    
    def _calculate_hierarchy(self, entries: List[Dict]) -> List[Dict]:
        """Calculate parent_id and full_path for each entry"""
        result = []
        parent_stack = []
        
        for entry in entries:
            section_id = entry['section_id']
            if not section_id:
                continue
                
            # Calculate level from section_id dots
            level = len(section_id.split('.'))
            
            # Adjust parent stack based on current level
            while len(parent_stack) >= level:
                parent_stack.pop()
            
            # Determine parent
            parent_id = parent_stack[-1] if parent_stack else None
            
            # Build full path
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
    
    def _get_title_by_id(self, section_id: str, entries: List[Dict]) -> Optional[str]:
        """Helper to get title by section_id"""
        for entry in entries:
            if entry.get('section_id') == section_id:
                return entry.get('title')
        return None
    
    def _validate_pages(self, entries: List[Dict]) -> List[Dict]:
        """Validate and clean page numbers"""
        try:
            doc = fitz.open(self.pdf_path)
            max_pages = len(doc)
            doc.close()
            
            for entry in entries:
                page = entry.get('page', 0)
                if not isinstance(page, int) or page < 1 or page > max_pages:
                    entry['page'] = 1  # Default to page 1 if invalid
                    
        except Exception:
            pass  # Keep original page numbers if validation fails
            
        return entries
    
    def parse(self) -> List[Dict]:
        """Main parsing method with fallback logic"""
        print(f"Parsing {self.pdf_path.name}...")
        
        # Try outline/bookmarks first
        entries = self.extract_outline_bookmarks()
        
        if entries:
            print(f"Extracted {len(entries)} entries from bookmarks")
        else:
            print("No bookmarks found, trying printed ToC...")
            entries = self.extract_printed_toc()
            
            if entries:
                print(f"Extracted {len(entries)} entries from printed ToC")
            else:
                print("No ToC found in document")
                return []
        
        # Process hierarchy and validate
        processed = self._calculate_hierarchy(entries)
        validated = self._validate_pages(processed)
        
        return validated
    
    def save_jsonl(self, entries: List[Dict], output_path: str):
        """Save entries to JSONL format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        print(f"Saved {len(entries)} entries to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Extract ToC from USB PD PDF')
    parser.add_argument('pdf_path', help='Path to USB PD PDF file')
    parser.add_argument('--out', default='usb_pd_spec.jsonl', 
                       help='Output JSONL file (default: usb_pd_spec.jsonl)')
    
    args = parser.parse_args()
    
    if not Path(args.pdf_path).exists():
        print(f"Error: PDF file not found: {args.pdf_path}")
        sys.exit(1)
    
    # Parse PDF
    parser_tool = USBPDParser(args.pdf_path)
    entries = parser_tool.parse()
    
    if entries:
        parser_tool.save_jsonl(entries, args.out)
        print(f"\nSample entries:")
        for entry in entries[:3]:
            print(f"  {entry['section_id']} {entry['title']} (p.{entry['page']}, level {entry['level']})")
    else:
        print("No ToC entries found")
        sys.exit(1)


if __name__ == '__main__':
    main()