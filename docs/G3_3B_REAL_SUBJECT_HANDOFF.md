# G3.3b — Vrais sujets et fragments G2.6 dans l'Atelier Express

## Résultat livré

L'inspecteur de nœud existant `SmartSVGChooseSubjectV21154` fournit déjà le tableau `smartsvg_subjects_v21154` avec :
- une empreinte `source_sha256` de l'image et des masques, les dimensions en pixels et au plus 32 sujets ;
- pour chaque masque, une vignette PNG, des codes d'avertissement et jusqu'à 12 rectangles de fragments à inspecter ;
- aucune suppression de micro-fragment ou modification automatique du masque.

Le grand Atelier Express peut maintenant **recevoir et afficher ce diagnostic réel**, sans le confondre avec sa planche de 12 escargots fictifs.

## Parcours volontaire (sans IA cachée)

1. Dans l'Atelier Express sous le même serveur ComfyUI, cliquer **Recevoir une inspection (90 s)**.
2. Dans l'onglet ComfyUI, connecter et exécuter manuellement le nœud **Inspecter et choisir les silhouettes V21.15.4** ; après le résultat, cliquer **Envoyer le dernier diagnostic vers l'Atelier**.
3. Revenir à l'Atelier : voir les vraies vignettes, avertissements, nombre de zones et coordonnées de source.
4. Utiliser les boutons de présélection pour **préparer sa revue** ; cette présélection est **locale à l'Atelier**, elle **ne modifie ni le masque, ni le widget numero_sujet, ni le workflow**. La sélection exécutable reste celle du nœud ComfyUI. Pour supprimer le rapport de la mémoire de cet onglet, cliquer Effacer.

L'Atelier ne déclenche ni segmentation IA, ni queue automatique, ni POST. Le diagnostic transite par `BroadcastChannel` **entre onglets du même origin** uniquement, et seulement après des actions explicites. Pas de stockage local, pas d'upload d'image et pas de persistance au disque ; le canal est fermé après réception ou au bout de 90 secondes. Les autres extensions qui partagent la même origine sont néanmoins techniquement capables d'observer ce canal : réserver ce mécanisme à une installation ComfyUI de confiance, jamais à une page de prévisualisation tierce.

## Contrats de sûreté

`smartsvg_subject_handoff_g33.mjs` valide *avant affichage* :

- version et type exacts du message, SHA-256 64 caractères hexadécimaux, dimensions positives sous 5 millions de pixels ;
- 1–32 objets exactement, indices uniques dans la limite annoncée, vignette **PNG base64 seulement** ;
- limite 700 000 caractères par vignette et 4 Mio cumulés, avertissements parmi les codes G2.6 connus ;
- zones source et 88 px bornées, jusqu'à 12 zones/objet ;
- affichage avec `textContent` et éléments DOM séparés, pas d'injection de SVG/HTML utilisateur.

Le rapport affiche son empreinte de source pour permettre une vérification manuelle de provenance, **sans authentifier cryptographiquement l'émetteur**, ni prouver que les masques de l'éditeur actuel sont identiques. Aucun bouton de focus automatique n'est émis vers un autre onglet. Les alertes demandent une inspection humaine et ne suppriment aucune forme.

## Limites et suite

- Ce lot **ne transporte pas les masques float32 ni l'image d'origine pleine résolution** ; il affiche le vrai rapport et les vignettes du nœud existant. La connexion automatique des projets, de l'état d'édition et de la sélection exécutable viendra dans G3.3c/G3.3d.
- Si aucun rapport n'est disponible, si `BroadcastChannel` manque ou si les onglets ne partagent pas exactement la même origine, un message explicite apparaît. La maquette hors ligne `file://` demeure utilisable pour ses fonctions démonstratives.
- Aucun test Windows/ComfyUI visuel, RTX 3070, Cricut Design Space ni Explore 5 n'est réalisé par cette PR.

## Vérifications

- `engine/tests/test_g33_subject_handoff.mjs` : message réel normalisé, limites 32/5M/4M, injection PNG/SVG/URL rejetée, zones bornées, sélection volontaire.
- `tests/test_g33b_real_subjects.py` : admission de la suite JS et contrôles de raccordement.
- Suites historiques de nœud inspecteur, G3.0, G3.1, G3.2, G3.3a et G0/CPU requises avant fusion.

**Déploiement** : prototype produit interne expérimenté, pas encore un parcours tout-en-un utilisable sans nœuds ComfyUI. Voir le critère de prêt-pour-première-recette dans l'issue #51.

## G3.3c-a — Examen ciblé des fragments (lot expérimental)

Pour chaque zone suspecte déjà identifiée par le vrai nœud G2.6, l'Atelier ajoute un bouton clavier « Examiner zone ». L'action annonce les coordonnées en pixels source et met en évidence le rectangle de la vignette 88 px ; le dernier repère remplace le précédent. Les contrôles restent bornés par la validation G3.3b (32 sujets × 12 zones affichées). Effacer ou recevoir un nouveau diagnostic efface les repères précédents. Aucun pixel, masque, sujet sélectionné, projet .smartsvg ou nœud ComfyUI n'est modifié.

Preuve requise : test DOM Node de deux zones successives, d'états `aria-pressed` et de leur effacement, plus tests G0/CPU sur HEAD et merge synthétique. Les boutons natifs sont accessibles au clavier, mais une recette visuelle navigateur et le runtime Windows restent à réaliser. Ce lot ne fournit pas encore le transfert des masques float32, la liaison automatique au projet ou la sélection exécutable ; G3.3c/d et G3.4 restent partiels. Retour arrière : revert de la PR sans migration de données.
