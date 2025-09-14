import json
from typing import List, Dict


def search_toc(jsonl_file: str, query: str) -> List[Dict]:
    matches = []
    query_lower = query.lower()
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line.strip())
            if (query_lower in entry['title'].lower() or 
                query_lower in entry.get('section_id', '')):
                matches.append(entry)
    
    return matches