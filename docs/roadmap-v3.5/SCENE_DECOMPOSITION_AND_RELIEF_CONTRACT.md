# Décomposer une scène — éléments éditables, planche et relief

**15 novembre 2026 — contrat candidat V3.5, aucun code produit livré.** Demande propriétaire : prendre une illustration avec personnage, décor et accessoires, en extraire des pièces indépendantes, les déplacer librement sur une planche et éventuellement recomposer le décor en relief. Base candidate `3ea07f8f5fdb0cfcf0450fdc1573a3cebc64f252`, main observé `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`. Les choix de conception ci-dessous sont des propositions du producteur autorisé à approfondir cette demande, pas des détails techniques prétendument dictés auparavant par l'utilisateur.

## 1. Fonction retrouvée et manque corrigé

La demande est partiellement distribuée entre **B03** décomposition en objets, **B08/D07** reconstruction facultative, **B01/B02/B04/B05** objets/calques/transformations, **C12–C14** planches et placement, **B14** composition et **S-044/S-066/S-099** diorama. Leurs fiches séparées ne décrivaient pas le parcours complet scène→pièces→planche→montage. Ce contrat le rend explicite, sans ajouter un 81e ID UX ni remplacer les 141 critères/140 tickets/437 assertions hérités.

Le nom de surface proposé est **« Décomposer une scène »**, dans l'Atelier existant. « Smart Scene » peut servir de nom court, sans nouvelle application ni canevas concurrent. Il s'agit d'une décomposition **par éléments de la scène**, distincte de la séparation par couleur du vinyle. Le fond reste un élément conservable ; il n'est pas automatiquement jeté comme lors d'un simple détourage. Un même élément peut comporter plusieurs fragments et des trous : une composante connexe n'est pas systématiquement un nouvel objet.

| Voie examinée | Décision et compromis |
|---|---|
| Tout extraire et compléter automatiquement par IA dès le premier clic | Non retenu comme socle : objets cachés indéductibles, erreurs sémantiques et dépendance modèle. L'IA propose des variantes révisables. |
| Sélection/correction manuelle, propositions assistées, objets indépendants et planche ; relief et reconstruction par incréments | **Retenu** : utile sans IA, raccord aux ports existants, résultat contrôlable. Le mode manuel n'efface pas l'obligation de qualifier ensuite l'assistance intelligente. |
| Quatre images aplaties ou quatre SVG prédéfinis uniquement | Insuffisant : ne permet pas la planche libre ni une scène rééditable. Le preset diorama quatre plans reste une recette distincte, obligatoire pour G9. |

## 2. Résultat utilisateur et exemple de référence

Une illustration contient un ciel, une colline, un arbre, un personnage, un accessoire et une touffe d'herbe devant le personnage. L'utilisateur choisit les éléments utiles, corrige les masques, renomme/regroupe si nécessaire, puis choisit :

1. **Planche d'éléments** : personnage à droite, arbre et herbe à gauche, fond sur une autre page ; tailles conservées, quantités explicites, pièces séparées pour stickers/découpage-collage.
2. **Scène recomposée** : déplacer ou réordonner les objets dans leur composition, en conservant une vue de référence à leur position d'origine.
3. **Montage en relief 2.5D** : affecter les pièces à des plans ordonnés, vérifier l'alignement et préparer les pièces/guide. Ce n'est pas la reconstruction d'un véritable volume 3D depuis une photo.

Choix par défaut du producteur : conserver les **pixels visibles seulement**, sans remplissage génératif. Le personnage caché derrière l'herbe est marqué « partie masquée non connue » : extraire son haut visible ne reconstitue pas ses jambes. Compléter le personnage et reboucher le fond après son déplacement sont **deux opérations distinctes**, chacune facultative. On peut garder l'herbe devant lui, dessiner/corriger manuellement ou accepter une variante reconstruite ; jamais déclarer automatiquement la pièce complète.

## 3. Parcours novice et expert dans un seul Atelier

**Novice :** Importer → Décomposer une scène → cliquer/entourer grossièrement les éléments → Garder/Exclure/Affiner → examiner fond et éléments manquants → accepter les pièces choisies → Planche ou Relief → indiquer la taille physique → déplacer/aligner/dupliquer → prévol du rôle choisi → exporter. Une planche ne devient pas un relief par simple changement de nom.

