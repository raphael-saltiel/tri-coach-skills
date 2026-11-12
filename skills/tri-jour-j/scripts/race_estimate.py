#!/usr/bin/env python3
"""Race-day time estimate for a triathlon. Standard library only.

Examples:
  race_estimate.py --format M --swim-pace 2:45 --bike-elevation-m 480 \
      --bike-power 156 --height-cm 172 --weight-kg 68 --position hoods \
      --run-endurance-pace 6:45 --start 09:30 \
      --cutoff-swim 1:00:00 --cutoff-bike 3:15:00 --cutoff-finish 4:30:00

  Without a power meter, give a recent solo ride instead of --bike-power:
      --ref-ride-km 38 --ref-ride-elevation-m 300 --ref-ride-time 1:40:00

Model:
  swim   pool pace per 100 m, plus 6 percent in open water
  bike   steady-state physics (air drag, rolling resistance, gravity) on the
         real elevation gain, half the distance climbing and half descending,
         CdA from body surface area and riding position
  run    endurance pace plus a fade per km that depends on the format
  T1/T2  defaults by format

The real bike elevation gain is required: a course is never assumed flat.
Output is JSON: time per leg, finish time, margin on each cut-off, levers
ranked by time gained, and every assumption used. Body weight is an input
of the physics, never a lever.
"""
import argparse
import json
import math
import sys

FORMATS = {
    "S": {"swim_m": 750, "bike_km": 20, "run_km": 5, "t1_s": 240, "t2_s": 180, "run_fade_s": 15},
    "M": {"swim_m": 1500, "bike_km": 40, "run_km": 10, "t1_s": 300, "t2_s": 180, "run_fade_s": 30},
    "70.3": {"swim_m": 1900, "bike_km": 90, "run_km": 21.1, "t1_s": 420, "t2_s": 300,
             "run_fade_s": 60},
    "IM": {"swim_m": 3800, "bike_km": 180, "run_km": 42.2, "t1_s": 600, "t2_s": 480,
           "run_fade_s": 90},
}
# CdA = body surface area x factor, by riding position.
POSITION_FACTOR = {"hoods": 0.19, "drops": 0.165, "aero": 0.145}
BETTER_POSITION = {"hoods": "drops", "drops": "aero"}
GRAVITY = 9.81
AIR_DENSITY = 1.2
ROLLING = 0.005
DRIVETRAIN = 0.975
OPEN_WATER_PENALTY = 0.06
DEFAULT_BMI = 22.5


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
    return f"{seconds // 3600}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def body_surface(height_cm, weight_kg):
    """Du Bois formula, m2."""
    return 0.007184 * weight_kg ** 0.425 * height_cm ** 0.725


def speed(power, mass, cda, grade):
    """Steady speed in m/s for a power in watts on a constant grade."""
    angle = math.atan(grade)
    resist = mass * GRAVITY * (ROLLING * math.cos(angle) + math.sin(angle))
    target = power * DRIVETRAIN
    low, high = 0.1, 40.0
    for _ in range(60):
        mid = (low + high) / 2
        if resist * mid + 0.5 * AIR_DENSITY * cda * mid ** 3 < target:
            low = mid
        else:
            high = mid
    return low


def bike_time(power, km, gain_m, mass, cda, max_descent_kmh):
    """Seconds for a loop course: half climbing, half descending."""
    half = km * 1000 / 2
    grade = gain_m / half
    up = speed(power, mass, cda, grade)
    down = min(speed(power, mass, cda, -grade), max_descent_kmh / 3.6)
    return half / up + half / down


def power_from_ride(km, gain_m, seconds, mass, cda, max_descent_kmh):
    """Average power that explains a known ride, by bisection."""
    low, high = 20.0, 600.0
    if not bike_time(high, km, gain_m, mass, cda, max_descent_kmh) < seconds \
            < bike_time(low, km, gain_m, mass, cda, max_descent_kmh):
        raise ValueError("the reference ride cannot be explained by a power between 20 and 600 W")
    for _ in range(50):
        mid = (low + high) / 2
        if bike_time(mid, km, gain_m, mass, cda, max_descent_kmh) > seconds:
            low = mid
        else:
            high = mid
    return low


