# SmartSVG V3.4 — Registre d'opportunités de conception

**DRAFT — registre cumulatif sans doublons.** Créé au cycle 02 (29 octobre 2026). Les opportunités ne sont **pas** des fonctionnalités implémentées ni des obligations P0. Avant tout ajout, comparer F01–F15, S-001..101, R33-001..040 et V34 existants. Une idée déjà couverte devient un **raffinement** d'exigence, jamais un second ticket identique.

## Méthode d'arbitrage

Échelles indicatives 1 (faible) à 5 (fort) : `U` utilité, `F` fréquence, `FA` faisabilité, `V` valeur utilisateur ; `C` complexité et `R` risque (5 = très défavorable). Score comparatif = `U × F × FA × V / (C × R)`, **heuristique non scientifique**, utilisée uniquement entre candidats de même maturité. Ne pas classer P0 sur la seule base du score. Le statut est `CANDIDAT`, `RETENU_POUR_SPEC`, `REPORTE` ou `REJETE`. Les tickets futurs nécessitent tests et preuves.

| ID | Proposition | Écart avec V3.3 / V34 | U/F/FA/V/C/R → score | Priorité / décision |
|---|---|---|---|---|
| **O-001** | Journal local de transfert Design Space (étapes confirmées, versions, réglages, incidents et photo facultative) | Raffine S-010, S-084, R33-022, R33-034 ; pas un doublon du rapport de prévol, car il suit **l'après-export** ; V34-010 | 4/3/4/4/2/2 → 48 | **P1 / RETENU_POUR_SPEC** |
| **O-002** | Vérification guidée de l'échelle imprimante et de l'orientation A4 avant découpe, avec état « vérification externe nécessaire » | Raffine S-029, R33-022 et le parcours P01 ; évite de présenter un nesting indicatif comme une coupe garantie ; V34-007, V34-009 | 5/4/4/4/2/2 → 80 | **P1 / RETENU_POUR_SPEC** |
| **O-003** | Pilotage direct de la Cricut depuis SmartSVG sans Design Space | Hors périmètre, non documenté comme interface publique supportée ; contredit la règle de non-promesse du lot 02 | 2/2/1/2/5/5 → 0,32 | **REJETÉ** |

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

## Gouvernance du registre

À chaque cycle, ajouter 1 à 3 idées distinctes **ou consigner l'absence d'idée pertinente** ; éviter les scores mécaniques et les promotions automatiques. Une opportunité retenue ne devient implémentable qu'avec exigence liée, ticket, tests et Definition of Done. Les références Cricut du cycle 02 sont consignées dans [02_VISION_PARCOURS.md](02_VISION_PARCOURS.md#10-références-externes-vérifiées-et-incertitudes-29-octobre-2026). Aucune licence de modèle IA n'est validée par ce registre.
