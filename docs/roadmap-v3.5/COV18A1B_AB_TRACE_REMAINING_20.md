# COV-18A-1b — Complément de traçabilité A/B (20 IDs restants) — 13/11/2026

> **RECTIFICATIF DOCUMENTAIRE DU 13/11/2026 — SUPERSEDED FOR B12/B13 ONLY :** Les hypothèses de rattachement B12→S-021/S-047 et B13→S-064/R33-028 dans ce tableau sont **inversées par rapport aux critères métier**. Utiliser désormais [COV18A3C_B_REMAINING_CORRECTED.md](COV18A3C_B_REMAINING_CORRECTED.md) : **B12 texte→chemins = S-036/S-064/R33-028 ; B13 OCR = S-021/S-047**, et ne pas confondre les dépendances de police après OCR avec un moteur OCR. La présente fiche demeure un historique des hypothèses, non une autorité adoptée.

**Statut : CANDIDAT / NON CERTIFIÉ.** Suite de COV18A1_AB_EXACT_TRACE_FIRST_PASS.md (10 IDs). Cette fiche complète l'inventaire des **20 autres IDs** sans transformer des proximités fonctionnelles en arêtes normatives. Source de contrôle : lot 23 V3.4 sur main, COV17A/B, COV18A et #134. La V3.4 reste ACTIVE.

## 1. Correspondances sémantiques candidates, non adoptées

Les identifiants S ci-dessous sont des **points d'entrée à confronter au critère intégral V3.3** ; les tickets indiqués ne valent comme **liens explicites de source** que lorsque la ligne S correspondante du lot 23 les cite. Le lien UX→S est toujours **inféré**, jamais prétendu canonique. Les tests T-V34-22 sont transversaux et ne remplacent pas les scénarios locaux.

| UX | Point d'entrée historique | Ticket(s) source ou statut | Test transversal de planification | Contradiction / DoD encore ouvert |
|---|---|---|---|---|
| A01 | S-061, S-052 | V34-025, V34-139 ; V34-025, V34-028, V34-018, V34-026 | 22-03 / 22-02 | PNG natif ≠ JPEG/WebP/SVG et lots sûrs |
| A05 | S-080, S-015 | V34-133 ; V34-088, V34-095, V34-076 | 22-04 / 22-05 | pinceau ≠ morphologie du masque et préservation des trous |
| A07 | S-015 | V34-088, V34-095, V34-076 | 22-05 | RGB/alpha, halo et fragments mesurés séparément |
| A10 | S-011, S-060 | V34-098, V34-099, V34-103 ; V34-101, V34-109 | 22-01 | palette algorithmique ≠ pipette/édition de dégradés |
| A11 | S-045, S-032 | V34-100, V34-112 ; V34-098, V34-129, V34-112 | 22-01 | groupe couleur artistique ≠ couche CUT ni ICC |
| A13 | S-034, S-035 | V34-099 ; V34-133 | 22-01 / 22-04 | simplification ≠ édition manuelle des tangentes |
| A14 | S-056 | V34-108, V34-109 | 22-08 | prévol ≠ opérations booléennes persistantes |
| A16 | S-060 | V34-101, V34-109 | 22-01 | score QA ≠ oracle de fidélité, automatisation P2 conservée |
| B01 | S-052, S-035 | V34-025, V34-028, V34-018, V34-026 ; V34-133 | 22-02 / 22-04 | Subject V1 ≠ modèle d'objets universel |
| B02 | S-087, S-035 | V34-133 ; V34-133 | 22-04 | groupes SVG ≠ calques persistés dans V1 |
| B03 | S-028, S-014 | V34-073 ; V34-073 | 22-04 / 22-12 | segmentation ≠ reconstruction d'accessoires |
| B05 | S-086 | V34-133 | 22-04 | bbox en mm ≠ guides/snap/distribution |
| B06 | S-035 | V34-133 | 22-04 | aucune preuve de perspective/warp/clip |
| B07 | S-028 | V34-073 | 22-04 | sujet et accessoires ≠ rig cinématique |
| B08 | S-014 | V34-073 | 22-12 | proposition de masque ≠ inpainting après déplacement |
| B10 | S-036, S-064 | **aucun ticket V34 direct G6/G9** | test V3.3 à qualifier | polices, glyphes, droits et conversion tracés |
| B11 | S-092 | **aucun ticket V34 direct G6/G9** | test V3.3 à qualifier | aperçu de police et glyphes manquants |
| B12 | S-021, S-047 | **aucun ticket V34 direct G6/G9** | test V3.3 à qualifier | OCR opt-in, confidentialité, provenance |
| B13 | S-064, R33-028 | **aucun ticket V34 direct G6/G9** | test V3.3 à qualifier | typographie éditable et conversion sans perte |
| B14 | S-037, S-088 | **S-037 sans ticket V34 direct** ; S-088→V34-126 | V3.3 / 22-08 | composition/gabarits métiers ≠ patron de coupe complet |

