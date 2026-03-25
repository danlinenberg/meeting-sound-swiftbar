#!/usr/bin/env python3
# <bitbar.title>Channel 12 Meeting Countdown</bitbar.title>
# <bitbar.version>2.0</bitbar.version>
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
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
STATE_DIR = SCRIPT_DIR / ".state"
AUDIO_PLAYED_FLAG = STATE_DIR / "audio_played"
AUDIO_PID_FILE = STATE_DIR / "audio_pid"
KEY_STOPPER_PID_FILE = STATE_DIR / "key_stopper_pid"
CALENDAR_CACHE = STATE_DIR / "calendar_cache.json"

LEAD_TIME = 33
RED_THRESHOLD = 8
BLINK_THRESHOLD = 10
AUDIO_FILE = "channel12-intro.mp3"

# Calendar calendars to skip
SKIP_CALENDARS = {"Birthdays", "Siri Suggestions", "Scheduled Reminders"}

JXA_SCRIPT = '''
const app = Application('Calendar');
const now = new Date();
const later = new Date(now.getTime() + 24 * 3600000);
const results = [];
const skip = %s;
const cals = app.calendars();
for (let c of cals) {
    if (skip.includes(c.name())) continue;
    try {
        const events = c.events.whose({startDate: {'>=': now, '<=': later}})();
        for (let e of events) {
            if (e.allDayEvent()) continue;
            results.push({name: e.summary(), start: e.startDate().toISOString()});
        }
    } catch(e) {}
}
JSON.stringify(results);
'''


def load_config():
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_next_meeting_from_calendar():
    """Query macOS Calendar for the next upcoming meeting."""
    skip_list = json.dumps(list(SKIP_CALENDARS))
    script = JXA_SCRIPT % skip_list

    # Cache calendar results for 30 seconds to avoid hammering Calendar.app
    now = time.time()
    if CALENDAR_CACHE.exists():
        try:
            cache = json.loads(CALENDAR_CACHE.read_text())
            if now - cache.get("ts", 0) < 30:
                events = cache["events"]
                return _pick_next(events)
        except (json.JSONDecodeError, KeyError):
            pass

    try:
        result = subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", script],
            capture_output=True, text=True, timeout=5,
        )
        events = json.loads(result.stdout) if result.stdout.strip() else []
    except Exception:
        events = []

    STATE_DIR.mkdir(exist_ok=True)
    CALENDAR_CACHE.write_text(json.dumps({"ts": now, "events": events}))
    return _pick_next(events)


def _pick_next(events):
    now = datetime.now()
    candidates = []
    for ev in events:
        start = datetime.fromisoformat(ev["start"].replace("Z", "+00:00")).astimezone().replace(tzinfo=None)
        if start > now - timedelta(seconds=60):
            candidates.append((start, ev["name"]))
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


def play_audio(audio_file):
    path = SCRIPT_DIR / "audio" / audio_file
    if not path.exists() or is_audio_playing():
        return
    try:
        proc = subprocess.Popen(
            ["afplay", str(path)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        STATE_DIR.mkdir(exist_ok=True)
        AUDIO_PID_FILE.write_text(str(proc.pid))

        stopper = subprocess.Popen(
            [str(SCRIPT_DIR / "key-stopper"), str(proc.pid)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        KEY_STOPPER_PID_FILE.write_text(str(stopper.pid))
    except Exception:
        pass


def stop_audio():
    for pid_file in [AUDIO_PID_FILE, KEY_STOPPER_PID_FILE]:
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                os.kill(pid, signal.SIGTERM)
            except (ValueError, ProcessLookupError, PermissionError):
                pass
            pid_file.unlink(missing_ok=True)


def mark_audio_played(meeting_key):
    STATE_DIR.mkdir(exist_ok=True)
    AUDIO_PLAYED_FLAG.write_text(meeting_key)


def was_audio_played(meeting_key):
    if not AUDIO_PLAYED_FLAG.exists():
        return False
    return AUDIO_PLAYED_FLAG.read_text().strip() == meeting_key


def clear_audio_state():
    stop_audio()
    AUDIO_PLAYED_FLAG.unlink(missing_ok=True)
    CALENDAR_CACHE.unlink(missing_ok=True)


SELF = str(Path(__file__).resolve())


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--stop":
        stop_audio()
        return

    config = load_config()
    lead_time = config.get("lead_time_seconds", LEAD_TIME)
    red_threshold = config.get("red_threshold_seconds", RED_THRESHOLD)
    blink_threshold = config.get("blink_threshold_seconds", BLINK_THRESHOLD)
    audio_file = config.get("audio_file", AUDIO_FILE)

    meeting_dt, meeting_name = get_next_meeting_from_calendar()

    if meeting_dt is None:
        print(":bell.fill: No meetings | size=15 font=Menlo-Bold")
        return

    now = datetime.now()
    seconds_left = (meeting_dt - now).total_seconds()
    meeting_key = f"{meeting_name}_{meeting_dt.isoformat()}"
    stop_cmd = f"bash={SELF} param1=--stop terminal=false refresh=true"

    # After meeting started - show "is live!" for 60 seconds
    if seconds_left <= 0 and seconds_left > -60:
        print(f":bell.fill: {meeting_name} is live! | size=15 font=Menlo-Bold")
        print("---")
        print(f"Started at {meeting_dt.strftime('%H:%M')} | {stop_cmd}")
        print(f"Stop Music | {stop_cmd}")
        return

    # Past the "is live!" window - clear state
    if seconds_left <= -60:
        clear_audio_state()

    # In countdown range
    if seconds_left <= lead_time:
        countdown = format_countdown(seconds_left)

        if not was_audio_played(meeting_key):
            play_audio(audio_file)
            mark_audio_played(meeting_key)

        blink_on = int(time.time()) % 2 == 0

        if seconds_left <= blink_threshold:
            color = "#FF3B30" if blink_on else "#FF9999"
            print(f":bell.fill: {meeting_name} in {countdown} | color={color} size=15 font=Menlo-Bold")
        else:
            print(f":bell.fill: {meeting_name} in {countdown} | color=#FF3B30 size=15 font=Menlo-Bold")

        print("---")
        print(f"Starting at {meeting_dt.strftime('%H:%M')} | {stop_cmd}")
        print(f"Stop Music | {stop_cmd}")
        return

    # More than lead_time away
    if seconds_left <= 300:
        countdown = format_countdown(seconds_left)
        print(f":bell.fill: {meeting_name} in {countdown} | size=15 font=Menlo-Bold")
    elif seconds_left <= 3600:
        mins = int(seconds_left / 60)
        print(f":bell.fill: {meeting_name} in {mins}m | size=15 font=Menlo-Bold")
    else:
        print(f":bell.fill: {meeting_name} at {meeting_dt.strftime('%H:%M')} | size=15 font=Menlo-Bold")

    print("---")
    print(f"Next: {meeting_name} at {meeting_dt.strftime('%a %H:%M')} | size=15 font=Menlo-Bold")


if __name__ == "__main__":
    main()
