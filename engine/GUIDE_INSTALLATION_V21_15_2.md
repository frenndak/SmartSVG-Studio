# Installation SmartSVG Studio V21.15.2 (ComfyUI)

1. Sauvegarder le dossier de l'extension actuelle avant modification ; ne jamais supprimer les fichiers de projet/export utilisateur.
2. Fermer ComfyUI. Extraire le ZIP **en conservant son dossier** puis installer la copie de `ComfyUI-SmartSVG-Studio-V21.15.2` dans `ComfyUI/custom_nodes/`.
3. Éviter deux copies actives de SmartSVG en parallèle ; l'ancienne copie doit rester sauvegardée **hors de `custom_nodes`** pour éviter les conflits de registre.
4. Redémarrer ComfyUI et, au besoin, actualiser l'onglet (Ctrl+F5) pour charger le widget.
5. Charger `demos_v21152/01_Planche_12_escargots.json`, sélectionner l'image fournie dans `LoadImage`, puis exécuter le nœud `SmartSVGExpressV21152` en profil **Planche - 12 images (4x3)**, IA `Desactivee` (CPU).
6. Ouvrir le dossier affiché : `RAPPORT_V21_15_2.json` et `CONTROLE_V21_15_2.json` indiquent précisément les refus et les points à vérifier. Les fichiers PNG/SVG produits restent des brouillons tant qu'aucun contrôle humain/Design Space n'a eu lieu.
7. Pour une planche noire, ouvrir l'exemple `02_Planche_24_fond_noir.json` : le détecteur fond blanc doit refuser et laisser le moteur historique gérer les pixels de fond noir.
8. Revenir à V21.15.1 : fermer ComfyUI, retirer seulement le dossier V21.15.2, remettre le dossier sauvegardé V21.15.1, puis redémarrer. Ne pas effacer les productions de projets.

Avertissement important : utiliser le PNG Print Then Cut dans **Design Space** selon les étapes de la machine. Ne pas envoyer automatiquement un SVG d'édition ou le SVG de contour en superposition comme des traits internes.

Ce logiciel ne pilote pas la Cricut ; repères d'impression et coupe physique restent effectués via Design Space. La création d'un fichier ne prouve pas sa fabricabilité.
