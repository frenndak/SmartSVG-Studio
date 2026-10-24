# SmartSVG Studio V20.1.2 — Choix explicite de l'opération Cricut

Cette version complète la branche **dessin photographié / scan** de V20.1.1.
Les moteurs précédents, notamment Florence-2/SAM2, le raffinement photo et les stickers historiques, sont conservés.

## Nouveau nœud ComfyUI

**SmartSVG V20.1.2 — Choix de découpe Cricut / Stylo** (`SmartSVGLineArtV2012`).

Deux réglages différents, qui ne doivent pas être confondus :

- `cible_decoupe` : `carte` (rectangle), `personnage` (silhouette géométrique proposée), `sticker` (silhouette proposée avec bord blanc de `marge_blanche_px`).
- `operation_cricut` : le travail PHYSIQUE attendu de la Cricut.

| Valeur `operation_cricut` | Export recommandé | Dans Design Space |
|---|---|---|
| `imprimer_decouper_contour` | `01_IMPRIMER_PUIS_DECOUPER_UNIQUEMENT_CONTOUR.png` | Imprimer puis découper : **une silhouette extérieure**, traits internes imprimés |
| `decouper_contour_seul` | `02_DECOUPER_SEULEMENT_CONTOUR_EXTERIEUR.svg` | Découpe de base : silhouette seulement, sans impression |
| `decouper_tous_les_traits` | `03_DECOUPER_CHAQUE_TRAIT.svg` | Découpe de base : suit toutes les formes des traits, y compris contours internes |
| `dessiner_au_stylo` | `04_DESSINER_LES_TRAITS_STYLO.svg` (si disponible) | Dessiner au stylo : chemins centraux expérimentaux |
| `tout_preparer` | Prépare toutes les variantes possibles, privilégie le PNG sticker | Choisir **une seule** méthode dans Design Space |

Les noms des fichiers sont volontairement distincts. Ne superposez PAS automatiquement les SVG de coupe et le PNG Print Then Cut dans un même projet : vous risquez de découper les détails internes.

## Réglages pour un sticker du personnage

- `cible_decoupe = sticker`
- `operation_cricut = imprimer_decouper_contour`
- `marge_blanche_px = 10` (puis adapter au dessin et à l'impression)
- `largeur_finale_mm = 90` (dimensions physiques définies dans les SVG ; vérifier la taille du PNG dans Design Space)

Importer uniquement le PNG `01_` comme **Imprimer puis découper**.

**ATTENTION** : la détection du personnage de V20.1 reste morphologique, non sémantique. Le contour proposé n'est pas certifié et peut englober des zones indésirables, surtout si la silhouette est ouverte/coupée à la bordure. Contrôler la prévisualisation Cricut avant toute découpe. Si aucun personnage n'est trouvé, l'ancien moteur se replie sur le contour de la carte et le rapport porte un avertissement explicite.

## Découper tous les traits

Importer **uniquement** le SVG `03_` en `Découpe de base`. Ce SVG représente le **périmètre des zones d'encre** : un trait d'épaisseur significative pourra donc avoir deux bords de coupe. Ce n'est pas un fichier de stylo ni une ligne médiane. Attention aux détails très fins, aux petits débris et aux découpes longues ou fragiles.

## Dessin au stylo

Le SVG `04_` est obtenu par amincissement géométrique des traits, sans modèle IA. Il est expérimental et peut être discontinu sur des photographies bruitées. Lorsque le dessin est trop fragmenté, le moteur refuse ce SVG et mentionne `TRACES_STYLO_INDISPONIBLES_IMAGE_TROP_COMPLEXE`; les autres exports restent utilisables. Si vous associez un tracé au stylo à une découpe extérieure, utilisez **Attacher** dans Design Space pour maintenir les positions relatives.

## Architecture et fichiers

L'archive conserve les anciens nœuds `SmartSVGLineArtV201` et `SmartSVGLineArtV2011` ; elle ajoute le nœud `SmartSVGLineArtV2012`.
La V20.1.2 appelle le moteur V20.1.1 **sans le modifier**, puis crée un dossier additionnel `08_CHOIX_CRICUT/` dans chaque résultat :

- `01_...png`, `02_...svg`, `03_...svg`, éventuellement `04_...svg`
- `A_LIRE_AVANT_CRICUT.txt`
- `CHOIX_CRICUT_V20_1_2.json` avec le fichier recommandé et les alertes.

Le dossier additionnel est créé de façon atomique. L'image de référence PNG de V20.1.1 demeure identique dans les scénarios testés.
Les SVG portent une largeur physique en millimètres ; le PNG Print Then Cut peut nécessiter un ajustement manuel dans Design Space.

## Limites et suite du projet

V20.1.2 a été testée sur CPU avec des dessins synthétiques et la photographie fournie ; elle n'a pas été testée sur une Cricut réelle. Le mode silhouette reste non validé tant qu'une IA n'a pas fourni une meilleure segmentation. Les travaux V20.2+ Florence-2/SAM2/BiRefNet et RTX 3070 sont **maintenus**.
