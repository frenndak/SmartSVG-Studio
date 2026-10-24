# SmartSVG Studio — Contre-expertise multi-passes V21.0 → V21.1

**Date : 23 octobre 2026**  
**Périmètre :** archive V21.0 fournie, moteurs historiques V8–V20.6, code V21, chemin Cricut, images réelles et nouvelle interface Express.  
**Nature :** revue statique + essais reproductibles CPU + tests d’intégration. **Ce n’est pas une certification Cricut/GPU.**

## Passe 1 — Reproduction, architecture et compatibilité

- Extraction du projet réel : extension Python, 88 workflows historiques, 31 batteries de tests historiques, V21 et son chemin simplifié.
- `verify_package_v21.py` **459/459 tests réussis** sur la source précédente.
- Vérification des invariants : alias des anciens nœuds, commandes legacy conservées, principe de masques externes prioritaires, repli sans IA.
- Risque ergonomique constaté : beaucoup de workflows historiques et descriptions techniques peu exploitables en usage régulier. Les nœuds Experts sont préservés pour éviter une rupture des projets.

### Correction V21.1

- Ajout de `SmartSVGExpressV211`, seulement cinq choix après l’image : répertoire, type de projet, largeur, ppp, politique IA.
- Six workflows « démarrer ici » séparés des 88 workflows historiques.
- Résumé en français avec nombre d’objets, planches, chemin de sortie et avertissements prioritaires.

## Passe 2 — Géométrie, PNG HD et SVG Cricut (priorité critique)

### Bug prouvé A : incohérence de taille physique

- Ancien cas reproduit : masque sur source de 600 px, taille demandée 40 mm à 300 ppp.
- Ancienne sortie PNG : **619 px**, soit **52,41 mm si les métadonnées 300 ppp sont respectées** ; rapport d’export : **42,32 mm**.
- Cause : `target=max(w, ceil(mm×ppp/25.4))` préservait tous les pixels de la source dans le PNG « prêt à imprimer », tout en conservant la largeur théorique dans le SVG.

### Correction

- `production_v211.py` conserve les sources natales (`SOURCE_ORIGINALE.png`, et PNG détouré transparent natif quand un masque existe) et **recalibre le PNG imprimable** à la taille cible.
- Le SVG de contour est **reconstruit depuis l’alpha du PNG imprimable final** : géométrie et dimension physique désormais cohérentes dans la tolérance d’un pixel.
- Les PNG utilisent des métadonnées 300 ou 450 ppp ; le rapport calcule explicitement les mm correspondants.
- Ces mm sont **des recommandations d’importation**, pas une garantie que Design Space les appliquera automatiquement. La taille doit être vérifiée dans l’interface Cricut.

### Bug prouvé B : marge tronquée au bord du sujet

- Sur certaines sorties de masques touchant l’image source, la dilatation de la bordure blanche avait lieu **avant ajout de marge au support**, ce qui tronquait la bordure au niveau de l’image recadrée.
- Correction V21.1 : **agrandissement du canevas avant la dilatation de la silhouette**, sans toucher à la copie RGBA native. Test sur sujet collé au bord gauche.

### Autres contrôles

- Rééchantillonnage des couleurs à alpha prémultiplié pour réduire les halos sombres autour des pixels semi-transparents.
- Recomposition des planches après recalibrage des PNG individuels ; aucun redimensionnement silencieux des objets dans le simple packer.
- Les découpes de « tous les traits » restent dans les anciens moteurs Line Art : **ne pas confondre** avec un SVG de contour extérieur.

## Passe 3 — IA, masques et erreurs (priorité critique/haute)

### Bug prouvé C : « IA obligatoire » pouvant revenir au visuel complet

- Reproduction : fournisseur simulé répondant `{'masks': None}` avec `segmentation='forcer'`.
- V21.0 produisait malgré tout un résultat `REPLI_V20_6_SANS_MASQUE`.
- V21.1 refuse de publier ce résultat en mode obligatoire, avec un message explicite.

### Sécurité et fiabilité

- Contrôle de la **forme et du budget des masques avant transfert éventuel du GPU vers le CPU** : 32 masques / 50 millions de valeurs maximum selon le contrat V21.
- Conservation du refus des NaN/Inf, valeurs de masques hors plage et tailles incompatibles.
- Les masques à chevauchement ou difficiles restent **« à vérifier »** ; l’amélioration de la taille n’est pas une preuve d’extraction sémantique correcte.
- Aucun chargement de poids SAM2/BiRefNet effectué dans l’environnement d’audit.

## Passe 4 — Robustesse, mémoire et transactions (priorité élevée)

