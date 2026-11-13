# COV-18A-2a — Revue hostile des liens A02/A03/A04/A08/A12/B09 (13 novembre 2026)

**Statut : AUDIT DOCUMENTAIRE PARTIEL — AUCUNE CERTIFICATION.** La V3.4 reste normative. Ce document complète COV18A1 et COV18A1B sans recopier les 30 lignes. Source relue : lot 23 V3.4 sur main, COV18A1, COV18A1B, COV17A et contrat qualité V3.5. Les critères **intégraux** des sources V3.3 et les DoD locaux ne sont pas encore vérifiés dans cette passe : le présent audit ne prétend donc pas clôturer COV-18A-2.

## Six confrontations indépendantes

| UX | Source lot 23 : exigence → tickets → test transversal | Contre-expertise du périmètre | Décision candidate et preuve encore nécessaire |
|---|---|---|---|
| A02 | S-070 → V34-075/V34-132 → T-V34-22-04 | « Sélection directe et croisée sujets↔vignettes » ne démontre ni lasso libre, ni ellipse, ni alternatives clavier ; strokes.py est un port raster, non une preuve d'interaction unifiée | **RACCORDER**, sans inventer de ticket : DoD exige test UI réel clic/lasso/ellipse, sélection par subject_id, focus et Undo |
| A03 | R33-006 → V34-028/V34-133 → T-V34-22-04 (association COV18A1 à confirmer dans critère R33) | Masque float32 et Subject ne démontrent pas union/intersection/soustraction/inversion, ni préservation des trous | **RACCORDER** sous brouillon non mutant ; fixture deux îlots et un trou, comparaison de topologie et SHA avant/après Undo |
| A04 | S-007 → V34-069/110/007/071/082 → T-V34-22-05 | « Validation sémantique du sujet désiré » ne prouve ni reconnaissance automatique, ni fiabilité de la confiance, ni consentement modèle | **RAFFINER** : proposition CPU/manuelle d'abord ; téléchargement IA explicite, alternatives visibles, rejet résultat périmé |
| A08 | S-016 → V34-089 → T-V34-22-05 | « HD conditionnelle + diagnostic » n'autorise pas la promesse de détail reconstruit ; auto_hd CPU produit des dérivés | **RAFFINER** : afficher facteur, méthode et limites ; métriques sur fixture avec bord alpha, pas de score inventé |
| A12 | S-032 → V34-098/129/112 → T-V34-22-01 | « Export SVG édition vs fabrication » ne garantit ni centerline ni quatre exports fonctionnels ; groupes couleur ≠ couches CUT | **AMÉLIORER** : quatre rôles séparés (PNG PTC, SVG Basic Cut, SVG CUT multicouche, SVG éditable), prévol par rôle, provenance et mm |
| B09 | S-036 → **aucun V34 direct** → test V3.3 à relier | Contrat texte/police/glyphes non couvert par la présence d'un canvas objets ; persistance texte V1 non autorisée implicitement | **BLOQUÉ G6/G9** : brouillon texte réversible seulement ; ADR + revue propriétaire avant schéma/persistance, tests polices/licences/reprise |

**Divergences relevées :** les tests T-V34-22 sont des recettes transversales et non les tests locaux du geste. A02 et A03 ne doivent pas être déclarés « implémentés » à partir du seul writer de masque. B09 ne peut pas hériter par proximité d'un ticket V34-133 de canvas pour prétendre couvrir S-036. Aucun des six n'est certifié. Les 24 lots, 141 exigences, 140 tickets, 80 UX et 437 scénarios demeurent les univers historiques ; 431/437 liens source explicites, six exceptions et dix G6/G9 sans ticket direct restent ouverts.

## Contrat de validation candidat, non exécuté

**Entrées** : projet .smartsvg V1, source SHA-256, subject_id, mask_id, masque float32 dimensions px, révision attendue ; pour SVG, viewBox et dimensions physiques mm ; pour texte, licence de police et jeu de glyphes explicités. **Sorties** : aperçu isolé du projet, résultat typé par rôle, diagnostic tri-state ; aucune mutation du writer sans CAS. Les noms d'API futurs ne sont pas prescrits avant inspection des consommateurs actuels.

**Transition** : ouvrir projet@SHA → sélectionner sujet → calculer brouillon → comparer avant/après → Undo/Redo → prévol → vérifier expected_revision → commit uniquement par writer existant ou rester en brouillon. Résultat asynchrone tardif = rejet ; erreur de persistance = restauration de la dernière version saine.

**Scénario positif** : fixture libre avec deux sujets et un trou ; sélection par ID, opération locale réversible, sauvegarde autorisée, réouverture et égalité des identités/masques. B09 ne franchit pas la sauvegarde sans ADR approuvé.

**Négatifs** : N1 révision concurrente → conflit CAS sans écriture ; N2 trou absorbé ou dimensions float32 incohérentes → refus sans altérer la source ; N3 SVG actif/NaN/units ambiguës → prévol FAIL ; N4 police sans licence/glyphe manquant → avertissement, aucune substitution muette ; N5 provider absent ou consentement refusé → zéro réseau, fallback manuel ; N6 OOM/annulation/crash/disque plein → pas de publication partielle ; N7 Undo après sélection sur mauvais subject_id → aucune mutation.

**UX** : novice, geste direct et correction visible ; expert, identité/SHA/units/diagnostics. Focus clavier, contraste, mouvement réduit, 1366×768 et DPI 200 % : tests Windows futurs. Performance : instrumenter p50/p95, RAM et VRAM avant de fixer des seuils. **Tests exécutés dans cette passe : 0** ; auto non-skip, UI Windows, GPU, Design Space et coupe physique = NOT_RUN. Aucun téléchargement, fixture privée ou modification produit.

**TDD futur** : 1. tests contractuels CAS/ID/Undo ; 2. booléens float32/topologie ; 3. preview et rôles export ; 4. consentement IA et typographie ; 5. UI Windows accessibilité ; 6. validation Design Space et physique séparée. Aucun développement autorisé dans cette mission.

## Contrôle des 25 axes

01–05 inventaires conservés, certification ouverte ; 06 statuts disjoints ; 07 CAS/float32 ; 08 quatre exports ; 09 opérations machine UNKNOWN sans revendication ; 10–12 UX/accessibilité à tester ; 13 crash/concurrence/Undo ; 14 IA facultative ; 15 alpha/HD ; 16 SVG/topologie ; 17 Fabrique/batch **non applicable à ces six gestes**, héritage maintenu ; 18 Smart Delivery **non applicable ici**, hérité ; 19 opportunités #141 **hors arbitrage de cette fiche**, conservées ; 20 mesures futures ; 21 licences/fixtures ; 22 branche documentaire uniquement ; 23 aucun second writer/store ; 24 revue/CI/promotion non acquises ; 25 aucune réduction de critères. Les critères intégraux V3.3 et DoD V34 doivent encore être lus et confrontés avant tout changement de statut.

**Prochaine action unique : COV-18A-2b** — retrouver les critères V3.3 intégraux et les DoD locaux exacts pour ces six IDs, citer fichiers et lignes, puis qualifier leurs scénarios T-V34 locaux ; étendre ensuite aux 24 autres sans certification prématurée.
