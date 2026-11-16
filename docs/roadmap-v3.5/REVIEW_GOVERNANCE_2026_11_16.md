# Contre-revue indépendante de gouvernance — V3.5 — 16 novembre 2026

## Verdict borné

**FAVORABLE pour publier la PR de gouvernance et la soumettre aux contrôles exact-HEAD ; aucune anomalie Critical, Important ou Minor ouverte relevée dans les 13 fichiers examinés.** Ce verdict documentaire n'est ni une fusion, ni une revue GitHub APPROVED, ni un PASS produit, ni la preuve que les prompts externes ont été modifiés. La promotion effective exige encore la revue/CI du HEAD publié, la fusion de gouvernance et le G0 post-merge sur son SHA exact ; G35-14 exige ensuite les deux écritures et leur relecture réelle, sans modification de cadence/activation.

Revue indépendante effectuée sur le checkout local sans métadonnées Git, base annoncée et comparée `37a4cd0f63c9dc78a352a8bab396cf3d47f81a52`, manifeste courant des 13 fichiers, arbre Git de base complet fourni. Aucun outil externe, aucun changement du candidat par le relecteur ; seul ce rapport a été écrit. Les anciens audits de produit ne sont pas rejoués.

## Éléments vérifiés

- L'arbre distant de base fourni n'est pas tronqué. Les contenus locaux correspondent à 1069 blobs inchangés ; huit blobs existants sont modifiés et cinq fichiers ajoutés. Les quatre alias historiques `docs/roadmap-v3-5/Q04P_*`, `Q04Q_*`, `Q04R_*`, `Q04X_*` ne sont pas présents dans ce checkout local : leur conservation dans l'arbre publié reste une postcondition à vérifier par le coordinateur, et n'est pas une suppression autorisée par cette revue. Aucun code produit, workflow, dépendance, archive source ou fichier V3.4/V3.3/V3.2 historique n'est changé dans le delta examiné.
- La politique V35 reprend le texte V34 : seules la cible/version/date, les marqueurs et une section explicite de continuité changent. Les périmètres code-only, exclusions, auteur/dépôt, DRAFT initial, cycle adversarial ultérieur, nouvelle revue après modification de HEAD, max une fusion/cycle, `expected_head_sha`, CI pertinente réellement exécutée au HEAD exact, contrôle de main et G0 post-merge sont préservés. Aucun bypass, faux APPROVED, nouveau privilège externe ou droit de fusion des documents/gardes n'est introduit. La politique historique V34 reste identique à son blob épinglé.
- L'autorisation de la session propriétaire transmise pour cette revue porte sur la finalisation complète puis le remplacement définitif de V3.4 et la continuité bornée du producteur existant ; la proposition la matérialise dans une PR distincte, avec opt-in V34 désactivé et V35 explicitement activé. L'autorisation antérieure seule ou un simple remplacement de chaîne ne serait pas suffisant. Les textes exigent la concordance AGENTS/READY/politique/prompt sur main et restent DRAFT-only en cas de désaccord. Aucun nouveau consentement matériel, réseau, IA ou publication n'est inféré.
- AGENTS, README, MASTER et PLAYBOOK définissent la précédence : référence V3.5 après gouvernance vérifiée, `EXECUTION_STATE.json` seul curseur d'ingénierie, RUN_STATE et PRIORITY_REGISTER photographies historiques. RUN_STATE conserve toutes ses données antérieures et reçoit seulement deux champs de rôle/précédence. L'AST du contrôleur `verify_run_state.py`, hors docstring et affichage, est identique : aucune assertion n'est abaissée pour masquer les anciens champs V3.4.
- Les sept anciens tests de délégation ont le même AST après la substitution explicite V34 vers V35. Trois tests ajoutent la désactivation V34, l'empreinte de la politique historique, l'héritage, le curseur, les deux contrats et l'absence de second producteur. Les autres tests V35 sont inchangés. Les digests des contrats sont définis sur texte UTF-8 avec fins de ligne LF ; le test utilise la lecture texte normalisant les fins de ligne, cohérente avec cette définition et les checkouts Windows CRLF, sans toucher aux empreintes Git des sources historiques.
- Les contrats producteur R11 et revue R4 conservent les 24 lots, 141 critères et DoD parents complets, 140 tickets, 80 UX et 437 scénarios proposés ; les 25 axes, SCN/CST/UXI, quatre sorties, single writer/float32/CAS et CP, consentements séparés IA et preuves matérielles distinctes sont repris. La lecture des parents/contrats complets reste obligatoire. Les 17 SCN/14 CST/18 UXI ne deviennent pas PASS par adoption. Les objectifs de tests utilisateurs, annulation/crash/reprise et mesures restent des protocoles à exécuter.
- Une seule tâche reste productrice. La tâche de conception devient lecture seule et interdit commits, PR, commentaires externes, tickets, changement de prompts/règles et fusion ; elle ne peut pas créer une seconde autorité sur l'ancienne candidate. Le producteur commence par rafraîchir les PR 138/139/140/144 et leurs HEAD/CI ; la photographie des quatre PR n'est pas présentée comme état actuel. WIP code maximum trois, maintenance documentaire séparée, pas de cinquième lot pour contourner un blocage.
- Les deux SHA-256 des bootstraps fournis correspondent aux valeurs d'EXECUTION_STATE. Leur contenu impose la lecture intégrale des contrats versionnés sur main. La comparaison porte sur ces textes locaux et les contrats normatifs du dépôt, pas sur une lecture de l'état réel des deux automatisations. Leur écriture après main/G0 puis readback et reçu « Handoff vérifié » dans la PR fusionnée restent requis avant de déclarer G35-14 clos. Aucun reçu externe fictif n'est inscrit dans main.

