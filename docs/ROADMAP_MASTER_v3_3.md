# SmartSVG Studio — ROADMAP MASTER V3.3

## Statut et décision documentaire

**Date de proposition :** 28 octobre 2026
**Statut :** version candidate à la publication ; devient directrice uniquement après fusion de la PR #60 **et** publication de la gouvernance protégée correspondante
**Document précédent :** `ROADMAP_MASTER_v3_2.md`, conservé intégralement et inchangé comme archive historique
**Objet :** restructurer et détailler la planification sans retirer, réduire ni repousser silencieusement une ambition approuvée

La V3.3 reprend toutes les exigences, familles F01 à F15, jalons G0 à G9, tickets S-001 à S-101, scénarios, risques et gates historiques. L'[annexe normative V3.3](ROADMAP_HERITAGE_v3_3.md) contient la copie intégrale des obligations V3.2 ; le [registre V3.3](ROADMAP_TRACEABILITY_v3_3.md) contient les 101 exigences historiques individualisées, pour permettre l'application de V3.3 sans revenir au fichier gelé V3.2. Les nouvelles obligations sous `R33-001` à `R33-040` complètent sans déclasser cet héritage.

Cette révision ne certifie ni installation Windows, ni inférence GPU RTX 3070, ni import Design Space, ni découpe Cricut Explore 5. Elle décrit comment obtenir et distinguer ces preuves.

**Navigation V3.3 :** [Registre de traçabilité](ROADMAP_TRACEABILITY_v3_3.md) · [Matrices de couverture](ROADMAP_COVERAGE_v3_3.md) · [Annexe historique normative](ROADMAP_HERITAGE_v3_3.md) · [Contre-expertise](ROADMAP_AUDIT_v3_3.md). Après fusion de la publication documentaire **et mise à jour approuvée du contrat AGENTS.md**, ce document devient l'unique maître actif ; la V3.2 originale reste une archive protégée.

## 1 Vision produit conservée

SmartSVG Studio est un atelier local de préparation créative et de fabrication. Il doit permettre à une personne non technique d'importer ou créer un visuel, choisir et corriger les sujets utiles, composer un projet, préparer le bon type de sortie, vérifier les risques connus, sauvegarder le travail et transférer le résultat vers Design Space.

Le produit conserve six espaces cohérents partageant un seul état de projet :

1. **Express** pour aller rapidement d'une source à une sortie contrôlée.
2. **Atelier** pour sélectionner, retoucher et composer.
3. **Fabrique** pour dimensionner, contrôler les chemins et préparer les planches.
4. **Vectoriel** pour distinguer édition graphique et chemins de fabrication.
5. **Bibliothèque** pour reprendre, rechercher, dériver et réutiliser.
6. **Expert** pour diagnostiquer les moteurs, modèles, ressources et performances.

Les six espaces ne deviennent jamais six applications indépendantes. Ils consomment les mêmes identifiants, ressources, révisions, commandes et preuves.

## 2 Principes non négociables

### 2.1 Vérité des sorties

- Un PNG Print Then Cut est une image raster aplatie ou transparente destinée au parcours d'impression de Design Space.
- Un SVG Basic Cut décrit des chemins de coupe et ne devient pas un SVG couleur éditable par simple changement d'extension.
- Un SVG Cut multicouche regroupe des chemins de coupe séparés par couche, couleur ou matière avec ordre, repères d'assemblage et profil physique ; il reste distinct du Basic Cut monochrome et du SVG d'édition.
- Un SVG d'édition peut contenir des calques, couleurs et structures qui ne sont pas directement adaptés à la découpe.
- Un fichier généré n'est pas automatiquement importable, découpable ou fabriqué.

### 2.2 Original et transformations

L'original reste immuable. Chaque transformation crée une révision traçable, avec provenance, paramètres, empreintes et possibilité de revenir au dernier état validé. Une conversion destructive exige une confirmation et ne remplace jamais silencieusement la source.

### 2.3 Local et facultatif

L'IA reste locale et facultative. Une voie CPU ou manuelle doit préserver l'accès aux parcours essentiels. Aucun contenu utilisateur n'est envoyé sur le réseau sans action et consentement explicites.

### 2.4 Preuves séparées

Chaque capacité utilise l'échelle de maturité suivante :

