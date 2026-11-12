---
name: tri-plan
description: Builds a triathlete's whole plan from today to race day in five phases, with a weekly hour ramp, recovery weeks, long-session progression, test calendar, intermediate races and taper. Writes athlete/plan.md and athlete/plan.csv. Use when an athlete with a profile needs a plan, or when the race date, the available hours or the starting volume change.
---

# Training plan

Turn the profile into a week-by-week frame up to the race: phases, hours, long sessions, tests, milestones. No session detail here, that is tri-semaine. Outputs: `athlete/plan.md` and `athlete/plan.csv`. Needs `athlete/profile.md`, and `athlete/zones.md` if it exists.

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

<!-- common:detail -->
## Level of detail

- The profile stores the athlete's level of detail: "detailed" (the default for a beginner) or "essential". If it is missing, use "detailed" and say once that the short version is available on request.
- **Detailed**: give the reason behind every number (where it comes from, what it is for) and explain each technical term in a few plain words. A file the athlete keeps (plan, zones, race day, fuelling) explains its own terms where they first appear. A recurring output (week file, debrief) explains a term only if it is not yet in `athlete/lexique.md`, then adds it there with its explanation.
- **Essential**: numbers and decisions only. Explain on request.
- At both levels: start with the conclusion, and keep the session instruction lines in their strict format. Detail goes below them, never into them. More detail never means more adjectives.
<!-- /common:detail -->

<!-- common:safety -->
## Safety limits

- This pack replaces neither a doctor nor a certified coach. That is said once, at onboarding. Do not repeat it in every message.
- Any medical condition (cardiac, metabolic, respiratory, pregnancy, ongoing treatment) is out of scope. Recommend the athlete's doctor, write down the constraint the athlete reports, and give no advice on treatment, dosage or management of the condition.
- Chest pain, faintness or abnormal breathlessness: the session stops and the athlete seeks medical advice. No negotiation.
- Never diagnose an injury. Describe what you observe, adapt the load and refer to a professional. Pain always overrules the plan.
<!-- /common:safety -->

## Inputs, all from the profile

- Race date and format (S sprint, M olympic, 70.3, IM Ironman).
- **Starting hours: the last complete, normal week.** Never an average that includes a break or an injury, never a wish. If the profile gives an average or a disrupted week, ask again before computing.
- Hours ceiling: the most the athlete can truly give in a week.
- Longest recent ride and run, in minutes.

If one is missing, ask for it. Do not guess it.

## Compute the ramp

Run the script (path relative to this file: `scripts/ramp.py`):

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/ramp.py --start-hours 4.5 --start-date 2026-11-16 \
  --race-date 2027-04-25 --format M --available-hours 8 \
  --long-bike-min 90 --long-run-min 50
