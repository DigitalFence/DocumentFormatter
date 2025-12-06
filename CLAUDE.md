# Claude AI Enhancement Documentation

This document details the AI-powered enhancements to the Word Formatter, including implementation details, prompts, and technical considerations.

## Overview

The AI enhancement uses Claude in headless mode to intelligently analyze and structure plain text files before applying Word formatting. This dramatically improves the quality of text file conversion by adding semantic understanding.

**Key Feature: Adaptive Document Type Detection**
The system automatically detects whether a document is:
- A **complete book** (with title, TOC, and multiple chapters)
- A **single chapter** (just one chapter/talk without TOC)

**Critical principle:** Chapters use IDENTICAL formatting whether in a book or standalone.

**Book structure (Markdown → Word):**
- `# Book Title` → Title style (largest font)
- `# Table of Contents` → Heading 1
- `# Chapter 1: Name` → Heading 1
- `## Section` → Heading 2
- `### Subsection` → Heading 3

**Single chapter structure (Markdown → Word):**
- `# Talk 13: Love That Dares` → Heading 1 (same as chapters in books)
- `## Section` → Heading 2 (same as in books)
- `### Subsection` → Heading 3 (same as in books)

**Key principle:** Chapters use **Heading 1** in Word (whether in a book or standalone). The only difference is books have a Title before chapters.

## Architecture

```
Input Text File → Claude AI Analysis → Markdown Generation → Word Formatter → Styled Output
```

## Implementation Plan

### Phase 1: Basic AI Integration

1. **Create `document_converter_ai.py`**
   - Wrapper around the existing converter
   - Claude CLI integration
   - Error handling and fallback mechanisms

2. **Claude Prompt Engineering**
   - Develop prompts for text analysis
   - Test with various text formats
   - Optimize for accuracy and consistency

3. **Integration with Existing System**
   - Update shell scripts
   - Maintain backward compatibility
   - Add progress indicators

### Phase 2: Advanced Features

1. **Smart Detection**
   - Automatic heading level detection
   - List type identification
   - Quote and citation formatting
   - Table structure recognition

2. **Customization Options**
   - User-defined prompt templates
   - Style preferences
   - Output format options

## Claude CLI Integration

### Basic Usage

```python
import subprocess
import json

def analyze_text_with_claude(text_content):
    prompt = f"""
    Convert the following plain text to well-structured markdown.
    Detect headings, lists, quotes, and other structural elements.
    Preserve all original content while adding appropriate markdown formatting.
    
    Text:
    {text_content}
    """
    
    result = subprocess.run(
        ['claude', '--print', prompt],
        capture_output=True,
        text=True
    )
    
    return result.stdout
```

### Error Handling

```python
def safe_claude_convert(text_content):
    try:
        return analyze_text_with_claude(text_content)
    except subprocess.CalledProcessError:
        # Fallback to simple conversion
        return simple_text_to_markdown(text_content)
    except FileNotFoundError:
        print("Claude CLI not found. Using simple conversion.")
        return simple_text_to_markdown(text_content)
```

## Prompt Templates

### Main Text Analysis Prompt

```
You are a document formatting assistant. Convert the provided plain text into well-structured markdown format.

STEP 1: DETECT DOCUMENT TYPE
First, analyze the document structure to determine its type:
- BOOK/MULTI-CHAPTER: Has title, TOC, multiple chapters, or clear chapter divisions
- SIMPLE ARTICLE/ESSAY: Single cohesive piece without chapter structure or TOC

STEP 2: APPLY APPROPRIATE FORMATTING
Instructions:
1. Identify and mark headings based on context and document type
2. For BOOKS: Use # (H1) for title/TOC/chapters, ## (H2) for sections, ### (H3) for subsections
3. For ARTICLES: Use # (H1) for main sections, ## (H2) for subsections, ### (H3) for sub-subsections
4. Detect lists (both bulleted and numbered) and format appropriately
5. Recognize quotes, citations, and special blocks
6. Preserve all original text content exactly
7. Add markdown formatting only where it enhances structure
8. Format code blocks if you detect code snippets
9. Identify tables and convert to markdown table format

Important:
- Do not add any content that wasn't in the original
- Maintain the original tone and style
- Focus on structure, not rewriting
- Match formatting style to actual document structure

Return only the markdown formatted text, no explanations.
```

