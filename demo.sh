#!/bin/bash
# Demo mode: sets a meeting 20 seconds from now so you can test the countdown
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/config.json"
BACKUP="$SCRIPT_DIR/config.json.bak"

# Calculate time 20 seconds from now
MEETING_TIME=$(date -v+20S +"%H:%M")
TODAY=$(date +"%a" | tr '[:upper:]' '[:lower:]')

echo "Setting demo meeting at $MEETING_TIME (20 seconds from now)..."

# Backup current config
cp "$CONFIG" "$BACKUP"

# Write demo config
cat > "$CONFIG" << EOF
{
  "meetings": [
    {
      "name": "Channel 12 News",
      "times": ["$MEETING_TIME"],
      "days": ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
    }
  ],
  "audio_file": "channel12-intro.mp3",
  "lead_time_seconds": 15,
  "red_threshold_seconds": 8
}
EOF

echo "Demo config written. SwiftBar will start counting down."
echo ""
echo "Press Enter after the demo to restore your config..."
read

# Restore
mv "$BACKUP" "$CONFIG"
# Clean up state
rm -rf "$SCRIPT_DIR/.state"
echo "Config restored."
