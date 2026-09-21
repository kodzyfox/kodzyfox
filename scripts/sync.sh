#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
python3 "$DIR/scripts/update_music.py"
cd "$DIR"
git commit -am "🎵 update currently playing music" 2>/dev/null && git push origin main 2>/dev/null
echo "✨ Profile music card updated & pushed to GitHub!"
