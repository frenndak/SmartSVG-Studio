# P1 — Admission des appels Codex payants (portage ciblé de #13)

Le workflow existant `.github/workflows/private-ai-development.yml` peut être déclenché par l'utilisateur ou par un `repository_dispatch` lorsque `SMARTSVG_AUTOMATION_ENABLED=true`. Avant le portage, la vérification de la présence de `OPENAI_API_KEY` ne bornait ni le nombre de runs payants possibles ni l'intention de dépense.

## Contrôle ajouté

Ce lot porte **uniquement** le garde-fou budgétaire de #13, avant toute action `openai/codex-action@v1`.

- `SMARTSVG_MONTHLY_API_BUDGET_USD` : variable dépôt explicite de budget mensuel déclaré (entier positif ou deux décimales ; maximum 99999,99). **Ce n'est pas un compteur de facturation réel.**
- `SMARTSVG_MAX_PAID_RUNS_PER_DAY` : variable dépôt explicite entre 1 et 24.
- Les ré-exécutions GitHub `GITHUB_RUN_ATTEMPT > 1` sont rejetées.
- Le workflow interroge le compteur GitHub Actions de ses propres exécutions le jour UTC courant, y compris les runs sans coût. Échec API, zéro résultat ou >100 runs : refus.
- Un échec interrompt la job **avant** l'accès au secret et à l'action payante.
- La condition initiale `SMARTSVG_AUTOMATION_ENABLED=true` et l'activation manuelle `inputs.execute=true` restent en vigueur.

**Attention** : le montant mensuel est seulement une **intention**. Le plafonnement financier réel doit être configuré chez le fournisseur de l'API ; les runs GitHub ne donnent pas les coûts de tokens. L'absence des variables bloque tous les appels Codex payants, mais pas la CI gratuite ni le développement ChatGPT séparé. Aucune variable, clé ou dépense n'est créée par cette PR.

## Recette

`tests/test_paid_budget_gate_gov.py` simule localement l'API GitHub avec des bornes positives, invalides et des tentatives rejouées. Le lot ne reprend **pas** le protocole humain/diff signé périmé de #13 ni les workflows historiques décalés de centaines de commits. Le précontrôle public de la PR #42 reste complémentaire et ses tests n'exécutent aucune IA.

Le source ZIP V21.15.2 et la roadmap V3.2 restent gelés. Aucun résultat Windows/GPU/Cricut n'est prétendu.
