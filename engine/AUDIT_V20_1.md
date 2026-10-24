# Audit V20.1 — rapport de développement

Date : 22 octobre 2026.

## Reproduction sur la photo réelle

- Fichier source : photo d'écran 1 152 × 1 536 pixels (`1000077568.jpg`).
- Carte principale reconnue, boîte quadrilatérale : `(335,85)`, `(1015,122)`, `(995,1159)`, `(333,1170)` ; valeurs arrondies.
- Correction homographique : carte d'environ **681 × 1 085 pixels**.
- La bande d'interface à droite est exclue. Les oreilles, yeux, tresses, vêtements restent reconnaissables dans le line-art.
- SVG monochrome produit à partir de **100 sous-tracés** après filtrage du bruit (mesure pour cette entrée et ce réglage).
- La silhouette externe du personnage est **une approximation morphologique** et la fin du torse est ouverte dans la source. Ne pas utiliser comme résultat de découpe validé.
- Comparaison visuelle PNG avant/après produite, ainsi que masque de silhouette, carte, SVG et rapport JSON.

## Tests

- 15 tests V20.1 sur détection/correction géométrique, nettoyage, SVG analysable, manque de cadre, coupes ouvertes, source préservée, erreurs transactionnelles et nœuds ComfyUI.
- 243 tests V20 hérités intacts : aucune modification des modules photo/segmentation V20.
- Total : **258 tests logiciels**, exécutés dans cet environnement CPU.

## Limites

- Pas d'inférence RMBG, SAM2, Florence-2, BiRefNet exécutée sur RTX 3070.
- Pas d'import testé dans Cricut Design Space et pas de découpe physique.
- Aucune reconstruction des pixels perdus par défocalisation ou moiré.
- Les masques personnage doivent être vérifiés avant découpe.
- Les réglages du nettoyage sont heuristiques, à adapter aux scans/photos difficiles.

## Suite prévue

Voir `ROADMAP_APRES_V20_1.md` : contre-expertise line-art, raccordement au moteur IA, profils GPU, benchmarks de détourage réel et validation Cricut.
