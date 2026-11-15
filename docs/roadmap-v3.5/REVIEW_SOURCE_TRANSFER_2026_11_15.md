# Contre-expertise du transfert de sources — 15 novembre 2026

Deux relectures indépendantes en lecture seule du producteur, chacune bornée à son périmètre. Base candidate `a14667dbeb398fe82d6d801f890d430b50b67ade`. Aucune revue GitHub APPROVED fabriquée, aucun test produit, Windows, GPU, Design Space ou physique exécuté.

## Corrections de scénarios — reviewer review_hourly_source_closure

Verdict final reçu : **réparations documentaires publiables ; aucun défaut important non résolu dans les quatre rapports relus**.

Constats corrigés : oracles de mauvaise famille dans SC-02E/SC-02F2 ; conditions receipts/epoch insuffisantes ; float32 confondu avec resync ; diagnostic privé confondu avec consentement ; préférences/portabilité confondues avec reprise FAILED seule ; atomicité batch confondue avec fichier/ZIP. Les 106 oracles corrigés contiennent les conditions complètes de leur assertion et les précisions pertinentes. Une erreur intermédiaire de normalisation des IDs des scénarios et une extraction du titre à la place de l'attendu lot22 ont été détectées par le reviewer et corrigées avant publication.

Contrôle reçu : **259/259 IDs, assertions littérales et niveaux de preuve historiques conservés**, répartis101/56/52/50. Le reviewer a comparé les106oracles modifiés à leurs conditions d'origine. Les catégories F1 ne sont pas des propriétaires ; AST/ESM148/30 est un graphe au snapshot source.

| Fichier relu | SHA256 final |
|---|---|
| SOURCE_CLOSURE_SC02D_LOTS13_17_2026_11_15.md | 319525bc29a866a54fcf5825a04abbae241a4dd763f2fadefbc63aceef4e49a1 |
| SOURCE_CLOSURE_SC02E_LOTS18_22_2026_11_15.md | 50962ff65aa98aad724142869a27b47f5f8967cfd40e2eabf7fff49034cee907 |
| SOURCE_CLOSURE_SC02F1_LOTS02_04_2026_11_15.md | 4080bfb0183add544efcf99352cce8d37ca8022424830803e21ceb9dc42e3292 |
| SOURCE_CLOSURE_SC02F2_LOTS05_06_2026_11_15.md | 7c943a6d173d9478bcc6e36d1889950bea36d8d4e41acc1525298a598d1553c2 |

## Critères, DoD et contrôleur — reviewer review_full_source_register

Verdict borné final reçu : **acceptable, aucun défaut important non résolu dans les éléments relus**. Toutes les141précisions individuelles et les140lignes de tickets ont été lues. Les textes, lignes et empreintes source stockés ont été comparés aux fichiers locaux. Les conditions du rapport SC-03B concernant15opérations/troisUndo-Redo, prototypes par usage, mesures complètes et observation de trois parcours/deux erreurs sont conformes aux sources inspectées.

Corrections relues : W16_OCR/W16_DIORAMA remplacés par propriétaire W16 + capacité ; CP4/CP6 séparés comme gates ; attributions explicites S-020/W16 et S-088/W11 ; liens historiques qualifiés comme planification/coordination, parfois partiels ; prototype fabriqué par usage S-037. Le registre ne modifie pas les critères intégraux du contexte parent.

Le contrôleur et les requêtes par ID passent ; ID inconnu refusé. Le reviewer a exécuté neuf corruptions ciblées supplémentaires refusées : dossiers intervertis, acceptations supprimées/dupliquées, mauvais ticket/lot, lien ajouté, propriétaire inventé et référence manquante/hors dossier. Le producteur a exécuté six corruptions initiales et le cas de waiver de préservation non vide ; tous refusés après corrections. Ces essais concernent l'intégrité documentaire, pas le studio.

| Fichier relu | SHA256 final |
|---|---|
| SOURCE_TRANSFER_REGISTER.json | 6c5be2af77b43ea6a3a51fbc3e9e355993f78d82db1128f39834ed5ebe875cb5 |
| verify_source_transfer.py | 84f222f0bb0089aa938533de972ee14a3d9731d6133f5a46e2d3e432e8e7818d |
| SOURCE_CLOSURE_SC03B_CRITERIA_DOD_2026_11_15.md | d7a38d882eaf6aead4763962aeca4c5baa76786bf00a9feb59607e2a49f8a150 |

## Limites qui restent ouvertes

Ces verdicts ne sont pas la revue globale des25axes et ne constituent pas une seconde lecture exhaustive de tous les paragraphes contextuels et tests locaux des21lots source. Ils n'attestent pas non plus la provenance GitHub à eux seuls : les26blobs ont été comparés à l'arbre distant observé par le producteur, pas par les reviewers. Un SHA de commit syntaxiquement valide dans le registre n'est pas une attestation du HEAD actuel. Le contrôle de la règle de préservation est strict sur son texte ; sa bonne application reste humaine.

**SOURCE_CLOSURE reste ouverte pour acceptation finale au contexte intégral, puis GLOBAL_REVIEW au SHA fixé.** Le registre évite de recommencer les tableaux d'intitulés : examiner les contradictions de contexte restantes et les gates avec ce dossier de preuves. Toute modification d'un fichier relu exige nouvelle empreinte et portée de relecture correspondante. La publication sur la branche candidate ne signifie ni adoption, ni code intégré, ni validation externe.
