import json
import re
from constants import SECTION_PATTERN


def filter_numbered_sections(input_file: str, output_file: str):
    section_pattern = re.compile(SECTION_PATTERN)
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        filtered_count = 0
        for line in infile:
            try:
                entry = json.loads(line.strip())
                section_id = entry.get('section_id', '')
                
                if section_id and section_pattern.match(section_id):
                    if not entry.get('parent_id'):
                        entry['parent_id'] = None
                    outfile.write(json.dumps(entry, ensure_ascii=False) + '\n')
                    filtered_count += 1
            except json.JSONDecodeError:
                continue
    
    print(f"Filtered {filtered_count} numbered sections")
    return filtered_count