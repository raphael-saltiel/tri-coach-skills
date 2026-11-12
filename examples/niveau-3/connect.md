# Connexions : Camille

Mis à jour : 25 novembre 2026

## Voie utilisée
- Le script `intervals.py` avec une clé API personnelle, dans Claude Code, depuis le 25 novembre 2026.
- Pourquoi pas le connecteur officiel : il demande l'abonnement Supporter d'Intervals.icu, que Camille n'a pas. Le script suffit.
- Les fichiers lus sont rangés dans `intervals/`, et c'est là que les bilans les trouvent.

## Appareil principal par sport
- Course à pied et natation : la montre GPS, reliée directement à Intervals.icu (source Garmin).
- Vélo en intérieur : l'application du home-trainer, reliée directement (source Zwift).
- Vélo en extérieur : la montre GPS.
- En cas de doublon, sources gardées en priorité : `GARMIN_CONNECT,ZWIFT`.

Un doublon, c'est la même séance enregistrée par deux appareils. On n'en garde qu'une, sinon les heures de la semaine sont comptées deux fois.

## Strava
- Le pack ne lit jamais Strava. Camille n'a pas de lien Strava vers Intervals.icu.

## Clé
- Dans la variable d'environnement `INTERVALS_API_KEY`, sur sa machine. Jamais dans ce dossier, jamais dans une conversation.

## Séances planifiées
- Agenda : le fichier `.ics` de chaque semaine, importé dans un agenda dédié "Entraînements".
- Intervals.icu : les séances de home-trainer uniquement, envoyées avec `intervals.py push` depuis `semaines/2026-S49-workouts.json`, puis transmises à l'application du home-trainer.
- Un seul seuil partout : 195 W dans `zones.md`, dans Intervals.icu et dans l'application du home-trainer. Sinon les blocs sont faux.

## Vérifié le
- 25 novembre 2026 : réglages Intervals.icu lus avec Camille, premier essai en `--dry-run`, puis une lecture des activités de la semaine.
