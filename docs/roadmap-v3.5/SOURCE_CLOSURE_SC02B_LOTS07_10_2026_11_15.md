# SC-02B — Interface, assistant, planificateur et sélection : 118 assertions

15 novembre 2026 — revue sémantique documentaire du producteur, candidate non adoptée. Main `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`, base candidate `8f718cf8a0cbbdeecb2920e28ad7389661ee352e`. Suite de SC-01 et SC-02A, sans les remplacer. **SOURCE_CLOSURE reste ouverte** pour les autres assertions, les critères intégraux et DoD non encore rapprochés. Aucun code ni test produit exécuté ici.

## Sources et règle de lecture

Les sections de contrats et DoD de [lot07](../roadmap-v3.4/07_UX_EXPRESS_NAVIGATION.md), [lot08](../roadmap-v3.4/08_ASSISTANT_CONTEXTUEL.md), [lot09](../roadmap-v3.4/09_PLANIFICATEUR_SECURISÉ.md) et [lot10](../roadmap-v3.4/10_ANALYSE_VISUELLE.md) sont confrontées aux décisions candidates, pas seulement à leurs intitulés. Blobs sources : `0846d31a7bd3b0c719423ee585e2ab8721dcbb76`, `e638a1b008aa1206b01eb4f3ef5d7ad2957c351a`, `52e61d658d47570edffb662fc4f8983cf1208512`, `9c0b0648a6b3c2790813ff59136fdb0a88df89c0`. Les textes intégraux des assertions sont conservés dans SCENARIOS_V34_02_08 et SCENARIOS_V34_09_16. Les numéros ci-dessous abrègent T-V34-LL-NN ; aucune recette nouvelle n'est ajoutée aux 437.

**Décision commune : CONSERVER l'assertion intégrale et le DoD source.** Chaque ligne précise le sens discriminant à conserver dans V3.5, son consommateur et son propriétaire fonctionnel candidat. Les propriétaires repris de la source ne sont pas tous des liens historiques explicites : 07-16 et 07-25 restent les exceptions historiques de SC-01. Une affectation complémentaire ne réécrit pas la source. Les suites corpus 058/067/077 restent responsables du parcours et des mesures, sans remplacer les tickets fonctionnels.

Les contrats détaillés à consommer sont EXECUTION_PLAYBOOK, DECISIONS_TRANSVERSALES, ADR_COMPOSITION_PERSISTENCE, les revues D/E horaires et REVIEW_DE_RESOLUTION. Dans les tables : W01=session/reprise, W02=atelier/interaction, W03=exports, W04=opérations, W13=accessibilité, W14=assistant/IA. Les préconditions de format de SC-02A s'appliquent : CAS V1 n'est pas receipt durable ; command_id/epoch/replay/Undo durable complet exigent le writer transactionnel qualifié CP2/V2. Aucun faux passage à IMPLEMENTED en ajoutant une ligne.

## Lot07 — 28 décisions d'assertion

