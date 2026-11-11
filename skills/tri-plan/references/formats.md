# Formats and ramp rules

## Parameters by format

| Format | Distances | Minimum weeks | Plateau | Long ride cap | Long run cap | Taper (share of the peak week) |
|---|---|---|---|---|---|---|
| S (sprint) | 750 m, 20 km, 5 km | 8 | 6 h | 90 min | 60 min | 2 weeks: 55 and 30 percent |
| M (olympic) | 1.5 km, 40 km, 10 km | 12 | 8 h | 150 min | 90 min | 2 weeks: 55 and 30 percent |
| 70.3 | 1.9 km, 90 km, 21.1 km | 16 | 11 h | 240 min | 120 min | 3 weeks: 65, 45 and 30 percent |
| IM (Ironman) | 3.8 km, 180 km, 42.2 km | 24 | 14 h | 330 min | 150 min | 3 weeks: 65, 45 and 30 percent |

These values are choices of this pack for a beginner whose goal is to finish well. They are not norms. The race week figure excludes the race itself.

- The plateau actually used is the smaller of the format plateau and the athlete's hours ceiling. The athlete's ceiling always wins.
- Sprint: most beginners will not reach 6 hours and must not aim for it.
- Ironman: 14 hours is a finisher's plateau, not a time-goal plateau.

## The ramp, step by step (what `scripts/ramp.py` does)

1. Count the weeks from the Monday of the start week to the race week included. Remove the taper weeks: the rest are build weeks. Fewer than four build weeks: no ramp is possible.
2. Mark the build weeks load, load, load, recovery, repeating, arranged so that the week before the taper is a load week.
3. Split the build weeks into base, development, specific and peak.
4. Week 1 = the starting hours. Plateau = min(format plateau, hours ceiling).
5. Rate = what is needed to reach the plateau at the end of the development phase, counting only the rises between two consecutive load weeks, and never more than 10 percent.
6. Each load week that follows a load week rises by that rate, without passing the plateau. A recovery week is 65 percent of the week before. The load week after a recovery week resumes at the previous peak.
7. Long ride +15 min and long run +10 percent or +10 min (the smaller), on the same weeks, up to the caps, and only if the two together stay under 60 percent of the week. Recovery weeks: 65 percent.
8. Taper weeks: the shares in the table, applied to the last load week.

Hours are rounded to five minutes, and the rounding never lets a rise pass 10 percent.

## Warnings and what to say

| Warning | What to tell the athlete |
|---|---|
| Weeks under the minimum for the format | The goal is risky. Aim only to finish, or choose a later or shorter race. |
| The ramp peaks under the plateau | Even at the fastest safe rate the volume stays short. Same two ways out. For a sprint or an olympic, finishing remains realistic: no time goal. |
| The plateau is reached after the development phase | Fewer weeks at full volume. Acceptable, the specific phase starts lighter. |
| Starting volume above the plateau | The plan holds the plateau. No ramp is needed. |
| Long sessions already over 60 percent of the week | They are held until the weekly volume catches up. |
| A long session not computed | A figure is missing in the profile. Ask for it. |

## Columns of `plan.csv`

`week` (1 to n), `week_start` (Monday), `iso_week`, `phase`, `type` (load, deload, taper, race), `minutes`, `hours`, `long_bike_min`, `long_run_min`, `brick` (light, weekly or empty), `test` (initial, deferred initial, bike+swim, run+swim or empty), `milestone` (rehearsal, race or empty).
