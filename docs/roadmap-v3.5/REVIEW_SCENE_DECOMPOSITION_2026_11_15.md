# Revue indépendante — décomposition de scène, planche et relief

15 novembre 2026. **Verdict sur le contrat figé : recevable pour planifier la conception ; aucun Critical/Important ni décision produit matérielle manquante identifiés.** Le parcours demandé est cohérent : sélectionner personnage/décor/accessoires, les accepter comme éléments indépendants, déplacer leurs instances sur une planche et préparer un montage en relief. Le raccordement des entrées opérationnelles doit encore être relu et contrôlé après son gel. Ce verdict initial n'est ni GitHub APPROVED, ni adoption V3.5, ni attestation d'une fonction déjà codée.

## Portée, base et empreintes

Reviewer indépendant `review_scene_contract`, sans sous-agent. Base candidate communiquée : `3ea07f8f5fdb0cfcf0450fdc1573a3cebc64f252` ; main communiqué : `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`. Le nouveau contrat est un delta local non publié au début de cette revue. `canonical-v35` et `history-work` sont des copies locales, sans dépôt Git utilisable : aucune vérification distante du HEAD ni attestation d'un SHA final publié n'est revendiquée ici.

Lecture intégrale du nouveau contrat, de l'ADR composition, de D01–D09 et des décisions B03/B08 ; rapprochement ciblé C12, Q04G/G9, recettes et dépendances. Lecture ciblée des consommateurs discriminants dans `history-work/engine` : contrats source/masque/sujet/artefact, identité float32, parser strokes, workspace, preview native, routage, génération de masques, correction et pagination historique. Les neuf SHA de blobs cités au §7 du contrat ont été recomputés localement selon le format Git : **9/9 identiques aux pins du contrat**. Cette égalité locale ne prouve pas la fraîcheur distante.

| Fichier sous `docs/roadmap-v3.5` | SHA256 local relu |
|---|---|
| `SCENE_DECOMPOSITION_AND_RELIEF_CONTRACT.md` | `1bac6caec388ea88c7c272ca3c4d37c12fe670a73ab83b332c3ba0da9a981865` |
| `ADR_COMPOSITION_PERSISTENCE.md` | `d34384dd1b5dbf8922e79c17932620c65f767775361c16e89a90dd42516a9647` |
| `DECISIONS_TRANSVERSALES.md` | `7821a634715b1601d62f3c20fc14d01b327918b4ed2eeedf2dbc0696620645be` |
| `Q04G_G9_OCR_TEMPLATES_DIORAMA.md` | `9230be013894095f869502a10fda29603044d74ce3d5fbd6459d12ea6d4d6456` |
| `COV18A3C_B_REMAINING_CORRECTED.md` | `7b61a742ed751cd529a05fb3356165f23010bcbaf334de73d79997830252e9f1` |
| `COV18B2_CUT_LAYOUT_C07_C12.md` | `5d246b307e49684b4a7658ec1ce6700ff71ff670989c548cfb031e15ac1698c6` |

Preuves antérieures réemployées : `GLOBAL_REVIEW_2026_11_15.md` (SHA256 confirmé `c2bea5cbe8f58ff6867d9d78744ec9bd3dfd25ef0a405da70bebfae9bf6e617d`), `GLOBAL_REVIEW_RESOLUTION_2026_11_15.md` (`d17ecc0a5899741471243a179c6533119c2bc0c49f61387cb4faf527ba0b9434`) et `REVIEW_SOURCE_ACCEPTANCE_2026_11_15.md` (`e17f1ccca980212df073b795974e402bec96e22ebce87c1b9675b92a4a534f63`). Leur lecture fournit le contexte de préservation historique et les limites de preuve ; cette revue n'est pas une nouvelle comparaison sémantique individuelle des 141 critères, 140 DoD ou 437 assertions.

## Buildercheck et contradictions recherchées

**Question : quels choix importants manquent pour planifier sans demander à l'auteur ? Réponse : aucun identifié dans ce périmètre.** Le producteur a choisi une voie manuelle utile, une assistance révisable, des objets/instances distincts et une persistance V2 progressive. Ces choix sont présentés comme propositions de conception, sans inventer une décision utilisateur antérieure. Les valeurs de budgets, champs de ressources, sérialisation, tolérances de fixtures et adaptateurs exacts sont explicitement la sortie bornée CP0-SCN/SCN0 ; leur absence actuelle n'est pas transformée en blocage documentaire ni en permission d'écrire avant CP0.

