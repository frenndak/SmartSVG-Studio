# SmartSVG V3.5 — Architecture ADR, opportunités héritées et risques

**COV-14 / CANDIDAT NON NORMATIF — 13 novembre 2026.** Cette fiche conserve les **33** opportunités de [OPPORTUNITIES V3.4](../roadmap-v3.4/OPPORTUNITIES.md), blob SHA `b766e953bd2fb1e07e3e315ed68f2e1c519c5210` et leur décision historique. Un intitulé présent ici ne constitue pas un ticket V35 ni une fonction implémentée. Les options rejetées ne sont pas réintroduites implicitement.

## 1. Décisions d'architecture proposées et refus contradictoires

| ADR candidat | Proposition argumentée | Solution refusée ou conditionnelle | Preuve manquante |
|---|---|---|---|
| **ADR35-01** projet/autorité | Projet V1 + `LoadedProject` + writer CAS/recovery uniques, migration V2 si compatibilité impossible | Écrire le modèle texte dans `editor_v216` strict ou un deuxième stockage | Compatibilité lecteur V1, round-trip et reprise, tests Windows |
| **ADR35-02** quatre exports | PNG Print Then Cut, SVG Basic Cut, SVG multicouche externe, SVG éditable indépendants | Déclarer multicouche `Artifact.use=editable_svg` ou ajouter valeur V1 à chaud | QA des quatre formats / unités, import DS distinct |
| **ADR35-03** Smart Delivery | Plan sans écriture, premier ZIP avec un vrai export, guide HTML statique et manifeste SHA | Faire de `write_delivery` JSON un deuxième exporteur ou certifier machine | ZIP no-clobber Windows, concurrence, SHA et confidentialité |
| **ADR35-04** UI | Conserver `NativeAppShell` Tk, organiser Express/Atelier/Expert, éventuelle décision par benchmark | Migration globale Qt/Tauri pour esthétique seule, double store | DPI 200 %, clavier, focus, cold start |
| **ADR35-05** composition | Texte/polices/licences/masques et projets V1 par un unique writer, OCR opt-in distinct | Stocker des objets éditables dans des champs arbitraires non interopérables | Tests Unicode/glyphes/licence, save/reopen, CAS |
| **ADR35-06** fabrication | CUT/SCORE/DRAW/PRINT/FOIL explicitement confirmés ; géométrie mm et guide DS | Pilotage direct Cricut, opération déduite d'une couleur/pointillé | Test versionné Design Space + coupon physique |
| **ADR35-07** IA | CPU/manuelle sans modèle ; opt-in pour GPU/VRAM, licence, modèle SHA | Upload automatique d'images, installer silencieux, upscale inventé | Tests sans réseau, OOM et récupération |
| **ADR35-08** batch | IDs/masques séparés des instances 12/24/50, un seul scheduler et archive V1 | 50 masques dans une limite 32, seconde queue, exécuter CSV | Test reprise batch/perte partielle, collisions/CSV |
| **ADR35-09** promotion | V3.5 non normative jusqu'à couverture, revue et promotion de gouvernance séparée | Une fiche/spec/PR suffit à déclarer la V3.5 « principale » | Exhaustivité et CI documentaire exact-head |

**Aucune ADR ci-dessus n'est adoptée au sens de la gouvernance.** Leurs dispositions reprennent les limites réellement examinées dans [COV10C](COV10C_V1_TEXT_EXPORT_PORTS.md) et le [backlog candidat](BACKLOG_AND_DEPENDENCIES.md).

## 2. Les 33 opportunités d'origine sans omission

**Extraction source :** 33/33 IDs uniques. Décisions historiques : **24** retenues pour spécification, **1** reportée, **8** rejets. L'affectation à Wxx signifie « domaine de revue », pas adoption.

