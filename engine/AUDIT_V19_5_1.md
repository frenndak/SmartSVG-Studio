# Contre-expertise V19.5.1 — conclusions

## Périmètre
Archive V19.5 publiée, sources des algorithmes de chevauchement et des nœuds ComfyUI, contrôles des PNG/MASK, workflow Express/Expert, suite de tests ciblés, archive réinstallée en environnement vierge.

## Défauts reproduits/confirmés dans le code d'origine

**P1 — Surallocation mémoire :** `propose_exclusive_masks` crée une carte de distance pour chaque masque, puis `np.stack(...)` et `np.sort(..., axis=0)`. Ces matrices grossissent linéairement avec le nombre de sujets. **Corrigé** avec deux minima incrémentaux et un index gagnant.

**P1 — Garde-fous incomplets dans le calcul de la proposition :** le contrôle strict du type, des dimensions et du budget mémoire était présent dans `analyze_overlaps`, mais absent de `propose_exclusive_masks` appelé directement. **Corrigé** en partageant une validation initiale.

**P2 — Insuffisance d'inspection :** le rapport donnait le nombre de pixels ambigus mais pas un aperçu propre à la proposition ni le ratio de pixels partagés attribués. **Corrigé** sans modifier les masques d'origine.

**P2 — Fichiers de masque issus de chemins non contrôlés :** la routine chargeait les chemins indiqués dans un rapport sans empêcher la sortie du répertoire de travail. **Corrigé** en limitant strictement à `03_MASQUES`.

**P2 — Manifeste chargé en mémoire :** le générateur historique lisait entièrement chaque fichier pour calculer son SHA-256. **Corrigé** en hachant par blocs dans le statut V19.5.1.

## Limites toujours ouvertes

- Les masques SAM2 et les boîtes Florence-2 ne sont pas validés en inférence réelle sur la RTX 3070. Les noms des modèles sont liés à l'interface RMBG et peuvent évoluer après une mise à jour du plugin.
- La séparation exclusive n'infère pas la profondeur ni les parties cachées. Elle peut être incorrecte pour des mains devant un objet semi-transparent. Elle ne doit pas alimenter automatiquement Cricut.
- La modification sémantique de texte, mains, verre, cheveux et effets de reflets n'est pas une fonctionnalité vérifiée.
- La compatibilité réelle de Design Space, les marges imprimables, le calibrage et la découpe physique restent non testés.
- Les tests ciblés photo ne remplacent pas tous les tests lourds du moteur vectoriel historique.

## Benchmark de performance reproductible (quatre masques synthétiques de 1 500 × 1 500 px)

| Mesure | V19.5 | V19.5.1 |
|---|---:|---:|
| Durée du calcul de proposition | 0,694 s | 0,158 s |
| Pic mémoire RSS du processus | 282,9 Mio | 175,9 Mio |
| Pixels partagés | 680 624 | 680 624 |
| Empreinte SHA-256 des quatre sorties | `27334dde...26052f` | Identique |

D'après ces deux exécutions CPU du même banc d'essai : environ **77 % de temps en moins** et **38 % de pic mémoire en moins**. Ce n'est **pas** une mesure GPU ni une garantie sur tous les jeux de masques. Le calcul et les modèles IA ne sont pas équivalents : ce benchmark ne mesure que la séparation géométrique.

## Tests élargis du moteur installé

- 69 tests historiques ciblés photo V19–V19.5 : réussis.
- 8 nouveaux tests V19.5.1 : réussis.
- 50 tests historiques des versions vectorielles V14.1–V18.1 : réussis.
- **Total : 127 tests réussis** dans cet environnement ; vraie exécution SAM2/Florence et Design Space non testées.
- Images réelles : `1000077453.png` (1229×1536) et `1000077462.png` (1152×1536) ; originaux sauvegardés à pixels identiques, aucune extraction sans masque, manifestes valides.
