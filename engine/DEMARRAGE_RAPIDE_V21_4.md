# Démarrage rapide — SmartSVG V21.4

**1. Installer :** retirer l'ancien dossier SmartSVG de `ComfyUI/custom_nodes`, placer `ComfyUI-SmartSVG-Studio-V21.4`, redémarrer.

**2. Vérifier :** ouvrir `example_workflows/SmartSVG_Studio_V21_4_00_Diagnostic.json`. Cela ne lance pas de modèle IA.

**3. Créer :** ouvrir `...V21_4_01_Express_Simple.json`, choisir une image dans `LoadImage`, un projet, une largeur en mm, 300/450 ppp et une politique IA. Une image PNG de sortie à 450 ppp **ne crée pas des détails inexistants dans la source**.

**4. Pour les 24 Pokémon :** utiliser le workflow `...V21_4_02_Pokemon_24.json` et vérifier les fichiers individuels et les planches dans le dossier de sortie.

**5. Pour les renards :** workflow `...V21_4_03_Trois_Renards.json` (détection automatique) ou `...V21_4_04_Renards_Manuel.json` (zones explicites). Le détourage réel nécessite RMBG + modèles, et ne sera pas prouvé par le simple diagnostic GPU.

**6. Cricut :** importer l'image d'impression pour *Imprimer puis découper* et vérifier sa taille réelle dans Design Space. Les SVG de contours et les SVG « tous les traits » sont **des opérations différentes**. La version ne certifie pas le comportement de la machine physique.

**Compatibilité :** tous les anciens nœuds et workflows restent enregistrés ; pour les projets nouveaux, privilégier les trois nœuds `V21.4`.
