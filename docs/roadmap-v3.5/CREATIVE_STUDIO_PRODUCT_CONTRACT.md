# SmartSVG — studio créatif, édition réversible et fabrication guidée

**15 novembre 2026 — approfondissement candidat autorisé, pas produit livré.** Base candidate `1fde26bbf3217b3b3a7cf75f8d33c98a3a8439b9`, main observé `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`. Ce contrat concrétise la vision propriétaire : réunir les bonnes idées de l'édition d'image et du vectoriel, les améliorer pour gagner du temps et obtenir principalement des SVG propres pour Cricut. Il complète [le maître](MASTER_PRIORISE.md), [la composition](ADR_COMPOSITION_PERSISTENCE.md), [les arbitrages](DECISIONS_TRANSVERSALES.md) et [Décomposer une scène](SCENE_DECOMPOSITION_AND_RELIEF_CONTRACT.md). Les choix ci-dessous sont ceux du producteur sous carte blanche, pas des préférences techniques attribuées rétroactivement à l'utilisateur.

## 1. Identité et décisions de produit

**Résultat visé : image ou idée → éléments compréhensibles → création modifiable → sorties adaptées à l'usage → fabrication guidée.** La qualité finale, le temps de correction et la reprise du travail définissent la valeur ; le nombre de boutons et la présence d'un modèle IA ne démontrent pas une supériorité.

Le studio créatif est le cœur de l'expérience. Smart Delivery conserve son rôle de première tranche de livraison P1 utile dès un export sain, sans devenir un prérequis à la sélection/édition ni la seule identité du logiciel. Les obligations sources et leurs priorités restent intégrales ; cet approfondissement ne renumérote ni les80UX, ni les140tickets, ni les437assertions et ne remplace aucune idée retenue/rejetée.

| Approche | Décision et raison |
|---|---|
| Collection de fonctions IA indépendantes et de fenêtres par outil | Écartée : ruptures de contexte, doublons de masques et perte de contrôle. Garder une session, un canevas, une barre contextuelle et le même projet. |
| Studio guidé par intention, gestes directs et propositions révisables | **Retenue** : sélectionner/corriger/composer reste manuel et local ; assistance ciblée et parcours de fabrication utilisent les mêmes objets. |
| Refaire toute la mise en page généraliste ou toute la retouche photo avant la création Cricut | Écartée comme ordre de livraison. Les outils servent d'abord une pièce, un motif, une planche, un gabarit ou un relief ; le SVG standard permet d'autres usages ultérieurs sans annoncer leur qualification matérielle. |

## 2. Cinq expériences qui doivent fonctionner ensemble

| Parcours et capacités existantes | Interaction et gain recherché | Contrat de sortie / critère utile |
|---|---|---|
| **Comprendre et sélectionner** — A02–A05, B03, D01–03, SCN1 | Entourer grossièrement un personnage, ajouter un accessoire, exclure le fond, corriger localement. Les fragments d'un même objet restent groupables ; aucune obligation de peindre chaque pixel. | Masques proposés vérifiés, zones incertaines visibles, source/IDs préservés, édition manuelle toujours possible. Assistance P1 à qualifier, pas reconnaissance universelle acquise. |
| **Transformer et recomposer** — B01–B08/B14, SCN2–4 | Déplacer les pièces d'une scène, recolorer, aligner, dupliquer, changer l'ordre ou choisir une planche/relief, sans aplatir le travail rééditable. | Scène CP3 et correspondance scène/planche conservées au save/reopen ; parties cachées inconnues par défaut, reconstruction séparée opt-in. Articulation/warp avancés restent P2, pas faux simple affine. |
| **Affiner sans recommencer** — A07–A16, B09–B12 | Ajuster un contour/offset ou une simplification et revenir à leurs paramètres ; comparer fidèle/équilibré/facile, protéger les détails utiles, garder le texte original. | Dérivés liés à leur source, paramètres/rôle/version/provenance explicites, base inchangée ; contrat paramétrique §4 avant toute persistance. Le SVG d'édition et le projet ne sont pas remplacés par le PNG d'aperçu. |
| **Préparer selon l'usage** — C01–C11, W03/W04/W07/W08 | Choisir sticker imprimé, silhouette vinyle, multicouche, dessin ou pièces papier ; voir taille réelle et problèmes localisés, corriger l'élément concerné. | Bon rôle d'export, mm confirmés, opérations/profil/QA séparés. PNG Print Then Cut ne force pas une vectorisation photographique ; prévol local distinct de DS et coupe. |
| **Réutiliser et produire** — C12–C17, D10/D11, E01–E03, W12 et SD | Réutiliser une recette, modifier des noms/quantités, conserver les placements verrouillés, reprendre uniquement les erreurs, fournir pièces et guide cohérents. | Quantités/identités/cotes préservées, état par unité, PARTIAL honnête et fichiers sains conservés ; ZIP vérifié sans nouveau writer/queue/exporteur. |

