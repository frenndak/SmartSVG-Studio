# SmartSVG Studio V21.12.2 — Contre-expertise du traitement par lots

## Observation initiale

Sur l'archive V21.12.1 et la planche Pokémon originale (1536 × 1097), l'export complet **avait été interrompu lors d'un contrôle précédent**. Un nouvel essai local a été instrumenté par étapes. **Il a terminé** en 26,28 s avec 24 PNG individuels, 24 fichiers HD et deux planches à 28 mm par sujet / 300 ppp. En revanche, le précontrôle d'import rejetait un PNG et une planche contenant un **trou transparent intérieur**.

## Correctifs réalisés

1. **Calcul redondant des planches.** `_render_subjects()` composait des pages, puis `_reconcile_report()` composait à nouveau les pages finales une fois les dimensions physiques recalibrées. La nouvelle classe Express évite la première étape via contexte isolé et arguments optionnels à valeur par défaut inchangée. Aucun changement pour les IDs anciens.
2. **Fond de découpe.** Le nouveau chemin remplit les trous intérieurs de l'alpha de découpe avant sauvegarde du PNG Print Then Cut et régénération du contour SVG. Les fichiers détourés natifs conservent les pixels/transparences originaux. Les quatre PNG affectés dans les 24 Pokémon sont les n° 2, 11, 21 et 23 ; les autres PNG de fabrication restent octet par octet identiques. **Tous les SVG de contour extérieur restent identiques**.
3. **Manifeste utilisateur.** Une inspection en lecture des sorties crée un manifeste relatif avec empreintes. Un échec de cette inspection facultative n'annule pas une fabrication déjà réussie, et aucun fichier existant n'est écrasé sans contrôle.

## Tests de référence

- 24 Pokémon : 24 masques proposés sans IA, 24 PNG individuels avec précontrôle local, deux planches avec précontrôle local, 24 fichiers HD. Durée instrumentée V21.12.1 : 26,28 s ; durée du nouveau chemin : 24,56 s. Ces mesures sont locales et non significatives sur la carte RTX 3070.
- 12 escargots : conserver 12 silhouettes distinctes sans IA (fonctionnalité historique). Tests de non-régression généraux en complément.
- Sept images opaques/complexes : l'absence de fournisseur IA doit rester un refus explicite, jamais un faux contour rectangulaire.

## Limites majeures

Les 24 masques Pokémon représentent des silhouettes proposées, pas une segmentation sémantique prouvée. **Trois fragments détachés potentiellement ignorés doivent être vérifiés manuellement.** L'export de PNG est techniquement précontrôlé, mais l'import dans Design Space et la découpe physique ne sont pas encore testés.

Le comblement des trous vise **uniquement le trajet extérieur de découpe de sticker**. Pour les usages avec trous délibérés ou la découpe de vinyle, utiliser un SVG/masque dédié et ne pas supposer que le blanc de backing convient. Pour créer des **SVG multicouches éditables**, il faudra reconstruire des zones de couleur avec contrôle de simplification, des courbes et de l'ordre des calques — un chantier distinct.

## Prochaine priorité

V21.13 : interface de préparation unifiée, choix du sujet, prévisualisation de la ligne de lame avec fond blanc/noir, séparation des fragments détachés, puis vectorisation multicouche expérimentale sur illustrations simples. Poursuivre les essais réels de BiRefNet/RMBG/SAM2 sur la machine de l'utilisateur et la découpe Explore 5.
