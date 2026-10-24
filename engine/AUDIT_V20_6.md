# Validation V20.6 — 23 octobre 2026

## Nature du changement

Deux modules additifs : `hd_multisticker_v206.py` (rendu/source/mesures) et `node_v206.py` (un nœud de 7 entrées ComfyUI, dont l'image). Les anciennes classes restent enregistrées par héritage de `node_v205`.

## Contrôles

- 431 tests automatisés (406 historiques + 25 V20.6).
- Anti-régression : tous les fichiers sources historiques V20.5 ont les mêmes SHA-256, sauf `__init__.py` volontairement changé pour exposer le nouveau nœud.
- Sérialisation des six workflows V20.6 contrôlée par type et ordre des paramètres ; import du package contrôlé.
- Protection dimensions : 20 millions de pixels maximum à l'entrée, 32 millions à l'export par image/planche.
- Rejet des entrées non finies / invalides et des fonds complexes dans le mode multi-stickers sans masque IA.
- Enregistrement des fichiers via fichiers temporaires puis renommage atomique.
- Grille multi : regroupement de composantes connectées entières, meilleur que découpage strict en cases. Fallback convexe signalé.
- Métadonnées DPI et largeur SVG mm ; avertissement explicite si pixels synthétiques interpolés.

## Essais réels

| Source | Dimensions | Profil | Résultat V20.6 | Limite |
|---|---:|---|---|---|
| Affiche « Le malaise est en toi » | 1087 × 1536 | affiche | PNG HD + SVG de cadre | personnages non extraits séparément |
| Courage | 1536 × 1152 | logo_cartoon | PNG HD + SVG de cadre | chien / lettres non séparés |
| Pokémon 24 | 1536 × 1097 | planche_multi 6×4 | 24 PNG + 24 SVG ; 2 planches de 12 (12 îlots chacune) | bord noir/masques et détail natif limité ; enveloppes convexes si îlots |
| Canard musclé, screenshot | 691 × 1536 | capture_produit | recadrage interface + PNG HD et cadre | détourage du canard requiert segmentation IA |
| Famille renard | 614 × 1536 | scene_decorative | PNG HD de l'image complète + cadre | séparer les personnages réclame une segmentation IA |

## Limites de validation

Le contrôleur fait une pré-estimation physique ; Design Space détermine la taille d'importation et la zone Print Then Cut. Ni un PNG enregistré à 300/450 ppp ni un contour détecté par CV ne certifient une impression ou une découpe correcte. Pas de GPU NVIDIA ni d'accès physique à la Cricut pendant ces essais.
