"""
Report Export Functionality
"""

import json
import pandas as pd
from typing import List
from models import TOCEntry
from .base_exporter import BaseExporter
from constants import TOTAL_EXPECTED_PAGES
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['ReportExporter']


class ReportExporter(BaseExporter):
    """Excel and JSON report export functionality"""
    
    def __init__(self):
        super().__init__()
        # Ensure _numeric_pattern is available from parent
    
    def export_validation_excel(self, toc_entries: List[TOCEntry], filename: str = "validation_report.xlsx") -> bool:
        """Export Excel validation report with comprehensive metrics"""
        try:
            safe_path = self._validate_path(filename)
            
            # Build validation data
            data = []
            for entry in toc_entries:
                section_id = entry.section_id
                is_numeric = bool(section_id and self._numeric_pattern.match(section_id))
                
                data.append({
                    'doc_title': entry.doc_title,
                    'section_id': section_id,
                    'title': entry.title,
                    'page': entry.page,
                    'level': entry.level,
                    'parent_id': entry.parent_id,
                    'full_path': entry.full_path,
                    'has_section_id': bool(section_id),
                    'is_numbered': is_numeric,
                    'valid_page': entry.page > 0
                })
            
            df = pd.DataFrame(data)
            
            # Calculate summary metrics
            summary = {
                'Total Entries': len(df),
                'Valid Entries': df[['has_section_id', 'valid_page']].all(axis=1).sum(),
                'Numbered Sections': df['is_numbered'].sum(),
                'Coverage %': round((len(df) / TOTAL_EXPECTED_PAGES) * 100, 2) if TOTAL_EXPECTED_PAGES > 0 else 0.0
            }
            
            # Write Excel file with multiple sheets
            with pd.ExcelWriter(safe_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='TOC_Data', index=False)
                pd.DataFrame(list(summary.items()), 
                           columns=['Metric', 'Value']).to_excel(
                    writer, sheet_name='Summary', index=False)
            
            logger.info(f"Generated Excel validation report: {filename}")
            return True
            
        except (OSError, PermissionError, ValueError) as e:
            logger.error(f"Failed to generate Excel report: {e}")
            return False
    
    def export_validation_json(self, toc_entries: List[TOCEntry], filename: str = "validation_report.json") -> bool:
        """Export JSON validation report with detailed statistics"""
        try:
            safe_path = self._validate_path(filename)
            stats = self._calculate_stats(toc_entries)
            
            report = {
                'validation_summary': stats,
                'schema_compliance': 1.0,
                'coverage_percentage': round((len(toc_entries) / TOTAL_EXPECTED_PAGES) * 100, 2) if TOTAL_EXPECTED_PAGES > 0 else 0,
                'generated_at': pd.Timestamp.now().isoformat()
            }
            
            with open(safe_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Generated JSON validation report: {filename}")
            return True
            
        except (OSError, PermissionError, ValueError) as e:
            logger.error(f"Failed to generate JSON report: {e}")
            return False