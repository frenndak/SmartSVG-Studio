# Arbitrages transversaux V3.5 — décisions exécutables

**14/11/2026 — décisions candidates à contre-relire avant adoption.** Corrige les contradictions concrètes trouvées dans les relectures indépendantes A/B, C et de l'orchestration ; les observations partielles D/E sont signalées au rapport. Les sources V3.4/V3.3 restent intactes. Dans la candidate, ces décisions remplacent les formulations locales contradictoires des anciens COV cités, jamais un critère historique sans arbitrage explicite.

## D01 — Sélections souples, topologie voulue et topologie perdue

Propriétaire W02/A03 pour masques, géométrie W03/A14. Sur le même repère source, masque float32 fini dans [0,1] : union `max(A,B)`, intersection `min(A,B)`, soustraction `min(A,1-B)`, inversion `1-A` **sur le domaine source complet borné**. Une ROI d'inversion est une option explicite et le reste est inchangé. Pas de seuillage L8 implicite ; autre algèbre nécessite une opération nommée/versionnée, pas une variation cachée du même bouton. Origine/dimensions différentes → refus ou rééchantillonnage explicite sur copie ; toute modification invalide puis revalide la preuve sujet selon contrat.

Une simplification « préserver le dessin » doit conserver trous/composantes dans les tolérances annoncées (T-V34-13-09). Une union/soustraction/inversion **voulue** peut créer/supprimer un trou : afficher opérandes, ordre, différence de composantes/trous et aperçu ; appliquer par geste utilisateur réversible, nouveau prévol CUT. Un anneau volontairement rempli n'est pas automatiquement une erreur. Morphologie A05 et correction alpha A07 suivent la même distinction : changement voulu annoncé versus perte silencieuse. Remplace les interdictions universelles de COV17A AUDIT et COV18A CROSS_REVIEW.

Tests proposés : anneau+disque→trou rempli volontairement ; disque moins disque intérieur→anneau ; A=.3,B=.7 : union .7, intersection .3, soustraction .3, inversion .7 ; double inversion tolérance float32 documentée ; simplification absorbe un trou→refus ; operand permuté change soustraction→aperçu explicitement distinct ; NaN/dimensions incohérentes/ancien SHA→zéro commit. Undo restaure exactement les patches, sans promettre une égalité arithmétique bit-à-bit après deux inversions recalculées.

## D02 — Calques et responsabilité fabrication

B02 : contrat complet et comportements locked/parent/hidden/opacité dans ADR_COMPOSITION_PERSISTENCE. Multi-vinyle : W03 géométrie/export + W04 validation fabrication, puis W09 échenillage consommateur. **W05 signifie SD0**, jamais « fabrication » : l'étiquette de COV18A2D §2 était erronée. Emballer une sortie n'en devient pas propriétaire géométrique.

C03/W03+W04 : pour HTV, décision de miroir **par couche** explicite avec contexte matière/profil et conservation au manifeste ; une couche sans décision reste NEEDS_REVIEW, jamais « prête machine ». Fixture trois couches dont une sans décision ; choix de miroir ne change pas ordre ni alignement. Raccord explicite T-V34-14-22, S-045 et T-V34-17-04 ; essais de superposition distincts d'un DRAW+Cut.

C04 : largeur de pont inconnue/matière inconnue → diagnostic et brouillon non qualifié, sans seuil universel inventé ; géométrie invalide → refus de publication fabriquable. C05 : DRAW accepte une ligne centrale existante prévolée ; son **extraction** est une capacité séparée W03/A12+C05, dépendance d'un extracteur qualifié. Fixture trait épais avec bifurcation : centreline ouverte continue, embranchements déclarés, erreur d'écart mesurée ; pas de remplacement par contour fermé. Les tolérances de mesure sont des paramètres du profil, UNKNOWN si absentes, et les tests de référence fixent leurs valeurs synthétiques.

## D03 — Publication, lots, identité et reprise

Trois frontières à ne plus confondre : (1) un fichier individuel est publié atomiquement ; (2) un ensemble de pages/fichiers peut être **PARTIAL**, ses sorties saines conservées et reçu final honnête ; (3) un ZIP Smart Delivery est publié tout entier ou pas du tout. « Aucun export partiel » dans COV18B2/B3 ne signifie jamais effacer les 17 pages déjà vérifiées quand la 18e échoue. Un pack PARTIAL peut contenir un sous-ensemble explicitement choisi et vérifié, mais son manifeste ne proclame jamais le lot d'origine complet.