Ces cinq parcours sont des usages partagés, pas cinq nouveaux moteurs ou tickets. Les outils texte/gabarits/OCR/diorama hérités restent obligatoires selon leurs critères propres, même lorsqu'un premier parcours ne les utilise pas.

## 3. Expérience continue, intention explicite et retours utiles

**Novice :** Importer → choisir une intention → sélectionner/corriger → composer → contrôler la taille et les alertes → exporter. On peut changer d'intention sans perdre la source ni les corrections ; les paramètres qui ne se transposent pas sont listés, jamais convertis silencieusement. **Expert :** les mêmes objets, plus inspection des courbes, géométrie, paramètres, variantes, provenance et profils.

Le même canevas permet de basculer entre apparence, opérations de fabrication et planche ; les vues Original/Composition/Planche de SCN restent les vues du même projet. Pas de seconde version autoritaire du dessin pour la vue « découpe ». Un survol/zoom/changement de vue n'écrit rien et ne remplace pas un masque accepté.

Une petite action réversible donne un retour immédiat et un groupe Undo logique : un drag, un changement de paramètre validé ou une acceptation de proposition. Pas de popup à chaque point de courbe ou lettre. Le calcul coûteux montre aperçu/progression/annulation ; migration, remplacement de police, perte d'éditabilité et publication externe gardent les confirmations proportionnées déjà prévues. Les commandes suivent le format actif et sa politique de sauvegarde ; aucune mutation ou sauvegarde n'est déclarée sur simple résultat asynchrone.

Pendant un curseur de réglage, seule la dernière génération d'aperçu reste applicable. Valeur provisoire visible, état « calcul en cours » puis « aperçu à confirmer » selon l'opération ; libérer le curseur ne déclenche pas un export. Une acceptation = paramètres/digest du rendu effectivement montré, pas les valeurs d'une requête plus récente. Annuler ou fermer le panneau rend la sélection/focus précédents sans retirer un fichier déjà publié.

Une alerte indique **où, pourquoi et quoi faire** : sélectionner le défaut dans l'objet/liste, voir sa taille mesurée, proposer correction sur copie ou conservation de l'intention. Gravité et réparation dépendent du rôle : un détail volontairement ajouré n'est pas forcément une erreur. Une tolérance matière inconnue donne UNKNOWN avec une demande utile ; aucun seuil universel ni score « 100% prêt Cricut ». Le parcours ne demande jamais d'inventer une cote, un matériau ou une licence pour continuer.

Clavier/liste en alternative au drag, focus restitué après correction, lecteur d'écran, contraste/mouvement réduit et écrans/échelles historiques conservés. D08 garde le benchmark Tk/Qt/Tauri avant gros éditeur ; le contrat n'installe ni framework ni moteur IA. Les moteurs sans UI peuvent avancer pendant ce benchmark.

## 4. Réglages liés à la source : offset et simplification réellement rééditables

**Ajout précis à la conception :** un offset ne doit pas devenir seulement une forme définitivement détachée du motif. Après fermeture/réouverture, l'utilisateur peut retrouver sa distance, le modifier, le désactiver ou revenir au contour de base. Même principe pour une simplification déterministe qualifiée. Cela précise les capacités existantes A15/C01/B01 et les variantes, sans prétendre que leur persistance paramétrique existe déjà.

