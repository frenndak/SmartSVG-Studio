# SmartSVG Studio V3.5 — contre-expertise des 17 lots et de l'expérience complète

**17 novembre 2026 — revue d'architecture produit et UX en session propriétaire.** Complète la [revue ID par ID 80/80](COUNTER_REVIEW_80_UX_2026_11_17.md) sans renuméroter les W00–W16, les 24 lots hérités, les 141 exigences V3.3, les 140 tickets V3.4, les 437 scénarios et les 33 opportunités. L'inventaire 80 IDs et les 15 groupes #142 ont été contrôlés dans `PRIORITY_REGISTER.json` ; ce document n'est **pas** une nouvelle revue sémantique ligne à ligne des 141 exigences, ni une preuve de réalisation.

**Base technique :** [MASTER](MASTER_PRIORISE.md), [BACKLOG_AND_DEPENDENCIES](BACKLOG_AND_DEPENDENCIES.md), [PRIORITY_INDEX](PRIORITY_INDEX.md), [UXI](UX_INTERACTION_AND_VISUAL_CONTRACT.md), [CST](CREATIVE_STUDIO_PRODUCT_CONTRACT.md), [SCN](SCENE_DECOMPOSITION_AND_RELIEF_CONTRACT.md), [CP](ADR_COMPOSITION_PERSISTENCE.md), [Smart Delivery](SMART_DELIVERY_EXECUTION_CONTRACT.md), [contrat qualité 25 axes](AUTOMATION_QUALITY_CONTRACT.md) et [contre-expertise M26/U26](COUNTER_REVIEW_2026_11_17_WORKFLOW_TOOLS.md). **Aucune implémentation, qualification machine ou mesure utilisateur réalisée par cette contre-expertise.**

## A. Diagnostic global : la faiblesse n'est pas le nombre de fonctions

La V3.5 a déjà prévu l'essentiel des fonctions. **Risque systémique principal :** après avoir acquis toutes les capacités, un débutant ne sait toujours pas *dans quel ordre les utiliser*, ni ce qui est seulement prévisualisé, enregistré, exporté ou prouvé compatible. Le correctif n'est pas un 81e bouton ni une nouvelle IA : **relier les gestes dans un même parcours avec des statuts précis et des retours immédiats**.

