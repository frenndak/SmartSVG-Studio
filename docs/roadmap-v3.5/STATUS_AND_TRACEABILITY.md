# SmartSVG V3.5 — Sources de vérité, matrice d'avancement et traçabilité

**But :** aucune copie statique d'un HEAD dans un README ne doit être prise pour l'état courant ; aucune couverture documentaire n'est comptée comme fonction livrée.

## Données faisant autorité par domaine

| Domaine | Référence à consulter | Périmètre exact |
|---|---|---|
| Gouvernance/permissions | `AGENTS.md`, `.automation/READY`, `docs/AUTONOMOUS_INTEGRATION_POLICY_V35.md`, R13 **sur main live** | Autorisations, exclusions, une seule fusion B/cycle |
| Scope/DoD | `MASTER_PRIORISE.md`, `BACKLOG_AND_DEPENDENCIES.md`, sources V3.3/V3.4 et SCN/CST/UXI/CP | Objectif sans inventer une implémentation |
| Curseur d'ingénierie documentaire | `EXECUTION_STATE.json` | Décisions, passation, observations **datées**, pas SHA/PR/CI live |
| Code/intégrations | API GitHub GET branches/main, PR, diff, runs et jobs SHA exact | Faits actuels et checks exécutés, pas juste couleur « success » |
| Windows réel / Design Space / coupe / RTX | Logs, artefacts, système/version, mesures et hash de build | Axes indépendants, sans transposition de PASS |
| Page d'accueil | Liens vers les références précédentes | Vitre de projet, pas journal immuable |

## Colonnes du tableau de maturité (réutiliser les 12 états existants)

À enregistrer **par capacité micro-lot** : `CANDIDATE`, `SPECIFIED`, `REVIEWED`, `DOC_ADOPTED`, `CODE_BRANCH`, `CODE_MAIN`, `WINDOWS_EXPOSED`, `UNIT_PASS_EXACT_SHA`, `WINDOWS_UI_PASS`, `RTX_GPU_PASS`, `DESIGN_SPACE_PASS`, `PHYSICAL_PASS`.

Ces états sont **des axes de preuve, pas un compteur de progression linéaire**. Chaque PASS doit pointer vers SHA, job/log ou rapport de test ; `UNKNOWN` et `NOT_RUN` ne valent ni `PASS` ni `FAIL`. `WINDOWS_EXPOSED` signifie seulement que le contrôle est présent, pas testé en vrai.

| Capacité | Code MAIN | Windows UI réel | Design Space | Coupe réelle | Prochain gap mesurable |
|---|---|---|---|---|---|
| W01 V1/session/récupération | Modules présents, fermeture E2E à qualifier | À démontrer sur build versionné | N/A | N/A | Test Windows propre et recovery |
| W02 premier Subject manuel / Undo | Code ciblé présent, état exact à relire | À qualifier E2E | N/A | N/A | PNG neuf → mask → save/reopen |
| W03 PNG PTC | Composants existants, relire leurs SHA | À qualifier E2E | NOT_RUN | NOT_RUN | Export utilisateur et CAL-PTC |
| W03/W04 SVG Basic Cut | Export backend PR selon état GitHub live ; ne pas le déclarer MAIN avant squash | Bouton/interface à raccorder et qualifier | NOT_RUN | NOT_RUN | Export depuis UI, puis CAL-CUT |
| W03 SVG multicouche CUT | À inventorier | NOT_RUN/UNKNOWN | NOT_RUN | NOT_RUN | Contrat typé, fixtures et réel |
| W03 SVG édition | À inventorier | NOT_RUN/UNKNOWN | NOT_RUN | NOT_RUN | Éditabilité vérifiable et V2 si nécessaire |

Le tableau est une **liste de tests à entreprendre, pas un tableau de bord actualisé automatiquement**. Avant chaque rapport, obtenir les PR et checks GitHub en direct ; ne pas copier les SHA de 2026-11-17 dans les conclusions. Un générateur de vue read-only peut produire plus tard un résumé à partir de `EXECUTION_STATE.json` + une collecte GET GitHub datée + rapports matériels locaux ; il ne doit ni modifier la roadmap normative ni inférer le PASS depuis le seul texte.

## Traçabilité minimale

Clé de jonction stable : **exigence V3.3 → ticket V3.4 (ou exception G6/G9 explicitée) → capacité W00–W16 → scénario T-V34 / SCN / CST / UXI → test exécutable réel → preuve SHA+axe → statut**. Ne pas fabriquer les associations manquantes.

Cas ouverts déjà documentés : 6 scénarios avec liens TEST→TICKET absents (`T-V34-03-16`, `06-22`, `06-24`, `06-25`, `07-16`, `07-25`) et 10 exigences G6/G9 sans ticket V34 direct (`S-021`, `S-036`, `S-037`, `S-044`, `S-047`, `S-064`, `S-066`, `S-092`, `S-099`, `R33-028`). Elles conservent leur propriétaire historique ou domaine W indiqué dans BACKLOG, mais la relation source reste `UNASSIGNED` tant qu'elle n'est pas prouvée.

Un nouveau statut « différé » ne retire **aucune** exigence héritée : il indique seulement le jalon cible de son implémentation. Les fonctions facultatives (ex. W14 IA) ne sont pas prérequis pour le chemin CPU/manuelle A1.
