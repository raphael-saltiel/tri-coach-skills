import argparse
import unittest

from helpers import load_script

zones = load_script("tri-tests", "zones")


def args(**overrides):
    base = dict(ftp=None, test_20min_power=None, bike_lthr=None, run_lthr=None,
                run_threshold_pace=None, swim_1000=None, max_hr=None)
    base.update(overrides)
    return argparse.Namespace(**base)


class ZonesTest(unittest.TestCase):
    def test_effort_zones_always_present(self):
        out = zones.build_zones(args())
        self.assertEqual(len(out["effort"]), 5)
        self.assertEqual(out["status"], {})
        self.assertNotIn("bike_power", out)

    def test_power_from_20_minute_test(self):
        out = zones.build_zones(args(test_20min_power=205))
        self.assertEqual(out["ftp_w"], 195)
        endurance = out["bike_power"][1]
        self.assertEqual((endurance["low"], endurance["high"]), (109, 146))
        self.assertEqual(out["endurance_ceiling"]["bike_power_w"], 146)
        self.assertEqual(out["status"]["bike_power"], "measured")

    def test_recovery_zone_has_no_floor(self):
        out = zones.build_zones(args(ftp=195, run_lthr=168))
        self.assertIsNone(out["bike_power"][0]["low"])
        self.assertIsNone(out["run_hr"][0]["low"])

    def test_zones_do_not_overlap_and_increase(self):
        out = zones.build_zones(args(ftp=195, run_lthr=168, bike_lthr=158))
        for key in ("bike_power", "run_hr", "bike_hr"):
            previous_high = 0
            for zone in out[key]:
                if zone["low"] is not None:
                    self.assertGreater(zone["low"], previous_high)
                self.assertGreater(zone["high"], previous_high)
                previous_high = zone["high"]

    def test_run_pace_zones(self):
        out = zones.build_zones(args(run_threshold_pace=320))
        endurance = out["run_pace"][1]
        self.assertEqual(endurance["fastest"], "6:05")
        self.assertEqual(endurance["slowest"], "6:53")
        self.assertIsNone(out["run_pace"][0]["slowest"])
        self.assertEqual(out["endurance_ceiling"]["run_pace_fastest"], "6:05")

    def test_swim_pace_from_1000(self):
        out = zones.build_zones(args(swim_1000=1500))
        self.assertEqual(out["swim_test_pace"], "2:30")
        self.assertEqual(out["swim_pace"][1]["fastest"], "2:38")
        self.assertEqual(out["swim_pace"][1]["slowest"], "2:45")

    def test_max_hr_gives_estimated_and_cautious_zones(self):
        estimated = zones.build_zones(args(max_hr=186))
        measured = zones.build_zones(args(run_lthr=168))
        self.assertEqual(estimated["status"]["run_hr"], "estimated")
        self.assertLess(estimated["endurance_ceiling"]["run_hr_bpm"],
                        measured["endurance_ceiling"]["run_hr_bpm"])

    def test_measured_threshold_wins_over_max_hr(self):
        out = zones.build_zones(args(run_lthr=168, max_hr=186))
        self.assertEqual(out["status"]["run_hr"], "measured")
        self.assertEqual(out["status"]["bike_hr"], "estimated")

    def test_parse_time(self):
        self.assertEqual(zones.parse_time("5:20"), 320)
        self.assertEqual(zones.parse_time("1:02:03"), 3723)
        with self.assertRaises(argparse.ArgumentTypeError):
            zones.parse_time("abc")


class VerdictTest(unittest.TestCase):
    def verdict(self, expected, measured, lower=False):
        return zones.build_verdict(argparse.Namespace(
            expected=expected, measured=measured, lower_is_better=lower))["verdict"]

    def test_band_is_two_and_a_half_percent(self):
        self.assertEqual(self.verdict(200, 205), "on_track")
        self.assertEqual(self.verdict(200, 195), "on_track")
        self.assertEqual(self.verdict(200, 206), "ahead")
        self.assertEqual(self.verdict(200, 194), "behind")

    def test_lower_is_better_for_times(self):
        self.assertEqual(self.verdict(1500, 1450, lower=True), "ahead")
        self.assertEqual(self.verdict(1500, 1550, lower=True), "behind")
        self.assertEqual(self.verdict(1500, 1520, lower=True), "on_track")


if __name__ == "__main__":
    unittest.main()
