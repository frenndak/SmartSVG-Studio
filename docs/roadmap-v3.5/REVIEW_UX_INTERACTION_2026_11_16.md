# Contre-revue indépendante du delta UXI — 16 novembre 2026

## Verdict initial et photographie examinée

**Recevable sur le plan documentaire, avec deux précisions Minor à traiter. Zéro Critical, zéro Important établi.** Ce verdict porte exclusivement sur le delta UXI et ses raccords, figés par `ux-review-snapshot.json`, base distante annoncée `dde08cc793bf0a810745b5991ad20462bc79c600`, branche `roadmap/v3-5-design-candidate-20261112`. Il ne vaut ni GitHub APPROVED, ni adoption de la roadmap, ni qualification produit. Le coordinateur doit faire relire les corrections ci-dessous avant publication selon la consigne de cette session.

Relecteur indépendant : `review_ux_interaction`, sans sous-agents. Aucun code produit, source historique, autre document candidat ou service externe modifié par cette revue. Seul le présent rapport est créé. L'autorité de développement reste V3.4 ; G35-12..14 ne sont pas promus. Les états historiques GLOBAL_REVIEW DONE et PROMOTION_DOCS READY sont interprétés avec PROGRESS/checklist : revue historique bornée à son SHA et préparation conditionnelle ; l'ajout du nom de ce rapport aux evidence ne prouve pas à lui seul un avis favorable sur le delta courant.

## Constats précis et corrections attendues

| ID / gravité | Localisation et problème | Conséquence / correction et oracle proposés |
|---|---|---|
| UXI-M01 — Minor | [Contrat UXI](UX_INTERACTION_AND_VISUAL_CONTRACT.md), §6, ligne77 et T-V35-UXI-07 : « échantillonnage raster défini et testé par le rendu » ne choisit pas encore entre pixel source, unité logique du framework et pixel physique de sortie. La distinction avec les mm est correcte ; le facteur de référence du libellé Pixels100% reste sous-déterminé. | Deux runtimes pourraient afficher des tailles différentes à200% tout en satisfaisant l'actuel négatif « ne promet pas des mm ». Définir le rapport attendu pour le raster orienté et sa conversion via DPI/device-pixel-ratio ; si ce rapport ne peut pas être assuré, annoncer un zoom nominal avec sa limite. Ajouter à UXI-07 une mire synthétique dont la taille de rendu attendue est connue à100/200% et entre écrans, indépendamment des120mm d'export. Ne pas faire de la calibration physique une dépendance obligatoire. |
| UXI-M02 — Minor | Contrat UXI §3, ligne37, « ancien projet conservé jusqu'à admission du nouveau », avec UXI-02 §2. La navigation conserve bien les brouillons, mais la transition d'admission d'une nouvelle source ne distingue pas explicitement ajout de source au projet et remplacement du document actif par Ouvrir/Importer. | Sans précision, l'implémentation pourrait abandonner un brouillon au moment où le nouveau fichier est valide. Expliciter ces deux intentions ; remplacement d'un document avec changements non enregistrés = choix explicite conserver/enregistrer/abandonner/annuler selon les ports qualifiés, jamais abandon implicite. Une écriture au résultat inconnu se réconcilie avant changement d'autorité. Compléter une recette existante : projet A sale, fichier B valide/invalide, abandon du dialogue et ACK perdu ; pas de perte silencieuse, pas de deuxième document actif. Ce constat précise la transition ; il n'affirme pas qu'un critère hérité a été supprimé. |

Pas de constat Critical/Important : aucun contournement technique ou perte de critère démontré par cette lecture. Les deux points ci-dessus ne justifient ni modification de l'archive UX figée, ni nouvel ID UX, moteur, store ou ticket. Les corrections doivent rester dans le nouveau contrat et ses raccords utiles.

## Lecture contradictoire et raccords vérifiés

