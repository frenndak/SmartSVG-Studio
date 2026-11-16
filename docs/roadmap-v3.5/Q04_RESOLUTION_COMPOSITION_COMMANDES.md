# Q04 — Décision consolidée : composition, critères métier et commandes

**14 novembre 2026 — décision de conception candidate.** Sources relues au main réel `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935` : [lot 06](../roadmap-v3.4/06_COMMAND_BUS.md), [lot 05](../roadmap-v3.4/05_PROJECT_SCHEMA.md), [héritage G6](../ROADMAP_HERITAGE_v3_3.md), [Q04B](Q04B_TEXT_G6_CLAUSE_RECONCILIATION.md), puis travaux horaires Q04C–Q04I publiés jusqu'au commit `5d5f1d3c80432c10fdf96e1fd2e14aa060d5f167`. Leur rapprochement source est conservé ; cette fiche prend une décision plus concrète, ne recommence pas Q04C. Le chemin du lot 06 est **06_COMMAND_BUS.md**. Le retrouver n'est plus une prochaine action. L'[ADR de composition persistante](ADR_COMPOSITION_PERSISTENCE.md) complète Q04F en fixant coordonnées, verrouillage, migration et tranches de réalisation. Elle ne certifie aucun logiciel.

## 1. Décision qui conserve l'exigence

L'Atelier complet devra sauvegarder et réouvrir des objets, calques et textes réellement modifiables. Un brouillon exportable est une étape intermédiaire, jamais l'achèvement de G6.3 ni S-035. Le format V1 actuel reste inchangé. La cible de conception est une **copie de projet V2 versionnée**, déjà envisagée par les lots 05/06 ; sa mise en œuvre comporte lecteur, migration, writer, historique et UI, avant d'activer la sauvegarde de composition. Ce n'est ni un second projet parallèle synchronisé, ni une extension cachée des strokes.

La demande propriétaire du 14/11/2026 autorise l'amélioration complète et le remplacement de la roadmap une fois finalisée. Elle permet de choisir cette cible dans la candidate. Elle n'est pas une preuve que le nouveau format, son writer ou sa migration fonctionnent. Les changements de code et de gouvernance passent par leurs PR dédiées et contrôles applicables ; aucune nouvelle question de principe « faut-il concevoir la persistance ? » n'est nécessaire.

## 2. G6 : sortie utilisateur et responsabilité exacte

| Clause source | Critère conservé | Capacité et propriétaire candidat | Contrôle métier complémentaire au lot 06 |
|---|---|---|---|
| G6.1 | Texte, formes, position, rotation, calques ; créer une étiquette sans autre logiciel | S-035, B01–B09 ; W02 scène + W10 texte | Créer texte+forme, déplacer/rotater, sauver, fermer, réouvrir, modifier le même texte ; objets et ordre identiques |
| G6.2 | Groupe, alignement, grille, palette ; aucun placement perdu | B01–B08/B14 ; W02 scène | Groupe à deux niveaux, aligner, sauvegarder, reprendre et dégrouper sans déplacement visuel ; identités conservées |
| G6.3 | Texte modifiable dans projet, exportable en tracés, police absente sans substitution silencieuse | S-036/S-064/S-092/R33-028 ; W10 | Round-trip du texte, style, police/version et mise en page ; absence de police visible ; conversion export seulement sur copie |
| G6.4 | Étiquette, topper, carte ; prototype de chaque usage déclaré | S-037 ; W11 | Trois projets éditables, trois recettes et leurs preuves physiques distinctes ; une boîte ouverte ne remplace pas un topper |
| G6.5 | Historique/variantes ; reprendre/dupliquer sans écraser l'original | W01/W02/W12 | Nouvelle identité de variante avec provenance, source intacte, historique borné et Undo après réouverture |
| G6.6 | Souris/clavier, mm, multisélection, Undo fiable | W02/W13 et B14 | Deux parcours produisent mêmes coordonnées logiques ; une action groupée = un Undo ; focus restauré |
| G6.7 | Démarrage guidé par usage sans tutoriel externe | W11/W13 | Étiquette/carton/sticker à partir de l'accueil, instructions contextuelles, erreurs récupérables et sauvegarde accessible |

