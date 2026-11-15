# Ajouts V3.5 : décisions et tranches de réalisation

15 novembre 2026 — candidate, revue documentaire du producteur. Base `7ad94ba3e411ea543d3a95657b59690bbbededbc`. Ce document complète COV19 et le programme #142 ; aucun code, modèle, essai Windows ou physique n'est déclaré livré. Les coûts sont des estimations relatives de conception : F faible (présentation/adaptateur), M moyen (contrat + moteur existant + UI), E élevé (nouvelle géométrie, migration ou preuve terrain). Ce ne sont ni des durées promises ni des budgets financiers.

## Contrat commun d'une tranche

Entrée liée à `project_id`, SHA/révision, source/artefact SHA, paramètres avec unités, rôle parmi les quatre exports et version des capacités/profils. Sortie : proposition/diagnostic/rapport typé avec origine, limites et état ; une proposition ne modifie rien. États EMPTY, RUNNING, READY, STALE, CANCELLED, FAILED et NEEDS_REVIEW ; les unités batch suivent DECISIONS_TRANSVERSALES D04. Aucun faux succès lors d'un résultat tardif, d'une licence inconnue ou d'un profil incomplet.

Les commandes acceptées passent par le bus/receipt/CAS unique du format actif ; les publications externes par exporteur existant puis publication exclusive et relecture. Undo porte sur le projet, pas les fichiers livrés ni la machine. Les nouveaux noms de données ci-dessous sont des contrats proposés, pas des APIs déjà présentes.

Chaque tranche reprend les tests du ticket propriétaire, plus : source changée après aperçu ; donnée requise inconnue ; entrée hostile/hors quota ; annulation/panne/reprise ; concurrence/double activation. Les cas applicables doivent avoir un oracle explicite, pas cinq tests génériques répétés. UI : novice avec une action principale, détails expert repliables, erreur réparable, clavier/lecteur écran/contraste/zoom hérités. Mesurer p50/p95, mémoire et annulation sur corpus autorisé avant promesse de performance. Rollback : désactiver le consommateur nouveau et conserver sources, projets et sorties saines.

## 33 opportunités, propriétaires et preuve discriminante

Les critères de chaque opportunité dans [OPPORTUNITIES V3.4](../roadmap-v3.4/OPPORTUNITIES.md) restent intégralement conservés ; les tableaux de DoD des lots V34 restent applicables. Les huit rejets sont maintenus. Fusion signifie présentation commune, pas disparition d'une assertion.