Les neuf fichiers de la photographie ont été consommés ; la revue sémantique se concentre sur les décisions et raccords nouveaux du16novembre, pas sur une réexécution des audits globaux141/140/437/80 ni de tout l'historique de PROGRESS. Références techniques lues : [SCN](SCENE_DECOMPOSITION_AND_RELIEF_CONTRACT.md), [CST](CREATIVE_STUDIO_PRODUCT_CONTRACT.md), [CP](ADR_COMPOSITION_PERSISTENCE.md), [arbitrages D01–D09](DECISIONS_TRANSVERSALES.md), [accessibilité E06–E10](COV18E2_ACCESSIBILITY_E06_E10.md), [interaction/recovery E07–E12](COV18D2_INTERACTION_RECOVERY_E07_E12_HOSTILE.md) et [source UX du13novembre](UX_ARCHITECTURE_AND_WORKFLOWS.md).

Sources héritées effectivement consultées dans la copie `history-work` : `docs/roadmap-v3.4/UX_UI_DESIGN_SYSTEM_ADDENDUM.md` (design system, navigation, clavier, privacy, DPI et benchmark), `02_VISION_PARCOURS.md` (5novices/4sur5, découverte30s), `06_COMMAND_BUS.md` (prévisualisation/durabilité, crash100 et annulation), `07_UX_EXPRESS_NAVIGATION.md` (raccourcis, navigation, layout et p95), `18_ATELIER_GRAPHIQUE.md`, et passages pertinents de `docs/ROADMAP_HERITAGE_v3_3.md` (15opérations/3Undo-Redo, latences et observation humaine). Leur présence locale n'est pas une nouvelle authentification distante de main.

| Domaine / axes pertinents | Conclusion documentaire bornée |
|---|---|
| Héritage et statuts01–06, critères25 | Douze rapprochements UXI-01..12 et dix états de session, sans81eUX ni réécriture de l'inventaire historique.18IDs T-V35-UXI uniques, distincts des437/17SCN/14CST ; tous proposés NOT_RUN. L'ancienne fiche UX reste figée et son bandeau Sain est précisé dans le nouveau contrat, sans être réécrit. |
| Autorité07, Undo/recovery13 | Une session/scène/writer/historique/file ; preview non durable, CAS V1 distinct du receipt CP2. Sauvegarde confirmée, état inconnu et reprise séparés. Un geste = commande logique, double acceptation non rejouée, versions/ACK perdu à réconcilier. La saisie de champ garde son Undo ; abandon de geste par perte de capture/focus sans écriture. M02 précise la frontière de remplacement. |
| Sorties et fabrication08–09, SD18 | Quatre rôles explicites ; PNG, Basic Cut, multicouche et édition ne sont pas des opérations CUT/SCORE. Profil inconnu reste inconnu, ancien export historique, QA invalidé après édition. PARTIAL conserve les succès ; ZIP ne proclame pas un lot complet incomplet. Annuler/Arrêter/Undo ne révoquent pas une publication externe. |
| Parcours/interactions/a11y10–12 | Une surface d'édition, choix d'intention sans perte des corrections, barre stable et cible nommée, sélection mêmeID après tri, valeurs mixtes et locked sans modification partielle. Clavier/liste/menu au lieu d'un geste obligatoire, focus restitué, notifications sans vol de focus, escape à portée définie. Layout client, DPI/multi-écran, thèmes/six accents/contraste élevé, mouvement réduit explicitement à tester. |
| IA14, raster/unités15, géométrie16 | Recherche locale à catalogue fermé, pas de mutation par saisie ni script/URL. Consentements distincts, source conservée, reconstruction séparée opt-in. Zoom et dimensions fabrication mm distincts ; comparaison alignée, overlays non exportés, paramètres CST après transformation monde. M01 demande un oracle plus précis pour Pixels100%. |
| SCN/batch17, opportunités19, réemploi23 | Scène/positions de montage/planche et plans de profondeur distincts ; quatre plans G9 recette propre, pas relief général substitué. CP requis seulement pour les capacités persistantes concernées, manuel indépendant de l'IA. Les tranches UXI0–3 réemploient W01/W02/W03/W12/W13/SCN/CST et D08 ; pas de catalogue concurrent ni remise en cause des huit rejets. |
| Mesures20 | Conserve cinq novices, au moins4comprenant les quatre états, et découverte des deux commandes en30s ; trois parcours/deux erreurs novices et réguliers. Conserve15opérations/3Undo-Redo,100points de crash, clic médian/pan/étatjob et navigation selon périmètres sources. Lot06 :100mutations légères, previewp95<150ms, durabilité séparée, annulation visuelle<250ms. Aucun résultat mesuré, gain ou benchmark inventé. |
| Privacy21, gouvernance22, contre-revue24 | Miniatures privées opt-in, démo isolée, logs/rapports expurgés sur copie et pas de chemin privé partagé par défaut. D08/benchmarks/licences préservés ; aucun framework ajouté. Checklist/README/MASTER/index/backlog/QA/PROGRESS/RUN raccordent le delta. WIP et CI/revue restent des conditions à revalider, aucune nouvelle PR docs ouverte par ce reviewer. |

