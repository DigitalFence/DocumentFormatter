#!/bin/bash
# Format Document - Shell wrapper for Finder integration

# Set up logging
LOG_FILE="/tmp/word_formatter.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=== Word Formatter Log - $(date) ==="
echo "Script started with arguments: $@"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Script directory: $SCRIPT_DIR"

# Check virtual environment
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "ERROR: Virtual environment not found at $SCRIPT_DIR/venv"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Check Python availability
python_version=$(python --version 2>&1)
echo "Python version: $python_version"

# Add common binary paths to PATH for Finder context
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
echo "Updated PATH: $PATH"

# Check notification settings
ENABLE_NOTIFICATIONS=${ENABLE_NOTIFICATIONS:-1}
NOTIFICATION_TYPE=${NOTIFICATION_TYPE:-notification}  # notification, dialog, or none
echo "Notifications enabled: $ENABLE_NOTIFICATIONS (type: $NOTIFICATION_TYPE)"

# Function to send notifications
send_notification() {
    local title="$1"
    local subtitle="$2" 
    local message="$3"
    local sound="${4:-Glass}"
    
    if [ "$ENABLE_NOTIFICATIONS" != "1" ]; then
        return
    fi
    
    case "$NOTIFICATION_TYPE" in
        "dialog")
            osascript -e "display alert \"$title\" message \"$subtitle: $message\" buttons {\"OK\"} default button \"OK\" giving up after 3"
            ;;
        "notification")
            # Try terminal-notifier first (more reliable), fallback to osascript
            if command -v terminal-notifier &> /dev/null; then
                terminal-notifier -title "$title" -subtitle "$subtitle" -message "$message" -sound "$sound" -sender com.apple.finder 2>/dev/null
            else
                osascript -e "display notification \"$message\" with title \"$title\" subtitle \"$subtitle\" sound name \"$sound\"" 2>/dev/null
            fi
            ;;
        "none")
            echo "NOTIFICATION: $title - $subtitle: $message"
            ;;
    esac
}

# Run the converter with all passed files
for file in "$@"; do
    echo "Processing file: $file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        echo "ERROR: File does not exist: $file"
        continue
    fi
    
    # Get file extension
    ext="${file##*.}"
    ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    echo "File extension: $ext_lower"
    
    # Use AI-enhanced converter for text and RTF files, simple converter for others
    if [[ "$ext_lower" == "txt" ]] || [[ "$ext_lower" == "rtf" ]]; then
        echo "Text file detected, checking for Claude CLI..."
        
        # Check if Claude is available in common locations
        claude_path=""
        claude_locations=(
            "claude"                                    # Check PATH first
            "/usr/local/bin/claude"                     # Homebrew Intel
            "/opt/homebrew/bin/claude"                  # Homebrew Apple Silicon
            "/usr/bin/claude"                          # System install
            "$HOME/.local/bin/claude"                  # User install
        )
        
        for location in "${claude_locations[@]}"; do
            if command -v "$location" &> /dev/null; then
                claude_path="$location"
                break
            elif [ -x "$location" ]; then
                claude_path="$location"
                break
            fi
        done
        
        if [ -n "$claude_path" ]; then
            claude_version=$("$claude_path" --version 2>&1)
            echo "Claude CLI found at: $claude_path"
            echo "Claude version: $claude_version"
            echo "Running AI converter..."
            
            # Send notification that AI processing is starting
            filename=$(basename "$file")
            send_notification "Word Formatter" "Claude is processing..." "Starting AI analysis of $filename" "Glass"
            
            # Export the claude path so Python subprocess can find it
            export CLAUDE_CLI_PATH="$claude_path"
            python "$SCRIPT_DIR/document_converter_ai.py" "$file"
            converter_exit_code=$?
            echo "AI converter exit code: $converter_exit_code"
            
            # Send completion notification
            if [ $converter_exit_code -eq 0 ]; then
                send_notification "Word Formatter" "Conversion Complete ✓" "$filename successfully converted with AI enhancement" "Hero"
            else
                send_notification "Word Formatter" "Error ✗" "AI conversion failed for $filename, check logs" "Basso"
            fi
        else
            echo "WARNING: Claude CLI not found in any common location, using simple converter"
            echo "PATH: $PATH"
            echo "Searched locations:"
            for location in "${claude_locations[@]}"; do
                echo "  - $location: $([ -x "$location" ] && echo "exists but not executable" || echo "not found")"
            done
            
            # Send notification for fallback to simple conversion
            filename=$(basename "$file")
            send_notification "Word Formatter" "Fallback Mode" "Claude AI not available, using simple conversion for $filename" "Submarine"
            
            python "$SCRIPT_DIR/document_converter_simple.py" "$file"
            converter_exit_code=$?
            echo "Simple converter exit code: $converter_exit_code"
            
            # Send completion notification for simple conversion
            if [ $converter_exit_code -eq 0 ]; then
                send_notification "Word Formatter" "Conversion Complete" "$filename converted successfully (simple mode)" "Hero"
            else
                send_notification "Word Formatter" "Error ✗" "Conversion failed for $filename" "Basso"
            fi
        fi
    else
        echo "Non-text file, using simple converter..."
        
        # Send notification for non-text file processing
        filename=$(basename "$file")
        send_notification "Word Formatter" "Standard Conversion" "Processing $filename (non-text file)" "Glass"
        
        python "$SCRIPT_DIR/document_converter_simple.py" "$file"
        converter_exit_code=$?
        echo "Simple converter exit code: $converter_exit_code"
        
        # Send completion notification
        if [ $converter_exit_code -eq 0 ]; then
            send_notification "Word Formatter" "Conversion Complete" "$filename converted successfully" "Hero"
        else
            send_notification "Word Formatter" "Error ✗" "Conversion failed for $filename" "Basso"
        fi
    fi
    
    echo "Finished processing: $file"
    echo "---"
done

# Deactivate virtual environment
deactivate
echo "Virtual environment deactivated"
echo "=== Word Formatter Log End - $(date) ==="
echo ""