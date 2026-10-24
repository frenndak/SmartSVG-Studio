# SmartSVG Studio V21.10 — Inspection et retouche native dans un seul éditeur

## Installer sans conflits

1. Quitter **ComfyUI**. Sauvegarder les workflows personnalisés et les fichiers PNG/SVG de projets existants.
2. Déplacer l'ancien dossier SmartSVG hors de `ComfyUI/custom_nodes` ; **ne pas laisser plusieurs versions de SmartSVG installées en parallèle**.
3. Extraire le dossier `ComfyUI-SmartSVG-Studio-V21.10` depuis l'archive ZIP dans `ComfyUI/custom_nodes/`.
4. Redémarrer ComfyUI et rafraîchir l'interface (`Ctrl+F5` si nécessaire).
5. Charger un exemple dans `example_workflows/SmartSVG_Studio_V21_10_*.json`.

## Ce qui change

Un nouveau nœud **SmartSVG V21.10 — corriger + inspecter (natif)** remplace *dans les nouveaux workflows seulement* la succession des anciens nœuds d'éditeur V21.6 et d'inspection V21.9. Les anciens nœuds et leurs workflows restent installés et utilisables.

Le nœud reçoit `IMAGE` et, de préférence, `MASK` (`masque_base`), puis produit `masques_corriges` (MASK), `image_source` (IMAGE), `diagnostic_json` (STRING).

Le bouton **Inspecter + corriger les contours** apparaît après une première exécution. Une seule fenêtre propose :

- vue haute résolution de l'image source et du masque sélectionné, zoom **100 % natif** et jusqu'à 1 600 % ;
- déplacement, molette, pinceaux **Ajouter** et **Retirer**, choix du sujet ;
- alertes localisées sur les trous, îlots, bords et chevauchements ;
- **Annuler / Rétablir**, sauvegarde ou fermeture sans enregistrer.

Les coups de pinceau sont sauvegardés dans le champ `retouches_json` du workflow. **Après Enregistrer, relancer le workflow** pour appliquer les corrections Python en pleine résolution et recalculer les alertes. L'aperçu est une simulation visuelle; l'export Python fait foi aux bords des traits.

## Quels workflows utiliser ?

- `...V21_10_01_Capture_Manuel.json` : capture recadrée **sans masque initial**. À la première exécution, l'export Express est désactivé volontairement. Dessiner puis enregistrer le masque, et **réactiver Express** pour fabriquer le sticker.
- `...V21_10_02_PNG_Alpha.json` : illustration PNG avec transparence. Le nœud natif **InvertMask** renverse le MASK provenant de `LoadImage`, conformément à la convention alpha de ComfyUI. Ne pas le conserver sur un masque de segmentation IA déjà orienté vers le sujet.
- `...V21_10_03_Planche_12.json` : une planche multi-sujets, avec préparation des masques automatiques via `SmartSVGInstancesV2151`. **Vérifier les 12 objets**, car leur bonne segmentation n'est pas garantie pour une image inconnue.

## Cricut Print Then Cut

1. Exécuter le workflow avec un masque correct et Express activé.
2. Ouvrir le dossier de sortie du projet, puis **`00_IMPORTER_DANS_CRICUT`**.
3. Importer uniquement le PNG voulu dans Cricut Design Space comme **image aplatie / Imprimer puis découper** ; ne pas superposer un SVG de découpe à ce PNG.
4. Vérifier visuellement **la silhouette, la taille en mm, l'absence de trous imprévus, la disposition dans la zone imprimable** ; respecter les repères d'impression Cricut.
5. Faire une découpe d'essai sur papier ordinaire avant le support final.

**Important :** ce système n'impose aucun résultat identique dans les détails internes d'un SVG multicalque. Le PNG reste une image aplatie, que Design Space peut dupliquer/redimensionner, mais dont chaque élément interne n'est pas éditable individuellement.

## Contraintes et dépannage

- IMAGE <= 5 Mp ; maximum **32 sujets**, **50 millions de pixels de masque cumulés**.
- Jusqu'à 400 traits / 12 000 points / 350 Ko de corrections par workflow.
- Les aperçus natifs temporaires sont publiés dans `ComfyUI/output/SmartSVG_Studio_Native_V219` ; ils peuvent être purgés lors de traitements ultérieurs. Les exports de fabrication ne sont pas affectés.
- En cas de changement d'image ou de segmentation, la correspondance des retouches est volontairement invalidée : effacer/recréer les anciennes retouches au lieu de les réappliquer au mauvais dessin.
- Si l'aperçu échoue, regarder le `diagnostic_json` et les sorties MASK/IMAGE ; un souci de panneau n'invalide pas le calcul des fichiers.
- L'éditeur et le mode **Nodes 2.0** demandent encore un essai dans **ton** ComfyUI. Les tests frontend actuels utilisent un navigateur simulé ; aucun essai physique sur Cricut Explore 5 n'a été réalisé.

## Auto-vérification facultative

Dans le dossier de l'extension :

```bash
python verify_package_v2110.py --integrity-only
python verify_package_v2110.py --javascript   # Node.js 18+ requis seulement pour les tests
python verify_package_v2110.py --run-all      # suites Python séparées
```

Les dépendances Python du projet doivent être présentes dans l'environnement ComfyUI. L'interface normale n'exige **pas** Node.js.
