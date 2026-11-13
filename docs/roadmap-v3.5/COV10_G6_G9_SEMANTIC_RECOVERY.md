# COV-10 — Rattrapage sémantique G6/G9 (candidate, non normatif)

Date : 2026-11-13. Autorité : V3.4 ACTIVE et exigences V3.3 intégrales. Ce document est une **proposition de rattachement V3.5**, non une nouvelle numérotation V34, une preuve de code ou une promotion. Sources vérifiées sur main : ROADMAP_TRACEABILITY_v3_3.md blob `a56edf8b2791590464a600627fbd3efdf27b9d28`, ROADMAP_HERITAGE_v3_3.md blob `c310adf3e972638c5a67332719bb2105ec37e688`, V3.4 lot 23 blob `177a0ecff5edd816e1bf879fc93c2a49efd83690`. Les 10 IDs sont absents des tickets V34 directs par choix historique. Leur statut demeure **GAP_HÉRITAGE_G6_G9** tant qu'une revue de critères et une adoption ne les rattache pas. main@HEAD exact NON_VÉRIFIÉ (recherche de commits non autoritative).

## 1. Dix décisions explicites, avec critères hérités

| ID | Priorité historique / dépendance vérifiée | Critère source conservé | Décision V3.5 candidate et propriétaire conceptuel (pas ticket V34) |
|---|---|---|---|
| S-021 | P2 ; S-007, S-011 | OCR affiche : texte préservé / averti | **RACCORDER** au sous-parcours OCR de composition ; reconnaissance non mutante, comparaison et confirmation |
| S-036 | P1 ; S-035 | Fontes → tracés : aucune substitution silencieuse | **AMÉLIORER** G6.3 ; conversion sur copie exportée, contrôle des glyphes, source éditable préservée |
| S-037 | P1 ; S-035 | Trois gabarits métiers testés | **RACCORDER** G6.4 ; étiquette, topper, carte, trois jeux de paramètres et reprises distinctes |
| S-044 | P2 ; S-030, S-035 | Diorama : prototype réel assemblé | **RACCORDER** G9 fabrication ; ne pas assimiler aperçu 2.5D et prototype |
| S-047 | P2 ; S-028, S-036 | OCR couverture : texte vérifié avant remplacement | **FUSIONNER** le moteur d'analyse avec S-021, mais conserver un scénario métier couverture distinct |
| S-064 | P1 ; dépendance non détaillée | Typographie/licence : rendu reproductible ou avertissement précis | **AMÉLIORER** le prévol typographique transversal G6 ; pas de redistribution implicite de police |
| S-066 | P2 ; dépendance non détaillée | Quatre plans alignables, assemblage réel et tolérances reportées | **AMÉLIORER** S-044 avec gate physique spécifique quatre plans, sans fusionner leurs critères |
| S-092 | P1 ; G6.3 | Aperçu police, caractères FR et absence de police contrôlés | **RACCORDER** au panneau texte existant, sans nouveau bouton « Smart Font » |
| S-099 | P2 ; G9 | Guide d'assemblage UI, prototype mesuré et assemblé | **RACCORDER** au parcours diorama et à son guide hors ligne, distinct de Smart Delivery SD2 |
| R33-028 | G6–G8 ; exigence transversale | Polices, licences et glyphes manquants visibles | **GARDER** comme gate transverse ; aucun export ne peut affirmer fidélité sans diagnostics |

Ces décisions sont **candidates** : aucune n'implique qu'un ticket V34 existant couvre réellement le critère. Conserver les textes originaux dans les sources, ne pas réécrire les archives. Les scénarios historiques T-V34-03-16 et les cinq exceptions 06/07 demeurent séparément ouverts.

## 2. Architecture proposée et invariants

