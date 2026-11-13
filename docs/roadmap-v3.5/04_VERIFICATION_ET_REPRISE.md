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

## Développement 03A — 14 novembre 2026

Candidat de code : [PR #144](https://github.com/frenndak/SmartSVG-Studio/pull/144), `955cfbdb6858c14d73ec3f4d2d2d5e474e64f6a5`, basé sur le même main. Les deux fichiers déposés ont été relus à ce commit distant et comparés aux fichiers testés : contenu identique. Tous les fichiers préexistants du snapshot complet ont été contrôlés contre les blobs de l'arbre main : **aucun modifié**. Le ZIP attaché a fourni uniquement les fichiers dont le blob correspondait au dépôt ; les autres ont été récupérés au SHA exact.

| Vérification locale, Python 3.12.14/Linux | Résultat | Limite |
|---|---|---|
| Tests du nouveau port de commande | 15/15 PASS, 0 skip | Vrais projets V1 synthétiques ; pas de bouton UI |
| Suite du dépôt `python -m unittest discover -s tests -p 'test_*.py' -v` | 758 tests, 0 échec, 32 skips | Skips graphiques faute de display ; baseline = 743 tests et mêmes 32 skips |
| `python tools/qualify_subject_brush_cpu_g33e.py` | 53/53 PASS, 0 skip | Runner historique CPU, distinct des 15 nouveaux tests ; ne pas additionner les compteurs |
| `python tools/verify_source_integrity.py --repo . --archive-only` | PASS, 651 empreintes manifestes | Archive d'origine ; ne qualifie pas tout le moteur actuel |
| `python -m compileall -q engine/smartsvg_core tools tests` | Exit 0 | Syntaxe/imports compilables, pas une recette fonctionnelle |

NumPy 2.3.5 et Pillow 13.0.0 présents. Les tests vérifient une sauvegarde réelle puis Undo/réouverture/Redo, ressources et notes conservées, exports intacts, confirmation stricte, sujet différent, révision périmée, nouvelle édition après Undo, métadonnées falsifiées, reçu invalide après vrai commit, erreur après publication et note concurrente entre disponibilité et écriture.

**Contre-expertise indépendante bornée :** lecture des contrats réels d'admission, historique et recovery ; exécution séparée des 15 tests ciblés, tous PASS sans skip ; aucune anomalie restante. Les deux recommandations initiales de couverture sont intégrées : vraie panne de rotation du backup après publication et modification concurrente des notes avant le writer. Cette relecture ne constitue pas une review GitHub APPROVED.

**CI distante :** quatre workflows ont démarré sur le SHA exact lors du dépôt ; leur état initial était `in_progress`. Ne pas les considérer PASS à partir des seuls résultats locaux. Pas de validation Windows, GPU, Design Space ou physique ajoutée par cette session à ce stade.

**Résultat distant relu ensuite sur ce même SHA :** quatre workflows SUCCESS — [G0 #43527574722](https://github.com/frenndak/SmartSVG-Studio/actions/runs/43527574722), [prévol #43527574638](https://github.com/frenndak/SmartSVG-Studio/actions/runs/43527574638), [CPU #43527574643](https://github.com/frenndak/SmartSVG-Studio/actions/runs/43527574643) et [stabilité #43527574662](https://github.com/frenndak/SmartSVG-Studio/actions/runs/43527574662). Journaux du job Windows `132237044759` relus : **758 tests, 2 skips POSIX, aucun échec ; les 15 nouveaux tests sont tous exécutés et `ok`**. Étape stricte native V1→Tk→CPU SUCCESS ; jobs Node et Chromium SUCCESS. Preuve de régression Windows sur ce candidat, sans qualification de packaging, de nouveaux boutons Undo/Redo, de GPU, de Design Space ou de découpe physique.

**Statut : TESTE_SUR_BRANCHE / NON_INTEGRE.** Les critères des tickets historiques restent ouverts ; V3.4 toujours active. Prochain développement : 03B, interface explicite et rafraîchissement sans perte du brouillon de notes. Ne pas confondre la réussite du port avec la livraison de boutons Annuler/Rétablir au bureau.
