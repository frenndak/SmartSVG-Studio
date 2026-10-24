# Contre-expertise SmartSVG V21.12 — 24 octobre 2026

## Sources

- Archive V21.11.2 comme base byte-preserved, hors `__init__.py`.
- Répertoire public de ComfyUI-RMBG v3.3.0, fichiers `py/AILab_BiRefNet.py`, `py/AILab_RMBG.py`, `py/AILab_SAM2Segment.py`.
- Régression sur les 7 images déjà fournies (sans modèles chargés) et fixtures simulées, pas de résultats de détourage IA observés sur carte réelle.

## Critères couverts

1. Les anciennes classes et ports restent accessibles via le registre ; cinq widgets Express conservés.
2. Le contrôleur ne charge pas les modèles lors du diagnostic ; il valide signatures, noms de modèles et ordre des sorties.
3. Les candidats invalides déclenchent un repli vers un autre fournisseur ; les erreurs de VRAM interrompent l'inférence.
4. Aucun JPG sombre avec silhouette absente n'est exporté comme sticker rectangulaire.
5. Les fichiers PNG/SVG et les fichiers de `00_IMPORTER_DANS_CRICUT` sont inchangés lorsque le masque fourni est identique.
6. L'inférence **peut** être appelée sur les nœuds installés, mais le taux de réussite visuel et la consommation réelle en VRAM restent non mesurés.

## Résultat des sept images sans IA

- Escargots (12) : 12 masques proposés.
- Manga, illustration cadeau, photo Leprechaun, affiche, capture du canard, Psyduck : aucun masque fiable sans IA ; il faut exécuter les modèles et contrôler les résultats visuellement.

## Limites d'architecture encore ouvertes

- ComfyUI-RMBG télécharge parfois des poids lors de la première inférence ; durée, taille et mémoire dépendent des modèles effectivement installés.
- La méthode choisit un sujet saillant ou des objets décrits par prompts génériques. Une **validation sémantique** de l'objet souhaité n'est pas possible sans instructions utilisateur ou vision supplémentaire.
- SAM2 avec GroundingDINO peut nécessiter plus que les 8 Go disponibles selon contexte GPU : arrêter ou réduire source, jamais promettre une vitesse précise.
- ComfyUI moderne/Nodes 2.0, impression Design Space et Cricut Explore 5 : non testés dans l'environnement de développement.
- Le PNG transparent permet Print Then Cut après import comme Flat Graphic ; ne pas promettre d'édition indépendante des couches internes.

## Décision

**GO conditionnel pour essais réels.** Les contrôles automatisés et contrats externes sont cohérents, mais il faut mesurer qualité, GPU, RAM et UX sur la machine cible avant de déclarer le détourage IA validé.
