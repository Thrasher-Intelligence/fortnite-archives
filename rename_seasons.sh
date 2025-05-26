#!/bin/bash

# Loop through each chapter folder
for chapter in chapter_*; do
  if [[ -d "$chapter" ]]; then
    echo "Checking $chapter..."
    cd "$chapter"
    
    for saison in Saison*; do
      if [[ -d "$saison" ]]; then
        num=$(echo "$saison" | grep -o '[0-9]\+')
        new_name="season_$num"
        mv "$saison" "$new_name"
        echo "Renamed '$saison' -> '$new_name'"
      fi
    done

    cd ..
  fi
done
