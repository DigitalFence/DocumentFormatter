# Manual Automator Setup Instructions

Since the automated installer isn't working, here's how to create the Quick Action manually:

## Step 1: Open Automator
1. Open **Automator** (should already be open)
2. Choose **"Quick Action"** as the document type

## Step 2: Configure the Quick Action
1. At the top, set:
   - **"Workflow receives current"**: `files or folders`
   - **"in"**: `Finder`

## Step 3: Add the Shell Script Action
1. In the left sidebar, search for **"Run Shell Script"**
2. Drag **"Run Shell Script"** to the workflow area
3. Set the shell to **`/bin/bash`**
4. Set **"Pass input"** to **"as arguments"**

## Step 4: Add the Script Code
Copy and paste this exact code into the script area:

```bash
for file in "$@"
do
    # Check if file is a supported format
    ext="${file##*.}"
    ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    
    if [[ "$ext_lower" == "txt" ]] || [[ "$ext_lower" == "md" ]] || [[ "$ext_lower" == "markdown" ]] || [[ "$ext_lower" == "rtf" ]] || [[ "$ext_lower" == "docx" ]] || [[ "$ext_lower" == "doc" ]]; then
        /Users/KDP/scripts/wordformatterbyclaude/format_document.sh "$file"
    else
        osascript -e "display dialog \"File format not supported: $ext\" buttons {\"OK\"} default button \"OK\""
    fi
done
```

## Step 5: Save the Quick Action
1. Press **Cmd+S** to save
2. Name it: **"Format with Reference Style"**
3. It will automatically save to `~/Library/Services/`

## Step 6: Test
1. Right-click on any `.txt`, `.md`, `.rtf`, or `.docx` file in Finder
2. Look under **"Quick Actions"** for **"Format with Reference Style"**

## Alternative: Use the Command Line Tool

If the Quick Action still doesn't work, you can use the command line tool I created:

```bash
# Navigate to the word formatter directory
cd /Users/KDP/scripts/wordformatterbyclaude

# Format any supported file
./format_file.sh path/to/your/document.txt
```

This will work exactly the same as the Finder integration!
