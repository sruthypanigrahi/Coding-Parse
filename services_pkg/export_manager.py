"""
Export Management Logic
"""

from typing import Dict, Any, List
from models import TOCEntry, ContentEntry
from constants import TOC_OUTPUT_FILE, CONTENT_OUTPUT_FILE
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['ExportManager']


class ExportManager:
    """Manages export operations with proper error handling"""
    
    def __init__(self, service_factory):
        """Initialize with service factory for dependency injection"""
        self._service_factory = service_factory
    
    def export_all_results(self, toc_entries: List[TOCEntry], content_entries: List[ContentEntry]) -> Dict[str, Any]:
        """Export all required files using factory pattern"""
        try:
            exporter = self._service_factory.create_exporter()
            
            # Export all 4 required files
            export_operations = [
                exporter.export_toc(toc_entries, TOC_OUTPUT_FILE),
                exporter.export_content(content_entries, CONTENT_OUTPUT_FILE),
                exporter.export_validation_excel(toc_entries),
                exporter.export_validation_json(toc_entries)
            ]
            
            success = all(export_operations)
            
            return {
                'success': success, 
                'error': 'Export failed' if not success else None
            }
            
        except (OSError, PermissionError) as e:
            logger.error(f"File system error during export: {e}")
            return {'success': False, 'error': 'Export failed due to file system error'}
        except Exception as e:
            logger.error(f"Unexpected export error: {e}")
            return {'success': False, 'error': 'Export operation failed'}