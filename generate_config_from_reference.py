#!/usr/bin/env python3
"""
Generate formatter_config.json from reference document
Analyzes the reference document and creates appropriate configuration.
"""

import json
import sys
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

try:
    from alias_resolver import resolve_path
except ImportError:
    def resolve_path(path):
        return str(path)

def analyze_reference_document(doc_path):
    """Analyze reference document to generate config."""
    # Resolve any aliases
    resolved_path = resolve_path(doc_path)
    doc = Document(resolved_path)
    
    config = {
        "heading_overrides": {},
        "heading_detection": {
            "title_keywords": ["title"],
            "dedication_keywords": ["dedicated to", "dedication", "in memory of"],
            "contents_keywords": ["contents", "table of contents", "toc"],
            "section_keywords": ["section", "part"],
            "chapter_keywords": ["chapter"],
            "always_use_heading_1_for_chapters": True
        },
        "page_breaks": {
            "before_sections": False,
            "before_chapters": True,
            "after_title": True,
            "after_dedication": True,
            "after_contents": True,
            "preserve_original": True
        },
        "blockquote_formatting": {
            "remove_em_dashes": True,
            "single_line_spacing": True,
            "center_align": True
        }
    }
    
    # Analyze heading styles
    for style in doc.styles:
        if hasattr(style, 'name') and style.name and 'Heading' in style.name:
            try:
                # Extract heading level
                level = int(style.name.split()[-1])
                if 1 <= level <= 6:
                    heading_key = f"heading_{level}"
                    override = {}
                    
                    # Get font properties
                    if hasattr(style, 'font'):
                        if style.font.name:
                            override['font_name'] = style.font.name
                        if style.font.size:
                            override['font_size'] = style.font.size.pt
                        if style.font.bold is not None:
                            override['bold'] = style.font.bold
                        if style.font.italic is not None:
                            override['italic'] = style.font.italic
                        if style.font.color and style.font.color.rgb:
                            override['color'] = str(style.font.color.rgb)
                    
                    # Get paragraph properties
                    if hasattr(style, 'paragraph_format'):
                        if style.paragraph_format.alignment:
                            alignment_map = {
                                WD_ALIGN_PARAGRAPH.LEFT: "left",
                                WD_ALIGN_PARAGRAPH.CENTER: "center",
                                WD_ALIGN_PARAGRAPH.RIGHT: "right",
                                WD_ALIGN_PARAGRAPH.JUSTIFY: "justify"
                            }
                            override['alignment'] = alignment_map.get(style.paragraph_format.alignment, "left")
                        
                        if style.paragraph_format.space_before:
                            override['space_before'] = style.paragraph_format.space_before.pt
                        if style.paragraph_format.space_after:
                            override['space_after'] = style.paragraph_format.space_after.pt
                    
                    if override:
                        config["heading_overrides"][heading_key] = override
            except (ValueError, AttributeError):
                pass
    
    # Add special content formatting based on common patterns
    config["special_content_formatting"] = {
        "hierarchical_lists": {
            "enabled": True,
            "detect_patterns": [
                "roles", "principles", "teachings", "qualities",
                "attributes", "characteristics", "types", "categories",
                "elements", "aspects", "dimensions"
            ],
            "numbered_item_style": "Normal (Web)",
            "bullet_point_style": "List Paragraph",
            "detection_rules": {
                "numbered_pattern": "^\\d+\\.\\s+[A-Z]",
                "section_keywords": ["roles", "principles", "qualities", "attributes", "types", "aspects"],
                "min_items": 2,
                "auto_detect_heading": True
            }
        }
    }
    
    # Add chapter opening/closing formatting
    config["chapter_opening_quote"] = {
        "enabled": True,
        "subtle_emphasis": True,
        "font_size_reduction": 1,
        "italic": True,
        "color": "666666",
        "spacing_after": 18,
        "detect_patterns": ["verse", "quote", "translation", "transliteration"]
    }
    
    config["chapter_closing_content"] = {
        "enabled": True,
        "subtle_emphasis": True,
        "font_size_reduction": 1,
        "italic": True,
        "color": "666666",
        "spacing_before": 18,
        "detect_patterns": ["story", "poem", "verse"]
    }
    
    # Add chapter separator (you'll need to update the symbol_source path)
    config["chapter_separator"] = {
        "enabled": True,
        "symbol": "❦",
        "symbol_source": None,  # Will be updated if Symbols.docx exists
        "comment": "Set symbol_source to path of Word doc to extract first symbol from it",
        "position": "after",
        "spacing_before": 12,
        "spacing_after": 12,
        "font_size": 14
    }
    
    # Check for Symbols.docx in common locations
    symbols_locations = [
        Path(__file__).parent / "References" / "Symbols.docx",
        Path(__file__).parent / "Symbols.docx",
        Path.home() / "Documents" / "WordTemplates" / "Symbols.docx",
        Path.home() / "Documents" / "Symbols.docx",
        Path.home() / "Desktop" / "Symbols.docx"
    ]
    
    for symbols_path in symbols_locations:
        if symbols_path.exists():
            config["chapter_separator"]["symbol_source"] = str(symbols_path)
            print(f"Found Symbols.docx at: {symbols_path}")
            break
    
    return config

def main():
    if len(sys.argv) < 2:
        # Use default reference document
        script_dir = Path(__file__).parent
        reference_path = script_dir / "referenceformat.docx"
        if not reference_path.exists():
            print("Usage: python generate_config_from_reference.py [reference_document.docx]")
            print("Or place referenceformat.docx in the script directory")
            sys.exit(1)
    else:
        reference_path = Path(sys.argv[1])
        if not reference_path.exists():
            print(f"Error: Reference document not found: {reference_path}")
            sys.exit(1)
    
    print(f"Analyzing reference document: {reference_path}")
    config = analyze_reference_document(str(reference_path))
    
    # Save configuration
    output_path = Path(__file__).parent / "References" / "formatter_config.json"
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nGenerated configuration saved to: {output_path}")
    print("\nConfiguration summary:")
    print(f"- Heading overrides: {len(config['heading_overrides'])} headings")
    print(f"- Chapter separator: {'Enabled' if config['chapter_separator']['enabled'] else 'Disabled'}")
    if config['chapter_separator']['symbol_source']:
        print(f"  Using symbols from: {config['chapter_separator']['symbol_source']}")
    print(f"- Special formatting: Hierarchical lists, opening quotes, closing content")
    print(f"- Page breaks: After title, dedication, and contents")

if __name__ == "__main__":
    main()