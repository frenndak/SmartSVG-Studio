# SmartSVG Studio V20.2 — Line Art + segmentation IA + choix Cricut

Cette version regroupe **tous les moteurs de SmartSVG V20/V20.1.2** avec le nouveau raccordement optionnel Florence-2/SAM2 du line-art.

## Installation Windows / ComfyUI
1. Fermer ComfyUI. Sauvegarder puis déplacer les anciens dossiers `ComfyUI-SmartSVG-*` hors de `custom_nodes` (éviter les doublons de nœuds).
2. Extraire le dossier `ComfyUI-SmartSVG-Studio-V20.2` de l'archive dans `ComfyUI/custom_nodes/`.
3. Vérifier les dépendances indiquées par les anciens fichiers `requirements.txt` et installer **ComfyUI-RMBG** si l'on souhaite l'inférence IA locale. Le mode sans IA fonctionne sans modèles chargés.
4. Redémarrer ComfyUI et charger `example_workflows/SmartSVG_Studio_V20_2_LineArt_Express.json`.
5. Charger `SmartSVG_Studio_V20_Diagnostic_Installation.json` pour contrôler l'environnement avant de forcer les modèles.

## Le nouveau nœud `SmartSVGLineArtV202`

- `operation_cricut` :
  - `imprimer_decouper_contour` : le personnage est imprimé, seule sa silhouette extérieure est destinée à la lame.
  - `decouper_contour_seul` : SVG du contour extérieur, en **Découpe de base**.
  - `decouper_tous_les_traits` : SVG de toutes les formes des traits, **pas** un sticker. Les traits épais peuvent donner deux bords de coupe.
  - `dessiner_au_stylo` : chemins médians en **Dessiner/Stylo**, si le tracé n'est pas trop fragmenté.
  - `tout_preparer` : produit les variantes pour contrôle, sans conseiller de les superposer.
- `segmentation_ia` : `auto` (essaie SAM2), `forcer` (échoue explicitement si aucun masque valide), `desactiver` (aucun appel modèle).
- `masques_objets` : masque externe optionnel ; **prioritaire** sur les modèles internes, même si `segmentation_ia=desactiver`.
- `repere_masque` : `source` (coordonnées de la photo) ou `carte_redressee` (coordonnées après homographie).
- `analyse_florence` : sélection des catégories si disponible ; en l'absence de Florence-2, les prompts du profil servent de repli si ce n'est pas forcé.
- `largeur_finale_mm` : dimension du **dessin sans marge**; les SVG de silhouette incluent proportionnellement le débord si une marge est ajoutée.

## Emplacements des fichiers

Chaque exécution crée un sous-dossier `LineArt_V20_1_*` (format historique conservé) :
- `01_SOURCE` : original RGB ou RGBA **inchangé**.
- `02_ZONE_UTILE`, `03_NETTOYAGE`, `04_LINEART` : redressement et traits.
- `05_CONTOURS`, `06_SVG`, `07_QA` : brouillons historiques, line-art vectorisé, aperçus.
- `08_CHOIX_CRICUT` : opérations de la V20.1.2 conservées, **géométriques**, même si un masque IA existe.
- `08_SEGMENTATION_IA_V20_2` : diagnostic et **candidats de silhouette IA** lorsque SAM2 ou MASK externe fournit des pixels utilisables.

Si un masque IA est disponible, `fichier_mode_choisi` dirige vers le candidat `01_IMPRIMER_DECOUPER_CONTOUR_IA_A_VERIFIER.png` ou `02_DECOUPER_CONTOUR_IA_A_VERIFIER.svg` pour les deux modes de contour. Pour les options « tous les traits » et « stylo », le fichier reste celui de `08_CHOIX_CRICUT`.

**Aucune image et aucun contour IA ne sont déclarés certifiés.** Les noms `A_VERIFIER` signalent qu'un masque peut exclure des cheveux, couper des mains, inclure une partie de l'interface ou tronquer un buste. Si aucun masque n'est produit, seul un contour géométrique brouillon reste disponible.

## Workflows
- `SmartSVG_Studio_V20_2_LineArt_Express.json` : sticker avec tentative IA.
- `SmartSVG_Studio_V20_2_Photo_Ecran_IA.json` : dessin pris en photo d'écran.
- `SmartSVG_Studio_V20_2_Masque_Externe.json` : masque pré-calculé d'un autre nœud ComfyUI (brancher la sortie `MASK` à `masques_objets`).
- `SmartSVG_Studio_V20_2_Silhouette_IA.json` : contour SVG extérieur.
- `SmartSVG_Studio_V20_2_Decoupe_Tous_Traits.json` : coupe des traits intérieurs (sans les confondre avec le contour IA).
- Les anciens workflows V20, V20.1.1 et V20.1.2 restent présents.

## Limites de validation

Les tests sont logiciels et comprennent des masques externes/simulés. **Aucun poids Florence-2/SAM2 n'a été exécuté sur la RTX 3070 de l'utilisateur**, et aucune découpe physique Cricut n'a été vérifiée. Pour un sticker, inspecter visuellement le candidat avant de l'importer dans Cricut Design Space en Imprimer puis découper.

## Continuité du chantier

V20.2 raccorde Line Art à la segmentation IA sans supprimer les projets photo, stickers multi-objets ou le profiler. Prochaine étape : V20.3, tests GPU 8 Go et corrections des vrais masques, puis photo complexe/occlusions et vérifications Cricut.
