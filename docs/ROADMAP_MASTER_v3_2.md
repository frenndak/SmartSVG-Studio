# SmartSVG Studio — ROADMAP MASTER v3.2 — INTÉGRATION UX/UI COMPLÈTE
## Document directeur complet · Vision produit · Priorisation · Ingénierie · Fabrication

**Date :** 24 octobre 2026  
**Type :** feuille de route et cahier de validation, pas annonce de fonctionnalités livrées  
**Statut documentaire :** **V3.2 CONSOLIDÉE — FIGÉE POUR PLANIFICATION** ; remplace v3.1 comme document directeur. V3.1 reste immuable et traçable. Toute évolution ultérieure passe par une version motivée, jamais par modification silencieuse.  
**Statut du logiciel :** baseline V21.14.1 **gelée**, aucun développement réalisé par cette révision ; les essais de fabrication et IA réelle restent à faire.  
**Référence logicielle B0 :** `ComfyUI_SmartSVG_Studio_V21_14_1_Installation.zip`  
**SHA-256 de la baseline (déclaré dans le rapport de gel, à revérifier sur l'archive avant toute reprise) :** `b35ed631bcf6243bf0dd9b0af5b8e01dab1cfe38a5ef0f93e74f21a49df28835`  
**Héritage :** conserve les 15 familles F01–F15, les jalons G0–G9, les tickets S-001–S-066 et le corpus ; S-001–S-022 sont issus de la v1 (implémentation non vérifiée). Les tickets UX v3.2 commencent à S-067. Aucune nouvelle famille ne crée de logiciel séparé.  
**Nouveau dans v3.0 :** trajectoire produit détaillée, scénarios d'interface, contrats de sorties, cas de validation utilisateur, conformité Explore 5/A4 actualisée, matrice de risques, ordre de reprise, cadre de gouvernance.  
**Compléments v3.1 :** correction MVP/V22.0, preuves indépendantes, `.smartsvg`, géométrie, conformité Cricut, politique IA et reprise.  
**Intégration v3.2 :** refonte détaillée des fonctions UX dans **F01–F15, G2/G4/G6/G7/G8, les KPI, le registre de risques, le backlog et les critères de recette** ; navigation, maquettes fonctionnelles, interactions, actions correctives, accessibilité, cohérence, personnalisation et performance perçue. Les §§36–41 explicitent les mêmes engagements dans le **document maître**, sans annexe séparée.  
**Empreinte de ce document :** référencée dans `SmartSVG_Studio_Gel_Roadmap_v3_2.json` (manifeste externe, pas de hash autoréférentiel).  
**Décision :** ne reprendre le code que dans un lot explicitement ouvert ; aucune validation physique ou IA réelle ne peut être déclarée sur la base de tests simulés.

> **Mission** — Permettre à quelqu'un de déposer ou créer une illustration, sélectionner précisément les éléments souhaités, éditer la composition, choisir un procédé et une matière, puis obtenir **le bon fichier, à la bonne taille, avec les bons chemins de coupe**, prêt à être vérifié et utilisé dans Design Space. Les opérations faciles doivent être faciles ; les opérations difficiles doivent être transparentes, réparables et reproductibles.

## Résumé de décision — une page

| Question | Décision figée v3.1 |
|---|---|
| Quel logiciel construirons-nous ? | Un *Creative-to-Cut Studio* local, spécialisé fabrication ; ni simple convertisseur ni clone universel de Canva. |
| Quel utilisateur en priorité ? | Une personne non technique avec Cricut Explore 5 ; Expert et graphes restent accessibles. |
| Quelle base technique ? | B0 V21.14.1 gelée ; modules conservés, améliorations via adaptateurs et contrats testés. |
| Quel produit minimal ? | Stickers Print Then Cut et silhouettes Basic Cut, corrections et planches 12/24, preuve d'import et de coupe sur la Explore 5 pour les parcours déclarés. |
| Quel produit étendu ? | Dessin/texte/calques, vectorisation de qualité, série de modèles et personnalisation, matériaux, dioramas. |
| Quelle IA ? | Locale et facultative ; alpha/heuristique d'abord, BiRefNet/RMBG/SAM2 selon tests RTX 3070 8 Go réels. |
| Quelle frontière Cricut ? | SmartSVG prépare et contrôle ; Design Space importe, imprime les repères, pilote la machine. |
| Quelle garantie ? | **Preuves par axe** (format, rendu, géométrie, import, coupe, sauvegarde) et par contexte matériel, jamais une certification universelle. |
| Comment éviter l'inflation ? | WIP 1 fonctionnalité + 1 correctif ; chaque lot a tests, rollback et décision GO/NO GO. |
| Quelle prochaine action ? | Préparer corpus/vérité terrain G0.2–G0.4, puis ouvrir uniquement G1.1 (inventaire et **comptage réel**, cible annoncée 186 workflows). **Aucun chantier UX ne contourne ces gates.** |
| Quelle exigence UX concrète ? | L’utilisateur peut réaliser un sticker de bout en bout dans **Express**, sans graphe ni jargon, avec une aide accessible et des corrections locales non destructives. |
| Quels détails doivent être vérifiés ? | Navigation sur écran réduit, interactions souris/clavier, états vides/chargement/erreur, reprise et absence de faux indicateurs « prêt Cricut ». |

### Ligne de livraison

`B0 gelée V21.14.1` → `G0 référentiel` → `G1 contrats/projet` → `G2 Express minimal` + `G3.1 diagnostic IA` → `G4 Cricut physique` → **`MVP utile`** → `G3 approfondi / G5 vectoriel / G6 composition / G7 production (tranches utiles)` → `G8 QA` → **`V22.0 stable`** → `G9 V22.x/V23+`.  
**Correctif de dépendance :** G3.2–G3.5 n'est pas un préalable rigide aux découpes simples G4 dès lors que les entrées transparentes, fonds simples et retouches manuelles disposent d'un chemin fiable ; l'IA avancée doit rester facultative et honnêtement désactivable.

Les versions V21.15 à V21.21 sont **indicatives** : un jalon n'est franchi qu'en présentant la preuve de son critère de sortie. L'architecture et l'UI peuvent avancer par petites tranches sans attendre une réécriture massive.

### Légende d'état et priorité

- **Existant démontré localement** : rapport/test d'exécution vérifiable sur un environnement précis ; ne préjuge ni ComfyUI sur PC utilisateur ni Cricut physique.
- **Prototype/expérimental** : comportement documenté mais qualité générale insuffisamment démontrée.
- **À développer** : exigence approuvée ou candidate, sans prétendre qu'elle existe.
- **P0** : intégrité des données, sécurité, vérité des formats, parcours principal et résultats Cricut. Un P0 bloqué suspend la fonctionnalité dépendante, pas nécessairement toutes les autres sorties.
- **P1** : réels gains d'utilisabilité, IA, vectoriel, production, composition.
- **P2–P3** : extensions créatives et confort après stabilisation.

---

## Sommaire

**Mise à jour v3.2 :** l’expérience utilisateur n’est pas un supplément ; voir F01–F15 (§3), jalons G2/G4/G6/G7/G8 (§6), indicateurs (§9), navigation (§15), backlog S-067–S-101 (§33.2) et la spécification intégrée (§§36–41).

**Partie I (héritage v2 consolidé)** : vision, familles F01–F15, cinq sorties, architecture, micro-lots G0–G9, références historiques S-001–S-022, backlog détaillé S-023–S-048, corpus, mesures, gouvernance.  
**Partie II (compléments v3)** : interfaces, scénarios d'usage, routage, Explore 5, priorités, risques, premiers lots et revue.  
**Partie III (héritage v3.1)** : contrats de données, tests, 66 tickets historiques et règles de livraison.  
**Partie IV (intégration v3.2)** : description détaillée des six espaces, 28 fonctions utilisateur, 10 scénarios UX, nouveaux tickets S-067–S-101, performances, accessibilité et règles de priorisation.

---

# 0. Ce qui change par rapport à la roadmap v1

La roadmap v1 établissait 10 piliers et une séquence G0–G8 centrée sur les moteurs. **On les conserve comme fondation.** La v2 améliore cinq dimensions :

1. **Création graphique** : SmartSVG ne sera pas seulement un convertisseur ; il pourra assembler des compositions, textes, couleurs, formes et gabarits personnalisables.
2. **Fabrication informée du matériau** : un bon SVG d'édition ne suffit pas ; les contraintes de lame, de dimensions, de papier, de marge et de petits chemins deviennent des contrôles de premier rang.
3. **Projets réutilisables** : bibliothèque, versions, modèles, variantes et historique non destructif.
4. **Personnalisation et production** : variables (noms, numéros, dates), étiquettes en série, imposition de planches, estimation matière et reprise des lots.
5. **Exécution fractionnée et vérifiable** : chaque jalon est désormais découpé en *micro-lots* avec entrées, sorties, tests et décision d'arrêt.

### Discipline de périmètre

- **Noyau stable (C)** : indispensable avant une V22.0 utilisable régulièrement.
- **Extension forte (E)** : souhaitable après stabilisation du noyau ou si elle débloque clairement un usage principal.
- **Exploratoire (X)** : recherche, prototypes ou options futures ; ne doit pas retenir V22.0.
- **Interdit comme promesse (H)** : pilotage alternatif de Cricut, Print Then Cut sans Design Space, détourage parfait de tout visuel, SVG multicouche fidèle sur toute photo, ou certification sans essais matériels.

**Règle de capacité :** un seul micro-lot fonctionnel ouvert à la fois, et au maximum un chantier technique correctif transversal. Aucun élargissement en cours de jalon sans passage par le backlog.

---

# 1. Définition du produit final

### Positionnement

**SmartSVG = « Creative-to-Cut Studio » local : créer, préparer, contrôler, réutiliser, fabriquer.**

L'utilisateur ne devrait pas avoir besoin de comprendre les modèles IA, la topologie, les chemins SVG ou les nœuds de ComfyUI pour créer un sticker. Le moteur reste avancé, mais la façade est accessible. Le mode Expert conserve la puissance des réglages et du graphe.

### Six espaces fonctionnels, dans cet ordre d'importance

| Espace | Ce que l'utilisateur y fait | Priorité |
|---|---|---|
| **Express** | Importer → choisir un usage → vérifier → exporter | C |
| **Atelier** | Sélectionner des sujets, détourer, corriger, composer, écrire, organiser | C puis E |
| **Fabrique** | Régler taille et matériau, inspecter le parcours de découpe, disposer les planches | C puis E |
| **Vectoriel** | Modifier des calques, couleurs et courbes ; basculer entre SVG d'édition et SVG de coupe | C (séparation des formats), E (édition avancée) |
| **Bibliothèque** | Retrouver projets, ressources, versions, modèles et gabarits | C (projets), E (catalogue) |
| **Expert** | IA, paramètres avancés, fournisseurs, VRAM, diagnostics, jobs automatisés | C (diagnostic), E (API) |

**Règle transversale UX :** ces six espaces utilisent un seul état de projet. La navigation et les raccourcis suivent le contrat du §15 ; les compléments opérationnels sont au §36–§41.

Ces six espaces ne doivent **pas** devenir six logiciels distincts. Ils partagent un modèle de projet, une interface cohérente et un historique commun.

### Parcours minimal visé

`Importer / ouvrir → objectif (sticker, découpe, vecteur, composition) → détection → aperçu → retouche éventuelle → précontrôle → export → Design Space`

### Contrat de vérité

- **Graphique réussi** : l'apparence répond à l'objectif.
- **Vecteur éditable** : les objets/couleurs sont de vrais chemins modifiables, pas un PNG enveloppé.
- **Découpable** : la géométrie, les détails et le matériau choisi passent les contrôles connus.
- **Importable Cricut** : fichier réellement accepté dans une version définie de Design Space.
- **Fabriqué** : un essai physique sur Explore 5 a réussi.

Ces cinq niveaux **ne sont pas interchangeables**. Un indicateur doit préciser quel niveau est atteint.

---

# 2. Inventaire des capacités — état actuel / ambition

| Capacités | Situation de B0 (V21.14.1) issue de v1 | Cible finale |
|---|---|---|
| Alpha, fonds simples, planches 12/24 | Fonctionnement local démontré | Routage fiable + corrections visuelles + modèles variés |
| IA BiRefNet / RMBG / SAM2 | Adaptateurs/contrats, GPU utilisateur non prouvé | Fournisseurs testés, fallbacks, sélection sujet + accessoires |
| Masques/retouches | Moteur et éditeur présents | Édition ergonomique réversible et enregistrée |
| PNG Print Then Cut | Pipeline local historique testé | Profil de fabrication et recette Design Space / Explore 5 |
| SVG contour | Présent | Chemin de lame contrôlé selon taille et matériau |
| SVG multicouche | Prototype à fidélité visuelle partielle | Deux profils : édition fidèle / coupe réalisable |
| Qualité couleur SVG | Erreur encore significative | Gains mesurés sans faux « prêt Cricut » |
| Création avec textes/gabarits | Pas établie comme atelier complet dans v1 | Nouveau module de composition |
| Bibliothèque et variantes | Modèle portable proposé, non livré comme produit fini | `.smartsvg` ouvert, migrable, traçable |
| Variables et personnalisation en masse | Non démontré | Étiquettes nominatives, variantes, exports de série |
| UX grand public | Incomplète, historique chargé | Parcours Express sans graphe ComfyUI |
| Utilisation réelle Explore 5 | Non certifiée | Banc de tests par matériau et format |

**NB :** ce tableau reprend les constats de la roadmap v1. Les idées nouvelles de v2 sont des *fonctionnalités proposées*, pas des développements déjà réalisés.

---

# 3. Catalogue fonctionnel étendu — 15 familles

## F01 — Acquisition et diagnostic d'image [C]

**Indispensable :** PNG/JPG/WebP/SVG sûr ; taille, profil couleur, résolution utile, alpha réel, EXIF, cadrage, fond blanc/noir, bruit de compression, orientation, aperçu avant toute transformation.  
**À ajouter :** import d’un répertoire, collage presse-papiers, image glissée-déposée, détection de doublons, détection de captures smartphone et de cadres ; **vignettes avec provenance et mini-diagnostic**, import par lots avec sélection des fichiers à conserver ; aucune conversion silencieuse d’un SVG en bitmap.  
**Plus tard :** import PDF page par page avec rendu sûr, appareils photo, scanner, lots distants sous consentement.  
**Gate :** source et métadonnées préservées ; retour arrière fidèle ; aucune interprétation d'alpha inversé.

## F02 — IA de compréhension et sélection [C → E]

**Indispensable :** alpha → heuristique → fournisseur IA installé ; choix du sujet à la souris, inclusion d'accessoires, segmentation multi-sujets ; diagnostic explicite des cas incertains.  
**À ajouter :** relations parent/enfant/accessoire, sélection par phrase (« personnage avec sa canne »), segmentation interactive points positifs/négatifs, choix entre *objet*, *groupe*, *scène entière*, *texte* ; **miniatures de propositions et retour « mauvais sujet »** qui restaure immédiatement l’étape antérieure.  
**Plus tard :** apprentissage local de préférences de détourage avec validation, routage de plusieurs modèles selon résultats objectifs.  
**Gate :** les neuf cas référence proposent le bon sujet ou refusent proprement ; aucune IA annoncée comme réelle sans journal d'inférence.

## F03 — Correction et édition non destructives [C]

**Indispensable :** pinceau ajouter/enlever, lasso, sélection d'îlots, agrandir/rétrécir le masque, remplir trou, annuler/rétablir, zoom, aperçus noir/blanc/quadrillé et sauvegarde.  
**À ajouter :** édition des composants connectés, halo de bord, fusion/séparation d’éléments, avant/après synchrone, indicateur de pertes de détails, raccourcis accessibles ; **clic de sélection direct sur la toile, réglage de taille de pinceau en unités adaptées au zoom, loupe locale, aperçu d’un coup de pinceau avant validation, correction appliquée à plusieurs sujets uniquement après confirmation explicite**.  
**Plus tard :** remplissage IA sous supervision et outils géométriques avancés.  
**Gate :** après fermeture/réouverture, pixel et géométrie identiques ; aucune retouche perdue.

## F04 — Qualité raster et impression [C → E]

**Indispensable :** redimensionnement sans déformer, taille physique liée aux pixels, diagnostics de netteté/halo, choix entre source et version améliorée, profil PNG transparent.  
**À ajouter :** correction du moiré et des captures de moniteur, détourage anti-franges, palette d’impression, contrôle à 100 % et à la taille de sticker réelle ; **aperçu comparatif fixe, avertissement faible résolution relatif à la taille cible, diagnostics imprimables distincts des diagnostics de découpe**.  
**Plus tard :** super-résolution assistée par modèle local, avec mesure explicite d'hallucination et préservation de l'original.  
**Gate :** pas de « HD » factice ; un agrandissement interpolé est étiqueté comme tel.

## F05 — SVG multicouche éditable [C → E]

**Indispensable :** SVG réel, éléments colorés indépendants quand la source le permet, comparaison de rendu avec image source, métriques de silhouette et couleur distinctes, alerte sur simplification.  
**À ajouter :** préservation des traits internes, hiérarchie objet/calque, nombre de couleurs cible, fusion manuelle, Bézier, palette éditable, trous utiles, dégradés gérés avec repli explicite ; **sélection croisée toile↔liste des calques, isoler/masquer/verrouiller un calque, vue différences et bouton « simplifier sans toucher à l’original »**.  
**Plus tard :** retouche des points de contrôle, courbes manuelles, gradients éditables dans un profil générique, en respectant le profil Cricut différent.  
**Gate :** aucune image raster « camouflée » en SVG complètement éditable ; limites affichées.

## F06 — SVG de fabrication / géométrie des chemins [C]

**Indispensable :** chemins fermés, groupes, union/soustraction, orientation des contours, limites des petits îlots, détection doubles/triples découpes, taille en mm, simplification sans perte de fonction.  
**À ajouter :** prévisualisation « chemin de lame » indépendante des couleurs, estimation de complexité, ordre de couches, chevauchements de vinyles, points de connexion fragiles ; **alerte contextuelle cliquable permettant de localiser le défaut sur la toile et d’essayer un correctif réversible**.  
**Plus tard :** optimisation de parcours pour autres machines si leurs contrats sont connus et testés.  
**Gate :** seuils obtenus par essais matériaux et machine, pas par nombre arbitraire de pixels.

## F07 — Sticker et Print Then Cut [C]

**Indispensable :** PNG aplati/transparent, bordure blanche réglable, halo et trous, redimensionnement physique, planches dans les limites définies par Design Space, précontrôle local explicite.  
**À ajouter :** modes « contours individuels » / « planche à découpe extérieure » / « kiss cut vs die cut » uniquement si capacité matérielle testée, marges sécurisées, variants de bordure ; **assistant visuel A4/Letter pour positionnement, repère d’orientation et checklist Design Space sans réinventer les marques de capteur**. L’outil Autocollant de Design Space propose déjà bordures et types de coupe : SmartSVG doit donc se différencier par la préparation/validation des sujets et non les revendiquer comme des fonctions inédites.  
**Plus tard :** gabarits papier optimisés issus de dimensions supportées par la machine et non une copie des repères propriétaires.  
**Gate :** import Design Space + découpe Explore 5 ; aucune promesse sur tous supports réfléchissants.

## F08 — Composer et créer visuellement [E, socle minimal avant V22]

**Premier bloc :** canevas avec ajout d’image/texte/formes simples, aligner/distribuer, grouper, verrouiller, déplacer, redimensionner, tourner, dupliquer, calques et ordre Z ; **poignées sur la toile, contrôle direct des mesures mm, accroches visuelles désactivables, zones sûres visibles, menu contextuel des actions courantes**.  
**Ensuite :** guides, grille magnétique, palettes, styles, modèles de cartes/étiquettes, mise en page d'anniversaire et déco, arrière-plans interchangeables.  
**Plus tard :** masques de clipping, effets artistiques, pinceaux graphiques, automatisation de composition.  
**Gate :** réaliser une étiquette prénom et un sticker composé sans sortir de l'interface ; la composition reste éditable après sauvegarde.

## F09 — Typographie et texte [E]

**Premier bloc :** zones de texte, police locale, taille, alignement, suivi/espacement, rotation, couleurs, contour ; **prévisualisation des polices installées, avertissement sur glyphes manquants et aperçu texte à sa taille physique de fabrication**.  
**Ensuite :** texte courbe, texte sur chemin, polices préférées, caractères accentués, alphabets multiples, gestion des fontes manquantes à l'ouverture.  
**Export :** garder le texte éditable **dans le projet SmartSVG** ; convertir en chemins pour un SVG Cricut lorsque nécessaire, avec avertissement sur la non-éditabilité du texte côté fichier découpable.  
**Plus tard :** OCR guidé de textes d'affiches sans remplacer automatiquement le texte d'origine.  
**Gate :** pas de substitution silencieuse des polices ; rendu stable entre sessions.

## F10 — Bibliothèque, projet, variantes [C → E]

**Premier bloc :** conteneur `.smartsvg` portable, original non modifié, données de masques/retouches, paramètres, historique, chemins relatifs, images utilisées et manifeste.  
**Ensuite :** bibliothèque par tags, collections, favoris, modèles personnels, dérivations (« version Noël », « version fond noir »), recherche, duplication de projet ; **« Reprendre le dernier travail », miniatures différenciées, dossier de sortie ouvrable, favoris de préréglages, recherche par nom/usage/matière**.  
**Plus tard :** indexation visuelle locale et liaison à un catalogue externe sous consentement.  
**Gate :** importer/sauvegarder/rouvrir sur une autre installation ; aucune ressource manquante silencieuse.

## F11 — Planche, imposition et économie matière [C → E]

**Premier bloc :** disposer automatiquement les sujets en respectant dimensions, marges, absence de collision et limites du projet.  
**Ensuite :** rotations autorisées, groupement par matériau/couleur, optimisation de chute, estimation consommation de feuilles et coût indicatif ; **comparer deux propositions de disposition, verrouiller certains placements, déplacer un sticker sans casser la planche, remettre en place seulement les autres**.  
**Plus tard :** imbrication complexe de formes avec heuristiques vérifiées et fiches matière personnalisées.  
**Gate :** aucune collision et aucune zone hors page ; calcul de quantité de feuilles reproductible.

## F12 — Production en lots et personnalisation [E]

**Premier bloc :** 12/24/50 images, cache par étape, annulation/reprise, états par sujet et rapports.  
**Ensuite :** variables depuis CSV (`prenom`, `numero`, `date`, `couleur`), exemple de prénom imprimé, aperçus des variantes, tirages multiples, numérotation séquentielle ; **tableau de lot avec filtres réussi/à corriger/échoué, reprise ciblée, aperçu avant export de chaque groupe de variantes**.  
**Plus tard :** règles conditionnelles, catalogue de produits paramétrés et kits récurrents.  
**Gate :** interrompre volontairement un lot de 50, reprendre sans doublon ; contrôler chaque variante de texte.

## F13 — Profils de matériaux et projets en volume [E → X]

**Premier bloc :** profils *papier*, *carton léger*, *vinyle autocollant*, *vinyle thermocollant compatible*, avec recommandations non prescriptives et avertissement de test.  
**Ensuite :** calques par matériau, miroir quand pertinent, gabarits de pliage/pointillés compatibles uniquement si validés, ordre d'assemblage.  
**Exploratoire :** dioramas multicouches, cadres lumineux, scènes 3D à plans, patronages papier, pop-up et décorations pliées.  
**Gate :** prototypes assemblés et contrôles des tolérances, épaisseurs et attaches. Ne pas promettre la coupe de matériaux que la machine ne prend pas en charge.

## F14 — Ergonomie, apprentissage et accessibilité [C]

**Premier bloc obligatoire (MVP) :** démarrage orienté objectif, Express FR « Importer → Vérifier → Exporter », sélection visuelle d’objet, une action principale visible, correction contextuelle, unités en mm, état « prêt / à vérifier / bloqué » détaillé, retour arrière et reprise du dernier projet. Les interfaces ne doivent pas exposer le graphe ComfyUI en usage courant.

**Confort à introduire par tranches :** panneaux adaptables et repliables, menus contextuels, raccourcis mémorisés, vision originale/masque/coupe, guides magnétiques, présélections sûres, recherche d’actions, disposition mémorisée par espace, galerie de recettes, aperçu de fabrication à taille réelle, annuler une opération longue.

**Accessibilité obligatoire :** texte lisible et agrandissable, navigation clavier complète du flux Express, focus visible, labels explicites, états non dépendants de la couleur, alternative aux actions de glissement, cibles suffisamment grandes, contraste vérifié (WCAG 2.2 AA comme cible de conception web quand applicable), messages d’erreur exploitables.

**Optimisations non bloquantes :** traitement des lots depuis une file de tâches, éditions multiples, comparaison de variantes, préférences de raccourcis, tutoriels guidés, espace de travail personnalisable ; application autonome indépendante de ComfyUI seulement si justifiée.

**Gates :** sur navigateur réel, les cas T-02/U-01 et un échec sont réalisables sans ouvrir le graphe ; essai souris+clavier, restauration d’état après fermeture, absence de bouton inerte, mesure d’erreurs et de latence ; détails aux §§15, 36–41. Les seuils ergonomiques provisoires doivent être calibrés avec les premiers utilisateurs.

## F15 — Sécurité, confidentialité et qualité [C]

**Premier bloc :** fichiers SVG/XML sûrs, chemins d'archive contrôlés, droits d'accès limités, fichiers d'origine protégés, sauvegardes atomiques, masques bornés, manifestes SHA.  
**Ensuite :** observabilité locale, tests d'accessibilité, catalogue des dépendances et licences, journaux de performance et provenance IA.  
**Plus tard :** signature des extensions, mises à jour contrôlées, packs d'extensions tiers documentés.  
**Gate :** aucun upload réseau implicite de créations ; aucune perte des originaux ; erreurs reproductibles.

---

# 4. Sorties officielles : cinq produits, et non un seul « SVG »

| Sortie | Fichier | Modification garantie | Usage |
|---|---|---|---|
| **Sticker imprimé** | PNG RGBA aplati | Taille/cadrage dans Design Space ; détails couleur non éditables séparément | Print Then Cut |
| **Contour unique** | SVG de coupe 1 couche | Courbe éditable | Vinyle/papier, coupe simple |
| **Calques couleur de coupe** | SVG de fabrication multicouche | Chemins/couleurs par couche | Assemblage de vinyle/papier après validation |
| **Illustration vectorielle** | SVG d'édition haute fidélité | Formes/couleurs (selon capacités du document) | Retouche dans SmartSVG/Inkscape/Canva ; **pas automatiquement découpe** |
| **Projet reproductible** | `.smartsvg` versionné | Source, textes, variantes, masque, positions, palette, historique | Reprendre plus tard |

### Dossiers d'export recommandés

```
Projet/
  00_LIRE_AVANT_IMPORT/
  01_CRICUT_PRINT_THEN_CUT/
  02_CRICUT_BASIC_CUT/
  03_SVG_EDITABLES_NON_CERTIFIES/
  04_PLANCHES/
  05_APERCUS_ET_QA/
  projet.smartsvg
  manifest.json
```

L'utilisateur doit voir **quel fichier importer**, pour **quelle opération**, et **ce qui reste à contrôler**. Les rapports ne peuvent pas appeler « certifié » un artefact dont aucun test matériel n'a été réalisé.

### Contraintes externes reconnues dans la conception

- Design Space importe les PNG en image de base et les SVG/DXF en vecteurs ; un SVG multilayer ne remplace pas un PNG Print Then Cut.
- Les SVG chargés dans Design Space ont une limite publiée de **5 000 chemins** ; un nombre bien inférieur peut être nécessaire pour une découpe raisonnable.
- Des éléments tels que du texte SVG encore éditable, des images liées et certains remplissages peuvent empêcher un import correct ; prévoir un **profil export Cricut** distinct.
- La zone Print Then Cut dépend de la machine, du format papier et des proportions du motif ; ne pas fixer une taille maximale universelle.
- Les repères Print Then Cut et la conduite de la machine restent du ressort de Design Space ; impression et découpe doivent être effectuées dans le flux approprié.

Références officielles vérifiées : https://help.cricut.com/hc/en-us/articles/360009556313-How-to-upload-images-into-Design-Space ; https://help.cricut.com/hc/fr/articles/360009553213-T%C3%A9l%C3%A9chargements-d-images-%C3%A9l%C3%A9ments-non-pris-en-charge ; https://help.cricut.com/hc/fr/articles/360009429814-Quelle-taille-puis-je-imprimer-puis-d%C3%A9couper-nbsp ; https://help.cricut.com/hc/fr/articles/360009387274-Comment-Imprimer-puis-d%C3%A9couper-dans-Design-Space

---

# 5. Architecture cible et frontières entre modules

```
INTERFACE (Express / Atelier / Fabrique / Bibliothèque / Expert)
                     │
                     ▼
PROJECT ENGINE — documents, scènes, objets, versions, journal
                     │
            ORCHESTRATEUR DE TÂCHES
                     │
    ┌────────────────┼──────────────────────┐
    ▼                ▼                      ▼
ACQUISITION       VISION / IA           GRAPHICS ENGINE
sources/alpha     objets/masques         formes/texte/courbes
    └────────────────┼──────────────────────┘
                     ▼
              FABRICATION ENGINE
       dimensions, couches, contours, pages
                     │
          QUALITY GATE & EXPORTER
                     │
  PNG Print Then Cut / SVG Cut / SVG Art / projet
                     │
                  Design Space
```

## Invariants techniques

1. Original immuable ; tous les traitements génèrent des dérivés identifiables.
2. Une identité d'objet stable (`subject_id`) de la détection à la sortie, sans dépendre de l'ordre temporaire des masques.
3. Une seule unité physique de référence (mm) avec conversion explicite en pixels/ppi ; la taille affichée correspond à l'objet utile, marge comprise ou non selon libellé.
4. Les masques d'analyse sont distingués des géométries de coupe et des objets graphiques.
5. Les fournisseurs IA sont des adaptateurs remplaçables, jamais des dépendances cachées de l'ouverture d'un projet.
6. Aucun composant d'interface ne peut annuler ni masquer un export déjà réussi.
7. Les profils matériaux contiennent des valeurs **calibrées et tracées**, ou marquées *à vérifier*, jamais des paramètres présentés comme universels.
8. Les fichiers externes ne déclenchent aucun script ni résolution d'URL externe sans action utilisateur.
9. Chaque extension doit préserver les anciens contrats d'entrée et de sortie, ou passer par un adaptateur de migration testé.
10. Les résultats de benchmark enregistrent versions, plateforme, échantillon, méthode, limites et erreurs, pas seulement une note « OK ».

## Schémas de données à définir avant interface nouvelle

- `SourceAsset`: source SHA, orientation, couleurs, métadonnées, licence, provenance.
- `Subject`: ID stable, bounding box, masque, composants liés, sélection, incertitude.
- `VectorLayer`: chemins, couleurs, trous, appartenance objet, version moteur et score de rendu.
- `TextElement`: chaîne Unicode, référence de police, droits, position, courbe si nécessaire.
- `CanvasDocument`: canevas, calques, transformation, guides, zones de sécurité, historique.
- `MaterialProfile`: matière, épaisseur connue/estimée, méthode, calibrations, provenance.
- `CutPlan`: unités, parcours, arêtes fragiles, nombre de chemins, collisions, warnings.
- `Project`: version schéma, ressources, variantes, journaux, dépendances, migrations.
- `Artifact`: type d'usage, destination, fichiers, SHA, état de validation, instructions.
- `QAResult`: niveaux distincts *informatique / géométrique / visuel / import / physique*.

## Packaging prudent

**Première voie** : extension ComfyUI avec façade guidée, mais moteurs testables indépendamment.  
**Seconde voie éventuelle** : application locale autonome bâtie sur les mêmes moteurs, seulement après démonstration que l'UX actuelle bloque les utilisateurs.  
**Pas d'obligation** de réécrire immédiatement toutes les anciennes classes ou les workflows historiques (186 déclarés, à vérifier dans B0) : migration incrémentale par catégories avec liste de correspondance.

---

# 6. Roadmap séquencée — petits lots, validation obligatoire

On conserve les étapes G0–G8 de v1, mais on les décompose. Les noms de versions ne sont **pas** une annonce de livraison. Certains micro-lots peuvent donner lieu à plusieurs correctifs sans ouvrir le jalon suivant.

## G0 — Référence et préparation [gel maintenu]

| Micro-lot | Livrable | Critère d'acceptation |
|---|---|---|
| G0.1 | SHA, manifeste, sauvegarde V21.14.1 | Archive source et référence inchangées |
| G0.2 | Corpus versionné (T-01 à T-09, R-01/R-02) | Originaux, variantes et consignes documentés |
| G0.3 | Jeu de vérité terrain (masques et objectifs) | Deux personnes peuvent juger le même résultat avec une grille commune |
| G0.4 | Matrice des risques et exceptions | Aucun essai sur matériel présenté comme simulation réussie |

**Sortie G0 :** cahier des charges et banc de test prêts. Pas de changement fonctionnel.

## G1 — Architecture / fiabilité / projet [V21.15 indicative]

| Lot | Développement limité | Preuve à produire |
|---|---|---|
| **G1.1** | Inventaire des nœuds et des workflows (186 annoncés, **décompte à confirmer**), dépendances, usages réels | Catalogue Stable/Historique/Expert, anciens workflows ouvrables |
| **G1.2** | Contrats `SourceAsset / Mask / Subject / Artifact / QAResult` | Tests de schéma, invariants de dimensions/polarité, conversions |
| **G1.3** | Projet `.smartsvg` minimal (source + masques + corrections) | Sauver, fermer, rouvrir, restaurer bit à bit les retouches |
| **G1.4** | Gestion des erreurs, tests d'installation, rollback | Erreur UI sans perte du calcul, rollback vérifié |
| **G1.5** | Point d'entrée Express unique et historique rangé | Une seule entrée recommandée par tâche, sans casser anciennes IDs |

**Gate G1 :** test d'installation sur copie, zéro régression PNG/SVG, projet réouvert, formats clarifiés.

## G2 — Fondations de l'expérience et des exports [V21.15.x / V21.17 partiel]

| Lot | Développement limité | Preuve à produire |
|---|---|---|
| **G2.1** | Coquille UI « Importer → Vérifier → Exporter » | Import simple sans toucher au graphe |
| **G2.2** | Sélection de sujet à la souris, état des masques | Choisir le bon sujet et accessoires sur cas simples |
| **G2.3** | Prévisualisation avant/après, persistance retouches | Comparaison, annuler/refaire, réouverture fidèle |
| **G2.4** | Modes de sortie visibles et instructions Design Space | Impossible de confondre PNG, SVG Cut et SVG Edit |
| **G2.5** | Architecture d’écran, états vide/chargement/erreur, panneau contextualisé | Navigation continue sur 1366×768 et 1920×1080 sans action perdue |
| **G2.6** | Alertes localisables et correctifs réversibles en un flux | Cas masque rectangle réparé ou refusé, sans faux « prêt » |
| **G2.7** | Focus, clavier, alternatif au drag, zoom texte, contrastes | Parcours Express entièrement opérable souris et clavier |
| **G2.8** | Prévisualisations source/masque/découpe synchronisées | Bascules et restauration de vue testées, sans changements implicites d’export |
| **G2.9** | Reprise d’activité, favoris et réglages explicites | Même projet et action après réouverture, sans nouvel upload |

**Gate G2 :** un novice prépare un PNG sticker simple en restant dans l’interface ; un cas d’erreur est récupérable ; clavier/souris et écran 1366×768 vérifiés ; on note actions, temps par étape, erreurs et incompréhensions sans déclarer une latence non mesurée.

## G3 — Validation IA réelle [V21.16 indicative]

| Lot | Développement limité | Preuve à produire |
|---|---|---|
| **G3.1** | Diagnostic environnement sur la machine cible | Inventaire versions/mémoire/poids des modèles, sans faux « compatible » |
| **G3.2** | Test BiRefNet Lite et RMBG-2.0 sur 3 cas distincts | Masques sauvegardés, temps, pic VRAM, erreurs |
| **G3.3** | Test SAM2 et sélection interactive | Personne/objet/accessoires, refus d'ambiguïtés |
| **G3.4** | Choix prudent de fournisseur et fallback OOM | Routeur ne dégrade pas les cas déjà bons |
| **G3.5** | Correction assistée contrôlée | Proposition non destructrice, validation visuelle obligatoire si doute |

**Gate G3 :** les neuf cas de référence obtiennent un résultat évalué ou un refus utile ; tous les statuts indiquent l'IA réellement exécutée. Une RTX 3070 8 Go n'est pas présumée capable de tout modèle.

## G4 — Production Cricut de base [V21.18 indicative]

| Lot | Développement limité | Preuve à produire |
|---|---|---|
| **G4.1** | PNG Print Then Cut : taille, marges, alpha, trous, halos | Import Design Space contrôlé sur plusieurs formats |
| **G4.2** | SVG Basic Cut : fermeture, micro-chemins, doubles coupes | SVG découpable réellement importé ; profil matériau associé |
| **G4.3** | Fiche de validation Explore 5 et calibrations | Coupon imprimé puis découpé ; erreurs mesurées |
| **G4.4** | Planche 12 puis 24 sujets + rapport par objet | Zéro hors-page, trous parasites et doublons non signalés |
| **G4.5** | Suite de recette de trois matières courantes | Résultats photo + annotations + paramètres utilisés |
| **G4.6** | Checklist prévol interactif et aide de transfert vers Design Space | Dossier et fichier exact indiqués, orientation A4 vérifiée, aucune fausse automatisation de Design Space |

**Gate G4 :** au moins les parcours *sticker imprimé*, *silhouette simple* et *planche* sont testés physiquement. Le logiciel ne fabrique pas lui-même les marques de capteur Design Space.

### **Palier important : MVP stable de fabrication**

Après G4, une version stable limitée aux **stickers imprimés et découpes simples** peut être envisagée, sous réserve de tous les tests d'installation et de sécurité. Il ne faut **pas** attendre la perfection du SVG couleur pour disposer d'un outil utile au quotidien. Cette étape est un produit intermédiaire, pas encore la vision finale.

## G5 — Vectoriel fidèle et coupe multicouche [V21.19 indicative]

| Lot | Développement limité | Preuve à produire |
|---|---|---|
| **G5.1** | Audit du SVG standard rendu vs original | IoU, couleur, trous, quantité de chemins séparées |
| **G5.2** | Préservation des traits internes et petites couleurs | Amélioration réelle sans dégrader la découpe |
| **G5.3** | Regroupement et simplification Bézier | Moins de chemins à qualité comparable |
| **G5.4** | Outils de regroupement/calques et palette éditable | Formes modifiables dans Inkscape et dans l'Atelier |
| **G5.5** | Export séparé « SVG d'édition » / « SVG Cricut » | Aucun SVG d'édition riche présenté comme directement découpable |
| **G5.6** | Découpe réelle de calques simples | Prototype multicouche assemblé, avec feuille matière |

**Gate G5 :** métriques sur planches adaptées, courbes réellement éditables, aucun micro-chemin critique non signalé ; les illustrations complexes disposent d'un fallback honnête.

## G6 — Atelier de composition minimal [V21.19.x / V22.x selon maturité]

| Lot | Développement limité | Preuve à produire |
|---|---|---|
| **G6.1** | Texte + formes + position, rotation et calques | Créer une étiquette simple sans autre logiciel |
| **G6.2** | Groupe, alignement, grille, palette | Composer un sticker personnalisé sans perte de placement |
| **G6.3** | Export de texte stable (police manquante, contours SVG Cricut) | Texte modifiable dans projet et importable en tracés si besoin |
| **G6.4** | Trois gabarits métiers : étiquette, topper, carte | Fabriquer au moins un prototype de chaque usage déclaré |
| **G6.5** | Historique et variantes de composition | Sauvegarder/reprendre/dupliquer sans écraser le projet initial |
| **G6.6** | Alignements directs, réglage mm, menus contextuels, actions multiobjet | Même composition reproductible par souris et clavier ; undo fiable |
| **G6.7** | Gabarits-guides et démarrage sur usage | Réaliser étiquette/carton/sticker simple sans tutoriel externe |

**Gate G6 :** l'Atelier permet un vrai projet composé, sans ambition de concurrencer l'ensemble de Canva.

## G7 — Factory, bibliothèque et personnalisation [V21.20 indicative]

| Lot | Développement limité | Preuve à produire |
|---|---|---|
| **G7.1** | Cache de jobs / pause / reprise | 50 images, interruption volontaire sans perte ni doublon |
| **G7.2** | Bibliothèque de projets, miniatures, tags | Rechercher/réutiliser un projet sans duplication opaque |
| **G7.3** | Variables CSV pour prénoms, dates et numéros | Exports de 30 variantes contrôlés un par un |
| **G7.4** | Imposition et coût matière indicatif | Zéro collision, quantité de feuilles et rebuts mesurables |
| **G7.5** | Packs de production lisibles | Rapports, PNG/SVG, instructions, variantes et manifestes traçables |
| **G7.6** | Tableau de lot, filtres « à revoir », relance unitaire, rapports ouverts au clic | 50 items ; 1 erreur n’oblige pas à tout recommencer |

**Gate G7 :** production reproductible et dossiers exploitables, sans nécessité d'ouvrir chaque image individuellement.

## G8 — Recette, sécurité et stable V22.0 [V21.21 RC → V22.0]

| Lot | Développement limité | Preuve à produire |
|---|---|---|
| **G8.1** | Tests Windows + ComfyUI + dépendances | Installations vierges et mises à jour/rollback documentés |
| **G8.2** | Sécurité fichier, accessibilité, sauvegarde | Zéro perte de projet, erreurs maîtrisées, navigation testée |
| **G8.3** | Recettes réelles et benchmarks externes | Procédure identique Canva/Design Space/SmartSVG |
| **G8.4** | Documentation, aide contextuelle, tutoriels | Un utilisateur novice réalise les tâches principales |
| **G8.5** | Gel des nouvelles fonctions et traitement des bugs | Aucun P0/P1 bloquant avant V22.0, matrice de compatibilité validée |
| **G8.6** | Recette UX multi-résolutions, accessibilité et tests de reprise | Scénarios U/T couverts, compte rendu observé, régressions UX P0/P1 corrigées |

**Gate G8 :** **V22.0 stable de préparation Cricut**. Les fonctions exploratoires qui n'ont pas leur gate restent derrière un statut bêta ou passent en V22.x.

## G9 — Extensions avancées après V22.0 [V22.x / V23, sans engagement de calendrier]

| Extension | Première preuve exigée avant lancement |
|---|---|
| Dioramas et cadres multicouches | Un assemblage physique simple documenté, profil matière connu |
| Vinyle multicouleur / thermocollant | Test réel de calques, miroirs et superpositions sur matériau compatible |
| Cartes pop-up / plis | La machine et l'outillage prennent en charge l'opération visée |
| OCR et reconstitution de textes | Conserver les textes originaux et signaler les incertitudes |
| Upscale IA avancé / styles graphiques | Qualité comparée à taille imprimée et refus des hallucinations critiques |
| Application autonome locale | Argument coût/maintenance/UX démontré, moteurs déjà indépendants |
| Catalogue produit et modèles commerciaux | Gestion des licences et droits documentée, aucune promesse de revente d'IP tierce |

---

# 7. Mini-backlog opérationnel après le gel

Les IDs **S-001 à S-022 de v1** sont conservés et leur définition source est reproduite au §33.1 ; les entrées S-023 à S-048 complètent le plan :

| ID | Lot | Priorité | Unité de travail | Dépendance | Critère mesurable |
|---|---|---|---|---|---|
| S-023 | G1.2 | P0 | Identité de sujet stable | S-003 | Identité persistante après retouche et export |
| S-024 | G1.3 | P0 | Projet `.smartsvg` v1 | S-003 | Chargement exact des masques, sources et actions |
| S-025 | G2.1 | P0 | Écran Express métier | S-004 | Sticker simple sans graphe |
| S-026 | G2.3 | P0 | Historique non destructif UI | S-024 | Undo/redo/reload conformes |
| S-027 | G3.2 | P0 | Contrôle GPU réel | S-005 | VRAM et latence mesurées |
| S-028 | G3.3 | P0 | Groupes sujet + accessoires | S-006,S-027 | Pas de perte silencieuse des détails annotés |
| S-029 | G4.1 | P0 | Contrat PNG/alpha Cricut | S-002 | Import Design Space contrôlé |
| S-030 | G4.2 | P0 | Contrat SVG Basic Cut | S-002 | Chemins fermés, géométrie contrôlée |
| S-031 | G4.3 | P0 | Matrice d'essais Explore 5 | S-029,S-030 | Coupons fabriqués et documentés |
| S-032 | G5.5 | P0 | Export SVG édition vs fabrication | S-011,S-030 | Aucun profil confondu |
| S-033 | G5.2 | P1 | Préservation traits et petites régions | S-011 | IoU, MAE et risques suivis |
| S-034 | G5.3 | P1 | Simplification de Bézier | S-033 | Courbes réduites à fidélité non dégradée |
| S-035 | G6.1 | P1 | Canevas objets/textes | S-024 | Composition éditable après réouverture |
| S-036 | G6.3 | P1 | Fonts et conversion textes → tracés | S-035 | Pas de substitution silencieuse |
| S-037 | G6.4 | P1 | Gabarits métiers | S-035 | Trois gabarits testés |
| S-038 | G7.1 | P1 | Job manager et checkpoints | S-024 | Reprise 50/50 sans doublon |
| S-039 | G7.3 | P1 | Variables CSV | S-035,S-038 | 30 variantes sans texte manquant |
| S-040 | G7.4 | P1 | Imposition mesurable | S-029,S-030 | Zéro collision, dimensions cohérentes |
| S-041 | G7.2 | P1 | Bibliothèque locale | S-024 | Recherche/duplication/archivage fiables |
| S-042 | G8.2 | P0 | Audit de sécurité des projets | S-024 | Entrées adversariales contenues |
| S-043 | G8.3 | P0 | Benchmark Canva/Design Space | S-031,S-032 | Procédure égale, répétée et auditée |
| S-044 | G9 | P2 | Dioramas multi-plans | S-030,S-035 | Prototype réel assemblé |
| S-045 | G9 | P2 | Vinyle multi-couleur | S-030,S-031 | Test superposition concluant |
| S-046 | G9 | P2 | Application autonome | S-025,S-038 | Étude de coût et de maintenance |
| S-047 | G9 | P2 | OCR texte de couverture | S-028,S-036 | Texte vérifié avant tout remplacement |
| S-048 | G9 | P2 | Upscale IA artistique | S-027,F04 | Audit des détails inventés |

### Règle pour chaque ticket

Tout ticket possède : **objectif en une phrase, entrée témoin, sortie attendue, tests automatiques, essai visuel ou physique si nécessaire, invariant de non-régression, estimation de complexité, rollback**. Il ne peut être fermé avec « semble fonctionner ».

---

# 8. Corpus de validation, y compris les nouveaux projets créatifs

## 8.1 Corpus technique obligatoire conservé

| ID | Image | Objectif | Ce qui ferait échouer |
|---|---|---|---|
| T-01 | Fille manga en capture d'écran | Retenir visage/cheveux, supprimer cadre si demandé | Cadre conservé à tort ou cheveux perdus |
| T-02 | 12 escargots | 12 sujets, fleurs conservées | Guides pointillés ou stickers fusionnés |
| T-03 | « Mon cadeau… » | Choix personnage/cadeau/affiche complète | Suppression tacite du texte |
| T-04 | Leprechaun avec chopes | Personne + accessoires ciblés | Verres, mains ou barbe amputés |
| T-05 / T-06 | Deux affiches fantastiques | Carte entière ou personnage spécifique | Texte ou objet non demandé choisi |
| T-07 | Technicien en atelier | Personne + options outils/câbles | Petits détails supprimés sans avertissement |
| T-08 | Couverture manhwa avec texte coréen | Sujet ou couverture, sans OCR forcé | Texte altéré ou fausse transcription |
| T-09 | 24 Pokémon sur fond noir | 24 sujets, accessoires, bords | Îlots ignorés ou double coupe |
| R-01 / R-02 | Capture canard / illustration Psyduck | Contrôles adversariaux de cadrage | Fond/objet confondus |

## 8.2 Nouveaux cas d'usage complets

| ID | Projet de fabrication | Ce qu'il doit valider | Phase |
|---|---|---|---|
| U-01 | Sticker nominatif à partir d'un dessin | Texte + sticker + marge + Print Then Cut | G4/G6 |
| U-02 | 30 étiquettes avec des prénoms différents | Variables, caractères FR, imposition, zéro omission | G7 |
| U-03 | Silhouette d'animal en vinyle uni | SVG Basic Cut, simplification, petites formes | G4 |
| U-04 | Logo simple en trois couleurs | SVG éditable, couches séparées, superposition | G5 |
| U-05 | Carte d'anniversaire avec texte et illustration | Composeur, sauvegarde, export | G6 |
| U-06 | Petite scène papier en 4 plans | Matières, calques, alignement, assemblage | G9 |
| U-07 | Dossier de 50 dessins mélangés | File, cache, erreurs isolées, reprise | G7 |
| U-08 | Réouverture d'un ancien workflow ComfyUI | Compatibilité et migration sans perte | G1/G8 |
| U-09 | Sticker imprimé mat vs brillant | Risque capteur / limites matière | G4 |
| U-10 | Design personnalisé avec police manquante | Fallback explicite / conversion tracés | G6 |

**Important :** conserver des images d'origines diverses **dont les droits sont connus** pour les packs de démonstration publics. Les Pokémon et autres visuels protégés servent à des essais locaux ; leur utilisation commerciale est une question de licence distincte.

---

# 9. Metrics / quality gates par couche

| Couche | Mesure | Cible proposée, à recalibrer sur corpus |
|---|---|---|
| Détection | Nombre de sujets corrects | 12/12 escargots, 24/24 Pokémon sur données annotées |
| Sémantique | Objet réellement souhaité | Aucun mauvais sujet annoncé validé dans corpus négatif |
| Alpha | Aucune inversion et dimension exacte | 100 % des fixtures alpha et JPEG sentinelle |
| SVG silhouette | IoU rendu vs masque référence | ≥98 % sur illustrations plates compatibles |
| SVG couleur | Erreur RGB (MAE, protocole fixe) | Seuil initial ≤12 sur sous-ensemble annoncé ; mesurer aussi les détails perdus |
| SVG coupe | Chemins ouverts, doublons, micro-formes | Aucun critique non signalé sur profil calibré |
| Print Then Cut | Taille, image aplatie, contour | Import réel et coupon découpé positif |
| Sauvegarde | Reconstruction projet | Masques/texte/calques identiques après réouverture |
| Factory | Interruption/reprise de lot | Aucun fichier perdu/dupliqué, statuts fiables |
| UX — compréhension | Erreurs de cible, aide demandée, choix de format erroné | Cas novice : compréhension du format sans graphe, échec expliqué |
| UX — tâches | Taux d’achèvement autonome, actions, retours arrière, temps médian/p90 | Cibles provisoires définies par tâche et avant/après ; aucune réduction proclamée sans benchmark |
| UX — ergonomie | Clics inertes, contrôles inaccessibles, pertes de sélection, zoom inattendu | Zéro contrôle principal inerte / perte de projet ; scénarios souris/clavier |
| UX — réactivité | Latence visualisation/aperçu, blocage du fil UI, reprise | Budget à calibrer sur PC cible avec échantillon, pas de « temps réel » garanti |
| Sécurité | Échec sur ressources hostiles | Aucun fichier écrit hors répertoire cible sans permission |
| Comparaison Canva | Temps, actions, qualité finale | Supériorité seulement si données comparables le montrent |

### Benchmarks justes

Trois répétitions par tâche, mêmes sources, même dimension physique, même utilisateur ou protocole standardisé, versions et abonnements indiqués ; consigner succès, temps, clics, temps correctif, erreur de fabrication, coût et consommation d'encre/matière. Canva Vectorify propose déjà des formes vectorielles modifiables ; ce n'est donc pas une fonction unique à SmartSVG. Référence : https://www.canva.com/fr_fr/help/convert-images-to-vectors/.

---

# 10. Performance, mémoire et sécurité : exigences explicites

### RTX 3070 8 Go / RAM 32 Go — cible connue, pas résultat garanti

- Préférer un modèle léger quand il donne un masque adéquat, puis monter en complexité seulement si le résultat est insuffisant.
- Un seul modèle GPU lourd actif à la fois si les tests le justifient ; pas de fuite de poids entre jobs.
- Budgets RAM/VRAM configurables ; dégradation élégante, pas d'effacement des projets au crash.
- Cache des masques, miniatures et courbes calculé par empreinte d'entrée et de paramètres.
- Les aperçus doivent être générés en résolution adaptée ; la haute résolution n'est traitée qu'aux étapes qui la nécessitent.
- Pas de téléchargement silencieux de poids : taille, emplacement, source et consentement clairs.
- Journaliser temps par phase (analyse, segmentation, retouche, vectorisation, export) et débit des lots.
- Borne sur nombre d'objets, densité des SVG et éléments XML, chemins longs, récursion et images malformées.

### Protection du projet

- Archive du projet créée de manière atomique, restaurable et versionnée.
- Historique sauvegardé sans explosion illimitée du disque ; politique de rétention visible.
- Références de fichiers sûres ; pas de chargement de contenus distants par défaut ; secrets jamais inclus dans les exports.
- Manifeste SHA et version du moteur de chaque artefact pour vérifier les transformations.

---

# 11. Comment découper et gouverner les travaux

## 11.1 Gabarit d'un micro-lot

```
ID / jalon : Gx.y
Problème utilisateur :
État de la base :
Un changement principal :
Interfaces/modules modifiés :
Compatibilités à préserver :
Cas de test positifs :
Cas adversariaux :
Mesure visuelle ou physique :
Critère d'arrêt :
Livrables : source + ZIP + diff + rapport + rollback
Décision : GO / GO avec réserve documentée / NO GO
```

## 11.2 Rythme qualitatif

1. **Spécifier et reproduire** : état actuel et témoin fiable.
2. **Implémenter la plus petite évolution** : un composant et ses adaptateurs.
3. **Tests unitaires et adversariaux** : ne pas s'appuyer uniquement sur les anciennes suites.
4. **Non-régression** : mêmes artefacts utiles avant/après, sauf changements explicitement approuvés.
5. **Validation physique si pertinent** : pas de faux statut de découpe validée.
6. **Rapport GO/NO GO et gel du lot** avant ouverture du suivant.

## 11.3 Règles de priorité

- P0 : perte de données, export faux, dimensions incohérentes, risque de découpe trompeuse, projet inutilisable.
- P1 : flux principal difficile, gros défaut visuel, performance, absence de contrôle pratique, migration compliquée.
- P2 : modèles nouveaux, optimisations de confort, options supplémentaires utiles mais non bloquantes.
- P3 : effets décoratifs, expérimentations, autres machines et services non nécessaires.

**WIP limite :** 1 fonctionnalité + 1 correctif ; pas de trois versions parallèles. À chaque jalon : archivage de la base et possibilité de revenir à la précédente sans intervention manuelle lourde.

---

# 12. Le vrai objectif final, organisé en deux niveaux

## V22.0 — Produit stable essentiel

**Contrat de sortie V22.0** : MVP G4 matériellement documenté ; PNG stickers, SVG contour, sélection/correction et planches 12/24 ; Express complet sans graphe ; projet `.smartsvg` robuste ; formats visuels/physiques séparés ; installation, QA et sécurité G8 ; diagnostic IA G3.1 et au moins une chaîne IA réelle testée sur cas pris en charge **ou** fonction IA explicitement limitée/désactivée sans prétendre qu'elle est livrée ; composition simple texte+forme+calques si son gate G6.1/G6.3 est atteint (sinon annoncer son report et ne pas l'inclure dans le périmètre publié). **SVG multicouche : état expérimental ou validé par scénario, jamais « certifié » sans essais.** La production robuste des 50 lots, la totalité de la bibliothèque et la vectorisation photo fidèle ne sont pas des bloqueurs V22.

