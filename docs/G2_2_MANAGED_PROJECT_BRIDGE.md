# SmartSVG G2.2 — Projets locaux gérés depuis Express (premier pont fonctionnel)

Dépendances : PR #14 G1.2 → #15 G1.3 → #16 G1.4 → #17 G1.5 → #18 G2.1. La V21.15.2 historique n'est pas modifiée.

## Ce qui fonctionne

Depuis le sous-panneau Projet .smartsvg du nœud Express :
1. Sélectionner explicitement un PNG local et donner un nom de projet limité aux lettres, chiffres, tirets et soulignements.
2. Créer un conteneur .smartsvg versionné dans le dossier de sortie de ComfyUI.
3. Ouvrir et inspecter le projet : empreintes SHA-256, aperçu source, métadonnées et notes.
4. Mettre à jour les notes avec contrôle d'une empreinte de révision et sauvegarde de secours atomique.
5. Restaurer explicitement la version précédente après confirmation uniquement lorsque la principale est absente ou invalide.

**Limite importante :** l'archive initiale sauvegarde le PNG source, les métadonnées et les notes. L'ouverture ne reconnecte pas encore IMAGE dans ComfyUI et ne rétablit ni les retouches, ni les masques, ni le graphe. Aucun objet exporté n'est déclaré compatible ou certifié pour Cricut. Il s'agit du premier pont de stockage, pas d'une restauration complète d'édition.

## Activation sécurisée

L'API de projets est désactivée par défaut. Pour une installation ComfyUI locale et autorisée, définir la variable d'environnement SMARTSVG_ENABLE_PROJECT_API=1 avant de lancer ComfyUI et redémarrer. **Ne pas activer sur un ComfyUI exposé sans authentification ou utilisé par plusieurs personnes sans cloisonnement.**

L'interface demeure visible si le service est inactif mais affiche une indisponibilité explicite lors d'une action. Les anciens exports restent opérationnels.

## Dossier et protocole

Stockage uniquement dans output/SmartSVG_Managed_Projects (dossier dérivé de folder_paths.get_output_directory côté serveur). Fichiers mon_projet.smartsvg, mon_projet.previous.smartsvg et mon_projet.smartsvg.lock. Aucun chemin client arbitraire accepté ; protection symlink, absence d'extraction ZIP, empreintes et validations G1.3/G1.4. Image limitée au PNG, 12 Mo et 20 mégapixels, avec contrôle strict PNG sans dépendance externe : format non entrelacé 8 bits L/RGB/RGBA, CRC des chunks, filtres de lignes et décompression zlib bornée. Les variantes PNG non prises en charge sont refusées (pas de garantie de rendu complet des métadonnées).

Endpoints optionnels :
- GET /smartsvg/g22/projects : liste bornée des projets.
- GET /smartsvg/g22/project?name=... : état vérifié, métadonnées, empreintes.
- GET /smartsvg/g22/source?name=... : PNG source conservé.
- POST /smartsvg/g22/create : formulaire d'import source.
- POST /smartsvg/g22/notes : révision des notes, fingerprint attendu.
- POST /smartsvg/g22/restore : récupération confirmée et fingerprint du secours.

Les POST exigent X-SmartSVG-UI: 1 et rejettent un Origin différent du Host. Cela contribue à la protection CSRF mais **ne constitue pas une authentification**. Le niveau de protection effectif dépend de ComfyUI, de son proxy et des permissions du système de fichiers.

## Tests et limitations

Tests Python sur PNG synthétiques, aller-retour exact, modification de notes, copie précédente, corruption, récupérations, refus d'écrasement, symlinks, formats refusés et garde anti-mauvais noms. Tests Node.js sur les requêtes UI, sélection explicite du PNG, l'empreinte de révision et la confirmation de récupération.

Pas de preuve d'exécution Windows, GPU RTX 3070, Design Space, coupe Explore 5, isolation multi-utilisateurs ni récupération du graphe éditable.

## Étape suivante

Relier les images et masques effectivement traités par le nœud ComfyUI au conteneur .smartsvg, puis rétablir les corrections dans l'éditeur. Vérifier la séparation des accès avant toute activation à distance.
