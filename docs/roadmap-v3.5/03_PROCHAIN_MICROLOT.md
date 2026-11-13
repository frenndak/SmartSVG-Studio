# Premier micro-lot : historique natif sans second moteur

**Proposition exécutable, non implémentée dans ce dossier.** Tranche V35-03 ; tickets historiques V34-035/V34-038/V34-132 et critères hérités associés, sans les redéfinir. Base auditée `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`.

## Prérequis immédiat

Relire la PR #139 et son HEAD courant : elle prépare la disponibilité Undo/Redo **en lecture seule**. Ne pas recopier son travail. Si elle n'est pas intégrée, deux actions séparées restent possibles : qualifier ce candidat selon les règles applicables, ou préparer le bridge de mutation sur main sans dépendre d'un champ privé de sa branche. La fusion éventuelle et la mutation UI restent des décisions vérifiées distinctes.

## Résultat attendu

Depuis l'Atelier, voir si une retouche persistée peut être annulée ou rétablie, confirmer l'action, puis retrouver le projet réexaminé et le sujet sélectionné. Le brouillon de notes est conservé ou l'action est refusée proprement si sa resynchronisation ne peut pas être garantie. Les fichiers déjà exportés restent inchangés.

## Réutilisation prouvée par lecture

| Besoin | Service existant |
|---|---|
| Lire la disponibilité | `ManagedWorkspace.subject_brush_history(name, expected_sha256=...)` |
| Appliquer l'historique | `ManagedWorkspace.change_subject_brush_history(name, expected_sha256=..., action=..., command_id=..., confirmed=False)` |
| Plan déterministe | `smartsvg_core/subject_brush_history_g33e.py::plan_history_change` |
| Vérifier le projet affiché | Snapshot d'Atelier et SHA ; `load_native_preview` dans le shell |
| Séparer UI et calcul | `LatestOnlyJob` existant, callbacks Tk sur le thread principal |
| Réexaminer après mutation | Chemin `refresh` déjà utilisé pour notes et retouches ; généraliser seulement ce qui est nécessaire |

## Découpage borné

**03A — bridge de mutation :** adaptateur minimal dans `engine/smartsvg_core/`, réutilisant le workspace sous verrou. Entrées : chemin géré absolu, SHA attendu, action `undo`/`redo`, ID de commande et confirmation booléenne stricte. Ne pas inventer de compteur de révision, receipt store ou writer. Examiner le contrat de reçu réel avant de définir la réponse publique de l'adaptateur.

**03B — raccordement UI :** boutons et raccourcis natifs avec disponibilité fraîche, exclusion pendant écriture et confirmation ; vérifier action/projet/révision du reçu, puis réexaminer et restaurer la sélection seulement si elle reste admissible. Une erreur de reçu après écriture donne « résultat à réexaminer », pas « aucune modification » ni retry automatique. Conserver le brouillon local en cas d'échec.

**03C — parcours de reprise :** Undo→fermer→rouvrir→Redo ; nouvelles notes et nouvelle retouche ; source et masques float32 conservés. Distinguer les fonctions CPU/headless du dispatch de vrais événements Tk sous Windows. Chaque sous-lot est vérifiable avant le suivant.

## Recettes nécessaires avant déclaration de réussite

| ID | Démonstration attendue |
|---|---|
| H01 | Confirmation absente, fausse ou de mauvais type : aucun appel mutant et SHA inchangé |
| H02 | Une sauvegarde réelle puis Undo/Redo : état logique attendu à chaque relecture, ressources source identiques |
| H03 | SHA obsolète, action inconnue, frontière historique non annulable : refus et aucun écrasement |
| H04 | Double activation / réponse tardive après changement de sujet : une seule action sur la cible confirmée |
| H05 | Disque plein, conflit writer, backup pending : message fidèle au résultat réel, récupération explicite |
| H06 | Reçu invalide après commit réel : résultat inconnu signalé, projet réinspecté sans répétition aveugle |
| H07 | Notes locales non sauvegardées : conservées après historique ou opération refusée avec une issue claire |
| H08 | Fichiers exportés existants inchangés après Undo/Redo et réouverture |
| H09 | Clavier et focus sur vrais widgets Tk ; test visuel Windows séparé de faux widgets headless |

Commandes de départ existantes, à adapter aux fichiers effectivement modifiés :

```bash
python -m unittest discover -s tests -p 'test_g33e_brush_history.py' -v
python -m unittest discover -s tests -p 'test_v34_native_subject_save.py' -v
python -m unittest discover -s tests -p 'test_v34_native_brush_draft.py' -v
python -m unittest discover -s tests -p 'test_v34_native_desktop_shell.py' -v
```

Ces commandes sont des instructions futures ; elles n'ont pas été exécutées pour qualifier l'application dans cette session. Ajouter les nouveaux tests du bridge et les assertions de parcours H01–H09 avant la livraison correspondante. Relire les commandes CI du dépôt au moment de l'implémentation.

## Frontières et retour arrière

Ne pas modifier AGENTS, archives, automatisations, dépendances ou schéma V1 ; pas d'export/IA supplémentaire dans ce micro-lot. Ne pas supprimer le mode inspection si l'historique est indisponible. Retirer le bridge/bouton nouveau restaure le parcours précédent ; ne pas réécrire les projets qui ont déjà enregistré une opération historique valide. La qualification du format persistant existant demeure nécessaire.