Ces contrôles sont proposés, **NOT_RUN**. G6.4 conserve sa preuve physique sans exiger cette preuve pour terminer le document de conception. S-036/S-064/S-092/R33-028 n'acquièrent aucun lien V34 historique inventé : W10 porte explicitement leur delta métier.

## 3. Les neuf DoD du lot 06 : soutien technique, pas moteur texte

| Ticket source | DoD intégral de la micro-fiche à conserver | Application à B09–B14 |
|---|---|---|
| V34-032 | Schéma strict, aucune écriture IA directe ; T06-02/04/12/27 | Commandes de composition typées ; texte, couleurs, transformations validés. Ne fournit pas le shaping |
| V34-033 | Un commit au plus, pending récupérable ; T06-04..08/28 ; auto + Windows | Mutation texte et ressources dans même publication ; inspecter après réponse perdue, jamais relancer aveuglément |
| V34-034 | Aucun retry ancien réappliqué ; T06-01..03/09..12 ; auto + Windows | Receipt + epoch, y compris conversion en chemins confirmée ; ancien epoch rejeté après compaction |
| V34-035 | Bit-identité float32, groupes atomiques ; T06-13..16/21 | Texte/calques ajoutent des patches exacts ; tests historiques des masques restent obligatoires et distincts |
| V34-036 | Aucun worker n'écrit le projet ; T06-17..20/27/29/30 | OCR B13 produit une proposition, jamais une nouvelle valeur du texte sans acceptation utilisateur |
| V34-037 | Perte/rejeu d'événement sans divergence ; T06-23/26 | Vue texte/calques reconstruite depuis la révision canonique ; aucun store UI maître |
| V34-038 | Geste unique réversible, pas de faux Undo physique ; T06-13..15/23 | Saisie groupée, drag et édition d'effet chacun un Undo documenté ; export externe non révoqué |
| V34-039 | Comparer/relancer, zéro rebind automatique ; T06-17/18/20/27 | OCR/calcul typographique périmé isolé, choisir relance sur nouveau snapshot |
| V34-040 | Preuves horodatées, **100 points d'injection**, pas de corruption ; T06-01..12/23/28 | Conserver le banc complet avant activation writer V2 ; quelques tests unitaires ne le remplacent pas |

`T06-NN` abrège ici seulement `T-V34-06-NN`. Les rollback originaux restent : bus désactivé ; V1 historique ; mutations V2 refusées ; historique en lecture seule ; manuel/CPU ; rechargement complet ; UI sans timeline ; abandon sûr ; NO-GO writer V2. Les chemins de futurs modules du lot 06 sont des propositions, pas des fichiers existants à importer.

## 4. Raccordement des 30 assertions du lot 06

Les assertions exactes du §9 du lot 06 sont conservées **par référence** et ne sont pas remplacées par les résumés ci-dessous.