### Specialized Prompts

#### Academic Text
```
Focus on:
- Chapter and section headings
- Citations and references
- Footnotes
- Academic formatting conventions
```

#### Business Documents
```
Focus on:
- Executive summary detection
- Bullet points and action items
- Tables and figures
- Professional formatting
```

#### Technical Documentation
```
Focus on:
- Code blocks and examples
- Command line instructions
- API documentation patterns
- Technical specifications
```

## Implementation Details

### Recent Improvements (2025-12-06)

#### 1. Smart Chunking for Large Documents
Large documents are now processed in manageable chunks to avoid Claude CLI timeouts and improve reliability.

**Chunking Strategy:**
- Default chunk size: ~10KB (`CHUNK_THRESHOLD` environment variable)
- First attempts to split on paragraph boundaries (`\n\n`)
- If a "paragraph" exceeds chunk size (common in RTF files with single newlines), splits further on single newlines (`\n`)
- Each chunk is processed independently with full retry strategy
- Results are reassembled maintaining document order

**Why This Matters:**
- RTF files often use single newlines instead of double newlines between paragraphs
- A 160KB document that appears as "3 paragraphs" (with one 150KB block) would timeout
- Smart chunking converts this to 18 manageable ~10KB chunks

**Progress Logging:**
```
📦 Processing 18 chunks...
   Chunk 1: 4,987 characters
   Chunk 2: 9,950 characters
   ...
   Chunk 18: 4,772 characters
```

#### 2. Script-Based Styling for Non-English Text
Automatic detection and styling of different scripts:

- **Devanagari** (Sanskrit, Hindi - Unicode U+0900-U+097F): `Intense Quote Char` style
- **Transliteration** (Latin with diacritics like ā, ī, ū, ṛ, ś): `Quote Char` style
- **Plain text**: No special styling

**Important:** Uses Word **character styles** (not paragraph styles) for run-level formatting.

#### 3. Real-Time Progress Logging
All progress messages now use `flush=True` for immediate output visibility in logs:
```python
print(f"🤖 Using Claude {model} model...", flush=True)
print(f"   ⏳ Waiting for Claude response (timeout: {self.timeout}s)...", flush=True)
print(f"   ✓ Claude response received ({len(result)} chars)", flush=True)
```

#### 4. Bug Fixes
- **Character Style Error**: Fixed "assigned style is type PARAGRAPH (1), need type CHARACTER (2)" by using `Quote Char` instead of `Quote`
- **SyntaxWarning**: Fixed Python 3.13+ invalid escape sequence `\.` by using raw f-string (`rf"""`)
- **Chunk Size**: Fixed issue where RTF files with single newlines created massive 150KB "paragraphs"

#### 5. Setup and Configuration Improvements (2025-12-06 - Second Update)

**Virtual Environment Setup:**
- Fixed shell script to use explicit venv Python path instead of relying on PATH activation
- Changed from `python` to `"$SCRIPT_DIR/venv/bin/python"` for reliability
- Ensures correct Python interpreter and dependencies are always used

**Reference Template Resolution:**
- Fixed `document_converter_ai.py` to use config system for template resolution
- Removed hardcoded search paths (References/, Documents/, Desktop/)
- Now properly uses `~/WordFormatReference/ReferenceFormat.dotx` via config_loader
- Template resolution order:
  1. Explicit `--reference` argument
  2. Config system (`FormatterConfig.get_reference_template_path()`)
  3. External reference folder (`~/WordFormatReference/`)

**Progress Visibility Enhancement:**
- Added `export SHOW_PROGRESS=1` to `format_document.sh` (lines 152, 185)
- Enables real-time progress output for all conversions
- Shows chunk-by-chunk progress for large documents
- Critical for understanding conversion status (avoids apparent "hangs")

