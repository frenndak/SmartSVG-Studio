# Smart Delivery — contrat SD0/SD1/SD2 prêt à décliner en micro-lots

**14/11/2026 — spécification candidate, implémentation NOT_RUN.** Complète les commentaires SD-V1/SD-V2 de #141, Q01 et COV22 ; aucun remplacement du manifeste historique ni des quatre contrats d'export. Propriétaires W05 plan/validation, W06 pack/guide. Un export réel suffit au premier ZIP ; quatre exporteurs restent requis pour clore W03.

## 1. Formats externes et absence de nouvelle autorité projet

`smartsvg-delivery-plan/1-draft` est un plan local immuable, hors archive V1. `smartsvg-delivery-manifest/1-draft` est le reçu portable du ZIP. Le plan peut contenir des handles/références de fichiers locaux gérés ; le manifeste **ne contient jamais** chemins absolus, noms privés de dossiers, poids IA, secrets ni métadonnées EXIF non approuvées. Sérialisation JSON UTF-8, clés déterministes, NaN/Infinity interdits, schéma strict, digest SHA256 de la représentation canonique choisie et versionnée dans le micro-lot SD0-A. Le digest du ZIP final n'est pas inclus dans lui-même ; il est retourné par le reçu externe.

| Champ du plan | Obligatoire / type / règle |
|---|---|
| schema, plan_id | version exacte, ID local opaque stable |
| project_ref | project_id et SHA64 du projet lu, ou provenance de génération géométrique versionnée sans projet ; choix discriminé |
| policy_version | version des règles de QA et de quotas |
| items | 1..500 éléments ; item_id unique, source_locator privé, size_bytes entier, sha256, media_type, role, target_relpath |
| dimensions | width_mm,height_mm positifs finis et confirmation/provenance ; PNG ajoute width_px,height_px, PPI dérivé si pertinent |
| role | PNG_PTC / SVG_BASIC_CUT / SVG_MULTILAYER_CUT / SVG_EDITABLE ; aucun alias entre rôles |
| operation_context | opérations sémantiques déclarées, groupes liés, guide minimal requis, miroir par couche si HTV ; non dérivé de la couleur |
| qa | contrôles locaux avec status PASS/FAIL/UNKNOWN/NOT_APPLICABLE et raison ; preuves externes DS/physique séparées et datées |
| machine_context | capacité par opération SUPPORTED/UNSUPPORTED/UNKNOWN, profil/version ou null ; disponibilité matériel séparée AVAILABLE/UNAVAILABLE/UNKNOWN |
| share_decision | ALLOWED/REVIEW_REQUIRED/DENIED et provenance/licence ; droits locaux de l'utilisateur distincts d'une licence tierce |
| guidance | étapes manuelles obligatoires identifiées, avertissements, optional_html booléen |
| admission | BLOCKED / EXPORT_UNVERIFIED / LOCAL_QA_PASSED ; liste stable des motifs par item et plan |

Manifeste portable : mêmes IDs/rôles/digests/dimensions/provenance expurgée/QA/opérations et instructions, chemins **internes au pack** uniquement ; ajoute `included_item_ids`, `omitted_items` avec raisons publiques, `batch_status=COMPLETE|PARTIAL|NOT_A_BATCH`, version exporteur et horodatage informatif. Manifestes sans hash autoréférent. Une sortie absente ne reçoit jamais un faux item PASS. Si seuls quelques items sont choisis, montrer leur liste avant publication ; aucune exclusion silencieuse des erreurs.

### Budgets logiciels initiaux proposés

Version `delivery-quota/1-draft` : 500 fichiers de contenu maximum, 2 GiB total non compressé, 512 MiB par fichier, manifeste ≤2 MiB, texte par champ ≤4096 caractères, profondeur JSON≤16, noms internes≤180 caractères, niveaux de chemins≤8. Ce sont des **limites de ressources de SmartSVG**, jamais des limites Cricut. Refus explicite au dépassement ; streaming de copie en blocs bornés, pas chargement ZIP complet en RAM. Une modification des budgets nécessite version/profil et tests frontière, pas un relèvement automatique pour contourner l'erreur. Les bornes PNG/SVG des exporteurs s'appliquent en plus.

