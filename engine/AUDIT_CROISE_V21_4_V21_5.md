# Contre-expertise croisée SmartSVG V21.4 et V21.5

**Date : 23 octobre 2026.** Périmètre : code modulaire V21.4, Python Express V21.5, scripts JavaScript, publication des vignettes, workflows, exports PNG/SVG. Audit correctif livré en **V21.5.1**.

## Passe 1 — Architecture et contrat ComfyUI

- La V21.4 a organisé plusieurs contrats dans `smartsvg_core`, `smartsvg_ai`, `smartsvg_vector`, `smartsvg_cricut`, `smartsvg_compat`, sans réécrire les moteurs historiques.
- La V21.5 a ajouté `smartsvg_ui`, `WEB_DIRECTORY` et le tableau de bord JavaScript, **en maintenant les cinq réglages et trois sorties Express**.
- Les anciennes classes sont conservées; aucun changement de type de port du nœud Express V21.5.1.
- **Risque encore ouvert :** coexistence de nombreux nœuds et validateurs historiques. Réduire progressivement leur visibilité sans casser les IDs des workflows.

## Passe 2 — API frontend et URL des aperçus

- **Défaut vérifié :** `new URL('/view', base)` supprime le préfixe `/proxy/8188/` de ComfyUI derrière un reverse proxy. Cela peut donner une miniature 404, même si le PNG a été généré correctement.
- **Correction :** import officiel de `api` depuis `../../scripts/api.js`, appel à `api.apiURL('/view')`, validation stricte des références de fichiers; miniatures rendues dans le panneau du nœud Express V21.5.1.
- Test simulé du navigateur avec `https://example.org/proxy/8188/` et vérification que l'URL obtenue contient `/proxy/8188/view`.
- Source de la méthode recommandée : ComfyUI frontend et documentation des extensions (voir URLs en fin de document).

## Passe 3 — Confinement des pannes de visualisation

- **Défaut vérifié dans le code :** V21.5 ne protégeait que `publish_previews()` ; une erreur `checked_report()` ou `build_presentation()` pouvait interrompre le retour du nœud **après que la fabrication a été effectuée**.
- **Correction :** retour normal du résultat de fabrication avec signalement « panneau graphique indisponible » ; le rapport JSON et les fichiers restent accessibles. Les erreurs survenant pendant **la fabrication elle-même** ne sont pas masquées.
- Le nouveau tableau de bord efface des données périmées si un appel `onExecuted` contient un rapport absent. Attention : aucune garantie que `onExecuted` soit invoqué lors d'une erreur de prompt externe; le navigateur réel reste à tester.

## Passe 4 — Confidentialité et gestion des aperçus

- **Défaut vérifié :** V21.5 conservait jusqu'à 280 miniatures récentes et ne supprimait les éléments excédentaires que s'ils avaient plus de 14 jours, sans plafond strict en cas de traitements fréquents.
- **Correction :** au maximum 96 miniatures propres à SmartSVG, nettoyage après 72 heures (à l'exécution suivante), protection des fichiers utilisateurs portant un autre nom, JPEG/SVG non acceptés dans le navigateur.
- Les copies UI demeurent dans le répertoire de sortie officiellement servi par ComfyUI, et le rapport du projet conserve sa fiche QA originale. Ce n'est pas une protection contre des utilisateurs déjà autorisés sur le serveur.

## Passe 5 — Non-régression et risques avant V21.6

- **629 tests Python** dont **13 nouveaux**; **19 tests JavaScript** dont **10 nouveaux**, soit **648 tests réussis**.
- Traitement de l'image réelle `1000077309.png` : **24 Pokémon**, **deux planches**, **77 fichiers PNG/SVG identiques par SHA-256** entre V21.4, V21.5 et V21.5.1.
- La nouvelle interface est testée avec un simulateur DOM : rendu, reset, URLs sous reverse proxy et exclusion des anciens nœuds.
- Ni session ComfyUI graphique réelle, ni inférence GPU RTX 3070, ni découpe physique Cricut n'ont été exécutées pendant l'audit.

## Priorités pour V21.6

| Importance | Chantier | Livrable mesurable |
|---|---|---|
| P0 | Modifier les masques réellement, avec aperçu avant/après | pinceau +/−, annuler/rétablir, sortie `MASK` corrigée |
| P0 | Tester le frontend moderne et l'import/export ComfyUI sur PC | workflows chargés, panneaux visibles, pas de sérialisation parasite |
| P1 | Sauvegarde et réouverture des corrections sans toucher aux PNG natifs | fichier de corrections versionné, réapplication déterministe |
| P1 | Contrôles des intersections et îlots de découpe | alertes sur objets fragmentés et contours en bord |
| P1 | Réduire les copies et l'accumulation des nœuds Legacy | interface principale simplifiée et modules chargés à la demande |
| P2 | Mesures réelles SAM2 sur RTX 3070 8 Go | temps, VRAM, qualité de détourage sur images annotées |

**Références publiques :**
- https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/docs/extensions/development.md
- https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/docs/WIDGET_SERIALIZATION.md
- https://github.com/Comfy-Org/ComfyUI/issues/14455
