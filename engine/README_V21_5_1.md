# SmartSVG Studio V21.5.1 — Corrections V21.4/V21.5

## Installer

1. Fermer ComfyUI, mettre les anciens dossiers SmartSVG **hors de `custom_nodes`** (ne pas laisser plusieurs versions installées).
2. Extraire `ComfyUI-SmartSVG-Studio-V21.5.1` dans `ComfyUI/custom_nodes/`.
3. Redémarrer ComfyUI et rafraîchir la page (Ctrl+F5 si nécessaire).
4. Charger `example_workflows/SmartSVG_Studio_V21_5_1_01_Express_Simple.json`, ou `..._02_Pokemon_24.json`.
5. Charger une image, choisir profil et largeur, exécuter le nœud. Le panneau affiche le résultat, ses alertes et les miniatures de QA lorsqu'elles sont disponibles.

**Le mode Express conserve ses 5 réglages**, le port facultatif MASK et les 3 sorties précédentes. Les nœuds historiques restent disponibles pour ouvrir les anciens workflows.

## Trois corrections principales

- **Aperçu derrière un proxy :** les URL sont construites avec `api.apiURL('/view')` ; elles respectent le préfixe public tel que `/proxy/8188/` au lieu de demander directement `/view` à la racine du domaine.
- **Échec de l'interface facultative :** une exception durant la préparation du panneau ou la copie des vignettes n'invalide plus un export de fabrication déjà réussi. Le JSON du traitement et les fichiers PNG/SVG restent accessibles. Les erreurs réelles de fabrication continuent à être signalées normalement.
- **Conservation des vignettes :** les miniatures temporaires publiées dans `ComfyUI/output/SmartSVG_Studio_Previews` sont ramenées à **96 au maximum**, avec nettoyage des miniatures de plus de **72 heures**, lors des exécutions suivantes. Seuls les fichiers portant le préfixe contrôlé `qa_*.png` et les caractères autorisés sont candidats à la suppression. L'ancien résultat à l'écran peut perdre son lien image une fois nettoyé : le **dossier QA du projet** est conservé.

Améliorations complémentaires : nettoyage du tableau de bord si une exécution fournit un résultat absent/invalide, message explicite en cas d'échec de copie, image non chargée signalée, redimensionnement des vignettes borné à 840 px.

## Différences et limites importantes

- Ces changements touchent **l'interface et ses copies d'aperçu**, **pas les moteurs de fabrication**. Les fichiers PNG/SVG produits par les versions V21.4, V21.5 et V21.5.1 ont été comparés sur les 24 Pokémon : **77/77 identiques SHA-256**, deux planches, 24 sujets.
- Le panneau visuel n'est pas un éditeur de masques : la retouche graphique reste prévue pour la V21.6.
- La présence de RMBG ne valide ni la précision Florence-2/SAM2, ni la VRAM réellement consommée sur RTX 3070.
- La taille dans Cricut Design Space, le nombre de découpes et le résultat physique doivent toujours être contrôlés sur la Cricut Explore 5.
- Le rendu visuel ComfyUI réel n'a pas été testé dans cet environnement, seulement via des simulations du navigateur et tests de code.
- Les miniatures publiées via `/view` peuvent être accessibles aux clients autorisés de ton serveur ComfyUI. Ne pas exposer ComfyUI sans authentification lorsqu'il traite des fichiers privés.

## Vérifier

Depuis le dossier de l'extension extraite, exécuter `python verify_package_v2151.py --integrity-only`, puis `--suite 1`, `--suite 2`, `--suite 3`, `--suite 4`, `--javascript`. Les suites doivent être lancées séparément dans l'environnement ComfyUI. Node.js >=18 est utile **uniquement pour les tests JavaScript**, pas pour faire fonctionner l'extension.
