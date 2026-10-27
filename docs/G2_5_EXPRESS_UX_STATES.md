# G2.5 — Ergonomie Express : étapes, états et panneau projet contextuel

**Référence contractuelle :** roadmap figée V3.2 — lot **G2.5**, tickets **S-068** et **S-069**. Cette étape correspond à l'architecture d'écran, au traitement des états vides/chargement/erreur et à la contextualisation des commandes, et NON à la reprise automatique des graphes (prévue ultérieurement). Dépend de G2.4 #22 puis #21, #19, #18 et leurs parents. Aucun changement de moteur, API, nœud ou connecteur ComfyUI.

## Changements

- Parcours sémantique unique à quatre étapes **Image → Création → Traitement → Contrôle**, avec étape courante indiquée par aria-current="step" et description contextuelle. La liaison IMAGE et l'application du profil ont priorité sur l'affichage d'un succès.
- Contrôles avancés des projets repliés par défaut dans un panneau natif details/summary, accessible au clavier, sans dédoubler le DOM ni créer de bouton inerte.
- Présentation compacte sur des écrans de type 1366×768 ou plus petits ; répartition en quatre étapes lorsque l'écran est assez grand (1920×1080). Hauteur du panneau bornée à 72dvh et scroll vertical, sans écraser les contrôles ni déclencher l'export.
- État de projet déterministe : source seulement, retouches sans masques, masques sans retouches, source/masques/retouches cohérents, incompatibilité de fingerprint, archive récupérable ou erreur. Aucun état ne signifie « découpe Cricut validée » ni « graphe restauré ».
- Opérations réseau du sous-panneau projet explicitement occupées (aria-busy=true) ; les boutons sont désactivés pendant l'opération et les déclenchements concurrents sont ignorés. Un changement de projet efface les révisions précédemment ouvertes.
- Identifiant de champ projet distinct par nœud afin d'éviter les collisions dans des graphes comprenant plusieurs nœuds Express.
- Les résultats bloqués et les projets incompatibles conservent leurs avertissements. Les opérations de sauvegarde sont toujours explicitement déclenchées.

## Ce que ce lot ne fait pas

- Pas d'insertion automatique de nœuds, de rebranchement d'IMAGE/MASK, de chargement automatique des traits ni de file d'exécution.
- Pas de déclaration de fonctionnement **autonome sans graphe** : le projet repose encore sur ComfyUI. Les masques et retouches persistés dans G2.3/G2.4 se reprennent avec les nœuds de la chaîne actuelle.
- Pas de prétention de conformité aux gates utilisateurs T-02/U-01 sur navigateur Windows : la CI vérifie le modèle, les DOM simulés et les règles de largeur/hauteur. Une **recette manuelle réelle à 1366×768 et 1920×1080**, souris et clavier, reste obligatoire.

## Gates CI

- Tests Node.js du modèle G2.5 et du panneau Express via `tests/test_g25_express_ux.py`.
- Suites précédentes G1.5, G2.1, G2.2 et G2.3 conservées ; archive immuable V21.15.2 conservée ; CPU Smoke conservé.
- Aucune promotion en « prêt Cricut ». Aucune suppression des PR parentes ni fusion automatique.

## Suite roadmap

Selon la roadmap gelée, les prochains lots portent sur les retours d'erreur contextualisés, les prévisualisations synchronisées et la reprise d'activité (notamment G2.9). La réouverture assistée complète n'est donc pas déclarée livrée par G2.5.
