# tri-coach-skills

*Lire en français : [README.fr.md](README.fr.md)*

A free pack of ten skills that turn Claude into a triathlon coach for beginners. You tell it which race you are preparing and what your week really looks like. It measures where you stand, builds the plan up to race day, writes each week, reviews your sessions when you ask, and prepares the race with you. It works for sprint, olympic, 70.3 and Ironman distances, with or without a watch.

It is not a generic plan. Its value is in the rules it applies: start from what you really do, never rise faster than the body adapts, never make up a missed session, and let pain overrule the schedule.

> **This pack replaces neither a doctor nor a certified coach.** It gives no medical advice. If you have a medical condition, are under treatment, or have any doubt, see your doctor before you start, and before any hard effort. Chest pain, faintness or abnormal breathlessness: stop and seek medical advice.

## Why this pack exists

This is the repository I wish I had when I started. I learned everything as I went, and I struggled more than once. This pack gathers what I wish someone had told me on day one, so that you do not have to go through the same.

Rapha

## What is in the pack

| Skill | What it does | It writes |
|---|---|---|
| `tri-onboarding` | Asks about your race, your real week, your equipment and your health | `athlete/profile.md` |
| `tri-tests` | Plans and reads your tests, computes your zones, says if you are on track | `athlete/zones.md` |
| `tri-plan` | Builds the plan to race day: phases, weekly hours, recovery weeks, taper | `athlete/plan.md`, `athlete/plan.csv` |
| `tri-semaine` | Writes the week session by session, adapts it, exports it to your calendar | `athlete/semaines/` |
| `tri-bilan` | Reviews a session or a week when you ask, and keeps the journal | `athlete/journal.md` |
| `tri-renfo` | Short strength, core and mobility sessions at home | sessions in the week |
| `tri-nutrition` | What to eat and drink during long sessions and the race | `athlete/nutrition.md` |
| `tri-jour-j` | Estimates your race time on the real course, checks the cut-offs, plans the day | `athlete/jour-j.md` |
| `tri-connect` | Links your training data (Intervals.icu, files, screenshots) and your devices | `athlete/connect.md` |
| `tri-guide` | Explains the vocabulary, the equipment, how to choose a first race, the rules | nothing |

## Three equipment levels

Every session can be written at each level. None is required.

| Level | You have | Your sessions are steered by |
|---|---|---|
| 1 | nothing but a watch with a timer | how hard it feels out of 10, and whether you can talk |
| 2 | a heart-rate sensor | heart rate |
| 3 | a home trainer or a power meter, a GPS watch | power on the bike, pace on the run |

A first triathlon can be finished at level 1.

## Install

Pick one of the three ways.

### 1. In the Claude app (web or desktop)

1. Open Claude and go to **Customize**, then **Plugins**.
2. Select **Add**, then **Add marketplace**.
3. Paste `raphael-saltiel/tri-coach-skills` and confirm.
4. The **Tri Coach** plugin appears in the list. Select it, then **Add**.

The pack uses small calculation scripts. For them to run, code execution and file creation must be turned on in your Claude settings. While this repository is private, Claude will ask you to connect your GitHub account first.

### 2. In Claude Code

```bash
claude plugin marketplace add raphael-saltiel/tri-coach-skills
```

```bash
claude plugin install tri-coach@tri-coach-skills
```

Inside a session, the same two commands are `/plugin marketplace add raphael-saltiel/tri-coach-skills` and `/plugin install tri-coach@tri-coach-skills`.

### 3. By hand

1. On the repository page, select **Code**, then **Download ZIP**, and unzip it.
2. Claude Code: copy the ten folders that are inside `skills/` into `~/.claude/skills/`.
3. Claude app: zip each of the ten folders separately, then in **Customize**, **Skills**, upload them one by one.

## Getting started, in five steps

Open a new conversation and write what you want in your own words. The right skill starts by itself.

