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
        """Export TOC structure to JSONL"""
        try:
            safe_path = self._validate_path(filename)
            with open(safe_path, 'w', encoding='utf-8') as f:
                for entry in entries:
                    data = {
                        'doc_title': entry.doc_title,
                        'section_id': entry.section_id,
                        'title': entry.title,
                        'page': entry.page,
                        'level': entry.level,
                        'parent_id': entry.parent_id,
                        'full_path': entry.full_path
                    }
                    f.write(json.dumps(data, ensure_ascii=False) + '\n')
            logger.info(f"Exported {len(entries)} TOC entries to {filename}")
            return True
        except (OSError, PermissionError, ValueError) as e:
            logger.error(f"Failed to export TOC: {e}")
            return False
    
    def export_content(self, entries: List[ContentEntry], filename: str = "usb_pd_spec.jsonl") -> bool:
        """Export full content to JSONL"""
        try:
            safe_path = self._validate_path(filename)
            with open(safe_path, 'w', encoding='utf-8') as f:
                for entry in entries:
                    data = {
                        'doc_title': entry.doc_title,
                        'section_id': entry.section_id,
                        'title': entry.title,
                        'page_range': entry.page_range,
                        'content': entry.content,
                        'content_type': entry.content_type,
                        'has_content': entry.has_content,
                        'word_count': entry.word_count,
                        'images': [img.to_dict() if hasattr(img, 'to_dict') else img for img in entry.images if img],
                        'tables': [tbl.to_dict() if hasattr(tbl, 'to_dict') else tbl for tbl in entry.tables if tbl]
                    }
                    f.write(json.dumps(data, ensure_ascii=False) + '\n')
            logger.info(f"Exported {len(entries)} content entries to {filename}")
            return True
        except (OSError, PermissionError, ValueError) as e:
            logger.error(f"Failed to export content: {e}")
            return False