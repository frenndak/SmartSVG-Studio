# SOURCE_CLOSURE — décision d'acceptation conditionnelle (15 novembre 2026)

## Portée et verdict

**Verdict : ACCEPTATION CONDITIONNELLE, pas DONE.** Le transfert littéral et les réparations d'oracles sont recevables comme *preuves documentaires bornées*. La revue indépendante ne couvre pas tous les paragraphes contextuels et tests locaux des 21 lots ; une conformité sémantique intégrale ne peut donc pas être certifiée. Cette fiche ne modifie ni les 141 critères, ni les 140 DoD, ni les 437 assertions, ni les 80 UX. Elle ne constitue aucune preuve d'exécution produit.

Sources consultées : `RUN_STATE.json`, `SOURCE_CLOSURE_SC03B_CRITERIA_DOD_2026_11_15.md`, `REVIEW_SOURCE_TRANSFER_2026_11_15.md`, `EXECUTION_PLAYBOOK.md` et fin de `PROGRESS.md` ; main observé par API `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`. La branche candidate doit encore être figée et son HEAD attesté avant GLOBAL_REVIEW.

## Contradictions à vérifier avant clôture

1. **Exceptions G6/G9 et scénario de coupe physique** : conserver les dix exigences sans ticket source explicite et les six exceptions de liens historiques ; le propriétaire candidat est une décision V3.5, jamais une réécriture du lien V3.4. Pour `T-V34-03-16`, une preuve de coupe réelle reste distincte d'une validation documentaire.
2. **V1/CAS versus receipts durables** : vérifier les clauses parentes des lots 05–06 et leurs consommateurs ; le projet `.smartsvg` V1 et le writer actuel restent inchangés, tandis que CP2/V2 est une évolution explicitement autorisée seulement après revue. Distinguer receipt d'installation de modèle, publication d'export et mutation de projet.
3. **Atomicité** : un fichier ou ZIP publié doit être complet, vérifié et sans écrasement ; un batch peut être PARTIAL et conserver ses sorties saines. Une annulation Undo ne révoque pas une livraison externe.
4. **Quatre exports et validation terrain** : PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche et SVG d'édition ont des contrats distincts. Aucun succès de prévol local n'atteste Design Space, outil machine ou coupe physique.
5. **Critères chiffrés et accessibilité** : garder p50/p90/max et p95, RSS/VRAM, cibles clic/pan/job, 1366×768 et DPI 200 %, 15 opérations/trois Undo-Redo, cinq novices et observation de trois parcours/deux erreurs. Les valeurs sont des cibles historiques ou protocoles, pas des mesures PASS.
6. **Confidentialité et licences** : provenance/hash n'est pas signature ; OCR, typographie, gabarits et dioramas quatre plans restent hérités, avec licences et validation humaine explicites. IA locale, modèles et réseau requièrent consentement.

## Gate de clôture restant

Effectuer **une revue contextuelle ciblée et contradictoire**, en lisant les paragraphes parents et tests locaux des sources pour chacune des six familles ci-dessus, puis consigner pour chaque famille : source SHA/section, contrat V3.5 consommateur, contradiction oui/non, correction ou justification, preuve et statut. Comparer les 26 blobs au HEAD GitHub courant ; exécuter les vérificateurs documentaires dans un checkout correspondant. Si et seulement si zéro contradiction non arbitrée et aucune perte détectée : publier un verdict SOURCE_CLOSURE DONE, actualiser RUN_STATE et PROGRESS, puis lancer GLOBAL_REVIEW des 25 axes au SHA fixé. Sinon conserver SOURCE_CLOSURE READY.

**Preuves de ce passage :** lecture de documents via connecteur GitHub et HEAD main via API. Contrôleur local, tests unitaires, Windows, GPU, Design Space, coupe physique : NOT_RUN. Aucune PR, fusion, code ou gouvernance.
