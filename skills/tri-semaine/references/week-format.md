# Week file and calendar format

## The week file

Path: `athlete/semaines/<iso week>.md`, for example `athlete/semaines/2026-S49.md`. Written in the athlete's language. It is the single source of truth: the calendar file is generated from it.

Structure:

1. A title line: week, dates, type (load, recovery, taper, race), planned hours.
2. The week note: phase, what matters this week, guardrails that apply, zones "estimated" if they are.
3. An overview table: day, session, duration.
4. One block per session, in date order, in exactly this shape:

```markdown
## 2026-S49-2 · mardi 1 décembre · 18:45 · 60 min
🏃 Seuil 3x8 min
LIEU: Piste du stade, Brumeval
DISCIPLINE: course
DISTANCE: 9 km
- 15 min d'échauffement en aisance
- 3x8 min à 5'15/km, 3 min de trot entre
- 10 min de retour au calme
---
Pourquoi : cette séance élève l'allure que tu tiens longtemps. Le piège est de partir trop vite sur le premier bloc. C'est réussi si le troisième bloc est aussi rapide que le premier.
Repli : si la piste est fermée, même séance sur une route plate, au ressenti 7 sur 10.
```

Rules for a block:

- Heading: the session id, the date, the start time, the duration. An all-day entry (rest day) has no time and no duration.
- Title line: the emoji of the sport, then the title. 40 characters at most, emoji and space included. 🏃 run, 🚴 bike, 🏊 swim, 🧘 strength, 😴 rest, 🏁 race.
- Location: always filled, except for a rest day.
- `DISCIPLINE:` in the athlete's language. `DISTANCE:` only when it means something (not for strength or rest), in km, or in m for the pool.
- Four instruction lines at most, each starting with a quantity, 45 characters at most.
- `---`, then the why paragraph and the fallback, each on its own line.
- A brick is one bike block whose last instruction line is the run.

The id is `<iso week>-<number>`. The rest day that opens the week is number 0. A session that moves keeps its id. A deleted session's id is never reused.

## From the week file to the calendar

Build this JSON from the week file, one object per block, and pass it to `scripts/export_ics.py`:

```json
{
  "calendar_name": "Entraînements",
  "default_reminders_min": [1440, 45],
  "sessions": [
    {
      "id": "2026-S49-0",
      "date": "2026-11-30",
      "discipline": "rest",
      "discipline_label": "repos",
      "title": "Repos complet",
      "why": "Semaine de charge, 5 h 20 prévues. Séance clé : le seuil de mardi."
    },
    {
      "id": "2026-S49-2",
      "date": "2026-12-01",
      "time": "18:45",
      "duration_min": 60,
      "discipline": "run",
      "discipline_label": "course",
      "title": "Seuil 3x8 min",
      "location": "Piste du stade, Brumeval",
      "distance": "9 km",
      "lines": [
        "15 min d'échauffement en aisance",
        "3x8 min à 5'15/km, 3 min de trot entre",
        "10 min de retour au calme"
      ],
      "why": "Cette séance élève l'allure que tu tiens longtemps. Le piège est de partir trop vite sur le premier bloc. C'est réussi si le troisième bloc est aussi rapide que le premier.",
      "fallback": "Repli : si la piste est fermée, même séance sur une route plate, au ressenti 7 sur 10."
    }
  ]
}
```

- `discipline` is one of `run`, `bike`, `swim`, `strength`, `rest`, `race`. It picks the emoji. `discipline_label` is the word shown to the athlete.
- `title` is given without the emoji: the script adds it.
- Omit `time` for an all-day entry. The rest day's `why` carries the week note.
- `reminders_min` on a session overrides the default. The default is 24 hours and 45 minutes before, for timed sessions only: an all-day entry has no reminder unless it carries its own `reminders_min`. Ask the athlete once: some want an extra reminder 12 hours before weekday evening sessions.
- Times are local times with no time zone: the calendar shows them at the same clock time wherever the athlete is.

The calendar event then reads, in this order: discipline, distance, instruction lines, a separator, the why paragraph, the fallback.

## Importing the file

The athlete imports the `.ics` into their calendar app, ideally into a dedicated calendar. Because each session keeps the same id, importing a newer export of the same week updates the events instead of duplicating them. This behaviour depends on the calendar app: tell the athlete to check after the first re-import, and to delete the dedicated calendar's week and import again if duplicates appear.
