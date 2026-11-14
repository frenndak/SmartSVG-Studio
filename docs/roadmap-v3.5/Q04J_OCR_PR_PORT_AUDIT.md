# V35-Q04J — Audit ciblé des PR natives et décision de port OCR B13 (14/11/2026)

**Statut : CANDIDAT / AUDITÉ PARTIELLEMENT ; aucun test produit exécuté.** Sources : #142, Q04H, Q04I, B13 dans INHERITANCE_REGISTER, S-021/S-047 (G9), G6.3 et lots 12/13. L'héritage historique reste inchangé.

## 1. Preuves effectivement consultées

La comparaison GitHub `main...roadmap/v3-5-design-candidate-20261112` retourne base `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`, branche documentaire **133 commits en avance, zéro derrière** à la lecture. Cela **ne constitue pas une lecture directe du HEAD main** : main@HEAD NON_VÉRIFIÉ. La liste des fichiers changés et le patch du port principal ont été obtenus pour quatre PR numérotées ; **leur statut ouvert/fermé et leurs SHAs de tête exacts n'ont pas été confirmés**. Ne pas déclarer un audit exhaustif du dépôt.

| PR | Fichiers examinés / signature effective du patch | Conséquence B13 |
|---|---|---|
| #138 | `engine/native_recovery_tk_v34.py` : plan de récupération épinglé, confirmation explicite, garde de fermeture et réception vérifiée | Réutiliser la discipline de réinspection/reprise ; **pas de moteur OCR dans ce patch** |
| #139 | `engine/native_atelier_tk_v34.py` : injection `history_fn=inspect_native_brush_history`, historique pinceau lecture seule et contrôle SHA | Pas un stockage texte/OCR ; une proposition OCR ne doit pas détourner ce journal |
| #140 | `engine/native_image_viewport_v34.py` : `fit_factor`, gestion dimensions nulles Tk et fenêtre minimisée | Viewport de prévisualisation réutilisable en principe, **pas une preuve de boîtes OCR** |
| #144 | `engine/smartsvg_core/native_brush_history_command_v34.py` : `change_native_brush_history(project_path, expected_sha256, subject_id, action, command_id, confirmed=False)`, CAS/receipt/readback | Port pinceau seulement, **ne pas le renommer en commande OCR** |

Les listes de fichiers ne montrent pas de module OCR ajouté par ces quatre PR. Cette conclusion est **bornée à ces PR et à leurs patches examinés** : un moteur OCR ailleurs dans main, dans une autre branche ou une dépendance demeure NON_VÉRIFIÉ.

## 2. Décision V3.5

**RACCORDER, sans nouveau moteur ni nouveau store par défaut.** B13 OCR reste une capacité candidate distincte de B12 texte→chemins, B09 texte éditable et V34-092 amélioration de textures. Une première tranche B13 doit proposer une transcription **éphémère** avec rectangles de reconnaissance, confiance non assimilée à exactitude, correction humaine et export externe explicite. Aucune persistance d'objet texte dans `.smartsvg` V1. G6.3 (« texte modifiable dans projet ») reste BLOQUÉ jusqu'à ADR V2 validée par le propriétaire ; une exportation de contours ne clôt pas ce gate.

**Port candidat (à ne pas présenter comme API existante)** : `recognize_text_candidate(image_ref, expected_project_sha256, region_px, language_tag, provider_id, consent)` → `{status, project_sha256, source_sha256, boxes_px, text, confidence_optional, provider_version, warnings}`. Coordonnées en pixels de l'image source, origine explicite ; le consommateur UI doit vérifier SHA et dimensions avant overlay. États : IDLE → PREVIEW_PENDING → PROPOSAL_READY → USER_CORRECTED → EXTERNAL_EXPORT_PENDING → EXPORTED ou FAILED/STALE/CANCELLED. Toute correction locale reste réversible tant que non exportée ; l'écriture externe nécessite destination/confirmation et politique no-clobber. Aucune IA/téléchargement/réseau silencieux ; fallback manuel toujours disponible, modèles soumis à licence/hash/VRAM et consentement.