Le canevas alterne trois **vues du même projet** : Original avec masques ; Composition avec objets ; Planche de fabrication. La disposition des pièces sur la planche ne modifie pas leurs coordonnées dans la scène d'origine. Les paramètres nécessaires sont proposés progressivement ; les IDs, digests et ports ne sont pas exposés dans le parcours novice.

**Expert :** inspecter et corriger masques/relations, zones non attribuées, ordre avant/arrière, liens d'accessoires, variantes et provenance, dimensions mm, marges et quantités. Verrouiller un placement avant réorganisation automatique ; importer une pièce corrigée seulement après vérification du lien source. Pas de score de confiance inventé : origine de la proposition et incertitudes visibles, validation humaine des noms/relations.

Gestes : clic/lasso/pinceau add/erase/multi-zones existants à raccorder ; déplacer par poignées et alternative clavier/liste ; zoom/pan non mutants ; Escape abandonne le brouillon courant sans retirer les pièces déjà acceptées. Un drag ou une acceptation groupée = une opération Undo logique. Le texte de champ garde son Undo local. Focus restitué après panneau/erreur, annonces accessibles, contrastes et mouvement réduit ; 1366×768 et échelles100/125/150/200% héritées, autres écrans historiques conservés.

États du brouillon : EMPTY → SELECTING → PROPOSED → REVIEWING → READY_TO_ACCEPT → COMMITTED. CANCELLED/FAILED/MODEL_UNAVAILABLE/STALE/NEEDS_REVIEW ne publient pas de mutation. Un nouveau choix de source/révision invalide jobs et aperçus ; fermer puis rouvrir la session invalide aussi l'ancienne génération UI. La file de jobs et les unités batch restent celles de D04, pas un second ordonnanceur.

## 4. Contrats logiques et autorité

Les noms ci-dessous sont **proposés**, aucune signature Python correspondante n'est revendiquée. Tous nombres doivent être finis, toutes références résolues, IDs uniques ; budgets bornés en octets/pixels/nombre d'éléments, refus explicite plutôt que troncature.

| Contrat proposé | Données et invariants |
|---|---|
| `SceneDecompositionProposal/1-draft` | `project_id`, `project_sha256`, `source_id`, `source_sha256`, `source_dimensions_px`, `request_id`, `ui_generation`, `params_digest`, `elements[]`, `unassigned_regions`, `diagnostics`, provenance méthode/version/permissions. Brouillon non autoritaire tant que non accepté. |
| Élément proposé | `proposal_element_id`, libellé corrigible, `role=BACKGROUND|SUBJECT|ACCESSORY|DECOR|UNCLASSIFIED`, bbox px et masque float32 lié à la source, `fragment_refs`, origine MANUAL/HEURISTIC/MODEL, `completeness=VISIBLE_ONLY|COMPLETE_BY_CONSTRUCTION|USER_CONFIRMED`, zones cachées connues/inconnues. Le rôle n'assigne pas CUT/SCORE ; un nom suggéré n'est pas une reconnaissance certifiée. |
| Relations | `part_of` et `front_of` explicites, sans cycles ; parent absent refusé. L'ordre définit les occultations, pas une distance physique. Des masques peuvent se chevaucher si leur sémantique avant/arrière est explicitée ; aucune partition disjointe universelle imposée aux objets complets ou transparents. |
| Élément accepté | `node_id` de la scène CP3, références source/sujet/masque vérifiées, transformation locale mm et liens validés. Les coordonnées/transforms/ordre restent dans les nœuds canoniques, pas dans un second document d'édition. Une duplication reçoit un nouveau node/instance ID ; la source originale reste partagée et immuable. |
| `ReconstructionProposal/1-draft` | Cible fond ou pièce, source/masque SHA, ROI de modification et masque de zones supposées cachées, raster dérivé/digest, méthode/modèle/version/licence/seed si disponible, consentement, diff et zones inchangées. Généré ≠ observé ; une variante refusée ne remplace aucun pixel accepté. |
| `SceneSheetPlan/1-draft` | Révision scène, `page_id`, dimensions utiles mm/profil daté, `instance_id→node_id`, rôle export, quantité, matrice de placement mm, rotation consentie, marges et verrous. Consomme le placement W12 ; ne réécrit pas la scène ni ne recrée un moteur de nesting. |
| `ReliefPlan/1-draft` | Référence scène, plans ordonnés avec membership explicite, alignements en coordonnées de montage mm, espacements/épaisseurs saisis ou UNKNOWN, pièces de support proposées, étapes de montage et diagnostics. Affectation de profondeur acceptée par l'utilisateur ; aucun z métrique déduit automatiquement de la seule image. |

