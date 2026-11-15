# SOURCE_CLOSURE SC-02D — 101 assertions des lots 13–17

15 novembre 2026. **Revue de préservation et attribution candidate, non certification intégrale.** Sources V3.4 lues directement sur la branche candidate, blobs : 13_VECTORISATION_SVG.md `f694c0016e896917084f1d70a642f67316d1cf70`; 14_LANGAGE_FABRICATION.md `3b7dd601c6f844f3a3d12b44bc971fc101133367`; 15_PROFILS_EXPLORE5.md `19cf7835044936e5cf2a2f894b5a42456c8fa8b4`; 16_PATRONS_PARAMETRIQUES.md `562af8bc7ceca562381e08251352dfd5bd6c2b69`; 17_EXPORTS_DESIGNSPACE.md `4c13bfe529f672d68a0c66a77c07fcd0068d5170`. Les assertions ci-dessous conservent le texte original, et les propriétaires proposés se rattachent aux tickets V34-096..131 existants, **sans créer de ticket ni de lien historique fictif**. La sélection du propriétaire est un arbitrage de conception, pas la preuve que le DoD est satisfait. Les 101 lignes sont individuelles : 30+30+18+10+13.

| Assertion historique | Propriétaire proposé | Oracle intégral conservé | Axe de preuve attendu |
|---|---|---|---|
| T-V34-13-01 | V34-96 (candidat; lien à confirmer contre DoD intégral) | Masque/source SHA identiques → proposition déterministe avec mêmes paramètres | auto |
| T-V34-13-02 | V34-96 (candidat; lien à confirmer contre DoD intégral) | Seuil alpha 0/20/128 change rapport, jamais contour accepté sans confirmation | auto |
| T-V34-13-03 | V34-96 (candidat; lien à confirmer contre DoD intégral) | Source EXIF orientée + transform mm → bounding box physique cohérente | auto |
| T-V34-13-04 | V34-97 (candidat; lien à confirmer contre DoD intégral) | Anneau + trou + îlot V13-A : hiérarchie exacte conservée | auto |
| T-V34-13-05 | V34-97 (candidat; lien à confirmer contre DoD intégral) | `evenodd`/`nonzero` rendus distincts et trous correctement signalés | auto |
| T-V34-13-06 | V34-98 (candidat; lien à confirmer contre DoD intégral) | Courbe Bézier fermée : aucun PASS topologique sans vérification de courbe | auto |
| T-V34-13-07 | V34-97 (candidat; lien à confirmer contre DoD intégral) | Auto-intersection V13-B → alerte localisée et export bloqué si CUT | auto |
| T-V34-13-08 | V34-97 (candidat; lien à confirmer contre DoD intégral) | Chemin de lame doublé → `VECTOR_DUPLICATE_CUT`, aucun silence | auto |
| T-V34-13-09 | V34-98 (candidat; lien à confirmer contre DoD intégral) | Simplification qui supprime un trou → refus, ancien digest conservé | auto |
| T-V34-13-10 | V34-98 (candidat; lien à confirmer contre DoD intégral) | Simplification valide : métriques de contour/surface avant-après consignées | auto |
| T-V34-13-11 | V34-99 (candidat; lien à confirmer contre DoD intégral) | Contour extérieur seul ≠ calques couleur, UX avertit | UI/auto |
| T-V34-13-12 | V34-99 (candidat; lien à confirmer contre DoD intégral) | Quatre calques : IDs, palette, ordre et visibilité réversibles | auto/UI |
| T-V34-13-13 | V34-99 (candidat; lien à confirmer contre DoD intégral) | Export d'édition garde les objets éditables, aucun raster déguisé | auto |
| T-V34-13-14 | V34-100 (candidat; lien à confirmer contre DoD intégral) | Export Basic Cut ne contient ni clipping, gradients, scripts ni images | auto |
| T-V34-13-15 | V34-100 (candidat; lien à confirmer contre DoD intégral) | SVG mm + viewBox : dimensions contrôlées et coordonnées finies | auto |
| T-V34-13-16 | V34-104 (candidat; lien à confirmer contre DoD intégral) | 5 001 paths V13-F → `VECTOR_PATH_BUDGET` avant handoff | auto |
| T-V34-13-17 | V34-104 (candidat; lien à confirmer contre DoD intégral) | 64 chemins G2.7 ≠ capacité du nouveau moteur, pas de promesse de 5 000 | auto/UI |
| T-V34-13-18 | V34-100 (candidat; lien à confirmer contre DoD intégral) | Import SVG avec texte éditable/clip/gradient → export Cricut refuse ou convertit avec diff | auto |
| T-V34-13-19 | V34-100 (candidat; lien à confirmer contre DoD intégral) | XML hostile DTD/XXE/script/externe → rejet sans exécution ni réseau | sécurité auto |
| T-V34-13-20 | V34-101 (candidat; lien à confirmer contre DoD intégral) | PNG Print Then Cut inchangé lorsque seul SVG diagnostic demandé | auto |
| T-V34-13-21 | V34-104 (candidat; lien à confirmer contre DoD intégral) | 12/24/50 objets : IDs uniques, aucun objet perdu ni tronqué silencieusement | auto |
| T-V34-13-22 | V34-104 (candidat; lien à confirmer contre DoD intégral) | Révision source modifiée durant job → `STALE`, aucun commit | intégration auto |
| T-V34-13-23 | V34-102 (candidat; lien à confirmer contre DoD intégral) | Retry même commande après ACK perdu → un seul commit, receipt rejoué | intégration auto |
| T-V34-13-24 | V34-104 (candidat; lien à confirmer contre DoD intégral) | OOM GPU simulé → fallback manuel/CPU, projet et source inchangés | auto ; GPU terrain séparé |
| T-V34-13-25 | V34-105 (candidat; lien à confirmer contre DoD intégral) | Clavier : choix contour/couches, revue alerte, Undo/Redo sans perte focus | UI/Windows |
| T-V34-13-26 | V34-101 (candidat; lien à confirmer contre DoD intégral) | V13-G : guide de pli non converti en CUT ou SCORE par couleur | auto |
| T-V34-13-27 | V34-101 (candidat; lien à confirmer contre DoD intégral) | Import SVG Basic Cut réel, dimensions et calques constatés, version Design Space enregistrée | DesignSpace |
| T-V34-13-28 | V34-105 (candidat; lien à confirmer contre DoD intégral) | Coupe Explore 5 d'un contour troué, mesures et matière consignées | physique |
| T-V34-13-29 | V34-104 (candidat; lien à confirmer contre DoD intégral) | Crash/lecture seule/disque plein : projet précédent et source intacts | auto/Windows |
| T-V34-13-30 | V34-103 (candidat; lien à confirmer contre DoD intégral) | Traçabilité test→ticket→S/R33, axe preuve et SHA présents, aucun faux PASS | documentaire/auto futur |
| T-V34-14-01 | V34-106 (candidat; lien à confirmer contre DoD intégral) | GUIDE_ONLY et CUT_CANDIDATE ne créent aucune assignation CUT sans confirmation | auto |
| T-V34-14-02 | V34-108 (candidat; lien à confirmer contre DoD intégral) | SCORE ouvert accepté comme candidat ; CUT ouvert non sûr bloque la fabrication | auto |
| T-V34-14-03 | V34-109 (candidat; lien à confirmer contre DoD intégral) | IDs, digest, unités mm et références invalides provoquent un refus non mutant | auto |
| T-V34-14-04 | V34-106 (candidat; lien à confirmer contre DoD intégral) | PRINT sur PATH et SCORE sur RASTER_REGION refusés | auto |
| T-V34-14-05 | V34-110 (candidat; lien à confirmer contre DoD intégral) | PRINT_THEN_CUT est recette composite ; ne devient pas une opération de PATH | auto |
| T-V34-14-06 | V34-107 (candidat; lien à confirmer contre DoD intégral) | Compatibilité KNOWN_UNSUPPORTED bloque, UNKNOWN avertit sans promotion | auto |
| T-V34-14-07 | V34-107 (candidat; lien à confirmer contre DoD intégral) | Source officielle datée et version du profil exigées pour KNOWN_SUPPORTED | auto |
| T-V34-14-08 | V34-108 (candidat; lien à confirmer contre DoD intégral) | Une double coupe exacte CUT/CUT sur même support est détectée et localisée | auto |
| T-V34-14-09 | V34-108 (candidat; lien à confirmer contre DoD intégral) | Croisement SCORE/CUT légitime est différencié d'une duplication exacte | auto |
| T-V34-14-10 | V34-111 (candidat; lien à confirmer contre DoD intégral) | Score + Cut sans groupe d'alignement donne avertissement Attacher | auto/UI |
| T-V34-14-11 | V34-108 (candidat; lien à confirmer contre DoD intégral) | Un groupe avec supports différents est refusé sans fusion implicite | auto |
| T-V34-14-12 | V34-111 (candidat; lien à confirmer contre DoD intégral) | Projet boîte : deux types d'opérations et géométries distincts préservés | auto |
| T-V34-14-13 | V34-111 (candidat; lien à confirmer contre DoD intégral) | Le guide d'export boîte inclut Score, Attacher, outil, matériau et contrôle mm | auto/UI |
| T-V34-14-14 | V34-111 (candidat; lien à confirmer contre DoD intégral) | Import réel Design Space : Score choisi et Attach vérifié manuellement | Design Space |
| T-V34-14-15 | V34-111 (candidat; lien à confirmer contre DoD intégral) | Essai carton : mesure pli/coupe et outil/version/matière consignés | physique |
| T-V34-14-16 | V34-112 (candidat; lien à confirmer contre DoD intégral) | Pen + Cut garde DRAW distinct et propose guide Attacher | auto/UI/Design Space |
| T-V34-14-17 | V34-113 (candidat; lien à confirmer contre DoD intégral) | Foil + Cut conserve FOIL et avertit sur support/outil non qualifiés | auto/UI/Design Space |
| T-V34-14-18 | V34-107 (candidat; lien à confirmer contre DoD intégral) | Explore 5 rejette Engrave/Deboss Maker-only sans substitution | auto |
| T-V34-14-19 | V34-110 (candidat; lien à confirmer contre DoD intégral) | A4 Print Then Cut n'utilise pas la pleine page comme zone de coupe | auto/UI |
| T-V34-14-20 | V34-110 (candidat; lien à confirmer contre DoD intégral) | 12 escargots : PNG et contrat Print Then Cut restent distincts du SVG Cut | auto/Design Space |
| T-V34-14-21 | V34-107 (candidat; lien à confirmer contre DoD intégral) | Smart Material sans tapis avec combinaison inconnue reste UNKNOWN | auto/UI |
| T-V34-14-22 | V34-109 (candidat; lien à confirmer contre DoD intégral) | HTV multicouche exige miroir explicite par couche et rapport de décision | auto/UI |
| T-V34-14-23 | V34-107 (candidat; lien à confirmer contre DoD intégral) | Tapis carte non déclaré bloque « prêt machine » sans empêcher brouillon | auto/UI |
| T-V34-14-24 | V34-108 (candidat; lien à confirmer contre DoD intégral) | Pochoir fragile : ponts trop fins signalés sans fausse cote universelle | auto |
| T-V34-14-25 | V34-115 (candidat; lien à confirmer contre DoD intégral) | Undo groupe CUT+SCORE restaure assignations, sans supprimer géométries | auto/Windows |
| T-V34-14-26 | V34-115 (candidat; lien à confirmer contre DoD intégral) | Projet périmé / commande dupliquée : CAS/idempotence, aucun double commit | auto/Windows |
| T-V34-14-27 | V34-109 (candidat; lien à confirmer contre DoD intégral) | 50 objets : prévol sans troncature silencieuse et résultats déterministes | auto/Windows |
| T-V34-14-28 | V34-115 (candidat; lien à confirmer contre DoD intégral) | Mode sans IA / OOM simulé : formulaire manuel et aucun commit partiel | auto/Windows |
| T-V34-14-29 | V34-114 (candidat; lien à confirmer contre DoD intégral) | Interface clavier/lecteur d'écran : opérations, avertissements, correctifs accessibles | UI/Windows |
| T-V34-14-30 | V34-109 (candidat; lien à confirmer contre DoD intégral) | Export final refuse BLOCKED, brouillon WARN étiqueté ; aucun PASS externe inventé | auto/UI |
| T-V34-15-01 | V34-116 (candidat; lien à confirmer contre DoD intégral) | La clé complète distingue outil, matière, support et version ; aucune résolution partielle réussie | auto |
| T-V34-15-02 | V34-116 (candidat; lien à confirmer contre DoD intégral) | Support officiel de l'outil sans preuve de combinaison complète reste UNKNOWN | auto |
| T-V34-15-03 | V34-116 (candidat; lien à confirmer contre DoD intégral) | Machine différente n'hérite pas silencieusement du verdict Explore 5 | auto |
| T-V34-15-04 | V34-117 (candidat; lien à confirmer contre DoD intégral) | Un outil Maker-only ne devient jamais SCORE/CUT accepté sur Explore 5 | auto |
| T-V34-15-05 | V34-119 (candidat; lien à confirmer contre DoD intégral) | Un outil absent et une combinaison supportée restent deux statuts indépendants | auto/UI |
| T-V34-15-06 | V34-119 (candidat; lien à confirmer contre DoD intégral) | Une déclaration utilisateur ne crée aucune fausse preuve fabricant ou physique | auto |
| T-V34-15-07 | V34-120 (candidat; lien à confirmer contre DoD intégral) | Scoring Tool conduit au guide Design Space « Score + Attacher » | auto/UI |
| T-V34-15-08 | V34-121 (candidat; lien à confirmer contre DoD intégral) | Support stylo vérifie le marquage de compatibilité, pas une correspondance par couleur | auto/UI |
| T-V34-15-09 | V34-121 (candidat; lien à confirmer contre DoD intégral) | Foil garde la feuille, l'outil et la matière distincts de Cut | auto |
| T-V34-15-10 | V34-118 (candidat; lien à confirmer contre DoD intégral) | Tapis carte inconnu : aucune simulation de placement réellement certifiée | auto/UI |
| T-V34-15-11 | V34-118 (candidat; lien à confirmer contre DoD intégral) | Smart Material sans tapis : type/largeur/longueur minimale contrôlés ; vinyle tiers rejeté sans tapis | auto/UI |
| T-V34-15-12 | V34-123 (candidat; lien à confirmer contre DoD intégral) | Changement de version du profil invalide le prévol précédent sans toucher au projet | auto |
| T-V34-15-13 | V34-122 (candidat; lien à confirmer contre DoD intégral) | Une feuille A4 n'est pas traitée comme un rectangle entièrement découpable | auto/UI |
| T-V34-15-14 | V34-119 (candidat; lien à confirmer contre DoD intégral) | Export brouillon permis avec UNKNOWN, sans étiquette machine-ready | auto |
| T-V34-15-15 | V34-124 (candidat; lien à confirmer contre DoD intégral) | Machine réelle : l'utilisateur confirme le matériel présent, les étapes Score+Cut et le changement d'outil | Windows + Design Space |
| T-V34-15-16 | V34-124 (candidat; lien à confirmer contre DoD intégral) | Essai carton : largeur/alignement du pli et coupe consignés, avec outil/matière/tapis/date | physique |
| T-V34-15-17 | V34-123 (candidat; lien à confirmer contre DoD intégral) | Lecture d'une archive historique conserve les profils/masques inchangés | auto |
| T-V34-15-18 | V34-125 (candidat; lien à confirmer contre DoD intégral) | Relecture de source officielle manquante : statut UNKNOWN, pas PASS « par défaut » | auto |
| T-V34-16-01 | V34-126 (candidat; lien à confirmer contre DoD intégral) | Fixture 80/50/30/10 → bbox 140×110, aire 13000 mm², 5 CUT/8 SCORE ; aucune auto-intersection du contour extérieur | auto |
| T-V34-16-02 | V34-127 (candidat; lien à confirmer contre DoD intégral) | Quatre fentes de 10 mm présentes, ouvertes et explicitement CUT ; aucun doublon exact ; jonctions de plis signalées mais non rejetées en bloc | auto |
| T-V34-16-03 | V34-127 (candidat; lien à confirmer contre DoD intégral) | `T=0`, `T=H`, NaN, Inf, cote négative ou manquante → refus sans mutation ni valeur cachée | auto/UI |
| T-V34-16-04 | V34-126 (candidat; lien à confirmer contre DoD intégral) | Carte 105×148 → développé 210×148, 1 CUT/1 SCORE ; pas de compatibilité tapis carte inventée | auto |
| T-V34-16-05 | V34-128 (candidat; lien à confirmer contre DoD intégral) | Changement de paramètre → nouvelle proposition et prévol invalidé ; source, masques float32 et projet V1 inchangés | auto |
| T-V34-16-06 | V34-127 (candidat; lien à confirmer contre DoD intégral) | Prévol export : mm/viewBox cohérents, chemins distincts, refus d'un doublon et d'une intersection non intentionnelle | auto |
| T-V34-16-07 | V34-128 (candidat; lien à confirmer contre DoD intégral) | Sans modèle IA, sans ComfyUI et sans format V2, le calcul/aperçu/export brouillon reste possible via un harness de test isolé | auto/intégration future |
| T-V34-16-08 | V34-128 (candidat; lien à confirmer contre DoD intégral) | UI novice : erreurs localisées, accès clavier, aucune mention « Score transmis » ou « prêt machine » avec profil UNKNOWN | UI/Windows |
| T-V34-16-09 | V34-128 (candidat; lien à confirmer contre DoD intégral) | Import réel : Score choisi, Attacher vérifié, dimensions relevées et changement d'outil consigné ; pas de PASS automatique | Design Space |
| T-V34-16-10 | V34-127 (candidat; lien à confirmer contre DoD intégral) | Coupon carton : coupe, plis, fentes, languettes et montage mesurés avec matière, outil, tapis, version et SHA exacts | physique |
| T-V34-17-01 | V34-129 (candidat; lien à confirmer contre DoD intégral) | Les quatre choix exportent des contrats distincts ; le SVG multicouche n'est jamais stocké sous `Artifact.use=editable_svg` V1 | auto |
| T-V34-17-02 | V34-129 (candidat; lien à confirmer contre DoD intégral) | Un PNG Print Then Cut conserve pixels/alpha/empreinte ; aucun SVG de diagnostic n'est automatiquement ajouté comme seconde coupe | auto |
| T-V34-17-03 | V34-129 (candidat; lien à confirmer contre DoD intégral) | Basic Cut refuse trou ambigu, contour ouvert non autorisé, double coupe, SVG actif et dimensions non physiques | auto |
| T-V34-17-04 | V34-129 (candidat; lien à confirmer contre DoD intégral) | SVG multicouche conserve ordre, groupes, repère mm et IDs ; aucune conversion silencieuse en SVG d'édition | auto |
| T-V34-17-05 | V34-129 (candidat; lien à confirmer contre DoD intégral) | SVG d'édition conserve styles/couches dans le profil autorisé ; pas de mention « Basic Cut prêt » | auto |
| T-V34-17-06 | V34-130 (candidat; lien à confirmer contre DoD intégral) | Fixture boîte 140×110 : 5 CUT/8 SCORE identifiés, guide « Score → Attacher → vérifier mm/outils » ; aucune opération transmise par SVG | auto/UI |
| T-V34-17-07 | V34-131 (candidat; lien à confirmer contre DoD intégral) | Stale SHA entre prévol et publication → refus sans mutation du projet ni remplacement d'un export antérieur | auto/concurrence |
| T-V34-17-08 | V34-131 (candidat; lien à confirmer contre DoD intégral) | Échec au 2e artefact d'un paquet → manifeste succès absent, ancien paquet intact, reprise sans écrasement | auto/fault-injection |
| T-V34-17-09 | V34-130 (candidat; lien à confirmer contre DoD intégral) | Guide A4 Explore 5 : paysage sur tapis, flèche haut-gauche, repères imprimés par Design Space, dimensions à confirmer | auto/UI |
| T-V34-17-10 | V34-130 (candidat; lien à confirmer contre DoD intégral) | Novice clavier : choisir chacun des quatre formats, voir avertissements et ouvrir résultat sans perte de focus | UI/Windows |
| T-V34-17-11 | V34-129 (candidat; lien à confirmer contre DoD intégral) | Import réel PNG Flat Graphic + SVG Basic/MultiCut : version Design Space, dimensions, calques et comportement constatés | DesignSpace |
| T-V34-17-12 | V34-130 (candidat; lien à confirmer contre DoD intégral) | Import réel boîte : Score et Attacher manuels, outil/matière et positions vérifiés, capture privée de preuve | DesignSpace |
| T-V34-17-13 | V34-131 (candidat; lien à confirmer contre DoD intégral) | Coupon Explore 5 : sticker et boîte testés, mesures et matière/outils/tapis/versions/SHA consignés | physique |

