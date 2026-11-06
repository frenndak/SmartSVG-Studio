# SmartSVG Studio V3.4 — Stabilisation et matrice de preuves

**Campagne du 6 novembre 2026 (propriétaire : vérification autorisée).** Base de référence avant travail : `main@426c297f23edb312cd2ce61c7f70a8b67ca8954f`; G0 push [42157563315](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42157563315) PASS. Cette campagne n'active **aucune tâche horaire**, aucun téléchargement IA, ni aucune action Cricut. Le travail de qualification est proposé sous [PR #106](https://github.com/frenndak/SmartSVG-Studio/pull/106). Les archives historiques et contrats d'export ne sont pas remplacés.

## Résultat de la première confrontation aux plateformes

| Environnement | Preuve | Premier résultat | Statut |
| --- | --- | --- | --- |
| Linux Python 3.11 | G0 de #106, `unittest discover -s tests` | G0 PASS sur premier HEAD `d7661a5` | Tests existants sur Linux, pas de preuve Windows |
| Node 22 | `tests/*.mjs` et `tools/test_*.mjs` | Job Node PASS [42161575086](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42161575086) | Tests JS réels, **pas** navigateur réel |
| Windows Python 3.11 | Suite complète non filtrée | [42161575086](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42161575086) : **555 exécutés, 10 FAIL + 2 ERROR + 48 SKIP** | Déficit de compatibilité détecté, pas de faux vert |
| Windows Python 3.11 après premier correctif | Suite complète non filtrée | [42162104800](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42162104800) : **555, 1 FAIL, 48 SKIP** | Une cause Windows restante, à qualifier sur le HEAD final |
| Chromium/Playwright | Vue d'atelier DEMO 360×740, 390×844, 768×1024, 1366×768, 1920×1080 | Job navigateur PASS [42162104800](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42162104800) | Aucun chevauchement **des éléments structurants testés**, pas de recette ComfyUI ni des panneaux facultatifs |

Le premier job navigateur a échoué à cause d'un défaut du *nouveau harnais* `request.url` utilisé comme propriété au lieu de `request.url()`. Corrigé et revalidé sur les cinq résolutions. Ne pas attribuer cette erreur à l'Atelier.

La première suite Windows a mis en évidence des problèmes d'encodage implicite `cp1252`, sélection de WSL au lieu de Git Bash, chemin DOS 8.3 vs long, différences `zipfile` sur les séparateurs, CRLF d'une fixture Node et chemin SVG de confinement. Chaque correction doit rester **fail-closed** ; conserver les tests de budget, de protection de fichiers, d'archive et de dimensions. Le dernier chemin SVG doit être vérifié par identité d'ancêtre de filesystem, pas par comparaison fragile des chaînes.

**IMPORTANT :** ce tableau est une photographie de **preuves exécutées** du premier passage, pas une certification du HEAD final de la PR. Examiner les jobs du dernier HEAD avant d'annoncer le résultat de qualification.

## Qualification de la correction (après première reproduction)

**Candidat technique testé : `f2660840fbf534c0640110f8fa3bb551b3f8f3c1`**. Les preuves de la dernière exécution **complète**, à ne pas confondre avec la première passe défaillante :

| Test sur SHA exact | ID workflow | Résultat |
| --- | --- | --- |
| [G0 Python/Linux](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42162762348) | `42162762348` | **PASS** |
| [Prévol public](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42162762329) | `42162762329` | **PASS** |
| [Moteur CPU historique](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42162762324) | `42162762324` | **PASS** |
| [Windows + Node + navigateur](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42162762358) | `42162762358` | **3 jobs PASS** |

**Windows : `Ran 556 tests` / `OK (skipped=48)`**, aucun échec ni erreur. Les contrôles de sécurité importants (`test_protected_source_renamed_into_unprotected_path_is_blocked`, `test_success_requires_explicit_budget_and_remaining_runs`, `test_windows_backslashes`, `test_svg_width_nan_cannot_be_reported_ok_local`, `test_svg_outside_project_is_never_approved_even_with_valid_mm`) sont **réellement exécutés et réussis**, et non ignorés. Les 48 skips concernent les tests soumis aux dépendances facultatives de l'environnement ; ne pas revendiquer 556 assertions toutes exécutées.

Les changements sont concentrés sur l'outil de qualification, les assertions de tests liées aux encodages et chemins Windows, et une seule fonction de production : `_svg_preflight`, qui vérifie l'appartenance d'un SVG au répertoire du projet par **identité d'ancêtre** sur Windows. Le contrôle PNG `_source` a été vérifié octet pour octet identique à celui du `main` initial. Le nouveau test externe refuse un SVG valide localisé hors projet. **Ne pas modifier la sémantique de sécurité pour faire passer les tests.**

La modification de cette documentation dans la PR crée un **HEAD plus récent** : relire les workflows du HEAD final avant tout squash. Les validations ci-dessus concernent explicitement le code `f2660840`.

## Matrice fonctionnelle : preuve existante ≠ recette de bout en bout

