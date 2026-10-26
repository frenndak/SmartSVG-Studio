# SmartSVG — protocole d'intégration V1 (candidat)

**Objectif :** réduire les PR empilées sans jamais assimiler « CI verte » à « fusion admissible ». Ce texte est ajouté à la PR de sécurité #13 ; **aucune fusion ni activation en production n'est effectuée par son ajout**.

## Acteurs et étapes

1. **Producteur (:15, Europe/Paris)** — travaille sur la PR racine la plus ancienne ou corrige une régression P0/P1. Tant qu'il existe au moins quatre PR ouvertes, pas de nouvelle PR fonctionnelle. Aucune modification de `main` en direct.
2. **Auditeur indépendant (:35)** — examine le diff réel, les entrées adversariales, la compatibilité des nœuds et projets, les preuves attachées au HEAD et aux dépendances. Pour une PR purement logicielle G1/G2, les tests L1 CPU pertinents et la revue du diff suffisent *au verdict d'intégration de code* si le risque matériel n'est pas dans son périmètre. L2 (ComfyUI+GPU réel) et L3 (Cricut) restent obligatoires pour tout jalon qui affirme leurs fonctionnalités prouvées, **jamais présumés satisfaits**.
3. **Qualification en lecture seule** — exécuter le workflow manuel `SmartSVG - Read Only Integration Preflight` sur **`main`** après fusion de la PR #13, avec l'entrée `pr_number`. Il interroge GitHub en direct, puis lance `tools/integration_eligibility.py`.
4. **Approbation et intégration** — la PR doit être ouverte, non brouillon, basée directement sur `main`, sans conflit ni retard de branche, avec **G0 obligatoirement** et **CPU Smoke si la PR modifie `engine/`**, exécutés avec succès sur le HEAD exact. L'inventaire complet des fichiers modifiés est récupéré via l'API GitHub ; s'il est absent, tronqué, incohérent ou dupliqué, CPU devient obligatoire et la qualification est bloquée. Pour éviter de confondre un test de la référence synthétique `pull/PR/merge` avec celui du code candidat, les deux workflows doivent avoir été lancés sur la **branche candidate** via `workflow_dispatch` (et correspondre à son nom de branche et HEAD). Exiger un commentaire `SMARTSVG_AUDIT_V1` lié au **HEAD, à `BASE=main@<SHA>` et à `DIFF_SHA256=<empreinte du diff>`**, avec `VERDICT=GO_POUR_REVUE_INTEGRATION`, écrit par un compte **ayant aussi donné une revue GitHub `APPROVED` indépendante**, non bot et non auteur, sur ce même HEAD. Un commentaire par l'auteur de la PR ne suffit jamais. Les demandes de changements ouvertes bloquent. Le workflow ne change pas le statut de brouillon, ne merge pas, n'attribue pas d'approbation et ne réécrit aucune branche.
5. **Action mainteneur** — une fois les conditions réunies, le mainteneur vérifie encore `main` et HEAD au moment de la fusion via les mécanismes GitHub de protection / comparaison SHA. La qualification seule ne vaut ni autorisation de fusion automatique ni release du produit.
6. **Après fusion** — constater le nouveau `main` et le SHA de fusion, puis traiter la PR fille (base à recalculer, réévaluation des conflits, nouveaux checks exact-head), une seule par une.

## Politique de dette

Au 26/10/2026, 16 PR brouillon : #13 (sécurité), #14→#24 (branche produit empilée avec alternatives #20/#21 et #23/#24), #25 (SVG), #26→#28 (masques/éditeur). Les numéros sont des repères historiques uniquement.

- Ne pas rendre automatiquement prêtes ni fusionner en masse les PR liées.
- Avant de fusionner des variantes parallèles, comparer le contenu et choisir une implémentation canonique ; archiver/fermer uniquement les doublons réellement remplacés après confirmation.
- Corriger les tests sur les HEAD pertinents ; une CI verte sur une PR fille ne qualifie pas ses parents.
- Prioriser la réduction de la dette et la stabilisation du graphe de dépendances plutôt que la croissance du nombre de PR.

## Admission budgétaire des appels payants (candidat, non actif sur main)

Avant `openai/codex-action`, le workflow privé impose désormais **trois conditions distinctes** :

- `SMARTSVG_AUTOMATION_ENABLED=true` : activation explicite (variable GitHub Actions déjà prévue).
- `SMARTSVG_MONTHLY_API_BUDGET_USD` : montant mensuel déclaré strictement positif (ex. `10` ou `12.50`). **Déclaration, pas limite de facturation effectivement appliquée.** Un plafond de dépenses côté fournisseur doit être configuré et vérifié séparément avant activation.
- `SMARTSVG_MAX_PAID_RUNS_PER_DAY` : nombre entier entre 1 et 24. Le workflow compte tous ses runs créés dans la journée UTC (y compris les runs gratuits et le run courant), et refuse un nouveau cycle payant lorsque ce total dépasse le plafond. En cas d'erreur API, de résultat incomplet ou de variable absente, il refuse l'appel.

Le plafond quotidien est **conservateur** : il borne le nombre de runs susceptibles d'appeler Codex, mais pas leur coût réel. Il ne remplace ni un contrôle de facturation du fournisseur, ni la limitation de backlog `TOTAL_OPEN_PRS >= 4` (qui interdit les nouvelles PR fonctionnelles). Aucune variable ni aucun secret n'a été configuré par ce correctif. La version présente sur `main` ne contient pas encore ces protections tant que la PR #13 reste non fusionnée.

