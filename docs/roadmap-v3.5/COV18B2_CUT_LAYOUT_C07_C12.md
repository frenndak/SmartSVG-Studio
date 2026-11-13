# SmartSVG V3.5 — COV-18B-2 : prévol, profils, exports, transfert et planches (C07–C12)

**13 novembre 2026 — V3.5 CANDIDATE / NON NORMATIVE.** Suite de [COV-18B-1](COV18B1_CRICUT_C01_C06.md), six UX supplémentaires C07–C12 examinées contre exigences V3.3 et DoD V3.4 (lots 13–17, 19 et 22). Source [UX #134](https://github.com/frenndak/SmartSVG-Studio/issues/134) / [COV17C](COV17C_UX_C01_C18_SEMANTIC_AUDIT.md), registre V3.4 lot 23, snapshot main aa0ff9e7d0c53dba3fdc429c02c6198736cfe935. Les nombres de tests historiques décrivent des **recettes**, pas des tests exécutés.

## 1. Contre-expertise individuelle

| UX | Héritage et tickets de référence | Contre-avis et risque de faux positif | Décision candidate et DoD |
|---|---|---|---|
| **C07 — Smart Cut Advisor / prévol** | **S-056 P0** géométrie CUT mm, holes/islands/segments/offset et coupon réel ; **S-085 P1** alertes précises sur chemins, lot 23 V34-108/109/118 et T-V34-22-08 | Un avertissement géométrique n'identifie pas la résistance d'un vinyle, la qualité d'une lame ou la coupe garantie ; les seuils de finesse restent UNKNOWN sans coupon. | **P0 AMÉLIORER** : diagnostics explicables par contour/segment, topologie, doubles chemins, version et provenance ; variante simplifiée en brouillon, aucun badge « fabriquable » non prouvé. |
| **C08 — Profils machine/matériau/lame/tapis** | **S-031 P0** matrice Explore 5, coupons fabriqués/documentés ; **R33-022** version Design Space associée aux preuves, lot V34-15 profils et V34-124 | Un champ « vinyle » ou « cardstock » n'est pas un profil matériel validé. Un profil inconnu ne doit jamais hériter du statut KNOWN par simple nom. | **P1 RACCORDER** : machine/modèle, outil, tapis, matière, épaisseur, support, source/édition/date et état KNOWN/UNKNOWN/REJECTED, preuves physiques séparées. |
| **C09 — Fidèle / équilibré / découpe facile** | **S-034 P1** simplification Bézier avec fidélité non dégradée ; **S-060 P1** score séparé silhouette/couleur/géométrie sur corpus fixé ; prévol S-056 P0 | Trois variantes avec courbes plus simples ne démontrent pas le même résultat visuel ou un temps de coupe mesuré. Perte d'un trou = rejet même si moyenne excellente. | **P1 AMÉLIORER** : trois projections réversibles liées à la même source, métriques/diff, aucun remplacement avant confirmation et profil matière UNKNOWN explicite. |
| **C10 — Quatre formats distincts** | **R33-008** séparation PNG PTC, SVG Basic Cut, SVG CUT multicouche, SVG éditable ; **S-032 P0** export édition ≠ fabrication ; **S-054 P0** preuves orthogonales/sidecar ; lot 17 V34-129, T-V34-17-01..05 | Artifact.use V1 possède seulement trois usages autorisés ; une projection CUT multicouche EXTERNE ne doit jamais être enregistrée sous editable_svg. | **P0 GARDER** : un contrat par rôle, dimensions/QA/provenance indépendantes, erreurs par rôle, exports absents non fabriqués. Smart Delivery assemble seulement les sorties réellement qualifiées. |
| **C11 — Transfert guidé Design Space** | **R33-022** version DS liée à preuve, **S-029** import PTC contrôlé, **S-031** coupons Explore 5 ; V34-130 guide, V34-107/116/117/121 selon opération | L'assistant ne contrôle pas l'application Cricut. « Préparer un import » ne signifie ni opération automatiquement attachée, ni calibration faite, ni coupe prouvée. | **P0 RACCORDER** : guide manuel avec vérification tailles/Attach/Score/Draw/Foil, version DS connue ou UNKNOWN, hors-ligne SmartSVG ≠ Design Space hors-ligne. |
| **C12 — Smart Layout planches 12/24/50** | **S-038 P1** checkpoints/reprise sans doublon, **S-040 P1** imposition zéro collision/dimensions cohérentes, **S-062 P1** 50 objets après interruption ; V34-134/135/138, lot 19 | 50 instances de travail ne permettent pas un pack V1 avec plus de 32 sujets ; les copies d'une silhouette ne sont pas des identités de sujets fusionnées. | **P1 RACCORDER** : distinguer sujet source, instance de placement et page ; planifier/écrire atomiquement par page, reprendre les seuls échecs, contrôler les collisions et quotas. |

## 2. Architecture sans doublon de moteurs

**Contrats candidats, non encore implémentés :** CutPreflightResult {source_sha, geometry_revision, per_path_findings, confidence_level, profile_version}; MachineProfile {machine,tool,mat,material,version,source,review_date,status}; LayoutPlan {source_subject_id,instance_ids,page_ids,dimensions_mm,locked_placements,expected_revision}; ExportResult {role,artifact_sha,units,qa_axis,report}. Il s'agit de données d'échange à raccorder aux ports existants, **pas** de nouveaux writers parallèles. V1/float32/CAS demeurent autorités et aucun rôle supplémentaire n'est inséré dans Artifact.use.

**Séquence de travail** : géométrie source → premier prévol local → variante éventuelle en brouillon → profil tri-state → choix du rôle export → QA et publication externe → guide Design Space → mesures physiques séparées. **Smart Delivery V1–V3** consomme ExportResult après prévol, vérifie les fichiers/hashes/manifestes et ne transforme jamais UNKNOWN en PASS. Les outils de Fabrication ne doivent pas dupliquer les règles de publication de ZIP.

**Débutant** : une intention, un aperçu, une action de correction et un statut lisible « vérifié localement / à vérifier dans Design Space / à tester physiquement ». **Expert** : chemin précis, unités mm, outils/versions, SHA, diff entre variantes, page/instance, feuilles et preuves réelles. Les icônes seules ne portent pas les statuts.

## 3. Négatifs et plans de recette, NOT_RUN

1. Deux paths superposés et une pointe fragile : trouver les régions précises, pas un score global ; si matériau UNKNOWN, ne pas qualifier une coupe.
2. Machine/profil expiré ou outil indisponible : état UNKNOWN ou REJECTED, jamais substitution automatique.
3. Une variante « facile » supprime un trou : refuser et conserver le contour fidèle malgré diminution de nœuds.
4. MultiCut sérialisé sous editable_svg V1 : refus contractuel ; exporter les groupes dans une projection externe typée.
5. Score non attaché, dimension d'import différente de la dimension mm source, version DS inconnue : guide d'action manuelle, pas badge de réussite.
6. Planche de 50 instances avec une page corrompue : reprise déterministe des seules pages manquantes, aucun double ID et aucune archive V1 au-delà des limites du schéma.
7. Rotation/marge de nesting hors tapis ou feuille : aucune garantie de placement, cache et sources inchangés.
8. Annulation, crash, disque plein ou conflit CAS : sortie partielle non publiée, retours vérifiables sans écraser une livraison existante.

**Axes de validation distincts** : fixtures CPU/unitaires et topologie, UI Windows 1366×768/DPI 200 % (clavier/focus), compatibilité Design Space par version, coupons Explore 5 documentés séparément ; RTX/GPU seulement pour les opérations IA facultatives avec licence/consentement. Toutes ces validations sont **NOT_RUN dans cette fiche**. Les cibles p50/p95 et coûts ne sont pas des mesures actuelles. Contrat des 25 obligations de qualité appliqué, y compris sécurité, confidentialité, rollback, 24/141/140/80/437 univers historiques préservés.

## 4. État et suite

**C07–C12 examinés : 6/6 décisions candidates, 0/6 certifiées.** Avec COV18B1, 12/18 UX C bénéficient de cette revue contradictoire, mais aucun code produit ou test machine n'a été changé. La V3.4 reste normative.

**Prochaine action unique COV-18B-3 :** C13–C18 (nesting, placements verrouillés, coût matière, Fabrique, patrons et simulation 3D), puis contre-expertise des D01–D12 et E01–E20, rapprochement des 33 opportunités et revue finale.
