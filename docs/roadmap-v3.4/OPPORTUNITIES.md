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

## Gouvernance du registre

À chaque cycle, ajouter 1 à 3 idées distinctes **ou consigner l'absence d'idée pertinente** ; éviter les scores mécaniques et les promotions automatiques. Une opportunité retenue ne devient implémentable qu'avec exigence liée, ticket, tests et Definition of Done. Les références Cricut du cycle 02 sont consignées dans [02_VISION_PARCOURS.md](02_VISION_PARCOURS.md#10-références-externes-vérifiées-et-incertitudes-29-octobre-2026). Aucune licence de modèle IA n'est validée par ce registre.
