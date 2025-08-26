#!/usr/bin/env python3
"""
AI-Enhanced Document Converter using Claude
Intelligently converts plain text to structured documents using AI analysis.
"""

import sys
import os
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Optional, Tuple
from document_converter import DocumentConverter
from striprtf.striprtf import rtf_to_text

class AIDocumentConverter:
    """Converts documents with AI-powered text analysis."""
    
    def __init__(self, reference_path: str):
        self.reference_path = reference_path
        self.converter = DocumentConverter(reference_path)
        self.debug = os.environ.get('WORD_FORMATTER_DEBUG', '0') == '1'
        # Configuration options
        self.save_markdown = os.environ.get('SAVE_MARKDOWN', '1') == '1'  # Default: save markdown
        self.show_progress = os.environ.get('SHOW_PROGRESS', '1') == '1'  # Default: show progress
        self.model = os.environ.get('CLAUDE_MODEL', 'sonnet')  # Default: sonnet
        self.timeout = int(os.environ.get('CLAUDE_TIMEOUT', '120'))  # Default: 120 seconds
    
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

Return only the markdown formatted text, no explanations.

Text to convert:
---
{text_content}
---"""
    
    def _call_claude(self, prompt: str) -> Tuple[bool, str]:
        """Call Claude CLI and return success status and output."""
        try:
            # Show progress if enabled
            if self.show_progress:
                print(f"🤖 Using Claude {self.model.upper()} model for AI analysis...")
            elif self.debug:
                print(f"Calling Claude ({self.model}) for text analysis...")
            
            # Use explicit Claude path if provided, otherwise use 'claude' from PATH
            claude_cmd = os.environ.get('CLAUDE_CLI_PATH', 'claude')
            
            # Use Claude in print mode for non-interactive output
            result = subprocess.run(
                [claude_cmd, '--model', self.model, '--print', prompt],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0 and result.stdout.strip():
                if self.show_progress:
                    print("✓ AI analysis completed successfully")
                elif self.debug:
                    print("Claude analysis successful")
                return True, result.stdout.strip()
            else:
                error_msg = result.stderr or "Unknown error"
                if self.show_progress:
                    print(f"⚠️  Claude returned an error: {error_msg}")
                elif self.debug:
                    print(f"Claude returned error: {error_msg}")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = f"Claude analysis timed out after {self.timeout} seconds"
            if self.show_progress:
                print(f"⏱️  {error_msg}")
            elif self.debug:
                print(error_msg)
            return False, error_msg
        except FileNotFoundError:
            error_msg = "Claude CLI not found. Please install claude CLI."
            if self.show_progress:
                print(f"❌ {error_msg}")
            elif self.debug:
                print(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error calling Claude: {str(e)}"
            if self.show_progress:
                print(f"❌ {error_msg}")
            elif self.debug:
                print(error_msg)
            return False, error_msg
    
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
    
    def convert_with_ai(self, input_path: str, output_path: Optional[str] = None) -> bool:
        """Convert document using AI analysis."""
        input_path = Path(input_path)
        
        if not output_path:
            output_path = input_path.parent / f"{input_path.stem}_formatted.docx"
        else:
            output_path = Path(output_path)
        
        try:
            # Show progress
            if self.show_progress:
                print(f"📄 Processing: {input_path.name}")
            
            # Read the input file based on format
            if input_path.suffix.lower() == '.rtf':
                # Read RTF file and extract plain text
                try:
                    with open(input_path, 'r', encoding='utf-8') as f:
                        rtf_content = f.read()
                    text_content = rtf_to_text(rtf_content)
                    if self.debug:
                        print(f"Extracted text from RTF: {len(text_content)} characters")
                except Exception as e:
                    print(f"❌ Error reading RTF file: {e}")
                    return False
            else:
                # Read regular text files
                with open(input_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            
            if not text_content.strip():
                print(f"❌ Error: Input file is empty: {input_path}")
                return False
            
            # Determine if we should use AI or simple conversion
            use_ai = True
            markdown_content = ""
            
            if input_path.suffix.lower() in ['.txt', '.rtf']:
                # Try AI analysis for text files
                if self.show_progress:
                    print(f"🔍 Analyzing document structure...")
                elif not self.debug:
                    print(f"Analyzing document structure with AI...")
                    
                prompt = self._create_analysis_prompt(text_content)
                success, result = self._call_claude(prompt)
                
                if success:
                    markdown_content = result
                    if self.debug:
                        print("Using AI-generated markdown")
                    
                    # Send notification that markdown analysis is complete
                    try:
                        subprocess.run([
                            'osascript', '-e', 
                            f'display notification "Markdown structure created for {input_path.name}" with title "Word Formatter" subtitle "AI Analysis Complete ✓"'
                        ], capture_output=True)
                    except:
                        pass  # Silently fail if notification fails
                else:
                    # Fallback to simple conversion
                    if self.show_progress:
                        print(f"⚡ Falling back to simple text conversion")
                        print(f"   Reason: {result}")
                    else:
                        print(f"AI analysis unavailable: {result}")
                        print("Using simple text conversion...")
                    markdown_content = self._simple_text_to_markdown(text_content)
                    use_ai = False
            else:
                # For markdown files, use content as-is
                if self.show_progress:
                    print(f"📝 Processing markdown file directly")
                markdown_content = text_content
                use_ai = False
            
            # Save intermediate markdown if enabled (not just for debug)
            if self.save_markdown or self.debug:
                markdown_path = output_path.parent / f"{input_path.stem}_markdown.md"
                with open(markdown_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                if self.show_progress:
                    print(f"💾 Markdown saved to: {markdown_path.name}")
                elif self.debug:
                    print(f"Markdown saved to: {markdown_path}")
            
            # Create temporary markdown file for conversion
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
                temp_file.write(markdown_content)
                temp_path = temp_file.name
            
            try:
                # Convert markdown to Word using existing converter
                if self.show_progress:
                    print(f"🎨 Applying reference document formatting...")
                elif use_ai and not self.debug:
                    print(f"Applying reference formatting...")
                
                self.converter.convert(temp_path, str(output_path))
                
                # Send notification that Word document is complete
                try:
                    model_info = f" (AI: {self.model.upper()})" if use_ai else ""
                    subprocess.run([
                        'osascript', '-e', 
                        f'display notification "Word document created: {output_path.name}{model_info}" with title "Word Formatter" subtitle "Formatting Applied ✓"'
                    ], capture_output=True)
                except:
                    pass  # Silently fail if notification fails
                
                if self.show_progress:
                    print(f"✅ Success! Output: {output_path.name}")
                    if use_ai:
                        print(f"   AI Model used: {self.model.upper()}")
                
                return True
                
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
                
        except Exception as e:
            error_msg = f"Error during conversion: {e}"
            if self.show_progress:
                print(f"❌ {error_msg}")
            else:
                print(error_msg)
            
            # Log error if ERROR_LOG is set
            error_log = os.environ.get('ERROR_LOG')
            if error_log:
                try:
                    with open(error_log, 'a') as log:
                        import datetime
                        log.write(f"{datetime.datetime.now()}: {error_msg}\n")
                        log.write(f"  Input: {input_path}\n")
                        log.write(f"  Model: {self.model}\n\n")
                except:
                    pass  # Silently fail if can't write to log
            
            return False


def main():
    """Main entry point for AI-enhanced converter."""
    if len(sys.argv) < 2:
        print("Usage: python document_converter_ai.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Find reference format file
    script_dir = Path(__file__).parent
    reference_path = script_dir / "referenceformat.docx"
    
    if not reference_path.exists():
        reference_path = Path.home() / "Documents" / "referenceformat.docx"
    
    if not reference_path.exists():
        reference_path = Path.home() / "Desktop" / "referenceformat.docx"
    
    if not reference_path.exists():
        print("Error: Reference format file not found. Please place 'referenceformat.docx' in one of these locations:")
        print(f"  - {script_dir}")
        print(f"  - {Path.home() / 'Documents'}")
        print(f"  - {Path.home() / 'Desktop'}")
        sys.exit(1)
    
    # Create converter and process
    converter = AIDocumentConverter(str(reference_path))
    success = converter.convert_with_ai(input_file, output_file)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()