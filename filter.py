import re
from constants import SECTION_PATTERN


def filter_numbered_sections(entries):
    """Keep only entries with numeric section IDs"""
    pattern = re.compile(SECTION_PATTERN)
    filtered = []
    
    for entry in entries:
        section_id = entry.get('section_id', '')
        if section_id and pattern.match(section_id):
            if not entry.get('parent_id'):
                entry['parent_id'] = None
            filtered.append(entry)
    
    return filtered