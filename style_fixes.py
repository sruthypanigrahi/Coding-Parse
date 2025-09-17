#!/usr/bin/env python3
"""
Style fixes script to automatically fix PEP8 line length issues
"""

import os
import re

def fix_long_lines():
    """Fix long lines in all Python files"""
    
    # Files to fix
    files_to_fix = [
        'content_extractor.py',
        'parser_service.py', 
        'pdf_parser.py',
        'filter.py',
        'models.py',
        'search.py',
        'validators.py',
        'performance_cache.py'
    ]
    
    for filename in files_to_fix:
        if os.path.exists(filename):
            print(f"Fixing {filename}...")
            fix_file_lines(filename)

def fix_file_lines(filename):
    """Fix long lines in a specific file"""
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    for i, line in enumerate(lines):
        if len(line.rstrip()) > 79:
            # Apply specific fixes based on patterns
            fixed_line = apply_line_fixes(line)
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

def apply_line_fixes(line):
    """Apply specific fixes to long lines"""
    
    # Fix long import lines
    if 'from models import' in line and len(line) > 79:
        return line.replace(
            'from models import TOCEntry, ContentEntry, ImageInfo, TableInfo, ProcessingStats',
            'from models import (\n    TOCEntry, ContentEntry, ImageInfo, TableInfo, ProcessingStats\n)'
        )
    
    # Fix long logger lines
    if 'logger.info(f"' in line and len(line) > 79:
        # Split logger lines
        parts = line.split('logger.info(f"', 1)
        if len(parts) == 2:
            indent = parts[0]
            message = parts[1].rstrip(')\n')
            return f'{indent}logger.info(\n{indent}    f"{message}\n{indent})\n'
    
    # Fix long function definitions
    if 'def ' in line and '(' in line and ')' in line and len(line) > 79:
        # Split function parameters
        if line.count(',') >= 2:
            parts = line.split('(', 1)
            if len(parts) == 2:
                func_part = parts[0] + '('
                params_part = parts[1]
                # Split parameters
                params = params_part.replace(') ->', '\n    ) ->').replace(', ', ',\n        ')
                return func_part + '\n        ' + params
    
    # Return original line if no fixes applied
    return line

if __name__ == '__main__':
    fix_long_lines()
    print("Style fixes completed!")