```

Add `--output-format csv --output athlete/plan.csv` to write the file. `--help` lists every option. The JSON output carries the weeks and a `warnings` list: read every warning to the athlete in plain words. If no script can run, apply the rules in `references/formats.md` by hand and say that the figures were computed by hand.

Start the plan on the coming Monday. If today is Monday to Wednesday, the current week can be week 1.

## The rules the ramp applies

- **Week 1 is what was really done**, not more.
- **Three load weeks, then one recovery week at minus 35 percent.** The recovery week is a ceiling: doing less is fine, doing more is not.
- **+10 percent is a ceiling, not a target.** Between two load weeks the rise never exceeds 10 percent. The script takes the rate needed to reach the plateau by the end of the development phase, capped at 10 percent. After a recovery week, load resumes at the previous peak, then the plateau is held.
- **Plateau = the smaller of the format plateau and the athlete's hours ceiling.** This rule comes first. The athlete's ceiling is never exceeded.
- **Long ride +15 min, long run +10 percent or +10 min, whichever is smaller**, on load weeks only, up to the format cap, and only while the two together stay under 60 percent of the week. In a recovery week both drop by 35 percent, then resume where they were.
- **Taper**: two weeks for S and M, three for 70.3 and Ironman, load cut sharply, nothing new.

| Format | Minimum weeks | Plateau, hours a week | Long ride cap | Long run cap | Taper |
|---|---|---|---|---|---|
| S | 8 | 6 | 1 h 30 | 1 h 00 | 2 weeks |
| M | 12 | 8 | 2 h 30 | 1 h 30 | 2 weeks |
| 70.3 | 16 | 11 | 4 h 00 | 2 h 00 | 3 weeks |
| Ironman | 24 | 14 | 5 h 30 | 2 h 30 | 3 weeks |

How to read the plateau:
- These are choices of this pack for a beginner, not norms.
- **Sprint, 6 hours**: most beginners will not reach it and must not aim for it. Their own hours ceiling sets the plateau, and a sprint is finished on much less.
- **Ironman, 14 hours**: this is a finisher's plateau, not a time-goal plateau. Say so when you present the plan.
- Below the minimum weeks, or when the ramp cannot reach the plateau even at +10 percent, the script warns that the goal is risky. Say it plainly and offer two ways out: aim only to finish, or choose a later or shorter race.

## Phases, tests and milestones

Details and the purpose of each phase: `references/phases.md`.

- **Five phases** counted back from the race: base, development, specific, peak, taper. Their lengths follow the time available.
- **Tests**: initial tests in weeks 1 and 2. The first recovery week takes initial tests that were deferred. Then each recovery week ends with a retest, bike and swim alternating with run and swim. No test in the taper. The first retest decides the time goal, and a goal revised downwards is not a failure of the preparation.
- **Bike-run bricks**: early and in small doses (the `light` weeks, one per block), then every load week in the specific and peak phases (`weekly`).
- **Intermediate races** are steps, not goals: place them in the plan as the long or quality session of their week, with no time target unless the plan says so.
- **Rehearsal**: a race of a shorter format, or a home simulation, on the week marked `rehearsal`, before the peak.
- **Two sessions a day** only when single sessions are full. Do not offer them before, even if the athlete asks.
- **Quality progresses by steps written in advance** (for example 3x8 min, then 3x10 min, then 2x15 min), one step per block at most.

## Write the two files

`athlete/plan.csv`: the script's CSV, untouched. One row per week: `week, week_start, iso_week, phase, type, minutes, hours, long_bike_min, long_run_min, brick, test, milestone`.

`athlete/plan.md`, in the athlete's language:
1. **Summary**: race, weeks, starting hours and their source, plateau and why (format or the athlete's ceiling), weekly rate, total hours.
2. **Warnings**, each in one plain sentence with what to do about it.
3. **Phases**: dates, purpose, what success looks like at the end of each.
4. **Week table**: week, dates, phase, type, hours, long ride, long run, brick, test, milestone.
5. **Test calendar** with expected values if `zones.md` has them, labelled "estimated" otherwise.
6. **Intermediate races and rehearsal**.
7. **Rules of the road**: the recovery week is a ceiling, a missed session is not made up, pain overrules the plan.

At the "detailed" level, `plan.md` also carries, using the plain-words explanations of `references/phases.md`:
- an opening section "How to read this plan": what a load week and a recovery week are, what the ramp is, what each column of the week table means,
- a section "Why these numbers": why the plan starts at this volume, why it never rises faster, why the plateau is where it is, why the taper cuts the load,
- for each phase, what it will feel like and what would be a warning sign.

## Rebuild the plan when

- The race date or the format changes.
- The hours ceiling changes.
- Two weeks in a row end under 85 percent of the planned hours: the plan is drifting. Find the cause with the athlete first, then rerun the ramp from the volume really held.
- A break of a week or more (illness, injury, travel): restart from the last complete, normal week after the break, not from where the plan was.

After a rebuild, tell the athlete which coming weeks changed and that the weeks already written in `athlete/semaines/` must be rewritten by tri-semaine.
