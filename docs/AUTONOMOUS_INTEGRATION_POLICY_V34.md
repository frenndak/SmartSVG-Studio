# SmartSVG V3.4 — protocole d'intégration autonome bornée (R1)

**Décision du propriétaire : 5 novembre 2026.** Activation effective seulement après fusion de la PR de gouvernance contenant ce document **ET** présence sur `main` de la ligne exacte `AUTONOMOUS_MERGE_V34=ENABLED` dans `.automation/READY` **ET** correspondance de `AGENTS.md`. Si une condition manque, le planificateur revient au régime DRAFT-only.

## 1. Autorité et périmètre

Le propriétaire autorise explicitement la tâche horaire SmartSVG V3.4 déjà existante à soumettre, contre-expertiser puis fusionner **sans validation humaine à chaque PR** les seuls micro-lots de code admissibles. Pas d'autre tâche parallèle requise. Cette décision ne change pas la visibilité publique du dépôt ni les règles GitHub; aucune protection de branche, review obligatoire, secret ou droit de dépôt ne peut être contourné. Une revue adversariale par la tâche n'est **pas** une revue GitHub `APPROVED` indépendante.

Un candidat auto-fusionnable doit être une PR vers `main` dans **ce même dépôt** `frenndak/SmartSVG-Studio`, ouverte par le compte propriétaire `frenndak` ou par l'identité d'automatisation déjà autorisée et effectivement vérifiable (ne jamais deviner une identité). Pas de fork, pas de cible extérieure, pas de PR d'auteur inconnu. Branches PR seulement, jamais de push direct sur `main`.

**Chemins autorisés pour l'autofusion :** uniquement du code fonctionnel sous `engine/**`, tests sous `tests/**` ou `engine/tests/**`, scripts techniques locaux sous `tools/**`, et fixtures synthétiques sous `examples/synthetic/**`, **sauf les exceptions suivantes**. Si une PR inclut un seul fichier hors périmètre, elle devient `MANUAL_GOVERNANCE_REVIEW`.

**Chemins et types exclus de l'autofusion, même si un test est vert :** `AGENTS.md`, `.automation/**`, `.github/**`, `docs/**`, `source-releases/**`, fichiers racine, baselines/roadmaps gelées, artefacts ZIP ou binaires, installation/packaging/distribution, `engine/requirements.txt`, dépendances et lockfiles, secrets/jetons, configuration de droits, publication/versionnement, mécanismes d'intégrité/admission et leurs tests (dont `tools/verify_source_integrity.py`, `tools/validate_release_archive.py`, `tools/import_release_archive.py`, `tools/verify_v21152_manifest.py`, `tests/test_governance_owner_delegation.py`, `tests/test_release_archive_gate.py`, `tests/test_release_import.py`, `tests/test_v21152_manifest.py`, `tests/test_private_workflow_routing.py`), ainsi que toute désactivation de contrôle de sécurité, modification de politique, téléversement réseau non prévu ou envoi de données utilisateur vers l'extérieur. Pas de nouvelles dépendances, de changement de format `.smartsvg`, ni d'évolution destructive de contrat sans procédure et approbation distinctes.

Cette autorisation est limitée à **un micro-lot code + éventuellement un correctif directement lié**, avec diff proportionné et tests. Une simple nouvelle interface graphique ne prouve ni la découpe Cricut physique ni une exécution GPU/Windows. Ne jamais certifier ces environnements sans essais réels.

## 2. Protocole en deux cycles distincts

**Cycle A — production :** relire `main`, `AGENTS.md`, `.automation/READY`, ce document, la roadmap V3.4, les PR ouvertes et les issues P0/P1; choisir un lot, créer/mettre à jour une branche et une PR initialement DRAFT, tests et scénarios négatifs inclus; inscrire dans la PR le ticket, le périmètre, les risques, les commandes/tests et la réversibilité. Aucun merge de ce code pendant le **cycle producteur**.

**Cycle B (ou ultérieur) — contre-expertise adversariale différée :** lors d'une nouvelle exécution du planificateur, relire **depuis GitHub** le diff complet, code consommateur, revue éventuelle, ancien et nouveau `main`, SHA HEAD exact, chevauchements, CI et logs. S'imposer une contre-expertise indépendante de la narration du cycle producteur : rechercher régressions, failles de sécurité, pertes de données, mutations, incohérences de contrat, tests manquants ou fausse confiance. Documenter un verdict factuel (aucune pseudo-approbation `APPROVED`). Seules les PR dont le HEAD reste **identique** après cette contre-expertise sont éligibles. Si correctif/HEAD évolue, recommencer une qualification et un cycle de revue distinct; ne pas réutiliser la revue du HEAD précédent.

**Au plus une PR auto-fusionnée par cycle**, uniquement via `squash`, avec `expected_head_sha` strict et vérification immédiatement préalable du SHA de `main`. Si `main` a changé depuis les preuves, recalculer la mergeabilité, le diff, les tests d'intégration pertinents et le risque; si nécessaire, réconcilier la branche, rerun CI et différer. Ne pas assimiler `behind>0` à un conflit automatique; mais ne pas ignorer les conflits ou la divergence.

