# SmartSVG Studio — V21.15.4 (candidat, inspection des silhouettes)

**Objectif :** un premier lot G2.2/G2.6 d'aide à la sélection multi-sujets, sans IA, sans modifier les masques ni déclencher une découpe.

## Fonctionnalités ajoutées

- Nouveau nœud ComfyUI **SmartSVGChooseSubjectV21154**, dérivé du sélecteur V21.13.1 ; anciens identifiants, paramètres, sorties et nœuds conservés.
- Diagnostics CPU déterministes par masque : aire en pixels, rectangle englobant en coordonnées source, fragments significatifs (>=8 px), microparticules, masque vide, contact bord image et rectangle de remplissage quasi intégral. Aucun composant n'est supprimé.
- Interface de sélection avec vignette, anomalies lisibles et accessibilité clavier native ; le clic met à jour `numero_sujet` puis **nécessite de relancer** le workflow.
- Repli non bloquant vers l'ancien sélecteur si les diagnostics dépassent les limites de taille.

## Utilisation

1. Ajouter le nœud **01 · Inspecter et choisir les silhouettes (V21.15.4)** depuis SmartSVG / 01 CRÉER.
2. Brancher `image` et `masques_objets` de la segmentation existante.
3. Exécuter le workflow ; examiner les alertes de chaque sujet dans le panneau.
4. Cliquer sur un sujet puis relancer le workflow pour appliquer la sélection (pas de calcul déclenché par le clic seul).
5. Corriger si nécessaire dans l'éditeur de masque existant, puis inspecter l'export dans Design Space.

**Invariants :** les sorties `MASK`, `IMAGE`, `STRING` sont celles de V21.13.1 ; les diagnostics sont facultatifs, non sauvegardés dans le masque ; aucune nouvelle opération réseau, modification silencieuse ni suppression d'accessoire.

## Tests vérifiés localement

- 40 tests Python des modules V21.13, V21.13.1, V21.15.1, V21.15.2 et V21.15.4 : réussis.
- 13 scripts de tests JavaScript : réussis.
- Compilation Python des nouveaux modules : réussie.
- Tentative de suite Python globale : **non terminée (timeout)** ; ne pas la déclarer validée.
- Exécution réelle de ComfyUI GUI, inférence RTX 3070, import Design Space et coupe physique Explore 5 : **non testés**.

## Limites connues et étapes suivantes

- Maximum 32 masques, 5 mégapixels/source et 50 millions de pixels de masques pour l'inspection ; au-delà, sélection historique mais **aucun diagnostic**. Les aperçus de V21.13.1 restent limités eux aussi : l'inspecteur n'est pas un outil A4 300 dpi universel.
- Les contours réellement fermés, la fidélité chromatique, la correspondance sujet/accessoire et la qualité de découpe ne sont **pas** certifiés par une analyse de composants.
- Une forme intentionnellement rectangulaire peut être légitime ; l'alerte impose seulement une revue humaine.
- Prochain travail : rapprocher le sélectionneur, l'éditeur de masque et les alertes d'export dans un parcours Express unique, puis lever prudemment la limite de prévisualisation haute résolution avec des aperçus proxy.

## Revenir à la version antérieure

Revenir à l'ancien `engine/__init__.py`, supprimer `node_v21154.py`, `smartsvg_core/subject_inspector_v21154.py` et `web/js/smartsvg_subject_inspector_v21154.js`. Laisser les autres fichiers du moteur inchangés. La baseline ZIP V21.15.2 et la roadmap v3.2 sont immuables ; la PR #25 (V21.15.3, précontrôle Cricut) est indépendante.
