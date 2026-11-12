#!/usr/bin/env python3
"""Turn training sessions (JSON) into an iCalendar file. Standard library only.

Example:
  export_ics.py --input week.json --output week.ics

Input JSON:
  {
    "calendar_name": "Training",            optional
    "uid_domain": "tri-coach-skills",       optional
    "default_reminders_min": [1440, 45],    optional, for timed sessions only
    "sessions": [
      {
        "id": "2026-S49-2",                 stable: same id, same calendar event
        "date": "2026-12-01",
        "time": "18:45",                    omit for an all-day event
        "duration_min": 60,                 required with "time"
        "discipline": "run",                run, bike, swim, strength, rest, race
        "discipline_label": "course",       optional, shown in the description
        "title": "Seuil 3x8 min",           emoji + title: 40 characters at most
        "location": "Stade municipal",      required except for rest
        "distance": "9 km",                 optional
        "lines": ["15 min ...", "..."],     at most 4, each starts with a quantity
        "why": "...",                       required for run, bike, swim, strength
        "fallback": "...",                  required for run, bike, swim
        "reminders_min": [1440, 45]         optional, overrides the default
      }
    ]
  }

The same "id" always gives the same UID, so importing a new export updates
the events instead of duplicating them. Times are floating local times.
Exit code 2 and a JSON list of problems on stderr if a session breaks a rule.
"""
import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone

EMOJI = {"run": "\U0001F3C3", "bike": "\U0001F6B4", "swim": "\U0001F3CA",
         "strength": "\U0001F9D8", "rest": "\U0001F634", "race": "\U0001F3C1"}
MAX_TITLE = 40
MAX_LINES = 4
MAX_LINE_LENGTH = 45
MAX_OCTETS = 75
DASHES = ("\u2014", "\u2013")
ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def summary(session):
    return f"{EMOJI[session['discipline']]} {session['title']}"


def validate(session, index):
    """Return the list of problems for one session."""
    label = session.get("id") or f"session {index + 1}"
    problems = []

    def problem(text):
        problems.append(f"{label}: {text}")

    for field in ("id", "date", "discipline", "title"):
        if not session.get(field):
            problem(f"missing '{field}'")
    if problems:
        return problems

    discipline = session["discipline"]
    if discipline not in EMOJI:
        problem(f"unknown discipline '{discipline}'")
        return problems
    if not ID_PATTERN.match(session["id"]):
        problem("id may only contain letters, digits, dot, underscore and hyphen")
    try:
        date.fromisoformat(session["date"])
    except ValueError:
        problem(f"date '{session['date']}' is not YYYY-MM-DD")
    if session.get("time"):
        try:
            datetime.strptime(session["time"], "%H:%M")
        except ValueError:
            problem(f"time '{session['time']}' is not HH:MM")
        if not isinstance(session.get("duration_min"), int) or session["duration_min"] <= 0:
            problem("'duration_min' is required with 'time'")
    if len(summary(session)) > MAX_TITLE:
        problem(f"title is {len(summary(session))} characters with its emoji, maximum {MAX_TITLE}")

    lines = session.get("lines", [])
    if len(lines) > MAX_LINES:
        problem(f"{len(lines)} instruction lines, maximum {MAX_LINES}")
    for line in lines:
        if not line[:1].isdigit():
            problem(f"line does not start with a quantity: '{line}'")
        if len(line) > MAX_LINE_LENGTH:
            problem(f"line is {len(line)} characters, maximum {MAX_LINE_LENGTH}: '{line}'")

    if discipline != "rest" and not session.get("location"):
        problem("missing 'location'")
    if discipline in ("run", "bike", "swim", "strength") and not session.get("why"):
        problem("missing 'why' paragraph")
    if discipline in ("run", "bike", "swim") and not session.get("fallback"):
        problem("missing 'fallback'")

    texts = [session["title"], session.get("why", ""), session.get("fallback", ""),
             session.get("location", ""), *lines]
    if any(dash in text for text in texts for dash in DASHES):
        problem("em dash or en dash found, use a comma, a colon or two sentences")
    return problems