**Ne doit pas attendre** : un clone complet de Canva, les dioramas 3D, l'OCR avancé, une IA parfaite sur toutes photos, 100 outils de dessin, un traitement de 50 visuels en toute circonstance ou une application autonome. Le manifeste de version V22.0 doit distinguer « livré », « option bêta », « reporté ».

## Vision étendue V22.x / V23 — Atelier créatif complet

**Pourra permettre** : composition texte/illustration, modèles, bibliothèque riche, variables CSV, multi-matériaux, préparation de dioramas et pop-ups, optimisation des planches, palettes et SVG complexes, éventuellement une application indépendante de ComfyUI.

La vision finale est ambitieuse, mais la **sortie stable reste volontairement plus courte** pour obtenir rapidement un outil utile et éviter le piège du développement permanent.

---

# 13. Dix décisions à figer avant toute reprise du code

1. Confirmer la liste des **cinq sorties** et leurs règles de validation distinctes.
2. Décider du format minimal de projet et de ses migrations.
3. Définir l'identité stable des sujets et les relations avec accessoires.
4. Choisir les trois parcours de validation utilisateur prioritaires : sticker seul, planche 12/24, photo à corriger.
5. Fig­er les jeux de référence et leurs masques annotés.
6. Définir les seuils de qualité **provisoires**, avec provenance, avant de benchmarker.
7. Valider le schéma des profils matériels sans y insérer des valeurs de découpe inventées.
8. Définir le statut exact des SVG multicouches expérimentaux.
9. Maintenir le gel SHA de V21.14.1 sans réécriture du ZIP.
10. Ouvrir **G1.1 seul** en premier lors du dégel : inventaire des classes, interfaces et décompte vérifié des workflows (186 annoncés).