Le premier périmètre couvre **offset en mm** puis **simplification de chemins** avec protection explicite des trous/îlots. Le nettoyage de masque conserve ses commandes/patches existants ; recoloration et effets texte suivent leurs contrats propres. Perspective, articulation, génération et retouche raster arbitraire ne sont pas admises par ce premier mécanisme.

### 4.1. Contrat logique proposé, pas API main

`CreativeProjectionRecipe/1-draft`, ressource du projet V2, référence :

- `recipe_id`, `target_node_id`, `purpose_role`, version de schéma et de sérialisation ;
- entrée canonique du nœud **avant** la recette : source/géométrie/masque digests et transformation monde ;
- opérations ordonnées à liste fermée, `operation_id`, type/version, paramètres typés et unités, détails protégés par références géométriques stables ;
- mode `LIVE` (suit les entrées du nœud) ou `FROZEN_VARIANT` (révision/ressources épinglées, ne se met pas à jour implicitement) ;
- diagnostics, provenance des moteurs et références de ressources nécessaires à Undo/reproduction ; profils/paramètres de rôle et politique QA dans le contexte d'évaluation.

Les références aux nœuds/ressources se valident avant publication ; cycle, entrée absente, type inconnu, NaN/Inf, unité incompatible ou budget dépassé = refus explicite. Une recette ne contient ni code/script, ni expression évaluée, ni URL d'installation, ni commande de fichiers/réseau. Le plan s'exécute via les opérateurs déterministes admis, pas un langage de programmation général.

Si une entrée LIVE change et que la correspondance d'un trou/îlot protégé n'est plus démontrable, résultat NEEDS_REVIEW et dérivé non publiable comme courant. Conserver la protection et demander de désigner explicitement le détail ; ni index, ni proximité géométrique ne réaffectent automatiquement son identité. Les ressources et l'ancien résultat restent disponibles pour comparer, sans recycler leur ancien QA au nouveau dessin.

Le verrouillage propre ou hérité défini dans l'ADR s'applique aussi aux recettes : changer une recette ou l'appliquer ne permet pas de modifier indirectement un descendant verrouillé. Refuser le groupe concerné sans application silencieuse au sous-ensemble ; aperçu non mutant et sélection explicite des cibles autorisées restent possibles. Déverrouiller demeure une action explicite, pas l'effet d'un calcul.

Le nœud conserve la géométrie et la transformation canoniques ; la recette décrit seulement la projection dérivée. Une entrée peut désigner la base d'un nœud, jamais se nourrir de sa propre sortie calculée. Les dépendances inter-objets sont acycliques et explicites ; le premier incrément peut refuser les dépendances non supportées avec diagnostic, pas les aplatir silencieusement. Graphe/profondeur/coût bornés sont fixés en CP0-CST avant moteur/writer.

### 4.2. Ordre, unités et recalcul

Pour ce premier contrat, les opérations de fabrication sont évaluées **après la transformation monde du motif, en millimètres physiques confirmés**, puis placées sur la page. La marge demandée en mm ne change donc pas implicitement quand on redimensionne le motif ; si l'utilisateur veut une marge proportionnelle, ce sera une opération distincte nommée/versionnée, pas une ambiguïté de la même option.

Fixture proposée : disque de base rayon10mm, motif agrandi×2, offset extérieur1mm → rayon21mm et diamètre42mm. Modifier offset à2mm → rayon22mm. Une translation ne change ni rayon ni marge ; rotation/nesting rigide ne redimensionnent pas. Tester aussi trous et contours intérieurs, auto-intersections, offsets négatifs et fermeture complète d'une forme. Le changement topologique volontaire suit D01 : diff visible et intention acceptée ; un détail protégé n'est jamais supprimé silencieusement.

Modification d'une entrée LIVE → dérivés affectés STALE, recalcul borné depuis les opérateurs existants et nouveau prévol. Les sorties saines déjà livrées restent historiques et ne sont pas réécrites. Déplacer une pièce, changer l'échelle, le masque, la fonte, le rôle, le profil ou l'algorithme invalide les dépendances appropriées ; la clé comprend leurs digests et versions. Le cache est reconstruisible, ne devient pas le maître des paramètres ni des ressources. Version de moteur absente/incompatible au reopen = paramètres conservés et rendu à revoir, jamais remplacement invisible par le moteur « le plus récent ».

