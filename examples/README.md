# Examples

One fictional athlete, Camille, preparing a fictional olympic-distance race, played through the skills at two equipment levels. Every name, place and number is invented. The files are in French because the skills write in the athlete's language.

| Folder | Equipment | What it shows |
|---|---|---|
| `niveau-1/` | no measurement | profile, effort-only zones, plan, week 1 with level 1 benchmarks and a swim test deferred by the base gate, a debrief from a story, a race estimate from a reference ride with a thin cut-off margin |
| `niveau-3/` | power on the home trainer, heart rate outdoors, pace on the run | profile, measured zones after the first tests, plan, week 3 with sessions in watts indoors and heart rate outdoors, a debrief from data, a race estimate from power |

In each folder:

| File | Written by |
|---|---|
| `profile.md` | tri-onboarding |
| `zones.md` | tri-tests |
| `plan.md`, `plan.csv` | tri-plan |
| `semaines/` (week file, JSON passed to the export script, `.ics`) | tri-semaine, with the strength sessions of tri-renfo |
| `journal.md`, and `bilan.md` (one debrief written out in full) | tri-bilan |
| `nutrition.md` | tri-nutrition |
| `jour-j.md`, `jour-j.json` | tri-jour-j |

`plan.csv`, the `.ics` files and `jour-j.json` are the exact output of the scripts: `tests/test_examples.py` regenerates them and compares.