## Contrat du précontrôle

### Authenticité des workflows de CI

Un résultat GitHub Actions `success` n'est pas une preuve suffisante : un workflow `workflow_dispatch` modifié sur la branche candidate peut réussir sans lancer les tests. Le précontrôle compare donc les **SHA des blobs** des workflows G0 et CPU entre `main` et le HEAD candidat, puis vérifie l'identifiant GitHub et le chemin du workflow de chaque run retenu. Une divergence ou une métadonnée absente bloque la qualification avec `CI_WORKFLOW_UNTRUSTED`, même si la CI affiche SUCCESS. Cette protection concerne l'identité du workflow, pas la qualité de tous les tests ni une certification du code.

**Bootstrap exceptionnel :** la PR #13 modifie elle-même le workflow G0. Tant que cette version n'est pas sur `main`, elle sera volontairement bloquée par son propre garde-fou. Son intégration initiale nécessite une **revue humaine indépendante et des tests L1 ciblés**, en dehors de ce verdict automatisé. Les futures modifications d'un workflow obligatoire exigent la même procédure de revue mainteneur documentée. Ne pas falsifier la provenance, supprimer la protection ou considérer un statut `BLOCKED` comme une autorisation de fusion.


Entrée : snapshot JSON `schema=1` (PR, compare main...HEAD, runs, reviews, audit comments, second relevé main/HEAD). Production depuis un checkout `main` avec permissions **lecture seule**. Le contrôle rejette par défaut les données absentes, brouillons, PR sur branche fille, conflits, main obsolète, HEAD changé, CI non terminée/non success, approbation périmée ou par l'auteur, absence d'audit favorable. Il exige des workflows `workflow_dispatch` rattachés à la branche et au SHA attendus ; un échec plus récent pour ce même HEAD annule un ancien succès, même si l'événement plus récent est une PR. Les runs plus récents peuvent invalider d'anciens succès.

Sortie : `BLOCKED` + raisons, ou `ELIGIBLE_FOR_MAINTAINER_MERGE_REVIEW` ; `automatic_merge_allowed=false` dans tous les cas.

### Identité et authenticité du verdict indépendant

Le reçu d'audit est **lié au diff précis**, pas seulement au commit candidat. L'auditeur doit vérifier l'inventaire complet de `pulls/<PR>/files`, puis inscrire :

```text
SMARTSVG_AUDIT_V1
PR=<numéro>
HEAD=<SHA du candidat>
BASE=main@<SHA exact de main au moment de la revue>
DIFF_SHA256=<empreinte calculée sur la liste exhaustive des fichiers modifiés>
VERDICT=GO_POUR_REVUE_INTEGRATION
```

L'empreinte est `tools.integration_eligibility.diff_identity(files)`, SHA-256 d'un JSON canonique trié par chemin contenant `filename/status/sha/previous_filename/additions/deletions/changes`. Le précontrôle retourne `diff_sha256` pour comparaison, même si la PR est bloquée ; il ne publie ni image ni contenu des patchs. La valeur doit être recalculée après chaque changement de base ou de HEAD. La liste de fichiers et la base de la PR sont relues avant décision afin de limiter les courses concurrentes.

**Provenance :** le champ `user.login` du commentaire GitHub doit correspondre à celui d'un reviewer indépendant avec `APPROVED` valide sur ce HEAD. Une simple chaîne `VERDICT=GO` écrite par le développeur, un bot ou un tiers non approuvé ne constitue pas une contre-expertise. Si l'auditeur utilise le même compte que l'auteur, la qualification reste bloquée et une seconde identité GitHub est requise ; ne jamais contourner cette condition.



**Pas de fausse preuve :** l'issue de coordination #29 est un journal non autoritaire, pas une signature de validation. Même avec un commentaire `GO_POUR_REVUE_INTEGRATION`, une approbation GitHub indépendante reste nécessaire. Comme le développeur et les tâches opèrent actuellement sur le compte `frenndak`, une revue réellement indépendante par un **autre compte humain** devra être obtenue pour franchir ce garde-fou. S'il n'est pas disponible, laisser `BLOCKED`, ne pas créer de fausse approbation ni contourner ce contrôle.

### Essai local

```bash
python -m unittest tests.test_integration_eligibility tests.test_private_agent_protected_paths -v
python tools/integration_eligibility.py /chemin/vers/snapshot.json
```

Le retour non nul indique un refus de qualification, pas une erreur de CI à masquer.

### Retour arrière

La PR #13 reste distincte et pourra être revert sans toucher aux moteurs, projets, archives ou modèles : supprimer les fichiers `tools/integration_eligibility.py`, `tests/test_integration_eligibility.py`, `.github/workflows/integration-preflight.yml`, cette documentation et restaurer la version précédente du garde-fou d'automatisation si nécessaire.

## Périmètre explicitement non couvert

Pas de tests réels Windows/ComfyUI/RTX 3070, Design Space ou Cricut Explore 5 produits par ce protocole. Pas de publication open source, pas de réglage automatique des secrets GitHub ni de facturation nouvelle. Aucune revendication de qualité de fabrication.