## Vérifications exécutées et limites

Avant rédaction : les neuf SHA256 correspondent exactement au snapshot ;18IDs de recettes UXI distincts. SHA256 de la source UX figée : `b54a687a2bfd510e8eb1bf4e30273433d5fbe02beaa1deda09bb8f981da5c269`, identique à `ux-baseline-dde08.json`. Ce contrôle ne prétend pas comparer tout le dépôt à main.

| Contrôle frais | Résultat |
|---|---|
| `python canonical-v35/docs/roadmap-v3.5/verify_source_transfer.py --main-root history-work` | exit0 — PASS littéral141critères/140DoD/26pins et références ; sémantique/produit séparés. |
| `python canonical-v35/docs/roadmap-v3.5/verify_priority_register.py --pinned --main-root history-work` | exit0 — PASS documentaire80UX/15groupes/33opportunités/24-141-140-437. |
| `verify_run_state.py` et liens locaux après création du présent rapport | Résultats consignés dans le complément d'exécution ci-dessous. |

Produit, UI Windows, GPU, lecteur d'écran réel, Design Space, coupe, montage et performances : **NOT_RUN**. Ni maquette ni exécution de produit ne sont fournies. La faisabilité effective des ports/runners devra être vérifiée au HEAD au moment du micro-lot d'implémentation. Les liens externes, ancres externes, état courant de GitHub/main/PR et benchmark Fluent/framework ne sont pas recertifiés par cette revue documentaire locale. Les rapports globaux/SCN/CST ne sont pas renommés comme preuve d'un nouveau SHA.

## Empreintes de la photographie initiale

Chemins relatifs à `canonical-v35/` ; SHA256 calculés avant toute correction producteur et identiques à `ux-review-snapshot.json`.

| Fichier | SHA256 |
|---|---|
| `docs/roadmap-v3.5/QUALITY_TESTS_AND_EVIDENCE.md` | `3ad3c07a1d1a58428f2d70d782e8a93996fccc1648b6d3063e67e730c70c4f46` |
| `docs/roadmap-v3.5/PROGRESS.md` | `254385194717809e63c5d3b52b5edf6f35fcf0ac4f59e071d4dba11f33425148` |
| `docs/roadmap-v3.5/PROMOTION_CHECKLIST.md` | `aa3d85e1c540c4b4f8be5ea7dae30b8caa50547082d4d674106b5af045820e9a` |
| `docs/roadmap-v3.5/PRIORITY_INDEX.md` | `1f9f3bbe6deaecf0b2c1eefb0655d04096fc54f003af508f0c03a56a8506c73f` |
| `docs/roadmap-v3.5/README.md` | `cbe7fddf77a1dcfe050e6c3633c3e35a248ef6af9f517dc8fcbd3dc84c805d0b` |
| `docs/roadmap-v3.5/UX_INTERACTION_AND_VISUAL_CONTRACT.md` | `cda6c2b8b46215c170d9e0d19a76dfb2f465fd70573f53feeebaf2cdc0f34f98` |
| `docs/roadmap-v3.5/MASTER_PRIORISE.md` | `1ed82505bb5eca060b05b29c7d07409a935157c8440fc2e9e6312031339897c0` |
| `docs/roadmap-v3.5/BACKLOG_AND_DEPENDENCIES.md` | `3ba898a32ffc553335d6724ce7e8011954da28706c9a2544e6d4464fe0e8a03f` |
| `docs/roadmap-v3.5/RUN_STATE.json` | `e3dda16796eb7426ca02930ddbf118bea6224bdb8b631028dda59606b0fd8170` |

