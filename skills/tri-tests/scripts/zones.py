#!/usr/bin/env python3
"""Training zones and test verdicts for triathlon. Standard library only.

Examples:
  zones.py zones --test-20min-power 200 --run-lthr 168 \
      --run-threshold-pace 5:20 --swim-1000 25:00
  zones.py zones --max-hr 186
  zones.py verdict --expected 190 --measured 196
  zones.py verdict --expected 25:00 --measured 24:10 --lower-is-better

Output is JSON on stdout. Effort zones (level 1) are always present.
Heart-rate zones need a measured threshold, or --max-hr for a cautious
estimate flagged "estimated". Power and pace zones need a measured test.
"""
import argparse
import json
import sys

ZONE_NAMES = ["recovery", "endurance", "tempo", "threshold", "vo2max"]

EFFORT = [
    ("1-2", "can sing or chat without effort"),
    ("3-4", "full sentences, breathing audible but calm"),
    ("5-6", "short sentences only"),
    ("7-8", "a few words at a time"),
    ("9", "single words"),
]

# Percent of the threshold value, (low, high) per zone. None means open.
BIKE_POWER_PCT = [(None, 55), (56, 75), (76, 90), (91, 105), (106, 120)]
BIKE_HR_PCT = [(None, 80), (81, 89), (90, 93), (94, 99), (100, 106)]
RUN_HR_PCT = [(None, 84), (85, 89), (90, 94), (95, 99), (100, 106)]
# Percent of threshold pace as time per km, (fast side, slow side):
# a higher percent is a slower pace.
RUN_PACE_PCT = [(129, None), (114, 129), (106, 113), (99, 105), (90, 98)]
# Seconds per 100 m added to the 1000 m test pace: (slow side, fast side).
SWIM_OFFSET_S = [(None, 15), (15, 8), (8, 3), (3, -2), (-2, -8)]

# Cautious threshold estimates from an observed maximum heart rate.
EST_RUN_LTHR = 0.85
EST_BIKE_LTHR = 0.82

VERDICT_BAND_PCT = 2.5


def parse_time(text):
    """'m:ss' or 'h:mm:ss' to seconds."""
    parts = text.split(":")
    if not 2 <= len(parts) <= 3 or not all(p.isdigit() for p in parts):
        raise argparse.ArgumentTypeError(f"expected m:ss or h:mm:ss, got {text!r}")
    seconds = 0
    for part in parts:
        seconds = seconds * 60 + int(part)
    return seconds


def fmt_time(seconds):
    seconds = int(round(seconds))
    return f"{seconds // 60}:{seconds % 60:02d}"


def pct_zones(threshold, table, unit):
    zones = []
    for i, (low, high) in enumerate(table):
        zones.append({
            "zone": i + 1,
            "name": ZONE_NAMES[i],
            "low": None if low is None else round(threshold * low / 100),
            "high": round(threshold * high / 100),
            "unit": unit,
        })
    return zones


def run_pace_zones(threshold_s):
    zones = []
    for i, (fast_pct, slow_pct) in enumerate(RUN_PACE_PCT):
        zones.append({
            "zone": i + 1,
            "name": ZONE_NAMES[i],
            "slowest": None if slow_pct is None else fmt_time(threshold_s * slow_pct / 100),
            "fastest": fmt_time(threshold_s * fast_pct / 100),
            "unit": "min/km",
        })
    return zones


def swim_pace_zones(pace_100_s):
    zones = []
    for i, (slow, fast) in enumerate(SWIM_OFFSET_S):
        zones.append({
            "zone": i + 1,
            "name": ZONE_NAMES[i],
            "slowest": None if slow is None else fmt_time(pace_100_s + slow),
            "fastest": fmt_time(pace_100_s + fast),
            "unit": "min/100m",
        })
    return zones