**Debug Instrumentation:**
- Added detailed timing logs to track conversion bottlenecks
- Shows prompt creation time (typically 0.00s)
- Shows subprocess execution time (~20-50s per chunk for Claude API calls)
- Helps diagnose performance issues and apparent hangs

**Key Insight - Apparent "Hang" Issue Resolved:**
- **Problem**: Conversions appeared to hang for 15+ minutes with no output
- **Root Cause**: `SHOW_PROGRESS` not set, so no output during Claude API calls
- **Reality**: Claude CLI takes ~50 seconds per chunk (normal API processing time)
- **Solution**: Progress display now shows real-time status during processing
- **Example**: 160KB document = 18 chunks × 50s = ~15 minutes (with visible progress)

**Debug Logging Added:**
```python
print(f"[DEBUG] Text content size: {len(text_content):,} chars", flush=True)
print(f"[DEBUG] Starting prompt creation...", flush=True)
print(f"[DEBUG] Prompt creation completed in {creation_time:.2f}s", flush=True)
print(f"[DEBUG] About to call Claude...", flush=True)
print(f"[DEBUG] subprocess.run completed in {subprocess_time:.2f}s", flush=True)
```

### Previous Improvements (2025-08-26)

#### 1. Enhanced Configuration System
- **Environment Variables**: Added comprehensive configuration via environment variables
- **Always Save Markdown**: Now saves intermediate `.md` files by default (configurable)
- **Progress Feedback**: User-friendly progress indicators with emoji feedback
- **Error Handling**: Improved error messages and fallback mechanisms
- **Logging**: Comprehensive logging to `/tmp/word_formatter.log` for debugging

#### 2. Fixed Finder Integration Issues
- **Problem**: Finder Quick Actions were using simple converter instead of AI
- **Root Cause**: Restricted PATH in Finder context didn't include Claude CLI and Node.js
- **Solution**: 
  - Added PATH expansion to include common binary directories
  - Enhanced Claude CLI detection with multiple search locations
  - Added detailed logging to track execution flow

#### 3. Multi-Model Support
- **Haiku**: Fast, efficient for simple documents
- **Sonnet**: Balanced performance and quality (default)
- **Opus**: Highest quality for complex documents

### document_converter_ai.py Structure

```python
#!/usr/bin/env python3
"""AI-Enhanced Document Converter using Claude"""

import sys
import os
import tempfile
from pathlib import Path
from document_converter import DocumentConverter

class AIDocumentConverter:
    def __init__(self, reference_path: str):
        self.reference_path = reference_path
        self.converter = DocumentConverter(reference_path)
        # Configuration from environment variables
        self.debug = os.environ.get('WORD_FORMATTER_DEBUG', '0') == '1'
        self.save_markdown = os.environ.get('SAVE_MARKDOWN', '1') == '1'
        self.show_progress = os.environ.get('SHOW_PROGRESS', '1') == '1'
        self.model = os.environ.get('CLAUDE_MODEL', 'sonnet')
        self.timeout = int(os.environ.get('CLAUDE_TIMEOUT', '120'))
    
    def convert_with_ai(self, input_path: str, output_path: str):
        # Read input file
        # Analyze with Claude (with configurable model/timeout)
        # Convert to markdown
        # Save intermediate markdown (if enabled)
        # Process with standard converter
        # Save output with progress feedback
```

### Shell Script Integration

Update `format_document.sh` to route text files through AI converter:

```bash
if [[ "$ext_lower" == "txt" ]]; then
    # Use AI-enhanced conversion for text files
    python "$SCRIPT_DIR/document_converter_ai.py" "$file"
else
    # Use standard conversion for other formats
    python "$SCRIPT_DIR/document_converter_simple.py" "$file"
fi
```

## Performance Considerations

1. **Caching**
   - Cache Claude responses for identical inputs
   - Store processed templates

