## V21.3.1 — Correctif audit multi-passes (2026-10-23)

- Nouveau nœud `SmartSVGInstancesV2131` plus fiable, ancien V21.3 conservé.
- Provenance honnête des détecteurs injectés.
- Alertes de chevauchement symétriques et empiètement entre boîtes.
- Arrêt en cas d'OOM CUDA; ne pas publier de lot partiel trompeur.
- Alias de catégories en français dans les boîtes manuelles.
- Calcul d'empiètement local pour réduire allocations temporaires.
- 7 nouveaux workflows V21.3.1 et vérificateur autonome.

## V20.0 (22 octobre 2026) — Consolidation majeure

- Anciens moteurs V19.9 conservés octet pour octet, y compris anciens identifiants de nœuds.
- Nouveau moteur V20.0 : refus des propositions contenant trop de pixels propres à un objet voisin et nouveaux contrôles des bords de ROI.
- Publication de diagnostic atomique dans `QA_MATTING_V20/<run>/` avec conservation source + proposition et suppression des sorties partielles après erreur.
- Repli sans masque sémantique forcé en analyse seule, sans détourage de fond historique non sollicité.
- Nœud indépendant de diagnostic RMBG et CUDA (noms `AILab_Florence2`, `SAM2Segment`, `BiRefNetRMBG`).
- 18 nouveaux tests, 243 tests complets réussis ; deux PNG Cricut historiques identiques ; deux images de référence conservées sans inférence.

# SmartSVG V19.8 — Changements

- Appariement par IoU et algorithme hongrois des objets entre différents lots.
- Abstention explicite en cas de masque absent, similaire ou ambigu.
- Sortie MASK dédiée aux incertitudes de contours.
- Trois modes distincts : diagnostic (inchangé), sélection prudente, sélection avec annotation.
- Nœuds Express/Expert V19.8, outil autonome AlignMasks et workflow guidé nécessitant un masque externe réel.
- Rapports JSON d'appariement séparés des exports Cricut.
- Aucune modification des anciens fichiers moteurs photo, stickers ou télémétrie.

# V19.7 — Instrumentation réelle (22 octobre 2026)

- Nouveau `SmartSVGStudioV197Express` / `SmartSVGStudioV197Expert`, compatibles avec les anciens identifiants V19.6.
- Paramètre `profil_performances = activer|desactiver` ; n'ajoute aucun téléchargement IA et ne modifie pas les fichiers de fabrication Cricut.
- Chronométrage synchronisé des étapes **réellement exécutées à l'intérieur du nœud SmartSVG** (Florence-2, SAM2, RMBG, export, comparaison de masques, stickers).
- Captures CUDA avant/après : mémoire PyTorch allouée/réservée, VRAM libre du périphérique, pic alloué historique de processus clairement qualifié.
- Rapports `PERFORMANCES_V19_7_*.json` hors du dossier de production, pour préserver les empreintes/manifeste de V19.6.
- Consignation des exceptions sans suppression d'un export réussi, conservation du mode sans instrumentation.
- Nombre de masques SAM2 accepté lorsqu'il peut être extrait ; temps moyen amorti par masque étiqueté comme tel, et non une vraie durée par objet.
- Tests supplémentaires : contexte imbriqué, absence CUDA, temps positif, panne, fausse CUDA, workflows, différence JSON, non-régression réelle du PNG Cricut.

## À mesurer sur machine réelle

- Charge / libération des modèles RMBG sur RTX 3070 8 Go.
- Bénéfice qualité de SAM2 / FeyNoBg / Finegrain sur les vrais masques de la femme/cadeaux et des chopes.
- Qualité/temps de chaque modèle externe si lancé **avant SmartSVG** (hors portée du chronométrage interne).
- Imports et coupes physiques sur la Cricut Explore 5.

## V19.7.1 — Audit indépendant et correctifs télémétrie
- Corrigé : `torch.cuda.synchronize()` échouait sans laisser de trace ; la durée n'est plus déclarée synchronisée dans ce cas.
- Corrigé : une seule API CUDA mémoire indisponible faisait perdre toutes les autres statistiques ; capture partielle détaillée par champ.
- Ajouté : signalement des changements de périphérique entre relevés et des étapes à synchronisation défaillante.
- Ajouté : mémoire RAM résidente du **processus** (best effort via psutil, si déjà disponible ; aucune dépendance obligatoire).
- Ajouté : durée exclusive **approximative** des étapes imbriquées et documentation de ses limites.
- Corrigé : impossibilité d'enregistrer un rapport de performances affichée dans le texte de sortie, sans annuler le travail Cricut.
- Nettoyage : imports dupliqués dans les nœuds historiques, sans changement de comportement.
- Nouveaux IDs V19.7.1 et workflows dédiés ; anciens IDs V19.7 conservés.
- La chaîne d'export et les modèles IA **ne changent pas**. Ce correctif ne valide pas les vrais GPU/modèles.

## V19.9 — Orchestration locale ciblee (2026-10-22)
- Introduit `adaptive_refiner_v199.py` : budget 5 MP / 25 M pixels, maximum 4 objets, crops ROI a marge borne, risques contour/transparent/chevauchement.
- Connexion directe a `BiRefNetRMBG` par introspection stricte de l'interface RMBG ; traitement sequentiel et liberation des poids si le provider expose `clear_model`.
- Nouveau noeud autonome SAM2->BiRefNet, avec optional MASK manuel ; sortie MASK retenu/MASK alternatif/carte d'incertitude/rapport.
- Noeuds Express & Expert opt-in : preservation du moteur V19.8 lorsque desactive ; second passage non destructif par defaut.
- Promotion seulement sur annotation explicite avec amelioration IoU de +0.025 ; refus des masques incoherents.
- Propositions et cartes QA en sous-dossier dedie, manifeste JSON separé, aucun ecrasement des fichiers Cricut historiques.
- Nouveaux tests V19.9 des echanges de masques, provider simulé, OOM/NaN et schemas ComfyUI.

## V20.1.0-alpha — branche « Dessin / Line Art »

- Nœud additif `SmartSVGLineArtV201` sans modification des moteurs photo et Cricut V20.
- Détection géométrique d'une carte rectangulaire, correction perspective, nettoyage du fond photographié, suppression d'une partie du moiré, double extraction des traits.
- Exports PNG et SVG monochromes avec aperçus QA, rapport JSON et publication transactionnelle dans un répertoire unique.
- Masque personnage géométrique explicitement marqué comme **candidat à vérifier**, jamais revendiqué comme segmentation IA.
- Nouveau guide `README_V20_1.md` et document de continuité `ROADMAP_APRES_V20_1.md`.
- 15 nouveaux tests, 258 tests exécutés au total sur le code source avant empaquetage.

## V20.6 — HD, profils simples et grille multi-stickers

- Nœud indépendant `SmartSVGSimpleV206` (six réglages, image à importer).
- Exports HD 300/450 ppp avec résolution native et interpolation déclarées.
- Grilles 6x4, 4x3, 3x3 : regroupement de composantes sans trancher les membres dépassant des cases.
- PNG individuel + contour SVG par personnage ; 2 planches de 12 pour 24 personnages, à taille conservée.
- Détection des bandes d'interface téléphonique ; PNG photo complet + cadre sans faux détourage sémantique.
- 25 nouveaux tests, 431 tests combinés.