| Assertion | Propriétaire candidat / consommateur | Sens conservé et contre-exemple exclu |
|---|---|---|
| 07-01 | V34-042 / W01 | État vide propose Importer/Créer/Reprendre ; export inactif avant artefact réel. |
| 07-02 | V34-042/048 / W01 | Import PNG travaille sur copie ; comparer octets de l'original avant/après. |
| 07-03 | V34-042/048 / W01 | Fichier tronqué refusé avec message FR, aucune mutation du projet. |
| 07-04 | V34-042 / W01 | Afficher JPEG/WebP ne prouve pas que le créateur V1 PNG les accepte ; conversion explicite tracée si ajoutée. |
| 07-05 | V34-041/046 / W02 | 100 changements d'espace restent de la navigation ; SHA/révision inchangés. |
| 07-06 | V34-041/046 / W02 | Deux vues partagent sélection résolue et révision ; événement perdu déclenche resync, pas commit. |
| 07-07 | V34-043/044 / W01 | Double clic reçoit un seul résultat durable ; CAS seul ne prouve pas le replay après ACK perdu. |
| 07-08 | V34-043/044 / W01 | Badge Enregistré après confirmation durable ; résultat indécidable demande inspection. |
| 07-09 | V34-041/044/048 / W02 | Édition externe rend le brouillon STALE, avec comparer/recharger et zéro écriture. |
| 07-10 | V34-042/044 / W01 | Pending sidecar impose RECOVERY_REQUIRED et choix explicite ; aucune restauration silencieuse. |
| 07-11 | V34-042/044 / CP1 | Ouvrir V1 n'active pas V2 ; migration sur copie avec aperçu et confirmation. |
| 07-12 | V34-047 / W14 | Sans job IA, import/édition manuels et réseau nul restent disponibles. |
| 07-13 | V34-047 / W14 | Résultat tardif isolé comme proposition STALE, jamais appliqué à la nouvelle révision. |
| 07-14 | V34-047 / W14 | 12 demandes dont 2 échecs affichent 10 propositions et 2 erreurs ; pas 12 sujets confirmés. |
| 07-15 | V34-045/046 / W13 | Undo d'un champ texte appartient au champ ; aucun Undo projet par interception globale. |
| 07-16 | V34-038/045 / W02 | Exception historique : Undo groupé Score+Cut ne révoque ni export ni opération physique. |
| 07-17 | V34-045/049 / W13 | Toutes les actions essentielles accessibles au clavier avec focus visible. |
| 07-18 | V34-045/046 / W13 | Conserver 1366×768 ET 1280×720, texte 200 % ; contrôle essentiel accessible, pas caché. |
| 07-19 | V34-045/049 / W13 | Texte/motif et annonces adaptées à la technologie choisie ; ni couleur seule ni répétition à chaque frame. |
| 07-20 | V34-043 / W03 | BLOCKED interdit publication fabriquable ; UNKNOWN peut rester brouillon explicitement non qualifié. |
| 07-21 | V34-043 / W03 | PNG PTC distinct de Basic Cut, multicouche CUT et éditable ; guide de transfert conservé. |
| 07-22 | V34-043/049 / W04 | Score sémantique et Attacher manuels ; motifs UI ne deviennent pas des commandes machine. |
| 07-23 | V34-047 / W02 | Liste de 50 entrées réelle et navigable ; exemple 12 éléments ne fixe pas le plafond UI. |
| 07-24 | V34-044 / W03 | Export reste EXPORTED_UNVERIFIED tant que preuve externe absente ; ZIP relu ne vaut pas coupe. |
| 07-25 | V34-041/045 / W13 | Exception historique : conserver cible p95 <150 ms sur 100 navigations avec matériel/protocole, pas simple « mesurer plus tard ». |
| 07-26 | V34-043 / W02 | Démo 12 escargots porte le statut fictif ; aucune segmentation ni vectorisation réelle inférée. |
| 07-27 | V34-045/049 / W13 | Contraste et motifs rendent les opérations distinguables sans perception des couleurs. |
| 07-28 | V34-048 / W01 | Abandon du scratchpad nettoie explicitement les temporaires, garde l'original intact et aucun projet fictivement sauvegardé. |

## Lot08 — 30 décisions d'assertion

