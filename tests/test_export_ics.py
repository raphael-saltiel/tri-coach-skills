import copy
import unittest

from helpers import load_script

ics = load_script("tri-semaine", "export_ics")

STAMP = "20261111T120000Z"
RUN = {
    "id": "2026-S49-2", "date": "2026-12-01", "time": "18:45", "duration_min": 60,
    "discipline": "run", "discipline_label": "course", "title": "Seuil 3x8 min",
    "location": "Piste du stade, Brumeval", "distance": "9 km",
    "lines": ["15 min d'échauffement en aisance", "3x8 min allure seuil, 3 min de trot",
              "10 min de retour au calme"],
    "why": "Cette séance élève l'allure que tu tiens longtemps ; le piège est de partir "
           "trop vite sur le premier bloc, la réussite est un troisième bloc aussi rapide.",
    "fallback": "Si la piste est fermée : même séance sur une route plate.",
}
REST = {"id": "2026-S49-0", "date": "2026-11-30", "discipline": "rest",
        "title": "Repos complet", "why": "Semaine de charge, 5 h 20 prévues."}


def calendar(*sessions, **extra):
    data = {"sessions": [copy.deepcopy(s) for s in sessions], **extra}
    return ics.build_calendar(data, STAMP)


def unfold(text):
    return text.replace("\r\n ", "").split("\r\n")


class FormatTest(unittest.TestCase):
    def setUp(self):
        self.text, problems = calendar(RUN, REST)
        self.assertEqual(problems, [])

    def test_lines_are_75_octets_at_most(self):
        for line in self.text.split("\r\n"):
            self.assertLessEqual(len(line.encode("utf-8")), 75, line)

    def test_crlf_everywhere(self):
        self.assertTrue(self.text.endswith("\r\n"))
        self.assertNotIn("\n", self.text.replace("\r\n", ""))
        self.assertNotIn("\r", self.text.replace("\r\n", ""))

    def test_folding_is_reversible(self):
        lines = unfold(self.text)
        description = next(l for l in lines if l.startswith("DESCRIPTION:DISCIPLINE: course"))
        self.assertIn(ics.escape(RUN["why"]), description)
        self.assertIn("\\n---\\n", description)

    def test_description_order(self):
        text = ics.description(RUN)
        rows = text.split("\n")
        self.assertEqual(rows[0], "DISCIPLINE: course")
        self.assertEqual(rows[1], "DISTANCE: 9 km")
        self.assertTrue(all(r.startswith("- ") for r in rows[2:5]))
        self.assertEqual(rows[5], "---")
        self.assertEqual(rows[6:], [RUN["why"], RUN["fallback"]])

    def test_structure(self):
        lines = unfold(self.text)
        self.assertEqual(lines[0], "BEGIN:VCALENDAR")
        self.assertEqual(lines[-2], "END:VCALENDAR")
        self.assertEqual(lines.count("BEGIN:VEVENT"), 2)
        self.assertEqual(lines.count("END:VEVENT"), 2)
        self.assertIn("DTSTART:20261201T184500", lines)
        self.assertIn("DTEND:20261201T194500", lines)
        self.assertIn("LOCATION:Piste du stade\\, Brumeval", lines)

    def test_all_day_event(self):
        lines = unfold(self.text)
        self.assertIn("DTSTART;VALUE=DATE:20261130", lines)
        self.assertIn("DTEND;VALUE=DATE:20261201", lines)
        self.assertIn("TRANSP:TRANSPARENT", lines)

    def test_events_sorted_by_date(self):
        lines = unfold(self.text)
        self.assertLess(lines.index("UID:2026-S49-0@tri-coach-skills"),
                        lines.index("UID:2026-S49-2@tri-coach-skills"))

    def test_title_has_emoji_and_fits(self):
        summaries = [l for l in unfold(self.text) if l.startswith("SUMMARY:")]
        self.assertEqual(summaries[1], "SUMMARY:\U0001F3C3 Seuil 3x8 min")
        self.assertTrue(all(len(s) - len("SUMMARY:") <= 40 for s in summaries))

    def test_default_and_custom_reminders(self):
        lines = unfold(self.text)
        self.assertEqual(lines.count("TRIGGER:-PT1440M"), 1)
        self.assertEqual(lines.count("TRIGGER:-PT45M"), 1)
        all_day = dict(REST, reminders_min=[900])
        text, _ = calendar(all_day)
        self.assertEqual([l for l in unfold(text) if l.startswith("TRIGGER")], ["TRIGGER:-PT900M"])
        custom = dict(RUN, reminders_min=[720])
        text, _ = calendar(custom)
        self.assertEqual([l for l in unfold(text) if l.startswith("TRIGGER")], ["TRIGGER:-PT720M"])


class StableIdTest(unittest.TestCase):
    def test_same_id_gives_same_uid_after_a_change(self):
        first, _ = calendar(RUN)
        moved = dict(RUN, date="2026-12-02", title="Seuil 3x10 min")
        second, _ = calendar(moved)
        uid = [l for l in unfold(first) if l.startswith("UID:")]
        self.assertEqual(uid, ["UID:2026-S49-2@tri-coach-skills"])
        self.assertEqual(uid, [l for l in unfold(second) if l.startswith("UID:")])

    def test_two_exports_are_identical_with_same_stamp(self):
        self.assertEqual(calendar(RUN, REST)[0], calendar(RUN, REST)[0])

    def test_duplicate_ids_are_refused(self):
        _, problems = calendar(RUN, RUN)
        self.assertTrue(any("used twice" in p for p in problems))


class RulesTest(unittest.TestCase):
    def problems(self, **changes):
        return calendar(dict(RUN, **changes))[1]

    def test_valid_session_has_no_problem(self):
        self.assertEqual(self.problems(), [])

    def test_five_lines_refused(self):
        self.assertTrue(any("maximum 4" in p for p in self.problems(lines=["10 min"] * 5)))

    def test_line_must_start_with_a_quantity(self):
        problems = self.problems(lines=["Échauffement de 15 min"])
        self.assertTrue(any("quantity" in p for p in problems))

    def test_line_length(self):
        self.assertTrue(any("maximum 45" in p for p in self.problems(lines=["1" * 46])))

    def test_title_length_counts_the_emoji(self):
        self.assertEqual(self.problems(title="x" * 38), [])
        self.assertTrue(any("maximum 40" in p for p in self.problems(title="x" * 39)))

    def test_missing_fields(self):
        self.assertTrue(any("location" in p for p in self.problems(location="")))
        self.assertTrue(any("why" in p for p in self.problems(why="")))
        self.assertTrue(any("fallback" in p for p in self.problems(fallback="")))
        self.assertTrue(any("duration_min" in p for p in self.problems(duration_min=None)))

    def test_dashes_refused(self):
        self.assertTrue(any("dash" in p for p in self.problems(why="Un test \N{EM DASH} raté.")))

    def test_unknown_discipline(self):
        self.assertTrue(any("unknown discipline" in p for p in self.problems(discipline="yoga")))


class FoldTest(unittest.TestCase):
    def test_multibyte_characters_are_never_split(self):
        line = "DESCRIPTION:" + "é\U0001F3C3" * 40
        parts = ics.fold(line)
        self.assertGreater(len(parts), 1)
        for part in parts:
            self.assertLessEqual(len(part.encode("utf-8")), 75)
        self.assertEqual(parts[0] + "".join(p[1:] for p in parts[1:]), line)


if __name__ == "__main__":
    unittest.main()
