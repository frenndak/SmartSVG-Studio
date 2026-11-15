# ADR — Composition persistante, texte et migration en copie

**14/11/2026 — cible de conception V3.5 proposée pour revue ; aucun changement produit.** Complète Q03, Q04A–Q04I (notamment Q04F) et les lots V3.4 05/06. En cas de divergence sur la cible texte/calques, cette décision candidate prévaut sur leurs propositions export-only ; elle ne modifie pas l'autorité de main. Propriétaires : W01 format/writer, W02 scène/historique, W10 texte, W11 gabarits, W12 variantes/séries. Les contrats ci-dessous sont **futurs**, jamais des signatures Python existantes.

## 1. Choix et alternatives

Choix : une archive `.smartsvg` versionnée V2 pour la composition durable, obtenue par migration **en copie** d'un V1 ou création géométrique neuve. Un seul document est actif dans une session ; l'ancien V1 devient une source conservée, sans synchronisation bidirectionnelle. Le lecteur et writer V1 restent inchangés. Un routeur de version choisit exactement un lecteur/writer pour l'archive active ; pas de deuxième auteur pour le même document.

Refus : TextNode caché dans strokes/operations V1 (perte chez anciens lecteurs), JSON/SQLite parallèle comme maître de scène (double vérité), tout convertir en pixels/tracés (perte de G6.3), migration du framework UI préalable (dépendance sans preuve). Un brouillon export-only peut arriver tôt, mais reste nommé « aperçu non sauvegardé » et n'est pas compté comme composition complète.

V3.4 lot05 envisage déjà V2 : il s'agit de préciser cette obligation, pas de créer un ticket de format concurrent. L'implémentation doit faire évoluer le point d'entrée de workspace et réutiliser validateurs/ressources vérifiés ; le protocole de publication V2 doit être qualifié séparément, sans appliquer aveuglément le writer ZIP V1.

## 2. Contrat logique `smartsvg-composition/1-draft`

Le futur document V2 contient une scène versionnée et un manifeste des ressources. Les limites sont des budgets de conception, configurables **dans des plafonds validés** ; atteindre un budget produit un refus explicite, jamais une troncature. Le premier lot de schéma fixe les valeurs et vérifie fixtures minimum/maximum/dépassement avant tout writer. Aucun benchmark non réalisé n'est transformé en capacité annoncée.

| Élément | Champs obligatoires et invariants | Autorité / reprise |
|---|---|---|
| Scene | `schema`, `canvas_mm:{width,height}`, `root_ids`, `nodes`, `resources` ; dimensions finies >0, IDs uniques | Dans l'archive ; ordre de root_ids = arrière vers avant |
| Node commun | `id`, `kind`, `parent_id|null`, `transform:[a,b,c,d,e,f]`, `visible`, `locked`, `opacity` dans [0,1], `operation_ref|null` | Parent group unique ou racine ; acyclique ; champs stricts selon kind ; référence manquante bloque mutation |
| GroupNode | `kind=group`, `child_ids` ordonnés | Chaque enfant exactement une fois ; retrait du groupe conserve positions mondiales ; pas de boucle |
| ShapeNode | `kind=shape`, `geometry_ref`, `fill`, `stroke` | Géométrie locale mm ; couleur n'assigne aucune opération machine |
| RasterNode | `kind=raster`, `source_id`, `subject_id|null`, `crop_px|null`, `physical_size_mm` | Référence source immuable et masque float32 existants ; crop dérivé, pas une source réencodée |
| TextNode | `kind=text`, `text_original`, `text_nfc`, `runs`, `paragraph`, `layout`, `effects`, `font_refs` | Texte original conservé ; NFC calculé avec version Unicode dans provenance ; pas de remplacement silencieux des caractères |
| TextRun | intervalle [start,end) en points de code du `text_nfc`, `font_ref`, `size_mm`, `tracking_mm`, style | Intervalles non chevauchants couvrent le texte ; aucune coupure utilisateur au milieu d'un grapheme ; shaping peut regrouper plusieurs points de code |
| FontRef | famille/style, hash du fichier si disponible, version, axes variables, origine, droits `UNKNOWN/VERIFIED/RESTRICTED`, droits séparés rendu/embed/export | Le nom de famille seul ne garantit pas même rendu. Pas de chemin privé absolu partagé ; pas de police embarquée sans droits vérifiés |
| Paragraph | direction `AUTO/LTR/RTL`, langue déclarée ou `und`, alignement, interligne_mm, largeur_mm|null | Mise en page reproducible avec version du moteur et font hashes ; moteur absent → état dégradé explicite |
| Layout | mode `straight/path/monogram`, `path_ref|null`, `start_offset_mm`, `baseline_offset_mm`, sens explicite | Texte reste sémantique ; suppression du chemin référencé refusée ou détachement explicite avec Undo ; rayon nul refusé |
| Effect | type `outline/shadow/texture/gradient`, paramètres typés, ressources/digests | Ordre appliqué explicite. Aucun effet visuel n'est automatiquement CUT ; contour fabriqué = géométrie dérivée prévolée |
| Provenance OCR | référence source/hash, zone px, moteur/version, proposition, corrections, statut humain | Facultative, locale ; score OCR non assimilé à confiance calibrée ; sauvegarde seulement après acceptation |

