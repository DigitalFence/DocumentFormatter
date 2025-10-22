# Word Formatter by Claude

An intelligent document formatter that converts text, markdown, and Word documents to match a reference Word document's styling. Features AI-powered text analysis for improved semantic detection and formatting.

## Features

- **Multiple Input Formats**: Supports `.txt`, `.rtf`, `.md`, `.markdown`, `.docx`, and `.doc` files
- **RTF File Support**: Native RTF processing with intelligent text extraction
- **Smart Style Matching**: Automatically extracts and applies formatting from a reference Word document
- **AI-Enhanced Text Processing**: Uses Claude AI to intelligently structure plain text and RTF files
- **Adaptive Document Type Detection**: Automatically distinguishes between complete books (with title, TOC, chapters) and single chapters, applying appropriate heading levels
- **Professional Typography**: Comprehensive Aptos Light font styling with configurable sizes
- **Style Override System**: Direct control over fonts, sizes, and spacing for all styles
- **Finder Integration**: Right-click any document in macOS Finder to format instantly
- **System Notifications**: Real-time notifications for processing stages and completion
- **Preserves Content**: Maintains all original content while upgrading formatting
- **External Configuration**: JSON-based configuration for custom formatting rules
- **Intelligent Page Breaks**: Separate pages for Title, Dedication, and Table of Contents
- **macOS Alias Support**: Works with alias files for reference documents
- **Flexible Heading Styles**: Template-based or custom heading formatting with Aptos Light
- **Advanced Document Structure**: Support for sections, chapters, and multi-level headings
- **Full Word Document Support**: Process existing Word documents with style preservation
- **Multilingual Support**: Automatic italic formatting for non-English text and quotes

## Installation

### Prerequisites

- macOS (tested on macOS 13+)
- Python 3.8 or higher
- Claude CLI (for AI features)

### Quick Install

1. Clone or download this repository:
```bash
cd /Users/KDP/scripts/wordformatterbyclaude
```

2. Set up the Python environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Install Finder Quick Action:
```bash
./install_quick_action.sh
```

4. Set up your reference document:
   - Place your reference Word document in the project directory
   - Rename it to `referenceformat.docx`

## Usage

### Method 1: Finder Quick Action (Recommended)

1. Right-click any supported document in Finder
2. Select **Quick Actions** → **Format with Reference Style**
3. The formatted document will be created with `_formatted` suffix

### Method 2: Command Line

```bash
# Basic usage
python document_converter.py --input document.txt --reference template.docx

# With custom output
python document_converter.py --input document.md --reference template.docx --output formatted.docx

# With configuration file
python document_converter.py --input document.md --reference template.docx --config formatter_config.json

# Using the shell wrapper
./format_document.sh /path/to/document.txt
```

### Method 3: AI-Enhanced Mode (for text files)

```bash
# Automatically uses Claude for intelligent text structuring
python document_converter_ai.py input.txt
```

## Input File Requirements

### Important: Clean Source Files

For best results, ensure your input files are clean and free of markdown-like special characters:

**⚠️ Common Issues:**

1. **Avoid pre-existing markdown characters in RTF/text files:**
   - Don't use `#` symbols around headings
   - Don't use `*` symbols around text for emphasis
   - Don't use `-`, `*`, or `•` at the start of regular paragraphs

2. **Example of problematic RTF content:**
   ```
   # Talk 13: Love That Dares    ← Remove # symbols

   *यथा व्रजगोपिकानाम्*          ← Remove * symbols
   *Yathâ Vrajagopikânâm*         ← Remove * symbols
   ```

3. **Why this matters:**
   - The formatter may misinterpret these characters as markdown
   - Leads to malformed output like `**text* *` instead of proper blockquotes
   - AI processing gets confused by mixed formatting

**✅ Clean Input Guidelines:**
- Use plain text without markdown characters
- Let the AI detect and add proper markdown structure
- Keep source files in their natural format
- Remove any manual markdown formatting

