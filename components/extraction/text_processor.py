"""Text processing utilities"""
from typing import List
from constants import CONTENT_LIMIT

class TextProcessor:
    """Handles text processing and truncation"""
    
    @staticmethod
    def truncate_content(content: str, limit: int = CONTENT_LIMIT) -> str:
        """Truncate content with word boundary preservation"""
        if len(content) <= limit:
            return content
        
        truncated = content[:limit]
        if ' ' in truncated:
            result = truncated.rsplit(' ', 1)[0]
            return result if result.strip() else truncated
        return truncated
    
    @staticmethod
    def join_page_texts(texts: List[str]) -> str:
        """Join page texts efficiently"""
        return '\n'.join(text.strip() for text in texts if text.strip())