# tri-coach-skills

*Read in English: [README.md](README.md)*

Un pack gratuit de dix skills qui font de Claude un coach de triathlon pour débutants. Tu lui dis quelle course tu prépares et à quoi ressemble vraiment ta semaine. Il mesure où tu en es, construit le plan jusqu'au jour de la course, écrit chaque semaine, fait le bilan de tes séances quand tu le demandes, et prépare la course avec toi. Il fonctionne pour les formats S, M, 70.3 et Ironman, avec ou sans montre.

Ce n'est pas un plan générique. Sa valeur est dans les règles qu'il applique : partir de ce que tu fais réellement, ne jamais monter plus vite que le corps ne s'adapte, ne jamais rattraper une séance manquée, et laisser la douleur avoir raison sur le tableau.

> **Ce pack ne remplace ni un médecin ni un entraîneur diplômé.** Il ne donne aucun conseil médical. Si tu as une condition médicale, un traitement en cours ou le moindre doute, vois ton médecin avant de commencer, et avant tout effort intense. Douleur dans la poitrine, malaise ou essoufflement anormal : tu arrêtes et tu consultes.

## Pourquoi ce pack existe

C'est le dépôt que j'aurais aimé avoir quand j'ai commencé. J'ai tout appris sur le tas, et j'ai galéré plus d'une fois. Ce pack rassemble ce que j'aurais voulu qu'on me dise dès le premier jour, pour que tu n'aies pas à passer par là.

Rapha

## Ce que contient le pack

| Skill | Ce qu'il fait | Ce qu'il écrit |
|---|---|---|
| `tri-onboarding` | Te questionne sur ta course, ta semaine réelle, ton matériel et ta santé | `athlete/profile.md` |
| `tri-tests` | Planifie et lit tes tests, calcule tes zones, dit si tu es dans les temps | `athlete/zones.md` |
| `tri-plan` | Construit le plan jusqu'à la course : phases, heures par semaine, décharges, affûtage | `athlete/plan.md`, `athlete/plan.csv` |
| `tri-semaine` | Écrit la semaine séance par séance, l'adapte, l'exporte vers ton agenda | `athlete/semaines/` |
| `tri-bilan` | Fait le bilan d'une séance ou d'une semaine quand tu le demandes, et tient le journal | `athlete/journal.md` |
| `tri-renfo` | Séances courtes de gainage, de renforcement et de mobilité à la maison | des séances dans la semaine |
| `tri-nutrition` | Quoi manger et boire pendant les sorties longues et la course | `athlete/nutrition.md` |
| `tri-jour-j` | Estime ton temps sur le vrai parcours, vérifie les barrières horaires, prépare la journée | `athlete/jour-j.md` |
| `tri-connect` | Relie tes données d'entraînement (Intervals.icu, fichiers, captures d'écran) et tes appareils | `athlete/connect.md` |
| `tri-guide` | Explique le vocabulaire, le matériel, le choix d'une première course, les règles | rien |

## Trois niveaux d'équipement

Chaque séance peut s'écrire à chaque niveau. Aucun n'est obligatoire.

| Niveau | Tu as | Tes séances se pilotent avec |
|---|---|---|
| 1 | rien d'autre qu'une montre avec chronomètre | ton ressenti sur 10, et ta capacité à parler |
| 2 | un capteur de fréquence cardiaque | la fréquence cardiaque |
| 3 | un home-trainer ou un capteur de puissance, une montre GPS | la puissance à vélo, l'allure à pied |

Un premier triathlon se termine très bien au niveau 1.

## Installer

Choisis une des trois façons. Les noms de menus ci-dessous sont ceux de l'interface en anglais : ils peuvent être traduits dans la tienne.

### 1. Dans l'app Claude (web ou bureau)

1. Ouvre Claude et va dans **Customize**, puis **Plugins**.
2. Choisis **Add**, puis **Add marketplace**.
3. Colle `raphael-saltiel/tri-coach-skills` et valide.
4. Le plugin **Tri Coach** apparaît dans la liste. Sélectionne-le, puis **Add**.

Le pack utilise de petits scripts de calcul. Pour qu'ils tournent, l'exécution de code et la création de fichiers doivent être activées dans les réglages de Claude. Tant que ce dépôt est privé, Claude te demandera d'abord de connecter ton compte GitHub.

### 2. Dans Claude Code

```bash
claude plugin marketplace add raphael-saltiel/tri-coach-skills
```

```bash
claude plugin install tri-coach@tri-coach-skills
```

Dans une session, les deux mêmes commandes s'écrivent `/plugin marketplace add raphael-saltiel/tri-coach-skills` et `/plugin install tri-coach@tri-coach-skills`.

### 3. À la main

1. Sur la page du dépôt, choisis **Code**, puis **Download ZIP**, et décompresse l'archive.
2. Claude Code : copie les dix dossiers qui se trouvent dans `skills/` vers `~/.claude/skills/`.
3. App Claude : compresse chacun des dix dossiers séparément, puis dans **Customize**, **Skills**, envoie-les un par un.

## Démarrer, en cinq étapes

Ouvre une nouvelle conversation et écris ce que tu veux avec tes mots. Le bon skill se lance tout seul.

