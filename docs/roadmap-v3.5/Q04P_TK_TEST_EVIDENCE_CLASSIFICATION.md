# V35-Q04P — Qualification des preuves Tk existantes pour ROI B13 (14 novembre 2026)

**Statut : CANDIDAT / NOT_RUN.** V3.4 reste normative. Suite directe de Q04O, sans code ni changement de gouvernance. Sources effectivement consultées : Q04O et `engine/native_image_viewport_v34.py` sur la branche candidate ; les chemins présumés `tests/test_native_image_viewport_v34.py` et `tests/test_native_ui_v34.py` ont retourné NOT_FOUND : **absence à ces chemins seulement**, pas preuve qu'aucun test Tk n'existe. La lecture répétée de PROGRESS a retourné NOT_FOUND après une lecture initiale réussie dans cette session ; ne pas présumer son contenu final ni modifier sans blob SHA.

## Décision et contre-expertise
**AMÉLIORER** l'oracle Q04O par une matrice de preuve et **REPORTER** toute certification OCR/ROI. Le viewport courant fournit `fit_factor`, `load`, `fit`, `actual_size`, `zoom_in/out`, `_show`, `scan_mark/scan_dragto`, `xview/yview`. Il n'expose ni ROI, ni `canvasx/canvasy` dans un port stable, ni item image conservé, ni génération/révision. Les tests purement arithmétiques de `fit_factor` ne certifient donc pas le mapping ROI réel. L'absence de gestion d'une sélection dans les bindings actuels interdit de présenter une démonstration UI comme fonctionnalité livrée. Alternative plus simple : sélection numérique sur pixels source, après contrôle SHA, ou transcription manuelle ; aucune migration Qt/Tauri sans benchmark.

## Matrice de qualification Q04O
| Cas | Oracle requis | Preuve acceptable | Statut |
|---|---|---|---|
| W01/W02 | rectangle canonique et k=1/2 | vrai Tk + pixels source comparés | NOT_RUN |
| W03 | bord impair 1001 px / k=3 | dimensions PhotoImage réelles, bornes exclusives | NOT_RUN |
| W04 | pan | coordonnées canvasx/y et xview/yview enregistrées | NOT_RUN |
| W05 | fit/100 % | génération invalidée, source inchangée | NOT_RUN |
| W06 | clavier | saisie source et focus réels | NOT_RUN |
| W07 | 1366×768, DPI 200 % | session Windows et captures anonymisées | NOT_RUN |
| N01–N12 | stale, annulation, crash, concurrence, corruption | fixtures synthétiques, assertions négatives et rollback | NOT_RUN |

**Classification stricte des tests :** `PURE_UNIT` (calcul sans GUI), `TK_SIMULATED` (mock), `TK_NATIVE_NON_WINDOWS`, `WINDOWS_TK_NATIVE`, `DESIGN_SPACE_REAL`, `PHYSICAL_CUT_REAL`. Aucune classe ne se substitue à une autre ; `SKIP` ≠ `PASS`. Reporter SHA, OS/build, Tk patchlevel, DPI, dimensions et résultat par ID. Ne jamais traiter les 437 scénarios documentés comme tests exécutés.

## Micro-lots TDD proposés (aucun implémenté ici)
1. **Q04P-A : inventaire vérifié** : trouver les fichiers tests réels par index du dépôt, relever chemins, blobs, classes de test, skips et fixtures. Interdit d'inférer leur absence des deux chemins 404.
2. **Q04P-B : oracle pur** : fixtures synthétiques 960×470, 1001×701 et 4096×1221, mapping demi-ouvert, bords, rejet NaN/dimensions nulles ; au moins trois négatifs (hors image, k invalide, SHA obsolète).
3. **Q04P-C : Tk natif Windows** : instrumentation non destructive de l'item image, coordonnées réelles, pan/zoom/DPI, gestion de focus et cancellation. Tests `NOT_RUN` jusqu'à exécution Windows.
4. **Q04P-D : revue hostile** : démontrer qu'aucune sélection sur miniature, aucun masque float32 et aucun TextNode ne modifie le projet V1 ; preuve de reprise, annulation et absence de fuite de données.

## Contrats transversaux
Un projet `.smartsvg` V1, writer CAS, provenance et masques float32 intacts ; quatre exports distincts PNG PTC, SVG Basic Cut, SVG CUT multicouche et SVG éditable ; KNOWN/UNKNOWN machine, aucune certification Cricut. IA/OCR facultative et consentie, sans téléchargement silencieux ; fallback manuel. Tests UI clavier/focus/contraste/motion réduite et DPI 200 % à exécuter, objectifs de performance à mesurer et non inventés. Pas de données privées ni police sous licence dans les fixtures. Undo de la ROI locale ne doit pas muter l'historique V1. Dépendances et packaging : aucun changement proposé.

## Contrôle R3 01–25
01–05 : héritage conservé, aucune couverture nouvellement certifiée ; 06 : statuts disjoints ; 07–09 : projet/exports/machine inchangés ; 10–13 : UX, clavier, DPI, stale, crash planifiés non exécutés ; 14–17 : IA, raster, vecteur, fabrique non modifiés (non applicables à l'oracle de ROI hors interfaces) ; 18–19 : Delivery et autres opportunités non modifiés (non applicables à ce micro-lot) ; 20 : mesures à établir ; 21 : fixtures synthétiques ; 22 : branche documentaire seule ; 23 : pas de second Canvas/store ; 24 : aucune promotion ; 25 : contrôle explicite sans raccourcissement d'obligation.

**Prochaine action unique :** identifier les chemins réels des tests Tk à partir de l'arbre GitHub et classer chaque assertion selon la matrice ci-dessus avant toute déclaration de couverture. Main@HEAD et WIP PR : NON_VÉRIFIÉS dans ce passage.