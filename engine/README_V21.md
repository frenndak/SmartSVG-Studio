# SmartSVG Studio V21.0 (bêta) — Unification des profils et découpe par masques

## Installation

1. **Fermer ComfyUI**. Retirer les anciennes versions SmartSVG du répertoire `custom_nodes` (ne pas conserver V20.6 et V21 ensemble).
2. Décompresser `ComfyUI-SmartSVG-Studio-V21.0` dans `custom_nodes`.
3. Redémarrer ComfyUI. Charger l'un des fichiers `example_workflows/SmartSVG_Studio_V21_*.json`.
4. La conversion des images et les tests historiques utilisent `numpy`, `Pillow`, `opencv-python`, et `torch` déjà présent dans ComfyUI. Pour la segmentation interne, l'extension **ComfyUI-RMBG** doit fournir le nœud `SAM2Segment`, et ses modèles doivent être présents ou téléchargés.

## L'interface : 7 paramètres visibles + 1 prise MASK facultative

- `dossier_sortie` : dossier global où enregistrer les créations.
- `profil` : auto / affiche / logo_cartoon / planche_multi / capture_produit / scene_decorative.
- `operation` : `sticker_contour` (PNG détouré, contour externe) ou `carte_rectangle` (visuel complet, sans segmentation).
- `largeur_mm` : largeur cible du sujet ou du visuel.
- `qualite_ppp` : 300 ou 450 ppp **de sortie**. Cela n'augmente pas le détail source.
- `grille_multi` : 6×4, 4×3, 3×3 ou estimation pour les planches uniformes.
- `segmentation_ia` : `desactiver` (par défaut), `si_disponible`, `forcer`.
- `masques_objets` : entrée **facultative** d'un lot ComfyUI `MASK` de la même dimension que la SOURCE image, obtenus avec un modèle segmentation (SAM2, RMBG, etc.). Ces masques **priment** sur l'IA interne.

⚠️ **Ne pas brancher le MASK de `LoadImage` d'une image JPG opaque** à l'entrée `masques_objets` ; il est généralement vide. Brancher la vraie sortie d'un segmentateur.

## Quel workflow pour chaque cas ?

| Workflow | Comportement |
|---|---|
| `V21_Auto_prudent` | Conserver l'image ou appliquer l'ancien profil auto **sans lancer l'IA** |
| `V21_Pokemon_24` | 24 vignettes sur fond uniforme, comme V20.6 ; coupe indépendante à vérifier |
| `V21_Courage_IA` | Appel SAM2 prompt `dog` ; fallback vers le cadre si absent |
| `V21_Canard_IA` | Appel SAM2 prompt `duck` ; fallback vers le cadre si absent |
| `V21_Renards_IA` | Appel SAM2 prompt `fox` ; résultat peut regrouper les 3 sujets |
| `V21_Affiche_cadre` | Image complète découpée au format cadre, **sans lancer de modèle** |
| `V21_Masques_externes` | Brancher un ou plusieurs masques existants au dernier port |

Les modèles ne reconnaissent **pas nécessairement les éléments** demandés : un masque mal positionné doit être corrigé/retiré avant découpe. Le mode externe ne mesure pas la qualité sémantique et n'affirme jamais « validé ».

## Exports V21

### Masques fournis ou SAM2 fonctionnel

Dans `SmartSVG_V21_<identifiant>/` :

- `SOURCE_ORIGINALE.png` : source RGB/RGBA intacte.
- `01_OBJETS/OBJET_XX_DETOURE_TRANSPARENT.png` : pixels originaux avec alpha issu du masque. A la résolution native, non interpolée.
- `01_OBJETS/OBJET_XX_IMPRIMER_DECOUPER_VERIFIER.png` : PNG à sous-couche blanche + marge (300/450 ppp), **une silhouette externe**.
- `02_CONTOURS/OBJET_XX_CONTOUR_SEUL.svg` : contour SVG en unités physiques mm, **aucune ligne des yeux ou des cheveux à découper**.
- `03_PLANCHES/PLANCHE_XX_VERIFIER.png` : planches multi-objets transparentes, sans réduction de leurs dimensions individuelles ; limites conservatrices de placement ~170 × 240 mm. La vraie zone autorisée varie selon Cricut Design Space.
- `04_CONTROLES/APERCU_SUJETS.png` et `RAPPORT_V21.json` : audit des objets, superpositions, doublons, régions incertaines et agrandissements.

Les masques multiples arrivant dans une même scène sont traités comme des propositions. Le moteur signale les doublons, petites surfaces et grands recouvrements. Il n'attribue pas automatiquement un ordre de profondeur (personne/objet devant).

### Sans masque

Le moteur V20.6 reste inchangé et produit **les mêmes PNG et SVG** dans un dossier `SmartSVG_V20_6_<identifiant>/`. Le rapport `RAPPORT_V21.json` y est ajouté et déclare explicitement qu'aucune segmentation sémantique n'a eu lieu. Le profil `planche_multi` conserve l'extraction 24 Pokémon sur fond noir/blanc, sans utiliser d'IA.

### Mode `carte_rectangle`

Priorité absolue au choix de **cadre rectangulaire** : les masques sont ignorés, l'IA interne n'est pas appelée, et un avertissement est inscrit au rapport.

## Principe Cricut

**Sticker imprimé =** charger le PNG `IMPRIMER_DECOUPER`, choisir l'opération *Imprimer puis découper* ; vérifier **taille, bord externe et nombre d'îlots** dans Design Space. Ne pas superposer le SVG contour au PNG imprimé si cette superposition provoque une double coupe.

**Découper chaque trait =** utiliser les workflows Line Art historiques V20.1.2 à V20.5 (toujours enregistrés) et importer le SVG de traits correspondant en **Découpe de base**. Le nœud simple V21 ne mélange pas ce mode avec l'impression de stickers pour éviter une mauvaise découpe.

## Sécurité et limitations de la bêta

- Les sorties PNG sont définies à 300 ou 450 ppp, **sans reconstruction de détails perdus**.
- Si les masques sont absents, le moteur n'invente pas la séparation de Courage, du canard ou des 3 renards.
- `segmentation_ia=si_disponible` lance réellement l'IA uniquement si le garde-fou CUDA préalablement disponible l'autorise ; sinon retour au profil V20.6 documenté. `forcer` produit une erreur si cela échoue.
- **L'inférence des vrais modèles sur RTX 3070 8 Go n'a pas été vérifiée dans l'environnement de développement.** Les tests IA utilisent un fournisseur simulé ; aucune preuve de précision photographique ne peut être tirée de ces tests.
- Les visuels de démonstration avec masques synthétiques ne sont pas des résultats de SAM2.
- L'intégration Cricut réelle, la découpe des petits détails, et l'échelle exacte importée dans Design Space restent à vérifier sur la machine.

## Vérification locale de l'archive

Dans le répertoire extrait, lancer :

```bash
python verify_package_v21.py
```

Ce script vérifie les sommes SHA-256, tous les anciens modules V20.6, les sept workflows V21, la présence des nœuds historiques et toutes les suites unitaires.
