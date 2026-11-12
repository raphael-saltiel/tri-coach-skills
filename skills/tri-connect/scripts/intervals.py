#!/usr/bin/env python3
"""Read training data from Intervals.icu and send planned workouts.
Standard library only.

Examples:
  intervals.py activities --oldest 2026-11-30 --newest 2026-12-06 \
      --output athlete/intervals/activities.json
  intervals.py activity i55751783 --output athlete/intervals/activity.json
  intervals.py wellness --oldest 2026-11-30 --output athlete/intervals/wellness.json
  intervals.py push --input workouts.json --dry-run

The API key is read from the INTERVALS_API_KEY environment variable. It is
never written to a file and never printed. With --dry-run the request is
printed with the key masked and nothing is sent.

What the commands keep:
  activities  one recording per session. Copies of the same session from
              another device are listed under "ignored", and so are
              activities that came through Strava: Intervals.icu does not
              expose them through its API.
  activity    the summary of one activity and its intervals (laps or blocks).
  wellness    fitness, fatigue and recovery fields only. No weight, no
              nutrition, no medical measurement is requested.
  push        planned workouts from a JSON file, written to the calendar.
              The same id always updates the same event.

Input for push:
  {"workouts": [{"id": "2026-S49-3", "date": "2026-12-03", "time": "18:30",
                 "sport": "VirtualRide", "name": "2x8 min tempo",
                 "duration_min": 40, "indoor": true,
                 "description": "- 12m 60%\\n2x\\n- 8m 90%\\n- 4m 50%\\n- 8m 50%"}]}
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

BASE = "https://intervals.icu/api/v1"
ENV_KEY = "INTERVALS_API_KEY"
UID_DOMAIN = "tri-coach-skills"
DUPLICATE_WINDOW_S = 300

ACTIVITY_FIELDS = [
    "id", "start_date_local", "type", "name", "moving_time", "elapsed_time", "distance",
    "total_elevation_gain", "average_heartrate", "max_heartrate", "icu_average_watts",
    "icu_weighted_avg_watts", "average_speed", "average_cadence", "icu_training_load",
    "icu_rpe", "feel", "trainer", "source", "device_name"]
INTERVAL_FIELDS = [
    "type", "label", "moving_time", "distance", "average_watts", "average_heartrate",
    "max_heartrate", "average_speed", "average_cadence"]
WELLNESS_FIELDS = ["id", "ctl", "atl", "rampRate", "restingHR", "hrv", "sleepSecs",
                   "sleepScore", "readiness"]
SPORTS = {
    "Ride": "bike", "VirtualRide": "bike", "GravelRide": "bike", "MountainBikeRide": "bike",
    "EBikeRide": "bike", "Run": "run", "VirtualRun": "run", "TrailRun": "run",
    "Swim": "swim", "OpenWaterSwim": "swim"}
PUSH_SPORTS = ("Ride", "VirtualRide", "Run", "Swim", "OpenWaterSwim", "WeightTraining")


class ApiError(Exception):
    pass


def build_request(method, path, query=None, body=None):
    url = BASE + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    request = {"method": method, "url": url, "headers": {"Accept": "application/json"}}
    if body is not None:
        request["headers"]["Content-Type"] = "application/json"
        request["body"] = body
    return request


def masked(request):
    shown = dict(request, headers=dict(request["headers"], Authorization="Basic ***"))
    return json.dumps(shown, indent=2, ensure_ascii=False)


def send(request, key, opener=urllib.request.urlopen):
    token = base64.b64encode(f"API_KEY:{key}".encode()).decode()
    data = None
    if "body" in request:
        data = json.dumps(request["body"]).encode("utf-8")
    http = urllib.request.Request(
        request["url"], data=data, method=request["method"],
        headers=dict(request["headers"], Authorization=f"Basic {token}"))
    try:
        with opener(http, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code in (401, 403):
            raise ApiError("Intervals.icu refused the key: check INTERVALS_API_KEY") from None
        if error.code == 429:
            wait = error.headers.get("Retry-After", "a few")
            raise ApiError(f"rate limit reached: retry in {wait} seconds") from None
        raise ApiError(f"Intervals.icu answered {error.code} for {request['url']}") from None
    except urllib.error.URLError as error:
        raise ApiError(f"cannot reach Intervals.icu: {error.reason}") from None


def pace_per_km(speed):
    if not speed:
        return None
    seconds = round(1000 / speed)
    return f"{seconds // 60}:{seconds % 60:02d}"


def start_seconds(activity):
    return datetime.fromisoformat(activity["start_date_local"]).timestamp()


def filled(activity):
    return sum(1 for value in activity.values() if value is not None)


def sort_activities(raw, prefer=()):
    """Keep one recording per session; list what was set aside and why."""
    ignored, readable = [], []
    for activity in raw:
        if activity.get("source") == "STRAVA" or "type" not in activity:
            ignored.append({"id": activity.get("id"),
                            "start_date_local": activity.get("start_date_local"),
                            "reason": "came through Strava: not readable through the API"})
        else:
            readable.append(activity)

    def rank(activity):
        source = activity.get("source")
        position = prefer.index(source) if source in prefer else len(prefer)
        return (position, -filled(activity))

    kept = []
    for activity in sorted(readable, key=start_seconds):
        sport = SPORTS.get(activity["type"], activity["type"])
        twin = next((k for k in kept
                     if SPORTS.get(k["type"], k["type"]) == sport
                     and abs(start_seconds(k) - start_seconds(activity)) <= DUPLICATE_WINDOW_S),
                    None)
        if twin is None:
            kept.append(activity)
            continue
        best, copy = sorted((twin, activity), key=rank)
        kept[kept.index(twin)] = best
        ignored.append({"id": copy["id"], "start_date_local": copy["start_date_local"],
                        "reason": f"same session as {best['id']}, recorded by another device"})

    minutes = {}
    for activity in kept:
        sport = SPORTS.get(activity["type"], "other")
        minutes[sport] = minutes.get(sport, 0) + round((activity.get("moving_time") or 0) / 60)
        if sport == "run":
            activity["pace_per_km"] = pace_per_km(activity.get("average_speed"))
    return {"activities": kept, "ignored": ignored, "minutes_by_sport": minutes}


def trim_activity(raw):
    """Summary and intervals of one activity, with only the fields a review needs."""
    if raw.get("source") == "STRAVA" or "type" not in raw:
        raise ApiError("this activity came through Strava: Intervals.icu does not expose it")
    out = {field: raw.get(field) for field in ACTIVITY_FIELDS}
    is_run = SPORTS.get(raw["type"]) == "run"
    if is_run:
        out["pace_per_km"] = pace_per_km(raw.get("average_speed"))
    out["intervals"] = []
    for interval in raw.get("icu_intervals") or []:
        row = {field: interval.get(field) for field in INTERVAL_FIELDS}
        if is_run:
            row["pace_per_km"] = pace_per_km(interval.get("average_speed"))
        out["intervals"].append(row)
    return out


def workout_events(data):
    """Turn the push input into calendar events; raise on a bad workout."""
    workouts = data.get("workouts")
    if not workouts:
        raise ApiError("no workouts in the input")
    events = []
    for index, workout in enumerate(workouts):
        label = workout.get("id") or f"workout {index + 1}"
        for field in ("id", "date", "sport", "name"):
            if not workout.get(field):
                raise ApiError(f"{label}: missing '{field}'")
        if workout["sport"] not in PUSH_SPORTS:
            raise ApiError(f"{label}: sport must be one of {', '.join(PUSH_SPORTS)}")
        try:
            start = datetime.fromisoformat(f"{workout['date']}T{workout.get('time', '00:00')}:00")
        except ValueError:
            raise ApiError(f"{label}: date must be YYYY-MM-DD and time HH:MM") from None
        event = {"category": "WORKOUT", "uid": f"{workout['id']}@{UID_DOMAIN}",
                 "start_date_local": start.isoformat(), "type": workout["sport"],
                 "name": workout["name"]}
        if workout.get("description"):
            event["description"] = workout["description"]
        if workout.get("duration_min"):
            event["moving_time"] = int(workout["duration_min"]) * 60
        if "indoor" in workout:
            event["indoor"] = bool(workout["indoor"])
        events.append(event)
    return events


def run(args, opener=urllib.request.urlopen, environ=os.environ):
    if args.command == "activities":
        query = {"oldest": args.oldest, "fields": ",".join(ACTIVITY_FIELDS)}
        if args.newest:
            query["newest"] = args.newest
        request = build_request("GET", "/athlete/0/activities", query)
        shape = lambda raw: sort_activities(raw, tuple(args.prefer.split(",")) if args.prefer else ())
    elif args.command == "activity":
        request = build_request("GET", f"/activity/{args.id}", {"intervals": "true"})
        shape = trim_activity
    elif args.command == "wellness":
        query = {"oldest": args.oldest, "fields": ",".join(WELLNESS_FIELDS)}
        if args.newest:
            query["newest"] = args.newest
        request = build_request("GET", "/athlete/0/wellness", query)
        shape = lambda raw: {"days": raw}
    else:
        with open(args.input, encoding="utf-8") as handle:
            events = workout_events(json.load(handle))
        request = build_request("POST", "/athlete/0/events/bulk",
                                {"upsertOnUid": "true", "updatePlanApplied": "false"}, events)
        shape = lambda raw: {"sent": len(raw), "events": [
            {key: event.get(key) for key in ("id", "uid", "name", "start_date_local")}
            for event in raw]}

    if args.dry_run:
        return masked(request) + "\n"
    key = environ.get(ENV_KEY)
    if not key:
        raise ApiError(f"{ENV_KEY} is not set. Put the key in your environment, "
                       "never in a file of this folder and never in a conversation.")
    return json.dumps(shape(send(request, key, opener)), indent=2, ensure_ascii=False) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dry-run", action="store_true",
                        help="print the request with the key masked, send nothing")
    common.add_argument("--output", help="write the result to this file instead of stdout")
    sub = parser.add_subparsers(dest="command", required=True)

    activities = sub.add_parser("activities", parents=[common], help="list activities")
    activities.add_argument("--oldest", required=True, help="YYYY-MM-DD")
    activities.add_argument("--newest", help="YYYY-MM-DD, default now")
    activities.add_argument("--prefer",
                            help="sources to keep first when a session was recorded twice, "
                                 "comma separated, for example GARMIN_CONNECT,ZWIFT")
    activity = sub.add_parser("activity", parents=[common], help="one activity with intervals")
    activity.add_argument("id")
    wellness = sub.add_parser("wellness", parents=[common], help="fitness and recovery by day")
    wellness.add_argument("--oldest", required=True, help="YYYY-MM-DD")
    wellness.add_argument("--newest", help="YYYY-MM-DD")
    push = sub.add_parser("push", parents=[common], help="send planned workouts")
    push.add_argument("--input", required=True, help="JSON file of workouts")
    args = parser.parse_args(argv)

    try:
        text = run(args)
    except (ApiError, OSError, json.JSONDecodeError) as error:
        sys.exit(f"error: {error}")
    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
