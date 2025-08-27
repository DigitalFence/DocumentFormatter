# Word Formatter by Claude

An intelligent document formatter that converts text, markdown, and Word documents to match a reference Word document's styling. Features AI-powered text analysis for improved semantic detection and formatting.

## Features

- **Multiple Input Formats**: Supports `.txt`, `.rtf`, `.md`, `.markdown`, `.docx`, and `.doc` files
- **Smart Style Matching**: Automatically extracts and applies formatting from a reference Word document
- **AI-Enhanced Text Processing**: Uses Claude AI to intelligently structure plain text files
- **Finder Integration**: Right-click any document in macOS Finder to format instantly
- **System Notifications**: Real-time notifications for processing stages and completion
- **Preserves Content**: Maintains all original content while upgrading formatting

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

### AI Enhancement Configuration

The AI converter supports several environment variables for customization:

- `CLAUDE_MODEL` - Choose AI model: `haiku`, `sonnet`, or `opus` (default: `sonnet`)
- `SAVE_MARKDOWN` - Save intermediate markdown file: `0` or `1` (default: `1`)
- `SHOW_PROGRESS` - Show conversion progress: `0` or `1` (default: `1`)
- `CLAUDE_TIMEOUT` - Timeout in seconds (default: `120`)
- `WORD_FORMATTER_DEBUG` - Verbose debug output: `0` or `1` (default: `0`)
- `ERROR_LOG` - Path to error log file (optional)
- `ENABLE_NOTIFICATIONS` - Enable system notifications: `0` or `1` (default: `1`)
- `NOTIFICATION_TYPE` - Notification style: `notification`, `dialog`, or `none` (default: `notification`)

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
- Detects heading structures
- Identifies lists and bullet points
- Recognizes quotes and citations (with special handling for Sanskrit, multilingual content)
- Automatically italicizes transliterated and non-English text
- Preserves intentional formatting
- Adds semantic structure
- Handles Unicode characters and diacritical marks

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