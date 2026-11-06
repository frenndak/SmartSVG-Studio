# SmartSVG Studio V3.4 — Annexe transversale UX/UI : design system, interactions et exécution

**Décision produit : 6 novembre 2026 — proposition d'approfondissement autorisée par le propriétaire dans une session active.** Cette annexe détaille les **lots existants 02, 06, 07, 18, 21 et 22** et les tickets **V34-017/019/041–049/132–133/139–140** ; elle ne crée **ni 25e cycle, ni ticket V34-141, ni exigence héritée supplémentaire**, et ne modifie pas les 141 exigences, les 140 tickets, les 437 scénarios de la campagne ou les quatre contrats d'export. Toute adoption dans `main` nécessite une PR documentaire et une validation propriétaire en session, jamais une autofusion horaire. Les critères UX-xx ci-dessous sont des **critères de recette complémentaires** et non des tickets.

**Objectif non négociable :** SmartSVG V3.4 est une application de bureau Windows **autonome sans ComfyUI obligatoire**, compréhensible pour un débutant, maîtrisable par un expert, réellement réactive et local-first. ComfyUI reste un adaptateur *facultatif*. Toute prévisualisation sans traitement réel est clairement étiquetée « démonstration ».

## 1. Autorité et état de preuve

La vérité métier reste le projet `.smartsvg`, ses `Subject` et ses SHA, ainsi que les contrats CUT/SCORE/DRAW/PRINT/FOIL. Une vue ne crée pas de deuxième writer, historique, file de jobs, cache autoritaire ni exporteur. `ProjectSession` décrit une lecture de l'état ; `CommandPort` et le writer historique sont seuls autorisés à publier des mutations et leurs reçus. Une modification en attente = « non enregistrée ». L'export local n'est jamais « prêt machine » sans prévol ; Design Space et une découpe réelle restent des étapes externes.