## 3. UX, sécurité et contre-expertise

Débutant : choisir une zone de texte → « Reconnaître le texte (optionnel) » → proposition sur canevas + correction → copier/exporter ; expert : langue et fournisseur explicites, boîtes éditables et rapport d'incertitude. États vides, pending, erreurs, stale, annulation, raccourcis et focus doivent être spécifiés dans la fiche UI suivante. À 1366×768 / DPI 200 %, aucune boîte ne doit bloquer le canevas ; contrastes et réduction de mouvement à vérifier. Les images ne doivent pas être téléversées sans consentement ; EXIF et données personnelles ne sont pas ajoutés aux logs. XML/SVG et quatre sorties restent séparés : PNG PTC, SVG Basic Cut, SVG CUT multicouche, SVG édition. Aucune opération Cricut certifiée.

Alternative rejetée : créer immédiatement un TextNode V1 ou brancher l'OCR sur le journal pinceau ; incompatibilité d'autorité et migration implicite. Alternative retenue provisoire : OCR CPU local seulement si dépendance/licence prouvée ; sinon saisie manuelle, sans promesse de reconnaissance équivalente.

## 4. Tests à écrire, pas des PASS

Positifs : texte synthétique autorisé avec orientation/Unicode ; correction et Undo du brouillon ; export externe sans toucher au projet V1 ; rechargement du projet inchangé. Négatifs : (1) SHA périmé après changement de projet ; (2) langue ou modèle absent/refusé ; (3) région hors image / dimension nulle ; (4) réponse OCR malformée, NaN, boîtes hors bornes ; (5) fermeture UI pendant calcul ; (6) concurrence de deux propositions ; (7) disque plein et collision de destination ; (8) tentative de téléchargement non consentie ; (9) fonte/glyphe non licencié ; (10) crash après écriture externe avec résultat inconnu. Exiger assertions de non-mutation SHA/CAS, absence de fuite et rollback du brouillon. Tests Windows/UI, GPU RTX 8 Go, Design Space et coupe physique **NOT_RUN**, indépendants ; Design Space/coupe physique non applicables au moteur OCR seul, mais nécessaires au workflow aval de fabrication.

Micro-lots TDD : J1 inventaire complet des ports main et dépendances OCR ; J2 fixtures CPU et contrat de propositions ; J3 overlay/édition avec stale/Undo ; J4 export externe et reprise ; J5 qualification Windows/accessibilité ; J6 raccordement aux quatre exports et gates V2 **seulement après autorisation**. Aucun code autorisé par cette fiche.

## 5. Contrôle 25 axes — bilan borné

Axes applicables : héritage/IDs, décisions et alternatives, source/ports/PR, JTBD, parcours, données/unités/versions, autorité V1, SHA/CAS, annulation/reprise/concurrence, UX/focus/DPI/accessibilité, permissions/licences/confidentialité, CPU/GPU, performances à mesurer, négatifs/TDD, quatre exports, statuts de preuve, sécurité et réversibilité, WIP/gouvernance. **Mesures de performance : NON_RUN**, seuils à établir sur corpus autorisé. Axes matériels Explore 5/Design Space et coupe physique : non applicables à l'algorithme OCR isolé, obligatoires au parcours de fabrication aval. Audit de conformité **non certifiant** : l'énumération des 25 clauses exactes du contrat n'est pas reproduite ici ; une validation clause par clause demeure nécessaire avant REVU.

**Couverture historique, sans nouvelle certification :** 24/24 lots, 141/141 exigences, 140/140 tickets, 80/80 UX, 437/437 scénarios inventoriés ; 431/437 liens source explicites, six exceptions, dix exigences G6/G9 sans ticket direct, 0/80 UX certifiées. Les 30/30 scénarios du lot 12 ont été rapprochés dans Q04I, pas exécutés.

**Prochaine action UNIQUE Q04K :** vérifier sur main les dépendances et modules OCR réels par inventaire de fichiers/signatures (avec SHAs), puis produire le contrat d'adaptation B13 relié aux critères G9 sans créer de TextNode V1.