2. **Batch Processing**
   - Group multiple files for efficiency
   - Parallel processing where possible

3. **Rate Limiting**
   - Implement backoff strategies
   - Queue management for large batches

## Testing Strategy

### Comprehensive Test Suite

#### 1. Basic Functionality Tests

**Test 1: Default AI Conversion**
```bash
./format_document.sh test_samples/input2_sample.txt
```
Expected results:
- ✅ Creates `input2_sample_formatted.docx`
- ✅ Creates `input2_sample_markdown.md`
- ✅ Shows progress with emojis
- ✅ Uses SONNET model by default
- ✅ Logs execution to `/tmp/word_formatter.log`

**Test 2: Direct Python Converter**
```bash
source venv/bin/activate
python document_converter_ai.py test_samples/input3_sample.txt
```
Expected results:
- ✅ AI analysis completes successfully
- ✅ Proper markdown structure detection
- ✅ Word document with correct formatting applied

#### 2. Model Selection Tests

**Test 3: Haiku Model**
```bash
CLAUDE_MODEL=haiku ./format_document.sh test_samples/input2_sample.txt
```
Expected results:
- ✅ Uses Claude HAIKU model
- ✅ Faster processing time
- ✅ Good quality formatting
- ✅ Logs show "Using Claude HAIKU model"

**Test 4: Opus Model**
```bash
CLAUDE_MODEL=opus ./format_document.sh test_samples/input3_sample.txt
```
Expected results:
- ✅ Uses Claude OPUS model
- ✅ Highest quality analysis
- ✅ Complex document structure preserved
- ✅ Longer processing time acceptable

**Test 5: Invalid Model Fallback**
```bash
CLAUDE_MODEL=invalid_model ./format_document.sh test_samples/input2_sample.txt
```
Expected results:
- ⚠️  Shows "Claude returned an error"
- ✅ Falls back to simple text conversion
- ✅ Still creates markdown file (simple format)
- ✅ Still creates Word document
- ✅ Logs show fallback reason

#### 3. Configuration Tests

**Test 6: Disable Progress Display**
```bash
SHOW_PROGRESS=0 ./format_document.sh test_samples/input2_sample.txt
```
Expected results:
- ✅ No emoji progress indicators
- ✅ Minimal console output
- ✅ Still creates expected files
- ✅ Basic progress messages only

**Test 7: Disable Markdown Saving**
```bash
SAVE_MARKDOWN=0 ./format_document.sh test_samples/input3_sample.txt
```
Expected results:
- ✅ No intermediate `.md` file created
- ✅ Word document still created correctly
- ✅ AI processing still occurs
- ✅ Logs show markdown saving disabled

**Test 8: Custom Timeout**
```bash
CLAUDE_TIMEOUT=60 ./format_document.sh test_samples/input4_sample.txt
```
Expected results:
- ✅ Uses 60-second timeout instead of default 120
- ✅ Normal processing if within timeout
- ✅ Logs show custom timeout value

**Test 9: Debug Mode**
```bash
WORD_FORMATTER_DEBUG=1 ./format_document.sh test_samples/input2_sample.txt
```
Expected results:
- ✅ Verbose debug output
- ✅ Shows Claude CLI calls
- ✅ Additional technical details
- ✅ Both progress and debug messages

#### 4. Error Handling Tests

**Test 10: Timeout Handling**
```bash
CLAUDE_TIMEOUT=1 ./format_document.sh test_samples/input3_sample.txt
```
Expected results:
- ⏱️  Claude analysis times out after 1 second
- ✅ Falls back to simple conversion
- ✅ Shows timeout message clearly
- ✅ Still produces usable output

**Test 11: Nonexistent File**
```bash
./format_document.sh nonexistent_file.txt
```
Expected results:
- ❌ Shows clear error message
- ✅ Logs error to `/tmp/word_formatter.log`
- ✅ Script exits gracefully
- ✅ No partial files created

