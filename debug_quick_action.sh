#!/bin/bash
# Debug script for Quick Action troubleshooting

# Log everything to a debug file
exec > "/tmp/quick_action_debug.log" 2>&1

echo "=== Quick Action Debug Log $(date) ==="
echo "Arguments received: $@"
echo "Number of arguments: $#"
echo "Current working directory: $(pwd)"
echo "User: $(whoami)"
echo "PATH: $PATH"
echo ""

# Process each file
for file in "$@"
do
    echo "Processing file: '$file'"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        echo "ERROR: File does not exist: $file"
        continue
    fi
    
    # Get file info
    echo "File exists: YES"
    echo "File size: $(stat -f%z "$file") bytes"
    echo "File permissions: $(stat -f%Mp%Lp "$file")"
    
    # Check file extension
    ext="${file##*.}"
    ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    echo "File extension: $ext_lower"
    
    # Check if supported
    if [[ "$ext_lower" == "txt" ]] || [[ "$ext_lower" == "md" ]] || [[ "$ext_lower" == "markdown" ]] || [[ "$ext_lower" == "rtf" ]] || [[ "$ext_lower" == "docx" ]] || [[ "$ext_lower" == "doc" ]]; then
        echo "File type supported: YES"
        
        # Check if the main script exists
        main_script="/Users/KDP/scripts/wordformatterbyclaude/format_document.sh"
        echo "Looking for main script: $main_script"
        
        if [ -f "$main_script" ]; then
            echo "Main script found: YES"
            echo "Main script permissions: $(stat -f%Mp%Lp "$main_script")"
            
            # Try to execute it
            echo "Attempting to execute main script..."
            "$main_script" "$file"
            exit_code=$?
            echo "Script exit code: $exit_code"
            
            if [ $exit_code -eq 0 ]; then
                echo "SUCCESS: Script executed successfully"
                # Show notification
                osascript -e "display notification \"Document formatted successfully\" with title \"Word Formatter\" sound name \"Hero\""
            else
                echo "ERROR: Script failed with exit code $exit_code"
                # Show error notification
                osascript -e "display notification \"Formatting failed. Check debug log.\" with title \"Word Formatter\" sound name \"Basso\""
            fi
        else
            echo "ERROR: Main script not found at $main_script"
            osascript -e "display notification \"Script not found at expected location\" with title \"Word Formatter\" sound name \"Basso\""
        fi
    else
        echo "File type not supported: $ext_lower"
        osascript -e "display dialog \"File format not supported: $ext\" buttons {\"OK\"} default button \"OK\""
    fi
    
    echo "--- End processing file: '$file' ---"
    echo ""
done

echo "=== Debug Log End ==="
