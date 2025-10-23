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

CRITICAL: Chapters use IDENTICAL formatting whether in a book or standalone!

DOCUMENT TYPE DETECTION:
Determine if this is:
- **COMPLETE BOOK**: Has book title, Table of Contents, and multiple chapters
- **SINGLE CHAPTER**: Just one chapter/talk without TOC

HEADING STRUCTURE:

FOR COMPLETE BOOKS:
- # Book Title (becomes Title style in Word - largest font)
- # Table of Contents (H1, treated like a chapter)
- # Chapter 1: [Name] (H1)
- ## Section in Chapter (H2)
- ### Subsection (H3)

FOR SINGLE CHAPTERS (no TOC, no book title):
- # Chapter/Talk Title (H1 - same as chapter in book)
- ## Section in Chapter (H2 - same as in book)
- ### Subsection (H3 - same as in book)

KEY POINT: A chapter has the same structure whether it's in a book or standalone. The only difference is books have Title + TOC before the chapters.

UNIVERSAL FORMATTING RULES (apply to ALL):

1. DETECT AND FORMAT SECTION HEADINGS:
   - Identify major sections, subsections, and sub-subsections
   - Use # (H1) for main title/chapter, ## (H2) for sections, ### (H3) for subsections
   - Preserve the natural hierarchy of the content
   - Headings should NOT end with periods, question marks, or exclamation points
   - Keep headings concise (not full sentences)

2. LISTS:
   - Detect lists (both bulleted and numbered) and format appropriately
   - Preserve list structure and indentation

3. RECOGNIZE QUOTES, CITATIONS, AND SPECIAL BLOCKS:
   - Format as blockquotes with > prefix
   - Maintain proper citation formatting

4. PRESERVE ALL ORIGINAL CONTENT:
   - Do not add any content that wasn't in the original
   - Maintain the original tone and style
   - Focus on structure, not rewriting

