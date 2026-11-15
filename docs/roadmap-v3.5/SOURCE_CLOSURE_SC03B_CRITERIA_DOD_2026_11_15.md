# SC-03B — Transfert des critères complets et conditions de fin

15 novembre 2026. Base candidate `a14667dbeb398fe82d6d801f890d430b50b67ade`, main `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`. **Travail de transfert documentaire du producteur ; validation indépendante finale du contexte encore à terminer.** V3.4 reste active ; aucun code produit modifié et aucun nouveau test produit exécuté. Ce rapport remplace la prochaine action de SC-03A : les dix premiers intitulés ne sont plus une nouvelle boucle de dix audits.

## Résultat utilisable par le producteur

[SOURCE_TRANSFER_REGISTER.json](SOURCE_TRANSFER_REGISTER.json) contient 141 entrées de critères et 140 lignes complètes de tickets V34. Pour chaque exigence : dossier littéral, lignes d'acceptation historiques, chemin/ligne/blob, liens de planification qualifiés, décision individuelle, précision de transfert et renvois aux consommateurs V3.5. Pour chaque ticket : ligne complète incluant dépendances, livrable, recettes, preuve, DoD et rollback lorsqu'ils figurent dans sa table, avec source intégrale conservée.

**Les sections parentes et clauses communes restent intégralement obligatoires.** Les extraits ne remplacent jamais MASTER/HERITAGE/TRACEABILITY/COVERAGE V3.3 ni les 24 lots V3.4. Les 314 liens du lot23 sont des points d'entrée de planification/coordination, parfois partiels ; ils ne déclarent ni propriétaire d'implémentation exclusif ni DoD déjà satisfait. Les dix exigences sans V34 direct gardent cette absence historique et ont leurs propriétaires W10/W11/W16, avec CP4/CP6 comme gates distincts. Aucun nouvel ID W16_OCR ou W16_DIORAMA n'est créé.

Le registre est un index de lecture vérifié, pas une seconde autorité de produit et pas un journal d'implémentation. Tous les états produit restent NOT_EVALUATED. Son intégrité est vérifiée par [verify_source_transfer.py](verify_source_transfer.py), qui ne certifie ni le sens de chaque paragraphe ni le fonctionnement du logiciel.

```bash
python docs/roadmap-v3.5/verify_source_transfer.py --main-root .
python docs/roadmap-v3.5/verify_source_transfer.py --main-root . --id S-036
python docs/roadmap-v3.5/verify_source_transfer.py --main-root . --id V34-033
```

La requête par ID retourne les critères et tickets reliés avec leur texte complet ; les contraintes communes ci-dessous et la section source restent à lire pour le lot affecté. Cela permet au prochain run de retrouver l'exigence sans reconstruire tout le contexte ni redéduire des propriétaires depuis un titre.

## Critères transversaux rétablis explicitement

Lecture du producteur : 101 dossiers S, 40 clauses R33 du maître, tables d'acceptation historiques, familles F01–F15, gates G0–G9, contrats projet/géométrie/mesures§29–32, UX§36–41 et matrice de couverture V3.3 ; tableaux complets des 140 tickets et leurs recettes/conditions communes de lot. Le périmètre de la contre-expertise reçue est précisé dans REVIEW_SOURCE_TRANSFER_2026_11_15.md : pas de revendication de seconde lecture exhaustive de chaque paragraphe contextuel.