## Arbitrages transversaux et contre-expertise hostile

1. **Géométrie vs rendu** : un trou rendu par fill-rule n'est pas une coupe validée ; toute simplification qui supprime trou, îlot, antenne voulue ou change le nombre de passages doit rester proposition non mutante. XML valide ≠ SVG sûr ≠ SVG compatible Design Space. Rejeter DTD/XXE, scripts, références externes, coordonnées non finies, doublons CUT et budgets excessifs. Un seuil alpha diagnostique ne remplace jamais le contour accepté.
2. **Opérations vs couleur** : CUT, SCORE, DRAW, PRINT et FOIL sont des intentions typées, jamais inférées de la couleur SVG. PRINT_THEN_CUT est une recette composite, non une opération PATH. Une ligne SCORE ouverte est légitime ; un CUT ouvert non autorisé bloque. La traversée SCORE/CUT intentionnelle n'est pas une double coupe CUT/CUT.
3. **Profil vs réalité** : KNOWN_SUPPORTED requiert une combinaison exacte versionnée machine+outil+matière+support+preuve datée ; UNKNOWN ne devient pas PASS par choix utilisateur. Le brouillon peut sortir avec avertissement, pas un badge machine-ready. Les pages fabricant ne remplacent ni import DS ni mesure physique.
4. **Patron paramétrique** : fixture boîte 80/50/30/10 → 140×110 mm, 5 CUT/8 SCORE et 13000 mm² ; ces nombres sont des *oracles historiques de fixture*, pas des mesures de carton. Dimensions intérieures, épaisseur, fentes et intersections intentionnelles nécessitent vérification distincte. Aucun second moteur de géométrie ni de prévol.
5. **Quatre exports, quatre contrats** : PNG Print Then Cut (pixels/alpha), SVG Basic Cut (coupe simple), SVG CUT multicouche (ordre/groupes/IDs), SVG d'édition (objets/styles) ; un artefact V1 `editable_svg` ne devient pas multicouche CUT par renommage. Le guide Score→Attacher→vérifier mm/outils reste manuel. Ne pas créer de pilote machine.
6. **Transactions** : source SHA et génération revérifiés avant commit ; staging, publication exclusive et manifeste de livraison séparés de l'archive projet V1. Le CAS V1 ne constitue pas un receipt durable de commande V2 ; un ACK perdu ne justifie pas un retry aveugle. Undo/Redo seulement pour mutations acceptées, pas pour prévisualisation.

