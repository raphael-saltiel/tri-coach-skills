#!/usr/bin/env python3
"""Weekly training ramp for a triathlon plan. Standard library only.

Example:
  ramp.py --start-hours 4.5 --start-date 2026-11-16 --race-date 2027-04-25 \
      --format M --available-hours 8 --long-bike-min 90 --long-run-min 50

Rules encoded:
  - Week 1 is the volume really held in the last complete, normal week.
  - Three load weeks then one recovery week at minus 35 percent.
  - Between two load weeks the increase never exceeds 10 percent. The rate
    is the one needed to reach the plateau by the end of the development
    phase, capped at 10 percent. After a recovery week, load resumes at
    the previous peak.
  - Plateau = min(format plateau, hours the athlete can give).
  - Long ride +15 min, long run +10 percent or +10 min (the smaller),
    on load weeks only, up to the format cap, and only while the two
    long sessions together stay under 60 percent of the week.
  - Initial tests in weeks 1 and 2. First recovery week: initial tests
    that were deferred. Then retests at the end of each recovery week,
    alternating bike+swim and run+swim.
  - Taper of two or three weeks depending on the format.

Output: JSON (default) or CSV, on stdout or to --output.
"""
import argparse
import csv
import io
import json
import sys
from datetime import date, timedelta

FORMATS = {
    "S": {"min_weeks": 8, "plateau_h": 6, "long_bike_cap": 90,
          "long_run_cap": 60, "taper": [0.55, 0.30]},
    "M": {"min_weeks": 12, "plateau_h": 8, "long_bike_cap": 150,
          "long_run_cap": 90, "taper": [0.55, 0.30]},
    "70.3": {"min_weeks": 16, "plateau_h": 11, "long_bike_cap": 240,
             "long_run_cap": 120, "taper": [0.65, 0.45, 0.30]},
    "IM": {"min_weeks": 24, "plateau_h": 14, "long_bike_cap": 330,
           "long_run_cap": 150, "taper": [0.65, 0.45, 0.30]},
}
PHASES = [("base", 0.30), ("development", 0.25), ("specific", 0.28), ("peak", 0.17)]
MAX_RATE = 0.10
DELOAD = 0.65
LONG_SHARE = 0.60
COLUMNS = ["week", "week_start", "iso_week", "phase", "type", "minutes", "hours",
           "long_bike_min", "long_run_min", "brick", "test", "milestone"]


def monday(d):
    return d - timedelta(days=d.weekday())


def round5(x):
    return int(x / 5 + 0.5) * 5