**Composition texte** : réutiliser la source de vérité projet V1, ses objets/IDs, son writer CAS, son historique et ses exports réels ; localiser les API concrètes avant tout ticket de code. Contrat logique *à adapter aux ports existants* : `TextDraft{object_id,project_revision,unicode_text,font_identity,font_license_status,glyph_coverage,layout_mm,source_provenance}` → `Preview{warnings,render_digest}` → `Commit(expected_revision,command_id)`. Les champs ci-dessus sont un **schéma conceptuel**, pas une API implémentée ni une migration V2. Statuts police/licence/glyphes : KNOWN_OK / KNOWN_BAD / UNKNOWN, jamais UNKNOWN→PASS. Le texte reste modifiable dans le projet ; conversion en chemins dans une copie d'export seulement, avec contrôle de viewBox, dimensions mm, Unicode, géométrie et rendu comparé. PNG PTC, SVG Basic Cut, SVG CUT multicouche et SVG éditable sont quatre rôles distincts ; le texte d'édition n'est pas un contour de coupe garanti.

**OCR** : `OCRProposal{source_asset_sha,revision,regions,recognized_text,confidence_or_unknown,engine_version_or_manual,license}` reste un brouillon non mutant. Flux : sélectionner région → prévisualiser zones/texte → corriger caractère par caractère → diff → confirmer substitution ciblée → transaction CAS/Undo. OCR absent : saisie manuelle, pas de téléchargement automatique. Aucun résultat obsolète ne s'applique. Respecter consentement, provenance, données personnelles et refus. L'image originale et les masques float32 ne changent pas.

**Gabarits** : une recette paramétrique par usage (étiquette, topper, carte) instancie des objets existants, sans second format projet. Dimensions en mm, unités validées et versions de recettes ; erreurs structurées pour paramètres absents/NaN, collision ID, matériaux UNKNOWN. Prévisualisation réversible, sauvegarde/reprise et exports réels, sans profil machine inventé.

**Diorama** : `DioramaDraft{project_revision,plane_ids[4],order,dimensions_mm,alignment_marks,material_thickness_mm_or_unknown,tool_profile_state}` représente quatre plans indépendants, sans prétendre constituer un schéma persistant. Le guide fournit ordre, repères, matériaux et incertitudes. CUT/SCORE/DRAW/PRINT/FOIL restent distincts ; les repères et tolérances physiques ne sont pas certifiés par le rendu. Version Design Space, outil, tapis, matière, mesures et opérateur sont des preuves externes requises pour le gate physique. Les dioramas deux/trois plans peuvent être prévisualisés mais **ne satisfont pas S-066**.

## 3. UX, erreurs et accessibilité

Novice : depuis Express, choisir Texte / Gabarit / Diorama, voir un aperçu fidèle ou un avertissement explicite, corriger, annuler ou valider, fermer et reprendre. Expert : panneau contextuel avec réglages mm, typographie, ordre de plans et diagnostics, clavier/focus et raccourcis sans changement de moteur. Aucun bouton par exigence. Prévoir état vide, calcul en cours annulable, police absente, licence inconnue, OCR refusé, matériau inconnu, conflit de révision, manque d'espace disque. Undo sur édition locale ; confirmation proportionnée avant substitution OCR et écriture externe. Vérifier à terme 1366×768, DPI 200 %, contraste, navigation clavier, focus visible et mouvement réduit.

## 4. Matrice de tests proposés (tous NOT_RUN)

| Domaine | Positif | Négatifs (minimum trois) | Reprise et preuve |
|---|---|---|---|
| G6 texte/polices | Accents français, glyphes complets, export chemins comparé au rendu | police absente ; glyphes manquants ; licence de redistribution inconnue/interdite ; substitution non autorisée | Undo, conflit CAS, reopen, export hash ; Windows UI et comparaison de rendu distinctes |
| G9 OCR | Affiche et couverture synthétiques, correction validée et diff traçable | OCR absent ; faible confiance ; résultat de révision périmée ; région hors image | refus sans mutation, crash/annulation, reprise manuelle ; aucun modèle téléchargé |
| G6 gabarits | Trois projets séparés étiquette/topper/carte : save/reopen/export | mm négatifs/NaN ; ID dupliqué ; matériau UNKNOWN ; disque plein | rollback, réouverture et quatre rôles export vérifiés individuellement |
| G9 diorama | Quatre plans ordonnés, prévol géométrique, guide ; puis prototype physique mesuré | plan manquant ; repères désalignés ; épaisseur inconnue ; ordre inversé ; outil non pris en charge | brouillon conservé, annulation et conflit ; Design Space PASS uniquement avec protocole réel, coupe physique PASS uniquement avec mesures |