## Contrats de tests et micro-lots proposés (aucune exécution)

- **P0 géométrie** : fixtures anneau/trou/îlot, Bézier fermé, 5001 chemins, 50 objets, SVG hostile. Tests négatifs : XXE/script externe, auto-intersection CUT, perte de trou par simplification ; plus stale SHA, crash et OOM simulé. Mesurer latence p50/p95 et mémoire sur fixtures épinglées, sans résultat inventé.
- **P0 fabrication** : parseur d'assignations typées → résolveur tri-state → prévol → guide manuel. Négatifs : PRINT sur PATH, SCORE sur raster, support hétérogène dans un groupe, profil inconnu présenté à tort comme certifié. Annulation et collision concurrente sans mutation.
- **P0 exports** : quatre producteurs typés réutilisant ports existants ; sortie vers fichier externe no-clobber et relecture. Négatifs : SVG actif, chemin CUT ambigu, échec au deuxième artefact, ancien digest. Tests Windows clavier/DPI 200% et DS versionné sont des gates séparés.
- **P1 patrons** : générateur déterministe → prévol géométrique partagé → aperçu → confirmation → guide. Négatifs : NaN, épaisseur nulle ou supérieure à hauteur, fentes dupliquées, projet changé avant commit. Coupe et montage mesurés seulement avec coupon physique.

