---
name: tri-jour-j
description: Prepares a triathlete's race day, with a time estimate on the real course (swim, bike physics, transitions, run), the pace or effort to hold on each leg, the margin on cut-off times, the levers ranked by time gained, the fuelling timeline and a checklist, written to athlete/jour-j.md. Use when the athlete asks how long the race will take, what pace or power to hold, whether they will make the cut-offs, or wants a race plan or checklist.
---

# Race day

Give the athlete an honest estimate of their race on the real course, a simple way to pace it, and nothing left to decide on the morning. Output: `athlete/jour-j.md`. Needs `athlete/profile.md` and `athlete/zones.md`. Reads `athlete/nutrition.md` and `athlete/journal.md` when they exist.

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

<!-- common:safety-nutrition -->
## Fuelling limits

- Effort fuelling only: carbohydrate per hour, fluids, training the gut in small steps, a tolerance log.
- No weight goal, no restriction, no daily calorie count. Weight is never presented as something to change.
- If the athlete describes a difficult relationship with food, stay out of the numbers and point to a professional (doctor or registered dietitian).
- With a metabolic condition, or a treatment that affects eating or drinking, give only the general range, say that it is general, do not adapt it to the condition, and refer to the athlete's care team to adjust it.
<!-- /common:safety-nutrition -->

<!-- common:open-water -->
## Open water

- Never swim alone in open water. Always tow a safety buoy. The first open-water session is done with an experienced swimmer.
<!-- /common:open-water -->

## Before any number

- **The real course first.** The bike elevation gain must be in the profile with its source. If it is "unknown", find it with the athlete before estimating anything. An estimate on an assumed flat course can be wrong by an hour.
- **Measured inputs.** Swim pace from the 1000 m test, run pace at the endurance ceiling from the long runs, bike power from the test or from a real ride. If an input is "estimated", the whole estimate is labelled "estimated", and you say which input would firm it up.
- **Race rules are dated facts.** Cut-offs, wetsuit rule, what the aid stations hand out: read them on the organiser's page and write the date you checked. Do not answer from memory.

## The estimate

Run the script (path relative to this file: `scripts/race_estimate.py`):

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/race_estimate.py --format M --swim-pace 2:45 \
  --bike-elevation-m 480 --bike-power 156 --height-cm 172 --weight-kg 68 \
  --position hoods --run-endurance-pace 6:45 --start 09:30 \
  --cutoff-swim 1:00:00 --cutoff-bike 3:15:00 --cutoff-finish 4:30:00
```

`--help` lists every option. How to get each input at each equipment level, and what the model assumes: `references/model.md`.

- **Bike, with power (level 3)**: race power is a share of threshold power that depends on the format (table in `references/model.md`). Pass it as `--bike-power`.
- **Bike, without power (levels 1 and 2)**: give a recent solo ride on similar roads with `--ref-ride-km`, `--ref-ride-elevation-m` and `--ref-ride-time`. The script works out the power behind that ride and applies it to the race course.
- **Weight** is optional. Without it the script estimates it from height and says so. Weight is an input of the physics and never a lever: the script does not offer it as one, and neither do you.
- If no script can run, do not improvise a bike time. Give the swim and run parts by hand (they are simple products) and say the bike part needs the script.

## Reading the result to the athlete

1. **Time per leg, total, and finish time on the clock.** As a range, not a promise: say "about", and name the two or three assumptions that matter most (no wind, the position held all the way, the run fade).
2. **Margin on each cut-off.** If a margin is negative, or thinner than about ten percent of the limit, say it plainly, first, and go to the levers. Never soften a cut-off risk.
3. **Levers, ranked by time gained**, from the script: bike power, position, swim pace. Give the minutes for each. Tell the athlete which one is worth their training time, and which is not worth chasing.
4. **Goal.** Before the first retest the goal is to finish. After it, a time goal can be set from this estimate. A goal revised downwards is not a failure of the preparation.

Run the estimate again after each retest, and whenever the course information changes.

## Pacing, leg by leg

Detail: `references/pacing.md`.

- **Swim**: start long, as in the 1000 m test. Ample strokes for the first 200 m, outside the pack if the start is crowded. The swim is never where the race is won, and often where it is spoiled.
- **Bike**: one ceiling, held all the way: the race power (level 3), the heart-rate ceiling for the format (level 2), or "full sentences" turning into "short sentences" only on climbs (level 1). On climbs, hold the ceiling and accept the speed. Eat and drink on the plan.
- **Run**: first minute walking fast or at a very easy jog, then five minutes deliberately slow, whatever the legs say. The first brick almost always started too fast, and race day is worse. Then settle at the planned effort. Walk the aid stations if it helps to drink.
- **Transitions**: practised in the rehearsal. Same order every time.

## Fuelling on the day

Take the race-day plan from `athlete/nutrition.md` and place it on the timeline (before the start, each 20 to 30 minutes on the bike, the aid stations of the run). Only what the tolerance log shows was practised. If `nutrition.md` does not exist, say so and point to tri-nutrition rather than inventing a plan. Nothing new on race day.

## Checklist

`references/checklist.md`: the week before, the day before, the morning, each transition. Adapt it to the race (wetsuit or not, weather, what the organiser requires) and to the athlete's equipment. Nothing in it is new: every item was used in training or in the rehearsal.

## Write `athlete/jour-j.md`

In the athlete's language:

1. **The race**: date, start, distances, course profile and its source, cut-offs, rules checked and when.
2. **Estimate**: per leg, total, finish time, labelled "measured inputs" or "estimated", with the assumptions.
3. **Cut-off margins.**
4. **Levers**, ranked, with what the athlete decided to do about each.
5. **Pacing plan**: one line per leg, at the athlete's equipment level.
6. **Fuelling timeline.**
7. **Checklist.**

At the "detailed" level, `jour-j.md` also carries, using the plain-words explanations of `references/model.md`:
- for each leg, how the figure was built and which input it rests on,
- what a cut-off is and what happens if it is missed,
- what a lever is, why these three, and why weight is not one,
- for each line of the pacing plan, the reason behind it.
