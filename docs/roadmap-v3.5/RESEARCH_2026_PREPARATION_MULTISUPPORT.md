# SmartSVG V3.5 — complément ciblé de préparation multi-supports (17 novembre 2026)

**Nature :** recherche comparative et **trois raffinements optionnels** du programme existant ; aucun nouveau workstream W17, aucun changement de priorité/ID source, des 80 capacités UX, 140 tickets, 141 critères, 24 lots et 437 scénarios hérités. Cette proposition devient un point de détail de la roadmap après revue/CI documentaire ; **aucune fonctionnalité produit n'est livrée par ce document**.

**Contre-expertise du 17 novembre :** [verdict neuf ajouts et U26-07](COUNTER_REVIEW_2026_11_17_WORKFLOW_TOOLS.md) : ne pas confondre PNG raster pour gravure et PNG PTC, ne pas imposer identités de groupes SVG si un export documenté les transforme, ne pas déduire kerf d'une épaisseur. **Décision propriétaire en conversation :** chercher des fonctions récentes vraiment utiles, ajouter un petit complément *au milieu* de V3.5 sans détourner l'équipe des exports et de Windows. Périmètre : **préparer le projet**, jamais piloter une machine, fabriquer des commandes de puissance/vitesse, transmettre des travaux ou déclarer une compatibilité matérielle non testée.

## 1. Recherche 2026 et refus des doublons

