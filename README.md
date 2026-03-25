# Channel 12 Meeting Countdown

A SwiftBar plugin that counts down to your next meeting in the macOS menu bar, then plays the Israeli Channel 12 (חדשות 12) news intro music as it hits zero.


## How it works

1. Shows countdown in the menu bar: `((•)) Team Sync in 0:15`
2. Turns red when under 8 seconds
3. Plays the Channel 12 news intro during the final countdown
4. Shows `((•)) Team Sync is live!` when it hits zero

## Setup

```bash
# 1. Install the SwiftBar plugin
chmod +x install.sh && ./install.sh

# 2. Download the Channel 12 intro audio
chmod +x download-audio.sh && ./download-audio.sh

# 3. Edit your meeting schedule
vim config.json
```

## Config

Edit `config.json`:

```json
{
  "meetings": [
    {
      "name": "Team Sync",
      "times": ["12:00"],
      "days": ["sun", "mon", "tue", "wed", "thu"]
    },
    {
      "name": "Standup",
      "times": ["09:30"],
      "days": ["sun", "mon", "tue", "wed", "thu"]
    }
  ],
  "audio_file": "channel12-intro.mp3",
  "lead_time_seconds": 15,
  "red_threshold_seconds": 8
}
```

- `lead_time_seconds`: How many seconds before the meeting to start the countdown and play audio
- `red_threshold_seconds`: When the countdown turns red
- `audio_file`: Filename in the `audio/` directory

## Requirements

- [SwiftBar](https://github.com/swiftbar/SwiftBar)
- Python 3
- `afplay` (built into macOS)
- `yt-dlp` + `ffmpeg` (for downloading audio)
