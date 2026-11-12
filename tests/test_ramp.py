import csv
import io
import unittest
from datetime import date

from helpers import load_script

ramp = load_script("tri-plan", "ramp")

CASES = {
    "12 weeks": dict(start_hours=3, start_date=date(2027, 1, 4), race_date=date(2027, 3, 28),
                     fmt="M", long_bike=60, long_run=40),
    "24 weeks": dict(start_hours=5, start_date=date(2026, 11, 16), race_date=date(2027, 5, 2),
                     fmt="70.3", long_bike=105, long_run=60),
    "32 weeks": dict(start_hours=7, start_date=date(2026, 11, 16), race_date=date(2027, 6, 27),
                     fmt="70.3", long_bike=120, long_run=70),
}
EXPECTED_WEEKS = {"12 weeks": 12, "24 weeks": 24, "32 weeks": 32}


class RampRulesTest(unittest.TestCase):
    def each_case(self):
        for name, kwargs in CASES.items():
            with self.subTest(case=name):
                yield name, kwargs, ramp.build(**kwargs)

    def test_week_count_and_first_week(self):
        for name, kwargs, plan in self.each_case():
            self.assertEqual(plan["weeks_total"], EXPECTED_WEEKS[name])
            self.assertEqual(plan["weeks"][0]["minutes"], kwargs["start_hours"] * 60)
            self.assertEqual(plan["weeks"][0]["type"], "load")

    def test_never_more_than_ten_percent_between_load_weeks(self):
        for _, _, plan in self.each_case():
            weeks = plan["weeks"]
            for previous, current in zip(weeks, weeks[1:]):
                if previous["type"] == current["type"] == "load":
                    self.assertLessEqual(current["minutes"], previous["minutes"] * 1.10)
                    self.assertGreaterEqual(current["minutes"], previous["minutes"])

    def test_exactly_ten_percent_when_start_is_too_low(self):
        plan = ramp.build(**CASES["12 weeks"])
        self.assertEqual(plan["weekly_rate_pct"], 10.0)
        weeks = plan["weeks"]
        for previous, current in zip(weeks, weeks[1:]):
            if previous["type"] == current["type"] == "load":
                self.assertGreater(current["minutes"], previous["minutes"] * 1.10 - 5)
        self.assertTrue(any("risky" in w for w in plan["warnings"]))

    def test_smoothed_rate_when_time_allows(self):
        plan = ramp.build(**CASES["32 weeks"])
        self.assertLess(plan["weekly_rate_pct"], 10.0)
        self.assertEqual(plan["warnings"], [])
        build = [w for w in plan["weeks"] if w["phase"] in ("base", "development")]
        self.assertEqual(max(w["minutes"] for w in build), 11 * 60)

    def test_recovery_week_is_minus_35_percent(self):
        for _, _, plan in self.each_case():
            weeks = plan["weeks"]
            for previous, current in zip(weeks, weeks[1:]):
                if current["type"] == "deload":
                    self.assertEqual(previous["type"], "load")
                    self.assertLessEqual(abs(current["minutes"] - 0.65 * previous["minutes"]), 2.5)

    def test_three_load_weeks_out_of_four(self):
        for _, _, plan in self.each_case():
            run_length, deloads = 0, 0
            for week in plan["weeks"]:
                if week["type"] == "load":
                    run_length += 1
                    self.assertLessEqual(run_length, 3)
                elif week["type"] == "deload":
                    deloads += 1
                    run_length = 0
            self.assertGreaterEqual(deloads, 2)

    def test_load_resumes_at_previous_peak_after_recovery(self):
        for _, _, plan in self.each_case():
            weeks = plan["weeks"]
            for i in range(1, len(weeks) - 1):
                if weeks[i]["type"] == "deload" and weeks[i + 1]["type"] == "load":
                    self.assertEqual(weeks[i + 1]["minutes"], weeks[i - 1]["minutes"])

    def test_plateau_never_exceeded(self):
        for _, _, plan in self.each_case():
            for week in plan["weeks"]:
                self.assertLessEqual(week["minutes"], plan["plateau_hours"] * 60)

    def test_taper_present_and_decreasing(self):
        for _, kwargs, plan in self.each_case():
            taper_weeks = [w for w in plan["weeks"] if w["phase"] == "taper"]
            self.assertEqual(len(taper_weeks), len(ramp.FORMATS[kwargs["fmt"]]["taper"]))
            self.assertEqual(taper_weeks[-1]["type"], "race")
            self.assertEqual(taper_weeks[-1]["milestone"], "race")
            before = [w for w in plan["weeks"] if w["phase"] != "taper"][-1]
            self.assertEqual(before["type"], "load")
            minutes = [before["minutes"]] + [w["minutes"] for w in taper_weeks]
            self.assertEqual(minutes, sorted(minutes, reverse=True))
            self.assertLess(taper_weeks[0]["minutes"], 0.7 * before["minutes"])

    def test_race_week_contains_race_date(self):
        for _, kwargs, plan in self.each_case():
            start = date.fromisoformat(plan["weeks"][-1]["week_start"])
            self.assertEqual(start.weekday(), 0)
            self.assertTrue(0 <= (kwargs["race_date"] - start).days <= 6)

    def test_long_sessions(self):
        for _, kwargs, plan in self.each_case():
            spec = ramp.FORMATS[kwargs["fmt"]]
            weeks = [w for w in plan["weeks"] if w["phase"] != "taper"]
            for previous, current in zip(weeks, weeks[1:]):
                self.assertLessEqual(current["long_bike_min"], spec["long_bike_cap"])
                self.assertLessEqual(current["long_run_min"], spec["long_run_cap"])
                if current["type"] == "deload":
                    self.assertLess(current["long_run_min"], previous["long_run_min"])
                elif previous["type"] == "load":
                    self.assertLessEqual(current["long_bike_min"] - previous["long_bike_min"], 15)
                    step = current["long_run_min"] - previous["long_run_min"]
                    self.assertLessEqual(step, min(10, previous["long_run_min"] // 10))
                    self.assertGreaterEqual(step, 0)
                if current["type"] == "load" and current["long_bike_min"] > kwargs["long_bike"]:
                    total = current["long_bike_min"] + current["long_run_min"]
                    self.assertLessEqual(total, 0.6 * current["minutes"])

    def test_tests_sit_on_recovery_weeks_and_alternate(self):
        for _, _, plan in self.each_case():
            deloads = [w for w in plan["weeks"] if w["type"] == "deload"]
            self.assertEqual(deloads[0]["test"], "deferred initial")
            retests = [w["test"] for w in deloads[1:]]
            self.assertTrue(all(t in ("bike+swim", "run+swim") for t in retests))
            self.assertTrue(all(a != b for a, b in zip(retests, retests[1:])))
            self.assertEqual(plan["weeks"][0]["test"], "initial bike+swim")
            for week in plan["weeks"]:
                if week["type"] in ("taper", "race"):
                    self.assertEqual(week["test"], "")

    def test_phases_in_order(self):
        order = ["base", "development", "specific", "peak", "taper"]
        for _, _, plan in self.each_case():
            seen = [w["phase"] for w in plan["weeks"]]
            self.assertEqual(seen, sorted(seen, key=order.index))
            self.assertEqual(set(seen), set(order))


class RampEdgeCasesTest(unittest.TestCase):
    def test_available_hours_cap_the_plateau(self):
        plan = ramp.build(4, date(2026, 11, 16), date(2027, 5, 2), "70.3", available_hours=7)
        self.assertEqual(plan["plateau_hours"], 7.0)
        self.assertEqual(max(w["minutes"] for w in plan["weeks"]), 420)

    def test_start_above_plateau_holds_the_plateau(self):
        plan = ramp.build(9, date(2026, 11, 16), date(2027, 3, 28), "S")
        self.assertEqual(plan["weeks"][0]["minutes"], 360)
        self.assertTrue(any("above the plateau" in w for w in plan["warnings"]))

    def test_under_minimum_weeks_warns(self):
        plan = ramp.build(6, date(2027, 1, 4), date(2027, 3, 28), "IM")
        self.assertTrue(any("under the minimum" in w for w in plan["warnings"]))

    def test_too_short_is_an_error(self):
        with self.assertRaises(ValueError):
            ramp.build(5, date(2027, 3, 1), date(2027, 3, 28), "M")

    def test_missing_long_sessions_are_reported_not_invented(self):
        plan = ramp.build(5, date(2026, 11, 16), date(2027, 5, 2), "M")
        self.assertEqual(plan["weeks"][0]["long_bike_min"], "")
        self.assertEqual(sum("not computed" in w for w in plan["warnings"]), 2)

    def test_start_date_moves_to_monday(self):
        plan = ramp.build(5, date(2026, 11, 18), date(2027, 5, 2), "M")
        self.assertEqual(plan["weeks"][0]["week_start"], "2026-11-16")

    def test_csv_has_one_row_per_week(self):
        plan = ramp.build(**CASES["24 weeks"])
        rows = list(csv.DictReader(io.StringIO(ramp.to_csv(plan))))
        self.assertEqual(len(rows), 24)
        self.assertEqual(list(rows[0].keys()), ramp.COLUMNS)


if __name__ == "__main__":
    unittest.main()
