# G2.9 — Contre-expertise des contours et de l'intégration UX

## Défaillance confirmée avant correction

Le lot G2.7 acceptait comme « chemin SVG candidat à la découpe » des chaînes de commandes contenant un `M`, un segment et un `Z` final sans vérifier la grammaire complète ni la surface géométrique. Ainsi un tracé ouvert suivi d'une fermeture artificielle, un second sous-tracé non fermé, une commande sans coordonnées suffisantes ou un triangle collinéaire pouvait être sérialisé dans un nouveau SVG.

## Correction candidate

- Analyse déterministe bornée des commandes SVG `M/L/H/V/C/S/Q/T/A/Z`, paramètres obligatoires, nombres finis et limites d'amplitude. Les arcs de rayon nul sont traités comme des segments droits, conformément à leur effet géométrique ; ils ne doivent pas simuler une forme à surface non nulle.
- Contrôle de fermeture **de chaque sous-tracé**, refus des boucles uniquement linéaires à aire nulle, rejet des Bézier dont tous les points de contrôle sont collinéaires, bornes non dégénérées pour les autres types, vérification des drapeaux d'arcs.
- Rejet des chemins dont l'enveloppe géométrique connue dépasse le `viewBox` ; évite un export visuellement tronqué. Pour les courbes, les points de contrôle sont utilisés dans une borne conservative : certains dessins pourtant valides peuvent nécessiter une normalisation manuelle avant d'être acceptés.
- Le sérialiseur SVG valide à nouveau les tracés **et les limites du viewBox** des éléments sélectionnés, même s'il est appelé indépendamment de l'inspecteur.
- Tests de non-régression sur les chemins incomplets/ouverts, les boucles nulles, les formes composites et le clipping.
- **Pas de certification de géométrie Cricut** : intersections de courbes, épaisseurs physiques, tolérance de la lame, inflexions Bézier et résultats Design Space ne sont pas déduits du parsing statique.

## Diagnostic transversal du dépôt au 27 octobre 2026

### Bloqueurs et risques

1. **Synchronisation des PR empilées** — la PR #16 G1.4 est en retard sur la #15 G1.3, qui a continué à recevoir des corrections JPEG/WebP/ZIP. Il faut resynchroniser et rejouer les tests sur la pile réellement destinée à main, sans écraser les modules existants. Les PR #20/#21 et #23/#24 représentent des alternatives concurrentes, pas deux versions cumulatives.
2. **Brouillons locaux G2.8** — la reprise des strokes V21.6 est fonctionnelle en simulation et liée à l'empreinte de source. Elle n'est pas un autosave complet de `.smartsvg`, ne transfère pas les images/masques, et dépend du stockage du navigateur.
3. **UX Express** — G2.7 est ajouté sous un panneau `details` du nœud Express de ComfyUI ; on ne peut pas dire que l'application autonome, l'importation sans graphe ou la restauration du graphe soient livrés.
4. **Sécurité des fichiers** — import source PNG/ZIP/JPEG/WebP plus robuste en G1.3, mais le décodage réel JPEG/WebP, la rotation EXIF, la gestion colorimétrique et les images smartphone à grande taille restent à qualifier.
5. **Précontrôle découpe** — #25 et #31 sont indépendants de G2.7. Le résultat du précontrôle local statique ne remplace ni leur intégration ni les essais Cricut.
6. **Visuel et ergonomie** — l'aperçu Canvas par chemins individualisés ne segmente pas une image bitmap et ne recrée pas des calques éditables. Les essais navigateur sur Windows à 1366×768, interactions tactiles/clavier, lisibilité, contraste et lecteur d'écran ne sont pas encore certifiés.
7. **Exploitation** — le dépôt public est **volontaire** ; ne pas le privativer. La PR #30 d'automatisation publique reste non fusionnée. Le contenu de `AGENTS.md` dans main affiche encore « private repository » (documentation obsolète), mais ce document protégé doit être mis à jour par le processus d'intégration gouverné, pas par une automatisation libre.
8. **Traçabilité** — les CI décrites dans les PR tournent principalement sur des commits de fusion synthétique. Les preuves Windows, RTX 3070, import Design Space et découpes physiques doivent être obtenues avant tout statut de fabrication validé.

### Ordre conseillé

