# V35-COV-18D3 — Revue contradictoire E13–E20 : preview, QA, Windows, confidentialité, aide

**13/11/2026 — CANDIDAT NON NORMATIF.** V3.4 reste ACTIVE. Sources effectivement lues : PROGRESS dernière section COV18D2, README, INHERITANCE_REGISTER (libellés E13–E20), AUTOMATION_QUALITY_CONTRACT (25 axes), issue #142, COV18D2. **Limite :** DoD locaux V34, APIs actuelles et HEAD exact de main non certifiés dans cette passe ; les correspondances de lots sont hypothèses à valider. Aucun test produit exécuté. Aucun moteur, schéma ou dépendance nouveau n'est autorisé par cette fiche.

## 1. Huit décisions séparées, avec critères falsifiables

| ID #134 / libellé original | Décision, priorité, sources à vérifier | Contrat et critère de non-régression |
|---|---|---|
| E13 — previews async/caches bornés/requêtes périmées | AMÉLIORER P0 ; lots V34 07/11/12/18/21 | Preview non mutante ; réponse liée au projet SHA, sélection, paramètres et génération ; seule dernière génération valide peut être affichée. Cache borné en octets, invalidation explicite et libération à fermeture. |
| E14 — diagnostics réparables et erreurs compréhensibles | RACCORDER P0 ; lots 04/07/21/22 | Code erreur stable, cause vérifiable, action de correction, état du projet inchangé ; aucune fuite de chemin absolu ou donnée privée dans message. |
| E15 — QA alpha/contours/couleurs/résolution | GARDER+AMÉLIORER P0 ; lots 12/17/22 | QA raster par artefact et rôle d'export, alpha/ICC/DPI/EXIF/bleed mesurés ou UNKNOWN ; résolution native ≠ interpolation. |
| E16 — QA SVG chemins/topologie/viewBox/mm | AMÉLIORER P0 ; lots 13/14/17/22 | Parser XML sécurisé, namespaces, unités/viewBox, contours ouverts/fermés, trous/îlots et complexité ; SVG édition et SVG CUT contrôlés séparément. |
| E17 — QA fabrication/profil/machine et preuve physique séparée | GARDER P0, essais physiques gate distinct ; lots 14–17/22 | Profil matière/tapis/outils KNOWN/UNKNOWN ; prévol local ne produit jamais COUPE_PHYSIQUE_PASS, compatibilité DS jamais déduite d'un SVG parseable. |
| E18 — packaging Windows/hors ligne/update/rollback | AMÉLIORER P0/P1 ; lots 04/21/22 | Installation autonome sans ComfyUI, démarrage offline, dépendances et licences explicites, update vérifié avec retour arrière et conservation du V1 ; benchmark Tk/Qt/Tauri avant migration. |
| E19 — confidentialité/local/opt-in réseau | GARDER+AMÉLIORER P0 ; lots 04/08–11/20/21 | Aucune requête ni téléchargement sans consentement ; EXIF/chemins/tokens purgés des livrables publics ; audit des données de télémétrie. |
| E20 — tutoriels/aide contextuelle | RACCORDER P1 ; lots 02/07/21 et annexe UX | Aide offline contextualisée au geste, erreurs et états ; jamais tutoriel mensonger sur coupe certifiée ; débutant/expert utilisent les mêmes commandes. |

**Revue hostile :** huit « Smart » assistants séparés seraient plus visibles mais dupliqueraient prévol, notifications, cache et état ; **REJETER**. Une preview GPU obligatoire pénaliserait le CPU/offline : **REJETER**. Un installateur auto-update muet simplifierait le déploiement mais viole consentement/rollback : **REJETER**. Conserver le QA raster/vecteur/machine comme trois vérificateurs spécialisés consommés par une **présentation de diagnostics commune**, et ne pas faire d'un rapport local un certificat de coupe.

## 2. Architecture candidate — contrats à raccorder aux ports réels, sans inventer d'API existante

`PreviewRequestV1{request_id,project_sha256,selection_revision,generation,role,parameters_digest,resource_budget_bytes}` → `PreviewResultV1{request_id,source_sha256,generation,status:READY|STALE|CANCELLED|FAILED,artifact_ref?,diagnostics[]}`. `artifact_ref` est temporaire et local, jamais une mutation V1. Les buffers/cache doivent être invalidés au changement de SHA, masque float32, sélection, paramètres, zoom pertinent ou fermeture ; réponse tardive ignorée. L'ordonnancement doit respecter l'UI Tk existante jusqu'à preuve d'une migration.