**Base réellement disponible au 6 novembre (à revérifier au moment de chaque lot) :** bootstrap natif CLI `engine/standalone_bootstrap_v34.py` (#98) et prototype Tkinter **lecture seule** `engine/standalone_desktop_v34.py` (#99) intégrés ; aperçu de vrai PNG proposé en PR #100 mais pas implicitement livré. **Ni choix de framework final, ni UI Windows validée, ni installateur, ni canevas complet, ni benchmark ne sont acquis.**

## 2. Architecture de l'expérience : six espaces et un projet

| Espace | Première action visible | Vue secondaire | Jamais masquer |
| --- | --- | --- | --- |
| **Express** | « Importer une image », « Faire des stickers », « Créer un patron » | Parcours guidé en 1–3 décisions métier significatives, pas un objectif artificiel de clics | Taille réelle, erreurs de prévol, statut d'export |
| **Atelier** | Canevas + sélection d'un vrai sujet, outils Ajouter/Effacer | Calques, propriétés, comparaison, grille/guides, Undo/Redo | Source originale et statut de sauvegarde |
| **Fabrique** | Choix explicite du produit et de la matière | Planche, CUT/SCORE, placements, vérifications | Profil machine UNKNOWN et passage manuel Design Space |
| **Vectoriel** | Inspecter les contours, basculer édition/découpe | Nœuds, courbes et topologie quand disponibles | SVG éditable ≠ SVG Basic Cut |
| **Bibliothèque** | Reprendre projet, modèles, variantes | Recherche/tri/favoris locaux, historique de travail | Aucune miniature de média privé par défaut sans choix |
| **Expert** | Diagnostic de projet, provenance et capacités | Paramètres, logs expurgés, modèles IA facultatifs, adaptateur legacy | Différence « installé / compatible / testé / certifié » |

**Structure commune souhaitée :** barre d'application (projet, état durable, Undo/Redo, accès aide) ; navigation d'espaces stable ; panneau gauche facultatif (objets/calques) ; **canevas central prioritaire** ; panneau droit contextuel (propriétés) ; zone basse escamotable (tâches, alertes, preuves). Toujours une alternative liste/clavier au geste sur canevas. L'ouverture/fermeture de panneaux ne modifie pas le fichier projet ni la sélection durable.

**États d'accueil :** premier lancement, reprise récente, import bloqué, projet corrompu, récupération requise, modèle IA absent, traitement interrompu. L'accueil ne simule pas des sujets détectés ; la démonstration est séparée de l'espace de production.

## 3. Design system réutilisable : contrat avant esthétique finale

Les valeurs ci-dessous sont **des hypothèses de démarrage pour un spike Windows**, pas une charte finale déjà validée. Le framework retenu devra permettre des **tokens sémantiques partagés** et des composants réutilisables.

| Famille de tokens | Proposition de départ | Règle |
| --- | --- | --- |
| Couleurs sémantiques | `surface.canvas`, `surface.panel`, `surface.raised`, `text.primary/secondary`, `border.subtle/strong`, `action.primary`, `status.success/warning/error/unknown`, `focus.ring` | Toutes les couleurs remplaçables par thème ; aucun statut seulement colorimétrique |
| Thèmes | Clair + sombre, préférence locale et « suivre Windows » | Changement sans toucher `.smartsvg`; vérifier contrastes dans les deux |
| Typographie | Famille système Windows accessible, base candidate 14 px, titres 16/20/26 px, monospaced pour coordonnées/ID | Agrandissement jusqu'à 200 %, largeur adaptée ; polices propriétaires non requises |
| Espacement | Base 4 px ; échelle candidate 4/8/12/16/24/32 | Cohérence de marges, zones cliquables adaptées au stylet/souris |
| Formes/élévation | Rayons candidats 6–10 px, bordure lisible, ombres très modérées | Priorité à la lisibilité et au zoom sur la décoration |
| Icônes | Jeu cohérent de pictogrammes vectoriels locaux + labels accessibles | Icône seule uniquement si accessible et non ambiguë |
| Densité | Confort / compact, sans changement du rendu du projet | État UI local, pas de réécriture des coordonnées de fabrication |
| Curseurs/états | Hover, focus visible, active, disabled + raison, processing, error, retry | Pas de faux succès optimiste ni de bouton actif pendant conflit |

**Composants à stabiliser une seule fois :** `AppShell`, `ProjectStatusBadge`, `ActionButton`, `ToolButton`, `SplitPanel`, `CanvasViewport`, `ObjectTree`, `PropertiesInspector`, `PreflightNotice`, `JobProgress`, `EmptyState`, `ErrorRecoveryCard`, `ConfirmDialog`, `HelpPopover`, `ToastLog` et `ExportHandoffCard`. Un composant doit posséder : états, libellés FR, focus clavier, rôle lecteur d'écran, apparence clair/sombre, taille min, et test associé. Aucun framework final choisi par cette annexe.

## 4. Gestes, micro-interactions et animations

| Interaction | Comportement attendu | Fallback/accessibilité | Preuve |
| --- | --- | --- | --- |
| Navigation d'espace | Vue changée sans perdre la session/les brouillons ; transitions discrètes, sans masquer une erreur | Animation désactivable ; navigation clavier et focus logique | UX-01 / UX-02 |
| Ouverture panneau | Repli/dimensionnement progressif facultatif ; canevas reprend l'espace utile | Panneau totalement accessible en mode « réduction des animations » | UX-03 |
| Sélection | Objet, liste et propriétés reflètent **même subject_id/revision** ; surbrillance sobre | Annonce du nom/ID ; flèche et tabulation | UX-04 |
| Zoom/pan | Zoom centré sur la position du curseur si possible, « ajuster », 100 %, aperçu des dimensions réelles | Ctrl+0, commandes clavier, coordonnées source inchangées | UX-05 |
| Retouche | Pinceau avec diamètre visible ; preview local → confirmer → reçu durable ; avant/après | Curseur compatible clavier et outils de correction alternatifs | UX-06 |
| Déplacement/redimensionnement | Poignées, bornes, aperçu avant validation, unités mm si connues | Champs numériques, flèches, Escape sans commit | UX-07 |
| Snap/grille/règles | Magnétisme facultatif, guides éphémères, désactivation simple ; pas de modification implicite du CUT | Option clavier ; unités et tolérances indiquées | UX-08 |
| Traitement long | Progression réelle ou état indéterminé honnête ; UI toujours réactive ; annulation coopérative | Etat textuel/lecteur d'écran, reprise explicite | UX-09 |
| Sauvegarde | « Modification en attente » → « Enregistrement… » → « Enregistré » **après receipt** | Conflit et disque plein avec procédure claire | UX-10 |
| Erreur/avertissement | Alerte courte près de l'action, détails dépliables, correctif ou retour sûr | Pas d'information codée par couleur seule | UX-11 |
| Export | Carte résultat avec nom/format/dimensions/état, bouton dossier et guide Design Space | Jamais appeler export « découpe réussie » | UX-12 |

**Paramètres de motion à qualifier** : animation décorative 120–220 ms, sans mouvement non nécessaire pendant le dessin ; priorité au ressenti de fluidité et à la latence réelle plutôt qu'à une animation imposée. `prefers-reduced-motion` ou option locale équivalente = durée ~0. Ne pas lancer de boucle permanente ni d'animations coûteuses pour masquer un calcul lent. Aucune mesure d'animation certifiée avant prototype.

**Notifications :** erreurs bloquantes persistantes et récupérables, succès brefs, progression sans doublons, historique consultable ; pas de pluie de toasts, de modale à chaque clic ni d'alertes hors contexte. Une suggestion IA ne confirme aucune action.

## 5. Canevas et interaction : exigences de conception

- Rendu sur couche indépendante de la source canonique : original, masque, découpe, guides, sélection, outils ; activer/désactiver chaque superposition. Mode damier, fond clair/sombre, avant/après.
- Transformations dans un espace de coordonnées explicite (image px / vue / unités mm). Zoom, recadrage et redimensionnement de panneau **ne changent jamais l'artefact** ; éviter dérive des bords et du placement.
- Affichage progressif : première image, puis tuiles/miniatures si nécessaire ; cache mémoire borné, libération lors du changement de projet ; pas de décompression massive sur thread UI.
- Pointeur : clic, déplacement, double-clic, clic droit selon contexte ; tous les gestes critiques ont une commande alternative. La sélection multiple n'attribue jamais automatiquement une opération CUT/SCORE.
- Calques : source, sujets, masques, texte, tracés, opérations de fabrication sont des vues dérivées ; visibilité/solo/verrouillage documentés. Groupement, alignement, magnétisme et duplication ne sont pas considérés acquis par la simple présence des boutons.
- Interface cohérente pour 12, 24 ou 50 **instances en lots** : liste virtualisée, progression par objet, échecs individuels, jamais 50 masques chargés hors contrat V1.
- Historique transverse : une action validée = une entrée explicable et inversible si c'est une mutation interne ; aucun Undo de feuille imprimée ou d'export externe.

## 6. Responsive Windows, performances, ergonomie et accessibilité

**Fenêtres cibles minimales de validation :** 1280×720 et 1366×768, puis 1920×1080/2560×1440, Windows à échelles 100/125/150/200 %. Barre d'actions essentielle visible sans scrolling horizontal ; si l'espace manque, replier les panneaux secondaires et préserver la zone de création. Réouverture de fenêtre avec arrangement local, possibilité « rétablir disposition ». Vérifier les chemins Unicode, grands intitulés et écran secondaire.

**Entrées :** souris, clavier, trackpad ; stylet si runtime le supporte, sans le rendre obligatoire. Raccourcis à valider : Ctrl+O, Ctrl+S, Ctrl+Z, Ctrl+Shift+Z, Ctrl+0, F5, Escape, et `?` (aide). Dans les champs texte, Ctrl+Z agit sur le texte local. Focus toujours visible ; aucune dépendance au survol. Libellés/contrôles utilisables au clavier et avec lecteur d'écran ; rôles/annonces adaptées au framework natif, pas copie aveugle de `aria-live`.

**Objectifs mesurables non acquis :** navigation p95 <150 ms sur projet synthétique 12 sujets (lot 07) ; aucune requête réseau au lancement ; pas d'IA chargée implicitement ; durée et pic RAM à enregistrer pour 12/24/50 ; 100 changements de vue sans fichier projet modifié et sans croissance mémoire non bornée. Les cibles de FPS pour le canevas et le temps de premier rendu seront **établies après mesure de baseline Windows** ; éviter les chiffres garantis sans plateforme. Les opérations ZIP/PNG/IA sur worker avec token d'annulation et rejet des réponses périmées.

**Contrastes/thèmes et retours d'état :** viser WCAG 2.2 AA lorsque transposable, tester effectivement sur le framework retenu. Texte+icône pour réussite/alerte/échec/inconnu ; formes/patterns accessibles pour CUT/SCORE/DRAW/FOIL. Les seuils WCAG ne prouvent pas une certification d'application Windows.

## 7. Choix de la technologie UI : décision ADR préalable au gros éditeur

**Tkinter actuel = spike autonome admissible**, pas décision de moteur graphique définitif. Comparer dans le dépôt des solutions **PySide6/Qt** et **Tauri + web UI** (Avalonia uniquement si la maintenance Python/.NET est justifiée). Le benchmark doit produire une **même tranche testable** :

1. Démarrage local sans ComfyUI, hors réseau, sans IA ni nouveau serveur public ;
2. Ouvrir `.smartsvg` V1 en lecture seule (mêmes SHA, mêmes compteurs) ;
3. Afficher 12 sources synthétiques sur canevas, zoom curseur, pan et deux panneaux redimensionnables ;
4. Thèmes clair/sombre, clavier/focus, longue tâche non bloquante, 200 % d'échelle ;
5. Prototype de sauvegarde **isolé** utilisant le writer existant, sans migration V1→V2 implicite ;
6. Construction Windows hors ligne testable, analyse licences/distribution et taille mémoire.

**Matrice pondérée proposée (total 100) :** performance canevas 25, intégration sans ComfyUI/Python et données 20, accessibilité Windows 15, sécurité/offline et installabilité 15, maintenabilité 15, finition UX/animations 10. Publier mesures, limites et analyse de licence. Ne pas migrer Tkinter ni adopter des dépendances lourdes sur la base d'une maquette ; PR distincte de packaging/dépendances = approbation propriétaire interactive obligatoire.

## 8. Formation et auto-assistance (sans surcharge)

Première ouverture : 3 choix clairement visibles (Importer/Créer/Reprendre), état « sans IA », aucune création de projet implicite. Aides contextuelles progressives à la première utilisation de l'outil, mais **désactivables** et retrouvables via `?`. Galerie de projets synthétiques fournis explicitement et étiquetés exemples. Parcours novice : miniature → corriger → comprendre 4 exports → prévol → transfert manuel Design Space ; parcours expert : identités, SHA, contrôle qualité, opérations. Les tutoriels ne peuvent pas servir de preuve de compatibilité machine.

## 9. Recettes UX/UI supplémentaires : critères, pas tickets

| ID | Scénario vérifiable | Lien backlog existant | Preuve requise |
| --- | --- | --- | --- |
| **UX-01** | 100 navigations Express↔Atelier↔Fabrique : SHA projet identique, sélection stable ou erreur STALE visible | 041/046 | auto + UI Windows |
| **UX-02** | Changer vue pendant brouillon : aucun commit, retour avec brouillon ou avertissement de révocation explicite | 041/044 | auto + UI |
| **UX-03** | Panneau latéral 200–480 px, repli/retour, aucune action principale cachée à 1280×720 | 041/045/046 | Windows 100–200 % |
| **UX-04** | Sélection sujet A conserve ID canonique après tri et zoom ; panneau propriétés et canevas synchronisés | 132/133 | auto + UI |
| **UX-05** | Zoom/pan 100 fois ne change ni bytes projet ni coordonnées source ; raccourci Ctrl+0 fonctionne | 045/132 | auto + UI |
| **UX-06** | Geste add/erase aperçu → annuler = 0 écriture ; confirmer = un reçu durable ; double clic n'en crée pas deux | 035/038/044/132 | auto + Windows |
| **UX-07** | Modification dimension/alignement par champ numérique et outil, même résultat ou refus explicite | 045/133 | UI |
| **UX-08** | Activer/désactiver grille et snap n'altère pas un patron non édité | 041/133 | auto |
| **UX-09** | Charger ZIP/image volumineux : barre de progression honnête, fenêtre navigable et annulation; mémoire bornée | 019/041/047/140 | Windows CPU sans IA |
| **UX-10** | Disque plein/recovery pending/conflit : jamais badge « Enregistré » ni restauration automatique | 044/140 | fault injection + Windows |
| **UX-11** | Erreurs CUT/SCORE et inconnus compréhensibles sans couleur et avec action de correction | 045/049/133 | UI + clavier + daltonisme |
| **UX-12** | Export terminé est déclaré « fichier créé, import non vérifié » ; Undo ne prétend pas annuler une découpe | 043/044/129/130 | UI + prévol |
| **UX-13** | Thèmes clair/sombre + échelle 200 % : focus, contrastes et alertes restent lisibles | 045/046 | UI Windows |
| **UX-14** | Réduction des mouvements désactive transitions ; aucune commande ou information perdue | 045/046 | UI Windows |
| **UX-15** | 50 instances : liste et état par objet utilisables, erreurs/reprises individualisées | 047/134/135 | auto + Windows |
| **UX-16** | Temps d'affichage/navigation/mémoire p50/p95 consignés, aucun succès inventé | 019/041/140 | mesures réelles |
| **UX-17** | Projet démonstration/absence de modèle : aucune détection « réelle » ni téléchargement implicite | 042/043/050/132 | UI + réseau capturé |
| **UX-18** | Changement de thème/disposition puis réouverture : préférences locales sans mutation de `.smartsvg` | 041/046 | auto + Windows |
| **UX-19** | Contrôles clavier/lecteur d'écran de la fenêtre native, y compris erreur et action de retour | 045/046/139 | Windows a11y |
| **UX-20** | Deux frameworks sur **le même** prototype : grille de décision, SHA projet préservé, benchmarks et licences | 017/019/041/139 | ADR + Windows |

**Ne pas annoncer 20/20 PASS sur une simple CI Linux**. Preuves `SPECIFIE/IMPLEMENTE/TESTE/INTEGRE/QUALIFIE_WINDOWS` séparées par scénario, commit et plateforme. Les recettes historiques T-V34-07, T-V34-18 et T-V34-22 conservent priorité/numérotation.

## 10. Ordre d'exécution concret, sans bloquer les moteurs

| Vague | Livraison minimale visible et réversible | Dépendances | Go/no-go |
| --- | --- | --- | --- |
| **U0 — immédiatement** | Bootstrap natif + fenêtre en lecture seule, premier PNG réel et diagnostics honnêtes | #98/#99 ; #100 sous revue | CI exact HEAD, aucune dépendance obligatoire à ComfyUI |
| **U1 — réactivité** | Chargement et sélection de sources/masques sur worker, spinner et annulation, projet vérifié | 017/019/041/047/140 | UI non bloquée, sorties périmées ignorées |
| **U2 — cadre UX commun** | Shell + tokens sémantiques + thèmes + navigation et panneau propriétés dérivé | 041–046/132–133 | test aucune mutation sur navigation, 1280×720/200 % |
| **U3 — vrai atelier** | Calques/sujets et outils de retouche déjà implémentés raccordés, Undo unique, badges de sauvegarde | 032–040/044/132–133 | CAS/recovery, Undo/reload et conflit sûrs |
| **U4 — fabrique connectée** | Quatre sorties et prévol visibles, planches/patrons, guide Design Space | 043/049/129–135 | formats distincts et aucun statut machine fictif |
| **U5 — maturité** | Assistant facultatif, bibliothèque, ergonomie avancée, validation terrain et Windows installable | 047/136–140 | métriques Windows, offline, GPU si concerné, tests UX |

**Politique de parallélisation :** les tranches B exports et C patrons poursuivent leur propre progression sans attendre l'UI ; U1/U2 peuvent avancer simultanément avec leur moteur mais une seule PR micro-lot par cycle de tâche planifiée, au plus une fusion admissible par cycle. Conserver le WIP <=4. Les PR touchant `docs/**`, `.github/**`, dépendances, packaging ou gouvernance sont exclues de l'autofusion horaire et requièrent intervention propriétaire explicite.

## 11. Risques, contre-expertise et décisions encore ouvertes

- **Choix framework trop tôt :** la disponibilité de Tkinter ne suffit pas pour un éditeur moderne ; prototype comparatif avant migration lourde. **Décision ouverte**.
- **Scope creep** : préférer liens vers tickets existants ; ces critères affinent les comportements, n'augmentent pas artificiellement le backlog 140.
- **UI trompeuse** : les 12 escargots fictifs, la détection non effectuée, le statut d'export non vérifié et l'absence de profil machine restent visibles comme tels.
- **Performance** : la signature PNG et le SHA ne prouvent pas le décodage Tk rapide ; mesurer thread UI, mémoire, Unicode Windows et écran réel.
- **Sécurité** : éviter images privées dans les logs/screenshots publics ; import URL/réseau jamais implicite, zip hostile borné, modèles facultatifs contrôlés.
- **Résolution/dimensions** : aucun chiffre mm ou profil Design Space deviné depuis un PNG ; la couleur d'un trait n'implique pas CUT/SCORE.
- **Accessibilité visuelle vs réelle** : clavier/focus, lecteurs d'écran, contraste, layout étroit doivent être exécutés, pas seulement inscrits dans un document.

**Critère de fermeture de cette annexe :** référentiel de design tokens, galerie des composants et ADR UI produits et reliés à des tests, puis première tranche Windows validée. La rédaction seule ne qualifie aucune fonctionnalité.