Identités W12 : SubjectRef = project_id + project_sha256 + subject_id ; PlacementInstance = instance_id stable + SubjectRef + transform_mm + rôle/opération + page_id. Deux placements peuvent référencer le même sujet, mais ont des instance_id distincts. Le cache de placement et le checkpoint de batch ne deviennent pas un projet éditable. Clé d'invalidation = source/projet/template SHA, masque/offset, dimensions mm/DPI, rotation, paramètres, rôle/opération, profil/version et version de l'algorithme. Un changement impose nouvel aperçu/revalidation, pas reprise sur ancien cache.

Première tranche 12/24/50 : traitement borné, pages externes, checkpoints locaux privés ; limite V1 de 32 masques inchangée. Persister 50 sujets dans un même projet appartient au V2 et aux packs internes de Q04/ADR, pas à cette première tranche. Respecter footprint **après offset**, groupes Score+Cut indivisibles, placements verrouillés jamais déplacés implicitement, collision après rasterisation et repli grille historique (lot19). Test 50 copies de 12 sujets distinct du test 50 sujets persistés ; panne page2 garde page1 saine ; reprise 17/30 et 17/50 sans doublon, source changée→STALE.

## D04 — États de batch et recettes

Unité : QUEUED/RUNNING/READY_FOR_REVIEW/SUCCEEDED/FAILED/NEEDS_REVIEW/STALE/CANCELLED/INTERRUPTED/SKIPPED. SUCCEEDED signifie uniquement production locale relue/hash, pas fabrication. Au restart, ancien RUNNING devient INTERRUPTED après inspection de sortie ; si fichier publié et vérifiable, réconcilier vers SUCCEEDED sans réécrire ; état indécidable→NEEDS_REVIEW. Reprise explicite des QUEUED, FAILED récupérables, INTERRUPTED et CANCELLED sélectionnés ; NEEDS_REVIEW après correction, STALE seulement après nouveau plan et nouvel identifiant de tentative. Ne pas relancer les réussites. Source et paramètres identiques requis ; collision de nom refusée. Une annulation ne révoque pas un fichier déjà publié.

BatchUnit requiert `params_digest` et `capability_revision`, **recipe_sha256 facultatif** : les paramètres directs suffisent. D10 presets/recettes déterministes restent P1 selon source ; partage enrichi/optimiseur en P2. D11 P1 ne dépend pas de la bibliothèque de recettes P2. CSV formules = texte littéral à l'entrée, jamais exécution ; rapports CSV échappés contre interprétation tableur. Corrige COV18C2_IA_D07_D12_HOSTILE enum/reprise/dépendance/priorité. DoD : 30 lignes dont 17 terminées, 2 annulées, 1 erreur et restantes en attente reprennent sans doublon ni effacement des réussites.

## D05 — Bibliothèque : index jetable, préférences durables

W12/E01–E05. L'index et miniatures sont reconstruisibles depuis projets. **Tags/collections/favoris saisis par l'utilisateur ne le sont pas**, sauf s'ils sont réellement contenus dans un contrat portable qualifié. Première tranche : stockage local versionné de préférences avec écriture atomique, backup/recovery et export/import explicites ; clé project_id + résolution des duplications, pas simple chemin qui casse lors d'un renommage. Afficher « local à cet ordinateur » tant que portabilité non implémentée. Ce store ne peut modifier sources, objets, masques ou identités de projet ; il n'est pas un second writer de composition.

Corruption des préférences→récupération explicite, jamais « tout reconstruire » en effaçant les tags. Supprimer l'index doit conserver exactement préférences ; supprimer volontairement les préférences nécessite confirmation et ne supprime pas projets. Clone reçoit nouvel ID et une politique explicite de copie des tags ; aucun lien silencieux entre variantes. Portabilité future V2/extension V1 éprouvée = micro-lot séparé, aucune injection immédiate. Critère T-V34-20-06 conservé.

## D06 — Intégrité, authenticité et consentements IA

D08 : un hash vérifie des octets attendus ; **il ne signe rien et ne prouve pas l'auteur**. La provenance est établie séparément par une source de confiance épinglée/revue ; signature cryptographique uniquement si une vraie signature et une clé de confiance sont vérifiées. Corrige « signé par hash » de COV18C2. Licence/version/SBOM/code requis, consentements téléchargement/exécution/transfert séparés, source/hash inconnus→pas d'installation. Fixtures : fichier+hash tous deux remplacés mais provenance non approuvée→admission refusée ; simple hash valide ne produit aucun badge d'authenticité. Aucun modèle réel nécessaire pour tester le validateur.

