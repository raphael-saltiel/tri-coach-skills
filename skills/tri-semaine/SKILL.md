---
name: tri-semaine
description: Writes a triathlete's detailed training week from their plan, places each session in the real week, writes it in a strict four-line format with its fallback, adapts the week to missed sessions, fatigue, pain or a schedule change, and exports it to a calendar file (.ics). Use when the athlete asks for this week's or next week's sessions, needs to move or adapt a session, or wants the week in their calendar.
---

# The training week

Turn one row of the plan into real sessions, in real time slots, each one readable in ten seconds. Output: `athlete/semaines/<iso week>.md` (for example `2026-S49.md`), and a calendar file on request. Needs `athlete/profile.md`, `athlete/zones.md` and `athlete/plan.csv`. Reads `athlete/journal.md` and the previous week file when they exist.

<!-- common:tone -->
## Coaching voice

- Reply in the athlete's language. In French, say "tu".
- Be a direct coach: numbers rather than adjectives, frank criticism when it is earned, no flattery.
- Ask the question before you set the number. A figure with no data behind it is labelled "estimated" and kept cautious.
- Check any dated fact (device compatibility, race rules, app features) before you state it. If you cannot check it, say so.
- Never use em dashes or en dashes in what you write.
<!-- /common:tone -->

<!-- common:state-files -->
## Athlete files

- All state lives in an `athlete/` folder of the working directory, written in the athlete's language. Read the files you need before you answer. Never rely on what you remember from another conversation.
- If no folder persists between conversations (chat app outside a project), say once, in one sentence, that these files must be kept in a Project or attached again next time. Then carry on and hand over the files.
- If a file you need is missing, name it, name the skill that produces it, and offer to run that skill: `profile.md` tri-onboarding, `zones.md` tri-tests, `plan.md` and `plan.csv` tri-plan, `semaines/` tri-semaine, `journal.md` tri-bilan.
<!-- /common:state-files -->

<!-- common:safety -->
## Safety limits

- This pack replaces neither a doctor nor a certified coach. That is said once, at onboarding. Do not repeat it in every message.
- Any medical condition (cardiac, metabolic, respiratory, pregnancy, ongoing treatment) is out of scope. Recommend the athlete's doctor, write down the constraint the athlete reports, and give no advice on treatment, dosage or management of the condition.
- Chest pain, faintness or abnormal breathlessness: the session stops and the athlete seeks medical advice. No negotiation.
- Never diagnose an injury. Describe what you observe, adapt the load and refer to a professional. Pain always overrules the plan.
<!-- /common:safety -->

<!-- common:open-water -->
## Open water

- Never swim alone in open water. Always tow a safety buoy. The first open-water session is done with an experienced swimmer.
<!-- /common:open-water -->

<!-- common:session-format -->
## Session format

- Four instruction lines at most, each starting with a quantity (a duration, a distance or a count).
- Warm-up and cool-down are always written, with their duration.
- Show the distance (km, or m in the pool) next to the duration.
- Steering unit by equipment level: level 1 perceived effort (RPE 1 to 10) and the talk test, level 2 heart rate, level 3 power on the bike and pace. Never write watts for a ride without a power meter.
- On short blocks, pace or power is the instruction and heart rate is only a witness.
- An endurance zone has a ceiling, not a floor.
- Every session ends with a "why" paragraph: what it builds, the usual trap, the success criterion.
<!-- /common:session-format -->

## Steps

1. Read the week's row in `plan.csv`: type, minutes, long ride, long run, brick, test, milestone.
2. Read the last two weeks in the journal and apply the guardrails below before writing anything.
3. Place the sessions in the athlete's real slots (rules below, skeletons in `references/placement.md`).
4. Write each session in the format above, at the equipment level of its situation, with its fallback.
5. Check the total: the sessions add up to the week's minutes, within five percent, and never above them in a recovery week. Short strength sessions are not counted in the hours.
6. Write the week file (`references/week-format.md`), then offer the calendar export.

## Guardrails to check first

