# G3.1 — Atelier Express plein écran : premier raccordement d'un outil réel

## Périmètre

Le prototype G3.0 affiche toujours 12 escargots fictifs pour la navigation. Ce lot **ne transforme pas une image PNG/JPEG/WebP en SVG** et ne connecte ni détourage IA, ni upscale, ni édition des masques.

Il expose dans la colonne de réglages un bouton **« Examiner un vrai SVG de contours »**. Un clic volontaire affiche le panneau **déjà existant** G2.7 (`smartsvg_cut_review_panel_g27.mjs`) utilisant le validateur G2.9 (`smartsvg_svg_path_grammar_g29.mjs`).

L'utilisateur peut alors, sur un SVG réellement généré ailleurs et conforme au sous-ensemble accepté :

- charger **localement** un fichier `.svg` de taille inférieure à 768 Kio ;
- vérifier la syntaxe des contours fermés, un `viewBox` cohérent et les dimensions explicites en millimètres ;
- visualiser et sélectionner/désélectionner jusqu'à 64 chemins de coupe ;
- télécharger un **brouillon** SVG ne contenant que les chemins choisis.

Le panneau réutilise la sécurisation de G2.7/G2.9 : refuse les éléments SVG actifs, attributs étrangers, scripts, ressources externes, unités non physiques et contours ouverts/malformés. L'export n'atteste pas l'absence de croisements géométriques complexes, ni la machine Cricut.

## Où tester

- **ComfyUI** : ouvrir le nœud Express et cliquer « Découvrir l'atelier complet » ; dans la nouvelle page Express, cliquer « Examiner un vrai SVG de contours ». Le navigateur charge le module `.mjs` **depuis la même origine** que la page ; le contrôle est hors serveur et n'exécute aucun graphe.
- **Aperçu HTML ouvert en `file://`** : la navigation fictive et l'import image restent utilisables, mais le nouveau bouton affiche clairement la limitation. Les importations de modules ES entre fichiers locaux sont interdites par la politique de sécurité de nombreux navigateurs ; ne pas contourner cette interdiction.
- Les liens de prévisualisation HTML tiers ne constituent pas une installation ComfyUI ; ils peuvent ne pas servir les modules voisins. Pour des SVG personnels, tester uniquement dans une page locale servie par ComfyUI, pas dans un proxy de prévisualisation externe.

## Contrats et sécurité

1. Le module d'inspection est chargé par `import()` **seulement après un clic** ; aucun module SVG n'est chargé au démarrage de la maquette.
2. Aucun SVG utilisateur n'est injecté brut dans le DOM de la maquette et aucune donnée utilisateur n'est transmise au serveur. Le contrôleur lit les données par l'API locale `File.text()`.
3. La planche fictive et les sélections du vrai SVG sont **deux états distincts**. Les cases « Tous/Aucun/1 sur 2 » de la démo ne pilotent pas les chemins de découpe.
4. Aucun `queuePrompt`, `fetch`, contrôle moteur IA ou opération destructive n'est appelé par le raccordement.
5. Le bouton fonctionne sans changer les IDs ComfyUI, la sauvegarde de projets, le moteur de masques, les sources figées ou la roadmap.
6. Le récapitulatif G3.1 ne remplace pas les vérifications manuelles Design Space/Explore 5.

## Validation

- `tests/test_g31_atelier_svg_bridge.py` : contrat d'affichage, absence de traitement caché, reconnaissance des modules et exécution des tests Node existants du contrôleur G2.7/G2.9.
- Le G0 exécute aussi la syntaxe du script inline HTML via `test_g30_atelier_preview.py`.
- Reste à vérifier **en navigateur réel sous Windows/ComfyUI** que le module `.mjs` est bien servi à la route de l'extension, puis importer un SVG produit par le pipeline sur GPU et confirmer l'export dans Design Space.

## Suite logique G3.2

Relier l'inspection des sujets et des fichiers `.smartsvg` au contexte de projet de l'interface (avec contrats existants G2.2/G2.6), puis seulement connecter le détourage/upscale local avec vrais médias tests. Cette PR ne prétend pas accomplir ces étapes.
