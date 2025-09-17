import yaml
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent / "application.yml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Load configuration
CONFIG = load_config()

# Folder paths
ASSETS_FOLDER = CONFIG['folders']['assets']

# File paths
TOC_OUTPUT_FILE = CONFIG['files']['toc_output']
CONTENT_OUTPUT_FILE = CONFIG['files']['content_output']
DEFAULT_PDF_FILE = CONFIG['files']['default_pdf']

# Parser settings
DOC_TITLE = CONFIG['parser']['doc_title']
PROGRESS_INTERVAL = CONFIG['parser']['progress_interval']
CONTENT_LIMIT = CONFIG['parser']['content_limit']
MAX_WORKERS = CONFIG['parser'].get('max_workers', 4)
PARALLEL_THRESHOLD = CONFIG['parser'].get('parallel_threshold', 50)

# Regex patterns
SECTION_PATTERN = CONFIG['patterns']['section_regex']
SECTION_TITLE_PATTERN = CONFIG['patterns']['section_title_regex']