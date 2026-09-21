#!/usr/bin/env python3
import subprocess
import urllib.request
import base64
import os
import ssl
import sys

def get_spotify_macos():
    script = """
    tell application "Spotify"
        if it is running then
            try
                set trackName to name of current track
                set trackArtist to artist of current track
                set trackArtwork to artwork url of current track
                return trackName & "|||" & trackArtist & "|||" & trackArtwork
            on error
                return ""
            end try
        end if
    end tell
    """
    try:
        res = subprocess.check_output(["osascript", "-e", script], text=True).strip()
        if "|||" in res:
            parts = res.split("|||")
            return parts[0], parts[1], parts[2]
    except Exception:
        pass
    return None

def main():
    info = get_spotify_macos()
    if not info:
        return

    track_name, artist_name, artwork_url = info
    card_path = os.path.join(os.path.dirname(__file__), "..", "assets", "spotify-card.svg")

    # Quick check if card already shows this track to avoid redundant work
    if os.path.exists(card_path):
        try:
            with open(card_path, "r", encoding="utf-8") as f:
                content = f.read()
                if f">{track_name}<" in content and f">{artist_name}<" in content:
                    print("Track unchanged, skipping.")
                    return
        except Exception:
            pass

    print(f"🎵 Updating to: {track_name} by {artist_name}")

    cover_bytes = b""
    if artwork_url:
        try:
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(artwork_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                cover_bytes = resp.read()
        except Exception as e:
            print(f"Warning: Could not fetch artwork: {e}")

    b64_img = ""
    if cover_bytes:
        raw_path = "/tmp/spotify_raw_art.jpg"
        thumb_path = "/tmp/spotify_art_thumb.jpg"
        with open(raw_path, "wb") as f:
            f.write(cover_bytes)
        subprocess.run(["sips", "-Z", "180", raw_path, "--out", thumb_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(thumb_path):
            with open(thumb_path, "rb") as f:
                b64_img = base64.b64encode(f.read()).decode("utf-8")
        else:
            b64_img = base64.b64encode(cover_bytes).decode("utf-8")

    svg = f"""<svg width="550" height="110" viewBox="0 0 550 110" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .brand {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 11px; font-weight: 600; fill: #8B949E; letter-spacing: 0.5px; }}
    .track {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 18px; font-weight: 700; fill: #FFFFFF; }}
    .artist {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 500; fill: #A0ACB8; }}
    .status {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 11px; fill: #1DB954; font-weight: 500; }}
    .bar {{ fill: #1DB954; }}
  </style>

  <rect x="0.5" y="0.5" width="549" height="109" rx="12" fill="#0D1117" stroke="#30363D"/>

  <defs>
    <clipPath id="albumCoverClip">
      <rect x="15" y="15" width="80" height="80" rx="8" />
    </clipPath>
  </defs>

  <image x="15" y="15" width="80" height="80" clip-path="url(#albumCoverClip)" href="data:image/jpeg;base64,{b64_img}" preserveAspectRatio="xMidYMid slice" />
  <rect x="15" y="15" width="80" height="80" rx="8" stroke="#30363D" fill="none" />

  <g transform="translate(110, 16)">
    <circle cx="6" cy="6" r="6" fill="#1DB954"/>
    <path d="M8.8 5.1C7.0 4.1 4.1 4.0 2.4 4.5C2.1 4.6 1.8 4.4 1.7 4.1C1.6 3.9 1.8 3.6 2.1 3.5C4.1 2.9 7.3 3.0 9.4 4.2C9.6 4.4 9.7 4.7 9.6 4.9C9.4 5.1 9.1 5.2 8.8 5.1ZM8.7 6.8C8.6 7.0 8.3 7.1 8.1 6.9C6.6 6.0 4.3 5.7 2.6 6.3C2.3 6.3 2.1 6.2 2.0 6.0C1.9 5.7 2.1 5.5 2.3 5.4C4.3 4.8 6.8 5.1 8.5 6.1C8.7 6.3 8.8 6.6 8.7 6.8ZM8.0 8.4C7.9 8.5 7.7 8.6 7.5 8.5C6.3 7.7 4.6 7.5 2.7 7.9C2.5 8.0 2.3 7.8 2.3 7.6C2.2 7.4 2.4 7.2 2.6 7.2C4.7 6.7 6.5 6.9 7.9 7.8C8.1 7.9 8.1 8.2 8.0 8.4Z" fill="#0D1117"/>
    <text x="18" y="10" class="brand">SPOTIFY NOW PLAYING</text>
  </g>

  <text x="110" y="55" class="track">{track_name}</text>
  <text x="110" y="76" class="artist">{artist_name}</text>

  <g transform="translate(110, 93)">
    <circle cx="4" cy="-4" r="3" fill="#1DB954">
      <animate attributeName="opacity" values="1;0.4;1" dur="2s" repeatCount="indefinite" />
    </circle>
    <text x="14" y="0" class="status">Listening now • Synced with AURA</text>
  </g>

  <g transform="translate(485, 45)">
    <rect class="bar" x="0" y="10" width="4" height="20" rx="2">
      <animate attributeName="height" values="8;30;12;32;8" dur="1.2s" repeatCount="indefinite"/>
      <animate attributeName="y" values="22;0;18;-2;22" dur="1.2s" repeatCount="indefinite"/>
    </rect>
    <rect class="bar" x="8" y="5" width="4" height="25" rx="2">
      <animate attributeName="height" values="24;8;30;14;24" dur="0.9s" repeatCount="indefinite"/>
      <animate attributeName="y" values="6;22;0;16;6" dur="0.9s" repeatCount="indefinite"/>
    </rect>
    <rect class="bar" x="16" y="15" width="4" height="15" rx="2">
      <animate attributeName="height" values="14;32;6;22;14" dur="1.1s" repeatCount="indefinite"/>
      <animate attributeName="y" values="16;-2;24;8;16" dur="1.1s" repeatCount="indefinite"/>
    </rect>
    <rect class="bar" x="24" y="8" width="4" height="22" rx="2">
      <animate attributeName="height" values="28;12;26;8;28" dur="1.3s" repeatCount="indefinite"/>
      <animate attributeName="y" values="2;18;4;22;2" dur="1.3s" repeatCount="indefinite"/>
    </rect>
    <rect class="bar" x="32" y="12" width="4" height="18" rx="2">
      <animate attributeName="height" values="10;24;16;30;10" dur="0.8s" repeatCount="indefinite"/>
      <animate attributeName="y" values="20;6;14;0;20" dur="0.8s" repeatCount="indefinite"/>
    </rect>
  </g>
</svg>"""

    with open(card_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Updated card to: {track_name}")

if __name__ == "__main__":
    main()
