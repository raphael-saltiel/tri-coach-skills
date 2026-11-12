# Data files in `athlete/intervals/`

Written by this skill, read by tri-bilan. Same shape whichever route produced them.

## `activities.json`

```json
{
  "activities": [
    {"id": "i1", "start_date_local": "2026-12-01T18:45:00", "type": "Run",
     "name": "Threshold", "moving_time": 2460, "distance": 6600.0,
     "average_heartrate": 161, "average_speed": 2.683, "pace_per_km": "6:13",
     "source": "GARMIN_CONNECT", "device_name": "watch"}
  ],
  "ignored": [
    {"id": "i4", "start_date_local": "2026-12-05T09:00:40",
     "reason": "same session as i3, recorded by another device"},
    {"id": "9001", "start_date_local": "2026-12-02T19:15:00",
     "reason": "came through Strava: not readable through the API"}
  ],
  "minutes_by_sport": {"run": 51, "bike": 123}
}
```

Times are in seconds, distances in metres, speeds in metres per second. `minutes_by_sport` counts each session once.

## `activity-<id>.json`

The summary of one activity and its `intervals` (laps or blocks), each with `type` (WORK or RECOVERY), `moving_time`, `distance`, `average_watts`, `average_heartrate`, `average_speed`, `average_cadence`, and `pace_per_km` for a run. This is what a debrief of a session with blocks needs.

## `wellness.json`

`{"days": [...]}`, one object per day with only: `id` (the date), `ctl` (fitness), `atl` (fatigue), `rampRate`, `restingHR`, `hrv`, `sleepSecs`, `sleepScore`, `readiness`. No weight, no food, no medical measurement.

## `workouts.json` (input of `push`)

```json
{
  "workouts": [
    {"id": "2026-S49-3", "date": "2026-12-03", "time": "18:30", "sport": "VirtualRide",
     "name": "2x8 min tempo", "duration_min": 40, "indoor": true,
     "description": "- 12m 60%\n2x\n- 8m 90%\n- 4m 50%\n- 8m 50%"}
  ]
}
```

`id` is the session id of the week file. `sport` is one of `Ride`, `VirtualRide`, `Run`, `Swim`, `OpenWaterSwim`, `WeightTraining`. `description` is the workout text of `workout-text.md`.

When the data came from the connector, save the same fields under the same names, and leave out anything the connector did not give.
