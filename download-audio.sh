#!/bin/bash
# Downloads Channel 12 (Keshet 12) news intro music from YouTube
# Requires: yt-dlp, ffmpeg

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AUDIO_DIR="$SCRIPT_DIR/audio"
OUTPUT="$AUDIO_DIR/channel12-intro.mp3"

if [ -f "$OUTPUT" ]; then
    echo "Audio file already exists at: $OUTPUT"
    echo "Delete it first if you want to re-download."
    exit 0
fi

mkdir -p "$AUDIO_DIR"

# Search for Channel 12 news intro on YouTube
# You may need to update this URL if the video becomes unavailable
echo "Searching for Channel 12 news intro..."
echo ""
echo "Please find a YouTube video of the Channel 12 (חדשות 12) news intro."
echo "Good search terms: 'פתיח חדשות 12' or 'channel 12 israel news intro'"
echo ""
read -p "Paste YouTube URL here: " URL

if [ -z "$URL" ]; then
    echo "No URL provided. Exiting."
    exit 1
fi

echo "Downloading audio..."
yt-dlp \
    -x \
    --audio-format mp3 \
    --audio-quality 0 \
    -o "$OUTPUT" \
    "$URL"

echo ""
echo "Done! Audio saved to: $OUTPUT"
echo ""
echo "Tip: You can trim it with ffmpeg if needed:"
echo "  ffmpeg -i '$OUTPUT' -ss 0 -t 15 -c copy '$AUDIO_DIR/channel12-intro-trimmed.mp3'"
echo "  mv '$AUDIO_DIR/channel12-intro-trimmed.mp3' '$OUTPUT'"
