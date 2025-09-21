"""Configuration loader for USB PD Parser"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Configuration manager with YAML support"""
    
    def __init__(self, config_path: str = "config.yml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            return self._get_defaults()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            return self._merge_with_defaults(config)
        except Exception:
            return self._get_defaults()
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            'parser': {
                'max_pages': None,
                'max_text_length': 300,
                'doc_title': 'USB PD'
            },
            'search': {
                'max_results': 10,
                'min_query_length': 2
            },
            'files': {
                'default_pdf': 'assets/USB_PD_R3_2 V1.1 2024-10.pdf',
                'toc_output': 'usb_pd_toc.jsonl',
                'content_output': 'usb_pd_spec.jsonl'
            },
            'performance': {
                'parallel_export': True,
                'encoding': 'utf-8'
            }
        }
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults"""
        defaults = self._get_defaults()
        for section, values in config.items():
            if section in defaults and isinstance(values, dict):
                defaults[section].update(values)
        return defaults
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(section, {}).get(key, default)
    
    @property
    def parser(self) -> Dict[str, Any]:
        return self._config.get('parser', {})
    
    @property
    def search(self) -> Dict[str, Any]:
        return self._config.get('search', {})
    
    @property
    def files(self) -> Dict[str, Any]:
        return self._config.get('files', {})
    
    @property
    def performance(self) -> Dict[str, Any]:
        return self._config.get('performance', {})

# Global config instance
config = Config()