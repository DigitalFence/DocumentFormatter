#!/usr/bin/env python3
"""
Text to Markdown Converter
Converts plain text to markdown using Claude AI or simple heuristics.
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Tuple


class TextToMarkdownConverter:
    """Convert plain text to markdown format."""
    
    def __init__(self):
        self.debug = os.environ.get('WORD_FORMATTER_DEBUG', '0') == '1'
    
    def _create_analysis_prompt(self, text_content: str) -> str:
        """Create the prompt for Claude to analyze and structure text."""
        return f"""Convert the following plain text to well-structured markdown format.

Instructions:
1. Identify and mark headings based on context and formatting cues
2. Detect lists (both bulleted and numbered) and format appropriately  
3. Recognize quotes, citations, and special blocks
4. Preserve all original text content exactly
5. Add markdown formatting only where it enhances structure
6. Use heading levels (# ## ###) based on document hierarchy
7. Format code blocks if you detect code snippets
8. Identify tables and convert to markdown table format

Important:
- Do not add any content that wasn't in the original
- Maintain the original tone and style
- Focus on structure, not rewriting
- If the text already has clear structure, preserve it

Return ONLY the markdown formatted text. Do not include any explanations, apologies, or commentary. Start directly with the converted markdown.

Text to convert:
---
{text_content}
---"""
    
    def _call_claude(self, prompt: str) -> Tuple[bool, str]:
        """Call Claude CLI and return success status and output."""
        try:
            # Get model from environment or use default
            model = os.environ.get('CLAUDE_MODEL', 'sonnet')
            
            if self.debug:
                print(f"Calling Claude ({model}) for text analysis...")
            
            result = subprocess.run(
                ['claude', '--model', model, '--print', prompt],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0 and result.stdout.strip():
                if self.debug:
                    print("Claude analysis successful")
                return True, result.stdout.strip()
            else:
                if self.debug:
                    print(f"Claude returned error: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "Claude analysis timed out"
        except FileNotFoundError:
            return False, "Claude CLI not found"
        except Exception as e:
            return False, str(e)
    
    def _simple_text_to_markdown(self, text_content: str) -> str:
        """Simple fallback conversion from text to markdown."""
        lines = text_content.split('\n')
        markdown_lines = []
        in_list = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                markdown_lines.append('')
                in_list = False
                continue
            
            # Detect potential headings (lines that are title-cased or all caps)
            if (len(stripped) < 100 and 
                (stripped.istitle() or stripped.isupper()) and 
                not any(stripped.startswith(c) for c in ['-', '*', '•', '1', '2', '3'])):
                # Add heading
                markdown_lines.append(f"\n## {stripped}\n")
                in_list = False
            # Detect list items
            elif any(stripped.startswith(c) for c in ['-', '*', '•']):
                # Bullet list
                markdown_lines.append(f"- {stripped[1:].strip()}")
                in_list = True
            elif len(stripped) > 0 and stripped[0].isdigit() and '. ' in stripped[:4]:
                # Numbered list
                markdown_lines.append(stripped)
                in_list = True
            else:
                # Regular paragraph
                if in_list and stripped:
                    markdown_lines.append('')
                markdown_lines.append(line)
                in_list = False
        
        return '\n'.join(markdown_lines)


def convert_text_to_markdown(input_path: str, output_path: str = None) -> bool:
    """Convert text file to markdown format."""
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
        
        print(f"Converting {input_path.name} to markdown...")
        
        # Check if we should force simple conversion
        force_simple = os.environ.get('FORCE_SIMPLE', '0') == '1'
        
        if not force_simple:
            # Try AI analysis first
            prompt = converter._create_analysis_prompt(text_content)
            success, result = converter._call_claude(prompt)
            
            if success:
                markdown_content = result
                print("✓ AI analysis successful")
            else:
                # Fallback to simple conversion
                print(f"AI unavailable: {result}")
                print("Using simple text analysis...")
                markdown_content = converter._simple_text_to_markdown(text_content)
        else:
            print("Using simple text analysis (forced)...")
            markdown_content = converter._simple_text_to_markdown(text_content)
        
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
        print("Usage: python text_to_markdown.py <input_text_file> [output_markdown_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_text_to_markdown(input_file, output_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()