| ID original | Titre historique | Décision V3.4 conservée | Révision V3.5 | Statut nouveau |
|---|---|---|---|---|
| **O-001** | Journal local de transfert Design Space (étapes confirmées, versions, réglages, incidents et photo facultative) | P1 / RETENU_POUR_SPEC | W08 | **À CONTRE-EXPERTISER** |
| **O-002** | Vérification guidée de l'échelle imprimante et de l'orientation A4 avant découpe, avec état « vérification externe nécessaire » | P1 / RETENU_POUR_SPEC | W08 | **À CONTRE-EXPERTISER** |
| **O-003** | Pilotage direct de la Cricut depuis SmartSVG sans Design Space | REJETÉ | **REJET conservé** | **À CONTRE-EXPERTISER** |
| **O-004** | Prévisualisation par opération et séquence physique Cut/Score/Draw/Foil avec alertes contextualisées | P1 / RETENU_POUR_SPEC | W04 | **À CONTRE-EXPERTISER** |
| **O-005** | Aperçu de pliage 3D purement géométrique d'un patron carton, sans IA | P2 / REPORTE | W16 | **À CONTRE-EXPERTISER** |
| **O-006** | Comparateur de migration lisible « ancien vs autonome » sur un même projet, opt-in | P1 / RETENU_POUR_SPEC | W13 | **À CONTRE-EXPERTISER** |
| **O-007** | Diagnostic de capacités hors ligne et recommandations réparatrices sans installation automatique | P1 / RETENU_POUR_SPEC | W13 | **À CONTRE-EXPERTISER** |
| **O-008** | Contrôle de portabilité et confidentialité avant partage d'un projet .smartsvg | P1 / RETENU_POUR_SPEC | W06 | **À CONTRE-EXPERTISER** |
| **O-009** | Aperçu non mutant d'un Undo groupé, historique lisible des gestes et opérations | P1 / RETENU_POUR_SPEC | W13 | **À CONTRE-EXPERTISER** |
| **O-010** | Boîte de réception locale des propositions de jobs devenues périmées, avec comparaison/relance explicite | P1 / RETENU_POUR_SPEC | W13 | **À CONTRE-EXPERTISER** |
| **O-011** | Bac à sable d'import local jetable avant création de projet canonique | P1 / RETENU_POUR_SPEC | W13 | **À CONTRE-EXPERTISER** |
| **O-012** | Légende Cut/Score/Draw/Foil à double codage texte + motif, indépendante des couleurs | P1 / RETENU_POUR_SPEC | W04 | **À CONTRE-EXPERTISER** |
| **O-013** | Fiche « pourquoi cette suggestion ? » : provenance, limites, conséquence sur sortie | P1 / RETENU_POUR_SPEC | W14 | **À CONTRE-EXPERTISER** |
| **O-014** | Préférences par intention avec portée et reconfirmation des dimensions/matériaux | P1 / RETENU_POUR_SPEC | W13 | **À CONTRE-EXPERTISER** |
| **O-015** | Assistant micro toujours à l'écoute, déclenchement automatique | REJETÉ | **REJET conservé** | **À CONTRE-EXPERTISER** |
| **O-016** | Diff exact des mutations projet avant confirmation d'un plan | P1 / RETENU_POUR_SPEC | W13 | **À CONTRE-EXPERTISER** |
| **O-017** | Refus réparateur avec action sûre et explicite | P1 / RETENU_POUR_SPEC | W13 | **À CONTRE-EXPERTISER** |
| **O-018** | Exécution automatique des plans suggérés sans clic | REJETÉ | **REJET conservé** | **À CONTRE-EXPERTISER** |
| **O-019** | Revue des relations accessoires↔sujets avec liaison réversible et justification | P1 / RETENU_POUR_SPEC | W02 | **À CONTRE-EXPERTISER** |
| **O-020** | Inspection de masques à 100 % avec échantillons de bord reproductibles | P1 / RETENU_POUR_SPEC | W02 | **À CONTRE-EXPERTISER** |
| **O-021** | Envoi automatique des photos importées à une API cloud pour « améliorer » la segmentation | REJETÉ | **REJET conservé** | **À CONTRE-EXPERTISER** |
| **O-022** | Comparaison de résultat IA vs sans IA **sur même ROI** avant toute recommandation de modèle | P1 / RETENU_POUR_SPEC | W14 | **À CONTRE-EXPERTISER** |
| **O-023** | Vérification de provenance des modèles déjà présents avant inférence (hash, licence, runtime, révocation) | P1 / RETENU_POUR_SPEC | W14 | **À CONTRE-EXPERTISER** |
| **O-024** | Installer silencieusement le « meilleur modèle » dès l'import | REJETÉ | **REJET conservé** | **À CONTRE-EXPERTISER** |
| **O-025** | Aperçu des franges RGB finales sur blanc/noir/damier et taille imprimée indicative | P1 / RETENU_POUR_SPEC | W07 | **À CONTRE-EXPERTISER** |
| **O-026** | Diff de topologie alpha multi-seuil (0/20/128) entre proposition et PNG publié | P1 / RETENU_POUR_SPEC | W07 | **À CONTRE-EXPERTISER** |
| **O-027** | Upscale IA automatique à 600 ppp pour chaque import | REJETÉ | **REJET conservé** | **À CONTRE-EXPERTISER** |
| **O-028** | Conseiller de budget de chemins SVG avant import Design Space | P1 / RETENU_POUR_SPEC | W07 | **À CONTRE-EXPERTISER** |
| **O-029** | Verrouillage de trous/îlots jugés essentiels avant simplification vectorielle | P1 / RETENU_POUR_SPEC | W07 | **À CONTRE-EXPERTISER** |
| **O-030** | Transformer automatiquement chaque couleur d'un dessin en chemin de coupe | REJETÉ | **REJET conservé** | **À CONTRE-EXPERTISER** |
| **O-031** | Détecteur de conflit d'opérations sur un segment partagé | P1 / RETENU_POUR_SPEC | W04 | **À CONTRE-EXPERTISER** |
| **O-032** | Contrôle guidé des dimensions et du groupe Attacher **après import** dans Design Space | P1 / RETENU_POUR_SPEC | W08 | **À CONTRE-EXPERTISER** |
| **O-033** | Affecter automatiquement Score depuis pointillés ou couleur SVG | REJETÉ | **REJET conservé** | **À CONTRE-EXPERTISER** |