Les caches de glyphes, miniatures, sélection/focus/zoom et résultats de jobs non acceptés restent reconstruisibles hors autorité. Les propriétés de scène (ordre, visibilité, transformation, texte, contraintes) restent durables. Enregistrer ne doit pas faire disparaître une propriété visible que l'interface annonce sauvegardée.

**Verrouillage et visibilité B02 :** locked est hérité des ancêtres. Une transformation/suppression/groupement qui affecterait un descendant verrouillé est refusée pour tout le groupe, avec liste des objets concernés ; une sélection mixte exige choisir explicitement les objets non verrouillés, jamais les déplacer silencieusement en sous-ensemble. Déverrouiller le parent ne déverrouille pas les descendants propres. Group/ungroup conserve les IDs enfants et leurs matrices mondiales. Les nœuds hidden sont exclus par défaut du rendu/export ; l'aperçu de prévol liste l'ensemble exporté, et l'inclusion volontaire de hidden est un paramètre explicite. Opacity est visuelle ; un CUT partiellement transparent n'a aucun sens machine et ne devient pas automatiquement une découpe partielle. Tests : déplacer parent avec enfant locked → aucune mutation ; supprimer cache → ordre/locked/visible/opacité inchangés ; export masque hidden avec preuve recalculée.

### Coordonnées et transformations

Coordonnées de scène : mm, origine haut gauche, x vers droite, y vers bas. Vecteurs colonnes : `x'=a*x+c*y+e`, `y'=b*x+d*y+f`. Les quatre premiers coefficients sont sans unité ; e/f sont mm. Composition monde = `M_parent × M_local`. Rotation positive dans ce repère visuel est horaire ; pivot explicite p : `T(p) × R(theta) × T(-p)`. Radians internes, degrés affichés et convertis une fois. Matrice inverse nécessaire aux poignées : determinant non nul et conditionnement dans budget numérique ; matrice singulière refusée à l'édition, aucune réparation silencieuse.

Raster : passage px→mm seulement via dimensions physiques confirmées `width_mm/source_width_px` et `height_mm/source_height_px`; DPI metadata est une proposition affichée, pas une échelle physique confirmée. Texte et SVG : géométrie mm avec viewBox cohérente ; `units_per_em` de police converties par taille_mm/units_per_em. Fixture de référence : p=(2,3), translation(10,20) → (12,23) ; scale(2,3) puis translation → (14,29). Inverser l'ordre donne un autre résultat et doit échouer au test de composition.

### Police indisponible et ressources inconnues

Si police/version/hash manque : préserver Unicode, styles et layout ; afficher « police manquante/rendu à vérifier », garder aperçu antérieur identifié comme cache si présent, bloquer l'export qui prétend reproduire le texte. L'utilisateur choisit une police de remplacement avec diff et Undo, ou une conversion depuis des contours **déjà vérifiés** de la police d'origine si disponibles et autorisés. Une police voisine n'est jamais substituée automatiquement. En embed interdit, conserver référence externe expurgée + diagnostic de portabilité ; ne pas annoncer projet portable. Import de projet tiers n'exécute ni script ni réseau.

## 3. Transactions et commandes