---

# 14. Sources externes et réserves

Recherche publique vérifiée le **24 octobre 2026** :

- Cricut Design Space, import et types vectoriels, limitation des chemins SVG : https://help.cricut.com/hc/en-us/articles/360009556313-How-to-upload-images-into-Design-Space
- Cricut, éléments SVG non pris en charge : https://help.cricut.com/hc/fr/articles/360009553213-T%C3%A9l%C3%A9chargements-d-images-%C3%A9l%C3%A9ments-non-pris-en-charge
- Cricut, tailles Print Then Cut : https://help.cricut.com/hc/fr/articles/360009429814-Quelle-taille-puis-je-imprimer-puis-d%C3%A9couper-nbsp
- Cricut, guide officiel Print Then Cut et calibration : https://help.cricut.com/hc/fr/articles/360009387274-Comment-Imprimer-puis-d%C3%A9couper-dans-Design-Space
- Canva Vectorify : https://www.canva.com/fr_fr/help/convert-images-to-vectors/

**Réserves :** les seuils de fabrication devront être définis par des tests sur le matériel réellement utilisé. Les coûts, délais de développement et gains de performances ne sont pas inférés à partir des seules capacités théoriques. L'archive gelée n'a pas été modifiée pendant cette révision de roadmap.

---

## Décision de direction