1. **"Je prépare mon premier triathlon, aide-moi à démarrer."** Le coach te questionne sur ta course, ta semaine, ton matériel et ta santé, puis écrit ton profil.
2. **"Quels tests je dois faire ?"** Il programme des tests simples sur tes deux premières semaines, à ton niveau d'équipement, puis calcule tes zones.
3. **"Construis mon plan."** Il construit les semaines jusqu'à la course et te dit franchement si l'objectif est risqué.
4. **"Je fais quoi cette semaine ?"** Il écrit chaque séance en quatre lignes, avec un repli en cas de mauvais temps, et peut mettre la semaine dans ton agenda.
5. **"Voilà comment s'est passée ma séance."** Après une séance, raconte-la, envoie une capture d'écran, ou laisse-le lire tes données. Il te dit ce qu'elle vaut et si quelque chose change.

Plus tard, quand tu en as besoin : le renforcement à la maison, l'alimentation des sorties longues, l'estimation et la liste de contrôle du jour J, et la connexion de tes appareils.

## Où vivent tes données

- Tout ce qui te concerne est gardé dans des fichiers lisibles, dans un dossier `athlete/` de ton dossier de travail. Tu peux les ouvrir, les modifier et les supprimer.
- Dans l'app de discussion Claude, les fichiers ne persistent pas toujours d'une conversation à l'autre : garde-les dans un Projet, ou joins-les à nouveau la fois suivante. Le coach te le rappelle une fois.
- Le pack n'envoie tes données nulle part. Les seuls appels réseau sont ceux que tu mets toi-même en place dans `tri-connect` pour lire ton propre compte Intervals.icu.
- Le pack n'utilise jamais l'API Strava. Intervals.icu indique que les conditions de Strava n'autorisent pas la transmission de leurs données à des outils d'IA.
- Une clé API Intervals.icu, si tu en utilises une, reste dans une variable d'environnement sur ta machine. Elle n'est jamais écrite dans un fichier ni demandée dans une conversation.

## Niveau de détail

Par défaut, le coach explique chaque terme et la raison de chaque chiffre : c'est le niveau "détaillé", pensé pour un premier triathlon. Demande le niveau "essentiel" quand tu ne veux plus que les chiffres et les décisions. Les consignes de séance tiennent en quatre lignes dans les deux cas.

## Exemples

[`examples/`](examples/) contient un athlète fictif, joué à travers tous les skills aux niveaux 1 et 3 : profil, zones, plan, une semaine complète avec son fichier d'agenda, un bilan de séance, l'alimentation et l'estimation du jour J. Tout y est inventé.

## Ce que le pack ne fait pas

- Conseil médical, diagnostic de blessure, ou quoi que ce soit sur une condition médicale ou un traitement.
- Objectifs de poids, calcul de calories, alimentation de tous les jours. Seule l'alimentation pendant l'effort est traitée.
- Notifications, messages programmés, tableau de bord, application web.
- Lecture de Strava.

## Limites connues

À lire avant de te reposer sur le pack.

- **Pas testé dans l'app Claude.** Le plugin a été validé et installé uniquement avec la ligne de commande de Claude Code. Les étapes d'installation dans l'app viennent de la documentation officielle.
- **`intervals.py` n'a jamais appelé le vrai service Intervals.icu.** Il a été écrit à partir de la spécification officielle de l'API et testé sur des réponses simulées. Commence par `--dry-run`.
- **Le connecteur officiel Intervals.icu est en bêta** et demande un abonnement Supporter payant. Il est décrit d'après sa page officielle (lue le 12 novembre 2026), pas testé.
- **La prise en charge des appareils n'est confirmée qu'en partie.** La liste vient de la page officielle des intégrations. Ce que chaque appareil synchronise (activités, données de récupération, séances planifiées) n'y est pas précisé.
- **Le réimport dans l'agenda dépend de ton application d'agenda.** Les séances gardent un identifiant stable, mais toutes les applications ne mettent pas à jour un événement au lieu de le dupliquer. Aucune application d'agenda n'a été testée.
- **Pas de lecteur de fichiers `.fit`.** Exporte un fichier `.tcx` ou `.gpx`, ou envoie une capture d'écran.
- **Plusieurs chiffres sont des choix du pack, pas des normes** : le nombre minimum de semaines et le plateau d'heures par format, les plafonds des sorties longues, les plages d'allure en natation, les zones prudentes utilisées avant un test, les gains attendus entre deux tests, la part de la puissance au seuil tenue en course, et le ralentissement à pied après le vélo. Chacun est signalé comme tel là où il sert.
- **L'estimation de course est un modèle.** Elle suppose l'absence de vent et lisse les montées. Compte quelques minutes d'erreur, davantage sur les parcours longs ou très raides.
- **La routine de mobilité est générique.** C'est de l'entretien de base, pas le fruit d'une méthode éprouvée.
- **Les exemples ont été joués par une personne et un assistant**, pas par des athlètes indépendants.
- **Les instructions des skills sont en anglais**, et le coach te répond dans ta langue. Les exemples sont en français.

## Contribuer

```bash
python3 -m unittest discover -s tests
```

- Les scripts n'utilisent que la bibliothèque standard de Python (3.10 ou plus). Aucune dépendance à installer.
- Les règles partagées par plusieurs skills vivent dans `common/` et sont recopiées mot pour mot dans chaque `SKILL.md`, entre des marqueurs. Modifie le fichier de `common/`, lance les tests : ils nomment les skills à mettre à jour.
- Aucune donnée personnelle dans le dépôt. Tous les exemples utilisent un athlète fictif.
- Aucun tiret cadratin ni demi-cadratin dans les fichiers : les tests le vérifient.
- Une nouvelle règle doit avoir son cas d'exemple dans un fichier `references/`.

## Licence

MIT. Voir [LICENSE](LICENSE). Auteur : Rapha.