def escape(text):
    return (text.replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\n", "\\n"))


def fold(line):
    """Fold a content line so that no physical line exceeds 75 octets."""
    if len(line.encode("utf-8")) <= MAX_OCTETS:
        return [line]
    parts, current, size = [], "", 0
    for char in line:
        width = len(char.encode("utf-8"))
        if size + width > MAX_OCTETS:
            parts.append(current)
            current, size = " ", 1
        current += char
        size += width
    parts.append(current)
    return parts


def description(session):
    rows = [f"DISCIPLINE: {session.get('discipline_label') or session['discipline']}"]
    if session.get("distance"):
        rows.append(f"DISTANCE: {session['distance']}")
    rows += [f"- {line}" for line in session.get("lines", [])]
    prose = [text for text in (session.get("why"), session.get("fallback")) if text]
    if prose:
        rows.append("---")
        rows += prose
    return "\n".join(rows)


def event(session, stamp, domain, default_reminders):
    day = date.fromisoformat(session["date"])
    title = summary(session)
    lines = ["BEGIN:VEVENT", f"UID:{session['id']}@{domain}", f"DTSTAMP:{stamp}"]
    if session.get("time"):
        start = datetime.combine(day, datetime.strptime(session["time"], "%H:%M").time())
        end = start + timedelta(minutes=session["duration_min"])
        lines += [f"DTSTART:{start:%Y%m%dT%H%M%S}", f"DTEND:{end:%Y%m%dT%H%M%S}"]
    else:
        lines += [f"DTSTART;VALUE=DATE:{day:%Y%m%d}",
                  f"DTEND;VALUE=DATE:{day + timedelta(days=1):%Y%m%d}",
                  "TRANSP:TRANSPARENT"]
    lines += [f"SUMMARY:{escape(title)}", f"DESCRIPTION:{escape(description(session))}"]
    if session.get("location"):
        lines.append(f"LOCATION:{escape(session['location'])}")
    # Default reminders only make sense for timed events.
    for minutes in session.get("reminders_min", default_reminders if session.get("time") else []):
        lines += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{escape(title)}",
                  f"TRIGGER:-PT{int(minutes)}M", "END:VALARM"]
    lines.append("END:VEVENT")
    return lines


def build_calendar(data, stamp):
    sessions = data.get("sessions", [])
    problems = [p for i, s in enumerate(sessions) for p in validate(s, i)]
    ids = [s.get("id") for s in sessions]
    problems += [f"{i}: id used twice" for i in sorted({i for i in ids if ids.count(i) > 1})]
    if problems:
        return None, problems

    domain = data.get("uid_domain", "tri-coach-skills")
    reminders = data.get("default_reminders_min", [1440, 45])
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//tri-coach-skills//export_ics//EN",
             "CALSCALE:GREGORIAN"]
    if data.get("calendar_name"):
        lines.append(f"X-WR-CALNAME:{escape(data['calendar_name'])}")
    for session in sorted(sessions, key=lambda s: (s["date"], s.get("time", ""))):
        lines += event(session, stamp, domain, reminders)
    lines.append("END:VCALENDAR")
    folded = [part for line in lines for part in fold(line)]
    return "\r\n".join(folded) + "\r\n", []


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", help="sessions JSON file (default: stdin)")
    parser.add_argument("--output", help=".ics file to write (default: stdout)")
    parser.add_argument("--now", help="DTSTAMP to use, as YYYYMMDDTHHMMSSZ (default: now)")
    args = parser.parse_args(argv)

    if args.input:
        with open(args.input, encoding="utf-8") as handle:
            data = json.load(handle)
    else:
        data = json.load(sys.stdin)
    stamp = args.now or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    text, problems = build_calendar(data, stamp)
    if problems:
        json.dump({"problems": problems}, sys.stderr, indent=2, ensure_ascii=False)
        sys.stderr.write("\n")
        sys.exit(2)
    payload = text.encode("utf-8")
    if args.output:
        with open(args.output, "wb") as handle:
            handle.write(payload)
    else:
        sys.stdout.buffer.write(payload)


if __name__ == "__main__":
    main()