**Règle d'exactitude :** le numéro T-V34-22-xx est abrégé dans la table, pas un PASS. La liste complète A/B = 10 IDs de COV18A1 + 20 ci-dessus = **30 IDs distincts candidats**, **0 certifié**. La présence d'un ticket sur une ligne S ne démontre ni le critère complet ni l'UX promise.

## 2. Architecture et frontières de décision

- **Un seul writer CAS et un seul .smartsvg V1**. Les ObjectRef, LayerDraft, TextDraft, transforms et OCR restent des propositions de brouillon en mémoire tant qu'un ADR de persistance n'est pas approuvé. Ne jamais écrire de champs texte/calques arbitraires dans editor_v216.
- **Transitions** : inspecter projet@SHA → sélectionner un Subject réel → créer brouillon avec provenance → prévisualiser → Undo/Redo local → vérifier expected_revision → commit uniquement via API autorisée, sinon conserver un brouillon exportable séparé explicitement nommé. Résultat asynchrone périmé = rejet sans mutation.
- **Quatre rôles d'export non interchangeables** : PNG Print Then Cut ; SVG Basic Cut ; SVG CUT multicouche ; SVG d'édition. Les chemins géométriques, masques float32 et calques visuels ne sont pas des équivalents. Profil machine UNKNOWN bloque toute promesse de compatibilité réelle.
- **UX** : novice = import, geste direct, avant/après, correction et reprise ; expert = coordonnées px/mm, SHA, source, révision, typographie et topologie. Une seule vue Atelier, focus clavier, 1366×768 et DPI 200 %, contrastes et mouvement réduit à tester, pas d'ajout d'un bouton « Smart » par ID.
- **IA facultative** : CPU/manuel disponibles sans téléchargement ; OCR, segmentation et inpainting demandent consentement explicite, modèle/version/hash/licence/provenance, OOM et annulation sans altérer la source. Aucun média propriétaire ni police non autorisée dans le dépôt.

## 3. Recettes futures et contre-expertise hostile

**Positif candidat** : image synthétique avec deux sujets, trou interne et légende ; sélectionner/transformer en brouillon, Undo, contrôler SHA original, prévisualiser séparément SVG édition et Basic Cut, puis reprendre la session. Persistance de texte/calques = SKIP tant que le contrat n'est pas autorisé.

**Négatifs à implémenter avant DoD :** N1 changement concurrent de SHA entre preview/commit → conflit CAS sans écriture ; N2 masque float32 dimensions erronées ou trou absorbé → refus, source intacte ; N3 SVG avec script, entity externe, path NaN ou unités ambiguës → rejet prévol ; N4 police absente, licence inconnue ou glyphes manquants → avertissement, aucune substitution silencieuse ; N5 OCR sans consentement ou modèle absent → parcours manuel, zéro réseau ; N6 groupes cycliques, transformation non inversible, ordre de calques invalide → rollback brouillon ; N7 crash/disque plein pendant publication → pas d'artefact partiel ni overwrite. Vérifier séparément auto non-skip, UI Windows, GPU, Design Space et coupe physique.

**Micro-lots TDD proposés** : (1) tests d'identité et CAS de brouillons ; (2) tests de géométrie/alpha/topologie et unités ; (3) tests typographie/OCR consentement et licence ; (4) tests Undo/annulation/reprise ; (5) tests UI Windows et accessibilité ; (6) prévols quatre exports puis validation DS/physique distincte. **Aucun développement dans cette mission.** Les cibles de latence p50/p95, RAM/VRAM et fidélité doivent être mesurées sur fixtures libres/synthétiques avant fixation de seuils.

## 4. Audit des 25 contrôles

01–05 : inventaires historiques 24/141/140/80/437 conservés ; 30/30 A/B ont une proposition de rapprochement, **0/30 certifié**. 06 : statuts indépendants ; 07 : CAS/V1/float32 protégés ; 08 : 4 sorties distinctes ; 09 : tri-state, aucun contrôle machine revendiqué ; 10–13 : UX, clavier, Undo, crash, concurrence en DoD futur ; 14 : IA opt-in ; 15 : alpha/HD préservés ; 16 : SVG/topologie ; 17 : Fabrique/batch hors micro-lot, héritage intact ; 18 : Smart Delivery hors micro-lot, non modifié ; 19 : #141/opportunités hors micro-lot, non abandonnés ; 20 : métriques à mesurer ; 21 : fixtures et licences ; 22 : branche documentaire seule ; 23 : réemploi des ports et refus du second store ; 24 : revue indépendante/CI/promotion ouvertes ; 25 : aucune réduction de couverture.

**État de preuve** : DOCUMENT CANDIDAT ; tests produit = 0 ; Windows UI/GPU/Design Space/coupe physique = NOT_RUN. Les 431/437 liens historiques scénarios→tickets et six exceptions ne changent pas ; dix exigences G6/G9 sans ticket direct restent visibles. **Prochaine action unique COV-18A-2** : vérifier les **30/30** associations A/B contre les critères V3.3 intégraux, les DoD V34 et les scénarios locaux, avec sources exactes et divergences à arbitrer ; ne certifier aucun ID sans cette revue.
