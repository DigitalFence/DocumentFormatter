#!/usr/bin/env python3
"""
Smart Document Converter
Converts text, markdown, or Word documents to match a reference Word document's formatting.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings

# Import required libraries
try:
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.style import WD_STYLE_TYPE
    from docx.text.paragraph import Paragraph
    from docx.text.run import Run
except ImportError:
    print("Error: python-docx not installed. Run: pip install python-docx")
    sys.exit(1)

try:
    import markdown
    from markdown.extensions import tables, fenced_code, nl2br
except ImportError:
    print("Error: markdown not installed. Run: pip install markdown")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: beautifulsoup4 not installed. Run: pip install beautifulsoup4")
    sys.exit(1)


class StyleExtractor:
    """Extracts formatting styles from a reference Word document."""
    
    def __init__(self, reference_doc_path: str):
        self.reference_doc = Document(reference_doc_path)
        self.styles = self._extract_styles()
        self._log_extracted_styles()
    
    def _extract_styles(self) -> Dict:
        """Extract all relevant styles from the reference document."""
        styles = {
            'document': self._get_document_styles(),
            'paragraphs': self._get_paragraph_styles(),
            'headings': self._get_heading_styles(),
            'normal': self._get_normal_style(),
            'lists': self._get_list_styles()
        }
        return styles
    
    def _get_document_styles(self) -> Dict:
        """Extract document-level formatting."""
        doc_styles = {}
        
        # Extract page margins if available
        sections = self.reference_doc.sections
        if sections:
            section = sections[0]
            doc_styles['margins'] = {
                'top': section.top_margin,
                'bottom': section.bottom_margin,
                'left': section.left_margin,
                'right': section.right_margin
            }
            doc_styles['page_width'] = section.page_width
            doc_styles['page_height'] = section.page_height
        
        return doc_styles
    
    def _get_paragraph_styles(self) -> List[Dict]:
        """Extract paragraph styles from the document."""
        paragraph_styles = []
        seen_styles = set()
        
        for para in self.reference_doc.paragraphs:
            if para.text.strip() and para.style.name not in seen_styles:
                seen_styles.add(para.style.name)
                
                style = {
                    'alignment': para.alignment,
                    'left_indent': para.paragraph_format.left_indent,
                    'right_indent': para.paragraph_format.right_indent,
                    'first_line_indent': para.paragraph_format.first_line_indent,
                    'space_before': para.paragraph_format.space_before,
                    'space_after': para.paragraph_format.space_after,
                    'line_spacing': para.paragraph_format.line_spacing,
                    'style_name': para.style.name if para.style else None
                }
                
                # Extract run formatting from all runs to get most common style
                if para.runs:
                    # Get the most common font properties
                    fonts = []
                    for run in para.runs:
                        if run.text.strip():
                            fonts.append({
                                'name': run.font.name,
                                'size': run.font.size,
                                'bold': run.font.bold,
                                'italic': run.font.italic,
                                'underline': run.font.underline,
                                'color': run.font.color.rgb if run.font.color else None
                            })
                    
                    # Use the first non-empty run's style
                    if fonts:
                        style['font'] = fonts[0]
                
                paragraph_styles.append(style)
                
                # Stop after collecting enough unique styles
                if len(paragraph_styles) >= 20:
                    break
        
        return paragraph_styles
    
    def _get_heading_styles(self) -> Dict:
        """Extract heading styles from the document."""
        heading_styles = {}
        
        for style in self.reference_doc.styles:
            if style.type == WD_STYLE_TYPE.PARAGRAPH and 'Heading' in style.name:
                heading_styles[style.name] = {
                    'font': {
                        'name': style.font.name,
                        'size': style.font.size,
                        'bold': style.font.bold,
                        'italic': style.font.italic,
                        'color': style.font.color.rgb if style.font.color else None
                    },
                    'paragraph': {
                        'alignment': style.paragraph_format.alignment,
                        'space_before': style.paragraph_format.space_before,
                        'space_after': style.paragraph_format.space_after,
                        'keep_with_next': style.paragraph_format.keep_with_next,
                        'page_break_before': style.paragraph_format.page_break_before,
                        'left_indent': style.paragraph_format.left_indent,
                        'right_indent': style.paragraph_format.right_indent,
                        'first_line_indent': style.paragraph_format.first_line_indent
                    }
                }
        
        # Also extract Title style if present
        for style in self.reference_doc.styles:
            if style.type == WD_STYLE_TYPE.PARAGRAPH and style.name == 'Title':
                heading_styles['Title'] = {
                    'font': {
                        'name': style.font.name,
                        'size': style.font.size,
                        'bold': style.font.bold,
                        'italic': style.font.italic,
                        'color': style.font.color.rgb if style.font.color else None
                    },
                    'paragraph': {
                        'alignment': style.paragraph_format.alignment,
                        'space_before': style.paragraph_format.space_before,
                        'space_after': style.paragraph_format.space_after,
                        'page_break_before': style.paragraph_format.page_break_before
                    }
                }
                
        return heading_styles
    
    def _get_normal_style(self) -> Dict:
        """Extract the normal/body text style."""
        normal_style = {}
        
        # First try to get from style definition
        for style in self.reference_doc.styles:
            if style.name == 'Normal':
                normal_style = {
                    'font': {
                        'name': style.font.name,
                        'size': style.font.size,
                        'bold': style.font.bold,
                        'italic': style.font.italic
                    },
                    'paragraph': {
                        'alignment': style.paragraph_format.alignment,
                        'space_before': style.paragraph_format.space_before,
                        'space_after': style.paragraph_format.space_after,
                        'line_spacing': style.paragraph_format.line_spacing
                    }
                }
                break
        
        # Override with actual font used in Normal style paragraphs
        for para in self.reference_doc.paragraphs:
            if para.style.name == 'Normal' and para.runs and para.text.strip():
                for run in para.runs:
                    if run.text.strip():
                        # Use the actual font from the document
                        normal_style['font'] = {
                            'name': run.font.name or normal_style.get('font', {}).get('name'),
                            'size': run.font.size or normal_style.get('font', {}).get('size'),
                            'bold': run.font.bold if run.font.bold is not None else normal_style.get('font', {}).get('bold'),
                            'italic': run.font.italic if run.font.italic is not None else normal_style.get('font', {}).get('italic')
                        }
                        break
                break
        
        return normal_style
    
    def _get_list_styles(self) -> Dict:
        """Extract list formatting styles."""
        list_styles = {
            'bullet': {'indent': Pt(36), 'font': None},
            'numbered': {'indent': Pt(36), 'font': None}
        }
        
        # Try to extract actual list styles from reference document
        for style in self.reference_doc.styles:
            if style.name == 'List Bullet' and hasattr(style, 'font'):
                list_styles['bullet']['font'] = {
                    'name': style.font.name,
                    'size': style.font.size
                }
            elif style.name == 'List Number' and hasattr(style, 'font'):
                list_styles['numbered']['font'] = {
                    'name': style.font.name,
                    'size': style.font.size
                }
        
        return list_styles
    
    def _log_extracted_styles(self):
        """Log all extracted styles for debugging."""
        import json
        import os
        
        # Only log if debug mode is enabled
        if os.environ.get('WORD_FORMATTER_DEBUG', '0') != '1':
            return
            
        print("\n" + "="*60)
        print("REFERENCE DOCUMENT STYLES EXTRACTED")
        print("="*60)
        
        # Show actual fonts used in the document
        print("\n🔍 ACTUAL FONTS DETECTED IN DOCUMENT:")
        font_usage = {}
        for para in self.reference_doc.paragraphs[:20]:  # Sample first 20 paragraphs
            if para.runs and para.text.strip():
                for run in para.runs:
                    if run.text.strip() and run.font.name:
                        font_name = run.font.name
                        if font_name not in font_usage:
                            font_usage[font_name] = {
                                'count': 0,
                                'sizes': set(),
                                'styles': {'bold': False, 'italic': False}
                            }
                        font_usage[font_name]['count'] += 1
                        if run.font.size:
                            font_usage[font_name]['sizes'].add(run.font.size)
                        if run.font.bold:
                            font_usage[font_name]['styles']['bold'] = True
                        if run.font.italic:
                            font_usage[font_name]['styles']['italic'] = True
        
        for font_name, usage in font_usage.items():
            print(f"  {font_name}:")
            print(f"    Used {usage['count']} times")
            if usage['sizes']:
                sizes_pt = [f"{s/12700:.1f}pt" for s in sorted(usage['sizes'])]
                print(f"    Sizes: {', '.join(sizes_pt)}")
            if usage['styles']['bold'] or usage['styles']['italic']:
                styles = []
                if usage['styles']['bold']:
                    styles.append('Bold')
                if usage['styles']['italic']:
                    styles.append('Italic')
                print(f"    Styles: {', '.join(styles)}")
        
        print("\n" + "="*60)
        
        # Document-level styles
        if 'document' in self.styles:
            print("\n📄 DOCUMENT SETTINGS:")
            doc = self.styles['document']
            if 'margins' in doc:
                margins = doc['margins']
                print(f"  Margins:")
                print(f"    Top: {margins.get('top', 'Not set')}")
                print(f"    Bottom: {margins.get('bottom', 'Not set')}")
                print(f"    Left: {margins.get('left', 'Not set')}")
                print(f"    Right: {margins.get('right', 'Not set')}")
            if 'page_width' in doc:
                print(f"  Page Width: {doc['page_width']}")
            if 'page_height' in doc:
                print(f"  Page Height: {doc['page_height']}")
        
        # Normal style
        if 'normal' in self.styles and self.styles['normal']:
            print("\n📝 NORMAL (BODY) STYLE:")
            normal = self.styles['normal']
            if 'font' in normal:
                font = normal['font']
                print(f"  Font:")
                print(f"    Name: {font.get('name', 'Default')}")
                print(f"    Size: {font.get('size', 'Default')}")
                print(f"    Bold: {font.get('bold', False)}")
                print(f"    Italic: {font.get('italic', False)}")
            if 'paragraph' in normal:
                para = normal['paragraph']
                print(f"  Paragraph:")
                print(f"    Alignment: {para.get('alignment', 'Default')}")
                print(f"    Space Before: {para.get('space_before', 0)}")
                print(f"    Space After: {para.get('space_after', 0)}")
                print(f"    Line Spacing: {para.get('line_spacing', 'Default')}")
        
        # Heading styles
        if 'headings' in self.styles:
            print("\n📌 HEADING STYLES:")
            for heading_name, heading_style in self.styles['headings'].items():
                print(f"\n  {heading_name}:")
                if 'font' in heading_style:
                    font = heading_style['font']
                    print(f"    Font: {font.get('name', 'Default')}")
                    print(f"    Size: {font.get('size', 'Default')}")
                    print(f"    Bold: {font.get('bold', False)}")
                    print(f"    Color: {font.get('color', 'Default')}")
                if 'paragraph' in heading_style:
                    para = heading_style['paragraph']
                    print(f"    Space Before: {para.get('space_before', 0)}")
                    print(f"    Space After: {para.get('space_after', 0)}")
                    print(f"    Keep with Next: {para.get('keep_with_next', False)}")
                    print(f"    Page Break Before: {para.get('page_break_before', False)}")
        
        # List styles
        if 'lists' in self.styles:
            print("\n📋 LIST STYLES:")
            lists = self.styles['lists']
            if 'bullet' in lists:
                print(f"  Bullet List:")
                print(f"    Indent: {lists['bullet'].get('indent', 'Default')}")
                if lists['bullet'].get('font'):
                    font = lists['bullet']['font']
                    print(f"    Font: {font.get('name', 'Default')}")
                    print(f"    Size: {font.get('size', 'Default')}")
            if 'numbered' in lists:
                print(f"  Numbered List:")
                print(f"    Indent: {lists['numbered'].get('indent', 'Default')}")
                if lists['numbered'].get('font'):
                    font = lists['numbered']['font']
                    print(f"    Font: {font.get('name', 'Default')}")
                    print(f"    Size: {font.get('size', 'Default')}")
        
        # Paragraph styles summary
        if 'paragraphs' in self.styles:
            print(f"\n📊 PARAGRAPH STYLES COLLECTED: {len(self.styles['paragraphs'])} unique styles")
            style_names = set()
            for para_style in self.styles['paragraphs']:
                if para_style.get('style_name'):
                    style_names.add(para_style['style_name'])
            if style_names:
                print(f"  Style names found: {', '.join(sorted(style_names))}")
        
        print("\n" + "="*60)
        print()


class DocumentConverter:
    """Converts various document formats to Word with reference styling."""
    
    def __init__(self, reference_doc_path: str):
        self.style_extractor = StyleExtractor(reference_doc_path)
        self.output_doc = Document()
        
    def convert(self, input_path: str, output_path: str):
        """Convert input document to styled Word document."""
        input_path = Path(input_path)
        
        # Determine file type and read content
        if input_path.suffix.lower() == '.txt':
            content = self._read_text_file(input_path)
            self._process_text_content(content)
        elif input_path.suffix.lower() in ['.md', '.markdown']:
            content = self._read_markdown_file(input_path)
            self._process_markdown_content(content)
        elif input_path.suffix.lower() in ['.docx', '.doc']:
            self._process_word_document(input_path)
        else:
            raise ValueError(f"Unsupported file format: {input_path.suffix}")
        
        # Apply reference document styles
        self._apply_reference_styles()
        
        # Save the output document
        self.output_doc.save(output_path)
        print(f"Document converted successfully: {output_path}")
    
    def _read_text_file(self, file_path: Path) -> str:
        """Read plain text file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _read_markdown_file(self, file_path: Path) -> str:
        """Read markdown file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _process_text_content(self, content: str):
        """Process plain text content."""
        paragraphs = content.split('\n\n')
        
        for para_text in paragraphs:
            if para_text.strip():
                para = self.output_doc.add_paragraph(para_text.strip())
    
    def _process_markdown_content(self, content: str):
        """Process markdown content to Word format."""
        # Convert markdown to HTML
        extensions = ['tables', 'fenced_code', 'nl2br']
        html = markdown.markdown(content, extensions=extensions)
        
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Process each element
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'blockquote', 'ul', 'ol', 'table', 'pre']):
            self._process_html_element(element)
    
    def _process_html_element(self, element):
        """Process individual HTML elements."""
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            heading_text = element.get_text().strip()
            
            # Check if this is a chapter heading (typically H1 or contains "Chapter")
            if level == 1 or 'chapter' in heading_text.lower():
                # Add page break before chapter (except for the first heading)
                if len(self.output_doc.paragraphs) > 0:
                    self.output_doc.add_page_break()
            
            heading = self.output_doc.add_heading(heading_text, level=level)
            
            # Apply special formatting for chapter headings
            if level == 1 or 'chapter' in heading_text.lower():
                heading.paragraph_format.space_before = Pt(24)
                heading.paragraph_format.space_after = Pt(18)
                heading.paragraph_format.keep_with_next = True
        
        elif element.name == 'blockquote':
            # Handle blockquotes (Sanskrit quotes, etc.)
            para = self.output_doc.add_paragraph()
            # Center align blockquotes
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            para.paragraph_format.space_before = Pt(12)
            para.paragraph_format.space_after = Pt(12)
            
            # Process blockquote content
            for child in element.children:
                if hasattr(child, 'name'):
                    if child.name == 'p':
                        # Process paragraph within blockquote
                        text = child.get_text().strip()
                        if text:
                            if text.startswith('—'):
                                # Source citation - make it italic and smaller
                                run = para.add_run(text)
                                run.italic = True
                                if run.font.size:
                                    run.font.size = Pt(10)
                            else:
                                # Check for italics in the original
                                if child.find('em') or child.find('i'):
                                    run = para.add_run(child.get_text().strip())
                                    run.italic = True
                                else:
                                    para.add_run(child.get_text().strip())
                            para.add_run('\n')
                else:
                    # Plain text in blockquote
                    if str(child).strip():
                        para.add_run(str(child).strip())
                        para.add_run('\n')
            
        elif element.name == 'p':
            para = self.output_doc.add_paragraph()
            self._process_inline_elements(element, para)
            
        elif element.name in ['ul', 'ol']:
            for li in element.find_all('li', recursive=False):
                para = self.output_doc.add_paragraph(li.get_text().strip())
                para.style = 'List Bullet' if element.name == 'ul' else 'List Number'
                
        elif element.name == 'table':
            self._process_table(element)
            
        elif element.name == 'pre':
            # Code block
            para = self.output_doc.add_paragraph(element.get_text())
            para.style = 'Quote'  # Use Quote style for code blocks
    
    def _process_inline_elements(self, element, paragraph):
        """Process inline formatting like bold, italic, links."""
        for child in element.children:
            if hasattr(child, 'name'):
                if child.name == 'strong' or child.name == 'b':
                    run = paragraph.add_run(child.get_text())
                    run.bold = True
                elif child.name == 'em' or child.name == 'i':
                    run = paragraph.add_run(child.get_text())
                    run.italic = True
                elif child.name == 'code':
                    run = paragraph.add_run(child.get_text())
                    run.font.name = 'Courier New'
                elif child.name == 'a':
                    run = paragraph.add_run(child.get_text())
                    run.font.color.rgb = RGBColor(0, 0, 255)
                    run.underline = True
                else:
                    paragraph.add_run(child.get_text())
            else:
                # Plain text
                paragraph.add_run(str(child))
    
    def _process_table(self, table_element):
        """Process HTML table to Word table."""
        rows = table_element.find_all('tr')
        if not rows:
            return
        
        # Count columns
        cols = len(rows[0].find_all(['td', 'th']))
        
        # Create table
        table = self.output_doc.add_table(rows=len(rows), cols=cols)
        table.style = 'Table Grid'
        
        # Populate table
        for i, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            for j, cell in enumerate(cells):
                table.rows[i].cells[j].text = cell.get_text().strip()
    
    def _process_word_document(self, file_path: Path):
        """Process existing Word document."""
        source_doc = Document(file_path)
        
        for element in source_doc.element.body:
            # Copy paragraphs
            if element.tag.endswith('p'):
                para = source_doc.paragraphs[0]  # This is simplified
                new_para = self.output_doc.add_paragraph()
                
                # Copy text and basic formatting
                for run in para.runs:
                    new_run = new_para.add_run(run.text)
                    new_run.bold = run.bold
                    new_run.italic = run.italic
                    new_run.underline = run.underline
    
    def _apply_reference_styles(self):
        """Apply styles from reference document to output document."""
        styles = self.style_extractor.styles
        
        # Apply document-level styles
        if 'document' in styles and 'margins' in styles['document']:
            section = self.output_doc.sections[0]
            margins = styles['document']['margins']
            if margins['top']:
                section.top_margin = margins['top']
            if margins['bottom']:
                section.bottom_margin = margins['bottom']
            if margins['left']:
                section.left_margin = margins['left']
            if margins['right']:
                section.right_margin = margins['right']
        
        # Apply normal style
        if 'normal' in styles and styles['normal']:
            normal_style = styles['normal']
            for para in self.output_doc.paragraphs:
                if para.style.name == 'Normal':
                    self._apply_paragraph_style(para, normal_style)
        
        # Apply heading styles
        if 'headings' in styles:
            for para in self.output_doc.paragraphs:
                if para.style and 'Heading' in para.style.name:
                    if para.style.name in styles['headings']:
                        self._apply_paragraph_style(para, styles['headings'][para.style.name])
    
    def _apply_paragraph_style(self, paragraph: Paragraph, style: Dict):
        """Apply style dictionary to a paragraph."""
        # Apply paragraph formatting
        if 'paragraph' in style:
            para_format = style['paragraph']
            if para_format.get('alignment'):
                paragraph.alignment = para_format['alignment']
            if para_format.get('space_before'):
                paragraph.paragraph_format.space_before = para_format['space_before']
            if para_format.get('space_after'):
                paragraph.paragraph_format.space_after = para_format['space_after']
            if para_format.get('line_spacing'):
                paragraph.paragraph_format.line_spacing = para_format['line_spacing']
            if para_format.get('left_indent'):
                paragraph.paragraph_format.left_indent = para_format['left_indent']
            if para_format.get('right_indent'):
                paragraph.paragraph_format.right_indent = para_format['right_indent']
            if para_format.get('first_line_indent'):
                paragraph.paragraph_format.first_line_indent = para_format['first_line_indent']
            if para_format.get('keep_with_next'):
                paragraph.paragraph_format.keep_with_next = para_format['keep_with_next']
            if para_format.get('page_break_before'):
                paragraph.paragraph_format.page_break_before = para_format['page_break_before']
        
        # Apply font formatting to all runs
        if 'font' in style and paragraph.runs:
            font_style = style['font']
            for run in paragraph.runs:
                if font_style.get('name'):
                    run.font.name = font_style['name']
                if font_style.get('size'):
                    run.font.size = font_style['size']
                if font_style.get('bold') is not None:
                    run.font.bold = font_style['bold']
                if font_style.get('italic') is not None:
                    run.font.italic = font_style['italic']
                if font_style.get('color'):
                    run.font.color.rgb = font_style['color']


def main():
    """Main entry point for the document converter."""
    parser = argparse.ArgumentParser(
        description='Convert text, markdown, or Word documents to match a reference Word document style.',
        epilog='Example: python document_converter.py --input document.txt --reference template.docx --output result.docx'
    )
    parser.add_argument('--input', '-i', required=True, dest='input_file',
                        help='Path to input file (txt, md, or docx)')
    parser.add_argument('--reference', '-r', required=True, dest='reference_file',
                        help='Path to reference Word document for styling')
    parser.add_argument('--output', '-o', dest='output',
                        help='Output file path (default: input_file_formatted.docx)')
    
    args = parser.parse_args()
    
    # Validate inputs
    input_path = Path(args.input_file)
    reference_path = Path(args.reference_file)
    
    if not input_path.exists():
        print(f"Error: Input file does not exist: {input_path}")
        sys.exit(1)
    
    if not reference_path.exists():
        print(f"Error: Reference file does not exist: {reference_path}")
        sys.exit(1)
    
    if reference_path.suffix.lower() not in ['.docx', '.doc']:
        print(f"Error: Reference file must be a Word document (.docx or .doc)")
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_formatted.docx"
    
    # Create converter and process
    try:
        converter = DocumentConverter(reference_path)
        converter.convert(str(input_path), str(output_path))
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()