**Note:** If you're manually preparing RTF files, keep them as plain text. The formatter's AI will intelligently add the appropriate structure and formatting.

## Configuration

### Reference Document Setup

The reference document (`referenceformat.docx`) should contain:
- Desired fonts and sizes
- Heading styles (Heading 1, 2, 3, etc.)
- Paragraph spacing and indentation
- Page margins and layout
- List styles

The formatter will extract and apply these styles to your documents.

### Supported Locations for Reference File

1. Project directory: `/Users/KDP/scripts/wordformatterbyclaude/referenceformat.docx`
2. Documents folder: `~/Documents/referenceformat.docx`
3. Desktop: `~/Desktop/referenceformat.docx`

### Formatter Configuration (New!)

The formatter now supports an external JSON configuration file for customizing formatting behavior. By default, the formatter uses styles from your reference document (template), but you can override specific styles using the configuration file.

#### Configuration File Format

Create a `formatter_config.json` file:

```json
{
  "style_overrides": {
    "Normal": {
      "font_name": "Aptos Light",
      "font_size": 12.0,
      "line_spacing": 1.4
    },
    "Title": {
      "font_name": "Aptos Light",
      "font_size": 48.0
    },
    "Subtitle": {
      "font_name": "Aptos Light",
      "font_size": 36.0
    }
  },
  "heading_overrides": {
    "heading_1": {
      "font_name": "Aptos Light",
      "font_size": 16.0,
      "alignment": "center"
    },
    "heading_2": {
      "font_name": "Aptos Light",
      "font_size": 15.0,
      "alignment": "center"
    },
    "heading_3": {
      "font_name": "Aptos Light",
      "font_size": 13.5,
      "alignment": "center"
    }
  },
  "heading_detection": {
    "section_keywords": ["section", "part"],
    "chapter_keywords": ["chapter"],
    "always_use_heading_1_for_chapters": true
  },
  "page_breaks": {
    "before_sections": false,
    "before_chapters": true,
    "after_title": true,
    "after_dedication": true,
    "after_contents": true
  },
  "blockquote_formatting": {
    "remove_em_dashes": true,
    "single_line_spacing": true,
    "center_align": true,
    "italic": true
  }
}
```

#### Configuration Options

**Style Overrides (New!):**
- `Normal`: Configure body text font, size, and line spacing
- `Title`: Set title font and size
- `Subtitle`: Configure subtitle font and size
- Properties: `font_name`, `font_size`, `line_spacing`
- Always applied when configuration exists

**Heading Overrides:**
- Set any property to `null` to use template defaults
- Available properties: `font_name`, `font_size`, `alignment` (left/center/right/justify), `italic`, `bold`
- Supports heading_1 through heading_6
- Recommended: Use Aptos Light for consistent typography

**Heading Detection:**
- `section_keywords`: Words that identify section headings
- `chapter_keywords`: Words that identify chapter headings (use Heading 1)
- `always_use_heading_1_for_chapters`: Ensures chapters always use Heading 1

**Page Breaks:**
- `before_sections`: Insert page break before section headings
- `before_chapters`: Insert page break before chapter headings
- `after_title`: Page break after title (separate title page)
- `after_dedication`: Page break after dedication
- `after_contents`: Page break after table of contents

**Blockquote Formatting:**
- `remove_em_dashes`: Remove em dashes (—) from citations
- `single_line_spacing`: Use single line breaks in blockquotes
- `center_align`: Center-align blockquote content
- `italic`: Format all blockquotes in italics (recommended for quotes)

#### Document Structure

The formatter now supports a hierarchical document structure:
- **Title**: Book title (when detected as a multi-chapter book)
- **Heading 1**: Chapters (e.g., "Chapter 1: Getting Started", "Table of Contents")
- **Heading 2**: Sections (e.g., "Introduction", "Key Concepts")
- **Heading 3**: Subsections (customizable via config)
- **Heading 4-6**: Additional levels (customizable via config)

