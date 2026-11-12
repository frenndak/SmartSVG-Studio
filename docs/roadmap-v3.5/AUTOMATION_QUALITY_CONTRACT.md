# SmartSVG V3.5 — Contrat d'exhaustivité de la tâche horaire (anti-régression R3)

**Statut :** document de préparation NON NORMATIF. Source de référence de la tâche d'architecture, en complément de la mission actuelle et des documents historiques ; ne remplace ni AGENTS.md ni les contrôles GitHub. Objectif : prouver qu'aucune réduction de longueur de prompt ne réduit les vérifications.

## 1. Tableau d'invariants à contrôler

| # | Obligation héritée ou renforcée | Source de vérité | Preuve exigée avant de clore la conception |
|---:|---|---|---|
| 01 | Architecture V3.4 : **24 lots**, zéro disparition ou contradiction non documentée | V3.4 README + 24 lots | 24/24 liens et décisions V3.5 dans matrice de couverture |
| 02 | **141 exigences historiques** intactes (101 S, 40 R33) | MASTER/COVERAGE/HERITAGE V3.3 + V3.4 lot 23 | 141/141 IDs et critères conservés, liens bidirectionnels |
| 03 | **140 tickets V34** sans renumérotation ni perte de DoD | V3.4 lot 23 | 140/140 tickets classés et nouveaux V35 seulement si nouveaux |
| 04 | **80 fonctions UX** A16/B14/C18/D12/E20 | issue #134 + INHERITANCE_REGISTER | 80/80 audits comparés, décisions et localisations V3.5 par ID |
| 05 | **437 scénarios** de conception V3.4 non équivalents à des tests exécutés | V3.4 lots et README | Inventaire ID par ID à produire ; aucune fausse affirmation PASS |
| 06 | Progrès réel vs documentation | main, PR, CI, Windows, GPU, Design Space et Cricut | Statuts indépendants, preuve exact HEAD ou NON VÉRIFIÉ |
| 07 | Un seul état projet, identities, SHA CAS et writer ; source originale et masques float32 préservés | V3.4 lots 05/06/10/18, code actuel | Interfaces et scénario négatif de conflit/rollback |
| 08 | **Quatre exports DISTINCTS** PNG PTC, SVG CUT basic, CUT multicouche, SVG éditable | AGENTS.md et lot 17 | Pas de réétiquetage V1 ; type, géométrie, dimensions, provenance et QA |
| 09 | Cut/Score/Draw/Print/Foil = opérations ; Explore 5 réelle, Design Space guidé | V3.4 lots 14–17/22 | Capacité KNOWN/UNKNOWN, aucune commande machine inventée |
| 10 | Express-first, parcours de découverte→geste→retour→correction→reprise | #134 et annexe UX/UI V3.4 | Débutant et expert, friction/choix réduits, erreurs actionnables |
| 11 | Canvas dynamique, clic/lasso/pinceau, panneau contextuel, poignées, souris et raccourcis | #134 A/B/E ; V3.4 lots 07/18 | Modèle d'interaction explicite, Undo/Redo, aperçu non mutant |
| 12 | Accessibilité/clavier/focus, petit écran 1366×768, zoom DPI 200 %, contraste/motion réduite | #134 + UX annex | Tests Windows UI futurs détaillés, sans prétendre testés |
| 13 | Annulation, fermeture, multitâche, stale result, récupération, corruptions et concurrence | V3.4 lots 05–07, 21 | Cas négatifs/unitaires + Windows et rollback par opération |
| 14 | IA **facultative**, locale d'abord, hash/licence/version/provenance/consentement | V3.4 lots 08–11 + #134 D | Budget CPU/VRAM, aucun téléchargement/transfert silencieux, repli vérifiable |
| 15 | Raster : alpha/colorimétrie, anti-halo, upscaling conditionnel sans fausse résolution | V3.4 lot 12 | Tests PNG/ICC/DPI/EXIF, cas haute résolution et limites honnêtes |
| 16 | Vectorisation : chemins, trous, Bézier, microformes, unités mm, SVG safe, qualité | V3.4 lot 13 et #134 A12–A16 | Prévol topologique, provenance, optimisation non destructive |
| 17 | Fabrique, patrons paramétriques, lots 12/24/50, bibliothèque et CSV | V3.4 lots 16, 19–20 | E2E, récupération partielle, révision et ancien comportement préservé |
| 18 | Smart Delivery : premier ZIP avec un export sain, manifeste, SHA, confidentialité, HTML statique | #141 V1/V2 + #142 | Plan, preview, ZIP relu, no-clobber, annulation, pas de fausse certification |
| 19 | Toutes les autres évolutions : Smart Cut Advisor, Weeding, PTC Assistant, DS matrix, Cost, Feedback, CSV/QR, recettes, multi-machines, optimiseur | #141 + #142 | Chaque proposition décidée (retenue/raffinée/reportée/rejetée) avec raison |
| 20 | Performance et UX : métriques mesurables, non inventées | V3.4 UX + lots 11/12/22 | Objectif et protocole, pas de résultat non mesuré |
| 21 | Sécurité publique : aucune donnée personnelle, secret, image non libre, poids modèles ou média propriétaire dans repo | AGENTS.md | Relecture sécurité/licence/stockage et partage |
| 22 | Gouvernance de branche, WIP des PR code et rôle producteur distinct | AGENTS.md + politique V3.4 | Aucun merge doc/AGENTS ni modification tâches dev par l'agent |
| 23 | Anti-doublons de moteurs, stores, tickets, UI et assistants | V3.4 lots 03–09/17/23 + #134 | Différence prouvée vs existant, alternative de fusion évaluée |
| 24 | Vérification avant conclusion et adoption uniquement après revue | V3.4 promotion + #142 | CI/revue documentaire + promotion de gouvernance séparée |
| 25 | Qualité de l'optimisation | Cette checklist | Aucun contrôle omis parce qu'un prompt a été raccourci ; suppression seulement de redondances vérifiables |