| Source et exigence | Condition complète qui continue à s'appliquer | Raccord V3.5 et contre-exemple interdit |
|---|---|---|
| Héritage§29/G1.3 ; S-003/024/026/053 | Créer, 15 opérations avec trois Undo/Redo, fermer/crash, rouvrir exactement positions/masques/textes/accessoires ; migration ancienne et archive hostile | CP1/CP2/CP3/CP4. Sauver une image aplatie ou mesurer seulement SHA source ne satisfait pas le round-trip éditable. |
| Héritage§4 ; S-002/R33-008 | Quatre exports et projet reproductible comme produit distinct | PNG PTC, Basic Cut, CUT multicouche, SVG éditable ; .smartsvg n'est ni un cinquième export de coupe ni un ZIP Delivery. |
| HéritageG0.3/G3 et S-005/006/027/050 | Neuf cas annotés, grille partagée, fournisseurs réellement exécutés sur machine cible ; G3.2 trois cas distincts | CPU/manual toujours disponible mais aucune preuve GPU déduite de ce repli ; licence/version/hash admis avant essai. |
| HéritageG4.3–G4.5 ; S-010/031/055 | Coupon impression/coupe ; trois parcours sticker/silhouette/planche, trois matières courantes pour recette déclarée | Prévol, import DS, impression et coupe mesurée restent des niveaux distincts. Ne pas cocher terrain depuis manifeste. |
| HéritageG5.4/G5.6 ; S-011/032/033/034 | Formes modifiables dans l'Atelier et un éditeur externe, comparaisons indépendantes et prototype multicouche assemblé | Fidélité couleur/traits/topologie mesurée séparément de fabricabilité. Contour seul ne satisfait pas l'édition multicouche. |
| HéritageG6.3/G6.4 ; S-035/036/037/064/088/092 | Texte éditable dans projet, fonte absente avertie ; étiquette, topper et carte sauvés/repris, au moins un prototype fabriqué par usage déclaré | W10/W11 + CP4/CP6. Patrons carte/boîte existants ne prouvent pas les trois gabarits métiers. |
| HéritageG7 ; S-038/039/062/089 | 50 unités, interruption/reprise sans doublon ; 30 variantes CSV contrôlées ; une erreur conserve49résultats | D04 traite INTERRUPTED/CANCELLED/NEEDS_REVIEW ; ni relancer toutes les réussites ni se limiter aux seuls FAILED dans tous les cas. |
| HéritageF10/G7 ; S-041/091/098 | Recherche, duplication, archivage, projet portable et droits visibles ; réouverture sur autre installation | Index jetable, préférences durables ; « local à cet ordinateur » est une tranche annoncée, pas achèvement de la portabilité. |
| Héritage§30 et F06 ; S-030/056 | Coordonnées source/document/fabrication séparées, transformations vérifiables, extérieur Basic Cut fermé | Les fentes ouvertes CUT de patrons sont des exceptions typées approuvées et prévolées ; pas autorisation générale de chemins ouverts Basic Cut. |
| Héritage§31 ; S-033/060/065 | Échantillon/corpus/version/rendu fixés ; silhouette, couleur, topologie, impression et fabrication séparées | Seuils de qualité conditionnels au corpus validé ; ni IoU universel ni score composite de qualification. |
| Couverture§11 ; S-096/R33-017/026 | Publier p50, p90, maximum, taille d'entrée et environnement ; mesures par phase et fournisseur | p95 et RSS/VRAM complètent ces valeurs ; ne pas remplacer p90 historique par p95 seul. |
| Héritage§40 et lots07/08 | Cibles initiales clic150ms médian, pan/zoom30fps, étatjob250ms ; navigation/règles p95<150ms sur100cas dans lots V34 | Ce sont des protocoles/conditions de qualification distincts, non résultats acquis. Révision de cible exige décision, pas omission. |
| Héritage§40.2 ; S-068/072/077/078/094 | 1366×768/1920×1080, zoom125/150%, petits écrans, lecteur écran, drag alternatif, cibles confortables et référentiel applicable | 1280×720/200% V34 complémentaires. Viser32px quand possible ; minimum24×24CSSpx ou exception web définie, selon applicabilité au framework. |
| Héritage§40.3 ; S-093/R33-039 | Observer au moins trois parcours fréquents et deux erreurs, novice/régulier, données anonymisées et minimales | Le test V34 de cinq novices dont au moins quatre comprennent les états est conservé séparément ; aucune réussite déduite d'une maquette. |
| MaîtreV3.3§8/Couverture§13 ; R33-021/038 | Neuf/update/rollback/désinstallation ; droits limités, Unicode/espaces, antivirus, port occupé, version dépendance/transport et offline | Portable actuel ≠ updater. Aucun projet ni modèle utilisateur supprimé par défaut ; compatibilité legacy toujours éprouvée. |
| Lot06 ; R33-011/014/025 | Receipts/epoch, replay avant contrôle stale, plafonds, digest logique non circulaire ; crash après publication inspectable | CASV1 seul ne vaut pas exactly-once ; CP2/V2 qualifié pour les nouveaux contrats durables. |
| Lot20 et D03–D05 ; R33-010/031/032 | États et rapports par unité, succès partiels, préférences durables et index reconstructible | Fichier et ZIP atomiques ; batch PARTIAL peut garder ses sorties saines, aucune annulation de succès externe par Undo. |
| HéritageG9 ; S-020/044/045/047/048/066/099 | Diorama quatre plans et assemblage/tolérances ; vinyle/HTV superposition/miroir ; OCR vérifié ; audit de détails IA inventés | Ces obligations restent conservées avec leur priorité source ; P2 n'est pas synonyme de fonction supprimable ou de simple étude facultative. |
| R33-024/028/030/034/035 | Droits/provenance, médias privés hors dépôt, consentements, preuve au SHA/environnement et validation humaine du matériel | Hash≠signature ; fichier et hash tous deux remplacés sans provenance fiable n'établissent pas authenticité. |
| HéritageG8 ; R33-040 | Gel fonctionnel, aucun P0 ni P1 bloquant et matrice de compatibilité avant stable | Adoption de roadmap ne qualifie pas un logiciel stable ; les capacités futures gardent leur statut explicite. |