def estimate(p):
    """p: dict of resolved inputs. Returns seconds per leg."""
    swim_pace = p["swim_pace_s"] * (1 if p["pool_swim"] else 1 + OPEN_WATER_PENALTY)
    cda = body_surface(p["height_cm"], p["weight_kg"]) * POSITION_FACTOR[p["position"]]
    return {
        "swim": p["swim_m"] / 100 * swim_pace,
        "t1": p["t1_s"],
        "bike": bike_time(p["bike_power"], p["bike_km"], p["bike_elevation_m"],
                          p["weight_kg"] + p["bike_kg"], cda, p["max_descent_kmh"]),
        "t2": p["t2_s"],
        "run": p["run_km"] * (p["run_endurance_pace_s"] + p["run_fade_s"]),
    }


def build(args):
    spec = FORMATS[args.fmt]
    assumptions = {}

    weight = args.weight_kg
    if weight is None:
        weight = round(DEFAULT_BMI * (args.height_cm / 100) ** 2, 1)
        assumptions["weight_kg"] = f"{weight} (not given: estimated from height)"
    p = {
        "swim_m": args.swim_m or spec["swim_m"],
        "bike_km": args.bike_km or spec["bike_km"],
        "run_km": args.run_km or spec["run_km"],
        "t1_s": spec["t1_s"] if args.t1 is None else args.t1,
        "t2_s": spec["t2_s"] if args.t2 is None else args.t2,
        "run_fade_s": spec["run_fade_s"] if args.run_fade_s is None else args.run_fade_s,
        "swim_pace_s": args.swim_pace, "pool_swim": args.pool_swim,
        "height_cm": args.height_cm, "weight_kg": weight, "bike_kg": args.bike_kg,
        "position": args.position, "bike_elevation_m": args.bike_elevation_m,
        "max_descent_kmh": args.max_descent_kmh,
        "run_endurance_pace_s": args.run_endurance_pace,
    }
    cda = body_surface(p["height_cm"], weight) * POSITION_FACTOR[p["position"]]

    if args.bike_power is not None:
        p["bike_power"] = args.bike_power
    else:
        p["bike_power"] = round(power_from_ride(
            args.ref_ride_km, args.ref_ride_elevation_m, args.ref_ride_time,
            weight + args.bike_kg, cda, args.max_descent_kmh))
        assumptions["bike_power_w"] = (
            f"{p['bike_power']} (inferred from the reference ride, at that ride's effort)")

    legs = estimate(p)
    total = sum(legs.values())
    result = {
        "format": args.fmt,
        "segments": {name: {"seconds": round(s), "time": fmt_time(s)} for name, s in legs.items()},
        "total": {"seconds": round(total), "time": fmt_time(total)},
    }
    result["segments"]["bike"]["avg_speed_kmh"] = round(p["bike_km"] / legs["bike"] * 3600, 1)
    if args.start is not None:
        clock = (args.start + total) % 86400
        result["finish_clock"] = f"{int(clock // 3600):02d}:{int(clock % 3600 // 60):02d}"

    elapsed = {"swim": legs["swim"], "bike": legs["swim"] + legs["t1"] + legs["bike"],
               "finish": total}
    cutoffs = []
    for name in ("swim", "bike", "finish"):
        limit = getattr(args, f"cutoff_{name}")
        if limit is not None:
            margin = limit - elapsed[name]
            cutoffs.append({"name": name, "limit": fmt_time(limit),
                            "elapsed": fmt_time(elapsed[name]),
                            "margin_s": round(margin),
                            "margin": ("-" if margin < 0 else "") + fmt_time(abs(margin)),
                            "ok": margin >= 0})
    result["cutoffs"] = cutoffs

    def gain(**change):
        return round(total - sum(estimate({**p, **change}).values()))

    levers = [
        {"lever": "bike power +20 W", "gain_s": gain(bike_power=p["bike_power"] + 20)},
        {"lever": "swim 10 s per 100 m faster", "gain_s": gain(swim_pace_s=p["swim_pace_s"] - 10)},
    ]
    if p["position"] in BETTER_POSITION:
        better = BETTER_POSITION[p["position"]]
        levers.append({"lever": f"position: {better} instead of {p['position']}",
                       "gain_s": gain(position=better)})
    for lever in levers:
        lever["gain"] = fmt_time(lever["gain_s"])
    result["levers"] = sorted(levers, key=lambda l: l["gain_s"], reverse=True)

    assumptions.update({
        "cda_m2": round(cda, 3),
        "total_mass_kg": round(weight + args.bike_kg, 1),
        "rolling_resistance": ROLLING,
        "air_density": AIR_DENSITY,
        "drivetrain_efficiency": DRIVETRAIN,
        "bike_profile": "half the distance climbing, half descending, no wind",
        "max_descent_kmh": args.max_descent_kmh,
        "open_water_penalty": 0 if args.pool_swim else OPEN_WATER_PENALTY,
        "run_fade_s_per_km": p["run_fade_s"],
        "t1_s": p["t1_s"], "t2_s": p["t2_s"],
    })
    assumptions.setdefault("bike_power_w", round(p["bike_power"]))
    result["assumptions"] = assumptions
    return result


