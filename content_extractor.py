import fitz
from pathlib import Path
from constants import DOC_TITLE, PROGRESS_INTERVAL, CONTENT_LIMIT


class ContentExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)
        self.doc_title = DOC_TITLE
    
    def extract_content(self, toc_entries):
        """Extract full content for each section"""
        try:
            doc = fitz.open(self.pdf_path)
            total_pages = len(doc)
            content_entries = []
            total_images = 0
            total_tables = 0
            
            print(f"Extracting content from {len(toc_entries)} sections...")
            
            for i, section in enumerate(toc_entries):
                try:
                    start_page = section['page'] - 1
                    
                    if i + 1 < len(toc_entries):
                        end_page = toc_entries[i + 1]['page'] - 1
                    else:
                        end_page = total_pages
                    
                    section_text = ""
                    
                    for page_num in range(start_page, min(end_page, total_pages)):
                        try:
                            page = doc[page_num]
                            text = page.get_text()
                            if text.strip():
                                section_text += text.strip() + "\n"
                            
                            # Extract detailed image information
                            images = page.get_images()
                            if images:
                                total_images += len(images)
                                section_text += f"\n=== IMAGES ON PAGE {page_num + 1} ===\n"
                                for img_idx, img in enumerate(images):
                                    section_text += f"Image {img_idx + 1}: xref={img[0]}, width={img[2]}px, height={img[3]}px, colorspace={img[4]}\n"
                                section_text += "=== END IMAGES ===\n"
                            
                            # Extract detailed table information
                            try:
                                tables = page.find_tables()
                                if tables:
                                    total_tables += len(tables)
                                    section_text += f"\n=== TABLES ON PAGE {page_num + 1} ===\n"
                                    for table_idx, table in enumerate(tables):
                                        try:
                                            table_data = table.extract()
                                            section_text += f"Table {table_idx + 1} ({len(table_data)} rows x {len(table_data[0]) if table_data else 0} cols):\n"
                                            # Include first 5 rows of table data
                                            for row_idx, row in enumerate(table_data[:5]):
                                                clean_row = [str(cell).strip() if cell else '' for cell in row]
                                                section_text += f"  Row {row_idx + 1}: {' | '.join(clean_row)}\n"
                                            if len(table_data) > 5:
                                                section_text += f"  ... and {len(table_data) - 5} more rows\n"
                                        except Exception as e:
                                            section_text += f"Table {table_idx + 1}: extraction failed ({str(e)})\n"
                                    section_text += "=== END TABLES ===\n"
                            except:
                                # Fallback: text-based table detection
                                page_text = page.get_text()
                                table_mentions = page_text.count('Table ') + page_text.count('TABLE ')
                                if table_mentions > 0:
                                    total_tables += table_mentions
                                    section_text += f"\n[{table_mentions} table reference(s) found in text on page {page_num + 1}]\n"
                        
                        except Exception:
                            continue
                    
                    content = section_text.strip()[:CONTENT_LIMIT] if section_text.strip() else f"[Section {section['section_id']} - No extractable content]"
                    
                    content_entries.append({
                        'doc_title': self.doc_title,
                        'section_id': section['section_id'],
                        'title': section['title'],
                        'page_range': f"{section['page']}-{end_page}",
                        'content': content,
                        'content_type': 'section_with_images_tables',
                        'has_content': bool(section_text.strip())
                    })
                    
                    if (i + 1) % PROGRESS_INTERVAL == 0:
                        print(f"Processed {i + 1}/{len(toc_entries)} sections")
                
                except Exception:
                    continue
            
            doc.close()
            print(f"\nExtraction complete:")
            print(f"Total Images: {total_images}")
            print(f"Total Tables: {total_tables}")
            
            return content_entries
        
        except Exception as e:
            print(f"Error extracting content: {e}")
            return []