Sources externes consultées le 17/11/2026 :
- [LightBurn 2.2, annonce du 19/10/2026](https://lightburnsoftware.com/blogs/news/lightburn-2-2-true-nest-center-line-trace-camera-print-and-cut-and-more) : True Nest (Pro), Center Line Trace, Multi Page ; **déjà représentés** dans W12/W16, C05/W03 et W12. Ne pas recréer des tickets génériques « nesting », « centerline » ou « pages multiples ».
- [xTool Studio, notes de version 2026](https://support.xtool.com/article/1773) : découpe/détourage, production variable, numérotation/QR, transfert de données ; **déjà représentés** dans W02/W12/W14/W16.
- [Adobe Illustrator, nouveautés 2026](https://helpx.adobe.com/illustrator/desktop/new-features/whats-new.html) : propositions de vectorisation/génération et variantes IA ; **déjà prévues** sous D01–D12/W14. Ne pas ajouter d'agent autonome créant des mutations non vérifiées.
- [LightBurn, guide « Getting a Design Laser-Ready »](https://docs.lightburnsoftware.com/2.1/Collections/GettingADesignLaserReady/) : jonctions, slots, compensation de kerf et préparation géométrique ; **une partie** est traitée par C17/W11 mais le flux de **réajustement contrôlé des assemblages existants** mérite précision.
- [Laser Image Forge](https://laserimageforge.com/dashboard) et [Laser Image Prep du 26/06/2026](https://1c3d.com/news_updates/new-tool-laser-image-prep-material-presets-dither-halftone) : flux photo → niveaux/contraste/tramage → aperçu → fichier de gravure. **Pas de parcours photo-gravure défini** dans les quatre rôles existants : une tranche facultative peut compléter le raster sans créer un logiciel laser.
- [xTool 2026, release notes pour l'édition d'images](https://support.xtool.com/article/1773) : preuve de l'importance de la conservation des détails et de l'édition non destructive ; déjà dans le contrat créatif, ne pas ajouter un autre moteur d'images.

Cette veille identifie des pratiques existantes, **pas une nouveauté exclusive SmartSVG**, ni un avantage concurrentiel déjà mesuré. L'état du code est réévalué à chaque micro-lot sur `main`, pas déduit des contrats.

## 2. Micro-compléments retenus, sous les workstreams existants

### M26-A — Préparation de photos pour gravure, sans pilotage (P1 optionnel ; W03/W04, ressources raster W14)

**Besoin :** un créateur doit préparer un portrait/logo photographique pour import dans *le logiciel de gravure qu'il possède déjà*, en contrôlant visuellement noir/blanc et finesse, sans confondre gravure et découpe Cricut.

**Petit périmètre proposé :** vue locale **original / niveaux / contraste / noir et blanc / tramage** ; deux algorithmes déterministes documentés en première itération (seuil + diffusion d'erreur), inversion explicite, dimensions réelles mm/px/ppi affichées **sans inventer de mm si PPI absent ou non fiable**, paramétrage réversible en brouillon, sortie d'image PNG raster **externe, hors contrat canonique PNG_PTC et hors pack Smart Delivery automatique**, profil proposé `RASTER_ENGRAVING_PREP_UNVERIFIED` **qui n'est ni rôle de projet ni preuve de compatibilité tierce**, et note de restitution. Réutiliser les fonctions raster existantes, **sans inventer un 5e rôle `Artifact.use` V1** ni rebaptiser silencieusement PNG_PTC. Si l'architecture requiert un nouveau contrat d'export, demander une ADR propriétaire distincte et différer la persistance.

**Négatifs/gates :** résolution ou dimensions mm inconnues → pas de « prêt gravure » ; transposition de la luminance sans licence/provenance → refuser si droits DENIED ; images trop grandes/OOM → refus/annulation propre, source intacte ; tramage rediscretisé à l'import dans logiciel tiers → avertissement, **test d'import réel indépendant**. Tests CPU de déterminisme/digest, image avant/après, no-clobber et absence de mutation ; Windows et application tierce séparés. Jamais de vitesse/puissance/matériau certifiés.

**Entrée en réalisation :** après un export natif W03 réel ; **ne bloque pas** W03, W04, Smart Delivery W05/W06, Cricut W07/W08 ou le premier Windows Alpha.

### M26-B — Contrôle de fidélité export/réimport et fiche de transfert (P1 ciblé ; W03/W04/SD2)

**Besoin :** un atelier veut vérifier qu'un fichier SVG fourni conserve **ses cotes, unités, trous, objets et opérations** malgré le passage projet → fichier → réouverture, avant import externe.

**Petit périmètre :** contrôles locaux en lecture seule d'un SVG réellement produit puis relu par le parseur sécurisé : dimensions/viewBox, contours fermés ou ouvertures autorisées selon rôle, **invariants de groupes/IDs seulement lorsque leur conservation est contractuelle** (sinon transformation déclarée et lien de provenance), trous/topologie/opérations attendus et delta de boîtes géométriques avec tolérances explicites ; signaler les différences liées au rendu et générer **un rapport court joint au guide Smart Delivery** lorsque pertinent. Une comparaison pixellisée peut aider mais ne remplace pas des unités mm ni la topologie.

**Anti-doublon :** les W03/W04 prévoient déjà un prévol et des fichiers relus ; **M26-B précise la preuve d'aller-retour et sa présentation utilisateur**, pas un autre moteur QA. Si les tests W03 satisfont déjà cette DoD au HEAD, ne pas créer de code duplicatif : réutiliser l'existant et clore la tranche par preuve. Ne pas présenter l'aller-retour dans SmartSVG comme un PASS **LightBurn / Design Space / xTool**.

**Négatifs/gates :** XML/script/référence externe rejeté ; dimensions unitless/NaN ou perte d'un trou = FAIL ; double chemin/collision d'ID = diagnostic ; sortie ou projet changé en cours de vérification = STALE ; aucun rapport ou pack n'est marqué READY sur simple vérification de parsing.

**Entrée en réalisation :** greffer au W03/W04 existant après le premier vrai export, puis SD2 ; pas de nouvelle file de travaux.

### M26-C — Ajuster des tenons/encoches à l'épaisseur déclarée (P2 conditionnel ; raffinement de W11/C17)

**Besoin :** réadapter une boîte ou un assemblage papier/bois/acrylique à une autre épaisseur nominale sans casser les dimensions ou redessiner tous les assemblages.

**Petit périmètre :** sur un **gabarit reconnu** uniquement, saisir manuellement l'épaisseur (mm) et le jeu explicite (mm) **sans en déduire automatiquement kerf, outil ni tenue mécanique**, analyser les couples tenon/encoche reconnus, montrer **avant/après et un diff coté**, proposer le recalcul **sur copie et après confirmation** ; vérifier interférences/géométrie et conserver l'original. Ne pas détecter automatiquement le matériau, ni inventer kerf/tolérances/force d'assemblage. Si topologie non reconnue, revenir à diagnostic manuel, pas « correction » automatique.

**Anti-doublon :** C17/W11 couvre déjà languettes, plis et épaisseur ; le delta nouveau est **le redimensionnement contrôlé de projets existants**, non un nouveau type de gabarit ni un moteur 3D.

**Négatifs/gates :** épaisseur absente ou <=0, jonctions ambiguës/autointersections, changement d'épaisseur produisant un tenon impossible et modification de cotes verrouillées → refuser ou proposer une variante isolée ; matériau inconnu = compatibilité physique UNKNOWN, contrôle de coupon par l'utilisateur hors logiciel. Tests géométriques, Undo, save/reopen seulement après ports CP/V2 réellement prêts.

**Entrée en réalisation :** après W11 édition/gabarits et CP requis ; **non bloquant** pour les priorités P0/P1, et à écarter si un port existant fournit déjà le même geste.

## 3. Classement, limites et contre-expertise

| Item | Décision | Effort relatif | Risque | Réussite vérifiable |
| --- | --- | --- | --- | --- |
| M26-A | **CANDIDAT P1**, micro-prototype CPU/raster après W03 | moyen | confusion gravure vs PTC, perte du tramage dans l'app cible | comparaison avant/après + PNG réouvert, aucune valeur de coupe/gravure présentée comme certifiée |
| M26-B | **P1 à raccorder dans W03/W04/SD2**, utiliser l'existant d'abord | faible à moyen | faux sentiment de compatibilité | défauts synthétiques détectés, cotes et trous relus, rapport informatif |
| M26-C | **P2 facultatif sous W11**, après contrat d'assemblage | moyen | assemblages physiques trompeurs | deux gabarits synthétiques, épaisseur différente, topologie stable, refus des cas ambigus |

**Rejets après analyse de non-doublon :** nouveau moteur de nesting (W12/W16 existant), assistant IA universel auto-opérant (D/W14 déjà prévu et sécurité des mutations), nouvelles pages/CSV/QR (W12/W16), pilotage d'une machine, G-code/puissance/vitesse, simulation de matériau/découpe présentée comme physique, prise en charge industrielle universelle ou ingestion DXF/PDF généralisée sans étude de sécurité.

## 4. Intégration sans déranger l'exécution

- Conserver l'ordre **W01 → W02 → W03/W04 → W05/W06 → W07/W08** en cours. Ce complément **s'insère en option au milieu**, après les premiers exports vérifiés ; les essais M26-A et M26-B peuvent avancer indépendamment de M26-C, mais ne deviennent jamais gate de la première livraison.
- Rattacher aux **workstreams existants**, aucune nouvelle catégorie normative : W03/W04/SD2 pour preuve export, W03/W14 pour image raster, W11/C17 pour encoches. Conserver 4 sorties contractuelles et schémas de projet intacts.
- Un micro-lot de code = test utile + cas adversariaux + aperçu Windows si promis + PR DRAFT + revue ultérieure + exact-head CI ; fonctions physiquement non testées restent explicitement NOT_RUN.
- Ne pas reprogrammer la tâche horaire, ni retoucher le prompt R12, les protections, les dates de release ou les priorités héritées à cause de cette veille. La prochaine tranche demeure W02 selon EXECUTION_STATE.
- Avant de transformer ces raffinements en tickets/code, refaire l'anti-doublon **contre `main` au SHA courant** et chiffrer le coût de support/mémoire ; rejeter toute proposition devenue redondante.

**Verdict :** complément ciblé pertinent **à conserver dans la référence**, mais non une nouvelle phase ni une preuve de supériorité 2026. La valeur dépendra de tests Windows et de cas utilisateurs réels.
