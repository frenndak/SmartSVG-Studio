# SmartSVG V3.5 — micro-gains UX et production (veille du 17 novembre 2026)

**Statut :** proposition documentaire adoptable ; **aucune capacité livrée ni performance mesurée**. Revue des pratiques 2026 et du corpus existant V3.5 au 17/11/2026, sans inventer un nouveau lot W17, un 81e ID UX, une sortie machine ou un rôle `Artifact.use` V1. La prochaine action d'ingénierie reste celle de `EXECUTION_STATE.json` : **W02 native selection**. Ce complément ne bloque pas l'alpha Windows, W03/W04 et Smart Delivery.

## 1. Pourquoi ce complément et quelles sources ?

Constat : les meilleurs gains peuvent provenir de **petites commandes déterministes recombinées**, pas d'un nouvel éditeur parallèle ou d'une IA autonome exécutant du code. Le produit conserve sa mission **préparer et contrôler des projets**, pas piloter un laser/plotter.

- [Adobe Illustrator (30.6, juin 2026)](https://helpx.adobe.com/illustrator/desktop/new-features/release-notes.html) : relier toutes les occurrences d'une image source en une étape ; enregistrer alignement/distribution comme actions ; aperçu des espacements.
- [Adobe Illustrator AI Assistant beta, 2026](https://helpx.adobe.com/fr/illustrator/desktop/use-ai-assistant/about-using-ai-assistant-in-illustrator.html) : planifier et guider des tâches multi-étapes, organisation, édition par lots, export ; Adobe signale que l'assistant peut être plus lent que l'outil manuel sur les gestes simples. **Pas de copie d'un agent autonome généraliste**.
- [Figma, menu Actions](https://help.figma.com/hc/en-us/articles/23570416033943-Use-the-actions-menu-in-Figma-Design) : sélectionner les éléments de mêmes propriétés, rechercher des actions, renommage assisté, aimantation ; [renommage IA](https://help.figma.com/hc/en-us/articles/24004711129879-Rename-layers-with-AI).
- [LightBurn 2.2, outils d'édition et nettoyage](https://docs.lightburnsoftware.com/2.2/Reference/UI/EditMenu/) : prétraitement, jonction de chemins et opérations de sélection ; ces bases restent nécessaires même à une génération IA.
- [Discussion atelier : fichiers clients mal préparés, septembre 2026](https://www.reddit.com/r/lasercutting/comments/1wod4kk/customer_cut_files_are_doing_my_head_in_lately/) : témoignage illustratif sur doublons, masques/contours et nettoyage manuel ; **ne mesure pas** une demande ou un marché.

**Anti-doublon obligatoire :** `UX_INTERACTION_AND_VISUAL_CONTRACT.md` prévoit déjà UXI-11 « Rechercher une action » local avec synonymes et UXI-03 barre contextuelle ; `CREATIVE_STUDIO_PRODUCT_CONTRACT.md` prévoit déjà recettes réversibles, CST0–4, réglages liés à la source ; W04/W07 prévoient déjà prévol/diagnostic, W12 placements/séries et W06 Smart Delivery/guide. Les six points ci-dessous **spécifient des usages précis manquants ou insuffisamment détaillés**, ils ne créent pas six nouveaux moteurs.

## 2. Six améliorations bornées

### U26-01 — Sélectionner par propriétés et édition groupée (P1 courte, W02/W13, après multi-objets)

**Parcours :** sélectionner un objet ; « Sélectionner les mêmes couleurs / opération / taille à tolérance déclarée / source » ; afficher le nombre et les groupes verrouillés ; **aperçu puis une commande Undo** pour recolorer, déplacer ou modifier une propriété commune. Un utilisateur peut corriger 80 contours similaires sans les cliquer un par un.

**Delta par rapport à B02 :** la multi-sélection/groupement existe ; **la sélection calculée par critère et son diagnostic de portée** ne sont pas détaillés. Commencer par la correspondance exacte de propriétés typées, **sans IA**.

**Refus/tests :** ne pas convertir « même couleur » en « même opération » ; valeurs mixtes non remplacées par zéro ; objets ou descendants verrouillés non modifiés, résultat STALE si sélection change ; 100 objets, 1 Undo, conservation d'IDs.

### U26-02 — Guides magnétiques en mm + distributeur visuel (P1 courte, W02/W13/C17)

**Parcours :** aligner à des bords/centres/espacements avec guides temporaires non imprimés, accrocher à des valeurs mm vérifiées, touches pour petits déplacements, **prévisualiser les écarts** puis appliquer. Désactivation facile pour éviter des corrections indésirables.

**Delta :** B04/UXI prévoient déplacer/aligner ; le **magnétisme explicite avec unités physiques, seuil de capture contrôlé et désactivation** mérite une recette de qualification, sans créer un moteur CAD.

**Refus/tests :** dimensions physiques inconnues → guide écran informatif seulement, jamais cote de fabrication ; zoom ≠ mm, points flottants sans arrondir les dimensions de sortie, interaction clavier et DPI 200%, objets verrouillés inchangés.

### U26-03 — « Préparer ce fichier » : diagnostic → propositions → aperçu (P1 UX, W04/W07/UXI-11)

**Parcours :** une entrée par intention (sticker, découpe vectorielle, dessin/gravure) agrège les **contrôles déjà existants** (taille, transparence, chemins ouverts, doublons, traits invisibles, trous, objets hors zone), distingue **corrigible localement / à vérifier dans l'application cible / inconnu** ; l'utilisateur choisit une à une ou en lot **les seules corrections sûres**, voit un diff puis valide. Aucun changement automatique implicite.

**Delta :** W04/W07 sont déjà propriétaires des diagnostics/correctifs. Le **panneau de triage unifié et d'actions explicables** est la plus-value d'ergonomie, pas un nouveau QA. Ne jamais prétendre que les validations locales garantissent une découpe physique. Les opérations distinctes ont des critères et tests propres.

**Refus/tests :** trou disparu sous auto-merge = bloqueur, profil matière UNKNOWN reste UNKNOWN, chemins non approuvés conservés, analyse de fichiers non fiables sans exécuter de code ou URL ; correction partielle annoncée précisément.

### U26-04 — Remplacer une source sur toutes ses occurrences (P2, W12 + CP2/CP3 requis)

**Parcours :** un logo réutilisé sur 50 placements est remplacé **sur copie et après confirmation** ; préserver quantité, positions, noms et contraintes existantes ; avertir si proportions/géométrie rendent certains placements invalides et permettre une reprise ciblée. Ne pas remplacer 50 `Subject` V1 ni inventer un second writer.

**Delta :** W12 sait dupliquer/positionner ; la **propagation versionnée du remplacement de source** est une capacité spécifique non suffisamment formalisée. Dépend de la persistance d'objets/instances réelle, **pas** de la fonctionnalité de base W02.

**Refus/tests :** source absente/ID incohérent, mauvaise proportion, placements verrouillés, anciennes sorties déjà publiées → conserver, ne pas écraser ; calculer hash/provenance, rollback, relecture/redo.

### U26-05 — Bon à tirer (BAT) client 2D hors ligne (P2 courte, W06/SD2 + W03/W04)

**Parcours :** produire **sur demande** une planche d'approbation visuelle PNG ou PDF avec miniature, dimensions connues, variante, date, révision de fichier et avertissements ; client peut valider le dessin **humainement** hors SmartSVG. Ce BAT est une **pièce de revue** jointe au dossier, **pas un cinquième format de fabrication** ni une preuve de coupe/gravure réussie.

**Delta :** Smart Delivery prévoit déjà un guide et manifeste, mais la **preuve visuelle d'accord client avec version et garde-fous** est un usage pro distinct.

**Refus/tests :** modèle non accordé/licence privée, cotes inconnues, rendu approximatif, changements après génération → BAT périmé/REVIEW_REQUIRED ; aucun lien distant ni contenu actif ; conserver source originale et qualité de l'export réel.

### U26-06 — Enregistrer une séquence d'actions comme recette sûre (P2, W12/CST/UXI, après bus de commandes fiable)

**Parcours :** « enregistrer comme recette » une **petite suite de commandes déjà typées et réversibles** (aligner, répartir, simplifier, ajouter contour, exporter à destination choisie) ; régler des paramètres explicites ; appliquer sur une nouvelle sélection **uniquement après aperçu et confirmation**.

**Delta :** les recettes CST et batch W12 existent dans la conception ; il manque un **mode de capture depuis les gestes utilisateur**, plus abordable qu'écrire des scripts ou configurer un agent IA. Le langage naturel pourrait **proposer** une recette admise en P2, jamais exécuter librement.

**Refus/tests :** aucune macro enregistrant des clics absolus, commandes machine, scripts, URL, chemins secrets, sauvegardes/publications automatiques ou opérations non prises en charge ; versions et permissions vérifiées ; refus groupé ou PARTIAL explicite, tests double-clic/Undo/annulation.

## 3. Arbitrage, ordre de livraison et limites

| Référence | Priorité recommandée | Raccord précis | Critère qui justifierait le développement |
| --- | --- | --- | --- |
| U26-01 | **P1** | W02/W13 après vrai multiselect | correction groupée sans perte d'IDs/locks, Undo réussi sur 100 objets |
| U26-02 | **P1** | W02/W13 | écart mm explicite, snapping annulable, UI DPI fiable |
| U26-03 | **P1** | W04/W07, une fois prévol réel | ≥3 défauts localisés et 1 correction approuvée ; aucune fausse certification |
| U26-04 | P2 | W12 après CP2/3 | 50 placements resynchronisés sans écraser les exports |
| U26-05 | P2 ciblée | W06 SD2 | BAT versionné et non confondu avec fichier machine ou validation matérielle |
| U26-06 | P2 | CST/W12, bus de commandes qualifié | 3 commandes réversibles rejouées ; preview diff, récupération et refus scripts |

**Ne pas ajouter** : nouvel agent généraliste IA à droits illimités, système de plugins arbitraires, assistant conversationnel comme passage obligatoire, duplication de la recherche d'action UXI-11, nouvelle application de CAO, simulation mécanique/laser certifiée, nouvel éditeur/canevas parallèle. Les idées « chercher des assets par image », « IA qui refait tout le dessin » et « 3D physique » sont reportées à étude distincte : coût mémoire, modèles, licences et risque de résultats invérifiables disproportionnés à ce stade.

### Exécution

- Tout reste **optionnel et non bloquant** pour le jalon Windows, W02/W03/W04/Smart Delivery.
- Réutiliser ports existants et historiques ; aucune nouvelle famille d'exports, nouveau `Artifact.use`, modifier `EXECUTION_STATE`, task R12, AGENTS/READY ou politique d'autofusion.
- Conception révisée **≠ code écrit** ; tester fixtures CPU/Windows, cas négatifs et critères mesurables au moment de chaque incrément. Avant chaque implémentation, refaire la recherche anti-doublon sur `main` au HEAD actuel ; **supprimer le micro-lot s'il est déjà couvert**.
