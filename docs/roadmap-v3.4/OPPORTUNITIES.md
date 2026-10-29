# SmartSVG V3.4 — Registre d'opportunités de conception

**DRAFT — registre cumulatif sans doublons.** Créé au cycle 02 (29 octobre 2026). Les opportunités ne sont **pas** des fonctionnalités implémentées ni des obligations P0. Avant tout ajout, comparer F01–F15, S-001..101, R33-001..040 et V34 existants. Une idée déjà couverte devient un **raffinement** d'exigence, jamais un second ticket identique.

## Méthode d'arbitrage

Échelles indicatives 1 (faible) à 5 (fort) : `U` utilité, `F` fréquence, `FA` faisabilité, `V` valeur utilisateur ; `C` complexité et `R` risque (5 = très défavorable). Score comparatif = `U × F × FA × V / (C × R)`, **heuristique non scientifique**, utilisée uniquement entre candidats de même maturité. Ne pas classer P0 sur la seule base du score. Le statut est `CANDIDAT`, `RETENU_POUR_SPEC`, `REPORTE` ou `REJETE`. Les tickets futurs nécessitent tests et preuves.

| ID | Proposition | Écart avec V3.3 / V34 | U/F/FA/V/C/R → score | Priorité / décision |
|---|---|---|---|---|
| **O-001** | Journal local de transfert Design Space (étapes confirmées, versions, réglages, incidents et photo facultative) | Raffine S-010, S-084, R33-022, R33-034 ; pas un doublon du rapport de prévol, car il suit **l'après-export** ; V34-010 | 4/3/4/4/2/2 → 48 | **P1 / RETENU_POUR_SPEC** |
| **O-002** | Vérification guidée de l'échelle imprimante et de l'orientation A4 avant découpe, avec état « vérification externe nécessaire » | Raffine S-029, R33-022 et le parcours P01 ; évite de présenter un nesting indicatif comme une coupe garantie ; V34-007, V34-009 | 5/4/4/4/2/2 → 80 | **P1 / RETENU_POUR_SPEC** |
| **O-003** | Pilotage direct de la Cricut depuis SmartSVG sans Design Space | Hors périmètre, non documenté comme interface publique supportée ; contredit la règle de non-promesse du lot 02 | 2/2/1/2/5/5 → 0,32 | **REJETÉ** |
| **O-004** | Prévisualisation par opération et séquence physique Cut/Score/Draw/Foil avec alertes contextualisées | Raffine S-085, R33-022..023 et V34-012 ; visualise la sémantique métier, sans inventer de commande machine | 5/4/4/4/2/2 → 80 | **P1 / RETENU_POUR_SPEC** |
| **O-005** | Aperçu de pliage 3D purement géométrique d'un patron carton, sans IA | Raffine le parcours boîte V34-008 et future géométrie cycle 16 ; distinct d'une prévisualisation 2D des plis | 3/2/3/3/4/3 → 4,5 | **P2 / REPORTE** |

| **O-006** | Comparateur de migration lisible « ancien vs autonome » sur un même projet, opt-in | Raffine S-022, S-046, S-063, R33-003/009, V34-021 ; distinct de la preuve dual-run car il explique les écarts à l'utilisateur | 4/2/4/4/3/2 → 21,33 | **P1 / RETENU_POUR_SPEC** |
| **O-007** | Diagnostic de capacités hors ligne et recommandations réparatrices sans installation automatique | Raffine S-022, S-084, R33-034, V34-024 ; étend le diagnostic ComfyUI actuel au mode natif et distingue présence/essai/licence | 5/4/4/4/2/2 → 80 | **P1 / RETENU_POUR_SPEC** |

| **O-008** | Contrôle de portabilité et confidentialité avant partage d'un projet .smartsvg | Raffine S-017, S-041, S-042, S-061, R33-010/015 et V34-031 ; distinct de O-007 (capacités locales), car il vérifie **les ressources embarquées et les références externes du projet à partager** | 4/3/4/4/3/2 → 32 | **P1 / RETENU_POUR_SPEC** |

| **O-009** | Aperçu non mutant d'un Undo groupé, historique lisible des gestes et opérations | Raffine S-008, S-071, R33-019, V34-035/038 ; distinct de l'Undo pinceau historique car traverse tous les espaces et prévisualise **un groupe complet** | 4/4/4/4/3/2 → 42,67 | **P1 / RETENU_POUR_SPEC** |
| **O-010** | Boîte de réception locale des propositions de jobs devenues périmées, avec comparaison/relance explicite | Raffine R33-005, R33-011/012, V34-036/039 ; distinct de O-006 (comparaison ComfyUI vs natif) et du cache de jobs | 4/3/4/4/3/2 → 32 | **P1 / RETENU_POUR_SPEC** |

| **O-011** | Bac à sable d'import local jetable avant création de projet canonique | Raffine S-003, S-023, S-067, R33-003/025/033 ; distinct de la reprise de job O-010 : essais d'intention et de format **avant** mutation du projet ; V34-048 | 4/4/4/4/3/2 → 42,67 | **P1 / RETENU_POUR_SPEC** |
| **O-012** | Légende Cut/Score/Draw/Foil à double codage texte + motif, indépendante des couleurs | Raffine S-072, S-077, S-080, R33-019/022 ; distinct de la preview O-004 : accessibilité des **types d'opération** dans toutes les vues ; V34-049 | 4/5/5/4/2/1 → 200 | **P1 / RETENU_POUR_SPEC** |

