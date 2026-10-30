# Décision de promotion proposée — SmartSVG V3.4

**Statut : PROPOSITION DE GOUVERNANCE (PR DRAFT). Ne prend effet qu'après intégration contrôlée.**

## Autorisation et sources
Le propriétaire a demandé explicitement le 30 octobre 2026 d'adopter intégralement la roadmap V3.4, après vérification. Cette proposition conserve les 141 obligations V3.3, sans ajouter de fonctionnalité ni prétendre que les tests spécifiés sont exécutés.

- Roadmap V3.4 : [dossier de conception](roadmap-v3.4/README.md), [traçabilité](roadmap-v3.4/23_TRACEABILITE_BACKLOG.md), [passation / arbitrages](roadmap-v3.4/24_CONTRE_EXPERTISE_PASSATION.md).
- Historique normatif intégral conservé : [V3.3 MASTER](ROADMAP_MASTER_v3_3.md), [TRACEABILITY](ROADMAP_TRACEABILITY_v3_3.md), [COVERAGE](ROADMAP_COVERAGE_v3_3.md), [HERITAGE](ROADMAP_HERITAGE_v3_3.md).
- Proposition documentaire à intégrer **avant cette PR** : #73 ; coordination #72.

## Contrat d'adoption (sans changement du périmètre)
Lorsque #73 est intégrée et que **cette PR de gouvernance** est elle-même intégrée et validée, V3.4 devient la référence d'**ordonnancement et de réalisation**. Tous les critères normatifs hérités des 101 S + 40 R33 demeurent obligatoires ; en cas de résumé incomplet V3.4, la formulation historique V3.3 fait autorité, sans régression ni report caché. Les tickets V34 sont des unités d'exécution et de suivi, pas de nouveaux gates bloquants.

Les 140 tickets et 437 tests V3.4 sont **SPECIFIE / NON_EXECUTE** par défaut, indépendamment des réalisations G3.3 et G4 déjà prouvées sur leurs propres PR. La promotion documentaire ne qualifie ni produit Windows, ni GPU RTX 3070, ni import Design Space, ni Cricut Explore 5 physique.

## Séquence d'intégration / contrôles requis
1. Vérifier la PR #73 au HEAD exact : 29 chemins sous `docs/roadmap-v3.4/`, couverture 141/141, 140 tickets uniques, liens de traçabilité cohérents et absence de contenu privé. Actualiser la branche face à `main` selon un plan non destructeur si nécessaire.
2. Obtenir les contrôles CI et une revue distincte sur #73, puis fusionner celle-ci dans une **session de mainteneur autorisée** sans forcer de protection.
3. Rebaser/actualiser **cette PR** sur le nouveau `main`; vérifier les liens internes et la présence des 24 lots. Valider que le changement `AGENTS.md` est uniquement une substitution de l'autorité documentaire, sans relâcher les protections.
4. Contrôler CI et revue de cette PR ; fusionner par l'intégration autorisée. **Ne jamais fusionner la PR de gouvernance avant #73** : ses liens seraient absents du `main`.
5. Informer le producteur horaire de lire l'autorité fraîche `AGENTS.md` à chaque cycle. Ne pas créer de nouveau producteur, ne pas modifier les automatisations dans cette PR.

## Réversibilité
En cas de régression de gouvernance, revenir sur le commit d'adoption `AGENTS.md` et ce dossier de promotion par un revert revu ; ne pas effacer le dossier V3.4 ni les roadmaps historiques. Les exports et données `.smartsvg` ne sont pas migrés par cette proposition.