1. **"I am preparing my first triathlon, help me get started."** The coach asks about your race, your week, your equipment and your health, and writes your profile.
2. **"Which tests should I do?"** It schedules simple tests for your first two weeks, at your equipment level, then computes your zones.
3. **"Build my plan."** It builds the weeks up to race day and tells you plainly if the goal is risky.
4. **"What do I do this week?"** It writes each session in four lines, with a replacement for bad weather, and can put the week in your calendar.
5. **"Here is how my session went."** After a session, tell it, send a screenshot, or let it read your data. It tells you what the session was worth and whether anything changes.

Later, when you need them: strength at home, fuelling for long sessions, the race-day estimate and checklist, and connecting your devices.

## Where your data lives

- Everything about you is kept in plain files in an `athlete/` folder of your working folder. You can open them, edit them and delete them.
- In the Claude chat app, files do not always persist between conversations: keep them in a Project, or attach them again next time. The coach reminds you once.
- The pack sends your data nowhere. The only network calls are the ones you set up yourself in `tri-connect` to read your own Intervals.icu account.
- The pack never uses the Strava API. Intervals.icu states that Strava's terms do not allow their data to be passed to AI tools.
- An Intervals.icu API key, if you use one, stays in an environment variable on your machine. It is never written to a file and never asked for in a conversation.

## Level of detail

The coach explains every term and the reason behind every number by default: that is the "detailed" level, meant for a first triathlon. Ask for the "essential" level when you only want the numbers and the decisions. Session instructions stay four lines long either way.

## Examples

[`examples/`](examples/) holds a fictional athlete, played through every skill at levels 1 and 3: profile, zones, plan, a full week with its calendar file, a session review, fuelling and a race-day estimate. Everything in it is invented.

## What this pack does not do

- Medical advice, injury diagnosis, or anything about a medical condition or a treatment.
- Weight goals, calorie counts or daily diet. Fuelling is covered during effort only.
- Notifications, scheduled messages, a dashboard or a web app.
- Reading Strava.

## Known limits

Read these before relying on the pack.

- **Not tested inside the Claude app.** The plugin was validated and installed with the Claude Code command line only. The app installation steps above come from the official documentation.
- **`intervals.py` has never called the real Intervals.icu service.** It was written from the official API specification and tested on simulated responses. Start with `--dry-run`.
- **The official Intervals.icu connector is in beta** and needs a paid Supporter plan. It is described from its official page (read on 12 November 2026), not tested.
- **Device support is only partly confirmed.** The device list comes from the official integrations page. What each device syncs (activities, recovery data, planned workouts) is not stated there.
- **Calendar re-import depends on your calendar app.** Sessions keep a stable identifier, but not every app updates an event instead of duplicating it. No calendar app was tested.
- **No reader for `.fit` files.** Export a `.tcx` or `.gpx` file, or send a screenshot.
- **Several figures are choices of this pack, not norms**: minimum weeks and weekly plateau by format, long-session caps, the swim pace bands, the cautious zones used before a test, the gains expected between tests, the share of threshold power held in a race, and the slowdown on the run after the bike. Each is labelled as such where it is used.
- **The race estimate is a model.** It assumes no wind and averages the climbs. Expect minutes of error, more on long or very steep courses.
- **The mobility routine is generic.** It is basic maintenance, not built from a tested method.
- **The examples were played by one person and an assistant**, not by independent athletes.
- **Skill instructions are in English**, and the coach answers in your language. The examples are in French.

## Contributing

```bash
python3 -m unittest discover -s tests
```

- Scripts use the Python standard library only (Python 3.10 or later). No dependency to install.
- Rules shared by several skills live in `common/` and are copied word for word into each `SKILL.md` between markers. Change the file in `common/`, run the tests: they name the skills to update.
- No personal data in the repository. Every example uses a fictional athlete.
- No em dash or en dash in any file: the tests check it.
- A new rule needs a worked case in a `references/` file.

## Licence

MIT. See [LICENSE](LICENSE). Author: Rapha.
