#!/usr/bin/env python3
"""
Chunked Text to Markdown Converter
Processes large text files by breaking them into chunks for AI analysis.
"""

import sys
import os
from pathlib import Path
from text_to_markdown import TextToMarkdownConverter


def split_into_chunks(text, chunk_size=3000):
    """Split text into chunks at paragraph boundaries."""
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_size = len(line) + 1  # +1 for newline
        
        # If adding this line would exceed chunk size and we have content
        if current_size + line_size > chunk_size and current_chunk:
            # Save current chunk
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_size = line_size
        else:
            current_chunk.append(line)
            current_size += line_size
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks


def convert_large_text_to_markdown(input_path: str, output_path: str = None) -> bool:
    """Convert large text file to markdown by processing in chunks."""
    input_path = Path(input_path)
    
    if not output_path:
        output_path = input_path.parent / f"{input_path.stem}.md"
    else:
        output_path = Path(output_path)
    
    converter = TextToMarkdownConverter()
    
    try:
        # Read the input file
        with open(input_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        if not text_content.strip():
            print(f"Error: Input file is empty: {input_path}")
            return False
        
        print(f"Converting {input_path.name} to markdown (chunked processing)...")
        
        # Split into chunks
        chunks = split_into_chunks(text_content)
        print(f"Split into {len(chunks)} chunks for processing")
        
        # Process each chunk
        markdown_parts = []
        for i, chunk in enumerate(chunks, 1):
            print(f"Processing chunk {i}/{len(chunks)}...")
            
            # Try AI analysis for this chunk
            prompt = converter._create_analysis_prompt(chunk)
            success, result = converter._call_claude(prompt)
            
            if success:
                markdown_parts.append(result)
            else:
                # Fallback to simple conversion for this chunk
                print(f"  AI unavailable for chunk {i}, using simple conversion")
                markdown_parts.append(converter._simple_text_to_markdown(chunk))
        
        # Combine all parts
        markdown_content = '\n\n'.join(markdown_parts)
        
        # Write the markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✓ Markdown saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python chunked_text_to_markdown.py <input_text_file> [output_markdown_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_large_text_to_markdown(input_file, output_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()