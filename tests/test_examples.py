"""The examples are the real output of the scripts: regenerate and compare."""
import csv
import io
import json
import re
import unittest
from datetime import date

from helpers import ROOT, load_script

ramp = load_script("tri-plan", "ramp")
ics = load_script("tri-semaine", "export_ics")
EXAMPLES = ROOT / "examples"
WEEKS = {
    "niveau-1": ("2026-S47", "20261111T190000Z", 270),
    "niveau-3": ("2026-S49", "20261125T190000Z", 320),
}


class ExamplesTest(unittest.TestCase):
    def test_plan_csv_is_the_ramp_output(self):
        plan = ramp.build(4.5, date(2026, 11, 16), date(2027, 4, 25), "M",
                          available_hours=8, long_bike=90, long_run=50)
        for level in WEEKS:
            text = (EXAMPLES / level / "plan.csv").read_text(encoding="utf-8")
            self.assertEqual(text, ramp.to_csv(plan), level)

    def test_calendar_is_the_export_of_the_week(self):
        for level, (week, stamp, _) in WEEKS.items():
            folder = EXAMPLES / level / "semaines"
            data = json.loads((folder / f"{week}.json").read_text(encoding="utf-8"))
            text, problems = ics.build_calendar(data, stamp)
            self.assertEqual(problems, [], level)
            self.assertEqual((folder / f"{week}.ics").read_bytes(), text.encode("utf-8"), level)

    def test_week_file_and_calendar_input_agree(self):
        for level, (week, _, _) in WEEKS.items():
            folder = EXAMPLES / level / "semaines"
            data = json.loads((folder / f"{week}.json").read_text(encoding="utf-8"))
            blocks = re.split(r"^## ", (folder / f"{week}.md").read_text(encoding="utf-8"), flags=re.M)[1:]
            self.assertEqual(len(blocks), len(data["sessions"]), level)
            for block, session in zip(blocks, data["sessions"]):
                rows = block.splitlines()
                self.assertTrue(rows[0].startswith(session["id"] + " "), session["id"])
                self.assertTrue(rows[1].endswith(session["title"]), session["id"])
                self.assertEqual([r[2:] for r in rows if r.startswith("- ")],
                                 session.get("lines", []), session["id"])
                for key in ("location", "distance", "fallback"):
                    if session.get(key):
                        self.assertIn(session[key], block, session["id"])

    def test_week_total_matches_the_plan_within_five_percent(self):
        for level, (week, _, planned) in WEEKS.items():
            rows = list(csv.DictReader(io.StringIO(
                (EXAMPLES / level / "plan.csv").read_text(encoding="utf-8"))))
            row = next(r for r in rows if r["iso_week"] == week)
            self.assertEqual(int(row["minutes"]), planned)
            data = json.loads((EXAMPLES / level / "semaines" / f"{week}.json").read_text(encoding="utf-8"))
            total = sum(s.get("duration_min", 0) for s in data["sessions"])
            self.assertLessEqual(abs(total - planned), 0.05 * planned, level)


if __name__ == "__main__":
    unittest.main()