## 2. Admission et contrôles par rôle

Toutes sorties : fichier régulier sous racine autorisée, SHA/taille correspondants, chemin sûr, source réelle et statuts non fabriqués. Symlink/reparse, chemins absolus dans ZIP, `..`, noms réservés Windows, collisions casse/NFC et noms de membres dupliqués rejetés. Si droits de partage inconnus : REVIEW_REQUIRED, demande de décision explicite sans inventer une licence ; DENIED ne peut être contourné par simple confirmation.

| Rôle | Contrôles locaux bloquants | Incertitudes admises avec étiquette |
|---|---|---|
| PNG_PTC | PNG lisible, dimensions px/mm confirmées, alpha/ICC selon politique, résolution cohérente, digest ; pas besoin d'un SVG companion | profil machine/DS non testé → EXPORT_UNVERIFIED ; bleed/calibration explicités ; pas de faux 600dpi |
| SVG_BASIC_CUT | XML sûr, namespaces/viewBox/mm, géométrie prévolée, type CUT explicite ; chemins ouverts seulement si opération/cas contractuel le permet | matière/outil non vérifiés → avertissement, jamais prêt machine |
| SVG_MULTILAYER_CUT | mêmes contrôles + IDs/groupes/couleurs/opérations séparés, alignement et décisions HTV par couche | superposition physique non vérifiée reste UNKNOWN ; ne pas encoder dans Artifact.use V1 |
| SVG_EDITABLE | XML sûr, unités explicites, ressources/références admises, capacité réelle annoncée (texte ou chemins) | éditable ne signifie pas découpe ; effets/textures non fabricables autorisés seulement comme édition déclarée |

Taille physique inconnue : un aperçu de travail peut être montré mais **pas admis comme export de fabrication**. Ne pas confondre dimensions inconnues avec compatibilité machine inconnue, qui peut autoriser un fichier local explicitement non qualifié. Un FAIL local bloquant n'est jamais converti en UNKNOWN pour créer un pack. Les contrôles `artifact_qa` historiques ne sont pas exécutés indistinctement sur tous les rôles : adaptateur de rôle mappe seulement les contrôles applicables, avec raisons NOT_APPLICABLE.

## 3. Instructions obligatoires, HTML facultatif

SD2 `instructions.html` est facultatif. Les informations nécessaires au transfert manuel **ne le sont pas** : assignation SCORE/DRAW/FOIL, Attacher, miroir et contexte de profil doivent être accessibles dans le manifeste et un `LIRE_AVANT_IMPORT.txt` minimal lorsque nécessaires. Le HTML les présente agréablement mais ne les invente ni ne les remplace. Cas de recette : boîte 5 CUT/8 SCORE, HTML désactivé → guide texte conserve huit plis SCORE et consigne Attacher ; aucun chemin de pli transformé automatiquement en CUT. Pas de pilotage machine/API privée.

HTML : statique, données échappées, aucun script/formulaire/ressource distante, liens strictement relatifs vers items autorisés, images embarquées seulement si dérivées approuvées et sous quota ; navigation clavier, contraste, texte compréhensible, offline. Afficher « fichiers créés, import Design Space non vérifié » si preuve absente. Les déclarations humaines existantes doivent être liées à la même version/artefact, pas réutilisées d'un autre projet.

## 4. Publication et reprise

