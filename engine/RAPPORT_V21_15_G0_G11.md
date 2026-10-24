# SmartSVG Studio V21.15 — Contre-expertise et état de recette

**Base logicielle protégée :** `ComfyUI_SmartSVG_Studio_V21_14_1_Installation.zip`, SHA-256 `b35ed631bcf6243bf0dd9b0af5b8e01dab1cfe38a5ef0f93e74f21a49df28835`, vérifiée le 24/10/2026.

## Résumé des preuves

| Domaine | Résultat réel | Portée |
|---|---|---|
| Archive source ZIP | SHA-256 conforme au gel V3.2 | même B0 |
| Fichiers moteurs hérités | aucun modifié, seule entrée `__init__.py` redirigée vers nouveau registre | vérification SHA |
| Test de base V21.14.1 | 132 tests Python ciblés et 50 JS avant la modification | comparaison de base |
| V21.15 tests dédiés + vectoriels | **45 Python sur 45 réussis** | conteneur Linux ; pas Windows |
| V21.15 tests frontend | **50 JS sur 50 réussis** | Node.js ; pas navigateur cible |
| Suite Python intégrale | **non terminée (limite de temps)** | ne PAS compter comme succès |
| Workflows de base | **186 JSON parsés** ; **483 occurrences de nœuds**, sans défaut statique après correction | n'est pas un chargement ComfyUI |
| Registre des nœuds | **98 IDs** (96 initialement, 2 V19.2 restaurés) | présence en Python |
| Duplications | 3 fichiers de diagnostic IA graphiquement identiques (1 groupe) | pas de suppression |
| Sources corpus T-01…T-09 | 9/9 présents, dimensions et empreintes vérifiées dans l'environnement de travail | fichiers images hors distribution |
| Vérité terrain | 2/2 masques synthétiques exacts, **9 masques humains en attente** | **G0.3 bloqué** |
| PC Windows / RTX 3070 / ComfyUI | non testé | aucune compatibilité matérielle certifiée |
| Cricut Design Space / Explore 5 | non testé physiquement | aucune sortie déclarée certifiée |

## Correctif de compatibilité identifié pendant G1.1

Deux workflows V19.2 historiques (`SmartSVG_Studio_V19_2_Express.json`, `SmartSVG_Studio_V19_2_Expert.json`) contenaient des types absents du registre chargé. Le nœud V19.2 Express comportait aussi `ia_locale` dans le workflow sauvegardé mais pas dans les ports déclarés de sa classe.

**Correction :** nouveau registre `node_v2115.py` (sans changer les 96 IDs antérieurs) et adaptateur Express avec champ `ia_locale` dans l'ordre sauvegardé, transmis au moteur. Les fichiers sources `node_v192.py` et tous les workflows restent inchangés. Aucune inférence IA n'a été exécutée pour valider cette correction.

## Vraies limites de l'audit

1. L'analyse vérifie la disponibilité des IDs, les champs requis, les types de sortie, les liens et le JSON. Elle ne peut démontrer à elle seule qu'un graphe produit une image valide.
2. Des ports optionnels historiquement absents ou dans un ordre d'affichage différent sont autorisés. Seuls les ports requis manquants et les ports inconnus sont déclarés incompatibles.
3. Le corpus humain sert uniquement à la **comparaison locale** ; les originaux ne sont pas dans l'archive publiable.
4. Le protocole G0.3 définit la méthode d'annotation et d'arbitrage, mais les masques réels restent à annoter et à vérifier indépendamment.
5. Les tests complets de non-régression, de navigateur Windows, d'IA GPU et de fabrication Cricut restent ouverts.

## GO / NO GO

- **GO — conservation du correctif V19.2 et des outils G0/G1.1 préliminaires** : preuves statiques et unitaires disponibles.
- **NO GO — bascule G0 → G1.2 / Express refondu** : attendre la vérité terrain et la revue de risques, conformément à la roadmap v3.2.
- **GO AVEC RÉSERVES — ZIP technique V21.15** : utilisable pour l'inspection des nœuds et l'inventaire ; une installation ComfyUI réelle doit confirmer les ports et les versions avant emploi courant.

## Suite ordonnée

1. Valider les masques humains T-01…T-09, avec deux évaluations indépendantes et un arbitrage consigné.
2. Exécuter les essais d'ouverture ComfyUI des workflows représentatifs et une suite Python intégrale sans interruption.
3. Fermer G0 et G1.1 au vu des preuves, puis démarrer **G1.2 contrats de données** (SourceAsset, Mask, Subject, Artifact, QAResult).

Aucune modification de l'interface Express globale n'est annoncée pour V21.15 ; ce chantier commence après les gates d'architecture.
