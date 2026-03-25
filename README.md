# Channel 12 Meeting Countdown

A SwiftBar plugin that counts down to your next meeting in the macOS menu bar, then plays the Israeli Channel 12 news intro music as it hits zero.

Reads meetings directly from your macOS Calendar app.

## Setup

```bash
git clone git@github.com:danlinenberg/meeting-sound-swiftbar.git
cd meeting-sound-swiftbar
./setup.sh
```

## How it works

1. Reads your next meeting from macOS Calendar
2. Shows countdown in the menu bar with a bell icon
3. Turns red when music starts (33s before)
4. Blinks in the final 10 seconds
5. Shows "is live!" when it hits zero
6. Move your mouse/trackpad to dismiss the music

## Config (optional)

Edit `config.json` to tweak timing:

```json
{
  "audio_file": "channel12-intro.mp3",
  "lead_time_seconds": 33,
  "red_threshold_seconds": 8,
  "blink_threshold_seconds": 10
}
```

## Requirements

- macOS
- [SwiftBar](https://github.com/swiftbar/SwiftBar)
- Python 3
