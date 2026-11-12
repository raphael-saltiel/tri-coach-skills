"""intervals.py against simulated responses: no network call is ever made."""
import argparse
import base64
import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path

from helpers import load_script

icu = load_script("tri-connect", "intervals")
KEY = "test-key-not-real"

ACTIVITIES = [
    {"id": "i3", "start_date_local": "2026-12-05T09:02:10", "type": "Ride", "name": "Long ride",
     "moving_time": 7380, "distance": 44000.0, "average_heartrate": 134, "source": "UPLOAD",
     "device_name": "bike computer"},
    {"id": "i4", "start_date_local": "2026-12-05T09:00:40", "type": "Ride", "name": "Activity",
     "moving_time": 7500, "source": "OAUTH_CLIENT"},
    {"id": "i5", "start_date_local": "2026-12-05T11:06:00", "type": "Run", "name": "Brick run",
     "moving_time": 600, "distance": 1500.0, "average_speed": 2.5, "source": "GARMIN_CONNECT"},
    {"id": "i1", "start_date_local": "2026-12-01T18:45:00", "type": "Run", "name": "Threshold",
     "moving_time": 2460, "distance": 6600.0, "average_speed": 2.683, "source": "GARMIN_CONNECT"},
    {"id": "9001", "start_date_local": "2026-12-02T19:15:00", "source": "STRAVA",
     "_note": "STRAVA activities are not available via the API"},
]
ACTIVITY = {"id": "i1", "start_date_local": "2026-12-01T18:45:00", "type": "Run",
            "name": "Threshold", "moving_time": 2460, "distance": 6600.0, "average_speed": 2.683,
            "source": "GARMIN_CONNECT", "icu_ftp": 195, "weight": 68,
            "icu_intervals": [
                {"type": "WORK", "moving_time": 360, "distance": 1169.0, "average_speed": 3.247,
                 "average_heartrate": 163, "average_dfa_a1": 0.7},
                {"type": "RECOVERY", "moving_time": 120, "distance": 270.0, "average_speed": 2.25}]}


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self.payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class Recorder:
    """Stands in for urllib.request.urlopen and records what would be sent."""
    def __init__(self, payload=None, error=None):
        self.payload, self.error, self.calls = payload, error, []

    def __call__(self, request, timeout=None):
        self.calls.append(request)
        if self.error:
            raise self.error
        return FakeResponse(self.payload)


def args(command, **values):
    base = dict(command=command, dry_run=False, output=None, oldest="2026-11-30",
                newest="2026-12-06", prefer=None, id="i1", input=None)
    base.update(values)
    return argparse.Namespace(**base)


def call(namespace, payload=None, error=None, key=KEY):
    opener = Recorder(payload, error)
    environ = {icu.ENV_KEY: key} if key else {}
    text = icu.run(namespace, opener=opener, environ=environ)
    return text, opener