## Complément d'exécution du reviewer

Contrôles réalisés après création du rapport : `python canonical-v35/docs/roadmap-v3.5/verify_run_state.py` exit0, PASS curseur/dépendances/existence des preuves, autorité V3.4. Vérification des destinations de liens Markdown des huit fichiers Markdown du snapshot et de ce rapport :353liens locaux de fichiers, dont2résolus via `history-work`, zéro cible absente, exit0 ; fragments et URL externes exclus. Aucun rapport existant n'est validé sémantiquement par son seul lien. Ce complément ne change aucun verdict produit ni la photographie des neuf fichiers.

## Relecture ciblée finale après corrections — 16 novembre 2026

**Verdict final : delta documentaire favorable ; zéro Critical, Important ou Minor ouvert. UXI-M01 et UXI-M02 sont corrigés et clos.** Cette relecture conserve la photographie initiale et examine uniquement les corrections décrites ci-dessous, avec leurs interactions aux autorités déjà lues. Elle ne constitue pas une nouvelle revue globale, un GitHub APPROVED, une adoption ou une promotion de roadmap. Produit/Windows/GPU/lecteur d'écran/Design Space/coupe/montage/performance demeurent NOT_RUN.

Photographie finale `ux-review-final-snapshot.json` contrôlée : le contrat `docs/roadmap-v3.5/UX_INTERACTION_AND_VISUAL_CONTRACT.md` a pour SHA256 **`40546ee3f8535edf5954cc539117e7744e69a10d08888c528e580e837a0a5162`** ; les huit autres fichiers ont exactement les empreintes initiales ci-dessus. Les neuf empreintes correspondent au manifeste final. La rédaction de ce complément ne modifie pas ces neuf fichiers.

| Constat initial | Correction effectivement relue et conclusion |
|---|---|
| UXI-M01 | §6 et T-V35-UXI-07 définissent100% raster par1pixel de source orientée/1pixel physique rendu, distinguent unités logiques et pixels de sortie, exigent une mire100×100px à100/200% et entre écrans, et prévoient le libellé Zoom nominal avec limite si le runtime ne peut garantir/vérifier le rapport. La définition ne s'étend pas au vecteur et ne promet aucun mm physique à l'écran ; les120mm d'export et la calibration facultative restent indépendants. Oracle désormais discriminant ; clos. |
| UXI-M02 | §3, paragraphe « Ajouter une source ou remplacer le projet », et T-V35-UXI-01 séparent ajout explicite dans le même projet et remplacement du document actif. Rejet/annulation/rester préservent l'état courant ; les changements non enregistrés et aperçus exigent des choix explicites ; Enregistrer n'applique pas un aperçu. Ports qualifiés, copie conditionnelle, un seul writer actif, attente/réconciliation avant transfert en cas d'écriture en cours/ACK perdu et conservation des checkpoints restent explicites. Aucun abandon implicite ni nouvelle autorité de scène/Undo V1/CP n'est introduit ; clos. |

Contrôles frais après correction : les trois commandes source-transfer/priorités-pinned/run-state déjà indiquées sont rejouées, toutes exit0 avec les mêmes portées documentaires. Aucun nouveau scénario n'est ajouté : les corrections spécialisent UXI-01/07 et conservent18IDs uniques. Les corrections n'ajoutent ni lien fichier ni référence technique nouvelle ; le contrôle de liens initial reste borné à son exécution, les contrôles finaux de publication relèvent du coordinateur.

Aucun résidu imposant une correction supplémentaire n'est identifié sur ce delta ciblé. Publication documentaire possible selon l'autorisation de la session et les conditions WIP/CI/revue existantes ; G35-12..14 et l'autorité V3.4 restent inchangés. Le verdict reste lié au contrat final ci-dessus, aux huit raccords inchangés et aux limites déclarées.
