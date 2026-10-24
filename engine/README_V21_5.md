# SmartSVG Studio V21.5 — Première interface visuelle dans ComfyUI

## Installation (Windows et ComfyUI)

1. Fermer ComfyUI et sauvegarder l'ancien dossier SmartSVG **hors** de `custom_nodes`.
2. Décompresser `ComfyUI-SmartSVG-Studio-V21.5` dans `ComfyUI/custom_nodes/`, **un seul dossier installé à la fois**.
3. Redémarrer ComfyUI **et rafraîchir le navigateur** (Ctrl+F5 si l'ancien tableau reste affiché).
4. Charger `example_workflows/SmartSVG_Studio_V21_5_01_Express_Simple.json` ou `02_Pokemon_24.json`.
5. Charger une image dans `LoadImage`, régler le projet, la taille, la qualité, la politique IA puis lancer le workflow.
6. Le nœud Express affiche un tableau de bord **dans ComfyUI** : nombre d'objets/planches, alertes et aperçu global ainsi que 6 premières fiches QA si disponibles.

**Contrat inchangé :** cinq choix d'Express après l'image, port `MASK` facultatif, sortie `IMAGE`, résumé et JSON. Les anciens workflows V21.4 et précédents restent compatibles.

## Parcours utilisateur

**Importer → Analyser → Exporter → Vérifier.** Les trois premières étapes sont exécutées par les moteurs existants ; la quatrième reste une **vérification humaine** de la taille, des contours et de l'opération *Imprimer puis découper* dans Cricut Design Space.

Le panneau est purement **consultatif** : il ne modifie ni les masques, ni les PNG, ni les SVG. La correction graphique des régions et des contours au stylet/souris fait partie de la future V21.6, **pas encore de V21.5**.

## Contrôle et aperçu

- Les images proviennent du rapport QA que la production a réellement généré, et sont placées en miniatures **PNG uniquement** dans le dossier de sortie officiel `SmartSVG_Studio_Previews` de ComfyUI. Il ne s'agit pas de nouvelles images inventées.
- Le panneau ne charge jamais un fichier du système par un chemin arbitraire depuis le navigateur : il utilise les métadonnées `filename/subfolder/type` de l'API `/view` déjà disponible dans ComfyUI.
- **Jusqu'à 7 images consultables** : la fiche globale et les six premières fiches individuelles. Tous les objets restent accessibles dans le dossier QA produit.
- Bouton **Copier dossier** : copie le chemin de sortie ; il n'ouvre pas de dossier depuis un navigateur distant.
- Si l'interface Javascript n'est pas disponible, le nœud Python fonctionne normalement et affiche le résumé habituel. Aucun export n'est bloqué.
- Les aperçus sont enregistrés dans le dossier `ComfyUI/output/SmartSVG_Studio_Previews`, qui peut être accessible aux clients autorisés de ton serveur ComfyUI. Éviter de partager un serveur ComfyUI non protégé contenant des images privées.

## Tests et limites

- Comparaison différentielles des 24 Pokémon avec V21.4, fichiers PNG/SVG conservés à l'identique.
- Suite de non-régression V21.4, nouveaux tests Python et JS du composant navigateur.
- Tests d'API et d'interface simulés : **le rendu graphique dans ton ComfyUI réel n'a pas été évalué** ; cela dépend aussi de la version du frontend (V2/Nodes 2.0).
- Florence-2/SAM2 sur GPU réel RTX 3070 et Cricut Explore 5 **non testés physiquement ici**. La qualité du détourage sémantique et la découpe demeurent à vérifier.

## Sources ComfyUI

- https://docs.comfy.org/custom-nodes/walkthrough
- https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/docs/extensions/development.md
- https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/docs/WIDGET_SERIALIZATION.md
