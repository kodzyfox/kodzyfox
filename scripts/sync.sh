#!/bin/bash
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

# Run update python script
python3 "$DIR/scripts/update_music.py"

# Only commit and push if the card actually changed
if ! git diff --quiet assets/spotify-card.svg; then
    git add assets/spotify-card.svg
    git commit -m "🎵 auto-update currently playing track"
    git push origin main
    echo "✨ Successfully synced new track to GitHub!"
else
    echo "No track change detected."
fi
