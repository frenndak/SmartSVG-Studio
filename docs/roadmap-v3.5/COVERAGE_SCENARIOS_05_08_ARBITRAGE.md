# COV-05B — Arbitrage des cinq scénarios sans ticket explicite (candidate V3.5)

**13 novembre 2026.** Statut : **SPÉCIFIÉ POUR RAPPROCHEMENT, NON ADOPTÉ**, aucune preuve d'exécution. Suite de [COV-05](COVERAGE_SCENARIOS_05_08.md). Source V3.4 sur main : `06_COMMAND_BUS.md` blob `074879c0729042a77e8addc60b8c9446c176c183`, `07_UX_EXPRESS_NAVIGATION.md` blob `0846d31a7bd3b0c719423ee585e2ab8721dcbb76`. Leurs tables de tickets, lignes 212–220 et 226–234, ne citent pas explicitement les cinq tests ci-dessous. **Ne pas réécrire les sources.**

## Décisions sémantiques proposées, non assimilées à des liens historiques explicites

| Scénario | Texte historique conservé | Raccord candidat / justification | Décision / statut |
|---|---|---|---|
| T-V34-06-22 | 50 sujets partitionnés en packs V2 ; aucun pack V1 >32, IDs uniques | V34-036 (orchestration), V34-035 (groupes atomiques) et **V34-025..031** (contrat V2, à confirmer individuellement) | **RACCORDER**, dépendance V2 **non implémentée par la spec** ; pas de ticket source explicite |
| T-V34-06-24 | Score/Draw/Print jamais convertis en CUT par Undo/Redo | V34-035 (patches/Undo) + V34-032 (validation de commandes), et V34-049 (légende UI, non autorité des opérations) | **AMÉLIORER** V34-035, test de préservation du rôle ; lien proposé |
| T-V34-06-25 | rapport expurgé sans chemin privé ni média/poids IA | V34-040 (banc et rapports), V34-037 (UI événements), politique de confidentialité transversale à contrôler | **RACCORDER** V34-040, avec gate de non-divulgation ; lien proposé |
| T-V34-07-16 | Undo groupé Score+Cut ne promet jamais annulation physique | V34-038 (UX Undo), V34-049 (opérations), V34-035 (historique) | **AMÉLIORER** l'UX existante ; aucune commande physique annulée |
| T-V34-07-25 | navigation 100 fois, p95 <150 ms mesuré | V34-041 (AppShell), V34-046 (navigation) | **RACCORDER** benchmark Windows, seuil cible non mesuré |

**Contre-avis :** créer cinq nouveaux tickets V35 serait un doublon des responsabilités existantes ; déclarer cinq liens « EXPLICITES_SOURCE » serait faux. La matrice COV-05 demeure **103/108 explicites**, plus **5/5 propositions argumentées en attente de revue**. Les exigences G6/G9 sans ticket restent 10 ; le scénario T-V34-03-16 reste sans attribution explicite.

## Contrats et garde-fous de validation

- **06-22 :** aucune mutation de `.smartsvg` V1 pour y faire entrer 50 sujets ; segmentation V2 seulement après migration autorisée, vérification SHA/CAS, identités et masques float32 ; packs déterministes et sans collision ; Undo atomique dans les limites du writer réel.
- **06-24 / 07-16 :** l'opération CUT/SCORE/DRAW/PRINT/FOIL est une identité sémantique, pas une couleur ni une propriété de preview ; Undo/Redo restaure le groupe et ses rôles, jamais une découpe déjà effectuée.
- **06-25 :** expurger chemins, noms de fichiers, métadonnées EXIF, médias, prompts et poids IA avant sérialisation ; aucun rapport réseau implicite. Un hash peut être identifiant indirect et doit être examiné avant partage.
- **07-25 :** mesurer sur Windows réel, 1366×768 et DPI 200 %, navigation clavier/focus et lecteur d'écran ; échantillons horodatés, matériel, SHA, p95 et mémoire. 150 ms est une **cible**, pas un résultat.

## Deux parcours et UX

**Novice :** importer, sélectionner Score+Cut, prévisualiser, appliquer une modification réversible puis Undo ; constater les deux rôles inchangés, et un message français « L'annulation ne modifie pas une découpe déjà réalisée ». Si session en conflit, lecture seule et reprise explicite. Un rapport de diagnostic se prévisualise avant écriture externe.

**Expert :** préparer 50 sujets avec aperçu virtuel et progression, examiner les packs proposés sans accepter de migration V2 implicite ; contrôler les IDs et opérations, interrompre sans projet partiellement publié, reprendre sur receipt durable. Navigation rapide et accessible au clavier ; exporter un rapport expurgé après inspection.

**États UI :** vide, préparation, proposition prête, conflit/recovery, erreur ; action locale réversible sans popup, confirmation proportionnée avant écriture de pack ou rapport. Aucun nouveau store, writer, exporteur ou moteur IA. Pour cette fiche, IA/GPU/Design Space/physique sont **axes de vérification séparés**, pas des dépendances d'exécution de la documentation.

## Tests proposés (NOT_RUN)

1. Positif : 50 identités uniques, partition valide sous plafond V1, et aucun pack V2 publié avant consentement/migration.
2. Positif : Undo/Redo groupé conserve exactement les opérations et les identités de couche, puis compare le SHA avant/après retour à l'état initial.
3. Négatif : 33 sujets dans snapshot V1 → rejet sans écriture.
4. Négatif : IDs dupliqués entre packs → rejet et rapport sans fuite de noms.
5. Négatif : export diagnostic avec chemins, EXIF, prompts ou modèle local → fuite détectée, export bloqué.
6. Négatif : annulation après découpe réelle → UI ne promet jamais de retour matériel.
7. Crash, disque plein, CAS concurrent, ACK perdu → état non ambigu, pas de retry aveugle, rollback/recovery via writer existant.
8. Windows : 100 navigations, p95, focus, DPI, contraste et motion réduit, logs exact-SHA. Design Space versionné et coupe physique : **NOT_RUN / hors preuve de ce rapprochement**.

**DoD documentaire :** revue humaine des cinq propriétaires candidats contre les fiches détaillées et les 25 axes du contrat, puis décision explicite de marquer `RAPPROCHÉ_SÉMANTIQUE` (jamais `EXPLICITE_SOURCE`). DoD produit : tests PASS non-SKIP par axe, preuve Windows et matérielle lorsqu'exigée. Aucun de ces DoD n'est satisfait par cette publication.

**Prochain lot unique :** COV-06, scénarios 09–12, liens source explicites et exceptions, en conservant la matrice 05–08 intacte jusqu'à revue.
