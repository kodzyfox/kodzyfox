#!/bin/bash
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# If Spotify isn't running, exit immediately (takes 0.002s, zero load)
if ! pgrep -x "Spotify" >/dev/null; then
    exit 0
fi

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
fi
