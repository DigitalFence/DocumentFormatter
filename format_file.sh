#!/bin/bash
# Simple wrapper for formatting documents
# Usage: ./format_file.sh path/to/document.txt

if [ $# -eq 0 ]; then
    echo "Usage: $0 <file>"
    echo "Supported formats: .txt, .md, .rtf, .docx, .doc"
    exit 1
fi

file="$1"

if [ ! -f "$file" ]; then
    echo "Error: File '$file' not found"
    exit 1
fi

echo "Formatting document: $(basename "$file")"
echo "Using Word Formatter with Claude AI..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the formatter
"$SCRIPT_DIR/format_document.sh" "$file"

if [ $? -eq 0 ]; then
    echo "✅ Document formatted successfully!"
    echo "Check for _formatted.docx and _markdown.md files in the same directory."
else
    echo "❌ Error occurred during formatting. Check the log at /tmp/word_formatter.log"
fi
