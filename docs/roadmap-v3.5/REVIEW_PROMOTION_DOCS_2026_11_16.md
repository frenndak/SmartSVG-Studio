# Contre-revue indépendante — intégration documentaire V3.5, 16 novembre 2026

**Verdict documentaire : favorable sur le delta local borné. Critical : 0 ; Important : 0 ; Minor ouvert : 0.** La publication puis la fusion restent conditionnées aux preuves GitHub du HEAD exact, à la concordance du diff distant, aux protections applicables et au G0 post-merge. Ce rapport ne marque aucun de ces événements comme réalisé. Aucune revue GitHub `APPROVED` n'est revendiquée.

## Cible et preuve de provenance

Revue indépendante du delta de sept fichiers préparé après la conception `9c936f763fafe2885674135b9c3dd6ab33dca25b`, pour intégration contre main observé `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`. Cible : [décision et séquence](INTEGRATION_SESSION_2026_11_16.md), bandeaux README/MASTER/PROMOTION_CHECKLIST, continuation et entrées de RUN_STATE, dernière entrée PROGRESS et `tests/test_v35_roadmap_integrity.py`.

Le checkout local ne contient pas de métadonnées Git : ce rapport atteste des fichiers et des manifestes, pas d'un futur SHA de commit ni d'une lecture fraîche des règles GitHub. Vérifications directes par cette revue :

- Les sept SHA256 correspondent exactement au snapshot de revue fourni.
- Les cinq bases locales de documents modifiés correspondent chacune au Git blob SHA du manifeste des141fichiers de conception. Leurs diffs complets ont été lus : trois bandeaux ajoutés, une continuation RUN raccourcie et ses deux entrées ajoutées, une entrée PROGRESS ajoutée ; aucun autre contenu changé dans ces cinq fichiers.
- Sur les141blobs du manifeste de conception,136sont inchangés et les cinq écarts sont précisément les documents du delta. Les deux autres fichiers du delta sont nouveaux.
- Les931blobs du snapshot main sont tous présents et identiques dans le checkout. Aucun code produit, fichier de workflow, politique, archive historique ou assertion existante n'a changé. `AGENTS.md` reste au blob `9e7d417ab902bc530308d3fa97c372e162ef9069`, la politique V34 au blob `dd7784b17d44814dbf657b52f652980c4d494f49`.

Les revues globales et des compléments SCN/CST/UXI restent attachées à leurs photographies propres ; elles ne sont pas réétiquetées comme revue intégrale d'un nouveau commit. Les136blobs inchangés permettent de conserver ces acquis, sans recommencer les audits141/140/437/80. La conservation distante des quatre alias historiques et le deuxième parent main sont à contrôler au tree/commit publié : aucune structure Git non disponible localement n'est présentée ici comme déjà vérifiée.

## Décision WIP et autorité

**Exception recevable et suffisamment bornée pour cette session propriétaire.** Le playbook §5 consigne déjà l'autorisation propriétaire de finaliser puis remplacer V3.4, avec PR documentaire puis gouvernance distincte. La nouvelle fiche explicite le seul écart à la consigne WIP précédente : une PR de maintenance documentaire en session propriétaire malgré quatre PR code DRAFT, puis sa gouvernance séquentielle. Elle ne généralise pas cette conduite aux exécutions horaires, ne lance aucun nouveau producteur et n'ouvre aucun micro-lot de code produit. Les quatre PR code ne sont ni closes ni fusionnées pour maquiller la saturation ; leur réconciliation reste requise avant nouveau code.

La règle horaire antérieure est conservée comme telle, et non effacée silencieusement. Le bandeau daté, RUN et l'entrée de journal dirigent vers la décision explicite ; l'ordre d'interprétation du playbook donne priorité aux instructions propriétaire actuelles. L'exception ne contourne aucune interdiction de fusion horaire des docs : la politique V34 continue à exclure `docs/**` de son opt-in code-only. AGENTS, READY et les protections restent inchangés. Une erreur d'accès ou une protection non satisfaite impose l'arrêt de la fusion.

Le séquencement reste cohérent : **G35-12 PENDING** jusqu'à intégration documentaire et contrôle main ; **G35-13 PENDING** jusqu'à gouvernance séparée vérifiée ; **G35-14 PENDING** jusqu'à passation effective et relue des tâches existantes. V3.4 reste active jusque-là. L'opt-in V34 ne devient pas un droit V35 par renommage ; la future gouvernance doit décider explicitement la politique, le marqueur et la cible, et conserver DRAFT-only en cas de contradiction. Aucun nouvel accord de principe n'est requis pour le seul choix de conduite déjà autorisé ; les contrôles concrets demeurent obligatoires.

