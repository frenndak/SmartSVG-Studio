# SmartSVG V3.5 — contre-expertise hostile des neuf améliorations 2026

**Date :** 17 novembre 2026. **Objet :** décider ce qui mérite une réalisation concrète, corriger les ambiguïtés des fiches [M26](RESEARCH_2026_PREPARATION_MULTISUPPORT.md) et [U26](RESEARCH_2026_UX_PRODUCTION_ACCELERATORS.md), repérer un manque à valeur élevée. **Type :** complément documentaire propriétaire en session ; **aucun code produit, test matériel, mesure de productivité ou certification de formats tiers n'est produit ici**. Le statut canonique d'ingénierie est [EXECUTION_STATE](EXECUTION_STATE.json), non ce document.

## 1. Sources et comparaison, sans fausse innovation

- [Illustrator, nouveautés novembre 2026](https://helpx.adobe.com/illustrator/desktop/new-features/whats-new.html) : AI Assistant (beta), comparaisons vectorielles, parcours guidés. La combinaison IA+outils existe donc ailleurs ; ne pas se déclarer premier.
- [Figma, menu Actions](https://help.figma.com/hc/fr/articles/23570416033943-Utiliser-le-menu-d-actions-dans-Figma-Design) : recherche de commandes, sélection par mêmes propriétés, renommage ; les fonctions déterministes sont une UX moderne sans IA obligatoire.
- [LightBurn 2.2](https://lightburnsoftware.com/blogs/news/lightburn-2-2-true-nest-center-line-trace-camera-print-and-cut-and-more) : True Nest, Center Line Trace, pages multiples ; déjà cadrés W12/W16, W03, W12, pas un nouveau lot.
- [Illustrator, Document Info](https://helpx.adobe.com/illustrator/desktop/get-started/learn-the-basics/document-info-panel.html), [Links](https://helpx.adobe.com/illustrator/desktop/add-and-import-files/manage-linked-and-embedded-files/links-panel-overview.html) et [Package](https://helpx.adobe.com/illustrator/desktop/save-and-export/export-files-to-different-formats/package-files-with-fonts-and-linked-images.html) : inventaire des fontes/liens/ressources, préparation pour transfert. Un **rapport d'admission compréhensible** est plus utile qu'un énième filtre IA lorsque le client fournit un fichier ambigu.
- [LightBurn, fichiers et chemins dupliqués](https://docs.lightburnsoftware.com/2.2/Reference/Selection/) : les erreurs géométriques demeurent un problème de base ; ne pas confondre diagnostic, réparation consentie et qualité de coupe physique.

**Fond documentaire vérifié dans la V3.5 :** [MASTER](MASTER_PRIORISE.md), [UXI](UX_INTERACTION_AND_VISUAL_CONTRACT.md), [CST](CREATIVE_STUDIO_PRODUCT_CONTRACT.md), [SD2](SMART_DELIVERY_EXECUTION_CONTRACT.md), [ADR composition](ADR_COMPOSITION_PERSISTENCE.md) et les fiches M26/U26. `W01` comprend l'import sécurisé, `W03/W04` sorties/contrôles, `W10` les fontes, `W12` la bibliothèque, `W13` l'UX et `W14` IA facultative ; les distinctions projet V1/V2 restent applicables. Les 80 UX et 141 obligations source ne sont jamais effacées.

## 2. Verdict contradictoire, neuf éléments conservés avec corrections

| Élément | Verdict | Correction / garde-fou indispensable | Quand l'évaluer |
| --- | --- | --- | --- |
| **M26-A** gravure raster | **CONSERVER P1 expérimental** | PNG de gravure **n'est pas PNG Print Then Cut** et n'entre pas implicitement dans les quatre rôles/pack ; source non mutée, ICC/ppi/inversion et tramage documentés, relecture réelle. Aucun « prêt laser ». Pas d'effet IA requis. | Après vrai export W03, profil externe explicitement non vérifié, ADR si contrat change |
| **M26-B** aller-retour | **RENFORCER, P1** | Comparer les **invariants du rôle et du moteur** (dimensions, topology/holes/operations, rendus si possible), pas exiger identités/compte des groupes si une conversion déclarée les change. Parseur local ≠ preuve dans logiciel tiers. | W03/W04 réel, puis SD2 |
| **M26-C** tenons | **CONSERVER P2 conditionnel** | Ne pas utiliser « épaisseur nominale = ajustement garanti » : dimensions/jeu définis par l'utilisateur, croisement des couples reconnus, essais coupon externes ; refus ambigu, pas de réglage machine. | Après W11/C17 et CP qualifiés |
| **U26-01** sélection même propriété | **CONSERVER P1 ciblé** | Filtres typés (couleur ≠ CUT), tolérance taille en unités réelles quand connue, verrouillage et portée visibles ; ne pas promettre 100 objets sur V1 si ce sont 100 instances non persistées. | Dès que le modèle objets et la sélection W02/CP le permettent |
| **U26-02** guides en mm | **CONSERVER P1 ciblé** | Visuel informatif si mm inconnus, seuil de snap en px écran indépendant du zoom avec placement mm stable ; jamais « guide vérifié en mm » sur pixels non calibrés. | Avec canevas W02/W13 réel |
| **U26-03** « Préparer ce fichier » | **PRIORISER P1** | Réutiliser W04/W07/M26-B, conserver les quatre rôles et trois états distincts : **défaut local / doute externe / inconnu**. Plan de réparation sur brouillon, une action à la fois, diff et consentement ; certains problèmes doivent rester bloquants. | Dès premier prévol W04 réel |
| **U26-04** remplacer toutes occurrences | **P2 ferme** | Source et instances versionnées, dimensions/contraintes revalidées, verrouillés exclus avec refus explicite, exports historiques jamais réécrits ; **pas d'accès direct V1 50 sujets**. | Après CP et bibliothèque W12 |
| **U26-05** BAT visuel | **P2 utile, recentrer** | **Document de revue**, non preuve d'accord, contrat signé, compatibilité, contrôle qualité ni certification physique ; aucune récolte d'identité/signature ; modèle sans droits de partage = refus ou examen. PDF optionnel, ne pas imposer nouvelle dépendance. | Après sortie saine W03 et SD2 W06 |
| **U26-06** capture de recettes | **CORRIGER P2** | **Séparer strictement gestes réversibles** (éditer/aligner/contour) et **publication externe** (export/ZIP) qui n'est pas Undo. Enregistrer les paramètres et la configuration d'export **sans exécuter sa publication en rejouant la recette** ; confirmation humaine/destination revalidée via W03/SD. Aucun script, URL, chemin secret ni macro de clics. | Après commandes typées/CP/CST et validation de sortie |

### Incohérences concrètes résolues par cette revue

1. U26-06 mélangeait « petite suite de commandes réversibles » et « exporter » dans le même exemple ; c'est contraire au principe SD « Undo ne retire aucun fichier livré ». La fiche U26 doit isoler la publication.
2. U26-05 pouvait être pris pour un **BAT approuvé par le client**, alors que SmartSVG ne reçoit pas et ne vérifie pas d'accord contractuel. Il génère un aperçu de revue, identifié par révision, **sans signature ni approbation implicite**.
3. U26-01 et U26-02 ont été qualifiés « courte P1 » alors que la vraie disponibilité dépend de **multi-objets persistants**, unités et locks ; ne pas vendre un prototype écran comme fonction achevée.
4. M26-A est un **PNG raster générique destiné à une application tierce**, mais les quatre rôles canoniques sont stricts. Aucun alias `PNG_PTC`, rôle V1 supplémentaire ou pack SD automatique.
5. M26-B vérifiait « nombre/groupes/IDs » sans distinguer une normalisation SVG volontaire du défaut réel : employer des oracles **par rôle et transformation documentée** (dimensions, remplissages/trous, opérations de fabrication, incidence visuelle).
6. M26-C ne doit pas sembler déduire kerf, jeu ou faisabilité réelle du matériau à partir de son épaisseur nominale.

## 3. Un manque plus prioritaire que plusieurs gadgets : U26-07 — Diagnostic d'entrée / « Fichier client » (P1 UX, par réemploi W01/W04/W10/W13)

**Pourquoi :** un atelier reçoit un SVG/PNG sans unités fiables, avec fontes absentes, dimensions arbitraires, traits cachés ou autres ressources. Ce sont précisément les types d'informations qu'un logiciel pro comme Illustrator rend visibles via Document Info/Links/Package. SmartSVG aura des contrôles d'import, des contrôles géométriques et un prévol ; **il manque un parcours utilisateur unifié et précoce qui rend visibles leurs conclusions**. Ne pas programmer un autre parseur.

**Micro-parcours :**
1. Importer par l'adaptateur **déjà autorisé** et inspecter en lecture seule : type, dimensions intrinsèques/unité connue ou inconnue, résolution/alpha/ICC applicables, éventuels liens externes invalides, texte/fontes manquantes **seulement si le format/parseur permet de les observer réellement**, opérations ambiguës et premiers défauts géométriques si disponibles.
2. Afficher une fiche synthèse **« prêt pour édition / à examiner / import impossible »** avec **cause et action** : fixer manuellement les mm, choisir la bonne intention, localiser un chemin problématique, remplacer/convertir une fonte sur une copie avec consentement, ou choisir une image compatible.
3. Ouvrir dans l'éditeur **sans mutation des sources originales**, et prolonger les contrôles dans U26-03 « Préparer ce fichier » quand la fabrication est choisie. Les assertions `UNKNOWN` restent inconnues, pas remplies par un modèle.
4. Le rapport d'entrée peut être éphémère au début ; il ne devient persistant que si le schéma/CP le prévoit. Aucune récupération automatique de fonte ni URL externe, aucune exécution de contenu importé, aucune fuite d'EXIF/chemins privés dans un document partagé.

**Anti-doublon :** W01/UXI possèdent l'import sûr et les écrans d'erreur ; W04 le prévol ; W10 les polices ; U26-03 le triage avant sortie. **Le delta unique est un rapport lisible à l'ouverture**, avant que l'utilisateur ait commencé une création. Si l'UI W01 réalise déjà ce parcours sur le HEAD courant, **ne pas ouvrir de nouveau lot de code**.

**Qualification minimale :** PNG avec dimensions px mais mm incertaines → REVIEW, aucune dimension inventée ; SVG avec déclaration mm et `viewBox` cohérents → propriétés affichées ; SVG malveillant → rejet avant prévisualisation ; fonte référencée et non installée → mention seulement si parser typé réel ; projet sain importé → aucune popup anxiogène ni action obligatoire ; fermeture/annulation → projet déjà ouvert inchangé. Test CPU et interface Windows séparés. **P1 facultatif après entrée W01 stable**, aucun blocage de W02/W03/SD.

## 4. Coût, valeur et décision de livraison

- **Haut rendement sans IA :** U26-03 (orchestrer QA), U26-07 (diagnostic d'entrée) et U26-01 (sélection ciblée), seulement après disponibilités des composants existants. Mesurer le temps réel novice/expert, erreurs évitées, gestes, relecture/Undo et taux de correction, pas un « -90 % » théorique.
- **Polish utile, mais non urgent :** U26-02 et M26-B à raccorder au même pipeline QA/projet, éviter doublons de vues.
- **Dépendances fortes, différer :** U26-04/U26-06 sous CP/W12, M26-C sous W11, U26-05 sous SD2. M26-A conserve son petit prototype isolé après W03, pas un nouveau moteur image.
- **Rien à rajouter maintenant :** agent IA omnipotent, générateur 3D fiable, import universel PDF/DXF, fausses compatibilités laser, cloud obligatoire, pilotage, auto-réparation silencieuse, téléchargements de polices sans licence.

## 5. Clauses de non-régression et preuves

Ne pas modifier `EXECUTION_STATE.json`, le prompt R12, la tâche planifiée, AGENTS/READY/policy, les archives/fonctions héritées. Pas de W17, pas de 81e UX ni de chiffre de complétion produit inventé. **Le curseur d'ingénierie demeure W02** tant qu'un nouveau constat GitHub n'en apporte pas la preuve inverse. Un fichier documentaire et une CI G0 documentaire ne sont **pas des tests fonctionnels**. Les micro-lots futurs devront vérifier le HEAD réel, les ports, la sécurité des imports, les cas négatifs, le writer et les tests Windows, puis les essais logiciels externes séparément si une compatibilité est revendiquée.

**Verdict final : conserver les neuf, rectifier leur contrat ; ajouter une seule facette UX U26-07 dans W01/W04 existants, et privilégier les parcours cohérents plutôt qu'une dixième famille de moteurs.**