**Référence source et échelle :** les masques de travail restent dans le repère source orienté, après normalisation EXIF explicite ; le crop d'affichage n'altère ni l'original ni ce repère. Si l'orientation crée un raster dérivé, son ID/digest/dimensions sont distincts et sa transformation vers l'original conservée ; aucun masque orienté n'est lié frauduleusement aux dimensions brutes, les octets d'origine restent intacts. Le convertisseur écran→source utilise la transformation inverse du viewport, pas la position du widget. Une bbox est `[x,y,width,height]` avec origine haut gauche, x droite/y bas et bornes semi-ouvertes. Une image1200×800px à largeur confirmée120mm donne0,1mm/px ; bbox(100,200,300,400) = pièce30×40mm, origine scène(10,20)mm avant placement. Déplacer la pièce sur la planche conserve sa taille et son attache à la source ; redimensionner est un geste distinct. Un DPI supposé n'est pas une cote confirmée.

**Zones non attribuées et recouvrement :** l'inspection montre le fond gardé, les pièces choisies et les zones non expliquées ; aucune suppression silencieuse d'un fragment. La vue réassemblée compare les pixels/rendus selon un protocole annoncé. L'égalité exacte est exigée pour la fixture binaire construite ; les images à alpha souple utilisent une tolérance de fixture explicitement fixée et un rapport, pas une promesse de reconstitution parfaite de toute photo.

## 5. Persistance, Undo et parties cachées

L'[ADR composition](ADR_COMPOSITION_PERSISTENCE.md) gouverne : V1 strict inchangé, migrations V2 sur copie, un seul writer actif. **SCN1 preview/export externe peut exister sans CP2 ; SCN2 scène rééditable save/reopen exige CP0–3 et CP2 qualifié.** Le graphe d'occultation, les annotations de complétude et les plans persistants non représentables par le contrat actuel doivent être inscrits comme ressources/extensions **strictement versionnées et validées dans CP0**, puis chargés/publiés par CP1/CP2. Interdiction de les cacher dans `strokes`, `operations`, un champ JSON libre V1 ou un fichier annexe maître. Aucun schéma de produit n'est modifié par cette fiche.

Le premier sous-lot CP0-SCN fixe les champs exacts de ces ressources, références/quotas/version/erreurs et leur inclusion au digest transactionnel avant toute écriture. Les données référencées ne recopient pas les transformations des nœuds : références invalides ou ressource inconnue = refus utile, jamais perte silencieuse de la fonction au reload. La scène, ses ressources et son receipt sont publiés par la même transaction CP2. Un plan de page calculé reste un dérivé ; un placement/verrou saisi annoncé sauvegardé appartient à la même autorité versionnée.

Accepter une décomposition fige un digest des seuls éléments effectivement choisis ; création des nœuds, liens et ressources acceptés = tout ou rien, CAS/epoch/receipt selon CP2. Rejouer une commande déjà publiée retourne son résultat avant de rejeter son ancien SHA, selon le contrat du bus ; payload différent même command_id refusé. L8 de prévisualisation ne devient jamais le masque de travail float32. V1 garde son plafond32 ; les50sujets persistés utilisent les packs V2 internes déjà décidés, pas cinquante placements présentés comme cinquante sujets.

Reconstruction : conserver l'original, le masque observé et toutes variantes acceptées nécessaires à Undo. Les pixels hors ROI de modification et hors zones explicitement acceptées sont inchangés ; le diff révèle toute variation des zones visibles. Un raster reconstruit est une **ressource dérivée avec provenance**, jamais l'original renommé. Le node_id logique peut rester stable, mais toute nouvelle liaison source/sujet/masque doit être créée/validée selon ses invariants ; on ne réaffecte pas silencieusement un subject_id à une autre source. Ancienne variante, relations et plan restent restaurables par Undo/reopen.

