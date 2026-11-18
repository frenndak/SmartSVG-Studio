# SmartSVG Studio — contre-expertise de l’existant et de la roadmap V3.5

**Date du contrôle** 18 novembre 2026, heure de Paris.

**Dépôt et révisions** [main 3a5c44d](https://github.com/frenndak/SmartSVG-Studio/commit/3a5c44d528a90c765e0bf7be581cf845f6ba92d2), [PR code 167](https://github.com/frenndak/SmartSVG-Studio/pull/167), [PR roadmap 168](https://github.com/frenndak/SmartSVG-Studio/pull/168) et [PR code 169](https://github.com/frenndak/SmartSVG-Studio/pull/169). Les trois PR sont ouvertes en brouillon au moment du contrôle.

**Périmètre** Application Windows prévue, point d’entrée natif Tk, moteurs et formats existants, expérience Cricut et roadmap V3.5. Les vérifications des gestes et des transitions détaillées ci-dessous concernent les révisions épinglées. La matrice de 80 fonctions examine leur conception et leur raccordement visible : elle n’est pas une exécution de 80 recettes produit. Les statuts sont une photographie datée ; la référence de pilotage demeure EXECUTION_STATE.json et les preuves exact-head. Tous les critères hérités restent applicables.

## Suivi des correctifs préparés

La [PR 169](https://github.com/frenndak/SmartSVG-Studio/pull/169), au HEAD `f8400ffd5b7ed9ff464cf04c29ddb36da11d88fa` lors de cette mise à jour, contient une tranche candidate W02/W13. Elle est **en brouillon et non fusionnée**. Les constats détaillés ci-dessous restent les observations initiales sur les révisions qui y sont indiquées ; ils ne décrivent pas automatiquement le comportement des versions ultérieures.

| Constats | Avancement dans la PR candidate | À poursuivre |
|---|---|---|
| F01 · Navigation et notes | Les notes attendent la fermeture du pinceau ; la création demande confirmation et ferme le panneau avant l’écriture. Une écriture en cours bloque l’ouverture d’une nouvelle retouche. | Qualifier les autres transitions, notamment la récupération, et étudier une synchronisation conservant simultanément les deux brouillons. |
| F02 · Enregistrement incertain | Le brouillon reste visible. Une nouvelle prévisualisation en lecture seule rétablit la possibilité d’enregistrer seulement si la révision et le sujet sont encore vérifiés ; une confirmation et les contrôles du writer restent exigés. Si la première écriture a abouti ou si le projet a changé, la reprise est refusée. | Réconcilier un résultat déjà écrit ; permettre de conserver et reprendre le brouillon après changement de révision ou redémarrage. |
| F03–F04 · Gestes et Échap | Un nouveau geste conserve le précédent ; Échap annule le geste courant tout en gardant les zones antérieures. | Rendre l’historique des gestes plus naturel et vérifier l’ergonomie sur le bureau Windows réel. |
| F05 · Budgets | L’interface vérifie le plafond global de 256 points avant la prévisualisation ; elle conserve le brouillon si un nouveau geste dépasse le budget. | Un geste de plus de 64 points reste interrompu et signalé. Étudier un découpage ou une simplification dont la fidélité est mesurée et qui conserve le geste complet. |
| F10 · Libellés | Les sauts de ligne et l’avis sur la disponibilité de la retouche sont corrigés dans la PR. | Noms et miniatures des sujets, version du build et autres états à qualifier dans W13. |

Les autres points, notamment premier sujet et export, grandes planches, import multiformat, zoom et superposition, restent des travaux à réaliser. Les résultats de CI du HEAD courant sont à relire sur GitHub ; une ancienne réussite ne valide pas un nouveau commit.

## Verdict

La V3.5 décrit largement le produit visé. Le premier parcours Windows est encore interrompu entre l’import et la fabrication. Un nouveau PNG peut être enregistré, mais le bureau ne crée pas encore son premier sujet à retoucher et ne déclenche pas le premier export d’autocollant.

Les problèmes les plus urgents portent sur **la conservation des retouches**. La PR 169 améliore plusieurs sorties du pinceau, mais deux autres actions ferment encore un brouillon sans avertissement. Un échec de sauvegarde peut aussi effacer les zones accumulées. Des gestes successifs, la touche Échap et les limites de points demandent une correction avant de qualifier l’Atelier.

La gestion mémoire doit être traitée tôt pour les usages de planches. La limite V1 actuelle porte sur **le nombre de masques multiplié par toute la surface de l’image**. Une page A4 à 300 ppp dépasse déjà le plafond de taille d’un masque de projet V1. Plusieurs images de 12 ou 24 sujets atteignent le plafond global même quand le nombre de sujets reste inférieur à 32.

La précédente contre-expertise apporte un inventaire utile des fonctions. Cette passe ajoute des reproductions et un essai visuel de l’interface. Elle corrige aussi un constat antérieur sur la virgule décimale.

## 1. Éléments et preuves vérifiés

| Contrôle | Résultat et portée |
|---|---|
| V3.5 active | Le dépôt désigne V3.5 comme référence de développement. Le curseur vise W02/W13. Les documents de la PR 168 seront intégrés à la branche principale après son traitement. |
| Inventaire et sources | Les contrôleurs existants passent sur 80 capacités UX, 17 unités, 141 exigences, 140 tickets et 437 scénarios inventoriés. L’archive d’origine V21.15.2 passe son contrôle de 651 empreintes. Ces nombres décrivent des inventaires et des contrôles documentaires. |
| Suite locale sur la PR 169 | **881 cas recensés, 838 réussis, 43 ignorés faute d’affichage, zéro échec**, sous Linux et Python 3.12.14. Les reproductions présentées ci-dessous ont été exécutées à part. |
| CI GitHub de la PR 169 | G0, contrôles CPU, prévol et stabilité réussis. Le [journal Windows](https://github.com/frenndak/SmartSVG-Studio/actions/runs/44285970214/job/134738634371) montre **879 réussites et 2 tests ignorés**. Le test Tk ajouté pour la fermeture et le sélecteur réussit sur ce runner. |
| Essai visuel | Interface Tk de la PR 169 ouverte sous Linux sur deux projets synthétiques. Observation de l’Atelier, de la fenêtre de retouche et de deux gestes successifs. L’essai ne qualifie pas l’accessibilité Windows, la RTX ou la découpe physique. |
| Formats d’entrée | Un exemple PNG, JPEG et WebP a été présenté localement au port de création. Le PNG a créé un projet sans sujet ; les exemples JPEG et WebP ont été refusés. Aucun fichier utilisateur n’est inclus dans le dépôt. |
| Distribution | L’[Alpha Windows du 14 novembre](https://github.com/frenndak/SmartSVG-Studio/actions/runs/43621278755) existe encore comme artefact expérimental. Elle précède les retouches ajoutées ensuite. Aucune version officielle n’apparaissait dans les Releases lors de cette lecture. |

Les scores de tests montrent l’état des scénarios qu’ils exercent. Les deux pertes de brouillon reproduites ci-dessous montrent pourquoi le contrôle entre fonctionnalités doit être ajouté en plus des tests déjà verts.

## 2. Défauts confirmés à corriger en priorité

### F01 — Deux transitions peuvent encore fermer le brouillon sans confirmation

**Priorité élevée · PR 169 · Reproduit avec une archive V1 réelle et des widgets simulés**

- Ouvrir un sujet, commencer une retouche, puis enregistrer une note. La note est enregistrée. Le rechargement du projet ferme le panneau de retouche sans demander si le brouillon doit être conservé.
- Ouvrir un sujet, commencer une retouche, puis créer un nouveau projet. Le nouveau projet est créé et le panneau de retouche est fermé sans avertissement.

Dans les deux cas, la reproduction a constaté zéro dialogue de confirmation et la fermeture du brouillon. Les octets du projet ont été manipulés par le writer réel dans un dossier temporaire. La reproduction reste à refaire sur le bureau Windows réel.

**Correction proposée.** Centraliser l’autorisation de changer de session ou de révision. Enregistrer une note peut conserver le brouillon en mémoire, puis l’associer à la nouvelle révision après relecture si sa source et son masque sont toujours les mêmes. Si cette réconciliation n’est pas possible, garder le brouillon inspectable et demander à l’utilisateur comment poursuivre. La création d’un autre projet demande une décision avant de remplacer la session active. La restauration d’un projet et les autres actions qui déclenchent une relecture doivent emprunter la même logique.

**Recette.** Deux zones, une note modifiée et deux sujets. Enregistrer la note, créer un projet, déclencher F5, ouvrir un autre projet et essayer la récupération. Tester retour, abandon explicite, changement externe de révision et fermeture pendant un traitement. Vérifier les notes, les zones, les deux sujets et les fichiers avant/après. [Rechargement de session](https://github.com/frenndak/SmartSVG-Studio/blob/7e82990af468d960c5678edfb93f75f85fac523b/engine/standalone_desktop_v34.py#L235) · [Création d’un projet](https://github.com/frenndak/SmartSVG-Studio/blob/7e82990af468d960c5678edfb93f75f85fac523b/engine/standalone_desktop_v34.py#L377) · [Fermeture du pinceau](https://github.com/frenndak/SmartSVG-Studio/blob/7e82990af468d960c5678edfb93f75f85fac523b/engine/native_atelier_tk_v34.py#L170)

### F02 — Un échec d’enregistrement efface les zones déjà constituées

**Priorité élevée · main et PR 169 · Reproduit au niveau du panneau avec une erreur d’écriture simulée**

Avec deux zones en brouillon, une erreur renvoyée par le writer provoque l’effacement des zones déjà ajoutées et invalide l’identité du sujet dans le panneau. Le dernier geste peut rester dans les variables locales, mais il ne dispose plus de sa liaison de travail. Le message demande de réexaminer le projet.

**Correction proposée.** Garder une copie du brouillon visible et exportable localement tant que l’état de l’écriture n’a pas été réconcilié. Afficher si le projet a changé et si une relecture est nécessaire. Recalculer l’aperçu pour la nouvelle révision avant toute nouvelle sauvegarde. Le programme doit déterminer si la première écriture a réellement abouti avant de proposer de la rejouer.

**Recette.** Provoquer disque plein, conflit de révision, exception et reçu manquant après deux zones. Contrôler d’abord l’état réel du projet et du secours, puis la restitution des zones et le recalcul. [Traitement des erreurs de sauvegarde](https://github.com/frenndak/SmartSVG-Studio/blob/7e82990af468d960c5678edfb93f75f85fac523b/engine/native_brush_draft_tk_v34.py#L649)

### F03 — Le geste précédent disparaît lorsqu’on commence le suivant

**Priorité élevée · main et PR 169 · Reproduit en code et observé dans Tk sous Linux**

Après un premier trait, un nouveau clic dans le canevas remplace la liste des points du geste courant. Le premier trait disparaît si l’utilisateur n’a pas d’abord cliqué sur **Ajouter cette zone**. Il n’est pas présent dans le rétablissement local.

**Correction proposée.** À la fin d’un geste, ajouter automatiquement une zone au brouillon lorsque celle-ci est valide. Conserver des commandes **Annuler le geste** et **Rétablir**. Si une limite de traitement est atteinte, préserver le travail déjà dessiné et proposer une suite claire.

**Recette.** Dessiner trois traits sans passer par un bouton intermédiaire, puis annuler et rétablir les derniers gestes. Comparer leur ordre, leurs modes et leurs pixels après réouverture. [Gestion du clic suivant](https://github.com/frenndak/SmartSVG-Studio/blob/7e82990af468d960c5678edfb93f75f85fac523b/engine/native_brush_draft_tk_v34.py#L349)

### F04 — Échap efface tout le brouillon

**Priorité élevée · main et PR 169 · Reproduit au niveau du panneau**

Avec une zone déjà constituée et un nouveau geste, Échap efface les deux, y compris les possibilités locales de rétablissement. La PR 168 prévoit qu’Échap interrompe le geste actif et que l’abandon de toutes les zones passe par une action dédiée ou réversible.

**Correction proposée.** Donner une portée claire à Échap selon le focus. Fermer d’abord le dialogue actif, puis interrompre le geste en cours. Conserver les zones antérieures. Une commande « Effacer le brouillon » doit rester explicitement réversible ou demander confirmation si elle détruit le travail.

**Recette.** Trois zones, dont une dans l’historique de rétablissement. Utiliser Échap pendant le geste, hors geste, pendant le calcul et dans un champ de saisie. Vérifier les zones conservées et le focus. [Raccourci actuel](https://github.com/frenndak/SmartSVG-Studio/blob/7e82990af468d960c5678edfb93f75f85fac523b/engine/native_brush_draft_tk_v34.py#L751) · [Contrat UX proposé](https://github.com/frenndak/SmartSVG-Studio/blob/44feb9901cc0fc7ae1641fb683af1550f1811b64/docs/roadmap-v3.5/UX_INTERACTION_AND_VISUAL_CONTRACT.md#L66)

### F05 — Les limites de points du pinceau ne concordent pas

**Priorité élevée · main et PR 169 · Reproduit**

L’interface permet jusqu’à 16 zones et jusqu’à 64 points par zone. Le moteur de prévisualisation accepte au maximum 256 points sur l’ensemble des zones. Un brouillon de **cinq zones totalisant 257 points** a été accepté dans l’interface de travail puis rejeté par le moteur avec `INVALID_PREVIEW_STROKE`. Le message présenté reste générique.

Un geste qui reçoit un 65e point passe également en dépassement et ne peut plus être prévisualisé tant qu’il n’a pas été modifié.

**Correction proposée.** Unifier les budgets entre interface, aperçu et sauvegarde. Rendre le suivi du nombre de points compréhensible uniquement lorsqu’une limite approche. Ajouter un échantillonnage ou une simplification géométrique contrôlée, avec tolérance mesurée sur les pixels du masque et sans déformation silencieuse. Préserver le geste complet jusqu’à ce que l’utilisateur accepte le résultat.

**Recette.** Tester 255, 256 et 257 points, 63, 64 et 65 points sur un geste, les virages serrés, les gestes longs et les limites après Undo/Redo. Vérifier l’écart sur les pixels et sur la découpe à deux tailles. [Limites de l’interface](https://github.com/frenndak/SmartSVG-Studio/blob/7e82990af468d960c5678edfb93f75f85fac523b/engine/native_brush_draft_tk_v34.py#L31) · [Limite totale du moteur](https://github.com/frenndak/SmartSVG-Studio/blob/7e82990af468d960c5678edfb93f75f85fac523b/engine/smartsvg_core/subject_brush_preview_g33e.py#L21)

### F06 — Le parcours d’un PNG neuf n’atteint pas la retouche

**Priorité élevée · main · Reproduit sur un PNG local et des fichiers synthétiques**

Un projet créé depuis un PNG contient zéro sujet, zéro masque et zéro export. L’outil de retouche attend un sujet déjà lié à un masque vérifié. Les profils « Planche 12 » et « Planche 24 » enregistrent une intention initiale. Ils ne produisent pas les sujets au moment de la création.

**Correction proposée.** Dans l’Atelier vide, proposer **Sélectionner un sujet**. Sur une image transparente, l’alpha peut servir de première proposition si sa silhouette est exploitable. Sur une image opaque, offrir une sélection manuelle avec aperçu et correction. Confirmer la liaison source/masque/sujet avant de l’enregistrer, puis rouvrir le projet et vérifier la même identité. Prévoir la reprise si l’écriture du masque réussit et que l’enregistrement du sujet s’interrompt ensuite.

**Recette.** PNG transparent, PNG opaque, image vide et sujet au bord du canevas. Importer, créer le premier sujet, retoucher, sauver et rouvrir. Essayer ensuite un second sujet sur la même image. [Création du projet](https://github.com/frenndak/SmartSVG-Studio/blob/3a5c44d/engine/smartsvg_core/project_workspace_g22.py#L238) · [Admission du pinceau](https://github.com/frenndak/SmartSVG-Studio/blob/3a5c44d/engine/native_atelier_tk_v34.py#L37)

### F07 — La taille des masques limite les planches à résolution utile

**Priorité élevée · main · Limites vérifiées dans le moteur et par appels ciblés**

La ressource V1 accepte au maximum **8 millions de valeurs de masque** au total, 32 masques et 5 millions de pixels par masque. Un masque est actuellement représenté sur toute la largeur et la hauteur de la source.

| Exemple | Valeurs de masque demandées | Résultat V1 |
|---|---:|---|
| 12 sujets sur une image 1 000 × 1 000 | 12 000 000 | Refusé, plafond global dépassé |
| 24 sujets sur une image 600 × 600 | 8 640 000 | Refusé, plafond global dépassé |
| 4 sujets sur une image 1 920 × 1 080 | 8 294 400 | Refusé, plafond global dépassé |
| Un masque sur une page A4 entière à 300 ppp, environ 2 480 × 3 508 | 8 699 840 | Refusé, plafond de 5 millions de pixels par masque dépassé |

La fenêtre de pinceau impose également 2 048 pixels par axe pour son aperçu. Ces limites n’interdisent pas toutes les planches possibles. Elles empêchent les cas indiqués avec la représentation V1 actuelle et doivent être prises en compte dès la création du premier sujet.

**Correction proposée.** Pour le premier parcours, annoncer les dimensions traitables avant de démarrer et conserver l’original. Étudier des masques recadrés avec coordonnées dans la source ou des tuiles, puis un traitement par sujet pour limiter les allocations. Pour une représentation durable plus riche, qualifier une migration de format et la relecture des projets V1. Les zones recadrées doivent conserver leurs pixels float32, leur origine, leurs chevauchements et leurs identités. Garder la possibilité de calculer et d’exporter des copies sans créer autant de sujets distincts.

**Recette.** 12 et 24 sujets à 1 000 × 1 000, une page A4 à 300 ppp, 50 placements issus de quelques sujets et 50 sujets réellement différents. Comparer chaque masque avant/après, la mémoire maximale, la durée et la reprise après interruption. Tester sur le PC de référence, avec la RTX 3070 lorsque l’étape IA est utilisée. [Plafonds du snapshot](https://github.com/frenndak/SmartSVG-Studio/blob/3a5c44d/engine/smartsvg_core/mask_snapshot_g24.py#L58) · [Analyse historique des plafonds](https://github.com/frenndak/SmartSVG-Studio/blob/3a5c44d/docs/roadmap-v3.4/19_PLANCHES_NESTING.md#L11)

### F08 — Le pinceau donne trop peu d’informations pour corriger précisément

**Priorité élevée · PR 169 · Observé dans Tk sous Linux et confirmé par le code**

La fenêtre de retouche présente le masque noir et blanc. Le dessin couleur n’est pas superposé dans cette fenêtre. Elle n’offre pas de zoom propre au pinceau, et les seuls rayons sont 0,02, 0,05 et 0,10 de la plus petite dimension du masque. Pour une image de 900 × 600, le plus petit rayon correspond à environ 12 pixels, soit un diamètre proche de 24 pixels. Le trait provisoire est dessiné avec une ligne de deux pixels à l’écran, ce qui ne représente pas l’épaisseur du pinceau appliqué.

**Correction proposée.** Vue synchronisée **Image**, **Masque**, **Superposition** et **Contour de coupe**, avec opacité réglable. Montrer la zone qui sera réellement peinte par le curseur. Ajouter zoom et déplacement dans la fenêtre de retouche et un rayon fin exprimé en pixels de la source, avec une conversion physique seulement quand l’échelle est connue. Garder la gestion des bords semi-transparents explicite, car les zones peintes à la main sont actuellement mises à 0 ou 1.

**Recette.** Reprendre une antenne fine et un bord semi-transparent, puis comparer la zone indiquée sous le curseur aux pixels réellement modifiés. Répéter à deux zooms et deux résolutions. [Affichage actuel](https://github.com/frenndak/SmartSVG-Studio/blob/7e82990af468d960c5678edfb93f75f85fac523b/engine/native_brush_draft_tk_v34.py#L287) · [Calcul du rayon et alpha](https://github.com/frenndak/SmartSVG-Studio/blob/3a5c44d/engine/smartsvg_editor/strokes.py#L131)

### F09 — Les formats admis à l’entrée et à l’édition sont trop différents

**Priorité moyenne à élevée · main · Reproduit sur trois fichiers locaux**

Le formulaire natif sélectionne le PNG et le port accepte un sous-ensemble de PNG 8 bits. Les exemples JPEG et WebP ont été refusés. Le PNG testé a été accepté. Les formats JPEG et WebP demeurent un besoin concret pour l’import multi-format prévu par A01.

**Correction proposée.** Offrir PNG, JPEG, WebP et SVG selon les capacités réellement raccordées. Montrer une vignette, orientation et transparence. Conserver les octets originaux et, si une conversion de travail est nécessaire, créer une ressource dérivée identifiée. L’utilisateur doit retrouver l’original, une image aux couleurs correctement interprétées et des coordonnées cohérentes après orientation EXIF.

**Recette.** JPEG pivoté par EXIF, PNG avec transparence ou palette, WebP, fichier invalide et très grande image. Enregistrer, rouvrir et comparer source, orientation, couleurs et état de la transparence. [Sélecteur natif](https://github.com/frenndak/SmartSVG-Studio/blob/3a5c44d/engine/native_create_tk_v34.py#L99) · [Formats PNG admis](https://github.com/frenndak/SmartSVG-Studio/blob/3a5c44d/docs/NATIVE_PNG_CREATE_V34.md#L24)

### F10 — Incohérences de texte et d’état dans l’interface et la roadmap

**Priorité moyenne · main et PR 168 · Vérifié**

- La fenêtre indique encore « Retouche … intégration à venir », tandis que l’Atelier ouvre déjà le pinceau pour un sujet vérifié. Le titre indique V3.4 alors que la roadmap directrice est V3.5. Le README contient aussi une description ancienne de projets en lecture seule.
- L’Atelier affiche des identifiants techniques longs et les caractères littéraux `\n` dans la description du sujet. Ces caractères ont été observés dans la fenêtre Linux et proviennent des chaînes utilisées pour les libellés.
- La première version de la PR 168, au SHA `44feb9901cc0fc7ae1641fb683af1550f1811b64`, affirmait que le formulaire refuse `40,5`. **Correction du précédent constat** : le formulaire normalise déjà la virgule avant de transmettre la valeur au moteur. Le test du formulaire avec `28,5` a réussi. Le port moteur appelé directement attend un nombre compatible avec son contrat. La description de cette PR doit également être mise à jour.
- La PR 167 remplace « Ajouter/Effacer » par « Garder/Masquer » et modifie les libellés d’historique. Ses contrôles CI sont verts. La lisibilité des nouveaux libellés dans la fenêtre réelle et à grande échelle Windows reste à mesurer.

**Correction proposée.** Remplacer le pied de fenêtre par des états liés aux fonctions réellement disponibles. Nommer les sujets avec un libellé lisible et, à terme, une miniature. Corriger les sauts de ligne et la phrase de la PR 168. Garder les identifiants complets dans les détails techniques copiables. [Libellés de l’Atelier](https://github.com/frenndak/SmartSVG-Studio/blob/3a5c44d/engine/native_atelier_tk_v34.py#L520) · [Conversion de la virgule](https://github.com/frenndak/SmartSVG-Studio/blob/3a5c44d/engine/native_create_tk_v34.py#L116) · [Contrat ajouté dans la PR 168](https://github.com/frenndak/SmartSVG-Studio/blob/44feb9901cc0fc7ae1641fb683af1550f1811b64/docs/roadmap-v3.5/ATELIER_PARCOURS_ET_RECETTES_UX.md#L15)

### F11 — Enregistrer une retouche peut bloquer l’interface

**Priorité moyenne · main et PR 169 · Lecture de code, latence non mesurée**

Le gestionnaire Tk appelle le writer de sauvegarde directement. Pour un gros projet ou un disque lent, cela peut immobiliser la fenêtre jusqu’au retour de l’opération. Les aperçus disposent déjà d’un traitement en arrière-plan.

**Correction proposée.** Exécuter l’écriture sur un travailleur unique et garder à l’écran la cible, l’étape et le résultat. Un retour tardif doit rester lié à la bonne révision. Mesurer le temps de réaction, la durée d’écriture et la relecture séparément. Le writer existant reste l’autorité pour l’archive.

**Recette.** Writer volontairement ralenti, notes présentes et demande de fermeture. Contrôler la réactivité, la conservation du sujet et le résultat après relecture. [Sauvegarde actuelle](https://github.com/frenndak/SmartSVG-Studio/blob/3a5c44d/engine/native_brush_draft_tk_v34.py#L649)

### F12 — L’application ne produit pas encore une sortie native complète

**Priorité élevée · main · Vérification des entrées et de la roadmap**

Le bureau ouvre et crée un projet PNG, inspecte des sujets déjà liés, permet certaines retouches et prévisualise deux gabarits. Le parcours natif qui part d’une image neuve et produit le premier PNG Print Then Cut reste à raccorder. Les moteurs historiques et les tests CPU disponibles fournissent des briques à étudier pour ce raccordement.

**Correction proposée.** Construire une première verticale depuis la sélection confirmée jusqu’au PNG effectivement écrit et relu. Afficher sa taille, son chemin, un aperçu de son alpha et le guide Design Space. Ajouter ensuite le SVG Basic Cut, les pièces multicouches puis le SVG d’édition avec leurs propriétés et leurs contrôles spécifiques. [État d’ingénierie](https://github.com/frenndak/SmartSVG-Studio/blob/3a5c44d/docs/roadmap-v3.5/ENGINEERING_STATUS_2026_11_17.md)

## 3. Expérience Cricut et économie de matière

L’étape de transfert doit montrer ce qui est réellement envoyé à Design Space. Pour un sticker imprimé, commencer par la forme, la marge, la taille et l’aperçu de coupe du PNG. Pour un motif vinyle, afficher le tracé et ses détails à l’échelle choisie. Pour un gabarit plié, montrer les éléments à découper et à rainer, puis guider le réglage Score et **Attacher**.

Pour l’Explore 5, Cricut indique que la feuille A4 imprimée doit être placée sur le tapis avec son grand côté horizontal. La documentation précise également que l’import de nouvelles images et les projets Imprimer puis découper demandent une connexion Internet dans Design Space. Le guide de SmartSVG peut rester lisible hors ligne et indiquer ces prérequis au moment du transfert. [Guide Explore 5](https://help.cricut.com/hc/en-us/articles/38613592650903-How-to-Print-Then-Cut-with-Cricut-Explore-5) · [Fonctionnalités hors ligne](https://help.cricut.com/hc/fr/articles/360033894014-Fonctionnalit%C3%A9-hors-ligne-Design-Space)

Cricut indique aussi que les SVG de plus de 5 000 tracés sont refusés à l’import et que certains éléments, dont les chemins d’écrêtage et les remplissages complexes, nécessitent une conversion adaptée. Le prévol doit compter les vrais tracés du fichier relu, localiser les éléments problématiques et proposer une variante sur copie en montrant les détails perdus. [Import d’images](https://help.cricut.com/hc/en-us/articles/360009556313-How-to-upload-images-into-Design-Space) · [Éléments SVG non pris en charge](https://help.cricut.com/hc/en-us/articles/360009553213-Image-uploads-unsupported-items)

Pour les planches, afficher la zone utilisable du format et du profil réellement sélectionnés. Les maxima horizontaux et verticaux indiqués par Cricut ne sont pas nécessairement atteignables ensemble pour tous les contours. Garder les marges et les positions verrouillées visibles, puis laisser Design Space produire ses propres repères. [Limites Print Then Cut](https://help.cricut.com/hc/en-us/articles/360009429814-How-large-can-I-Print-Then-Cut)

## 4. Parcours et design recommandés

| Moment | Écran ou action | Vérification à obtenir |
|---|---|---|
| **Démarrer** | Glisser une image ou choisir un fichier. Afficher une vignette et proposer « Un sticker », « Une planche », « Vinyle », « Carte ou boîte » et « Ouvrir un projet ». Le choix reste modifiable. | Une première création s’ouvre sans devoir comprendre les formats du projet. Les formats disponibles sont indiqués avant sélection. |
| **Choisir** | Afficher l’image et proposer une sélection par clic, cadre ou masque alpha. Montrer les sujets détectés et le nombre à confirmer pour une planche. | Une illustration avec deux objets proches permet de garder un sujet sans altérer l’autre. |
| **Corriger** | Même zone de travail avec image, masque et contour, taille du pinceau visible, zoom et historique par geste. Garder les paramètres avancés repliés. | Reprendre un détail fin et annuler sans perdre les autres zones, à la souris et au clavier. |
| **Préparer** | Choisir la taille en mm, le type de matériau quand il est connu et le nombre d’exemplaires. Localiser les zones fragiles et garder l’original. | Changer une taille invalide uniquement les contrôles dépendants et donne un nouveau prévol. |
| **Organiser** | Déplacer, dupliquer et verrouiller les pièces. Voir les collisions et les pages avant de lancer la production. | La correction d’un contour ne déplace pas un élément verrouillé. Un conflit devient visible et résoluble. |
| **Sortir** | Afficher le type de fichier en toutes lettres, le chemin, sa taille et les étapes à faire dans Design Space. | Le fichier est écrit, relu et vérifié à la bonne révision. Une erreur donne une action de reprise. |
| **Reprendre** | À la réouverture, afficher les projets récents et leur dernier état fiable. Proposer la récupération d’une modification interrompue si le port est qualifié. | Retrouver les sources, les réglages de taille et les pièces, avec leurs historiques et leurs fichiers déjà publiés. |

Pour le design, privilégier une barre de commandes stable, une image centrale utilisable, une liste d’éléments à noms compréhensibles et un panneau de propriétés repliable. Le mode avancé développe les paramètres du même projet. À faible largeur, les panneaux deviennent des boutons nommés plutôt que de réduire excessivement l’image. Tester Windows à 100 %, 150 % et 200 %, au clavier et avec lecteur d’écran.

## 5. Arbitrages pour les fonctions futures

| Domaine | Décision conseillée | Dépendances et contrôle |
|---|---|---|
| **Détourage local** | Proposer une première sélection simple, puis une aide facultative pour les images difficiles. Conserver l’action manuelle immédiatement accessible. | Vérifier les formats réels et la limite mémoire. Une proposition IA reste attachée au sujet, à l’image et à sa révision. |
| **Upscale et netteté** | Mesurer la résolution à la taille de sortie et proposer une amélioration quand le gain est utile. Comparer l’original et le résultat à la même échelle. | Mesurer sur la RTX 3070 8 Go. Contrôler lettres, bords, bruit et identité du dessin. |
| **Vectorisation multicolore** | Donner le choix silhouette, pièces couleur et SVG éditable, avec prévisualisation de chaque calque. Afficher les détails trop fins à la dimension choisie. | Vérifier trous, traits, chemins ouverts, contours et fidélité sur des images connues. Le SVG final est relu avant la fiche de transfert. |
| **Texte et gabarits** | Conserver le texte éditable et produire une copie vectorisée pour la fabrication lorsque nécessaire. Signaler police manquante et caractères indisponibles. | La persistance des objets et du texte doit être qualifiée. Tester accents, polices, étiquettes, cartes, plis et trous des lettres. |
| **Scène et diorama** | Extraire personnage, décor et accessoires en pièces sélectionnables, puis organiser les plans et les pages. Les parties cachées restent signalées. | Distinguer coordonnées d’origine, de planche et de montage. Tester une composition à quatre plans et un montage physique. |
| **Planches, CSV et séries** | Reprendre à la pièce en erreur, préserver les succès et afficher combien de pièces et de sujets existent. Conserver les positions verrouillées. | Vérifier 12/24 sujets, 50 copies et 50 sujets distincts, avec interruption, renommage et collisions. |
| **Assistant et modèles IA** | Expliquer ce qui sera modifié et montrer l’aperçu sur la cible. Une image difficile peut revenir au mode manuel avec son brouillon conservé. | Mesurer RAM/VRAM, temps et annulation. Version, licence, téléchargement et poids installés doivent être visibles. |
| **Paquet et Windows** | Livrer un dossier clair et un guide dès qu’un premier fichier est réellement vérifié. Prévoir mise à jour et récupération. | Exercer le build empaqueté sur Windows vierge, sans Python installé, y compris création, retouche, sauvegarde, export, hors ligne et retour arrière. |

### Ajouts et approfondissements concrets

| Idée | Utilité et place dans le projet | Vérification prévue |
|---|---|---|
| **Planches de vignettes réutilisables** | Dans W11/W12, une base de semainier avec tailles, nombre de copies, texte et images échangeables permet de décliner rapidement les activités. Enregistrer chaque vignette comme élément du projet et afficher la quantité par page. | Changer « École » en « Cantine », produire trois copies et rouvrir la composition. Contrôler marges, largeur et emplacement des pièces. |
| **Réutiliser les mêmes réglages sur plusieurs images** | Dans D10/W12, enregistrer une recette lisible, par exemple marge, taille et choix de sortie. Afficher un aperçu d’un fichier représentatif, puis le résultat et les erreurs par image. | Une série avec un fichier opaque, un transparent et un fichier illisible donne trois états propres. Une relance ne réécrit pas les fichiers déjà vérifiés. |
| **Importer une page PDF** | Ajout à étudier après le premier parcours image. Les kits de vignettes existent souvent sous forme de PDF. Choisir une page et sa résolution d’import, conserver le PDF et préciser si la page a été rasterisée. L’extraction vectorielle dépend du contenu et du moteur qualifié. | Page synthétique avec texte, formes et image intégrée. Comparer cotes et orientation après import, puis contrôler les éléments effectivement éditables. |
| **Historique de fabrication par matériau** | Réutiliser W04/W08 pour noter localement la machine, le papier ou vinyle, le résultat et une photo facultative. Réouvrir les paramètres déclarés pour un nouveau test. | Deux essais sur des matériaux différents restent associés à la bonne version du fichier et permettent de retrouver la taille réellement fabriquée. |
| **Contrôle avant consommation** | En sortie et dans W07/W12, signaler les très petites pièces, marges qui se touchent et dépassements de page. Estimer le nombre de feuilles à partir du placement effectivement calculé. | Une page de 24 stickers avec deux pièces trop proches signale leur position et montre la nouvelle disposition après correction. |
| **Diagnostic local partageable sur choix** | En W13/W15, proposer une copie du rapport d’erreur lisible. Exclure par défaut contenu de l’image, nom du compte et chemins personnels. L’utilisateur voit ce qui sera inclus. | Simuler une erreur d’import et une panne de sauvegarde. Vérifier que le rapport permet de distinguer les cas et contient seulement les éléments sélectionnés. |

Le premier export et la conservation des brouillons gardent la priorité. Toutes ces propositions restent à implémenter et à qualifier à leur étape ; elles ne constituent pas un état de livraison. L’import PDF demande une étude du décodeur et de sa distribution. Les autres propositions approfondissent des chantiers déjà prévus.

## 6. Contrôles transversaux à ajouter au développement

1. **Transitions de session.** Multiplier les tests qui traversent deux fonctions. Retouche → notes → relecture, retouche → création d’un autre projet, retouche → récupération, et résultat tardif → changement de sujet. Un test de fermeture isolé couvre seulement son propre chemin.
2. **Limites cohérentes.** Même budget vérifié pour l’interface, le moteur, le writer et la réouverture. Afficher la cause d’un refus avant que l’utilisateur investisse plusieurs gestes.
3. **Fichiers de sortie.** Conserver les quatre intentions d’export et relire le fichier réel après publication. Vérifier alpha, dimensions, trous, tracés et opérations selon leur rôle.
4. **Projets existants.** Rejouer ouverture, sauvegarde, secours, conflits et migration sur des projets créés par les versions précédentes et sur des fichiers synthétiques volumineux.
5. **Performance.** Sur la machine de référence, mesurer le temps avant premier retour visuel, le calcul, la sauvegarde et la relecture séparément. Relever RAM et VRAM avec une petite image, une page A4 et une planche de plusieurs sujets.
6. **Vraie utilisation.** Faire tester à des personnes débutantes une vignette simple, une planche et une carte pliée. Relever où elles hésitent, les actions nécessaires, les erreurs récupérées et la compréhension des états.
7. **Paquet Windows.** Tester la version distribuée et son contenu avec un vrai projet. Le démarrage seul, les tests Python et une maquette navigateur ne suffisent pas à prouver la retouche ou l’export du paquet.
8. **Preuves.** Pour chaque fonction, garder la distinction entre spécification, code intégré, test sur Windows, import Design Space, coupe et assemblage.

L’ancien défaut de restauration d’une copie de secours remplacée entre la confirmation et le verrou a été corrigé depuis l’audit des PR 1 à 125. Le test ciblé de remplacement du secours passe sur le code examiné. [Correctif et contrat de restauration](https://github.com/frenndak/SmartSVG-Studio/blob/3a5c44d/engine/smartsvg_core/project_workspace_g22.py#L368)

## 7. Priorité proposée pour la reprise

| Rang | Travail | Résultat observable |
|---:|---|---|
| **1** | Corriger F01 à F05 et compléter les tests de transition de la PR 169. | Aucun geste utile ne disparaît à la fermeture, à une autre action, à un dépassement ou à une sauvegarde incertaine. |
| **2** | Créer le premier sujet depuis un PNG neuf, avec masque vérifié et reprise en cas d’interruption. | Une image simple peut entrer dans l’Atelier, être sélectionnée, retouchée, sauvegardée et rouverte. |
| **3** | Ajouter le premier PNG Print Then Cut depuis le bureau, sa relecture et son guide. | Une vignette est produite à une largeur choisie, retrouvée dans son dossier et importée pour essai. |
| **4** | Résoudre le budget des masques, les grandes images et les planches 12/24. | La résolution traitable, le nombre de sujets et la mémoire utilisée sont mesurés et annoncés. |
| **5** | Rendre la retouche visuelle et précise, puis ajouter les autres sorties. | L’image et son masque se superposent, les détails sont accessibles et les quatre rôles de fichier sont vérifiés séparément. |
| **6** | Poursuivre texte, scènes, séries et IA selon leurs dépendances, avec des essais sur des cas d’usage complets. | Les projets sont réutilisables et les résultats de fabrication sont contrôlés sur le matériel ciblé. |

## 8. Relecture des 17 unités de la roadmap

| Unité | Point de vigilance ou amélioration à intégrer lors de la réalisation |
|---|---|
| **W00** Héritage | Conserver les 141 critères et leurs recettes. Distinguer inventaire de documents, comportement réellement raccordé et test exécuté. Suivre les six liens scénario-ticket et les dix exigences déjà identifiés comme exceptions. |
| **W01** Projet natif | Accepter les formats prioritaires, donner un aperçu aux sources admises et préserver les originaux. Vérifier sauvegarde, secours et formulaires avec les chemins et noms français. |
| **W02** Atelier | Fermer F01 à F06, afficher l’image derrière le masque, puis qualifier la sélection et le retour d’erreur sur deux sujets. |
| **W03** Exports | Livrer un PNG d’abord, puis les trois rôles SVG. Vérifier le fichier écrit, son alpha, ses cotes et sa provenance. |
| **W04** Prévol | Associer les défauts à une zone ou un paramètre. Contrôler les détails fins, trous, chemins doubles et opérations à taille réelle. |
| **W05** Plan de livraison | Montrer les fichiers qui seront réunis, leur version et leur état avant écriture du pack. |
| **W06** Smart Delivery | Préparer un ZIP vérifié depuis au moins un fichier sain. Préserver les succès et présenter clairement les erreurs partielles. |
| **W07** Qualité de coupe | Comparer les variantes à la même taille. Afficher les détails qui disparaissent et autoriser une protection locale. |
| **W08** Design Space | Donner un guide qui correspond à l’Explore 5, au format A4 et au fichier choisi. Maintenir à jour l’étape de connexion, Score, Attacher et vérification des dimensions. |
| **W09** Échenillage | Prévisualiser les suggestions et vérifier les distances avant toute production. Mesurer les résultats sur les matériaux utilisés. |
| **W10** Texte | Préserver texte, accents, police et styles dans le projet. Produire des chemins réels en gardant une copie rééditable. |
| **W11** Gabarits | Étiquette, carte et boîte doivent garder dimensions, pliage et montage compréhensibles après réouverture. Vérifier coupe et Score séparément. |
| **W12** Planche et série | Traiter F07 comme une dépendance concrète pour les images de qualité. Vérifier placements, sujets distincts, sources, reprise et collisions. |
| **W13** Interface | Corriger les ambiguïtés relevées en F08/F10. Tester la fenêtre de retouche sur de vrais DPI, au clavier et avec lecteur d’écran. |
| **W14** IA locale | Tester modèles, prévisualisation, mémoire, annulation et repli manuel sur le matériel visé. Les propositions restent réversibles. |
| **W15** Windows | Vérifier l’installation et le paquet réellement livrés sur poste vierge, leurs dépendances, la récupération et le fonctionnement hors ligne de SmartSVG. |
| **W16** Création avancée | Préserver les usages hérités OCR et diorama. Garder une recette métier propre pour chaque format, machine et montage. |

## 9. Grille des 80 capacités UX

Le statut indique ce qui a été établi pour le bureau à la révision examinée. **Partiel** signifie qu’une partie est visible ou testée, avec les limites précisées. **À qualifier** signifie que la capacité reste à vérifier dans le parcours natif complet. **Historique** indique une brique du moteur ou une interface ComfyUI à examiner lors du raccordement. Les dernières colonnes donnent une recette proposée, sans revendiquer son exécution.


### Image et sélection

| Fonction | Priorité et chantier | État observé | Recette à exécuter |
|---|---|---|---|
| **A01** Import PNG/JPEG/WebP/SVG et lots | P0 · W01 | Partiel · PNG natif, F09 | Déposer un JPEG pivoté, un PNG alpha et un format refusé. Vérifier orientation, source intacte et traitement indépendant des trois. |
| **A02** Gestes de sélection | P0 · W02 | Partiel · pinceau, F03/F05/F08 | Tracer une même zone à 100 % et 200 %, puis au clavier via l’alternative de sélection. Vérifier la cible et les coordonnées. |
| **A03** Sélections multizones et opérations de masque | P0 · W02 | Partiel · zones, F04/F05 | Sur deux sujets qui se chevauchent, combiner des zones de sens opposé et un trou. L’annulation locale rétablit le masque du seul sujet actif. |
| **A04** Contour assisté et alternatives | P1 · W02 | À qualifier dans le parcours natif | Deux sujets proches entourés ensemble donnent une proposition à confirmer. Une réponse tardive ne remplace jamais le sujet sélectionné entre-temps. |
| **A05** Affinage des bords | P1 · W02 | À qualifier dans le parcours natif | Affiner une antenne de dessin sur fond proche. Vérifier le contour hors zone et la possibilité de récupérer l’antenne. |
| **A06** Retrait du fond par alpha | P0 · W02 | À raccorder · premier sujet, F06 | Sur un objet partiellement transparent, conserver sa transparence interne et retirer le fond opaque. Réouvrir puis comparer l’alpha. |
| **A07** Halos, défauts et microfragments | P1 · W07 | À qualifier dans le parcours natif | Comparer sur fond clair et foncé. Un reflet volontaire et un trou fonctionnel survivent à la correction du halo. |
| **A08** Netteté, bruit et amélioration de résolution | P1 · W07 | À qualifier dans le parcours natif | Une capture peu définie garde le même dessin, la même taille imprimée et un original récupérable après amélioration. |
| **A09** Contrôle visuel du détourage | P0 · W02 | Partiel · avant/après masque, F08 | Basculer les quatre vues autour d’un bord semi-transparent à 100 %, avec le même point et la même sélection. |
| **A10** Palette, pipette et recoloration | P1 · W02 | À qualifier dans le parcours natif | Prendre une couleur, conserver les valeurs d’opacité prévues et annuler sur le seul objet sélectionné. |
| **A11** Séparation des couleurs et impression | P1 · W03 | À qualifier dans le parcours natif | Ajouter une teinte proche et parcourir le résultat par couche. Comparer séparément la composition imprimée et les pièces CUT. |
| **A12** Silhouette, contour, ligne centrale et vectoriel éditable | P0 · W03 | Historique · sortie native à raccorder | Un même dessin produit des résultats identifiables par intention. Les chemins d’un SVG d’édition se sélectionnent indépendamment. |
| **A13** Plume, crayon et nœuds Bézier | P1 · W02 | À qualifier dans le parcours natif | Déplacer une poignée à fort zoom. Le retour arrière restaure le chemin et le point d’édition avec la courbe initiale. |
| **A14** Opérations booléennes et fermeture | P0 · W02 | À qualifier dans le parcours natif | Soustraire un anneau d’une forme, contrôler trous et winding puis annuler avec retour des identités. |
| **A15** Simplification des tracés | P1 · W07 | À qualifier dans le parcours natif | Comparer à 40 mm et 80 mm. Le trou et l’angle marqués protégés survivent même si le nombre de nœuds baisse. |
| **A16** Variantes et métriques vectorielles | P2 · W07 | À qualifier dans le parcours natif | Une variante légère dont un trou disparaît déclenche un motif visible et distinct d’une simple note de similarité. |

### Objets et texte

| Fonction | Priorité et chantier | État observé | Recette à exécuter |
|---|---|---|---|
| **B01** Objets raster, vectoriels, textes, masques et opérations | P0 · W02 | Partiel · sujets/masques V1 | Créer un groupe mixte et rouvrir. Retrouver les mêmes membres et propriétés dans le modèle de composition qualifié. |
| **B02** Calques, ordre, verrou, visibilité et opacité | P0 · W02 | À qualifier dans le parcours natif | Cacher et verrouiller un enfant puis exporter suivant les choix d’inclusion. Recharger et contrôler chaque état indépendamment. |
| **B03** Séparation de personnage, décor et accessoires | P1 · W02 | À qualifier dans le parcours natif | Extraire personnage et accessoire partiellement superposés. Déplacer l’accessoire sans perdre le masque source ni confirmer une partie inventée. |
| **B04** Déplacement, échelle, rotation, miroir et duplication | P0 · W02 | À qualifier dans le parcours natif | Dupliquer et miroiter un motif asymétrique. Seul le clone change et les deux transformations reviennent après réouverture. |
| **B05** Alignement, répartition, grille et mesures | P0 · W02 | À qualifier dans le parcours natif | Répartir cinq pièces avec deux verrous. Prévisualiser les distances mm et garder les deux ancrages. |
| **B06** Perspective, déformation et écrêtage | P2 · W16 | À qualifier dans le parcours natif | Déformer un logo puis déplacer son masque d’écrêtage. Rouvrir et reprendre les réglages avec les mêmes repères. |
| **B07** Articulation de personnage | P2 · W16 | À qualifier dans le parcours natif | Modifier un bras sans déplacer le visage ni la zone verrouillée du torse. Basculer ancien/nouveau et annuler. |
| **B08** Reconstruction après extraction | P2 · W16 | À qualifier dans le parcours natif | Sur un motif répété derrière une pièce, annuler la reconstruction et retrouver le décor d’origine ainsi que la pièce détachée. |
| **B09** Texte éditable et polices | P1 · W10 | À qualifier dans le parcours natif | Rouvrir sur un poste sans la fonte et avec « Étiquettes – Noël ». Retrouver le texte et résoudre la substitution en connaissance de cause. |
| **B10** Texte courbe, circulaire ou sur chemin | P1 · W10 | À qualifier dans le parcours natif | Inverser l’arc d’une étiquette. Le texte reste éditable, son ordre attendu et l’alignement peuvent être restaurés. |
| **B11** Ombres, contours, dégradés et textures de texte | P1 · W10 | À qualifier dans le parcours natif | Une ombre reste visible à l’impression. La vue CUT montre les chemins réels et les effets laissés à l’impression. |
| **B12** Texte converti en chemins | P1 · W10 | À qualifier dans le parcours natif | Convertir « Bébé », conserver les trous des glyphes et modifier le texte source sans écraser un export archivé. |
| **B13** OCR vérifié et texte éditable | P1 · W16 | À qualifier dans le parcours natif | Faire reconnaître réellement une ligne accentuée et la corriger caractère par caractère. La validation humaine et la réouverture du texte enregistré font partie de la recette. |
| **B14** Composition, marges, hiérarchie et modèles | P1 · W11 | À qualifier dans le parcours natif | Passer une carte d’une taille à l’autre. Les éléments verrouillés et la hiérarchie restent stables ou un débordement explicite apparaît. |

### Fabrication

| Fonction | Priorité et chantier | État observé | Recette à exécuter |
|---|---|---|---|
| **C01** Sticker, offset, fond perdu et PNG PTC | P0 · W03 | Historique · export natif à raccorder, F12 | Un PNG relu garde l’alpha et la silhouette attendus. Contrôler largeur et aperçu de coupe lors de l’import Design Space. |
| **C02** Silhouette vinyle et coupe monochrome | P0 · W03 | Historique · export natif à raccorder | Une petite lettre à contreforme conserve son trou et un seul chemin attendu après relecture du SVG Basic Cut. |
| **C03** Coupe multicouche par couleur | P1 · W03 | À qualifier dans le parcours natif | Réimporter trois pièces et contrôler superposition, orientation par couleur et présence correcte des repères. |
| **C04** Pochoirs et ponts | P1 · W04 | À qualifier dans le parcours natif | Tester un A et un O. La contreforme tient dans la géométrie corrigée et la source reste disponible pour un retour arrière. |
| **C05** Penne et ligne centrale | P1 · W04 | À qualifier dans le parcours natif | Une ligne ramifiée conserve l’ordre choisi et un segment unique par portion voulue. Le contrôle distingue chemin ouvert et contour. |
| **C06** CUT, SCORE, DRAW, PRINT et FOIL | P0 · W04 | Partiel · aperçu de gabarit | Un gabarit avec pli et motif imprimé garde ses trois usages identifiés après relecture et guide chaque affectation Design Space. |
| **C07** Prévol géométrique localisé | P0 · W04 | Historique · prévol natif à raccorder | Insérer trois anomalies différentes. Chacune conduit à la bonne zone et recalculer celle corrigée retire seulement son diagnostic. |
| **C08** Profils Explore 5, matière, lame, tapis | P1 · W04 | À qualifier dans le parcours natif | Un matériau inconnu affiche les limites de qualification. Changer le tapis invalide le contrôle d’encombrement concerné. |
| **C09** Fidèle, équilibré et facile à découper | P1 · W07 | À qualifier dans le parcours natif | Choisir la variante facile, puis rouvrir le projet. Retrouver ses réglages et les écarts mesurés à même largeur. |
| **C10** Quatre contrats d’export | P0 · W03 | Historique · quatre rôles natifs à raccorder | Lancer chaque rôle individuellement et relire quatre artefacts selon leurs attentes. Le rôle multicouche externe conserve son identité métier. |
| **C11** Transfert Design Space | P0 · W08 | Prévu · guide à qualifier | Une personne novice retrouve le fichier, vérifie sa largeur et suit le bon parcours d’import pour autocollant et pli. |
| **C12** Planches, duplications et quantités | P1 · W12 | À qualifier dans le parcours natif | Vérifier 12 sujets et 50 placements sur plusieurs pages, avec chaque instance identifiable et des totaux cohérents. |
| **C13** Placement par silhouette et contraintes | P1 · W12 | À qualifier dans le parcours natif | Calculer deux dispositions avec contraintes différentes. Aucune pièce n’empiète et une rotation interdite reste refusée. |
| **C14** Placement manuel, verrous et réoptimisation | P1 · W12 | À qualifier dans le parcours natif | Verrouiller deux stickers, élargir leur contour et réoptimiser. Les ancrages sont préservés et la collision éventuelle devient une tâche visible. |
| **C15** Économie de matière et reprise | P2 · W12 | À qualifier dans le parcours natif | Interrompre une série multipage. Reprendre la page restante avec le même décompte et sans redéposer les pages déjà reconnues. |
| **C16** Cartes, boîtes, enveloppes et pochoirs | P1 · W11 | Partiel · deux aperçus | Changer la profondeur d’une boîte et le format d’une enveloppe. Réouvrir les réglages et contrôler leurs tracés d’export. |
| **C17** Géométrie mm, plis, épaisseur et languettes | P1 · W11 | Partiel · géométrie et aperçu | Deux épaisseurs donnent deux géométries mesurables. Une languette devenue trop courte est localisée avant export. |
| **C18** Aperçu de patron et pliage 3D éventuel | P2 · W16 | À qualifier dans le parcours natif | Sélectionner un pli dans les deux vues quand elles existent. Vérifier que la pièce correspond et réserver la validation pratique au montage réel. |

### IA et automatisation

| Fonction | Priorité et chantier | État observé | Recette à exécuter |
|---|---|---|---|
| **D01** Fournisseurs de segmentation CPU et IA | P1 · W14 | Historique · fournisseur natif à qualifier | Retirer le modèle, démarrer sans réseau et produire une sélection manuelle ou CPU avec la même logique de confirmation. |
| **D02** Consignes combinées clic, pinceau, lasso et texte | P1 · W14 | À qualifier dans le parcours natif | Combiner deux zones positives et un refus avec une consigne texte facultative. Retirer un seul indice et comparer les résultats. |
| **D03** Propositions d’IA et validation | P1 · W14 | À qualifier dans le parcours natif | Deux variantes concurrentes arrivent après modification manuelle. Seule une proposition recalculée et confirmée peut être appliquée. |
| **D04** Détourage fin des cheveux et translucides | P2 · W14 | À qualifier dans le parcours natif | Une mèche imprimable et une zone translucide restent fidèles. La vue coupe rend visible ce qui serait trop fin à l’échelle choisie. |
| **D05** Upscale HD conditionnel | P1 · W14 | Historique · HD native à qualifier | Agrandir une petite illustration et vérifier les lettres et bords. En cas d’échec du modèle, retrouver l’état initial et l’export de qualité connue. |
| **D06** Génération raster ou vecteur | P2 · W16 | À qualifier dans le parcours natif | Comparer une proposition raster et une vectorielle réelle. Seuls les chemins éditables sont annoncés comme tels. |
| **D07** Réparation locale et inpainting | P2 · W16 | À qualifier dans le parcours natif | Réparer une déchirure sous contrôle du masque. Comparer les pixels hors zone et annuler la variante. |
| **D08** Catalogue de modèles, licences et consentement | P1 · W14 | À qualifier dans le parcours natif | Télécharger uniquement après accord dans le test prévu. Un hash discordant déclenche un refus clair et le mode local de secours reste disponible. |
| **D09** VRAM, annulation et repli | P1 · W14 | À qualifier dans le parcours natif | Sur RTX 3070 8 Go, provoquer un manque de VRAM contrôlé puis essayer autre réglage ou CPU. Vérifier l’état de la cible et la réactivité. |
| **D10** Recettes et préréglages | P1 · W12 | À qualifier dans le parcours natif | Rejouer trois gestes réversibles après changement de source. Un réglage incompatible est indiqué et aucune sortie n’est écrite implicitement. |
| **D11** Lots, dossiers, CSV et erreurs individuelles | P1 · W12 | À qualifier dans le parcours natif | Interrompre 24 lignes, en corriger deux et reprendre. Vérifier association ligne→fichier, absence de doublon et caractères d’accent préservés. |
| **D12** Assistant contextuel | P1 · W14 | À qualifier dans le parcours natif | Soumettre une petite forme détectée. L’assistant cible le bon contour et une correction proposée est réversible. |

### Interface et projets

| Fonction | Priorité et chantier | État observé | Recette à exécuter |
|---|---|---|---|
| **E01** Bibliothèque, récents, favoris et recherche | P1 · W12 | Partiel · ouverture de fichier | Déplacer un projet et retrouver sa fiche, sa miniature et l’action de reliaison sans toucher à des fichiers voisins. |
| **E02** Collections, tags et modèles | P1 · W12 | À qualifier dans le parcours natif | À partir d’un modèle, dupliquer, changer un tag et modifier la copie. La source du modèle garde ses propriétés. |
| **E03** Variantes et historique | P1 · W12 | Partiel · historique de retouche | Ouvrir une ancienne variante, revenir à l’actuelle et retrouver leurs réglages et exports distincts. |
| **E04** Atelier hybride | P0 · W02 | Partiel · pinceau sur sujet, F08 | Alterner image, masque, courbe et texte sur un même projet, avec édition et retour à la vue précédente. |
| **E05** Zoom, pan, poignées, aimants et overlays | P0 · W02 | Partiel · zoom hors pinceau, F08 | Redimensionner la fenêtre pendant une comparaison, réajuster à 100 % et vérifier que le geste vise toujours les bons pixels source. |
| **E06** Avant/après, curseur et superposition | P1 · W02 | Partiel · comparaison de masque, F08 | Balayer un détail fin puis changer de mode d’affichage sans perte de cadrage ou inversion silencieuse des côtés. |
| **E07** Survol, barre contextuelle et raccourcis | P0 · W13 | Partiel · raccourcis ciblés | Utiliser la suite Garder → aperçu → annuler avec souris et clavier. Le survol et les infobulles restent facultatifs. |
| **E08** Express et avancé | P0 · W13 | À qualifier dans le parcours natif | Modifier un offset expert, revenir en Express et vérifier que la valeur est conservée et lisible avant export. |
| **E09** Thèmes, panneaux et préférences | P1 · W13 | Partiel · thèmes | Changer thème, fermer un panneau, redémarrer sur une autre résolution et retrouver les commandes essentielles. |
| **E10** Clavier, focus, contraste, DPI et mouvement réduit | P0 · W13 | Partiel · preuve Windows à compléter | Finir import et prévol au clavier à 100 %, 150 % et 200 %, avec contraste renforcé et retour du focus après dialogue. |
| **E11** Undo/Redo, brouillons et transactions | P0 · W02 | Partiel · Undo et brouillons, F01–F05 | Fermer puis revenir après deux zones. Annuler le geste enregistré après réouverture en conservant les exports historiques associés. |
| **E12** Sauvegarde V1, conflit et récupération | P0 · W01 | Partiel · sauvegarde et récupération | Conflit de révision, sauvegarde interrompue et disque plein. Retrouver l’archive saine et un statut qui distingue réussite, refus et relecture à faire. |
| **E13** Aperçus asynchrones et cache | P0 · W01 | Partiel · aperçu asynchrone, F11 | Une série rapide de changements provoque une seule mise à jour finale cohérente. Un grand original admis obtient au minimum son aperçu borné. |
| **E14** Erreurs compréhensibles et réparables | P0 · W13 | Partiel · messages, F05/F10 | Provoquer source absente, chemin invalide et taille hors budget. Chaque message conduit à une action différente et correcte. |
| **E15** Contrôle alpha, contour, couleurs et résolution | P0 · W03 | Historique · QA native à raccorder | Un halo ajouté à l’artefact est visible à la relecture même si l’aperçu initial était correct. La densité effective suit la largeur choisie. |
| **E16** Contrôle SVG, topologie, viewBox et mm | P0 · W03 | Historique · QA native à raccorder | Injecter dans une fixture un trou perdu et une échelle erronée. Le prévol signale deux causes distinctes. |
| **E17** Preuves de fabrication | P0 · W04 | À qualifier · preuve matérielle | Un SVG sain en local importé avec erreur dans Design Space conserve ses preuves distinctes. Les mesures physiques sont enregistrées avec leur contexte. |
| **E18** Installation, hors ligne, mises à jour et retour arrière | P1 · W15 | Partiel · Alpha portable antérieure | Échouer volontairement une mise à jour, revenir à l’ancienne version et rouvrir projets et préférences sans perte. |
| **E19** Confidentialité et consentement réseau | P0 · W15 | Partiel · noyau local | Lancer une session complète hors ligne et examiner les destinations de sauvegarde et rapports. Une action réseau annulée ne transmet rien. |
| **E20** Aide contextuelle et tutoriels | P1 · W13 | Partiel · consignes dans les fenêtres | Sur un premier sticker, retrouver le contrôle de largeur et l’étape Design Space à partir de la sortie, sans parcourir un manuel général. |

Les 80 lignes reprennent les capacités du [registre V3.5](https://github.com/frenndak/SmartSVG-Studio/blob/3a5c44d/docs/roadmap-v3.5/PRIORITY_INDEX.md). Les constats numérotés s’appuient sur les reproductions, la lecture ciblée ou l’observation visuelle précisées dans les sections précédentes.
