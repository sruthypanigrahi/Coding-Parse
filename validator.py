"""Validation and report generation"""
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from constants import TOC_OUTPUT_FILE
from logger_config import setup_logger

logger = setup_logger(__name__)


class ValidationReport:
    """Generate validation reports comparing TOC vs parsed output"""
    
    def __init__(self):
        self.toc_data = []
        self.validation_results = []
    
    def load_toc_data(self) -> bool:
        """Load TOC data from JSONL file"""
        try:
            with open(TOC_OUTPUT_FILE, 'r', encoding='utf-8') as f:
                self.toc_data = [json.loads(line) for line in f]
            logger.info(f"Loaded {len(self.toc_data)} TOC entries")
            return True
        except Exception as e:
            logger.error(f"Failed to load TOC data: {e}")
            return False
    
    def validate_entries(self) -> Dict[str, Any]:
        """Validate TOC entries and generate statistics"""
        if not self.toc_data:
            return {'error': 'No TOC data loaded'}
        
        stats = {
            'total_entries': len(self.toc_data),
            'numbered_sections': 0,
            'missing_fields': 0,
            'valid_entries': 0,
            'coverage_percentage': 0
        }
        
        required_fields = ['section_id', 'title', 'page', 'level']
        
        for entry in self.toc_data:
            # Check required fields
            missing = [f for f in required_fields if not entry.get(f)]
            if missing:
                stats['missing_fields'] += 1
            else:
                stats['valid_entries'] += 1
            
            # Check if numbered section
            if entry.get('section_id') and entry['section_id'].replace('.', '').isdigit():
                stats['numbered_sections'] += 1
        
        stats['coverage_percentage'] = (stats['valid_entries'] / stats['total_entries']) * 100
        return stats
    
    def generate_excel_report(self, filename: str = 'validation_report.xlsx'):
        """Generate Excel validation report"""
        if not self.toc_data:
            logger.error("No TOC data to generate report")
            return False
        
        try:
            # Create DataFrame
            df = pd.DataFrame(self.toc_data)
            
            # Add validation columns
            df['has_section_id'] = df['section_id'].notna() & (df['section_id'] != '')
            df['is_numbered'] = df['section_id'].str.match(r'^\d+(\.\d+)*$', na=False)
            df['has_title'] = df['title'].notna() & (df['title'] != '')
            df['valid_page'] = df['page'] > 0
            
            # Create summary sheet
            summary_data = {
                'Metric': [
                    'Total Entries',
                    'Valid Entries',
                    'Numbered Sections',
                    'Missing Section IDs',
                    'Missing Titles',
                    'Invalid Pages'
                ],
                'Count': [
                    len(df),
                    df[['has_section_id', 'has_title', 'valid_page']].all(axis=1).sum(),
                    df['is_numbered'].sum(),
                    (~df['has_section_id']).sum(),
                    (~df['has_title']).sum(),
                    (~df['valid_page']).sum()
                ]
            }
            
            # Write to Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='TOC_Data', index=False)
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            logger.info(f"Generated Excel report: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate Excel report: {e}")
            return False
    
    def generate_json_report(self, filename: str = 'validation_report.json'):
        """Generate JSON validation report"""
        stats = self.validate_entries()
        
        report = {
            'validation_summary': stats,
            'sample_entries': self.toc_data[:5] if self.toc_data else [],
            'generated_at': pd.Timestamp.now().isoformat()
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Generated JSON report: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate JSON report: {e}")
            return False


def generate_validation_reports():
    """Generate both Excel and JSON validation reports"""
    validator = ValidationReport()
    
    if not validator.load_toc_data():
        return False
    
    excel_success = validator.generate_excel_report()
    json_success = validator.generate_json_report()
    
    return excel_success and json_success