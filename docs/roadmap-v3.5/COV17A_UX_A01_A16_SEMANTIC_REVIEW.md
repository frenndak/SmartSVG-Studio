# COV-17A — Revue sémantique individuelle UX A01–A16 (13 novembre 2026)

**Statut : CANDIDAT / AUDIT DOCUMENTAIRE, NON ADOPTÉ, tests NOT_RUN.** V3.4 reste ACTIVE. Cette fiche complète la cartographie UX #134 et la fiche COV-16 sans modifier les descriptions originales conservées dans INHERITANCE_REGISTER. Elle constitue une décision **de conception** pour chacun des 16 IDs, et non une certification codable de chaque capacité.

## Sources et limites de preuve
- [#134](https://github.com/frenndak/SmartSVG-Studio/issues/134), [INHERITANCE_REGISTER](INHERITANCE_REGISTER.md), [UX_ARCHITECTURE_AND_WORKFLOWS](UX_ARCHITECTURE_AND_WORKFLOWS.md), [BACKLOG_AND_DEPENDENCIES](BACKLOG_AND_DEPENDENCIES.md), [COV10C](COV10C_V1_TEXT_EXPORT_PORTS.md), [25 contrôles](AUTOMATION_QUALITY_CONTRACT.md).
- Les correspondances exactes S/R33/T-V34 pour chaque ID **restent à extraire des lots V3.4 et à vérifier** avant certification. Les propriétaires Wxx ci-dessous sont des unités candidates, jamais de nouveaux tickets V34.
- Code connu par audits antérieurs : `LoadedProject`, `ManagedWorkspace`, `editor_v216`, writer/CAS et exporteurs historiques ; **aucune nouvelle lecture complète du code A01–A16 ni exécution Windows dans cette fiche**. Ne pas déduire la disponibilité d'un outil à partir de son nom.

## Matrice d'arbitrage individuelle

| ID | Décision candidate | Propriétaire | Contrat et différence V3.4→V3.5 | Trois tests négatifs minimaux |
|---|---|---|---|---|
| **A01** | RACCORDER | W01/W12 | Import réel, contrôle type MIME/signature, limites pixel, orientation EXIF, DPI absent UNKNOWN; lot atomique par fichier | SVG actif, decompression bomb, doublon SHA, interruption lot |
| **A02** | AMÉLIORER | W02/W13 | Gestes clic/lasso/rectangle/ellipse/pinceau sur un unique canevas; coordonnées image source, non viewport; aperçu non mutant | zoom transform erroné, polygone auto-intersecté, pointer capture perdu |
| **A03** | RACCORDER | W02 | Algèbre union/intersection/soustraction/inversion sur sélection binaire ou float32 explicitée; conserver trous et îlots | masques tailles différentes, sélection vide, inversion hors bornes |
| **A04** | REPORTER IA / GARDER CPU | W02/W14 | Prompt grossier→proposition de masque, fournisseur/version/licence/consentement, alternatives incertaines; pas de commit silencieux | modèle absent, OOM RTX 8Go, réponse périmée |
| **A05** | AMÉLIORER | W02 | Morphologie en pixels source et rayon déclaré, preview local et rollback, détails fins avec comparaison alpha | rayon négatif, disparition îlot, conflit CAS |
| **A06** | RACCORDER | W02/W03 | Alpha de sortie dérivé du masque float32, source RGB intacte, bords sur fonds contrastés | alpha tout nul, frange RGB, export sans source |
| **A07** | AMÉLIORER | W02/W03 | Anti-halo RGB non destructif, fragments classés en aperçu, ne jamais supprimer trous sans validation | trous utiles supprimés, prémultiplication incorrecte, microformes perdues |
| **A08** | REPORTER HD / GARDER retouches CPU | W02/W14 | Netteté/bruit/contraste séparés de résolution réelle; upscale facultatif provenance et coût affichés | image 1px, dépassement mémoire, hallucination de détails |
| **A09** | GARDER | W02/W13 | Damier + fonds sombre/clair + zoom pixel 100% + comparaison avant/après synchronisée | cache stale, profil ICC absent, écart rendu/export |
| **A10** | RACCORDER | W02/W03 | Pipette RGB/alpha, palettes et quantification comme transformations réversibles, dégradés distincts de couches CUT | profil couleur incohérent, palette vide, alpha effacé |
| **A11** | AMÉLIORER | W03/W04 | Séparer couches visuelles couleur et opérations machine; profils d'impression UNKNOWN et rendu preuve | profil ICC invalide, nombre couches explosif, confusion PRINT/CUT |
| **A12** | RACCORDER | W03/W07 | Silhouette/contour/centerline/multicouleur sorties typées, SVG éditable distinct du SVG CUT | trous inversés, XML actif, centerline faussement fermée |
| **A13** | AMÉLIORER | W02/W03 | Nœuds Bézier avec unités source et transformations explicites, poignées clavier et Undo par transaction | NaN coordonnées, tangente dégénérée, sortie viewBox erronée |
| **A14** | RACCORDER | W03/W04 | Booléens géométriques sur chemins fermés, winding/holes déterministes, QA avant CUT | polygone ouvert, auto-intersection, îlots perdus |
| **A15** | AMÉLIORER | W07 | Simplification non destructive avec mesures fidélité/topologie et variantes; conserver l'original | fusion de trous, décalage dimensionnel, perte angles fins |
| **A16** | REPORTER IA / GARDER métriques | W07/W14 | Variantes fidèle/équilibrée/facile et métriques séparées fidélité, complexité, topologie; pas de score de coupe certifié | score non calibré, variantes identiques, métriques sur preview stale |

**Sémantique des décisions :** REPORTER IA/HD ne supprime jamais l'ID ni les critères hérités ; seul le calendrier de l'accélération est candidat. FUSIONNER les surfaces UX ne fusionne pas les exigences ni les preuves. Les 16 intitulés et leurs périmètres demeurent intacts dans le registre #134.

## Contrat transversal candidat, sans nouvelle autorité

**Entrée** : image ou SVG validé avec `source_sha256`, `subject_id`, `revision`, dimensions `width_px/height_px`, orientation et profil déclarés ; masques float32 en espace image. **Calcul** : transformation locale réversible ou job facultatif avec provenance, `generation_id`, annulation et rejet du résultat stale. **Sortie** : proposition `preview` non persistée puis commit via writer/CAS V1 existant uniquement après validation. Les pixels ne deviennent pas implicitement chemins CUT, ni la sélection un masque persisté. La V2 de projet n'est pas autorisée implicitement.

**UX novice** : importer, voir les limites et le fond transparent, choisir geste de sélection, corriger au pinceau, comparer avant/après, appliquer et exporter un rôle réellement disponible. **UX expert** : inspecter source SHA, unités px/mm, masque et topologie, seuils et provenance, comparaison des variantes, états UNKNOWN et journal d'Undo. Un seul atelier/canevas, context bar et commandes clavier ; état vide, calcul en cours, erreur, annulation et conflit lisibles à 1366×768/DPI 200 %, sans supposer ces tests PASS.

**Sorties inchangées** : PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche, SVG éditable. Le prévol statique ne certifie ni Design Space ni coupe réelle ; profil machine tri-state KNOWN/UNKNOWN. IA opt-in, licence/hash/version/VRAM et réseau explicitement consentis, repli CPU/manuel. Pas de modèles, médias ou polices propriétaires embarqués.

## TDD et tests à programmer (tous NOT_RUN)
1. **Micro-lot A** : retrouver pour A01–A16 les API, tests, tickets V34, scénarios et DoD exacts (inclure consommateurs) ; documenter `EXISTANT`, `PR`, `ABSENT_NON_PROUVÉ`, et les risques de double moteur.
2. **Micro-lot B** : fixtures synthétiques RGB/alpha, ICC, EXIF, SVG sûr, trous/îlots, géométrie et masques float32 ; tests de chaque positif (résultat vérifié) et des 48 négatifs ci-dessus ; aucun média tiers.
3. **Micro-lot C** : tests CAS stale, annulation pendant calcul, crash avant/après commit, fermeture de session, restauration Undo/Redo, conflits de fichiers et rollback. Vérifier la stabilité de `subject_id`, SHA source, writer unique et absence de mutation en preview.
4. **Micro-lot D** : Windows Tk réel, clavier/focus, 1366×768/DPI 200 %, latence et pic mémoire instrumentés sur corpus défini. Définir des budgets **avant** mesures, ne pas inventer de résultats. Tester export PNG et SVG dans leurs rôles respectifs ; DS et coupe physique restent des gates séparés.
5. **Micro-lot E** : revue hostile de fidélité couleur/alpha, topologie et sécurité XML, dégradation CPU sans modèle, licences et alternatives plus simples ; fermer chaque écart par preuve exact SHA et DoD, pas par renvoi générique.

**Alternatives rejetées à ce stade :** 16 nouveaux boutons « Smart », un second projet, une seconde queue de jobs, un second writer, une conversion automatique sélection→masque→CUT, un score de facilité de coupe présenté comme mesure terrain. **Alternatives retenues sous réserve :** barre contextuelle unique, prévisualisations locales et variantes réversibles, opérations CPU en premier.

## Contrôle des 25 axes (documentaire, sans certification)
01–05 : 24/141/140/80/437 conservés, 16 IDs A décidés mais critères exacts non certifiés ; 06 : preuves disjointes ; 07 : projet V1/CAS/float32/identités ; 08 : quatre sorties ; 09 : opérations et profils tri-state ; 10–13 : novice/expert, canevas, accessibilité, Undo/erreurs/crash proposés ; 14 : IA facultative, licences/VRAM ; 15–16 : raster, couleur, SVG/topologie ; 17 : lot/CSV et Fabrique hors périmètre direct, A01 batch conservé ; 18 : Smart Delivery non modifié ; 19 : idées #141 et opportunités non arbitrées ici ; 20 : performance à mesurer ; 21 : données synthétiques et confidentialité ; 22 : branche docs seulement ; 23 : anti-doublon, audit API approfondi encore ouvert ; 24 : revue/promotion non obtenues ; 25 : aucune réduction des critères, décision par ID.

**Bilan** : 16/16 capacités A avec décision candidate et au moins trois négatifs par ID ; **0/16 certifiée prête à coder par cette fiche**. Inventaire historique 24/141/140/80/437 inchangé, 431/437 liens textuels, six exceptions et dix exigences G6/G9 sans ticket V34 direct, propriétaires candidats COV-16. Tests produit/Windows/GPU/DS/physique : NOT_RUN.

**Prochaine action unique : COV-17B**, contre-expertise B01–B14 sur objets/calques/texte/OCR avec rapprochement API/DoD et décisions individuelles.
