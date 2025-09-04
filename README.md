# Word Formatter by Claude

An intelligent document formatter that converts text, markdown, and Word documents to match a reference Word document's styling. Features AI-powered text analysis for improved semantic detection and formatting.

## Features

- **Multiple Input Formats**: Supports `.txt`, `.rtf`, `.md`, `.markdown`, `.docx`, and `.doc` files
- **Smart Style Matching**: Automatically extracts and applies formatting from a reference Word document
- **AI-Enhanced Text Processing**: Uses Claude AI to intelligently structure plain text files
- **Finder Integration**: Right-click any document in macOS Finder to format instantly
- **System Notifications**: Real-time notifications for processing stages and completion
- **Preserves Content**: Maintains all original content while upgrading formatting
- **External Configuration**: JSON-based configuration for custom formatting rules
- **macOS Alias Support**: Works with alias files for reference documents
- **Flexible Heading Styles**: Template-based or custom heading formatting
- **Advanced Document Structure**: Support for sections, chapters, and multi-level headings
- **Full Word Document Support**: Process existing Word documents with style preservation

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
  "heading_overrides": {
    "heading_3": {
      "alignment": "center",
      "italic": false,
      "bold": null,
      "font_name": null,
      "font_size": null
    },
    "heading_4": {
      "alignment": "left", 
      "italic": true
    }
  },
  "heading_detection": {
    "section_keywords": ["section", "part"],
    "chapter_keywords": ["chapter"],
    "always_use_heading_2_for_chapters": true
  },
  "page_breaks": {
    "before_sections": false,
    "before_chapters": true
  },
  "blockquote_formatting": {
    "remove_em_dashes": true,
    "single_line_spacing": true,
    "center_align": true
  }
}
```

#### Configuration Options

**Heading Overrides:**
- Set any property to `null` to use template defaults
- Available properties: `alignment` (left/center/right/justify), `italic`, `bold`, `font_name`, `font_size`
- Supports heading_1 through heading_6

**Heading Detection:**
- `section_keywords`: Words that identify section headings (use Heading 1)
- `chapter_keywords`: Words that identify chapter headings (use Heading 2)
- `always_use_heading_2_for_chapters`: Ensures chapters always use Heading 2

**Page Breaks:**
- Control when page breaks are inserted before sections and chapters

**Blockquote Formatting:**
- `remove_em_dashes`: Remove em dashes (—) from citations
- `single_line_spacing`: Use single line breaks in blockquotes
- `center_align`: Center-align blockquote content

#### Document Structure

The formatter now supports a hierarchical document structure:
- **Heading 1**: Sections (e.g., "Section I: Introduction")
- **Heading 2**: Chapters (e.g., "Chapter 1: Getting Started")
- **Heading 3**: Sub-sections (customizable via config)
- **Heading 4**: Sub-sub-sections (customizable via config)
- **Heading 5-6**: Additional levels

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
- Detects heading structures (sections, chapters, sub-sections)
- Identifies lists and bullet points
- Recognizes quotes and citations (with special handling for Sanskrit, multilingual content)
- Automatically italicizes transliterated and non-English text
- Preserves intentional formatting
- Adds semantic structure
- Handles Unicode characters and diacritical marks
- Formats blockquotes without extra spacing
- Removes em dashes from citations (configurable)

## Troubleshooting

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

## Recent Changes (2025-09-03)

### New Features

1. **External Configuration System**
   - JSON-based configuration files for formatting rules
   - Template styles used by default, with selective overrides
   - Configurable heading detection and formatting
   - Page break control for sections and chapters

2. **Enhanced Document Structure**
   - Sections use Heading 1 style
   - Chapters always use Heading 2 style (configurable)
   - Sub-sections and sub-sub-sections with customizable formatting
   - Automatic heading level adjustment

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