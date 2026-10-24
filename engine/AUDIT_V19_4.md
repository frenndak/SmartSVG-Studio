# V19.4 — contre-expertise de la segmentation photo

La V19.3 connecte Florence-2/SAM2 mais son export manque d'un diagnostic par objet pour décider si un masque est digne d'un sticker.

## Risques traités

1. Différencier un masque **fragmenté** et un sujet monobloc ; distinguer les petits îlots.
2. Repérer les trous internes qui deviennent des zones blanches sur la version Cricut.
3. Détecter les sujets accolés au bord de la photo et les transitions de transparence.
4. Ne pas appeler un filtrage d'alpha une « reconstitution des cheveux ».
5. Éviter tout changement silencieux de la géométrie d'impression : les anciens fichiers et leurs empreintes restent identiques.
6. Garder une logique sans faux positifs si les modèles sont absents : aucun objet extrait sans masque valable.

## Qualification

- Tests de contrat et de simulation en Python : résultats consignés par `verify_package.py`.
- Source réelle image du cadeau : diagnostic seul, source pixel-identique, zéro extraction sans masque.
- Source réelle photo du personnage avec les chopes : même comportement.
- Les variantes `BORDS_DOUX` sont explicitement expérimentales et n'écrasent jamais `CRICUT_TEST.png`.
- Les métriques de masque sont **des indications de qualité, pas des pourcentages de précision ML**.

## Pour passer au niveau supérieur

Tester physiquement V19.4 sur ComfyUI, relever la version RMBG et les ressources CUDA disponibles puis conserver de vrais masques sur ces deux photos. Construire alors un jeu de comparaison annoté : frontières cheveux/barbe/bras/verre, erreurs de segmentation par objet, et impression/découpe Cricut.