### AI Enhancement Configuration

The AI converter supports several environment variables for customization:

- `CLAUDE_MODEL` - Choose AI model: `haiku`, `sonnet`, or `opus` (default: `sonnet`)
- `SAVE_MARKDOWN` - Save intermediate markdown file: `0` or `1` (default: `1`)
- `SHOW_PROGRESS` - Show conversion progress: `0` or `1` (default: `1`)
- `CLAUDE_TIMEOUT` - Timeout in seconds (default: `600`)
- `WORD_FORMATTER_DEBUG` - Verbose debug output: `0` or `1` (default: `0`)
- `ERROR_LOG` - Path to error log file (optional)
- `ENABLE_NOTIFICATIONS` - Enable system notifications: `0` or `1` (default: `1`)
- `NOTIFICATION_TYPE` - Notification style: `notification`, `dialog`, or `none` (default: `notification`)
- `FORMATTER_CONFIG_PATH` - Path to formatter configuration file (default: `formatter_config.json`)

Example usage:
```bash
# Use Haiku model with debug output
CLAUDE_MODEL=haiku WORD_FORMATTER_DEBUG=1 python document_converter_ai.py input.txt

# Disable progress display and markdown saving
SHOW_PROGRESS=0 SAVE_MARKDOWN=0 ./format_document.sh input.txt

# Use dialog notifications (always visible)
NOTIFICATION_TYPE=dialog ./format_document.sh input.txt

# Disable all notifications
ENABLE_NOTIFICATIONS=0 ./format_document.sh input.txt

# Log errors to a file
ERROR_LOG=/tmp/errors.log ./format_document.sh input.txt

# Use custom configuration file
FORMATTER_CONFIG_PATH=/path/to/custom_config.json ./format_document.sh input.txt
```

### System Notifications

The Word Formatter provides real-time notifications during conversion:

- **Start notification**: When AI analysis begins
- **Progress notifications**: When markdown is created and Word formatting is applied
- **Completion notification**: When conversion is finished (with success/error status)

**Notification Requirements:**
- Requires `terminal-notifier` (installed automatically via Homebrew)
- Can be configured via environment variables
- Falls back to modal dialogs if notifications are blocked

**If notifications don't appear:**
1. Check **System Settings** → **Notifications** for **terminal-notifier** entry
2. Ensure notifications are enabled for the application
3. Use `NOTIFICATION_TYPE=dialog` for always-visible modal dialogs

## Features in Detail

### Style Extraction
- Font properties (name, size, color, bold, italic)
- Paragraph formatting (alignment, spacing, indentation)
- Page setup (margins, orientation)
- Heading hierarchy
- List formatting

### Markdown Support
- Headers (H1-H6)
- Bold and italic text
- Lists (ordered and unordered)
- Code blocks
- Tables
- Links

### AI Text Analysis
When processing plain text files, the AI enhancement:
- **Adaptive Document Type Detection**: Automatically distinguishes between complete books (with title, TOC, chapters) and single chapters, applying appropriate heading levels
- Detects heading structures (sections, chapters, sub-sections)
- Identifies lists and bullet points
- Recognizes quotes and citations (with special handling for Sanskrit, multilingual content)
- Automatically italicizes transliterated and non-English text (including diacritics like â, î, û)
- Preserves intentional formatting
- Adds semantic structure
- Handles Unicode characters and diacritical marks
- Formats blockquotes without extra spacing
- Removes em dashes from citations (configurable)
- **Consistent Chapter Formatting**: Chapters use Heading 1 style whether in a book or standalone

**Document Structure Recognition:**
- **Books**: Detected when document has 3+ H1 headings or TOC + 2+ H1 headings
  - First H1 → Title style (largest font)
  - TOC → Heading 1
  - Chapters → Heading 1
  - Sections → Heading 2
  - Subsections → Heading 3
