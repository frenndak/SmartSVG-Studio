# SmartSVG — guide des mécanismes de développement

**Référence corrigée le 6 novembre 2026, Europe/Paris.** Dépôt `frenndak/SmartSVG-Studio` public intentionnellement. Autorité : [AGENTS.md courant](../AGENTS.md), [roadmap V3.4](roadmap-v3.4/README.md), [état et prochaine action](roadmap-v3.4/EXECUTION_ET_INTEGRATION_2026_11_06.md). Les 141 exigences V3.3 restent exigibles. La V3.2 et l'archive V21.15.2 sont des références historiques protégées ; leur hash ne détermine pas l'ordre actuel de développement.

La présence de fichiers de workflow ou de `.automation/READY` ne démontre pas qu'un mécanisme est activé, configuré ou en cours d'exécution. Le marqueur consigne admission et autorisation conditionnelle, pas une qualification du produit ou une preuve d'activité.

## Deux mécanismes distincts

| Mécanisme | Source de comportement / activation | Périmètre et fusion |
| --- | --- | --- |
| **Worker GitHub historique** `private-ai-development.yml` | [Workflow réel](../.github/workflows/private-ai-development.yml), appel manuel ou événement `repository_dispatch` ; variables, secret et budgets requis pour l'étape payante | Produit/répare une PR `smartsvg/auto-*` initialement DRAFT, WIP=1. **Ce worker ne fusionne pas** ; son prompt conserve l'interdiction de pousser/fusionner/publier lui-même. Les étapes contrôlées du workflow assurent les opérations Git/PR |
| **Tâche ChatGPT d'ingénierie V3.4** | Configuration effective du planificateur à relire séparément ; [AGENTS.md](../AGENTS.md), `.automation/READY` et [politique d'intégration](AUTONOMOUS_INTEGRATION_POLICY_V34.md) doivent concorder | Fusion de code seulement si l'opt-in courant et l'ensemble des conditions sont satisfaits : cycle ultérieur de revue indépendante, tests/CI au HEAD exact, `expected_head_sha`, au plus une fusion par cycle, puis CI post-fusion. Sinon DRAFT-only |
| **Session interactive propriétaire** | Instruction explicite du propriétaire et contrat courant du dépôt | Modifications bornées autorisées, y compris maintenance dédiée ; revue/contrôles et protections restent applicables. Aucune autorisation nouvelle n'est créée par ce guide |

Ne pas appliquer au worker GitHub l'autorisation conditionnelle de la tâche ChatGPT. Ne pas présenter la règle « aucun merge » du worker comme une interdiction universelle contredisant la politique courante.

## Activité et anciennes cadences

Les anciennes références HH:05/HH:50 UTC pour un dispatch externe et HH:35 Europe/Paris pour un audit GPT appartiennent au dispositif historique ; **elles ne décrivent pas un échéancier courant vérifié**. La configuration du planificateur et celle d'un éventuel orchestrateur externe doivent être consultées avant toute affirmation d'activité. Ce guide ne crée, ne relance ni ne modifie de tâche.

Dans l'audit du 6 novembre, le worker historique n'apparaissait dans aucune des 100 dernières exécutions Actions de ce dépôt consultées. Cette fenêtre bornée ne prouve ni sa désactivation ni l'état de la tâche ChatGPT. Les secrets/variables ne sont pas réputés configurés par la seule présence du YAML.

## Contrôles sans appel payant

Le worker expose `workflow_dispatch` avec `execute=false` par défaut : admission de source, marqueur et intégrité sont vérifiés, sans invocation Codex. Lancer même ce contrôle reste une action explicite, pas une étape exécutée par la lecture du présent guide.

Les workflows G0 et prévol public contrôlent la révision candidate ; leur hash V3.2 reste un **contrôle d'intégrité historique**, non une sélection de roadmap active. Une modification de ce hash ou de ces garde-fous n'est pas nécessaire pour suivre V3.4.

## Cycle du worker GitHub

1. Lire l'autorité et le point de reprise V3.4 actuels, les PR, le code et le ticket existant avant de choisir un micro-lot. Conserver archives, IDs/ports ComfyUI et les quatre contrats de sortie.
2. Contrôler admission, source et file des seules PR `smartsvg/auto-*`. WIP=1 sur ces branches ; les PR humaines ne sont pas des cibles de réparation et ne bloquent pas ce filtre.
3. L'étape d'ingénierie payante reste soumise à ses conditions d'activation, budget déclaré et plafond quotidien. Une instruction de roadmap n'autorise pas à contourner ces conditions ou à modifier les secrets.
4. La réparation exige un label de revue sur la PR autonome et le consomme avant l'appel : au plus une tentative par demande. Une nouvelle tentative nécessite une nouvelle demande justifiée ; aucun retry payant implicite.
5. Les étapes Git/PR du workflow publient la proposition DRAFT et dispatchent G0/CPU sur la branche candidate selon leur logique actuelle. Un dispatch accepté n'est pas une réussite de test.
6. Lire les résultats réellement terminés sur le **HEAD exact** ; analyser les skips par axe. Ne pas substituer une réussite ancienne, absente ou d'un autre SHA aux contrôles requis. Ce worker laisse la PR candidate, sans fusion automatique.

## Configuration et coûts

Les conditions effectives sont dans le workflow : variable `SMARTSVG_AUTOMATION_ENABLED`, secret API, budget mensuel explicite, plafond de runs quotidiens et refus des tentatives répétées non admises. La valeur déclarée dans GitHub ne prouve pas un plafond de facturation réellement appliqué chez le fournisseur. Ne pas renseigner de clé dans un document, log ou message.

Un ancien orchestrateur externe peut avoir ses propres variables et jeton de dispatch. Sa présence, ses droits et son activité ne sont pas certifiés ici. La correction des références documentaires et du prompt n'active aucun compte, dispatch, appel API, budget ou fusion.

## Preuves et incidents

- Tests automatiques : conserver commandes, environnement, SHA et run ID ; les skips ne sont pas des réussites des scénarios ignorés.
- Interface native : la preuve Tk Windows bornée de #119 ne qualifie pas l'installation, le DPI élevé ou l'accessibilité complète.
- ComfyUI/GPU, Design Space et fabrication physique : preuves indépendantes, jamais déduites de CI ou de présence d'un modèle.
- En incident, identifier d'abord le mécanisme concerné et ses journaux ; une éventuelle suspension de tâche/activation doit viser ce mécanisme avec l'autorisation applicable. Ne pas changer arbitrairement les paramètres d'un ancien dépôt.

Les gardes, permissions, budgets, déclencheurs et interdictions du workflow demeurent ceux du code relu. La modification du 6 novembre porte sur ses **instructions de reprise uniquement**, en session propriétaire autorisée ; elle ne transfère aucun privilège d'un mécanisme à l'autre.