**Test 12: Empty File**
```bash
touch test_samples/empty.txt
./format_document.sh test_samples/empty.txt
```
Expected results:
- ❌ Shows "Input file is empty" error
- ✅ No processing attempted
- ✅ Clear error message
- ✅ Script exits gracefully

**Test 13: Error Logging**
```bash
ERROR_LOG=/tmp/converter_errors.log CLAUDE_MODEL=invalid ./format_document.sh test_samples/input2_sample.txt
```
Expected results:
- ✅ Error logged to specified file
- ✅ Log includes timestamp, error, input file, and model
- ✅ Conversion continues with fallback
- ✅ Both console and file logging work

#### 5. Environment and Path Tests

**Test 14: Restricted PATH (Simulating Finder)**
```bash
PATH="/usr/bin:/bin:/usr/sbin:/sbin" ./format_document.sh test_samples/input2_sample.txt
```
Expected results:
- ✅ Claude CLI found in `/usr/local/bin/claude`
- ✅ PATH automatically expanded
- ✅ Node.js dependency resolved
- ✅ Full AI processing works
- ✅ Logs show PATH expansion

**Test 15: Finder Integration Test**
```bash
# Use Finder Quick Action on test_samples/input4_sample.txt
# Then check results
ls test_samples/input4_sample*
tail -20 /tmp/word_formatter.log
```
Expected results:
- ✅ Both `.docx` and `_markdown.md` files created
- ✅ AI analysis successful in logs
- ✅ No PATH-related errors
- ✅ Same quality as command-line execution

#### 6. Performance and Quality Tests

**Test 16: Large File Handling**
```bash
# Create or use a large text file (>50KB)
./format_document.sh test_samples/large_sample.txt
```
Expected results:
- ✅ Processes within reasonable time
- ✅ Doesn't timeout with default settings
- ✅ Maintains formatting quality
- ✅ Memory usage remains reasonable

**Test 17: Complex Document Structure**
```bash
# Use a file with multiple heading levels, lists, quotes, etc.
./format_document.sh test_samples/complex_structure.txt
```
Expected results:
- ✅ Proper heading hierarchy detected
- ✅ Lists formatted correctly
- ✅ Quotes and special formatting preserved
- ✅ Overall document structure logical

**Test 18: Special Characters and Unicode**
```bash
# Use a file with Unicode characters, accents, symbols
./format_document.sh test_samples/unicode_sample.txt
```
Expected results:
- ✅ Unicode characters preserved
- ✅ No encoding issues
- ✅ Special symbols handled correctly
- ✅ Formatting applied appropriately

#### 7. Integration Tests

**Test 19: End-to-End Workflow**
```bash
# Full workflow test
cp some_plain_text.txt test_samples/workflow_test.txt
./format_document.sh test_samples/workflow_test.txt
# Verify output in Word processor
```
Expected results:
- ✅ Professional-looking Word document
- ✅ Formatting matches reference document
- ✅ Content structure improved from plain text
- ✅ No manual editing needed

**Test 20: Batch Processing**
```bash
# Process multiple files
./format_document.sh test_samples/input2_sample.txt test_samples/input3_sample.txt test_samples/input4_sample.txt
```
Expected results:
- ✅ All files processed successfully
- ✅ Individual progress tracking
- ✅ No interference between files
- ✅ Consistent quality across all outputs

### Validation Criteria

For each test, verify:
- **Functionality**: Core features work as expected
- **Quality**: Output formatting is professional and readable
- **Performance**: Processing completes in reasonable time
- **Reliability**: Consistent results across multiple runs
- **Error Handling**: Graceful failure and clear error messages
- **Logging**: Comprehensive logs for debugging
- **User Experience**: Clear feedback and intuitive operation

### Automated Testing (Future)

Priority test cases for automation:
1. Basic functionality with all three models
2. Configuration option validation
3. Error handling and fallback scenarios
4. PATH and environment compatibility
5. File format validation and quality checks

## Future Enhancements

1. **Machine Learning Integration**
   - Train custom models on document types
   - Learn from user corrections