**Règles d'analyse** : ne pas supprimer un ID rejeté ; ne pas inventer une nouvelle fonction pour un critère déjà couvert par V34/UX. Les **rejets** comprennent le pilotage Cricut direct (O-003), l'écoute micro permanente (O-015), les plans exécutés sans accord (O-018), l'upload cloud automatique (O-021), l'installation IA silencieuse (O-024), l'upscale IA automatique (O-027), la conversion de chaque couleur en chemin CUT (O-030) et Score à partir de pointillés/couleurs (O-033). Leur réintroduction exigerait une décision explicite de changement de périmètre et des preuves.

**O-028** mentionne un plafond de chemins présenté comme « officiel » dans V3.4. Cette fiche **ne vérifie pas** l'affirmation auprès de l'éditeur : ne pas encoder `5000` comme seuil universel et intemporel. Séparer les limites de l'application, le budget de rendu, la version de Design Space et les limites de machine ; faire contrôler la documentation officielle datée si une valeur chiffrée affecte le prévol.

## 3. Opportunités nouvelles de #141 et décisions candidates

| Sujet | Décision | Domaine/contrat à réemployer | Bloqueur concret |
|---|---|---|---|
| **Smart Delivery** | **P1 fort** : SD0 plan, SD1 ZIP mono-artefact, SD2 guide/offline, SD3 reprise versionnée P2 | W05/W06, `delivery_manifest` historique, source/QA/projet V1 | typer les vrais exports ; ZIP relu, hash et no-clobber |
| **Smart Cut Advisor** | **P1 / RAFFINER**, aucune garantie matière inventée | W07, C07/C08/C09, O-028/O-029 | métriques topologiques vérifiées, variantes conservant l'original |
| **Print Then Cut Assistant** | **P1 / RAFFINER** | W08, C01/C10/C11, O-001/O-002/O-032 | alpha/bleed, DPI, dimensions et transfert externe daté |
| **Smart Weeding** | **P1 diagnostic**, création de chemins **P2 sous preuve** | W09, prévol et couche CUT existante | risque de coupes dommageables sans coupons physiques |
| **Smart Cost** | **P2 CANDIDAT** | W12/W16, C15 | prix/temps/pertes seulement si mesures/saisie vérifiables |
| **CSV/QR et variantes** | **P2 extension** | W12/W16, CSV/objets existants | ne pas exécuter formules, maintenir identités/reprise |
| **Smart Cut Feedback (photo)** | **P2 exploration** | W16, QA/provenance | jeu de données avec consentement et incertitude |
| **Recettes partageables / SD3** | **P2** | W05/W06/W12/W16 | version/ressources/licences et reconstitution contrôlée |
| **Multi-machines** | **P2 exploration** | W04/W16 | ne pas simuler des commandes/outils non documentés |
| **Optimiseur multicritère** | **P2 exploration** | W07/W12/W16 | pas d'« optimal » sans modèle métrique éprouvé |
| **G6 texte/gabarits et G9 OCR/diorama** | **HÉRITAGE OBLIGATOIRE** avec priorités V3.3 P1/P2 | W10/W11/W16, COV10C | 10 exigences actuellement sans ticket V34 direct |