`DiagnosticV1{code,severity:INFO|WARNING|BLOCKER|UNKNOWN,source_role,source_sha256,measured_value?,unit?,profile_state:KNOWN|UNKNOWN,remediation_key?,evidence_ref?}`. Les mesures ne doivent jamais être devinées ; UNKNOWN n'est ni PASS ni FAIL. Une action « réparer » génère un brouillon réversible et une nouvelle QA, pas une modification silencieuse du fichier original. Toute correction exige un expected_sha CAS et passe par le writer V1 unique.

`QaReportV1{artifact_sha256,export_role:PNG_PTC|SVG_BASIC_CUT|SVG_MULTILAYER_CUT|SVG_EDITABLE,checks[],profile_revision?,ds_version?,test_level:LOCAL|WINDOWS_UI|DESIGN_SPACE|PHYSICAL}`. Une vérification LOCAL ne peut remplir les autres niveaux. Les quatre rôles sont distincts, y compris quand un seul est exporté. Les opérations CUT/SCORE/DRAW/PRINT/FOIL restent des intentions distinctes, non inventées à partir de la couleur des calques. La qualité PTC dépend du bleed et des dimensions réellement disponibles ; aucun faux profil Explore 5.

`ReleaseEvidenceV1{source_commit,build_sha256,platform,dependency_manifest,offline_smoke_status,update_status,rollback_status,windows_ui_status}` est un **format de preuve documentaire candidat**, pas une modification du projet .smartsvg. Les mises à jour ne remplacent jamais un projet utilisateur ; rollback de l'application et recovery du projet sont deux procédures différentes. Toute évolution du packaging, des dépendances ou de la gouvernance requiert une revue propriétaire distincte.

## 3. UX : novice et expert, états et accessibilité

**Novice** : importer → aperçu avec indicateur « calcul en cours » → modifier sans toucher à la source → lire un diagnostic compréhensible (« contour ouvert : inspecter ») → corriger avec Undo → choisir un des quatre exports → prévol correspondant → enregistrer. **Expert** : même pipeline, inspection des valeurs, unités, SHA, profils et rapports détaillés. Les diagnostics s'affichent dans le panneau contextuel commun, pas huit modales.

États E13 : EMPTY→PENDING→READY ou STALE/CANCELLED/FAILED ; un aperçu obsolète ne remplace pas le READY récent. États QA : NOT_RUN→RUNNING→PASS/FAIL/UNKNOWN ; changement d'artefact ou profil invalide le rapport. États update : AVAILABLE→CONSENTED→STAGED→VERIFIED→ACTIVATED ou ROLLED_BACK/FAILED. En cas de fermeture, aucune mutation du V1, les tâches de preview sont annulées ; en cas de crash pendant update, la version précédente reste démarrable (à prouver, pas présumer).

**UI testable** : 1366×768 et DPI 200 %, clavier/focus logique, annonces textuelles des erreurs, contrastes et motion réduite ; aucune information uniquement par couleur ou animation. L'aide fonctionne sans réseau, s'adapte au rôle d'export et ne suggère pas une opération machine inconnue. Les panneaux restent utilisables en mode novice et expert.

## 4. Sécurité, ressources et consentement

XML sans entités externes ni accès réseau ; raster hostile limité avant décodage ; cache borné en mémoire/disque avec suppression à fermeture ; symlinks/reparse et chemins Windows/Unicode à tester. Les diagnostics et logs n'incluent ni image privée, ni chemins complets, ni clés. Aucun upload de projet, modèle IA, mise à jour ou télémétrie par défaut. Mode CPU/manual toujours fonctionnel ; GPU 8 Go uniquement optionnel après vérification de modèle/version/licence/hash/VRAM et consentement. E15–E17 n'ont **aucun besoin d'IA** pour leurs contrôles déterministes (N/A pour téléchargement modèle). E18 ne doit pas modifier AGENTS, .github ou politique de signature sans approbation.

**Performances :** mesurer p50/p95 de preview, pic mémoire, cache hit rate, temps d'ouverture offline, temps QA par type/volume, et temps rollback sur machines Windows représentatives. Définir budgets et seuils avec corpus puis relever les résultats ; aucune valeur observée n'est affirmée ici.

## 5. Matrice de tests proposés (NOT_RUN)

