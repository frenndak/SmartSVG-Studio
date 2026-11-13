# COV-09 — Liens scénarios→tickets, lots V3.4 21–22

13/11/2026 — **CANDIDAT DOCUMENTAIRE**, V3.4 demeure ACTIVE. Sources historiques lues sur main : `21_WINDOWS_OFFLINE_RECOVERY.md` blob `8700846208315f405b7f60266fabf8181e160ff4`, `22_VALIDATION_CORPUS_PREUVES.md` blob `6fa98816ae2a8048471f6625d3c099df171fb0fb`. Références explicites extraites de la colonne « Ticket » (lot 21) ou « Tickets V34 existants » (lot 22), sans inférence par numéro. Les assertions intégrales demeurent dans `SCENARIOS_V34_17_22.md`.

| ID source | Tickets explicitement cités | Nature de la preuve |
|---|---|---|
| T-V34-21-01 | V34-019 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-21-02 | V34-020, V34-139 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-21-03 | V34-023, V34-140 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-21-04 | V34-139 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-21-05 | V34-139 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-21-06 | V34-139, V34-022 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-21-07 | V34-139, V34-022 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-21-08 | V34-022, V34-140 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-21-09 | V34-024, V34-140 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-21-10 | V34-139 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-22-01 | V34-005, V34-129, V34-130 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-22-02 | V34-018, V34-022, V34-132 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-22-03 | V34-022, V34-140 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-22-04 | V34-132, V34-133 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-22-05 | V34-129, V34-134, V34-135 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-22-06 | V34-122, V34-129, V34-130 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-22-07 | V34-124, V34-129, V34-135 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-22-08 | V34-106, V34-109, V34-126, V34-127, V34-128 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-22-09 | V34-111, V34-120, V34-124, V34-130 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-22-10 | V34-124, V34-128 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-22-11 | V34-074, V34-134, V34-135 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-22-12 | V34-078, V34-079, V34-086, V34-140 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-22-13 | V34-136, V34-137, V34-138 | PLANIFICATION_EXPLICITE, NON_TESTÉ |
| T-V34-22-14 | V34-019, V34-020, V34-139, V34-140 | PLANIFICATION_EXPLICITE, NON_TESTÉ |

## Qualification et contre-expertise

**24/24 scénarios** (10+14) possèdent au moins un ticket explicitement cité, **0 exception textuelle**. Cette propriété est uniquement syntaxique ; les liens sémantiques aux 141 exigences, les DoD et la correspondance au code Windows courant restent à vérifier. Aucun PASS n'est inféré.

**Lot 21 — GARDER / AMÉLIORER :** distribution Windows indépendante de ComfyUI, installation et rollback logiciel séparés du recovery projet. Le bootstrap `V34-019` ne prouve pas l'écriture CAS `V34-018/022`. Réutiliser `project_recovery.py` et les backups existants ; refuser un second writer. Démarrage manuel sans `torch`/ComfyUI ni réseau. Installer depuis une source connue avec provenance et hash : SHA seul n'authentifie pas l'éditeur. Ne pas imposer Qt/Tauri/MSI sans benchmark. **Risques** : verrou NTFS, antivirus, OneDrive, Unicode, disque plein, paquet falsifié, mises à jour partielles, fuite du diagnostic. Alternative plus simple : distribution locale manuelle versionnée avant service d'update. Réversibilité : ancienne installation réactivable, fichiers utilisateur inchangés.

**Lot 22 — GARDER / RACCORDER :** réutiliser le registre de preuve `V34-003`, pas de second dashboard de certification. Les quatre sorties sont **PNG Print Then Cut / SVG Basic Cut / SVG CUT multicouche / SVG éditable**, non interchangeables ; `SCORE` n'est pas implicitement `CUT`. Les 14 tests transversaux sont des protocoles, non 14 gates ni 14 succès. Les scénarios 06/07/09/10 exigent Design Space/physique séparés ; pas de machine-ready par prévol XML. IA locale facultative avec licence, hash, consentement et repli CPU. Alternative rejetée : « tests unitaires verts ⇒ Cricut certifiée ».