**La bonne stratégie n'est pas d'accumuler des fonctionnalités : c'est de construire une plate-forme capable de produire des résultats maîtrisés, puis d'étendre méthodiquement les usages.**

La prochaine action après validation de ce document est **G1.1 : inventaire et assainissement**, sans nouvelle vectorisation IA ni réécriture globale tant que les interfaces et formats de projet ne sont pas contractualisés.

---

# PARTIE II — ADDITIONS DIRECTRICES v3.0

*Les sections ci-dessous précisent et complètent les 15 familles et les jalons conservés ci-dessus. En cas de conflit de détail, les critères de sécurité et les précisions v3 priment ; le code B0 et les éléments archivés ne sont pas modifiés.*

## 15. Le produit vu de l'utilisateur : navigation unique et six espaces

**Une application, un modèle de projet, six vues.** Chaque vue agit sur les mêmes `SourceAsset`, `Subject`, `CanvasDocument` et `Artifact`. Toute action produit une modification versionnée, non une copie anonyme de l'image.

| Vue | Écran initial obligatoire | Actions principales | Ne doit jamais imposer |
|---|---|---|---|
| **Express** | Visuel glissé-déposé, « Que veux-tu faire ? », taille mm, bouton aperçu | `Sticker`, `Découpe simple`, `SVG éditable`, `Planche` ; aperçu, correction rapide, export | Choisir un modèle IA ou ouvrir un graphe. |
| **Atelier** | Toile centrale, liste de sujets à droite, outils simples à gauche | Isoler, ajouter/enlever, fusionner, effacer frange, annuler, déplacer, dupliquer | Comprendre une opération booléenne avant de détourer. |
| **Fabrique** | Prévisualisation matériau/page/ligne de coupe + dimensions | Choisir matière, épaisseur si pertinente, bordure, marge, trous, disposition, vérifier et exporter | Croire qu'une simulation équivaut à une coupe testée. |
| **Vectoriel** | Original / rendu / différences, arborescence de calques | Fusion/séparation, palettes, contour, lissage, détails, profils Art et Cut | Traiter un SVG contenant un bitmap comme des tracés intégralement éditables. |
| **Bibliothèque** | Grille de projets et filtres | Reprendre, dupliquer, versionner, créer variantes/gabarits, archiver | Perdre l'original après édition ou migration. |
| **Expert** | Diagnostique machine/modèles, versions, mémoire, logs | Activer fournisseurs, comparer modèles, gérer lots et budget VRAM, logs QA | Télécharger ou exécuter un service externe à l'insu de l'utilisateur. |

### Ergonomie concrète

1. **Flux compact** dans Express : **Importer → Vérifier → Exporter** ; quatrième étape « Corriger » affichée uniquement si nécessaire.
2. **Langage métier** : « Bordure blanche 2 mm » et « Découper le contour extérieur » plutôt que noms internes OpenCV ou masques.
3. **Mesures univoques** : dimensions *illustration seule*, *bordure comprise* et *dimensions de la planche* visuellement distinctes.
4. **Actions sans perte** : sauvegarde automatique locale avant traitement risqué, undo/redo, aperçu de résultat, annulation de l'opération sans perdre les précédentes.
5. **Messages exploitables** : problème → conséquence → correction accessible ; exemple « Bord rectangulaire détecté : choisis Carte ou lance un détourage ».
6. **Aide intégrée à la tâche** : chaque sortie a un bouton « Comment importer dans Design Space » et la liste des contrôles encore nécessaires.
7. **Progrès clair** : analyse, masque, vectorisation, rendu, export ; *aucun progrès simulé* pour une étape bloquée.
8. **Accessibilité** : contraste, textes FR, raccourcis, navigation clavier, cibles suffisamment grandes, zoom et tailles ajustables.

### 15.1 — Principes UX obligatoires, y compris les cas négatifs

1. **Une tâche = un but observable**, non une page de réglages. Une action « Créer 12 stickers » charge une planche et propose 12 sujets indépendants ; l’utilisateur confirme la sélection avant tout export.
2. **Montrer le résultat avant la technique.** Les contrôles avancés ne disparaissent pas : ils sont disponibles via « Ajuster » ou l’espace Expert, avec valeurs explicites et effet prévisualisé.
3. **Pas de bouton magique opaque.** Si l’IA choisit un masque ou un profil, afficher méthode, incertitude éventuelle, alternative manuelle et bouton annuler.
4. **Une seule source de vérité des dimensions.** Choisir clairement : taille de l’illustration, taille finale bordure incluse, planche utile et page ; tous les autres panneaux reflètent la même valeur du projet.
5. **À tout moment :** voir ce qui a changé, ce qui sera exporté, où se trouve le résultat, ce qui reste à valider et ce qui peut être annulé.
6. **Les erreurs servent à avancer :** « Pourquoi bloqué ? » → surlignage de la zone → action prudente « Corriger/Changer d’usage/Ignorer le sujet » ; pas de suppression silencieuse des trous, détails ou textes.
7. **Réactivité perçue :** lancement immédiat d’un état en cours réel ; traitement lourd asynchrone au sein du logiciel, annulation avec état vérifiable, aucune promesse de calcul instantané.
8. **Respect de la décision utilisateur :** préréglages suggérés et mémorisés avec consentement visible ; l’utilisation précédente ne déplace pas automatiquement les sujets d’un projet différent.

### 15.2 — Grille de navigation et structure d’écran cible

**Desktop prioritaire, Windows + interface ComfyUI intégrée dans un navigateur.** Les six espaces partagent une barre supérieure (projet, sauvegarde, annuler/refaire, aide), une zone centrale prévisualisation/toile, un contexte à droite, un panneau d’import/bibliothèque repliable et un pied d’écran pour états/erreurs/export. La vue Express réduit ces panneaux au strict minimum.

```text
┌ Projet / statut ● / Annuler / Refaire / Recherche / Aide ─────┐
│  Express  Atelier  Fabrique  Vectoriel  Bibliothèque  Expert   │
├──── Panneau source ───┬───────── TOILE ─────────┬── Réglages ─┤
│ sujets / calques      │  avant / après / coupe   │ taille mm  │
│ masques / variantes   │  sélectionner / zoomer   │ bordure   │
│ (repliable)           │  guides, erreurs         │ matière   │
├───────────────────────┴──────────────────────────┴────────────┤
│ État réel / diagnostic court   [Vérifier]     [Exporter…]      │
└───────────────────────────────────────────────────────────────┘
```

*Schéma fonctionnel, non maquette pixel-perfect ni preuve de faisabilité du frontend.* À 1366×768, priorité à la toile et aux actions ; les panneaux secondaires passent en onglet/repli, sans défilement horizontal pour le parcours Express. À 1920×1080, deux panneaux peuvent rester ouverts. Taille de police et échelle système respectées ; aucune commande décisive sous une zone masquée.

### 15.3 — Comportements uniformes de l'interface

| Interaction | Comportement attendu | Limite/sécurité |
|---|---|---|
| Cliquer un sujet / une vignette | Sélection sur la toile et dans la liste simultanément | Ne sélectionne pas des éléments hors image ni un objet masqué sans indication |
| Ctrl/Shift sélection | Multi-sélection explicite et nombre indiqué | Action en masse soumise à aperçu/confirmation lorsque destructive |
| Glisser sujet/poignée | Déplacement ou redimensionnement avec coordonnées et mm visibles | Alternative par saisie + flèches ; proportions verrouillables |
| Molette / zoom +/- | Zoom centré sur pointeur si possible, « Ajuster » toujours disponible | Ne change jamais les dimensions physiques exportées |
| Pinceau | Surface d’effet visible, modes Ajouter/Retirer, taille stable et zoom cohérent | Altération sauvegardée comme révision ; pas de surpeinture irréversible |
| Avant/après | Bascule et comparaison divisée, alignement 1:1 | Données affichées identifiées original/masque/PNG/SVG |
| Erreur localisée | Clic sur erreur recentre et surligne la région problématique | Ne « corrige » jamais sans action explicite |
| Annuler/Refaire | Historique d’actions cohérent à travers les espaces | Export passé non effacé ; distinction annuler modification/annuler job |
| Export | Liste des artefacts possibles, validité et choix de dossier | Désactive ou prévient le fichier invalide ; raison affichée |
| Quitter / relancer | Proposer dernier projet et récupération si état interrompu | Aucune fermeture silencieuse avec modifications non écrites |

### 15.4 — États d’écran normés

Chaque composant de tâche doit gérer **vide, source chargée, analyse en cours, résultat prêt à vérifier, corrections en cours, export en cours, succès, succès partiel, annulation, erreur récupérable, erreur bloquante**. Les fichiers en cours ne sont jamais confondus avec des fichiers terminés. Les boutons désactivés ont une raison accessible ; les jauges sont déterminées par étapes réelles, pas par pourcentage arbitraire. Les erreurs préservent la source et toutes les révisions validées.

### 15.5 — Profil de démarrage sans courbe d’apprentissage

- Premier lancement : « Nouveau sticker », « Découper une silhouette », « Séparer une planche », « Ouvrir un projet » et « Reprendre ». Pas de tutoriel obligatoire ni création de compte.
- Mode Expert **replié mais découvrable** ; aucun réglage nécessaire pour réussir la voie déterministe.
- Préférences locales : thème clair/sombre/auto, taille d’interface, dernier dossier, valeurs récentes *avec contrôle*, sauvegardes, raccourcis ; export/import des préférences ultérieurement.
- Aide « Pourquoi cette alerte ? », micro-tutoriels liés au contexte, checklist avant Design Space ; jargon technique uniquement sur demande.

### État de travail commun

- Un projet possède `project_id`, `schema_version`, date, source originale hashée, objets et transformations, masque versionné, palette, textes, document, paramètres de fabrication, artefacts et preuves.
- Une opération génère une révision ; aucune nouvelle action destructive ne supprime automatiquement l'original ni l'export précédent.
- Les unités sont **mm** dans le modèle de fabrication ; les points/pixels ne sont que représentations de calcul explicitement converties.
- Chaque « sujet » conserve son `subject_id` et ses accessoires même après réordonner, redimensionner, exporter ou recharger.
- Les versions à migrer sont validées sur les corpus antérieurs ; en cas d'échec, ouverture en lecture seule avec message et export des contenus originaux.

## 16. Les cinq sorties : contrat UX, technique et preuve

| Produit | Contenu réel exigé | Validation automatisable | Preuve externe restant requise |
|---|---|---|---|
| **Sticker PNG Print Then Cut** | Couleurs raster fidèles, alpha sujet, bordure et dimensions correctes, aucune superposition SVG nécessaire | Dimensions/alpha, trous/contours, marges, absence de faux masque, rendu comparatif | Import en **Flat Graphic**, opération Print Then Cut, lecture repères et coupe sur la vraie Explore 5 |
| **SVG silhouette / Basic Cut** | Tracés géométriques simples, fermés, unités réelles ; nombre de chemins sans doublons | Validation XML sûre, chemins et intersections, détails matériel, comparaison du masque | Import Cricut en coupe de base puis test sur matière cible |
| **SVG fabrication multi-couches** | Un groupe et une couleur/matière par pièce prévue ; ajours, sens, assemblage explicités | Groupe/calques, chevauchements, ordre, ponts, trous, micro-pièces | Découpe réelle et assemblage des calques ; étiquetage expérimental avant cela |
| **SVG artistique éditable** | Formes, chemins, couleurs/groupes modifiables ; bitmap incorporé interdit pour la qualification « entièrement vectoriel » | Rendu SVG standard vs source, nombre de points/chemins, fidélité silhouette/couleur, présence d'images embarquées | Ouverture dans éditeur tiers, édition de vraies formes ; n'implique pas la découpabilité |
| **Projet `.smartsvg`** | Sources, paramètres, textes, calques, masques, variantes, versions et preuves | Save/load identique, migrations, contrôles d'intégrité et sécurité | Ouverture sur seconde installation / ancienne version selon matrice de compatibilité |

**Chaque artefact exporté doit être accompagné d'un état de validation lisible dans le manifeste/rapport compagnon (`manifest.json` et interface) ; ne pas imposer l'insertion de métadonnées propriétaires dans un PNG ou un SVG si cela nuit à leur compatibilité.** Ne jamais afficher « certifié Cricut » après un simple contrôle logiciel. Le nom de fichier et le dossier reflètent clairement l'opération. Une sortie multi-couches n'est ni une instruction d'impression ni une garantie de coupe de tous les détails internes.

### Registre de preuves

**Événements possibles, non hiérarchie universelle :** `CREATED`, `LOCAL_QA_PASSED`, `RENDER_REVIEWED`, `DESIGN_SPACE_IMPORTED`, `MATERIAL_CUT_TESTED`, `PROJECT_ROUNDTRIP_PASSED`. Stocker chaque événement avec son protocole, son contexte, ses réserves et ses preuves indépendamment, y compris les échecs.

Ces états sont *des jalons de preuve, pas une chaîne qui s'applique à tous les formats*. Un SVG artistique peut être éditable sans `MATERIAL_CUT_TESTED`, et un PNG peut être découpé sans aucun vecteur éditable. Conserver pour chaque preuve : date, versions, machine, source, format, matériau, photo/capture s'il y a lieu, résultat et réserves.

## 17. Routage intelligent : la méthode avant l'IA

| Situation analysée | Première approche | Escalade possible | Défaillance acceptable |
|---|---|---|---|
| PNG RGBA avec alpha utile validé | Alpha natif sans IA | Retouche utilisateur | Alerte sur bord/halo, pas d'invention de sujet |
| Illustration isolée sur fond uniforme | Heuristique déterministe | IA locale si zones ambiguës | Demande de confirmation si deux sujets se touchent |
| Planche multi-sujets régulière | Détection de cases, composantes, tri par identité stable | SAM2 points/boîtes si collision | Refus d'une division non sûre, pas de stickers fusionnés silencieux |
| Capture d'écran/texte/cadre | Recadrer avec consentement puis segmenter | Correction assistée | Préserver le texte de la source ; choix « affiche entière » possible |
| Photo sur fond chargé | Segmentation locale réelle si modèle disponible | Intervention manuelle | Ne pas sortir un contour rectangulaire prétendu détourage |
| Art linework noir/blanc simple | Extraction de lignes/couches ou trace Bézier | Retouche vectorielle | Reconnaissance que l'image imprimable est parfois préférable |
| Illustration complexe / 24 sujets | Sélection explicite et diagnostic par objet | IA interactive, inspection lot | Résultats partiels numérotés + erreurs tracées, sans faux succès 24/24 |

