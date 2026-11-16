# V35-COV-21 — Confrontation des contrats de transfert aux lots V3.4 14–17

**14 novembre 2026 — CANDIDAT, NON NORMATIF.** Périmètre : O-001/O-002/O-004/O-028/O-032 de COV-20. Sources lues directement : `docs/roadmap-v3.4/README.md`, `14_LANGAGE_FABRICATION.md`, `15_PROFILS_EXPLORE5.md`, `16_PATRONS_PARAMETRIQUES.md`, `17_EXPORTS_DESIGNSPACE.md` sur main ; `COV20_TRANSFER_PREFLIGHT_OPPORTUNITIES.md`, `AUTOMATION_QUALITY_CONTRACT.md` et `PROGRESS.md` sur la branche candidate. Les anciens commentaires SD-V1/SD-V2 et les signatures du code HEAD ne sont **pas encore** qualifiés ici : ne pas transformer les noms de ports documentés en preuves de leur présence actuelle.

## 1. Décisions contradictoires et écarts concrets

| Contrat | Exigence V3.4 exacte pertinente | Décision V3.5 et arbitrage |
|---|---|---|
| O-001, journal post-export | Lot 17 : `EXPORTED_UNVERIFIED`, manifeste externe, source SHA, absence de transaction atomique multi-fichiers | **RACCORDER** : journal local facultatif par hash d'artefact ; ne jamais qualifier un clic utilisateur comme import DS réussi. Conserver journal séparé de V1. Une simple checklist non persistante est alternative si les reprises ne sont pas démontrées utiles. |
| O-002, PTC | Lot 15 : zone Print Then Cut A4 dépend de la configuration, pas de marge universelle ; lot 17 : PNG Flat Graphic, repères capteur produits par DS, import initial nécessitant Internet | **AMÉLIORER** : dimensions physiques et PPI de l'artefact ; affichage de l'orientation historique Explore 5 avec version/source, mais aucune certification universelle de zone. Bloquer seulement les dimensions invalides ; profil UNKNOWN = guide manuel et absence de garantie. |
| O-004, CUT/SCORE | Lot 14 : `OperationAssignment`, `OperationGroup`, `attachment_intent` rappel uniquement ; lot 16 : fixture 140×110 mm, 5 CUT et 8 SCORE ; lot 17 : Score et Attach sont configurés manuellement dans DS | **RACCORDER** aux groupes du plan de fabrication ; pas de cinquième export ni de commande machine. Les quatre fentes CUT ouvertes de la fixture sont des exceptions explicites, pas des contours fermés implicitement validés. |
| O-028, budget de chemins | Lot 16 : inspecteur G2.7 historiquement limité à 64 chemins/1–300 mm ; lot 17 : limite de sous-ensemble, **pas** limite machine | **AMÉLIORER** : séparer `inspector_limit`, `preflight_resource_budget` et `ds_versioned_observation`. Le nombre 5000 cité historiquement ne doit pas devenir plafond Cricut. Prévoir mesure comparative sur corpus synthétique. |
| O-032, guide DS | Lot 17 : PNG PTC, Basic Cut, multicouche et édition distincts ; guide Score/Attach, étapes externes non vérifiées | **FUSIONNER l'interface** avec O-001, préserver deux exigences et deux identifiants. Guide statique local selon rôle, sans télémétrie DS. Ne jamais prétendre que le SVG multicouche peut être persisté en `Artifact.use` V1 : seules les valeurs `print_then_cut_png`, `basic_cut_svg`, `editable_svg` sont historiquement admises. |

**Contradiction résolue :** le `TransferContextV1` de COV-20 emploie un statut simplifié `KNOWN/UNKNOWN`. Le lot 15 impose `KNOWN_SUPPORTED/KNOWN_UNSUPPORTED/UNKNOWN` pour la **capacité d'une combinaison**, distinct de la disponibilité utilisateur `USER_NOT_AVAILABLE`. La V3.5 doit réutiliser la granularité V3.4 sans l'écraser. Les champs de COV-20 restent conceptuels jusqu'à réconciliation avec les types de code actuels.

