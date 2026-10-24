# Contre-expertise multi-passes — SmartSVG V21.3.1 vers V21.3.2

## Référentiel et portée

Inspection du code source complet de la V21.3.1 (environ 12 873 lignes Python, dont validateurs et tests), des 7 workflows actifs et de l'interface ComfyUI. Vérification des cinq cas historiques : affiche, logo Courage, planche 24 Pokémon, canard et famille renard. Les masques réels Florence-2/SAM2, la VRAM de la RTX 3070 et la machine Cricut ne sont pas disponibles dans cet environnement.

## Passe 1 — Architecture [impact élevé]

- **Constat** : 58 nœuds enregistrés et plusieurs générations d'implémentations, 14 manifests historiques, nombreux README/anciens vérificateurs. Compatibilité réussie, mais découverte difficile et dette de maintenance importante.
- **V21.3.2** : trois nœuds mis en avant (`00 Diagnostic`, `01 Express`, `02 Guidage IA`), tous les anciens IDs conservés et intitulés préfixés `Ancien`.
- **Reste à faire** : séparation `core/`, `integrations/rmbg/`, `ui/`, `qa/`, `legacy/` et `tests/` ; réduire les verificateurs doublons avec un seul exécutable de tests. Faire cette extraction à l'étape suivante avec comparaison SHA des PNG/SVG.

## Passe 2 — Expérience utilisateur [impact très élevé]

- **Constat** : `IA desactivee` avec un masque relié a l'entrée facultative parait contradictoire ; la source réelle du résultat n'est pas assez lisible ; le champ JSON manuel expose des détails sans expliquer le repère des coordonnées.
- **V21.3.2** : aides contextuelles dans le nœud Express et le guide d'instances ; provenance des masques mentionnée dans le message final ; sept workflows guidés avec noms et étapes explicites ; workflow de diagnostic indépendant. Aucun nouveau réglage ajouté à Express.
- **Reste à faire** : interface web dédiée avec aperçu interactif des objets, retouche de boîtes à la souris, choix visuel contour vs tous les traits et vues avant/après. Une vraie UI nécessite tests sur ComfyUI Frontend (et Nodes 2.0), non validés ici.

## Passe 3 — Robustesse SVG / Cricut [problème démontré]

- **Constat reproductible** : le validateur `_svg_width_mm` lisait la première chaîne `<svg width=...>` du fichier, y compris en commentaire. Exemple : commentaire prétendant `42 mm`, racine vraie `140 mm` → rapport erroné de `42 mm`.
- **Correction V21.3.2** : parser XML de la vraie racine; rejet DTD/ENTITY et SVG malformed; limites de tailles et des dimensions; 6 nouveaux tests. Le rendu SVG de production demeure inchangé.
- **Reste à faire** : contrôle de topologie des paths, périmètres de lissage, taille de la zone Imprimer puis découper dépendante de Design Space et fichier imprimé à taille réelle.

## Passe 4 — Segmentation / données [risque ouvert]

- **Constat** : boîtes guidées != masques, catégories définies manuellement et instances qui se chevauchent (renards). Le fonctionnement est conservateur, sans suppression de pixels de contact. Aucun essai avec poids réels ici.
- **Reste à faire** : vrais tests SAM2/BiRefNet sur RTX 3070, matrice de masques annotés, métriques IoU/Dice des contours et évaluation de la fourrure/cheveux. Ajouter une option de masques à corriger au lieu d'afficher un verdict heuristique trop confiant.

## Passe 5 — Installation, maintenance et performance

- **V21.3.2** : diagnostic non invasif des interfaces `AILab_Florence2` et `SAM2Segment`, de la présence CUDA et de la VRAM libre. Aucune garantie de poids disponibles à partir d'un nœud enregistré.
- **Reste à faire** : compatibilité V3 de ComfyUI, tests Windows portable / Nodes 2.0, matrice de dépendances; tests de charge sur fichiers 24/48/96 stickers; CI, packaging sans documentation historique et sans modèles embarqués.

## Bilan des corrections

- 16 nouveaux tests interface / diagnostic.
- 6 nouveaux tests du parseur de largeur SVG.
- 555 tests V21.3.1 de référence restent exigés, soit **577 tests prévus** après intégration.
- Test différentiel du moteur réel avec un masque contrôlé : SHA-256 identique sur PNG imprimable, PNG transparent et SVG contour entre V21.3.1 et V21.3.2.
- Ancien nœud, catégories d'opérations, formats PNG/SVG et 5 options du nœud Express conservés.

## Priorités proposées pour la suite

| Priorité | Chantier | Pourquoi |
|---|---|---|
| P0 | Exécuter les modèles réels et comparer des masques annotés | Le plus grand risque produit reste la précision des détourage |
| P0 | UI graphique de corrections manuelles de boîtes/masques | Permet une retouche fiable quand les IA se trompent |
| P1 | Nettoyer les 58+ nœuds via UI/registre d'archives versionnées | La simplicité d'accès aux nœuds devient difficile à maintenir |
| P1 | Simplifier architecture core/adapters/export/qa + tests CI | Diminue les régressions et les migrations dangereuses |
| P1 | Tracé SVG modifiable par formes et couleurs sur dessins | Fonction demandée mais incomplète pour images complexes |
| P2 | Tests de performance et de mémoire sous Windows RTX 3070 | Évite de prédire un besoin de VRAM depuis une simulation |
| P2 | Tests impression/découpe sur Cricut Explore 5 | Seule vérification physique de l'importation, des marges et du matériel |

## Documentation externe

- ComfyUI : `https://docs.comfy.org/custom-nodes/backend/interface` pour les nœuds et interfaces.
- ComfyUI : `https://docs.comfy.org/custom-nodes/backend/more_on_inputs` pour les entrées facultatives.
- ComfyUI : `https://docs.comfy.org/basic-concepts/custom-nodes` pour la gestion et les mises à jour.