- Les traitements V21.1 utilisent un dossier temporaire **à l’intérieur du dossier cible**.
- Les changements de taille, SVG et planches sont achevés avant publication atomique du dossier final.
- En cas d’échec de recalibrage ou d’écriture, le dossier temporaire est nettoyé ; aucun projet V21.1 « réussi » partiel n’est publié.
- Les chemins du rapport principal et des rapports historiques sont recalculés après choix du dossier final. Les rapports de noms historiques reprennent aussi les **dimensions corrigées** : aucune contradiction silencieuse entre deux JSON.
- Les limites existantes de pixels et masques sont préservées ; test ciblé de refus avant copie GPU coûteuse.
- Ce protocole réduit les dossiers orphelins, **mais ne rend pas atomiques les écritures dans les moteurs historiques utilisés directement**.
- La sortie recalibrée peut prendre légèrement plus de CPU et de mémoire qu’un traitement V21.0 sans recalibrage : aucun gain de vitesse global non mesuré n’est revendiqué.

## Passe 5 — UX et tests sur les cinq sources de l’utilisateur

| Source réelle | Résultat exécuté V21.1 | Ce qui n’est PAS démontré |
|---|---|---|
| Affiche *Le malaise est en toi* | 1 PNG recalibré, cadre SVG | personnages isolés |
| Courage | 1 PNG recadré recalibré + SVG de cadre | chien séparé de son titre |
| Planche Pokémon | **24 fichiers PNG**, contours SVG, **2 planches** | perfection des 24 contours, disponibilité juridique d’un usage commercial |
| Canard musclé (capture mobile) | image recadrée, sortie cadre PNG/SVG | canard isolé de l’arrière-plan |
| Famille renard | image entière et contour rectangulaire | trois renards séparés |

Test supplémentaire sur **trois masques synthétiques** : export d’objets transparents, PNG imprimables, SVG et planche ; bord source vérifié.

### Bilan tests

- **459 anciens tests** : réussis après modification de l’interface d’enregistrement.
- **27 nouveaux tests V21.1** : réussis (dimensions, bord blanc, erreur du mode `forcer`, mémoire, sortie atomique, UI, planche de 24, chemins, alpha natif).
- **Total : 486 tests automatisés réussis** dans l’environnement CPU local.
- Test réel de cinq images : réussi en mode hors IA, sans revendication de découpe physique.

## Registre de risques restant ouvert

| Priorité | Problème non résolu | Décision proposée |
|---|---|---|
| **P0** | Pas d’exécution documentée des poids SAM2/BiRefNet sur RTX 3070 8 Go | Test installation utilisateur, premier profil GPU/masques, comparer résultats et VRAM |
| **P0** | Pas de test Cricut réel, tailles parfois reconfigurées lors de l’import | Importer PNG/SVG, régler mm dans Design Space, faire une planche test de 4 stickers |
| **P1** | Plusieurs renards qui se touchent ou petits détails des Pokémon : masques susceptibles d’être fusionnés | Segmentation d’instances par boîtes/points, correction manuelle par objet |
| **P1** | Aucune vectorisation couleur universelle entièrement éditable dans Design Space | Pipeline de calques vectoriels par régions/couleurs, sans forcer les photos réalistes en SVG |
| **P1** | Qualité d’impression native des petites sources (Pokémon ~159 ppp à 32 mm selon V20.6) | Conserver natifs, comparaison d’upscalers **seulement après tests qualitatifs** |
| **P2** | Historiques nombreux (workflows, documentation) | Menu unique Express, raccourci Démarrer, documentation séparée Expert et Archives |
| **P2** | IA externe en masque `MASK` ne prouve pas la catégorie ni l’ordre des objets | Vérification visuelle et édition par objet, rapport d’origine de masque |

## Critères avant de considérer le projet « prêt à produire »

1. Sur GPU réel : des masques obtenus pour canard et renards, un temps d’inférence et une VRAM mesurés, sans crash.
2. Sur planche Pokémon : 24 stickers avec des contours réellement inspectés à taille finale.
3. Dans Design Space : largeur de deux PNG et SVG de référence mesurée et corrigée au millimètre près ; opération *Imprimer puis découper* validée.
4. Sur Cricut : une planche test physique et comparaison des découpes à l’aperçu.
5. En UX : un utilisateur peut partir d’un Load Image jusqu’aux fichiers finis sans ouvrir les réglages experts ni naviguer dans 90 anciens workflows.

**Verdict : V21.1 est une corrective bêta plus cohérente et plus simple. Tests logiciels validés, résultat matériel et précision IA non encore validés.**
