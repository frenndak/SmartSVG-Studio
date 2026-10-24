# SmartSVG Studio V21.12.1 — Contre-expertise indépendante et suites

## Objectif

Améliorer le routage automatique et les diagnostics de masque sans casser les exports Cricut V21.12. Le logiciel est **bêta** et l'inférence GPU ou la découpe physique n'ont pas été exécutées dans cette session.

## Évaluation des neuf images utilisateur (mode sans IA)

| Exemple | Sortie sans IA | Portée |
|---|---:|---|
| Fille manga photographiée | 0 | scène opaque, orientation IA |
| 12 escargots sur fond blanc | 12 propositions | segmentation de sujets réussie, export PNG/SVG local 12 vérifié |
| Illustration cadeau + texte | 0 | scène complexe, aucune lecture OCR revendiquée |
| Leprechaun en photo | 0 | photo réelle, détourage IA nécessaire |
| Affiche fantasy A | 0 | affiche avec texte/personnages |
| Affiche fantasy B | 0 | affiche avec texte/personnages |
| Homme en atelier | 0 | photo réelle avec détails fins |
| Couverture manga coréenne | 0 | typographie et personnage confondus dans l'image |
| 24 personnages Pokémon sur fond noir | 24 propositions | trois petits éléments secondaires potentiellement absents ; vérifier chaque masque |

Le routage décrit la structure de l'image, **pas** son sens. Une découpe alpha propre ne prouve pas que le bon sujet est isolé. Une IA simulée dans les tests ne prouve pas que BiRefNet/SAM2 fonctionne sur une RTX 3070 8 Go.

## Priorités V21.12.1

- **P0** : ne jamais convertir un fond sombre quelconque en sticker « prêt » ; garder garde-fous et indications explicites.
- **P0** : stabiliser le détourage 24 Pokémon en tant que proposition de masques ; conserver les 12 escargots sans régression.
- **P1** : fournir qualité géométrique machine-lisible et distinction « à vérifier » / « correction prioritaire ».
- **P1** : optimiser la mémoire d'une planche 24 avant export haute résolution, en limitant le nombre de buffers full-frame et les cas VRAM.
- **P2** : unification du panneau Express et gestion des textes quand le modèle IA le permet (à confirmer, **pas de promesse OCR**).

## Critères de validation avant étape suivante

1. Neuf images catégorisées ; deux planches reconnues comme cas favorables sans IA.
2. Les modes IA « Désactivée », « Si disponible », « Obligatoire » conservent le même sens et ne déclenchent aucun modèle dans le diagnostic.
3. Les 24 Pokémon restent séparés et numérotés dans l'ordre de lecture ; fragments éventuellement ignorés signalés.
4. L'exemple escargots sort 12 fichiers PNG individuels conformes au précontrôle Cricut local (non certifié physiquement).
5. Les nouveaux nœuds n'altèrent aucun moteur ni identifiant historique.
6. Un échec de segmentation IA ou un masque faux provoque un refus clair, jamais un rectangle déclaré comme détourage.

## Point non validé lors de cette livraison

Le test de fabrication **complète** des 24 Pokémon a dépassé le délai d'exécution de contrôle, même si les 24 masques étaient détectés. Il faut profiler les étapes d'export, les deux planches et le post-traitement HD, puis mesurer les temps et la mémoire, idéalement dans ComfyUI sur le PC cible. Pas de certification de Print Then Cut tant que ce test n'est pas passé dans Design Space.
