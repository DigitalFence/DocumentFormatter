#!/bin/bash
# Ultra simple test script

echo "Quick Action was called at $(date)" > /tmp/simple_test.log
echo "Arguments: $@" >> /tmp/simple_test.log

# Show a visible notification
osascript -e "display notification \"Quick Action Test - Arguments: $*\" with title \"Debug\" sound name \"Glass\""
