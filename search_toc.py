#!/usr/bin/env python3
import json
import sys
import re

def search_toc(jsonl_file, query):
    """Search TOC entries by title or section_id"""
    matches = []
    query_lower = query.lower()
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line.strip())
            
            # Search in title and section_id
            if (query_lower in entry['title'].lower() or 
                query_lower in entry.get('section_id', '')):
                matches.append(entry)
    
    return matches

def main():
    if len(sys.argv) != 3:
        print("Usage: python search_toc.py <jsonl_file> <search_term>")
        sys.exit(1)
    
    jsonl_file = sys.argv[1]
    query = sys.argv[2]
    
    matches = search_toc(jsonl_file, query)
    
    if matches:
        print(f"Found {len(matches)} matches for '{query}':\n")
        for match in matches:
            print(f"{match['section_id']} {match['title']} (page {match['page']})")
    else:
        print(f"No matches found for '{query}'")

if __name__ == '__main__':
    main()