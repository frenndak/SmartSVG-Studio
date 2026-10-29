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

## Gouvernance du registre

À chaque cycle, ajouter 1 à 3 idées distinctes **ou consigner l'absence d'idée pertinente** ; éviter les scores mécaniques et les promotions automatiques. Une opportunité retenue ne devient implémentable qu'avec exigence liée, ticket, tests et Definition of Done. Les références Cricut du cycle 02 sont consignées dans [02_VISION_PARCOURS.md](02_VISION_PARCOURS.md#10-références-externes-vérifiées-et-incertitudes-29-octobre-2026). Aucune licence de modèle IA n'est validée par ce registre.