## Contrôle ajouté et adéquation de la preuve

Le nouveau module unittest est découvert par le runner G0 existant (`python -m unittest discover -s tests -p 'test_*.py' -v`), lequel vérifie le checkout du HEAD exact. Aucun workflow n'est modifié.

| Exigence ou risque | Observation directe | Résultat |
|---|---|---|
| Critères/DoD et provenance conservés | Sous-processus réel `verify_source_transfer.py --main-root ROOT`, avec ROOT calculé depuis le fichier du test | Couverture adaptée à l'intégrité littérale ; pas de qualification sémantique inventée |
| Inventaires épinglés et ports du checkout | Sous-processus réel `verify_priority_register.py --pinned --main-root ROOT` | Les pins et ports sont comparés aux fichiers effectifs, sans mock |
| Curseur, dépendances et preuves | Sous-processus réel `verify_run_state.py` | Code de retour non nul fait échouer le test ; timeout/erreur ne sont pas transformés en succès |
| Destinations Markdown locales | Résolution effective des liens du dossier canonique, confinement au dépôt, existence du fichier | Contrôle proportionné ; fragments, URL externes et syntaxe Markdown non prise en charge ne sont pas certifiés |
| Assertions et source historiques | Trois contrôleurs et anciens tests identiques ; aucun retrait ou affaiblissement dans le delta | Aucune réduction constatée |

Les tests ne recopient pas un verdict de rapport : ils exécutent les trois contrôleurs réels à chaque checkout et capturent stdout/stderr en cas d'échec. Leur valeur est documentaire. Le succès ne prouve pas à lui seul l'exécution CI distante, une revue de protection, le sens de toutes les clauses ni le fonctionnement du produit.

## Exécution indépendante et limites

Le rapport est créé avant le test pour que ses destinations soient présentes lors du parcours des liens. Commande ciblée exécutée : `python -m unittest discover -s tests -p 'test_v35_roadmap_integrity.py' -v`.

**Résultat ciblé frais : PASS — 4 tests exécutés, 0 échec, 0 erreur, 0 SKIP, exit0, en0,304s.** Les trois sous-processus de contrôle et le parcours des destinations locales ont effectivement été exécutés par cette commande. Aucun des sept fichiers revus n'a été modifié après leur snapshot. La présente mise à jour du seul rapport ajoute le résultat observé, sans nouvelle destination de lien.

Le contrôle distant du diff complet, la fraîcheur de main, le maintien des quatre alias, la mergeabilité, les checks CI réellement exécutés sur le HEAD publié et le G0 du main post-merge restent à la charge de l'intégration. Aucun push, PR, merge, changement de gouvernance ou outil externe n'est effectué par cette revue. Produit, UI Windows, GPU, Design Space, coupe et montage : **NOT_RUN**.


## Complément final — contexte R10.1, même session

Le coordinateur a ajouté uniquement le paragraphe « Contexte propriétaire déjà en vigueur » à INTEGRATION_SESSION. Son SHA256 final vérifié directement est `077984c455c6078345c1970c81c187d533748a45eed756340390a03679af9dfd`. Les six autres fichiers revus conservent exactement leur SHA256 initial ; les sept empreintes du snapshot final ont été vérifiées.

Le complément a été relu : il explicite la distinction déjà demandée entre WIP PRODUIT (PR code ouvertes) et WIP TOTAL, et le traitement d'une PR protégée CI/docs hors de l'emplacement produit. Il conserve expressément la restriction des passages horaires de conception, l'absence de droit de fusion docs/gouvernance et le traitement préalable des quatre PR code avant nouveau code. Il renforce donc le bornage de la voie en session propriétaire, sans extension d'autorité. La provenance du prompt R10.1 et son extrait ont été communiqués par le coordinateur après sa lecture de la tâche existante ; cette revue locale ne prétend pas avoir elle-même relu le service de tâches distant.

**Verdict final documentaire maintenu favorable : 0 Critical, 0 Important, 0 Minor ouvert.** Le seul paragraphe ajouté ne crée aucun lien ni changement de contrôleur, test ou registre : les quatre tests PASS réellement exécutés au passage initial restent une preuve de cette exécution, sans être réétiquetés comme un nouveau run. Aucun besoin de les répéter pour ce delta de prose sans destination nouvelle. Les contrôles CI/API au HEAD publié et post-merge restent intégralement requis ; G35-12..14 ne sont pas déclarés PASS et V3.4 reste active. Aucun résultat produit nouveau.