| Point examiné | Conclusion bornée et preuve |
|---|---|
| Visible / parties cachées / réparation du fond | §2 et §5 : visible seulement par défaut ; compléter un objet et reboucher le fond sont deux opérations opt-in distinctes. Une silhouette partielle n'est pas annoncée complète. SCN-04/09 les discriminent. |
| Alpha, fragments, trous et occultation | §1/4 : objet sémantique distinct d'une composante connexe ; recouvrement permis si explicité. Pas de partition universelle ni de promesse de reconstitution photographique exacte. SCN-02/03/04 ; algèbre des corrections héritée D01. |
| Pixel, millimètre et montage | §4 fixe repère orienté source, viewport inverse, bbox semi-ouverte et exemple 30×40mm ; §6 sépare placement matière et montage. Une rotation de nesting ne tourne pas le guide de scène. |
| Source, float32 et identité | §5 interdit substitution L8 et réaffectation silencieuse d'un sujet à une nouvelle source. Le code historique confirme les preuves float32 ; `Mask` L8 reste un enregistrement distinct. Reconstruction = dérivé, duplication = nouvelle instance. |
| V1 / extensions et autorité V2 | §5/8 : CP0-SCN strict avant écriture, ressources versionnées dans le digest/transaction CP2, aucun JSON libre V1 ni maître annexe. Transformations canoniques dans les nœuds. CP0–3 requis pour SCN2. |
| Receipt / CAS / reprise | §5 : acceptation groupée atomique, replay avant rejet du SHA ancien, payload différent refusé ; CAS V1 distinct du receipt durable CP2. Primary publié/backup échoué et issue inconnue gardent leurs statuts et inspection avant retry. |
| SCN1 / SCN2 / SCN3 | §8 : aperçu/export SCN1 sans CP2 ; scène rééditable SCN2 obligatoirement persistante ; SCN3 réemploie W12, peut commencer en export-only mais ne clôt pas sa DoD rééditable ainsi. Pas de dépendance V2 globale artificielle. |
| Relief et héritage G9 | §6/8 : plans manuels sans OCR/texte/3D ; quatre plans et prototype mesuré restent le cas G9. `ReliefPlan` à trois/cinq plans est un autre cas, sans contredire le refus Q04G-N6 propre au preset quatre plans. |
| Quatre sorties et preuves physiques | §6/9 : PNG PTC, Basic Cut, CUT multicouche et SVG d'édition gardent des critères distincts. Pas de raster présenté comme vecteur, quatrième usage V1, capteur Cricut généré ou profil UNKNOWN proclamé prêt. Import DS, coupe et montage restent trois preuves. |
| Réemploi des ports | §7 décrit correctement les capacités présentes et manquantes. `auto_masks._accept` filtre aussi les masques quasi pleins/rectangulaires ; ce port ne certifie donc pas à lui seul le fond conservé ni les fragments sémantiques. Le contrat exige inventaire/adaptation avant usage, sans prétendre que ce raccord existe déjà. |
| Modèles et confidentialité | `generate_masks(allow_ai=True, provider=None)` appelle bien un fournisseur legacy ; le contrat ne l'admet pas implicitement. Admission/no-network préalable, consentements séparés, zéro média personnel/poids publié ; SCN-12/16. Aucun téléchargement exécuté ici. |

**Points fermés :** fonction nommée, parcours scène→pièces→planche→relief, comportement visible/caché, autorité des coordonnées, persistance, réemploi W12, obligations G9 et limites d'export. **Points restant à produire, déjà attribués :** CP0-SCN et schémas/quotas/erreurs, fixtures/runner SCN0, raccords UI/moteurs, qualification de l'assistance, Windows et fabrication. Ce sont des livrables d'exécution futurs ; aucun résultat NOT_RUN n'est promu en PASS.

## Les 25 axes sur ce delta

`Recevable` signifie ici que le nouveau contrat préserve l'obligation et permet de planifier sa réalisation ; ce n'est pas un PASS produit. Tous les axes restent applicables, avec la profondeur bornée ci-dessous.

