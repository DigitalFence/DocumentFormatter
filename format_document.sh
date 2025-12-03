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

# Determine configuration file path (matches Python config_loader.py priority)
# Priority order:
# 1. FORMATTER_CONFIG_PATH environment variable
# 2. External reference folder (~/WordFormatReference/formatter_config.json)
# 3. If no config found, uses .dotx template styles (no local fallbacks)

CONFIG_FILE=""
EXTERNAL_REF_FOLDER="$HOME/WordFormatReference"

# Priority 1: Environment variable
if [ -n "$FORMATTER_CONFIG_PATH" ] && [ -f "$FORMATTER_CONFIG_PATH" ]; then
    CONFIG_FILE="$FORMATTER_CONFIG_PATH"
    echo "Using config from environment variable: $CONFIG_FILE"

# Priority 2: External reference folder
elif [ -f "$EXTERNAL_REF_FOLDER/formatter_config.json" ]; then
    CONFIG_FILE="$EXTERNAL_REF_FOLDER/formatter_config.json"
    echo "Using config from external reference folder: $CONFIG_FILE"

else
    echo "No config file found - will use .dotx template styles"
fi

# Note: Python's config_loader.py will handle all template path resolution
# If no config exists, the .dotx template's built-in styles will be used
# This ensures shell and Python use the same logic

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
            "$HOME/.claude/local/claude"               # Claude Code install
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
            # Enable debug logging
            export WORD_FORMATTER_DEBUG=1
            
            # Add config file parameter if available
            # Python will resolve template path via config_loader.py
            if [ -n "$CONFIG_FILE" ]; then
                python "$SCRIPT_DIR/document_converter_ai.py" --config "$CONFIG_FILE" "$file"
            else
                python "$SCRIPT_DIR/document_converter_ai.py" "$file"
            fi
            converter_exit_code=$?
            echo "AI converter exit code: $converter_exit_code"
            
            # Send completion notification
            if [ $converter_exit_code -eq 0 ]; then
                send_notification "Word Formatter" "Conversion Complete ✓" "$filename successfully converted with AI enhancement" "Hero"
            else
                send_notification "Word Formatter" "Error ✗" "AI conversion failed for $filename, check logs" "Basso"
            fi
        else
            echo "WARNING: Claude CLI not found in any common location"
            echo "PATH: $PATH"
            echo "Searched locations:"
            for location in "${claude_locations[@]}"; do
                echo "  - $location: $([ -x "$location" ] && echo "exists but not executable" || echo "not found")"
            done
            echo "Using AI converter with fallback to simple text-to-markdown conversion..."

            # Send notification for fallback to simple conversion
            filename=$(basename "$file")
            send_notification "Word Formatter" "Fallback Mode" "Claude AI not available, using simple conversion for $filename" "Submarine"

            # Enable debug logging
            export WORD_FORMATTER_DEBUG=1

            # Still use AI converter - it has fallback logic for when Claude is not available
            # This ensures RTF/TXT files get proper markdown structure detection
            # Python will resolve template path via config_loader.py
            if [ -n "$CONFIG_FILE" ]; then
                python "$SCRIPT_DIR/document_converter_ai.py" --config "$CONFIG_FILE" "$file"
            else
                python "$SCRIPT_DIR/document_converter_ai.py" "$file"
            fi
            converter_exit_code=$?
            echo "AI converter (fallback mode) exit code: $converter_exit_code"

            # Send completion notification for simple conversion
            if [ $converter_exit_code -eq 0 ]; then
                send_notification "Word Formatter" "Conversion Complete" "$filename converted successfully (fallback mode)" "Hero"
            else
                send_notification "Word Formatter" "Error ✗" "Conversion failed for $filename" "Basso"
            fi
        fi
    else
        echo "Non-text file, using simple converter..."
        
        # Send notification for non-text file processing
        filename=$(basename "$file")
        send_notification "Word Formatter" "Standard Conversion" "Processing $filename (non-text file)" "Glass"
        
        # Use document_converter.py with config support
        # Python will resolve template path via config_loader.py
        if [ -n "$CONFIG_FILE" ]; then
            python "$SCRIPT_DIR/document_converter.py" --input "$file" --config "$CONFIG_FILE"
        else
            python "$SCRIPT_DIR/document_converter.py" --input "$file"
        fi
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