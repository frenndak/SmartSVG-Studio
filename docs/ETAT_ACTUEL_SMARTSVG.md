# SmartSVG Studio — État réel et prochains développements

**État constaté : 27 octobre 2026**. Document de suivi vivant **non normatif** ; la roadmap contractuelle et figée reste `ROADMAP_MASTER_v3_2.md`.

## Synthèse à ne pas confondre

| Niveau | Ce qui est prouvé | Ce que cela ne prouve pas |
| --- | --- | --- |
| **Code fusionné** | Modules Python/JS, contrats projets, inspecteur SVG, interface Express G3.1 sur `main` | Logiciel complet installé chez l'utilisateur |
| **CI automatisée** | Gates Python/Node G0/CPU des micro-lots et sécurité des sources ; derniers G3.1 : G0 **264**, HEAD **264**, CPU **4** réussis | Qualité visuelle d'une photographie, compatibilité hardware |
| **Essai navigateur** | Maquette statique manipulable, fichier HTML disponible dans le dépôt | Fonctionnement du module `.mjs` dans l'installation ComfyUI Windows |
| **Certification Cricut** | **Aucune** | Pas d'import/marge/dimension/coupe réelle validés sur Explore 5 |

Les réussites de CI sont des **constats de leurs commits**, pas un compteur global cumulable ni une garantie permanente sur les changements futurs.

## Jalons livrés en code et traçabilité

| Jalon | État intégré | Source / limites |
| --- | --- | --- |
| **G1.3/G1.4** | Archive `.smartsvg` et sauvegarde atomique de secours ; rejet projet invalide sans altérer l'ancien secours | PR #38 (incluant #40), précédemment #15/#16 |
| **G1.5/G2.1/G2.2** | Express guidé, API projets gérés, sélection de profil, contrôle d'état | PR #38 ; création de projet dans panneau existant principalement PNG |
| **G2.3/G2.4** | Retouches natives sauvegardées, snapshots float32 pleine résolution | PR #38 ; compatibilité et reprise réelle sur PC à éprouver |
| **G2.5/G2.6** | Ergonomie compacte, inspecteur de fragments et focus de masques | PR #38 ; UI graphique de terrain non certifiée |
| **G2.7/G2.9** | Inspecter les vrais SVG conformes, choisir chemins, brouillon vectoriel local | PR #38 ; sous-ensemble de SVG uniquement, géométrie complexe à vérifier |
| **G2.8** | Brouillon de traits récupérable après incident navigateur | PR #38 ; ne sauvegarde pas tout le graphe ComfyUI |
| **G3.0** | Atelier plein écran responsive, mode exemple 12 sujets, image locale | PR #39 ; pas de conversion ni segmentation IA réelle |
| **G3.1** | Bouton pour charger volontairement l'inspecteur réel G2.9 depuis l'atelier servi par ComfyUI | PR #46 ; route module ES à tester sur ComfyUI installé |
| **CI / gouvernance** | Précontrôle public HEAD, protection de sauvegarde, budgets optionnels et chemins historiques, dépôt public | PR #42–45 ; aucun appel payant nécessaire |

## Candidats prioritaires

**P0 — Test de terrain nécessaire avant promesse produit :** installer le `main` actuel sur le Windows cible, relever versions ComfyUI/Node/Python/extensions, vérifier que l'Atelier se charge depuis Express et que la PR #46 peut importer un SVG local. Enregistrer preuves écran + fichiers de sortie **dans un emplacement privé** (ne pas publier d'illustrations de l'utilisateur). Cette étape reste **NON FAITE** tant qu'une vérification matérielle n'est pas remontée.

**P1 — G3.2, première vraie intégration du projet dans l'atelier :** réutiliser les routes G2.2 de façon authentifiée et same-origin ; exposer sélection/projets en cours, statuts, source PNG, sans chargement automatique de fichier ni effet serveur à l'ouverture. Ajouter gestion claire des conflits de sauvegarde et tests de sûreté.

**P1 — G3.3, sujets et masques réellement visibles :** raccorder l'inspecteur G2.6 (fragments / zones suspectes) et l'état des masques G2.4 sans conversion destructive ; séparation visuelle des 12 sujets fictifs et des vrais objets.

**P1 — G3.4, détourage et segmentation IA facultatifs :** intégrer une importation orientée caméra (EXIF, profils couleurs, alpha) puis appeler le moteur ComfyUI de façon **explicite**, avec repli CPU et logs lisibles. Sur RTX 3070 8 Go, mesurer mémoire et temps avant de définir une qualité par défaut.

**P2 — G4/G6 :** valider dimension, topologie des contours (intersections, trous, Béziers), Print Then Cut image aplatie + SVG de coupe distinct, et planches 12/24 ; import réel dans Design Space puis essais de coupe Explore 5 et correction des écarts.

## Contrats non négociables

- SVG **Basic Cut** (chemins) différent du PNG destiné à **Print Then Cut** ; le SVG contour seul n'offre pas de calques couleur automatiquement éditables.
- Les tailles mm, le `viewBox`, les unités et les chemins fermés doivent être inspectables. Ne jamais assimiler « SVG enregistré » à « coupe certifiée ».
- Le dépôt est public : **aucun secret, photo personnelle ni média tiers sous droit** dans le code/tests publics.
- Roadmap V3.2 et ZIP V21.15.2 intouchables ; fonctions nouvelles sous micro-PR et régression avant fusion.
- Conserver l'accès à l'interface de démonstration malgré l'absence d'IA/GPU, et annoncer clairement toute fonction indisponible.

## Guide d'essai rapide

1. Parcourir `engine/web/js/smartsvg_express_atelier_preview.html` (maquette hors ligne).
2. Sur une installation ComfyUI compatible, ouvrir le panneau Express → **Découvrir l'atelier complet**.
3. Cliquer **Examiner un vrai SVG de contours**, choisir localement un SVG déjà exporté, sélectionner ses chemins et télécharger le **brouillon**.
4. Vérifier les dimensions et le résultat dans Design Space **sans prétendre à une découpe validée** ; documenter les erreurs et conditions du test.

Le gestionnaire de projets du panneau Express dispose déjà de fonctions réelles distinctes de cette interface plein écran. L'intégration progressive doit les réutiliser, pas recopier leur logique dans une deuxième application.

## Références

- [Roadmap figée](ROADMAP_MASTER_v3_2.md)
- [Documentation du raccordement G3.1](G3_1_EXPRESS_REAL_SVG_REVIEW.md)
- [Contrat de source figée](SOURCE_V21_15_2_PROVENANCE.json)
- [Suivi GitHub des anciennes PR](https://github.com/frenndak/SmartSVG-Studio/issues/41)