SD0 = inspecter/planifier en lecture seule, aucune création du ZIP. SD1 = confirmer destination et sélection du plan → revalider source/projet/politique → staging privé sur même volume → copie streaming avec hash **pendant** copie → générer manifeste/guide → fermer → relire ZIP, chaque hash, membres attendus et quotas → publication exclusive sans écrasement → lecture de contrôle → reçu externe `{plan_digest,zip_sha256,size,status}`. Destination apparue entre prévol et publication : collision, aucune suppression. Supprimer seulement temporaires appartenant à cette tentative.

Si fichiers source changent pendant copie : refuser publication, même si nom/taille restent égaux. Si le projet change mais les fichiers restent identiques : exiger replanification de provenance/QA au nouveau SHA, pas de pack prétendument courant. Deux tentatives : clé plan_digest+destination et identifiant tentative ; fichier existant n'est jamais adopté comme succès sans hash/reçu correspondants inspectés explicitement. Crash après publication avant ACK : état UNKNOWN, inspecter fichier final et reçu/relecture ; aucune réécriture automatique. Annulation avant publication n'annonce aucun pack ; après publication, rapporter pack créé avec annulation tardive, ne pas le supprimer sans choix.

Un ensemble de fichiers hors ZIP peut rester PARTIAL conformément au lot17/19 ; un ZIP individuel reste atomique. Un guide modifié à la main ne modifie pas le projet ; recréer le pack utilise une nouvelle destination. Undo ne retire aucun fichier livré. Erreurs : SOURCE_CHANGED, QA_BLOCKED, RIGHTS_REVIEW_REQUIRED, RIGHTS_DENIED, UNSAFE_PATH, BUDGET_EXCEEDED, DESTINATION_EXISTS, DISK_FULL, CANCELLED, OUTCOME_UNKNOWN, READBACK_FAILED ; mapper à l'UI sans fuite de chemin privé.

## 5. Adaptateurs et micro-lots

Pas de deuxième exporteur : W03 produit les fichiers. Adaptateur conceptuel `inspect_delivery_item(file_ref,role,context,policy)` retourne descriptif, QA et admission, sans copier ni écrire le projet. `plan_delivery(items,selection,context)` agrège et refuse incohérences ; `publish_delivery(plan,destination,confirmed)` consomme le plan stable. Aucun de ces noms n'est une API main actuelle ; `delivery_manifest`/`write_delivery` restent le JSON historique. COV22 donne les ports effectivement disponibles.

| Micro-lot | Sortie et critère de clôture | Dépendance |
|---|---|---|
| SD0-A | schéma/validateurs purs + fixtures PNG seul, rôles4, profil inconnu, tailles inconnues ; décisions d'admission déterministes | aucune production réelle requise pour contrats |
| SD0-B | adaptateurs lecture seule des sorties réelles et écran plan/diagnostics | ≥1 export réel et ses QA |
| SD1-A | ZIP staging/stream/hash/relecture/no-clobber + fault injection | SD0-A/B, aucun HTML nécessaire |
| SD1-B | UI destination, annulation/reprise, guide texte requis, reçu | SD1-A ; Windows I/O/UI pour prétendre livré |
| SD2 | HTML offline/échappement/clavier reprenant exactement le guide minimal | SD1, facultatif pour premier pack |
| SD3 | historique/comparaison/recréation par provenance | incrément ultérieur, pas prérequis SD1 |

Tests proposés NOT_RUN : positif PNG seul sans SVG ; quatre rôles distincts ; export local à capacité machine UNKNOWN ; HTML désactivé conserve Score/Attach ; pack sélectionné PARTIAL honnête. Négatifs : taille physique absente, SVG XXE/script/lien externe, QA FAIL, licence DENIED, nom Windows réservé/collision NFC, source remplacée même taille, fichier destination concurrent, disque plein pendant copie/close/readback, coupure après publication, manifeste tronqué/empreinte fausse, item dépassant quotas, annulation tardive, ancien projet SHA, image privée non sélectionnée. Mesurer débit/RSS/latence annulation sur tailles progressives ; ce sont des mesures prévues. DS/physique séparés.
