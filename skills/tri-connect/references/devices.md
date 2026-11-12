# Devices and apps that feed Intervals.icu directly

Read on 12 November 2026. The list changes: check the integrations page on intervals.icu and the athlete's own Intervals.icu settings before stating that a device is supported.

## What the official sources show

| Device or app | On the official integrations page | Listed as an activity source in the API specification |
|---|---|---|
| Garmin | yes | yes (Garmin Connect) |
| Polar | yes | yes |
| Suunto | yes | yes |
| Coros | yes | yes |
| Wahoo | yes | yes |
| Zwift | yes | yes |
| Amazfit | yes | yes (Zepp) |
| Huawei | yes | yes |
| Concept2 | yes | yes |
| Dropbox (files dropped in a folder) | yes | yes |
| Hammerhead, SIGMA, iGPSPORT, MyWhoosh, Rouvy | yes | not as a named source |
| Oura, WHOOP | yes | wellness data, not a training source |
| Strava | yes | yes, but its activities are not readable by AI tools or through the API |

What the page does not say, device by device: whether completed activities, wellness data and planned workouts all sync. The page only states that "activities and wellness data sync automatically, and planned workouts can go to several devices". For a given device, read the athlete's Intervals.icu settings with them.

Activities can also be uploaded by hand as a file, or pushed by a third-party app authorised by the athlete.

## Apple Watch

Not on the official integrations page. Intervals.icu mentions that wellness data can come from Apple Health through third-party apps. One such app, HealthFit, lists Intervals.icu among its supported services on its App Store page (read on 12 November 2026), and its version notes mention pool swimming workouts. It is a paid third-party app, not part of this pack: the athlete decides.

## Setting up a direct link

1. In Intervals.icu settings, find the box of the device or app and connect it. The athlete signs in on the device maker's page.
2. Record one short session and check that it appears in Intervals.icu with its data.
3. If sessions also arrive through Strava, there will be two copies: one readable, one showing only its date. Remove the Strava link to Intervals.icu once the direct link works.
4. Write the main device for each sport in `athlete/connect.md`.

## A recovery band next to a watch

A recovery band often creates its own "activity" for a session the watch already recorded. It is always the copy. Its recovery score, if the athlete uses it as their recovery signal, is read on the day itself: if it has not synced yet, say so.