`SPECIFIE → ARCHITECTURE → IMPLEMENTE → RACCORDE → QUALIFIE → STABILISE`

Les axes de preuves **automatiques, Windows, Design Space et physiques sont indépendants**, et ne constituent pas des étapes obligatoires dans un ordre unique (un test Windows n'atteste pas un test Cricut). Le registre de traçabilité porte le statut d'implémentation, les quatre axes séparés, le SHA, l'environnement, la date et l'emplacement des preuves. Un état ne prouve jamais automatiquement le suivant.

## 3 Parcours utilisateur de référence

### P01 Sticker Print Then Cut simple

**Entrée :** PNG, JPG ou WebP unique.
**Flux :** importer, diagnostiquer, choisir le sujet, corriger le masque, régler la taille et la bordure, vérifier la résolution, exporter le PNG et consulter la checklist Design Space.
**Sorties :** original préservé, projet `.smartsvg`, PNG transparent ou aplati selon profil, rapport de prévol.
**Erreurs :** résolution insuffisante, alpha absent ou inversé, bord coupé, halo, fichier corrompu, export interrompu.
**Récupération :** revenir à l'original, modifier taille ou masque, reprendre l'export sans remplacer un fichier valide.
**Preuve attendue :** import Design Space documenté puis coupon imprimé et découpé sur le contexte matériel déclaré.

### P02 Silhouette SVG Basic Cut

**Entrée :** image avec alpha, masque validé ou SVG sûr.
**Flux :** produire ou choisir les contours, inspecter fermeture, trous, doubles chemins, micro-détails et dimensions, corriger ou refuser, exporter.
**Sorties :** SVG Basic Cut avec unités explicites et rapport des chemins.
**Erreurs :** chemin ouvert, auto-intersection, îlot fragile, tracé hors `viewBox`, unité absente, complexité excessive.
**Récupération :** localiser le défaut, appliquer une correction réversible ou revenir au masque validé.
**Preuve attendue :** import Design Space puis découpe sur une matière et une machine identifiées.

### P03 Photo smartphone multi-sujets

**Entrée :** JPEG ou HEIC préalablement converti, orientation EXIF, profil couleur et arrière-plan variables.
**Flux :** normaliser l'affichage sans altérer l'original, proposer plusieurs sujets, conserver accessoires, corriger les masques, comparer et sauvegarder.
**Sorties :** sujets distincts, masques float32, provenance de source et révisions.
**Erreurs :** sujet ambigu, accessoire séparé, profil couleur inconnu, OOM GPU, modèle absent, timeout et résultat obsolète.
**Récupération :** choisir manuellement, réassocier un accessoire, basculer CPU ou outil manuel, refuser tout résultat d'une ancienne révision.
**Preuve attendue :** cas de référence évalués sur l'environnement déclaré, masques sauvegardés puis rouverts à l'identique.

### P04 Planche 12 24 ou 50 sujets

**Entrée :** sujets d'un ou plusieurs projets.
**Flux :** filtrer, dimensionner, disposer, verrouiller certains placements, comparer des dispositions, corriger les collisions, interrompre et reprendre.
**Sorties :** planche, exports individuels, manifeste par sujet et rapport des échecs.
**Erreurs :** un élément invalide, espace insuffisant, doublon, collision, annulation, disque plein ou crash.
**Récupération :** conserver les éléments réussis, corriger ou retirer l'élément fautif et reprendre sans doublon au dernier checkpoint.
**Preuve attendue :** planches 12 et 24 sans collision ni hors-page, puis lot 50 interrompu et repris avec rapport par objet.

### P05 Composition avec texte

**Entrée :** images, formes, texte et police locale.
**Flux :** placer, redimensionner en mm, aligner, grouper, verrouiller, ordonner les calques, sauvegarder, rouvrir et exporter selon l'usage.
**Sorties :** composition éditable dans `.smartsvg`, PNG de rendu, SVG d'édition et éventuellement tracés de texte pour Basic Cut.
**Erreurs :** police absente, glyphe manquant, ressource déplacée, substitution refusée, sortie de zone sûre.
**Récupération :** relier la ressource, choisir explicitement une police ou conserver le rendu figé, annuler la transformation fautive.
**Preuve attendue :** étiquette composée, sauvegardée, rouverte et exportée avec mesures et rendu identiques dans le contexte déclaré.

### P06 SVG multicouche éditable

**Entrée :** illustration adaptée à la vectorisation.
**Flux :** vectoriser, comparer au rendu source, isoler les calques, ajuster palette et simplification, produire séparément édition et fabrication.
**Sorties :** SVG d'édition, aperçu raster, SVG Cut multicouche par couleur ou matière, fiche d'ordre et d'assemblage, mesures de fidélité et de fabricabilité séparées.
**Erreurs :** trop de couleurs, traits internes perdus, trous incorrects, dégradé non représentable, micro-chemins, couche sans matière ou ordre ambigu.
**Récupération :** revenir au rendu raster, fusionner ou corriger une couche sans toucher à l'original, refuser le profil de coupe tout en conservant le SVG d'édition.
**Preuve attendue :** ouverture et édition du SVG riche, import séparé des couches de coupe, prototype multicouche assemblé avec contexte matériel.

### P07 Bibliothèque et variantes

**Entrée :** projets et gabarits locaux.
**Flux :** reprendre le dernier travail, rechercher, prévisualiser, dupliquer, créer une variante, retrouver les ressources et ouvrir le dossier de sortie.
**Sorties :** projets indépendants reliés par provenance, miniatures et tags.
**Erreurs :** index corrompu, ressource manquante, préférence invalide, doublon ou migration interrompue.
**Récupération :** reconstruire l'index, relier ou signaler la ressource, réinitialiser les préférences et conserver l'archive originale avant migration.
**Preuve attendue :** retrouver, dupliquer et rouvrir un projet sur une autre installation sans ressource manquante silencieuse.

### P08 Production personnalisée

**Entrée :** modèle et CSV avec noms, numéros, dates ou couleurs.
**Flux :** valider les colonnes, prévisualiser chaque variante, produire par lot, filtrer les erreurs, relancer un élément.
**Sorties :** exports nommés de manière sûre, manifeste, rapport et reprise.
**Erreurs :** encodage CSV, valeur trop longue, glyphe absent, collision de nom, erreur partielle et annulation.
**Récupération :** isoler les lignes fautives, conserver les sorties valides, corriger le mapping et relancer uniquement les variantes concernées.
**Preuve attendue :** 30 variantes contrôlées, puis reprise d'un lot partiel sans doublon ni écrasement.

### P09 Projet matériaux multiples

**Entrée :** composition avec calques associés à des matériaux.
**Flux :** choisir des profils indicatifs, séparer les sorties, appliquer miroir lorsqu'il est pertinent, ordonner l'assemblage et documenter les essais.
**Sorties :** fichiers par matière, instructions et avertissements.
**Erreurs :** matière non qualifiée, couche trop fragile, miroir incohérent, tolérance insuffisante, ordre ou repères d'assemblage ambigus.
**Récupération :** changer de profil, renforcer ou regrouper une couche, réordonner et régénérer uniquement les sorties touchées.
**Preuve attendue :** prototype assemblé avec contexte, tolérances et limites documentés.

### P10 Diagnostic et récupération

**Entrée :** installation, projet, job ou export défaillant.
**Flux :** collecter un rapport local expurgé, identifier la révision saine, restaurer ou reprendre, exporter les informations sans média privé.
**Sorties :** diagnostic reproductible, état de récupération et preuve d'absence de perte silencieuse.
**Erreurs :** rapport impossible, logs incomplets, backup invalide, droits insuffisants, version inconnue ou diagnostic contenant une donnée privée.
**Récupération :** produire un diagnostic minimal expurgé, préserver tous les originaux, proposer les révisions candidates sans en appliquer une silencieusement.
**Preuve attendue :** panne injectée reproduite, dernier état sain restauré et rapport vérifié sans média, secret ni chemin personnel non nécessaire.

## 4 Catalogue fonctionnel exhaustif

### F01 Acquisition et diagnostic d'image

**Capacités conservées :** PNG, JPG, WebP et SVG sûr ; EXIF, orientation, profil couleur, dimensions, alpha, netteté, bruit, cadrage, captures smartphone, glisser-déposer, presse-papiers, dossiers, lots, doublons, provenance et aperçus.
**Détails obligatoires :** limites de taille et de pixels, décodage borné, rejet des formats malformés, choix explicite en cas de conversion, conservation de l'original, diagnostic avant transformation.
**Extensions conservées :** PDF page par page, scanner et appareils photo lorsque leurs contrats de sécurité et de qualité sont définis.
**Gate :** aucun canal d'import ne modifie la source ni n'inverse silencieusement alpha, orientation ou couleur.

### F02 IA de compréhension et sélection

**Capacités conservées :** alpha, heuristiques, BiRefNet, RMBG, SAM2, multi-sujets, accessoires, groupes, scène, texte, points positifs ou négatifs, sélection par phrase et apprentissage local supervisé.
**Détails obligatoires :** action explicite, journal du fournisseur réellement exécuté, empreinte des modèles, annulation, timeout, résultat obsolète, OOM, fallback CPU ou manuel et restauration immédiate après « mauvais sujet ».
**Gate :** chaque cas de référence produit un sujet évalué ou un refus utile ; aucune vignette ne vaut preuve de masque raccordé.

### F03 Correction et édition non destructives

**Capacités conservées :** pinceau ajouter ou enlever, lasso, îlots, trous, dilatation, érosion, fusion, séparation, halo, loupe, taille adaptée au zoom, aperçu du geste, avant-après, annuler-rétablir et correction multi-sujets confirmée.
**Détails obligatoires :** masque float32 pleine résolution comme autorité, commandes versionnées, historique borné, instantanés atomiques, correspondance stricte entre source, sujet et révision.
**Gate :** fermeture, crash et réouverture conservent les pixels validés et la géométrie.

### F04 Qualité raster et impression

**Capacités conservées :** redimensionnement, taille physique, diagnostics de résolution, halos, franges, moiré, palette d'impression, aperçu à 100 %, taille réelle et super-résolution facultative.
**Détails obligatoires :** distinguer interpolation et information réelle, préserver l'original, séparer diagnostic d'impression et diagnostic de découpe, documenter DPI, profil couleur et dimensions.
**Gate :** aucune mention HD ou imprimable sans mesure relative à la taille cible.

### F05 SVG multicouche éditable

**Capacités conservées :** vrais chemins, couleurs, calques, traits internes, trous, palette, fusion, Bézier, dégradés avec fallback, sélection croisée, verrouillage, visibilité et comparaison au rendu source.
**Détails obligatoires :** métriques silhouette et couleur distinctes, alerte de simplification, provenance des formes, limites de fidélité.
**Gate :** aucun raster enveloppé n'est annoncé comme vectoriel entièrement éditable.

### F06 SVG de fabrication et géométrie

**Capacités conservées :** chemins fermés, orientation, union et soustraction, trous, doubles coupes, micro-îlots, taille mm, `viewBox`, unités, simplification, ordre, chevauchements, connexions fragiles et vue chemin de lame.
**Détails obligatoires :** alertes localisables, correction réversible, grammaire SVG sûre, calculs indépendants du rendu couleur, seuils reliés aux essais.
**Gate :** aucune sortie « prête » avec défaut critique non résolu ou non explicitement refusé.

### F07 Sticker et Print Then Cut

**Capacités conservées :** PNG transparent ou aplati selon profil, bordure, halo, trous, taille physique, planches, A4 et Letter, orientation, checklist Design Space, contours individuels, découpe extérieure, kiss cut et die cut lorsque prouvés.
**Détails obligatoires :** ne pas reproduire les marques propriétaires de capteur, versionner les limites Design Space et séparer préparation logicielle et validation physique.
**Gate :** import puis découpe documentés pour le profil et le contexte revendiqués.

### F08 Composer et créer visuellement

**Capacités conservées :** canevas, images, texte, formes, déplacer, redimensionner, tourner, dupliquer, aligner, distribuer, grouper, verrouiller, ordre Z, poignées, mm, guides, grille, zones sûres, menus contextuels, palettes, modèles, clipping et effets futurs.
**Détails obligatoires :** commandes accessibles sans drag, undo cohérent, coordonnées stables, sélection multiobjet et sauvegarde complète.
**Gate :** une étiquette, un sticker et une composition simple restent éditables après réouverture.

### F09 Typographie et texte

**Capacités conservées :** police locale, aperçu, taille, alignement, suivi, interligne, rotation, couleur, contour, texte courbe, texte sur chemin, favoris, accents, alphabets, glyphes, police manquante et OCR guidé futur.
**Détails obligatoires :** aucune substitution silencieuse, licence visible, texte éditable dans le projet et conversion en chemins distincte pour la fabrication.
**Gate :** rendu stable entre sessions ou erreur explicite et récupérable.

### F10 Bibliothèque projet et variantes

**Capacités conservées :** `.smartsvg`, original, ressources, masques, retouches, historique, chemins relatifs, manifeste, tags, collections, favoris, recherche, duplication, modèles, variantes, miniatures et reprise du dernier travail.
**Détails obligatoires :** schéma versionné, migration transactionnelle, sauvegarde atomique, index reconstructible, ressources manquantes explicites et export du dossier.
**Gate :** projet portable et migrable, sans perte silencieuse ni dépendance à une préférence d'interface.

### F11 Planche imposition et économie matière

**Capacités conservées :** disposition sans collision, marges, limites, rotations, groupement matière ou couleur, optimisation, estimation, comparaison de dispositions, verrouillage, déplacement local et recalcul partiel.
**Détails obligatoires :** unités physiques, déterminisme ou graine enregistrée, contrôle hors-page, quantité de feuilles et coût étiqueté comme indicatif.
**Gate :** aucune collision, aucun sujet hors zone et résultat reproductible.

### F12 Production en lots et personnalisation

**Capacités conservées :** 12, 24 et 50 éléments, cache, file, pause, annulation, reprise, états par sujet, CSV, variables, numérotation, variantes, filtres, relance ciblée et rapports.
**Détails obligatoires :** idempotence, noms sûrs, succès partiel, reprise sans doublon, contrôle de chaque variante et budget disque ou mémoire.
**Gate :** un lot interrompu reprend au bon élément et conserve tous les succès déjà validés.

### F13 Profils de matériaux et projets en volume

**Capacités conservées :** papier, carton léger, vinyle autocollant, thermocollant compatible, calques par matière, miroir, pliage validé, ordre d'assemblage, dioramas, cadres lumineux, scènes 3D, pop-up et patronages.
**Détails obligatoires :** recommandations non prescriptives, machine et outil identifiés, tolérances, épaisseur, attaches, prototype et avertissement de test.
**Gate :** aucune compatibilité matière ou machine annoncée sans prototype documenté.

### F14 Ergonomie apprentissage et accessibilité

**Capacités conservées :** Express en français, objectif visible, action principale, état prêt-à vérifier-bloqué, reprise, panneaux, raccourcis, recherche d'action, aide, recettes, personnalisation de l'espace, file de tâches et tutoriels.
**Détails obligatoires :** clavier complet, focus visible, contrastes, libellés, zoom 150 %, alternative au drag, cibles confortables, lecteur d'écran, écrans 1366×768 et mobiles, erreurs exploitables.
**Gate :** parcours principal et une récupération d'erreur réalisables par novice, souris et clavier, sans graphe ComfyUI.

### F15 Sécurité confidentialité et qualité

**Capacités conservées :** SVG et XML sûrs, archives bornées, chemins contrôlés, permissions, originaux protégés, sauvegardes atomiques, manifestes, licences, observabilité locale, provenance IA, mises à jour contrôlées et extensions documentées.
**Détails obligatoires :** menace même origine, données privées, journaux expurgés, dépendances, intégrité, signature future, restauration et aucune requête réseau implicite.
**Gate :** aucune perte de source, exfiltration implicite ou acceptation de contenu actif.

## 5 Architecture cible

### 5.1 Autorités

- Le projet `.smartsvg` est l'autorité portable des ressources, commandes validées, masques et révisions.
- Le moteur Python applique les contrats de fichier, géométrie et persistance.
- ComfyUI exécute les workflows et fournisseurs, sans devenir l'autorité de l'état produit.
- L'interface affiche et émet des commandes ; elle ne fabrique pas un état divergent.
- Design Space et la machine restent des systèmes externes dont les résultats sont enregistrés comme preuves, pas simulés.

### 5.2 Identités et révisions

Chaque source, sujet, masque, objet, export et job possède un identifiant stable. Toute commande transporte `project_id`, `project_revision`, `source_sha256`, `subject_id`, `operation_id` et, si nécessaire, `provider_run_id`. Un résultat en retard ou issu d'une autre révision est refusé ou présenté comme proposition non applicable.

### 5.3 Commandes applicatives

Les actions `import`, `select`, `paint`, `move`, `resize`, `compose`, `preflight`, `export`, `undo`, `redo`, `cancel` et `resume` sont versionnées et testables hors navigateur. Les adaptateurs Express, Atelier et ComfyUI consomment ces commandes au lieu de dupliquer la logique.

### 5.4 Persistance et migrations

Les écritures utilisent temporaire, synchronisation, relecture et publication atomique. Les migrations sont monotones, rejettent les versions futures, préservent l'archive originale et produisent un rapport. L'index de bibliothèque est reconstructible depuis les projets.

### 5.5 Jobs et concurrence

Les jobs sont annulables, bornés et idempotents. Le produit distingue attente, initialisation, exécution, succès partiel, échec, annulation et résultat obsolète. Deux onglets ou processus ne peuvent pas appliquer silencieusement une commande sur des révisions différentes.

## 6 Plan d'exécution complet G0 à G9

L'ordre ci-dessous exprime les dépendances. Aucune capacité des jalons ultérieurs n'est supprimée.

### G0 Référentiel et préparation

Conserver provenance, corpus synthétique ou autorisé, inventaire, licences, environnements cibles, baseline et règles de preuve. Ajouter un inventaire vivant des dépendances et des surfaces privées.
**Gate :** chaque source et fixture est autorisée, chaque environnement est nommé, aucun compteur déclaré n'est accepté sans recomptage.

### G1 Architecture fiabilité et projet

Consolider contrats, identités, `.smartsvg`, migrations, sauvegarde atomique, récupération, projets gérés, commandes et sécurité fichier.
**Gate :** création, écrasement, crash, corruption, disque plein, verrouillage, migration et rollback sont testés sans perte du dernier état sain.

### G2 Fondations de l'expérience et des exports

Livrer Express, sélection, retouches persistantes, formats visibles, états complets, alertes localisées, clavier, aperçus synchronisés et reprise d'activité.
**Gate :** un novice réalise P01 ou P02 et récupère une erreur sur navigateur réel sans ouvrir le graphe.

### G3 Compréhension sélection et IA réelle

Raccorder les vrais sujets, appliquer la sélection à une révision saine, transporter les masques float32, centraliser les retouches, intégrer import smartphone, exécuter explicitement les fournisseurs et mesurer CPU, RAM, VRAM, temps et erreurs.
**Gate :** les cas de référence obtiennent un masque évalué ou un refus utile ; sessions doubles, expiration, résultat obsolète et OOM sont testés.

### G4 Production Cricut de base

Valider PNG Print Then Cut, SVG Basic Cut, prévol interactif, Design Space, Explore 5, planches 12 et 24, matières de référence et checklist de transfert.
**Gate :** P01, P02 et P04 possèdent des preuves distinctes d'import et de fabrication, avec versions et limites.

### G5 Vectoriel fidèle et coupe multicouche

Mesurer fidélité, préserver traits et couleurs, simplifier les Béziers, éditer calques et palette, séparer SVG édition et Cricut et assembler des prototypes multicouches.
**Gate :** fidélité et fabricabilité sont mesurées séparément ; aucun micro-chemin critique n'est masqué.

### G6 Atelier de composition

Livrer canevas, texte, formes, groupes, alignements, dimensions mm, calques, polices, gabarits, historique, variantes, menus contextuels et commandes clavier.
**Gate :** P05 est créé, repris et exporté sans autre logiciel de composition.

### G7 Factory bibliothèque et personnalisation

Livrer cache et reprise de jobs, bibliothèque, tags, variables CSV, imposition, coûts indicatifs, packs de production, tableau de lot et relance unitaire.
**Gate :** P04, P07 et P08 fonctionnent avec succès partiels, interruption et reprise sans doublon.

### G8 Recette sécurité et stable V22

Qualifier installation et mise à jour Windows, sécurité, accessibilité, récupération, documentation, comparaison externe, utilisateurs novices et réguliers, performance et gel fonctionnel.
**Gate :** aucune anomalie P0 ou P1 bloquante ; matrice de compatibilité et preuves liées au head exact.

### G9 Extensions avancées

Conserver PDF, scanner, OCR guidé, modèles avancés, apprentissage local, dioramas, cadres lumineux, pop-up, patronages, nouvelles machines et écosystème d'extensions.
**Gate :** chaque extension possède un contrat, une preuve, un rollback et ne dégrade pas le noyau stable.

## 7 Vagues de livraison sans réduction de périmètre

### Vague A Fondation vérifiable

G0 et G1, sécurité fichier, identités, projets et récupération. Cette vague rend les développements suivants sûrs ; elle ne remplace aucune fonction créative.

### Vague B Parcours connecté

G2 et G3 : vrais sujets, masques, retouches et parcours continu. Les fonctions avancées restent planifiées et utilisent ces contrats.

### Vague C Fabrication utile

G4 : sorties contrôlées et preuves Design Space ou physiques. Elle transforme la génération de fichier en préparation de fabrication.

### Vague D Création et vectoriel

G5 et G6 : édition vectorielle, texte, composition et gabarits. Les contrats de sortie de la vague C empêchent de confondre rendu et découpe.

### Vague E Production et réutilisation

G7 : bibliothèque, lots, variantes et imposition. Les parcours unitaires restent disponibles et servent de référence.

### Vague F Stabilisation et extensions

G8 stabilise l'ensemble ; G9 continue les ambitions avancées sans supprimer leurs dépendances ni leurs gates.

## 8 Sujets transversaux obligatoires

### Installation et exploitation

Installation neuve, mise à jour, rollback, désinstallation, chemins avec espaces ou Unicode, droits limités, antivirus, ports occupés, dépendance absente, mode hors ligne et rapport de diagnostic.

### Compatibilité et migration

Anciennes archives, versions futures, polices absentes, ressources déplacées, préférences corrompues, schémas partiels, migration interrompue et export de secours.

### Fichiers et stockage

Fichier malformé, archive hostile, collision de nom, verrouillage, disque plein, panne pendant écriture, répertoire en lecture seule, réseau lent ou synchronisé et conservation du dernier état sain.

### Sessions et concurrence

Double clic, deux onglets, deux projets, révision déplacée, canal expiré, message dupliqué, résultat en retard, annulation et fermeture brutale.

### IA et ressources

Modèle absent, poids incompatibles, téléchargement interdit, OOM, CPU lent, initialisation, timeout, résultat vide, masque invalide, provenance et reproductibilité.

### Accessibilité et responsive

Clavier, focus, lecteur d'écran, contraste, zoom 125 et 150 %, écran 1366×768, petits écrans, alternative au drag, cible tactile, messages non fondés sur la couleur et réduction des animations.

### Confidentialité et licences

Aucun média privé dans le dépôt ou les logs, consentement réseau, rapport expurgé, licences des polices, modèles et dépendances, durée de conservation et suppression locale.

### Fabrication

Versions Design Space, A4 ou Letter, unités, calibration, matière, lame, tapis, miroir, tolérances, kiss ou die cut, impression, conditions ambiantes et photographie de preuve privée.

## 9 Critères communs de prêt et de terminé

### Définition de prêt

Un lot peut commencer lorsque son parcours, ses entrées, sorties, autorités, dépendances, risques, données de test autorisées, critères d'acceptation, rollback et niveau de preuve visé sont documentés.

### Définition de terminé

Un lot est terminé uniquement lorsque le code est raccordé au parcours réel, les tests pertinents passent, les erreurs sont récupérables, l'accessibilité et la persistance sont vérifiées, le statut documentaire correspond aux preuves, le rollback est praticable et la CI est verte sur le head exact. Les validations matérielles restent obligatoires pour les revendications qui en dépendent.

## 10 Gouvernance et traçabilité

- Toute nouvelle exigence reçoit un identifiant, une famille, un parcours, un gate, une preuve et un responsable de décision.
- Toute modification de capacité met à jour le registre et la matrice de couverture dans la même révision.
- Une preuve stockée porte environnement, versions, SHA, commande ou protocole, résultat et limites.
- Une absence de preuve reste `NON_VERIFIE`, jamais `PASS`.
- Une CI sautée, indisponible ou exécutée sur un autre SHA ne qualifie pas la révision.
- Une régression de compatibilité exige une migration approuvée et un rollback.
- La roadmap ne remplace pas le suivi opérationnel ; le suivi ne peut pas réduire la roadmap.

## 11 Nouvelles exigences R33

| ID | Exigence | Gate principal |
|---|---|---|
| R33-001 | Héritage intégral et vérifiable de V3.2 | Gouvernance |
| R33-002 | Échelle de maturité commune sans promotion implicite | Tous |
| R33-003 | Projet unique partagé par les six espaces | G1-G7 |
| R33-004 | Identités et révisions sur chaque commande asynchrone | G1-G3 |
| R33-005 | Résultat obsolète refusé ou isolé | G3 |
| R33-006 | Masques float32 comme autorité de retouche | G2-G3 |
| R33-007 | Fallback manuel ou CPU pour le parcours essentiel | G2-G3 |
| R33-008 | Séparation permanente PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche et SVG d'édition | G2-G6 |
| R33-009 | Migration transactionnelle des projets | G1-G8 |
| R33-010 | Index de bibliothèque reconstructible | G7 |
| R33-011 | Jobs idempotents avec succès partiel | G7 |
| R33-012 | Annulation et reprise sans doublon | G3-G7 |
| R33-013 | Gestion explicite disque plein et lecture seule | G1-G8 |
| R33-014 | Gestion de sessions concurrentes et double activation | G2-G3 |
| R33-015 | Rapport de diagnostic local expurgé | G8 |
| R33-016 | Inventaire des licences et provenances | G0-G8 |
| R33-017 | Mesure CPU RAM VRAM et temps par fournisseur | G3 |
| R33-018 | Validation responsive et zoom Windows | G2-G8 |
| R33-019 | Alternative clavier à chaque geste complexe | G2-G8 |
| R33-020 | Localisation française cohérente et messages actionnables | G2-G8 |
| R33-021 | Tests d'installation mise à jour et rollback | G8 |
| R33-022 | Versions Design Space associées aux preuves | G4-G8 |
| R33-023 | Contexte machine matière outil associé aux preuves physiques | G4-G9 |
| R33-024 | Données de preuve privées hors dépôt public | Tous |
| R33-025 | Tests de panne pendant sauvegarde export et IA | G1-G8 |
| R33-026 | Budgets pour projets et lots volumineux | G2-G8 |
| R33-027 | Noms de fichiers sûrs et collisions contrôlées | G1-G7 |
| R33-028 | Polices licences et glyphes manquants visibles | G6-G8 |
| R33-029 | Comparaison de rendu indépendante de la fabricabilité | G4-G6 |
| R33-030 | Aucune requête réseau implicite | Tous |
| R33-031 | Rapport par objet pour planches et lots | G4-G7 |
| R33-032 | Préférences UI séparées de l'état projet | G2-G8 |
| R33-033 | États vide chargement erreur annulation et reprise | G2-G8 |
| R33-034 | Preuve liée au SHA exact et à l'environnement | Tous |
| R33-035 | Gate humain pour toute certification matérielle | G4-G9 |
| R33-036 | Rollback documenté pour chaque micro-lot | Tous |
| R33-037 | Registre de risques relié aux tests | Tous |
| R33-038 | Matrice de compatibilité versionnée | G8 |
| R33-039 | Observation utilisateur sans collecte excessive | G2-G8 |
| R33-040 | Gel fonctionnel avant déclaration stable | G8 |

## 12 Documents compagnons

- [Registre de traçabilité](ROADMAP_TRACEABILITY_v3_3.md) définit la conservation des tickets historiques, les statuts et les liens vers les preuves.
- [Matrices de couverture](ROADMAP_COVERAGE_v3_3.md) fournissent les matrices à compléter pour chaque lot et chaque recette.
- `ETAT_ACTUEL_SMARTSVG.md` reste un constat opérationnel vivant et ne remplace ni les exigences ni leurs gates.

## 13 Décision de publication

Cette PR propose de promouvoir V3.3 en roadmap directrice après contre-expertise, vérification de la CI et fusion autorisée. Avant fusion, la V3.2 reste la référence opérationnelle. Après fusion, V3.3 est publiée mais ne devient le seul document maître **opérationnellement applicable** qu'une fois le contrat AGENTS.md basculé par un micro-lot de gouvernance distinct. La V3.2 originale et son manifeste demeurent intacts, en archive. Les automatismes et le contrat AGENTS.md devront être basculés dans un micro-lot de gouvernance distinct et vérifié avant d'annoncer la migration opérationnelle achevée.
