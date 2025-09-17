#!/usr/bin/env python3
"""
Validation Report Generator - Creates XLS/JSON comparing TOC vs parsed output
"""

import json
import fitz
from pathlib import Path
from typing import Dict, List, Any
from logger_config import setup_logger

logger = setup_logger(__name__)


class ValidationReportGenerator:
    """Generate validation report comparing parsed TOC with source PDF TOC"""
    
    def __init__(self, pdf_path: str, toc_file: str):
        self.pdf_path = Path(pdf_path)
        self.toc_file = Path(toc_file)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        logger.info("Starting validation report generation")
        
        # Load parsed TOC
        parsed_toc = self._load_parsed_toc()
        
        # Extract source TOC from PDF
        source_toc = self._extract_source_toc()
        
        # Compare and validate
        validation_results = self._compare_tocs(parsed_toc, source_toc)
        
        # Save reports
        self._save_json_report(validation_results)
        self._save_excel_report(validation_results)
        
        logger.info("Validation report generated successfully")
        return validation_results
    
    def _load_parsed_toc(self) -> List[Dict]:
        """Load parsed TOC from JSONL file"""
        entries = []
        if not self.toc_file.exists():
            logger.warning(f"TOC file not found: {self.toc_file}")
            return entries
        
        with open(self.toc_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entries.append(json.loads(line.strip()))
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping malformed JSON: {e}")
        
        return entries
    
    def _extract_source_toc(self) -> List[Dict]:
        """Extract TOC directly from PDF for comparison"""
        entries = []
        try:
            with fitz.open(self.pdf_path) as doc:
                toc = doc.get_toc()
                for level, title, page in toc:
                    entries.append({
                        'level': level,
                        'title': title.strip(),
                        'page': page
                    })
        except Exception as e:
            logger.error(f"Failed to extract source TOC: {e}")
        
        return entries
    
    def _compare_tocs(self, parsed: List[Dict], source: List[Dict]) -> Dict:
        """Compare parsed TOC with source TOC"""
        results = {
            'total_source_entries': len(source),
            'total_parsed_entries': len(parsed),
            'matched_entries': 0,
            'missing_entries': [],
            'accuracy_percentage': 0.0,
            'detailed_comparison': []
        }
        
        # Create lookup for parsed entries
        parsed_lookup = {entry.get('title', ''): entry for entry in parsed}
        
        # Check each source entry
        for source_entry in source:
            title = source_entry['title']
            if title in parsed_lookup:
                results['matched_entries'] += 1
                parsed_entry = parsed_lookup[title]
                
                comparison = {
                    'title': title,
                    'source_page': source_entry['page'],
                    'parsed_page': parsed_entry.get('page', 0),
                    'page_match': source_entry['page'] == parsed_entry.get('page',
                        0),
                    'status': 'MATCHED'
                }
            else:
                results['missing_entries'].append(source_entry)
                comparison = {
                    'title': title,
                    'source_page': source_entry['page'],
                    'parsed_page': None,
                    'page_match': False,
                    'status': 'MISSING'
                }
            
            results['detailed_comparison'].append(comparison)
        
        # Calculate accuracy
        if results['total_source_entries'] > 0:
            results['accuracy_percentage'] = (
                results['matched_entries'] / results['total_source_entries']
            ) * 100
        
        return results
    
    def _save_json_report(self, results: Dict) -> None:
        """Save validation report as JSON file"""
        with open('validation_report.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info("JSON report saved: validation_report.json")
    
    def _save_excel_report(self, results: Dict) -> None:
        """Save validation report as Excel file (simplified CSV format)"""
        try:
            # Create CSV format for Excel compatibility
            csv_content = []
            csv_content.append("Metric,Value")
            csv_content.append(
                f"Total Source Entries,{results['total_source_entries']}"
            )
            csv_content.append(
                f"Total Parsed Entries,{results['total_parsed_entries']}"
            )
            csv_content.append(
                f"Matched Entries,{results['matched_entries']}"
            )
            csv_content.append(
                f"Missing Entries,{len(results['missing_entries'])}"
            )
            csv_content.append(
                f"Accuracy Percentage,{results['accuracy_percentage']:.2f}%"
            )
            csv_content.append("")
            csv_content.append(
                "Title,Source Page,Parsed Page,Page Match,Status"
            )
            
            for comparison in results['detailed_comparison']:
                csv_content.append(
                    f"\"{comparison['title']}\","
                    f"{comparison['source_page']},"
                    f"{comparison.get('parsed_page', 'N/A')},"
                    f"{comparison['page_match']},"
                    f"{comparison['status']}"
                )
            
            with open('validation_report.csv', 'w', encoding='utf-8') as f:
                f.write('\n'.join(csv_content))
            
            logger.info("Excel-compatible report saved: validation_report.csv")
            
        except Exception as e:
            logger.error(f"Failed to save Excel report: {e}")


def generate_validation_report(pdf_path: str = None, toc_file: str = None):
    """Generate validation report for parsed TOC"""
    from constants import ASSETS_FOLDER, DEFAULT_PDF_FILE, TOC_OUTPUT_FILE
    
    if not pdf_path:
        pdf_path = Path(ASSETS_FOLDER) / DEFAULT_PDF_FILE
    if not toc_file:
        toc_file = TOC_OUTPUT_FILE
    
    generator = ValidationReportGenerator(pdf_path, toc_file)
    return generator.generate_report()


if __name__ == '__main__':
    generate_validation_report()