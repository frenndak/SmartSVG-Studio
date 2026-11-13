# SmartSVG V3.5 — maître de réalisation priorisé

**14 novembre 2026 — CANDIDAT NON NORMATIF.** Point d'entrée de la branche existante `roadmap/v3-5-design-candidate-20261112`, programme [#142](https://github.com/frenndak/SmartSVG-Studio/issues/142). Ce document réunit et ordonne la conception existante ; il ne crée ni nouvelle branche maîtresse, ni nouvelle version de produit, ni tickets de remplacement. V3.4 reste active pour le code.

**Instruction propriétaire de cette session :** compléter au plus vite et avec la meilleure couverture possible la V3.5, avec l'ensemble des améliorations discutées, de la plus intéressante/urgente/utile à la moins nécessaire. La vitesse vient du réemploi et de la réduction des doublons, jamais de la suppression des critères, des fonctions difficiles ou de la distinction entre conception et produit livré.

## 1. Une seule référence et deux travaux séparés

Sources primaires : [programme #142](https://github.com/frenndak/SmartSVG-Studio/issues/142), [80 UX #134](https://github.com/frenndak/SmartSVG-Studio/issues/134), [extensions #141](https://github.com/frenndak/SmartSVG-Studio/issues/141), commentaires [SD-V1](https://github.com/frenndak/SmartSVG-Studio/issues/141#issuecomment-6832674467) et [SD-V2](https://github.com/frenndak/SmartSVG-Studio/issues/141#issuecomment-6833936737), 24 lots V3.4 et critères intégraux V3.3. Les dossiers COV restent les approfondissements par domaine.

La PR documentaire parallèle **#143 n'est pas la conception V3.5 maîtresse** : elle a omis la branche existante lors de sa création. Ses observations et preuves utiles doivent être rapprochées ici, sans importer ses 15 tranches comme nouvelle numérotation officielle. Le code de commande d'historique [#144](https://github.com/frenndak/SmartSVG-Studio/pull/144) est un candidat distinct ; son succès en CI n'implique ni fusion dans main ni boutons Annuler/Rétablir livrés. Les critères V34-035/038 restent à qualifier dans le parcours natif.

**Conception :** compléter cette branche, ses contrats, dépendances et preuves de non-perte. **Ingénierie :** continuer les parcours V3.4 autorisés. La conception P2 n'attend pas leur implémentation ; le premier logiciel utilisable n'attend pas la fin de toute la R&D P2. Aucune tâche horaire supplémentaire et aucun changement de fréquence nécessaires.

## 2. Critères d'ordre — valeur avant spectaculaire

L'ordre ci-dessous est un **ordre d'entrée et de livraison de tranches**, pas une modification des priorités normatives V3.3/V3.4. Les dépendances ne bloquent que leurs consommateurs. Un gros lot peut livrer plusieurs incréments : Smart Delivery ne doit pas attendre la prise en charge des quatre formats, et le mode manuel ne doit pas attendre l'IA.

| Critère | Décision pratique |
|---|---|
| Risque de perte ou résultat trompeur | Traiter projet, recovery, identité, unités et QA avant de multiplier les traitements |
| Utilité immédiate pour une création réelle | Favoriser importer → sélectionner → corriger → enregistrer → exporter et retrouver les fichiers |
| Gain répété et réduction des erreurs | Ensuite pack de livraison, conseil de découpe, impression guidée, outils de composition et lots |
| Réemploi et dépendance minimale | Consommer les moteurs et writers existants ; prototype borné si le port manque ; aucun bus universel ou V2 imposé pour les fonctions V1 possibles |
| Coût/risque et incertitude | Conserver mais différer les effets complexes, génération, rig de personnage, simulation 3D et analyse de photo |

Pas de score numérique fabriqué ni de date de livraison inventée. Effort/risque restent qualitatifs jusqu'au prototype. À bénéfice comparable, livrer l'incrément plus petit et plus facilement vérifiable.

## 3. Ordre de livraison recommandé

| Rang | Capacité / unité existante | Première tranche utile et résultat vérifiable | Dépendance réelle / suite |
|---:|---|---|---|
| 1 | **W01/W02 — socle natif fiable** | Ouvrir/créer, même sujet, aperçu manuel, retouche, sauvegarde, réouverture, Undo/Redo et recovery ; notes et source préservées | Writers V1 et identité ; réconcilier #138/#139/#144 avant d'ajouter des doublons |
| 2 | **W02 + W13 — sélection et canevas utilisables** | Clic/lasso/pinceau, garder/exclure plusieurs zones, inspection 100 %, modes novice/expert, clavier ; gestes réversibles et coordonnées source | A02/A03 ne sont pas une segmentation intelligente automatique A04 ; affiner A04/A05 sur CPU puis IA facultative |
| 3 | **W03/W04 — sorties réelles et prévol par usage** | PNG Print Then Cut puis Basic Cut dans le bureau, dimensions et avertissements, dossier choisi et fichiers relus ; poursuivre séparément les quatre contrats | Un PNG n'invente pas un SVG ; les quatre rôles restent exigibles pour clore W03 ; UI et QA accessibles dès chaque tranche |
| 4 | **W05/W06 — Smart Delivery, première signature V3.5** | SD0 plan sans écriture → SD1 ZIP vérifié dès **un** export réel → SD2 guide hors ligne facultatif | Plan + artefact réel seulement ; pas quatre exporteurs achevés, pas de nouveau writer ; SD3 historique/recréation plus tard |
| 5 | **W07/W08 — réduire les ratés Cricut** | Smart Cut Advisor (diagnostic, détails fragiles, variantes comparées) ; assistant PTC et guide Design Space versionné | Métriques/artefact fiables ; dimensions et capacités inconnues visibles ; aucun « prêt machine » inféré |
| 6 | **W02/W03 — édition vectorielle et couleur** | Calques/objets, poignées, alignement, recoloration, nœuds/Bézier et booléens ; SVG éditable réellement reconstruit | Modèle objet/texte et persistance à décider explicitement ; aucun champ clandestin V1 ni second canevas |
| 7 | **W10/W11 — texte et gabarits réutilisables** | Texte éditable/polices/glyphes → texte sur chemin/effets → conversion sur copie ; étiquette/topper/carte | Critères G6 P1 conservés ; licence/police et sauvegarde/réouverture prouvées avant d'activer une fausse édition |
| 8 | **W12 — bibliothèque et production répétée** | Récents/recherche/miniatures/duplication, puis planches 12/24/50, placements verrouillés, CSV de base et reprise des erreurs isolées | Index reconstructible et identité ; lot de 50 partitionné si moteur limité à 32 ; aucune troncature |
| 9 | **W14 — accélérations locales utiles** | Segmentation facultative, affinage, matting et HD conditionnelle, propositions explicables | Catalogue/licence/hash/consentement et repli ; mesurer CPU/RTX 8 Go ; aucun modèle ni réseau requis pour le socle |
| 10 | **W09/W16 — économie de fabrication** | Weeding en diagnostic non destructif, Smart Cost indicatif, séries noms/numéros/QR et recettes partageables | Prix utilisateur, nesting fiable et contrats texte ; lignes de coupe Weeding après géométrie et coupons physiques |
| 11 | **W16 — créativité avancée conservée** | Diorama quatre plans/OCR hérités avec critères propres ; perspective, déformation, articulation et reconstruction locale | Séparer obligations G9 conservées et nouvelles capacités facultatives ; étude par opération, pas un moteur universel |
| 12 | **W16 — recherche la moins nécessaire au premier usage** | Photo de découpe/feedback incertain, autres marques, optimisation multicritère, génération et pliage 3D éventuel | Faisabilité/licences/corpus/mesures ; absence de résultat = refus ou mode manuel, pas de promesse générique |
| transverse | **W00/W13/W15 — qualité, UI et installation** | Registre de non-perte, accessibilité, sécurité, offline, packaging/update/rollback et tests par parcours | À chaque rang ; aucun report en toute fin. Benchmark Tk/Qt/Tauri borné ; migration seulement si blocage mesuré |

Les rangs 6–9 peuvent progresser sur fixtures indépendamment de l'attente d'une preuve matérielle des rangs précédents. L'OCR automatique et la génération ne remplacent pas les contrats de texte, de masque ou de vecteur.

## 4. Couverture des fonctions, sans inflation

Le [registre structuré PRIORITY_REGISTER.json](PRIORITY_REGISTER.json) conserve individuellement : **80 UX**, les **15 groupes exacts du programme #142** (groupes, pas 15 nouveautés indépendantes), les **33 opportunités et leurs huit rejets**, les **24 lots**, **141 exigences**, **140 tickets** et **437 scénarios source**. Les libellés UX de #134 et l'ordre/priorité d'origine restent distingués de l'ordre de livraison recommandé ici.

L'[index de toutes les fonctions triées](PRIORITY_INDEX.md) donne pour chaque UX son libellé original, sa priorité source, sa première tranche de livraison et ses dossiers de conception. Les fonctions P2 ne sont pas effacées. Les dossiers COV18 corrigés priment leurs anciennes correspondances, notamment **B12 = texte→chemins, B13 = OCR**, et les différences entre couche couleur, opération de fabrication, masque et objet.

Un ID relié à une unité ne prouve pas que tous ses critères sont satisfaits. Les 437 assertions restent proposées ; les six sans lien TEST→TICKET explicite sont tracées séparément. Les dix exigences G6/G9 sans V34 direct gardent leurs critères et propriétaires candidats W10/W11/W16. Les huit rejets de COV19 restent rejetés, même s'ils paraissent spectaculaires.

## 5. Compléments fonctionnels obligatoires par famille

| Famille | Ce que la consolidation doit conserver, même si moins urgent |
|---|---|
| A01–A16 | Import formats/lot/EXIF/ICC, gestes/multi-zones, sélection intelligente et affinage ; alpha, anti-halo et détails ; contrôle visuel ; couleur/palette/profils ; quatre rôles vectoriels, courbes, booléens, simplification et métriques |
| B01–B14 | Objets typés, calques/lock/ordre/opacité, accessoires, transformations/alignements ; perspective/warp/clip ; articulation et reconstruction opt-in ; texte/polices/chemin/effets/contours/OCR ; composition avec marges et gabarits |
| C01–C18 | Stickers/vinyle/multicouche/pochoir/centerline, opérations distinctes, prévol/profils/variantes, quatre exports et transfert ; duplication/nesting/verrouillage/économie/reprise ; patrons/plis/épaisseur, aperçu 2D et simulation 3D éventuelle |
| D01–D12 | Fournisseurs CPU/IA, prompts combinés et variantes, matting/HD/génératif/inpainting facultatifs ; catalogue/licences/versions/hashes, budget/annulation, recettes, batch/CSV et assistant explicable |
| E01–E20 | Bibliothèque/collections/historique, atelier/canevas/comparaison, contexte/novice/expert/thèmes/accessibilité ; Undo/recovery/asynchrone/diagnostics ; QA raster/SVG/fabrication, installation/offline/privacy et aide |

## 6. Niveau de détail exigé avant de donner une fiche au développeur

Le contrat des [25 contrôles](AUTOMATION_QUALITY_CONTRACT.md) reste intégral. Pour chaque tranche : besoin novice/expert ; exemple d'entrée et de sortie avec unités/version ; références de code et consommateurs vérifiés au même SHA ; ce qui existe versus ce qui est proposé ; invariants projet/identités/float32 ; dépendances minimales ; gestes/états/Undo ; licences/privacy ; trois négatifs pertinents au minimum ; annulation/crash/concurrence/disque plein ; tests par axe et DoD ; effort/risque qualitatifs et rollback.

Un petit geste local réversible se voit immédiatement et dispose d'Undo. Une publication externe ou opération coûteuse exige choix et confirmation proportionnés ; aucune popup systématique ni IA silencieuse. La sortie du modèle ne valide jamais seule une mutation.

**DoD de tranche :** résultat observable dans le parcours visé, contrôles du fichier réellement produit, erreurs récupérables, tests pertinents sans skip critique caché et limites affichées. Un bouton présent, une image de démonstration ou une CI générique ne prouvent pas la fonctionnalité entière.

## 7. Architecture et frontières non négociables

Projet unique `.smartsvg` V1 + CAS ; un writer/historique existant ; sources/masques float32 préservés. Les modèles d'objets/texte/transform non représentables dans le schéma actuel restent des propositions jusqu'à ADR et migration explicite sur copie. ComfyUI demeure un adaptateur facultatif. Le chemin manuel/CPU est toujours une voie réelle.

PNG PTC, SVG Basic Cut, SVG CUT multicouche et SVG d'édition sont quatre rôles. `Artifact.use` V1 n'accepte historiquement que trois valeurs : le rôle CUT multicouche externe ne doit jamais être déguisé en édition. CUT/SCORE/DRAW/PRINT/FOIL sont des opérations, pas des formats supplémentaires. Capacités machine/support/outillage = KNOWN_SUPPORTED / KNOWN_UNSUPPORTED / UNKNOWN ; l'inventaire de l'utilisateur est un autre objet.

Smart Delivery consomme des artefacts, ne refait ni leur export ni la sauvegarde du projet. Guide hors ligne inerte, ZIP externe unique publié sans écrasement après relecture ; ni copie multiple dite atomique, ni génération de repères capteur, ni commande directe Cricut. La comparaison photo n'est pas une certification matérielle.

## 8. Accélérer la conception sans perdre le contrôle

1. Reprendre le dernier vrai commit/cursor, comparer les SHAs des sources pertinentes, puis produire un delta utilisable. Le présent maître résout l'ordre d'entrée ; il ne justifie pas de recommencer les 80 audits.
2. Réutiliser les COV déjà détaillés ; n'ouvrir une fiche que pour une ambiguïté, un contrat manquant ou une divergence identifiée. Finir chaque défaut du registre [COMPLETION_QUEUE.md](COMPLETION_QUEUE.md), pas une nouvelle liste d'idées.
3. Utiliser une table source→critère→port→consommateur→recette→statut comme travail de clôture. Si le port manque, écrire le contrat futur et sa preuve attendue ; ne pas bloquer la conception sur l'absence du futur produit.
4. Faire la revue indépendante du lot consolidé puis les corrections ; conserver les risques restants explicitement. Aucun pourcentage mélangeant inventaire et produit.
5. Une fois les gates documentaires prêts, une seule PR de conception depuis cette branche ; pas de promotion d'AGENTS ni changement de tâche dev implicites.

**État de cette passe :** ordre de livraison et inventaire consolidés, COV22 ports/SD-V1/SD-V2 rapprochés ; pas « V3.5 adoptée » ni « 80 fonctions prêtes à coder ». Les derniers écarts sémantiques et décisions d'architecture sont suivis dans la file de clôture.
