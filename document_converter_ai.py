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
import time
import datetime
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

    def __init__(self, reference_path: Optional[str] = None, config_path: Optional[str] = None):
        """Initialize AI Document Converter.

        Args:
            reference_path: Path to reference template. If None, uses path from config.
            config_path: Path to configuration file. If None, uses default config location.
        """
        # Load config first to get reference template path
        from config_loader import FormatterConfig
        self.config = FormatterConfig(config_path)

        # Resolve reference path from config if not provided
        if reference_path is None:
            template_path = self.config.get_reference_template_path()
            if template_path:
                self.reference_path = str(template_path)
            else:
                # Fall back to default in References folder
                script_dir = Path(__file__).parent
                self.reference_path = str(script_dir / "References" / "referenceformat.docx")
        else:
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
    
    def _create_analysis_prompt(self, text_content: str, toc_chapters: list = None, ultra_strict: bool = False) -> str:
        """Create the prompt for Claude to analyze and structure text.

        Args:
            text_content: The text to convert to markdown
            toc_chapters: List of chapter names extracted from TOC (if present)
            ultra_strict: If True, adds enhanced anti-hallucination warnings (for retry attempts)
        """
        # Build TOC-specific instructions if chapters were detected
        toc_instructions = ""
        if toc_chapters and len(toc_chapters) > 0:
            chapter_list = "\n".join(f"  - {ch}" for ch in toc_chapters)
            toc_instructions = f"""
📚 TABLE OF CONTENTS DETECTED:
The document contains these chapters (from TOC):
{chapter_list}

CRITICAL: Use THESE chapter names for H1 headings.
- Do NOT create different chapter names
- Do NOT add chapters not in this list
- Do NOT invent additional chapters
- Use EXACT names from TOC
"""
        else:
            toc_instructions = """
📄 SINGLE CHAPTER/DOCUMENT FORMAT (No TOC detected):
- Use H1 for the main chapter/talk/article title ONLY
- Use H2 for major sections within the chapter
- Use H3 for subsections
- Do NOT invent multiple chapters
- Treat this as ONE cohesive document
"""

        # Add ultra-strict warnings for retry attempts
        ultra_strict_section = ""
        if ultra_strict:
            ultra_strict_section = """

🔴🔴🔴 CRITICAL: ULTRA-STRICT MODE ENABLED 🔴🔴🔴

This is a RETRY attempt because previous AI output FAILED validation.

🚨 WHAT WENT WRONG PREVIOUSLY:
- AI added dialogue that doesn't exist in original
- AI created conversations between speakers
- AI "improved" or "clarified" content by adding text
- AI fabricated character names not in source

⛔ ABSOLUTE PROHIBITIONS - THESE ARE FAILURES:
1. Writing ANY speaker name not explicitly in the original
2. Creating dialogue format (Speaker: text) when original doesn't have it
3. Adding explanatory text "to help the reader"
4. Expanding abbreviated content into full sentences
5. "Inferring" what should be between paragraphs

✅ YOUR ONLY ALLOWED ACTIONS:
1. Add # or ## before text that's ALREADY a heading
2. Add * around non-English text that's ALREADY there
3. Add > before blockquotes that are ALREADY there
4. NOTHING ELSE

🔍 SELF-CHECK BEFORE SUBMITTING:
□ Did I add ANY words not in the original? (If YES → FAIL)
□ Did I create ANY dialogue format? (If YES → FAIL)
□ Did I add ANY speaker names? (If YES → FAIL)
□ Did I only add markdown symbols? (If NO → FAIL)

⚠️ IF YOU'RE UNSURE: Just copy the text exactly and add ## before headings. That's it.

"""

        return f"""Convert the following plain text to well-structured markdown format.
{ultra_strict_section}
🚨 ABSOLUTELY CRITICAL - ZERO TOLERANCE RULES - READ FIRST:

⚠️⚠️⚠️ CRITICAL OUTPUT FORMAT ⚠️⚠️⚠️
- Return ONLY the markdown formatted text
- Start IMMEDIATELY with the first heading or content from the document
- NO introductions, explanations, analysis, or meta-commentary
- NO phrases like "Here's the formatted text", "I'll analyze", "Based on my analysis"
- NO "This is a X document" or ANY commentary about the document
- Your FIRST character should be # or > or actual text from the document

WRONG: "I'll format this text for you. # Chapter 1..."
RIGHT: "# Chapter 1..."

1. ⛔ NEVER ADD, REMOVE, OR FABRICATE ANY CONTENT
   - Do NOT create dialogue that doesn't exist in the original
   - Do NOT add characters, names, speakers, or people not in original
   - Do NOT expand, elaborate, paraphrase, or "improve" the text
   - Do NOT write what you think should be there
   - Do NOT add your own interpretations or explanations
   - ⚠️ Do NOT remove, skip, or omit ANY original text - even short headings like "Sutra 47"
   - ⚠️ EVERY line from the original must appear in your output
   - ONLY format what IS ACTUALLY in the original text
   - IF YOU ADD EVEN ONE SENTENCE NOT IN THE ORIGINAL, YOU HAVE COMPLETELY FAILED
   - IF YOU REMOVE EVEN ONE SENTENCE FROM THE ORIGINAL, YOU HAVE COMPLETELY FAILED

2. ✅ YOUR ONLY JOB: ADD MARKDOWN FORMATTING SYMBOLS
   - Add # ## ### for headings (only to text that's already there)
   - Add * for italics (only around non-English text already there)
   - Add > for blockquotes (only around quoted text already there)
   - Add markdown list formatting to lists already there
   - DO NOT CHANGE, REARRANGE, OR ADD ANY ACTUAL WORDS OR SENTENCES
   - Every sentence in your output must exist in the input

3. ⚠️ VERIFICATION: Before outputting, ask yourself:
   - "Is EVERY sentence in my output present in the original?"
   - "Did I invent ANY dialogue, characters, or content?"
   - "Am I ONLY adding markdown symbols to existing text?"
   - If answer is NO to any question, START OVER

{toc_instructions}

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
   - ⚠️ DETECT DESCRIPTIVE SECTION HEADINGS:
     - Look for standalone paragraphs that set scene/time/location
     - Examples: "A Week Later, Before Dawn at...", "The Next Morning", "Three Days Later"
     - These typically appear AFTER opening quotes/sutras and BEFORE narrative content
     - Format as ## (H2) even if they're complete phrases/sentences
     - Example: "A Week Later, Before Dawn at Kanha Shantivanam" → ## A Week Later, Before Dawn at Kanha Shantivanam

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
   - ⚠️ PRESERVE SUTRA TITLES/NUMBERS: If you see "Sutra 47", "Verse 12", etc. as standalone heading, format as ## heading
   - Example structure:
     ## Sutra 47

     > *sanskrit text...*
     > *transliteration...*
     > Translation...
   - Detect Sanskrit/spiritual quotes at the beginning of sections/chapters
   - ⚠️ CRITICAL: PRESERVE LABELS EXACTLY as they appear in the original
   - If original has "Sanskrit: [text]", keep "Sanskrit: [text]" character-for-character
   - If original has "Transliteration: [text]", keep "Transliteration: [text]" character-for-character
   - If original has "Translation: [text]", keep "Translation: [text]" character-for-character
   - Your ONLY job: Add > and * markdown formatting symbols to what's already there
   - NEVER modify, rewrite, shorten, or substitute the actual Sanskrit/transliteration/translation content
   - Pattern for formatting WITH labels (if present in original):
     > Sanskrit: यो विविक्तस्थानं सेवते, यो लोकबन्धमुन्मूलयति, निस्त्रैगुण्यो भवति, योगक्षेमं त्यजति
     > Transliteration: yo viviktasthanaṁ sevate yo lokabandhamunmûlayati nistraiguṇyo bhavati yogakṣemaṁ tyajati
     > Translation: Someone who worships alone, lets go of worldly attachments, becomes free from the three gunas, and gives up material security is beyond illusion.
   - Pattern for formatting WITHOUT labels (if not in original):
     > *devanagari text* (if present, italicize)
     > *transliteration text* (if present, also italicize)
     > English translation (plain text, no italics)
     > — Source citation (if present, always start with em dash)
   - Use > for blockquote with single line breaks
   - Both Devanagari AND transliteration should be italicized when NO labels exist
   - ALWAYS use em dash (—) before attribution/source, not hyphen (-)
   - Example CORRECT with labels (preserve exactly):
     > Sanskrit: यो विविक्तस्थानं सेवते, यो लोकबन्धमुन्मूलयति, निस्त्रैगुण्यो भवति, योगक्षेमं त्यजति
     > Transliteration: yo viviktasthanaṁ sevate yo lokabandhamunmûlayati nistraiguṇyo bhavati yogakṣemaṁ tyajati
     > Translation: Someone who worships alone, lets go of worldly attachments, becomes free from the three gunas, and gives up material security is beyond illusion.
   - Example CORRECT without labels (italicize):
     > *यो विविक्तस्थानं सेवते*
     > *yo viviktasthanaṁ sevate*
     > Someone who worships alone...

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
            start_time = time.time()
            if self.show_progress:
                print(f"🤖 Using Claude {model.upper()} model for AI analysis...")
                print(f"🕐 Started: {datetime.datetime.now().strftime('%H:%M:%S')}")
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

            elapsed = time.time() - start_time
            
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
                    print(f"⏱️  Elapsed: {elapsed:.1f}s")
                elif self.debug:
                    print(f"Claude analysis successful (took {elapsed:.1f}s)")
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

    def _fix_sutra_placement(self, markdown_content: str) -> str:
        """
        Fix opening sutras/epigraphs that appear BEFORE the chapter title.

        This is a safety net in case the AI prompt doesn't prevent reordering.
        The AI prompt instructs Claude to preserve original line order, but this
        post-processing ensures correct placement even if the AI doesn't follow instructions.

        Pattern to fix:
        > *Sanskrit text*
        > *Transliteration*
        > Translation

        # Chapter Title

        Should be:
        # Chapter Title

        > *Sanskrit text*
        > *Transliteration*
        > Translation
        """
        import re

        # Pattern: blockquote(s) followed by blank line(s) followed by H1 heading
        # This captures opening sutras/epigraphs that appear before the chapter title
        pattern = r'^((?:>\s*\*[^*]+\*\s*\n)+(?:>\s*[^\n]+\n)*)\n+(# .+)$'

        match = re.search(pattern, markdown_content, re.MULTILINE)

        if match:
            blockquote_section = match.group(1)
            h1_heading = match.group(2)

            if self.debug:
                print(f"⚠️  Found opening blockquote BEFORE H1 title")
                print(f"   Moving blockquote to appear AFTER the title")

            # Replace the matched section with title first, then blockquote
            replacement = f"{h1_heading}\n\n{blockquote_section}"
            markdown_content = re.sub(pattern, replacement, markdown_content, count=1, flags=re.MULTILINE)

            if self.show_progress:
                print(f"   ✓ Fixed opening sutra placement (moved after title)")

        return markdown_content

    def _extract_toc_chapters(self, text_content: str) -> list:
        """
        Extract chapter names from Table of Contents if present.

        Args:
            text_content: The full text content to search for TOC

        Returns:
            List of chapter names found in TOC, or empty list if no TOC
        """
        import re

        # Find TOC section - look for common TOC headers
        toc_patterns = [
            r'(?i)(table\s+of\s+contents|contents|index)(.*?)(?=\n\n[A-Z#]|\Z)',
            r'(?i)^(toc)\s*$\n(.*?)(?=\n\n[A-Z#]|\Z)'
        ]

        chapters = []
        for pattern in toc_patterns:
            match = re.search(pattern, text_content, re.DOTALL | re.MULTILINE)
            if match:
                toc_text = match.group(2) if len(match.groups()) > 1 else match.group(1)

                if self.debug:
                    print(f"📚 Found TOC section: {len(toc_text)} characters")

                # Extract chapter names - look for various patterns:
                # 1. "Chapter X: Name" or "Chapter X - Name"
                # 2. Numbered lines "1. Name" or "1 Name"
                # 3. Standalone capitalized lines (potential chapter names)

                # Pattern 1: Explicit "Chapter" keyword
                chapter_matches = re.findall(
                    r'(?i)chapter\s+\d+[:\-\s]+([^\n]{5,80})',
                    toc_text
                )
                chapters.extend([m.strip() for m in chapter_matches])

                # Pattern 2: Numbered items (1. Something, 2. Something)
                if not chapters:
                    numbered_matches = re.findall(
                        r'^\s*\d+[\.\)]\s+([A-Z][^\n]{10,80})$',
                        toc_text,
                        re.MULTILINE
                    )
                    chapters.extend([m.strip() for m in numbered_matches])

                # Pattern 3: Lines that look like titles (all caps or title case, standalone)
                if not chapters:
                    title_matches = re.findall(
                        r'^([A-Z][A-Z\s]{10,80})$|^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,})$',
                        toc_text,
                        re.MULTILINE
                    )
                    for match in title_matches:
                        title = next((x for x in match if x), None)
                        if title:
                            chapters.append(title.strip())

                if chapters:
                    if self.debug or self.show_progress:
                        print(f"   ✓ Extracted {len(chapters)} chapters from TOC")
                        for i, ch in enumerate(chapters[:5], 1):
                            print(f"      {i}. {ch}")
                        if len(chapters) > 5:
                            print(f"      ... and {len(chapters) - 5} more")
                    break

        return chapters

    def _show_attempt_alert(self, config: dict):
        """Display detailed alert for each AI conversion attempt."""
        model_name = config['model'].upper()
        attempt_num = config['attempt']
        is_strict = config['strict']
        total_attempts = 4

        prompt_type = "ULTRA-STRICT (enhanced anti-hallucination rules)" if is_strict else "Standard (zero-tolerance rules)"

        if self.show_progress or self.debug:
            print(f"\n{'='*60}")
            if attempt_num == 1:
                print(f"🤖 AI CONVERSION - ATTEMPT {attempt_num} of {total_attempts}")
            else:
                retry_label = "RETRY" if attempt_num == 2 else ("MODEL SWITCH" if attempt_num == 3 else "FINAL AI ATTEMPT")
                print(f"🔄 AI CONVERSION - ATTEMPT {attempt_num} of {total_attempts} ({retry_label})")
            print(f"{'='*60}")
            print(f"Model: Claude {model_name}")
            print(f"Prompt: {prompt_type}")

            if attempt_num == 1:
                print(f"Strategy: Initial attempt with default settings")
            elif attempt_num == 2:
                print(f"Changes: Enhanced prompt with explicit red-flag examples")
                print(f"Strategy: Same model, much stricter instructions")
            elif attempt_num == 3:
                print(f"Changes: Switched to most capable OPUS model")
                print(f"Strategy: Higher capability model may better follow rules")
                print(f"Note: This may take longer but should be more accurate")
            elif attempt_num == 4:
                print(f"Changes: Switched to faster HAIKU model")
                print(f"Strategy: Sometimes simpler models follow rules better")
                print(f"Note: This is the last AI attempt before rule-based fallback")

            print(f"{'='*60}\n")

    def _show_failure_alert(self, config: dict, validation_details: dict):
        """Display detailed failure alert with next action."""
        model_name = config['model'].upper()
        attempt_num = config['attempt']
        total_attempts = 4

        if self.show_progress or self.debug:
            print(f"\n{'!'*60}")
            print(f"⚠️  ATTEMPT {attempt_num} FAILED - VALIDATION DETECTED ISSUES")
            print(f"{'!'*60}")
            print(f"Problem: AI added content not in original")
            if 'dialogue_lines' in validation_details:
                print(f"Details: Detected {validation_details['dialogue_lines']} dialogue lines (original had {validation_details['original_lines']})")
            elif 'length_ratio' in validation_details:
                print(f"Details: Output {validation_details['length_ratio']:.0%} the size of input")

            if attempt_num < total_attempts:
                if attempt_num == 1:
                    print(f"Action: Retrying with stricter prompt on same model")
                    print(f"Next: Attempt 2/4 with ULTRA-STRICT prompt")
                elif attempt_num == 2:
                    print(f"Action: Switching to more capable OPUS model")
                    print(f"Next: Attempt 3/4 with OPUS + ULTRA-STRICT prompt")
                elif attempt_num == 3:
                    print(f"Action: Trying HAIKU model (faster, different approach)")
                    print(f"Next: Attempt 4/4 with HAIKU + ULTRA-STRICT prompt")
            else:
                print(f"Action: All AI models exhausted, falling back to rule-based")

            print(f"{'!'*60}\n")

    def _show_success_alert(self, config: dict):
        """Display success alert when validation passes."""
        model_name = config['model'].upper()
        attempt_num = config['attempt']
        is_strict = config['strict']
        prompt_type = "ULTRA-STRICT" if is_strict else "Standard"

        if self.show_progress or self.debug:
            print(f"\n{'='*60}")
            print(f"✅ AI CONVERSION SUCCESSFUL - ATTEMPT {attempt_num} of 4")
            print(f"{'='*60}")
            print(f"Model: Claude {model_name}")
            print(f"Prompt: {prompt_type}")
            print(f"Validation: PASSED - No fabricated content detected")
            print(f"Content: Original text preserved exactly")
            print(f"Quality: AI-enhanced structure and formatting")
            print(f"{'='*60}\n")

    def _show_all_attempts_failed_alert(self, attempts: list):
        """Display final alert when all AI attempts fail."""
        if self.show_progress or self.debug:
            print(f"\n{'!'*60}")
            print(f"⚠️  ALL AI ATTEMPTS EXHAUSTED")
            print(f"{'!'*60}")
            print(f"Problem: All 4 AI attempts detected fabricated content")
            print(f"Models Tried:")
            for i, attempt in enumerate(attempts, 1):
                model = attempt['model'].upper()
                prompt = "standard" if not attempt['strict'] else "ultra-strict"
                status = "Failed" if i < len(attempts) else "Failed"
                print(f"  {i}. {model} ({prompt} prompt) - {status}")
            print(f"Action: Falling back to rule-based conversion")
            print(f"Safety: Original content will be preserved exactly")
            print(f"{'!'*60}\n")

    def _attempt_ai_conversion_with_retries(self, text_content: str, toc_chapters: list = None) -> Optional[str]:
        """
        Attempt AI conversion with up to 4 retries using different strategies.

        Strategy:
        1. Attempt 1: Sonnet + Standard prompt
        2. Attempt 2: Sonnet + ULTRA-STRICT prompt
        3. Attempt 3: Opus + ULTRA-STRICT prompt
        4. Attempt 4: Haiku + ULTRA-STRICT prompt

        Returns:
            Markdown content if successful, None if all attempts fail
        """
        attempts = [
            {'model': 'sonnet', 'strict': False, 'attempt': 1},
            {'model': 'sonnet', 'strict': True, 'attempt': 2},
            {'model': 'opus', 'strict': True, 'attempt': 3},
            {'model': 'haiku', 'strict': True, 'attempt': 4}
        ]

        for attempt_config in attempts:
            # Show attempt alert
            self._show_attempt_alert(attempt_config)

            # Create prompt (standard or ultra-strict)
            prompt = self._create_analysis_prompt(
                text_content,
                toc_chapters,
                ultra_strict=attempt_config['strict']
            )

            # Call Claude with specified model
            success, result = self._call_claude(prompt, model=attempt_config['model'])

            if success:
                # Validate result
                if self.show_progress or self.debug:
                    print(f"🔍 Validating AI output for hallucinations...")

                validation_passed = self._validate_no_hallucination(text_content, result)

                if validation_passed:
                    # SUCCESS!
                    self._show_success_alert(attempt_config)
                    return result
                else:
                    # Validation failed - extract details for alert
                    validation_details = self._get_validation_failure_details(text_content, result)
                    self._show_failure_alert(attempt_config, validation_details)
            else:
                # Claude call failed
                if self.show_progress or self.debug:
                    print(f"\n⚠️  Claude API call failed: {result}")
                    if attempt_config['attempt'] < 4:
                        print(f"   Proceeding to next attempt...")

        # All attempts exhausted
        self._show_all_attempts_failed_alert(attempts)
        return None

    def _get_validation_failure_details(self, original_text: str, markdown_output: str) -> dict:
        """Extract details about why validation failed."""
        import re

        # Count dialogue lines
        dialogue_pattern = r'^\*\*[A-Z][a-zA-Z\s]+\*\*:\s*.+$'
        dialogue_lines = len(re.findall(dialogue_pattern, markdown_output, re.MULTILINE))
        dialogue_count_in_original = len(re.findall(dialogue_pattern, original_text, re.MULTILINE))

        # Calculate length ratio
        def strip_markdown(text):
            text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
            text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            text = re.sub(r'\*([^*]+)\*', r'\1', text)
            text = re.sub(r'_([^_]+)_', r'\1', text)
            text = re.sub(r'^\s*[-*•]\s+', '', text, flags=re.MULTILINE)
            return text.strip()

        original_len = len(strip_markdown(original_text))
        output_len = len(strip_markdown(markdown_output))
        length_ratio = output_len / original_len if original_len > 0 else 1.0

        details = {}
        if dialogue_lines > 5 and dialogue_lines > dialogue_count_in_original * 1.5:
            details['dialogue_lines'] = dialogue_lines
            details['original_lines'] = dialogue_count_in_original
        elif length_ratio > 1.2:
            details['length_ratio'] = length_ratio

        return details

    def _validate_no_hallucination(self, original_text: str, markdown_output: str) -> bool:
        """
        Validate that AI didn't hallucinate or add content.

        Args:
            original_text: The original input text
            markdown_output: The AI-generated markdown output

        Returns:
            True if validation passes, False if hallucination detected
        """
        # Check if validation is enabled in config (default: enabled)
        validation_enabled = self.config.config.get('ai_validation', {}).get('enabled', True)

        if not validation_enabled:
            if self.debug:
                print(f"⚠️  AI validation disabled via configuration")
            return True

        import re

        # Get validation settings from config
        check_dialogue = self.config.config.get('ai_validation', {}).get('check_dialogue', True)
        check_length_ratio = self.config.config.get('ai_validation', {}).get('check_length_ratio', True)
        check_suspicious_speakers = self.config.config.get('ai_validation', {}).get('check_suspicious_speakers', True)
        max_length_ratio = self.config.config.get('ai_validation', {}).get('max_length_ratio', 1.2)
        dialogue_tolerance = self.config.config.get('ai_validation', {}).get('dialogue_tolerance', 1.5)

        # Strip markdown formatting to get raw text for comparison
        def strip_markdown(text):
            """Remove markdown formatting symbols"""
            text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
            text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            text = re.sub(r'\*([^*]+)\*', r'\1', text)
            text = re.sub(r'_([^_]+)_', r'\1', text)
            text = re.sub(r'^\s*[-*•]\s+', '', text, flags=re.MULTILINE)
            text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
            text = re.sub(r'`([^`]+)`', r'\1', text)
            return text.strip()

        # Check 2: Detect dialogue patterns
        # FIX: Use different patterns for input (plain text) vs output (markdown with bold)
        if check_dialogue:
            # Pattern for markdown output with bold formatting: **Name**: text
            bold_dialogue_pattern = r'^\*\*[A-Z][a-zA-Z\s]+\*\*:\s*.+$'
            # Pattern for plain text input: Name: text (no bold markers)
            plain_dialogue_pattern = r'^[A-Z][a-zA-Z\s]+:\s+.+$'

            dialogue_lines = re.findall(bold_dialogue_pattern, markdown_output, re.MULTILINE)
            dialogue_count_in_original = len(re.findall(plain_dialogue_pattern, original_text, re.MULTILINE))

        # Calculate lengths for ratio check
        original_stripped = strip_markdown(original_text)
        output_stripped = strip_markdown(markdown_output)
        original_len = len(original_stripped)
        output_len = len(output_stripped)
        length_ratio = output_len / original_len if original_len > 0 else 0

        # Check 1: Output significantly longer than input
        if check_length_ratio and length_ratio > max_length_ratio:
            if self.debug or self.show_progress:
                print(f"⚠️  WARNING: Output is {length_ratio:.1%} the size of input")
                print(f"   Original: {original_len} chars, Output: {output_len} chars")
                print(f"   This may indicate AI added content not in the original")

        # Check if we found significant dialogue in output
        if check_dialogue and len(dialogue_lines) > 5:
            # Found multiple dialogue lines - check if they exist in original
            if len(dialogue_lines) > dialogue_count_in_original * dialogue_tolerance:
                if self.debug or self.show_progress:
                    print(f"⚠️  WARNING: Detected {len(dialogue_lines)} dialogue lines in output")
                    print(f"   Original had {dialogue_count_in_original} dialogue lines")
                    print(f"   AI may have fabricated dialogue - please review output carefully")
                return False

        # Check 3: Look for common speaker names that might be hallucinated
        if check_suspicious_speakers:
            suspicious_speakers = ['questioner', 'student', 'disciple', 'seeker', 'interviewer']
            found_suspicious = []

            for speaker in suspicious_speakers:
                pattern = rf'\*\*{speaker}\*\*:'.lower()
                if pattern in markdown_output.lower():
                    # Check if this speaker also exists in original (without bold)
                    plain_speaker = f"{speaker}:".lower()
                    if plain_speaker not in original_text.lower():
                        found_suspicious.append(speaker.title())

            if found_suspicious:
                if self.debug or self.show_progress:
                    print(f"⚠️  WARNING: Found dialogue with speaker(s) not in original:")
                    for speaker in found_suspicious:
                        print(f"   - {speaker}")
                    print(f"   AI may have fabricated dialogue - please review output carefully")
                return False

        # Validation passed
        if self.debug:
            print(f"✓ Validation passed: No obvious hallucination detected")
            print(f"  Length ratio: {length_ratio:.1%}, Dialogue lines: {len(dialogue_lines) if check_dialogue else 'N/A'}")

        return True

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
        # Extract TOC chapters first (if present)
        toc_chapters = self._extract_toc_chapters(text_content)

        if len(text_content) <= chunk_size:
            # Small enough to process in one go - use retry strategy
            result = self._attempt_ai_conversion_with_retries(text_content, toc_chapters)
            return result  # Returns None if all attempts fail (triggers fallback)
        
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
        
        # Process each chunk with full retry strategy
        markdown_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_start_time = time.time()
            if self.show_progress:
                print(f"\n{'='*60}")
                print(f"📦 PROCESSING CHUNK {i+1} of {len(chunks)}")
                print(f"🕐 Chunk started at {datetime.datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*60}\n")

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

            # Use full retry strategy for each chunk (prioritize quality)
            result = self._attempt_ai_conversion_with_retries(chunk, toc_chapters)

            chunk_elapsed = time.time() - chunk_start_time
            if result:
                # AI conversion succeeded with validation
                markdown_chunks.append(result)
                if self.show_progress:
                    print(f"✓ Chunk {i+1}/{len(chunks)} completed in {chunk_elapsed:.1f}s ({chunk_elapsed/60:.1f}min)")
            else:
                # All AI attempts failed for this chunk - use simple conversion as last resort
                if self.show_progress:
                    print(f"\n{'='*60}")
                    print(f"⚠️  CHUNK {i+1}/{len(chunks)}: All AI attempts exhausted")
                    print(f"{'='*60}")
                    print(f"Using rule-based conversion for this chunk only")
                    print(f"{'='*60}\n")
                # Only first chunk can have H1 headings
                is_first_chunk = (i == 0)
                markdown_chunks.append(self._simple_text_to_markdown(chunk, is_first_chunk=is_first_chunk))
                if self.show_progress:
                    print(f"✓ Chunk {i+1}/{len(chunks)} completed (rule-based) in {chunk_elapsed:.1f}s")
        
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

        # Validate final output for hallucinations
        if self.show_progress:
            print(f"🔍 Validating final output for hallucinations...")
        validation_passed = self._validate_no_hallucination(text_content, markdown_content)

        if not validation_passed:
            if self.show_progress or self.debug:
                print(f"\n{'!'*60}")
                print(f"⚠️  ALERT: AI VALIDATION FAILED")
                print(f"{'!'*60}")
                print(f"Issue: AI output contains fabricated or added content")
                print(f"Action: Falling back to rule-based text conversion")
                print(f"Result: Original content will be preserved exactly")
                print(f"{'!'*60}\n")
            # Fall back to simple conversion
            return None

        # Post-process to remove duplicate H1 headings
        markdown_content = self._remove_duplicate_h1_headings(markdown_content)

        # Post-process to fix sutra placement (safety net if AI doesn't follow instructions)
        markdown_content = self._fix_sutra_placement(markdown_content)

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
                    if self.show_progress:
                        print(f"📖 Reading RTF file...")
                    with open(input_path, 'r', encoding='utf-8') as f:
                        rtf_content = f.read()
                    if self.show_progress:
                        print(f"📝 Extracting text from RTF...")
                    text_content = rtf_to_text(rtf_content)
                    if self.show_progress or self.debug:
                        print(f"✓ Extracted text from RTF: {len(text_content)} characters")
                except Exception as e:
                    print(f"❌ Error reading RTF file: {e}")
                    return False
            else:
                # Read regular text files
                if self.show_progress:
                    print(f"📖 Reading text file...")
                with open(input_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                if self.show_progress:
                    print(f"✓ Read {len(text_content)} characters")
            
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
                        print(f"\n{'='*60}")
                        print(f"⚡ USING RULE-BASED TEXT CONVERSION")
                        print(f"{'='*60}")
                        print(f"Reason: AI analysis unavailable or failed")
                        print(f"Method: Rule-based markdown formatting")
                        print(f"Note: Original content preserved, basic formatting applied")
                        print(f"{'='*60}\n")
                    else:
                        print(f"\n{'='*60}")
                        print(f"⚡ USING RULE-BASED TEXT CONVERSION")
                        print(f"{'='*60}")
                        print(f"AI analysis unavailable")
                        print(f"Applying rule-based text-to-markdown formatting...")
                        print(f"{'='*60}\n")
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
    
    # Create converter and process (pass None if using config-based path)
    ref_path_str = str(reference_path) if args.reference else None
    converter = AIDocumentConverter(ref_path_str, config_path=args.config)
    success = converter.convert_with_ai(input_file, output_file)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()