**Autre précision :** un ZIP Smart Delivery à un export peut être atomiquement publié comme **fichier unique** après staging/relecture ; les multiples artefacts individuels et leur manifeste ne forment pas, par magie, une transaction atomique commune. Ne pas promettre l'atomicité d'un paquet de fichiers décompressés.

## 2. Contrats de consommation proposés (pas d'API affirmée)

`ArtifactTransferRef` : `role` (PNG_PTC / SVG_BASIC_CUT / SVG_MULTILAYER_CUT / SVG_EDITABLE), `sha256` (64 hex), `byte_length` (entier >= 0), `dimensions_mm` (finies positives), `source_project_sha256` (64 hex ou origine fixture explicitement qualifiée), `export_revision`, `artifact_path` validé au point d'usage. Un rôle est déterminé par l'exporteur, jamais inféré de l'extension.

`MachineCapability` : `state` = KNOWN_SUPPORTED / KNOWN_UNSUPPORTED / UNKNOWN, `scope` = combinaison machine/outillage/matière/support/opération, `source_url`, `source_checked_at`, `profile_version`, `conditions`. `UserInventory` séparé. `DSObservation` = version/date/protocole, observation utilisateur ou essai contrôlé, jamais une certification par défaut.

`TransferGuide` : `artifact_sha256`, `role`, `guide_version`, `operation_groups`, `steps`, `unverified_assumptions`, `proof_axes`. Pour SCORE/DRAW/FOIL : instruction de sélection manuelle de l'opération puis Attach. Pour PTC : PNG Flat Graphic, contrôle dimensions et calibration dans DS, pas de marque capteur générée par SmartSVG.

`DeliveryReceipt` : hash du ZIP final relu, hash de chaque membre et manifeste, état `EXPORTED_UNVERIFIED` ou erreur ; la relecture ZIP ne vaut pas test Design Space. Aucune modification de `.smartsvg` V1 ni writer parallèle.

**Transitions** : EMPTY → PREFLIGHT_PENDING → PREFLIGHT_READY/WARN/BLOCKED → ARTIFACT_VERIFIED → STAGING → ZIP_VERIFIED → PUBLISHED_UNVERIFIED. Une mutation du projet ou un changement de hash invalide la projection correspondante ; CANCELLED, STALE, QUOTA, DISK_FULL, EXISTS, HASH_MISMATCH, UNSAFE_PATH et CRASH sont des issues distinctes. Undo restaure les commandes projet réversibles mais ne retire pas un ZIP publié. Aucun téléchargement IA/ComfyUI requis ; CPU manuel suffit.

## 3. UX, permissions et sûreté

Débutant : « Exporter » → choix de l'un des quatre rôles → prévol contextualisé → fichier existant → « Préparer le transfert » → guide local et, si demandé, ZIP. Expert : accès aux IDs de chemins, mm/viewBox, groupe et opération, hashes, provenance et avertissements. États vide, calcul, erreur, annulation et STALE visibles ; focus clavier, contraste, motion réduit et inspection à 1366×768/DPI 200 % à tester. Une modification locale réversible ne déclenche pas de confirmation systématique ; la publication externe demande une destination et un accord explicites.

Menaces : chemins absolus, liens/reparse, ZIP traversal, noms Unicode équivalents, collision no-clobber, symlink après prévol, XML externe/actif, EXIF, licences, HTML non échappé, ZIP bomb et disque plein. Quotas de nombre de membres, taille individuelle/totale et ratio de décompression doivent être configurés et testés, non inventés comme capacités machine. Guide HTML statique offline sans JS, URL distante ni média utilisateur intégré par défaut. Aucun chemin personnel ni image non libre en dépôt.

## 4. Scénarios TDD candidats — TOUS NOT_RUN