**IA locale :** diagnostic des modèles installés, licence/source/poids, VRAM maximale observée, test unitaire de bout en bout, sortie masques reproductibles. L'IA n'est pas « implémentée » au sens produit tant que les modèles visés n'ont pas été réellement exécutés sur le PC cible.

### Gestion des résultats ambigus

- Masque absent, uniforme, presque rectangulaire, inversion alpha, trop d'îlots, trous inattendus, accessoire détaché : état *à revoir* et non *prêt à fabriquer*.
- Retourner plusieurs **propositions classées** si deux objets plausibles existent, et permettre « conserver l'image entière » plutôt que forcer un détourage.
- Un mode *qualité visuelle* peut préserver des micro-détails qui seront refusés en *fabrication découpable* ; afficher le compromis à **taille physique réelle**.

## 18. Mise à jour spécifique Cricut Explore 5 / Design Space (24 octobre 2026)

1. L'aide officielle de **Cricut Explore 5** confirme le flux **Flat Graphic → Print Then Cut** et l'obligation d'**Aplatir** les compositions multicouches destinées à une seule impression/découpe.
2. En format **A4**, l'aide Cricut décrit la pose de la feuille **avec le côté long à l'horizontale sur le tapis** pour ce modèle. Un assistant de recette doit rappeler la pose du tapis et la flèche des marques d'enregistrement : ne pas présumer une orientation identique à Letter.
3. La **surface utile Print Then Cut** varie selon machine, format, proportion et repères. Ne jamais forcer un unique rectangle A4 « garanti » ; le gabarit SmartSVG est indicatif, Design Space fait foi pour sa version installée.
4. SVG : **limite d'import publiée 5 000 chemins** ; cette limite n'est pas une cible raisonnable de fabrication. Préférer quelques pièces cohérentes plutôt que des milliers de micro-formes.
5. Le profil SVG Cricut doit éviter les **clipping paths**, dégradés/patterns/images non adaptés à l'import en calques. Les convertir en géométrie simple quand c'est justifié, sinon utiliser un PNG imprimable et le signaler.
6. **Design Space Desktop v10.8 (production le 19 octobre 2026)** apporte un nouveau panneau d'import et corrige un problème d'alignement de l'écran de calibration A4. **La v10.9 du 21 octobre 2026 est une bêta**, à exclure du socle de certification tant que sa version réellement installée n'est pas connue ; l'UI peut changer.
7. Les impressions Print Then Cut doivent rester dans la **même session Design Space** ; pas de contournement par une planche PDF avec repères bricolés.
8. L'app doit proposer un **coupon de vérification** (taille, contour blanc, petites courbes, intérieur évidé), mais **aucune valeur de pression/passes/outil** n'est garantie sans calibration avec le matériau exact.  
9. **Imprimer en portrait** dans le dialogue de l'imprimante, sans mise à l'échelle ; ceci n'annule **pas** la consigne distincte d'**orientation A4 horizontale sur le tapis** pour Explore 5. Conserver la flèche de repérage en haut à gauche selon le flux Design Space.  
10. **Matières brillantes/holographiques :** ne pas dire « toutes interdites » ; Cricut documente certaines matières compatibles de sa marque, tandis que d'autres supports brillants ou sombres peuvent perturber le capteur. Recette expérimentale par matière avec statut spécifique.

**Sources officielles** :
- Cricut Explore 5 Print Then Cut : https://help.cricut.com/hc/fr/articles/38613592650903-Comment-imprimer-puis-d%C3%A9couper-avec-la-Cricut-Explore-5
- Import SVG/PNG et plafond des chemins : https://help.cricut.com/hc/en-us/articles/360009556313-How-to-upload-images-into-Design-Space
- Limitations SVG : https://help.cricut.com/hc/fr/articles/360009553213-T%C3%A9l%C3%A9chargements-d-images-%C3%A9l%C3%A9ments-non-pris-en-charge
- Surface Print Then Cut : https://help.cricut.com/hc/fr/articles/360009429814-Quelle-taille-puis-je-imprimer-puis-d%C3%A9couper-nbsp
- Notes Design Space : https://help.cricut.com/hc/en-us/articles/27054006457111-Design-Space-Release-Notes
- Calibrage Explore 5 : https://help.cricut.com/hc/fr/articles/360009424974-Calibrage-de-votre-machine-pour-l-impression-puis-la-d%C3%A9coupe

## 19. User stories réellement testables

| Réf. | En tant qu'utilisateur je veux... | Résultat attendu | Gate |
|---|---|---|---|
| US-01 | Déposer un escargot transparent et créer un sticker de 40 mm | PNG conservant la couleur, contour correct, dimensions mesurées, export clair | G2/G4 |
| US-02 | Importer 12 escargots d'une planche | 12 identités, 12 exports individuels et une planche sans fusion | G2/G4 |
| US-03 | Importer 24 personnages sur fond noir | Reconnaissance complète ou correction assistée par élément, échecs visibles | G3/G5 |
| US-04 | Détourer une personne tenant un accessoire | Sujet et accessoire conservés, contrôle avant validation | G3 |
| US-05 | Retirer une erreur au pinceau et enregistrer | Masque et histoire retrouvés après fermeture | G1/G2 |
| US-06 | Créer une étiquette prénom depuis l'Atelier | Texte net, police contrôlée, découpe et composition cohérentes | G6 |
| US-07 | Fabriquer un logo papier 3 couleurs | Une pièce cohérente par couleur, prévisualisation d'assemblage | G5/G9 |
| US-08 | Produire 30 stickers nominatifs à partir d'un CSV | Aucun prénom oublié, accents justes, planche sans collision | G7 |
| US-09 | Reprendre un lot de 50 visuels après arrêt | Reprise sans écraser, reproduire ni perdre les exports terminés | G7 |
| US-10 | Créer un décor papier multicouche | Ordre des plans, trous d'assemblage et tolérances vérifiés physiquement | G9 |
| US-11 | Retrouver une version d'un projet | Original et ancien export conservés, retraitement reproductible | G1/G7 |
| US-12 | Savoir si mon SVG est éditable, découpable ou simplement imprimable | Trois statuts indépendants et une proposition d'action concrète | Tous |

## 20. Priorités de construction et dépendances — sans sauter de jalons

### Release train A — Fiabilité avant élégance (G0 + G1)

**Objectif** : restaurer la confiance dans toutes les sorties. Terminer vérité terrain, inventaire des nœuds et contrats avant d'introduire un autre moteur de vectorisation. Livrables minimaux : corpus, matrice de workflows, `subject_id`, projet minimal et tests de non-régression.

### Release train B — Première expérience fluide (G2 + diagnostic G3)

**Objectif** : remplacer l'entrée « graphes de nœuds » par un parcours Express lisible. Les GPU/IA sont facultatifs pour réussir le test de sticker alpha existant ; rendre visibles les cas qui demandent la correction.

### Release train C — Fabrication réellement validée (G3 + G4)

**Objectif** : calibrer Explore 5, isoler les responsabilités de Design Space, photographier et mesurer les coupons. **MVP** après validation des deux procédés sticker imprimé et SVG de silhouette. Un utilisateur peut déjà produire sans SVG artistique parfait.

### Release train D — Différenciation forte (G5 + G6 + G7)

**Objectif** : qualité vectorielle visible et mesurable ; création de textes/formes/calques ; lots et variantes. Prioriser les quatre actions qui évitent les retours dans Canva : *détourer, composer, vectoriser simplement, préparer une planche*.

### Release train E — Produit stable puis extensions (G8 + G9)

**Objectif** : stabilité V22.0, coût raisonnable, support et documentation ; réserver dioramas et projets mixtes à une extension si aucun usage central n'en dépend.

**Dépendances critiques** : `G0→G1.1→G1.2→G1.3→G2` ; `G1/G2→G3.1` ; `G2+G3.1+G4→MVP` (sans imposer G3.2–G3.5) ; `G1.3+G2→G6`; `G4+SVG QA→G5` ; `G1.3+G4→G7` ; `MVP+socle V22+G8→V22.0`. Les sous-lots G3.2–G3.5/G5/G6/G7 sont admissibles selon leurs dépendances réelles, **non comme prérequis globaux et simultanés**. Aucun prototype isolé n'est déclaré intégré.

## 21. Matrice de valeur — quelles fonctions justifient le développement ?

| Fonction candidate | Valeur pour le travail Cricut | Complexité/risque | Stratégie |
|---|---|---|---|
| Extraction propre d'un sujet et de ses accessoires | Très élevée | Élevée selon les images | **P0**, routage prudent + correction rapide |
| Contrôle taille mm/bordure et export correct | Très élevée | Moyenne | **P0**, immédiat |
| 12/24 stickers sur planche | Très élevée | Moyenne/élevée | **P0**, preuves par sujet |
| Projet `.smartsvg` sauvegardable | Très élevée | Élevée | **P0**, avant nouvel éditeur |
| Aperçu réel du chemin de lame | Très élevée | Moyenne | **P0**, affichage honnête |
| SVG d'édition couleur fidèle | Élevée | Très élevée | P1, cas compatibles et métriques distinctes |
| Atelier texte + formes + calques | Élevée | Moyenne/élevée | P1, fonctionnant dès le premier socle |
| Lots et prénoms CSV | Élevée en production répétée | Moyenne | P1, après projet/texte fiables |
| Bibliothèque/gabarits | Moyenne à élevée | Moyenne | P1 après sauvegarde fiable |
| Harmonisation de palette, masques créatifs | Moyenne | Élevée | P2, quand rendu SVG stable |
| Reconstitution sémantique universelle d'une illustration | Incertaine | Très élevée | **Recherche**, jamais promesse générale |
| Dioramas, cadres lumineux, pop-up | Élevée pour quelques projets, moins fréquente | Élevée / matériel | P2, prototype réel en V22.x |
| Génération libre type Canva / effets décoratifs massifs | Complémentaire mais coûteuse | Très élevée | P3, ne doit pas retarder V22.0 |
| Application Windows autonome | Potentiellement élevée pour l'UX | Très élevée | Étude seulement après moteur stable |

**Principe** : favoriser une dizaine d'outils utilisés tous les jours plutôt que cinquante fonctions difficiles à tester et à maintenir.

## 22. Politique d'architecture et développement long terme

### Interopérabilité

- Conserver les anciens IDs ComfyUI et produire une table de compatibilité ; déprécier avec avertissement, pas supprimer avant migration prouvée.
- Backend découplé de l'UI et de ComfyUI : traitement d'image, masque, vectorisation, fabrication, export, QA appelables en tests sans navigateur.
- `Project` n'enregistre pas des chemins absolus fragiles comme seule référence ; assets portable + hash et schéma migrable.
- Adapter le format à l'usage, pas l'usage à un « super SVG » magique ; exporter séparément raster imprimable, vecteurs artistiques et courbes de coupe.
- Proposer un mode « confidentiel / tout local » explicite. Toute future génération distante doit être opt-in et clairement annoncée.

### Fiabilité

- Pipeline déterministe quand les composants le permettent : `source_sha + paramètres + moteur/version + ressources IA` → clé de cache.
- Conservation des rapports de qualité et des raisons du fallback.
- Rendu de vérité par moteur SVG standard indépendant du générateur, mesure IoU silhouette + erreur couleur **sur protocole figé**.
- Tests structurels XML/SVG sécurisés, charge mémoire bornée, SVG malveillants/incomplets refusés et chemins d'archives contrôlés.
- Les tests de qualité ne devraient **pas** additionner des sous-chemins et des segments comme s'il s'agissait de chemins indépendants ; publier les trois mesures.
- Profils de matériau versionnés (épaisseur réelle, bande de coupe, matière, fournisseur, date, lame/tapis, état calibré/non calibré).

### Distribution

- Un paquet Windows/ComfyUI reproductible : archive, manifeste, vérificateur, guide court, exemples minimaux, procédure de désinstallation/retour à la version N-1.
- Contrôle de licence des dépendances/modèles/polices avant diffusion ; pas d'œuvres protégées tierces dans les packs publics sans autorisation.
- Versionnage sémantique des **formats de projet** indépendamment du numéro de build application.

## 23. Risques produit — registre vivant

| Risque | Niveau | Signal d'alerte | Réponse |
|---|---|---|---|
| Masque rectangulaire ou inversion alpha présentés comme sujet | P0 | Bounding box ~image complète, incohérence MASK | Bloquer export sticker auto, choisir carte ou correction |
| SVG visuellement bon mais « milliers de coups de lame » | P0 | Micro-chemins/segments/anneaux nombreux | Voir chemin de lame, profil Art ≠ profil Cut, fusion |
| Mauvaise taille en mm | P0 | Écart entre visuel, feuille, Design Space | Mesures physiques, unités testées, coupon |
| Confusion PNG + SVG superposés | P0 | Plusieurs découpes internes inattendues | Export PNG seul pour Print Then Cut, instructions claires |
| Action masquée ou « Exporter » prématurément actif | P0 | utilisateur clique sans comprendre la vérification | Action unique contextualisée, blocage explicite et contrôle avant export |
| Mauvais état d’interface après erreur GPU / redémarrage | P0 | données visuelles divergentes / corrections perdues | réouverture du dernier snapshot, réconciliation des artefacts, diagnostic contextualisé |
| Interface illisible, dépendante du glisser-déposer | P1 | tests clavier ou petite fenêtre impossibles | alternative au drag, focus, cible d’action, adaptation 1366×768 |
| IA indisponible/OOM | P1 | Erreur mémoire/poids incompatibles | Repli heuristique/manuelle, cache, jamais annoncer succès |
| Régressions dues aux workflows historiques (186 annoncés) | P0 | ID disparu, contrat port cassé | Inventaire G1.1, tests de chargement, migrations |
| Fichier `.smartsvg` corrompu ou ressource perdue | P0 | Différence après réouverture | Écriture atomique, hashes, rollback, fixtures |
| Fausse promesse de fonctionnalités type Canva | P1 | Cases non supportés annoncés OK | Démo comparative de tâches réellement testées |
| Matière incompatible/capteur Print Then Cut perturbé | P1 | Échec de lecture, sur-découpe | Calibrage Explore 5, recette par matière, réserve |
| Explosion de scope/retard V22.0 | P1 | Lots ouverts sans gate / dépendances floues | WIP 1+1 et report d'extensions |
| Licences de modèles/polices/images non adaptées à diffusion | P1 | Origine ou droit absent | Inventaire licences, assets tests internes seulement |

## 24. Plan des premiers micro-lots à exécuter à l'ouverture

**Important : tous les lots ci-dessous sont planifiés, pas exécutés.** Le gel n'est pas levé par le présent document.

| Ordre | ID | Travail strictement circonscrit | Sortie vérifiable |
|---|---|---|---|
| 1 | **G0.2** | Inventorier les neuf tests T et deux cas R, types et tailles, sources sans altération | `corpus_manifest.json`, droits et objectifs par image |
| 2 | **G0.3** | Dessiner et valider les masques cibles, définir critères par cas | Vérité terrain avec plusieurs profils et traitement des ambiguïtés |
| 3 | **G0.4** | Enregistrer risques réels, versions locales et limites connues | Carte risques/testabilité + statut de preuve initial |
| 4 | **G1.1** | Analyser tous les nœuds et **186 workflows annoncés**, vérifier le décompte sur B0 | `node_inventory.csv`, `workflow_inventory.csv`, `compatibility_map.md` |
| 5 | **G1.2** | Formaliser 5 types stables + les règles alpha, unités et identités | Contrats testés sur fixtures source/MASK/Subject/Artifact/QAResult |
| 6 | **G1.3** | Projet minimal `.smartsvg` avec retouches/restauration | Save/load exact, crash simulé, migration de fixture |
| 7 | **G1.4–G1.5** | Installation/rollback + point d'entrée Express compatible | Un seul workflow conseillé pour 3 cas, ancien flux inchangé |
| 8 | **G2.1** | Coquille visuelle en trois étapes | Test d'un sticker alpha complet sans graphe |
| 9 | **G2.2–G2.4** | Choix des sujets, correction, statuts d'exports | Trois sorties clairement distinguées, logs et sauvegarde |
| 10 | **G3.1** | Diagnostic IA sur machine RTX 3070 réelle | Journal reproductible modèles/versions/VRAM sans inférence prétendue |

### Checkpoint avant le premier changement de code

- [ ] La baseline B0 est présente et son empreinte vérifiée indépendamment.
- [ ] Les résultats de fabrication PNG/SVG existants sont mis de côté comme témoins de non-régression.
- [ ] Les limites de l'environnement sont consignées ; tests simulés et réels sont étiquetés.
- [ ] Le lot à modifier contient une phrase d'objectif, un périmètre, un test négatif et une condition d'arrêt.
- [ ] Le rollback est documenté et possible sans toucher à B0.

## 25. Recette de livraison et format de compte rendu

Chaque version devra publier simultanément :

1. **ZIP intégral de l'extension** et SHA-256 de l'archive (pas uniquement un patch partiel).
2. **Manifeste signé ou hashé**, inventaire des fichiers ajoutés/modifiés/supprimés et migration requise.
3. **Rapport de tests** ventilé Python/JS/UI/intégrité, plus résultats de cas visuels et limites externes.
4. **Comparaison avant/après** sur même image/paramètres et comptage chemins/sous-chemins/segments si SVG.
5. **Rapport d'UX** pour toute évolution d'écran, avec scénario utilisateur et éventuelles régressions d'accessibilité.
6. **Rapport Cricut physique** uniquement après test réel ; photo/screenshot, version Design Space, matière et dimensions.
7. **Notice d'installation** et possibilité de retour version N-1 sans écraser la référence B0.
8. **Décision GO / GO AVEC RÉSERVES / NO GO**, réserves traduites en tickets.

### Définition de « terminé »

- « Implémenté » ≠ « testé » ≠ « utilisable » ≠ « fiable » ≠ « vérifié sur machine ».
- Un lot est **terminé** si les cas positifs et négatifs prévus sont satisfaits, les résultats sont reproductibles, et les nouvelles limites sont visibles à l'utilisateur.
- Un cas particulièrement difficile peut rester non pris en charge ; la qualité du produit tient aussi à la précision du diagnostic et à l'absence de faux résultats.