| ID | Décision ; propriétaire ; effort | Entrée → sortie et critère de tranche |
|---|---|---|
| O-001 | Raccorder ; V34-131/130, W08 ; M | Export SHA + déclarations locales → journal supprimable. Cocher « importé » ne crée jamais une preuve DS ; changement d'export isole le journal. Q01 et lot17 T07/08. |
| O-002 | Améliorer ; V34-110/122/130, W08 ; M | PNG + mm + profil daté → checklist échelle/orientation. Profil absent garde UNKNOWN, aucune marque capteur inventée ; lot15 T13/14 et lot17 T02/09. |
| O-003 | Rejeter ; aucun nouveau ticket | Pas de pilotage Cricut non documenté. Alternative : fichiers + guide manuel. Test absence d'appel machine. |
| O-004 | Raccorder ; V34-106/108/111/112/113, guides121/130, W04 ; M | Opérations CUT/SCORE/DRAW/FOIL typées → aperçu de séquence indicative. Croisement intentionnel différent du doublon ; lot14 T08–17/29. Outil/matière non qualifiés restent UNKNOWN. |
| O-005 | Reporter P2 ; W16, patron lot16 ; E | Panneaux/charnières/mm → aperçu 3D géométrique expérimental. Cube synthétique, arêtes raccordées ; collision/épaisseur inconnue visibles. Retour 2D, aucune preuve carton. |
| O-006 | Améliorer ; V34-021, W01 ; M | Même projet sur copies legacy/native → diff sémantique. IDs/mm/masques comparés, SHA ZIP seul insuffisant ; lot04 T11–14. Double calcul opt-in, original intact. |
| O-007 | Raccorder ; V34-024, W01/W15 ; F | Inventaire offline → absent/présent/vérifié/testé distincts. Modèle présent non testé ne devient pas runtime qualifié ; lot04 T08–10/15. |
| O-008 | Améliorer ; V34-031, W12 ; M | Archive + ressources/licences → inventaire partage autorisé/refusé. Ressource manquante, police non redistribuable, chemin privé signalés ; copie expurgée, original intact ; lot05 T02/06/07/17/19. |
| O-009 | Raccorder ; V34-035/038, W02 ; M | Groupe de commandes → preview Undo, puis confirmation si nécessaire. Prévisualiser zéro écriture ; undo atomique, bit-identité float32 ; lot06 T13–16/21/23. |
| O-010 | Améliorer ; V34-039, W14 ; M | Proposition r8 arrivée à r9 → boîte locale bornée. Comparer ou relancer, jamais rebind automatique ; purge sans mutation du projet ; lot06 T17/18/20/27. |
| O-011 | Raccorder ; V34-048, W01 ; M | Import autorisé → brouillon temporaire clairement non enregistré. Abandon nettoie ; crash n'invente pas de projet canonique ; lot07 T02/03/09/28. |
| O-012 | Fusionner surface ; V34-049, W04/W13 ; F | Types d'opérations → texte/motif/icône accessibles. Motifs UI jamais exportés comme chemins CUT ; lot07 T17/19/22/27. |
| O-013 | Fusionner surface ; V34-056, W14 ; F | Règle/source/limites → justification repliable. Basic Cut annonce perte des couleurs internes ; justification modèle ≠ preuve ; lot08 T11/13/21/22. |
| O-014 | Améliorer ; V34-055/057, W12 ; M | Préférence locale datée → suggestion de cote/intention. Sans choix explicite aucune cote physique appliquée ; changement profil invalide ; lot08 T19–21. |
| O-015 | Rejeter ; aucun nouveau ticket | Pas d'écoute permanente. Alternative texte/clavier ; aucun accès microphone au lancement. |
| O-016 | Raccorder ; V34-062/065, W02/W14 ; M | Plan simulé → diff exact des champs modifiés. Mutation absente du diff invalide acceptation ; plan stale exige nouvelle simulation ; lot09 T15/25/26. |
| O-017 | Fusionner surface ; V34-066, W15 ; F | Code blocage + champ → correction guidée sûre. Valeur manquante jamais inventée, SHA inchangé tant que non accepté ; lot09 T27/28. |
| O-018 | Rejeter ; aucun nouveau ticket | Pas d'autovalidation des plans IA. Confirmation groupée liée au digest ; lot09 T17/18/21/23, zéro commande sans consentement. |
| O-019 | Améliorer ; V34-073, W02/CP3 ; M | Accessoire + parents candidats → relation réversible. Graphe acyclique, parent orphelin refusé, pixels inchangés ; lot10 T15/20. Persistance suit le modèle objet qualifié. |
| O-020 | Raccorder ; V34-076, W02 ; M | Masque float32/seed → points d'inspection 1:1 reproductibles. Changement masque invalide inspection, échantillons jamais annoncés exhaustifs ; lot10 T15/16/27/28. |
| O-021 | Rejeter ; aucun nouveau ticket | Pas d'upload automatique de photos. Import manuel/CPU = zéro requête, lot10 T24/25. |
| O-022 | Améliorer ; V34-084, W14 ; E | Même ROI/référence manuelle + modèle déjà admis → gain marginal/temps/mémoire. Sans vérité terrain, comparaison visuelle seulement ; lot11 T19/20/27/28. Distinct de migration O-006. |
| O-023 | Raccorder ; V34-086, W14 ; M | Artefact modèle exact → admission avant inférence. Révocation ou source inconnue bloque malgré hash cohérent ; lot11 T02/04/05/10/15–17 ; DECISIONS D06. |
| O-024 | Rejeter ; aucun nouveau ticket | Pas d'installation silencieuse ; catalogue sur demande, consentement et provenance préalables. |
| O-025 | Raccorder ; V34-095, W03 ; M | PNG final relu → aperçu blanc/noir/damier et taille indicative. Franges visibles, zoom ne change pas export ; lot12 T06/09/11/12/17/20/27. |
| O-026 | Améliorer ; V34-095, W03 ; M | Proposition et PNG publié → diff alpha aux seuils historiques 0/20/128 (échelle L8 de diagnostic seulement). Trous/îlots apparus localisés ; masque float32 source inchangé. Aucun seuil de fabricabilité inventé. |
| O-027 | Rejeter ; aucun nouveau ticket | Pas d'upscale IA automatique 600 ppp. Dimension et besoin réels, CPU/IA opt-in ; D05 reste conservé. |
| O-028 | Améliorer ; V34-101/103/109, W07 ; M | SVG développé et profil daté → compte de chemins/complexité. Le nombre historique 5 000 reste une observation à revalider, pas une constante machine universelle. Q01 sépare limites inspecteur, logiciel et DS. Conserver T-V34-13-16 : fixture5 001 chemins refusée contre budget logiciel injecté5 000 ; cet oracle ne certifie aucune limite matérielle. |
| O-029 | Raccorder ; V34-097/102, W03/W07 ; M | Géométrie + trous/îlots essentiels verrouillés → simplification candidate. Perte d'un élément protégé refuse proposition ; annuler restitue état ; contraintes conservées à la réouverture selon ADR. |
| O-030 | Rejeter ; aucun nouveau ticket | Couleur seule ne devient jamais opération CUT. Conversion explicite avec prévol, quatre rôles conservés. |
| O-031 | Raccorder ; V34-108/109, W04 ; M | Segments + opérations → conflits localisés. Doublon CUT/CUT signalé, croisement voulu non bloqué arbitrairement ; lot14 T08/09/24. |
| O-032 | Fusionner surface ; V34-111/114/130, W08 ; F | Cotes attendues + saisie DS → checklist taille/Attacher. Observation utilisateur ≠ qualification physique ; lot14 T13/14/30, Q01. |
| O-033 | Rejeter ; aucun nouveau ticket | Couleurs/pointillés ne confirment pas SCORE. Candidats seulement, choix utilisateur + capacité contrôlée ; lot14 T01/02/30. |