| Axe | Examen du delta et limite |
|---:|---|
| 01 — 24 lots | Raccords de responsabilités identifiés aux lots existants ; pas de nouvelle relecture exhaustive des lots ni de lot livré. |
| 02 — 141 critères | Préservation explicite et G6/G9 rapprochés ; inventaire historique réemployé, pas 141 nouvelles validations sémantiques. |
| 03 — 140 tickets | §7/8 : responsabilités candidates, pas preuve historique fabriquée ni tickets V34 dupliqués. |
| 04 — 80 UX | Raffinement B03/B08/B04/C12 et Atelier existant, aucun 81e ID nécessaire. |
| 05 — 437 scénarios | SCN-01..17 sont 17 recettes proposées NOT_RUN séparées ; compteur historique inchangé. |
| 06 — maturité/preuves | Bandeau et §4/7/9 distinguent contrat, ports présents, code futur et preuve réelle. |
| 07 — projet unique | CP0–3, writer actif unique, V1 intact, source/float32/identités et ressources transactionnelles explicités. |
| 08 — quatre exports | §6 et SCN-08 : obligations distinctes, sans enrichissement clandestin d'Artifact.use V1. |
| 09 — opérations/machine | Rôle objet distinct d'opération ; profil/cote inconnus et supports non validés = revue requise, pas état prêt machine. |
| 10 — Express-first | Parcours novice progressif et parcours expert dans le même Atelier ; observation utilisateur future. |
| 11 — canevas/gestes | Trois vues d'un même projet, poignées/liste/clavier, Undo logique, source/viewport séparés ; UI future. |
| 12 — accessibilité | Alternative au drag, focus/annonces/mouvement réduit, écrans/DPI historiques conservés ; Windows/lecteur réel NOT_RUN. |
| 13 — annulation/reprise | Session/revision STALE, rejet sans commit, crash/recovery, exports PARTIAL et Undo externe exclus. |
| 14 — IA facultative | Voie manuelle complète ; assistance P1 conservée, avancée SCN5 P2 ; admission legacy non inférée. |
| 15 — raster | Alpha souple, EXIF, repère source, mm/DPI, reconstruction séparée et ROI/diff ; tolérances de fixtures à fixer. |
| 16 — vecteur | Chemins réellement vectorisés, trous/fragments, prévol géométrique ; aucun rendu raster renommé CUT. |
| 17 — Fabrique/séries | W12 instances/pages/verrous/quantités réemployé ; relief W16 et quatre plans G9 avec prototype propres. |
| 18 — Smart Delivery | Consommateur d'exports/guide existants, pas nouveau segmentateur/writer ni dépendance globale CP2. |
| 19 — autres évolutions | Raffinement candidat B03/B08/C12/G9, sans suppression d'opportunité ni fonction concurrente ajoutée. |
| 20 — métriques | §9 : même source/taille/matériel, qualité/échelle/latence p50/p90/p95/max/RAM/VRAM ; aucune mesure acquise. |
| 21 — sécurité publique | Sources/poids privés exclus, ressources/URL hostiles et guide expurgé ; licences futures à qualifier. |
| 22 — gouvernance/WIP | Delta documentaire ; aucune permission de merge, code, CI, tâche ou gouvernance créée par cette revue. |
| 23 — anti-doublons | Aucun moteur de nesting/bus/queue/store/canevas concurrent ; ports vérifiés localement, adaptation future explicite. |
| 24 — revue/adoption | Présente revue du contrat ; contrôle des raccords et du SHA final requis, aucune GitHub APPROVED. |
| 25 — optimisation | Revue du delta avec réemploi borné des rapports ; aucun critère supprimé pour éviter une nouvelle revue globale. |

## Contrôles documentaires et limite du verdict initial

Effectué : lecture contradictoire ci-dessus, recalcul des empreintes et comparaison 9/9 pins de ports. **En attente du gel des raccords** : relecture README/MASTER/BACKLOG/PRIORITY_INDEX/QUALITY/RUN_STATE, trois vérificateurs documentaires et liens locaux du delta. Cette attente concerne le raccordement ; elle ne masque aucun Important constaté dans le contrat principal figé.

Non exécutés : les 17 recettes produit SCN, tests studio, UI/Windows/NTFS, GPU, réseau instrumenté produit, Design Space, impression, découpe, assemblage, benchmark ou observation d'accessibilité. Les modèles réels ne sont ni téléchargés ni exécutés. Aucun code produit/gouvernance/CI ni autre fichier modifié par ce reviewer.

**Verdict initial net : conception du contrat recevable ; aucun défaut Critical/Important identifié ; intégration documentaire à terminer et contrôler.** L'absence d'une fonction future déjà codée n'est pas un défaut de conception. Le HEAD final publié et ses preuves propres restent sous la responsabilité du coordinateur.

## Complément final des raccords — 15 novembre 2026 — review_scene_final

