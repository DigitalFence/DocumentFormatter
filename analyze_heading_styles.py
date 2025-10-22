#!/usr/bin/env python3
"""Analyze heading styles in both reference and output documents"""

from docx import Document
from pathlib import Path

def analyze_styles(doc_path, doc_name):
    """Analyze styles in a document"""
    doc = Document(doc_path)
    print(f"\n{'='*60}")
    print(f"Analyzing: {doc_name}")
    print(f"{'='*60}")
    
    # Check Title style
    print("\nTitle Style:")
    for style in doc.styles:
        if style.name == 'Title':
            print(f"  Name: {style.name}")
            if hasattr(style, 'font'):
                print(f"  Font Name: {style.font.name}")
                print(f"  Font Size: {style.font.size}")
                print(f"  Bold: {style.font.bold}")
                print(f"  Color: {style.font.color.rgb if style.font.color and style.font.color.rgb else 'None'}")
            if hasattr(style, 'paragraph_format'):
                print(f"  Alignment: {style.paragraph_format.alignment}")
                print(f"  Space Before: {style.paragraph_format.space_before}")
                print(f"  Space After: {style.paragraph_format.space_after}")
    
    # Check Heading styles
    for i in range(1, 7):
        heading_name = f'Heading {i}'
        print(f"\n{heading_name}:")
        for style in doc.styles:
            if style.name == heading_name:
                if hasattr(style, 'font'):
                    print(f"  Font Name: {style.font.name}")
                    print(f"  Font Size: {style.font.size}")
                    print(f"  Bold: {style.font.bold}")
                    print(f"  Italic: {style.font.italic}")
                    print(f"  Color: {style.font.color.rgb if style.font.color and style.font.color.rgb else 'None'}")
                if hasattr(style, 'paragraph_format'):
                    print(f"  Alignment: {style.paragraph_format.alignment}")
                    print(f"  Space Before: {style.paragraph_format.space_before}")
                    print(f"  Space After: {style.paragraph_format.space_after}")
                break
    
    # Check actual paragraph styles
    print("\n\nActual paragraphs in document:")
    for i, para in enumerate(doc.paragraphs[:10]):
        if para.text.strip():
            print(f"\nPara {i}: {para.text[:50]}")
            print(f"  Style: {para.style.name if para.style else 'None'}")
            if para.runs:
                run = para.runs[0]
                print(f"  Font: {run.font.name}")
                print(f"  Size: {run.font.size}")
                print(f"  Bold: {run.font.bold}")
                print(f"  Color: {run.font.color.rgb if run.font.color and run.font.color.rgb else 'None'}")

# Analyze reference document
ref_path = Path("References/referenceformat.docx")
# Always try to resolve aliases
try:
    from alias_resolver import resolve_path
    ref_resolved = resolve_path(str(ref_path))
    print(f"Resolved reference path: {ref_resolved}")
except Exception as e:
    print(f"Could not resolve alias: {e}")
    ref_resolved = ref_path

analyze_styles(ref_resolved, "Reference Document")

# Analyze output document
output_path = Path("test_samples/test_all_fixes_formatted.docx")
if output_path.exists():
    analyze_styles(output_path, "Output Document")