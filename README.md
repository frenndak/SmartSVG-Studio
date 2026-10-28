# SmartSVG Studio — atelier créatif local pour Cricut

**Dépôt public de développement**, basé sur le moteur ComfyUI SmartSVG. Objectif : passer d'une image à une planche de sujets et à des fichiers de découpe / impression préparés pour être vérifiés dans Cricut Design Space.

> **Statut au 27 octobre 2026 : prototype logiciel consolidé, pas de version Cricut certifiée.** Les bibliothèques, interfaces et tests G1/G2/G3.1/G3.2 sont présents dans `main`. La qualité du détourage IA sur les images de référence, la compatibilité Windows/RTX 3070 et la découpe physique Explore 5 attendent une recette réelle.

📋 **[Voir l'état précis des fonctions et les prochaines étapes](docs/ETAT_ACTUEL_SMARTSVG.md)** · 🗺️ **[Roadmap maître V3.3 active](docs/ROADMAP_MASTER_v3_3.md)** · 📦 [V3.2 historique](docs/ROADMAP_MASTER_v3_2.md) · 🧪 **[État du regroupement G1/G2 (archive historique du processus)](docs/INTEGRATION_CANDIDATE_2026_10_27.md)**

## Ce qui est disponible dans le code

| Domaine | Implémentation intégrée | Validation restant à faire |
| --- | --- | --- |
| Projets `.smartsvg` (G1.3–G2.4) | Contrats, archives durcies, sauvegarde atomique avec secours, session d'édition et snapshots de masques float32 | E2E du panneau dans ComfyUI Windows, gros projets/photos |
| Express guidé (G1.5–G2.5) | Choix du mode, panneaux de projets, état de traitement, garde-fous avant export | Vérifier le parcours complet pour novice |
| Masques / retouches (G2.6–G2.8) | Inspecteur de fragments, focus dans l'éditeur, brouillons locaux récupérables | Ergonomie navigateur et inférence réelle |
| Contrôle SVG (G2.7/G2.9) | Grammaire des chemins, filtrage XML, contrôle mm/viewBox, sélection de chemins et **brouillon SVG local** | Vérifier les cas géométriques complexes et l'import Design Space |
| Atelier plein écran (G3.0–G3.2) | Interface responsive avec 12 escargots **fictifs**, accès volontaire au véritable inspecteur SVG et au gestionnaire `.smartsvg` natif (création PNG uniquement), lorsque l'interface est servie par ComfyUI | Raccorder vrais sujets, détourage et retouches à l'écran ; valider les modules Windows/ComfyUI |
| Qualité et intégration | Tests G0, CPU, précontrôle de PR en lecture seule, vérification des sources d'origine | Recette Windows/GPU/Explore 5 et mesures de découpe |

**Important :** la planche de 12 escargots dans le nouvel atelier est une démonstration d'ergonomie. Importer un PNG/JPEG/WebP dans ce prototype **n'effectue pas encore une segmentation IA** et **n'exporte pas de résultat vectorisé**. Le bouton G3.1 ouvre un contrôleur SVG réel **pour un fichier déjà existant** ; le bouton G3.2 donne accès au gestionnaire de projets `.smartsvg` **avec import PNG uniquement**, sous ComfyUI.

## Voir l'interface

Ouvrir `engine/web/js/smartsvg_express_atelier_preview.html` dans un navigateur pour tester la **maquette locale** sans GPU. On peut y naviguer, sélectionner les 12 exemples et prévisualiser un PNG/JPEG/WebP sans envoi.

Pour **inspecter réellement un SVG**, utiliser l'installation ComfyUI et ouvrir l'Atelier depuis le panneau Express, puis sélectionner « Examiner un vrai SVG de contours ». Le navigateur doit charger les modules de l'extension depuis le même serveur HTTP ; ce chargement **n'est pas garanti en `file://` ou via un proxy HTML tiers**. Voir [la procédure et les limites G3.1](docs/G3_1_EXPRESS_REAL_SVG_REVIEW.md). Pour créer ou ouvrir un projet, cliquer ensuite **Gérer mes projets .smartsvg** : voir [le contrat G3.2](docs/G3_2_ATELIER_NATIVE_PROJECTS.md). Ne pas importer de fichiers personnels dans des visualiseurs publics.

## Source historique vérifiée

- Archive figée : `source-releases/ComfyUI_SmartSVG_Studio_V21_15_2_Installation.zip`.
- SHA-256 attendu : `9369656f0216cebb6dccce0d0155bffa16d8c384da6a984bf848cdd8aa003c54`.
- Manifeste V21.15.2 : **651 empreintes internes**, conservées et testées par CI.
- La roadmap **active** est `docs/ROADMAP_MASTER_v3_3.md` (141 exigences, [traçabilité](docs/ROADMAP_TRACEABILITY_v3_3.md) et [couverture](docs/ROADMAP_COVERAGE_v3_3.md)). La V3.2 originale reste **figée et archivée** ; une roadmap décrit l'objectif, **pas la liste de fonctions déjà achevées**.

## Vérifications reproductibles

```bash
python tools/verify_source_integrity.py --repo . --archive-only
python -m unittest discover -s tests -p 'test_*.py' -q
node --test engine/tests/test_g27_cut_review.mjs engine/tests/test_g29_path_grammar.mjs
```

Les contrôles historiques Python, JavaScript et dépendances CPU/GPU complètes peuvent demander une installation supplémentaire. Les CI de PR Linux valident du **code**, pas la fiabilité d'une fabrication réelle.

## Automatisation et sécurité

Les GitHub Actions publiques incluent des contrôles **lecture seule**. La tâche Codex optionnelle nécessiterait des variables et un secret API renseignés volontairement, ainsi qu'un budget déclaré et un plafond quotidien ; **aucun appel payant n'est une condition pour consulter le dépôt ou ouvrir l'aperçu**. Les tâches autonomes ne fusionnent pas de PR ; dans une session explicitement autorisée par le propriétaire, l'assistant peut fusionner uniquement après contre-expertise documentée et tests pertinents.

Ne jamais commiter de clé API, image personnelle, poids de modèle soumis à restriction ou artefact de fabrication confidentiel dans ce dépôt public.