## 2. Contrôle par fiche V3.5

Un travail n'est **terminé** que s'il comprend au minimum : **ID et sources réels**, JTBD novice/expert, comparaison V3.4 vs V3.5 et arbitrage contradictoire, architecture et ports réutilisés, contrat entrée/sortie et unités, étapes UI/récupération/Undo, sécurité/licences/privacy/performance, dépendances et priorités, trois scénarios négatifs, jeux synthétiques et tests positifs, crash/annulation/rollback, preuves par axe (auto, UI Windows, CPU/GPU, Design Space, terrain), micro-lots et DoD, statut exact, preuve GitHub et prochaine fiche.

Si le domaine ne comporte pas d'UI ou d'IA, marquer **NON APPLICABLE avec raison**, jamais effacer silencieusement un axe. Les seuils de performance sont des *objectifs à mesurer* tant qu'ils ne sont pas relevés.

### 2.1. Anti-audit superficiel
Une fiche ne compte pas comme terminée si elle ne fait que renommer une fonctionnalité ou recopier une liste ; elle doit résoudre au moins une ambiguïté concrète, expliciter une interface ou un test utile, ou arbitrer une contradiction. Si aucune modification utile : écrire NO_UPDATE sans nouvelle fiche fictive. Une PR documentaire ne prouve pas que le produit est disponible.

### 2.2. Méthode de lecture
L'optimisation utile consiste à **ne pas relire tous les gros fichiers inchangés** quand leur SHA est identique et que leurs parties pertinentes ont déjà été vérifiées. La profondeur de recherche requise pour la fonctionnalité en cours doit, elle, rester complète. Si un changement touche un contrat transversal, relire **tous les consommateurs concernés**, même si le fichier est long.

## 3. Promotion V3.5

La V3.5 reste candidate jusqu'à validation complète des points 01–25, contrôle exhaustif du graphe d'héritage et des 437 scénarios, revue contradictoire de la roadmap entière, PR documentaire approuvée et **changement de gouvernance séparé** autorisé. L'auto-tâche de développement V3.4 ne change pas de cible avant cette promotion.