## 26. Évolutivité de cette roadmap

Ce fichier est le **document maître v3.2 figé** ; les décisions v3.0/v3.1 demeurent documentées comme historique. À chaque réunion de pilotage du projet :

- ne **pas modifier ce fichier figé** pour changer les statuts ; actualiser le **tableau de pilotage séparé** seulement lorsque la preuve existe ; conserver le document gelé et l'historique ;
- maintenir un tableau séparé `id, priorité, état, dépendances, preuve, prochain pas` ;
- ajouter les idées aux familles F et aux extensions G9, sans ouvrir de chantier avant la stabilisation du lot actif ;
- conserver le journal des décisions modifiées et leur justification ;
- vérifier régulièrement l'aide Design Space au moment des tests réels, puisque son comportement et son interface évoluent ;
- ne fixer de délais ou de coût qu'après inventaire, tests de performance et définition de charge vérifiables.

### Décision directrice de l'historique v3.0

**Ordre impératif :** préserver → rendre compréhensible → rendre fabriquable → rendre modifiable → rendre productif → enrichir. Le succès de SmartSVG ne se mesure pas au nombre de modèles IA ou d'options ; il se mesure à la capacité de fabriquer une création voulue **sans la perdre, sans découpe imprévue et sans opérations manuelles inutiles**.


---

# PARTIE III — CONTRATS D’INGÉNIERIE HÉRITÉS DE v3.1 (CONSERVÉS)

*Les sections 27–35 sont conservées pour la traçabilité de v3.1 ; la v3.2 les précise sans les supprimer. Pour l’UX/UI, les contrats plus détaillés des §§15 et 36–41 priment en cas de divergence non critique. Aucun constat ne représente un test de code, d’IA GPU ou de coupe physique réalisé dans cet audit documentaire.*

## 27. Audit de cohérence : constats, décisions, résiduel

| Code | Problème de la v3.0 | Action imposée v3.1 | Gravité initiale | Résiduel |
|---|---|---|---|---|
| A01 | G3 IA complète placée avant G4, retardant le MVP même pour PNG transparents | G3.1 diagnostic obligatoire ; autres capacités IA activables indépendamment avec fallback | P0 produit | IA complexes non éprouvées |
| A02 | Périmètre V22 et G5–G7 assimilés à une obligation globale | Contrat MVP/V22/V23 précis au §28 ; fonctions hors gate labellisées bêta/reportées | P0 planning | Arbitrage de fonctionnalités en fin de cycle |
| A03 | « Chaque fichier embarque son statut » potentiellement nuisible à PNG/SVG | Manifeste et rapport compagnon ; format standard non altéré | P1 interop | Métadonnées facultatives à éprouver |
| A04 | Statuts de preuve décrits comme séquence unique | Matrice orthogonale datée, incluant les échecs | P0 vérité | Essais réels non exécutés |
| A05 | `.smartsvg` cité mais non spécifié | Contrat de conteneur v1 + sécurité + migration §29 | P0 données | Implémentation à faire |
| A06 | SVG géométrique manquait le détail sur trous et transforms | Pipeline de géométrie vérifiable §30 | P0 coupe | Calibration matérielle absente |
| A07 | Métriques non normées et seuils universels risqués | Protocoles reproductibles et seuils par famille §31 | P1 QA | Jeu de vérité terrain à produire |
| A08 | Nuance impression portrait / pose A4 paysage manquante | Deux étapes distinctes et orientation contrôlée | P0 mode d'emploi | Test utilisateur réel à faire |
| A09 | Nouveautés Design Space après 10.8 incomplètes | v10.9 (bêta 21/10/2026) dans la veille, pas dans la matrice stable | P1 externe | Évolution future Design Space |
| A10 | Tickets S-001–S-022 cités sans leur définition en V3.0 | Définitions retrouvées dans la v1 et reproduites au §33.1 | P1 traçabilité | Vérifier leur correspondance avec les modules/lot B0 |
| A11 | « 186 workflows » traité trop facilement comme un chiffre exact | Compter les JSON/workflows dans B0 et documenter les doublons / usages | P1 inventaire | ZIP B0 non audité ici |
| A12 | Configuration ComfyUI/JS locale non contractualisée | Matrice version moteur/frontend/nœuds/modèles §32 | P1 installation | PC cible non testé |
| A13 | Pas de frontière précise cache/écriture/annulation | Atomicité, journaux, reprise idempotente §29/§32 | P0 robustesse | Crash tests à venir |
| A14 | Couleurs/segments sur SVG confondus avec nombre de trajets physiques | Compter groupes/chemins/sous-chemins/segments et opérations prévues | P1 performance | Essai de coupe requis |
| A15 | Corpus orienté majoritairement illustrations connues | Fixtures hostiles, transparentes, dimensions et polices §31 | P1 couverture | Droits tiers à vérifier |
| A16 | Risques de dérive « tout faire comme Canva » | Budget de complexité et critères de report §28/§34 | P1 stratégie | Décisions à maintenir |

**Verdict documentaire :** les anomalies de spécification bloquantes sont traitées par règle explicite ; les risques de **mise en œuvre** restent ouverts. Ne pas transformer « roadmap auditée » en « logiciel certifié ».

## 28. Contrat de périmètre en trois produits successifs