Ces décisions sont **des arbitrages initiaux**. La revue sémantique individuelle des 33 opportunités V3.4 contre chaque lot/ticket et contre les 80 UX est **encore ouverte**. Un tableau de mapping Wxx ne remplace pas cette revue.

## 4. Registre des risques et contre-mesures

| Risque | Sévérité qualitative | Prévention vérifiable |
|---|---|---|
| Perte d'exigences anciennes | **Critique** | 24/141/140/80/437 IDs, 10 G6/G9 et 6 tests non assignés suivis ; DoD complets V3.3 conservés |
| V1 corrompu par composition/AI | **Critique** | source SHA, CAS, validation de contrat, reviewer de schéma, tests recovery |
| Fausse compatibilité Cricut | **Élevée** | preuve locale/Design Space/physique séparée, limites versionnées et UNKNOWN |
| ZIP incomplet ou dangereux | **Élevée** | hashing avant/pendant copie, contrôle de liens, zip-slip, streaming, publication exclusive |
| UX surchargée / double application | **Élevée** | un canevas, Express/Atelier/Expert, benchmark Tk/Qt/Tauri avant migration |
| Données sensibles/licences | **Critique** | aucun original, police protégée ou poids IA dans GitHub public ; opt-in réseau et inspecteur de provenance |
| Faux « 437 tests PASS » | **Critique** | SHA exact, test non-SKIP, preuve par axe, registre NOT_RUN |
| Roadmap promue trop tôt | **Élevée** | checklist de promotion, PR documentaire revue puis AGENTS séparé |
| Dette d'intégration PR | **Moyenne** | WIP code respecté, pas de PR docs supplémentaire si trois PR ouvertes |
| Dérive produits tiers | **Élevée** | compatibilité DS versionnée, source officielle datée quand nécessaire |

## 5. Prochaines décisions nécessaires

- Étudier **chaque** O-001..O-033 contre les micro-lots d'origine et les 80 UX pour fermer la déduplication, sans rouvrir les rejets.
- Définir la charte de performance/métriques (aucune mesure inventée), le contrat UI et les gates de sécurité des sorties.
- Préparer [PROMOTION_CHECKLIST.md](PROMOTION_CHECKLIST.md) : critères documentaires avant changement d'autorité, **distincts** du développement de la V3.5.

**Preuve :** consultation source snapshot, zéro test produit exécuté, aucun code/AGENTS/pr/merge modifié. La V3.4 reste ACTIVE.
