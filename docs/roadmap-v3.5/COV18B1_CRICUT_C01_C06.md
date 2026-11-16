# SmartSVG V3.5 — COV-18B-1 : contre-expertise des six capacités Cricut C01–C06

**13 novembre 2026 — DOCUMENT CANDIDAT, NON NORMATIF.** Sources : UX #134, COV17C_UX_C01_C18_SEMANTIC_AUDIT.md, ROADMAP_HERITAGE_v3_3.md, ROADMAP_TRACEABILITY_v3_3.md, V3.4 lots 13–17/22 et code du snapshot main aa0ff9e7d0c53dba3fdc429c02c6198736cfe935. L'objectif est d'approfondir la conception sans réétiqueter des fonctionnalités ou des tests comme livrés.

## 1. Six décisions et sources historiques

| UX | Obligations source et portée | Contre-expertise | Décision candidate |
|---|---|---|---|
| **C01 — Stickers Print Then Cut** | **S-029 P0/G4.1** : contrat PNG/alpha, dépend S-002, **import Design Space contrôlé**. **S-009 P0** : QA Cricut par format, dimensions/trajets précontrôlés. Lot23 : V34-087/129/122 et V34-090/101/129 | Un PNG alpha généré ne démontre ni la dimension imprimée, ni le bleed/les marges, ni la calibration ; un SVG de contrôle n'est pas une deuxième découpe à superposer. | **P0 RACCORDER** : PNG PTC par rôle, unités mm/ppi, alpha, guide DS et preuve d'import séparée |
| **C02 — Vinyle Basic Cut** | **S-030 P0/G4.2** : chemins fermés/géométrie contrôlée ; **S-056 P0** : trous/îlots/segments/offset en mm et coupon réel. Lots 13/14 | Un XML SVG valide peut comporter double coupe, pointe fragile ou tracé ouvert. Aucun seuil matière certain sans coupon physique. | **P0 AMÉLIORER** prévol géométrique ; Smart Weeding en suggestion non destructive |
| **C03 — Multicouche couleur** | **S-011 P0** : fidélité multicouche mesurée ; **S-032 P0** : édition ≠ fabrication ; **S-045 P2/G9** : test concluant de superposition de vinyles | Groupes visuels SVG ≠ calques CUT géométriques ; le V1 Artifact.use ne stocke pas de 4e rôle multicouche CUT. | **P1 RACCORDER**, multicouche comme projection EXTERNE, ordre/alignement/IDs et test physique distinct |
| **C04 — Pochoirs et ponts** | **S-056 P0** : prévol trous/îlots et **S-085 P1** : avertissements de micro-détails sur chemins précis | Détecter un îlot flottant ne génère pas automatiquement des ponts corrects. Largeur sûre inconnue sans matière/profil vérifié. | **P1 RAFFINER**, ponts facultatifs en brouillon et topologie contrôlée |
| **C05 — Centerline et Pen** | **S-032** : profils distincts ; **S-085** : prévol CUT ; **V34-112** du lot 14 : Pen/Draw+Cut, tests T-V34-14-04/16/29 | Le contour d'un SVG coloré ne devient pas une ligne centrale continue. DRAW ≠ CUT ; assignation stylo manuelle dans Design Space. | **P1 étude centerline**, continuité, contrôle des doubles traits et guide par opération |
| **C06 — CUT/SCORE/DRAW/PRINT/FOIL** | **R33-008** : 4 exports distincts ; **S-012 P0** : coupe adaptée à matière réellement testée ; **R33-022** : preuves liées aux versions Design Space | Cinq opérations ne signifient pas cinq formats ni pilotage automatique de la machine. FOIL peut dépendre d'outils inconnus. | **P0 GARDER**, opérations typées, outils/matériaux KNOWN/UNKNOWN/REJECTED et guide manuel |

Les priorités historiques P0/P1/P2 restent intactes. Une décision de présentation UX en P1 ne rétrograde pas S-009/S-029/S-030 P0, et la présence de S-045 P2 n'autorise pas à déclarer une superposition de vinyle validée sans essai.

## 2. Réemploi, contrats et frontières de code

