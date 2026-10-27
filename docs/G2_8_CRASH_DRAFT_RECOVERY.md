# G2.8 — Reprise automatique des brouillons de pinceau après interruption

## Comportement utilisateur

Dans l'éditeur de masques **V21.6** déjà intégré au parcours G2.3/G2.5, les coups de pinceau terminés sont désormais enregistrés automatiquement **dans le navigateur local**. Une opération Annuler/Rétablir actualise également ce secours.

Après un plantage, fermeture forcée ou rafraîchissement de navigateur, la réouverture du **même nœud**, avec **la même source et le même nombre/dimensions de masques**, propose une restauration **avec confirmation explicite**. Les retouches récupérées ne sont appliquées au widget du graphe qu'après action utilisateur sur **Enregistrer les retouches**. Aucune exécution ComfyUI automatique.

Le secours est volontairement supprimé lors d'un choix explicite **Fermer sans enregistrer**, d'un enregistrement réussi ou de l'action **Effacer les retouches enregistrées**.

## Sûreté et limites

- Brouillons limités aux traits structurés validés par le schéma V21.6 : **400 traits, 12 000 points, 350 Kio maximum**. Ni photo PNG originale, ni masques float32, ni modèles, ni nœuds ComfyUI ne sont sauvegardés dans localStorage.
- Clé locale liée à l'identifiant du nœud **et** à l'empreinte SHA-256 complète de sa source ; les dimensions/nombre de masques sont revérifiés à la lecture. Brouillons expirés après **7 jours**.
- En cas de navigateur refusant le stockage local ou de quota saturé, l'éditeur fonctionne sans secours : l'utilisateur doit sauvegarder régulièrement dans le nœud/projet.
- **Ce mécanisme n'est pas la sauvegarde automatique complète d'un fichier .smartsvg** ; les sauvegardes persistantes et les masques natifs continuent de dépendre des modules G1.3/G1.4/G2.2/G2.4 et de gestes explicites.
- Le stockage local de navigateur est lié au profil, à l'origine et à la politique de nettoyage du navigateur. Un changement d'URL ComfyUI ou de profil peut rendre le secours inaccessible.
- Un brouillon récupérable ne valide jamais les contours, l'import dans Design Space ni la découpe Cricut. Le test navigateur Windows avec vraie image reste L2/L3 non exécuté.

## Tests

`node --test engine/tests/test_g28_editor_drafts.mjs`, `node --test engine/tests/test_v216_runtime.mjs`, et `python -m unittest discover -s tests -p 'test_*.py' -q`.

PR empilée sur G2.7 #32 et G2.5 #24 : ne fusionner qu'après revue technique indépendante et intégration des parents. Risque d'intersection de fichier avec la branche de l'inspecteur G2.6b #28 : effectuer une résolution de conflit et des régressions avant intégration combinée.