Les dix conventions transverses recommandées (raffinements d'UXI/CST, pas un dixième moteur) :

1. **Une seule surface d'édition, plusieurs vues contrôlées.** Source, masque, scène, planche, opérations et aperçu sont des perspectives sur le même projet et la même révision ; pas de duplication des objets ni d'Undo. Une couleur, un calque, un masque, une opération, un objet et une page de placement ne sont jamais synonymes.
2. **Trois niveaux d'information, pas trois applications :** Express (intention et 1 action principale), Atelier (gestes usuels), Expert (mesures/provenance/révisions). Le changement de niveau ne détruit pas le brouillon.
3. **Commandes stables à la souris et au clavier :** la barre contextuelle a un emplacement constant, nomme l'objet, propose seulement les actions applicables ; recherche locale par synonymes renvoie au **même** bus de commandes. Pas d'activation par survol.
4. **Une proposition n'est jamais une mutation.** Masque, filtrage IA, offset, retouche, placement et réparation s'affichent sur un brouillon identique à l'entrée validée. Appliquer crée une transaction unique ; Escape/Annuler le brouillon laisse le projet inchangé.
5. **États de travail distincts :** aperçu calculé, modification acceptée, projet sauvegardé, fichier exporté, pack publié, import Design Space/logiciel tiers vérifié, fabrication physique testée. Ni un badge unique « terminé », ni une barre de progrès inventée.
6. **Alerte ancrée dans l'objet :** chaque problème donne *où, pourquoi, impact, correctif possible, inconnues* ; un clic cadre l'élément et propose une variante sur copie si le correctif est dangereux.
7. **Taille et zoom séparés :** dimensions physiques mm confirmées et pixels source ne découlent pas du zoom 100 %. Les guides magnétiques n'inventent pas de cotes. Écran DPI/125–200 % réellement testé.
8. **Traitements fluides et annulables :** saisie/drag rendus localement en aperçu, jobs lourds bornés avec statut et annulation, seuls derniers résultats source+révision+ROI+paramètres sont applicables. Cache borné ; pas d'estimation de secondes fausse. Mesurer p50/p95, mémoire, saccades et fluidité au Windows réel.
9. **IA utile mais invisible quand inutile :** l'assistance propose une réparation ou une sélection *précise* si un modèle local admissible existe ; les gestes simples déterministes ne passent jamais obligatoirement par le LLM. Mode manuel sans réseau reste complet selon les capacités P0.
10. **L'utilisateur sait ce qu'il recevra :** écran Sortie par intention avec vrai rôle PNG PTC/SVG Basic CUT/SVG CUT multicouche/SVG éditable, périmètre de QA et limite du profil. Un ZIP ou un BAT n'est pas une preuve d'approbation externe ou de coupe.

## B. Contre-expertise de W00–W16 : risques, amélioration concrète, critères d'arrêt

| Lot | Diagnostic adversarial et risque de friction | Correction ergonomique et articulation recommandées | Gate discriminant avant fermeture |
| --- | --- | --- | --- |
| **W00 — patrimoine** | Inventaire complet peut devenir « 80 éléments = 80 fonctions testées ». | Vue de traçabilité par ID avec état **spécifié / code main / Windows / tiers / physique**, sans score global trompeur ; l'utilisateur ne voit pas cet inventaire dans le menu. | Conserver 24/141/140/80/437, 15 groupes/33 opportunités/8 rejets ; remonter les six liens T→ticket non explicites et les dix exigences G6/G9 sans V34 direct plutôt que prétendre couverture sémantique close. |
| **W01 — session/projet** | Trop d'étapes et risques de confusion « ouvrir / importer / ajouter au projet » ; format source mal compris. | Action de démarrage immédiate et **Fichier client** U26-07 en panneau discret ; une intention n'enferme pas le projet. Source intacte, annuler l'import conserve l'ancien projet. | Import PNG sain, formats supplémentaires seulement si vérifiés, erreur malveillante avant preview, reopen CAS/recovery, Windows et CPU sans ComfyUI. |
| **W02 — sélection/atelier** | 10 outils séparés nécessitent une formation ; masques et objets peuvent paraître la même chose ; vraie persistance objets V2 absente. | Même canevas et cible, clic/lasso/pinceau progressivement, gestes garder/masquer sans ambiguïté, zone contextuelle stable, mini-diff ; avancées U26-01/02 **après** multi-objets et CP. | Même Subject ID au clic, pinceau, Undo, sauvegarde/reopen ; aucune fausse persistance SceneNode/TextNode dans V1 ; Windows DPI/focus. **Prochaine tranche d'ingénierie réelle.** |
| **W03 — quatre exports** | L'utilisateur croit qu'un format porte toutes les informations ; PNG PTC vs PNG gravure et « SVG éditable » vs « CUT ». | Écran Sortie avec quatre cartes et 1 phrase de conséquence chacune, destination, cotes, contrôle de perte d'éditabilité, relecture et rapport M26-B par rôle. | Fichier réel ouvert dans parser sûr, cotes/topologie/bleed par rôle, dégradations déclarées ; CUT multicouche reste projection externe si V1 ne l'admet pas. |
| **W04 — prévol** | Alertes trop générales, seuils matière implicites et faux « prêt machine ». | Centre des problèmes commun à U26-03 ; cliquer une anomalie zoome vers le chemin, correction sur copie et classification local/logiciel tiers/physique ; U26-07 réutilise l'inspection pour intake. | Pas d'erreur bloquante silencieuse, statut KNOWN/UNKNOWN/UNSUPPORTED, dimension inconnue refuse export de fabrication, source non mutée. |
| **W05 — SD0 plan** | ZIP assistant peut compliquer un export simple ; préparation dite « livrée » sans fichier. | Une action « Exporter » reste directe ; « Préparer un pack » secondaire, d'abord une **liste en lecture seule** de fichiers admissibles, omissions et licences. | SD0 sans écriture, au moins 1 artefact réel, aucune source privée ni sortie dont QA est FAIL sélectionnée. |
| **W06 — SD1/SD2 livraison** | Confusion projet .smartsvg / export externe / ZIP / BAT / guide ; Undo externe impossible. | Un assistant de livraison sobre : choisir fichiers → contrôler → destination → reçu ; instructions TXT obligatoires quand nécessaires, HTML facultatif ; BAT U26-05 reste une fiche de revue non signée. | Hashs, quotas, chemins relatifs, refus overwrite, crash/reprise, ZIP relu, statut PARTIAL explicite ; pas de fausse compatibilité Design Space/laser. |
| **W07 — Smart Cut Advisor** | Un score de complexité unique peut supprimer des détails volontaires. | Vue fidèle/équilibré/facile liée à la même source, zoom identique, micro-détails surlignés ; l'IA peut expliquer, ne décide pas seule. | Conservation des îlots/trous, seuils par matière UNKNOWN, absence de promesse de vitesse réelle ; variantes réversibles. |
| **W08 — PTC/DS** | Mélange de préparation fichier et d'étapes faites par Design Space, incite à croire à un import direct. | Fiche de transfert versionnée, opérations manuelles Score/Attacher/mirroir, vérification tailles et calibration hors application ; mention « fichier créé / import non vérifié ». | Essai DS/version lié au fichier et preuve distincte, pas API privée ni prétendue calibration SmartSVG. |
| **W09 — Weeding** | Générer des lignes supplémentaires peut ruiner une géométrie valide. | Commencer par une **carte visuelle des zones difficiles** ; propositions de boîtes de désherbage en brouillon seulement après validation. | Pas de coupe générée sans preuve topologique et protocole coupon physique ; source et contours originaux inchangés. |
| **W10 — texte** | Police invisible/manquante, perte d'éditabilité et bouton conversion trop facile. | Édition du texte sur canevas, inspecteur glyphes, police et licence, aperçu courbes sur copie ; B10/B11 restent sous le même panneau Texte/Apparence. | CP0–6 selon capacité et migration V2 sur copie ; tests accents/ligatures/convertir/réouvrir, aucun rendu substitution silencieuse. |
| **W11 — gabarits** | Trop de patrons prédéfinis sans paramètres simples ; une boîte peut être appelée « topper ». | Cartes de gabarits par usage et 3–5 champs dimensionnels prioritaires ; variantes et languettes M26-C seulement après contrat reconnus. | Étiquette/carte/topper réellement différents, coordonnées mm, CUT/SCORE, original, save/reopen ; gabarit impossible refusé. |
| **W12 — bibliothèque/séries** | Un lot 50 pourrait être 50 masques V1 ou 50 fichiers écrasés ; UI chantier confuse. | Tableau lignes « entrée / quantité / état / relancer les échecs », pages/instances distinctes, placements verrouillés U26-04 après CP, favoris/recherche locaux. | Aucun doublon au retry, quota mémoire et masques V1 respectés, méta locales/non portables visibles, projets et instances identifiables. |
| **W13 — UX/framework** | Refaire l'UI en Qt/Tauri au nom de l'esthétique pourrait retarder tout le produit ; composants dupliqués. | Tester Tk avec interactions réelles ; maintenir **une seule base** de commandes et composants (canevas, inspecteur, comparateur, problèmes, export), mode Express/Expert. | Windows 1366×768, DPI100/125/150/200%, clavier/focus, barre visible, temps/latence, crash, faible RAM ; changer de framework seulement sur blocage mesuré. |
| **W14 — IA locale facultative** | Trop de modèles, consommation VRAM, prompts confus ; absence du fournisseur = outil cassé. | Cacher les outils non installés ou les annoter « facultatif », montrer coût estimatif qualitatif, annuler et repli CPU ; un seul système de proposition/validation IA. | Catalogue licences/hashes, consentement séparé, OOM et résultats périmés, tests RTX réels distincts ; pas de téléchargement implicite. |
| **W15 — Windows autonome** | Une belle maquette sans installateur, updates sûrs ni reprise ne constitue pas logiciel autonome. | Installation hors ligne, démarrage direct, mise à jour signée/contrôlée selon mécanisme retenu, récupération explicite et retour arrière. | Installer Windows testé, composants non cachés (pas de ComfyUI obligatoire), projets réouvrables et absence de dépendance réseau par défaut. |
| **W16 — R&D avancée** | Génération/3D/rig/multimarque peut dévorer la roadmap, promettre précision non atteinte. | Mini-expériences **isolées** : OCR vérifié, relief 4 plans, Smart Cost indicatif, photo feedback incertain, nom/QR versionné, multimarque via profils d'export seulement, sans pilotage. | Gates propres à chaque S-021/044/047/066/099 et aux suggestions P2, aucune qualification physique déduite d'une simulation, retour aux parcours P0 prioritaire. |

**Correctif de planification :** les fonctions locales U26-01, U26-02 et U26-07 peuvent être préparées par tests de fixtures lorsque leurs ports existent ; elles ne deviennent pas un prérequis avant un premier import→sélection→export validé. Les systèmes de recettes, réédition V2, PDF/BAT avancé et optimiseur ne commencent pas sans leur autorité d'objet et leurs révisions.

## C. Quinze groupes du programme #142 : couverture transversale, sans duplication

Tous conservés : **Fondation produit, Architecture UI, Smart Delivery, Smart Cut Advisor, Smart Weeding, Print Then Cut Assistant, Compatibilité Design Space, Smart Cost, Séries personnalisées, Smart Cut Feedback, Recettes/modèles partageables, Production multimarque, Optimisation multicritère, 80 capacités UX, Héritage intégral V3.4**.

- **À mutualiser en composant UI commun :** Architecture UI + 80UX + aide ; Smart Cut Advisor/Weeding/PTC/DS + centre des problèmes/prévol ; Smart Delivery + export/guide/BAT ; séries/recettes + bibliothèque et tâches.
- **À maintenir conceptuellement distincts :** diagnostic local vs résultat matériel, document de revue vs approbation client, recette de dessin vs publication, source/masque/objet/scène/placement, prix de matière estimé vs facturé.
- **P2 à limiter par prototype :** feedback d'une photo physique (conditions d'éclairage non contrôlées), multimarque (formats/profils, pas machine), optimisation multicritère (gains mesurés, pas score arbitraire). Les huit opportunités rejetées O-003/O-015/O-018/O-021/O-024/O-027/O-030/O-033 restent rejetées.

