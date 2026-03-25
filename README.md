# Channel 12 Meeting Countdown

A SwiftBar plugin that counts down to your next meeting in the macOS menu bar, then plays the Israeli Channel 12 (חדשות 12) news intro music as it hits zero.


## How it works

1. Shows countdown in the menu bar with a bell icon
2. Turns red when music starts (33s before)
3. Blinks in the final 10 seconds
4. Shows "is live!" when it hits zero
5. Move your mouse/trackpad to dismiss the music

## Setup

```bash
git clone git@github.com:danlinenberg/meeting-sound-swiftbar.git
cd meeting-sound-swiftbar
./setup.sh
```

That's it. Edit `config.json` to set your meetings.

## Config

```json
{
  "meetings": [
    {
      "name": "Team Sync",
      "times": ["12:00"],
      "days": ["sun", "mon", "tue", "wed", "thu"]
    }
  ],
  "audio_file": "channel12-intro.mp3",
  "lead_time_seconds": 33,
  "red_threshold_seconds": 8,
  "blink_threshold_seconds": 10
}
```

- `lead_time_seconds`: Seconds before meeting to start countdown and play audio
- `red_threshold_seconds`: When the countdown turns red
- `blink_threshold_seconds`: When the countdown starts blinking
- `audio_file`: Filename in the `audio/` directory

## Requirements

- macOS
- [SwiftBar](https://github.com/swiftbar/SwiftBar)
- Python 3, yt-dlp, ffmpeg (`brew install yt-dlp ffmpeg`)
