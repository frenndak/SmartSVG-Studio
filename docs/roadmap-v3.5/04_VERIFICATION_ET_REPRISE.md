# Vérification documentaire et reprise

**Date : 13 novembre 2026, Europe/Paris.** Base lue : `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`. Cette vérification porte sur la proposition V3.5 ; elle ne déclare aucune fonction de l'application terminée.

## Résultats locaux obtenus

| Commande | Résultat | Portée |
|---|---|---|
| `python tools/verify_roadmap_v35.py --pinned` | Exit 0 | 141 exigences, 140 tickets, 15 tranches ; relations, fichiers, critères, DAG et blobs des sources lus |
| `python -m unittest discover -s tests -p 'test_v3*_roadmap_integrity.py' -v` | Exit 0, 11 tests réussis | 4 tests documentaires V3.4 conservés et 7 nouveaux tests d'intégrité V3.5 |

Les tests négatifs modifient une copie en mémoire du plan : ID manquant/dupliqué/inconnu, suppression d'un lien dans chacun des deux sens, cycle ou dépendance inconnue, promotion d'autorité ou faux PASS, disparition d'une exigence sans ticket V34, critère perdu, mauvaise source et double affectation d'un ticket. Les documents sources ne sont jamais modifiés par ces tests.

Une première exécution a exposé une erreur de sélection de section dans le nouveau contrôleur (regex trop large) : corrigée avant les résultats ci-dessus. Le premier contrôle V3.4 dans la copie partielle signalait un fichier de lien non récupéré ; les deux documents liés manquants ont été récupérés au même SHA puis les 11 tests ont été exécutés à nouveau avec succès. Aucune assertion historique n'a été réduite.

## Auto-revue du lot

- Chaque ticket V34 conserve son ID, son lot source, les exigences et recettes de la matrice héritée ; son affectation V35 n'est pas une réécriture de ses critères.
- Les dix exigences sans ticket V34 ont un chemin explicite dans V35-12 ; texte, polices, glyphes et dioramas ne disparaissent pas.
- Les 15 tranches ont des critères positifs et des cas de récupération ; le micro-lot initial distingue disponibilité, mutation et parcours persistant.
- Les états lus dans le code sont distingués des propositions et des recettes non exécutées ; aucune preuve CPU/Windows/GPU/Design Space/physique produite ici.
- Aucun fichier existant n'est modifié par ce lot ; les nouveaux fichiers concernent le dossier V3.5 et son contrôle documentaire. AGENTS, archives, automatisations, workflows et moteurs restent hors du diff proposé.
- Auto-revue effectuée dans la même session ; **aucune contre-expertise indépendante ni approbation GitHub inventée**. La revue et les checks de la future PR restent distincts de ces résultats locaux.

## Point de reprise

Relire main, le statut et le diff de la proposition V3.5 ainsi que les PR #138–140. Si les sources de planification ont changé, comparer avant de régénérer le backlog ; un échec de `--pinned` signale une différence avec la photographie initiale, pas automatiquement une régression produit.

Le prochain incrément de code est décrit dans [03_PROCHAIN_MICROLOT.md](03_PROCHAIN_MICROLOT.md). Réutiliser l'historique G3.3e ; ne pas créer un moteur de journal concurrent. Reprendre le développement sous les règles de la roadmap active tant qu'une promotion explicite V3.5 n'est pas intégrée.

Après ce premier parcours, raccorder l'export PNG natif (V35-05A) avec dossier choisi, prévol, écriture protégée, relecture et retour UI. La géométrie, les fixtures et les autres sorties peuvent progresser indépendamment de la qualification physique. Ni l'assistant ni le GPU ne bloquent cette livraison.
