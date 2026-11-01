# SmartSVG Studio — Accélération de l'exécution V3.3 (sans extension de périmètre)

**Nature :** guide opérationnel complémentaire **non normatif**, établi le 29 octobre 2026 à partir du maître V3.3, de ses registres, du code et des issues disponibles. **Autorité :** [ROADMAP_MASTER_v3_3.md](ROADMAP_MASTER_v3_3.md) + [traçabilité](ROADMAP_TRACEABILITY_v3_3.md) + [couverture](ROADMAP_COVERAGE_v3_3.md) ; l'[héritage](ROADMAP_HERITAGE_v3_3.md) reste intégral. **Aucune nouvelle exigence fonctionnelle, aucun gate supplémentaire, aucune fonction supprimée ou repoussée.** Ce fichier n'est ni une promotion V3.4 ni une modification de l'état de preuve d'une exigence.

## 1. Règles de non-ralentissement

1. **Maintenir la totalité du produit prévu** : F01–F15, P01–P10, G0–G9, S-001–S-101 et R33-001–R33-040. Le présent document réordonne des *travaux* uniquement lorsque les dépendances réelles le permettent ; il ne déplace pas les critères normatifs des gates.
2. **Une correction qui débloque un parcours réel prime sur un enrichissement de spécification.** Éviter les travaux de conception redondants, la réécriture des modules stables et les couches intermédiaires sans utilisateur ou consommateur identifié.
3. **L'architecture suit le besoin démontré.** Réutiliser d'abord les contrats G1.2, la sauvegarde G1.3/G1.4, l'atelier G2/G3, le snapshot G2.4, l'inspecteur G2.6 et le replay `smartsvg_editor/strokes.py`. N'introduire une abstraction que lorsque deux consommateurs réels ou un risque vérifiable la justifient.
4. **Une fonction terminée ne doit pas être redivisée pour la planification.** Conserver les lots vérifiables nécessaires à la sécurité, mais éviter les PR de préparation sans effet observable. Pas de nouvel outil, nouveau framework, migration imposée ni seconde application pour satisfaire ce guide.
5. **Ne pas allonger artificiellement les revues.** Tester les invariants ciblés puis les CI existantes au HEAD exact ; ne jamais alléger les tests, la protection des sauvegardes, les contrôles de provenance, les révisions ni les vérifications humaines/physiques exigées pour revendiquer une capacité.
6. **Ne pas conditionner une livraison courante à la V3.4 en rédaction.** La PR V3.4 #73 et l'issue #72 sont des propositions séparées, **sans effet de gate** tant qu'une promotion formelle n'est pas décidée. Une idée V3.4 ne devient pas une nouvelle dépendance P0/P1 par simple présence dans un document.

## 2. Ordre de livraison utile — aucun décalage des fonctions

**Point de départ vérifié à la création :** G3.3e-a PR #68 et G3.3e-b1 PR #70 intégrées ; issue [#71](https://github.com/frenndak/SmartSVG-Studio/issues/71) ouverte pour G3.3e-b2a. Ces repères ne remplacent jamais la consultation de `main` lors d'un cycle futur.

| Voie | Prochaine livraison ou preuve | Réutiliser / limiter | Dépendance réelle et possibilité de parallèle |
| --- | --- | --- | --- |
| **A — Édition des vrais sujets** | G3.3e-b2a : une retouche `add/erase` **prévisualisée** sur le bon `subject_id`, sans écriture | `strokes.py`, G2.4 et la preuve de sujet G3.3e-b1 ; conserver float32 exact, garde de révision, annulation | Immédiat ; issue #71. Ne pas préconstruire un nouveau moteur de pinceau. |
| **A — Édition persistante** | G3.3e-b2b : valider/enregistrer le geste, récupération, undo/redo selon les contrats déjà prévus | Sauvegarde atomique/recovery existants et modèle de commandes ; ne pas refaire le format `.smartsvg` | Après preuve d'aperçu b2a ; pas de double édition concurrente. |
| **A — Parcours intégré** | Faire fonctionner import → inspection réelle → sujet choisi → retouche → sauvegarde/réouverture depuis Express/Atelier | Une autorité `.smartsvg` et un seul état de sélection ; retirer les allers-retours techniques inutiles dans **le parcours existant**, sans nouvel espace applicatif | À raccorder progressivement à chaque lot A ; UX réelle Windows à qualifier dès qu'un poste est disponible. |
| **B — Préparation Cricut existante** | Auditer/tester séparément PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche et SVG d'édition ; unité mm, `viewBox`, topologie, contours et défauts | Moteurs et fixtures SVG/PNG présents, sans changement de contrat et sans certification anticipée | **Peut avancer en parallèle des retouches A** sur des fixtures synthétiques, sans exiger une IA de segmentation opérationnelle. Gates G4/G5 conservés. |
| **C — Masques et IA facultative** | Achever le détourage véritable des images smartphone, choix des sujets/accessoires et modes manuel/CPU/GPU explicites | Adaptateurs ComfyUI/fournisseurs existants ; une exécution identifiée et des replis honnêtes | Brancher sur les contrats de sujets déjà éprouvés. Ne **bloque pas** les tests statiques des exports B. Respecter G3 et ses preuves. |
| **D — Fonctions créatives et production** | Continuer G5/G6/G7 : vecteurs, calques, composition, texte, bibliothèque, planches 12/24, lots et variantes | Même état de projet, mêmes unités et commandes ; mutualiser les contrôles sans créer un moteur parallèle | Selon les dépendances G0–G9 réelles ; toutes les capacités restent au programme. |
| **E — Qualification / extension** | G8 : installation, compatibilité et recette ; G9 : fonctions avancées déjà prévues | Preuves distinctes automatique / Windows / Design Space / physique | Recettes ciblées réalisées dès que possible, sans les présenter comme réussies avant exécution ; jalons normatifs inchangés. |