Fermer pendant calcul annule le brouillon ; fermer après publication réconcilie le résultat. Erreur après primaire publié/backup échoué = COMMITTED_NEEDS_RECOVERY selon le format actif ; résultat indécidable = UNKNOWN_AFTER_INTERRUPTION, inspection avant retry. Undo du projet ne retire jamais un PNG/SVG/ZIP livré ni une pièce découpée. Exports multiples PARTIAL avec réussites conservées ; fichier/ZIP individuel complet ou absent, conformément à D03/D04.

## 6. Planche, relief et quatre sorties

| Sortie choisie | Résultat obligatoire et limites |
|---|---|
| PNG Print Then Cut | Pièces colorées sur transparence, dimension physique/résolution/alpha/bleed contrôlés, page dans zone confirmée du profil, aucun repère capteur Cricut créé. Taille de chaque pièce conservée, pas de réduction automatique pour faire tenir la page. |
| SVG Basic Cut | Silhouette/contour géométrique effectivement vectorisé et prévolé ; détail intérieur conservé seulement selon le rôle demandé. Pas de PNG enveloppé dans SVG présenté comme découpe vectorielle. |
| SVG CUT multicouche | Géométries/couches/opérations distinctes et alignées ; un objet de scène peut contenir plusieurs couleurs, une couleur peut apparaître dans plusieurs objets : ces deux découpages ne se confondent pas. Pas de quatrième Artifact.use caché en V1. |
| SVG d'édition | Objets/groupes/chemins réellement éditables selon capacités annoncées ; bitmap incorporé nommé comme raster, pas fausse vectorisation. Projet `.smartsvg` reste nécessaire pour toute sémantique non portable en SVG ; pertes signalées. |

La planche possède deux jeux de coordonnées : **placement des pièces à découper** et **position de montage dans la scène**. Une rotation d'optimisation ne tourne pas la pièce dans le guide d'assemblage ; le manifeste garde le lien et l'inverse. Quantités, noms de pièces et numéros de plans se retrouvent dans le guide et le pack ; les numéros de montage restent dans le guide par défaut. Toute marque ajoutée à la matière est une option explicite avec rôle PRINT/DRAW/CUT approprié, jamais une coupe parasite cachée.

Mode relief : choisir l'ordre, regrouper ou scinder les plans, contrôler l'alignement et l'espacement. Une suggestion de profondeur ne suffit pas à connaître l'épaisseur ni le jeu matière. Supports/entretoises/languettes éventuels = géométrie dérivée visible avec paramètres mm, prévol et protocole propre ; aucun ajout automatique au motif. Élément fragile ou détaché sans support = NEEDS_REVIEW, pas suppression du détail. Le preset historique **quatre plans** et son prototype assemblé satisfont seulement la recette G9 correspondante. Une scène à3ou5plans reste possible comme nouveau cas, sans prétendre satisfaire S-066 ; le négatif N6 de Q04G§4 garde son sens pour le contrat historique exactement quatre plans.

Le guide comprend miniature de la scène, pièces/quantités/pages, ordre de montage, cotes confirmées, spacers/adhésifs déclarés, zones reconstruites signalées et inconnues. La prévisualisation 2.5D est illustrative ; relief manuel doit pouvoir fonctionner sans moteur3D ni génération IA. Import DS, coupe et montage mesurés restent trois preuves distinctes. Smart Delivery consomme ces exports/guide existants ; il ne refait ni segmentation ni vectorisation ni sauvegarde de scène.

## 7. Réemploi réel, provenance et manques

Fichiers lus sur main0692f804 ; SHA de blobs vérifiés dans son arbre distant. Les adaptateurs futurs inventorient leurs signatures au HEAD avant code, en conservant les contrats des appels déjà utilisés.

