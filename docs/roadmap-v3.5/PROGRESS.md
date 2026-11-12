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

## 2026-11-12 — Contre-expertise COV-03 / COV-04 : défauts de couverture et première qualification explicite des scénarios

**Motivation :** demande propriétaire de vérification, contre-expertise, corrections, recherche d'erreurs et optimisation des travaux V3.5. Périmètre documentaire seulement ; V3.4 ACTIVE. Sources historiques inspectées sous `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`, V3.3 norme intégrale et lots V3.4 02/03/04/23.

### Constats et corrections concrètes
- [COVERAGE_V34_TO_V35.md](COVERAGE_V34_TO_V35.md) : **141 exigences**, **140 tickets**, **314 liens réciproques**, **0 arête unilatérale**, mais **10 exigences V3.3 sans ticket V34 explicite**, héritées G6/G9 (polices/licences/glyphes, OCR, gabarits métiers, dioramas multi-plans). Commit `5a7d53eb5acc216332cfd85c4cb8ebf3ce7dce62`.
- [COVERAGE_SCENARIOS_02_04.md](COVERAGE_SCENARIOS_02_04.md) : extraction des **19 micro-fiches** et des **52 scénarios des lots 02–04** ; **51/52** ont au moins un ticket source explicite, **1 scénario sans propriétaire direct : T-V34-03-16** (certification de coupe physique). Propriété à arbitrer sans falsifier le lot historique (V34-012/V34-003 candidats). Commit `56587e252a42aa53dc758c97d71d54f78368c47b`.
- [README.md](README.md) : correction de la mention historique des **437 scénarios déjà inventoriés**, lien vers la nouvelle matrice et visibilité explicite des fonctions héritées **texte/typographie/OCR** et **dioramas quatre plans**, sans les déguiser en nouveautés optionnelles. Commit `8d21201af942e50d7282f8f99374fcd1f583bf65`.
- Recettes testées : **aucune**. La vérification réalisée est un contrôle de documents/IDs et de références textuelles ; les tests Windows/RTX/Design Space/physiques restent axes distincts. Le fait de lier 51 scénarios à des tickets ne qualifie pas leurs 51 critères techniques.

### Prochain passage horaire à privilégier
1. Lire COV-03 et COV-04 avant de commencer ; **ne pas refaire** les 437 inventaires ni les 314 liens réciproques.
2. Confronter les exigences G6/G9 complètes aux critères et aux tickets V3.5 ; produire un vrai dossier de rattrapage de 10 obligations sans renuméroter arbitrairement les 140 tickets V34.
3. Continuer **COV-05** sur les lots 05–08 pour la relation explicite `scénario→ticket`, puis les autres lots en conservant le statut `NON_ATTRIBUÉ` lorsqu'il manque une ligne source.
4. Maintenir le développement Windows V3.4 inchangé, la confidentialité des sources et la promotion de gouvernance séparée.

**Conclusion de contre-expertise :** inventaire 24/141/140/80/437 conservé ; liens internes ticket↔exigence **314/314 réciproques**, **10 exigences héritées à raccorder**, scénario→ticket **51/52** sur le sous-ensemble 02–04. Aucun KPI « spécifié / implémenté / testé » gonflé.