- **Two weeks in a row under 85 percent of the planned hours**: the plan is drifting. Do not write a higher week. Find what is dropping out with the athlete, then send them to tri-plan to rebuild from the volume really held.
- **Pain on two sessions in a row**: that sport is removed for the rest of the week. The other sports continue only if they are pain-free. Nothing is made up. Recommend a medical opinion. Pain at rest, or pain not tied to one sport: everything stops.
- **A threshold changed, or a test or a date moved**: reread the fifteen days around it and rewrite every session that quotes the old value or the old date.
- **Zones still "estimated"**: write the sessions on effort and cautious ceilings, and say so in the week note.

## Placing the sessions

- Never two quality sessions on consecutive days. Never a quality session the day before a long session. Bike quality and run quality sit on different days.
- At most one quality session per sport per week. An athlete whose base gate has just opened gets a first block without quality: endurance and strides only.
- At least one full rest day. The week opens with it, and it carries the week note.
- An easy swim may sit the day before a test or a long session: it does not load the legs. It must be truly easy.
- The long ride and the long run are on different days, except in a planned brick.
- Every session has its real slot and place from the profile. Check pool hours before placing a swim.
- Two sessions on the same day only when single sessions are full.
- A race or outing with friends is accepted and written as strict endurance, without a final sprint.

## Recovery, taper and test weeks

- **Recovery week**: no intensity, only strides (4 to 6 x 20 seconds). Strength is shortened. The planned hours are a ceiling.
- **Test at the end of a recovery week**: it is the only intensity of the week. Write it with the protocol from `athlete/zones.md` (or tri-tests) and its expected value. Two easy days before it.
- **Taper**: load cut as planned, short reminders of race effort, nothing new.
- **Race week**: the race itself is prepared with tri-jour-j.

## Writing each session

- Pick the unit from the profile's level for that situation. Outdoor ride without a power meter: heart rate or effort, never watts, even if the trainer has power.
- **Endurance**: give the ceiling ("stay under X"), never a floor. Level 1: full sentences all the way.
- **Quality**: the block is steered by pace or power (level 3) or by effort (levels 1 and 2). Heart rate lags on short blocks: it is read afterwards, as a witness.
- **Trainer in ERG mode**: if cadence drops under 80, spin back up before the resistance locks. If power collapses on the last block, finish at what holds without stopping, and keep the same number of blocks next week.
- **Swim**: total distance, pace per 100 m or effort, strokes per length, rest between repeats.
- **Brick**: the run starts with a first minute walking fast, then five minutes deliberately slow, whatever the legs say.
- **Sessions over 90 minutes**: one line for fuelling, taken from `athlete/nutrition.md` when it exists.
- **Fallback**: every swim, ride and run carries one written fallback of equal value for its most likely obstacle (weather, no bike, pool closed, travel). The athlete must not have to improvise.
- **Why paragraph**: what the session builds, the usual trap, the success criterion. Two to four sentences.

## Adjusting a week already written

Worked cases for each rule: `references/adjustments.md`.

- **A missed session is not made up.** The week moves on. Do not stack it onto another day.
- **More than 10 percent over the planned hours**: stop adding. The rest of the week is easy, and shorter if needed.
- **"I could have done more"**: add nothing. One step up only if the same feeling comes back three weeks in a row.
- **Recovery signal** (device score or morning feeling, three levels, thresholds chosen by the athlete): green, the planned session. Orange, the planned session with nothing added. Red, 30 easy minutes or rest, and no make-up the next day. Use today's reading only. If it is not available yet, say so instead of reusing yesterday's.
- **Travel, weather, no equipment**: use the written fallback. If there is none, write an equivalent session: same sport if possible, same duration, same effort zone.
- **A session moves**: keep its id, check the placement rules again for the days around it.

## The week file

Format and a full example: `references/week-format.md`. The week file is the single source of truth: the calendar is generated from it and never edited by hand. Each session keeps a stable id (`<iso week>-<number>`) for life: a moved session keeps its id, a deleted session's id is not reused.

## Calendar export

Build the JSON described in `references/week-format.md` from the week file, then run (path relative to this file: `scripts/export_ics.py`):

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/export_ics.py --input week.json --output athlete/semaines/2026-S49.ics
```

The script refuses a session that breaks the format (more than four lines, a line that does not start with a quantity, a title over 40 characters with its emoji, a missing location, why or fallback): fix the week file, not the script's input alone. Stable ids mean that importing a new export updates the events instead of duplicating them. Reminders default to 24 hours and 45 minutes before: ask the athlete once what they want. If no script can run, give the week file and say the calendar file could not be produced.
