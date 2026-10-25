# SmartSVG G2.3 — Révisions de retouches natives V21.6 dans les projets .smartsvg

**Portée :** premier raccordement fiable du travail de l'éditeur graphique V21.6 aux projets locaux G2.2. Dépendance PR #19 → #18 → #17 → #16 → #15 → #14. Aucune modification de l'archive historique V21.15.2, ni des IDs ou des ports de nœuds ComfyUI.

## Commandes dans le nœud SmartSVGMaskEditorV216

Le nœud dispose désormais, en plus de son éditeur graphique historique, d'un champ « Projet .smartsvg » et de deux commandes :

1. « Enregistrer les retouches » : les traits du champ retouches_json sont vérifiés selon le contrat natif V21.6, puis sauvés dans le projet existant, avec version SHA-256 attendue et copie de secours.
2. « Recharger les retouches » : le contenu natif de ce projet est relu, comparé strictement au fingerprint fourni par le nœud V21.6 (image **et masques de base**), puis injecté dans le widget retouches_json **après confirmation**. Il faut relancer le workflow pour appliquer les nouvelles corrections.

L'absence d'empreinte compatible, le mauvais nombre de masques, les dimensions différentes ou un changement de connexion ComfyUI observable empêchent le chargement.

## Exactement ce qui est sauvegardé

Dans document.json de l'archive G1.3, une section editor_v216 contient les coups de pinceau, leurs coordonnées normalisées, les index d'objets, le rayon et le fingerprint natif (SHA-256). Le journal operations.json conserve un événement de révision. Toute écriture utilise la sauvegarde G1.4 avec vérification d'empreinte attendue **à l'intérieur du verrou**.

L'enregistrement reste non certifié : aucune preuve de coupe Cricut, d'import Design Space ou de transformation SVG éditable n'est créée.

**Limite décisive : les masques de base haute résolution ne sont pas encore contenus dans cette sauvegarde.** Le fingerprint natif est calculé sur l'image et sur les masques de base de l'exécution. Pour recharger les traits, l'utilisateur doit conserver ou recréer le même workflow et les mêmes masques de départ ; les aperçus du navigateur n'ont pas la résolution ou les octets permettant de reconstituer fidèlement ces masques. Il serait trompeur de dire que le lot restaure toute une session à partir du seul .smartsvg.

## Sécurité

- L'API de projets G2.2 est désactivée par défaut : SMARTSVG_ENABLE_PROJECT_API=1 uniquement sur une installation ComfyUI locale/contrôlée. Les POST restent protégés par le header custom et une vérification de l'origine ; cela n'est pas une authentification.
- Références aux seuls noms de projets gérés ; pas de chemin arbitraire côté navigateur.
- JSON V21.6 strict : version 1, empreinte source hexadécimale, dimensions et compte d'objets bornés, 400 traits, 1 500 points par trait, 12 000 points au total, 350 Ko en UTF-8.
- Rejet des champs non documentés, doublons JSON, nombres NaN/Inf et coordonnées hors [0,1]. Les traits ne sont jamais exécutés en tant que code.
- L'incompatibilité de fingerprint est validée dans le navigateur par decodeDocument(meta, text) **avant la confirmation** ; le backend ne peut pas authentifier un fingerprint fourni par le client.
- Une réécriture concurrente est bloquée par comparaison de SHA-256 du .smartsvg au moment de l'opération sous verrou.
- Une erreur de callback dans ComfyUI rétablit la valeur précédente du widget.
- L'éditeur natif conserve sa logique d'annulation/rétablissement ; le projet archive le document validé sauvegardé, pas la pile de redo temporaire non validée.

## Développements ultérieurs

Le prochain sous-lot devra sauvegarder les masques de base entiers directement depuis les tenseurs serveur (et non depuis les aperçus de 760 px), leur associer les SHA-256 du projet et les réinjecter après contrôles. Ensuite : retour complet dans une séance ComfyUI ou dans une interface autonome.

## Gate d'acceptation

Les tests Python vérifient l'enregistrement/rechargement réel dans des archives synthétiques, les limites de strokes, les dimensions, corruption, conflits et conservation des versions. Les tests Node.js vérifient les gestes utilisateur, empreintes incompatibles, refus sans confirmation, source modifiée, conservation des widgets historiques. Les anciens tests V21.6 du viewport doivent également continuer de passer.

Pas de preuve de test Windows / RTX 3070 / Design Space / coupe Cricut physique. PR maintenue en brouillon en attente des PR parentes et de leur revue.
