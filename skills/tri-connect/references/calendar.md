# Getting the week into a calendar

tri-semaine produces `athlete/semaines/<iso week>.ics`. This page is about what the athlete does with it.

## Advice that holds for every calendar app

- **A dedicated calendar.** Create a calendar called "Training" (or the athlete's word for it) and import into that one. The sessions can then be shown, hidden or wiped without touching the rest.
- **Import, do not subscribe.** The file is imported: its events are copied into the calendar. There is no live link.
- **Each session has a stable id.** When a week changes, export it again and import the new file: a calendar app that recognises the ids updates the events instead of duplicating them. Not every app does. After the first re-import, check one moved session: if it appears twice, delete that week from the dedicated calendar and import again.
- **Times are local times.** A session at 18:45 shows at 18:45 wherever the phone is.
- **Reminders** come from the file: 24 hours and 45 minutes before by default. Some apps ignore the reminders of imported events and apply their own default: check after the first import.

## How to import

The menus differ between apps and change with their versions. Do not recite steps from memory: look at the current help page of the athlete's calendar app, then guide them. In general, on a computer the calendar app has an import command that takes an `.ics` file, and on a phone, opening the `.ics` file offers to add its events.

## What the event shows

Title: the emoji of the sport and the session title. Description, in this order: discipline, distance, the instruction lines, a separator, the why paragraph, the fallback. Location: the place of the session.

## Calendar or Intervals.icu?

Both can hold the planned sessions, for different uses. The calendar is where the athlete sees the week among the rest of their life, with the fallback and the reason. Intervals.icu is where a structured session becomes a workout on the trainer or the watch. The week file stays the single source: both are generated from it.
