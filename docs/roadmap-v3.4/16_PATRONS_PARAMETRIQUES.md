# SmartSVG Studio V3.4 — Lot 16/24 : patrons paramétriques de cartes et boîtes (périmètre existant)

**DRAFT DE CONCEPTION, 29 octobre 2026.** V3.3 reste **ACTIVE** ; issue [#72](https://github.com/frenndak/SmartSVG-Studio/issues/72), [PR #73](https://github.com/frenndak/SmartSVG-Studio/pull/73) documentaire. **Aucune nouvelle fonction imposée.** Les chemins et tickets ci-dessous sont des propositions, non du code exécuté. Les preuves produit/Windows/RTX/Design Space/physiques sont **NON_EXECUTE**.

## 1. Contre-expertise ciblée des lots 14–15 et état réel

1. **Un patron n'est pas une image ni un Score automatique.** Le lot 14 montre une boîte fictive de 80 × 50 × 30 mm avec un bbox indicatif de 140 × 100 mm : ce n'est **pas** une géométrie calculée ni une cote garantie. Le présent lot fournit un exemple paramétrique *cohérent* de plateau ouvert 80 × 50 × 30 mm, **bbox 140 × 110 mm**, avec découpe, quatre fentes et huit plis distincts. Il ne remplace pas rétroactivement l'exemple illustratif du lot 14.
2. **Ne pas transformer un inspecteur en générateur.** `engine/web/js/smartsvg_cut_review_model_g27.mjs` sait inspecter un sous-ensemble SVG de coupe (64 chemins, dimensions 1–300 mm), et `engine/cricut_preflight_v205.py` fournit un prévol SVG/PNG indicatif ; **aucun ne génère aujourd'hui une boîte paramétrique ni ne transporte une opération Score dans Design Space**. `engine/smartsvg_quality/geometry.py` contrôle des *masques*, pas des patrons en mm. Réutiliser leurs validations pertinentes sans inventer un second moteur de prévol.
3. **Supprimer les fausses dépendances de livraison.** Le lot 14 mentionne bootstrap autonome, format V2 et bus complet comme « bloquants ». Ils ne sont **pas requis pour calculer, prévisualiser et vérifier une fixture de patron en mémoire puis exporter un brouillon SVG**, tant qu'aucune persistance V2 ni commande multi-utilisateur n'est annoncée. Les fonctions d'enregistrement/Undo utiliseront l'autorité `.smartsvg` et les commandes validées quand elles seront raccordées ; **G3.3e-b2a et G4 continuent en parallèle**.

**Héritage approuvé :** V3.3 F06/F08/F09/F13, P02/P05/P09, G4/G6/G9 ; S-012, S-020, S-030, S-085, S-088 ; R33-008, R33-022, R33-023, R33-025, R33-034. **Dépendances fonctionnelles déjà spécifiées :** lot 13 géométrie/units, lot 14 opérations/prévol, lot 15 profils Explore 5. Pas de nouvelle famille, moteur universel, modèle IA ou gate ajouté.

## 2. Deux parcours réellement consommables

**Novice — plateau carton ouvert.** Dans Fabrique : « Créer → Boîte simple ouverte » → saisir largeur de base, profondeur, hauteur et largeur des languettes **en mm** → voir le développé et les plis → choisir matière, tapis et outil *déclarés*, sans inventer leurs compatibilités → « Prévol » → « Exporter brouillon SVG + guide ». Une seule question apparaît pour une cote absente. La prévisualisation distingue texte/motifs pour **CUT extérieur, CUT fentes, SCORE plis**. Après import, l'utilisateur sélectionne les plis, leur assigne **Score**, utilise **Attacher** avec la coupe, vérifie les dimensions, la matière et les changements d'outil dans Design Space. L'application ne pilote pas la machine.

**Expert — patron et tolérances.** Panneau paramètres mm, vue de développé avec IDs stables, liste de segments CUT/SCORE, intersections classées, bbox, budget de chemins, provenance du profil, transformations et diff avant/après. Les modifications créent une **proposition immuable** ; l'acceptation peut devenir une commande projet seulement si le writer/Undo existant le supporte. Les cotes sont nominales ; **l'épaisseur, le jeu d'assemblage, le sens du grain, le rayon de pli et la compensation matière ne sont jamais déduits**. En l'absence de données, indiquer « assemblage à tester » et proposer un coupon, pas une tolérance chiffrée inventée.

**Carte pliée — même moteur, pas une application distincte.** Carte fermée nominale 105 × 148 mm : développé rectangulaire **210 × 148 mm**, un contour CUT fermé et une ligne SCORE verticale de (105,0) à (105,148). Un tapis pour cartes ne peut être présumé compatible avec cette disposition : le support reste `UNKNOWN` jusqu'au profil précis du lot 15. Aucun gabarit de carte supplémentaire n'est imposé par ce lot.

**Wireframe textuel :**
```text
[Fabrique > Créer un patron]  [Boîte ouverte | Carte pliée] [Brouillon / Enregistré]
Largeur [80 mm]  Profondeur [50 mm]  Hauteur [30 mm]  Languette [10 mm]
[Développé 140 × 110 mm]  CUT contour + 4 fentes | SCORE 8 plis
[Prévol]  0 erreur géométrique statique / Matériau et outil : NON QUALIFIÉS
[Voir erreurs sur le dessin] [Revenir aux paramètres] [Exporter brouillon]
[Guide Design Space : importer > choisir Score > Attacher > vérifier mm/outils]
```

## 3. Contrat géométrique minimal et exemple de référence

**Entrées requises :** nombres finis positifs `W,D,H,T` en mm, avec `0<T<H`, sans valeurs implicites provenant d'une photo. `W,D` sont les dimensions nominales **de la base** ; `H` est la hauteur nominale des parois ; `T` est une largeur de languette choisie, **pas une tolérance validée**. La dimension intérieure finale dépend de la matière et du pliage : elle n'est pas garantie. Vérifier les budgets/tailles du composant et du support ciblés avant export, sans transformer une limite d'inspecteur (300 mm) en capacité machine.

**Construction déterministe de la boîte simple ouverte (pas de couvercle) :** base `[H,H]–[H+W,H+D]` ; quatre parois de hauteur `H` ; quatre languettes de largeur `T` attachées aux parois haut/bas ; contour extérieur unique fermé ; quatre fentes CUT ouvertes explicitement approuvées pour libérer les languettes ; quatre plis de base et quatre plis de languettes SCORE. Lignes ouvertes CUT = **fentes explicites à examiner**, jamais conversion automatique d'une ligne de guide en coupe. L'algorithme conserve l'orientation et l'ordre des chemins, déduplique les segments, signale les contacts intentionnels fente/pli, et refuse toute auto-intersection non expliquée.

**Fixture JSON de SPÉCIFICATION (coordonnées absolues en mm, pas de fichier généré par le moteur) :**
```json
{
  "schema": "smartsvg-template-preview/1-draft",
  "template_id": "open-tray-glue-tabs",
  "units": "mm",
  "parameters": {
    "base_width": 80,
    "base_depth": 50,
    "wall_height": 30,
    "tab_width": 10
  },
  "geometry": {
    "bbox_mm": [
      0,
      0,
      140,
      110
    ],
    "cut_outer": [
      [
        20,
        0
      ],
      [
        120,
        0
      ],
      [
        120,
        30
      ],
      [
        140,
        30
      ],
      [
        140,
        80
      ],
      [
        120,
        80
      ],
      [
        120,
        110
      ],
      [
        20,
        110
      ],
      [
        20,
        80
      ],
      [
        0,
        80
      ],
      [
        0,
        30
      ],
      [
        20,
        30
      ],
      [
        20,
        0
      ]
    ],
    "cut_slits": [
      [
        [
          20,
          30
        ],
        [
          30,
          30
        ]
      ],
      [
        [
          110,
          30
        ],
        [
          120,
          30
        ]
      ],
      [
        [
          20,
          80
        ],
        [
          30,
          80
        ]
      ],
      [
        [
          110,
          80
        ],
        [
          120,
          80
        ]
      ]
    ],
    "score_folds": [
      [
        [
          30,
          30
        ],
        [
          110,
          30
        ]
      ],
      [
        [
          30,
          80
        ],
        [
          110,
          80
        ]
      ],
      [
        [
          30,
          30
        ],
        [
          30,
          80
        ]
      ],
      [
        [
          110,
          30
        ],
        [
          110,
          80
        ]
      ],
      [
        [
          30,
          0
        ],
        [
          30,
          30
        ]
      ],
      [
        [
          110,
          0
        ],
        [
          110,
          30
        ]
      ],
      [
        [
          30,
          80
        ],
        [
          30,
          110
        ]
      ],
      [
        [
          110,
          80
        ],
        [
          110,
          110
        ]
      ]
    ],
    "expected_cut_paths": 5,
    "expected_score_paths": 8,
    "expected_area_mm2": 13000
  },
  "handoff": {
    "requires_manual_score_assignment": true,
    "requires_manual_attach": true,
    "physical_validation": "NON_EXECUTE"
  }
}
```

**Contrôles arithmétiques de la fixture :** bbox `(2H+W) × (2H+D) = 140 × 110 mm` ; aire du contour `W×D + 2H(W+D) + 4TH = 13 000 mm²` ; **1 contour fermé + 4 fentes ouvertes = 5 chemins CUT**, **8 segments SCORE**, aucun segment de coupe exactement dupliqué. Les quatre fentes aboutissent aux jonctions de plis et nécessitent une vérification de fabricabilité : **une intersection intentionnelle de bout de ligne n'est pas un doublon ni une garantie physique**. Pour une variante sans languettes, un patron en croix sans collage est possible seulement si elle appartient au choix déjà approuvé de modèle ; ne pas créer une nouvelle fonctionnalité de « génération universelle ».

**Autorités et modules à réutiliser :** `.smartsvg` reste source de vérité dès qu'une proposition est acceptée/persistée ; `engine/smartsvg_core/project_archive.py` et recovery pour le projet existant ; géométrie et projections du lot 13 ; **un seul** résolveur d'opérations/prévol des lots 14–15 ; inspecteur G2.7 pour le sous-ensemble accepté ; `engine/cricut_preflight_v205.py` pour le diagnostic d'artefact exporté. **Futur consommateur pressenti**, sans créer un service supplémentaire : `engine/smartsvg_app/fabrication/templates.py` appelé par le même `FabricationPlan` et la même interface Fabrique. Si ce chemin change lors du spike de bootstrap, préserver le contrat, pas le nom de dossier.

## 4. Validation, erreurs, annulation et absence de faux prérequis

| Contrôle | Comportement prévu et message FR |
|---|---|
| Cote absente, NaN/Inf, zéro, `T≥H` | `INVALID_TEMPLATE_DIMENSION` ; « Vérifiez les quatre mesures en millimètres. » Aucun commit. |
| Patron trop grand pour l'inspecteur ou la feuille déclarée | `TEMPLATE_BOUNDS_EXCEEDED` ; « Le développé ne tient pas dans la zone choisie ; adaptez les dimensions ou la disposition. » Ne pas prétendre connaître toute la zone de coupe Cricut. |
| Fente absente, doublon CUT, intersection inattendue | `TEMPLATE_TOPOLOGY_INVALID` ; surligner les segments et refuser l'export de coupe concerné ; ne pas effacer le dessin. |
| SCORE non confirmé / outil ou matière inconnus | `CAPABILITY_UNKNOWN` ; conserver **brouillon** et guide, jamais « prêt machine ». |
| Projet périmé / conflit SHA / panne d'écriture | `STALE_PROJECT_SHA` ou `SAVE_FAILED` ; conserver projet et proposition, relire l'état et utiliser la récupération existante ; ne pas écraser l'archive V1. |
| Profil modifié après prévol | Prévol `STALE` à recalculer ; aucune requalification implicite. |
| Erreur Design Space ou changement de position après import | Revenir au guide de transfert, vérifier l'alignement et **Attacher** ; pas de résultat physique attribué à SmartSVG. |

**Persistance/Undo :** modifier les paramètres en mémoire n'altère ni original ni masque float32 ; les paramètres/segments acceptés seront historisés uniquement par les commandes déjà prévues. Les exports externes ne sont pas annulés par Undo. Si le writer V1 ne sait pas sérialiser ce modèle, **ne pas injecter de champs V2 en douce** : conserver l'export brouillon et signaler que la reprise du patron éditable n'est pas encore disponible. La migration V2 reste un travail parallèle conditionnel, pas un bloqueur pour les tests de géométrie.

**Performance :** aucun benchmark inventé. Mesurer génération, prévol et rendu sur carte/boîte synthétiques, avec temps médian/p95 et mémoire sur machine de référence ; comparer réexécution identique et modification d'un seul paramètre. Un changement de dimension invalide les dérivés géométriques concernés, pas les masques d'une autre image. Aucun GPU/IA nécessaire.

## 5. Tests proposés — tous NON_EXECUTE

| Test | Assertion exacte | Preuve future |
|---|---|---|
| T-V34-16-01 | Fixture 80/50/30/10 → bbox 140×110, aire 13000 mm², 5 CUT/8 SCORE ; aucune auto-intersection du contour extérieur | auto |
| T-V34-16-02 | Quatre fentes de 10 mm présentes, ouvertes et explicitement CUT ; aucun doublon exact ; jonctions de plis signalées mais non rejetées en bloc | auto |
| T-V34-16-03 | `T=0`, `T=H`, NaN, Inf, cote négative ou manquante → refus sans mutation ni valeur cachée | auto/UI |
| T-V34-16-04 | Carte 105×148 → développé 210×148, 1 CUT/1 SCORE ; pas de compatibilité tapis carte inventée | auto |
| T-V34-16-05 | Changement de paramètre → nouvelle proposition et prévol invalidé ; source, masques float32 et projet V1 inchangés | auto |
| T-V34-16-06 | Prévol export : mm/viewBox cohérents, chemins distincts, refus d'un doublon et d'une intersection non intentionnelle | auto |
| T-V34-16-07 | Sans modèle IA, sans ComfyUI et sans format V2, le calcul/aperçu/export brouillon reste possible via un harness de test isolé | auto/intégration future |
| T-V34-16-08 | UI novice : erreurs localisées, accès clavier, aucune mention « Score transmis » ou « prêt machine » avec profil UNKNOWN | UI/Windows |
| T-V34-16-09 | Import réel : Score choisi, Attacher vérifié, dimensions relevées et changement d'outil consigné ; pas de PASS automatique | Design Space |
| T-V34-16-10 | Coupon carton : coupe, plis, fentes, languettes et montage mesurés avec matière, outil, tapis, version et SHA exacts | physique |

**Données :** coordonnées synthétiques du présent lot, carte synthétique et cas invalides générés en tests ; aucune image privée ou fichier tiers. **DoD documentaire :** test→ticket→exigence relié, exemple syntaxiquement valide, limites explicites. **DoD produit ultérieure :** code au SHA, assertions exécutées, preuves séparées auto/Windows/Design Space/physique et rollback éprouvé. Une preuve statique ne vaut pas qualification machine.

## 6. Tickets minimaux pour implémentation future (aucune fonction supplémentaire)

| ID / priorité | Dépendances utiles, livrable pressenti, test, preuve, DoD et rollback |
|---|---|
| **V34-126 P1** — génération géométrique carte/boîte | S-020/S-088, R33-008, V34-096/106 ; **futur** `engine/smartsvg_app/fabrication/templates.py` ou module de géométrie retenu après spike ; T-V34-16-01..04 ; preuve auto ; DoD = contours/fentes/plis déterministes en mm, IDs stables, sans nouveau store ; rollback = désactiver le gabarit sans toucher au projet. |
| **V34-127 P1** — prévol de patron par règles existantes | S-012/S-085, R33-023, V34-108/107/116 ; **adapter** le prévol du lot 14 et `engine/cricut_preflight_v205.py` à la sortie, pas un second validateur ; T-V34-16-02/03/06/09/10 ; preuve auto + axes Design Space/physique distincts ; DoD = erreurs localisées, profil UNKNOWN non promu, tests de fabrication avant qualification ; rollback = brouillon non qualifié. |
| **V34-128 P1** — parcours Fabrique, reprise et transfert guidé | S-030/S-088, R33-008/022/025/034, V34-041/111/114/120 ; **futur** panneau dans l'UI Fabrique existante et réemploi du guide Score/Attacher, sans nouveau protocole machine ; T-V34-16-04/05/07/08/09 ; preuve auto/UI/Windows et Design Space ultérieur ; DoD = preview/acceptation distincts, V1 non corrompu, export brouillon explicite, Undo sur commande acceptée seulement ; rollback = masquer l'entrée gabarit et préserver les artefacts déjà produits. |

**Mapping inverse local :** T01→126 ; T02→126/127 ; T03→126/127 ; T04→126/128 ; T05→128 ; T06→127 ; T07→128 ; T08→128 ; T09→127/128 ; T10→127. Les 141 exigences historiques restent dans `HERITAGE_INDEX.md` ; leur matrice bidirectionnelle globale est prévue au lot 23, **sans créer de dépendance pour G3.3**.

## 7. Sécurité, arbitrages et lot suivant

- Pas de script SVG, de référence externe, d'exécution de code depuis une « recette », de téléchargement de modèle ou de modification des fichiers protégés. Le paramétrage est strictement numérique et borné ; le prévol de géométrie n'accorde aucune permission de fabrication.
- **Alternative rejetée :** une bibliothèque de patrons indépendante avec son propre stockage/undo/QA. **Option retenue en proposition :** petit générateur déterministe de gabarits approuvés, branché sur les contrats géométrie et fabrication existants ; le catalogue de bibliothèque du lot 20 ne devient pas une autorité concurrente.
- **Risques ouverts :** fentes CUT ouvertes et intersections intentionnelles à qualifier dans Design Space, effet de l'épaisseur/du grain et de la colle, dimensions nominales vs dimensions intérieures, limites de l'inspecteur G2.7, stabilité des exports, profil réel matière/tapis/outil, writer V1/V2. Aucun réglage machine ou jeu physique n'est fixé.
- **Sources officielles consultées le 29/10/2026 :** [Cricut Explore 5 — Scoring Tool](https://help.cricut.com/hc/en-us/articles/38613473602455-Cricut-Explore-5-How-to-use-the-Scoring-Tool) (sélection Score, Attacher, changement d'outil) ; [Cricut — Attach in Design Space](https://help.cricut.com/hc/en-us/articles/360009380514-How-to-use-Attach-in-Design-Space) (modifié le 02/10/2024 ; maintien des positions relatives). Ces documents attestent le **flux externe**, pas la qualité d'un patron SmartSVG.
- **Prochain lot 17 :** clarifier les **quatre contrats d'export déjà prévus** et le transfert guidé vers Design Space, en réutilisant le même guide Score/Attacher ; aucune création de driver ni duplication du prévol.

**État : SPECIFIE uniquement.** Les tests T-V34-16-* ne sont pas implémentés ; auto/Windows/Design Space/physique restent NON_EXECUTE pour le lot 16.