**Verdict indépendant sur le delta local figé : conception et raccordement recevables, zéro Critical/Important identifié ; delta publiable sur la branche documentaire existante.** Cette conclusion complète le verdict initial sans le réécrire ni remplacer ses empreintes. Elle ne constitue ni GitHub APPROVED, ni G35-12 PASS, ni fusion, adoption ou qualification produit. L'ouverture d'une PR consolidée reste soumise au WIP courant, à sa CI au SHA exact et aux protections décrites dans la checklist.

Revue bornée par `review_scene_final`, sans sous-agent. Base du delta communiquée `3ea07f8f5fdb0cfcf0450fdc1573a3cebc64f252` ; main communiqué et revalidé par le coordinateur `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`. Lecture du contrat courant et du rapport initial ; relecture ciblée des dix raccords, de leurs paragraphes voisins, du graphe BACKLOG et de tout RUN_STATE. Aucun appel distant effectué par ce reviewer : les neuf blobs exacts du §7 et leur égalité au tree main sont des preuves du coordinateur, non une observation distante personnelle. Les 17 lignes de recettes ont en revanche été recomptées ici : 17 IDs uniques.

### Contradictions recherchées et résultat

| Point du delta | Résultat borné |
|---|---|
| Trois usages et pixels observés | Contrat §2–6, README et MASTER rendent accessibles planche, scène recomposée et relief. Fond conservé ; fragments/trous et occultation explicites. Compléter la pièce et réparer le fond restent deux propositions distinctes ; pixels cachés non inventés comme observations. |
| Ajout depuis la revue initiale | Le repère EXIF du §4 précise désormais le raster orienté dérivé : ID/digest/dimensions distincts et transformation vers l'original conservée. Les masques ne sont pas rattachés aux dimensions brutes d'une autre source ; original intact. Cet ajout est cohérent avec SCN-01 et ferme l'ambiguïté de repère sans changer la géométrie de montage. |
| Persistance et reprise | Contrat §5/8 et ADR §8 imposent CP0-SCN strict avant ressources persistantes, inclusion au digest/transaction CP2, CP0–3 qualifiés pour SCN2. Aucun JSON libre V1, graphe maître annexe, second writer ou identité réaffectée silencieusement. CAS V1 ne devient pas receipt durable ; replay, UNKNOWN_AFTER_INTERRUPTION et inspection après échec backup sont conservés. |
| Dépendances minimales | SCN1 et l'aperçu/export SCN3 peuvent progresser avant V2 ; leur mode externe ne clôt pas la DoD rééditable. SCN3 réemploie le placement W12, sans second moteur. Les capacités CP4/5, OCR, texte ou 3D non utilisées ne deviennent pas des prérequis globaux du relief manuel. |
| Planches et relief | MASTER, BACKLOG et ADR conservent 50 placements distincts de 50 sujets persistés. Coordonnées de montage et de matière séparées ; quantités/verrous et inverse de rotation explicités. Q04G garde son contrat exactement quatre plans et son négatif N6 ; ReliefPlan à trois/cinq plans ne revendique pas S-066. Import DS, coupe et prototype assemblé mesuré restent des preuves distinctes. |
| Exports et assistance | Les quatre sorties restent typées, sans raster nommé vecteur ni quatrième Artifact.use V1. Voie manuelle complète, assistance de base P1 et reconstruction avancée P2 distinctes ; admission/licence/provenance et consentements téléchargement/exécution/transfert séparés. Le provider legacy n'est pas admis par citation d'un port. |
| Héritage et preuve | Aucun compteur 24/141/140/80/437 gonflé par les six incréments ou 17 recettes SCN. Schémas, quotas, fixtures/tolérances et runner exacts sont explicitement à produire en SCN0/CP0-SCN avant écritures ou résultats revendiqués, sans exiger leur implémentation pour accepter cette conception. |
| Curseur et non-rétroactivité | RUN garde GLOBAL_REVIEW DONE → PROMOTION_DOCS READY → GOVERNANCE_HANDOFF PENDING, promotion_ready=false et V3.4 active. Ses références SCN renvoient à cette revue complémentaire. README, checklist et dernière entrée PROGRESS précisent que l'ancien rapport global demeure limité à son SHA ; ils n'étendent pas rétroactivement son verdict au delta. La phrase de PROGRESS annonçant le contrôle final à terminer est la photographie antérieure au présent complément. |

### Contrôles exécutés ici

Les trois commandes ont terminé avec code de sortie 0 :