## 3. Conditions bloquantes avant chaque fusion (fail-closed)

Toutes les conditions doivent être **démontrées**, pas inférées :
1. Autorité actuelle : `AGENTS.md` et `.automation/READY` concordants, opt-in exact activé, dépôt public attendu, aucun stop propriétaire, aucune règle GitHub inconnue à contourner.
2. PR admissible selon §1; HEAD SHA complet et base `main` courants, état `mergeable=true` confirmé après rafraîchissement, revue GitHub sans `CHANGES_REQUESTED` non résolu, aucune exigence de review obligatoire non satisfaite. Si une API protection renvoie 403, **ne pas prétendre que le dépôt n'a pas de protection** : GitHub décide et le connecteur doit s'arrêter à toute erreur de permission/protection.
3. Aucun défaut connu P0/P1 non résolu touchant la PR, aucun secret/donnée privée, suppression de test, assertion affaiblie, check supprimé, fichier protégé, changement destructif ni diffusion non prévue.
4. Preuve CI sur le HEAD exact : **G0 Admission Tests** `completed/success`, **Public read-only preflight** `completed/success`, tous les jobs requis/relevants `completed/success` avec étapes obligatoires exécutées. Une conclusion `success` contenant un test pertinent `SKIPPED` n'est PAS un PASS; rechercher dans logs/steps la commande et le cas vraiment exécutés. Pour tout changement `engine/**` ou nécessitant CPU, exiger `Live Engine CPU Smoke` `completed/success`, et tests fonctionnels ciblés réellement réussis (NumPy/Pillow si nécessaires); aucune validation runtime seulement théorique. Un `skipped` admis dans G0 n'est couvert que si **le même test** est effectivement PASS dans un autre job sur le même HEAD.
5. Une PR portant seulement sur `tests/**` ou `tools/**` nécessite des tests ciblés pertinents et des workflows réellement déclenchés pour ce HEAD; pas de passe-droit parce qu'un workflow n'a pas été programmé. `QUEUED/PENDING/CANCELLED/TIMED_OUT/FAILURE/UNKNOWN` interdisent la fusion.
6. Réversibilité : squash clairement identifié, procédure de revert par PR et risque de données évalué. Ne pas fusionner un changement irréversible ou une migration exigeant sauvegarde sans l'autorisation distincte nécessaire.

**Toute condition absente = NO_MERGE**, classifier `NEEDS_CI`, `FIX_REQUIRED`, `MANUAL_GOVERNANCE_REVIEW`, `BLOCKED_GITHUB_PROTECTION` ou `UNVERIFIED`. Ne jamais utiliser admin bypass, force-push sur main, auto-approve, token alternatif, changement de règles, fausse CI ou suppression de tests pour accélérer.

## 4. Post-fusion et anti-embouteillage

Après fusion, revérifier GitHub `closed+merged`, SHA du nouveau `main`, et lancement puis verdict du **G0 push post-merge** sur le SHA de `main` (et autres checks pertinents disponibles). Tant que ce verdict reste `pending`, ne pas fusionner une autre PR. S'il échoue, **geler les intégrations** et examiner la cause ; préparer un revert sur branche/PR avec CI et contrôle des changements intervenus, sans annuler en aveugle des données utilisateur ni contourner les protections. Une PR de revert qui traverse un chemin protégé exige revue de gouvernance distincte.

En cas de WIP>=4, qualifier les PR existantes et intégrer au plus une PR admissible plutôt que déclarer une impasse. Les PR non admissibles reçoivent un motif précis et une réparation reproductible, sans commentaire identique répété. En cas de panne DNS/git locale, utiliser les connecteurs GitHub pour inspecter les SHAs, diffs et logs; ne pas prétendre exécuter NumPy ou une suite locale si seul le connecteur est disponible.

Noter dans l'issue de coordination #29 **uniquement un changement matériel** : PR/HEAD/base, tests réellement exécutés et `SKIPPED`, checks exact-head, verdict hostile, merge/revert SHA, résultat G0 post-merge, statut du lot `SPECIFIE/IMPLEMENTE/TESTE/INTEGRE`, prochain lot. Ne jamais clore automatiquement une issue plus large que la tranche livrée.

## 5. Désactivation et réversibilité

Le propriétaire peut révoquer l'opt-in en retirant `AUTONOMOUS_MERGE_V34=ENABLED` de `.automation/READY` via une modification de gouvernance autorisée, ou en arrêtant la tâche planifiée. Une contradiction entre sources rétablit immédiatement DRAFT-only. Une modification de ce document ou de la gouvernance elle-même est **toujours exclue** de l'autofusion; elle exige une session propriétaire spécifique. Aucun privilège GitHub supplémentaire ni nouvelle tâche payante n'est créé par ce protocole.
