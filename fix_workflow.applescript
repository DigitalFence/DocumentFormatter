-- AppleScript to fix the Automator workflow
tell application "Automator"
    -- Close any open workflows
    close every workflow saving no
    
    -- Create new Service workflow
    set newWorkflow to make new workflow
    set type of newWorkflow to service workflow
    
    -- Set service to receive files or folders in Finder
    set input types of newWorkflow to {"public.item"}
    set application file of newWorkflow to (path to application "Finder")
    
    -- Add Run Shell Script action
    set runShellScript to make new action at end of actions of newWorkflow with data {name:"Run Shell Script"}
    
    -- Configure the shell script action
    tell runShellScript
        set value of setting "shell" to "/bin/bash"
        set value of setting "inputMethod" to 1 -- as arguments
        set value of setting "COMMAND_STRING" to "for file in \"$@\"
do
    # Check if file is a supported format
    ext=\"${file##*.}\"
    ext_lower=$(echo \"$ext\" | tr '[:upper:]' '[:lower:]')
    
    if [[ \"$ext_lower\" == \"txt\" ]] || [[ \"$ext_lower\" == \"md\" ]] || [[ \"$ext_lower\" == \"markdown\" ]] || [[ \"$ext_lower\" == \"docx\" ]] || [[ \"$ext_lower\" == \"doc\" ]]; then
        /Users/KDP/scripts/wordformatterbyclaude/format_document.sh \"$file\"
    else
        osascript -e \"display dialog \\\"File format not supported: $ext\\\" buttons {\\\"OK\\\"} default button \\\"OK\\\"\"
    fi
done"
    end tell
    
    -- Save the workflow
    save newWorkflow in POSIX file "/Users/KDP/Library/Services/Format with Reference Style.workflow"
    
    -- Close the workflow
    close newWorkflow saving no
end tell