## Les 15 groupes du programme #142 : résultat attendu et découpage

| Groupe source | Première tranche et sortie concrète | Suite conservée / DoD spécifique / coût |
|---|---|---|
| Fondation produit | W01–04 : import→retouche→sauvegarde/reprise→export, trace source→ticket→code→UI→preuve | Trois parcours E2E réellement raccordés ; gros PNG ne devient pas petit preview par erreur ; quatre exports achevés séparément. M/E selon persistance. |
| Architecture UI | W13 : même protocole six tâches Tk/Qt/Tauri et décision ADR | Mesures/installation/licences, clavier et lecteur écran ; pas de migration avant résultat, pas de blocage des moteurs indépendants. E, DECISIONS D08. |
| Smart Delivery | SD0A contrat/fixtures ; SD0B adaptateurs ; SD1 ZIP dès un export réel | SD2 guide HTML offline ; SD3 reconstitution/history séparé. Quotas, licence, SHA, no-clobber, PARTIAL honnête ; contrat SMART_DELIVERY_EXECUTION_CONTRACT. M puis E pour SD3. |
| Smart Cut Advisor | W07 : diagnostic localisé de complexité/fragilité ; variantes fidèle/équilibrée/facile sur copie | `CutAdvice{artifact_sha,profile_revision,metrics,findings,variants}` ; métriques silhouette/couleur/coupe séparées. Choix explicite puis nouveau prévol ; îlot verrouillé perdu = refus. M/E. |
| Smart Weeding | W09-A diagnostic/overlay non mutant des petites zones et espaces | W09-B lignes/boîtes sur copie après prévol et coupons. `WeedingPlan{base_sha,material_profile,regions,proposed_paths,unknowns}` ; intersection avec motif/verrou = refus ; aucune génération en présence de tolérance indispensable inconnue. M puis E. |
| Print Then Cut Assistant | W08-P : PNG/alpha/mm/bleed + checklist papier/tapis/orientation | Calibration dans DS ; aucune surface imprimable universelle. Tests O-002/O-025, aucune marque capteur imitée. M. |
| Compatibilité Design Space | W08-D : matrice profil/version/role/opération/source/date et guide manuel | Changement de version invalide preuve concernée ; import contrôlé séparé de fabrication. Journal O-001 et checklist O-032 partagent UI sans fusion de leurs critères. M + terrain. |
| Smart Cost | W16-COST : surface utilisée/perdue et prix fournis par utilisateur | `CostEstimate{layout_sha,currency,unit_price,basis,quantity,waste,included,excluded,total?,unknowns}` ; pas de total complet si prix requis absent, unités incompatibles refusées, arrondi monétaire explicite. Hors coût machine inconnu et marge commerciale supposée. M après nesting. |
| Séries personnalisées | W12 CSV texte simple/nombres d'abord ; W16-SERIES noms/QR/packaging ensuite | `SeriesPlan{template_sha,rows_digest,field_bindings,sequence,params_digest}` ; QR contient uniquement contenu validé, aperçu et décodage indépendant avant export. Glyphes manquants/ligne invalide isolés, noms collision refusés. M/E, batch 30 lignes avec reprise. |
| Smart Cut Feedback | W16-FEEDBACK : import volontaire de photo privée et points de calibration | `CutObservation{artifact_sha,photo_sha,scale_reference,alignment,uncertainty,observed_deltas}` ; photo floue/perspective sans repère = insuffisant, pas diagnostic garanti. Corpus autorisé et erreur de mesure documentée avant recommandations. E/recherche. |
| Recettes/modèles partageables | W12 préréglages locaux ; W16-RECIPE import/export externe versionné | Actions fermées, ressources/licences et versions, dry-run avant exécution ; aucune commande/code/URL arbitraire. Modèle manquant/révoqué = refus utile. Projet éditable n'est pas remplacé par recette. M/E. |
| Production multimarque | W16-PROFILE : contrat d'adaptateur de profil, sans driver | `CapabilityProfile{vendor,machine,tool,material,operation,source,version,verified_at,state}` ; état inconnu par défaut, tests propres à chaque machine, retour profil Explore 5 inchangé. E/recherche, aucune prétention matérielle. |
| Optimisation multicritère | W16-OPT : comparaison explicable de solutions déjà admissibles | `OptimizationRequest{base_sha,hard_constraints,objectives,weights,seed,budget}` ; contraintes dures d'abord, métriques absentes exclues explicitement, résultat timeout = meilleure solution vérifiée ou refus, jamais optimum garanti. E après métriques/nesting/coûts. |
| 80 capacités UX | Un catalogue de capacités et des parcours partagés, pas 80 boutons | A/B/C relus antérieurement, D/E dans REVIEW_DE_RESOLUTION ; source et priorités conservées. Le compteur ne clôt pas les critères ; revue globale indépendante attendue. M/E, preuves par fonction. |
| Héritage intégral V3.4 | Sources intègres + responsabilités corrigées + SOURCE_CLOSURE | IA facultative, 12/24/50, opérations, patrons, V1/V2 explicite, Windows autonome, 141 exigences/140 DoD/437 assertions. Pas de suppression par « P2 » ou « optionnel ». E de réalisation, revue documentaire distincte. |

