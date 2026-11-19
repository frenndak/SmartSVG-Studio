# Proposition R13 — SmartSVG V3.5 Dual Producer (NON ACTIVE)

Statut: **PROPOSITION DOCUMENTAIRE / DRAFT / NO_MERGE**. Décision propriétaire du 19 novembre 2026: carte blanche pour préparer l'architecture à deux agents, sous réserve des autorités effectives de main. Ce fichier n'accorde aucune permission et ne remplace pas AGENTS.md, .automation/READY, AUTONOMOUS_INTEGRATION_POLICY_V35.md, PRODUCER_TASK_V35.md ni EXECUTION_STATE.json.

## But et invariants
Accélérer les **capacités utilisateur réellement intégrées** dans main, sans réduire les 141 exigences, 140 DoD, 24 lots, 80 UX, 437 scénarios, contrats SCN/CST/UXI/SD, un writer pour les données projet, sources float32 et quatre sorties distinctes. V3.4 reste DISABLED, V3.5 ENABLED. Pas de validation Windows/GPU/Design Space/Cricut inventée, d'IA/téléchargement implicite, de dépendance, secret, packaging, publication ou modification des contrôles sans autorisation séparée.

## Rôles et autonomie
- **A**: tâche horaire existante SmartSVG V3.5 R12, priorité développement de micro-lots et corrections. Identité et cadence conservées.
- **B**: nouvelle tâche horaire, décalée de 30 minutes, priorité revue indépendante, tests, résolution des blocages, intégration; peut aussi produire un micro-lot indépendant.
- Capacités de code/tests/PR/revue équivalentes, mais attribution exclusive des branches et travaux actifs. Les permissions de fusion ne deviennent effectives qu'après promotion de la politique et vérification de l'identité GitHub, de la capacité de fusion et de la sérialisation.
- Ancienne tâche de conception désactivée, non réactivée.

## Plan de migration — étapes obligatoires
1. Relever au SHA exact de main AGENTS, READY, promotion, politique V35, EXECUTION_STATE et contrat R12 intégral. Relever les PR ouvertes et les tâches actives; aucun ancien curseur candidat ne fait autorité.
2. Faire revoir et approuver séparément cette proposition, puis préparer une **PR de gouvernance distincte** mettant à jour de façon cohérente AGENTS.md, .automation/READY si nécessaire, politique V35, contrat(s) producteur(s), promotion et EXECUTION_STATE. Les changements de gouvernance ne sont jamais auto-fusionnés par les tâches.
3. Définir l'activation atomique: avant vérification post-merge de la gouvernance et de ses CI, A demeure seul producteur autorisé et B n'est pas activée. Après, créer B et contrôler son prompt, son état et son horaire; ne pas changer A silencieusement. Prévoir retour à un producteur si désaccord.
4. Une éventuelle file de fusion GitHub Actions exige sa propre revue de workflow/permissions/protection; ne pas la supposer disponible ni l'installer implicitement. Tant qu'une exclusion mutuelle fiable n'est pas démontrée, **une seule tâche explicitement désignée** possède l'autorité effective de fusion; l'autre peut préparer/revoir mais pas fusionner. Un simple commentaire, label ou timestamp n'est pas un verrou atomique.

## Attribution, progrès et WIP
- GitHub canonique. Attribuer un identifiant de lot, un propriétaire A/B, branche, base SHA, HEAD, dépendances, horodatage de lease, critères et prochaine action; reprendre seulement après relecture et vérification d'absence de writer actif. Ne jamais écraser une branche concurrente.
- WIP code global <=3 au départ, micro-lot + correctif lié par itération, pas de cinquième lot pour masquer une PR bloquée. Ne pas créer de nouvelle PR si le plafond est atteint; corriger ou qualifier l'existant.
- Si aucune PR admissible, B peut travailler sur un lot indépendant explicitement libre. Prioriser les blocages critiques, PR qualifiables et chemin critique, plutôt que des audits génériques répétés.
- Les deux tâches publient un checkpoint durable: main SHA, lot, PR/HEAD, tests PASS/FAIL/SKIP/NOT_RUN, anomalies, rôle, next_action; pas de prétention de travail entre cycles.

## Revue et fusion
- Production et revue adversariale **dans des cycles distincts** sur le diff complet, HEAD exact et main courant. Une modification substantielle par B impose une nouvelle revue différée par A ou une validation réellement indépendante; ne pas inventer de review GitHub APPROVED (même compte GitHub != reviewer indépendant).
- Les règles de périmètre code-only V35 restent applicables: aucun merge autonome docs, AGENTS, READY, workflows, politiques, deps, packaging, formats, secrets, intégrité/admission ou publication. DRAFT initial, GitHub protections et exigences de review prévalent.
- Avant squash: vérification du HEAD attendu, base/main, auteur, mergeability, discussions bloquantes, CI completed/success sur HEAD exact, tests pertinents non-SKIP, CPU et Windows si applicables; absence de P0/P1. Jamais de bypass.
- Maximum **une fusion par cycle global de coordination** initialement; sérialisation vérifiable et expected_head_sha. Sans preuve de verrou effectif: autorité unique B ou A, jamais les deux. Après fusion, vérifier main SHA et G0 push exact completed/success avant toute autre fusion. Échec/pending => gel et diagnostic, sans rollback aveugle.

