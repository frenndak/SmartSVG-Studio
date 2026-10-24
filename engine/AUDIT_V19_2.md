# Audit V19.2 — périmètre de validation

Référence fournisseur : `AILab_SAM2Segment.py` du dépôt `1038lab/ComfyUI-RMBG`. API constatée : `SAM2Segment.INPUT_TYPES()` -> `image,prompt,sam2_model,dino_model,device`; `FUNCTION='segment_v2'` ; `RETURN_TYPES=('IMAGE','MASK','IMAGE')` ; masque tensor `[1,H,W]`.

Le moteur instancie la classe par le registre ComfyUI seulement si ces exigences sont satisfaites. Il **ne prétend pas appeler directement Florence-2** : GroundingDINO sert de détecteur textuel en amont de SAM2. Le résultat garde ses pixels originaux et la chaîne de sortie/photo V19.1 ; les fichiers Cricut des planches restent sur le moteur V18.1.

Tests locaux : contrat d'API simulé, masque multi-catégories, échec du plug-in, mauvais masque NaN, doublons, priorité aux masques externes, échec `forcer`, diagnostic `auto`, exports PNG+masques, câblage des workflows.

Limites : sur ce conteneur, pas de GPU RTX 3070 et aucun poids SAM2 téléchargé. Une validation des contours réelle sur les deux photographies du projet reste nécessaire. Pour les photos sans modèle utilisable, seule l'image d'origine et le diagnostic sont livrés ; cela n'est pas une segmentation IA réussie.