2. **Multi-Language Support**
   - Detect and handle different languages
   - Preserve language-specific formatting

3. **Template Learning**
   - Learn from reference documents
   - Build style profiles

## Configuration

### External Reference Folder (Simplified System)

The Word Formatter uses a simplified configuration system with an external reference folder:

**Primary Location:** `~/WordFormatReference/`

```
~/WordFormatReference/
├── ReferenceFormat.dotx              ← Template file (primary formatting source)
├── formatter_config_template.json    ← Config template (copy to enable)
├── Symbols.docx                      ← Chapter separator symbols
└── README.md                         ← Documentation
```

**Default Behavior (No Config):**
- The formatter uses **only the .dotx template** for all styling
- No configuration file is needed
- Simple, clean, maintainable

**Custom Configuration (When Needed):**
```bash
cd ~/WordFormatReference
cp formatter_config_template.json formatter_config.json
# Edit formatter_config.json with your custom settings
```

### Configuration Priority

1. `FORMATTER_CONFIG_PATH` environment variable (if set)
2. `~/WordFormatReference/formatter_config.json` (if exists)
3. Built-in defaults + .dotx template styles (no config needed)

### Config Template Structure

```json
{
  "external_reference_folder": "~/WordFormatReference",
  "reference_template": "ReferenceFormat.dotx",
  "style_overrides": {
    "Normal": { "font_name": "Aptos Light", "font_size": 12.0 },
    "Title": { "font_name": "Aptos Light", "font_size": 48.0 }
  },
  "heading_overrides": {
    "heading_1": { "font_name": "Aptos Light", "font_size": 16.0, "alignment": "center" }
  },
  "page_breaks": { "before_chapters": true, "after_title": true },
  "blockquote_formatting": { "center_align": true, "italic": true }
}
```

### AI Enhancement Environment Variables

- `CLAUDE_MODEL` - Choose AI model: `haiku`, `sonnet`, or `opus` (default: `sonnet`)
- `SAVE_MARKDOWN` - Save intermediate markdown file: `0` or `1` (default: `1`)
- `SHOW_PROGRESS` - Show conversion progress: `0` or `1` (default: `1`)
- `CLAUDE_TIMEOUT` - Timeout in seconds (default: `600`)
- `CHUNK_THRESHOLD` - Max chunk size in characters (default: `10000`)
- `WORD_FORMATTER_DEBUG` - Verbose debug output: `0` or `1` (default: `0`)
- `FORMATTER_CONFIG_PATH` - Override config file path (optional)

## Troubleshooting

### Common Issues

1. **Claude CLI not found**
   - Solution: Install Claude CLI or disable AI enhancement

2. **Timeout errors**
   - Solution: Increase timeout with `CLAUDE_TIMEOUT=900` or reduce chunk size with `CHUNK_THRESHOLD=5000`

3. **Large chunks causing timeouts**
   - Symptom: One chunk is 150KB while others are 10KB
   - Cause: RTF files often use single newlines instead of double newlines
   - Solution: Fixed in latest version - splits large paragraphs on single newlines

4. **"assigned style is type PARAGRAPH" error**
   - Cause: Trying to apply paragraph styles (Quote, Intense Quote) to runs
   - Solution: Use character styles (Quote Char, Intense Quote Char)

5. **SyntaxWarning in Python 3.13+**
   - Cause: Invalid escape sequences like `\.` in strings
   - Solution: Use raw strings (`r"..."` or `rf"..."` for f-strings)

6. **Formatting inconsistencies**
   - Solution: Adjust prompt templates

### Debug Mode

Enable debug output:
```bash
export WORD_FORMATTER_DEBUG=1
./format_document.sh input.txt
```

## Contributing

When contributing AI enhancements:
1. Test prompts thoroughly
2. Document any new prompt templates
3. Ensure fallback mechanisms work
4. Add appropriate error handling

---

This document will be updated as the AI enhancement features are implemented and refined.
- Never hard code the font in the python code.