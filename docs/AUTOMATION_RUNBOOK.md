# SmartSVG — Exploitation des cycles privés Codex

## Référence

Source V21.15.2 conservée dans `source-releases/` ; moteurs évolutifs dans `engine/`. La roadmap active approuvée est `docs/ROADMAP_MASTER_v3_3.md` avec ses registres `docs/ROADMAP_TRACEABILITY_v3_3.md` et `docs/ROADMAP_COVERAGE_v3_3.md`. Le master V3.2 et son gel restent des archives protégées. La présence de `.automation/READY` confirme l'admission documentaire, pas une certification Cricut, ComfyUI ou GPU.

## Cadence opérationnelle

| Horaire | Origine | Effet |
|---|---|---|
| HH:05 UTC | SmartSVG-Automation public | Événement develop privé |
| HH:35 Europe/Paris | Tâche GPT indépendante | Lecture diff + CI HEAD, remarque GO/NO GO |
| HH:50 UTC | SmartSVG-Automation public | Événement repair privé, uniquement sur PR autonome labellisée |

**La tâche GPT ne pousse ni code, ni fusion, et ne contourne pas les secrets GitHub.** GitHub schedule peut retarder ou omettre un cycle. Le fuseau CET/CEST ne modifie pas les minutes, mais les durées d'exécution peuvent modifier la chronologie observée.

## Essai sans coût API

Dans le privé, Actions → `SmartSVG - Private AI Development` → Run workflow :
- `execute=false` (**défaut**) : préflight SHA roadmap et ZIP, vérification du marqueur et du rapport, puis aucun Codex.
- `execute=true` : seulement après configuration du secret privé `OPENAI_API_KEY`, de la variable `SMARTSVG_AUTOMATION_ENABLED=true`, et acceptation du coût API.

Dans le public, Actions → `SmartSVG - Secure half-hour orchestration` → Run workflow :
- `dry_run=true` (**défaut**) : vérifie la requête, sans contacter le dépôt privé.
- `dry_run=false` : déclenche réellement un événement privé seulement si variable d'activation publique et `SMARTSVG_DISPATCH_TOKEN` de portée minimale existent.

## Cycle de développement

1. Les garde-fous lisent l'empreinte de la roadmap, le rapport import, le marqueur READY et la file des PR `smartsvg/auto-*`.
2. **WIP=1** pour les PR autonomes uniquement. Les PR humaines ne bloquent pas l'agent et ne sont jamais modifiées par lui.
3. Un nouveau lot doit être borné par la roadmap et accompagné de tests ; il n'a pas le droit d'éditer les fichiers de gouvernance, la CI, les secrets ou l'archive originale.
4. Après commit, les workflows G0 et CPU sont **explicitement dispatchés sur la branche candidate** si pertinents. Envoyer le dispatch ne prouve pas leur réussite.
5. La tâche GPT examine le dernier HEAD et les checks `completed/success` pour ce même HEAD. Les résultats `skipped`, `pending`, refusés ou périmés sont des preuves insuffisantes.
6. Une PR saine reste candidate à une fusion **humaine**, pas automatique.

## Cycle de réparation : au plus une tentative par demande

L'audit indépendant vérifie un P0/P1, commente avec une procédure reproductible et applique le label `bug` (ou `smartsvg:repair` s'il existe) **uniquement** sur la PR autonome concernée. Le worker privé refuse un cycle de réparation sans ce label. Avant toute invocation de l'API, il retire le label, ce qui évite une nouvelle tentative payante sans nouvel audit.

Si la réparation échoue, la PR reste ouverte et le journal porte l'erreur. Une nouvelle demande doit être justifiée par une revue sur un HEAD ou un état CI significativement nouveau. L'apposition d'un label n'est pas une validation de la proposition.

## Prérequis GitHub Settings

- **Privé** : secret `OPENAI_API_KEY` avec plafond budgétaire défini dans la plateforme ; variable `SMARTSVG_AUTOMATION_ENABLED=true` ; autoriser GitHub Actions à créer des PR et à déclencher les workflows explicitement. Protéger `main` via ruleset.
- **Public** : secret `SMARTSVG_DISPATCH_TOKEN` dont la permission **Contents write** vise uniquement `frenndak/SmartSVG-Studio` ; variable `SMARTSVG_AUTOMATION_ENABLED=true`.
- Les connexions ChatGPT/GitHub actuelles permettent de modifier les fichiers et PR, **pas** de renseigner secrets, variables Actions ou rulesets via une action dédiée. Ne jamais placer les tokens dans des messages, des documents Git ou une PR.

## Attestations

- L1 : tests synthétiques et CPU sur runner, avec run ID, SHA du HEAD et dépendances pertinentes.
- L2 : authentique ComfyUI et modèle GPU exécuté sur la machine cible, non déductible d'un check GitHub.
- L3 : import Design Space, impression puis découpe et contrôle dimensionnel réels, non déductibles de L1/L2.

En cas de problème : mettre `SMARTSVG_AUTOMATION_ENABLED=false` dans les deux dépôts avant diagnostic. Un check vert sur une ancienne révision ne doit jamais justifier une fusion.
