#!/bin/bash
# Installs the Channel 12 Countdown plugin into SwiftBar

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$SCRIPT_DIR/channel12-countdown.1s.py"
SWIFTBAR_PLUGINS="$HOME/dev/private/swiftbar-plugins"

# Make plugin executable
chmod +x "$PLUGIN"

# Create symlink in SwiftBar plugins directory
if [ -d "$SWIFTBAR_PLUGINS" ]; then
    LINK="$SWIFTBAR_PLUGINS/channel12-countdown.1s.py"
    if [ -L "$LINK" ] || [ -f "$LINK" ]; then
        echo "Removing existing link..."
        rm "$LINK"
    fi
    ln -s "$PLUGIN" "$LINK"
    echo "Symlinked plugin to SwiftBar: $LINK"
    echo ""
    echo "SwiftBar should pick it up automatically."
    echo "If not, click SwiftBar icon -> Refresh All."
else
    echo "SwiftBar plugins directory not found at: $SWIFTBAR_PLUGINS"
    echo "Please symlink manually:"
    echo "  ln -s '$PLUGIN' /path/to/swiftbar/plugins/channel12-countdown.1s.py"
fi

echo ""
echo "Next steps:"
echo "  1. Run ./download-audio.sh to get the Channel 12 intro music"
echo "  2. Edit config.json to set your meeting times"
