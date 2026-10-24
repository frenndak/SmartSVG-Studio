# SmartSVG Studio V21.11.1 — Changelog

## Corrections

- **ComfyUI alpha natif** : récupération du MASK inversé de `LoadImage` sur les nœuds AutoMasks et AutoExpress V21.11 ; connexions ajoutées aux workflows 01 et 02.
- **Masques opaques** : un MASK natif à zéro (y compris la sentinelle 64×64 de certaines versions de `LoadImage`) ne provoque ni faux détourage ni inversion de silhouette ; il laisse agir l'heuristique ou l'IA selon le mode.
- **Masques externes** : validation de la forme `(N,H,W)`, exactitude H/W, plage 0..1, surface, nombre d'îlots et quasi-rectangles avant le moteur de fabrication.
- **Quasi-rectangles** : détection partagée entre détourage et précontrôle `00_IMPORTER_DANS_CRICUT` ; un rectangle imparfait n'est plus une silhouette supposée fiable.
- **33+ composantes** : comptage des grandes composantes avant tout plafond ; rejet et diagnostic explicites.
- **Mémoire** : budget global évalué avant création des masques de chaque case ; buffers `uint8` intermédiaires.
- **Vérification** : vérificateur V21.11.1 dédié, et ancien point d'entrée de vérification redirigé vers celui-ci.

## Conservé

- Identifiants et contrats des nœuds antérieurs à V21.11.
- Cinq paramètres Express et trois sorties.
- Modules PNG/SVG d'export de fabrication, dossier Print Then Cut, HD optionnelle automatique.
- Les 12 masques du test réel escargots sont identiques SHA-256 à ceux de V21.11.

## Limites

- Inférence IA RMBG/SAM2 réelle non testée dans cet environnement.
- Le workflow de capture recadrée ne peut pas reprendre directement un masque alpha non recadré.
- Tests d'import dans Design Space et découpe Cricut non effectués.
