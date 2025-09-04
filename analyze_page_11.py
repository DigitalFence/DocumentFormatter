#!/usr/bin/env python3
"""Analyze specific page content in reference document."""

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import sys

def analyze_document_for_special_formatting(doc_path):
    """Analyze document for special formatting patterns."""
    doc = Document(doc_path)
    
    # Track special formatting patterns
    special_paragraphs = []
    paragraph_count = 0
    estimated_page = 1
    paras_per_page = 35  # Rough estimate
    
    print("=== DOCUMENT STRUCTURE ANALYSIS ===\n")
    
    # Look for patterns that might indicate special formatting
    for i, para in enumerate(doc.paragraphs):
        paragraph_count += 1
        estimated_page = (i // paras_per_page) + 1
        
        # Skip empty paragraphs
        if not para.text.strip():
            continue
            
        # Check for special formatting characteristics
        special_features = []
        
        # 1. Check alignment
        if para.alignment == WD_ALIGN_PARAGRAPH.CENTER:
            special_features.append("CENTER ALIGNED")
        elif para.alignment == WD_ALIGN_PARAGRAPH.RIGHT:
            special_features.append("RIGHT ALIGNED")
        
        # 2. Check indentation
        pf = para.paragraph_format
        if pf.left_indent and pf.left_indent > Pt(0):
            special_features.append(f"LEFT INDENT: {pf.left_indent.pt}pt")
        if pf.right_indent and pf.right_indent > Pt(0):
            special_features.append(f"RIGHT INDENT: {pf.right_indent.pt}pt")
        if pf.first_line_indent and pf.first_line_indent != Pt(0):
            special_features.append(f"FIRST LINE INDENT: {pf.first_line_indent.pt}pt")
        
        # 3. Check for blockquote-like content (quotes, verses, poems)
        text_lower = para.text.lower()
        quote_chars = ['"', '"', ''', '—']
        keywords = ['verse', 'sutra', 'prayer', 'poem']
        if any(char in para.text for char in quote_chars) or any(word in text_lower for word in keywords):
            special_features.append("QUOTE/VERSE-LIKE")
        
        # 4. Check for all italic text
        if para.runs:
            all_italic = all(run.italic for run in para.runs if run.text.strip())
            if all_italic and any(run.italic for run in para.runs):
                special_features.append("ALL ITALIC")
        
        # 5. Check for special styles
        if para.style and para.style.name not in ['Normal', 'Heading 1', 'Heading 2', 'Heading 3']:
            special_features.append(f"STYLE: {para.style.name}")
        
        # If we found special features, record this paragraph
        if special_features and 9 <= estimated_page <= 13:  # Focus on pages around 11
            special_paragraphs.append({
                'index': i,
                'page': estimated_page,
                'text': para.text[:100] + '...' if len(para.text) > 100 else para.text,
                'features': special_features,
                'style': para.style.name if para.style else 'None'
            })
    
    # Print findings
    print(f"Total paragraphs analyzed: {paragraph_count}")
    print(f"Special paragraphs found around page 11: {len(special_paragraphs)}\n")
    
    # Group by estimated page
    pages = {}
    for sp in special_paragraphs:
        page = sp['page']
        if page not in pages:
            pages[page] = []
        pages[page].append(sp)
    
    # Print detailed analysis for each page
    for page in sorted(pages.keys()):
        print(f"\n=== ESTIMATED PAGE {page} ===")
        for para in pages[page]:
            print(f"\nParagraph {para['index']}:")
            print(f"  Text: {para['text']}")
            print(f"  Style: {para['style']}")
            print(f"  Special Features: {', '.join(para['features'])}")
    
    # Look for recurring patterns
    print("\n=== PATTERN ANALYSIS ===")
    
    # Count feature occurrences
    feature_counts = {}
    for sp in special_paragraphs:
        for feature in sp['features']:
            if feature not in feature_counts:
                feature_counts[feature] = 0
            feature_counts[feature] += 1
    
    print("\nMost common special formatting features:")
    for feature, count in sorted(feature_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {count} occurrences")

if __name__ == "__main__":
    try:
        analyze_document_for_special_formatting('referenceformat.docx')
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)