## D07 — Priorités d'incréments et catalogue

La priorité source reste intacte dans PRIORITY_REGISTER ; les splits opérationnels suivants précisent une première tranche, sans renuméroter ni déclasser l'héritage : A16 métriques P1 / automatisation IA P2 ; B13 contrat/correction P1 / moteur OCR P2 ; C15 économie de matière+reprise P1 W12 (S-038/S-040/S-062, V34-134/135/138) / Smart Cost prix utilisateur P2 W16 ; C18 aperçu 2D P1 W11/V34-128 / simulation pliage3D P2 W16 ; D10 préréglages locaux P1 / partage enrichi P2. E01 bibliothèque et E06 canvas conservent leurs priorités sources ; aucune table COV sommaire ne les rétrograde globalement.

C16 : W11 catalogue initial étiquette/topper/carte conservant G6.4, puis incrément catalogue W11-CAT avec **enveloppe et pochoir** (libellé source #134), sans attendre une simulation3D. Chaque modèle définit paramètres mm, bornes, instructions d'opérations, recette sauver/réouvrir/export et prototype de l'usage déclaré. Cas enveloppe largeur/hauteur négatives, rabats superposés, pli non assigné ; pochoir îlot isolé, pont inconnu, perte de trou. Pas de faux succès physique.

## D08 — UI : choix mesuré, pas blocage global

Le spike Tk continue pour les tranches déjà utiles. Avant le gros éditeur, W13 réalise la comparaison prévue par l'annexe UX V3.4 §7, pas seulement « migrer si Tk bloque ». Même tranche à six tâches : lancement offline ; V1 read-only ; canvas12 sujets+zoom/pan/panneaux ; thèmes/clavier/focus/longue tâche/DPI200% ; sauvegarde isolée par writer ; packaging Windows et licences. Comparer deux alternatives Qt/PySide6 et Tauri/web, Tk baseline ; échec d'installation documenté, pas score inventé.

Matrice source100 : canvas25, intégration20, accessibilité15, sécurité/offline/install15, maintenance15, finition10. Chaque critère score0–5 avec protocole/trace et sous-critères annoncés ; absence de mesure=UNKNOWN et comparaison incomplète, pas zéro arbitraire. Même machine/corpus, 3 lancements froids et 100 navigations, p50/p95/RSS ; architecture/charge des fichiers identiques. Tester aussi 1280×720 et 100/125/150/200%, lecteur d'écran, annulation. Choix ADR motivé par mesures et risques, pas seulement somme. Pas de dépendance/framework installé implicitement ; PR distincte si retenu. Ce **protocole** peut être approuvé sans benchmark exécuté ; implémenter le gros éditeur attend le choix mesuré, les moteurs/contrats non UI continuent.

## D09 — Critère de roadmap prête

SPECIFIED = comportement, responsabilités, E/S, erreurs, dépendances, DoD et recettes décidés ; REVIEWED = contradiction examinée avec rapport ; ADOPTED = promotion effectuée. Aucune de ces étapes n'exige d'avoir déjà codé toutes les fonctions. À l'inverse, CODE_MAIN, UI_WINDOWS_PASS, GPU_PASS, DESIGN_SPACE_PASS et PHYSICAL_PASS exigent leurs preuves propres. Les anciennes phrases « pas prêt à coder car Windows/physique NOT_RUN » sont remplacées par cette séparation ; une ADR manquante reste un vrai défaut documentaire.

Les responsables des six exceptions sont **acceptés dans la candidate revue**, puis adoptés avec la roadmap : ne pas exiger leur adoption avant la promotion elle-même. L'autorisation de fusion automatique V3.4 ne se transpose pas par renommage : le handoff précise les références AGENTS/politique/READY/prompt ; V3.5 DRAFT-only tant qu'une décision de gouvernance n'a pas explicitement repris ce périmètre. Aucune nouvelle permission utilisateur pour simplement documenter cette règle.

Tous les tests nouveaux de ce document sont **NOT_RUN**. Les 25 axes et les limites de revue sont suivis dans CAMPAIGN_REVIEW_2026_11_14.md.
