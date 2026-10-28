# SmartSVG V3.4 — Cycle 01 : audit du référentiel, du code et des lacunes

**DRAFT non normatif.** Audit du main fdbda304beb77d97340a8be4dd5c5e9cefde15f4, 28 octobre 2026. Aucun code moteur, aucune archive et aucun fichier de gouvernance modifiés.

## 1. Décision de conception proposée

La V3.3 demeure active. V3.4 ajoute une architecture autonome **incrémentale**, sans réécrire les moteurs fiables. Un seul projet canonique .smartsvg, plusieurs transports (ComfyUI et futur runtime natif). Assistant IA = compréhension, propositions, planification contrôlée ; moteurs métier = calculs déterministes, géométrie et validation. Les opérations de fabrication Cut/Score/Draw/Print Then Cut/Foil ont une sémantique distincte des chemins SVG. Les choix de framework restent ouverts à des prototypes et ADR.

## 2. Sources réellement consultées

| Source | Constat | Limite |
|---|---|---|
| AGENTS.md | Dépôt public intentionnel, V3.3 active, branches/PR draft et chemins protégés | Gouvernance, pas preuve produit |
| README.md | Prototype ComfyUI, Express/Atelier, projets, masques et inspecteur SVG | Démo 12 escargots fictifs ; pas de segmentation IA depuis l'Atelier |
| ROADMAP_MASTER_v3_3.md | 15 familles F01–F15, G0–G9, P01–P10, 40 exigences R33 | Vision et obligations, pas certification |
| ROADMAP_TRACEABILITY_v3_3.md | 101 S + 40 R33, preuves orthogonales | Preuves du code actuel à reconstruire |
| ROADMAP_COVERAGE_v3_3.md | Matrices formats, erreurs, UI, concurrence, sécurité, terrain | Checklist, pas exécution |
| ROADMAP_HERITAGE_v3_3.md | Historique V3.2 intégral | Archive non modifiable |
| ROADMAP_AUDIT_v3_3.md | Historique de publication et CI documentaire | PASS ancien ≠ PASS V3.4 |
| ETAT_ACTUEL_SMARTSVG.md | G1/G2/G3 et limites documentées au 27 octobre | Ne décrit pas toutes les évolutions G3.3e du 28 |
| Code moteur et UI ciblés | Projet, identités, masques, pont HTTP, IA, Atelier | Inventaire ciblé, pas graphe exhaustif |

L'[index exhaustif](HERITAGE_INDEX.md) conserve les 141 dossiers individuels. **Recensement complet ne signifie pas couverture V3.4 complète.**

## 3. Inventaire des autorités existantes

| Domaine | Fichiers existants vérifiés | Rôle / migration envisagée |
|---|---|---|
| Projet | engine/smartsvg_core/project_workspace_g22.py, project_archive.py, project_recovery.py | Espace projet et récupération ; réutiliser, ne pas dupliquer |
| Masques et identité | engine/smartsvg_core/subject_identity_g33e.py, mask_binding_g33e.py, mask_snapshot_g24.py | Liaison identité–masque float32 ; conserver empreintes, révisions et invalidation |
| Transport | engine/project_routes_g22.py | Routes ComfyUI same-origin ; introduire un transport natif séparé |
| IA | engine/smartsvg_ai/provider_v2112.py | Adaptateur registre de nœuds ComfyUI ; prévoir fournisseurs directs avec mode CPU |
| Interface | engine/web/js/smartsvg_express_atelier_preview.html, smartsvg_subject_identity_g33e.mjs | Démo + fonctions réelles sous ComfyUI ; réutiliser les commandes et états |
| Moteurs SVG | engine/smartsvg_vector/, engine/smartsvg_cricut/, engine/smartsvg_quality/ | Inventaire de modules à approfondir ; ne pas présumer toutes les fonctions prêtes |
| Historique | engine/node_v*.py et engine/__init__.py | Maintenir IDs, ports, anciens workflows et sorties pendant migration |

**Écart vérifié :** le HEAD contient une identité de sujet persistante G3.3e, alors que le suivi ETAT_ACTUEL_SMARTSVG.md est principalement au niveau G3.3b. Ne pas ouvrir un ticket qui réimplémente une fonction déjà intégrée sans audit du diff et des preuves.

## 4. Lacunes et risques prioritaires

- **L01 / Autorité :** S-022 et S-046 classent l'app autonome G9/P2 ; la nouvelle ambition la rend transversale. Créer une ADR et des tickets V34, **sans changer la priorité historique**.
- **L02 / Double état :** risque de deux formats projet si l'interface native duplique la logique du workspace ; imposer une autorité métier et deux adaptateurs.
- **L03 / Démo :** 12 escargots fictifs ne constituent pas un vrai parcours image → segmentation → retouche → export.
- **L04 / IA :** provider_v2112 peut demander des poids externes ; hors ligne réel exige disponibilité locale, licence et repli manuel/CPU.
- **L05 / Fabrication :** un SVG ne transmet pas de façon garantie une opération Score dans Design Space ; prévoir calques, manifeste et guide utilisateur.
- **L06 / Preuves :** aucun test Windows/RTX 3070/Design Space/Explore 5 physique ne peut être inféré des tests CI.
- **L07 / Gouvernance :** .automation/BOOTSTRAP.md parle d'un dépôt privé alors que AGENTS.md dit public ; signaler à une PR de gouvernance séparée, ne pas modifier ici.
- **L08 / Modèles :** licences, redistribution, consommation VRAM et installation sans réseau doivent être vérifiées modèle par modèle.
- **L09 / Obsolescence :** chaque rapport doit lier la version du code et les preuves au SHA exact, sans extrapoler depuis un document daté.