class RequestTest(unittest.TestCase):
    def test_activities_request(self):
        _, opener = call(args("activities"), ACTIVITIES)
        request = opener.calls[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertTrue(request.full_url.startswith(
            "https://intervals.icu/api/v1/athlete/0/activities?oldest=2026-11-30"))
        self.assertIn("newest=2026-12-06", request.full_url)
        expected = "Basic " + base64.b64encode(f"API_KEY:{KEY}".encode()).decode()
        self.assertEqual(request.get_header("Authorization"), expected)

    def test_wellness_asks_only_for_fitness_and_recovery_fields(self):
        _, opener = call(args("wellness"), [])
        url = opener.calls[0].full_url
        for private in ("weight", "bloodGlucose", "bodyFat", "kcal", "menstrual", "systolic"):
            self.assertNotIn(private, url)
        self.assertIn("restingHR", url)
        self.assertIn("ctl", url)

    def test_activity_request_asks_for_intervals(self):
        _, opener = call(args("activity"), ACTIVITY)
        self.assertEqual(opener.calls[0].full_url,
                         "https://intervals.icu/api/v1/activity/i1?intervals=true")


class DryRunTest(unittest.TestCase):
    def test_dry_run_sends_nothing_and_masks_the_key(self):
        text, opener = call(args("activities", dry_run=True), ACTIVITIES)
        self.assertEqual(opener.calls, [])
        shown = json.loads(text)
        self.assertEqual(shown["headers"]["Authorization"], "Basic ***")
        self.assertNotIn(KEY, text)
        self.assertNotIn(base64.b64encode(f"API_KEY:{KEY}".encode()).decode(), text)

    def test_dry_run_works_without_a_key(self):
        text, opener = call(args("wellness", dry_run=True), key=None)
        self.assertEqual(opener.calls, [])
        self.assertIn("/athlete/0/wellness", text)

    def test_missing_key_is_an_error_that_does_not_ask_for_it_in_chat(self):
        with self.assertRaises(icu.ApiError) as caught:
            call(args("activities"), ACTIVITIES, key=None)
        self.assertIn("never in a conversation", str(caught.exception))

    def test_the_key_never_reaches_the_output(self):
        text, _ = call(args("activities"), ACTIVITIES)
        self.assertNotIn(KEY, text)


class ActivitiesTest(unittest.TestCase):
    def setUp(self):
        text, _ = call(args("activities"), ACTIVITIES)
        self.result = json.loads(text)

    def test_strava_activities_are_set_aside_with_the_reason(self):
        strava = [i for i in self.result["ignored"] if i["id"] == "9001"]
        self.assertEqual(len(strava), 1)
        self.assertIn("Strava", strava[0]["reason"])
        self.assertNotIn("9001", [a["id"] for a in self.result["activities"]])

    def test_duplicate_recording_is_kept_once(self):
        kept = [a["id"] for a in self.result["activities"]]
        self.assertEqual(kept, ["i1", "i3", "i5"])
        copy = next(i for i in self.result["ignored"] if i["id"] == "i4")
        self.assertIn("same session as i3", copy["reason"])

    def test_preferred_source_wins_a_duplicate(self):
        text, _ = call(args("activities", prefer="OAUTH_CLIENT,UPLOAD"), ACTIVITIES)
        kept = [a["id"] for a in json.loads(text)["activities"]]
        self.assertIn("i4", kept)
        self.assertNotIn("i3", kept)

    def test_minutes_count_each_session_once(self):
        self.assertEqual(self.result["minutes_by_sport"], {"run": 41 + 10, "bike": 123})

    def test_a_run_right_after_a_ride_is_not_a_duplicate(self):
        self.assertIn("i5", [a["id"] for a in self.result["activities"]])

    def test_run_pace_is_added(self):
        run = next(a for a in self.result["activities"] if a["id"] == "i1")
        self.assertEqual(run["pace_per_km"], "6:13")


class ActivityTest(unittest.TestCase):
    def test_intervals_are_trimmed_to_review_fields(self):
        text, _ = call(args("activity"), ACTIVITY)
        result = json.loads(text)
        self.assertEqual(len(result["intervals"]), 2)
        work = result["intervals"][0]
        self.assertEqual(work["pace_per_km"], "5:08")
        self.assertEqual(work["average_heartrate"], 163)
        self.assertNotIn("average_dfa_a1", work)
        self.assertNotIn("weight", result)

    def test_strava_activity_is_refused(self):
        with self.assertRaises(icu.ApiError):
            call(args("activity"), {"id": "9001", "source": "STRAVA", "_note": "hidden"})


class PushTest(unittest.TestCase):
    def push(self, workouts, **extra):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "workouts.json"
            path.write_text(json.dumps({"workouts": workouts}), encoding="utf-8")
            reply = [{"id": 77, "uid": "2026-S49-3@tri-coach-skills", "name": "2x8 min tempo",
                      "start_date_local": "2026-12-03T18:30:00", "icu_training_load": 40}]
            return call(args("push", input=str(path), **extra), reply)

    WORKOUT = {"id": "2026-S49-3", "date": "2026-12-03", "time": "18:30", "sport": "VirtualRide",
               "name": "2x8 min tempo", "duration_min": 40, "indoor": True,
               "description": "- 12m 60%\n2x\n- 8m 90%\n- 4m 50%\n- 8m 50%"}

    def test_event_body_and_stable_uid(self):
        text, opener = self.push([self.WORKOUT])
        request = opener.calls[0]
        self.assertEqual(request.get_method(), "POST")
        self.assertIn("/athlete/0/events/bulk?upsertOnUid=true&updatePlanApplied=false",
                      request.full_url)
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(body, [{
            "category": "WORKOUT", "uid": "2026-S49-3@tri-coach-skills",
            "start_date_local": "2026-12-03T18:30:00", "type": "VirtualRide",
            "name": "2x8 min tempo", "description": self.WORKOUT["description"],
            "moving_time": 2400, "indoor": True}])
        self.assertEqual(json.loads(text)["sent"], 1)

    def test_moving_a_session_keeps_its_uid(self):
        moved = dict(self.WORKOUT, date="2026-12-04")
        first = json.loads(self.push([self.WORKOUT])[1].calls[0].data)[0]["uid"]
        second = json.loads(self.push([moved])[1].calls[0].data)[0]["uid"]
        self.assertEqual(first, second)

    def test_push_dry_run_shows_the_body_and_sends_nothing(self):
        text, opener = self.push([self.WORKOUT], dry_run=True)
        self.assertEqual(opener.calls, [])
        self.assertEqual(json.loads(text)["body"][0]["name"], "2x8 min tempo")

    def test_bad_workouts_are_refused_before_any_call(self):
        for broken in (dict(self.WORKOUT, sport="Yoga"), dict(self.WORKOUT, date="3 dec"),
                       {k: v for k, v in self.WORKOUT.items() if k != "name"}):
            with self.assertRaises(icu.ApiError):
                self.push([broken])
        with self.assertRaises(icu.ApiError):
            self.push([])


class ErrorsTest(unittest.TestCase):
    def error(self, code, headers=None):
        return urllib.error.HTTPError("https://intervals.icu", code, "error", headers or {},
                                      io.BytesIO(b""))

    def test_refused_key(self):
        with self.assertRaises(icu.ApiError) as caught:
            call(args("activities"), error=self.error(401))
        self.assertIn("refused the key", str(caught.exception))
        self.assertNotIn(KEY, str(caught.exception))

    def test_rate_limit_reports_the_wait(self):
        with self.assertRaises(icu.ApiError) as caught:
            call(args("activities"), error=self.error(429, {"Retry-After": "42"}))
        self.assertIn("42 seconds", str(caught.exception))

    def test_unreachable(self):
        with self.assertRaises(icu.ApiError):
            call(args("activities"), error=urllib.error.URLError("no route"))


if __name__ == "__main__":
    unittest.main()
