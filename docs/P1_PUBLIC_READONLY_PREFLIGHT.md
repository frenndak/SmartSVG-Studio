# Précontrôle public SmartSVG en lecture seule — réconciliation P1 (27/10/2026)

## Pourquoi ne pas fusionner la PR #30 telle quelle ?

La PR #30 était basée sur une ancienne version de main (~260 commits de retard au moment du contrôle), modifiait **AGENTS.md** et program­mait deux déclenchements GitHub Actions supplémentaires chaque heure. L'automatisation ChatGPT SmartSVG existe déjà à cadence horaire : une nouvelle routine GitHub qui **ne fait qu'exécuter des tests** aurait augmenté le bruit et les consommations GitHub sans livrer de fonctionnalité.

## Contrat de cette micro-PR de remplacement

Le fichier `.github/workflows/public-readonly-preflight.yml` est volontairement limité à :

- **pull_request** sur moteurs/outils/tests et références sensibles ;
- **workflow_dispatch** pour relancer manuellement une qualification gratuite ;
- `permissions: contents: read` uniquement ; `persist-credentials: false` ;
- checkout de **HEAD exact** de la PR et assertion runtime de la révision ;
- vérification SHA-256 de la roadmap V3.2, ZIP originel V21.15.2 + empreintes internes, `.automation/READY` ;
- tests `python -m unittest discover` et compilation des modules ;
- pas de schedule/cron, pas d'appel payant, de dispatch vers dépôt privé ni d'auto-merge.

Cela est **complémentaire**, non substitutif, aux workflows G0 et CPU qui continuent à tester la fusion synthétique de GitHub (`pull/N/merge`). Les deux preuves sont utiles : le vrai HEAD d'une PR et son intégration sur la base actuelle.

Les tests `tests/test_public_readonly_preflight.py` reprennent la matrice de sécurité de #30, mais interdisent désormais une création de schedule (et détectent l'absence de déclencheur manuel, les permissions write ou un mauvais checkout).

## Limites et décisions

- **Aucune nouvelle tâche autonome.** Le workflow informe sans modifier le code ni fusionner.
- Le correctif de description du dépôt public dans `AGENTS.md` sera traité séparément sous maîtrise du mainteneur ; ce fichier est protégé et n'est pas modifié dans ce lot.
- Les documents historiques de la PR #30 (ADR, reprise canonique) restent sur sa branche d'origine ; ils décrivent un état révolu (avant fusion de #38 et #39) et ne sont pas copiés aveuglément.
- Tests Linux/CI seulement : aucune preuve d'environnement Windows, GPU ou découpe Cricut.

## GO / NO-GO

GO pour intégration technique seulement si : les nouveaux tests statiques passent, G0 + CPU sur la nouvelle base passent, aucun nouveau secret ou permission écriture, absence de cron confirmée. Le workflow actif devra ensuite être constaté via une exécution `pull_request` ou `workflow_dispatch` sur `main` ; une CI verte avant merge n'est pas la preuve que la planification existe réellement.
