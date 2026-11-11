# Examples

One fictional athlete, Camille, preparing a fictional olympic-distance race, played through the skills at two equipment levels. Every name, place and number is invented. The files are in French because the skills write in the athlete's language.

| Folder | Equipment | What it shows |
|---|---|---|
| `niveau-1/` | no measurement | profile, effort-only zones, plan, week 1 with level 1 benchmarks and a swim test deferred by the base gate |
| `niveau-3/` | power on the home trainer, heart rate outdoors, pace on the run | profile, measured zones after the first tests, plan, week 3 with sessions in watts indoors and heart rate outdoors |

In each folder: `profile.md` (tri-onboarding), `zones.md` (tri-tests), `plan.md` and `plan.csv` (tri-plan), `semaines/` (tri-semaine) with the week file, the JSON passed to the export script and the resulting `.ics`.

`plan.csv` and the `.ics` files are the exact output of the scripts: `tests/test_examples.py` regenerates them and compares.
