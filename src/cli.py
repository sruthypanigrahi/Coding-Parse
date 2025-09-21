from .core import ParserService, SearchService
from .utils import SecurePathValidator
from .config import config

def handle_parse(pdf_file=None):
    """Parse PDF file and display statistics including image count."""
    try:
        pdf_file = pdf_file or config.files['default_pdf']
        print(f"Parsing: {pdf_file}")
        result = ParserService().parse_pdf(pdf_file)
        
        if result['success']:
            # Calculate image statistics
            total_images = sum(item.get('image_count', 0) for item in result['content_data'])
            pages_with_images = sum(1 for item in result['content_data'] if item.get('image_count', 0) > 0)
            
            print(f"\n✓ Successfully parsed PDF")
            print(f"  • Table of Contents: {len(result['toc_data'])} entries")
            print(f"  • Content Pages: {len(result['content_data'])} pages")
            print(f"  • Total Images: {total_images} images")
            print(f"  • Pages with Images: {pages_with_images} pages")
            print(f"  • Files Created: {', '.join(result['files_created'])}")
            print(f"\n[COMPLETE] PDF parsing finished successfully")
            return 0
        print(f"[ERROR] {result['error']}")
        return 1
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}")
        return 1

def handle_search(query):
    """Search through parsed content with unlimited results."""
    try:
        print(f"Searching for: '{query}'")
        result = SearchService().search(query)
        
        if result['success']:
            matches = result['matches']
            total = result.get('total_found', len(matches))
            
            if matches:
                print(f"\n✓ Found {total} result{'s' if total != 1 else ''}:")
                print("-" * 60)
                for i, m in enumerate(matches, 1):
                    print(f"{i:3d}. {m['title']} (Page {m['page']})")
                    if m.get('content'):
                        print(f"     {m['content'][:80]}...")
                print("-" * 60)
                print(f"[COMPLETE] Search finished - {total} result{'s' if total != 1 else ''} found")
            else:
                print(f"\n[NO RESULTS] No matches found for '{query}'")
            return 0
        print(f"[ERROR] {result['error']}")
        return 1
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}")
        return 1

def handle_validate():
    """Validate that required output files exist."""
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