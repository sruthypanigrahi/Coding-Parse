"""Parser service with all business logic"""
from pathlib import Path
from pdf_parser import PDFParser, JSONLWriter
from content_extractor import ContentExtractor
from filter import SectionFilter
from search import TOCSearcher
from constants import ASSETS_FOLDER, DEFAULT_PDF_FILE, TOC_OUTPUT_FILE, CONTENT_OUTPUT_FILE


def parse_pdf(pdf_arg=None):
    """Parse PDF and generate output files"""
    pdf_file = resolve_pdf_path(pdf_arg)
    if not pdf_file.exists():
        print(f"Error: PDF file not found: {pdf_file}")
        return
    
    # Extract TOC
    with PDFParser(str(pdf_file)) as parser:
        raw_toc = parser.extract_toc()
        if not raw_toc:
            print("No TOC found in PDF")
            return
        structured_toc = parser.build_hierarchy(raw_toc)
    
    # Filter and save TOC
    section_filter = SectionFilter()
    filtered_toc = section_filter.filter_numbered_sections(structured_toc)
    
    writer = JSONLWriter()
    writer.save(filtered_toc, TOC_OUTPUT_FILE)
    print(f"TOC output: {TOC_OUTPUT_FILE} ({len(filtered_toc)} sections)")
    
    # Extract and save content
    with ContentExtractor(str(pdf_file)) as extractor:
        content_entries = extractor.extract_content(filtered_toc)
    
    writer.save(content_entries, CONTENT_OUTPUT_FILE)
    print(f"Content output: {CONTENT_OUTPUT_FILE} ({len(content_entries)} entries)")


def search_toc(query):
    """Search TOC entries"""
    searcher = TOCSearcher()
    searcher.search(query)


def resolve_pdf_path(pdf_arg):
    """Resolve PDF file path"""
    if not pdf_arg:
        return Path(ASSETS_FOLDER) / DEFAULT_PDF_FILE
    elif Path(pdf_arg).exists():
        return Path(pdf_arg)
    else:
        return Path(ASSETS_FOLDER) / pdf_arg