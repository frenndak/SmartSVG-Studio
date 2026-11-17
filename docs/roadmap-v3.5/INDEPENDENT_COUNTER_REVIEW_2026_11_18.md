# SmartSVG Studio V3.5 — deuxième contre-expertise complète et indépendante

**Date de la vérification : 18 novembre 2026 (Europe/Paris)**. **Source analysée :** `main@5110b0905eaa206bd3d7fe710a1f068ce26bf0d4`. **Portée :** recertification d'inventaire et de cohérence documentaire, analyse produit/ergonomie, lecture ciblée du port Windows natif ; **pas** d'exécution locale des tests, pas de démonstration Windows/GPU/Design Space/coupe physique, pas de nouvelle certification de fonctionnalité. Les éventuelles données d'état postérieures à ce SHA doivent être relues avant implémentation.

**Autorité courante :** `AGENTS.md`, `.automation/READY`, `docs/AUTONOMOUS_INTEGRATION_POLICY_V35.md`, [EXECUTION_STATE](EXECUTION_STATE.json), puis [MASTER_PRIORISE](MASTER_PRIORISE.md). **La V3.5 est active** et sa prochaine tranche reste **W02** au moment de cette revue. Le `PRIORITY_REGISTER.json` est un **inventaire photographique historique** dont les champs `status=CANDIDATE`, `active_roadmap=3.4`, `canonical_branch=roadmap/v3-5-design-candidate-20261112` décrivent la conception **avant promotion**, et **ne sont pas un deuxième pilote de roadmap**. Aucun changement silencieux de ce JSON de référence n'est fait par l'audit.

## 1. Audit source contre source : résultats réellement obtenus

