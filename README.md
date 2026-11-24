# SmartSVG Studio — atelier créatif local pour Cricut

**Dépôt public de développement**, basé sur le moteur ComfyUI SmartSVG. Objectif : passer d'une image à une planche de sujets et à des fichiers de découpe / impression préparés pour être vérifiés dans Cricut Design Space.

> **Roadmap active : V3.5.** L'avancement réel se vérifie dans [les PR et CI GitHub](https://github.com/frenndak/SmartSVG-Studio/pulls), sur le SHA courant de `main`, et dans [le plan de livraison](docs/roadmap-v3.5/DELIVERY_EXECUTION_PLAN.md). Le [bilan du 17 novembre](docs/roadmap-v3.5/ENGINEERING_STATUS_2026_11_17.md) et l'Alpha ZIP du 14 novembre sont des **photographies historiques**, non une preuve du binaire actuel. Les quatre exports, les essais sur Windows utilisateur, Design Space, RTX 3070 et la coupe Explore 5 ont chacun leur propre statut. **Aucune certification Cricut n'est revendiquée.**

📋 [Bilans historiques et statut](docs/ETAT_ACTUEL_SMARTSVG.md) · 🗺️ **[Roadmap V3.5 active](docs/roadmap-v3.5/README.md)** · **[État d'ingénierie au 17/11](docs/roadmap-v3.5/ENGINEERING_STATUS_2026_11_17.md)** · **[Ordre priorisé W00–W16](docs/roadmap-v3.5/MASTER_PRIORISE.md)** · [Ancienne V3.4](docs/roadmap-v3.4/README.md) · [Héritage V3.3](docs/ROADMAP_MASTER_v3_3.md) · [V3.2 archivée](docs/ROADMAP_MASTER_v3_2.md)

## Avancées natives récentes (17 novembre 2026)

- **Atelier natif :** gestion d'un sujet vérifié, pinceau/multizones, aperçu, sauvegarde, annulation/rétablissement, isolation d'un sujet voisin. PR [#139](https://github.com/frenndak/SmartSVG-Studio/pull/139) et [#155–160](https://github.com/frenndak/SmartSVG-Studio/pull/160).
- **Validation automatisée :** [G0 post-fusion de #160](https://github.com/frenndak/SmartSVG-Studio/actions/runs/44161000593) SUCCESS ; tests CPU ciblés pinceau **55/55 PASS** dans cette PR. Windows runner qualifie des scénarios ciblés, pas un usage réel sur PC/Cricut.
- **Distribution :** [Alpha portable Windows](https://github.com/frenndak/SmartSVG-Studio/actions/runs/43621278755) construite et testée le 14 novembre, **antérieure** aux retouches les plus récentes ; aucune Release officielle ni certification Cricut.
- **Suite :** clore le WIP courant vérifié dans GitHub, puis qualifier un parcours complet PNG → sujet manuel → retouche → sauvegarde/réouverture → export typé relu sur Windows. Voir le [plan A0–C](docs/roadmap-v3.5/DELIVERY_EXECUTION_PLAN.md) et le [protocole matériel](docs/roadmap-v3.5/CALIBRATION_PROTOCOL.md).

## Inventaire historique du moteur et du prototype (photographie du 6 novembre)

> Les lignes de cette ancienne matrice sont conservées pour la provenance. Elles **ne décrivent pas intégralement le `main` actuel** après les PR V3.5.

| Domaine | Implémentation intégrée | Validation restant à faire |
| --- | --- | --- |
| Bureau autonome | Fenêtre commune, création PNG et première sauvegarde/relecture V1, lecteur/aperçu PNG, gabarits théoriques et thèmes | Mise à jour/recovery, Atelier, exports natifs ; distribution Windows |
| Projets `.smartsvg` (G1.3–G2.4) | Contrats, archives durcies, sauvegarde atomique avec secours, session d'édition et snapshots de masques float32 | E2E du panneau dans ComfyUI Windows, gros projets/photos |
| Express guidé (G1.5–G2.5) | Choix du mode, panneaux de projets, état de traitement, garde-fous avant export | Vérifier le parcours complet pour novice |
| Masques / retouches (G2.6–G2.8) | Inspecteur de fragments, focus dans l'éditeur, brouillons locaux récupérables | Ergonomie navigateur et inférence réelle |
| Contrôle SVG (G2.7/G2.9) | Grammaire des chemins, filtrage XML, contrôle mm/viewBox, sélection de chemins et **brouillon SVG local** | Vérifier les cas géométriques complexes et l'import Design Space |
| Atelier plein écran (G3.0–G3.2) | Interface responsive avec 12 escargots **fictifs**, accès volontaire au véritable inspecteur SVG et au gestionnaire `.smartsvg` natif (création PNG uniquement), lorsque l'interface est servie par ComfyUI | Raccorder vrais sujets, détourage et retouches à l'écran ; valider les modules Windows/ComfyUI |
| Qualité et intégration | Tests G0, CPU, précontrôle de PR en lecture seule, vérification des sources d'origine | Recette Windows/GPU/Explore 5 et mesures de découpe |

**Important :** la planche de 12 escargots dans le nouvel atelier est une démonstration d'ergonomie. Importer un PNG/JPEG/WebP dans ce prototype **n'effectue pas encore une segmentation IA** et **n'exporte pas de résultat vectorisé**. Le bouton G3.1 ouvre un contrôleur SVG réel **pour un fichier déjà existant** ; le bouton G3.2 donne accès au gestionnaire de projets `.smartsvg` **avec import PNG uniquement**, sous ComfyUI.

## Voir l'interface

**Prototype bureau, avec Python et Tkinter disponibles :**

```bash
python engine/standalone_desktop_v34.py
python -I -S engine/standalone_desktop_v34.py --probe
```

Le premier lance la fenêtre autonome locale, le second contrôle les imports sans ouvrir de fenêtre. Ce n'est pas encore un installateur ; les projets existants restent en lecture seule et la Fabrique n'exporte pas. La création PNG est une action explicite : [parcours et limites](docs/NATIVE_PNG_CREATE_V34.md). Voir [le parcours de réalisation prioritaire](docs/roadmap-v3.4/EXECUTION_ET_INTEGRATION_2026_11_06.md).

Dépendances et reproductibilité : [profil du socle natif](docs/NATIVE_RUNTIME_V34.md).

**Interface web historique / démonstration :**

Ouvrir `engine/web/js/smartsvg_express_atelier_preview.html` dans un navigateur pour tester la **maquette locale** sans GPU. On peut y naviguer, sélectionner les 12 exemples et prévisualiser un PNG/JPEG/WebP sans envoi.

Pour **inspecter réellement un SVG**, utiliser l'installation ComfyUI et ouvrir l'Atelier depuis le panneau Express, puis sélectionner « Examiner un vrai SVG de contours ». Le navigateur doit charger les modules de l'extension depuis le même serveur HTTP ; ce chargement **n'est pas garanti en `file://` ou via un proxy HTML tiers**. Voir [la procédure et les limites G3.1](docs/G3_1_EXPRESS_REAL_SVG_REVIEW.md). Pour créer ou ouvrir un projet, cliquer ensuite **Gérer mes projets .smartsvg** : voir [le contrat G3.2](docs/G3_2_ATELIER_NATIVE_PROJECTS.md). Ne pas importer de fichiers personnels dans des visualiseurs publics.

## Source historique vérifiée

- Archive figée : `source-releases/ComfyUI_SmartSVG_Studio_V21_15_2_Installation.zip`.
- SHA-256 attendu : `9369656f0216cebb6dccce0d0155bffa16d8c384da6a984bf848cdd8aa003c54`.
- Manifeste V21.15.2 : **651 empreintes internes**, conservées et testées par CI.
- La roadmap **active** est la [V3.5](docs/roadmap-v3.5/README.md), adoptée par [promotion contrôlée](docs/ROADMAP_PROMOTION_v3_5.md), avec les 141 exigences V3.3, 140 tickets V3.4, 24 lots, 80 capacités UX et 437 scénarios historiques préservés ([état d'exécution](docs/roadmap-v3.5/EXECUTION_STATE.json)). V3.4/V3.3/V3.2 restent archivées ; une roadmap décrit l'objectif, **pas le nombre de fonctions déjà achevées**.

## Vérifications reproductibles

```bash
python tools/verify_source_integrity.py --repo . --archive-only
python -m unittest discover -s tests -p 'test_*.py' -q
node --test engine/tests/test_g27_cut_review.mjs engine/tests/test_g29_path_grammar.mjs
```

Les contrôles historiques Python, JavaScript et dépendances CPU/GPU complètes peuvent demander une installation supplémentaire. Les CI de PR Linux valident du **code**, pas la fiabilité d'une fabrication réelle.

## Automatisation et sécurité

Les GitHub Actions publiques incluent des contrôles **lecture seule**. Les deux tâches SmartSVG V3.5 **A (développement, H:55) et B (QA/intégration, H:25)** suivent le contrat R13 après readback effectif ; B est le seul exécuteur autorisé des squash code admissibles, au plus un par cycle. La tâche séparée de conception reste suspendue. Leurs états effectifs se relisent dans le service d'automatisation, jamais depuis cette page. Les GitHub Actions complémentaires de développement privé qui réclament une clé ou un budget optionnel restent distinctes : **aucun appel payant ni installation externe n'est obligatoire pour consulter le dépôt ou ouvrir l'aperçu**. Les conditions de fusion sont celles du [contrat courant AGENTS.md](AGENTS.md), relu sur `main` : autorisation applicable, éligibilité du lot, revue indépendante et contrôles du candidat exact. Cette documentation ne crée ni n'active de tâche et ne modifie aucune autorisation.

Ne jamais commiter de clé API, image personnelle, poids de modèle soumis à restriction ou artefact de fabrication confidentiel dans ce dépôt public.
