# SmartSVG Studio V21.7.1 — Audit de qualité automatique

**Base étudiée :** archive V21.7 fournie. **Livrable :** nouveau nœud Express `SmartSVGExpressV2171` et exports PNG HD additionnels sans changement des cinq réglages.

## 1. Contrat du nœud

- Même ensemble de cinq réglages Express historiques + entrée IMAGE et entrée facultative MASK ; trois sorties inchangées.
- Le nouveau nœud est indépendant : les anciens identifiants de nœuds/workflows restent enregistrés.
- En cas d'erreur de fabrication, l'erreur reste visible. En cas d'erreur de qualité HD après une fabrication correcte, la sortie historique reste disponible.

## 2. Stratégie automatique, sans modèle IA supplémentaire

- Chaque PNG « imprimer/découper » produit par Express peut obtenir une **copie HD à 600 ppp** dans `06_HD_AUTOMATIQUE_V21_7_1` ; à 300 ppp, le rapport de pixels est ~2 ; à 450 ppp, ~1,33.
- Rééchantillonnage Lanczos avec couleurs prémultipliées pour limiter les franges aux bordures transparentes.
- Accentuation RVB **très légère** et limitée à l'intérieur opaque lorsque les contrôles ne détectent pas de bruit excessif ou une modification trop forte. Sinon, rééchantillonnage seul.
- L'alpha est contrôlé par comparaison conservatrice (IoU >= 98,5 % après retour à la taille originale) ; en cas de divergence, le PNG HD est ignoré.
- Aucune IA téléchargée, aucun upscale génératif : **des pixels plus nombreux ne signifient pas de nouveaux détails réels**.

## 3. Protection Cricut

- Les **PNG et SVG de fabrication d'origine ne sont jamais écrasés**. Le SVG garde exactement sa géométrie ; l'alpha du PNG d'origine n'est pas altéré.
- Les copies HD peuvent être utilisées pour des besoins d'impression/retouche, mais la découpe physique dépend toujours des masques et contours vérifiés dans Design Space.
- **Cricut peut ignorer les informations ppp** : contrôler manuellement la largeur en mm.
- Les planches déjà produites restent inchangées : les copies HD sont générées **par sujet**, pas comme une nouvelle grande planche, pour limiter la mémoire.

## 4. Limites et sécurité

- Maximum 5 millions de pixels lus par PNG d'origine, 6 millions de pixels par dérivé HD et 50 millions par traitement ; 32 sujets au maximum.
- Les fichiers d'entrée sont vérifiés comme PNG situés dans le dossier projet, sans lien symbolique ni sortie hors du dossier ; pas d'écrasement silencieux des exports HD existants.
- Échec isolé par fichier : statut `complete`, `partielle` ou `ignore` avec raison dans `RAPPORT_HD_V21_7_1.json` et dans le JSON du nœud.
- Un rapport complémentaire est écrit indépendamment ; les rapports historiques ne sont pas modifiés.

## 5. Tests effectivement réalisés

| Groupe | Résultat |
|---|---:|
| Python suites historiques 1–6 | **666/666** |
| Python V21.7.1 (nouveaux cas) | **12/12** |
| JavaScript historiques | **35/35** |
| **Total** | **713/713** |

Couverture : identité SHA-256 des PNG/SVG anciens par rapport à Express V21.5.1 sur image synthétique, ratios HD 300→600 et 450→600, conformité alpha, import/export des nœuds, traitement synthétique 12 sujets, refus des dossiers externes/symboliques, seuils mémoire, panne d'amélioration, transparence douce, aperçu des sept exemples fournis.

La suite historique n°3 a dû être lancée en deux sous-groupes (136 et 91 tests) pour rester dans le délai d'exécution autorisé par l'environnement de tests. Les deux sous-groupes ont réussi.

## 6. Check-up des sept images fournies

Les sept images ont été chargées depuis les fichiers utilisateur, réduites à une taille de test, puis soumises au moteur de redimensionnement et de légère accentuation. Leurs variantes RGBA ont passé le contrôle de conservation de la zone alpha. **Cela valide le moteur de retouche raster, pas la qualité de leur détourage réel**.

| Visuel | Gain potentiellement utile | Limite inchangée |
|---|---|---|
| Dessin manga photographié | Lissage du rééchantillonnage / netteté modeste | Trame d'écran / moiré non résolus |
| 12 escargots | Images individuelles HD après détourage | Pointillés, multiples contours à isoler |
| Illustration cadeau et texte | Agrandissement d'impression | Caractères non reconnus et non modifiables |
| Personnage avec chopes | Contours imprimés plus fins en raster | Interstices et transparence à segmenter |
| Affiche fantasy complexe | Sortie raster de meilleure densité si budget respecté | Détails de fond/texte non vectorisés proprement |
| Canard dans capture mobile | HD après détourage/recadrage V21.7 | UI du téléphone non supprimée par le module HD |
| Personnage devant PC en feu | Amélioration douce des contrastes locaux | Fumée/feu difficiles pour le masque |

## 7. Limites non validées

- Absence de test sur frontend ComfyUI réel, Nodes 2.0 et PC utilisateur RTX 3070.
- Absence d'inférence réelle SAM2 / Florence-2 et de découpe physique Cricut Explore 5.
- La V21.7.1 n'est pas un upscaler neuronal et ne peut pas créer fidèlement des détails inexistants.
- Aucune garantie de correspondance à la taille finale sans contrôle dans Design Space.

**Verdict :** amélioration automatique prudente et non destructive testée au niveau Python/JavaScript. Pour les dessins très dégradés, un futur upscaler facultatif pourrait être pertinent seulement après validation de non-régression des masques.
