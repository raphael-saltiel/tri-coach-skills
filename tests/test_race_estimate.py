import contextlib
import io
import json
import unittest

from helpers import load_script

race = load_script("tri-jour-j", "race_estimate")

BASE = ["--format", "M", "--swim-pace", "2:45", "--height-cm", "172", "--weight-kg", "68",
        "--position", "hoods", "--run-endurance-pace", "6:45"]
COURSES = {"flat": 100, "hilly": 480, "mountain": 1100}


def run(*extra, base=BASE):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        race.main([*base, *extra])
    return json.loads(out.getvalue())


def course(name, power=156, *extra):
    return run("--bike-elevation-m", str(COURSES[name]), "--bike-power", str(power), *extra)


def bike(result):
    return result["segments"]["bike"]["seconds"]


class ThreeCoursesTest(unittest.TestCase):
    def test_more_elevation_is_slower(self):
        times = [bike(course(name)) for name in ("flat", "hilly", "mountain")]
        self.assertEqual(times, sorted(times))
        self.assertEqual(len(set(times)), 3)

    def test_more_power_is_faster_on_every_course(self):
        for name in COURSES:
            with self.subTest(course=name):
                times = [bike(course(name, power)) for power in (120, 156, 190, 230)]
                self.assertEqual(times, sorted(times, reverse=True))
                self.assertEqual(len(set(times)), 4)

    def test_speeds_are_plausible(self):
        expected = {"flat": (27, 33), "hilly": (23, 29), "mountain": (15, 22)}
        for name, (low, high) in expected.items():
            with self.subTest(course=name):
                speed = course(name)["segments"]["bike"]["avg_speed_kmh"]
                self.assertTrue(low < speed < high, speed)

    def test_total_is_the_sum_of_the_legs(self):
        for name in COURSES:
            result = course(name)
            legs = sum(leg["seconds"] for leg in result["segments"].values())
            self.assertLessEqual(abs(legs - result["total"]["seconds"]), 3)

    def test_power_matters_more_as_the_course_climbs(self):
        gains = []
        for name in ("flat", "hilly", "mountain"):
            levers = {l["lever"]: l["gain_s"] for l in course(name)["levers"]}
            gains.append(levers["bike power +20 W"])
        self.assertEqual(gains, sorted(gains))


class ModelTest(unittest.TestCase):
    def test_better_position_is_faster(self):
        times = []
        for position in ("hoods", "drops", "aero"):
            base = [position if v == "hoods" else v for v in BASE]
            times.append(bike(run("--bike-elevation-m", "100", "--bike-power", "156", base=base)))
        self.assertEqual(times, sorted(times, reverse=True))
        self.assertEqual(len(set(times)), 3)

    def test_heavier_is_slower_uphill(self):
        light = bike(course("mountain"))
        heavy = bike(course("mountain", 156, "--bike-kg", "14"))
        self.assertGreater(heavy, light)

    def test_open_water_penalty(self):
        open_water = course("flat")["segments"]["swim"]["seconds"]
        pool = course("flat", 156, "--pool-swim")["segments"]["swim"]["seconds"]
        self.assertEqual(pool, 15 * 165)
        self.assertAlmostEqual(open_water / pool, 1.06, places=2)

    def test_run_is_endurance_pace_plus_the_fade(self):
        self.assertEqual(course("flat")["segments"]["run"]["seconds"], 10 * (405 + 30))
        slower = course("flat", 156, "--run-fade-s", "60")
        self.assertEqual(slower["segments"]["run"]["seconds"], 10 * (405 + 60))

    def test_taller_rider_has_more_drag(self):
        tall = [v if v != "172" else "195" for v in BASE]
        self.assertGreater(run("--bike-elevation-m", "100", "--bike-power", "156",
                               base=tall)["assumptions"]["cda_m2"],
                           course("flat")["assumptions"]["cda_m2"])

    def test_missing_weight_is_estimated_and_flagged(self):
        base = [v for v in BASE if v not in ("--weight-kg", "68")]
        result = run("--bike-elevation-m", "480", "--bike-power", "156", base=base)
        self.assertIn("estimated from height", result["assumptions"]["weight_kg"])

    def test_elevation_is_required(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            run("--bike-power", "156")


class ReferenceRideTest(unittest.TestCase):
    def test_round_trip(self):
        seconds = bike(course("hilly", 140))
        time = race.fmt_time(seconds)
        result = run("--bike-elevation-m", "480", "--ref-ride-km", "40",
                     "--ref-ride-elevation-m", "480", "--ref-ride-time", time)
        self.assertIn("inferred", result["assumptions"]["bike_power_w"])
        self.assertLessEqual(abs(bike(result) - seconds), 30)

    def test_power_or_ride_is_required_but_not_both(self):
        for extra in ([], ["--bike-power", "150", "--ref-ride-km", "40",
                           "--ref-ride-elevation-m", "300", "--ref-ride-time", "1:40:00"]):
            with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
                run("--bike-elevation-m", "480", *extra)

    def test_impossible_ride_is_an_error(self):
        with self.assertRaises(SystemExit):
            run("--bike-elevation-m", "480", "--ref-ride-km", "40",
                "--ref-ride-elevation-m", "300", "--ref-ride-time", "0:20:00")


class CutoffsAndLeversTest(unittest.TestCase):
    def test_margins_and_finish_clock(self):
        result = course("hilly", 156, "--start", "09:30", "--cutoff-swim", "1:00:00",
                        "--cutoff-bike", "2:00:00", "--cutoff-finish", "4:30:00")
        by_name = {c["name"]: c for c in result["cutoffs"]}
        self.assertTrue(by_name["swim"]["ok"])
        self.assertFalse(by_name["bike"]["ok"])
        self.assertTrue(by_name["bike"]["margin"].startswith("-"))
        self.assertEqual(by_name["finish"]["margin_s"], 4 * 3600 + 1800 - result["total"]["seconds"])
        total = result["total"]["seconds"]
        clock = 9 * 3600 + 1800 + total
        self.assertEqual(result["finish_clock"], f"{clock // 3600:02d}:{clock % 3600 // 60:02d}")

    def test_levers_are_ranked_and_weight_is_never_one(self):
        result = course("hilly")
        gains = [l["gain_s"] for l in result["levers"]]
        self.assertEqual(gains, sorted(gains, reverse=True))
        self.assertTrue(all(g > 0 for g in gains))
        names = " ".join(l["lever"] for l in result["levers"])
        self.assertNotIn("weight", names)
        self.assertNotIn("kg", names)
        self.assertEqual(len(result["levers"]), 3)

    def test_no_position_lever_when_already_on_aero_bars(self):
        base = ["aero" if v == "hoods" else v for v in BASE]
        result = run("--bike-elevation-m", "480", "--bike-power", "156", base=base)
        self.assertEqual(len(result["levers"]), 2)

    def test_formats_have_standard_distances(self):
        for fmt, km in (("S", 5), ("M", 10), ("70.3", 21.1), ("IM", 42.2)):
            base = [fmt if v == "M" else v for v in BASE]
            result = run("--bike-elevation-m", "300", "--bike-power", "150", base=base)
            fade = race.FORMATS[fmt]["run_fade_s"]
            self.assertEqual(result["segments"]["run"]["seconds"], round(km * (405 + fade)))


if __name__ == "__main__":
    unittest.main()