**Parcours novice** : installation offline → projet synthétique V1 → aperçu/édition manuelle → sauvegarde → export de rôle choisi → guide de transfert manuel, puis vérification dans Design Space par l'utilisateur. **Expert** : inspecter code/package SHA, version, état CAS/backup, capacités KNOWN/UNKNOWN, diagnostics expurgés, protocole et preuve par axe. UI : un seul espace Express/Expert, erreurs FR avec cause/action/état conservé, clavier/focus, 1366×768 et DPI 200 % à tester sur Windows ; annulation avant activation, confirmation pour recovery/écriture externe. Aucun nouveau panneau Smart X.

**Contrats de conception** : source de vérité = projet `.smartsvg` V1, writer/CAS existants ; package Windows versionné séparé des projets/modèles/exports ; récupération sous lock avec empreinte attendue ; pas de migration V2 implicite ; résultats de tests = `test_id,ticket_id,requirement_id,code_sha,fixture_sha,environment,axis,result,evidence_ref,limitations` via `V34-003`. Résultats par axe indépendants : auto/Windows/GPU/Design Space/physique. Le guide d'installation et les logs ne contiennent ni chemin personnel complet, ni média, ni secrets. Les seuils de latence, RAM/VRAM et tolérance mm doivent être pré-déclarés puis mesurés.

**Tests positifs futurs** : T21-01 démarrage natif avec modules ComfyUI interdits, puis save/reload V1 mesuré séparément ; T21-06 rollback paquet et empreintes des données inchangées ; T22-01 quatre exports distincts ; T22-08 boîte 80×50×30 mm et CUT/SCORE distincts ; T22-13 105 projets et CSV hostile. **Négatifs futurs** : (1) paquet SHA incorrect/provenance inconnue → refus sans activation ; (2) coupure en staging + binaire verrouillé → version saine conservée ; (3) ZIP corrompu ou pending backup → aucune restauration silencieuse ; (4) DNS/HTTP interceptés au démarrage → zéro requête ; (5) CSV formule → chaîne littérale ; (6) stale CAS ou job annulé → zéro mutation/duplication. Tests d'annulation, concurrence, crash et rollback sont **NOT_RUN**. Fixtures synthétiques C1–C5, terrain privé C6 non publié.

**Découpage TDD à transmettre au producteur seulement après promotion :** (A) fixtures import/boot + assertions d'absence de dépendances ; (B) CAS/recovery et erreurs Windows ; (C) package/rollback et provenance ; (D) quatre rôles d'exports et géométrie ; (E) E2E Design Space et coupons physiques sous protocoles datés. Fichiers historiques candidats du lot 21 : `engine/smartsvg_core/project_recovery.py`, `project_archive.py`, `engine/__init__.py`, tests recovery ; leur état courant et les consommateurs doivent être revérifiés avant toute modification. **Aucun code produit dans cette tâche.**

## Audit 25 critères (limité à COV-09)

01–06 : 24 IDs et tickets explicites vérifiés, inventaire global 24 lots/141 exigences/140 tickets/80 UX/437 scénarios conservé ; pas de qualification globale ni HEAD main autoritatif. 07–09 : CAS/V1/float32, quatre exports, KNOWN/UNKNOWN et CUT/SCORE maintenus, non exécutés. 10–12 : parcours novice/expert, focus, clavier, 1366×768/DPI 200 % spécifiés ; UI Windows NOT_RUN. 13 : crash, annulation, concurrence, rollback scénarisés, NOT_RUN. 14 : IA optionnelle/licences/consentement préservés, GPU NOT_RUN. 15–16 : raster/vecteur non modifiés par ce rattachement, **N/A pour l'extraction textuelle**, tests de ces domaines demeurent dus. 17 : bibliothèque/CSV/planche couverts par protocoles transversaux, E2E NOT_RUN. 18–19 : Smart Delivery et #141 non modifiés, **N/A à cette qualification de tickets**, arbitrage exhaustif toujours ouvert. 20 : métriques seulement à mesurer. 21 : sécurité/licences et confidentialité sans nouvelles ressources externes. 22–25 : branche documentaire seule, pas de merge/AGENTS/code/tâche, pas de nouveau ticket, promotion interdite, audit anti-perte conservé.

**Gaps non résolus :** dix exigences G6/G9 sans ticket V34 direct ; T-V34-03-16 sans propriétaire explicite ; cinq arbitrages COV-05B ; sémantique des 437 scénarios et 25 critères non certifiée. **Prochaine action unique :** COV-10, contre-expertise sémantique des 10 exigences G6/G9, avec critères exacts et propositions de rattachement V3.5 sans renuméroter V34.
