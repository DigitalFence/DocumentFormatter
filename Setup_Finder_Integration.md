# Setting Up Finder Quick Action for Document Formatter

Follow these steps to create a right-click menu option in Finder:

## Step 1: Create the Quick Action in Automator

1. Open **Automator** (find it in Applications or use Spotlight)
2. Choose **Quick Action** (or "Service" on older macOS versions)
3. Configure the workflow settings at the top:
   - **Workflow receives current**: `files or folders`
   - **in**: `Finder.app`

## Step 2: Add the Shell Script Action

1. In the Actions library on the left, search for "Run Shell Script"
2. Drag **Run Shell Script** to the workflow area
3. Configure the action:
   - **Shell**: `/bin/bash`
   - **Pass input**: `as arguments`
   - Replace the default script with this code:

```bash
for file in "$@"
do
    # Check if file is a supported format
    ext="${file##*.}"
    ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    
    if [[ "$ext_lower" == "txt" ]] || [[ "$ext_lower" == "md" ]] || [[ "$ext_lower" == "markdown" ]] || [[ "$ext_lower" == "docx" ]] || [[ "$ext_lower" == "doc" ]]; then
        /Users/KDP/scripts/wordformatterbyclaude/format_document.sh "$file"
    else
        osascript -e "display dialog \"File format not supported: $ext\" buttons {\"OK\"} default button \"OK\""
    fi
done
```

## Step 3: Save the Quick Action

1. Save the workflow with a descriptive name like **"Format with Reference Style"**
2. The workflow will be saved to `~/Library/Services/`

## Step 4: Set Up Reference File

Before using the service, place your reference Word document in one of these locations:
- `/Users/KDP/scripts/wordformatterbyclaude/referenceformat.docx`
- `~/Documents/referenceformat.docx`
- `~/Desktop/referenceformat.docx`

## How to Use

1. Right-click on any text, markdown, or Word document in Finder
2. Go to **Quick Actions** (or **Services** on older macOS)
3. Click **"Format with Reference Style"**
4. The formatted document will be created in the same folder with "_formatted" suffix

## Supported File Types
- Text files (.txt)
- Markdown files (.md, .markdown)
- Word documents (.docx, .doc)

## Troubleshooting

If the service doesn't appear:
- Go to **System Preferences** > **Security & Privacy** > **Privacy** > **Automation**
- Make sure Finder is allowed to control System Events

If you get permission errors:
- Make sure the format_document.sh script is executable
- Check that the virtual environment is properly set up