| Assertion | Propriétaire candidat / consommateur | Sens conservé et contre-exemple exclu |
|---|---|---|
| 08-01 | V34-051 / W14 | Règles locales « 12 stickers » proposent PTC sans modèle ni réseau. |
| 08-02 | V34-051/052 / W14 | « SVG » seul fait préciser éditable ou découpe ; aucun rôle choisi silencieusement. |
| 08-03 | V34-051 / W14 | Négation « sans imprimer » exclut proposition PTC automatique. |
| 08-04 | V34-054 / W14 | Nom de fichier hostile reste donnée, jamais instruction. |
| 08-05 | V34-054 / W14 | OCR/SVG ne donnent ni lecture externe ni droit réseau. |
| 08-06 | V34-050/053 / W14 | Dialogue seul n'altère pas le SHA du projet. |
| 08-07 | V34-053 / W14 | Preview n'émet ni receipt durable ni nouvelle révision logique. |
| 08-08 | V34-053 / W14 | Acceptation stale refuse sans mutation et demande nouvel aperçu. |
| 08-09 | V34-053 / W14 | Double acceptation réutilise receipt dans le writer qualifié ; pas seconde commande indépendante. |
| 08-10 | V34-052 / W04 | Cote absente reste manquante ; fabrication bloquée plutôt que valeur plausible inventée. |
| 08-11 | V34-052/056 / W14 | 40 mm explicitement saisis ont une provenance utilisateur, distincte d'un défaut ou suggestion. |
| 08-12 | V34-051/052 / W14 | NaN/Inf/zéro/hors plage rejetés avant CommandPort, avec champ/unité à corriger. |
| 08-13 | V34-051/056 / W14 | « Couleurs sans imprimer » expose les alternatives avec leurs limites ; pas substitution silencieuse. |
| 08-14 | V34-050/052 / W14 | Cas complet avance sans question inutile ; confirmation de mutation reste distincte de clarification. |
| 08-15 | V34-052 / W14 | Plus de trois champs critiques ouvre un formulaire, pas une boucle de questions. |
| 08-16 | V34-050/055 / W14 | Ne plus suggérer supprime relances facultatives, garde diagnostics bloquants visibles. |
| 08-17 | V34-054/055 / W14 | Préférence IA jamais ne se transforme jamais en installation automatique. |
| 08-18 | V34-054 / W14 | OOM préserve le brouillon ; règles/manuel restent utilisables sans commit. |
| 08-19 | V34-052/055/057 / W12 | Largeur préférée n'entre pas dans une commande physique sans choix explicite. |
| 08-20 | V34-055/057 / W12 | Effacer préférences/historique de dialogue n'efface ni projet ni son historique d'édition portable. |
| 08-21 | V34-053/056/057 / W14 | Changement de profil invalide proposition et explication dépendantes. |
| 08-22 | V34-051/056 / W03 | Quatre rôles restent distincts dans proposition, aperçu et sortie. |
| 08-23 | V34-058 avec V34-122 / W08 | Zone A4 inconnue n'obtient aucun placement garanti. |
| 08-24 | V34-058 avec V34-111/130 / W04 | Score/Attach restent étapes manuelles ; aucun driver Cricut déduit. |
| 08-25 | V34-058 avec V34-047/074 / W14 | Rapport de propositions partielles 12/24/50 ne devient pas compteur de sujets détectés/acceptés. |
| 08-26 | V34-050 / W02 | 100 ouvertures/fermetures de dialogue conservent sélection et révision. |
| 08-27 | V34-050 / W13 | Clavier : répondre, ignorer, revenir et restaurer le focus, y compris après erreur. |
| 08-28 | V34-050 / W13 | Lecteur écran annonce question/unité/erreur/conséquence sans répétition parasite. |
| 08-29 | V34-058 avec V34-051 / W14 | Cible historique p95 règles <150 ms, 100 demandes synthétiques et preuve Windows ; aucune mesure inventée. |
| 08-30 | V34-051/058 / W14 | Mesurer intentions FR correctes et questions superflues ; seuils à fixer après baseline, pas précision alléguée. |

## Lot09 — 30 décisions d'assertion

