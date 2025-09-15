import json
from pathlib import Path
from constants import TOC_OUTPUT_FILE


def search_toc(query):
    """Search TOC entries"""
    if not Path(TOC_OUTPUT_FILE).exists():
        print(f"Error: {TOC_OUTPUT_FILE} not found. Run parse first.")
        return
    
    matches = []
    query_lower = query.lower()
    
    with open(TOC_OUTPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line.strip())
            if (query_lower in entry['title'].lower() or 
                query_lower in entry.get('section_id', '')):
                matches.append(entry)
    
    if matches:
        print(f"Found {len(matches)} matches for '{query}':\n")
        for match in matches:
            print(f"{match['section_id']} {match['title']} (page {match['page']})")
    else:
        print(f"No matches found for '{query}'")