- **Single Chapters**: Detected when document has only 1 H1 heading without TOC
  - Chapter → Heading 1 (same as chapters in books)
  - Sections → Heading 2 (same as in books)
  - Subsections → Heading 3 (same as in books)

## Troubleshooting

### Common Issues

#### Malformed Markdown Output (Sutra/Quote Formatting Issues)

**Problem:** AI-generated markdown shows malformed text like:
```markdown
**यथा व्रजगोपिकानाम्* *
*Yathâ Vrajagopikânâm*
The Gopis of Vraja, for instance.
```

Instead of properly formatted blockquotes:
```markdown
> *यथा व्रजगोपिकानाम्*
> *Yathâ Vrajagopikânâm*
> The Gopis of Vraja, for instance.
```

**Cause:** The input RTF/text file contains pre-existing markdown-like special characters (`#`, `*`, `-`, etc.) that confuse the formatter.

**Solution:**
1. Open your RTF file in a text editor
2. Remove any `#` symbols around headings
3. Remove any `*` symbols around text (unless they're part of the actual content)
4. Remove markdown-like list markers (`-`, `*`, `•`) at the start of regular paragraphs
5. Keep the source file as plain text and let the AI add proper structure

**Prevention:** Always prepare source files without markdown formatting. The AI will intelligently detect and add the appropriate structure.

#### Chapter/Heading Level Issues

**Problem:** First heading becomes Title style when it should be Heading 1 (chapter style).

**Cause:** The formatter detected only one H1 heading without a TOC, but still treated it as a book title.

**Solution:** The formatter now automatically detects document type:
- **Books** (with title, TOC, multiple chapters): First H1 → Title style
- **Single chapters** (one chapter/talk): First H1 → Heading 1 style

If detection is incorrect, check your document structure or manually adjust in Word after conversion.

### Quick Action Not Appearing

1. Check if installed:
```bash
ls -la ~/Library/Services/ | grep "Format"
```

2. Refresh services:
```bash
/System/Library/CoreServices/pbs -update
```

3. Enable in System Settings:
   - Go to **System Settings** → **Privacy & Security** → **Extensions** → **Finder**
   - Enable "Format with Reference Style"

### AI Enhancement Not Working

If the Finder integration falls back to simple conversion instead of using AI:

1. **Check the log file** for detailed information:
```bash
tail -50 /tmp/word_formatter.log
```

2. **Verify Claude CLI is installed**:
```bash
which claude
claude --version
```

3. **Test manually** to isolate the issue:
```bash
cd /Users/KDP/scripts/wordformatterbyclaude
source venv/bin/activate
python document_converter_ai.py test_samples/input2_sample.txt
```

4. **Common issues and solutions**:
   - **Claude CLI not found**: Install Claude CLI or ensure it's in PATH
   - **Node.js not found**: Install Node.js (required for Claude CLI)
   - **Permission issues**: Make sure scripts have execute permissions
   - **Virtual environment issues**: Recreate the virtual environment

### Testing AI Enhancement

To verify AI enhancement is working correctly:

1. **Basic functionality test**:
```bash
./format_document.sh test_samples/input2_sample.txt
# Should create: input2_sample_formatted.docx and input2_sample_markdown.md
```

2. **Different models test**:
```bash
CLAUDE_MODEL=haiku ./format_document.sh test_samples/input3_sample.txt
CLAUDE_MODEL=opus ./format_document.sh test_samples/input4_sample.txt
```

3. **Configuration options test**:
```bash
# Test with progress disabled
SHOW_PROGRESS=0 ./format_document.sh test_samples/input2_sample.txt

# Test with markdown saving disabled
SAVE_MARKDOWN=0 ./format_document.sh test_samples/input3_sample.txt

# Test with custom timeout
CLAUDE_TIMEOUT=60 ./format_document.sh test_samples/input4_sample.txt
```

4. **Error handling test**:
```bash
# Test with invalid model (should fallback to simple conversion)
CLAUDE_MODEL=invalid ./format_document.sh test_samples/input2_sample.txt

# Test with nonexistent file (should show error)
./format_document.sh nonexistent_file.txt
```

### Python Dependencies Issues

```bash
# Reinstall dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Permission Errors

```bash
# Make scripts executable
chmod +x format_document.sh
chmod +x install_quick_action.sh
```

### Logging and Debugging

All Finder Quick Action executions are logged to `/tmp/word_formatter.log`. This log includes:
- Script execution details
- PATH information
- Claude CLI detection results
- Error messages and fallback reasons
- Conversion success/failure status

To monitor in real-time:
```bash
tail -f /tmp/word_formatter.log
```

To clear old logs:
```bash
rm /tmp/word_formatter.log
```

## Advanced Usage

### Batch Processing

```bash
# Format all markdown files in a directory
for file in *.md; do
    ./format_document.sh "$file"
done
```

### Custom Reference Documents

You can use different reference documents by specifying them explicitly:

```bash
python document_converter.py --input doc.txt --reference /path/to/custom_template.docx
```

### Word Document Processing

The formatter now fully supports Word documents as input, applying your reference template styling while preserving content structure:

```bash
# Process a Word document with reference styling
python document_converter.py --input existing.docx --reference template.docx --output reformatted.docx

# Apply configuration to Word documents
python document_converter.py --input report.docx --reference template.docx --config formatter_config.json

# Batch process Word documents
for file in *.docx; do
    python document_converter.py --input "$file" --reference template.docx --output "${file%.docx}_reformatted.docx"
done
```

**Word Document Features:**
- Intelligent heading detection and level adjustment
- Section/Chapter recognition based on configuration
- List style preservation (bullets and numbering)
- Table structure and content preservation  
- Font and paragraph formatting from reference
- Blockquote detection (centered, indented paragraphs)
- Configuration-based style overrides

### Configuration Examples

```bash
# Use template defaults for all headings
python document_converter.py --input doc.md --reference template.docx --config formatter_config_template_defaults.json

# Apply custom heading styles
python document_converter.py --input doc.md --reference template.docx --config formatter_config_custom.json

# Create your own configuration
cp formatter_config.json my_config.json
# Edit my_config.json with your preferences
python document_converter.py --input doc.md --reference template.docx --config my_config.json
```

## Recent Changes (2025-10-22)

### Latest Features - Adaptive Document Detection

1. **Adaptive Document Type Detection**
   - Intelligent detection of book vs single chapter documents
   - Books: Detected by presence of TOC and multiple H1 headings
   - Single chapters: Detected when only one H1 heading exists without TOC
   - Automatic heading level adjustment based on document type
   - Consistent chapter formatting regardless of document type

2. **Enhanced Markdown Processing**
   - Improved handling of pre-existing markdown characters in input files
   - Better bullet point detection (avoids treating dialogue as lists)
   - Smarter heading detection (excludes sentences ending with punctuation)
   - Fixed chunking issues for multi-chunk AI processing
   - Prevention of markdown duplication in output

3. **Consistent Chapter Heading Levels**
   - Chapters always use Heading 1 in Word (whether in book or standalone)
   - Books: Title style → Heading 1 (chapters) → Heading 2 (sections) → Heading 3 (subsections)
   - Single chapters: Heading 1 (chapter) → Heading 2 (sections) → Heading 3 (subsections)
   - No forced title or TOC for single-chapter documents

4. **Improved Sutra and Special Text Formatting**
   - Enhanced detection of Sanskrit transliterations (including circumflex â, î, û)
   - Better blockquote formatting for opening sutras
   - Improved non-English text italicization
   - Support for Devanagari and transliterated text

5. **Debug and Logging Enhancements**
   - Added comprehensive debug output for troubleshooting
   - Improved error messages for file permission issues
   - Better logging of document structure detection
   - Enhanced fallback mechanisms when AI processing fails

6. **Documentation Improvements**
   - Added "Input File Requirements" section with best practices
   - Documented common issues and solutions
   - Clear examples of clean vs problematic input
   - Updated troubleshooting guide with real-world scenarios

### Previous Changes (2025-10-21)

### Features

1. **Comprehensive Aptos Light Font Styling**
   - All text styles now support Aptos Light font family
   - Configurable font sizes for all heading levels
   - Professional typography with consistent font usage across document
   - List paragraph styles inherit font configuration
   - Style overrides system for precise control

2. **Enhanced RTF File Support**
   - Native RTF file format processing
   - Automatic text extraction and structure detection
   - Claude AI integration for intelligent RTF conversion
   - Preserves document content while applying modern formatting

3. **Advanced Style Override System**
   - New `style_overrides` configuration section
   - Direct control over Normal, Title, and Subtitle styles
   - Font name, size, and line spacing configuration
   - Heading font overrides for all levels (H1-H6)
   - Always applies when configuration exists (no environment variable needed)

4. **Professional Typography Settings**
   - **Title**: 48pt Aptos Light
   - **Subtitle**: 36pt Aptos Light
   - **Heading 1 (Chapters)**: 16pt Aptos Light, centered
   - **Heading 2 (Sections)**: 14pt Aptos Light, centered
   - **Heading 3 (Subsections)**: 13.5pt Aptos Light, italic
   - **Body Text**: 12pt Aptos Light with 1.4 line spacing

5. **Improved Page Break Management**
   - Separate pages for Title, Dedication, and Table of Contents
   - Page break after TOC now configurable (enabled by default)
   - Professional document structure with proper page separation
   - Configurable page breaks for all special sections

6. **Enhanced Quote and Multilingual Formatting**
   - Automatic italic formatting for quotes and blockquotes
   - Non-English text (Sanskrit, transliterations) italicized automatically
   - Configurable em-dash removal from citations
   - Centered alignment for quotes with proper spacing

7. **Claude AI Enhancements**
   - Support for Claude Code CLI path (~/.claude/local/claude)
   - Automatic code fence removal from AI output
   - Improved incomplete response detection
   - Better error handling with fallback mechanisms
   - Multi-chunk processing for large documents

### Previous Changes (2025-09-03)

1. **External Configuration System**
   - JSON-based configuration files for formatting rules
   - Template styles used by default, with selective overrides
   - Configurable heading detection and formatting
   - Page break control for sections and chapters

2. **Enhanced Document Structure**
   - Chapters use Heading 1 style (configurable)
   - Sections use Heading 2 style
   - Subsections and additional levels with customizable formatting
   - Automatic heading level adjustment based on document type

3. **macOS Alias Support**
   - Reference documents can now be macOS aliases
   - Automatic alias resolution for all file inputs
   - Transparent handling of both aliases and regular files

4. **Improved Blockquote Formatting**
   - Removed extra blank lines between transliteration and translation
   - Em dashes removed from citations (configurable)
   - Single-line spacing within blockquotes
   - Configurable alignment options

5. **AI Enhancement Updates**
   - Better detection of sections vs chapters
   - Improved handling of multilingual content
   - Increased timeout to 600 seconds for large documents
   - Enhanced error handling and fallback mechanisms

6. **Enhanced Word Document Processing**
   - Full support for processing existing Word documents
   - Intelligent heading detection and remapping
   - Preservation of lists, tables, and formatting
   - Configuration-based style application
   - Blockquote detection and formatting

### Configuration Migration

If you're upgrading from a previous version:
1. Your existing setup will continue to work without changes
2. To use new features, create a `formatter_config.json` file
3. Start with the provided template and customize as needed
4. Use `--config` parameter to specify custom configurations

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is provided as-is for personal and educational use.

## Acknowledgments

- Built with Claude AI assistance
- Uses python-docx for Word document manipulation
- Markdown processing powered by Python-Markdown

---

For more technical details and AI enhancement information, see [CLAUDE.md](CLAUDE.md).