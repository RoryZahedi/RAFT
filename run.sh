#!/bin/bash

# Open five VS Code terminal windows and run the client.py script in each one
cd "$(dirname "$0")"
for i in {1..5}
do
  osascript -e 'tell application "Visual Studio Code"
    activate
    tell application "System Events" to keystroke "j" using command down
    delay 1
    tell application "System Events" to keystroke "cd $(pwd)" & return
    tell application "System Events" to keystroke "python3 client.py" & return
    delay 1
  end tell'
done
