# Contre-expertise indépendante SmartSVG V19.0 → V19.1
**Audit et corrections : 22 octobre 2026.**

## Ce qui a réellement été examiné
- ZIP V19.0 d'origine, code de `photo_v19.py`, `node_v19.py`, nœuds historiques V18.1 et workflows.
- 3 fichiers sources : planche de 12 escargots, illustration cadeau, photographie personnage aux chopes.
- Documentation officielle Cricut « Imprimer puis découper » et projet public ComfyUI-RMBG.
- Tests Python hérités et nouveaux tests de régression, sans GPU ni inférence Florence-2/SAM réelle.

## Défauts confirmés dans V19.0
| ID | Sévérité | Défaut | Impact | Correction V19.1 |
|---|---|---|---|---|
| P0-01 | Haut | Bord blanc calculé sur le canevas d'origine et rogné aux limites | Sticker touchant un bord, marge manquante et contour non désiré | PNG imprimable local rembourré sur les quatre côtés |
| P0-02 | Haut | Boîte du PNG détouré déduite de `mask >= 0.5` | Pixels avec alpha faible coupés (cheveux, poils, fumée, mousse) | Recadrage incluant la présence d'alpha dès 1 niveau sur 255 |
| P0-03 | Haut | Variante Cricut reprenait les alpha partiels sur la base blanche | Risque de bord intérieur transparent/trou ou découpe supplémentaire | Alpha de la variante Cricut strictement opaque dans la silhouette, trous blancs, couleurs compositées sur blanc |
| P1-04 | Moyen | Plus de masques que la mémoire CPU ne peut supporter | Mémoire potentiellement excessive à haute résolution | Max. 32 millions de valeurs masque par lot, erreur explicite |
| P1-05 | Moyen | Pas de diagnostic sur les îlots déconnectés | Multiples contours sur un même objet | Nombre de composantes et avertissement par objet |
| P2-06 | Moyen | Seuil auto photo fixé à 900 000 pixels | Certaines photos moyennes routées vers une vectorisation inadaptée | Seuil abaissé à 300 000 pixels pour scènes opaques à bord non blanc |
| P2-07 | Mineur | Masque externe qualifié « réel » sans prouver une inférence IA | Surinterprétation | Champ explicite d'origine non vérifiée ajouté au JSON ; statut V19.1 |

## Ce qui est conservé
- La branche `stickers` utilise toujours le moteur V18.1.
- `01_ORIGINAL.png` conserve le source ; `*_DETOURE.png` conserve les pixels et les transparences.
- Les masques sont exportés à la résolution de la photo.
- Pas de suppression destructrice des masques qui se chevauchent : avertissement explicite.
- Échec atomique : en cas d'erreur, aucun dossier final d'extractions n'est publié.

## Vérifications
- Tests de V19.0 : 61 précédemment déclarés ; chaîne complète dans le ZIP V19.1 : voir log de validation après extraction.
- 10 nouvelles vérifications : bord de photo, alpha doux, trou intérieur, compositing blanc, limitation mémoire, dimensions/DPI et SHA-256, îlots déconnectés, routage photo moyen, 2 photos réelles sans masque, absence de fausse segmentation automatique.
- Les deux photos de référence **ne sont pas découpées automatiquement** sans modèle/masque de segmentation : statut attendu `A_VERIFIER_MASQUES_INSUFFISANTS`.
- Simulation de masque sur figure de test uniquement ; ne prouve pas la qualité de Florence-2/SAM ou du détourage du leprechaun/femme.

## Compatibilité Cricut
- Le PNG `*_CRICUT_TEST.png` est adapté à un essai d'import en image plate : bord blanc extérieur ; aucun élément SVG superposé requis.
- Le PNG `*_DETOURE.png` n'a **pas** de remplissage blanc et convient au photomontage.
- Taille en mm calculée via les DPI du PNG ; vérifier les dimensions après import dans Design Space.
- Aplatir une composition multicouche dans Design Space ; suivre le flux Print Then Cut depuis le même appareil, calibrer et tester sur papier.
- Attention : remplir tous les trous internes en blanc favorise le contour extérieur unique, mais peut aussi modifier l'apparence d'un trou réel (anse de tasse, ouverture entre les bras). La photo PNG originale reste fournie ; ce traitement est volontaire et doit être contrôlé.

## Ce qui reste à réaliser
1. **Orchestration automatique réelle Florence-2 + SAM2** : actuellement, le moteur exige un masque provenant de ComfyUI-RMBG ou d'un autre nœud externe. La V19.1 ne télécharge ni n'exécute elle-même de modèle de reconnaissance sémantique.
2. Vérification de la compatibilité des signatures du plugin ComfyUI-RMBG réellement installé dans le Windows de l'utilisateur et de sa RTX 3070.
3. Contrôle de qualité des contours réels (cheveux/barbe, verres transparents, masques multiples), métriques IoU sur annotations manuelles.
4. Importation Design Space et test de découpe physique Cricut.
5. Édition et reconstruction sémantique des parties cachées : non implémentées.

**Conclusion :** V19.1 = maintenance de qualité de détourage et d'export Cricut. Ne pas qualifier de système de segmentation sémantique automatique validé.