Fixtures : polices à licence vérifiée ou glyphes synthétiques, textes inventés, patrons géométriques générés, sans médias commerciaux ni polices redistribuées illégalement. Mesurer temps de rendu, RAM, durée d'ouverture et latence Undo sur Windows réel : **aucun chiffre mesuré ici**. IA/GPU : NON APPLICABLE aux fonctions manuelles ; pour OCR local optionnel, CPU/GPU et OOM à tester séparément sans promesse d'équivalence. Smart Delivery : NON APPLICABLE à ce lot, aucune modification du ZIP.

## 5. Découpage TDD et revue contradictoire

1. **G6-T1** : identifier les API de texte/objets/projet/export existantes sur main et PR, écrire fixtures polices/glyphes/licences, tests négatifs avant conception de port.
2. **G6-T2** : définir le prévol et l'UX texte, conserver l'édition native et les quatre exports distincts ; démontrer relecture et rollback.
3. **G9-T1** : contrat OCR brouillon/diff/CAS et repli manuel ; tests stale/consentement/absence moteur.
4. **G6-T3** : trois recettes métiers, tests dimension/identité/reprise.
5. **G9-T2** : diorama quatre plans et guide ; tests topologie/ordre ; protocole de terrain indépendant.
6. **Gate hostile** : examiner doublons avec éditeur de calques, patrons, SVG et SD2 ; vérifier que tout nouvel objet n'est qu'un raffinement d'un port existant ; refus de créer un second moteur OCR, un nouveau format projet ou un faux certificat de découpe.

DoD documentaire : dix exigences chacune liée à une fiche et à son critère historique, trois négatifs par domaine, port source vérifié avant codage, tests/risques/consentement/Undo décrits, aucune confusion de statuts. **Ce document ne satisfait pas encore** la vérification des API sur HEAD, la revue indépendante, ni les tests. La qualification sémantique des 437 scénarios reste ouverte.

## 6. Contrôle des 25 invariants R3

01–05 : héritage 24/141/140/80/437 inchangé ; 10 gaps explicités, pas résolus par fiction. 06 : aucune preuve produit. 07–09 : V1/CAS, quatre exports, opérations machine distinctes conservés. 10–13 : parcours, clavier/DPI, Undo, crash/concurrence spécifiés, UI non testée. 14 : IA optionnelle, OCR manuel ; pas de téléchargement. 15 : raster hors périmètre de modification, non régressé par conception. 16 : géométrie SVG, unités et trous à tester. 17 : gabarits oui ; batch/bibliothèque hors périmètre direct, obligations conservées. 18 : Smart Delivery hors périmètre direct, sans modification. 19 : opportunités globales O-001..033 non arbitrées dans ce lot ; restent ouvertes. 20 : protocole performance, mesures absentes. 21 : fixtures et licences protégées. 22 : branche documentaire uniquement, aucun merge ni changement producteur. 23 : réutilisation et anti-doublon proposés, audit code restant. 24 : adoption soumise à revue/CI/gouvernance distincte. 25 : aucune réduction du contrat, aucun PASS inféré.

**Prochaine action unique :** COV-10B, confronter ces dix fiches aux ports et tickets exacts du code main et des PR ouvertes, documenter propriétaire technique ou absence, puis produire une revue contradictoire sans changer V3.4.
