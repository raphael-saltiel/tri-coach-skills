# Zone model

Five zones. The percentages below are what `scripts/zones.py` applies. Use them by hand only when no script can run.

## Effort zones (level 1, always valid)

| Zone | Name | RPE (1 to 10) | Talk test |
|---|---|---|---|
| 1 | recovery | 1 to 2 | can sing or chat without effort |
| 2 | endurance | 3 to 4 | full sentences, breathing audible but calm |
| 3 | tempo | 5 to 6 | short sentences only |
| 4 | threshold | 7 to 8 | a few words at a time |
| 5 | VO2max | 9 | single words |

## Measured zones

| Zone | Bike power, percent of threshold power | Bike heart rate, percent of bike threshold | Run heart rate, percent of run threshold | Run pace, percent of threshold pace (time per km) | Swim pace, seconds per 100 m added to the 1000 m pace |
|---|---|---|---|---|---|
| 1 | under 56 | under 81 | under 85 | slower than 129 | slower than +15 |
| 2 | 56 to 75 | 81 to 89 | 85 to 89 | 114 to 129 | +8 to +15 |
| 3 | 76 to 90 | 90 to 93 | 90 to 94 | 106 to 113 | +3 to +8 |
| 4 | 91 to 105 | 94 to 99 | 95 to 99 | 99 to 105 | -2 to +3 |
| 5 | 106 to 120 | 100 to 106 | 100 to 106 | 90 to 98 | -8 to -2 |

Threshold power is 95 percent of the 20 minute average. Bike power zones use the common Coggan percentages. Heart-rate and run-pace zones use Joe Friel's threshold percentages. The swim offsets are a convention of this pack, built on the 1000 m pace.

The endurance ceiling is the top of zone 2. An endurance zone has a ceiling, not a floor: the lower bound is only a landmark.

## Estimated zones (before any test)

With the highest heart rate the athlete has really observed, the script takes run threshold as 85 percent of it and bike threshold as 82 percent. These factors are a convention of this pack, chosen low on purpose: an estimated ceiling that is too low costs nothing, one that is too high turns every easy session into a hard one. They are replaced at the first test. Never use an age formula as if it were a measurement.

Power and pace are never estimated: they wait for a test.

## Expected gains between two retests (about eight weeks apart)

Defaults of this pack for a beginner, always labelled "estimated":

| Retest | Bike threshold power | Run threshold pace | Swim 1000 m time |
|---|---|---|---|
| first | +6 percent | 3 percent faster | 3 percent faster |
| second | +4 percent | 2 percent faster | 2 percent faster |
| third | +3 percent | 2 percent faster | 2 percent faster |
| later | +2 percent | 1 percent faster | 1 percent faster |

These are starting assumptions, not norms. From the first retest, replace the default with what the athlete really gained, reduced a little for each later retest: gains shrink as fitness rises.

## Verdict

Compare the result with the expected value. Within 2.5 percent either way: on track. Better by more than 2.5 percent: ahead. Worse by more than 2.5 percent: behind. For times and paces, lower is better.

The first retest decides the time goal. A goal revised downwards is not a failure of the preparation.
