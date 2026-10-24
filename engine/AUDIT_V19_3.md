# V19.3 — Contre-expertise de l'intégration

## Source de vérité

Interface RMBG `AILab_Florence2` : le module publié expose `FUNCTION=analyze`, `RETURN_TYPES=(IMAGE, MASK, JSON)`, la tâche `Phrase Grounding (text boxes)` et des données `bboxes` / `labels`. **Ce n'est pas un moteur autonome de captioning libre.** Les résultats servent exclusivement à sélectionner des catégories candidates parmi un lexique borné.

## Contrats testés

1. Une boîte non numérique, infinie, trop petite ou débordante est rejetée/normalisée.
2. Les doublons de même catégorie sont écartés ; aucune confiance numérique artificielle n'est attribuée.
3. Les masques externes ignorent Florence et SAM2.
4. Le mode Florence `forcer` échoue sans publication en cas de node manquant.
5. Le mode `auto` conserve les prompts conservateurs de V19.2 si Florence échoue.
6. Une exécution Florence est limitée à 5 MP de source, en réduisant la passe de détection à 1024 px maximum.
7. La sortie du provider SAM2 reste le seul fournisseur de masques IA reconnus.
8. Les workflows Expr/Expert sont contrôlés contre la signature des classes, les widgets et les liens.

## Validation à effectuer sur le PC réel

- Test de chargement de l'extension dans ComfyUI et vérification des deux nœuds RMBG.
- Journal d'inférence Florence-2 Base sur RTX 3070 8 Go, puis SAM2.1 Tiny / GroundingDINO.
- Comparaison visuelle des vrais masques sur la femme + cadeau et sur le personnage + chopes.
- Vérification des parties fines et d'un test Print Then Cut sur papier ordinaire.

**Statut : validation logicielle du pont, pas validation matérielle ou du modèle neural réel.**
