# Q04J — Ports OCR : vérification main et PR, décision bornée

**14/11/2026 — conception candidate.** Main lu directement par `GET /branches/main` : `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`. Branche documentaire relue au `5d5f1d3c80432c10fdf96e1fd2e14aa060d5f167`. Cette fiche termine l'action demandée par Q04I ; elle ne relance pas une recherche globale d'OCR à chaque cycle.

## 1. PR ouvertes effectivement consultées

Source : collection REST `/pulls?state=open&per_page=100`, puis `/pulls/{number}/files`. Quatre PR DRAFT, aucune fusion inférée. Leurs diff et définitions ajoutées/modifiées sont consultés ; absence d'ajout OCR dans ces diff, pas affirmation d'absence dans toutes branches possibles.

| PR | HEAD exact | Fichiers produit du diff | Port / portée vérifiée |
|---|---|---|---|
| #138 | dd76533696deeefcaea65328b4cda6326d5df9b9 | native_recovery_tk_v34.py | chargement, confirmation et réception d'une récupération ; aucun port de reconnaissance texte ajouté |
| #139 | f8aa1a632080ecc0158fad667640818677319ed7 | native_atelier_tk_v34.py ; smartsvg_core/native_brush_history_v34.py | inspect_native_brush_history(project_path,expected_sha256), état Undo/Redo et UI ; pas OCR |
| #140 | e3a072f6f0e5735bf7d9a567e89a536048810ae0 | native_image_viewport_v34.py | taille/fit du viewport Tk ; pas OCR |
| #144 | 58efc58e1fe730786f6a2ec04d14c850bbec4826 | smartsvg_core/native_brush_history_command_v34.py | change_native_brush_history avec projet/SHA/subject/action/command_id/confirmed ; Undo du pinceau, pas moteur texte ni Undo universel |

Tous les chemins ci-dessus sont sous `engine/`. Les fichiers de tests associés n'ajoutent pas de fournisseur OCR. Cette observation ne qualifie pas la correction ni les CI de ces PR dans ce passage.

## 2. Code source lu

Recherche dans `engine/` et `tests/` du snapshot main exact : `ocr`, `tesseract`, `easyocr`, `paddleocr`. Les mentions trouvées concernent surtout l'absence de promesse OCR. Lecture directe de `engine/smartsvg_ai/routing_v21121.py` : `inspect_route(image, *, has_alpha=False)` retourne notamment `texte_extrait_ocr=False` ; `dark_sheet_masks(image)` propose des masques et ne reconnaît pas le texte. `engine/smartsvg_ai/provider_v2112.py` : `available(registry=None)` inspecte des signatures ComfyUI sans exécuter de modèle ; `segment_adaptive(rgb, *, registry=None, max_results=12)` retourne des propositions de masque, pas des chaînes Unicode. Ses candidats RMBG/BiRefNet/SAM2 ne forment pas une interface OCR démontrée. Le fournisseur historique peut télécharger à l'exécution : aucune réutilisation sans garde de consentement.

Conclusion bornée : **aucun adaptateur OCR réutilisable identifié dans ces ports ni dans les quatre diff ouverts**. V34-092 reste une amélioration de texture IA ; aucun changement de nom pour simuler une fonction OCR. Le prochain travail utile est un contrat d'adaptateur optionnel, non une dixième fiche disant seulement « port à rechercher ».

## 3. Interface de proposition OCR future — sans choix de modèle implicite

Propriétaire W14 infrastructure/provenance ; W16 capacité OCR héritée S-021/S-047 ; W10 consomme le texte accepté. B13 étude P1, moteur optionnel P2. `recognize_text(request)` est une **interface conceptuelle à implémenter**, pas un symbole existant.

Entrée versionnée `smartsvg-ocr-request/1-draft` : request_id, project_id, project_sha256, source_sha256, source_size_px, ROI `[x,y,w,h]` entière dans source orientée, language_hints[], provider_ref ou `MANUAL`, model/checkpoint hashes si IA, budget_policy_version, consent_execution_ref. Ressource image fournie par référence locale admise, jamais URL arbitraire ni chemin publié dans rapport. Refus coordonnées hors image, NaN, volume excessif, hash divergent, provider absent/incompatible, licence non admise ou consentement absent. Le chemin manuel ne prétend pas reconnaître une image : l'utilisateur saisit le texte.

Sortie `smartsvg-ocr-proposal/1-draft` : proposal_id, request_digest, project/source SHA, moteur/version, lignes `{text_original,box_source_px,score_raw|null,score_definition|null}`, ordre proposé, langues observées si supportées, diagnostics et limitations. Pas de police identifiée sans preuve indépendante ; score brut non calibré n'est pas un pourcentage de certitude. Le texte est donné non fiable : aucun Markdown/HTML/action/script exécuté.

États : REQUESTED → RUNNING → READY_FOR_REVIEW ; branches CANCEL_REQUESTED/CANCELLED, FAILED, STALE, INTERRUPTED. Un résultat tardif avec token révoqué ne devient pas accepté. Fermer/réouvrir ne relance pas de modèle. À validation humaine, conserver corrections et provenance ; appliquer via commande de composition compatible, uniquement sur même révision. Sans persistance V2, permettre une copie explicite vers le brouillon texte en mémoire avec avertissement de non-sauvegarde ; **pas** statut G6.3 accompli.

UX : image et transcription côte à côte, surlignage des zones incertaines, correction clavier, ignorer une zone, conserver original, accepter puis Undo. Aucun téléchargement pour afficher le panneau. Refus d'installation ≠ blocage de la saisie manuelle. Expert voit modèle/hash/langue/ROI et unités ; novice voit les mots à contrôler et leur source.

## 4. Tranches et recette

OCR0 : contrat pur + faux fournisseur de test déterministe explicitement étiqueté, aucune reconnaissance « réelle ». OCR1 : UI de correction + attachement de provenance dans brouillon ; OCR2 : choix d'un fournisseur officiellement documenté, licence/runtime et installation consentie ; OCR3 : adaptateur local, CPU/GPU/OOM et benchmark de corpus autorisé ; OCR4 : acceptation via CP4 de composition et tests de sauvegarde. OCR0/1 n'attendent pas un modèle ; OCR4 n'autorise aucun champ V1 nouveau.

Positifs : transcription corrigée conserve source et ROI ; saut de ligne/accents conservés ; refus IA laisse saisie manuelle fonctionnelle ; projet réouvert conserve texte accepté après CP4. Négatifs : modèle absent, checkpoint altéré, licence inconnue, langue non supportée, ROI illégale, sortie géante, injection textuelle, score sans définition, résultat après annulation/changement SHA, deux acceptations, disque plein après acceptation, crash avant ACK. Assertions : zéro mutation avant acceptation ; pas de réseau involontaire ; aucune substitution de police ; au plus un effet durable et récupération explicite. Fixtures synthétiques, aucun document personnel public. Performance : temps/RSS/VRAM/erreurs par langue et taille, résultats NOT_RUN. Pas de test Design Space requis pour le parseur OCR ; ses exports aval gardent leurs propres gates.

**Action Q04J documentaire accomplie.** Tests produit nouveaux NOT_RUN. La suite de campagne est le curseur `RUN_STATE.json`, pas une recherche répétée des mêmes PR tant que leurs HEAD ne changent pas.