| Assertion | Propriétaire candidat / consommateur | Sens conservé et contre-exemple exclu |
|---|---|---|
| 09-01 | V34-059 / W14 | Compilation par règles possible offline sans modèle installé. |
| 09-02 | V34-059 / W14 | shell/HTTP/InstallModel hors catalogue refusés avec zéro effet. |
| 09-03 | V34-059 / W14 | Suggestion de modèle ne contourne pas CatalogPort. |
| 09-04 | V34-059 / W03 | Catalogue distingue les quatre contrats de sortie. |
| 09-05 | V34-060 / W14 | Propriété inconnue et mauvais type rejetés strictement. |
| 09-06 | V34-060 / W14 | Clés JSON dupliquées et NaN/Infinity refusés avant validation de schéma. |
| 09-07 | V34-060 / W14 | Conserver budgets historiques : 64 KiB, 8 étapes, profondeur16 ; +1, étape9, profondeur17 refusés. Aucun quota d'archive substitué. |
| 09-08 | V34-060 / W04 | Taille physique absente ne devient pas une cote implicite. |
| 09-09 | V34-061 / W02 | Sujet absent ou digest masque changé invalide plan avant toute mutation. |
| 09-10 | V34-061/072 / W14 | AcceptSubjectsBatch unique pour lot confirmé ; 50 résultats peuvent être calculés par chunks, pas 50 acceptations prétendues atomiques. Persister 50 suit CP2/V2 packs internes. |
| 09-11 | V34-061 / W04 | SCORE demeure assignation sémantique distincte de CUT, y compris Undo/reload. |
| 09-12 | V34-061 / W04 | UNKNOWN ne crée ni FABRICATION_QUALIFIED ni Score automatique dans DS. |
| 09-13 | V34-062 / W14 | Simulation n'altère SHA/révision/receipt. |
| 09-14 | V34-062 / W14 | Timeout preview CPU borné ; nettoyage temporaire et zéro commit. |
| 09-15 | V34-062/065 / W14 | Diff exhaustif des effets ; aucun champ muté hors ce qui est confirmé. |
| 09-16 | V34-062 / W14 | Preview GPU ne télécharge pas de poids et ne contacte aucun service réseau. |
| 09-17 | V34-063 / W14 | Sans acceptation explicite, CONSENT_REQUIRED ; consentement de tâche ChatGPT distinct de consentement produit. |
| 09-18 | V34-063 / W14 | Digest changé invalide le grant après aperçu. |
| 09-19 | V34-063 / W14 | Snapshot/epoch changés avant clic imposent STALE sans commit. |
| 09-20 | V34-063 / W14 | Grant one-shot expiré/consommé refuse nouvelle commande ; retry identique lit receipt sans réexécution. |
| 09-21 | V34-064 / W14 | Instructions dans OCR/SVG ne donnent pas accès disque extérieur. |
| 09-22 | V34-064 / W14 | URL dans EXIF/nom reste inerte, aucune requête réseau. |
| 09-23 | V34-064 / W14 | Modèle ne propose pas Undo/SaveProjectCopy/MigrateCopy exécutables ; utilisateur garde commandes directes autorisées. |
| 09-24 | V34-064 / W01 | Crash commit/réponse inspecte receipt ou UNKNOWN ; jamais deuxième mutation par retry aveugle. |
| 09-25 | V34-065 / W14 | Résumé novice distingue changement, export et téléchargement ; « 1 changement/0 export/0 téléchargement » vérifiable. |
| 09-26 | V34-065 / W14 | Diff expert paramètres/source/révision, sans badge physique indu. |
| 09-27 | V34-066 / W14 | Refus expose correction autorisée sans relance en boucle. |
| 09-28 | V34-066 / W04 | Plan SCORE+CUT garde guide Score/Attacher manuel. |
| 09-29 | V34-067 avec V34-045/050/065 / W13 | Clavier/lecteur écran inspectent/refusent/confirment puis récupèrent focus ; test corpus ne remplace pas implémentation accessible. |
| 09-30 | V34-067 avec V34-059/062 / W14 | Compilation ET preview : p95 et faux refus avec SHA/corpus ; aucune cible arbitraire ajoutée. |

## Lot10 — 30 décisions d'assertion