| **O-013** | Fiche « pourquoi cette suggestion ? » : provenance, limites, conséquence sur sortie | Raffine S-071, S-075, S-083, R33-020/034 et V34-056 ; distinct de O-007 (capacités installées) et O-009 (Undo) : justification **avant** validation d'intention | 4/4/4/4/2/2 → 64 | **P1 / RETENU_POUR_SPEC** |
| **O-014** | Préférences par intention avec portée et reconfirmation des dimensions/matériaux | Raffine S-081/083, R33-032/039 et V34-055/057 ; distinct des préréglages globaux : **pas de réutilisation silencieuse** de données physiques ou d'outil | 4/3/4/4/3/2 → 32 | **P1 / RETENU_POUR_SPEC** |
| **O-015** | Assistant micro toujours à l'écoute, déclenchement automatique | Hors cœur Explore 5 ; confidentialité, accessibilité, complexité et latence disproportionnées ; aucune nécessité pour langage naturel **saisi** | 1/2/2/1/5/5 → 0,16 | **REJETÉ** |
| **O-016** | Diff exact des mutations projet avant confirmation d'un plan | Raffine S-071/075/083, R33-019/020 et V34-062/065 ; différent de O-013 (raison de suggestion), car expose **les champs réellement modifiés** | 4/4/4/4/3/2 → 42,67 | **P1 / RETENU_POUR_SPEC** |
| **O-017** | Refus réparateur avec action sûre et explicite | Raffine S-072/077/084, R33-020/022/034, V34-061/066 ; distinct de O-007 (diagnostic de capacité) et O-013 (justification d'une suggestion) | 4/4/4/4/2/2 → 64 | **P1 / RETENU_POUR_SPEC** |
| **O-018** | Exécution automatique des plans suggérés sans clic | Rejet : incompatible avec l'autorité utilisateur, les mutations transactionnelles et les prévols matériels | 2/3/1/1/5/5 → 0,24 | **REJETÉ** |

| **O-019** | Revue des relations accessoires↔sujets avec liaison réversible et justification | Raffine S-028 et V34-073 : S-028 exige de conserver les accessoires, mais pas le **geste explicite de liaison/déliaison sans fusion des pixels** ; différent de O-013 explication d'intention | 4/4/4/4/3/2 → 42,67 | **P1 / RETENU_POUR_SPEC** |
| **O-020** | Inspection de masques à 100 % avec échantillons de bord reproductibles | Raffine S-073/079 et V34-076 : contrôle de **l'intégrité du bord du masque avant acceptation**, pas le prévol physique ni le comparateur de migration O-006 | 4/4/4/4/3/2 → 42,67 | **P1 / RETENU_POUR_SPEC** |
| **O-021** | Envoi automatique des photos importées à une API cloud pour « améliorer » la segmentation | Contradiction avec traitement local/offline, consentement réseau et confidentialité ; ne complète ni S-005 ni V34-074 | 1/3/2/1/5/5 → 0,24 | **REJETÉ** |
| **O-022** | Comparaison de résultat IA vs sans IA **sur même ROI** avant toute recommandation de modèle | Raffine S-005/027, R33-018, V34-084 ; différent de O-006 (ancien vs autonome) et O-020 (inspection du masque) : mesure **le gain marginal du modèle** | 4/3/3/4/3/3 → 16 | **P1 / RETENU_POUR_SPEC** |
| **O-023** | Vérification de provenance des modèles déjà présents avant inférence (hash, licence, runtime, révocation) | Raffine S-042/067/084, R33-025/030, V34-086 ; différent de O-007 diagnostic de capacités générales : vérifie **l'artefact exact** | 5/4/4/5/3/2 → 66,67 | **P1 / RETENU_POUR_SPEC** |
| **O-024** | Installer silencieusement le « meilleur modèle » dès l'import | Contradiction avec consentement réseau, licences et parcours sans IA ; alternative catalogue sur demande | 2/3/2/2/4/5 → 1,2 | **REJETÉ** |

| **O-025** | Aperçu des franges RGB finales sur blanc/noir/damier et taille imprimée indicative | Raffine S-015/016, V34-095 ; distinct de O-020 (masque avant acceptation) et O-002 (A4/transfert) : examine le **PNG final** | 4/4/4/4/3/2 → 42,67 | **P1 / RETENU_POUR_SPEC** |
| **O-026** | Diff de topologie alpha multi-seuil (0/20/128) entre proposition et PNG publié | Raffine S-015/073, R33-019, V34-095 ; distinct de QA statique historique : diagnostique **la régression entre deux étapes** | 5/4/4/4/3/2 → 53,33 | **P1 / RETENU_POUR_SPEC** |
| **O-027** | Upscale IA automatique à 600 ppp pour chaque import | Contredit le consentement explicite et confond pixels interpolés avec détails acquis ; alternative CPU/manuel et modèle opt-in | 2/4/2/2/4/4 → 2 | **REJETÉ** |

| **O-028** | Conseiller de budget de chemins SVG avant import Design Space | Raffine S-030/034/056, V34-101/103 ; différent de la QA topologique O-026 : prédit **le risque de dépassement du plafond officiel de 5 000 paths**, après expansion | 4/4/4/4/3/2 → 42,67 | **P1 / RETENU_POUR_SPEC** |
| **O-029** | Verrouillage de trous/îlots jugés essentiels avant simplification vectorielle | Raffine S-033/034, V34-097/102 ; différent de O-020 inspection du masque et O-026 diff alpha : protège une **intention géométrique explicite** pendant l'édition Bézier | 4/3/4/4/3/2 → 32 | **P1 / RETENU_POUR_SPEC** |
| **O-030** | Transformer automatiquement chaque couleur d'un dessin en chemin de coupe | Confond SVG d'édition et fabrication, ignore matériau/outil, crée doublons et microformes ; contredit R33-008, V34-101 | 2/3/2/1/4/5 → 0,6 | **REJETÉ** |

### O-001 — Journal local de transfert

- **Problème :** un export local peut être correct alors que l'utilisateur choisit une mauvaise opération ou un mauvais support dans Design Space ; l'incident est ensuite impossible à reproduire.
- **Scénario :** après export d'une boîte, cocher « import contrôlé », « Score choisi », « Attacher vérifié », « essai physique », saisir version Design Space et commentaire ; aucune collecte automatique.
- **Gain :** diagnostic, reproductibilité et apprentissage sans prétendre certifier la coupe.
- **Interaction :** panneau discret `[Guide] [Marquer étape effectuée] [Note facultative] [Effacer le journal]` ; optionnel et non bloquant.
- **Dépendances/effort :** modèle local de journal + UX + confidentialité + migration non destructive ; effort moyen ; photos locales jamais ajoutées au dépôt public.
- **Risques :** confusion « utilisateur l'a coché » avec preuve validée, exposition de données privées, complexité ; traiter par badges `DECLARATION_UTILISATEUR` distincts de `PASS`.
- **Recette :** enregistrer une confirmation n'élève aucun axe de preuve à `PASS` ; effacement n'altère pas le projet ; reprise conserve les étapes sans les appliquer à un autre export.

### O-002 — Contrôle de transfert Print Then Cut

- **Problème :** les dimensions sur le papier, les marges et l'orientation A4 ne se déduisent pas d'une simple prévisualisation PNG.
- **Scénario :** après export d'une planche, SmartSVG rappelle impression portrait sans mise à l'échelle, A4 grand côté horizontal sur le tapis Explore 5, puis demande de vérifier le placement dans Design Space.
- **Gain :** réduire les erreurs d'échelle et les fausses attentes de précision.
- **Interaction :** `[Aperçu indicatif] [Ouvrir la checklist] [Dimensions vérifiées dans Design Space ?]` ; aucun faux bouton « imprimer avec marques capteur ».
- **Dépendances/effort :** profils machine/format versionnés, source Cricut datée, guide contextuel ; faible à moyen ; ne pas figer les dimensions maximales en dur.
- **Risques :** évolution de Design Space, machine différente, options imprimante ; si profil inconnu, avertissement et vérification humaine obligatoire.
- **Recette :** T-V34-02-05 et 06 ; une zone non vérifiée ne produit pas l'état « placement garanti ».

### O-003 — Contrôle direct machine : rejet explicite

- **Raison :** aucune interface officielle de pilotage direct validée dans le lot ; risque d'endommagement, de compatibilité, de responsabilité et de périmètre disproportionné.
- **Alternative :** préparer des fichiers conformes aux contrats, un manifeste d'opérations et un guide Design Space. Ne rouvrir le sujet que sur preuve officielle d'API supportée, autorisation du propriétaire et ADR séparée.

### O-004 — Prévisualisation par opération et ordre de fabrication (cycle 03)

- **Problème :** une superposition de traits SVG masque les différences Cut/Score/Draw ; l'utilisateur peut oublier une opération ou un changement d'outil dans Design Space.
- **Scénario :** boîte ou carte : choisir « Voir les opérations » puis parcourir les groupes avec couleurs + libellés accessibles et liste « vérifier Score, Attacher, changer d'outil ».
- **Gain :** diminuer les confusions de fabrication sans piloter la machine ; s'appuie sur le modèle d'assignation métier du cycle 03.
- **Interaction :** `[CUT 4 chemins] [SCORE 3 plis] [Guide de transfert] [Voir défauts]`, surbrillance du chemin sélectionné ; mode daltonien textuel.
- **Effort/dépendances :** moyen ; V34-012, V34-009, modèle opérations cycle 14, profil machine cycle 15.
- **Risques :** faire croire que l'ordre de fabrication est imposé par SmartSVG ; afficher « ordre indicatif / séquence réelle gérée par Design Space ».
- **Recette :** T-V34-03-08,09,15 ; aucun SCORE rendu comme CUT ; une assignation inconnue produit alerte, jamais une instruction inventée.

### O-005 — Aperçu de pliage 3D géométrique (cycle 03)

- **Problème :** un patron de boîte correct en 2D peut être difficile à comprendre avant de gaspiller du carton.
- **Scénario :** après création du développé, bouton facultatif « Simuler le pliage » pour inspecter panneaux et languettes, sans prétendre valider le comportement physique du carton.
- **Gain :** meilleure compréhension et repérage de collisions géométriques grossières.
- **Interaction :** `[Patron 2D] [Aperçu 3D expérimental] [Revenir au 2D]`, aucun blocage du parcours Express.
- **Effort/dépendances :** élevé ; moteur paramétrique cycle 16, contraintes de charnières, collision, performance UI ; ne pas faire dépendre le socle P0 de la 3D.
- **Risques :** fausse confiance sur jeu matière, pliage réel, épaisseur, collage ; simulation étiquetée « indicative » et validée seulement sur géométries simples.
- **Recette future :** cube synthétique à dimensions connues : panneaux raccordés sans trou topologique ; carton physique **NON QUALIFIÉ** par l'aperçu ; erreur d'épaisseur inconnue signalée. Statut **REPORTÉ**, aucun ticket d'implémentation immédiat.

### O-006 — Comparateur de migration compréhensible (cycle 04)

- **Problème :** lors du passage de ComfyUI au mode autonome, une différence de contour ou d'identité est difficile à diagnostiquer sans savoir si elle est significative.
- **Scénario :** un utilisateur avancé active volontairement « Comparer les résultats » sur un projet synthétique ou privé, exécute deux transports sur des copies isolées et visualise les écarts de masques, dimensions, IDs, export et provenance.
- **Gain :** décider de conserver le chemin historique ou d'accepter une proposition autonome, sans écraser la source.
- **Interaction :** `[Ancien] [Autonome] [Superposition] [Écarts mesurés] [Garder mon projet] [Exporter rapport privé]`. Aucune exécution IA supplémentaire sans consentement.
- **Alternatives :** rapport JSON brut (moins ergonomique) ; comparaison automatique silencieuse (rejetée : double charge GPU et risques de téléchargement).
- **Effort/dépendances :** moyen ; V34-017, V34-020, V34-021, corpus autorisé ; tests T-V34-04-11..14 ; P1 après parité déterministe P0.
- **Risques :** révélation de données personnelles dans un rapport, non-déterminisme IA, comparaison de SHA ZIP non pertinente ; expurger, comparer sémantiquement, indiquer limites.
- **Recette :** aucune divergence IA n'est affichée « échec » sans métrique définie ; le dual-run ne modifie pas le projet ; les différences de dimensions mm et d'IDs sont visibles ; rapport local supprimable.

### O-007 — Diagnostic de capacités autonome, sans téléchargement implicite (cycle 04)

- **Problème :** « modèle disponible », « extension installée » et « capacité testée » sont confondus ; l'utilisateur ne sait pas pourquoi une fonction n'est pas utilisable.
- **Scénario :** ouverture hors ligne sans ComfyUI, affichage de `MANUEL DISPONIBLE`, `COMFYUI ABSENT`, `IA NON INSTALLÉE`, `LICENCE NON QUALIFIÉE`, `GPU NON TESTÉ`, avec solutions locales sans installation forcée.
- **Gain :** compréhension des limites et choix éclairé du mode CPU/manuel ou du futur téléchargement volontaire.
- **Interaction :** `[Fonctions disponibles] [Diagnostic détaillé] [Continuer sans IA] [Installer plus tard] [Exporter diagnostic expurgé]`.
- **Alternatives :** afficher une erreur générique (rejeté), lancer automatiquement un installateur (rejeté).
- **Effort/dépendances :** moyen ; V34-019, V34-023, V34-024, cycle 11 pour le catalogue de modèles ; T-V34-04-08..10 et 15.
- **Risques :** faux statut « compatible » déduit de la simple présence d'une librairie, exposition des chemins/versions privés ; différencier `PRESENT`, `CONTRACT_CHECKED`, `RUNTIME_TESTED`, `UNVERIFIED`.
- **Recette :** aucun téléchargement ni accès réseau hors consentement ; démarrage manuel/CPU si IA absente ; aucune preuve RTX/Cricut créée par le diagnostic.

### O-008 — Vérification de portabilité et confidentialité avant partage (cycle 05)

- **Problème :** un projet fonctionne sur un PC mais devient inutilisable ailleurs lorsque ses sources ou polices restent externes ; un export de diagnostic peut exposer des chemins personnels. Un ZIP valide ne signifie pas « projet autonome ».
- **Scénario :** depuis la bibliothèque, choisir « Vérifier avant partage » ; l'inspecteur signale les ressources embarquées, les dépendances manquantes, les chemins locaux, la taille et les licences déclarées. Le contrôle reste hors ligne et ne modifie pas l'archive.
- **Gain :** éviter des projets incomplets, des fuites de chemins et des promesses de portabilité non prouvées ; utile aux projets éducatifs, stickers et patrons.
- **Interaction :** `[Projet portable ? À vérifier]` `[Ressources 12/12 présentes]` `[Dépendances externes 2]` `[Rapport expurgé]` `[Annuler]`. Ne pas afficher « 100 % portable » sans validation du lecteur cible.
- **Alternatives :** recopier tout le dossier de travail (dépendances et secrets involontaires) ou partager sans vérification (échecs non reproductibles) ; rejetées. La création d'un package partageable est une évolution distincte à qualifier, **pas** un zip automatique.
- **Effort/dépendances :** moyen ; schéma V2, inventaire de ressources et liens, tests V34-031, `T-V34-05-02,06,07,19`. L'implémentation serait P1 après les garanties d'intégrité P0.
- **Risques :** faux sentiment de conformité, copie de médias sous droits, chemins privés et métadonnées EXIF ; affichage explicite « droits à vérifier », aucun upload, aucun nettoyage destructif de l'original.
- **Recette :** fixture avec 2 dépendances externes et un chemin privé : statut `NON_PORTABLE`, rapport expurgé, archive inchangée ; fixture sans dépendance : statut `PORTABILITE_STRUCTURELLE_VERIFIEE` uniquement, **pas** certification de Design Space.


### O-009 — Historique groupé et aperçu d'annulation (cycle 06)

- **Problème :** un utilisateur ne sait pas si « Annuler » retirera un coup de pinceau, douze sujets acceptés ou une opération SCORE entière ; une annulation partielle peut détruire la cohérence d'un patron.
- **Scénario :** après AcceptSubjectsBatch ou AssignOperation(CUT+SCORE), ouvrir « Historique », sélectionner le dernier groupe et voir une superposition avant/après **sans modifier le projet** ; confirmer Undo. La même vue est accessible au clavier et en Express/Expert.
- **Gain :** rendre prévisible une action destructive et faciliter la correction sans perte d'identités ou de masques float32 ; **pas** un Undo de fabrication physique.
- **Interaction :** [Historique] [Groupe : 12 sujets] [Avant / Après] [Annuler le groupe] [Retour] ; un export déjà transmis affiche « ne peut pas être annulé dans Design Space ».
- **Alternatives :** Ctrl+Z sans aperçu (insuffisant pour groupes), snapshot complet à chaque geste (coût RAM/ZIP élevé) ; retenir patches exacts et preview dérivée non autoritaire.
- **Effort/dépendances :** moyen, V34-035, V34-037 et V34-038 ; corpus de masques float32 et groupes Score/Cut ; tests T-V34-06-13..16,21,23. P1, non bloquant pour le moteur P0.
- **Risques/limites :** historique trop volumineux, preuve sujet périmée, faux Undo d'une découpe ; quotas visibles, vérification de digests et avertissement explicite.
- **Recette :** aperçu n'incrémente aucune révision ; Undo du groupe CUT+SCORE restaure toutes les assignations ; Undo/Redo float32 est bit-identique ; aucun export externe effacé.

### O-010 — Propositions de jobs périmées récupérables (cycle 06)

- **Problème :** pendant une segmentation locale longue, l'utilisateur retouche son projet ; le résultat IA arrive sur une révision ancienne. Le jeter sans explication gaspille du temps, l'appliquer silencieusement corrompt les liens d'identité.
- **Scénario :** job commencé en r8, projet passé en r9 ; la proposition est isolée en « À revoir », avec source, révision, date, différences de géométrie et boutons « Comparer », « Relancer sur r9 », « Ignorer ». Aucun rebind automatique de masque ou de sujet.
- **Gain :** transparence et récupération de travail sans sacrifier CAS, compatibilité CPU/manuelle et confidentialité.
- **Interaction :** [1 proposition obsolète] [Comparer r8/r9] [Relancer — consentement si IA] [Supprimer la proposition] ; stockage local temporaire avec durée/volume affichés.
- **Alternatives :** appliquer automatiquement (REJET, risque d'identité), relancer silencieusement (REJET, GPU/consentement), supprimer sans signaler (moins utile).
- **Effort/dépendances :** moyen, V34-036/037/039, corpus jobs annulés/OOM ; T-V34-06-17..20,27 ; P1 après sécurité P0.
- **Risques/limites :** images privées en cache, propositions incompatibles, accumulation disque ; TTL et quotas contrôlés, purge explicite, aucune donnée publiée ni modèle téléchargé sans accord.
- **Recette :** proposition r8 n'altère jamais r9 ; action Relancer crée un nouveau job et exige consentement ; absence de modèle IA laisse la voie manuelle ; suppression n'altère pas le .smartsvg.

### O-011 — Bac à sable d'import avant projet (cycle 07)

- **Problème :** l'utilisateur veut essayer une image, voir si elle convient et changer d'intention sans créer de projets vides ni polluer sa bibliothèque.
- **Scénario :** déposer une photo, inspecter format/orientation/alpha, prévisualiser « sticker / silhouette / SVG », décider « Créer le projet » ou « Abandonner » ; le fichier original reste inchangé. Un brouillon temporaire ne possède ni receipt de commit ni statut « enregistré ».
- **Gain :** moins de projets parasites et d'actions inutiles ; possibilité d'essayer sans IA, sans téléchargement, sans coût réseau.
- **Interaction :** `[Essayer l'image] [Choisir une intention] [Créer un projet] [Abandonner et nettoyer]` ; statut permanent `BROUILLON NON ENREGISTRÉ`.
- **Alternatives :** création immédiate d'un `.smartsvg` (plus simple techniquement, mais bibliothèque polluée), état volatile seul (perdu au crash), espace temporaire local à quota (recommandé sous réserve de tests).
- **Effort/dépendances :** moyen ; V34-025, V34-041/042/048 ; formats d'entrée sécurisés et stratégie de suppression des copies temporaires.
- **Risques :** accumulation de données privées, chemin externe/ZIP hostile, fausse promesse de récupération ; quotas, purge explicite et avertissement de non-sauvegarde.
- **Recette :** T-V34-07-02/03/09/28 ; aucune mutation du SHA original, abandon nettoie la copie temporaire, crash ne crée aucun projet canonique ; aucune publication de média personnel.

### O-012 — Opérations lisibles sans dépendance à la couleur (cycle 07)

- **Problème :** des calques Cut, Score, Draw et Foil représentés uniquement par couleurs peuvent être confondus, notamment en cas de daltonisme, impression monochrome ou contraste faible.
- **Scénario :** patron carton ouvert en Fabrique : CUT = trait plein + ciseaux, SCORE = pointillé + pli, DRAW = motif fin + stylo, FOIL = motif distinct + texte ; la légende accompagne la liste accessible et l'export du guide, sans modifier les opérations sémantiques.
- **Gain :** réduction des erreurs d'interprétation et meilleure accessibilité ; utile même sans IA et sans connexion.
- **Interaction :** `[Afficher les opérations] [☑ Icônes] [☑ Motifs] [☑ Noms]` ; le texte reste toujours présent dans la liste accessible. Les motifs sont des **aides visuelles**, pas des instructions de coupe exportées comme chemins.
- **Alternatives :** couleurs seules (REJET accessibilité), légende textuelle seule (fallback minimal), couleurs+motifs+texte (recommandé).
- **Effort/dépendances :** faible à moyen ; V34-012, V34-041/045/049 ; aucun changement du moteur géométrique.
- **Risques :** confusion si motifs SVG sont exportés dans la géométrie de fabrication ; séparation stricte overlay UI vs chemins de production. Pas de prétention à la compatibilité outil sans profil.
- **Recette :** T-V34-07-17/19/22/27 ; les quatre opérations sont distinguables sans couleur, l'export géométrique reste inchangé, le lecteur d'écran annonce l'opération.

### O-013 — Explication de chaque suggestion (cycle 08)

- **Problème :** un novice ne sait pas pourquoi « sticker » entraîne PNG Print Then Cut plutôt que SVG Basic Cut ; un modèle pourrait proposer une opération sur la base d'une hypothèse non vérifiée.
- **Scénario :** « Je veux découper mes escargots » → carte « Découpe seule » avec [Pourquoi ?] : mots reconnus, effet sur couleurs, contrat de sortie, limites Cricut et besoin de confirmer la taille.
- **Gain :** décisions plus sûres et compréhensibles, correction d'une mauvaise suggestion avant toute commande.
- **Interaction :** [Pourquoi cette suggestion ?] [Autre résultat] [Ignorer] ; badge USER_EXPLICIT/RULE_MATCH/MODEL_SUGGESTION/UNKNOWN et avertissement non certifié.
- **Alternatives :** explication opaque d'un LLM (REJET, non vérifiable), aucun contexte (moins utile), justification par règles/contrats (recommandée).
- **Effort/dépendances :** faible à moyen ; V34-051..054/056, S-071/075/083, R33-020/034 ; T-V34-08-11/13/21/22.
- **Risques :** explication trompeuse ou trop verbeuse ; limiter à source, effet, incertitude, une phrase initiale et détail repliable.
- **Recette :** suggestion d'un SVG Basic Cut précise que les couleurs internes ne sont pas conservées ; source modèle jamais présentée comme preuve ; changement de profil invalide l'ancienne justification.

### O-014 — Préférences d'intention à reconfirmation (cycle 08)

- **Problème :** répéter les mêmes choix ralentit les utilisateurs, mais réutiliser une cote, une épaisseur ou un outil sans vérification peut produire une fabrication erronée.
- **Scénario :** après plusieurs stickers, suggérer « largeur utilisée précédemment : 40 mm » **sans préremplir silencieusement** ; si une autre matière ou machine est sélectionnée, la suggestion est réévaluée.
- **Gain :** moins de saisie répétée, conservation du contrôle utilisateur et du contexte.
- **Interaction :** [Utiliser 40 mm pour ce projet] [Autre taille] [Ne plus suggérer] ; portée explicite « ce type de projet », date et provenance locale.
- **Alternatives :** défaut automatique (REJET), aucune mémoire (fallback), rappel local à confirmation (recommandé).
- **Effort/dépendances :** moyen ; V34-052/055/057, R33-032/039, T-V34-08-19..21.
- **Risques :** préférences obsolètes, données privées, faux profil machine ; stockage local versionné, suppression et expiration, jamais certification.
- **Recette :** sans clic de confirmation, aucune dimension n'entre dans la commande ; changement de machine/profil force nouvelle vérification ; suppression des préférences ne change pas le .smartsvg.

### O-015 — Écoute permanente au microphone : rejet (cycle 08)

- **Problème allégué :** rendre le dialogue mains libres.
- **Scénario proposé :** capturer automatiquement la voix à l'ouverture de SmartSVG.
- **Gain réaliste :** marginal pour les workflows de création au clavier/souris.
- **Alternatives :** champ texte, boutons de choix, commandes clavier, dictée OS volontaire si disponible (hors intégration produit).
- **Effort/risques :** élevé, permissions micro, confidentialité, fausses activations, accessibilité, maintenance ; aucun avantage démontré sur RTX 3070 ou Explore 5.
- **Interaction rejetée :** aucun bouton d'écoute automatique ; si étudié ultérieurement, opt-in explicite et étude de besoin séparée.
- **Recette de non-régression :** aucun accès au microphone ni permission demandée à l'ouverture ; tests T-V34-08-04/05/17 (frontière de confiance). **REJET**, aucun ticket d'implémentation.

### O-016 — Diff des mutations avant validation (cycle 09)

- **Problème :** une proposition « fais une planche » peut modifier des paramètres du projet sans que l'utilisateur comprenne lesquels ; une explication de la suggestion (O-013) ne décrit pas ses **effets réels**.
- **Scénario :** après simulation, voir « intention : non définie → stickers ; largeur : absente → 40 mm ; aucun export, aucun téléchargement » ; comparaison des IDs/calques touchés et possibilité de refuser.
- **Gain :** réduire les confirmations aveugles et les Undo ; utile en mode novice et expert.
- **Interaction :** [Voir les changements] [Confirmer les changements visibles] [Modifier] [Annuler] ; accessible clavier et lecteur d'écran.
- **Alternatives :** simple résumé textuel (fallback), diff structuré (retenu P1), application silencieuse (rejet).
- **Effort/dépendances :** moyen ; V34-062/065, SessionPresenter, CommandPort et snapshot V2 ; risque de diff incomplet ou de décalage entre aperçu et commit.
- **Recette :** T-V34-09-15/25/26 ; toute modification non affichée invalide la confirmation ; un plan périmé exige nouveau diff ; aucun badge de fabrication certifiée.

### O-017 — Refus réparateur contextualisé (cycle 09)

- **Problème :** « PLANNER_MISSING_DIMENSION » ne dit pas au débutant comment corriger le blocage ; l'assistant ne doit pas contourner la contrainte.
- **Scénario :** boîte sans épaisseur : « Il manque l'épaisseur du carton pour préparer les plis » → [Saisir l'épaisseur] [Rester en brouillon] ; SCORE non vérifié → [Ouvrir le guide Design Space].
- **Gain :** moins d'impasses sans diminuer le niveau de sécurité.
- **Interaction :** message localisé FR, champ/objet concerné, prochaine action autorisée, aucun dialogue en boucle.
- **Alternatives :** code brut (fallback expert), action corrective guidée (retenu), valeur inventée (rejet).
- **Effort/dépendances :** faible à moyen ; V34-061/066, moteur de prévol, mapping de codes d'erreur.
- **Risques :** suggérer un achat inutile ou présenter une compatibilité non vérifiée ; ne proposer qu'une action sûre et ne pas prétendre configurer la machine.
- **Recette :** T-V34-09-27/28 ; le refus ne modifie aucun SHA, conserve l'erreur bloquante et annonce explicitement les étapes manuelles Score/Attacher.

### O-018 — Autovalidation des plans : rejet (cycle 09)

- **Problème allégué :** gagner un clic en laissant l'IA confirmer et exécuter les changements.
- **Scénario rejeté :** un modèle déduit matière/dimensions et applique plusieurs commandes sans revue humaine.
- **Gain :** marginal par rapport à la confirmation groupée, sans bénéfice démontré sur la fabrication.
- **Alternatives :** plan non mutant, aperçu/diff, confirmation explicite unique sur groupe transactionnel sûr.
- **Effort/risques :** risque critique d'erreur matérielle, faux consentement, attaque par injection, écriture hors CAS.
- **Interaction rejetée :** pas de bouton « toujours exécuter les suggestions » ; le mode expert conserve les mêmes autorisations.
- **Recette de non-régression :** T-V34-09-17/18/21/23 ; sans clic lié au digest, 0 commande mutante. **REJET**, aucun ticket.

### O-019 — Liaison explicite des accessoires à leur sujet (cycle 10)

- **Problème :** la détection d'une fleur, d'une antenne ou d'un œil détaché peut produire un objet séparé, ou un faux rattachement ; S-028 impose de conserver les accessoires, mais ne spécifie pas le contrôle utilisateur sur la **relation**.
- **Scénario :** une planche de 12 escargots propose 12 sujets et 3 accessoires ambigus ; sélectionner « Fleur ? », voir deux parents candidats, choisir [Lier à escargot 02] ou [Conserver séparé]. Les pixels et le masque float32 ne changent pas par cette liaison.
- **Gain :** évite perte de détails et fusion irréversible ; trace une décision humaine utile au futur nesting.
- **Interaction :** `[Accessoire 03] [Parent : aucun ▾] [Lier] [Séparer] [Annuler]` ; afficher la région et la provenance de la suggestion, ne pas deviner la sémantique.
- **Alternatives :** fusion automatique des pixels (rejet), conserver tous les fragments séparés (fallback), relation explicite réversible (retenue).
- **Effort/dépendances :** moyen ; V34-073, S-028, R33-006, V34-032..040, V34-071/072 ; modèle relationnel V2.
- **Risques :** relation erronée, cycles, suppression parent, projet stale ; validation graphe acyclique, CAS/epoch, Undo, warnings, pas de `subject_id` dérivé du numéro de vignette.
- **Recette :** T-V34-10-15/20 ; lier/délier préserve digest float32, Undo retrouve l'état exact, relation orpheline refusée. **P1 / RETENU_POUR_SPEC**.

### O-020 — Contrôle des bords au pixel 1:1 (cycle 10)

- **Problème :** un masque paraît correct en vignette, mais coupe une antenne ou conserve un halo d'arrière-plan. Le prévol de découpe intervient trop tard pour corriger la segmentation.
- **Scénario :** avant « Accepter », sélectionner [Inspecter les bords] ; le logiciel montre zoom 100 % et points d'inspection reproductibles autour du contour, sans masquer les régions non inspectées.
- **Gain :** qualité de revue plus fiable sans exiger un nouveau modèle IA ; possible sans GPU.
- **Interaction :** `[Original] [Masque float32] [Différence] [Bord suivant] [Corriger]` ; avertissement « échantillons indicatifs, pas contrôle exhaustif ».
- **Alternatives :** accepter sur miniatures (risque), inspecter tous les pixels manuellement (coûteux), échantillonnage déterministe + accès zoom libre (retenu).
- **Effort/dépendances :** moyen ; V34-076, V34-071/075, S-015/073/079, R33-019 ; index de contour et rendu fidèle.
- **Risques :** illusion de certification, coût CPU sur 50 objets, biais d'échantillonnage ; aucun badge `QUALIFIE`, quota et navigation accessible.
- **Recette :** T-V34-10-15/16/27/28 ; même masque+seed = mêmes points, modification du masque invalide le contrôle, aucune mutation lors de l'inspection. **P1 / RETENU_POUR_SPEC**.

### O-021 — Upload cloud automatique : rejet (cycle 10)

- **Problème allégué :** améliorer les masques sans installation locale.
- **Scénario rejeté :** la photo est téléversée à l'import vers un fournisseur externe, sans action explicite.
- **Gain :** non démontré ; l'utilisateur perd le contrôle sur les œuvres et images privées.
- **Interaction rejetée :** aucun bouton ou comportement d'envoi silencieux ; le mode manuel/CPU demeure disponible.
- **Alternatives :** règles déterministes, correction manuelle, modèles locaux installés uniquement sur consentement séparé.
- **Effort/risques :** coûts, fuite de données, dépendance réseau, licences et gouvernance disproportionnés ; incompatible avec R33-030.
- **Recette :** T-V34-10-24/25 ; import et segmentation sans IA = **zéro** appel réseau, aucune donnée de source envoyée. **REJETÉ**, pas de ticket d'implémentation.

## Gouvernance du registre

À chaque cycle, ajouter 1 à 3 idées distinctes **ou consigner l'absence d'idée pertinente** ; éviter les scores mécaniques et les promotions automatiques. Une opportunité retenue ne devient implémentable qu'avec exigence liée, ticket, tests et Definition of Done. Les références Cricut du cycle 02 sont consignées dans [02_VISION_PARCOURS.md](02_VISION_PARCOURS.md#10-références-externes-vérifiées-et-incertitudes-29-octobre-2026). Aucune licence de modèle IA n'est validée par ce registre.

### O-022 — Comparateur de valeur marginale d'un modèle (cycle 11)

- **Problème :** l'utilisateur peut télécharger plusieurs centaines de Mo sans savoir si la qualité s'améliore réellement sur son image ; le modèle n'est pas systématiquement meilleur que le détourage manuel.
- **Scénario :** sur une ROI autorisée et déjà dotée d'une vérité terrain ou d'une retouche manuelle de référence, comparer règles/manuel et un modèle local **déjà installé** ; afficher IoU/bords/temps/VRAM lorsque mesurés. Sans référence, afficher « aperçu visuel uniquement, gain non quantifié ».
- **Gain :** choix informé, moins d'installations et de retouches inutiles. **Alternative :** classement générique de modèles (rejeté comme preuve de gain sur une image donnée).
- **UX :** `[Sans IA] [Avec modèle local] [Comparer à 100 %] [Conserver la version manuelle]` ; aucune suggestion de téléchargement déclenchée par le comparateur.
- **Effort/dépendances :** moyen ; V34-071/074/076/081/084, corpus, métriques alignées et provenance. **Risques :** temps supplémentaire, faux scores sur masques sans vérité terrain, biais de sélection.
- **Recette :** T-V34-11-27/28 ; comparer le même SHA/ROI, ne jamais afficher une métrique IoU sans vérité terrain, aucune mutation ni réseau ; si aucun modèle installé, rester sur règles/manuel. **P1**, pas de dépendance P0.

### O-023 — Gate de provenance des modèles locaux déjà installés (cycle 11)

- **Problème :** un modèle déjà présent peut avoir été modifié, être devenu incompatible avec le runtime, ou ne pas avoir de licence exploitable ; « présent » ne signifie pas « sûr ».
- **Scénario :** à la demande d'inférence, contrôle offline du hash de tous les fichiers, révision, licence approuvée, SBOM et runtime, puis `READY_QUALIFIED` seulement si la preuve liée à l'environnement existe.
- **Gain :** réduction du risque d'exécution non autorisée et meilleure reproductibilité ; **alternative :** simple contrôle d'existence de fichier (insuffisant).
- **UX :** `[Modèle présent — provenance non vérifiée] [Vérifier localement] [Passer en manuel]`, sans connexion ni mise à jour implicite.
- **Effort/dépendances :** moyen ; V34-078/080/086, manifests épinglés et hashing streaming. **Risques :** coût de re-hash sur gros fichiers, erreurs de droits Windows ; cache de vérification seulement si intégrité du cache prouvée, sinon re-hash.
- **Recette :** T-V34-11-02/04/10/15/16/17 ; 1 octet altéré = `CORRUPT` et inférence bloquée, modèle inconnu = `MANUAL`, 0 réseau, 0 mutation projet. **P1** comme raffinement d'une gate de sécurité P0.

### O-024 — Installation automatique à l'import : rejet (cycle 11)

- **Problème allégué :** économiser un clic de configuration. **Scénario refusé :** l'utilisateur importe une photo et le programme télécharge automatiquement un modèle « optimal ».
- **Pourquoi rejet :** poids/licences/usage commercial non qualifiés, réseau et espace disque non consentis, exécution possible de code distant, latence et confusion UX. **Alternative :** `[Continuer sans IA]` et fiche facultative avec consentement explicite.
- **Effort/risque :** implémentation moyenne, risque juridique/sécurité élevé, valeur faible ; **UX alternative** `[Installer maintenant] [Plus tard] [Jamais]`.
- **Recette de non-régression :** T-V34-11-01/02/07 ; 0 requête réseau au simple import, même avec modèle absent ou suggestions actives. Aucun ticket pour l'installation silencieuse.

### O-025 — Contrôle de franges à l'échelle de sortie (cycle 12)

- **Problème :** un sticker propre en miniature peut présenter un liseré sombre ou blanc une fois imprimé ; l'aperçu du masque seul ne révèle pas la couleur RGB des pixels semi-transparents.
- **Scénario :** après préparation de 12 escargots, sélectionner [Fond blanc] [Fond noir] [Damier] [Zoom 100 %] [Échelle indicative mm] ; afficher la **texture PNG finale**, les pixels à alpha intermédiaire et la provenance du redimensionnement. Aucun affichage ne promet le rendu exact de l'imprimante.
- **Gain :** détecter des halos avant export et éviter des réimpressions. **Alternatives :** aperçu sur damier seulement (insuffisant), épreuve papier physique (plus fiable mais coûteuse), comparateur multi-fonds (retenu).
- **Effort/dépendances :** moyen ; V34-088/089/091/095, gestion ICC et alpha. **Risques :** confusion simulation/rendu réel, faux sentiment de qualité ; badge `SIMULATION` obligatoire.
- **Recette :** T-V34-12-06/11/12/27 ; franges visibles sur fixture R12-B, aucune mutation de la coupe, clavier et tailles accessibles. **P1 / RETENU_POUR_SPEC**.

### O-026 — Diff topologique entre alpha accepté et export (cycle 12)

- **Problème :** un rééchantillonnage peut supprimer un petit trou, fusionner deux îlots ou ajouter un pixel faible non visible en vignette ; la QA statique n'indique pas **à quelle transformation** l'écart est apparu.
- **Scénario :** [Voir les changements de coupe] affiche `avant/après` sur les mêmes coordonnées, compte composantes/trous aux seuils 0/20/128, signale la première transformation divergente et propose [Revenir à la coupe acceptée].
- **Gain :** diagnostic reproductible des régressions, sans fausse preuve Cricut. **Alternatives :** comparer seulement à 128 (perd les franges), QA finale seule (pas de localisation), diff multi-seuil (retenu).
- **Effort/dépendances :** moyen ; V34-088/090/095, digest de contour, budget CPU. **Risques :** coût sur 50 ROI, faux positifs aux seuils bas ; rapport borné et warning sans seuil arbitraire de certification.
- **Recette :** T-V34-12-09/17/20 ; une microcomposante ajoutée est détectée au seuil concerné, ancien digest inchangé, aucune correction sans commande explicite. **P1 / RETENU_POUR_SPEC**.

### O-027 — Upscale IA systématique à l'import : rejet (cycle 12)

- **Problème allégué :** rendre chaque dessin « HD » sans effort.
- **Scénario rejeté :** chaque JPG/PNG déclenche automatiquement une inférence et inscrit 600 ppp, même lorsque l'original est net ou la machine est hors ligne.
- **Raison du rejet :** licence/VRAM/consentement, latence et hallucination de détails ; 600 ppp interpolés ne signifient pas résolution native, et la qualité physique dépend de l'impression.
- **Alternative UX :** [Conserver] [Rééchantillonnage CPU] [Essayer un modèle local déjà installé] avec comparaison et avertissement de résolution source.
- **Recette de non-régression :** T-V34-12-13/14/15 ; 0 modèle lancé au simple import, OOM non mutant, aucun badge « détail réel augmenté ». **REJETÉ**, aucun ticket dédié.

### O-028 — Conseiller de budget de chemins SVG (cycle 13)

- **Problème :** une illustration détaillée peut produire des milliers de chemins, parfois au-delà de la limite de **5 000 paths** annoncée par Cricut pour l'upload SVG ; l'utilisateur découvre l'erreur après l'export.
- **Scénario :** l'utilisateur choisit « Tous les traits » sur un dessin synthétique très dense ; le panneau montre `1 820 chemins après expansion`, `limite documentaire Cricut : 5 000`, `performance non qualifiée`, et propose `Réduire les détails` ou `Séparer en fichiers`. **Ne jamais affirmer que 4 999 chemins s'importent vite ou se découpent correctement.**
- **Gain :** anticiper l'échec d'upload et aider à simplifier sans perdre silencieusement des éléments ; aucune preuve machine.
- **Alternatives :** avertir après export (tardif), simplifier automatiquement sans aperçu (perte), conseiller avant export avec comparaison/Undo (retenu).
- **Effort/dépendances :** moyen ; V34-098/100/101/103, S-030/034/056, profil Cricut daté ; comptage après expansion et hiérarchie, quotas CPU.
- **Risques :** confondre nombre de paths et nombre de segments ; compter avant expansion ; sous-estimer la complexité ; avertissement sans garantie.
- **Interaction :** `[Complexité : 1 820 paths] [Voir par calque] [Simplifier avec aperçu] [Conserver] [Répartir]`.
- **Recette :** T-V34-13-16/17 : fixture 5 001 paths bloquée en profil Cricut ; 64 chemins G2.7 n'est pas annoncé comme limite universelle ; aucun export automatique sans validation. **P1 / RETENU_POUR_SPEC**.

### O-029 — Verrouillage des trous utiles (cycle 13)

- **Problème :** une simplification qui préserve l'aspect général peut effacer un petit trou d'une silhouette ou souder deux ouvertures, modifiant l'usage prévu.
- **Scénario :** l'utilisateur sélectionne le trou central d'un anneau et choisit `Préserver ce trou`; une simplification ultérieure qui le détruirait passe en `REVIEW_REQUIRED` et propose un réglage plus conservateur.
- **Gain :** préservation d'une intention utilisateur sans imposer des tolérances identiques à tous les matériaux ; complète S-033/034 et le moteur topologique, pas une nouvelle famille fonctionnelle.
- **Alternatives :** simplifier sans contrôle (rejet), bloquer toute simplification (trop restrictif), marquer des contraintes locales réversibles (retenu).
- **Effort/dépendances :** moyen ; V34-097/098/102, S-033/034, R33-004/008 ; identités persistantes des anneaux et recalcul d'empreinte.
- **Risques :** trous trop petits pour être découpés malgré préservation mathématique ; ne pas promettre fabricabilité. Changement de source/révision invalide la contrainte périmée.
- **Interaction :** `[Trou 03] [🔒 Préserver] [Voir avant/après] [Annuler]` ; raccourcis clavier équivalents et avertissement machine distinct.
- **Recette :** T-V34-13-04/09/25 : trou marqué jamais supprimé silencieusement, Undo rétablit le statut, changement de masque force une revue ; preuve physique indépendante. **P1 / RETENU_POUR_SPEC**.

### O-030 — Une coupe par couleur sans choix : rejet (cycle 13)

- **Problème allégué :** automatiser la fabrication d'une image multicolore.
- **Scénario rejeté :** à l'import, transformer chaque région de couleur en `CUT` sans demander matière, opération ou simplification ; un œil de 0,5 mm devient une coupe et des zones se superposent.
- **Gain :** non démontré ; forte probabilité de doubles chemins, détails impossibles et erreurs de fabrication.
- **Alternative :** vectoriser les couches **pour édition**, puis proposer une fabrication multicouche distincte avec prévol et confirmation.
- **Effort/risque :** faible pour créer des paths, mais risque élevé et QA disproportionnée ; valeur utilisateur négative sur dessins complexes.
- **Interaction rejetée :** pas de bouton `Convertir toutes les couleurs en coupes automatiquement` sans simulation et validation matière.
- **Recette négative :** T-V34-13-11/13/26 : un changement de palette ou une extraction de couche n'assigne aucune opération `CUT` et ne transforme jamais un guide de pli en `SCORE`. **REJETÉ**, aucun ticket propre.
