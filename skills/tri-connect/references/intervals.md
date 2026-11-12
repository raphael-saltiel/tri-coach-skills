# Intervals.icu, as read on 12 November 2026

Everything here is a dated fact. Read the official page again before repeating a detail to the athlete.

## The official connector

Source: the connector page on intervals.icu, and the forum thread "Intervals MCP Connector (Official MCP) Beta testers needed!" (posted 31 October 2026, updated 11 November 2026).

- It is the official Intervals.icu MCP server. Address: `https://mcp.intervals.icu/mcp`.
- Status: beta. It requires an Intervals.icu Supporter plan (4 dollars a month on the page that day).
- Setup in Claude: Settings, then Connectors, then Add custom connector. Name it, paste the address, select Connect, sign in to Intervals.icu and approve. Nothing to install and no API key to copy.
- It reads: activities and their intervals, fitness and form, wellness, best efforts, planned workouts, races, zones and thresholds by sport.
- It can write: planned workouts and notes (add, move, change, delete one at a time), thresholds and zones for one sport at a time, daily wellness, effort and feel on completed activities, season entries (targets, phases, races, sick or injured days). Changes ask for the user's confirmation.
- Strava: activities that came through Strava show only their date and id. The page gives the reason: Strava's terms do not allow their data to be passed to AI tools. Activities from devices connected directly to Intervals.icu are included.
- It reads up to 12 months back, 6 months per question.
- The athlete can disconnect it at any time in Intervals.icu settings, under connected apps.
- Known gaps listed that day: step-by-step comparison of planned and completed workouts, swim lengths, coach access.

This pack does not bundle the connector: the athlete adds it in their own settings.

## The API with a personal key

Sources: the forum thread "API access to Intervals.icu", the API integration cookbook, the thread "Uploading planned workouts to Intervals.icu", and the API specification at intervals.icu/api/v1/docs.

- Authentication: HTTP Basic. The user name is the literal `API_KEY`, the password is the key. The key is created in Intervals.icu settings, under the developer settings near the bottom of the page.
- Athlete id `0` means "the athlete this key belongs to".
- Activities: `GET /api/v1/athlete/0/activities?oldest=YYYY-MM-DD&newest=YYYY-MM-DD`. A `fields` parameter limits what comes back.
- One activity with its intervals: `GET /api/v1/activity/{id}?intervals=true`.
- Fitness and recovery by day: `GET /api/v1/athlete/0/wellness?oldest=...&newest=...`. The record also holds weight, food and medical fields: the script does not ask for them.
- Planned workouts: `POST /api/v1/athlete/0/events/bulk` with an array of events (`category` WORKOUT, `start_date_local`, `type`, `name`, `description`, `moving_time`, `uid`). With `upsertOnUid=true`, an event whose `uid` already exists is updated instead of created. The script builds the `uid` from the session id.
- Rate limits for a personal key: 5000 requests a day and 2500 per rolling 15 minutes, plus 10 calls a second per IP address. Over the limit: status 429 and a `Retry-After` header in seconds.
- Strava: "data from Strava is not available from the API". Such an activity comes back with only its id, date and source.

Not tested against the live service: `scripts/intervals.py` was written from the specification and tested on simulated responses only. The first real use must start with `--dry-run`, then one read command, before any `push`.
