import os
from pathlib import Path

class SecurePathValidator:
    def __init__(self):
        self._base_dir = Path.cwd().resolve()
        self._assets_dir = self._base_dir / 'assets'
    
    def validate_and_resolve(self, filename):
        if not filename:
            raise ValueError("Empty filename")
        
        clean_name = str(filename).strip()
        
        if clean_name.startswith('assets/'):
            return self._validate_assets_path(clean_name[7:])
        else:
            return self._validate_base_path(clean_name)
    
    def _validate_assets_path(self, filename):
        if '..' in filename or '/' in filename or '\\' in filename:
            raise ValueError("Path traversal not allowed")
        
        resolved_path = (self._assets_dir / filename).resolve()
        
        try:
            resolved_path.relative_to(self._assets_dir)
        except ValueError:
            raise ValueError("Path outside assets directory")
        
        return resolved_path
    
    def _validate_base_path(self, filename):
        if '..' in filename or '/' in filename or '\\' in filename:
            raise ValueError("Path traversal not allowed")
        
        resolved_path = (self._base_dir / filename).resolve()
        
        try:
            resolved_path.relative_to(self._base_dir)
        except ValueError:
            raise ValueError("Path outside base directory")
        
        return resolved_path