Commandes proposées : CreateNode, UpdateText, SetTextStyle, SetTextLayout, SetTextEffects, SetTransform, GroupNodes, UngroupNodes, SetLayerOrder, SetVisibility, SetLocked, DeleteNodes, ConvertTextCopyToPaths, ApplyCompositionProposal. Toutes utilisent le bus/epoch/receipt futur du lot06, pas un nouveau bus. `operation_ref` conserve CUT/SCORE/DRAW/PRINT/FOIL typés et distincts, y compris dans Undo ; `null` veut dire non assigné.

Entrée commune : project_id, expected SHA archive, epoch/command_id, digest canonique, cibles stables et préconditions de ressources. Préparation sur snapshot hors verrou ; sous verrou, autorisation et receipt avant CAS, validation graphe/ressources, publication atomique du document+patch+receipt, lecture de contrôle. Résultat = COMMITTED / REPLAYED / REJECTED / COMMITTED_NEEDS_RECOVERY / UNKNOWN_AFTER_INTERRUPTION avec diagnostics. Aucun message UI « sauvegardé » avant réconciliation du résultat avec l'archive. Erreurs proposées : UNSUPPORTED_SCHEMA, STALE_PROJECT_SHA, INVALID_GRAPH, RESOURCE_MISSING, FONT_UNAVAILABLE, GLYPH_MISSING, LICENSE_RESTRICTED, INVALID_AFFINE, BUDGET_EXCEEDED ; mapper aux erreurs existantes lors de l'implémentation.

Un drag = un groupe ; saisie = groupe terminé au changement de focus, confirmation ou pause explicitement définie par l'UI. Undo restaure texte, styles, parent/ordre, opérations et ressources nécessaires ; nouvelle édition invalide Redo sans supprimer l'audit. La création/suppression conserve tombstones/ressources tant qu'un Undo retenu les référence. Les quotas historiques et consentement à purge restent ceux du lot06. Export externe exclu d'Undo.

## 4. Migration V1→V2, ouverture et retour

1. Inspecter V1 via son lecteur actuel ; source SHA, toutes ressources, masques float32, identités et historique. Toute preuve incohérente produit diagnostic et refuse migration éditable ; aucune identité créée à partir d'un index.
2. Plan pur : destination neuve, empreintes, espace requis et changements. V1 reste intact même si une étape échoue. Le plan ne modifie ni notes ni artefacts.
3. Confirmation de création d'une copie ; lire sous verrou source et CAS exact. Construire V2 temporaire sur volume destination, avec provenance du SHA V1 et copie exacte des ressources originales. Migration conserve project_id logique ; session d'édition ne garde qu'une archive active. « Dupliquer » est une autre commande, nouvelle identité avec parent/provenance.
4. Valider format/refs/hashes, source byte-identical, masques bit-identical, IDs stables et absence de conversion de rôle ; publier sans écraser un fichier existant, relire. Annulation prépublication nettoie uniquement le temporaire créé par l'opération.
5. Si crash après publication : inspecter destination et reçu de migration avant toute relance ; source conservée. Sélectionner explicitement la copie valide ou retourner à V1. Deux tentatives même destination ne publient pas deux fois.
6. Ancien client refuse V2 ; pas de downgrade silencieux. Retour = réouvrir le V1 conservé (sans les nouvelles modifications), ou copie/export de contenu compatible avec liste explicite des pertes. Le rollback d'un binaire ne doit pas écraser un V2 avec le writer V1.

Le premier V2 peut n'offrir qu'une composition bornée avec ressources connues. Le support de 50 masques est une tranche séparée, packs internes ≤32 chacun, identités globales, limites cumulées de décompression et mémoire. Ne pas proclamer 50 persistés parce que 50 copies sont placées sur une planche.

## 5. Export et UX

PNG PTC rend les effets ; Basic Cut exige géométrie de découpe valide ; multicouche CUT conserve la séparation de couches/opérations et prévol d'assemblage ; SVG d'édition expose ses capacités exactes (texte sémantique si droits/compatibilité, sinon chemins éditables avec avertissement). Aucun de ces fichiers n'est le projet de composition. Les quatre QA restent séparées, sans ajouter de quatrième `Artifact.use` en V1. La conversion en tracés à l'export ne remplace pas le TextNode du projet.