## Findings et corrections

| Gravité | Résultat | Correction requise |
|---|---|---|
| Critical | 0 | Aucune dans le périmètre relu. |
| Important | 0 | Aucune dans le périmètre relu. |
| Minor | 0 | Aucune dans le périmètre relu. |

La correction de portabilité CRLF annoncée par le coordinateur avant le gel courant est intégrée à la photographie relue : définition UTF-8/LF dans EXECUTION_STATE et lecture texte des deux contrats dans le test. Elle conserve le sens de l'assertion et n'altère aucun pin historique. Ce n'est pas une anomalie ouverte.

## Vérification locale

Vérifications réalisées avant les tests : correspondance SHA-256 des 13 fichiers avec le manifeste courant ; correspondance des deux bootstraps ; comparaison des 1069 blobs inchangés au tree de base ; diff complet des huit fichiers modifiés ; comparaison V34/V35 de la politique ; contrôle AST des assertions anciennes et du contrôleur ; lecture intégrale des deux nouveaux contrats et de la décision.

**Résultat des tests locaux : PASS — 20 tests, aucun SKIP ni échec.** Rapport présent avant les deux commandes, lancées depuis le checkout de gouvernance avec Python et `PYTHONDONTWRITEBYTECODE=1` :

- `python -m unittest discover -s tests -p 'test_v35_*.py' -v` : dix tests PASS (six provenance Git, quatre intégrité documentaire dont les liens du rapport), 0.377 s.
- `python -m unittest discover -s tests -p 'test_governance_owner_delegation.py' -v` : dix tests PASS, 0.009 s.

Ces tests vérifient les propriétés documentaires et les gardes, pas la sémantique universelle ni le produit.

Les environnements Windows, GPU/RTX, ComfyUI, Design Space, Cricut/coupe et assemblage sont **NOT_RUN par cette revue**. Les résultats de la PR documentaire #146 cités dans la décision sont des reçus amont transmis, pas des tests réexécutés ni une qualification du nouveau HEAD de gouvernance. L'accès GitHub, les protections réelles, la CI exacte, l'arbre publié final et les deux prompts effectifs sont hors vérification locale et doivent être contrôlés par le coordinateur aux étapes prévues. Aucun statut produit aval n'est modifié.

## Empreintes de la photographie relue

SHA-256 du contenu local des 13 fichiers, hors présent rapport ; ces valeurs ne sont pas un SHA de commit ni un remplacement des pins Git historiques.

| Fichier | SHA-256 |
|---|---|
| `AGENTS.md` | `55429180e531ec4e49196fd4282e677a1ca93e1dd744c5f3991daca327b902f7` |
| `.automation/READY` | `5f9cf789078229688e6c0600f78fce491d43d67e2702277a3a5aac9bd8293f54` |
| `tests/test_governance_owner_delegation.py` | `b9ed655c4b076d731b38ddac8fd8c1c0f83bbdac9b798db96764354538a2ddcb` |
| `docs/ROADMAP_PROMOTION_v3_5.md` | `818e861ae0b79ef23393067d5a3abbd42b9ecfb5e5671cc06619c9f82034664b` |
| `docs/AUTONOMOUS_INTEGRATION_POLICY_V35.md` | `3ed30f9dbb7a58ea0bf1a113956f042b3f858942748d8124949b94da1a33ab6f` |
| `docs/roadmap-v3.5/DESIGN_REVIEW_TASK_V35.md` | `36cb8bae9165e6a0f8376f4e133a927722d2af1a92e2a1116e62748473d62941` |
| `docs/roadmap-v3.5/RUN_STATE.json` | `85a532370230e33a2074f3923f6e4ab90ae0f4e421dda2dd7d1766376797e33c` |
| `docs/roadmap-v3.5/EXECUTION_PLAYBOOK.md` | `39d1a48c8cae1fc51b12a0be2765aae66e4f236c02289233e8e908ea078c478c` |
| `docs/roadmap-v3.5/PRODUCER_TASK_V35.md` | `0341a007d1da96e59f0a8b16dde31c10e340580d80e79504a650690bd2c0cea6` |
| `docs/roadmap-v3.5/MASTER_PRIORISE.md` | `7c9b9d23495bf8195e8adc4aa9505aaef319429a686ef88e62f2927c66d233cf` |
| `docs/roadmap-v3.5/README.md` | `e659684a80ca9478522a625f1856f90e11dbf2619e55f282080d5074a601a408` |
| `docs/roadmap-v3.5/verify_run_state.py` | `dd5aa6621411d328da9f38e9ed3e7dbbd7dddd12bbfb29a26bcc4e35fef115da` |
| `docs/roadmap-v3.5/EXECUTION_STATE.json` | `2ba0300d0c6874d6a0d961edf853ebda30669f942292eb99dbbeb93c73a54da2` |