**UX** : un seul canevas et panneau contextuel, découverte novice puis détails experts, feedback de prévol localisé, correctif réversible et focus préservé ; état vide/pending/erreur explicite. 1366×768, DPI 200%, lecteur écran, contraste et motion réduit restent des recettes Windows à exécuter. **IA** : non requise dans ces cinq lots ; aucun téléchargement, aucun GPU obligatoire, repli manuel/CPU ; OOM simulé ne prouve pas RTX réelle. **Confidentialité** : pas de projet, image, modèle ou capture privée ajoutés au dépôt ; preuves DS/physiques doivent être expurgées.

## Vérification des 25 axes R3

01–05 : inventaires hérités 24/141/140/80/437 préservés, **non certifiés globalement** ; 101 assertions conservées ici sans suppression. 06 : statut conception uniquement. 07 : projet V1/CAS/float32 inchangé, V2 explicite. 08–09 : quatre exports et cinq opérations distincts. 10–12 : parcours, canevas, clavier/DPI conservés. 13 : stale/crash/Undo/concurrence explicités. 14 : IA facultative, pas d'admission de modèle dans ce lot. 15 : alpha/ICC hérités du lot12, non requalifiés ici. 16 : topologie/SVG sûr détaillés. 17 : patron traité ; bibliothèque/CSV hors périmètre de cette tranche, conservés lots19–20. 18 : Smart Delivery externe non modifié, contrat antérieur conservé. 19 : opportunités traitées dans leur clôture distincte, pas de nouveau doublon. 20 : mesures proposées, non réalisées. 21 : sécurité/licences/privacy précisées. 22 : branche documentaire seulement, pas de code ni merge. 23 : réutilisation des moteurs existants, ports HEAD à revalider. 24 : promotion interdite avant revue globale. 25 : aucune réduction du contrat de contrôle.

**Limites :** les 101 textes ont été relus et rapprochés à un propriétaire candidat, mais l'équivalence sémantique des critères V3.3 et des 140 DoD complets reste à auditer. Pas de test nouveau, pas de PASS Windows/GPU/Design Space/physique. **Suite unique SC-02E :** assertions lots18–22 (56 lignes), puis jugement individuel des lots02–06 et revue exhaustive des 141 critères/140 DoD.
