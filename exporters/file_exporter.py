"""
File Export Facade - Unified Export Interface
"""

from typing import List
from models import TOCEntry, ContentEntry
from .jsonl_exporter import JSONLExporter
from .report_exporter import ReportExporter
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['FileExporter']


class FileExporter:
    """Unified file export facade with modular exporters"""
    
    def __init__(self):
        """Initialize with specialized exporters for better encapsulation"""
        self._jsonl_exporter = JSONLExporter()
        self._report_exporter = ReportExporter()
    
    def export_toc(self, entries: List[TOCEntry], filename: str = "usb_pd_toc.jsonl") -> bool:
        """Export TOC structure using JSONL exporter"""
        return self._jsonl_exporter.export_toc(entries, filename)
    
    def export_content(self, entries: List[ContentEntry], filename: str = "usb_pd_spec.jsonl") -> bool:
        """Export full content using JSONL exporter"""
        return self._jsonl_exporter.export_content(entries, filename)
    
    def export_validation_excel(self, toc_entries: List[TOCEntry], filename: str = "validation_report.xlsx") -> bool:
        """Export Excel validation report using report exporter"""
        return self._report_exporter.export_validation_excel(toc_entries, filename)
    
    def export_validation_json(self, toc_entries: List[TOCEntry], filename: str = "validation_report.json") -> bool:
        """Export JSON validation report using report exporter"""
        return self._report_exporter.export_validation_json(toc_entries, filename)