# V35-COV-16 — Réconciliation sémantique des six exceptions et dix exigences G6/G9

**Date : 13 novembre 2026.** **Statut : REVUE DE CONCEPTION CANDIDATE / NON ADOPTÉE** ; V3.4 ACTIVE. Sources V3.4 `02_VISION_PARCOURS.md`, `03_ARCHITECTURE_ADR.md`, `06_COMMAND_BUS.md`, `07_UX_EXPRESS_NAVIGATION.md` et V3.3 `ROADMAP_TRACEABILITY_v3_3.md`, `ROADMAP_HERITAGE_v3_3.md`. Audit précédent : [COV-04](COVERAGE_SCENARIOS_02_04.md), [COV-05B](COVERAGE_SCENARIOS_05_08_ARBITRAGE.md), [COV-10](COV10_G6_G9_SEMANTIC_RECOVERY.md), [COV-10C](COV10C_V1_TEXT_EXPORT_PORTS.md).

## 1. Méthode : trois degrés de preuve différents

1. `EXPLICIT_SOURCE` : ticket cité directement par la ligne du micro-lot historique V3.4 ; conserve le total **431/437**.
2. `REVIEWED_CANDIDATE` : proposition de propriétaire après lecture du critère et de son impact ; ne transforme pas rétrospectivement l'historique en lien explicite.
3. `ADOPTED_V35` : correspondance acceptée dans une PR documentaire revue et la future gouvernance, avec DoD de chaque consommateur ; **aucune des 6+10 exceptions n'a encore ce statut**.

Cette séparation évite le faux raisonnement « les 437 tests sont affectés donc les 437 fonctionnalités sont implémentées ». Les critères restent des **recettes de spécification**, pas des tests exécutés.

## 2. Six scénarios sans ticket explicite : arbitrage technique proposé

| Scénario original | Critère exact à préserver | Premier propriétaire V3.5 **candidat** | DoD de liaison et cas négatif ; preuve reste NOT_RUN |
|---|---|---|---|
| `T-V34-03-16` | Une découpe réelle n'est `PASS` physique qu'avec mesures/protocole | **W04 + W00** (V34-012 fabrication ; V34-003 preuves **à vérifier**), pas le seul prévol statique | Ajouter explicitement une recette de campagne : dimensions cibles/mesurées, version DS, matière/tapis/outil, responsable humain ; `UNKNOWN` si une preuve manque |
| `T-V34-06-22` | 50 sujets partitionnés en packs V2, aucun pack V1 >32, IDs uniques | **W02 + W12** (V34-036 orchestration, V34-035 Undo groupé, et contrat V2 à décider) | Simuler 50 identités, maximum 32 masques par archive V1 si cette limite s'applique, aucune migration V2 automatique ; rejeter IDs doublons et dépassement, tester reprise |
| `T-V34-06-24` | Undo/Redo ne convertit jamais `SCORE/DRAW/PRINT` en `CUT` | **W02 + W04** (V34-035 Undo ; V34-032 validation commandes) | Snapshot avant/après Undo exact pour opérations et positions ; refuser texte/trait/color déduisant CUT |
| `T-V34-06-25` | Rapport expurgé, aucun chemin privé ni média ou poids IA | **W00 + W15**, rapport/transfert (V34-040 et politique confidentialité) | Fixture contenant chemin privé, EXIF, prompt, poids modèles ; contrôle redaction/export sans fichier non autorisé, aucun réseau |
| `T-V34-07-16` | Undo groupé Score+Cut n'annule jamais une opération machine réelle | **W02 + W04** (V34-038 UX Undo, V34-035 historique, V34-049 légende) | Undo du projet rend exactement les deux rôles, affiche « découpe déjà effectuée non annulable », aucun statut PHYSICAL faux |
| `T-V34-07-25` | 100 navigations, p95 moins de 150 ms **mesuré** | **W13 + W15** (V34-041 shell, V34-046 navigation) | Script de mesure Windows réel 100 navigations au SHA avec p95, 1366×768/DPI 200 % et focus, si >150 ms le critère échoue ; ne pas inventer le résultat |

**Décision contradictoire :** six nouveaux tickets V35 autonomes seraient probablement redondants avec W02/W04/W12/W13/W15. **Recommandation actuelle** : réemployer les tickets existants comme responsabilités **candidates**, puis ajouter dans V3.5 un registre de recettes transversales et leurs preuves; proposer un ticket nouveau **uniquement** si un contrat technique réellement absent émerge. Cela respecte la V3.4 historique et le plafond WIP, sans cacher les 6 liens manquants.

## 3. Les dix exigences sans ticket V34 : regroupement technique, obligations individualisées

