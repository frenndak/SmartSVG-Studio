# SmartSVG Studio — G3.3a : préinstallation, qualité et ergonomie

Le propriétaire souhaite améliorer la fiabilité de l'interface avant un essai manuel sous Windows/ComfyUI. Ce lot corrige des défauts comportementaux dans la maquette Express tout en conservant les vrais panneaux G3.1 SVG et G3.2 .smartsvg.

## Défauts corrigés

1. Lien d'ouverture : un window.open avec noopener peut renvoyer null après ouverture réelle. L'accès se fait désormais par une ancre HTML native en nouvel onglet, avec rel noopener noreferrer et navigation au clavier.
2. Navigation : six étapes explicitement nommées, dont Retouches. Sur mobile, leurs noms restent visibles dans une barre horizontale défilante ; les boutons disposent d'étiquettes accessibles.
3. Réinitialisation : le bouton de sélection ne fait plus perdre l'image importée. Le retour à la démo entière reste un bouton distinct. Les choix de sujets fictifs sont désactivés après un import réel non analysé.
4. Chargements concurrents : toute nouvelle tentative d'import, même invalide, invalide les anciens onload/onerror. Les images décodées à contretemps ne remplacent pas la source choisie en dernier.
5. Sécurité mémoire : fichier PNG/JPEG/WebP non vide de 12 Mio maximum, image décodée sous 20 millions de pixels, rejet sans détruire l'aperçu précédent. Ce seuil vaut uniquement pour cette maquette.
6. Messages honnêtes : une source importée reste NON SEGMENTÉE ; ses mm fictifs ne sont pas présentés comme appliqués. L'export SVG de G3.1 reste un brouillon distinct, jamais une découpe Cricut certifiée.

## Tests de régression

- tests/test_g33_express_ux.py vérifie noms accessibles, six étapes, lien sécurisé, absence de traitement automatique et robustesse de l'import.
- tests/g33_ux_dom_smoke.mjs simule navigation, boutons, import successif, erreurs de décodage, refus d'image trop grande et impossibilité explicite du mode file:// pour modules ES.
- G0, préflight HEAD, CPU et manifeste historique V21.15.2 sont requis avant fusion.

## Conditions restant ouvertes

Les tests DOM synthétiques ne sont PAS un navigateur graphique réel. Un essai Chrome/Firefox sous ComfyUI Windows sera encore requis à 1366×768, 1920×1080 et 390 px, avec clavier, chargement des modules JS, PNG/JPEG/WebP, gestion G2.2 et inspecteur G2.9. La recette GPU RTX3070, Design Space et Cricut Explore5 n'est pas faite.

Décision : intégrer uniquement comme correction de qualité UI expérimentale si la CI confirme son HEAD et la fusion synthétique. G3.3b devra ensuite relier les vraies données G2.6 de sujets et de masques à la planche.