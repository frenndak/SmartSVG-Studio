# SmartSVG Studio — État réel et prochains développements

**État courant vérifié : 6 novembre 2026, Europe/Paris**, code `main@467712be9421034c69fa2f2e6ace0b0bf153dd08`, après la [PR #119](https://github.com/frenndak/SmartSVG-Studio/pull/119). Roadmap active : **V3.4**, avec les 141 exigences héritées conservées. Point de reprise unique : [roadmap d'exécution et matrice des raccordements](roadmap-v3.4/EXECUTION_ET_INTEGRATION_2026_11_06.md).

| Domaine | État courant |
| --- | --- |
| Logiciel autonome | Fenêtre Python/Tk sans ComfyUI obligatoire, Accueil/Projet/Fabrique/Apparence ; navigation et thèmes communs |
| Projet natif | Lecture V1, diagnostic et aperçu source PNG ; **pas encore de création/sauvegarde/recovery exécutables dans le bureau** |
| Fabrique native | Carte pliée et boîte ouverte : géométrie théorique mm, CUT/SCORE et brouillons en RAM ; pas d'export ni de persistance du gabarit |
| Retouches et historique | Moteurs et raccords web historiques livrés ; **Atelier natif, calques/propriétés et commandes de sauvegarde restent à raccorder** |
| Exports | #115 contrôle Basic Cut ; #117 producteur réel/QA/transfert/livraison sur fixtures 300/450 DPI ; qualification complète des quatre contrats et parcours d'export natif ouverts |
| Catalogue et lots | Pagination API/web #114 ; bibliothèque bureau, recherche/variantes/CSV et qualification 12/24/50 encore à compléter |
| Windows | #119 : suite de 610 tests, 48 skips ; test réel Tk PASS aux trois tailles 900×650, 1100×760, 1280×720. Installation, DPI élevé et accessibilité complète non qualifiés |
| GPU / Design Space / Cricut | Aucune nouvelle preuve terrain de ces axes dans ce point ; tests CPU/UI distincts |

**Prochaine action de code : importer un PNG → créer un projet avec le moteur existant → vérifier sa sauvegarde → le rouvrir dans le logiciel autonome.** Le port/session sera étendu aux commandes historiques avant de raccorder Atelier, sorties, bibliothèque et lots. Le packaging reste un chantier distinct ; aucune présence de modèle IA n'est requise pour le parcours manuel/CPU.

**Preuves datées :** voir [le registre courant](roadmap-v3.4/EXECUTION_ET_INTEGRATION_2026_11_06.md#4-preuves-acquises-et-limites) pour les SHA et CI exacts. Les compteurs d'anciens commits ne s'additionnent pas et ne mesurent pas la complétion des tickets.

## Archive du bilan des PR #85–94

Le texte ci-dessous est une photographie conservée, avec ses compteurs, priorités et limites de l'époque. Il ne remplace pas le point de reprise courant ci-dessus.

**État logiciel vérifié : 6 novembre 2026 (Europe/Paris)**, code `main@a6f335c7c72658c07acf365ce111cf7682befc47` après les PR #85–94. Document vivant **non normatif** ; la référence active est la [roadmap V3.4](roadmap-v3.4/README.md), adoptée par la [promotion contrôlée](ROADMAP_PROMOTION_v3_4.md), avec les **141 exigences V3.3 conservées**. Les anciens lots de conception restent des photographies datées.

**Reprise indiquée à cette date historique :** consulter le [point de reprise G3.3e du 6 novembre](G3_3E_REPRISE_2026_11_06.md). La sauvegarde de gestes cumulés, Undo/Redo persistants, le trait continu temporaire borné et les aperçus agrandissables sont intégrés. Les coordonnées/clavier restent disponibles pour un point ; les calques/propriétés complets restent à réaliser. Les essais Windows/ComfyUI/Design Space/Cricut restent à exécuter séparément.

## Synthèse à ne pas confondre

| Niveau | Ce qui est prouvé | Ce que cela ne prouve pas |
| --- | --- | --- |
| **Code fusionné** | Modules Python/JS, contrats projets, inspecteur SVG, interface Express et retouches G3.3e sur la révision ci-dessus | Logiciel complet installé chez l'utilisateur |
| **CI automatisée** | PR #94 : suite G0 **484** tests (46 skips CPU attendus), workflow CPU **4 + 46** réussis sans skip ; local **484** sans skip et **54** tests Node ciblés réussis ; voir le point de reprise pour les SHA et journaux | Qualité visuelle d'une photographie, compatibilité hardware |
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
| **G3.2** | Bouton opt-in vers le **vrai gestionnaire de projets G2.2** dans le grand atelier : création PNG, inspection `.smartsvg`, notes et récupération avec confirmation ; DPI 300/450 natifs | Micro-lot G3.2 ; même origine ComfyUI/route API et UI réelle Windows à vérifier |
| **G3.3b** | Réception volontaire des vrais diagnostics G2.6 (vignettes, codes et zones), 1–32 sujets, depuis le nœud ComfyUI via canal même origine ; présélection locale uniquement | Deux onglets et lancement manuel du nœud toujours nécessaires ; aucune modification des vrais masques dans l’Atelier |
| **G3.3e — retouches** | Aperçu calculé depuis les gestes natifs cumulés ; sauvegarde explicite avec preuve Subject, digest de l’aperçu, CAS et relecture ; masques float32 de base conservés | PR #85–87 ; gestes natifs bornés, pas de deuxième moteur ni store |
| **G3.3e — historique** | Undo/Redo persistants, réouverture, reprise et contrôles Atelier ; les exports externes ne sont pas supprimés | PR #88–89 ; frontières de session native et anciens reçus sans inverse connu refusés explicitement |
| **G3.3e — trait/rayon/aperçus** | Trait continu temporaire jusqu’à 1 500 points ; rayon 0,05–20 % du petit côté ; aperçus 112/224/336 px ; accès clavier, annulation et recalcul avant sauvegarde | PR #91/93/94 ; gestes concurrents exclus, aucune taille physique déduite de l’affichage ; tests DOM simulés, pas de validation graphique Windows |
| **Prévol SVG** | Géométrie sous opacité nulle/négative exclue, cascade inline et valeurs ambiguës contrôlées | PR #90 ; contrôle statique limité, pas équivalence complète à un moteur de rendu SVG |
| **CI / gouvernance** | Précontrôle public HEAD, protection de sauvegarde, budgets optionnels et chemins historiques, dépôt public | PR #42–45 ; aucun appel payant nécessaire |

## Candidats prioritaires

**P0 — Test de terrain nécessaire avant promesse produit :** installer le `main` actuel sur le Windows cible, relever versions ComfyUI/Node/Python/extensions, vérifier que l'Atelier se charge depuis Express et que la PR #46 peut importer un SVG local. Enregistrer preuves écran + fichiers de sortie **dans un emplacement privé** (ne pas publier d'illustrations de l'utilisateur). Cette étape reste **NON FAITE** tant qu'une vérification matérielle n'est pas remontée.

**P1 — G3.2, première intégration de projets :** le panneau natif G2.2 est accessible volontairement dans l'atelier en cours. **À vérifier sur le PC cible** : accès au module ES, disponibilité des routes G2.2 activées, création PNG, lecture `.smartsvg` et récupération de secours. Aucun projet n'est créé ou modifié à l'ouverture du panneau.

**P1 — prochaine tranche B, quatre sorties sur fixtures :** relire les exporteurs et tests actuels, puis produire une preuve transversale des contrats PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche et SVG édition, avec provenance et préservation des fichiers antérieurs. Réutiliser les exporteurs et le prévol existants, sans nouveau store ni V2 imposé. Le dessin continu de la tranche A/D est intégré ; ses essais Windows et les calques/propriétés restent ouverts, sans bloquer les fixtures de B/C.

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

- [Roadmap V3.4 active](roadmap-v3.4/README.md) · [V3.3 héritée](ROADMAP_MASTER_v3_3.md) · [V3.2 historique](ROADMAP_MASTER_v3_2.md)
- [Preuves et reprise G3.3e au 6 novembre](G3_3E_REPRISE_2026_11_06.md) · [point précédent du 5 novembre](G3_3E_REPRISE_2026_11_05.md)
- [Documentation du raccordement G3.1](G3_1_EXPRESS_REAL_SVG_REVIEW.md)
- [Gestion native des projets dans l'atelier G3.2](G3_2_ATELIER_NATIVE_PROJECTS.md)
- [Contrat de source figée](SOURCE_V21_15_2_PROVENANCE.json)
- [Suivi GitHub des anciennes PR](https://github.com/frenndak/SmartSVG-Studio/issues/41)
