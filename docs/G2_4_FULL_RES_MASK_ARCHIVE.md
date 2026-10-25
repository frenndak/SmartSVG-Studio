# G2.4 — Conservation exacte des masques de base en float32

Branche privée : feat/g2-4-lossless-base-masks. Dépend de G2.3 (#21), G2.2 (#19) et des PR précédentes. Micro-lot indépendant, sans fusion automatique.

## Pourquoi un PNG 8 bits ne suffit pas

Les masques ComfyUI originaux sont des tenseurs float32 [N,H,W] pouvant conserver des valeurs de transparence intermédiaires. Réécrire un masque en L8/PNG ne conserve pas ces valeurs au bit près ; le fingerprint V21.6 (image ET masques de base) changerait et empêcherait la reprise des coups de pinceau.

Ce lot utilise deux représentations dans le même .smartsvg :
- Un PNG en niveaux de gris **pleine résolution native** par masque, pour inspection visuelle uniquement (rééchantillonnage et retouche interdits).
- Une ressource snapshots/base_masks_float32_v1.zlib contenant les **octets float32 little-endian exacts**, compressés sans perte. La section base_masks_f32_v1 du document conserve shape [N,H,W], SHA-256 des octets restaurés, empreinte de l'image et fingerprint combiné V21.6.

Le format de base .smartsvg conserve la compatibilité du schéma smartsvg-project/1. L'extension est explicitement déclarée, contrôlée par le validateur de l'archive et interdite sans les masques PNG cohérents. Les anciens projets sans extension restent lisibles.

## Capture et restauration dans ComfyUI

Un nouveau nœud **SmartSVGProjectMaskVaultG24** est enregistré uniquement lorsque SMARTSVG_ENABLE_PROJECT_API=1 est activé sur une instance ComfyUI locale maîtrisée.

**Capture** : connecter l'IMAGE et éventuellement les MASK de base à ce nœud, indiquer un nom de projet existant, sélectionner « Capturer les masques », fournir le SHA-256 actuel de la révision (affiché dans le panneau Express) et lancer manuellement. Le nœud compare les pixels IMAGE au PNG original dans le projet, vérifie dimensions, nombre d'objets et valeurs finies, écrit les vrais float32 et leurs PNG d'inspection, puis produit une sortie MASK transmissible sans rééchantillonnage.

**Restaurer** : connecter l'IMAGE originale à ce nœud, sélectionner « Restaurer les masques » et fournir **le nouveau** SHA-256 de l'archive courante ; les masques exacts sont reconstruits depuis le fichier float32, vérifiés par SHA-256, puis leur empreinte image + masques est recalculée. Une IMAGE différente est refusée. La sortie MASK peut alors être reconnectée à l'éditeur V21.6. Les retouches sauvegardées dans G2.3 ne sont acceptées que si leur empreinte native correspond.

Le nœud G2.4 ne remplace pas le nœud éditeur V21.6. Il ne modifie aucun port historique. Il doit être inséré explicitement dans le workflow, puis utilisé pour alimenter l'entrée MASK de l'éditeur. L'utilisateur conserve ainsi un contrôle clair des opérations d'écriture.

## Limitations et sécurité

- Maximum : 32 masques, 5 Mpixels par masque et 8 millions de pixels de masques au total (float32 environ 32 Mo avant compression). Les grosses planches doivent être scindées en lots.
- Chaque ressource est vérifiée à la sauvegarde comme à l'ouverture ; décompression zlib bornée ; SHA-256 de la copie float32 ; contrôle des pixels finaux finie sur [-0.001,1.001]. Les PNG L8 doivent être exactement ceux dérivés du float32 compressé.
- Les PNG L8 servent à inspecter ; **la relecture travaille uniquement sur les octets float32**.
- L'API de projets reste désactivée par défaut et ne constitue pas un système d'authentification. À utiliser uniquement en local ou dans un ComfyUI contrôlé.
- Un projet G2.2 créé depuis un PNG dont les pixels ne correspondent pas au tenseur IMAGE connecté est refusé pour la capture ; l'utilisateur doit conserver sa source exacte.
- Pas de sauvegarde automatique à chaque exécution : la capture est un choix explicite et nécessite un SHA de révision à jour.
- Le format n'est pas une preuve d'import Design Space ou de découpe physique. Aucune certification Cricut ou SVG éditable n'est introduite.
- Cette PR inclut des tests synthétiques du codec et des archives ; des essais avec l'installation Windows, l'environnement torch complet, le GPU RTX 3070 et un vrai flux ComfyUI restent indispensables avant une publication.

## À poursuivre après G2.4

G2.5 : automatiser l'association entre le projet, le graphe ComfyUI et les contrôles ergonomiques tout en protégeant les révisions. Tester la reprise complète image + masques + coups de pinceau, et enrichir l'interface d'un chargement assisté du nœud.