- **V34-129 du lot 17 (L105)** : quatre projections d'export distinctes, tests T-V34-17-01..05 ; il s'agit de projections externes et non d'un élargissement caché du V1.
- **V34-130 (lot 17)** : guide Score/Draw/Foil/Attach et confirmations de dimensions dans Design Space ; aucune commande matérielle sans API prouvée.
- **V34-109 (lot 14)** : prévol PASS/WARN/BLOCKED, mais aucune certification physique automatique.
- **V34-112 (lot 14)** : Pen+Cut, DRAW conservé distinct de CUT ; **V34-113** : FOIL seulement selon matériel connu.
- **V34-097/100/101 (lot 13)** : topologie, sérialiseur SVG sûr et profils Basic/MultiCut ; chemins fermés, unités mm, pas de contenu XML actif.
- **project_contracts.py** (blob 7bfd2d714384717c6ce0bb66659971881bd285c2) : Artifact.use V1 accepte print_then_cut_png, basic_cut_svg, editable_svg. Le quatrième rôle SVG CUT multicouche doit rester une projection métier externe tant qu'une migration n'est pas approuvée.
- **direct_import_v218.py** (blob a49fc10844559d431f393a7f7f56343ebefeb1cf) : SVG de contrôle explicitement DIAGNOSTIC, ne pas superposer au PNG PTC ; pas de pilotage Design Space démontré.
- **layers_v2113.py** (blob 486ca4f980288b55bbe89db7e9203d1f76237d03) : groupes de couleurs éditables, pas un plan de découpe multicouche qualifié.
- **delivery_v21122.py** (blob 98a2580c529f613ca732a69fda5273a317f64daf) : manifeste JSON historique, pas encore le ZIP Smart Delivery. Le pack externe ne doit ni inventer les rôles absents ni déclarer une machine certifiée.

## 3. Parcours utilisateur et micro-lots TDD

**Novice :** choisir son intention réelle (imprimer/découper, vinyle, dessiner), voir seulement les sorties supportées, dimensions, avertissements et étapes manuelles Design Space, puis exporter avec confirmation. En cas d'inconnu matériel, pas de badge de compatibilité garanti.

**Expert :** inspecter source SHA, sujet, coupe, alpha, mm/ppi, profils, épaisseur matière, topologie, calques et ordre, QA par rôle et état distinct local/Design Space/physique. Toute modification graphique passe par brouillon, diff et CAS si le writer connaît le type ; sinon sortie EXTERNE vérifiée.

**Tests candidats — tous NOT_RUN** :
1. PTC PNG avec alpha : refuser image dite détourée mais opaque, mm absents et ajout d'un SVG diagnostic comme seconde coupe ; vérifier l'import DS séparément.
2. Basic Cut avec trous/îlots/pointe : rejeter double coupe, ouverture interdite, autointersection et dimensions NaN ; source préservée.
3. Multicouche 3 couleurs : conserver ordre et transformations, ne pas enregistrer CUT sous editable_svg V1 ; rapport UNKNOWN avant test de superposition.
4. Pochoir : îlot flottant et pont proposé en brouillon ; échec si un pont casse les contours ou s'il manque un seuil matière vérifié.
5. Centerline DRAW : vérifier continuité/double trait, ne pas transformer DRAW en CUT, guide Attacher manuel.
6. Score/Cut/Draw/Print/Foil : tester combinaison typée, rejeter FOIL sans outil, contrôle physique NOT_RUN tant que non fabriqué.
7. Crash, panne disque, annulation, concurrence CAS et entrée SVG active : aucun artefact partiel publié ; précédent projet intact. Profil inconnu = UNKNOWN, non PASS.
8. Interface Windows 1366×768 et DPI 200 %, clavier/focus/motion réduit : tests et chronométrages p50/p95 à réaliser, pas de chiffres inventés.

## 4. Résultat et suite

Six décisions candidate contre-expertisées, **0/6 certifiées**. Les obligations des 24 lots, 141 exigences, 140 tickets, 80 UX, 437 scénarios et contrat qualité 25 axes restent applicables. Aucun code produit, merge, AGENTS ou tâche de développement modifié. Aucun test Windows/RTX/Design Space/coupe physique réalisé.

**Prochaine étape unique COV-18B-2 :** étudier C07–C12 (Smart Cut Advisor, profils, variantes, quatre exports, transfert Design Space, planches) à partir des lots 13–17/19/22 et de Smart Delivery ; puis C13–C18, D/E et revue finale.