**Règle anti-fausse dépendance :** G4 peut commencer la vérification de ses **contrats de fichiers sur fixtures** avant que l'IA G3 soit totalement raccordée. Cela **ne** permet pas de déclarer P01/P02/P04 qualifiés sans les preuves Design Space et physiques exigées. À l'inverse, enregistrer les vraies retouches nécessite le contrat d'identité/révision : cette dépendance est réelle et conservée.

## 3. Réduction de la dette de coordination, pas des tests

| Risque de ralentissement | Traitement sans nouveau chantier |
| --- | --- |
| Une PR apporte seulement une couche intermédiaire | Préférer une tranche verticale courte : action accessible, code minimal, test ciblé, échec récupérable ; sinon rattacher la préparation à son consommateur du même lot lorsque c'est sûr. |
| Doubles implémentations API/éditeur/Atelier | Déterminer le module autoritaire existant et y brancher le nouvel usage ; aucun doublon de stockage, moteur de pinceau, logique SHA, état de session ou export. |
| Tout retester manuellement à chaque micro-changement | Tests unitaires ciblés pendant l'édition, puis gates CI **pertinents** avant intégration ; requalification Windows/Design Space/physique lorsque la fonctionnalité ou sa preuve dépend réellement de cet environnement. |
| Matériel Windows ou Cricut momentanément indisponible | Enregistrer `NON_EXECUTE` sur l'axe concerné et poursuivre les lots **indépendants** ; ne pas prétendre qu'une CI remplace la recette requise au jalon. |
| Backlog V3.4 se transforme en obligations | Tri : **déjà prévu V3.3**, **simplification/remplacement interne sans changement UX**, ou **idée de fonction nouvelle = à part, non bloquante et non intégrée d'office**. |
| PR concurrentes ou base obsolète | Relire `main` et PR ouvertes, limiter les changements aux chemins du lot ; rebase/mettre à jour les preuves sur le SHA exact, jamais écraser une branche d'automatisation. |
| Documentation d'état datée | Un état compact fondé sur le `main` et les preuves du jour ; aucune campagne documentaire interminable ni retour sur des lots déjà fusionnés. |

**Test de valeur pour chaque modification proposée :** elle doit **réduire la duplication, le risque de régression ou une manipulation utilisateur existante**. Si elle ne le fait pas, elle ne doit pas entrer sur le chemin critique. Les optimisations de cache, traitements ciblés ou interfaces ne sont retenues que si leur gain ou problème est vérifiable ; aucune mesure de performance inventée.

## 4. Règle de décision rapide par micro-lot

**Avant développement :** relire `main`, PR en cours et issue liée ; vérifier **seulement** dépendances obligatoires, contrat d'autorité et scénario utilisateur. **Pendant :** utiliser modules existants, tests ciblés et cas d'échec liés au changement. **Avant fusion :** diff réel et chemins protégés, contre-expertise, régression adaptée, CI verte sur HEAD exact, absence de conflit/obstacle, rollback. Ces contrôles sont ceux de `AGENTS.md`, pas des gates supplémentaires. Les agents horaires créent des PR brouillon, ne les fusionnent jamais.

**Produit tangible à privilégier :** un fichier réellement utilisable ou une action réellement raccordée, et non un lot de documentation supplémentaire. **Métrique qualitative :** nombre d'étapes manuelles évitées, réutilisation d'un module réel, et preuve de non-régression ; ne pas fixer des dates ou pourcentages de vitesse sans mesure.

## 5. Interface avec la proposition V3.4 — zéro dérive

La campagne documentaire V3.4 (issue #72 / PR #73) peut **clarifier et ordonner ce qui est déjà prévu**, expliciter les interfaces et détecter les contradictions. **Elle ne doit pas étirer les fonctionnalités**, imposer de nouveaux prérequis pour V3.3, ni créer de « must-have » supplémentaires via des idées exploratoires. Les propositions de fonctionnalités réellement nouvelles restent identifiées comme **HORS PÉRIMÈTRE DE CETTE OPTIMISATION** et non actives ; aucune obligation de générer 1–3 idées par cycle. Terminer les cycles programmés selon leur échéancier actuel, sans relancer une campagne supplémentaire au nom de cette note.

**Ne pas déplacer le périmètre :** suppression, réduction ou report de G5–G9 interdits ; les enrichissements existants ne sont ni abandonnés ni rebaptisés « déjà faits ». L'accélération consiste exclusivement à retirer les dépendances fictives et la duplication.

**Retour arrière documentaire :** supprimer cette note et son lien depuis la matrice de couverture ; ni schéma projet, ni données utilisateur, ni outil ni fonctionnalité modifiés.