## Réparation des fiches horaires de scénarios

La contre-expertise a vérifié la conservation littérale des259assertions des fiches SC-02D/E/F1/F2, mais relevé des oracles ajoutés incohérents. Ce défaut est corrigé au niveau de la couche d'interprétation :

- SC-02E et SC-02F2 : 106 oracles reprennent désormais les conditions propres à leur assertion intégrale, avec précisions pour epoch/receipt, float32, diagnostic expurgé, verrous, format, préférences et environnement Windows. Les colonnes sources/niveaux de preuve ne changent pas.
- SC-02E : suppression de « aucune publication partielle » appliquée à tous les lots ; atomicité fichier/ZIP et batch PARTIAL explicitement distingués. Reprise D04 et préférences D05 rétablies.
- SC-02F1 : catégories génériques déclarées comme catégories, jamais propriétaires. AST/ESM148/30 est un contrôle de graphe au snapshot déclaré, pas un test recovery.
- SC-02D : IDs V34 normalisés sur trois chiffres ; absence de lien historique n'est pas fabriquée par cette normalisation.

Les textes complets des437assertions et les exceptions restent conservés dans les sources et inventaires. Le rapprochement individuel de SC-02B/C et des fiches corrigées couvre le transfert de leurs recettes ; aucun de ces scénarios n'est déclaré exécuté par cette campagne.

## Contrôles réellement exécutés et limites de clôture

Le contrôleur de transfert vérifie les26blobs source, les lignes littérales, les ensembles141/140, les liens de planification et les références candidates ; requête par ID disponible après validation. Six corruptions adversariales (suppression exigence/ticket/pin, ligne source altérée, propriétaire inventé, faux état produit PASS) ont été refusées. Les contrôles de priorité et de reprise restent complémentaires. Ce sont des contrôles documentaires ; pas des tests du studio.

Les empreintes sont comparées au répertoire source fourni et au manifeste du registre. Ce manifeste n'est pas signé ; le contrôleur ne prouve pas que le SHA main déclaré est le HEAD actuel. Le producteur a vérifié les26blobs contre l'arbre GitHub de la candidate observée ; relire main/branche via API avant promotion. La règle textuelle de préservation est figée par le schéma du contrôleur, mais la justesse de son application reste une appréciation humaine.

**Suite finie :** contre-expertise des106oracles corrigés et du registre/contrôleur, acceptation de SC-03 au contexte intégral conservé, puis GLOBAL_REVIEW des25axes/gates au SHA fixé. Si la portée de la seconde lecture est limitée, l'écrire et conserver le point ouvert ; ne pas continuer une série SC-03 par lots arbitraires de dix intitulés, ni marquer DONE par comptage.