## 5. Contrat de données pour la traçabilité — PROPOSITION

~~~json
{
  "requirement_id": "S-023",
  "canonical_source": "docs/ROADMAP_TRACEABILITY_v3_3.md",
  "source_sha": "fdbda304beb77d97340a8be4dd5c5e9cefde15f4",
  "review_status": "HERITEE_A_REEVALUER",
  "v34_specs": ["docs/roadmap-v3.4/01_BASELINE_AUDIT.md"],
  "v34_tickets": ["V34-004"],
  "existing_code": ["engine/smartsvg_core/subject_identity_g33e.py"],
  "proof_axes": {
    "auto": "NON_VERIFIE",
    "windows": "NON_EXECUTE",
    "design_space": "NON_EXECUTE",
    "physical": "NON_EXECUTE"
  }
}
~~~

**Invariants :** IDs source immuables, historique intact, preuve PASS avec SHA+environnement+commande/protocole+résultat, statut de maturité distinct des quatre axes de preuve, N/A justifié, aucune priorité historique modifiée sans ADR. Les liens V34↔S/R33 doivent fonctionner dans les deux sens.

## 6. Événements, erreurs et pseudo-code de spécification

- roadmap.source_changed : le HEAD change ; invalider ou repinner les conclusions.
- roadmap.link_requirement : ajouter une relation bidirectionnelle, refuser les IDs inconnus.
- roadmap.attach_evidence : accepter seulement une preuve contextualisée ; refuser un PASS non sourcé.
- roadmap.conflict_detected : enregistrer une contradiction et ouvrir une ADR.
- roadmap.cycle_completed : marquer achevé uniquement après commit et lecture de vérification.

~~~python
# PSEUDO-CODE DE SPECIFICATION, NON EXECUTE
def append_coverage_delta(registry, proposed, proof):
    assert proposed.requirement_id in registry.canonical_ids
    assert proposed.source_sha == proof.base_sha
    if proof.claim == "PASS":
        require(proof.sha, proof.environment, proof.protocol, proof.result)
    return registry.append_immutable(proposed, proof)
~~~

**UX documentaire :** le mainteneur suit README → index 141 → dossier canonique → spec V34 → ticket → test/proof → PROGRESS. Badges séparés : SPECIFIE, PRESENT_CODE, RACCORDE, QUALIFIE_ENVIRONNEMENT. Un badge ne vaut jamais preuve des autres. L'UI produit finale suivra la même distinction entre aperçu, export, import et fabrication vérifiée.

## 7. Micro-tickets V34 du lot 01

| ID | P | Dépendances V3.3 | Livrables pressentis | Test exact attendu | Preuve / DoD / rollback |
|---|---|---|---|---|---|
| V34-001 | P0 | S-001, S-049, S-051, R33-001, R33-034 | 01_BASELINE_AUDIT.md, provenance SHA | Chaque source existe au HEAD, aucune archive modifiée | Relecture du diff, revert documentaire |
| V34-002 | P0 | S-001..S-101, R33-001..R33-040 | HERITAGE_INDEX.md, futur registre machine lisible | 101 S + 40 R33 uniques, égalité des ensembles source/cible | Parsing vérifiable, liens inverses à enrichir |
| V34-003 | P0 | S-054, S-057, R33-002, R33-022..024, R33-034 | Contrat de preuve versionné | Refuser PASS sans SHA+environnement+protocole ; N/A motivé | Cas positifs/négatifs, zéro fausse certification |
| V34-004 | P0 | S-022, S-046, S-052, S-053, S-063, R33-003..005 | Graphe d'import, ADR migration, interfaces | Un seul projet partagé par runtime natif/ComfyUI ; tests dual-run | Parité et rollback par adaptateur |
| V34-005 | P0 | S-002, S-004, S-024, S-030, R33-008, R33-009, R33-038 | Matrice de non-régression des 4 exports et du projet | Aucun ID/port ancien ni format supprimé sans migration | Fixtures et tests de compatibilité, revert |

**Tous les tickets sont SPECIFIES uniquement.** Les chemins à créer sont des propositions, pas des fichiers déjà implémentés.

## 8. Vérifications et contre-expertise

**Effectivement vérifié :** 101 dossiers S, 40 R33, 141 IDs uniques sans trou ; 40 titres R33 dans le maître ; présence des chemins moteur principaux ; écart G3.3b/G3.3e ; règles de gouvernance lues.

**Non exécuté :** tests Python/JS, CI PR, graphe complet des imports, installation Windows, inférence RTX, import Design Space, rainurage/découpe physique.

**Auto-revue :** (1) titres abrégés ≠ texte canonique ; (2) index exhaustif ≠ traçabilité tickets/tests achevée ; (3) Python présent ≠ indépendance totale ComfyUI ; (4) Score ≠ Cut ; (5) autonomie ne justifie pas la perte des workflows ; (6) les écarts de documentation ne prouvent pas une régression ; (7) aucun modèle IA ne doit être réputé redistribuable sans licence.

## 9. Cycle 02 à préparer

Vision, non-objectifs, personas novice/expert, objectifs mesurables, parcours complets « 12 escargots → stickers » et « boîte carton → Score + Cut », états UX et tests de non-promesse.