## D. La vraie navigation proposée : cinq moments, une seule création

1. **Commencer.** Accueil par intention : Importer / Stickers / Scène / Reprendre ; toute fonction réelle reste trouvable par « Autres créations » ou recherche d'actions. Import pris en charge et diagnostic U26-07 non anxiogène.
2. **Modifier.** Atelier à canevas unique, liste d'éléments repliable, une seule zone propriétés contextuelles ; action principale pour créer/corriger, avant/après synchronisé, barre Undo stable. L'utilisateur sait constamment *quelle cible* il édite.
3. **Préparer.** Sélectionner une intention de sortie, conserver le dessin original, vue des opérations, dimensions mm, contrôles localisés et propositions de réparation sur copie U26-03. Absences de paramètres = UNKNOWN, pas pré-remplissage trompeur.
4. **Exporter.** Quatre rôles stricts selon disponibilité réelle, taille et effets du choix, chemin visible, fichier relu et reçu ; option secondaire « Pack » avec consentement. Pas de simple navigation qui réalise l'export.
5. **Retrouver.** Bibliothèque/récents, projet .smartsvg, exports historiques et variantes distingues ; reopen/restauration sans perte d'identité et sans montrer les médias privés dans les miniatures par défaut.

Le passage entre moments **ne crée aucune mutation ni sauvegarde implicite**. Un novice peut exporter sans passer dans le mode Expert ; un expert voit provenance, unités, topologie et logs à la demande.