- `python canonical-v35/docs/roadmap-v3.5/verify_source_transfer.py --main-root history-work` : PASS littéral 141 critères / 140 DoD / 26 pins et références.
- `python canonical-v35/docs/roadmap-v3.5/verify_priority_register.py --pinned --main-root history-work` : PASS documentaire 80 UX / 15 groupes / 33 opportunités / 24 lots / 141 exigences / 140 tickets / 437 assertions.
- `python canonical-v35/docs/roadmap-v3.5/verify_run_state.py` : PASS documentaire curseur/dépendances/preuves.

Contrôle local complémentaire : 374 occurrences de liens de fichiers et références inputs/evidence RUN examinées, aucune nouvelle cible SCN absente ; aucune ancre locale présente dans ces raccords. Une seule cible historique absente de la copie partielle `canonical-v35`, `BACKLOG_AND_DEPENDENCIES.md` → `../roadmap-v3.4/README.md`, existe dans `history-work/docs/roadmap-v3.4/README.md` : ce n'est pas un lien ajouté par ce delta. Les URLs externes, les ancres distantes et le tree publié final ne sont pas certifiés par ce contrôle. IDs d'actions RUN uniques et dépendances résolues ; le contrôleur confirme la cohérence du curseur.

### Empreintes du contenu relu

SHA256 locaux, sous `docs/roadmap-v3.5` ; les anciennes empreintes du rapport restent inchangées et décrivent leur ancien état.

| Fichier | SHA256 |
|---|---|
| `SCENE_DECOMPOSITION_AND_RELIEF_CONTRACT.md` | `69ba06117a0d15b7ef3da119dfe78206f1ecfc626260106b19105b62d470496d` |
| `MASTER_PRIORISE.md` | `3693d2534feeef5b13e78b0840fc0ad00f5624e82b725d3da6fd1d767f60c0a6` |
| `BACKLOG_AND_DEPENDENCIES.md` | `fc29dcbead2327a02388425c28934aa3cd7eeec9a2f6756ea8b05caa866d3b42` |
| `PRIORITY_INDEX.md` | `be526959c04fb484e5bb0e03df27a48f15d8452855704517dc64fbdd447049d3` |
| `ADR_COMPOSITION_PERSISTENCE.md` | `ada008128aca2bd80eaf24e657fb6085789cf546f5c08d09375fd21667011989` |
| `Q04G_G9_OCR_TEMPLATES_DIORAMA.md` | `169fadaf585e156ba2ecdb38cf160c43171576bccff90f16a54d1d1973e37041` |
| `QUALITY_TESTS_AND_EVIDENCE.md` | `e7e13e579655fd9cb00ef2aead96ba78cd9d0432efefa6811ff584a24f791ab6` |
| `README.md` | `8e6f03886acf49d7f6b1babacb2e6288d69903bea2ea41e4f9b6655c234ef604` |
| `PROMOTION_CHECKLIST.md` | `0f5381adfd829d54616af2a9f43bca3ca90d5d30ab618aa0e0193179f5b6cbd4` |
| `RUN_STATE.json` | `2b4920e41d499d907884e583e78acad97e75431dd8df4f368d02ab53ee0e053d` |
| `PROGRESS.md` | `6552697b9357d1e14aedda0ec4015114310e160a8a0b1f2269e6ca50352b978a` |

Preuves antérieures réemployées avec leurs limites, non refaites individuellement : `GLOBAL_REVIEW_2026_11_15.md` (`c2bea5cbe8f58ff6867d9d78744ec9bd3dfd25ef0a405da70bebfae9bf6e617d`), `GLOBAL_REVIEW_RESOLUTION_2026_11_15.md` (`d17ecc0a5899741471243a179c6533119c2bc0c49f61387cb4faf527ba0b9434`) et `REVIEW_SOURCE_ACCEPTANCE_2026_11_15.md` (`e17f1ccca980212df073b795974e402bec96e22ebce87c1b9675b92a4a534f63`). Leurs empreintes ont été recomputées ici et sont inchangées. Ce complément ne prétend donc pas réexécuter une revue sémantique de chaque 141/140/437 élément.

Limites inchangées : aucun test produit, Windows/UI/accessibilité réelle, GPU, modèle, Design Space, impression, découpe, montage ou benchmark exécuté. Toutes les recettes SCN restent NOT_RUN produit. Ce reviewer a uniquement ajouté ce complément au présent rapport ; aucun contrat, autre document, code, gouvernance, CI, tâche ou distant modifié. Le coordinateur doit encore relire le SHA final après publication et revalider les faits de plateforme avant toute PR ou intégration.

**Signé `review_scene_final`, 15 novembre 2026 : delta documentaire recevable et publiable ; aucune réserve Critical/Important ouverte dans le périmètre relu.**
