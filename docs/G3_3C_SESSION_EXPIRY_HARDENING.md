# G3.3c — Sessions de sélection : concurrence et expiration

Correctif **au-dessus de la PR #54**. À ne pas confondre avec la validation de tous les chemins produit ni avec le test réel ComfyUI.

## Problèmes reproduits
- Deux activations « Envoyer le dernier diagnostic » avant la résolution des imports ES pouvaient ouvrir des canaux différents (une ancienne session n'avait pas une propriété d'exclusivité).
- Le nœud révoquait sa session après 90 secondes mais l'Atelier conservait un bouton « Proposer » actif. Même lorsque le nœud ignorait le message, l'interface pouvait annoncer une proposition « réussie ».

## Contrat corrigé
- **Une activation à la fois** : verrou `shareInFlight` acquis **avant** le premier `await`, libéré dans `finally`. La confirmation et le renvoi se bloquent mutuellement. Une exécution nouvelle qui invalide `latest` n'est pas envoyée par une opération ancienne.
- **Une seule échéance partagée** : `createSelectionBinding` génère le champ `expires_at_ms` au moment du partage (90 secondes). L'échéance accompagne le rapport lié au nœud et la proposition du sujet ; le nœud vérifie la même limite lors de la confirmation.
- **Interface désactivée à l'expiration** : l'Atelier ne crée plus de bouton de proposition pour un rapport périmé, retire les boutons déjà affichés au timeout et refuse aussi les anciens boutons détachés cliqués ensuite. Les vignettes et zones G2.6 restent visibles en lecture seule.
- **Fail-closed** : données liées node/session sans échéance valable, expirées ou dont l'échéance a été modifiée = refus. Les rapports G3.3b historiques **sans lien exécutable** restent consultables.

## Tests ajoutés
- `engine/tests/test_g33_node_selection_ui.mjs` : clics Envoyer concurrents ; timeout ferme le canal et refuse les confirmations futures.
- `engine/tests/test_g33_subject_selection.mjs` : proposition et validation expirées, échéance falsifiée.
- `engine/tests/test_g33_subject_handoff.mjs` : rapports liés sans timestamp ou obsolètes refusés ; rapport simple non lié conservé.
- `tests/g33_ux_dom_smoke.mjs` : horloge simulée et bouton Atelier retiré à 90 s ; clic tardif ne déclenche pas de canal de proposition.

Les contrôles G0 / préflight HEAD / CPU + manifeste V21.15.2 sont requis avant toute intégration. Aucun changement de nœud Python, de masque float32, d'API projet, de fichier historique ou de roadmap V3.2. Windows, Playwright réel, RTX3070 et Cricut restent non qualifiés.

**Attention fusion :** ce correctif cible la branche de #54 et n'est pas destiné à être fusionné seul dans `main`, puisque le moteur de sélection G3.3c est encore dans cette PR parent.
