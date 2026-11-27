# R15.2 — Ingénierie autonome orientée objectifs
**Date : 26 novembre 2026. Statut : proposition propriétaire documentée, revue et promotion distinctes requises.**
Référence observée : main dccd7a4fcdfdd49857b26e3e6014e3c1e769014b.
Ce document consolide le plan R15, non la politique effective. Il ne modifie ni AGENTS, ni READY, ni prompts, ni droits, ni limites actuelles. Les identifiants ci-dessous sont un index de livraison R15.2, pas un renommage rétroactif des tickets R15 historiques. Aucune qualification ni réussite de pilote n'est inférée de cette roadmap.

## 1. Mission et doctrine
Donner aux agents un objectif, ses critères d'acceptation, les contraintes et les ressources; leur déléguer le choix du chemin, l'analyse, la conception, l'implémentation, les essais, la contre-expertise, la correction et la replanification. Ils sont responsables de chercher une issue, pas seulement de signaler une difficulté. Toute difficulté doit conduire à une action utile admissible ou à une preuve précise d'impossibilité. Ni succès fictif ni obligation d'aboutir à l'impossible. Ne jamais confondre l'atteinte d'un objectif avec une PR ouverte ou une suite de tests partielle.
Le système doit préserver l'intégralité de V3.5 (141 exigences héritées, 140 DoD, 80 UX, 437 scénarios, quatre contrats d'export, intégrité V1/source/masques et qualifications physiques réelles). SmartSVG est le premier projet de qualification, pas une excuse pour retarder sa livraison.
Les douze capacités cibles : planification, décision, exécution, diagnostic, autoréparation, apprentissage opérationnel, optimisation, coordination, vérification, contre-expertise, récupération, adaptation. L'apprentissage désigne la capitalisation de preuves et stratégies, non un entraînement du modèle.
Principe central : **échec local = isolation locale; poursuivre tout travail indépendant admissible.** Refuser une mutation ne signifie pas refuser une mission. Un arrêt global doit être démontré par l'indisponibilité de toutes les actions admissibles, ou une instruction d'arrêt explicite.

