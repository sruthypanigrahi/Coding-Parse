import yaml
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent / "application.yml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Load configuration
CONFIG = load_config()

# Used constants only
ASSETS_FOLDER = CONFIG['folders']['assets']
RAW_OUTPUT_FILE = CONFIG['files']['raw_output']
CLEAN_OUTPUT_FILE = CONFIG['files']['clean_output']
DEFAULT_PDF_FILE = CONFIG['files']['default_pdf']
DOC_TITLE = CONFIG['parser']['doc_title']
SECTION_PATTERN = CONFIG['patterns']['section_regex']
SECTION_TITLE_PATTERN = CONFIG['patterns']['section_title_regex']