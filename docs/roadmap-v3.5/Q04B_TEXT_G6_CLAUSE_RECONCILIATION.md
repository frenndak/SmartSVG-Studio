# V35-Q04B — B09–B14 : rapprochement des libellés originaux et des gates G6/G9

**14/11/2026 — CANDIDAT, AUDITÉ PARTIELLEMENT, NON CERTIFIÉ.** Succède à Q04A. V3.4 demeure ACTIVE. Cette fiche ne crée ni ticket historique ni persistance texte V1. Sources directement lues : `INHERITANCE_REGISTER.md` blob `cc0dd60e598fab4c7b90910c3f1d54687eaaeee2`, `docs/ROADMAP_HERITAGE_v3_3.md` blob `c310adf3e972638c5a67332719bb2105ec37e688`, Q04A blob `8d91d1f571b0ef41ab01841a8c61205f826007f6`. Les intitulés du lot 06 et ses DoD n'ont **pas** été obtenus sous leur chemin exact dans ce passage : aucune certification DoD n'est déclarée.

## 1. Corrections vérifiées par registre canonique

| ID | Libellé exact hérité #134 via registre | Gate et décision candidate | Réserve |
|---|---|---|---|
| B09 | texte éditable/polices/typographie | G6.1, G6.3, **AMÉLIORER P1** | G6.3 exige le texte modifiable **dans le projet**, non satisfait par export-only |
| B10 | texte courbe/circulaire/chemin/monogrammes/étiquettes | G6.1/G6.3, **RACCORDER P1** | courbes et monogrammes ne prouvent ni sauvegarde ni découpe |
| B11 | **effets de texte/contours/ombres/textures/dégradés** | G6.3 et G5.5, **RACCORDER P1** | Q04A « opérations typographiques et mise en page » était un intitulé provisoire trop vague ; préserver séparément ombres, textures et dégradés |
| B12 | texte→chemins, fusion et contrôles de fabrication | G6.3/G5.5, **AMÉLIORER P1** | trous, winding, unités et fusion doivent être testés, SVG éditable ≠ CUT |
| B13 | OCR facultatif→texte éditable après vérification | G9, **RACCORDER P2 selon S-047** ; capacité préservée | OCR n'est pas un substitut de B12, ni une police détectée |
| B14 | **Smart Compose : marges/alignement/hiérarchie/modèles visuels.** | G6.2/G6.6/G6.7, **GARDER P1** | Q04A « composition » était trop générique ; hiérarchie et modèles visuels restent explicites |

**Clauses exactes G6 relevées :** G6.1 texte/formes/position/rotation/calques avec preuve étiquette ; G6.2 groupe/alignement/grille/palette et placement préservé ; G6.3 texte modifiable dans projet et importable en tracés, police manquante sans substitution ; G6.4 trois gabarits métiers (étiquette/topper/carte) avec prototype de chacun ; G6.5 historique/variantes et réouverture ; G6.6 souris/clavier, réglage mm, Undo ; G6.7 démarrage par usage sans tutoriel externe. **Ne pas rabattre G6.4–G6.7 sur B09–B14 seuls :** ils concernent aussi les autres fonctions UX, les lots V3.4 et les scénarios de fabrication.

**Contradiction matérielle persistante :** Q03/Q04A autorisent un brouillon de texte export-only sans mutation V1, mais cela ne remplit pas G6.3 « texte modifiable dans projet ». Décision candidate : maintenir l'export externe honnête comme **capacité partielle**, garder G6.3 **OUVERT**, et soumettre tout modèle persistant/migration V2 à ADR + revue propriétaire séparée. Aucune modification de schéma implicite.

## 2. Traçabilité négative explicite

Le registre des tickets lot 06 inventorie V34-032..040, mais ses associations visibles concernent R33-004/005/014 et S-003/008/026/027/053/067, **pas** les exigences G6/G9 S-021, S-036, S-047, S-064 ou R33-028. Ces cinq exigences demeurent `ABSENT_TICKET_V34_DIRECT`, sans invention de lien. Les autres exigences G6/G9 de Q02 restent également ouvertes. Les renvois T-V34-22-xx sont des **liens de planification** et non des tests texte qualifiés. Le fichier du lot 06 exact, ses DoD et ses scénarios doivent être confrontés avant toute promotion de B09–B14 en REVU/CERTIFIABLE.

## 3. Contrat d'interface candidat, ergonomie et sécurité