| Port existant et blob | Capacité réelle / travail futur |
|---|---|
| `engine/smartsvg_core/project_contracts.py` · `7bfd2d714384717c6ce0bb66659971881bd285c2` | SourceAsset/Mask/Subject/bbox/accessory_ids et trois Artifact.use stricts ; pas de décomposition sémantique ni scène complète déjà livrée. |
| `engine/smartsvg_core/project_workspace_g22.py` · `13b8e40d6fcc9cf03ed2c935b38ad6eff0bcbe03` | create/inspect, snapshots et subject_brush : réutiliser pour V1 ; ne pas lui passer des champs V2 inconnus. |
| `engine/smartsvg_core/subject_identity_g33e.py` · `2d799a34915ae7648f39c89df25b876e5ddfcee0` | Liaisons de sujets aux masques vérifiés ; une vignette/index ne crée pas une identité. |
| `engine/smartsvg_core/editor_session_g23.py` · `dda853694d22f59252b9549b5e2fdbd59933bd59` | Parser d'édition strokes strict ; pas de scène/plan d'occultation caché. |
| `engine/smartsvg_core/native_subject_preview_v34.py` · `cd0568267327618b05748e0d434ff352943b0f47` | preview_native_subject_stroke ciblé et CAS ; raccord UI et transformation source exigés, pas preuve d'une sélection sémantique. |
| `engine/smartsvg_ai/routing_v21121.py` · `b039543450d69ff94c9a9e83e6e93c5255f1b1fe` | inspect_route/dark_sheet_masks annoncent explicitement absence de reconnaissance sémantique ; fond uniforme ≠ décor compris. |
| `engine/smartsvg_ai/auto_masks_v2111.py` · `4530631c75051a115f030fb0e76bc269bc3c1d74` | generate_masks propose masques via alpha/heuristique/provider ; son repli legacy peut charger un fournisseur : admission/no-network doit être qualifiée avant l'usage SCN. Aucun modèle réputé installé ou capable par ce renvoi. |
| `engine/smartsvg_editor/strokes.py` · `18a04b0ddd0449c98a2ccc676ccc971ebef5adc8` | decode/apply_strokes sur masques ; réemploi correction add/erase, conservation des autres masques, pas nouveau moteur pinceau. |
| `engine/multi_subject_v21.py` · `72298cb6e9fa2b2e23a7d49bb9a5e25a4009ba8a` | _make_pages réemploie _save_sheet ; grille/répartition raster historique, non éditeur de planche libre ou nesting de silhouette déjà acquis. Les170×240mm codés sont une hypothèse historique, pas limite constructeur actuelle. |

Tickets réutilisés par responsabilité : V34-069/070/071/072/073 pour propositions/masques/acceptation/liens ; V34-035/038 pour historique ; V34-132/133 pour Atelier/objets ; V34-134/135 pour placements/lots ; V34-129/131 pour exports, prévol/profils lots13–17 ; W16/CP6 pour relief G9 et B08/D07 pour reconstruction. **Ce sont des raccordements candidats de responsabilités**, pas la preuve que tous ces tickets décrivaient déjà la nouvelle fonction complète.

## 8. Plan de réalisation borné

Chaque tranche localise au HEAD les consommateurs, garde une seule source d'autorité et suit le modèle de fiche du playbook. Aucun nouveau ticket V34 ni nouveau moteur/queue/store créé par automatisme.

| Tranche | Priorité / dépendances minimales | DoD et prochain résultat observable |
|---|---|---|
| SCN0 — contrat et fixtures | P1 W02 ; ports ci-dessus + CP0 pour extensions persistantes | Fixture synthétique6éléments, schémas de propositions/annotations/plan, limites et erreurs explicites ; validateurs purs, aucune écriture. Définir runner/commandes réels avant tout test revendiqué. |
| SCN1 — extraire/corriger | P1 W02 ; sélection/masques/QA et export existant | Source inchangée, sélection manuelle et fond conservé, fragments regroupables, pièces choisies en aperçu/export unitaire ; proposition assistée testée séparément. V1 sans save de scène avancée affiche « brouillon non sauvegardé ». |
| SCN2 — scène rééditable | P1 W01/W02 ; SCN0 + CP0–3 qualifiés, sans attendre CP4/5 texte | Nœuds/relations/variants enregistrés puis réouverts, déplacements et Undo durables, aucune injection V1. Reconstruction non requise. |
| SCN3 — planche libre | P1 W12 ; SCN1 + placement W12, persistance de placements via SCN2 | Déplacer gauche/droite, quantité, verrou, multi-pages et taille conservée ; guide de correspondance scène/planche. Optimisation avancée facultative, réemploi grille si profil compatible. |
| SCN4 — plans de relief | P2 W16 ; scène/planche + géométrie/prévol W03/W04, capacités précises CP6 | Affectation manuelle aux plans, coordonnées de montage, guide ; fixture quatre plans G9 puis coupon physique distinct avant revendication d'assemblage qualifié. Pas de dépendance au texte/OCR ou à une simulation3D. |
| SCN5 — assistance/reconstruction avancée | P2 W14/W16 ; SCN1/2 + admission modèle et budgets qualifiés | Propositions d'objets/occlusion/comblement, diff/source/provenance, rejet/Undo ; repli manuel complet. Aucun « toutes photos parfaitement décomposées ». |

