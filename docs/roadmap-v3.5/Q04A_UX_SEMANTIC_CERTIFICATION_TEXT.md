# V35-Q04A — Certification sémantique UX : protocole et premiers arbitrages B09–B14

**14/11/2026 — CANDIDAT / NON CERTIFIÉ.** Complément à COV17B, COV18A3C, Q02 et Q03. Ne remplace ni les 80 libellés #134, ni les critères V3.3, ni les 140 DoD V34. V3.4 demeure ACTIVE. Les liens ci-dessous sont des responsabilités de conception candidates, **pas** des liens historiques TEST→TICKET.

## 1. Règle de certification Q04, appliquée aux 80 IDs sans doublonner les audits

Pour chaque ID original, enregistrer : libellé exact #134 ; critère(s) V3.3 intégral(aux) avec citation de clause ; ticket(s) V34 et DoD exacts ou `ABSENT_SOURCE` ; scénario(s) V34 avec preuve explicite ou `SANS_LIEN_SOURCE` ; port code et SHA de blob ; delta d'architecture/UX ; positif, trois négatifs, annulation/concurrence/crash/rollback ; vérifications Windows/GPU/DS/physique séparées ; décision GARDER/RACCORDER/AMÉLIORER/FUSIONNER/AJOUTER/REPORTER/REJETER ; contradicteur ; statut de revue. **Aucun ID n'est certifié par la seule présence d'une ligne COV17.**

États par ID : `INVENTORIÉ` → `AUDITÉ` → `SPÉCIFIÉ` → `REVU` ; `CERTIFIABLE` uniquement si clauses et DoD exacts rapprochés et contradictions résolues. `CODE_MAIN`, `UI_WINDOWS`, `TEST_UNITÉ_PASS`, `DS_PASS`, `PHYSIQUE_PASS` sont des axes indépendants, jamais induits. Une exception de source peut être couverte par un **nouveau contrat V35 candidat**, sans fabriquer une liaison V34.

## 2. B09–B14 : arbitrages de risque immédiats

| UX | Décision candidate et source | Contrat de non-régression / trou restant | État |
|---|---|---|---|
| B09 texte éditable/polices | AMÉLIORER P1 ; Q03, S-036/S-064/S-092/R33-028 | `editor_v216` ne persiste que strokes ; un TextDraft non sauvegardable doit rester export-only explicitement. Vérifier licences, glyphes manquants, reopen CAS avant prétention d'édition durable | AUDITÉ, NON CERTIFIÉ |
| B10 texte courbe/monogrammes/étiquettes | RACCORDER P1 ; G6 et lot 06 | Projection texte-sur-chemin avec unité mm et police/licence ; un contour SVG externe n'est pas un objet texte V1 persistant ; garantir reprise ou annoncer export-only | AUDITÉ, NON CERTIFIÉ |
| B11 opérations typographiques et mise en page | RACCORDER P1 sous libellé exact de #134 à confirmer dans COV17B | Aucun moteur typographique distinct sans justification ; graphe de dépendance B09→B11, pas de second writer | AUDITÉ, NON CERTIFIÉ |
| B12 conversion texte en chemins | AMÉLIORER P1 ; **S-036/S-064/R33-028** selon COV18A3C corrigé | Ne pas inverser B12 et B13. Conversion irréversible dans export externe seulement, ou garder original et Undo ; provenance police/glyphes et droits ; vérifier trous/îlots/units avant CUT | AUDITÉ, NON CERTIFIÉ |
| B13 OCR contrôlé | RACCORDER P1 ; **S-021/S-047** selon COV18A3C corrigé | OCR produit proposition de texte avec incertitude, jamais preuve d'une police ou d'un objet éditable. CPU manuel sans téléchargement ; consentement pour modèle facultatif | AUDITÉ, NON CERTIFIÉ |
| B14 composition | GARDER comme capacité héritée, décision précise à confirmer dans COV17B | Distinguer plan de composition éphémère, masque float32, objet V1, groupe SVG externe et CUT ; aucune mutation silencieuse du schéma | AUDITÉ, NON CERTIFIÉ |

**Contradiction résolue au niveau conception :** B12 ≠ OCR ; B13 ≠ conversion en chemins. La lecture ancienne COV18A1B n'est pas source de vérité contre COV18A3C corrigé. **Non résolu :** rattachement clause-par-clause à tous les tickets et tests historiques, et capacité native de sauvegarder/recharger du texte. Les dix obligations G6/G9 restent distinctes et les six exceptions scénarios ne deviennent pas des liens historiques.

## 3. Micro-contrat candidat de transformation texte, sans changement V1

