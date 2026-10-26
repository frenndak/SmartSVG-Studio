# SmartSVG — protocole d'intégration V1 (candidat)

**Objectif :** réduire les PR empilées sans jamais assimiler « CI verte » à « fusion admissible ». Ce texte est ajouté à la PR de sécurité #13 ; **aucune fusion ni activation en production n'est effectuée par son ajout**.

## Acteurs et étapes

1. **Producteur (:15, Europe/Paris)** — travaille sur la PR racine la plus ancienne ou corrige une régression P0/P1. Tant qu'il existe au moins quatre PR ouvertes, pas de nouvelle PR fonctionnelle. Aucune modification de `main` en direct.
2. **Auditeur indépendant (:35)** — examine le diff réel, les entrées adversariales, la compatibilité des nœuds et projets, les preuves attachées au HEAD et aux dépendances. Pour une PR purement logicielle G1/G2, les tests L1 CPU pertinents et la revue du diff suffisent *au verdict d'intégration de code* si le risque matériel n'est pas dans son périmètre. L2 (ComfyUI+GPU réel) et L3 (Cricut) restent obligatoires pour tout jalon qui affirme leurs fonctionnalités prouvées, **jamais présumés satisfaits**.
3. **Qualification en lecture seule** — exécuter le workflow manuel `SmartSVG - Read Only Integration Preflight` sur **`main`** après fusion de la PR #13, avec l'entrée `pr_number`. Il interroge GitHub en direct, puis lance `tools/integration_eligibility.py`.
4. **Approbation et intégration** — la PR doit être ouverte, non brouillon, basée directement sur `main`, sans conflit ni retard de branche, avec CI **G0 ET CPU Smoke** success sur le HEAD exact. Pour éviter de confondre un test de la référence synthétique `pull/PR/merge` avec celui du code candidat, les deux workflows doivent avoir été lancés sur la **branche candidate** via `workflow_dispatch` (et correspondre à son nom de branche et HEAD). Exiger le commentaire `SMARTSVG_AUDIT_V1` associé au HEAD avec `VERDICT=GO_POUR_REVUE_INTEGRATION`, puis une revue GitHub `APPROVED` par un autre compte utilisateur non bot et non auteur, sur ce même HEAD. Les demandes de changements ouvertes bloquent. Le workflow ne change pas le statut de brouillon, ne merge pas, n'attribue pas d'approbation et ne réécrit aucune branche.
5. **Action mainteneur** — une fois les conditions réunies, le mainteneur vérifie encore `main` et HEAD au moment de la fusion via les mécanismes GitHub de protection / comparaison SHA. La qualification seule ne vaut ni autorisation de fusion automatique ni release du produit.
6. **Après fusion** — constater le nouveau `main` et le SHA de fusion, puis traiter la PR fille (base à recalculer, réévaluation des conflits, nouveaux checks exact-head), une seule par une.

## Politique de dette

Au 26/10/2026, 16 PR brouillon : #13 (sécurité), #14→#24 (branche produit empilée avec alternatives #20/#21 et #23/#24), #25 (SVG), #26→#28 (masques/éditeur). Les numéros sont des repères historiques uniquement.

- Ne pas rendre automatiquement prêtes ni fusionner en masse les PR liées.
- Avant de fusionner des variantes parallèles, comparer le contenu et choisir une implémentation canonique ; archiver/fermer uniquement les doublons réellement remplacés après confirmation.
- Corriger les tests sur les HEAD pertinents ; une CI verte sur une PR fille ne qualifie pas ses parents.
- Prioriser la réduction de la dette et la stabilisation du graphe de dépendances plutôt que la croissance du nombre de PR.

## Contrat du précontrôle

Entrée : snapshot JSON `schema=1` (PR, compare main...HEAD, runs, reviews, audit comments, second relevé main/HEAD). Production depuis un checkout `main` avec permissions **lecture seule**. Le contrôle rejette par défaut les données absentes, brouillons, PR sur branche fille, conflits, main obsolète, HEAD changé, CI non terminée/non success, approbation périmée ou par l'auteur, absence d'audit favorable. Les runs plus récents peuvent invalider d'anciens succès.

Sortie : `BLOCKED` + raisons, ou `ELIGIBLE_FOR_MAINTAINER_MERGE_REVIEW` ; `automatic_merge_allowed=false` dans tous les cas.

**Pas de fausse preuve :** l'issue de coordination #29 est un journal non autoritaire, pas une signature de validation. Même avec un commentaire `GO_POUR_REVUE_INTEGRATION`, une approbation GitHub indépendante reste nécessaire. Comme le développeur et les tâches opèrent actuellement sur le compte `frenndak`, une revue réellement indépendante par un **autre compte humain** devra être obtenue pour franchir ce garde-fou. S'il n'est pas disponible, laisser `BLOCKED`, ne pas créer de fausse approbation ni contourner ce contrôle.

### Essai local

```bash
python -m unittest tests.test_integration_eligibility tests.test_private_agent_protected_paths -v
python tools/integration_eligibility.py /chemin/vers/snapshot.json
```

Le retour non nul indique un refus de qualification, pas une erreur de CI à masquer.

### Retour arrière

La PR #13 reste distincte et pourra être revert sans toucher aux moteurs, projets, archives ou modèles : supprimer les fichiers `tools/integration_eligibility.py`, `tests/test_integration_eligibility.py`, `.github/workflows/integration-preflight.yml`, cette documentation et restaurer la version précédente du garde-fou d'automatisation si nécessaire.

## Périmètre explicitement non couvert

Pas de tests réels Windows/ComfyUI/RTX 3070, Design Space ou Cricut Explore 5 produits par ce protocole. Pas de publication open source, pas de réglage automatique des secrets GitHub ni de facturation nouvelle. Aucune revendication de qualité de fabrication.
