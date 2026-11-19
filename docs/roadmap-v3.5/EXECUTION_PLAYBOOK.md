# Exécuter la V3.5 étape par étape sans recommencer la roadmap

> **Historique R12 :** la tâche séparée de conception/contre-expertise est arrêtée à la demande du propriétaire. Suivre [l’amendement R12](PRODUCER_R12_PLUGIN_AMENDMENT_2026_11_16.md) et EXECUTION_STATE ; qualité et auto-audit intégrés au producteur, cycle de revue ultérieur obligatoire inchangé. Aucun second producteur ni réactivation automatique.

> **Conduite après adoptionV3.5 :** [EXECUTION_STATE.json](EXECUTION_STATE.json) est le curseur courant, sous autorité AGENTS/main et [décision d’adoption](../ROADMAP_PROMOTION_v3_5.md). [Producteur R11](PRODUCER_TASK_V35.md) pour l’ingénierie, [contre-expertise R4](DESIGN_REVIEW_TASK_V35.md) en lecture seule. Les consignes de préparation/promotions et anciennes prochaines actions datées restent une archive de la campagne close, pas une mission de recommencer la conception. RUN_STATE est scellé comme photographie avant adoption, avec ses champs historiques3.4. La routine de production§3/4 et les critères complets continuent à s’appliquer.

**14/11/2026 — conduite candidate ; V3.4 reste active jusqu'à promotion.** Le propriétaire a autorisé la finalisation complète puis le remplacement de V3.4. L'objectif est de produire une application Windows autonome utilisable, en livrant des tranches utiles vérifiées. Une campagne documentaire n'est pas une réalisation du produit.

## 1. Un point de reprise unique

Lire **RUN_STATE.json** puis ce document et la dernière entrée PROGRESS. `next_action` est le curseur courant ; les « prochaine action » des anciens COV/Q restent l'historique de leur rédaction, pas des consignes concurrentes. Si le curseur désigne une action finie, un document absent ou une dépendance non satisfaite, corriger la cohérence à partir des derniers commits avant d'exécuter. Ne jamais revenir à Q01/COV05 sur simple lecture d'un vieux prompt. Tous les Q04C–Q04J publiés sont des acquis à consommer, pas à recopier.

Priorité d'interprétation : instructions propriétaire actuelles et AGENTS/main ; conditions de promotion ; présent playbook + décisions transversales/ADR/contrat SD ; MASTER_PRIORISE ; fiches de domaine avec corrections explicites ; snapshots/audits historiques. Un conflit d'exigence se tranche explicitement, jamais par « le fichier le plus récent doit avoir raison ». Les sources historiques intégrales restent contraignantes sauf décision autorisée clairement documentée. Les champs source de PRIORITY_REGISTER restent des photographies ; les splits actuels sont dans DECISIONS_TRANSVERSALES D07.

## 2. Routine de conception, jusqu'à adoption

1. Lire le HEAD main avec `/branches/main` et le HEAD de la branche canonique ; lire les PR ouvertes via `/pulls?state=open` si le lot touche leurs interfaces. Un moteur de recherche de commits ne suffit pas. Conserver SHAs des sources consultées et ne relire que les consommateurs impactés/changés.
2. Prendre `next_action`. Si dépendance bloquée, noter le fait et sélectionner une action indépendante explicitement autorisée dans la file ; ne pas attendre une preuve physique pour écrire un contrat de fichier. Pas de nouveau chapitre de « possibilités » si un arbitrage suffit.
3. Réaliser le résultat concret attendu : décision, interface complète, contradiction corrigée, chaîne critère→DoD→recette, ou revue avec verdict. Une absence de code futur se transforme en tranche d'implémentation, pas en série sans fin d'audits d'absence.
4. Vérifier les fichiers et le registre. Revue indépendante du changement quand requise, avec portée et limites. Si indisponible, statut REVIEW_PENDING explicite ; ne pas fabriquer un reviewer ni remplacer son verdict par un compteur PASS.
5. Publier sur la même branche documentaire, avec **lease HEAD**. En cas d'avancée horaire concurrente, lire le delta et réappliquer sans l'écraser. Ajouter preuve et prochain état dans la même publication quand possible ; ne pas insérer le SHA du commit dans son propre contenu. La ref Git du fichier porte son SHA ; une entrée ultérieure peut citer le commit précédent.
6. Continuer un second lot cohérent si le premier est réellement clos et les outils le permettent. Arrêter sur dépendance réelle, blocage d'accès ou limite effective ; laisser un curseur exact. Les contraintes de micro-lot s'appliquent à chaque itération, pas comme obligation d'interrompre la conversation après une action.

