# The estimate model

What `scripts/race_estimate.py` computes, what it assumes, and where each input comes from.

## Inputs, by equipment level

| Input | Level 3 | Level 2 | Level 1 |
|---|---|---|---|
| Swim pace per 100 m | 1000 m test | 1000 m test | 1000 m test with the wall clock. Before the test: the easy calibration pace, labelled "estimated" |
| Bike | race power = threshold power x the share below | a recent solo ride (distance, elevation gain, moving time) | same: distance from a map, time from a watch |
| Run pace at the endurance ceiling | long runs, pace at the ceiling heart rate | long runs with GPS, or a measured route | time on a measured route at talk-test effort |
| Height, position | profile | profile | profile |
| Weight, bike weight | profile, optional | same | same |
| Course: distances, elevation gain, cut-offs, start time | profile, with sources | same | same |

The reference ride must be solo, on roads like the race course, without long stops, at the effort the athlete can hold for the race duration. The script then answers: "at that effort, on the race course, the bike takes this long."

## Race power as a share of threshold power

Starting values of this pack for a beginner. They are conventions, to be replaced by what the athlete holds in the rehearsal and the long bricks.

| Format | Share of threshold power |
|---|---|
| S | 85 percent |
| M | 80 percent |
| 70.3 | 72 percent |
| Ironman | 65 percent |

## The legs

**Swim.** Distance x pool pace, plus 6 percent in open water (sighting, no walls, other swimmers). No penalty with `--pool-swim`. A wetsuit usually helps and a rough sea hurts: the model knows neither.

**Bike.** Steady-state physics. For a given power, the speed is the one where the power equals air drag plus rolling resistance plus gravity:

- half of the distance climbs at the average grade given by the elevation gain, the other half descends at the same grade,
- descending speed is capped (45 km/h by default) because a beginner brakes,
- total mass = rider + bike, bottles and kit (10 kg by default),
- drag area (CdA) = body surface area (from height and weight) x a factor for the position: 0.19 on the hoods, 0.165 in the drops, 0.145 on aero bars,
- rolling resistance 0.005, air density 1.2 kg/m3, drivetrain efficiency 97.5 percent,
- no wind, no drafting, no stops.

**Run.** Distance x (pace at the endurance ceiling + a fade per km): 15 s for a sprint, 30 s for an olympic, 60 s for a 70.3, 90 s for an Ironman. The fade is a cautious convention for a beginner running off the bike. Replace it with `--run-fade-s` once long bricks show the athlete's real figure.

**Transitions.** By format: 4 and 3 minutes (S), 5 and 3 (M), 7 and 5 (70.3), 10 and 8 (Ironman). Replace them with the times of the rehearsal.

## What the output contains

- Time per leg, total, finish time on the clock when `--start` is given.
- For each cut-off given: time elapsed at that point, margin, and whether it holds.
- Levers ranked by time gained: bike power +20 W, the next better position, swim 10 s per 100 m faster. Weight is never listed.
- Every assumption used, including what was estimated.

## Limits to tell the athlete

- It is a model. On a calm day, with honest inputs, expect the real bike time within several minutes of it on an olympic distance, more on longer races. Wind alone can move it by more than any lever.
- Averaging the climbs makes a course with a few very steep ramps look a little faster than it is. For such a course, add the note and keep a margin.
- The position factor assumes the position is held. A position the athlete cannot hold for the whole bike leg is not a gain: only count the one practised on the long rides.
- The run fade is the least certain figure before the first long bricks.
