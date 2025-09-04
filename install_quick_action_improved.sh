#!/bin/bash
# Improved installer script for Format Document Quick Action

echo "Installing Format Document Quick Action (Improved)..."

# Create the Automator workflow file
WORKFLOW_PATH="$HOME/Library/Services/Format with Reference Style.workflow"
mkdir -p "$WORKFLOW_PATH/Contents"

# Create the improved workflow plist file with specific file types
cat > "$WORKFLOW_PATH/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>com.wordformatter.quickaction</string>
    <key>CFBundleName</key>
    <string>Format with Reference Style</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>NSServices</key>
    <array>
        <dict>
            <key>NSMenuItem</key>
            <dict>
                <key>default</key>
                <string>Format with Reference Style</string>
            </dict>
            <key>NSMessage</key>
            <string>runWorkflowAsService</string>
            <key>NSSendFileTypes</key>
            <array>
                <string>public.plain-text</string>
                <string>public.utf8-plain-text</string>
                <string>com.adobe.rtf</string>
                <string>public.rtf</string>
                <string>net.daringfireball.markdown</string>
                <string>public.text</string>
                <string>org.openxmlformats.wordprocessingml.document</string>
                <string>com.microsoft.word.doc</string>
            </array>
            <key>NSRequiredContext</key>
            <array>
                <dict>
                    <key>NSApplicationIdentifier</key>
                    <string>com.apple.finder</string>
                </dict>
            </array>
        </dict>
    </array>
</dict>
</plist>
EOF

# Create the main workflow document (same as before but with better structure)
cat > "$WORKFLOW_PATH/Contents/document.wflow" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>AMApplicationBuild</key>
    <string>523</string>
    <key>AMApplicationVersion</key>
    <string>2.10</string>
    <key>AMDocumentVersion</key>
    <string>2</string>
    <key>actions</key>
    <array>
        <dict>
            <key>action</key>
            <dict>
                <key>AMAccepts</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Optional</key>
                    <true/>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.string</string>
                    </array>
                </dict>
                <key>AMActionVersion</key>
                <string>2.0.3</string>
                <key>AMApplication</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>AMParameterProperties</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <dict/>
                    <key>CheckedForUserDefaultShell</key>
                    <dict/>
                    <key>inputMethod</key>
                    <dict/>
                    <key>shell</key>
                    <dict/>
                    <key>source</key>
                    <dict/>
                </dict>
                <key>AMProvides</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.string</string>
                    </array>
                </dict>
                <key>ActionBundlePath</key>
                <string>/System/Library/Automator/Run Shell Script.action</string>
                <key>ActionName</key>
                <string>Run Shell Script</string>
                <key>ActionParameters</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <string>for file in "$@"
do
    # Check if file is a supported format
    ext="${file##*.}"
    ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    
    if [[ "$ext_lower" == "txt" ]] || [[ "$ext_lower" == "md" ]] || [[ "$ext_lower" == "markdown" ]] || [[ "$ext_lower" == "rtf" ]] || [[ "$ext_lower" == "docx" ]] || [[ "$ext_lower" == "doc" ]]; then
        /Users/KDP/scripts/wordformatterbyclaude/format_document.sh "$file"
    else
        osascript -e "display dialog \"File format not supported: $ext\" buttons {\"OK\"} default button \"OK\""
    fi
done</string>
                    <key>CheckedForUserDefaultShell</key>
                    <true/>
                    <key>inputMethod</key>
                    <integer>1</integer>
                    <key>shell</key>
                    <string>/bin/bash</string>
                    <key>source</key>
                    <string></string>
                </dict>
                <key>BundleIdentifier</key>
                <string>com.apple.RunShellScript</string>
                <key>CFBundleVersion</key>
                <string>2.0.3</string>
                <key>CanShowSelectedItemsWhenRun</key>
                <false/>
                <key>CanShowWhenRun</key>
                <true/>
                <key>Category</key>
                <array>
                    <string>AMCategoryUtilities</string>
                </array>
                <key>Class Name</key>
                <string>RunShellScriptAction</string>
                <key>InputUUID</key>
                <string>0C8D43E6-8311-4B5C-A298-0A2C6F8AC4B0</string>
                <key>Keywords</key>
                <array>
                    <string>Shell</string>
                    <string>Script</string>
                    <string>Command</string>
                    <string>Run</string>
                    <string>Unix</string>
                </array>
                <key>OutputUUID</key>
                <string>7F7E5B92-C6D7-4E56-9E81-81F9B35FC306</string>
                <key>UUID</key>
                <string>B5E2C71F-0467-4657-93AD-E8A83F11C15C</string>
                <key>UnlocalizedApplications</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>arguments</key>
                <dict>
                    <key>0</key>
                    <dict>
                        <key>default value</key>
                        <integer>0</integer>
                        <key>name</key>
                        <string>inputMethod</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>0</string>
                    </dict>
                    <key>1</key>
                    <dict>
                        <key>default value</key>
                        <string></string>
                        <key>name</key>
                        <string>source</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>1</string>
                    </dict>
                    <key>2</key>
                    <dict>
                        <key>default value</key>
                        <false/>
                        <key>name</key>
                        <string>CheckedForUserDefaultShell</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>2</string>
                    </dict>
                    <key>3</key>
                    <dict>
                        <key>default value</key>
                        <string></string>
                        <key>name</key>
                        <string>COMMAND_STRING</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>3</string>
                    </dict>
                    <key>4</key>
                    <dict>
                        <key>default value</key>
                        <string>/bin/sh</string>
                        <key>name</key>
                        <string>shell</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>4</string>
                    </dict>
                </dict>
            </dict>
            <key>isViewVisible</key>
            <true/>
            <key>location</key>
            <string>309.000000:305.000000</string>
            <key>nibPath</key>
            <string>/System/Library/Automator/Run Shell Script.action/Contents/Resources/Base.lproj/main.nib</string>
        </dict>
    </array>
    <key>connectors</key>
    <dict/>
    <key>workflowMetaData</key>
    <dict>
        <key>applicationBundleID</key>
        <string>com.apple.finder</string>
        <key>applicationPath</key>
        <string>/System/Library/CoreServices/Finder.app</string>
        <key>applicationPID</key>
        <integer>615</integer>
        <key>workflowTypeIdentifier</key>
        <string>com.apple.Automator.service</string>
    </dict>
</dict>
</plist>
EOF

# Make the workflow executable
chmod +x "$WORKFLOW_PATH"

echo "Quick Action installed successfully!"
echo ""
echo "Now forcing macOS to refresh the services..."

# Force macOS to refresh services
/System/Library/CoreServices/pbs -flush
killall pbs
/System/Library/CoreServices/pbs -update
killall Finder

echo ""
echo "IMPORTANT: After Finder restarts, you may need to:"
echo "1. Open System Settings > Privacy & Security > Extensions > Finder Extensions"
echo "2. Make sure 'Format with Reference Style' is enabled"
echo ""
echo "Then right-click on any .txt, .md, .rtf, or .docx file in Finder"
echo "and select 'Quick Actions' > 'Format with Reference Style'"
echo ""
echo "The formatted file will be created in the same directory with '_formatted' suffix."
