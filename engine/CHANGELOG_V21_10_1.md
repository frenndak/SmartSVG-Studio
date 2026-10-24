# SmartSVG Studio V21.10.1 — Journal des changements

- Mise en cache du raster de contours : un mouvement du pinceau ne redessine pas tous les anciens traits et ne relit pas 1,8 million de pixels à chaque événement.
- Indicateur de trait actif distinct (vert pour ajouter, orange pour retirer) ; recalcul fiable après validation, zoom, changement de sujet et annulation.
- Diagnostic multi-masques moins gourmand : compteur de chevauchements `uint8` exact jusqu'à 32 sujets.
- Confirmation à la fermeture implicite lorsque des corrections n'ont pas été sauvegardées.
- Restauration de la valeur précédente de `retouches_json` si le callback de sauvegarde échoue.
- Refus de sauvegarder en l'absence d'un masque d'aperçu correctement chargé ; avertissement à la limite de points d'un trait.
- Tests JS renforcés (cache, stockage, confirmation de fermeture), test Python avec 32 masques.
- **Inchangés** : nœuds ComfyUI / port MASK-IMAGE-STRING, format des traits, cinq paramètres Express, engines PNG/SVG/HD, dossier `00_IMPORTER_DANS_CRICUT`, workflows V21.10.
