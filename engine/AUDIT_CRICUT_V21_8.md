# SmartSVG Studio V21.8 — Audit d'import Cricut Print Then Cut

Audit du code V21.7.1 et de la documentation officielle Cricut consultée le 23/10/2026.

## Ce qui est réellement compatible

- Le PNG de fabrication est une image couleur RGBA : import **Flat Graphic / Imprimer puis découper** (une image avec ses découpes déduites du fond transparent).
- **Un seul PNG suffit** pour un sticker, sans SVG de contour superposé.
- Le SVG de contour est un fichier de **découpe seule** : aucune image couleur n'y est intégrée. Les SVG éditables de régions, lorsqu'ils existent, ne sont pas des calques sémantiques (yeux/cheveux/texte).
- Pour une planche, une seule image PNG permet d'imprimer plusieurs stickers, mais ceux-ci ne sont pas déplaçables indépendamment sans importer les PNG individuels.

## Problèmes identifiés et réponses

1. **Ambiguïté du choix de fichier :** V21.7.1 dispersait PNG, SVG de découpe et variantes HD dans plusieurs dossiers. V21.8 crée `00_IMPORTER_DANS_CRICUT` contenant seulement les PNG jugés utilisables après le précontrôle local, ainsi qu'un guide et un rapport.
2. **Îlots de découpe parasites :** un PNG peut porter plusieurs îlots alpha (à l'import, cela pourrait donner plusieurs découpes). Le contrôle refuse le statut prêt quand un sticker individuel a plusieurs îlots.
3. **Trous transparents :** les trous intérieurs du PNG peuvent se transformer en découpes indésirables; le statut prêt est refusé. Rien n'est rebouché silencieusement.
4. **Taille physique :** contrôle de cohérence dimensionnelle PNG ↔ millimètres demandés ↔ SVG contour, avec seuil de 0,2 mm. Design Space doit toujours être contrôlé après import, car les métadonnées ppp ne sont pas garanties d'être reprises.
5. **HD ≠ géométrie améliorée :** le PNG HD additionnel de V21.7.1 est conservé; le fichier conseillé pour la découpe est le PNG de fabrication, contrôlé et copié octet par octet. C'est une priorité à la fiabilité du contour.
6. **Planches A4 :** prévalidation prudente des planches jusqu'à 175 × 240 mm (ce n'est PAS la limite officielle ni une garantie). Nombre d'îlots attendu comparé au nombre d'objets.

## Périmètre des tests

- Test de bout en bout sur sticker synthétique : PNG d'import identique octet pour octet à celui du moteur précédent; autres sorties PNG/SVG inchangées.
- Test de 12 stickers synthétiques : 12 fichiers individuels, 1 planche avec 12 îlots; pas de double contour.
- Cas hostiles : masque troué, objets disjoints, alpha vide, lien symbolique, chemin externe, fichier utilisateur déjà existant, panne de l'interface accessoire.
- Aucune inférence SAM2/Florence-2, aucun lancement réel de Design Space, aucune découpe physique Explore 5 réalisés ici.

## Limites impératives

- Un PNG Flat Graphic n'est pas un SVG multicouche librement modifiable. Il peut être redimensionné, tourné, dupliqué, disposé et imprimé/découpé en tant qu'objet; pas édité par élément interne.
- Une image opaque sur fond complexe sans IA produit au mieux une **découpe rectangulaire**, même si l'export est valide pour Print Then Cut. Il faut un masque valide pour la découpe en silhouette.
- Le test logiciel examine la transparence des PNG; Cricut Design Space peut appliquer des règles ou seuils différents. Vérifier l'aperçu « couche unique », la taille physique et faire une découpe test.
- Les dimensions Print Then Cut dépendent de la machine, du papier et des proportions : Cricut Explore 5 sur A4 : vertical max. 26,98 cm, horizontal max. 18,3 cm, limites non simultanément maximales pour toutes les compositions.

## Références officielles

- https://help.cricut.com/hc/en-us/articles/38613592650903-How-to-Print-Then-Cut-with-Cricut-Explore-5
- https://help.cricut.com/hc/en-us/articles/360009556313-How-to-upload-images-into-Design-Space
- https://help.cricut.com/hc/fr/articles/360009429814-Quelle-taille-puis-je-imprimer-puis-d%C3%A9couper-nbsp
- https://help.cricut.com/hc/en-us/articles/360009553213-Image-uploads-unsupported-items

## Résultat additionnel sur les 7 exemples utilisateur

Les sept images ont aussi traversé le chemin Express CPU sans IA/masque (six essais sur miniatures <=620 px, le mème au PC sur miniature <=300 px). **Tous les sept** ont produit un PNG précontrôlable en tant que carte rectangulaire, et non un détourage de personnage. L'absence de masque est maintenant indiquée par `PRET_POUR_IMPORT_LOCAL_AVEC_CADRES`, `cartes_rectangulaires` et `CADRE_RECTANGULAIRE_SANS_DETOURAGE`. Cette passe ne remplace pas l'exécution réelle de SAM2 / Florence-2. Une des grandes miniatures a nécessité une réduction supplémentaire pour terminer dans les limites de temps du banc CPU.

La V21.8 ne revendique donc **aucune segmentation IA réellement mesurée sur les sept exemples** ; son amélioration vise la sécurité et la clarté des fichiers effectivement transférables à Design Space.
