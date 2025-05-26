#!/bin/bash

for dir in Chapter*; do
  if [[ -d "$dir" ]]; then
    # Extract the number from the folder name
    num=$(echo "$dir" | grep -o '[0-9]\+')
    # Create new name
    new_name="chapter_$num"
    # Rename the folder
    mv "$dir" "$new_name"
    echo "Renamed '$dir' -> '$new_name'"
  fi
done