| Assertion | Propriétaire candidat / consommateur | Sens conservé et contre-exemple exclu |
|---|---|---|
| 10-01 | V34-068 / W02 | EXIF1–8 : vue/masque alignés et transformation inverse exacte ; coordonnées en pixels source orientés. |
| 10-02 | V34-068 / W01 | Diagnostic/retouche ne changent pas les octets/SHA originaux. |
| 10-03 | V34-068 / W03 | ICC absent/corrompu signalé ; toute conversion couleur est tracée. |
| 10-04 | V34-068 / W01 | Bombe de décompression ou image corrompue refusée avant allocation excessive. |
| 10-05 | V34-069 / W14 | Alpha RGBA et LoadImage MASK concurrents ambiguës imposent choix, pas priorité implicite. |
| 10-06 | V34-069 / W14 | Alpha opaque/vide ne crée aucun sujet certifié. |
| 10-07 | V34-069 / W14 | Fond photo/blanc non uniforme ne justifie pas un rectangle inventé. |
| 10-08 | V34-069 / W14 | H/W permutés, NaN/Inf, shape/strides invalides refusés avant traitement. |
| 10-09 | V34-070 / W14 | ROI hors source ou halo de tuile non résolu bloque acceptation. |
| 10-10 | V34-070 / W14 | Douze propositions réelles sur fixture douze sujets, IDs uniques ; pas simple duplication de démo. |
| 10-11 | V34-070/074 / W14 | Vingt-quatre sujets ne sont pas tronqués au top12 legacy. |
| 10-12 | V34-070/074 / W14 | Cinquante résultats individuellement suivis et reprenables sans perte. |
| 10-13 | V34-070 / CP1–2 | 12×2MP dépasse snapshot V1 8M : refus ou V2 explicite ; partition d'exports n'autorise pas V1 invalide. |
| 10-14 | V34-070 / W14 | Sujet traversant deux tuiles recomposé ou bloqué, jamais dupliqué. |
| 10-15 | V34-071/073/076 / W02 | Îlots/accessoires/chevauchements localisés précisément ; pas avertissement générique inexploitable. |
| 10-16 | V34-071/075/076 / W02 | Masque touchant le bord exige revue ; pas d'auto-acceptation sur miniature. |
| 10-17 | V34-071/072 / W14 | Digest float32 exact, forme et transformation revérifiés à acceptation. |
| 10-18 | V34-072 / W02 | ID persistant alloué par SubjectPort/receipt qualifié ; jamais index de vignette ou nom PNG. |
| 10-19 | V34-072 / W02 | Correction du masque invalide la preuve d'identité précédente. |
| 10-20 | V34-073 / W02/CP3 | Lier/séparer accessoire = relation réversible ; aucun collage des pixels pour simuler la relation. |
| 10-21 | V34-074 / W14 | OOM/interruption produit PARTIAL de propositions, aucun commit ; reprise ciblée sans doublon. |
| 10-22 | V34-072/074 / W14 | Réponse d'ancien SHA/epoch STALE ; session/génération ajoutées à la clé pour éviter les collisions inter-session. |
| 10-23 | V34-072 / W14 | Double acceptation batch = une transaction/receipt dans writer qualifié. |
| 10-24 | V34-074 / W14 | Sans modèle/téléchargement consenti, CPU/manuel et réseau nul. |
| 10-25 | V34-077 avec V34-054/064 / W14 | Nom/EXIF/OCR hostile n'exécute commande ni requête ; corpus sécurité a un consommateur identifié. |
| 10-26 | V34-075 / W02 | Novice sélectionne/rejette/corrige douze propositions liées aux vrais sujets. |
| 10-27 | V34-075/076 / W02 | Expert inspecte float32/coordonnées/rapport sans badge QUALIFIE non prouvé. |
| 10-28 | V34-075/076 / W13 | Clavier, lecteur écran, inspection zoom100 % couvrent revue ET correction. Autres zoom/DPI hérités restent transversaux. |
| 10-29 | V34-077 avec V34-074 / W14 | Qualité et p50/p95 CPU/RAM/VRAM par version/corpus ; GPU réel séparé du mock OOM. |
| 10-30 | V34-077 avec V34-129/130 / W03 | PNG PTC distinct des SVG ; niveaux DS/physique NOT_RUN tant que preuve absente. |