| Palier | Obligatoire pour annoncer la livraison | Non obligatoire à ce palier | Preuve |
|---|---|---|---|
| **MVP Cricut local** | Import PNG/JPG, alpha fiable, fond simple, correction manuelle, export PNG Print Then Cut et SVG contour, unités réelles, planche 12/24 avec contrôle individuel, Express sans graphe, sauvegarde minimale, installation reproductible, tests Explore 5 ciblés | IA photo universelle, SVG artistique haute fidélité, bibliothèque avancée, CSV, app indépendante | Trois parcours utilisateurs + coupons physiques documentés |
| **V22.0 stable** | MVP stable, correctifs et sécurité, `.smartsvg` versionné, journal de preuves, diagnostics IA et adaptation réelle sur cas déclarés (sinon indication d'indisponibilité), contrôle SVG distinct Art/Cut, aide FR, accessibilité de base, rapports et rollback | Photo vers SVG couleur parfait, diorama complet, 50 lots garantis, catalogues, OCR et effets Canva, app autonome | Gate G8, matrice environnement/compatibilité, zéro P0, aucun P1 bloquant |
| **V22.x/V23 atelier étendu** | Selon lot : éditeur avancé, textes/courbes, modèles, usine CSV/50, bibliothèque riche, SVG couleur complexe, projets multi-matériaux/dioramas | Aucun engagement universel ; chaque capacité est une livraison indépendante | Gate par scénario/matière et déploiement progressif |

**Règle anti-fonction-fantôme :** les modules/fonctions visibles dans une maquette ne sont pas réputés disponibles. Les états `désactivé`, `bêta`, `validé sur cas`, `indisponible` doivent être affichés avec motif. Pas de boutons sans action ni de menus présumant un moteur inexistant.

**Stratégie de réduction du délai sans réduire la fiabilité :** une chaîne alpha/manuale utilisable vaut mieux qu'un pipeline IA multimodèle déclaré partout mais instable. En cas de blocage durable de G3.2+, G4 continue uniquement si ses propres entrées sont validées et si les fonctions AI sont réellement désactivées.

**Composition avant V22 :** les lots G6.1/G6.3 peuvent intégrer la stable seulement s'ils franchissent leur gate sans retarder G8. Sinon, les étiquettes composées restent explicitement reportées ; le périmètre figé de V22 conserve d'abord la préparation et la fabrication.

## 29. Format projet `.smartsvg` v1 — contrat préalable à G1.3

Le format **proposé à implémenter** est une archive ZIP portable structurée (non exécutable), à contenu relatif, sans dépendance obligatoire à ComfyUI :

```text
mon_projet.smartsvg
├── manifest.json                # schema_version, project_id, app_version, checksums
├── document.json                # scènes, transformations, dimensions, objets et Z-order
├── operations.json              # historique non destructif, paramètres et révisions
├── subjects.json                # subject_id, liens parent/accessoires, repères
├── sources/                     # originaux immuables, hashés
├── masks/                       # alpha positif normalisé + polarité déclarée
├── vectors/                     # chemins/art/layers, avec classe d'usage explicite
├── assets/                      # ressources autorisées et polices référencées
└── proofs/                      # rapports de contrôle, jamais auto-certification
```

**Contrats obligatoires :** `schema_version` indépendant de la version produit ; `project_id` stable ; `source_id` = identité logique + hash ; `subject_id` non lié à l'ordre de détection ; `layer_id`, `revision_id`, `artifact_id` immuables ; dimensions et repères explicités ; taille physique en mm et pixel/ppi exposés comme conversions, sans supposer que « 300 dpi » résout une erreur de géométrie.

**Modifications/undo :** les opérations réversibles sont enregistrées avec versions, paramètres et dépendances ; checkpoints périodiques pour éviter un journal interminable. Retouches = masques/deltas versionnés ; ne pas recopier intégralement la source à chaque action. La sauvegarde est *write-temp → fsync si possible → checksum → remplacement atomique* dans les limites du système. Après interruption, un projet valide précédent reste récupérable. Ne jamais écraser silencieusement un export utilisateur.

**Sécurité d'ouverture :** limite stricte de taille totale décompressée, quantité d'entrées, ratio de compression, profondeur, dimensions pixels, nombres de vecteurs et JSON imbriqués ; rejet traversal `../`, liens symboliques, URL réseau et ressources exécutables. Aucun script SVG ou fichier XML non sûr ; verrouillage de toute résolution d'entité externe. L'archive inconnue se traite en lecture seule avec diagnostic, sans écriture par défaut.

**Migrations :** adaptateur `n → n+1` vérifié sur fixtures ; compatibilité montante documentée, **pas** obligation d'ouverture par une ancienne version. Lors d'une migration, conserver l'original et produire un rapport de modification. Un projet corrompu ne doit pas faire planter le catalogue ni contaminer les autres projets.

**Gate G1.3 :** création → 15 opérations avec 3 undo/redo → fermeture/crash simulé → réouverture exacte des positions, masques, textes et liens d'accessoires ; migration fixture ancienne et test archive hostile. Tests au moins Windows/ComfyUI simulé puis PC cible quand disponible.

## 30. Contrat de précision graphique, métrique et géométrique

### Trois espaces de coordonnées sans ambiguïté

1. **Source** : pixels, EXIF et profil de couleur ; origine et axes documentés.
2. **Document** : transform affine d'objet, rotation/échelle/translations, clipping graphique seulement pour profil Art ; objets et calques.
3. **Fabrication** : géométrie normalisée en **mm**, taille utile objet/bordure/page distinctes ; `viewBox` cohérent avec dimensions et transformations aplaties quand nécessaire.

Chaque passage source→document→coupe doit être testable à l'aller et au retour, y compris recadrage, rotation EXIF et redimensionnement. Un masque 64×64 sentinelle ou un alpha inverse ne doit jamais être traité comme une silhouette valide.

### Géométrie de coupe

**Pipeline obligatoire :** masque positif fiable → contour(s) orientés → gestion des trous et règle de remplissage (`evenodd` ou conversion explicite) → élimination/fusion d'îlots **sur décision contrôlée** → offset/bordure avec jonctions explicites → simplification avec erreur géométrique bornée → contrôle auto-intersections, doubles segments, ouvertures, chevauchements, micro-ponts et positions hors matériau → SVG profil Cut → *rendu indépendant* et vue « chemin de lame ».

**En fichier Cricut Cut :** limiter SVG à formes et courbes compatibles. Convertir texte en courbes si nécessaire ; éviter clipping, motifs de remplissage, bitmap, URL ou dégradé ; vérifier que les opérations sont des *coups de lame voulus*, pas des contours colorés accidentels. Mesurer séparément `paths`, `subpaths`, `segments`, `cuts_expected`, `islands`, `holes` et petits composants.

**Cahier de fabrication :** pour chaque matière/lame/tapis, distinguer contraintes *connues officiellement*, *mesurées sur cette machine* et *estimées non validées* ; aucune pression, profondeur, passe ou largeur d'îlot présentée comme universelle. `kiss cut`/`die cut` et matériau réfléchissant restent des profils séparés, à tester avec l'outil réel.

**Spécification raster** : Print Then Cut repose sur **une seule image raster éventuellement transparente**, dite aplatie en nombre de calques (non obligatoirement opaque). Le PNG conserve ses couleurs, ses transparences réellement utiles, le cadrage et la bonne taille ; **ne pas superposer de SVG contour** au même design dans Design Space. Une marge blanche est un effet de rendu distinct de la ligne de coupe ; les trous internes sont explicitement contrôlés.

## 31. Banc d'essai, mesures reproductibles et critères d'arrêt

### Dimensions de qualité indépendantes

| Axe | Mesure minimale | Protocole | Condition d'échec |
|---|---|---|---|
| Détourage | IoU, précision/rappel, nombre de sujets, accessoires, holes | Masque de référence annoté, sujet/objet déterminé à l'avance | Mauvais sujet « validé », alpha inversé, mauvais count non signalé |
| Bordure | Comparaison contour SVG/raster, distance max et percentile Hausdorff en mm | Rendu indépendant à dimension fixée ; métrique mm | Déviation hors tolérance du profil testé |
| Couleur | sRGB/alpha/gamma normalisés, MAE RGB et si pertinent ΔE00 avec profil fixe | même source, même taille et fond de composition documenté | Gain de forme mais régression couleur non déclarée |
| Vectoriel | nombre de régions, chemins/sous-chemins/segments, trous, IoU, fidélité couleur | renderer standard indépendant, répétitions à échantillons identiques | SVG bitmap nommé « totalement éditable » ou détails critiques perdus |
| Fabrication | collisions, densité détails, ponts/îlots, géométrie finale | profil matière et géométrie en mm | P0 de coupe non détecté ou hors-page |
| Impression | dimension imprimée et décalage réel mesuré, lumière/matière | coupon calibré, version Design Space, imprimante et pose | Décalage de coupe non consigné ou mal attribué |
| Projet | roundtrip exact sources/masques/transforms/texte | ouvrir/sauver/crasher/migrer sur installations | perte silencieuse ou mauvaise ressource |
| Performance | médiane et p95 par phase, RSS RAM, pic VRAM, taille cache, fréquence OOM | répétitions, GPU et versions capturés | crash sans fallback ou perte de travail |
| UX | taux de réussite de tâches, étapes, erreurs, besoin d'aide | utilisateur novice, interface FR, clavier | flux simple exige ComfyUI ou JSON |

Les cibles v2 (ex. IoU ≥ 0,98 sur illustrations plates compatibles, MAE couleur ≤12 sur sous-corpus, 12/12, 24/24) sont **hypothèses de performance**, non critères de réception globaux ni métriques universelles. Elles deviennent des seuils acceptés **uniquement après** G0.3 (annotation référence, seuil par famille, méthode/versions figées). L'examen humain des accessoires, des trous et de l'adéquation matérielle prime sur un score agrégé élevé.

**Fixtures négatives et métamorphiques à ajouter :** alpha zéro/opaque/inversé ; sentinelle MASK 64×64 ; JPEG CMYK/ICC/EXIF rotation et PNG avec profils ICC / alpha ; fond blanc troué ; planche incomplète avec sujets chevauchants ; texture type cheveux ; texte vectoriel sans police ; Unicode avec accents/ligatures ; SVG externe malveillant ; ZIP bomb/chemin traversal ; très grande image ; fichiers tronqués ; planche entièrement noire ; couleurs semi-transparentes ; variations d'échelle et rotations préservant l'identité.

**Critère d'arrêt automatique** : retour erreur compréhensible + récupération de l'original dès qu'un invariant P0 est violé. Il est interdit de « poursuivre avec un meilleur effort » en produisant un fichier étiqueté prêt à couper lorsque dimensions, masque ou géométrie sont incohérents.

## 32. Infrastructure et comportement en production (PC local)

- **Compatibilité :** relever versions Windows 11, Python, PyTorch/CUDA, pilote NVIDIA, ComfyUI, frontend/Nodes 2.0, extensions RMBG, SAM2, dépendances Python/JS et leurs contrats. Tester installation vierge et installation avec anciennes extensions en collision ; documenter matrice « supporté / non testé / incompatible ».
- **Adaptateurs IA :** même interface entrée (`SourceAsset`, masque initial facultatif, boxes/points), sortie (masque positif H×W, confiance diagnostique éventuelle, provider/version), limites RAM/VRAM, erreurs normalisées ; aucune requête externe ni téléchargement de poids sans information et consentement.
- **Cache :** clé SHA des pixels/paramètres/versions, collision impossible présumée seulement avec vérification d'intégrité ; nettoyage explicite et bornes disque. Ne jamais utiliser un masque d'une ancienne version sans compatibilité prouvée.
- **Jobs :** états `queued/running/needs_review/succeeded/failed/cancelled`, étape, source, artefacts et hashes ; commits atomiques par objet, annulation idempotente, reprise après redémarrage, aucun doublon silencieux ; un export validé reste récupérable si l'UI plante.
- **Performance :** aperçus légers, traitement original uniquement à l'étape utile, une inférence GPU lourde à la fois si nécessaire, cache/réutilisation du modèle mesurés, batch configurable, arrêt propre OOM et possibilité de basculer sur un mode manuel.
- **Sécurité :** parseurs sûrs, contrôle des chemins d'accès, pas de code arbitraire via SVG/JSON, logs sans données personnelles par défaut, suppression/export explicites, licence fournisseur et modèles consignés. Ne pas présenter une IA téléchargée comme « hors ligne » avant que les ressources locales soient réellement disponibles.
- **Packaging :** ZIP installable, versions figées, vérificateur d'intégrité, procédure de rollback **sans toucher B0**, compatibilité API et anciennes IDs conservées tant que migration non certifiée.

## 33. Registre des tâches complémentaires S-049 à S-066

| Ticket | Phase | Priorité | Livrable | Gate / critère |
|---|---|---|---|---|
| S-049 | G0.2 | P0 | `corpus_manifest` et droits d'usage des fixtures | original hashé, origine et statut de droit explicites |
| S-050 | G0.3 | P0 | Vérité terrain versionnée + protocole annotations | ambiguïtés documentées, silhouettes/accessoires cohérents |
| S-051 | G1.1 | P0 | Rapprochement historique S-001–S-022 et inventaire réel workflows | fiches source conservées ; contrats B0 réellement vérifiés |
| S-052 | G1.2 | P0 | Schéma `Subject/Source/Artifact` avec identité et coordonnées | rotations/crop/alpha testés |
| S-053 | G1.3 | P0 | Format `.smartsvg` v1, migration et recovery | crash/reopen/malveillance testés |
| S-054 | G2.4 | P0 | Preuves orthogonales et sidecar `manifest.json` | aucune fausse certification dans PNG/SVG |
| S-055 | G4.1 | P0 | Profil Explore 5 A4/Letter, imprimer portrait/poser A4 paysage | procédure suivie, captures et coupon |
| S-056 | G4.2 | P0 | QA geometry Cut en mm : holes, islands, segments, offset | coupe simulée signalée comme telle et coupon réel |
| S-057 | G4.3 | P0 | Registre matériel : machine, lame, tapis, matière, tests | valeurs étiquetées source/calibrée/hypothèse |
| S-058 | G3.1 | P1 | Matrice environnement local et fournisseur IA | pas de promesse non exécutée |
| S-059 | G2.1 | P1 | Audit accessibilité clavier/contraste/labels | scénario Express réalisable au clavier |
| S-060 | G5.1 | P1 | Score qualité séparé silhouette/couleur/géométrie | benchmark reproductible/échantillon fixé |
| S-061 | G1.4 | P0 | Tests fichiers hostiles et bombes XML/ZIP | aucune sortie hors projet ni épuisement incontrôlé |
| S-062 | G7.1 | P1 | File de jobs avec identité, cache et pause/reprise | 50 objets après interruption sans duplication |
| S-063 | G8.1 | P1 | Matrice de compatibilité ComfyUI/frontend/node API | installation ancienne/nouvelle testées |
| S-064 | G6 | P1 | Contrat typographie et licence des polices | rendu reproductible ou avertissement précis |
| S-065 | G8.3 | P1 | Comparaison contrôlée Design Space/Canva/SmartSVG | protocole temps/clics/qualité/correction commun |
| S-066 | G9 | P2 | Prototype diorama à quatre plans alignables | assemblage réel et tolérances reportées |

**Traçabilité stricte :** S-049–S-066 sont des précisions nouvelles, non des tickets déjà implémentés. Les définitions S-001–S-022 ci-dessous sont recopiées de la roadmap v1 retrouvée, non devinées ; leur **état d’implémentation** et leur correspondance à B0 restent non vérifiés.

### 33.1 Reprise exacte des 22 tickets de la roadmap v1 (état non vérifié)

| ID | Priorité v1 | Intitulé historique | Dépendances v1 | Critère historique |
|---|---|---|---|---|
| S-001 | P0 | Geler archive V21.14.1 et corpus | aucune | SHA + manifeste |
| S-002 | P0 | Spécifier les trois contrats de sortie | S-001 | exemples importables |
| S-003 | P0 | Définir modèle de projet/retouches sérialisables | S-001 | ouverture/reprise identique |
| S-004 | P0 | Réduire la complexité visible, conserver anciens IDs | S-003 | anciens workflows ouvrables |
| S-005 | P0 | Test réel RMBG/SAM2/BiRefNet RTX 3070 | S-001 | logs et masques réels |
| S-006 | P0 | Créer masques de référence des neuf images | S-001 | vérité terrain annotée |
| S-007 | P0 | Validation sémantique du sujet désiré | S-005,S-006 | rejet des faux sujets |
| S-008 | P0 | Éditeur pinceaux/undo/reload vérifié sur frontend | S-003,S-007 | aucun trait perdu |
| S-009 | P0 | Assurance qualité Cricut par format | S-002 | dimensions/trajets précontrôlés |
| S-010 | P0 | Couper physiquement des exemplaires Explore 5 | S-009 | photos et mesures |
| S-011 | P0 | Fidélité SVG multicouche et analyse des formes | S-006 | mesures render standard |
| S-012 | P0 | Chemins SVG utilisables avec matériau choisi | S-009,S-011 | découpes testées |
| S-013 | P1 | Écran Express unifié | S-002,S-004 | test utilisateur |
| S-014 | P1 | Segmentation objets et fragments associés | S-005,S-006 | suites multiobjets |
| S-015 | P1 | Nettoyage des halos / découpe et offset | S-008,S-009 | comparatifs zoom |
| S-016 | P1 | HD conditionnelle + diagnostic d'artefacts | S-006 | avant/après objectif |
| S-017 | P1 | Packaging « projet SmartSVG » | S-003 | relecture multi-version |
| S-018 | P1 | Queue/batch/cache avec reprise | S-017 | lot interrompu/repris |
| S-019 | P1 | Benchmark Canva/Design Space sur corpus identique | S-009,S-011,S-013 | rapport chronométré |
| S-020 | P2 | Papier découpé multicouche / dioramas | S-012 | prototype assemblé |
| S-021 | P2 | OCR et gestion du texte sur affiches | S-007,S-011 | texte préservé / averti |
| S-022 | P2 | App autonome hors ComfyUI, si justifiée | S-013,S-018 | décision architecture chiffrée |

**Décision de normalisation :** les priorités d'origine v1 servent à la traçabilité historique. Les dépendances et la priorité opérationnelle prévalentes sont celles des lots G0–G9 et de la matrice §28/§34. Un ticket v1 P0 lié au SVG artistique ou à l'IA avancée ne doit pas bloquer mécaniquement le **MVP** si une voie sûre et explicitement limitée fonctionne ; toute dérogation à sa priorité historique est consignée dans le pilotage.


### 33.2 Tickets produit/ergonomie v3.2 — intégrés au backlog canonique

*Les tickets ci-dessous sont **proposés et non exécutés**. Priorité : P0 pour la voie simple, sa sûreté et les données ; P1 pour une amélioration déterminante mais non bloquante ; P2 pour l’extension. Ils utilisent les contrats UX §15 et les user stories §37. Le WIP 1+1 demeure applicable.*

| ID | Lot principal | Priorité | Livrable utilisateur | Preuve d’acceptation |
|---|---|---|---|---|
| S-067 | G2.1 | P0 | Accueil 4 objectifs + Reprendre | Choix d’usage sans graphe ni terminologie IA |
| S-068 | G2.5 | P0 | Schéma unique d’écran responsive desktop | 1366×768 + 1920×1080, pas d’action cachée |
| S-069 | G2.5 | P0 | États vide/chargement/erreur/export | Aucun contrôle factice ; succès partiel signalé |
| S-070 | G2.2 | P0 | Sélection directe et croisée sujets↔vignettes | T-02 : 12 sujets identifiables, même ID |
| S-071 | G2.6 | P0 | Erreurs cliquables avec région et correction réversible | Masque rectangle : refus ou reprise explicite |
| S-072 | G2.7 | P0 | Flux Express souris + clavier | T-02/U-01 jusqu’à export sans drag obligatoire |
| S-073 | G2.8 | P0 | Aperçus original/masque/coupe séparés | Dimensions constantes, aucune inversion confondue |
| S-074 | G2.9 | P0 | Reprise dernier projet et contexte | fermeture + réouverture identiques, pas de retouche perdue |
| S-075 | G2.4 | P0 | Panneau de validation du format par usage | PNG Print Then Cut ≠ SVG Cut ≠ SVG Art |
| S-076 | G4.6 | P0 | Checklist d’export et transfert Design Space | fichier recommandé, version, mise en garde A4/Letter |
| S-077 | G2.7 | P1 | Alternative clavier aux gestes souris complexes | sélection/déplacement/redimensionnement possible |
| S-078 | G2.7 | P1 | Contrastes/focus/texte ajustable | audit WCAG applicable et test manuel |
| S-079 | G2.8 | P1 | Loupe locale et comparaison glissante | détecter halo / trait coupé dans fixture |
| S-080 | G2.3 | P1 | Pinceau correction tactile souris + aperçu effet | undo, zoom et sauvegarde sans incohérence |
| S-081 | G2.9 | P1 | Réglages récents et préréglages utilisateur | aucune application cachée sur nouveau projet |
| S-082 | G2.5 | P1 | Disposition de panneaux persistante | contexte Express/Atelier conservé, reset disponible |
| S-083 | G2.6 | P1 | Recherche d’action et aide contextuelle | utilisateur retrouve l’outil sans documentation externe |
| S-084 | G2.9 | P1 | Ouvrir dossier/export/rapport depuis la réussite | fichiers corrects et artefacts immuables |
| S-085 | G4.6 | P1 | Aperçu cutter-only et repères micro-détails | alertes pointent sur chemins précis |
| S-086 | G6.6 | P1 | Toiles avec poignées et dimensions mm | proportions, alignements, guides vérifiés |
| S-087 | G6.6 | P1 | Multi-sélection, groupement et menu contextuel | batch d’objets sans perte d’identité |
| S-088 | G6.7 | P1 | Trois gabarits de départ guidés | étiquette, carte, topper sauvegardés et repris |
| S-089 | G7.6 | P1 | Tableau de lot et reprise d’un échec isolé | 50 éléments, 1 échec, 49 conservés |
| S-090 | G7.4 | P1 | Comparer deux dispositions de planche | aucune collision ; placements verrouillés stables |
| S-091 | G7.2 | P1 | Bibliothèque avec miniatures et filtre métier | retrouver un projet en test utilisateur |
| S-092 | G6.3 | P1 | Choix de police avec aperçu et alertes glyphes | caractères FR et police absente contrôlés |
| S-093 | G8.6 | P0 | Protocole de test utilisateur novice/régulier | tests scénarisés et observations anonymisées |
| S-094 | G8.6 | P0 | Tests d’accessibilité + vérification Windows zoom | aucun blocage critique de la voie principale |
| S-095 | G8.6 | P0 | Tests de récupération pendant export/IA | zéro perte de source/correction validée |
| S-096 | G8.6 | P1 | Instrumentation locale UX et latence (opt-in export rapport) | p50/p90 et cas d’erreur disponibles localement |
| S-097 | G7 | P2 | Commandes « refaire sur sélection » | répétition sûre sur objets compatibles |
| S-098 | G7 | P2 | Liste de recettes/gabarits personnels | modèle portable et droits visibles |
| S-099 | G9 | P2 | Guide d’assemblage de diorama dans l’UI | prototype mesuré et assemblé |
| S-100 | G9 | P2 | Raccourcis personnalisables / commandes favorites | conflits clavier détectés et restaurables |
| S-101 | G9 | P2 | Comparaison de variantes avec scores séparés | rendu/coupe/coût non confondus |

**Priorité et dépendances :** les tickets UX visent des micro-lots, non 35 versions distinctes ; S-067–S-075 n’entrent en implémentation qu’après les contrats projet G1 ; S-076 et S-085 demandent les contrôles de fabrication G4 ; S-093–S-095 sont des tests transversaux activés dès la première UI mais leur gate final appartient à G8. Le tableau de pilotage doit référencer ces ID et distinguer « spécifié », « implémenté », « vérifié ». Aucun ticket ne représente une fonction déjà livrée.

## 34. Portes de décision et gestion des changements

### Définition de « DONE » par type de tâche

- **Analyse/documentation** : inventaire vérifiable, sources et incertitudes indiquées ; n'implique aucune réussite produit.
- **Unitaire/intégration** : tests passés sur version/environnement enregistrés et non-régression documentée.
- **Interface** : scénario complet, navigateur réel, tests souris + clavier ; aucun faux bouton.
- **IA** : modèle réellement exécuté et version/poids/VRAM/durée consignés ; résultat négatif évalué, non simulé.
- **Cricut** : export contrôlé + import Design Space identifié + coupon physique, matière/machine/paramètres et photo.
- **Release** : ZIP, SHA256, manifeste, documentation, historique des migrations, test install/rollback, P0=0 et P1 bloquant=0.

### Arbitrage automatique de scope

1. Un correctif P0 est prioritaire et peut suspendre le seul parcours concerné.
2. Les fonctions MVP n'absorbent aucune fonction P2 simplement « utile ».
3. Une fonctionnalité P1 entre dans V22 uniquement si elle a fini son gate et ne retarde pas la stabilité ; sinon elle est reportée avec libellé d'interface.
4. Tout ticket sort du gel de façon **ciblée** : demande, changement de statut pilotage, branche/copie B0 et tests ; ne pas modifier rétroactivement le master v3.1 figé.
5. Toute contradiction d'exigence découverte doit produire **un addendum** `ADR-YYYYMMDD-NNN` avec conséquence et tests à reprendre ; si l'impact est majeur, publier v3.2, sans effacer v3.1.
6. Arrêt et rollback avant perte de données, fausse sortie « prêt Cricut » ou régression critique.

### Première action autorisée à la reprise

**G0.2–G0.4 (préparation du corpus, lecture seule), puis G1.1 (inventaire sans refactoring).** Le seul résultat attendu au premier lot code est un catalogue machine-lisible des nœuds/workflows/dépendances et une liste d'IDs garantis, pas une nouvelle IA ni une nouvelle interface. Le comptage « 186 » doit être mesuré sur B0 et non confirmé par répétition.

## 35. Acte de gel documentaire et limites finales

**Objet du gel v3.1 historique :** décisions produit, périmètres MVP/V22/V23, catégories F01–F15, lots G0–G9, principes de sécurité, format des cinq sorties, exigences de preuves et ordre de reprise. Les 18 tickets v3.1 sont du *backlog*, pas du travail accompli. **La présente v3.2 ajoute une intégration UX/UI documentée directement dans les mêmes familles, jalons et gates.**

**Ne sont pas gelés comme faits prouvés :** nombre réel de workflows dans B0, état d’exécution des tickets historiques, empreinte B0 non recalculée depuis l'archive dans cet audit, performance RTX 3070, annotations corpus non vérifiées, imports réels Design Space, résultats physiques de coupe, compatibilité des versions futures et seuils matière encore à calibrer.

**Pièces de contrôle** : cette roadmap v3.1, le rapport de contre-expertise séparé, le manifeste de gel SHA-256 séparé. Les états de développement doivent être tenus dans un tableau de pilotage distinct ; aucune édition silencieuse de l'un des trois documents figés.

**Décision historique :** la **ROADMAP V3.1 est archivée, figée et non réécrite**. La V3.2 consolidée devient le projet de référence documentaire, sous réserve de son acte de gel séparé ; le logiciel reste gelé.

# PARTIE IV — CONTRAT PRODUIT ET UX/UI TRANSVERSAL v3.2

*Cette partie **appartient à la roadmap principale**. Elle développe les engagements introduits dans F01–F15, G2/G4/G6/G7/G8, la grille de qualité §9 et les tickets S-067–S-101. Il ne s'agit ni d'un document autonome ni d'une nouvelle couche de produit obligatoire pour le MVP. En cas de contradiction, privilégier : sécurité/sauvegarde, vérité d'export, accessibilité du flux principal, puis confort.*

## 36. Conception détaillée des écrans et contrats d'interaction

### 36.1 — Accueil et première utilisation

**Contenu :** derniers projets avec miniature + date et état ; quatre parcours *Sticker imprimé*, *Silhouette à découper*, *Séparer une planche*, *Ouvrir/modifier un projet* ; glisser-déposer central, bouton parcourir ; « Pourquoi choisir ceci ? ». Afficher clairement « Sur cet ordinateur » et l'absence d'envoi en ligne par défaut.

**Succès :** débutant part sans installer de modèle IA, sélectionner une opération ComfyUI ni créer un compte. **Échec utile :** aucune image choisie → appel à importer ; extension non reconnue → liste des formats acceptés, source préservée.

### 36.2 — Express : quatre états fonctionnels

| État | Ce qui est affiché | Action principale | Sortie attendue |
|---|---|---|---|
| Importer | Déposer/fichier/exemple contrôlé + destination | « Analyser mon image » | Source chargée et vérifiée |
| Vérifier | Sujets numérotés, vue masque/source, dimensions mm, statut et avertissements | « Vérifier la découpe » ou « Corriger » si problème | Sélection explicite |
| Préparer | Usage/couleur/bordure/planches, aperçu de chemin ou PNG aplati | « Contrôler l'export » | Artefact(s) adaptés sans promesse physique |
| Exporter | Formats recommandés, dossier, états de contrôle, version et instructions | « Exporter ces fichiers » | Fichiers, dossier ouvrable, rapport lisible |

La présentation peut rester en **trois grandes étapes** (« Importer → Vérifier → Exporter ») si « Préparer » est une section de Vérifier, pour ne pas fragmenter inutilement le MVP. Aucun « Suivant » inerte ; bouton précédent conserve toutes les corrections. Prévoir les états « source non compatible », « traitement interrompu », « résultat à revoir », « export partiel ».

### 36.3 — Atelier : sélection et retouche

**Éléments :** arborescence des objets avec vignettes, calques, icônes visibilité/verrouillage, toile zoomable, pinceaux Ajouter/Retirer, lasso, sélection d’îlots, trous, bordures, comparaison. **Point clé :** un sujet détaché (fleur, accessoire, antenne) est visible comme sous-élément relié au sujet principal, plutôt que supprimé parce qu’il ne touche pas la silhouette.

**Contrats :** changement de sélection n'efface pas la correction en cours ; si le masque est recalculé par IA, l'ancienne version est conservée et la différence affichée. Tout clic « Corriger tout » affiche le nombre exact d'objets affectés ; un changement local reste local.

### 36.4 — Fabrique : assistant de faisabilité

**Centre :** motif à sa taille indiquée en mm, page, tapis/document, ligne de coupe (mode tracés, non simulée en couleurs), surlignage de détails fragiles et collisions. **Droite :** opération, taille, matériau, bordure, trous, nombre, version de profil matière et état calibré/non testé. **Bas :** « 2 contours trop fins », chaque avertissement cliquable.

**Export Print Then Cut :** guide de transfert pour Design Space, sans création de marques propriétaires ; le fichier aplati PNG reste recommandé pour le parcours sticker historique. **Export Basic Cut :** inspection des chemins, unités et trous. Éviter de présenter un aperçu de tapis comme une reproduction certifiée du placement Design Space.

### 36.5 — Vectoriel : deux finalités distinctes

- **Art :** fidélité colorimétrique/graphique, vrais chemins, nombre de calques, dégradés/limites, couleurs et points modifiables.
- **Cut :** regroupement par opération/matière, géométrie exploitable, seuil de détails, trous/îlots, doubles coupes, ordre d'assemblage.
- **Comparateur en 3 vues** : source / rendu SVG / contours ; la simplification qui améliore Cut peut dégrader Art et inversement. Aucune « meilleure version » sans désigner l'usage.

### 36.6 — Bibliothèque : retrouver et réutiliser

Miniatures avec indicateur « source intacte / projet modifié / export existant », filtre par format/usage/matière et date, favoris, duplication, variantes, dernières ouvertures ; un projet manquant signale son emplacement et offre un chemin de réparation explicite. Jamais de suppression silencieuse d’un fichier source ; suppression définitive avec confirmation et politique de sauvegarde claire.

### 36.7 — Expert : sans mettre la complexité devant les débutants

Montrer fournisseurs installés/non installés/non testés, VRAM/RAM mesurées, répertoire modèles, jobs et journaux, latences, paramètres techniques et diagnostics. L'activation d'un fournisseur est optionnelle, son absence ne bloque pas l'import d'un PNG transparent ; aucun état « IA prête » basé uniquement sur la présence d'un nom dans un menu.

## 37. Catalogue de fonctions utiles au quotidien — découverte et décision

**Évaluation UX centrée sur fréquence d'utilisation, temps évité, risque de confusion et coût technique.** Une idée peut être très utile tout en restant P2 si elle retarde le produit stable.

| ID valeur | Besoin utilisateur concret | Fonction cible | Première fenêtre | Raison / preuve |
|---|---|---|---|---|
| VU-01 | « Je veux commencer sans savoir quel SVG choisir » | Accueil orienté objectif + export recommandé | MVP | Choix cohérent observé sur trois scénarios |
| VU-02 | « J'ai douze images sur une seule planche » | Détection, vignettes numérotées, vérification par sujet | MVP | 12/12 ou refus explicite et correction ciblée |
| VU-03 | « Je ne veux pas couper un rectangle » | Diagnostic de masque presque rectangulaire + action corrective | MVP | Aucun faux positif « prêt sticker » |
| VU-04 | « Je veux juste un joli sticker imprimé » | PNG aplati Print Then Cut et guide d'import | MVP | Coupon validé réellement dans Design Space |
| VU-05 | « Je veux éviter de recommencer » | Autosave, révisions, reprise du dernier contexte | MVP | Relance après crash sans perte d'actions validées |
| VU-06 | « Je ne connais pas les dimensions utilisables » | Taille en mm, bordure comprise, état de gabarit | MVP | Mesures cohérentes, limites indicatives clairement nommées |
| VU-07 | « Quel détail la lame va-t-elle tenter de couper ? » | Vue chemin de coupe + diagnostic localisable | MVP/G4 | Aucun chemin critique silencieux |
| VU-08 | « J'ai une erreur, comment je la règle ? » | Message problème→impact→solutions + action directe | MVP/G2 | Un novice reprend sans réimporter |
| VU-09 | « Je veux ajouter mon prénom » | Texte et étiquette avec gabarit | G6 | Projet sauvegardé et export conforme |
| VU-10 | « Je veux déplacer plusieurs objets » | Multi-sélection, alignement, duplications | G6 | identités et positions conservées |
| VU-11 | « Je veux changer de couleur » | Palette éditable, couleurs conservées sur calques | G5/G6 | propriétés vectorielles réelles, non bitmap |
| VU-12 | « Je veux remplir une feuille sans gâcher » | Disposition comparée et placement verrouillé | G7 | collision = 0, surface et pertes quantifiées |
| VU-13 | « J'ai 30 prénoms différents » | Variables CSV avec aperçu de toutes les variantes | G7 | accents et débordements détectés |
| VU-14 | « Je ne veux pas refaire les 49 réussites » | Job manager, statut par élément, relance ciblée | G7 | lot interrompu repris sans doublon |
| VU-15 | « Quelle découpe pour ce papier ? » | Fiche matière versionnée + coupon de test | G4/G9 | recommandation non universelle, test consigné |
| VU-16 | « Où ai-je enregistré ce design ? » | Bibliothèque locale, miniatures et ouverture du dossier | G7 | projet retrouvé par usage/nom |
| VU-17 | « Ce PNG est flou à la taille finale » | Alerte qualité image et avant/après sans fausse HD | G2/G4 | note de qualité raster honnête |
| VU-18 | « Je veux un SVG que je puisse éditer » | Mode artistique avec classification vraie vectorisation | G5 | formes éditables dans logiciel tiers |
| VU-19 | « Je veux refaire le même projet Noël » | Dupliquer / créer une variante | G6/G7 | source inchangée, variante indépendante |
| VU-20 | « Je veux une scène papier en plusieurs plans » | Module diorama + plan d'assemblage | G9 | prototype physique reproductible |
| VU-21 | « Je ne veux pas un logiciel qui rame » | Aperçu léger, opérations lourdes découplées, file, pause | MVP/G8 | UI réactive sur machine cible, temps mesuré |
| VU-22 | « Je veux utiliser le clavier ou agrandir le texte » | Accessibilité, alternative au drag, taille UI | MVP/G8 | parcours complet sans souris obligatoire |
| VU-23 | « Je fais toujours la même action » | Préréglages/favoris et « refaire sur sélection » | G2/G7 | aucun changement implicite hors sélection |
| VU-24 | « Je ne veux pas perdre mon visuel privé » | Tout local, source protégée et logs nettoyés | MVP | zéro transfert non sollicité, auditable |
| VU-25 | « Je veux estimer mon coût » | Estimation feuilles/matière/encres si données utilisateur | G7/G9 | coût marqué « estimé » et hypothèses visibles |
| VU-26 | « Je veux savoir si une police rendra bien » | Aperçu fontes et texte converti en tracés à l’export | G6 | défauts de glyphes et substitution signalés |
| VU-27 | « Je me trompe entre édition et découpe » | Libellés de formats et statut par axe | MVP | erreur d'export évitée dans cas de test |
| VU-28 | « Je veux être guidé dans Design Space » | Aide de transfert contextualisée, liens officiels | MVP/G4 | procédure alignée sur version machine actuelle |

### Fonctions à ne pas intégrer au MVP malgré leur attrait

Génération d'images universelle, éditeur de dessin complet type Illustrator, refonte automatique de textes/OCR, marketplace, synchronisation cloud, pilotage direct Explore 5, génération des repères d'impression, gestion de commandes clients, reconnaissance totale des personnages et application autonome indépendante : **hors MVP**, potentiellement exploratoires ou incompatibles avec la frontière Design Space. Refus des abonnements cachés et du téléchargement IA implicite.

### « Intelligence utile » et non « IA partout »

Proposer automatiquement le meilleur *parcours* à partir des propriétés vérifiables d'une image, tout en montrant pourquoi : « image déjà transparente : pas besoin de détourage », « fond uni : méthode rapide », « 12 zones candidates : confirmer leur nombre », « fond complexe : IA locale ou correction ». Si une étape échoue, préserver l'original et proposer un autre chemin. Une heuristique reproductible a la priorité sur une inférence lourde lorsqu'elle suffit.

## 38. Parcours utilisateur : scripts de recette concrets

| Scénario | Préconditions | Actions minimales | Critère de réussite | Échec testé |
|---|---|---|---|---|
| UX-A : sticker simple | PNG alpha correct | déposer → aperçu → taille → exporter | fichier recommandé, vraie taille, instructions | alpha inversé détecté |
| UX-B : 12 escargots | planche T-02 annotée | déposer → identifier 12 → contrôler corrections → exporter | 12 PNG individuels + planche ; pas de guides pointillés | deux sujets fusionnés, refus visible |
| UX-C : photo et accessoire | photo multiélément | choisir sujet + conserver accessoire → retoucher | aucun accessoire supprimé sans accord | IA non disponible et voie manuelle |
| UX-D : vinyle monochrome | silhouette U-03 | taille mm → vue chemins → export Basic Cut | chemins fermés, unité correcte, coupon | trou parasite / double chemin signalé |
| UX-E : sticker avec texte | dessin + police | insérer prénom → bordure → sauvegarder | texte identique après ouverture, rendu fixe | police manquante avertie |
| UX-F : planche 24/50 | sources de tailles mixtes | charger lot → examiner anomalies → exporter/reprendre | succès partiels conservés et identifiants stables | annulation/OOM à la moitié |
| UX-G : erreur de contour | JPEG fond variable | tentative de détourage → alerte → corriger/choisir Carte | aucune exportation mensongère comme sujet | clique « voir problème », focus correct |
| UX-H : récupération | projet en cours sauvegardé | fermer brutalement → relancer | restauration des révisions validées | fichier projet corrompu sans perte original |
| UX-I : mobilité réduite/zoom | écran 1366×768 à 150% | clavier → choisir fichier → vérifier → exporter | aucune action principale inaccessible | geste drag indispensable refusé |
| UX-J : le même design dans deux logiciels | même image/taille/profil | tester Design Space, Canva et SmartSVG | protocole chronométré, rendu/découpe comparés | aucune « meilleure qualité » affirmée sans chiffres |

**Observations minimales par essai utilisateur :** réussite autonome, nombre de retours arrière, erreurs récupérées, temps total, temps de correction, clics/commandes, confusion de format, réponse au feedback, latence perçue, problème d’accessibilité. Les images/productions fournies par une personne réelle ne sont pas collectées au-delà du nécessaire sans accord.

## 39. Décisions produit et UX : que construire dans quel ordre ?

### 39.1 Échelle de priorisation indépendante des envies ponctuelles

Pour chaque proposition, noter **usage (1–5), gain utilisateur (1–5), réduction du risque (1–5), charge technique (1–5), dépendances et incertitude**. Une scorecard éventuelle ne décide pas seule : tout P0 sécurité/exactitude reste prioritaire. Ne pas annoncer ces notes comme issues de données utilisateur ; elles sont des hypothèses à valider. Examiner toute idée P2 seulement après les gates du parcours central.

### 39.2 Paquets de travail incrémentaux et non bloquants

| Paquet | Dépendance non négociable | Livrable visible | Valeur avant enrichissement |
|---|---|---|---|
| UX-0 Contrat | G0/G1.2, identités et sorties | écrans/états détaillés et tests, aucune feature | empêche une UI contradictoire |
| UX-1 Express | G1.3 projet + exporter stable | 3 étapes, choix de sujet, premier export | stickers simples utilisables |
| UX-2 Correction | masques / retouches persistants | sélectionner/peindre/comparer/sauver | cas difficiles récupérables |
| UX-3 Prévol Cricut | QA géométrie et import | erreurs cliquables, vue coupe, checklist | moins de mauvaises découpes |
| UX-4 Atelier | scène/texte et polices | création/placement/alignement/variantes | autonomie graphique courante |
| UX-5 Factory | file/cache/checkpoints | lot visible, filtré, repris | gain de temps répétitif |
| UX-6 Expert avancé | moteurs stabilisés | profil matériel/IA/outils experts | personnalisation sans bloquer débutants |

### 39.3 Frontière de compatibilité et dette UX

Le nouveau Shell UX ne doit **pas** dupliquer les implémentations Python/JS ni se reposer sur des propriétés UI ComfyUI non stables. Les interactions `select/move/paint/export` sont des commandes applicatives versionnées, sauvegardées et testables hors navigateur ; l'adaptateur d'écran n'est qu'un client. Prévoir les migrations de raccourcis et préférences indépendamment des migrations `.smartsvg` ; le projet doit rester utilisable même si une préférence de disposition est corrompue.

## 40. Performance perçue, accessibilité, robustesse UX : protocole de vérification

### 40.1 Budgets proposés (hypothèses à confirmer sur PC cible)

| Indicateur | Cible de conception initiale | État de preuve |
|---|---|---|
| Réponse visuelle à un clic simple (hors calcul lourd) | ≤ 150 ms médian, à qualifier selon navigateur/charge | **Non mesuré** |
| Pan/zoom sur prévisualisation moyenne | fluide avec aperçu adapté, viser 30 fps minimum | **Non mesuré** |
| Retour d'état au lancement d'un job | ≤ 250 ms hors initialisation GPU, sinon afficher « initialisation » | **Non mesuré** |
| Sauvegarde après changement | journal de révisions durables + snapshots atomiques différés ; fermeture propre et crash testés pour les actions effectivement validées | **Non testé** |
| Navigation clavier Express | 100% des fonctions essentielles accessibles | **Non testé** |
| Écran 1366×768 / 1920×1080, zoom 125/150% | actions indispensables atteignables, pas de défilement horizontal Express | **Non testé** |
| Régression visuelle | capture baseline sur états vide/sujet/erreur/export | **Non implémenté** |

Ces nombres sont des **objectifs initiaux à recalibrer**, non des performances promises. Les aperçus basse résolution ne doivent pas dégrader les fichiers d'export ; distinguer qualité affichée et qualité du document.

### 40.2 Accessibilité et prise en main : obligations par fonctionnalité

- Contraste texte/contrôles selon WCAG 2.2 niveau AA comme référentiel de conception ; tests clavier et lecteur d'écran sur le flux principal dans un navigateur réel ; focus visible et non masqué, étiquettes localisées.
- Objectif de conception : cibles cliquables confortables **≥32 px** quand possibles ; documenter les exceptions tout en respectant l'exigence **24×24 CSS px ou exception définie** de WCAG 2.2 2.5.8. Tout drag doit posséder une alternative sans glisser.
- Informations « vert/rouge » doublées de texte/icônes ; zoom image différent du zoom interface ; raccourcis évitent collisions ComfyUI et système.
- Tests sur écran petit et contrôle clavier ; flux simple sans geste de précision extrême. L'interface reste en français, termes de métier cohérents, glossaire contextuel facultatif.

### 40.3 Tests automatiques + observation humaine

1. Tests de machine d'états UI et contrats back-end, y compris succès partiel, job annulé, erreur GPU, fichier malformé, export réussi + UI planté.
2. Snapshot UI pour les six espaces et variantes d'états, contrôles réellement connectés aux actions.
3. End-to-end avec navigateur **réel** : importer, choisir, zoomer, corriger, exporter, rouvrir ; tests souris+clavier+focus, plusieurs résolutions.
4. Instrumentation locale opt-in pour journaux de performance (mesures agrégées ; anonymisation par défaut) ; aucun envoi de contenu utilisateur.
5. Observation humaine sur utilisateurs novices et récurrents ; au minimum trois parcours fréquents et deux scénarios d'erreur. Nombre de participants à préciser lors du protocole, ne pas extrapoler une réussite générale d'un seul test.
6. Recette Explore 5 sur matière physique séparée des tests de widgets. Un écran réussi ne signifie pas une coupe réussie.

## 41. Registre de décisions / concurrence / limites v3.2

| Décision | Justification utilisateur | Risque évité / règle |
|---|---|---|
| UX/UI au cœur de F14 et G2, pas une annexe | confort et réussite sont des résultats du produit | aucun développement ergonomique hors roadmap |
| Ne pas cloner l'outil autocollant de Cricut par principe | Design Space sait déjà créer sticker, bordures et Kiss/Die Cut | différenciation = acquisition multiobjets, réparation, vérité des sorties |
| Ne pas promettre « meilleur que Canva » par défaut | Canva Vectorify fournit déjà une vectorisation éditable | seules mesures contrôlées peuvent établir une supériorité par tâche |
| Ne pas retirer une fonction utile au prétexte « simplicité » | avancé accessible si besoin | divulgation progressive et Expert réel |
| Ne pas masquer le statut de preuve | risque de matériaux gâchés et coupe parasite | « localement contrôlé », « import testé », « matière testée » séparés |
| Ne pas suivre tous les gadgets UI | maintenance/bugs/délais | un paquet UX à la fois, preuves avant extension |
| Respecter l'environnement ComfyUI existant | conserver compatibilité et possibilité de rollback | UI adossée à API de commande propre, non au graphe en usage simple |
| Limites A4/Letter et capteur gérées par Design Space | machine et logiciel propriétaire évolutifs | checklist versionnée, marges indicatives, rien de certifié sans essai |

### Sources officielles vérifiées le 24 octobre 2026

- Cricut — outil Autocollant, découpe Kiss/Die Cut, bordure, aplatissement : https://help.cricut.com/hc/fr/articles/19366738622359-Comment-utiliser-l-outil-Autocollant-dans-Design-Space
- Cricut — Print Then Cut Explore 5, orientation A4, enchaînement Design Space : https://help.cricut.com/hc/fr/articles/38613592650903-Comment-imprimer-puis-d%C3%A9couper-avec-la-Cricut-Explore-5
- Cricut — Offset, calques et aplatissement : https://help.cricut.com/hc/fr/articles/360061650414-Comment-utiliser-la-fonction-de-d%C3%A9calage-dans-Design-Space
- Canva — Vectorify, vecteurs éditables : https://www.canva.com/fr_fr/help/convert-images-to-vectors/
- W3C — WCAG 2.2 (2.5.7 glissement / 2.5.8 taille cible) : https://www.w3.org/TR/WCAG22/

### Gate de la roadmap consolidée

**À considérer acquis documentairement :** périmètres, parcours, rôles des six espaces, contrats d'interface, liens avec moteurs, gabarits d'essai UX, dépendances et nouveaux tickets. **Toujours à vérifier sur le vrai logiciel :** écran réel, vitesse, respect clavier, sauvegarde en cas de crash, GPU et fabrication Cricut. Ni une roadmap plus longue ni des mockups ne valent une validation en utilisation.

**Le premier lot à ouvrir reste G0.2–G0.4 puis G1.1 (inventaire en lecture seule)**. Cette roadmap V3.2 est figée pour planification, sans reprise du développement ; chaque future modification devra être portée par une nouvelle révision traçable ou un ADR, en conservant intégralement V3.1.


## 42. Acte de gel V3.2 et règle de reprise

**Décision finale : ROADMAP MASTER V3.2 FIGÉE POUR PLANIFICATION.** Ce gel concerne exclusivement l’ingénierie des exigences et la priorité des fonctionnalités. Le fichier V3.1 original n’a pas été réécrit ; la référence code V21.14.1 n’a pas été analysée ni modifiée dans ce travail. Le gel du master ne certifie ni interface, ni IA, ni import, ni découpe physique.

**Dès la reprise :** consolider le corpus G0.2–G0.4, vérifier l’archive B0 et inventorier les modules/workflows en G1.1 ; produire ensuite les contrats G1.2/G1.3 avant l’UI Express G2.1. **Pas d’implémentation prématurée des tickets UX, même considérés P0, avant leurs dépendances.**

**Politique de changement :** toute nouvelle idée recevra un ID, une preuve utilisateur visée, une dépendance, une priorité et une décision documentée ; elle sera intégrée dans la **prochaine version principale**, pas reléguée automatiquement à une annexe.