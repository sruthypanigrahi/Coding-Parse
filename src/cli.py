from .core import ParserService, SearchService
from .utils import SecurePathValidator
from .config import config

def handle_parse(pdf_file=None):
    try:
        pdf_file = pdf_file or config.files['default_pdf']
        result = ParserService().parse_pdf(pdf_file)
        
        if result['success']:
            print(f"[OK] TOC: {len(result['toc_data'])}, Content: {len(result['content_data'])}")
            return 0
        print(f"[ERROR] {result['error']}")
        return 1
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}")
        return 1

def handle_search(query):
    try:
        result = SearchService().search(query)
        
        if result['success']:
            matches = result['matches']
            if matches:
                print(f"Found {len(matches)} results:")
                for i, m in enumerate(matches, 1):
                    print(f"{i}. {m['title']} (Page {m['page']})")
            else:
                print("No results found")
            return 0
        print(f"[ERROR] {result['error']}")
        return 1
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}")
        return 1

def handle_validate():
    try:
        validator = SecurePathValidator()
        missing = []
        
        for f in [config.files['toc_output'], config.files['content_output']]:
            try:
                if not validator.validate_and_resolve(f).exists():
                    missing.append(f)
            except:
                missing.append(f)
        
        if missing:
            print(f"[ERROR] Missing files: {', '.join(missing)}")
            return 1
        
        print("[OK] All required files present")
        return 0
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}")
        return 1