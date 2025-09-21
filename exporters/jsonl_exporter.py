"""
JSONL Export Functionality
"""

import json
from typing import List
from models import TOCEntry, ContentEntry
from .base_exporter import BaseExporter
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['JSONLExporter']


class JSONLExporter(BaseExporter):
    """JSONL file export functionality"""
    
    def export_toc(self, entries: List[TOCEntry], filename: str = "usb_pd_toc.jsonl") -> bool:
        """Export TOC structure to JSONL with all required fields"""
        # Secure path validation - resolve and validate within working directory
        from pathlib import Path
        safe_path = Path(filename).resolve()
        cwd = Path.cwd().resolve()
        try:
            safe_path.relative_to(cwd)
        except ValueError:
            logger.error(f"Path outside working directory: {filename}")
            return False
        safe_filename = safe_path
        
        try:
            # Batch serialize for performance
            json_lines = []
            for entry in entries:
                data = {
                    'doc_title': entry.doc_title or "USB Power Delivery Specification",
                    'section_id': entry.section_id or "",
                    'title': entry.title or "",
                    'page': entry.page or 0,
                    'level': entry.level or 0,
                    'parent_id': entry.parent_id or None,
                    'full_path': entry.full_path or ""
                }
                json_lines.append(json.dumps(data, ensure_ascii=False))
            
            with open(safe_filename, 'w', encoding='utf-8') as f:
                # Optimized writing to avoid large string concatenation
                for line in json_lines:
                    f.write(line + '\n')
            
            logger.info(f"Exported {len(entries)} TOC entries to {filename}")
            return True
        except (OSError, PermissionError, TypeError) as e:
            logger.error(f"Failed to export TOC: {e}")
            return False
    
    def export_content(self, entries: List[ContentEntry], filename: str = "usb_pd_spec.jsonl") -> bool:
        """Export full content to JSONL with optimized batch processing"""
        # Secure path validation - resolve and validate within working directory
        from pathlib import Path
        safe_path = Path(filename).resolve()
        cwd = Path.cwd().resolve()
        try:
            safe_path.relative_to(cwd)
        except ValueError:
            logger.error(f"Path outside working directory: {filename}")
            return False
        safe_filename = safe_path
        
        try:
            # Batch serialize for performance
            json_lines = []
            for entry in entries:
                # Optimized attribute access with try/except for performance
                images = []
                tables = []
                
                if entry.images:
                    for img in entry.images:
                        try:
                            images.append(img.to_dict())
                        except AttributeError:
                            images.append(img)
                            
                if entry.tables:
                    for tbl in entry.tables:
                        try:
                            tables.append(tbl.to_dict())
                        except AttributeError:
                            tables.append(tbl)
                
                data = {
                    'doc_title': entry.doc_title or "USB Power Delivery Specification",
                    'section_id': entry.section_id or "",
                    'title': entry.title or "",
                    'page_range': entry.page_range or "",
                    'content': entry.content or "",
                    'content_type': entry.content_type or "text",
                    'has_content': bool(entry.has_content),
                    'word_count': entry.word_count or 0,
                    'images': images,
                    'tables': tables
                }
                json_lines.append(json.dumps(data, ensure_ascii=False))
            
            with open(safe_filename, 'w', encoding='utf-8') as f:
                # Optimized writing to avoid large string concatenation
                for line in json_lines:
                    f.write(line + '\n')
            
            logger.info(f"Exported {len(entries)} content entries to {filename}")
            return True
        except (OSError, PermissionError, TypeError) as e:
            logger.error(f"Failed to export content: {e}")
            return False