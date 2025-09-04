#!/usr/bin/env python3
"""Test access to Symbols.docx file"""

import os
import sys
from pathlib import Path

symbols_path = "/Users/KDP/Documents/WordTemplates/Symbols.docx"

print(f"Testing access to: {symbols_path}")
print(f"Current working directory: {os.getcwd()}")
print(f"Running as user: {os.getuid()}")
print(f"File exists: {Path(symbols_path).exists()}")
print(f"File is readable: {os.access(symbols_path, os.R_OK)}")
print(f"File size: {Path(symbols_path).stat().st_size if Path(symbols_path).exists() else 'N/A'}")

# Try to open with docx
try:
    from docx import Document
    doc = Document(symbols_path)
    print(f"Successfully opened with python-docx")
    print(f"Number of paragraphs: {len(doc.paragraphs)}")
except Exception as e:
    print(f"Failed to open with python-docx: {e}")

# Try alias resolution
try:
    from alias_resolver import resolve_path
    resolved = resolve_path(symbols_path)
    print(f"Alias resolver result: {resolved}")
    if resolved != symbols_path:
        print(f"  Resolved file exists: {Path(resolved).exists()}")
except ImportError:
    print("Alias resolver not available")