## Tests et limites des ajouts sans moteur actuel

Les contrats de recherche P2 sont des lots de faisabilité bornés. Ils commencent par fixtures synthétiques et un résultat GO/NO_GO motivé, jamais par une promesse d'algorithme universel. Pour Cost : prix absent, devise mixte, surface négative et unité ambiguë ; pour séries : formule CSV inerte, QR trop dense ou non décodable, doublon de nom et fonte absente ; pour Feedback : repère absent, photo inversée, erreur d'alignement et contraste insuffisant ; pour profils : source manquante, profil périmé, outil incompatible et machine inconnue ; pour optimisation : contrainte impossible, métrique absente, budget épuisé et seed rejouée. Tous sont NOT_RUN ; chaque implémentation ajoute les oracles chiffrés de fixtures et commandes de son runner réel.

Les mesures physiques et données privées restent hors dépôt public. Une impossibilité actuelle laisse l'exigence et son motif visibles, sans remplacer une fonction héritée par une simple étude. Les extensions nouvelles P2 ne bloquent ni SD1, ni les exports de base, ni la bibliothèque et le texte hérités.

## Verdict borné

33 décisions rapprochées de leurs propriétaires/recettes, dont 8 rejets maintenus ; 15 groupes rattachés aux tranches et sorties attendues. Corrections : O-026 conserve ses trois seuils de diagnostic ; O-028 ne fige plus une ancienne observation DS ; préférences/CSV de base ne sont pas repoussés avec partage/QR avancés. **OPPORTUNITIES_CLOSURE clos au niveau documentaire du producteur**, à soumettre à GLOBAL_REVIEW avec les autres deltas. SOURCE_CLOSURE reste distinct ; aucun PASS de produit ou adoption n'est inféré.