## Outillage
GitHub en premier. Context7 seulement pour API/version officielle pertinente; Superpowers si effectivement disponible pour méthode TDD/débogage. Graphify uniquement si index SmartSVG et snapshot prouvés; Linear/Figma/GitBook uniquement si espace SmartSVG pertinent vérifié. Aucun plugin, service, installation ou API payante ne constitue un prérequis au micro-lot CPU.

## Mesure de performance (essai 7 jours après activation)
Comparer à une base pré-activation les exigences/DoD effectivement intégrés, temps PR->main, anomalies P0/P1 introduites, nombre de retours de revue, attente CI, temps de blocage et WIP. Aucun gain chiffré anticipé sans mesure. Si régressions ou goulot d'intégration, revenir à un seul producteur par modification de gouvernance vérifiée, sans effacer branches/commits.

## État à la rédaction
Autorités R12 actuelles explicitement **un seul producteur**, et interdisent à la tâche horaire de modifier AGENTS/.automation/.github/politique. Cette proposition est donc une **étape documentaire préparatoire**, non une activation R13. PR de code #174 ouverte DRAFT au dernier relevé; re-vérifier HEAD/CI et blocage de concurrence avant toute intégration. Aucun test logiciel, matériel ou CI n'est revendiqué par ce document.

## Contre-expertise de faisabilité — observations du 19 novembre 2026
- GitHub confirme les droits du compte connecté sur le dépôt (admin/push), **mais cela ne prouve pas** que les branch protections, required reviews ou checks autorisent une fusion automatique. Ne pas déduire les règles de protection des permissions du compte.
- Automations: quatre tâches actives au relevé (SmartSVG R12 + trois TITAN), onze en pause. L'ancienne tâche SmartSVG de conception n'a pas été réactivée. La création de B doit respecter le plafond réel des tâches et l'exécution horaire minimale; ne pas sacrifier un service TITAN ni créer un autre producteur de roadmap.
- Main observé au moment de l'ouverture de #175: `10b25a9e03fc51b88744125902e92837e59f89fc`; proposition #175 HEAD initial `c6a03d41bf8fa5ed0f5d2578b7869236adccf85a`. La PR de code #174 est **toujours DRAFT** et son HEAD a progressé à `e2a1d43ae742c165ce3d7a22fe702891d38a620e` : les anciennes revues de `081208c` ne valent pas qualification de ce HEAD. La correction de concurrence et les CI doivent être réévaluées indépendamment avant fusion.
- `EXECUTION_STATE.json` R12 contient des empreintes SHA256 du contrat et du bootstrap. Toute promotion R13 doit recalculer et vérifier les digests des **textes réellement déployés**, puis lire la tâche A et la tâche B après modification; ne jamais inventer ces preuves ni éditer l'état normatif depuis une tâche code-only.
- `AGENTS.md`, `.automation/READY`, la politique V35 et le playbook R12 interdisent explicitement un second producteur en l'état. Le présent document ne saurait rendre B active par lui-même.

## Critères d'acceptation R13 avant bascule
1. Une PR documentaire de proposition (#175) relue, puis **une PR de gouvernance distincte** comprenant les amendements complets et cohérents; revue des exclusions et contrôle de tous les fichiers modifiés.
2. Les contrats définissent clairement la tâche de coordination et le verrou de fusion. Option minimale sûre : **un seul merge executor** désigné, l'autre agent pouvant faire toutes les tâches de production et de revue, sans merger. Option double merge executor seulement après implémentation d'une file atomique et preuve de non-chevauchement.
3. Un identifiant de cycle global non ambigu: une fenêtre de coordination commune (par exemple de H:25 à H+1:25), avec au plus une fusion dans cette fenêtre; une nouvelle fenêtre ne peut pas intégrer si le G0 post-merge de la précédente est absent ou échoué.
4. Attribution des lots avec lease vérifiable; toute mutation de branche doit utiliser un état fraîchement relu et échouer en cas de divergence. La limite WIP code <=3 est **globale**; les PR de gouvernance restent séparées.
5. Tests d'acceptation de la coordination: (a) deux agents revendiquent le même lot; (b) HEAD modifié après revue; (c) main avance entre qualification et fusion; (d) G0 post-merge échoue; (e) tâche B absente/désactivée; (f) GitHub exige un reviewer externe; (g) trois PR code déjà ouvertes; (h) tâche A interrompue après commit. Chaque cas doit avoir un résultat sûr et un point de reprise.
6. G0/prévol et tests pertinents sur HEAD exact de gouvernance, puis squash **manuel/autorisé** de cette PR, puis G0 post-merge PASS. Aucune auto-fusion documentaire.
7. Mise à jour de la tâche A après promotion, création de B ensuite seulement; vérification par lecture des prompts, horaires, activation, permissions et digest du contrat. Si une étape échoue, B reste désactivée et A conserve le mode R12 ou DRAFT-only selon l'autorité effective.

## Risques résiduels explicitement non résolus
La présence d'une GitHub Action de file atomique, les règles de protection exactes, le coût/quotas de la tâche supplémentaire et la disponibilité de vrais environnements Windows/GPU/Design Space n'ont pas été démontrés. Aucun statut de test de coordination n'est revendiqué. **Ne pas déclarer R13 ACTIVE avant ces preuves.**
