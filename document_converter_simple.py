#!/usr/bin/env python3
"""
Simplified Document Converter for Finder Quick Action
Converts documents using a hardcoded reference format file.
"""

import sys
import os
from pathlib import Path
from document_converter import DocumentConverter

def main():
    """Simple entry point that uses hardcoded reference file."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple document converter')
    parser.add_argument('input_file', help='Input file to convert')
    parser.add_argument('--reference', '-r', help='Reference format document path')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    
    # Use reference format from argument or find default
    if args.reference:
        reference_path = Path(args.reference)
        if not reference_path.exists():
            print(f"Error: Reference format file not found: {args.reference}")
            sys.exit(1)
    else:
        # Look for reference file in the same directory as this script
        script_dir = Path(__file__).parent
        reference_path = script_dir / "referenceformat.docx"
        
        # If not found in script directory, try user's Documents folder
        if not reference_path.exists():
            reference_path = Path.home() / "Documents" / "referenceformat.docx"
        
        # If still not found, try Desktop
        if not reference_path.exists():
            reference_path = Path.home() / "Desktop" / "referenceformat.docx"
        
        if not reference_path.exists():
            print(f"Error: Reference format file not found. Please place 'referenceformat.docx' in one of these locations:")
            print(f"  - {script_dir}")
            print(f"  - {Path.home() / 'Documents'}")
            print(f"  - {Path.home() / 'Desktop'}")
            sys.exit(1)
    
    if not input_path.exists():
        print(f"Error: Input file does not exist: {input_path}")
        sys.exit(1)
    
    # Determine output path
    output_path = input_path.parent / f"{input_path.stem}_formatted.docx"
    
    # Create converter and process
    try:
        print(f"Converting: {input_path.name}")
        print(f"Using reference: {reference_path}")
        converter = DocumentConverter(str(reference_path))
        converter.convert(str(input_path), str(output_path))
        print(f"Success! Output saved to: {output_path}")
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()