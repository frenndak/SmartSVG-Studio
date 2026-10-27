# G2.7 — Contrôle visuel et sélection des contours SVG dans Express

## Intention utilisateur

Compléter le parcours existant de la sauvegarde et de la reprise de projets SmartSVG par une étape visuelle **manuelle**, sans modifier les fichiers sources ni lancer ComfyUI automatiquement.

Dans le panneau **Projet .smartsvg** déjà intégré à Express (G2.5), une section « 5 · Contrôler les contours SVG » permet :

1. de choisir un **SVG local** produit lors d'une précédente exportation ;
2. d'inspecter la structure XML et les dimensions physiques en `mm` ;
3. de voir la géométrie des chemins sur un canevas local (Path2D, aucun SVG XML inséré dans la page) ;
4. de sélectionner/désélectionner des chemins séparément, par cases à cocher et, quand le navigateur le permet, au clic sur l'aperçu ;
5. de télécharger **volontairement** un SVG simplifié des seuls chemins sélectionnés, étiqueté `-brouillon.svg`, sans déclarer une découpe validée.

Cette étape exploite les contrôles déjà présents dans la pile G1.3 → G2.5 : sauvegarde atomique, récupération avec secours, conservation des masques float32 et retouches V21.6, parcours Express et état de reprise. Le présent lot ne modifie pas les nœuds ni leurs ports historiques.

## Cas d'usage

Une planche de **12 escargots** ou de **24 illustrations** contenant un chemin distinct par sujet peut être examinée et réduite à une sélection, tant que le SVG répond à ce contrat conservateur. Un dessin regroupant plusieurs éléments dans un seul chemin reste considéré comme **un seul objet** : l'outil ne sépare pas magiquement les sous-tracés.

## Restrictions et sécurité

- Lecture exclusivement **locale** du fichier : aucun envoi au serveur, aucun appel API IA, aucune exécution de script.
- Jusqu'à **768 Kio** de texte SVG et **64 chemins** ; présence de dimensions explicites en millimètres (1–300 mm) et d'un `viewBox` cohérent.
- Éléments admis : `svg`, `g`, `path`, `title`, `desc` ; attributs volontairement limités. Refus des liens, images externes, JavaScript, styles CSS, définitions, transformations et tout élément inattendu.
- Les tracés doivent contenir des commandes de géométrie et une fermeture `Z`. **Cela n'atteste pas** l'absence d'auto-intersections, la topologie, la surface minimale, le chevauchement, la taille de lame ou la capacité de la machine.
- Les courbes et chemins multi-segments sont **uniquement prévisualisés**. L'analyse statique complète de découpe et les tests physiques restent des portes distinctes.
- Les chemins sélectionnés sont réécrits avec des identifiants normalisés, sans conserver les attributs source ; sortie SVG **brouillon non certifié**.
- La sélection effectuée ici n'est **pas** encore synchronisée avec les masques de l'éditeur V21.6 ni avec une scène ComfyUI.
- Le navigateur doit prendre en charge `DOMParser`, `Path2D` et les API Canvas pour l'aperçu graphique. L'absence de `Path2D` conserve la sélection textuelle.

## État des 5 axes d'expérience

| Axe demandé | Travail existant | Situation actuelle |
| --- | --- | --- |
| Sauvegarder et récupérer | G1.3/G1.4/G2.2 : persistance, secours, inspection et confirmation | **Sauvegarde déclenchée par l'utilisateur** ; pas encore une sauvegarde automatique périodique des masques et traits |
| Retouches et masques conservés | G2.3/G2.4 : sessions de pinceau et captures float32 | Préservation candidate, reprise **manuelle** ; pas de réinjection automatisée du graphe |
| Interface Express unique | G1.5/G2.1/G2.5 | Accessible depuis le nœud Express ; dépend des PR parentes |
| Sélection visuelle | G2.6 : inspecteur de masques ; G2.7 : chemins SVG locaux | L'inspecteur G2.6 est une **branche distincte**, pas une fusion dans ce lot ; le nouveau panneau manipule des chemins SVG |
| Prévisualisation de découpe | **G2.7 : canevas Path2D local, mm et sélection** | Fonction candidate ici, **sans validation Design Space ou Cricut** |

## Vérifications

`node --test engine/tests/test_g27_cut_review.mjs` et `python -m unittest tests.test_g27_cut_review -v`.

Le wrapper Python exécute le test JS dans la CI publique G0 ; aucune dépendance supplémentaire n'est nécessaire à la CI. Les simulations DOM de Node.js ne constituent pas une recette d'interface Windows réelle. Les parents empilés doivent être qualifiés et intégrés dans l'ordre ; cette PR reste brouillon tant que les gates indépendants et tests matériels requis ne sont pas obtenus.