Entrée : `TextProposal{source_project_sha,source_subject_id?,utf8_text,font_ref{family,version,license,sha?},size_mm,baseline_path?,locale,confidence?}`. Le point d'interrogation signifie optionnel ; ne pas inventer de champ persistant dans V1. Les longueurs sont en **mm**, les glyphes en séquences Unicode ; `confidence` n'est pas une certification OCR. Sortie : `Preview{raster_preview,missing_glyphs,license_state,revision}` puis, après consentement, **un artefact externe** de rôle `SVG_EDITABLE` ou `SVG_BASIC_CUT` avec géométrie validée ; aucune écriture de texte dans `editor_v216`. `PNG_PTC` et `SVG_MULTILAYER_CUT` restent deux rôles séparés, non dérivés automatiquement de cette sortie.

Transitions : DRAFT→PREVIEW_READY→USER_REVIEW→EXTERNAL_EXPORT_READY→PUBLISHED, ou REJECTED/STALE/CANCELED/ERROR. Si SHA source change, publication bloquée jusqu'à rebase explicitement revue. Un export externe ne doit pas entrer dans Undo du projet ; la modification locale du brouillon est réversible. Un projet fermé sans commit ne prétend pas rouvrir le brouillon.

UX novice : saisir texte, voir police/glyphes et dimensions, aperçu sur canevas, correction avant export ; avertissement « non rééditable après fermeture » tant que la persistance n'est pas qualifiée. Expert : chemin, fonte, contours, trous, calques CUT et provenance affichés ; contrôle du rôle d'export. Clavier/focus, 1366×768, DPI 200 %, contraste et mouvement réduit sont des gates Windows futurs.

## 4. Tests proposés, non exécutés

Positifs : accents français et Unicode avec fonte autorisée ; texte-sur-chemin avec unités mm ; comparaison OCR proposé/corrigé ; conversion en chemins qui préserve trous et dimensions ; réouverture du projet V1 inchangé après export.

Négatifs : (N1) fonte absente/glyphe manquant → avertissement sans substitution muette ; (N2) police à licence inconnue → refus d'incorporation ; (N3) OCR hallucine un caractère → correction manuelle avant commit ; (N4) `source_project_sha` périmé → STALE et aucune publication ; (N5) courbe auto-intersectée ou échelle nulle → erreur géométrique ; (N6) DTD/entité externe SVG → rejet ; (N7) export existant → no-clobber ; (N8) disque plein pendant publication → aucun artefact présenté comme terminé ; (N9) deux éditeurs concurrents → CAS et relecture ; (N10) fermeture/crash pendant preview → V1 original inchangé. Les tests de CUT physique/Design Space et UI Windows restent **NOT_RUN** ; les tests de code futurs sont des recettes, pas des PASS.

Micro-lots TDD futurs (non exécutés) : (1) fixture Unicode/fontes libres + licence ; (2) validation de proposition/erreurs ; (3) preview pure et invalidation SHA ; (4) projection externe typée ; (5) QA SVG et publication no-clobber ; (6) UX Windows/accessibilité ; (7) essais DS/Explore 5 distincts. Alternative hostile : exporter des contours sans prétendre conserver texte éditable ; moins de risque que modifier V1, mais insuffisant pour certifier B09. Toute persistance V2 exige ADR, propriétaire et migration validée.

## 5. Audit 25 axes (statut de cette fiche)

01–05 : inventaires inchangés, sous-ensemble B09–B14 seulement, **couverture intégrale Q04 non close**. 06 : statuts indépendants ; HEAD main non confirmé. 07–09 : V1/CAS/float32 et quatre exports protégés ; machine non pilotée. 10–13 : novice/expert, canevas, accessibilité, annulation/crash/concurrence spécifiés, Windows NOT_RUN. 14 : IA OCR facultative et CPU manuel ; aucun téléchargement. 15 : raster/ICC **N/A** à la conversion de contours, QA PNG PTC demeure exigence globale. 16 : SVG/topologie/mm contrôlés en recette. 17 : batch/Fabrique **N/A** à ce micro-contrat, héritage maintenu. 18 : Smart Delivery **N/A** à cette fiche ; publication externe ne certifie pas ZIP. 19 : autres opportunités hors micro-lot, non supprimées. 20 : métriques de latence/VRAM à mesurer, aucun seuil PASS inventé. 21 : sécurité XML/licences/confidentialité. 22 : branche docs uniquement, producteur V3.4 intact. 23 : réemploi writer/export existants, pas nouveau store. 24 : adoption/revue globale non effectuées. 25 : réemploi COV17/COV18, pas de nouvel audit de 80 fiches.

**Couverture globale historique (non recalculée ici)** : 24 lots, 141 exigences, 140 tickets, 80 UX, 437 scénarios inventoriés ; 431/437 liens source explicites, six exceptions ; dix G6/G9 sans ticket V34 explicite. **UX certifiées : 0/80.** Cette fiche ne transforme aucun scénario proposé en PASS.

**Prochaine action UNIQUE Q04B :** comparer COV18A3C et COV17B aux clauses exactes du lot 06 et au registre V3.3 pour B09–B14, puis établir les associations tickets/DoD/scénarios individuelles et corriger tout libellé provisoire B11/B14 avant certification.
