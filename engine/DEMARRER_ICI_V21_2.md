# SmartSVG V21.2 — DEMARRER ICI

## Premier essai, sans menus compliqués

1. Retirer toute version SmartSVG précédente de `ComfyUI/custom_nodes` (la sauvegarder ailleurs).
2. Copier **le dossier entier** `ComfyUI-SmartSVG-Studio-V21.2` dans `custom_nodes` et redémarrer ComfyUI.
3. Ouvrir `example_workflows/SmartSVG_Studio_V21_2_01_Express_Auto.json`.
4. Charger une image via **Load Image**.
5. Choisir **Projet**, **Largeur mm**, **Qualité 300/450 ppp**, **IA**, puis lancer.
6. Ouvrir le **Dossier** affiché dans la sortie. Le fichier `05_CONTROLE_V21_2/APERÇU_GLOBAL.png` est la fiche visuelle.
7. Inspecter les contours, puis confirmer manuellement la largeur et l'opération dans **Cricut Design Space**.

Le mode Express garde **cinq réglages après l'image** (le dossier plus les quatre choix). Le contrôle qualité ne demande aucun paramètre de plus.

### Essai de vraie IA locale (sur le PC de l'utilisateur)

Ouvrir `SmartSVG_Studio_V21_2_07_Essai_SAM2_Reel.json` et sélectionner **IA : Si disponible**. Le mode essaie la chaîne SAM2 de ComfyUI-RMBG si elle est installée et si le garde-fou VRAM autorise l'appel. Il peut **se replier vers l'image complète**. Vérifier dans le rapport si le champ `analyse_ia` prouve l'appel et s'il a fourni un masque. Le seul fait de produire un dossier ne prouve pas la segmentation.

Pour une segmentation déjà exécutée dans un autre nœud, connecter sa sortie **MASK** à l'entrée facultative `masques_objets` du nœud Express, en gardant la sortie **IMAGE** de la même source. Les masques doivent avoir les mêmes dimensions H×W que l'image.

### Ce que vérifie V21.2

- Taille PNG en pixels / millimètres calculée depuis les ppp et dimension SVG exportée.
- Nombre de fragments alpha, transparences partielles, masques touchant le bord.
- Présence de fichiers réellement écrits, empreintes SHA-256 des PNG de découpe.
- Aperçu par objet et mosaïque globale de contrôle.
- Tout projet reste étiqueté **À VÉRIFIER AVANT CRICUT**.

### Ce que V21.2 ne garantit **pas**

- Que SAM2 reconnaisse correctement un renard, la tête du canard, une main ou tous les Pokémon ; un masque plausible peut être sémantiquement erroné.
- Qu'une image artificiellement agrandie retrouve les détails absents de l'original.
- Que Design Space adopte les métadonnées DPI sans réglage ; saisir et vérifier les millimètres.
- Que la lame découpe avec une qualité certifiée sans essai physique.
- Que les tests CPU du paquet valident les modèles GPU sur une RTX 3070.

### Fichiers à transmettre pour contre-expertise d'un vrai essai SAM2

- `RAPPORT_V21_2.json`
- `05_CONTROLE_V21_2/APERÇU_GLOBAL.png`
- Les fichiers individuels `05_CONTROLE_V21_2/OBJET_XX_AVANT_APRES.png` qui montrent un problème.
- Le journal de ComfyUI si l'IA échoue.

Ne pas communiquer de données confidentielles avec ces fichiers.
