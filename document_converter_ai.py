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

try:
    from alias_resolver import resolve_path
except ImportError:
    # If alias_resolver is not available, create a dummy function
    def resolve_path(path):
        return str(path)

class AIDocumentConverter:
    """Converts documents with AI-powered text analysis."""
    
    def __init__(self, reference_path: str, config_path: Optional[str] = None):
        # Resolve any aliases or symlinks
        self.reference_path = resolve_path(reference_path)
        self.converter = DocumentConverter(self.reference_path, config_path=config_path)
        self.config_path = config_path
        self.debug = os.environ.get('WORD_FORMATTER_DEBUG', '0') == '1'
        # Configuration options
        self.save_markdown = os.environ.get('SAVE_MARKDOWN', '1') == '1'  # Default: save markdown
        self.show_progress = os.environ.get('SHOW_PROGRESS', '1') == '1'  # Default: show progress
        self.model = os.environ.get('CLAUDE_MODEL', 'sonnet')  # Default: sonnet
        self.timeout = int(os.environ.get('CLAUDE_TIMEOUT', '600'))  # Default: 600 seconds (10 minutes)
        self.enable_haiku_fallback = os.environ.get('ENABLE_HAIKU_FALLBACK', '1') == '1'  # Default: enabled
    
    def _create_analysis_prompt(self, text_content: str) -> str:
        """Create the prompt for Claude to analyze and structure text."""
        return f"""Convert the following plain text to well-structured markdown format.

Instructions:
1. TITLE DETECTION: The first substantial line of text (not a date or other metadata) should be marked as #Heading0
   - This is typically the document title/name
   - Use exactly "#Heading0 " followed by the title text
   - Example: #Heading0 The Complete Guide to Spiritual Wisdom
2. Identify and mark other headings based on context and formatting cues:
   - Main sections or parts should use # (H1) - look for "Section", "Part", or similar major divisions
   - Chapters should use # (H1) - look for "Chapter" followed by numbers or titles
   - Sub-sections within chapters should use ## (H2)
   - Sub-sub-sections should use ### (H3), and so on
3. Detect lists (both bulleted and numbered) and format appropriately  
3. Recognize quotes, citations, and special blocks
4. Preserve all original text content exactly
5. Add markdown formatting only where it enhances structure
6. Use heading levels (# ## ###) based on document hierarchy as described above
7. Format code blocks if you detect code snippets
8. Identify tables and convert to markdown table format
9. ITALICIZE non-English text and transliterated text with *text* formatting:
   - Sanskrit transliterations (text with diacritical marks like ā, ī, ū, ṛ, ṣ, ṇ, ṃ, ḥ, etc.)
   - Devanagari script (हिन्दी, संस्कृत)
   - Arabic, Hebrew, Chinese, Japanese, or any other non-Latin scripts
   - Romanized/transliterated words from other languages
   - Example: *Vāg vai brahma | vācā hy evedaṃ sarvaṃ sṛṣṭam*
10. SPECIAL FORMATTING for chapter opening quotes:
   - Detect Sanskrit/spiritual quotes at the beginning of chapters
   - Format as centered blockquotes with this pattern:
     > *Sanskrit transliteration in italics*
     > English translation
     > Source citation
   - Use > for blockquote with single line breaks
   - The transliteration should be italicized
   - Remove any em dashes from citations
11. SPECIAL FORMATTING for hierarchical lists (like roles, principles, qualities):
   - Look for patterns like "Transformational Roles", "Meta Roles", "Principles", "Types", "Aspects", etc.
   - Format these headers using appropriate heading level based on document context (don't force H2)
   - CRITICAL: Format numbered items with their numbers but NOT as markdown numbered lists
   - To preserve the numbers, add a backslash before the period: 1\. The Teacher (not 1. The Teacher)
   - Format sub-items with bullet points (•) and proper indentation (4 spaces)
   - Example pattern:
     [Appropriate heading level] Transformational Roles
     
     16\. The Facilitator of Surrender
         • Teaches active alignment with divine will
         • Shows strength through yielding
         • Guides through release
     
     17\. The Mirror of Possibility
         • Reflects highest potential back to seekers
         • Shows what is possible
   - Use bullet character • (not -) with 4-space indentation for sub-items
   - This creates proper visual hierarchy while preserving exact numbering

CRITICAL REQUIREMENTS:
- Process the ENTIRE document in one response
- Do NOT ask for confirmation or permission to continue
- Do NOT break the response into parts or sections
- Do NOT stop midway through the document
- Convert ALL text provided, regardless of length
- No explanations, questions, or meta-commentary
- Return ONLY the complete markdown formatted text

Important:
- Do not add any content that wasn't in the original
- Maintain the original tone and style
- Focus on structure, not rewriting
- If the text already has clear structure, preserve it

Text to convert:
---
{text_content}
---"""
    
    def _call_claude(self, prompt: str, model: str = None) -> Tuple[bool, str]:
        """Call Claude CLI and return success status and output."""
        if model is None:
            model = self.model
            
        try:
            # Show progress if enabled
            if self.show_progress:
                print(f"🤖 Using Claude {model.upper()} model for AI analysis...")
            elif self.debug:
                print(f"Calling Claude ({model}) for text analysis...")
            
            # Use explicit Claude path if provided, otherwise use 'claude' from PATH
            claude_cmd = os.environ.get('CLAUDE_CLI_PATH', 'claude')
            
            # Use Claude in print mode for non-interactive output
            result = subprocess.run(
                [claude_cmd, '--model', model, '--print', prompt],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0 and result.stdout.strip():
                output = result.stdout.strip()
                
                # Check for incomplete response patterns
                incomplete_patterns = [
                    "Would you like me to continue",
                    "Shall I proceed",
                    "Should I continue",
                    "Let me know if",
                    "I can continue",
                    "break it down into",
                    "manageable sections"
                ]
                
                if any(pattern.lower() in output.lower() for pattern in incomplete_patterns):
                    error_msg = "Claude returned an incomplete response (asked for confirmation)"
                    if self.show_progress:
                        print(f"⚠️  {error_msg}")
                    elif self.debug:
                        print(error_msg)
                    return False, error_msg
                
                if self.show_progress:
                    print("✓ AI analysis completed successfully")
                elif self.debug:
                    print("Claude analysis successful")
                return True, output
            else:
                error_msg = result.stderr or "Unknown error"
                if self.show_progress:
                    print(f"⚠️  Claude returned an error: {error_msg}")
                elif self.debug:
                    print(f"Claude returned error: {error_msg}")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = f"Claude {model.upper()} analysis timed out after {self.timeout} seconds"
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
    
    def _detect_non_english_text(self, text: str) -> str:
        """Detect and italicize non-English and transliterated text."""
        import re
        
        # Pattern for Sanskrit transliteration with diacritical marks
        diacritical_pattern = r'[āīūṛṝḷḹēōṃḥśṣṇḍṭñ]'
        
        # Pattern for common non-Latin scripts
        non_latin_pattern = r'[\u0900-\u097F]|[\u0980-\u09FF]|[\u0A00-\u0A7F]|[\u0600-\u06FF]|[\u4E00-\u9FFF]|[\u3040-\u309F]|[\u30A0-\u30FF]'
        
        # Check if text contains diacritical marks or non-Latin scripts
        if re.search(diacritical_pattern, text, re.IGNORECASE) or re.search(non_latin_pattern, text):
            # Check if it's not already italicized
            if not (text.startswith('*') and text.endswith('*')):
                return f"*{text}*"
        
        return text
    
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
                # Check if it's a section or chapter
                if any(word in stripped.lower() for word in ['section', 'part', 'chapter']):
                    # Use H1 for sections and chapters
                    markdown_lines.append(f"\n# {stripped}\n")
                else:
                    # Use H2 for other headings
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
                # Regular paragraph - check for non-English text
                if in_list and stripped:
                    markdown_lines.append('')
                # Apply italicization to non-English text
                processed_line = self._detect_non_english_text(line)
                markdown_lines.append(processed_line)
                in_list = False
        
        return '\n'.join(markdown_lines)
    
    def _process_in_chunks(self, text_content: str, chunk_size: int = 20000) -> str:
        """Process large text in chunks and reassemble."""
        if len(text_content) <= chunk_size:
            # Small enough to process in one go
            prompt = self._create_analysis_prompt(text_content)
            success, result = self._call_claude(prompt)
            
            # Try Haiku if initial model times out
            if not success and "timed out" in result and self.enable_haiku_fallback and self.model != 'haiku':
                if self.show_progress:
                    print(f"🔄 Trying faster Haiku model...")
                success, result = self._call_claude(prompt, 'haiku')
                if success:
                    self.model = 'haiku'
            
            return result if success else None
        
        # Split into chunks at paragraph boundaries
        paragraphs = text_content.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            if current_size + para_size > chunk_size and current_chunk:
                # Save current chunk and start new one
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        if self.show_progress:
            print(f"📦 Processing {len(chunks)} chunks...")
        
        # Process each chunk
        markdown_chunks = []
        for i, chunk in enumerate(chunks):
            if self.show_progress:
                print(f"   Processing chunk {i+1}/{len(chunks)}...")
            
            # Send notification for chunk progress
            try:
                percent = int((i / len(chunks)) * 100)
                notification_msg = f"Processing chunk {i+1} of {len(chunks)} ({percent}% complete)"
                
                # Try terminal-notifier first if available
                if subprocess.run(['which', 'terminal-notifier'], capture_output=True).returncode == 0:
                    subprocess.run([
                        'terminal-notifier',
                        '-title', 'AI Document Converter',
                        '-subtitle', 'Analyzing text structure...',
                        '-message', notification_msg,
                        '-sender', 'com.apple.finder'
                    ], capture_output=True, timeout=1)
                else:
                    # Fallback to osascript
                    subprocess.run([
                        'osascript', '-e',
                        f'display notification "{notification_msg}" with title "AI Document Converter" subtitle "Analyzing text structure..."'
                    ], capture_output=True, timeout=1)
            except:
                pass  # Silently fail if notification fails
            
            prompt = self._create_analysis_prompt(chunk)
            success, result = self._call_claude(prompt)
            
            if not success and "timed out" in result and self.enable_haiku_fallback:
                if self.show_progress:
                    print(f"   🔄 Retrying chunk {i+1} with Haiku...")
                success, result = self._call_claude(prompt, 'haiku')
            
            if success:
                markdown_chunks.append(result)
            else:
                # Fallback to simple conversion for this chunk
                if self.show_progress:
                    print(f"   ⚠️ Chunk {i+1} failed, using simple conversion")
                markdown_chunks.append(self._simple_text_to_markdown(chunk))
        
        # Send completion notification for chunked processing
        if len(chunks) > 1:
            try:
                completion_msg = f"All {len(chunks)} chunks processed successfully!"
                
                # Try terminal-notifier first if available
                if subprocess.run(['which', 'terminal-notifier'], capture_output=True).returncode == 0:
                    subprocess.run([
                        'terminal-notifier',
                        '-title', 'AI Document Converter',
                        '-subtitle', 'Analysis Complete ✓',
                        '-message', completion_msg,
                        '-sound', 'default',
                        '-sender', 'com.apple.finder'
                    ], capture_output=True, timeout=1)
                else:
                    # Fallback to osascript
                    subprocess.run([
                        'osascript', '-e',
                        f'display notification "{completion_msg}" with title "AI Document Converter" subtitle "Analysis Complete ✓"'
                    ], capture_output=True, timeout=1)
            except:
                pass
        
        # Reassemble the markdown
        return '\n\n'.join(markdown_chunks)
    
    def convert_with_ai(self, input_path: str, output_path: Optional[str] = None) -> bool:
        """Convert document using AI analysis."""
        # Resolve any aliases or symlinks
        input_path = Path(resolve_path(input_path))
        
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
                
                # Check if chunking is needed
                chunk_threshold = int(os.environ.get('CHUNK_THRESHOLD', '10000'))  # Changed to 10KB
                if len(text_content) > chunk_threshold:
                    if self.show_progress:
                        print(f"📊 Document size: {len(text_content):,} chars, using chunked processing...")
                
                # Use chunking method which handles both small and large files
                result = self._process_in_chunks(text_content, chunk_threshold)
                
                if result:
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
                        print(f"   Reason: All AI attempts failed")
                    else:
                        print(f"AI analysis unavailable")
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
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-enhanced document converter')
    parser.add_argument('input_file', help='Input file to convert')
    parser.add_argument('output_file', nargs='?', help='Output file path (optional)')
    parser.add_argument('--reference', '-r', help='Reference format document path')
    parser.add_argument('--config', '-c', help='Configuration file path')
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output_file
    
    # Use reference format from argument or find default
    if args.reference:
        reference_path = Path(args.reference)
        if not reference_path.exists():
            print(f"Error: Reference format file not found: {args.reference}")
            sys.exit(1)
    else:
        # Find default reference format file
        script_dir = Path(__file__).parent
        reference_path = script_dir / "References" / "referenceformat.docx"
        
        if not reference_path.exists():
            # Try old location for backward compatibility
            reference_path = script_dir / "referenceformat.docx"
        
        if not reference_path.exists():
            reference_path = Path.home() / "Documents" / "referenceformat.docx"
        
        if not reference_path.exists():
            reference_path = Path.home() / "Desktop" / "referenceformat.docx"
        
        if not reference_path.exists():
            print("Error: Reference format file not found. Please place 'referenceformat.docx' in one of these locations:")
            print(f"  - {script_dir / 'References'}")
            print(f"  - {script_dir}")
            print(f"  - {Path.home() / 'Documents'}")
            print(f"  - {Path.home() / 'Desktop'}")
            sys.exit(1)
    
    # Create converter and process
    converter = AIDocumentConverter(str(reference_path), config_path=args.config)
    success = converter.convert_with_ai(input_file, output_file)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()