La sélection assistée de base reste P1 dans A04/B03 ; SCN5 concerne la compréhension/reconstruction avancées, pas le report global de B03. SCN3 aperçu/export externe peut avancer sans scène persistée, mais ne clôt pas son DoD de planche rééditable. SCN4 n'attend que les capacités nécessaires de CP3–6, jamais un OCR ou moteur de texte non utilisé. Effort qualitatif : SCN0/1 moyen ; scène persistée/relief/reconstruction élevé. Pas de date, tarif, gain de temps ou GPU garanti.

## 9. Recettes discriminantes — proposées, toutes NOT_RUN produit

IDs nouveaux `T-V35-SCN-*`, distincts des437assertions historiques. Fixtures générées et annotations reproductibles, aucune image personnelle/propriétaire publiée.

| ID | Entrée / résultat attendu |
|---|---|
| T-V35-SCN-01 | Illustration1200×800 synthétique6éléments connus, largeur120mm ; extraire bbox(100,200,300,400), pièce30×40mm. Repositionner gauche/droite ne change source, masque ni taille ; zoom/DPI/EXIF n'introduisent pas de décalage de repère. |
| T-V35-SCN-02 | Deux fragments disjoints d'un même accessoire et un trou intérieur : groupement conservé, trou préservé ; nombre de composantes non présenté comme nombre d'objets. |
| T-V35-SCN-03 | Fixture binaire sans occultation avec masques annotés : réassemblage original exact ; alpha souple : tolérance fixée par fixture avant test, diff localisé, aucune retouche cachée. |
| T-V35-SCN-04 | Personnage devant arbre et herbe devant personnage : ordre explicite et preview cohérente ; jambes non visibles restent inconnues, fond conservé, aucune reconstitution automatique proclamée. |
| T-V35-SCN-05 | Accepter6éléments, déplacer/grouper/dupliquer, Undo/Redo, save/reopen CP2/3 : IDs, ordre, masques float32 et ressources stables ; duplication ID distinct, source inchangée. |
| T-V35-SCN-06 | Pièces sur2pages, rotations et placement verrouillé : zéro collision/hors-zone selon profil fixture, dimensions/quantités conservées ; guide garde positions de montage indépendantes des rotations de planche. |
| T-V35-SCN-07 | Quatre plans G9 avec épaisseurs de fixture explicites : alignements/guide/mm cohérents ; test de montage réel distinct avec matière/outil/tapis/DS/mesures avant PHYSICAL_PASS. Cas3ou5plans ne revendique pas S-066. |
| T-V35-SCN-08 | Deux objets partagent la même couleur : restent deux objets ; un objet à trois couleurs n'est pas arbitrairement trois pièces. Quatre sorties séparées, SVG raster annoncé, jamais faux CUT multicouche ou édition vectorielle. |
| T-V35-SCN-09 | Reconstruction fond puis variante personnage : deux consentements de modification/propositions, originaux conservés, zone extérieure ROI bit-identique, visible modifié signalé ; rejet zéro commit, acceptation puis Undo restaure ancienne variante. |
| T-V35-SCN-10 | Masque vide/NaN, bbox hors-source, cycle part_of/front_of, référence supprimée ou doublon ID : refus sans écriture ni pièce rectangulaire inventée. |
| T-V35-SCN-11 | Proposition ancienne après retouche/source changée ou fermeture/réouverture : STALE ignoré, pas d'application au nouvel objet sélectionné ; double commande même payload rejouée CP2, payload différent refusé. |
| T-V35-SCN-12 | Modèle absent/non admis, consentement refusé, OOM/timeout/annulation : zéro téléchargement/inférence/réseau implicites, brouillon préservé, voie manuelle et raison visibles. |
| T-V35-SCN-13 | Épaisseur/profil/cote inconnus, pièce détachée fragile, support non validé : NEEDS_REVIEW/UNKNOWN, aucun « prêt à découper/monter » ; pas de minuscule redimensionnement pour remplir une page. |
| T-V35-SCN-14 | Crash/disque plein/CAS concurrent/perteACK entre préparation et publication CP2 : aucune demi-scène ; inspection primaire/backup/receipt avant retry, au plus une acceptation logique ; source V1 intacte. |
| T-V35-SCN-15 | Échec du2eexport : premier fichier sain conservé et état PARTIAL ; ZIP partiel non publié comme complet, collision de destination refusée ; Undo ne supprime pas une sortie externe. |
| T-V35-SCN-16 | SVG hostile, ressource/URL arbitraire, noms de pièces avec chemins/HTML : refus ou échappement selon contrat ; guide/manifeste expurgés, aucun script ni chemin privé ni poids modèle dans livraison. |
| T-V35-SCN-17 | Parcours clavier/liste sans drag, zoom200%, petit écran, source longue et erreurs : sélection/correction/placement/save/export accessibles ; lecteur d'écran et fenêtres réels restent à tester sous Windows. |