Conserver un `TextProposal` transitoire (Unicode, police/version/licence, dimensions mm, SHA projet source, révision, éventuellement chemin et score OCR) ; prévisualisation non mutante ; état `DRAFT → PREVIEW → REVIEWED → EXTERNAL_EXPORT`, ou `STALE/CANCELED/ERROR`. Le writer .smartsvg V1/CAS reste seule autorité du projet. Aucun TextNode persistant inventé. Les sorties `PNG_PTC`, `SVG_BASIC_CUT`, `SVG_MULTILAYER_CUT`, `SVG_EDITABLE` restent quatre contrats distincts ; un effet visuel ne devient jamais automatiquement un contour CUT. Aucune capacité machine KNOWN n'est déduite d'un aperçu.

Novice : entrée texte, aperçu dimensions, avertissement de non-reprise, correction glyphes, consentement avant écriture externe. Expert : gestion du chemin, des effets B11 et des trous, mesure en mm, accès aux avertissements de licence et de compatibilité. Barre contextuelle et canevas sans nouveau moteur de calques ; Undo sur brouillon, pas sur publication externe. Clavier, focus, 1366×768, DPI 200 %, contraste et mouvement réduit sont des **recettes Windows NOT_RUN**. OCR facultatif avec correction humaine, sans téléchargement implicite ; CPU/manuel reste possible sans prétendre fournir la même précision.

## 4. Recettes TDD à exécuter (aucun PASS dans ce cycle)

Positifs : accent/glyphe autorisé ; B11 contour/ombre/texture/dégradé visuellement distinguables et non promus en CUT ; B12 texte→chemins avec trous et dimensions ; B13 OCR corrigé avant export ; B14 marges/alignements/hiérarchie conservés au preview ; roundtrip V1 inchangé.

Négatifs : (N1) fonte absente et substitution silencieuse interdite ; (N2) licence d'incorporation inconnue → pas d'embed ; (N3) SVG avec entité externe/DTD → rejet ; (N4) projet SHA changé pendant OCR/preview → STALE ; (N5) géométrie auto-intersectée ou dimensions nulles → rejet CUT ; (N6) texte à effet visuel exporté en Basic Cut → refus d'équivalence ; (N7) fichier externe existant → no-clobber ; (N8) disque plein → publication atomique non annoncée ; (N9) crash/fermeture → projet V1 intact ; (N10) deux sessions → conflit CAS sans écrasement. Fixtures synthétiques sous licences autorisées. Mesurer latence, RAM et coût de rendu avant fixation de budgets ; aucun chiffre PASS inventé.

Découpage futur : TDD1 inventaire exact lot 06/DoD/scénarios ; TDD2 validation TextProposal ; TDD3 preview et Undo ; TDD4 effets B11 et Smart Compose B14 ; TDD5 conversion sûre B12 et OCR B13 ; TDD6 QA des quatre exports ; TDD7 essais UI Windows et DS/Explore 5 physiques indépendants. Aucun nouveau code développé ici.

## 5. Contre-expertise et 25 contrôles

Alternative minimale : exporter des chemins externes sans modifier V1. **Acceptable** comme fonctionnalité limitée, **insuffisante** pour G6.3. Alternative migration persistante : valeur élevée, risque de CAS/writer/compatibilité ; **REPORTER** jusqu'à ADR et approbation. Ne pas multiplier stores, moteurs texte, assistants ou tickets dupliqués.

Axes 01–05 : 24/141/140/80/437 conservés, six UX traitées partiellement, six exceptions de scénarios et dix exigences G6/G9 non résolues. 06 : preuves disjointes, main HEAD non vérifié. 07–09 : V1/CAS, quatre exports, tri-state préservés. 10–13 : parcours, Undo, accessibilité, crash/concurrence spécifiés, Windows NOT_RUN. 14 : OCR IA facultative, repli manuel ; 15 : ICC/alpha raster N/A pour typographie pure mais reste gate PNG PTC ; 16 : SVG/mm/topologie à tester ; 17 : batch/Fabrique N/A pour cette fiche, héritage maintenu ; 18 : ZIP Smart Delivery N/A, export seul non équivalent à livraison ; 19 : autres opportunités inchangées ; 20 : performance non mesurée ; 21 : licences/XML/confidentialité ; 22 : branche documentaire uniquement ; 23 : aucun second writer ; 24 : revue/adoption non effectuées ; 25 : delta réel = correction B11/B14 + conflit G6.3 rendu explicite, sans prétendre clôturer les DoD.

**Statut final :** B09–B14 `AUDITÉ PARTIELLEMENT / NON CERTIFIÉ`, 0/80 UX certifiées. Couverture historique 24/141/140/80/437 ; 431/437 liens explicites, six exceptions et dix G6/G9 sans ticket direct. Tous nouveaux tests NOT_RUN, aucun Windows/GPU/Design Space/coupe physique PASS ajouté.

**Prochaine action UNIQUE Q04C :** identifier le chemin exact du lot 06 V3.4 et confronter chaque DoD et scénario B09–B14 aux clauses G6.1–G6.7, en consignant ABSENT_SOURCE quand nécessaire.