## 3. Routine du producteur après promotion

Lire la référence adoptée sur main et le journal d'intégration produit, pas la branche candidate comme autorité implicite. D'abord intégrer/corriger le WIP réel avant de multiplier les PR : #138/#139/#140/#144 sont des repères de ce jour, **à revérifier**, pas un état permanent. Aucun ticket « fait » sans preuve du code et de son branchement dans le parcours Windows.

Choisir une tranche d'après MASTER_PRIORISE et dépendances minimales : socle V1 sûr, geste sélection/retouche réel, exports typés, Smart Delivery dès un export valide, prévol/assistant, édition/scène, texte/gabarits, séries/bibliothèque, IA facultative et extensions. Accessibilité/reprise/qualité accompagnent chaque tranche. CP0–CP2 sont les sous-lots nécessaires à la persistance de composition ; SD0–SD2 indépendants des quatre exporteurs complets ; W13 benchmark avant gros éditeur, pas avant chaque correction Tk.

Avant modification : lire les fonctions effectivement appelées, tests affectés et statut PR au SHA exact ; définir déclencheur utilisateur et résultat observable. Écrire le test qui prouve l'écart quand pertinent, faire la plus petite modification cohérente, exécuter tests touchés + contrôles requis, revoir le diff, vérifier intégration UI/CLI prévue. Ne pas écrire un nouveau moteur quand un port convient. Ne pas arrêter au module backend si le ticket promet un bouton Windows ; sinon limiter explicitement la tranche backend et garder la tranche UI dans l'état restant.

## 4. Fiche de tranche minimale obligatoire

Chaque tranche possède : `id`, capacité/valeur utilisateur, exigences sources et priorités, ticket existant/justification d'un nouveau, entrées/sorties/unités/erreurs, source d'autorité, fichiers/ports **existants** vs **proposés**, dépendances, étapes, DoD, tests (positif, ≥3 négatifs pertinents, annulation/reprise/concurrence), commandes de vérification réellement disponibles, rollback, preuve et suite. Un code « test command to define » ne doit pas être utilisé comme commande exécutée : la première tâche d'implémentation localise le runner du repo au HEAD et inscrit sa commande exacte dans le plan borné.

États de conception : DRAFT → SPECIFIED → REVIEW_PENDING → REVIEWED → ADOPTED. États produit séparés : NOT_STARTED → CODE_BRANCH → CODE_MAIN → WINDOWS_EXPOSED ; preuves par axe PASS/FAIL/SKIP/NOT_RUN, jamais un TESTED global. Les fonctions dont l'essai réel manque restent visibles avec limites, sans empêcher des contrats indépendants d'avancer.

Sortie de run : ce qui a changé et pourquoi ; SHA source/candidat ; preuve réellement obtenue ; défauts restant à résoudre ; `next_action`. Un rapport de « 437 tests » doit dire **scénarios documentés** tant que ce ne sont pas des exécutions attestées. Ne pas relancer toute la suite sans nouveau changement/échec justifiant le coût.

## 5. Finalisation et bascule contrôlée

La fin de conception exige couverture sémantique, contradictions tranchées, responsabilités non circulaires, contrats et recettes, puis revue globale indépendante. Elle n'exige pas un logiciel V3.5 fini. Les actions restantes sont finies et nommées dans RUN_STATE, non une liste infinie de COV supplémentaires.

