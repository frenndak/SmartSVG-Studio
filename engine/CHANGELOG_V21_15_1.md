# SmartSVG V21.15.1 — module de contrôle pré-découpe (ajout non destructif)

- Ajout `smartsvg_governance/artifact_qa.py` : audit PNG/SVG/planche **en lecture seule**.
- Diagnostic P0 : contours presque rectangulaires lorsque l'objectif est un sticker silhouette.
- Diagnostic P0 : désaccord entre nombre d'îlots alpha significatifs et nombre d'objets attendus.
- Diagnostic P1 : composantes alpha de très faible intensité (ne pas déduire une vraie coupe à partir de ces pixels seuls).
- Vérification des chemins SVG, de l'unité mm et des fichiers associés, avec protection contre chemins externes et SVG actifs.
- Tests positifs et négatifs pour les cas principaux.

**Aucun moteur de vectorisation, nœud ComfyUI ou fichier workflow V21.15 n'est modifié.**
L'audit n'est pas encore branché sur le bouton Exporter de ComfyUI et ne modifie pas les PNG/SVG ; cette intégration relève d'un micro-lot ultérieur. Les 9 masques humains G0.3 restent à annoter.