Une variante gelée conserve ses entrées ; la mettre à jour est un choix explicite avec diff et Undo. « Convertir en géométrie fixe » crée un résultat dérivé clairement nommé avec provenance et avertissement de perte de réglage sur cette copie ; l'original rééditable reste conservé. Un chemin SVG exporté n'est pas une sauvegarde complète de la recette.

### 4.3. Persistance et transaction

CP0-CST fixe schéma strict/champs/quotas/erreurs, ressources et sérialisation canonique avant écriture ; CP1 lit/planifie ; CP2 publie copie V2/ressources/receipt ; CP3 et capacités CP5 utilisées exposent édition et reprise. Aucun champ clandestin dans V1/strokes/operations, aucun JSON annexe maître, deuxième writer, exporteur ou historique. V1 permet des previews/exports externes explicitement non paramétriques et non sauvegardés ; cela ne satisfait pas le DoD rééditable.

Le nouveau contrat précise l'ADR, sans modifier un schéma produit par documentation. L'activation du writer/format et tout moteur/dépendance restent soumis aux micro-lots et validations applicables. CAS V1≠receipt durable ; groupe de commandes accepté, replay et UNKNOWN suivent CP2/D03/D04. L'effacement du cache ne perd pas les recettes ; Undo restaure leurs paramètres, entrées et ressources nécessaires. Le quota d'historique et les purges restent explicites, pas d'éviction silencieuse qui casserait un retour arrière annoncé.

## 5. Intention, qualité et quatre exports

| Intention utilisateur | Projection et vérification attendues |
|---|---|
| Sticker imprimé | PNG Print Then Cut, couleurs/alpha/bleed et dimensions/ppi cohérents ; contour propre adapté, aucune génération de repères capteur. Une photo n'est pas inutilement vectorisée pour conserver ses couleurs. |
| Silhouette vinyle | SVG Basic Cut, vrais chemins/topologie/mm et simplification préservant les détails choisis ; pas de raster enveloppé nommé vecteur. |
| Découpe multicouche | SVG CUT multicouche, palette/couches/alignement/opérations/miroir HTV explicites ; une couleur n'assigne jamais CUT par elle-même. |
| Création réutilisable | SVG d'édition avec capacités annoncées, projet `.smartsvg` pour sémantique non portable ; texte non aplati silencieusement et recette non promise portable par simple SVG. |
| Pièces de collage ou relief | Réutilise SCN pour éléments, planche et montage ; export approprié à chaque pièce, guide et quantités cohérents. Prévisualisation 2.5D n'est pas preuve d'assemblage. |

Les cinq intentions ne créent pas cinq formats : les quatre rôles restent distincts. Un jeu de variantes compare apparence, géométrie et fabrication séparément, sur la même base et à la même taille. Pas de meilleur choix fabriqué par un score unique, de certification machine par la géométrie seule, ni de contrôle Cricut privé.

## 6. IA à effort ciblé et contrôle utilisateur

Proposer des masques/objets, affinages, variantes et réparations localisées avec source/révision et limites. Distinguer résultat déterministe, heuristique et modèle réellement exécuté ; aucun score de confiance non calibré. La reconstruction de zones cachées SCN reste une proposition distincte, jamais des pixels « retrouvés ». Modèle absent/refusé = voie manuelle et diagnostic, pas blocage de tout le projet ni téléchargement automatique.

Choix modèle/version/hash/licence/provenance fiable, consentements téléchargement/exécution/transfert distincts, budgets CPU/RAM/VRAM et OOM/annulation avant usage. Ne pas supposer qu'un modèle tient sur RTX3070 8Go ou qu'une génération conserve exactement le dessin ; mesurer sur le vrai environnement. L'IA n'autorise ni commandes, ni écriture projet/export, ni modification de contraintes protégées. Les contrôles géométriques/publication passent par les mêmes ports déterministes.

## 7. Livraison progressive et premiers résultats observables