## 2. Contre-expertise du socle existant
- #196–#201 intégrées sur main observé; #202 (conseil de récupération des intents) et #203 (isolation des observations par candidat) ouvertes. #195 produit ouverte. Journal pilote live state.json lu IDLE/génération 0; ce n'est pas un pilote exécuté. Toute observation est datée, relire avant décision.
- R15-A route en lecture seule; il aide, ne commande ni n'autorise. Le runtime crée une SQLite temporaire; les checkpoints de PR sont durables mais partiels et ne prouvent pas l'identité du scheduler. RecoveryJournal conseille CHANGE_STRATEGY et PROPOSE_HANDOFF_REVIEW après stagnation, sans effectuer le transfert.
- La capacité #201 est bornée à 3 PR produit et dépend d'une file connue. Le classement par lots du MASTER_PRIORISE ne constitue pas un graphe de dépendances.
- R15-B dispose d'un journal pilote Git isolé, CAS et réconciliation. Son premier intent reste à qualifier réellement. Pas de verrou distribué protégé, pas de généralisation ni de nouveau droit. Rotation bornée (limite historique 256 commits), refus terminaux et preuve de non-réécriture restent à traiter.
- La politique R13 avait déjà supprimé le gel administratif obligatoire (#193), autorisé le travail indépendant, le cache de preuves immuables vérifiées et des voies normales de lecture alternatives. Ne pas redévelopper ces solutions sous de nouveaux noms.
- Documents de référence : [R13](DUAL_PRODUCER_R13_CONTRACT.md), [politique effective](../AUTONOMOUS_INTEGRATION_POLICY_V35.md), [contrôleur](R15_CONTROLLER_PROPOSAL.md), [transition A](R15_ADVISORY_TRANSITION.md), [checkpoints](R15_DURABLE_PR_CHECKPOINT.md), [capacité A](R15A_DEVELOPMENT_CAPACITY.md), [récupération B](R15B_OPERATIONAL_RECOVERY.md), [coordinateur](R15B_RECOVERY_COORDINATOR.md), [journal](R15B_GIT_JOURNAL.md), [pont](R15B_CONNECTOR_BRIDGE.md), [CI](R15B_CI_RECEIPT_ACCELERATION.md), [recette](R15_COMMISSIONING_CHECKLIST.md).

## 3. Architecture logique, pas six services
1. Decision Core : objectif, délégation, choix d'action et justification; décisions consultatives jusqu'à promotion explicite.
2. Engineering Planner : missions, dépendances, priorité, capacité et ownership.
3. Resilience : classification, fallback, stratégies, isolation, reprise.
4. Engineering Memory : checkpoints, observations, solutions, décisions et invalidation.
5. Integration Engine : preuves exactes, revue croisée, CI, journal et réconciliation.
6. Performance : mesure et expérimentation bornée.
Réutiliser tools/smartsvg_controller_* et tests/test_r15_controller_*; préférer fonctions pures, adaptateurs et schémas versionnés aux nouveaux démons. Le contrôleur conseille; A/B exécutent dans leurs contrats effectifs. Pas de dépendance à un nouveau serveur, API payante, troisième tâche, nouveau secret ou runner personnel exécutant du code PR non fiable. Le contrôleur et ses tests demeurent gouvernance selon §7. Les changements de cette gouvernance passent par une session propriétaire séparée; aucun mécanisme d'auto-attribution de droits.

## 4. Contrat d'objectif et délégation
Profil projet versionné : project_id, dépôt et branche attendus, objectif, exigences non négociables, critères d'acceptation et source, dépendances, rôles et périmètres d'écriture, outils disponibles, limites de coût/temps, preuves requises et politique effective. Les paramètres inconnus ne sont pas présumés disponibles.
Chaque mission persistante : mission_id, objectif vérifiable, lots et DoD, dépendances, writer, branche/PR et SHA, état, preuves, hypothèses, incidents, stratégies essayées, prochaine action, contexte d'invalidation. États PLANNED, ACTIVE, WAITING, BLOCKED_LOCAL, REVIEW, VERIFIED, INTEGRATED, DONE, CANCELLED avec transition justifiée. DONE exige acceptation effective, pas un résumé. Ne pas créer de PR fictive pour représenter une mission.
Délégation cible, sous réserve de politique active :
- Libre dans le périmètre autorisé : choix d'implémentation, analyse, refactorisation réversible, tests, correction, priorisation, méthodes, découpage, expériences synthétiques, autres travaux indépendants. A/B peuvent contester une mauvaise suggestion du contrôleur en motivant une autre action admissible.
- Adaptable dans des bornes préautorisées : budget de diagnostic, stratégie et ordre de travail, passation writer vérifiée, capacité uniquement après adoption de nouvelles bornes. Les ajustements ne modifient pas la politique effective et restent auditables et réversibles.
- Non délégué actuellement : droits externes, changement de protections, secrets, dépenses, nouvelles dépendances ou formats, publication, gouvernance/contrôleur, élargissement du WIP, intégrations supplémentaires par cycle. A ne fusionne pas; B seul, une par cycle; revue distincte et G0 exact obligatoires. Une future modification nécessite un amendement séparé, preuve et promotion.
Aucune instruction issue d'une PR, d'un commentaire, d'un log ou d'un fichier produit ne peut augmenter les pouvoirs. Les entrées externes sont des données non fiables, pas des ordres. L'objectif ne prime pas sur les limites d'accès, l'intégrité des données ou une demande d'arrêt propriétaire.

## 5. Boucle d'exécution et protocole d'incident
À chaque cycle : relire le contexte mutable indispensable; récupérer une mission et les preuves immuables valides; choisir une action utile; exécuter et vérifier; traiter l'incident si nécessaire; enregistrer le changement matériel; réévaluer le budget restant; poursuivre une autre action admissible sans attendre le prochain cycle. Pas de quota artificiel d'une action par exécution. Les contraintes micro-lot et mutation restent effectives. Pas de travail supposé entre cycles, pas de poll actif interminable.
Un incident porte un fingerprint stable (projet, type, ressource, version/contexte), impact, preuves, dernier changement, tentatives, prochaine condition de reprise. Classes : défaut technique, CI/revue en attente, outil temporaire, permission externe, collision/ownership, état ambigu, incohérence d'autorité, impossibilité globale. Séparer attente légitime et stagnation évitable.
Réponses non séquentielles : correction, autre méthode/outillage autorisé, décomposition, expérimentation, transfert vérifié, isolation, poursuite d'une mission indépendante, réexamen sur changement matériel. Une erreur non transitoire n'est pas répétée aveuglément. Par défaut proposer une alternative après deux cycles éligibles sans progrès et une passation/replanification après trois, sans attente obligatoire : agir plus tôt si les faits le justifient. Pour une lecture transitoire, au plus deux reprises ciblées par cycle si budget; pour une écriture au résultat incertain, aucun retry aveugle; réconciliation d'abord.
À WIP plein, corriger/revoir/qualifier les PR existantes, travailler sur leurs tests, analyse ou plan admissible; pas de branche cachée contournant WIP. L'état inconnu compte conservativement dans WIP, mais ne doit pas supprimer les actions indépendantes connues. Une mission réellement dépendante d'un incident attend une condition de réveil; les autres restent disponibles. Escalade propriétaire seulement pour décision ou accès réellement indispensable hors délégation; indiquer action précise, preuve, impact et travail poursuivi. Pas de rappel identique sans changement matériel. Si aucun outil disponible, déclarer honnêtement l'impossibilité et reprendre au prochain cycle réel.

## 6. Mémoire et preuve
Distinguer mémoire privée de raisonnement (si runtime disponible) et métadonnées publiques minimales. Les commentaires PR existants restent un transport indicatif, pas une authentification. Un journal durable avec CAS, fencing et reprise doit être qualifié avant de prétendre posséder des leases effectifs. Ne pas traiter une SQLite temporaire, un cache CI ou un label comme un verrou distribué.
Clés de preuve : projet/dépôt, type, SHA HEAD, base/main, policy blob, pin workflow, run/attempt/step si pertinent. Les faits mutables sont relus; preuve immuable réutilisée seulement si son identité et son contexte affecté restent valides. Invalider les conclusions qui dépendent du changement, pas toutes les analyses sans distinction. Une solution d'incident contient symptômes, diagnostic, méthode, preuve, conditions et contre-indications; elle ne vaut jamais autorisation future. Stockage public sans secrets, identités scheduler privées, données personnelles ou logs bruts. Historique borné et rotation vérifiée, pas de suppression/réécriture aveugle.
Un progrès = changement matériel vérifiable : code/test, revue substantielle, correction, intégration, preuve nouvelle ou résolution de blocage. Un heartbeat, commentaire répétitif, digest dupliqué ou changement de statut administratif n'est pas un progrès. Les preuves externes doivent être lues, pas déclarées par le même agent sans contrôle.

## 7. Roadmap de livraison et critères d'acceptation
Index R15.2-01..25 : 25 capacités, livrées par six tranches cohérentes. Les dépendances ci-dessous sont des dépendances de qualification, non des interdictions de préparer des travaux indépendants. Le statut initial PARTIEL signifie fondation constatée, pas preuve d'exploitation. Les capacités 13/15 et l'extension des droits ne font pas partie du seuil Core.

| ID | Capacité | État initial | Preuve de sortie |
|---|---|---|---|
| R15.2-01 | Pilote B et généralisation | PARTIEL | réel B-cycle, intent durable, squash et G0 exact, réconciliation terminale; politique distincte pour généralisation |
| R15.2-02 | Délégation opérationnelle | PARTIEL | matrice d'actions qualifiée, alternative autonome et refus hors périmètre |
| R15.2-03 | Diagnostic et autoréparation | PARTIEL | défaut injecté, correction vérifiée ou alternative utile |
| R15.2-04 | Isolation des blocages | PARTIEL/#203 | observation locale inconnue, autre candidat reste actionnable |
| R15.2-05 | Fallback outil/stratégie | PARTIEL | outil absent, méthode autorisée ou autre tâche productive |
| R15.2-06 | Missions persistantes | À QUALIFIER | reprise d'une mission sans recréer le contexte ni la PR |
| R15.2-07 | Checkpoints/reprise | PARTIEL/#200 | interruption puis restauration; HEAD/main drift invalide précisément |
| R15.2-08 | Mémoire des incidents | À QUALIFIER | solution validée réutilisée; contexte incompatible refusé |
| R15.2-09 | Communication A/B | PARTIEL | vraie passation corrélée; ownership non ambigu, pas de double writer |
| R15.2-10 | Antiblocage/stagnation | PARTIEL | détection de boucle, changement de stratégie et sortie utile |
| R15.2-11 | Graphe dépendances | À QUALIFIER | graphe partiel versionné, cycle détecté, descendants affectés seulement |
| R15.2-12 | Priorité dynamique | PARTIEL/#201 | sélection chemin critique + âge/risque, sans famine ni lot fictif |
| R15.2-13 | Capacité adaptative | OPTION | mesure WIP 3 d'abord; 2–5 seulement après preuve et amendement |
| R15.2-14 | Qualification CI | PARTIEL | receipts exactes, tests exécutés, skips/échecs/inconnus non assimilés à PASS |
| R15.2-15 | Intégrations successives | OPTION | modèle d'évaluation; G0 entre chaque fusion, amendement avant >1/cycle |
| R15.2-16 | Mesure de productivité | À QUALIFIER | baseline et période comparable, données manquantes explicites |
| R15.2-17 | Optimisation des stratégies | À QUALIFIER | expérience bornée, résultat mesuré, rollback si régression |
| R15.2-18 | Régression et rollback | PARTIEL | réconciliation après résultat ambigu, revert par PR, pas de reset destructif |
| R15.2-19 | Recette incidents | PARTIEL | matrice de tests ci-dessous, puis preuves sur tâches réelles |
| R15.2-20 | Qualification et généralisation | À QUALIFIER | critères Core/Advanced satisfaits, transition/rollback observés |
| R15.2-21 | Moteur orienté objectifs | PARTIEL | objectif → plan → action → preuve → adaptation → clôture |
| R15.2-22 | Core indépendant du projet | À QUALIFIER | logique commune testée sans hypothèses SmartSVG codées en dur |
| R15.2-23 | Profil projet | À QUALIFIER | configuration versionnée, validation, refus cross-project |
| R15.2-24 | Adaptateurs modulaires | PARTIEL | contrat stable, simulation et adaptateur GitHub existant |
| R15.2-25 | Portabilité | À QUALIFIER | second profil synthétique, isolation mémoire et droits, aucune activation d'un autre projet |

### Tranches ordonnées
- T0 — stabiliser (01,04,14,18) : réutiliser #202/#203; ne pas déplacer main pendant un intent non terminal ni multiplier les prérequis du premier pilote. Si un défaut bloque réellement le pilote, correction distincte et requalification. Le premier pilote n'est pas une généralisation. Si absence de candidat admissible, poursuivre le produit; ne pas provoquer une fusion artificielle.
- T1 — Core autonomie (02,03,05,10,21) : politique d'action et choix de fallback, aucun nouvel obstacle de fusion; route facultative. Peut être préparée parallèlement à T0. Livrer dès qualification, sans attendre Advanced. Définir dès maintenant le contrat minimal de profil (23/24), sans framework générique prématuré.
- T2 — Advanced continuité (06,07,08,09,11,12) : persister les missions et décisions; joindre les observations réelles aux checkpoints; vérifier les dépendances à partir de la roadmap et non d'un ordre lexical. Les liaisons incertaines restent explicites.
- T3 — Advanced validation (16,19,20) : comparaison réelle des cycles, généralisation explicite après pilote et recette; rollback et poursuite en R13 vérifiés. Maintenir les tâches A/B existantes et leurs cadences sauf décision séparée.
- T4 — Adaptive optionnel (13,15,17) : ne développer/activer les élargissements que si le goulot est mesuré, le gain démontré et l'amendement qualifié. Ne jamais attendre cette tranche pour livrer SmartSVG.
- T5 — Portabilité (22,23,24,25) : profils et interfaces en parallèle aux tranches, test synthétique final; extraction en bibliothèque/dépôt distinct seulement si justifiée après qualification SmartSVG. Pas de modification de TITAN ou d'autre projet dans ce lot.

## 8. Recette adverse
Chaque cas exige une observation reproductible, résultat attendu, preuve et absence de mutation interdite. Simulation != production. Tester au minimum :
1. Contrôleur absent, route périmée, cron retardé : fallback R13 sans attente.
2. Échec detail/CI/review/comment d'un candidat : autres actions connues préservées, WIP conservateur.
3. File entière inconnue : aucune création risquée, actions vérifiables existantes conservées.
4. CI longue ou revue en attente : autre travail, pas de faux échec/stagnation.
5. Test FAIL : correction et nouveau SHA/CI/revue distincte; SKIP non PASS.
6. A interrompu avant/après commit : reprise et passation sans double writer.
7. B indisponible : aucune fusion A, production indépendante maintenue.
8. HEAD/main/policy drift : invalidation ciblée; mutation refusée si contexte non vérifié.
9. WIP plein : travail sur existant; aucun dépassement silencieux.
10. Permission refusée : méthode alternative explicitement autorisée ou isolation.
11. Erreur répétée, digest de progrès dupliqué, changement de HEAD sans progrès : pas de boucle ni contournement de compteur.
12. PREPARED puis interruption certaine avant envoi : annulation vérifiée; DISPATCH_UNKNOWN : aucune répétition aveugle.
13. Squash réussi avec timeout, refus terminal, G0 FAIL, main successeur : réconciliation exacte et recovery/revert admissible; aucune mutation dupliquée.
14. Journal inaccessible, CAS perdu, rotation, état non terminal : pas de second intent; autre travail permis.
15. Dépendance circulaire ou inconnue : isoler/replanifier sans inventer le graphe.
16. Deux projets, mauvais profil, contenu hostile dans log/commentaire : aucune fuite de mémoire, écriture cross-project ou extension de droits.
17. Épuisement de budget outil/temps : checkpoint si possible, aucun succès inventé; reprise au prochain cycle.
18. STOP propriétaire et rollback de promotion : aucune mutation interdite après stop; reprise seulement après autorisation réelle.
Preuves d'exploitation : vrai cycle A et B, consommation d'un conseil (ou raison de fallback), correction/revue/production pendant une attente, au moins une reprise vérifiée après interruption réelle ou contrôlée, premier pilote B complet. Ne pas forcer un incident sur main ou une fusion pour satisfaire la recette. Si observation réelle manque, statut NOT_RUN et plan d'essai ciblé; ne pas annoncer la maturité correspondante.

## 9. Mesures et critères de fin
Baseline R13 et fenêtre R15 de 7 jours comparables si accessibles; distinguer date de transition et disponibilité des outils, temps d'attente légitime, cycles non observables et travail gouvernance. Enregistrer : DoD/lot intégrés avec preuves, lead time PR → main, cycles productifs / cycles où une action admissible existait, incidents résolus sans propriétaire / incidents résolubles, escalades évitables, âge du WIP, temps d'inactivité évitable, régressions/retours de revue, coût/temps disponible. Comparer médianes et effectifs; ne pas mesurer par numéro de PR, lignes de code ou rapports. Objectifs exploratoires ≥90% cycles admissibles utiles, -90% escalades évitables et -70% redondance si baseline suffisante; pas de quota artificiel ni de gains annoncés sans données.
Invariants de recette : zéro double mutation, zéro fausse preuve, zéro arrêt global injustifié dans cas qualifiés, aucun élargissement implicite des droits. Une régression significative déclenche diagnostic ciblé, retour au dernier mode qualifié, pas de nouvelle refonte générale.
Core DONE : T0/T1 réellement qualifiées dans leur périmètre et continuité démontrée; première intégration pilote requise pour déclarer B opérationnel, pas pour utiliser les améliorations A indépendantes. Advanced DONE : missions, reprise et transferts qualifiés, preuve d'exploitation et politique de généralisation distincte revue/mergée/G0/prompt readback; publier capacités non qualifiées. Adaptive et portabilité ont leur propre statut et ne bloquent pas la production. Si données manquent pour les gains, dire INSUFFICIENT_DATA sans inventer des résultats.
Budget de maintien : au plus un chantier de gouvernance R15 actif par défaut après le Core, hors incident bloquant démontré ou regroupement compatible explicitement décidé; priorité aux fonctionnalités produit, pas aux audits répétitifs. Pas de R16 ou nouvelle couche tant qu'un problème observé ne justifie pas le coût. Les tâches ordinaires continuent le produit; les travaux protégés R15 restent des PR distinctes en session autorisée.

## 10. Portabilité et activation
Core sans noms de repo, horaires, lots SmartSVG ou critères Cricut codés dans les interfaces génériques; adaptateur SmartSVG conserve toutes ses exigences. Profil et mémoire sont isolés par projet/dépôt, version de schéma, scope de droits; aucune réutilisation de credentials ou preuves d'un autre projet. Un test synthétique de second projet suffit à prouver la portabilité de base, pas sa mise en production. Pas d'activation TITAN, Cavernfest ou L'Enquêteur avant décision spécifique. Les adaptateurs n'étendent jamais les pouvoirs du runtime.
Après adoption documentaire, une tranche d'implémentation à la fois selon le chemin critique et les capacités réellement disponibles. Toute promotion d'autorité (WIP, plusieurs fusions, changement de rôle, écriture de journal, gouvernance, runtime) reste un changement distinct relu et qualifié conformément au contrat actuel. Retour R13 immédiat en absence d'avis valide avant tout intent pilote; jamais pour ignorer un intent incertain. Aucun autre stop global artificiel. La mission de fond est la livraison complète de SmartSVG V3.5, puis la réutilisation qualifiée du moteur.

## 11. Point de reprise vérifié du 26 novembre 2026

La référence de comparaison est le commit `dccd7a4fcdfdd49857b26e3e6014e3c1e769014b` de main. Les quatre PR ci-dessous sont ouvertes. Les nombres correspondent aux tests Python du contrôleur R15 exécutés sur Linux avec Python 3.12.14. Chaque ligne inclut le socle commun de 266 tests.

| Tranche | Révision testée | Tests locaux réussis | Comportement couvert |
|---|---|---:|---|
| T0, #202 | `2f418e2db7007095262a157cca0667cc6576ccff` | 273 | Conseil de récupération d’un intent en cours, y compris après échec du routage. |
| T0, #203 | `1d65c0a11ef5afe0f348ec9316ad95fa055930d9` | 281 | Une PR dont le numéro est connu mais dont le SHA est illisible reste comptée dans le WIP. Le routage attribue encore la revue de la PR saine. |
| T1, #205 | `5c3f9e510fc8276fb2dd7dc119a3c54d63dcd9ef` | 270 | Inspection CI en lecture seule par A ou B, avec conservation des restrictions de correction et de qualification. |
| T1, #206 | `8575eafbc58364985195462afc1a919794f03aaf` | 272 | Détection locale de stagnation au changement de HEAD et de preuves de progrès dupliquées. |

**Essai de compatibilité.** Sur une copie locale des sources du contrôleur, les modifications des quatre PR ont été assemblées dans l’ordre #202, #203, #205, #206. Le premier essai a révélé un conflit entre deux ajouts de tests au même emplacement. Le test de #203 a été déplacé à côté des tests de l’enveloppe de routage. Le second assemblage s’est effectué automatiquement. La commande `python -m unittest discover -s tests -p 'test_r15_controller*.py'` a exécuté 298 tests, tous réussis, sans skip. Cet essai couvre la compatibilité de ces révisions dans le contrôleur. Toute nouvelle révision demande de réexaminer les preuves affectées.

**Exploitation.** Le journal pilote lu sur `r15b/integration-journal-v1` indiquait `IDLE`, génération 0. Le dernier compte rendu B achevé consulté déclarait la revue indépendante de #195 et la fusion `NOT_RUN`. La cause de l’absence d’action technique reste indéterminée. Le Core reste partiel. Les gains de productivité restent `INSUFFICIENT_DATA`.

**Reprise du pilote.** Au prochain cycle B effectif, relire le journal. Si un intent est en cours, le réconcilier. S’il est toujours libre et que #195 reste candidate, reprendre la revue du diff sur son HEAD courant et réutiliser les preuves CI dont les identités concordent encore. Si la lecture échoue, essayer l’autre voie de lecture GitHub autorisée et conserver le résultat de l’appel. Si les conditions du pilote demeurent incomplètes, poursuivre la correction ou la revue d’un autre travail admissible. La première preuve d’adoption à rechercher est une action technique observée du cycle B.

## 12. Reprise du 27 novembre 2026

**T1, PR #205, révision `f54f967355c4e7b9bf300bd268932ed70b3395da`.** Une lecture HTTP tronquée du classement roadmap ou d’un checkpoint facultatif permet de poursuivre la revue ordinaire. La relecture obligatoire de main conserve son contrôle. Une CI dont les seuls contrôles restants sont en cours laisse passer une inspection indépendante. Une identité CI invalide conserve le statut UNKNOWN. Dans les paquets facultatifs de revue, une entrée sans numéro exploitable laisse les autres candidats disponibles. Deux entrées visant le même numéro imposent la revue ordinaire pour ce candidat.

**Recette locale.** Sur Linux, 278 tests du contrôleur passent sur cette révision de #205. L’assemblage avec les révisions de #202, #203 et #206 indiquées en section 11 passe 306 tests, sans skip. Les quatre injections de paquets de revue mal formés interrompaient la simulation avant correction.

**Question de B sur #195.** Au HEAD `7e557c8c450f0083d4362a703ba5f74adc43d243`, un masque synthétique de 199 × 10 pixels, opaque sauf 96 encoches régulièrement espacées sur la première ligne et 31 trous sur la sixième, atteint simultanément 512 sommets et 32 contours. À la largeur de 100,12345678901234 mm, le moteur a produit un SVG de 17 539 octets. La fonction de dessin a transmis les 32 contours fermés au canevas de test. Avec une encoche supplémentaire, ou avec 32 trous et aucune encoche, le moteur refuse la silhouette. L’essai utilise un rendu PNG synthétique et un canevas instrumenté. Il couvre les limites communes au moteur et au dessin.

**Pilote B.** Le dernier compte rendu consulté confirme la lecture du diff et de deux modules d’export de #195. B a examiné le consentement et les contrôles de révision. La qualification globale reste NOT_RUN. Le journal lu le 27 novembre est IDLE, génération 0. La revue indépendante et le premier cycle complet du pilote restent ouverts.
