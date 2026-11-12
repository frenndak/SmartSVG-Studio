# Journal de conception — SmartSVG V3.5

## 2026-11-12 — Initialisation contrôlée

- **Version** : V3.5 candidate, non normative ; V3.4 reste la référence des producteurs de code.
- **main de référence historique** : `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`.
- **Branche candidate** : `roadmap/v3-5-design-candidate-20261112`.
- **Issue canonique** : [#142](https://github.com/frenndak/SmartSVG-Studio/issues/142) ; sources #141 (enrichissements, Smart Delivery V1/V2) et #134 (80 UX).
- **Actions réalisées** : lecture de la politique AGENTS et de la promotion V3.4 ; inventaire extraction des tables : 24 lots, 141 exigences, 140 tickets, 80 UX, IDs uniques ; constitution de la nouvelle photographie sans toucher aux sources V3.4.
- **Tests produits** : AUCUN dans cette opération ; aucune certification Windows/GPU/Design Space/coupe physique.
- **Tests d'intégrité documentaire** : dénombrement/exclusivité des IDs V3.4/UX et des liens vers 24 lots contrôlés dans la session de préparation ; traçabilité exhaustive des 437 recettes **ouverte**.
- **Travaux V3.5 restant à faire** : matrice sémantique exigence par exigence, liens aux 437 scénarios, étude des 80 UX, micro-tickets V35 nouveaux, critères d'acceptation E2E, architecture UX, plans de test, ADR, revue et promotion.
- **Prochaine action à portée d'un cycle** : qualifier la méthode d'héritage et les vérifications automatisables, confronter V3.4 à #141 et #134 sans dupliquer le contenu. Reprendre les fiches Smart Delivery SD-V1/SD-V2 déjà publiées, puis SD0/SD1 et l'ensemble des autres fonctions selon les dépendances. Débuter la matrice `COVERAGE_V34_TO_V35.md` sans annoncer 100 % de spécifications rédigées.

**Règle de suivi :** une entrée de journal référence un changement/une preuve réelle. Pas de répétition de statut ni de relecture exhaustive sans cause ; jamais de pass mécanique pour cocher un ID.

## 2026-11-12 — Exécution manuelle immédiate, inventaire exhaustif des 437 scénarios

- **Déclenchement** : demande explicite propriétaire d'exécuter maintenant la tâche horaire V3.5 ; l'exécution a été acceptée sans création d'une tâche supplémentaire ni changement de calendrier. Travail documentaire poursuivi directement dans cette conversation.
- **Référence source** : `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`, 21 documents sources des lots 02 à 22. Les lots 01 et 23/24 ne contiennent pas de nouveaux tableaux T-V34 identifiés.
- **Livrables effectivement créés et commits** :
  - [SCENARIOS_V34_02_08.md](SCENARIOS_V34_02_08.md) : **160 IDs**, commit `a823f0eb0c8311cd57f438ebf1c243937595aa7a`.
  - [SCENARIOS_V34_09_16.md](SCENARIOS_V34_09_16.md) : **208 IDs**, commit `fbd4b1e6c2ab63a6829432279ae4ef71d6c0c1cf`.
  - [SCENARIOS_V34_17_22.md](SCENARIOS_V34_17_22.md) : **69 IDs**, commit `6b2ed78f483ddab8997ba0dbca5f6116cfb7851f`.
  - [SCENARIOS_V34_INDEX.md](SCENARIOS_V34_INDEX.md) : inventaire central 21 lots, commit `fc492941174150fbd560592312dbc69a920c3a61` ; README lié en commit `f637b85c11d938ae2b5d388b1266c7889aea7788`.
- **Contrôles exécutés à l'écriture et relecture** : source IDs de chaque lot vérifiés avec décompte attendu et séquence 01..NN ; relecture des trois documents publiés → **160+208+69 = 437 IDs distincts**, 21 lots représentés, aucun doublon ni trou. SHA du fichier historique et numéro de ligne d'origine conservés ; texte complet de chaque ligne source copié, sans supprimer ses axes de test.
- **État de couverture HONNÊTE** : `INVENTAIRE_ID_ET_TEXTE = 437/437` ; `RATTACHEMENT_SÉMANTIQUE_AUX_EXIGENCES_ET_TICKETS = OUVERT` ; `TESTS PRODUITS EXÉCUTÉS PAR CE PASSAGE = 0`. Les 141 exigences, 140 tickets, 24 lots et 80 UX restent conservés par le registre initial, mais leurs critères détaillés ne sont pas tous requalifiés dans V3.5.
- **Gouvernance** : branche candidate uniquement ; aucune PR documentaire, aucun merge, aucune modification de code, roadmap active V3.4, tâche de développement ou règle AGENTS. Les 25 contrôles anti-perte restent applicables.
- **Prochaine micro-action PRÉCISE** : commencer `COVERAGE_V34_TO_V35.md` en reliant les 437 scénarios à leurs exigences et tickets, **sur preuves sources explicites**, en traitant d'abord les lots 02–04 et les références du lot 23 ; marquer `À RAPPROCHER` chaque relation qui serait inférée du seul numéro de lot. Ne pas recommencer l'inventaire ni annoncer prématurément une conformité V3.5 intégrale.
