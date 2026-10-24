# SmartSVG Studio V21.9 — Inspection à résolution native

## Périmètre

Inspecteur **non destructif** inséré **après** la correction de masques V21.6 / la QA V21.7 et **avant** Express V21.8. Les cinq widgets Express, ports de sortie, SVG/PNG de fabrication et dossier `00_IMPORTER_DANS_CRICUT` restent inchangés.

### Mode d'inspection

- Source RGB et masques enregistrés en PNG **à la dimension native** (`SmartSVG_Studio_Native_V219`). Pas de redimensionnement 760 px avant le zoom.
- Zoom centré sous la molette ou par boutons, panoramique en glissant, bouton `100 % natif` (un pixel source = un pixel CSS à DPR 1, hors limites d'affichage), `Adapter` et lecture des coordonnées réelles.
- La couche colorée représente les zones sélectionnées; les contours visuels sont approximatifs aux zooms < 100 %. Les frontières de découpe définitives restent celles des fichiers Cricut, non celles du navigateur.
- Les points de diagnostic conduisent automatiquement à une zone d'inspection : îlots détachés, trous intérieurs, chevauchements, contact avec les bords et passages étroits possibles.
- Inspecteur lecture seule : pour corriger, rouvrir V21.6, enregistrer et réexécuter. Les masques en sortie du nouveau nœud restent **les objets torch d'entrée, sans copie ni modification**.

### Consommation mémoire et confidentialité

- Budget de traitement : jusqu'à 5 Mp par image, 32 masques et 50 Mp cumulés, comme les contrôles historiques.
- Copie UI : 64 Mo maximum par session ; maximum 8 sessions ou 192 Mo stockés dans le répertoire des aperçus propres V21.9, suppression des fichiers vieux de plus de 48 h à la prochaine publication. Les fichiers inconnus ne sont pas supprimés.
- L'inspecteur ne garantit pas qu'une image IA est correctement détourée, ni que Cricut Design Space interprétera à l'identique les contours, ni le résultat d'une découpe physique.
- Les aperçus sont accessibles aux clients déjà autorisés à accéder au serveur ComfyUI. Ne pas exposer ComfyUI à Internet sans authentification.

### Tests en environnement CPU

- Nœuds : compatibilité d'enregistrement et des cinq réglages Express, préservation des références identiques aux masques et à l'image d'origine, masques partiellement transparents, limites d'entrée, exception d'aperçu, nettoyage et liens symboliques.
- Défauts : tests d'îlots détachés, trous, chevauchements, masque vide et rapports localisés en pixels natifs.
- Frontend : références de fichiers sécurisées, URL `/view` derrière `/comfyui/`, zoom avec ancrage, coordonnées pixels, bouton pour aller à une alerte, chargement de plusieurs sujets, widget non sérialisé.
- Production : test synthétique de 12 masques passant par V21.9 puis Express V21.8 et création du PNG Cricut.
- Les sept exemples réels ont des dimensions compatibles avec l'inspection native; les essais locaux sans inférence IA ne permettent pas de conclure à la qualité du détourage des sujets originaux.

## Vérifications réelles encore nécessaires

- Chargement et interaction dans le frontend ComfyUI actuel, y compris Nodes 2.0 et extensions tierces.
- Performance de visualisation et VRAM/RAM sur PC réel selon nombre de masques et fréquence de zoom.
- Détourage IA pour les sept images de référence et import final dans Cricut Design Space, suivis d'une découpe physique Explore 5.

Source développement ComfyUI : https://github.com/Comfy-Org/docs/blob/main/development/comfyui-server/comms_routes.mdx
