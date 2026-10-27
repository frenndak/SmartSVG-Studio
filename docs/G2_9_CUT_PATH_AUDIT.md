# G2.9 — Contre-expertise des contours et de l'intégration UX

## Défaillance confirmée avant correction

Le lot G2.7 acceptait comme « chemin SVG candidat à la découpe » des chaînes de commandes contenant un `M`, un segment et un `Z` final sans vérifier la grammaire complète ni la surface géométrique. Ainsi un tracé ouvert suivi d'une fermeture artificielle, un second sous-tracé non fermé, une commande sans coordonnées suffisantes ou un triangle collinéaire pouvait être sérialisé dans un nouveau SVG.

## Correction candidate

- Analyse déterministe bornée des commandes SVG `M/L/H/V/C/S/Q/T/A/Z`, paramètres obligatoires, nombres finis et limites d'amplitude.
- Contrôle de fermeture **de chaque sous-tracé**, refus des boucles uniquement linéaires à aire nulle, bornes non dégénérées pour les autres types, vérification des drapeaux d'arcs.
- Rejet des chemins dont l'enveloppe géométrique connue dépasse le `viewBox` ; évite un export visuellement tronqué. Pour les courbes, les points de contrôle sont utilisés dans une borne conservative : certains dessins pourtant valides peuvent nécessiter une normalisation manuelle avant d'être acceptés.
- Le sérialiseur SVG valide à nouveau les tracés des éléments sélectionnés, même s'il est appelé indépendamment de l'inspecteur.
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