| Assertions | Responsabilité V3.5 | Cas à préserver |
|---|---|---|
| T-V34-06-01..03 | W01 writer + receipts | ACK perdu, payload divergent, retry déjà commité avant CAS |
| T-V34-06-04..08 | W01 publication/recovery | STALE, concurrence, commit+backup échoué, échec sans publication, état indécidable |
| T-V34-06-09..12 | W01 epochs et digest | epoch close, checkpoint interrompu, plafond, aucune autoréférence SHA ZIP |
| T-V34-06-13..16 | W02 historique | float32 exact, CUT+SCORE atomiques, branche Redo invalidée, identité revalidée |
| T-V34-06-17..20 | W14 jobs, W10 consomme OCR | STALE, cancel tardif, OOM, aucun relancement/téléchargement muet |
| T-V34-06-21 | W02 groupe sujets | 12 IDs acceptés ensemble ou zéro ; Undo groupé |
| T-V34-06-22 | W01 format V2 + W12 séries | 50 sujets en packs internes au **même projet V2**, chaque pack compatible ≤32, IDs uniques globaux ; jamais deux projets autorités |
| T-V34-06-23/26 | W01 événements + W13 UI | resynchronisation depuis archive ; deux vues cohérentes |
| T-V34-06-24 | W02 historique + W04 opérations | Score/Draw/Print restent leur type après Undo/Redo/reload ; pas de conversion automatique CUT |
| T-V34-06-25 | W15 diagnostics | rapport expurgé, sans chemins privés, médias, poids IA |
| T-V34-06-27 | W01 commandes + W14 assistant | proposition assistant non confirmée : zéro mutation |
| T-V34-06-28 | W01 sécurité/publication | disque plein, read-only, symlink, ZIP hostile : aucune destruction source |
| T-V34-06-29..30 | W14 jobs + W12 séries | déduplication de tentative, succès partiel non commité, reprise ciblée sans doublons |

Décision explicite pour 06-22 : le lot 05 §3.2 définit déjà les packs V2 et la limite V1. Il n'y a pas à réinterpréter « V2 » comme simple partition d'export : conserver l'assertion telle quelle et en faire une dépendance de la persistance de 50 sujets. Les planches externes de 50 éléments n'ont pas automatiquement besoin de 50 masques persistés ; les deux capacités portent des tests distincts.

Les autres exceptions Q02 reçoivent des propriétaires de **conception V3.5**, non des citations historiques : T-V34-03-16 → W04/W15 preuve terrain ; 07-16 → W02/W13 Undo non physique ; 07-25 → W13 benchmark 100 transitions p95 <150 ms avec protocole/matériel. Le total historique reste 431 liens explicites sur 437. L'adoption de ces responsabilités dépend de la promotion, pas d'une modification des sources gelées.

## 5. Six capacités texte, DoD minimal distinct

| ID | Entrée → résultat persistant attendu | Conditions et tests supplémentaires |
|---|---|---|
| B09 | Unicode + police → TextNode conservant texte/style/layout | accents FR, police absente, glyphes absents, source intacte ; sauver/réouvrir/modifier |
| B10 | TextNode + chemin/monogramme/étiquette → layout rééditable | rayon nul, chemin trop court, chemin supprimé, renversement ; aucune perte du texte original |
| B11 | TextNode + effets → liste typée et réversible | contour/ombre/texture/dégradé distincts ; effets visuels non promus en CUT ; ressource manquante visible |
| B12 | TextNode → chemins d'export ou copie convertie explicitement | trous/winding/mm, union de glyphes, glyphe absent ; conversion destructive seulement sur copie ou commande Undo |
| B13 | raster + OCR facultatif → proposition corrigée → TextNode | ambiguïté/glyphe manquant/résultat périmé ; aucune police devinée ou remplacement automatique |
| B14 | objets + contraintes → proposition de composition validée | marges/alignement/hiérarchie/modèles ; cycle de contraintes, objet verrouillé, dépassement du canevas ; Undo groupé |

Toutes partagent les contrats précis de l'ADR, le fallback manuel/CPU, les quatre exports et l'accessibilité Windows. Aucun moteur de texte/paquet externe n'est choisi sans inventaire de dépendances et licence. La première tranche codable est le contrat de données et ses fixtures, pas l'annonce d'un studio typographique livré.

## 6. Fermeture bornée

Q04C–Q04I : **rapprochements source conservés** ; contradiction de conception G6.3 arbitrée par la cible V2, sous revue. G6.3 produit reste non satisfait tant que le round-trip n'existe pas. Les tests proposés restent NOT_RUN. La certification de toutes les 80 UX et la promotion globale ne découlent pas de cette fiche. Les contrôles 01–25 sont traités dans le rapport de campagne commun ; aucun critère historique n'est retiré.