def build_zones(args):
    out = {
        "effort": [
            {"zone": i + 1, "name": ZONE_NAMES[i], "rpe": rpe, "talk_test": talk}
            for i, (rpe, talk) in enumerate(EFFORT)
        ],
        "status": {},
        "endurance_ceiling": {
            "note": "An endurance zone has a ceiling, not a floor.",
            "rpe": "4",
        },
    }
    ceiling = out["endurance_ceiling"]

    ftp = args.ftp
    if args.test_20min_power is not None:
        ftp = round(args.test_20min_power * 0.95)
    if ftp is not None:
        out["ftp_w"] = ftp
        out["bike_power"] = pct_zones(ftp, BIKE_POWER_PCT, "W")
        out["status"]["bike_power"] = "measured"
        ceiling["bike_power_w"] = out["bike_power"][1]["high"]

    for key, measured, factor, table in (
        ("bike_hr", args.bike_lthr, EST_BIKE_LTHR, BIKE_HR_PCT),
        ("run_hr", args.run_lthr, EST_RUN_LTHR, RUN_HR_PCT),
    ):
        if measured is not None:
            lthr, status = measured, "measured"
        elif args.max_hr is not None:
            lthr, status = round(args.max_hr * factor), "estimated"
        else:
            continue
        out[key] = pct_zones(lthr, table, "bpm")
        out[key.replace("_hr", "_lthr_bpm")] = lthr
        out["status"][key] = status
        ceiling[key + "_bpm"] = out[key][1]["high"]

    if args.run_threshold_pace is not None:
        out["run_pace"] = run_pace_zones(args.run_threshold_pace)
        out["run_threshold_pace"] = fmt_time(args.run_threshold_pace)
        out["status"]["run_pace"] = "measured"
        ceiling["run_pace_fastest"] = out["run_pace"][1]["fastest"]

    if args.swim_1000 is not None:
        pace = args.swim_1000 / 10
        out["swim_pace"] = swim_pace_zones(pace)
        out["swim_test_pace"] = fmt_time(pace)
        out["status"]["swim_pace"] = "measured"
        ceiling["swim_pace_fastest"] = out["swim_pace"][1]["fastest"]

    return out


def parse_value(text):
    """A number, or a time as m:ss / h:mm:ss (returned in seconds)."""
    if ":" in text:
        return float(parse_time(text))
    try:
        return float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected a number or m:ss, got {text!r}")


def build_verdict(args):
    if args.expected <= 0:
        sys.exit("error: --expected must be positive")
    delta = (args.measured - args.expected) / args.expected * 100
    if args.lower_is_better:
        delta = -delta
    if delta > VERDICT_BAND_PCT:
        verdict = "ahead"
    elif delta < -VERDICT_BAND_PCT:
        verdict = "behind"
    else:
        verdict = "on_track"
    return {
        "expected": args.expected,
        "measured": args.measured,
        "progress_vs_expected_pct": round(delta, 1),
        "band_pct": VERDICT_BAND_PCT,
        "verdict": verdict,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    z = sub.add_parser("zones", help="compute zones from thresholds")
    power = z.add_mutually_exclusive_group()
    power.add_argument("--ftp", type=int, help="bike threshold power in watts")
    power.add_argument("--test-20min-power", type=float,
                       help="average watts of the 20 min test (threshold = 95 percent)")
    z.add_argument("--bike-lthr", type=int, help="bike threshold heart rate, bpm")
    z.add_argument("--run-lthr", type=int,
                   help="run threshold heart rate: average of the last 20 min of the 30 min test")
    z.add_argument("--run-threshold-pace", type=parse_time,
                   help="average pace of the 30 min test, m:ss per km")
    z.add_argument("--swim-1000", type=parse_time, help="1000 m test time, m:ss")
    z.add_argument("--max-hr", type=int,
                   help="highest heart rate actually observed; gives cautious estimated zones")

    v = sub.add_parser("verdict", help="compare a test result with its expected value")
    v.add_argument("--expected", type=parse_value, required=True)
    v.add_argument("--measured", type=parse_value, required=True)
    v.add_argument("--lower-is-better", action="store_true",
                   help="use for times and paces")

    args = parser.parse_args(argv)
    result = build_zones(args) if args.command == "zones" else build_verdict(args)
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