| ID | Exigence source à garantir | Propriétaire V3.5 candidat | Gate sémantique à vérifier avant la promotion |
|---|---|---|---|
| **S-036** | Polices converties en tracés sans substitution silencieuse | **W10** typographie, ADR schéma texte | Source textuelle éditable conservée + SVG rendu/tracé vérifié, glyphes sans substitution |
| **S-064** | Police/licence : rendu reproductible ou avertissement | **W10** prévol typographique | Absence de police et licence inconnue = `UNKNOWN/BLOCKED`, pas de faux PASS |
| **S-092** | Prévisualisation de police, caractères FR et fonte absente | **W10 + W13** UI texte | Aperçu réel et avertissements de glyphes, focus/clavier et relecture |
| **R33-028** | Visibilité des licences/glyphes manquants F09 G6–G8 | **W10 + W03** gate export transversal | Unité et export dessin/texte cohérents, provenance et licence maintenues |
| **S-037** | Trois gabarits métier réellement testés | **W11** étiquette/topper/carte | Trois instanciations et reouvertures de projet, non confondues avec `folded_card/open_tray` |
| **S-021** | OCR affiche, texte préservé/averti | **W16 OCR** facultatif, support W14 si IA | Proposition non-mutante et correction, fallback manuel, pas de remplacement sans accord |
| **S-047** | OCR sur couverture, texte vérifié avant remplacement | **W16 OCR** même port que S-021 | Cas d'usage couverture et seuils incertitude propres, fixture et diff |
| **S-044** | Diorama multi-plans, prototype réel assemblé | **W16 diorama** (dépend W04/W11) | Géométrie, ordre, alignement et prototype matériel; simulation non suffisante |
| **S-066** | Diorama à quatre plans alignables avec tolérances mesurées | **W16 diorama** | Quatre plans identifiés, repères de pose, test d'alignement et mesures réelles |
| **S-099** | Guide de montage diorama dans l'UI avec prototype mesuré | **W16 diorama + W13** | Instructions hors ligne, ordre/couches/épaisseur, confirmation physique distincte |

**Inversion corrigée** : `S-037` est un gabarit métier, `S-064` une exigence de typographie/licence. `R33-028` ne doit jamais devenir un gate de diorama par une simple erreur de tableau. COV-10B a été corrigé et les normes V3.3 sont inchangées.

## 4. Décision P0/P1/P2 et non-glissement

- **P0 transversal de couverture** : aucune des seize obligations ne doit disparaître ; vérifier les responsabilités et scénarios, l'existence d'une API réelle et le statut des tests. Ce P0 **n'oblige pas à livrer les seize fonctions avant le jalon A**.
- **P1 G6** : typo et modèles métiers restent dans les domaines W10/W11 ; pas de moteur de typographie parallèle, pas de schéma V2 imposé sans justification.
- **P2 G9** : OCR/diorama et montage réel sont des obligations **historiquement prévues** (non une invention V3.5). Elles peuvent être jalonnées ultérieurement **avec décision explicite et trace de leurs DoD**, mais ne sont pas effacées.
- **Preuves** : texte/canevas/undo, CPU/GPU, Design Space et montage physique ont des axes indépendants. `NOT_RUN` pour toutes les réalisations de cette fiche.

## 5. Scénarios adversariaux et cas de récupération

- **Adversarial A** : un rapport `S-064` avec police à licence inconnue pourrait sembler identique visuellement : refuser le PASS de redistribution malgré un rendu correct.
- **Adversarial B** : une boîte `open_tray` à 4 languettes n'est pas un diorama à 4 plans : démontrer la différence via 4 `plane_id`, ordre et preuve d'assemblage.
- **Adversarial C** : le projet V1 permet seulement les 3 valeurs `Artifact.use` ; ne pas détourner `editable_svg` pour un résultat multicouche CUT lors de cette réconciliation.
- **Adversarial D** : une application peut annuler son historique sans pouvoir annuler une découpe déjà effectuée ; test QA doit refuser l'équivalence.
- **Adversarial E** : le nombre de scénarios liés à des tickets ne prouve pas le nombre de tests passés ; un lien de planning reste un lien de planning.
- **Recovery** : disque plein et revision CAS conflictuelle doivent laisser source/image/masque intacts ; OCR absent, carte/diorama malformé et GPU OOM reviennent aux états manuels sans mutation; faux SUCCESS interdit.

## 6. Prochaine étape après revue

Ces **16 décisions candidates** peuvent maintenant servir de point de départ à l'arbitrage de leur propriétaire normatif V35. Il reste à **relire individuellement les DoD des tickets et les critères V3.3 complets** pour une adoption réelle, puis à donner une décision personnelle à chaque UX A01–E20 et à chaque opportunité O-001..O-033, sans remplacement des 437 assertions.

**Résultat exact** : 6/6 scénarios ont une **proposition de propriétaire**, 10/10 exigences G6/G9 ont un **responsable de parcours proposé**. Les valeurs restent **431/437 explicites historiques** et **10/10 sans ticket V34 direct** ; `ADOPTED_V35=0` pour ces seize cas à cette étape. Aucune PR normative, merge, modification de code, test Windows/Design Space/physique ou changement de tâche V3.4.