| Incrément de conception | Réemploi / dépendance | Premier résultat et limite de clôture |
|---|---|---|
| CST0 — règles et fixtures | W02/W03/W07 ; CP0 pour ressources, ports actuels et contrats SCN/ADR | Schémas stricts proposés, opérateurs admis, unités/erreurs/quotas, trois fixtures géométriques et quatre parcours §8 ; inventorier les signatures et le runner réel avant implémentation. |
| CST1 — geste créatif cohérent | Sélection/preview native W02, SCN1, UI W13 | Même objet sélection/correction/avant-après ; premières intentions et alertes actionnables, clavier et voie manuelle. Pas de dépendance globale au gros éditeur ou à l'IA. |
| CST2 — première opération paramétrique | Offset déterministe W03/W07, CST0 ; CP0–3 pour réglage durable | Aperçu source→offset en mm puis changement de taille et recalcul, acceptation/Undo, save/reopen rééditable après CP2/3 qualifiés. Export externe possible plus tôt, jamais compté comme persistance. |
| CST3 — simplification/variantes et qualité | Géométrie W03/W07, protections D01, CST2 ; CP5 seulement pour texte/effets utilisés | Paramètres retrouvables, détails protégés, variantes gelées/live explicites ; prévol invalidé/recalculé. Aucun moteur général de déformation imposé au premier offset. |
| CST4 — répétition et comparaison d'usage | W12 et SD existants ; données/exports réels | Recette appliquée à des entrées compatibles, reprise par unité et livraison vérifiée ; gain observé séparé de disponibilité technique. Le batch de base ne dépend pas du partage P2 enrichi. |

CST est un découpage de réalisation à l'intérieur des responsabilités existantes, pas cinq nouveaux tickets/moteurs ni changement des priorités sources. Le noyau sélection/qualité reste au premier plan ; texte/gabarits P1 et autres obligations héritées ne sont pas repoussés par cet ajout. Smart Delivery mono-export avance indépendamment ; scène rééditable, paramètres et créativité avancée suivent leurs dépendances précises. Effort/risque qualitatifs : moyen pour gestes/alertes, élevé pour migration/recettes paramétriques et validation UI ; aucun délai ou gain promis sans prototype.

## 8. Recettes proposées et preuve de valeur

Nouveaux IDs **T-V35-CST**, distincts des437historiques et17SCN. Tous tests produit proposés ci-dessous sont **NOT_RUN** ; ce document n'ajoute aucun code de test exécuté.

| ID | Oracle discriminant |
|---|---|
| T-V35-CST-01 | Même objet après clic/lasso/correction, zoom/pan et réordre ; identité et source stables, affichage ne mutent pas le projet. |
| T-V35-CST-02 | Disque rayon10mm, scale2, offset1mm→rayon21mm ; changer offset2→22mm ; translation/rotation rigide sans changement d'épaisseur. Échelle physique inconnue bloque export de fabrication. |
| T-V35-CST-03 | Offset/simplification avec trou protégé : disparition refusée ; changement topologique volontaire annoncé, protégé déverrouillé explicitement puis nouveau prévol, aucune perte silencieuse. |
| T-V35-CST-04 | Save/reopen CP2/3 puis régler de nouveau distance/tolérance, désactiver opération et Undo : paramètres/ressources/base retrouvés, cache supprimé sans perte. |
| T-V35-CST-05 | Ancien job d'aperçu après changement de paramètres, de source ou de session : STALE non appliqué ; accepter référence le digest du rendu montré et jamais un rendu absent. |
| T-V35-CST-06 | Modifier masque, échelle, fonte ou profil : invalidation des dépendances ; variante gelée non mise à jour automatiquement ; ancien export conservé et nommé historique. Correspondance d'un détail protégé devenue ambiguë : NEEDS_REVIEW, aucune réaffectation par index/proximité, ancien QA non recyclé. |
| T-V35-CST-07 | Cycle, ressource absente, opération/version inconnue, NaN/Inf ou dépassement de coût/profondeur : refus borné, aucun appel arbitraire ni aplatissage caché. |
| T-V35-CST-08 | Moteur/version manquant au reopen : recette conservée, rendu à revoir ; aucun changement invisible des courbes ou export sur ancien QA. |
| T-V35-CST-09 | Passer PNG PTC→Basic Cut→multicouche→édition : source/corrections conservées, différences listées et quatre QA distinctes ; aucun quatrième Artifact.use V1 ni fausse vectorisation. |
| T-V35-CST-10 | Défaut localisé : action clavier rejoint le bon objet, message explique correction ; seuil matière inconnu reste UNKNOWN, pas score de fabricabilité inventé. Appliquer une recette au groupe avec descendant locked : aucune mutation indirecte ni application partielle silencieuse ; preview reste non mutante. |
| T-V35-CST-11 | Acceptation, conflit CAS, perteACK, primaire publié/backup échoué et disque plein : transaction/receipt CP2 réconciliés, aucune réapplication aveugle, pas d'Undo d'un fichier livré. |
| T-V35-CST-12 | Modèle absent/OOM/refus/annulation : source intacte, pas de réseau implicite, manuel disponible ; résultat généré signalé, moteur déterministe seul ne revendique pas inférence. |
| T-V35-CST-13 | Régler via clavier/liste à1366×768 et DPI200%, focus/lecteur d'écran, annulation et retour : mêmes capacités que souris, pas popup systématique ni retour de focus perdu. |
| T-V35-CST-14 | Recette versionnée externe avec script/URL/chemin privé/licence inconnue : admission fermée, aucune exécution ; copie de livraison expurgée, original privé intact. |