**P0** corriger la grammaire des chemins (ce lot) ; qualifier l'exactitude des dimensions/couleurs et refuser les faux « prêts pour découpe ». **P0** intégrer séquentiellement la pile G1.3→G2.8 en distinguant alternatives G2.3/G2.5 ; porter les correctifs indépendants #25/#31 et le scénario d'inspection #26–#28 avec résolution des conflits. **P1** joindre sélection SVG, sujets, masques et retouches par identifiants stables ; améliorer autosave complet, reprise du graphe et parcours Express sans nœuds ; puis recette navigateur et coupe réelle.

Ne pas modifier `docs/ROADMAP_MASTER_v3_2.md` ; tout élargissement de portée relève d'une nouvelle décision de roadmap, pas d'un amendement silencieux.

## Matrice de sévérité et critères GO / NO GO

| Priorité | Constat | Preuve actuelle | Condition d'acceptation |
| --- | --- | --- | --- |
| **P0 bloquant export** | Fermeture fictive, commande de tracé malformée, aire nulle ou contour masqué par débordement du viewBox | Défaut G2.7 identifié puis corrections G2.9 + tests ciblés | Nouveau HEAD CI vert, tests négatifs de forme et bornes, revue indépendante |
| **P0 bloquant intégration** | Décalage de versions G1.3 → G1.4 et chaîne G2 ; alternatives #20/#21 et #23/#24 | `compare_commits` indique G1.4 derrière G1.3 ; 19 PR ouvertes au moment de l'audit | Choix explicite d'une variante par lot, réconciliation sans perte, CI sur pile d'intégration |
| **P0 fabrication** | Pas de test matériel Design Space/Explore 5 ni Windows ComfyUI RTX 3070 | Les journaux G0/CPU déclarent des tests synthétiques | Matrice réelle : 12 escargots, 24 illustrations, sticker Print Then Cut et SVG Basic Cut, dimensions mm et tolérance de coupe mesurées |
| **P1 sauvegarde** | G2.8 autoenregistre des coups de pinceau locaux, pas toute l'archive ou les masques | Modules G2.8/G2.4 distincts, reprise du graphe manuelle | Crash-tests rechargement projet source + masques + strokes et reprise des liens ComfyUI |
| **P1 qualité d'entrée** | Photos JPEG/WebP ne sont pas intégrées au parcours de création de projet Express G2.2 (PNG seul) | Champ de fichier UI `accept='image/png'` | Importer normalisé : EXIF, rotations, alpha, espace couleur, erreurs de décodeur et photos > budget |
| **P1 UX** | Clic de sélection Canvas et états responsive testés en DOM simulé, pas dans navigateur de production | Tests Node.js, aucun essai interactif attesté sur Windows | Recette souris/clavier/lecteur d'écran, 1366×768 et 1920×1080, 12/24 objets, conflits et erreurs |
| **P1 performances** | Chaque rafraîchissement de la sélection G2.7 reconstruit actuellement jusqu'à 64 objets Path2D | Lecture `smartsvg_cut_review_panel_g27.mjs` | Cache par signature du fichier, 24/64 chemins sans gel UI, bornage temps/mémoire |
| **P2 confort** | Dossier de sortie global, import de photos et création non technique de bout en bout restent incomplets | Documents de roadmap et branches Express | Paramètres utilisateur stables, prévisualisation avant exécution et export réellement vérifiable |

### Protocole de contre-vérification

- **Sources et invariants** : comparer les 651 empreintes de l'archive historique, vérifier que les fichiers de roadmap figée et IDs de nœuds n'ont pas changé.
- **Tests automatiques** : admission Python et JS, scénarios d'attaque XML/SVG, chemins multi-sujets 12/24, défauts de syntaxe, clip et sauvegarde atomique.
- **Tests d'intégration** : charger la pile réellement réconciliée, vérifier que les cinq expériences coexistent dans une seule installation ComfyUI.
- **Tests utilisateur** : importer une photo smartphone, reprendre un projet après fermeture imprévue, dessiner/annuler/rétablir, sélectionner une planche, visualiser la découpe.
- **Essais de fabrication** : mesurer les dimensions réelles A4/Print Then Cut et SVG Basic Cut après import Design Space et découpe Explore 5.
- **Communication** : ne jamais annoncer « prêt Cricut », « vectorisé intégralement » ou « récupération complète » sans preuves correspondant précisément à la fonctionnalité.

**Aucune fusion ni certification matérielle n'est autorisée par ce rapport.** Le dépôt public SmartSVG-Studio est le choix déclaré de l'utilisateur.