def floor5(x):
    return int(x // 5) * 5


def split_phases(build_weeks):
    raw = [build_weeks * share for _, share in PHASES]
    counts = [max(1, int(r)) for r in raw]
    by_remainder = sorted(range(len(raw)), key=lambda i: raw[i] - int(raw[i]), reverse=True)
    i = 0
    while sum(counts) < build_weeks:
        counts[by_remainder[i % len(counts)]] += 1
        i += 1
    while sum(counts) > build_weeks:
        counts[counts.index(max(counts))] -= 1
    phases = []
    for (name, _), count in zip(PHASES, counts):
        phases += [name] * count
    return phases


def build(start_hours, start_date, race_date, fmt, available_hours=None,
          long_bike=None, long_run=None):
    spec = FORMATS[fmt]
    taper = spec["taper"]
    start = monday(start_date)
    total = (monday(race_date) - start).days // 7 + 1
    n_build = total - len(taper)
    if n_build < 4:
        raise ValueError(
            f"only {total} weeks before the race: too short to build a ramp for format {fmt}")

    warnings = []
    if total < spec["min_weeks"]:
        warnings.append(
            f"{total} weeks is under the minimum of {spec['min_weeks']} for format {fmt}: "
            "the goal is risky, aim to finish and consider a later or shorter race")

    cap = spec["plateau_h"] * 60
    if available_hours is not None:
        cap = min(cap, floor5(available_hours * 60))
    first = floor5(start_hours * 60)
    if first > cap:
        warnings.append(
            "starting volume is above the plateau: the plan holds the plateau, it does not ramp")
        first = cap

    # Load and recovery weeks: L L L D repeating, never a recovery week
    # right before the taper.
    offset = 1 if n_build % 4 == 0 else 0
    types = ["deload" if (i + offset) % 4 == 3 else "load" for i in range(n_build)]
    phases = split_phases(n_build)
    dev_end = max(i for i, p in enumerate(phases) if p == "development")

    def is_step(i):
        return i > 0 and types[i] == "load" and types[i - 1] == "load"

    steps = sum(1 for i in range(dev_end + 1) if is_step(i))
    needed = (cap / first) ** (1 / steps) - 1 if steps and cap > first else 0.0
    rate = min(MAX_RATE, needed)

    # Weekly minutes. Exact compounding is kept aside so rounding never
    # stalls the ramp; the displayed value never rises more than 10 percent.
    minutes, exact, shown = [], float(first), first
    for i in range(n_build):
        if types[i] == "deload":
            minutes.append(round5(DELOAD * shown))
            continue
        if is_step(i):
            exact = min(cap, exact * (1 + rate))
            shown = min(round5(exact), floor5(shown * (1 + MAX_RATE)))
        minutes.append(shown)
    peak = shown

    if peak < cap:
        advice = ("aim only to finish, or pick a later or shorter race"
                  if fmt in ("70.3", "IM") else "aim to finish, not for a time")
        warnings.append(
            f"even at +10 percent a week the ramp peaks at {peak / 60:.1f} h, under the "
            f"plateau of {cap / 60:.1f} h: the goal is risky, {advice}")
    else:
        reached = minutes.index(cap)
        if reached > dev_end:
            warnings.append(
                f"the plateau is reached in week {reached + 1}, after the development "
                "phase: fewer weeks at full volume than the format calls for")

    # Long sessions: step on load weeks while both fit in the week.
    steps_fn = {"long_bike_min": lambda v: v + 15,
                "long_run_min": lambda v: v + min(10, v // 10)}
    caps = {"long_bike_min": spec["long_bike_cap"], "long_run_min": spec["long_run_cap"]}
    current = {}
    for key, value in (("long_bike_min", long_bike), ("long_run_min", long_run)):
        if value is None:
            warnings.append(f"{key} not computed: the last long session is missing")
        else:
            current[key] = min(value, caps[key])
    if sum(current.values()) > LONG_SHARE * first:
        warnings.append(
            "the long sessions already take more than 60 percent of the week: "
            "they are held until the weekly volume catches up")
    longs = {key: [] for key in current}
    for i in range(n_build):
        if types[i] == "deload":
            for key in current:
                longs[key].append(round5(DELOAD * current[key]))
            continue
        if is_step(i):
            candidate = {k: min(caps[k], steps_fn[k](v)) for k, v in current.items()}
            if sum(candidate.values()) <= LONG_SHARE * minutes[i]:
                current = candidate
        for key in current:
            longs[key].append(current[key])

    weeks = []
    deloads = 0
    last_specific_load = max(
        (i for i in range(n_build) if phases[i] == "specific" and types[i] == "load"),
        default=None)
    for i in range(total):
        week_start = start + timedelta(weeks=i)
        iso = week_start.isocalendar()
        row = {
            "week": i + 1,
            "week_start": week_start.isoformat(),
            "iso_week": f"{iso[0]}-S{iso[1]:02d}",
            "brick": "", "test": "", "milestone": "",
            "long_bike_min": "", "long_run_min": "",
        }
        if i < n_build:
            row.update(phase=phases[i], type=types[i], minutes=minutes[i])
            for key, values in longs.items():
                row[key] = values[i]
            ends_block = i + 1 == n_build or types[i + 1] == "deload"
            if types[i] == "deload":
                deloads += 1
                if deloads == 1:
                    row["test"] = "deferred initial"
                else:
                    row["test"] = "run+swim" if deloads % 2 else "bike+swim"
            elif phases[i] in ("specific", "peak"):
                row["brick"] = "weekly"
            elif ends_block:
                row["brick"] = "light"
            if i == 0:
                row["test"] = "initial bike+swim"
            elif i == 1 and types[i] == "load":
                row["test"] = "initial run"
            if i == last_specific_load:
                row["milestone"] = "rehearsal"
        else:
            k = i - n_build
            is_race = i == total - 1
            row.update(phase="taper", type="race" if is_race else "taper",
                       minutes=round5(taper[k] * peak))
            if is_race:
                row["milestone"] = "race"
            else:
                for key, last in current.items():
                    row[key] = round5(taper[k] * last)
        row["hours"] = round(row["minutes"] / 60, 2)
        weeks.append(row)

    return {
        "format": fmt,
        "weeks_total": total,
        "race_date": race_date.isoformat(),
        "plateau_hours": round(cap / 60, 2),
        "weekly_rate_pct": round(rate * 100, 1),
        "total_hours": round(sum(w["minutes"] for w in weeks) / 60, 1),
        "warnings": warnings,
        "weeks": weeks,
    }


def to_csv(plan):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows({k: w[k] for k in COLUMNS} for w in plan["weeks"])
    return buffer.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--start-hours", type=float, required=True,
                        help="hours really done in the last complete, normal week")
    parser.add_argument("--start-date", type=date.fromisoformat, required=True,
                        help="first day of the plan, YYYY-MM-DD (moved to its Monday)")
    parser.add_argument("--race-date", type=date.fromisoformat, required=True)
    parser.add_argument("--format", choices=FORMATS, required=True, dest="fmt")
    parser.add_argument("--available-hours", type=float,
                        help="most hours per week the athlete can really give")
    parser.add_argument("--long-bike-min", type=int, help="last long ride, minutes")
    parser.add_argument("--long-run-min", type=int, help="last long run, minutes")
    parser.add_argument("--output-format", choices=["json", "csv"], default="json")
    parser.add_argument("--output", help="write to this file instead of stdout")
    args = parser.parse_args(argv)

    if args.start_hours < 0.5:
        parser.error("--start-hours must be at least 0.5")
    try:
        plan = build(args.start_hours, args.start_date, args.race_date, args.fmt,
                     args.available_hours, args.long_bike_min, args.long_run_min)
    except ValueError as error:
        sys.exit(f"error: {error}")

    if args.output_format == "csv":
        text = to_csv(plan)
        for warning in plan["warnings"]:
            print(f"warning: {warning}", file=sys.stderr)
    else:
        text = json.dumps(plan, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