Une fois les gates documentaires prouvés : PR documentaire consolidée depuis la branche existante, contrôle des fichiers/archives et CI exact-head, puis PR distincte de gouvernance en session autorisée. L'autorisation propriétaire de finaliser/remplacer est déjà donnée ; ne pas redemander une confirmation de principe sans nouveau choix hors périmètre ou exigence de protection réelle. Aucun agent horaire ne s'attribue le pouvoir de fusionner les docs/AGENTS.

La gouvernance doit décider explicitement la cible du producteur et la portée de fusion : `AUTONOMOUS_MERGE_V34=ENABLED` n'est pas un opt-in V3.5 par renommage. Préserver un merge maximum/cycle, cycle indépendant de revue, tests au HEAD exact et post-merge ; V3.5 DRAFT-only par défaut jusqu'au transfert explicite des règles. Ne pas modifier `.automation`/`.github` dans la PR docs.

Après vérification de l'autorité main, adapter **la tâche de développement existante**, sans en créer une autre ni supprimer la tâche de conception par défaut. Enregistrer ancien/nouveau prompt et références adoptées. Retour arrière : PR de référence V3.4 préservant code/historique, prompt cohérent avec main, ne pas écraser des projets V2 avec un writer V1. La task de conception peut alors devenir revue d'amélioration seulement après décision explicite, pas un second producteur concurrent.

## 6. Vérification documentaire reproductible

Depuis un checkout complet contenant la candidate et les sources main correspondantes :

```bash
python docs/roadmap-v3.5/verify_priority_register.py --pinned --main-root .
python docs/roadmap-v3.5/verify_run_state.py
```

Le premier vérifie l'intégrité des inventaires/provenance, le second le curseur, dépendances et preuves documentaires. **Aucun ne certifie le sens de toutes les exigences ni le fonctionnement produit.** Revoir les sources épinglées seulement quand leur contenu change ; si main diverge, requalifier les ports impactés sans reconduire un vieux SHA comme HEAD courant.

## 7. Retrouver un critère complet avant le prochain micro-lot

Le registre SOURCE_TRANSFER_REGISTER.json indexe les141critères et les140DoD avec sources littérales et précisions, sans remplacer les clauses parentes. Après validation de l'intégrité :

```bash
python docs/roadmap-v3.5/verify_source_transfer.py --main-root . --id S-036
python docs/roadmap-v3.5/verify_source_transfer.py --main-root . --id V34-033
```

Lire l'entrée ciblée, les tickets liés, le contexte parent et la fiche candidate. Les liens historiques sont des renvois de planification, pas des propriétaires exclusifs. Les acteurs W10/W11/W16 sont distincts des gates CP4/CP6. Le SHA main du JSON est une observation datée ; vérifier HEAD réel avant d'en déduire la fraîcheur du code.

Pour terminer SOURCE_CLOSURE, consommer SC-03B et REVIEW_SOURCE_TRANSFER_2026_11_15 : tableaux individuels transférés, erreurs d'oracles corrigées et limites de relecture déclarées. Il reste l'acceptation au contexte complet et les contradictions réellement restantes, pas une nouvelle série de dix intitulés ou de compteurs. Les tests de produit continuent à dépendre de leurs preuves propres après implémentation.


## Mode R13 — production parallèle conditionnelle

Après fusion de gouvernance, CI main PASS et read-back des deux prompts, charger [le contrat R13](DUAL_PRODUCER_R13_CONTRACT.md) en complément de tout R12. Le producteur A H:55 et le producteur B H:25 choisissent chacun un lot libre et utile, sans écriture concurrente sur la même branche; B est prioritaire pour contre-revue, réparation et fusion conditionnelle. Les mentions R12 de producteur unique ci-dessus sont **historiques** et cessent de s'appliquer seulement après activation R13; aucune ancienne création de roadmap n'est réactivée. Le prochain travail se déduit du WIP actuel (pas des snapshots historiques), maximum trois PR code ouvertes. Seul B peut fusionner, maximum une par cycle B, après revue différée et exact-HEAD CI, puis G0 push post-merge PASS; aucun signal inconnu n'est un PASS.