## Écarts traités et critères intégraux des 37 tickets

Les DoD V34-041–049 (9), 050–058 (9), 059–067 (9) et 068–077 (10) sont conservés dans leurs lots sources. Leurs exigences S/R33, dépendances, rollback et nature des preuves restent obligatoires. Les tables précédentes précisent leur consommateur V3.5 sans redéfinir ces tickets. Les conditions communes de V3.3 F01–F04/F08/F14/F15 et G1–G3/G6–G8 restent applicables, notamment édition persistante, local/offline et accès clavier.

Les pertes concrètes évitées ici :

1. **Promesse de format** : un viewer JPEG/WebP ne qualifie pas un créateur d'archive PNG. Admission et conversion doivent être explicites. Le brouillon ne prétend pas être sauvegardé.
2. **Preuve de sauvegarde** : navigation et preview ne créent pas de receipt ; ACK perdu, primary publié et backup échoué exigent inspection. V1 CAS reste distinct du mécanisme durable CP2.
3. **Accessibilité et performances** : conserver petits écrans, zooms et lecteur d'écran hérités, les deux cibles distinctes p95<150 ms (navigation et règles), et le basculement vers formulaire au-delà de trois champs critiques. Les budgets ne sont pas supprimés au motif qu'ils ne sont pas encore mesurés.
4. **Planificateur** : plafond64KiB/8 étapes/profondeur16 reste un contrat spécifique ; quotas Smart Delivery/archive ne le remplacent pas. Le modèle n'obtient pas Undo/SaveCopy/MigrateCopy, alors que l'utilisateur conserve les commandes directes. Aucun consentement documentaire ne forge un grant produit.
5. **Propositions versus projets** : calculer 50 objets par tuiles/chunks, afficher50 lignes et persister50 sujets sont trois exigences distinctes. Acceptation batch atomique complète et packs internes V2 restent des étapes qualifiées, pas une boucle de50 commandes ou50 projets.
6. **Sélection réelle** : digests float32, preuve d'identité invalidée par retouche, orientation EXIF1–8, ambiguïté MASK/RGBA et sujet traversant deux tuiles conservent chacun leur contre-exemple.

Les niveaux logiciels/Windows/GPU/DS/physiques restent séparés ; tous nouveaux essais NOT_RUN. Développement futur : localiser les ports actuels au HEAD de la PR, prouver l'écart par fixture autorisée, appliquer le changement minimal, vérifier la recette de la ligne concernée et les DoD du ticket. Rollback adapté à chaque source : read-only/scratchpad, formulaires/règles, plan lecture seule, revue manuelle ou CPU. Aucune dépendance/framework, source protégée ou gouvernance modifiée.

## Résultat et suite

118 assertions traitées individuellement (28+30+30+30), critères des 37 tickets conservés avec corrections explicites. Ce résultat est une décision de transfert documentaire, pas 118 tests exécutés ni une certification indépendante des 437. Les 25 axes restent applicables : inventaires intègres, statuts distincts, autorité/float32/exports, opérations/machines, UX et erreurs, reprise, IA/licences, qualité raster/vectorielle, batch/Delivery, performances, confidentialité, anti-doublon et promotion contrôlée. Les critères hors ces quatre lots ne sont pas réputés clos.

**Suite SOURCE_CLOSURE : compléter SC-02A par une résolution individuelle des assertions05–06 non encore jugées, traiter les autres lots et les141 critères/140 DoD, puis GLOBAL_REVIEW.** Ne pas recommencer REVIEW_DE ou OCR ; ne fermer SOURCE_CLOSURE qu'après consolidation de toutes les lignes et exceptions.
