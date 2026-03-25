#!/bin/bash
# One-command setup for Channel 12 Meeting Countdown
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$SCRIPT_DIR/channel12-countdown.1s.py"
AUDIO_DIR="$SCRIPT_DIR/audio"
AUDIO_FILE="$AUDIO_DIR/channel12-intro.mp3"
YOUTUBE_URL="https://www.youtube.com/watch?v=YXDMkme5rb0"

echo "=== Channel 12 Meeting Countdown Setup ==="
echo ""

# 1. Check dependencies
for cmd in python3 yt-dlp ffmpeg afplay swiftc; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Missing: $cmd"
        echo "Install with: brew install $cmd"
        exit 1
    fi
done

# 2. Make scripts executable
chmod +x "$PLUGIN" "$SCRIPT_DIR/demo.sh"

# 3. Download and trim audio
if [ ! -f "$AUDIO_FILE" ]; then
    echo "[1/4] Downloading Channel 12 news intro..."
    mkdir -p "$AUDIO_DIR"
    TMP="/tmp/channel12-full.mp3"
    yt-dlp -x --audio-format mp3 --audio-quality 0 -o "$TMP" "$YOUTUBE_URL" 2>/dev/null
    echo "[2/4] Trimming audio (seconds 7-40, 1s fade out)..."
    ffmpeg -y -ss 7 -i "$TMP" -t 33 -af "afade=t=out:st=32:d=1" "$AUDIO_FILE" 2>/dev/null
    rm -f "$TMP"
    echo "       Audio ready."
else
    echo "[1/4] Audio already downloaded. Skipping."
    echo "[2/4] Skipping trim."
fi

# 4. Compile key-stopper (mouse-to-dismiss)
echo "[3/4] Compiling key-stopper..."
swiftc -o "$SCRIPT_DIR/key-stopper" "$SCRIPT_DIR/key-stopper.swift" 2>/dev/null
echo "       Done."

# 5. Symlink to SwiftBar
echo "[4/4] Installing SwiftBar plugin..."
SWIFTBAR_DIR=$(defaults read com.ameba.SwiftBar PluginDirectory 2>/dev/null || echo "")
if [ -z "$SWIFTBAR_DIR" ]; then
    echo "       SwiftBar not found. Install it: brew install --cask swiftbar"
    echo "       Then re-run this script."
    exit 1
fi
LINK="$SWIFTBAR_DIR/channel12-countdown.1s.py"
[ -L "$LINK" ] || [ -f "$LINK" ] && rm "$LINK"
ln -s "$PLUGIN" "$LINK"
echo "       Symlinked to $LINK"

echo ""
echo "=== Done! ==="
echo ""
echo "Edit config.json to set your meetings, then SwiftBar picks it up."
echo "Run ./demo.sh to test it now."
