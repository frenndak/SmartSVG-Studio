# SmartSVG Studio V21.3 — Détection par instance + export Cricut (bêta)

## Ce qui change

L'ancien fournisseur SAM2 interroge une **catégorie** entière (`fox`, `dog`, `duck`), ce qui peut mélanger plusieurs sujets identiques. V21.3 ajoute une chaîne distincte :

1. **Florence-2** (nœud `AILab_Florence2` de ComfyUI-RMBG) cherche **plusieurs boîtes distinctes**, y compris pour une même catégorie. Alternative : des boîtes en JSON saisies/corrigées manuellement.
2. **SAM2** (nœud `SAM2Segment` de ComfyUI-RMBG) travaille **sur chaque recadrage**, un sujet après l'autre.
3. SmartSVG valide les plages, tailles, débordements, chevauchements, doublons et la cohérence spatiale des masques.
4. Le nœud Express V21.3 réutilise le moteur **V21.2** : chaque masque produit son PNG transparent, son PNG de travail pour Imprimer puis découper, son contour SVG et sa fiche QA.

**Une boîte n'est jamais un masque.** Une proposition issue de SAM2 reste **à vérifier** ; aucun score n'est une précision de segmentation certifiée.

## Commencer facilement

1. Fermer ComfyUI. Déplacer l'ancien dossier SmartSVG de `custom_nodes` hors de ce répertoire.
2. Décompresser **un seul** dossier `ComfyUI-SmartSVG-Studio-V21.3` dans `ComfyUI/custom_nodes/`.
3. Conserver/installer `ComfyUI-RMBG` et ses modèles Florence-2 / GroundingDINO / SAM2 compatibles. Premier lancement peut télécharger les poids.
4. Redémarrer ComfyUI. Ouvrir `example_workflows/SmartSVG_Studio_V21_3_03_Trois_Renards.json`.
5. Mettre l'image des renards dans `LoadImage` et exécuter ; le nœud central renvoie le lot `MASK` vers Express, les aperçus et un diagnostic.
6. Si Florence ne détecte pas séparément les renards, choisir le workflow `04_Renards_Manuel` et **vérifier/ajuster** les trois rectangles `boites_json` déjà pré-remplis pour l'image 614×1536 px fournie. Ce sont des **régions indicatives**, pas des contours validés.

Workflow Express simple : `01_Express_Simple` ; Pokémon : `02_Pokemon_24` ; Courage : `05_Courage` ; canard : `06_Canard` ; personnages : `07_Personnages`.

## Ergonomie

- Le **nœud Express conserve ses cinq paramètres**, plus l'image et l'entrée MASK optionnelle.
- Pour un sujet sur fond complexe, **le workflow guidé a un nœud additionnel** préconfiguré : profil du sujet, source des boîtes, boîtes manuelles éventuelles, nombre maximal d'objets.
- Le masque issu du nœud de guidage est connecté à l'Express avec IA **Désactivée**, car les masques sont déjà calculés par le nœud de guidage. La segmentation ne s'exécute donc pas deux fois.
- Pour imprimer un autocollant, importer le PNG `IMPRIMER_DECOUPER` dans Design Space et vérifier taille et opération. Le SVG est un **contour de contrôle/alternatif**, pas une promesse que Design Space associera automatiquement le PNG et le SVG comme une seule opération.

## Contraintes et garde-fous

- Source RGB/RGBA ComfyUI ; maximum **5 mégapixels** pour la chaîne d'instances locale.
- Au maximum **12 sujets** ; défaut **6** ; **50 millions** de valeurs de masque au maximum ; chaque recadrage <=4 mégapixels.
- Contrôle CUDA au début du nœud et **seuil conservateur 3 Gio libres** ; seuil de prévention, pas besoin VRAM mesuré de SAM2.
- Plusieurs animaux très proches peuvent rester fusionnés. Les masques similaires sont dédupliqués, les recouvrements signalés **sans suppression automatique**.
- Avec plusieurs objets enchevêtrés (famille de renards), la segmentation *par boîte* est une aide mais peut manquer des membres, des cheveux ou des vêtements. Revoir les aperçus.
- Sans Florence/SAM2 en état de marche, le workflow guidé échoue **explicitement** : aucune boîte n'est « convertie » en faux PNG détouré.
- Les **24 Pokémon** restent traités par le moteur à fond uniforme, sans inférence IA obligatoire.

## Qualité / tests

- **534 tests de code** : 507 historiques, 27 nouveaux V21.3. Les 27 nouveaux tests couvrent notamment 3 instances, filtre des boîtes, déduplication, mémoire, sorties invalides et trois exports Cricut de bout en bout **avec modèle simulé**.
- Cinq images de référence disponibles. Les images de Courage, du canard et des renards ne sont **pas** prétendument détournées par de véritables poids IA lors de cette construction : seuls les rectangles de guidage ont été visualisés.
- **Aucune inférence CUDA sur RTX 3070 ni découpe Cricut réelle n'a été exécutée ici.**

## Prochaines priorités

Mesurer les masques réellement obtenus sur GPU local, corriger les superpositions persistantes puis améliorer le matting des cheveux/fourrures et la vérification physique dans Design Space. Les SVG couleur complètement éditables restent distincts du PNG photo haute résolution.