| Test | Entrée / action | Attendu |
|---|---|---|
| POS-01 | Deux previews successives, même projet, paramètres différents | seule la génération la plus récente apparaît ; source inchangée |
| POS-02 | PNG transparent + profil connu, SVG éditable + SVG CUT distincts | rapports raster/vecteur et rôles séparés, mesures avec unités |
| POS-03 | démarrage Windows sans réseau ni ComfyUI, aide locale | interface et tutoriels accessibles, aucun téléchargement |
| NEG-01 | réponse preview tardive après changement SHA/selection | STALE, pas d'affichage ni commit |
| NEG-02 | PNG hostile avec dimensions déclarées excessives / ICC corrompu | rejet borné, diagnostic sans crash ni allocation démesurée |
| NEG-03 | SVG avec entité externe / viewBox absent / unités ambiguës | parsing sécurisé, BLOCKER ou UNKNOWN, jamais « prêt à couper » |
| NEG-04 | profil machine UNKNOWN et version DS non vérifiée | prévol non certifiant, pas de PASS physique |
| NEG-05 | réseau refusé + demande update/modèle | aucun accès réseau ; parcours manuel disponible |
| NEG-06 | chemin Unicode, reparse pointant hors zone, espace disque insuffisant pendant staging | pas d'écrasement, rollback vérifiable, pas de fuite de données |
| REC-01 | annulation QA/preview, fermeture puis reprise | ressources libérées, V1 inchangé, nouvelle exécution propre |
| REC-02 | crash pendant staging/update puis relance | ancienne version démarrable ; état incertain signalé, pas de faux PASS |
| CONC-01 | modification concurrente CAS entre QA et export | QA invalidée et nouveau prévol requis |

Fixtures synthétiques autorisées seulement, aucune police ou image non libre. Pour E17, prévoir trois rapports distincts : unité/CPU, import Design Space versionné, coupe Explore 5 avec dimensions mesurées et protocole physique ; **tous NOT_RUN**. Windows UI, GPU, Design Space, coupe physique = NOT_RUN ; tests unitaires également NOT_RUN.

## 6. Micro-lots TDD et DoD candidats

1. **D3.1** : retrouver ports existants preview/cache, QA raster/vector/machine, packaging, help dans HEAD main et PR ; cartographier signatures, DoD V34 et scénarios exacts. **BLOQUANT pour certification**.
2. **D3.2** : tests stale/cache/cancel/close sur ports existants ; ajouter uniquement les adaptateurs nécessaires, sans deuxième moteur.
3. **D3.3** : QA à quatre rôles + diagnostics UNKNOWN, fixtures négatives XML/PNG, SHA/profil et invalidation.
4. **D3.4** : validation Windows offline/rollback, privacy opt-in, accessibilité et tutoriels ; tests DS/physiques indépendants.

DoD : chaque E13–E20 dispose d'un ticket source vérifié, de tests positifs et >=3 négatifs pertinents, d'une trace SHA et d'un protocole de rollback ; aucune fonction « intégrée » sans preuve code main + exposition Windows + tests non skip. Le graphe minimal est preview→QA artefact→diagnostics→export/livraison ; packaging/help/privacy traversent le flux, pas une dépendance artificielle sur IA. Toute migration de framework ou de schéma est hors autorisation de cette tâche.

## 7. Audit des 25 axes — statut documentaire

01 inventaire 24 lots **conservé**, couverture sémantique ouverte ; 02 141 exigences conservées, dix G6/G9 non résolues ; 03 140 tickets conservés, DoD à vérifier ; 04 E13–E20 **8/8 traités ici**, total UX deuxième niveau 80/80 à confirmer dans PROGRESS ; 05 437 scénarios inventoriés, 431 liens historiques, six exceptions ; 06 statuts indépendants, main HEAD NON_VÉRIFIÉ ; 07 V1/CAS/float32 conservés ; 08 quatre rôles distincts ; 09 machine/DS/physique séparés ; 10 parcours novice/expert décrit ; 11 sélection/Undo brouillon explicités ; 12 accessibilité protocole prévu ; 13 annulation/crash/concurrence prévus ; 14 IA facultative, N/A aux contrôles QA déterministes ; 15 QA raster/alpha/ICC prévu ; 16 SVG sûr/topologie prévu ; 17 Fabrique/CSV N/A à cette fiche (héritage conservé, aucun changement) ; 18 Smart Delivery N/A en implémentation, rapports QA réutilisables sans nouveau ZIP ; 19 autres opportunités non arbitrées dans cette fiche ; 20 métriques protocolées non mesurées ; 21 confidentialité/licences revues ; 22 branche documentaire seule, WIP PR à vérifier ; 23 refus de moteurs/assistants dupliqués ; 24 aucune promotion ; 25 aucun contrôle supprimé. **Ce contrôle est une revue de présence, pas certification d'exécution.**

**Prochaine action unique après publication : V35-COV-19 — revue contradictoire O-001..O-033 avec source OPPORTUNITIES et #141, décisions et dépendances individuelles.**