**Positifs :** P1 PNG PTC réel seul → ZIP contenant exactement PNG, manifeste et guide, aucun SVG contour implicite ; P2 boîte synthétique 80/50/30/10 → 140×110 mm, 5 CUT/8 SCORE, guide Score/Attach ; P3 même artefact/hash → journal réouvrable sans preuve DS accrue ; P4 quatre rôles distincts et aucune sérialisation V1 multicouche.

**Négatifs :** N1 `KNOWN_UNSUPPORTED` ou `UNKNOWN` combiné à matière/outillage → aucun « prêt machine » ; N2 modification des bytes après hash, même taille → HASH_MISMATCH et aucun ZIP final ; N3 chemin reparse/traversal ou collisions Unicode → UNSAFE_PATH avant publication ; N4 SVG XML externe ou `viewBox`/mm contradictoires → refus de qualification CUT ; N5 conflit de segments CUT/SCORE non intentionnel → BLOCK sans mutation ; N6 annulation, crash ou disque plein durant staging → pas de faux reçu PUBLISHED ; N7 deux workers sur même destination → au plus une publication, jamais overwrite ; N8 changement de version du profil ou de DS → observation précédente STALE, preuve physique inchangée ; N9 EXIF et photo utilisateur absents du ZIP par défaut.

**Axes de preuve séparés :** tests unitaires CPU et intégrité ZIP, UI Windows DPI/clavier, observation Design Space versionnée, coupon physique Explore 5 mesuré (matière/lame/tapis/version/SHA). GPU = N/A car aucune IA ; réseau = N/A pour le ZIP offline, **mais l'import initial Design Space requiert Internet selon le lot 17**. Mesurer temps p50/p95 et mémoire sur corpus autorisé, sans inventer de résultats.

**Micro-lots** : M1 réconciliation types/ports exact HEAD ; M2 fixtures d'artefacts et prévol par rôle ; M3 guide et journal séparés de V1 ; M4 ZIP unique staging/relecture/no-clobber ; M5 UI Windows ; M6 observations DS et coupe physique. Aucun micro-lot n'est autorisé à créer un second writer ou exporteur.

## 5. Revue hostile et contrat 25 axes

01–05 : inventaires historiques 24/141/140/80/437 **conservés**, rapprochement sémantique non certifié ; 06 : aucun PASS produit ; 07 : V1/CAS préservés conceptuellement, HEAD non qualifié ; 08 : quatre rôles distincts ; 09 : capacité tri-state V3.4 corrigée ; 10–12 : novice/expert, clavier et DPI spécifiés, UI NOT_RUN ; 13 : crash/concurrence/rollback couverts par scénarios, NOT_RUN ; 14 : IA N/A (aucun modèle) ; 15 : alpha/PPI/EXIF abordés, tests NOT_RUN ; 16 : XML/topologie/mm abordés, tests NOT_RUN ; 17 : Fabrique en consommateur, batch/CSV N/A dans ce lot ; 18 : ZIP à un export et manifeste spécifiés, NOT_RUN ; 19 : cinq opportunités arbitrées, autres décisions COV-19 conservées ; 20 : protocole de performance, aucune mesure ; 21 : risques sécurité/licences/privacy explicités ; 22 : branche documentaire seulement, pas de fusion ; 23 : ports réutilisés à identifier avant codage, pas de moteur doublon ; 24 : revue et promotion NON AUTORISÉES ; 25 : aucune réduction de contrôle, écarts déclarés.

**Réserves bloquantes avant certification :** (a) lire les deux commentaires historiques SD-V1/SD-V2 intégralement ; (b) vérifier signatures et disponibilité des ports sur HEAD main ; (c) associer chaque test du lot 14–17 à son DoD et à sa preuve exacte, pas seulement au domaine ; (d) revue indépendante et tests réels. **Prochaine action unique COV-22 :** vérifier les ports et les contrats existants du code `main` puis résoudre les divergences avec les commentaires SD-V1/SD-V2, sans modifier la V3.4 active.