def clock_time(text):
    seconds = parse_time(text + ":00") if text.count(":") == 1 else parse_time(text)
    return seconds


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--format", choices=FORMATS, required=True, dest="fmt")
    parser.add_argument("--swim-m", type=float, help="swim distance if not the standard one")
    parser.add_argument("--bike-km", type=float, help="bike distance if not the standard one")
    parser.add_argument("--run-km", type=float, help="run distance if not the standard one")
    parser.add_argument("--swim-pace", type=parse_time, required=True,
                        help="pool pace per 100 m, m:ss (from the 1000 m test)")
    parser.add_argument("--pool-swim", action="store_true",
                        help="the race swims in a pool: no open-water penalty")
    parser.add_argument("--bike-elevation-m", type=float, required=True,
                        help="real elevation gain of the bike course, metres")
    parser.add_argument("--bike-power", type=float, help="planned race power, watts")
    parser.add_argument("--ref-ride-km", type=float, help="reference ride: distance")
    parser.add_argument("--ref-ride-elevation-m", type=float, help="reference ride: elevation gain")
    parser.add_argument("--ref-ride-time", type=parse_time, help="reference ride: moving time, h:mm:ss")
    parser.add_argument("--height-cm", type=float, required=True)
    parser.add_argument("--weight-kg", type=float,
                        help="optional: estimated from height when missing")
    parser.add_argument("--bike-kg", type=float, default=10.0,
                        help="bike, bottles and kit (default 10)")
    parser.add_argument("--position", choices=POSITION_FACTOR, required=True)
    parser.add_argument("--max-descent-kmh", type=float, default=45.0)
    parser.add_argument("--run-endurance-pace", type=parse_time, required=True,
                        help="pace per km at the endurance ceiling, m:ss")
    parser.add_argument("--run-fade-s", type=float,
                        help="seconds per km added to the endurance pace (default by format)")
    parser.add_argument("--t1", type=parse_time, help="m:ss (default by format)")
    parser.add_argument("--t2", type=parse_time, help="m:ss (default by format)")
    parser.add_argument("--start", type=clock_time, help="start time, HH:MM")
    parser.add_argument("--cutoff-swim", type=parse_time, help="h:mm:ss after the start")
    parser.add_argument("--cutoff-bike", type=parse_time, help="h:mm:ss after the start")
    parser.add_argument("--cutoff-finish", type=parse_time, help="h:mm:ss after the start")
    args = parser.parse_args(argv)

    ride = (args.ref_ride_km, args.ref_ride_elevation_m, args.ref_ride_time)
    if args.bike_power is None and None in ride:
        parser.error("give --bike-power, or the three --ref-ride-* values")
    if args.bike_power is not None and any(v is not None for v in ride):
        parser.error("give --bike-power or a reference ride, not both")
    try:
        result = build(args)
    except ValueError as error:
        sys.exit(f"error: {error}")
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
