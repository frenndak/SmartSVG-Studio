# SmartSVG V3.5 — COV-18E-2 : comparaison, interactions et accessibilité (E06–E10)

**13 novembre 2026 — CANDIDATE, NON NORMATIVE.** Deuxième tranche E après [COV18E1](COV18E1_LIBRARY_ATELIER_E01_E05.md). Source UX #134/COV17E, héritage V3.3 et V3.4 lot 07/12/18/21/22, snapshot main aa0ff9e7d0c53dba3fdc429c02c6198736cfe935. Aucun test Windows/produit exécuté ici.

## 1. Les cinq contrats UX et les écarts identifiés

| UX | Engagement historique | Problème identifié et décision de conception |
|---|---|---|
| **E06 — Avant/après, slider et superposition** | **S-073 P0/G2.8** : vues original/masque/coupe distinctes, **dimensions constantes, aucune inversion confondue** ; **S-079 P1** : loupe locale/comparaison glissante, doit repérer halo ou trait coupé | **AMÉLIORER P1** : dériver deux previews même source/révision et calculer le rendu delta, sans modifier les pixels. Source_preview_v34 et previews.py n'établissent pas le slider 1:1. Une couche « coupe » doit provenir d'un profil géométrique, pas d'un simple masque de couleur. |
| **E07 — Context bar, hover, gestes et raccourcis** | **S-072 P0/G2.7** : Express souris + clavier sans drag obligatoire ; **S-070 P0** sujet/vignettes même ID ; **S-071 P0** erreurs actionnables | **RACCORDER P0** : actions contextualisées sur la vraie sélection et sa capacité, raccourcis à portée connue (pas dans champ texte), Undo/Redo sur la bonne transaction. Aucun outil absent représenté comme action active. |
| **E08 — Modes novice/avancé** | **S-025 P0** : sticker simple sans graphe ; **S-068 P0** : aucun contrôle caché 1366×768/1920×1080 ; S-072 clavier | **GARDER P0** : divulgation progressive, non un second éditeur. Les modes partagent projet/selection/transactions, et changer de mode ne convertit jamais une sortie Basic Cut en SVG d'édition. |
| **E09 — Thèmes, panneaux et préférences** | **S-059 P1** audit clavier/contraste/labels ; S-068 desktop responsive | **RACCORDER P1** : native_theme_tk_v34.py propose thème/accent/motion réduit, pas de garantie complète du contraste/focus à 200 % ; préférences locales séparées des données de projet, recovery de config corrompue. |
| **E10 — Accessibilité étendue** | **S-059 P1** : scénario Express réalisable au clavier ; **S-068 P0** responsive sans action masquée ; **S-093 P0** : tests utilisateurs novice/régulier, observations anonymisées | **AMÉLIORER P0 UX** : protocole Windows réel, tab-order/focus visibles, lecteur d'écran, contrastes, messages FR non codés par couleur seule, 1366×768/DPI 200 %, réduction des animations. Ne jamais annoncer accessible parce que Tk émet des key bindings. |

## 2. Contrat commun et tests de fermeture

**Etat unique** : ProjectRevision, active_subject_id, mode_affichage, viewport_transform, draft_id. Une comparaison ou un déplacement de panneau ne change pas les sujets ou la sauvegarde ; un raccourci s'applique au composant qui a effectivement le focus. Les overlay de masque/pixel/cut sont explicitement typés, avec source et unités (px ou mm) ; une preview `STALE` ne remplace pas la vue active.

**Parcours novice** : ouvrir sticker → cliquer sujet ou vignette → comparer fond blanc/noir/damier avec slider → Undo → enregistrer et exporter ; clavier sans drag. **Expert** : inspecter IDs, zoom exact, mesures mm, QA et codes d'erreur, sans imposer 80 boutons permanents.

**Tests proposés, NOT_RUN** : (1) deux projets ouverts successivement, une réponse async tardive ne peut écraser le bon overlay ; (2) écran DPI 200 % 1366×768 sans action hors écran ; (3) état hover/Focus/Shortcut dans un champ texte ne déclenche pas une action destructrice ; (4) contraste insuffisant en thème accent personnalisée → test de lisibilité FAIL et repli ; (5) sliders avec sources de dimensions différentes → refus de diff faussement aligné ; (6) preview cutter-only sans géométrie mm connue → UNKNOWN ; (7) lecteur d'écran annonce noms/rôles/erreurs et confirmation, non de simples icônes ; (8) raccourci Annuler après publication ZIP externe ne supprime pas l'archive livrée.

**Mesures** : réponse au zoom, scroll et previews p50/p95, mémoire et latence d'une vraie UI Windows à recueillir ; ne pas inventer les seuils. Conserver screenshot/test users anonymisés et sous consentement, aucune donnée personnelle dans repo public. L'IA locale/QR/Smart Delivery sont réutilisables depuis la même barre contextuelle mais ne peuvent installer modèles ou activer réseau implicitement.

**Etat** : E06–E10 = cinq décisions candidates contre-expertisées, 0 certifiées. Aucune modification produit ni AGENTS. **Prochaine étape COV-18E-3** : E11–E15 (Undo/CAS/recovery, caches, diagnostics et QA).
