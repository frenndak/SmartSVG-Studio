# V21.0 — 23 octobre 2026

**Ajouts :**
- Le nœud `SmartSVGSimpleV21` complète sans remplacer `SmartSVGSimpleV206` ; sept workflows directs.
- Masques `MASK` ComfyUI optionnels par objet, ou segmentation interne SAM2 (activation explicite, garde-fou CUDA).
- Fichiers transparents à résolution native et PNG sticker à marge blanche / unités physiques ; SVG de contour uniquement ; planches sans mise à l'échelle silencieuse.
- Validation stricte de masques 0/1 ou 0/255, formes et dimensions, refus des lots trop grands, élimination de doublons évidents, signalement de superpositions et fragmentation.
- Repli explicite V20.6 si aucun masque IA n'est disponible.
- Nouveau mode coupe rectangulaire prioritaire : aucun masque n'est utilisé, aucune IA inutile.
- Export V21 atomique (répertoire temporaire renommé une fois tous les fichiers créés).

**Préservé :** les 431 tests V20.6, les anciens moteurs photo, Line Art, stickers, profils et paramètres. La vraie qualité de segmentation GPU reste non évaluée.

**À développer V21.1+ :** segmentation réelle de multiples instances identiques sur les renards, validation des masques sur PC utilisateur, test d'importation Design Space, amélioration des contours délicats et éditabilité SVG par zones/couleurs.