**Quatre parcours de comparaison, futures fixtures synthétiques autorisées :** planche12motifs→stickers ; scène6éléments SCN→pièces/collage ; illustration avec trou fin→vinyle à deux tailles ; texte étiquette→changement de nom/taille puis export. Comparer même source, taille physique, objectif et environnement, avec voie manuelle puis assistée. Le protocole peut inclure d'autres logiciels mais ne présume ni leur incapacité ni un temps de référence.

Relever temps actif total, nombre d'actions/corrections/retours entre outils, réussite de reprise et d'import, erreur mm, nœuds/fragments/topologie, qualité visuelle, matière perdue si placement comparable. Inclure l'échec, les relances IA et corrections manuelles dans le temps total ; déclarer l'expérience de l'opérateur et l'ordre des essais. p50/p90/p95/max, RSS/VRAM par taille/corpus ; novice et régulier, observations humaines héritées conservées. Tolérances et critères de fixture sont fixés avant les essais, aucune réduction pour faire passer le résultat. Design Space, coupe et montage mesurés sont des axes séparés. Aucun « x fois plus rapide/meilleur » sans ces relevés.

## 9. Raccordement, revue et limites

Ports existants réemployés : ceux de SCN§7 (source/masques/identités/preview/strokes/workspace), les exporteurs/QA W03, géométrie W07, placement W12, publication SD. Les noms de recettes et opérations sont proposés ; leur implémentation doit lire les signatures et les consommateurs au HEAD, pas inventer un module déjà disponible. Aucun nouveau bus, stockage maître, provider IA, moteur de nesting ou exporteur autorisé par cette fiche.

Les25axes restent applicables : 01–05 inventaires hérités inchangés et CST séparés ;06 statuts disjoints ;07 autorité/source/float32/CP2 ;08–09 quatre sorties/opérations/profils ;10–12 intention/gestes/accessibilité ;13 annulation/STALE/recovery ;14 IA opt-in ;15 raster et résolution ;16 géométrie/mm/topologie ;17 séries/gabarits/SCN ;18 SD consommateur ;19 opportunités et rejets conservés ;20 mesures sans promesse ;21 sécurité/licences/privacy ;22 WIP/autorité ;23 réemploi sans doublon ;24 contre-revue de ce delta avant intégration ;25 aucun critère raccourci. Les sources V3.3/V3.4 et anciens rapports ne sont pas réécrits.

Le rapport global antérieur reste borné à son SHA ; le présent approfondissement requiert sa revue de delta et doit être joint à la PR documentaire consolidée. V3.4 active, aucune adoption ni opt-in de fusion transmis. Rollback futur : désactiver une opération/entrée non qualifiée sans perdre sources/recettes, conserver les variantes connues, revenir au V1 conservé plutôt qu'écraser un V2 ; rollback documentaire par delta revu, archives intactes. Prochaine exécution : consommer RUN_STATE et cette fiche, pas recommencer un inventaire ou ajouter une liste d'idées sans résultat observable.