## E. Prototype d'écran testable sans nouveau framework

```text
SmartSVG Studio  |  Mon projet [Modifié]           [Annuler] [Rétablir] [Enregistrer]
[Importer] [Sélectionner] [Créer] [Préparer] [Exporter]     [Rechercher une action]
┌─────────────────┬─────────────────────────────────┬──────────────────┐
│ Éléments        │ Canevas unique                   │ Propriétés       │
│  Fond           │   [image / objets / masques]      │ Cible : fleur    │
│  Fleur          │                                 │ Garder / Masquer │
│  Texte          │   guides / preview non mutant    │ Contour : 2 mm   │
│  [Liste repliable]│ [Avant | Après / Diff]          │ [Aperçu/Appliquer]│
└─────────────────┴─────────────────────────────────┴──────────────────┘
[2 alertes] [Voir la première]          État : aperçu prêt ; projet non enregistré
```

**Attention :** uniquement un croquis UX de contrat, ni capture d'une application actuelle ni prescription de maintenir trois panneaux ouverts sur petit écran. En fenêtre étroite et DPI 200 %, rabattre les panneaux ; garder action principale et état visibles. Barre contextuelle à emplacement stable ; pas de boutons flottants sous le curseur.

## F. Huit parcours E2E à rendre plus courts et mesurables