| Contrôle | Sources lues et comparaison | Résultat | Ce que cela ne prouve pas |
| --- | --- | --- | --- |
| **24 lots V3.4** | `docs/roadmap-v3.4/` et registre V3.5 : numéros 01..24 présents (un autre document commence par 04, mais ce n'est pas un 25e lot) | **24/24 numéros** | Implémentation ni acceptation des lots |
| **141 obligations héritées** | `docs/roadmap-v3.4/23_TRACEABILITE_BACKLOG.md` vs `docs/roadmap-v3.5/INHERITANCE_REGISTER.md`, et `PRIORITY_REGISTER.json` | **141/141 IDs**, lignes de traçabilité exactement identiques à la source V3.4 | Chaque critère intégral de V3.3 exécuté ou relié à une preuve |
| **140 tickets V34** | Mêmes sources, miroir inverse | **140/140 IDs**, lignes de traçabilité exactement identiques à la source V3.4 | Exécution de leurs DoD |
| **281 lignes de traçabilité** | Exigences 141 + tickets 140, texte de chaque ligne V3.4 et copie V3.5 | **281/281 identiques**, aucune ligne manquante ou différente | Couverture sémantique de chaque ticket par l'UI Windows |
| **80 fonctions UX** | `PRIORITY_REGISTER.json`, `PRIORITY_INDEX.md`, [première contre-revue complète](COUNTER_REVIEW_80_UX_2026_11_17.md) | **80/80 IDs**, 16 A +14 B +18 C +12 D +20 E ; descriptions, priorités d'origine et rattachements W du tableau conformes au registre | Les 80 fonctions Windows codées, testées ou commercialisables |
| **17 unités W00–W16** | [BACKLOG_AND_DEPENDENCIES](BACKLOG_AND_DEPENDENCIES.md) et [revue transversale du 17/11](COUNTER_REVIEW_W00_W16_UX_2026_11_17.md) | **17/17 unités présentes** dans la seconde analyse | 17 lots techniques achevés ; ce sont des conteneurs, pas 17 tickets |
| **437 scénarios source** | Trois inventaires `SCENARIOS_V34_02_08.md`, `09_16.md`, `17_22.md` contre les **21 documents V3.4 d'origine (02–22)** | **160 + 208 + 69 = 437/437**, chaque ligne de scénario et son ID exactement identiques au texte source, aucun doublon/oubli | Tests exécutables implémentés, ni 437 PASS |
| **15 groupes #142 / 33 opportunités** | `PRIORITY_REGISTER.json` | **15/15 et 33/33** ; huit décisions historiques de REJET conservées | Chaque proposition implémentée |
| **Liens documentaires récents** | Liens Markdown relatifs des fiches principales MASTER, INDEX, BACKLOG, deux revues du 17/11, M26/U26 et README contre la liste de fichiers | **Aucun lien local manquant détecté** dans le périmètre contrôlé | Tous les liens externes accessibles ou tous les liens du dépôt contrôlés |
| **État GitHub** | Branch `main`, PR ouvertes, G0 et PR #165 | `main` au SHA ci-dessus ; **0 PR ouverte** à l'observation ; G0 post-merge #165 SUCCESS | Ce G0 ne remplace pas un test manuel d'ergonomie ou de coupe |

**Exceptions réelles toujours ouvertes et conservées :**
- **Six scénarios sans ticket source explicite** : `T-V34-03-16`, `T-V34-06-22`, `T-V34-06-24`, `T-V34-06-25`, `T-V34-07-16`, `T-V34-07-25`. Ne pas leur fabriquer un ticket de rattachement.
- **Dix exigences V3.3 sans ticket direct V34** : `S-021`, `S-036`, `S-037`, `S-044`, `S-047`, `S-064`, `S-066`, `S-092`, `S-099`, `R33-028`. G6 (texte/typographie/gabarits) et G9 (OCR/diorama) demeurent juridiquement et techniquement des obligations de roadmap, même si leur couverture doit être qualifiée via W10/W11/W16.
- Ces manques de **lien** ne constituent pas un manque automatique de fonction mais doivent être résolus par preuves, et jamais masqués par « 80/80 relus ».

## 2. Défauts et ambiguïtés identifiés à cette deuxième passe

| ID de constat | Gravité / type | Source et écart confirmé | Correction retenue |
| --- | --- | --- | --- |
| **CR2-01** | **P1 — ambiguïté de pilotage documentaire** | `PRIORITY_REGISTER.json` conserve `active_roadmap=3.4` et `status=CANDIDATE`, tandis qu'`EXECUTION_STATE.json`/AGENTS désignent V3.5. `BACKLOG_AND_DEPENDENCIES.md` et `PRIORITY_INDEX.md` montrent encore des mentions « V3.4 active », valides comme **photographies datées** mais dangereuses si lues comme état courant. | Ajouter des **bandeaux d'autorité actuels** à ces deux entrées, sans changer les données archivées ni réécrire l'historique. |
| **CR2-02** | **P1 — formulation contradictoire de priorité UX** | `COUNTER_REVIEW_80_UX_2026_11_17.md` classe **B13 « OCR facultatif→texte éditable après vérification »** `DIFFÉRER IA`, alors que son rang source est **P1/B**. Le moteur OCR relève d'une expérimentation ultérieure mais le parcours sûr de **validation/correction** ne doit pas disparaître de W10/W16. | Réviser le libellé vers **« P1 parcours / moteur OCR conditionnel P2 »**. Texte importé/retapé manuellement et vérification humaine peuvent être disponibles avant un OCR modèle ; ne pas annoncer un OCR qui n'existe pas. Conserver G9 et sa qualification P2 séparées. |
| **CR2-03** | **P0 produit, non corrigible par Markdown — aucun premier fichier de sortie native prouvé** | Lecture ciblée des entrées Tk `engine/standalone_desktop_v34.py`, `engine/native_atelier_tk_v34.py` : UI actuelle donne surtout ouverture/création PNG, aperçu, pinceau et historique ; **aucune commande native complète d'export W03 raccordée n'est démontrée dans ces fichiers**. Le statut d'ingénierie du 17/11 confirme la tranche suivante W02 puis W03. | **Ne pas faire passer cette revue en progrès produit**. Prioriser premier export réel depuis un Subject V1 vérifié après W02 ; ne jamais annoncer les quatre W03 sur simple présence d'un exporteur historique. |
| **CR2-04** | **P1 transversal — manque de preuve UX empirique** | Les revues du 17/11 proposent 80 critères et 8 parcours, mais pas de trace d'exécution Windows/novice/expert ; gains de temps, fluidité ou simplicité sont des objectifs. | Ajouter une **recette d'essai courte et mesurable** (voir §4), sans seuil de performance prétendument observé, sans nouvelle tâche et sans bloquer l'export P0. |
| **CR2-05** | **P1 — risque de présentation des statuts** | Une activité peut être localement valide mais non compatible avec Design Space ni une machine physique. Les contrats UXI/E17 le prévoient déjà mais les parcours sont susceptibles de faire afficher « terminé » à tort. | Reprendre **les statuts normalisés** dans un même panneau Sortie : aperçu / accepté / sauvegardé / export relu / pack / tiers inconnu / physique non testé, et lier chaque état à preuve et version. C'est un raffinement d'UI, pas un nouveau service. |
| **CR2-06** | **P1 — ergonomie complexe malgré le catalogue complet** | Le modèle 80 UX peut multiplier les changements d'outil si les gestes A02/A03/A05/B04/C07 sont isolés. UXI prévoit déjà un canevas unique ; il manque un **critère de validation entre commandes**. | Tester explicitement que changer d'intention, calque, vue et outil **ne perd ni cible, ni brouillon, ni protection**, et qu'une action sur une sélection remplacée est refusée plutôt qu'appliquée ailleurs. |
| **CR2-07** | **P2 — rédaction trompeuse sur les ajouts laser/BAТ/recettes** | M26/U26 clarifiés par #164 : PNG gravure ≠ PNG PTC ; BAT ≠ accord client ; Undo d'édition ≠ retrait des exports ; matériau/jeu inconnus. | **Conserver les corrections déjà appliquées, pas réintroduire d'API laser/exports supplémentaires** ni de nouveau moteur. Revalider à chaque implémentation. |

**Verdict :** les deux défauts documentaires CR2-01/02 sont immédiatement corrigibles ; CR2-03–07 sont des risques de qualification et d'intégration à traiter par les workstreams existants. Aucune suppression des 80 fonctions ni « fonctionnalité gadget » ajoutée.

## 3. Contre-expertise par famille — valeur, dynamique et garde-fou

| Famille | Audit contradictoire | Amélioration à juger à l'usage | Ne pas confondre |
| --- | --- | --- | --- |
| **A01–A16 — source / sélection / raster / vecteur** | Les commandes couvrent le besoin, mais les réglages peuvent sembler interchangeables (lissage alpha, anti-halo RGB, simplification Bézier, vectorisation). | Une **fiche cible unique** et avant/après synchronisé, bouton « récupérer source », variantes optionnelles et contrôle mm/topologie avant export. | Détourage d'image ≠ création de chemins de découpe ; grossissement de pixels ≠ détail reconstruit. |
| **B01–B14 — objets / scènes / texte** | La promesse d'objets rééditables persiste seulement avec CP/V2 qualifiés. B13 P1 corrigé comme ci-dessus. | Palette d'objets lisible : visibilité/verrou/type séparés des opérations, texte source durable et clone contours, propriétés en mm seulement si échelle connue. | Subject V1 ≠ Layer V2, texte vu à l'écran ≠ TextNode sauvegardé, pièce de scène ≠ page imprimée. |
| **C01–C18 — stickers / coupe / gabarits / planches** | Les options doivent dépendre de l'intention de sortie, non d'une « compatibilité universelle ». | Détection localisée des chemins, guide Score/Attach, placement protégé, correctifs de géométrie sur copie et prévol par rôle. | Couleur graphique ≠ opération machine ; ZIP SVG valide ≠ coupon physique. |
| **D01–D12 — IA / automatisation** | Une IA obligatoire dégrade l'outil ; la VRAM/l'interface ne peuvent pas être évaluées sans environnement réel. | Choix manuel/CPU avant modèle, preview bornée, annulation, rejet des résultats périmés, recette sur commandes whitelistées. | Proposition ≠ mutation ; modèle catalogue ≠ modèle installable ni licence commerciale autorisée. |
| **E01–E20 — UX / projet / installation** | La fenêtre Tk, l'accessibilité et la reprise méritent de vrais tests sur Windows plutôt qu'un nouveau framework choisi par apparence. | Un seul canevas + barre stable, commandes clavier, cache borné, recherche d'actions, bibliothèque et récupération ; état projet visible et contenu de tâche non intrusif. | Undo local ≠ CAS durable ≠ fichier exporté ; G0 GitHub ≠ interface Windows qualifiée. |

**Synthèse technique :** les 17 lots W00–W16 restent nécessaires. **W01/02/03/04/05/06/13/15** forment la chaîne prioritaire du produit ; les extensions **W07–12/14/16** se qualifient selon leurs dépendances sans bloquer le premier outil Windows. W10/W11 (G6 P1) et W16 (G9 P2) ne disparaissent jamais sous prétexte de simplifier l'UI.

## 4. Matrice d'essais utilisateur (proposée, NOT_RUN)

Tests à exécuter **après existence des fonctions** avec deux profils de difficulté : Express sans tutoriel et Expert avec contrôle des propriétés. Rejouer à 1366×768, échelles système 100 % et 200 %, clavier/souris, PC Windows réel. Les fichiers sont synthétiques ou libres et sans données personnelles.

| Parcours | Action de l'utilisateur | Signal d'échec observable | Preuve exigée |
| --- | --- | --- | --- |
| **VUX-01 : premier projet** | PNG → nouveau projet → aperçu → enregistrer/reprendre | Projet initial écrasé, import autre format annoncé sans port, dimension mm inventée | Source SHA identique, CAS, réouverture et explication d'unité |
| **VUX-02 : sélection réelle** | Clic → pinceau garder/masquer → autre Subject → Undo/Redo | Un masque voisin changé, résultat asynchrone appliqué à la mauvaise cible | IDs/SHA, diff des masques et même identité après reopen |
| **VUX-03 : changement de contexte** | Depuis sticker → vinyle → scène → retour sticker sur le **même projet** | Objet/trous/intentions perdus, contrôle inutilisable hors écran, bouton déplacé pendant geste | Comparatif source/projet et Undo, capture écran clavier/focus |
| **VUX-04 : vectorisation/export** | PNG → silhouette → mm → SVG Basic CUT → relecture | Double chemin, trou perdu, SVG CUT étiqueté éditable, « prêt machine » affiché | SVG sûr, mesures/diagnostics par rôle, fichier réel et reçu |
| **VUX-05 : texte/gabarits** | Saisir texte accentué → choisir fonte → convertir copie → patron CUT/SCORE | Police silencieusement substituée, texte source perdu, pli devenu CUT | Save/reopen CP, glyphes, opération, avertissement licence |
| **VUX-06 : série et reprise** | 50 placements, en verrouiller 2, interrompre puis relancer les erreurs | Pièce verrouillée déplacée, doublon d'export ou sujets V1 artificiellement multipliés | 50 instance IDs, manifestes, zéro duplicate et replay idempotent |
| **VUX-07 : IA facultative** | Choisir détourage manuel → IA admissible si présente → annuler job | Freeze UI, transfert réseau sans consentement, réponse périmée appliquée | Logs minimisés, consentement, test OOM/cancel et fallback |
| **VUX-08 : livraison** | Un export sain → plan ZIP → fichier existant → nouveau nom → relire pack | Écrasement, zip partiel annoncé complet, chemins privés publiés | Hashs, no-clobber, QA par rôle, reçus et guide hors ligne |
| **VUX-09 : usage professionnel** | Import client → rapport problèmes → corrections ciblées → BAT de revue | BAT considéré comme signature, police manquante ignorée, condition matériau inventée | Fiche U26-07, fichier de revue marqué non approuvé, profil UNKNOWN |

**Mesures à recueillir, jamais inventer :** réussite sans assistance, nombre d'actions pour atteindre une sortie, retours de vue, erreurs d'unité, undo/recovery réussi, temps actif (dont calculs/retry), latence p50/p95 de gestes, pics RAM/VRAM, quota et délai d'annulation. Les seuils d'acceptation **doivent être fixés avec tests sur le même corpus / même machine** puis validés en revue, pas déduits de « 2026 ».

## 5. Ordre des réparations et frontières

1. **Immédiatement documentaire :** clarifier autorité actuelle V3.5 aux deux pages principales ; corriger B13 sans reclassifier ses obligations.
2. **W02 courant :** commande réelle et réversible selection/masque avec anti-race, clavier et même sujet après sauvegarde.
3. **W03/W04 :** brancher un premier fichier réel et prévol à l'UI ; remplir la matrice locale de preuve par export avant projet complet.
4. **W05/W06 :** pack ZIP seulement depuis artefact validé ; préserver export direct simple.
5. **W10/W11/W12/W13/W14/W15/W16 :** avancer selon CP/ports/priorités, appliquer VUX-03..09 lors de livraison réelle, sans bloquer le socle par une étude laser, 3D ou agent IA.

**Ce qui reste sans preuve dans cette passe :** exécution de l'application Windows, rendu aux différentes échelles, import réel dans Design Space et logiciels laser, compatibilité matérielle, modèle RTX local, coût/temps gagné, efficacité de l'IA et réussite de chacun des 437 tests. Ne déclarer aucun PASS pour ces axes.

**Décision :** préserver la V3.5 complète ; corrections limitées à la lisibilité de l'autorité et à B13 ; introduire **zéro nouvelle fonction**, zéro W17, zéro tâche/cron, zéro changement de `PRIORITY_REGISTER.json` photographique, `AGENTS.md`, `.automation/READY`, schéma de projet, CLI, GitHub workflows ni code produit.
