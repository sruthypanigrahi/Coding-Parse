
import json
import re
import sys
from pathlib import Path
import argparse

def filter_numbered_sections(input_file: str, output_file: str):
    
    section_pattern = re.compile(r'^\d+(\.\d+)*$')
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        filtered_count = 0
        total_count = 0
        
        for line in infile:
            total_count += 1
            try:
                entry = json.loads(line.strip())
                section_id = entry.get('section_id', '')
                
                # Keep only entries with valid numeric section_id
                if section_id and section_pattern.match(section_id):
                    # Ensure parent_id is null if empty
                    if not entry.get('parent_id'):
                        entry['parent_id'] = None
                    
                    # Build proper full_path
                    if entry.get('section_id') and entry.get('title'):
                        entry['full_path'] = f"{entry['section_id']} {entry['title']}"
                    
                    outfile.write(json.dumps(entry, ensure_ascii=False) + '\n')
                    filtered_count += 1
                    
            except json.JSONDecodeError:
                continue
    
    print(f"Filtered {filtered_count} numbered sections from {total_count} total entries")
    print(f"Output saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Filter JSONL to keep only numbered sections')
    parser.add_argument('input_file', help='Input JSONL file')
    parser.add_argument('output_file', help='Output filtered JSONL file')
    
    args = parser.parse_args()
    
    if not Path(args.input_file).exists():
        print(f"Error: Input file not found: {args.input_file}")
        sys.exit(1)
    
    filter_numbered_sections(args.input_file, args.output_file)

if __name__ == '__main__':
    main()