| Parcours UX historique | Friction actuelle plausible | Correction de parcours et test concret |
| --- | --- | --- |
| **F01 Sticker** | Refaire détourage puis taille puis contrôle dans plusieurs écrans. | Import → masque → aperçu alpha/bleed → mm → PNG PTC ; tester mêmes réglages après retour arrière, source non altérée et avertissement DS. |
| **F02 Retouche pinceau** | Confusion entre ajouter/retirer masque et supprimer un élément. | Une cible et geste explicites, avant/après, 1 Undo pour un stroke validé, pinceau et lasso sur le même SubjectID ; tests focus et annulation. |
| **F03 Vinyle Basic Cut** | Le rendu visuel paraît bon mais contient un double tracé ou trou disparu. | Préparer montre chemin exact/îlot, 3 variantes et erreurs cliquables ; impossibilité de déclarer « prêt matière » avec profil inconnu. |
| **F04 Texte/compose** | Police absente ou effet aplati, export coupe écrase le texte source. | Texte source encore rééditable après reopen CP ; conversion sur copie, avertissement de licence/glyphe et correspondance de dimensions. |
| **F05 Boîte/diorama** | Un tracé pliage est importé comme CUT. | Opérations typées, aperçu des plis/ordre, instructions SCORE/Attacher, relief 2.5D explicite ; coupon de test distinct. |
| **F06 Planche/lot** | Duplications et reprise cassent quantité ou déplacent les verrous. | Vue 12/24/50 instances, « verrouiller cette pièce », relancer seulement lignes échouées ; zéro doublon/replacement verrouillé. |
| **F07 IA optionnelle** | Modèle absent bloque le geste ; prompt remplace une sélection non validée. | Même ROI, proposition isolée, alternative CPU/manuelle, origin/provenance, annuler résultat périmé ; test OOM et consentement absent. |
| **F08 Export/livraison** | Projet sauvé est pris pour un fichier prêt ; ZIP présumé certifié. | Nommer chaque état, rôle et réception ; PNG seul peut suffire à ZIP après QA ; tests no-clobber/crash, contenu licite et import tiers NON_VERIFIÉ. |

## G. Trois correctifs immédiats de langage produit, sans nouvelle fonction

- **« Terminé » → phrase d'état vérifiable :** « Aperçu mis à jour », « Projet enregistré », « Fichier exporté et relu », « Pack créé », « Import logiciel tiers non vérifié ». Le mot **« prêt machine »** est réservé à une éventuelle preuve matérielle explicitement identifiée, jamais au seul parser SVG.
- **« IA intelligente » → proposition explicable :** dire si la sortie est règle déterministe, heuristique ou résultat de modèle avec provenance ; proposer le mode manuel quand disponible.
- **« Export universel » → format et profil :** la compatibilité signifie un fichier aux invariants du rôle, pas import garanti dans tous logiciels/firmwares. Laser, autres plotters et découpeurs restent préparation seule.

## H. Stratégie d'exécution bornée (priorités originales inchangées)

**T0 — Maintenant :** W02 sous le producteur horaire déjà existant. Raccorder même identité/masque/Undo et UXI/E13 ; ne pas dupliquer le canevas ni créer un nouveau store. Preuves attendues : parcours vrai sur code, tests exact-head, puis UI Windows séparée.

**T1 — Après premier W03 réel :** W04 et centre de diagnostic U26-03, rapport M26-B, premier Smart Delivery plan/pack selon W05/W06. Une option avancée n'attend pas les quatre rôles pour aider le premier export sain.

**T2 — Quand CP d'objets est réellement prêt :** B01/B02/B04/B05 et U26-01/U26-02 ; W10 texte et W11 gabarits, puis bibliothèque/lot W12, U26-04/U26-06 si writer et recettes sont qualifiés.

**T3 — Extensions isolées :** M26-A gravure raster externe, M26-C tenons, BAT U26-05, AI W14 avancée et W16 R&D ; pas de dépendance sur P0 hors connexion technique indispensable.

**Portes de succès humain à programmer :** cinq novices+au moins un profil expert testent les parcours réels, avec clavier et petites fenêtres ; mesurer réussite sans aide, nombre d'aller-retours, temps total y compris relances IA, erreurs de dimension et récupération après interruption. Ne pas transformer des seuils proposés en statistiques observées. Le protocole historique UXI conserve ses objectifs.

## I. Frontière d'audit et risques résiduels

- **Revu par ID 80/80** via PRIORITY_INDEX et dossiers COV existants ; **W00–W16 revus transversalement** et quinze groupes #142 couverts conceptuellement.
- Les **141 obligations, 140 tickets, 437 scénarios et 24 lots** ont été **réconciliés en cardinalité et héritage**, mais cette passe ne lit pas/revalide chaque ligne des 437 scénarios ni ne démontre leur exécution. Leur traçabilité normée et tests de chaque critère demeurent nécessaires.
- Un correctif UX est **proposé**, jamais livré par un PDF/markdown. Les preuves axes `CODE_MAIN`, `CPU`, `WINDOWS_UI`, `RTX_GPU`, `DESIGN_SPACE`, `PHYSICAL` restent indépendantes.
- Ne pas modifier `AGENTS.md`, `.automation/READY`, workflows, tâches, schéma/reader-writer V1/V2, CI, dépendances ou états de cursor pour une simple revue. La V3.5 est déjà adoptée ; aucune « V3.6 ».