Novice : créer étiquette → saisir texte → police/glyphes vérifiés → positionner en mm → enregistrer la copie compatible → fermer/réouvrir → modifier → exporter selon usage. Expert : inspecter police/hash/licence, arbre de scène, coordonnées et diagnostics. Gestes directs et Undo, pas de popup pour chaque lettre ; confirmation pour migration, remplacement de police, perte d'éditabilité ou publication externe. Une seule barre contextuelle ; clavier/focus, lecture des erreurs sans couleur seule, 1366×768/DPI200%, mouvement réduit. Aucun GPU ni ComfyUI requis pour éditer/migrer ; OCR reste opt-in.

## 6. Tranches de réalisation et critères de sortie

| Tranche | Dépendance réelle | Résultat vérifiable avant suivante |
|---|---|---|
| CP0 contrat/fixtures | inventaire lecteurs/writers et contraintes réelles | schéma discriminé, bornes, ressources/erreurs, sérialisation canonique et fixtures synthétiques validées ; aucun writer activé |
| CP1 lecture/plan migration | CP0 | ouvrir V1/V2 en lecture seule, plan sans mutation, refus des archives malveillantes |
| CP2 migration/writer/history | CP1 + invariants lot06 | copie CAS, receipt durable, crash100 points, recovery Windows ; activation seulement après preuves requises |
| CP3 scène native | CP2 | objets/calques/transformations souris+clavier, save/reopen/Undo réels |
| CP4 texte de base | CP3 + choix moteur/fontes licenciés | B09 accents/glyphes/style rééditables après réouverture ; aucun export-only compté complet |
| CP5 texte avancé/compose | CP4 + géométrie vérifiée | B10/B11/B12/B14, paths/effets/contraintes, rollback et QA par rôle |
| CP6 gabarits/OCR/diorama | capacités précises de CP3–5 | W11 trois usages ; B13 OCR séparé et facultatif ; W16 quatre plans, preuves physiques propres |

Ces tranches réutilisent les tickets V34 concernés ; ne pas ouvrir sept tickets duplicatifs par automatisme. Smart Delivery mono-export, sélection V1, raster et accessibilité peuvent avancer sans attendre CP2. Un choix de moteur de shaping est une tâche d'implémentation évaluée par spike borné (licence, Unicode, reproduction, empaquetage), pas une excuse pour reporter toute la roadmap.

## 7. Recettes de contrat (toutes proposées, NOT_RUN)

Positifs : P01 texte « Éloïse — Noël » save/reopen/modify ; P02 composition affine chiffrée ci-dessus ; P03 groupes imbriqués puis dégroupage avec positions identiques ; P04 copie migrée source/masks byte-identical ; P05 retour V1 sans écrasement ; P06 texte→paths garde TextNode ; P07 effet visuel en PNG et refus d'équivalence CUT ; P08 OCR corrigé avant remplacement ; P09 trois gabarits indépendants ; P10 packs 25+25, IDs uniques.

Négatifs : N01 police absente ; N02 hash/version de police divergents ; N03 licence d'embed inconnue ; N04 glyphe manquant et combinaisons Unicode ; N05 parent cyclique/référence manquante ; N06 NaN/Inf/matrice singulière/mm inconnus ; N07 chemin supprimé/longueur nulle ; N08 résultat OCR après nouveau SHA ; N09 même command_id payload différent ; N10 rollback client ancien refuse V2 ; N11 ZIP traversal/collision NFC/casse/bombe/symlink ; N12 dépassement budget sans troncature ; N13 destination existante/no-clobber ; N14 deux writers CAS ; N15 publication réussie+backup échoué ; N16 perte ACK et replay ; N17 disque plein à chaque frontière ; N18 annulation avant/après publication ; N19 type SCORE perdu par Undo ; N20 cache supprimé ne perd aucun texte ni propriété.

Fixtures uniquement générées ou ressources libres explicitement autorisées. Tests de rendu/logique/CPU, tests Windows d'I/O et UI, puis Design Space et matériel demeurent axes séparés. Mesurer latence p50/p95 par taille de texte/nombre d'objets, RSS et taille archive ; les résultats futurs détermineront les budgets, sans promettre RTX ou reproduction physique.
