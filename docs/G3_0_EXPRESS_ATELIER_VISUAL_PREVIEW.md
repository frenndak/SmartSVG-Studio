# G3.0 — Premier atelier Express en grand écran (aperçu interactif)

**Portée :** interface visuelle *locale de démonstration* pour obtenir rapidement un retour utilisateur sans exécuter de traitement IA ni prétendre valider une découpe Cricut.

## Ouverture

Ouvrir directement le fichier **`engine/web/js/smartsvg_express_atelier_preview.html`** dans Chrome/Edge/Firefox, par exemple après téléchargement depuis GitHub. Il ne requiert ni serveur, ni GPU, ni connexion Internet, ni module externe.

Lorsque cette branche sera installée sous ComfyUI avec `WEB_DIRECTORY='./web/js'`, le nœud Express inclura un bouton **« Découvrir l’atelier complet (aperçu interactif) »**. Cette commande tente d'ouvrir le fichier HTML statique dans un autre onglet depuis le répertoire Web de l'extension. La route statique dépend de la version de ComfyUI et devra être vérifiée sur le PC cible.

## Ce que l'on peut tester sans moteur

- cinq étapes visuelles : importer, nettoyer, sélectionner, découpe, exporter ;
- navigation depuis une barre latérale ;
- démo de 12 escargots **dessinés spécifiquement pour le prototype**, sélection/désélection de chaque sujet, tout / aucun / un sujet sur deux ;
- modes cible Basic Cut / Print Then Cut / SVG éditable : messages et réglages différenciés sans transformation de fichier ;
- aperçu de zoom, largeur en mm, choix DPI, ergonomie à 1366×768, 1920×1080 et mobile par CSS responsive ;
- import **local uniquement** de PNG/JPEG/WebP de moins de 12 MiB, via bouton ou glisser-déposer. L'image choisie est affichée avec une URL objet locale, invalidée au remplacement ; **aucun envoi ni segmentation n'est tenté**.
- navigation sans téléchargement de faux résultats.

## Ce que cette prévisualisation ne fait PAS

**Pas de détourage**, upscale, séparation automatique des 12 vrais sujets, IA locale, édition réelle de masques, chargement de projets `.smartsvg`, aperçu analytique de la topologie, sauvegarde serveur ni export de production. Ces fonctions existent partiellement dans les autres modules G1/G2 et doivent être raccordées ensuite via des contrats testables ; cet HTML n'est pas un substitut au workflow réel.

Les visuels d'escargots sont des exemples vectoriels simplifiés, pas une image de référence validée. Les dimensions présentées dans la démo ne sont **pas** calculées d'après les vecteurs dessinés.

## Choix d'architecture et de sécurité

- fichier unique auto-contenu, sans CDN ni dépendance tierce, utilisable offline ;
- les noms de fichiers utilisateurs sont injectés via `textContent` ; aucun contenu utilisateur n'est inséré comme SVG/HTML ;
- les radios n'exécutent rien ; le bouton final refuse explicitement un export en l'absence de moteur ;
- input limité à image/png/jpeg/webp, taille maximale 12 MiB et vérification de décodage navigateur ;
- bouton de navigation dans ComfyUI seulement après clic explicite (window.open), sans queue ni écritures invisibles.

## Prochain lot recommandé

1. Revue visuelle directe par l'utilisateur (captures et ergonomie, densité/contraste).
2. Extraire la couche état/commandes de cette prévisualisation vers un module testé de navigation.
3. Raccorder l'import réellement normalisé (orientation EXIF, espaces couleur, alpha), le routeur de projets et l'affichage d'inspection G2.6/G2.7 à une UI principale ; conserver les opérations destructrices et GPU explicitement déclenchées.
4. Recette de bout en bout Windows/ComfyUI puis Design Space/Explore5.

Cette branche se base sur le candidat **PR #38**, qui reste **DRAFT** et non fusionné. La roadmap V3.2 et les 651 hashes historiques sont préservés.