Mesurer temps de sélection/correction, nombre d'actions, qualité des masques/contours sur vérité terrain autorisée, erreur d'échelle mm, chemins/nœuds/fragments, mémoire/RAM/VRAM et latence p50/p90/p95/max selon taille/nombre d'éléments. Comparaison manuelle/assistée sur même source, même taille physique et même matériel ; aucune métrique sémantique calibrée inventée. La qualité du montage se mesure sur prototype, pas sur l'effet de parallaxe à l'écran.

## 10. Sécurité, alternatives et portée des25axes

IA locale facultative, admission modèle/licence/version/hash/provenance fiable et consentements téléchargement/exécution/transfert séparés. Le hash ne signe pas l'auteur. La génération respecte les droits de la source et des modèles ; pas de média ni de poids à publier. Brouillons/cache locaux bornés et purgeables, aucune copie du projet source dans les livraisons sans choix explicite. Le moteur géométrique déterministe prend le relais pour les contrôles de fabrication.

| Axes | Traitement dans ce contrat |
|---|---|
| 01–05 | Héritage24lots/141critères/140tickets/80UX/437assertions conservé ; nouveaux scénarios SCN séparés, raccordements candidats explicites. |
| 06 | Conception, port présent, code futur et qualification par axe distingués ; aucune réussite produit. |
| 07 | Autorité unique, source/float32/IDs, CP0–3 pour persistance, CAS V1≠receipt. |
| 08–09 | Quatre exports, opérations distinctes, profils inconnus et guidage DS sans driver. |
| 10–12 | Parcours novice/expert, sélection directe, vues communes, clavier/liste/focus/petits écrans/DPI. |
| 13 | STALE/session, annulation, Undo, crash/backup/concurrence, réussite partielle export. |
| 14–16 | IA opt-in/repli/budgets ; alpha/EXIF/résolution ; vrais chemins/topologie/mm et trous. |
| 17 | Planche, quantité/verrous, montage quatre plans et responsabilités W12/W16 séparées. |
| 18–19 | SD consommateur après export ; raffinement B03/B08/C12/G9, pas remplacement des opportunités ni fonction factice supplémentaire. |
| 20–21 | Protocole de mesure sans gain chiffré promis ; droits, média/source, guides inertes et expurgation. |
| 22–25 | Branche documentaire seulement, pas gouvernance/code/CI/archives modifiés ; réemploi des ports ; contre-revue du delta avant intégration ; aucune obligation réduite. |

**Sortie de conception attendue :** fonction nommée, scénario complet, données/erreurs/limites, tranches SCN et tests ci-dessus, revue indépendante du raccordement et des consommateurs. L'ancien verdict global vaut pour son SHA ; ce nouveau delta doit avoir sa propre preuve avant promotion. La tâche horaire consomme cette fiche et reprend le curseur courant, sans créer un nouveau cycle infini d'audits ni une autre tâche. Rollback documentaire : revenir à ce delta en préservant sources et anciens rapports ; rollback produit futur : désactiver l'entrée SCN/consommateur non qualifié, conserver projets/variantes et réouvrir V1 conservé, jamais écraser V2 avec writer V1.
