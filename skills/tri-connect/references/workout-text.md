# Workout text for Intervals.icu

Intervals.icu turns a plain-text description into a structured workout that it can send to a trainer app or a watch. Syntax read on the official workout builder thread of the Intervals.icu forum (12 November 2026). Use only the forms below, and look at the preview in Intervals.icu after the first send.

## The forms

| Form | Example |
|---|---|
| A step starts with a hyphen | `- 20m 60%` |
| Duration | `30s`, `10m`, `1m30` |
| Percent of threshold power | `- 10m 85%` |
| Watts | `- 10m 175w` |
| A range | `- 10m 80-90%` |
| A ramp | `- 15m Ramp 50-75%` |
| Cadence | `- 20m 60% 90-100rpm` |
| Percent of threshold heart rate | `- 20m 85% LTHR` |
| A zone, by power or by heart rate | `- 60m Z2`, `- 60m Z2 HR` |
| A repeat: a line with the count, then its steps | `3x` |
| A section header: a line without a hyphen | `Warmup`, `Cooldown` |
| A prompt: text before the duration | `- Recovery 30s 50%` |

## From a session to a workout

Session from the week file:

```
- 12 min d'échauffement de 100 à 145 W
- 2x8 min à 175 W, cadence 85 à 95
- 4 min à 100 W entre les deux blocs
- 8 min de retour au calme sous 110 W
```

Workout text, in percent of a threshold power of 195 W:

```
Warmup
- 12m Ramp 50-75%

2x
- 8m 90% 85-95rpm
- 4m 50%

Cooldown
- 8m 50%
```

- Prefer percentages to watts: the workout stays right when the threshold changes, as long as the same threshold is set in Intervals.icu, in the trainer app and in `athlete/zones.md`.
- Heart-rate steps suit steady efforts. Do not write short blocks by heart rate: on short blocks, heart rate is a witness.
- Outdoor rides without a power meter are not written in watts or percent of power.
- Run pace steps and swim steps: check the current syntax on the Intervals.icu forum before using them. If in doubt, send the run by heart-rate zone or keep it in the calendar only.