5. ⚠️ CRITICAL: PRESERVE ORIGINAL LINE ORDER:
   - NEVER rearrange, reorder, or move lines from their original position
   - Keep everything in EXACTLY the same sequence as the input text
   - If the original has: Title → Sutra → Content, keep that exact order
   - Do NOT move sutras/epigraphs/quotes before titles
   - Do NOT reorganize content for "better structure"
   - Only ADD markdown formatting symbols (# ## * > etc.) without changing position
   - Example: If input is:
     "Title
      Sanskrit text
      Translation
      Content"
   - Output should be:
     "# Title
      > *Sanskrit text*
      > Translation
      Content"
   - NOT:
     "> *Sanskrit text*
      > Translation
      # Title
      Content"

6. FORMAT CODE BLOCKS:
   - Identify code snippets and format with triple backticks

7. IDENTIFY TABLES:
   - Convert to markdown table format

8. ITALICIZE NON-ENGLISH TEXT with *text* formatting:
   - Sanskrit transliterations (text with diacritical marks like ā, ī, ū, ṛ, ṣ, ṇ, ṃ, ḥ, etc.)
   - Devanagari script (हिन्दी, संस्कृत)
   - Arabic, Hebrew, Chinese, Japanese, or any other non-Latin scripts
   - Romanized/transliterated words from other languages
   - Example: *Vāg vai brahma | vācā hy evedaṃ sarvaṃ sṛṣṭam*

9. SPECIAL FORMATTING FOR OPENING QUOTES (sutras, epigraphs, etc.):
   - Detect Sanskrit/spiritual quotes at the beginning of sections/chapters
   - Format as centered blockquotes with this pattern:
     > *Sanskrit transliteration in italics*
     > English translation
     > — Source citation (always start with em dash)
   - Use > for blockquote with single line breaks
   - The transliteration should be italicized
   - ALWAYS use em dash (—) before attribution/source, not hyphen (-)

10. SPECIAL FORMATTING FOR HIERARCHICAL LISTS (roles, principles, qualities, etc.):
   - Look for patterns like "Transformational Roles", "Meta Roles", "Principles", "Types", "Aspects", etc.
   - Format these headers using appropriate heading level based on document type and context
   - CRITICAL: Format numbered items with their numbers but NOT as markdown numbered lists
   - To preserve the numbers, add a backslash before the period: 1\. The Teacher (not 1. The Teacher)
   - Format sub-items with bullet points (•) and proper indentation (4 spaces)
   - Example pattern:
     ### Transformational Roles

     16\. The Facilitator of Surrender
         • Teaches active alignment with divine will
         • Shows strength through yielding
         • Guides through release

     17\. The Mirror of Possibility
         • Reflects highest potential back to seekers
         • Shows what is possible
   - Use bullet character • (not -) with 4-space indentation for sub-items
   - This creates proper visual hierarchy while preserving exact numbering

11. DIALOGUE FORMATTING:
   - Keep dialogue as regular paragraphs with speaker names in bold
   - Format as: **Speaker Name**: dialogue text
   - Do NOT add bullet points to dialogue lines

CRITICAL REQUIREMENTS:
- Process the ENTIRE document in one response
- Do NOT ask for confirmation or permission to continue
- Do NOT break the response into parts or sections
- Do NOT stop midway through the document
- Convert ALL text provided, regardless of length
- ABSOLUTELY NO explanations, analysis, questions, or meta-commentary
- Do NOT include phrases like "Based on my analysis" or "This is a X document"
- Return ONLY the complete markdown formatted text - start directly with the content

CRITICAL REMINDERS:

0. ⚠️ NEVER REORDER CONTENT: Keep all lines in their ORIGINAL sequence. Do NOT move sutras, quotes, or any content before/after where they appear in the input.

1. CHAPTER FORMATTING IS IDENTICAL:
   - Single chapter "Talk 13: Love That Dares" → # Talk 13: Love That Dares (H1)
   - Chapter in book "Chapter 5: The Journey" → # Chapter 5: The Journey (H1)
   - Both use # (H1) for the chapter title
   - Both use ## (H2) for sections within the chapter
   - Both use ### (H3) for subsections

2. BOOKS vs SINGLE CHAPTERS:
   - Books START with: # Book Title, then # Table of Contents, then chapters
   - Single chapters START with: # Chapter Title (no book title, no TOC)
   - But the chapter itself has the same structure in both cases

3. SPECIAL FORMATTING (apply to ALL):
   - Italicize ALL non-English text (Sanskrit, transliterations, etc.)
   - Format opening quotes/sutras as centered blockquotes: > *Sanskrit* > Translation
   - Use proper hierarchical list formatting (escaped numbers: 1\.)
   - Format dialogue with **Speaker**: text (no bullets)

4. OUTPUT FORMAT:
   - No meta-commentary or analysis
   - Start directly with the formatted content
   - Preserve all original content exactly
   - Same rich formatting quality for all documents

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

                # Remove markdown code fences if Claude wrapped the output
                import re
                # Check if output starts with ```markdown or ``` and ends with ```
                if output.startswith('```'):
                    # Remove opening code fence (```markdown or just ```)
                    output = re.sub(r'^```(?:markdown)?\s*\n', '', output)
                    # Remove closing code fence
                    output = re.sub(r'\n```\s*$', '', output)

                # Check for incomplete response patterns
                incomplete_patterns = [
                    "Would you like me to continue",
                    "Shall I proceed",
                    "Should I continue",
                    "Let me know if",
                    "I can continue",
                    "break it down into",
                    "manageable sections",
                    "I'd be happy to help",
                    "Could you please provide",
                    "Please paste the text"
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
    
    def _is_bullet_point(self, line: str) -> bool:
        """
        Intelligently detect if a line is actually a bullet point.

        Returns True only for actual list items like:
        - item text
        * item text
        • item text

        Returns False for:
        **Name**: dialogue
        *italic text*
        --- separators
        """
        if not line:
            return False

        # Check for common bullet markers
        if line.startswith('- ') or line.startswith('* ') or line.startswith('• '):
            # Additional checks to avoid false positives
            # Not a separator like "---" or "***"
            if line.startswith('---') or line.startswith('***') or line.startswith('- -'):
                return False
            # Not dialogue/bold like "**Name**:"
            if line.startswith('**') or (line.startswith('*') and ':' in line[:20]):
                return False
            # Not italic text like "*text*"
            if line.startswith('*') and line.count('*') >= 2 and len(line) < 100:
                return False
            return True

        return False

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
    
    def _remove_duplicate_h1_headings(self, markdown_content: str) -> str:
        """
        Remove duplicate H1 headings from single-chapter documents.

        In single-chapter documents, there should only be ONE H1 heading (the chapter title).
        Sometimes Claude AI accidentally generates duplicate H1 headings, which causes
        sections to be misidentified as new chapters.

        This function detects and removes duplicate H1 headings while preserving the first one.
        """
        import re

        # Find all H1 headings (lines starting with # followed by space)
        h1_pattern = r'^# (?!#)(.*?)$'
        h1_matches = list(re.finditer(h1_pattern, markdown_content, re.MULTILINE))

        if len(h1_matches) <= 1:
            # No duplicates, nothing to fix
            return markdown_content

        # Check if this is a book (has TOC) or single chapter
        has_toc = bool(re.search(r'^# (?:Table of Contents|Contents|TOC)$', markdown_content, re.MULTILINE | re.IGNORECASE))

        if has_toc:
            # This is a book with TOC - multiple H1s are expected (Title, TOC, Chapter 1, Chapter 2, etc.)
            return markdown_content

        # Single chapter document with duplicate H1 headings - keep only the first one
        if self.debug:
            print(f"⚠️  WARNING: Found {len(h1_matches)} H1 headings in single-chapter document")
            print(f"   First H1: '{h1_matches[0].group(1)}'")
            for i, match in enumerate(h1_matches[1:], start=2):
                print(f"   Duplicate #{i}: '{match.group(1)}' at position {match.start()}")

        # Remove all duplicate H1 headings (keep only the first)
        lines = markdown_content.split('\n')
        first_h1_line = None
        lines_to_remove = []

        for i, line in enumerate(lines):
            if re.match(h1_pattern, line):
                if first_h1_line is None:
                    first_h1_line = i
                else:
                    # This is a duplicate - mark for removal
                    lines_to_remove.append(i)
                    if self.debug:
                        print(f"   Removing duplicate H1 at line {i+1}: {line}")

        # Remove duplicate H1 lines (and any empty line immediately after)
        cleaned_lines = []
        skip_next_empty = False
        for i, line in enumerate(lines):
            if i in lines_to_remove:
                skip_next_empty = True
                continue
            if skip_next_empty and line.strip() == '':
                skip_next_empty = False
                continue
            cleaned_lines.append(line)
            skip_next_empty = False

        cleaned_content = '\n'.join(cleaned_lines)

        if self.show_progress and len(h1_matches) > 1:
            print(f"   ✓ Removed {len(h1_matches) - 1} duplicate H1 heading(s)")

        return cleaned_content

    def _simple_text_to_markdown(self, text_content: str, is_first_chunk: bool = True) -> str:
        """
        Simple fallback conversion from text to markdown.

        Args:
            text_content: Text to convert
            is_first_chunk: True if this is the first chunk in a multi-chunk document
        """
        lines = text_content.split('\n')
        markdown_lines = []
        in_list = False
        in_sutra = False
        # Only allow first heading to be H1 in the first chunk
        first_heading_found = not is_first_chunk
        h2_count = 0  # Track H2 headings after first H1

        for line in lines:
            stripped = line.strip()

            if self.debug and ('sutra' in stripped.lower() or 'यथा' in stripped or 'Yathâ' in stripped):
                print(f"DEBUG LINE: {repr(stripped[:60])}, in_sutra={in_sutra}, h2_count={h2_count}")

            # Skip empty lines
            if not stripped:
                markdown_lines.append('')
                in_list = False
                # Don't reset in_sutra on empty lines - wait for actual content
                continue

            # Separators end sutra mode
            if stripped in ['---', '***', '___']:
                markdown_lines.append(line)
                in_sutra = False
                in_list = False
                continue
            
            # Skip lines that already have markdown headings
            if stripped.startswith('#'):
                markdown_lines.append(line)
                in_list = False
                # Track if this is a Sutra heading
                if 'sutra' in stripped.lower():
                    in_sutra = True
                    h2_count = 0  # Reset counter after Sutra
                elif stripped.startswith('##'):
                    h2_count += 1
                    in_sutra = False
            # Detect sutra text when in sutra mode
            elif in_sutra:
                # Clean up any existing markdown first (** and * mixed)
                clean_text = stripped.replace('**', '').replace('*', '').strip()

                if self.debug:
                    print(f"DEBUG SUTRA: stripped={repr(stripped[:50])}, clean={repr(clean_text[:50])}")

                # Check if this is sutra content (not a separator or heading)
                if clean_text and not clean_text.startswith('#') and clean_text not in ['---', '***', '___']:
                    # Check if it's Sanskrit, transliteration, or translation
                    has_sanskrit = any('\u0900' <= c <= '\u097F' for c in clean_text)
                    # Include macrons (ā), circumflex (â), dots below (ṭ), etc.
                    has_diacritics = any(c in clean_text for c in ['ā', 'ī', 'ū', 'ṛ', 'ṝ', 'ḷ', 'ḹ', 'ē', 'ō', 'ṃ', 'ḥ', 'ś', 'ṣ', 'ṇ', 'ḍ', 'ṭ', 'ñ', 'â', 'î', 'û', 'ê', 'ô'])
                    is_continuation = len(markdown_lines) > 0 and markdown_lines[-1].startswith('>')

                    if self.debug:
                        print(f"  sanskrit={has_sanskrit}, diacritics={has_diacritics}, continuation={is_continuation}")

                    if has_sanskrit or has_diacritics or is_continuation:
                        # Format as blockquote with italics for Sanskrit/transliteration
                        if has_sanskrit or has_diacritics:
                            markdown_lines.append(f"> *{clean_text}*")
                            if self.debug:
                                print(f"  -> Added blockquote with italics")
                        else:
                            # Translation (no italics for English translation)
                            markdown_lines.append(f"> {clean_text}")
                            if self.debug:
                                print(f"  -> Added blockquote (translation)")
                        in_list = False

                        # After 3 sutra lines, exit sutra mode
                        sutra_lines = [l for l in markdown_lines if l.startswith('>')]
                        if len(sutra_lines) >= 3:
                            in_sutra = False
                            if self.debug:
                                print(f"  -> Exiting sutra mode (3 lines collected)")
                        continue
            # Detect potential headings (lines that are title-cased or all caps)
            # Must be short, not contain sentence-ending punctuation, and not start with list markers
            elif (len(stripped) < 100 and
                (stripped.istitle() or stripped.isupper()) and
                not any(stripped.startswith(c) for c in ['-', '*', '•', '1', '2', '3']) and
                not stripped.endswith('.') and  # Not a sentence
                not stripped.endswith('?') and
                not stripped.endswith('!')):
                # Use H1 (#) for:
                # - First major heading (chapter/talk title)
                # - Sections and chapters (keywords)
                # Use H2 (##) for major sections
                # Use H3 (###) for the first subsection after Sutra, then back to H2
                if not first_heading_found or any(word in stripped.lower() for word in ['section', 'part', 'chapter', 'table of contents', 'contents', 'toc']):
                    # Use H1 for first heading or major structural elements
                    markdown_lines.append(f"\n# {stripped}\n")
                    first_heading_found = True
                    h2_count = 0
                elif h2_count == 0:
                    # First major section after chapter title
                    markdown_lines.append(f"\n## {stripped}\n")
                    h2_count += 1
                    # Set sutra mode if this is a Sutra heading
                    if 'sutra' in stripped.lower():
                        in_sutra = True
                elif h2_count == 1:
                    # Immediately after first H2 (Sutra), use H3 for narrative intro
                    markdown_lines.append(f"\n### {stripped}\n")
                    h2_count += 1
                else:
                    # Back to H2 for major sections
                    markdown_lines.append(f"\n## {stripped}\n")
                in_list = False
                in_sutra = False
            # Detect list items (but not dialogue, italics, or separators)
            elif self._is_bullet_point(stripped):
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
                # Only first chunk can have H1 headings
                is_first_chunk = (i == 0)
                markdown_chunks.append(self._simple_text_to_markdown(chunk, is_first_chunk=is_first_chunk))
        
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
        markdown_content = '\n\n'.join(markdown_chunks)

        # Post-process to remove duplicate H1 headings
        markdown_content = self._remove_duplicate_h1_headings(markdown_content)

        return markdown_content
    
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