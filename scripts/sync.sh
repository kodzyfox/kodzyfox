#!/bin/bash
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# If Spotify isn't running, exit immediately (takes 0.002s, zero load)
if ! pgrep -x "Spotify" >/dev/null; then
    exit 0
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

# 1. Сначала синхронизируемся с GitHub на случай новых коммитов в профиле
git fetch origin main --quiet 2>/dev/null
if ! git rebase origin/main --quiet 2>/dev/null; then
    git rebase --abort 2>/dev/null
    git reset --hard origin/main
fi

# 2. Обновляем SVG-карточку текущего трека
python3 "$DIR/scripts/update_music.py"

# 3. Коммитим и пушим только если карточка изменилась
if ! git diff --quiet assets/spotify-card.svg; then
    git add assets/spotify-card.svg
    git commit -m "🎵 auto-update currently playing track"
    if ! git push origin main 2>/dev/null; then
        # Если push отклонен, аккуратно подтягиваем изменения через rebase и повторяем
        git pull --rebase origin main --quiet 2>/dev/null
        git push origin main
    fi
    echo "✨ Successfully synced new track to GitHub!"
fi
