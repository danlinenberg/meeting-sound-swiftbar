#!/usr/bin/env python3
# <bitbar.title>Channel 12 Meeting Countdown</bitbar.title>
# <bitbar.version>1.0</bitbar.version>
# <bitbar.author>Dan</bitbar.author>
# <bitbar.desc>Counts down to meetings with Channel 12 news intro music</bitbar.desc>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
STATE_DIR = SCRIPT_DIR / ".state"
AUDIO_PLAYED_FLAG = STATE_DIR / "audio_played"
KEY_STOPPER = SCRIPT_DIR / "key-stopper.py"
KEY_STOPPER_PID_FILE = STATE_DIR / "key_stopper_pid"
AUDIO_PID_FILE = STATE_DIR / "audio_pid"

DAY_MAP = {
    0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat", 6: "sun"
}


def load_config():
    if not CONFIG_PATH.exists():
        return {
            "meetings": [
                {"name": "Team Sync", "times": ["12:00"], "days": ["sun", "mon", "tue", "wed", "thu"]}
            ],
            "audio_file": "channel12-intro.mp3",
            "lead_time_seconds": 15,
            "red_threshold_seconds": 8,
        }
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_next_meeting(config):
    now = datetime.now()
    today_name = DAY_MAP[now.weekday()]
    candidates = []

    for meeting in config["meetings"]:
        days = meeting.get("days", ["sun", "mon", "tue", "wed", "thu", "fri", "sat"])

        for day_offset in range(7):
            check_date = now + timedelta(days=day_offset)
            check_day = DAY_MAP[check_date.weekday()]

            if check_day not in days:
                continue

            for time_str in meeting["times"]:
                parts = list(map(int, time_str.split(":")))
                h, m = parts[0], parts[1]
                s = parts[2] if len(parts) > 2 else 0
                meeting_dt = check_date.replace(hour=h, minute=m, second=s, microsecond=0)

                if meeting_dt > now:
                    candidates.append((meeting_dt, meeting["name"]))

    if not candidates:
        return None, None

    candidates.sort(key=lambda x: x[0])
    return candidates[0]


def format_countdown(seconds):
    if seconds <= 0:
        return "0:00"
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}:{s:02d}"


def is_audio_playing():
    if not AUDIO_PID_FILE.exists():
        return False
    try:
        pid = int(AUDIO_PID_FILE.read_text().strip())
        os.kill(pid, 0)
        return True
    except (ValueError, ProcessLookupError, PermissionError):
        AUDIO_PID_FILE.unlink(missing_ok=True)
        return False


def play_audio(config):
    audio_file = SCRIPT_DIR / "audio" / config.get("audio_file", "channel12-intro.mp3")
    if not audio_file.exists():
        return

    if is_audio_playing():
        return

    try:
        proc = subprocess.Popen(
            ["afplay", str(audio_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        STATE_DIR.mkdir(exist_ok=True)
        AUDIO_PID_FILE.write_text(str(proc.pid))

        # Invisible window that catches any keypress and kills audio
        stopper = subprocess.Popen(
            [str(SCRIPT_DIR / "key-stopper"), str(proc.pid)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        KEY_STOPPER_PID_FILE.write_text(str(stopper.pid))
    except Exception:
        pass


def mark_audio_played(meeting_key):
    STATE_DIR.mkdir(exist_ok=True)
    AUDIO_PLAYED_FLAG.write_text(meeting_key)


def was_audio_played(meeting_key):
    if not AUDIO_PLAYED_FLAG.exists():
        return False
    return AUDIO_PLAYED_FLAG.read_text().strip() == meeting_key


def stop_audio():
    for pid_file in [AUDIO_PID_FILE, KEY_STOPPER_PID_FILE]:
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                os.kill(pid, signal.SIGTERM)
            except (ValueError, ProcessLookupError, PermissionError):
                pass
            pid_file.unlink(missing_ok=True)


def clear_audio_state():
    stop_audio()
    AUDIO_PLAYED_FLAG.unlink(missing_ok=True)


SELF = str(Path(__file__).resolve())


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--stop":
        stop_audio()
        return
    config = load_config()
    meeting_dt, meeting_name = get_next_meeting(config)

    if meeting_dt is None:
        print("No meetings | size=15 font=Menlo-Bold")
        return

    now = datetime.now()
    seconds_left = (meeting_dt - now).total_seconds()
    lead_time = config.get("lead_time_seconds", 15)
    red_threshold = config.get("red_threshold_seconds", 8)
    meeting_key = f"{meeting_name}_{meeting_dt.isoformat()}"

    stop_cmd = f"bash={SELF} param1=--stop terminal=false refresh=true"

    # After meeting started - show "is live!" for 60 seconds
    if seconds_left <= 0 and seconds_left > -60:
        print(f":bell.fill: {meeting_name} is live! | size=15 font=Menlo-Bold")
        print("---")
        print(f"Started at {meeting_dt.strftime('%H:%M')} | {stop_cmd}")
        print(f"Stop Music | {stop_cmd}")
        return

    # Past the "is live!" window - clear state and show next meeting
    if seconds_left <= -60:
        clear_audio_state()

    # In countdown range
    if seconds_left <= lead_time:
        countdown = format_countdown(seconds_left)

        # Play audio once when entering lead time
        if not was_audio_played(meeting_key):
            play_audio(config)
            mark_audio_played(meeting_key)

        blink_threshold = config.get("blink_threshold_seconds", 10)
        blink_on = int(time.time()) % 2 == 0

        if seconds_left <= blink_threshold:
            # Rapid blink: alternate red/hidden
            if blink_on:
                print(f":bell.fill: {meeting_name} in {countdown} | color=#FF3B30 size=15 font=Menlo-Bold")
            else:
                print(f":bell.fill: {meeting_name} in {countdown} | color=#FF9999 size=15 font=Menlo-Bold")
        else:
            # Red as soon as music starts
            print(f":bell.fill: {meeting_name} in {countdown} | color=#FF3B30 size=15 font=Menlo-Bold")

        print("---")
        print(f"Starting at {meeting_dt.strftime('%H:%M')} | {stop_cmd}")
        print(f"Stop Music | {stop_cmd}")
        return

    # More than lead_time away - show time until meeting
    if seconds_left <= 300:  # Within 5 minutes, show countdown
        countdown = format_countdown(seconds_left)
        print(f":bell.fill: {meeting_name} in {countdown} | size=15 font=Menlo-Bold")
    elif seconds_left <= 3600:  # Within 1 hour
        mins = int(seconds_left / 60)
        print(f":bell.fill: {meeting_name} in {mins}m | size=15 font=Menlo-Bold")
    else:
        print(f":bell.fill: {meeting_name} at {meeting_dt.strftime('%H:%M')} | size=15 font=Menlo-Bold")

    print("---")
    print(f"Next: {meeting_name} at {meeting_dt.strftime('%a %H:%M')} | size=15 font=Menlo-Bold")
    print(f"Countdown starts {lead_time}s before | size=11 color=gray")
    print(f"Audio: {'ready' if (SCRIPT_DIR / 'audio' / config.get('audio_file', 'channel12-intro.mp3')).exists() else 'MISSING - run download-audio.sh'} | size=11 color=gray")
    print("---")
    print(f"Edit Config | bash=open param1={CONFIG_PATH} terminal=false")
    print(f"Edit Meetings | bash=open param1={CONFIG_PATH} terminal=false")


if __name__ == "__main__":
    main()
