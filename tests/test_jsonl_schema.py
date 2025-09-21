"""Test JSONL schema compliance"""
import json
import pytest
from pathlib import Path


class TestJSONLSchema:
    """Test JSONL output schema compliance"""
    
    def test_toc_jsonl_schema(self):
        """Test TOC JSONL has all required fields"""
        toc_file = Path("usb_pd_toc.jsonl")
        if not toc_file.exists():
            pytest.skip("TOC file not found")
        
        required_fields = {
            'doc_title', 'section_id', 'title', 'page', 
            'level', 'parent_id', 'full_path'
        }
        
        with open(toc_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        entry = json.loads(line.strip())
                        assert isinstance(entry, dict), f"Line {line_num}: Not a dict"
                        
                        # Check all required fields exist
                        missing = required_fields - set(entry.keys())
                        assert not missing, f"Line {line_num}: Missing fields {missing}"
                        
                        # Validate field types with descriptive error messages
                        assert isinstance(entry['doc_title'], str), f"Line {line_num}: doc_title must be string, got {type(entry['doc_title'])}"
                        assert isinstance(entry['section_id'], str), f"Line {line_num}: section_id must be string, got {type(entry['section_id'])}"
                        assert isinstance(entry['title'], str), f"Line {line_num}: title must be string, got {type(entry['title'])}"
                        assert isinstance(entry['page'], int), f"Line {line_num}: page must be integer, got {type(entry['page'])}"
                        assert isinstance(entry['level'], int), f"Line {line_num}: level must be integer, got {type(entry['level'])}"
                        assert entry['parent_id'] is None or isinstance(entry['parent_id'], str), f"Line {line_num}: parent_id must be None or string, got {type(entry['parent_id'])}"
                        assert isinstance(entry['full_path'], str), f"Line {line_num}: full_path must be string, got {type(entry['full_path'])}"
                        
                    except json.JSONDecodeError as e:
                        pytest.fail(f"Line {line_num}: Invalid JSON - {e}")
    
    def test_content_jsonl_schema(self):
        """Test content JSONL has all required fields"""
        content_file = Path("usb_pd_spec.jsonl")
        if not content_file.exists():
            pytest.skip("Content file not found")
        
        required_fields = {
            'doc_title', 'section_id', 'title', 'page_range', 
            'content', 'content_type', 'has_content', 'word_count',
            'images', 'tables'
        }
        
        with open(content_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        entry = json.loads(line.strip())
                        assert isinstance(entry, dict), f"Line {line_num}: Not a dict"
                        
                        # Check all required fields exist
                        missing = required_fields - set(entry.keys())
                        assert not missing, f"Line {line_num}: Missing fields {missing}"
                        
                        # Validate field types with descriptive error messages
                        assert isinstance(entry['doc_title'], str), f"Line {line_num}: doc_title must be string, got {type(entry['doc_title'])}"
                        assert isinstance(entry['section_id'], str), f"Line {line_num}: section_id must be string, got {type(entry['section_id'])}"
                        assert isinstance(entry['title'], str), f"Line {line_num}: title must be string, got {type(entry['title'])}"
                        assert isinstance(entry['page_range'], str), f"Line {line_num}: page_range must be string, got {type(entry['page_range'])}"
                        assert isinstance(entry['content'], str), f"Line {line_num}: content must be string, got {type(entry['content'])}"
                        assert isinstance(entry['content_type'], str), f"Line {line_num}: content_type must be string, got {type(entry['content_type'])}"
                        assert isinstance(entry['has_content'], bool), f"Line {line_num}: has_content must be boolean, got {type(entry['has_content'])}"
                        assert isinstance(entry['word_count'], int), f"Line {line_num}: word_count must be integer, got {type(entry['word_count'])}"
                        assert isinstance(entry['images'], list), f"Line {line_num}: images must be list, got {type(entry['images'])}"
                        assert isinstance(entry['tables'], list), f"Line {line_num}: tables must be list, got {type(entry['tables'])}"
                        
                    except json.JSONDecodeError as e:
                        pytest.fail(f"Line {line_num}: Invalid JSON - {e}")