| Parcours | Code et tests déjà présents | Ce qui n'est PAS encore prouvé | Verdict |
| --- | --- | --- | --- |
| Import PNG et archive `.smartsvg` | `test_g22_managed_projects.py`, `test_g13_project_archive.py`, `test_v34_native_desktop_shell.py` | Photo réelle, ouverture GUI Windows et sauvegarde native dans le shell autonome | **TESTÉ_PARTIEL** |
| Récupération après sauvegarde interrompue | `test_g14_project_recovery.py`, `test_recovery_transaction.py`, `test_g33e_brush_history.py` | Interruption réelle sous Windows, verrouillage multi-processus et récupération opérateur en interface | **TESTÉ_PARTIEL** |
| Retouches réelles de sujet, Undo/Redo | `test_g33e_subject_brush_preview.py`, `test_g33e_brush_history.py` et modules Atelier legacy | Retouche réellement pilotable et sauvegardée depuis le shell autonome | **TESTÉ_PARTIEL** |
| PNG Print Then Cut | `test_v34_cricut_handoff_guide.py`, `test_v34_png_density.py`, `direct_import_v218.py` | Import Design Space, impression A4, tolérance des marques et découpe réelle | **TESTÉ_STATIQUE / NON_CERTIFIÉ** |
| SVG Basic Cut | `test_svg_contracts.py`, `test_g4_cut_preflight_integrated.py` | Topologie géométrique, paramètres du tapis et véritable découpe | **TESTÉ_STATIQUE / NON_CERTIFIÉ** |
| SVG Cut multicouche | `test_v34_svg_publication.py`, contrats V3.4 lots 14/17 | Séparation couleur et opérations réelle via l'application autonome et Design Space | **PREUVE_BOUT_EN_BOUT_ABSENTE** |
| SVG d'édition | `test_g29_svg_path_grammar.py`, `test_g31_atelier_svg_bridge.py` | Édition complète des nœuds/courbes, round-trip modifiable et rendu Windows | **PREUVE_BOUT_EN_BOUT_ABSENTE** |
| Habillage UX artisanal | `test_v34_native_theme_tokens.py`, `test_v34_native_theme_picker.py` | Contraste *rendu*, 1280×720 en DPI 200 %, lecteur d'écran et focus effectif Tk | **TESTÉ_SIMULÉ / NON_QUALIFIÉ_WINDOWS** |
| Interface web d'atelier | `tests/g33_ux_dom_smoke.mjs`, nouveau `tests/stability_atelier_browser.cjs` | Panneaux ComfyUI locaux, longue langue FR, états en erreur, zoom 200 %, API même origine | **TESTÉ_PARTIEL** |
| IA locale / RTX / installateur | Conception V3.4, moteur historique ComfyUI/CPU | Catalogue IA autonome, inference RTX et installateur Windows | **NON_QUALIFIÉ / NON_LIVRÉ** |

**Règle d'attribution de maturité :** SPECIFIE → IMPLEMENTE → TESTE_AUTOMATIQUEMENT → INTEGRE_MAIN → QUALIFIE_WINDOWS → QUALIFIE_MACHINE. Un test unitaire n'atteste pas de la dernière colonne. Les 437 tests proposés par la conception V3.4 restent des **recettes planifiées**, pas 437 tests intégralement exécutés.

## Réconciliation des issues sans effacer le passé

| Issue | Statut d'audit au 6 novembre | Condition de résolution |
| --- | --- | --- |
| [#2](https://github.com/frenndak/SmartSVG-Studio/issues/2) | Source V21.15.2 présente, rapport `docs/IMPORT_V21_15_2.json` et G0 validés ; **historique réconciliable** | Comparer précisément aux critères d'admission et rapporter la fermeture |
| [#3](https://github.com/frenndak/SmartSVG-Studio/issues/3) | `inspect_svg_contracts.py` rejette `<style>` et `d` invalide ; tests dédiés présents | Confirmer sur HEAD final, ne pas certifier topologie |
| [#41](https://github.com/frenndak/SmartSVG-Studio/issues/41) | Ancien suivi de 26 PR désormais obsolète | Documenter remplacement par suivi courant |
| [#71](https://github.com/frenndak/SmartSVG-Studio/issues/71) | Gestion pinceau et preuves G3.3e intégrées depuis son ouverture | Réconcilier tous les cas d'acceptation |
| [#72](https://github.com/frenndak/SmartSVG-Studio/issues/72) | Campagne de conception 24/24 terminée, promue V3.4 dans AGENTS | Clôturer l'activité de conception, **pas** l'implémentation |
| [#51](https://github.com/frenndak/SmartSVG-Studio/issues/51) | Porte préinstallation encore ouverte | Parcours réel de bout en bout, UX + ComfyUI/Windows |
| [#57](https://github.com/frenndak/SmartSVG-Studio/issues/57) | Défauts Windows reproduits dans la campagne | Suite Windows complète PASS sur HEAD final sans neutralisation |
| [#58](https://github.com/frenndak/SmartSVG-Studio/issues/58) | Pas de débordement structurel sur 5 tailles dans la **demo par défaut** | Essai des panneaux ouverts, focus et captures de conflit avant fermeture |
| [#29](https://github.com/frenndak/SmartSVG-Studio/issues/29) | Registre de coordination central, pause maintenue | Conserver |

## Décision GO / NO-GO

**GO** pour la CI de qualification et pour poursuivre la correction de dysfonctionnements **confirmés** pendant cette campagne manuelle. **NO-GO** pour une annonce de logiciel complet : installer la GUI native sur le PC de l'utilisateur, qualifier les quatre types d'export dans Design Space, la sauvegarde UI, le flux sujet→détourage→retouche et le matériel Cricut sont encore des tâches séparées.

Le prochain micro-lot ne doit pas reprendre le développement fonctionnel automatiquement : le planificateur SmartSVG reste désactivé jusqu'à instruction du propriétaire.
