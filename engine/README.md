# SmartSVG Studio V21.5 — Interface visuelle

**Démarrer ici : [README_V21_5.md](README_V21_5.md).** La V21.5 ajoute un panneau de contrôle de résultats directement au nœud Express ComfyUI. Pour les versions antérieures, consulter les sections archivées ci-dessous.

---

# SmartSVG Studio V21.3.1

**Commencer ici :** [README_V21_3_1.md](README_V21_3_1.md). Rapport d'audit : [AUDIT_V21_3_1_MULTIPASSES.md](AUDIT_V21_3_1_MULTIPASSES.md).

Les anciennes versions sont archivées ci-dessous pour compatibilité.

---

# SmartSVG Studio V20.0 — Version consolidée

**Guide actuel : [`README_V20.md`](README_V20.md).** Les sections ci-dessous sont conservées pour l’historique.

---

# SmartSVG Studio V19.8 — Appariement des masques entre modèles

**Nouveautés et procédure : voir [`V19_8_README.md`](V19_8_README.md).**

Tous les moteurs Cricut antérieurs et leurs workflows sont préservés. Le nœud V19.8 compare les masques provenant de modèles externes sans les générer lui-même.

---

# SmartSVG Studio V19.7.1 — Profiler CPU/GPU corrigé

**Statut : bêta instrumentée.** Cette version reprend le moteur de production de V19.6 sans modifier ses exports Cricut. Elle ajoute un **profil facultatif d'exécution** pour les opérations réellement lancées **dans le nœud SmartSVG** : Florence-2, SAM2, RMBG, comparaison de masques, export photo et transformation vectorielle d'une planche.

## Installation ComfyUI sous Windows

1. Fermer ComfyUI, sauvegarder `ComfyUI-SmartSVG-Studio-V19.6` puis déplacer toutes les anciennes versions SmartSVG **hors de `custom_nodes`**.
2. Extraire entièrement `ComfyUI-SmartSVG-Studio-V19.7` dans le dossier `custom_nodes` **de la bonne installation** ComfyUI. Laisser les sous-dossiers `tests` et `example_workflows` intacts.
3. Conserver **ComfyUI-RMBG** pour utiliser les modèles déjà installés. Aucun modèle nouveau n'est téléchargé par le profiler V19.7. Ne pas réinstaller PyTorch/CUDA sans besoin.
4. Redémarrer ComfyUI puis ouvrir `example_workflows/SmartSVG_Studio_V19_7_Express.json` ou `..._Expert.json`.
5. Choisir une image ou planche, un **seul dossier global de sortie**, et `profil_performances = activer`. Lancer `Queue Prompt`.
6. Ouvrir le dossier de sortie. Les exports restent rangés dans un sous-dossier `SmartSVG_...` et le rapport de performances est enregistré **à côté** sous le nom `PERFORMANCES_V19_7_<id>.json` ; le chemin apparaît également dans le retour texte du nœud.

`profil_performances = desactiver` ne crée aucun fichier de télémétrie ni synchronisation GPU supplémentaire.

## Quelles données sont réellement mesurées ?

- Durée murale en secondes pour le **traitement total SmartSVG** et, si ces étapes ont été exécutées en interne, Florence-2, SAM2, RMBG, comparaison de masques, export photo, ou préparation d'une planche vectorielle.
- Avant / après : mémoire PyTorch allouée, réservée, mémoire libre globale du GPU. Les mesures sont disponibles seulement si `torch.cuda.is_available()` et l'API CUDA répondent.
- Pic `max_memory_allocated()` historique **du processus ComfyUI** (pas le pic isolé du modèle ou de l'étape). Le profiler **ne réinitialise jamais** les statistiques de mémoire GPU d'autres nœuds.
- Nombre de masques acceptés par SAM2 (lorsque disponible), avec un temps *moyen amorti* : ce n'est **pas** une mesure du coût par objet individuel.
- En cas d'erreur de l'IA ou de l'export, un fichier JSON de diagnostic peut être produit avec l'étape et une description bornée, puis l'exception initiale est propagée.

**Limites importantes :** les opérations de nœuds **externes** (SAM2/FeyNoBg/Finegrain exécutés avant le nœud SmartSVG) ne sont pas chronométrées. Le `MASK` entrant est déjà calculé et son coût n'est pas récupérable rétroactivement. Pour comparer le temps réel des modèles, les exécuter l'un après l'autre dans le moteur SmartSVG ou mesurer chaque nœud indépendamment, avec une instrumentation dédiée. La synchronisation CUDA peut augmenter légèrement les durées relevées. La mémoire PyTorch ne comptabilise pas forcément tous les allocateurs tiers.

## Utiliser les modèles sur une RTX 3070 de 8 Go

1. Démarrer sur **une seule image**, `analyse_florence=auto` et `segmentation_objets=auto`, puis relever `PERFORMANCES_V19_7_*.json`.
2. Répéter la même image et le même modèle **plusieurs fois** ; comparer des exécutions à froid et après chargement en mémoire est trompeur.
3. Ne pas charger en même temps plusieurs modèles lourds sur 8 Go de VRAM. Surveiller les avertissements CUDA et la mémoire libre.
4. Pour comparer **la qualité des masques**, utiliser le comparateur V19.6 avec un masque annoté, lorsque disponible. Ses scores heuristiques ne valent pas une annotation.
5. Si un modèle est absent ou incompatible, conserver le mode diagnostic, puis lire les erreurs : **ne jamais annoncer un objet détouré sans vrai masque**.

## Cricut Design Space — mêmes fichiers que V19.6

- PNG transparent fidèle à l'image d'origine pour réutilisation/montage ; PNG à sous-couche blanche et marge pour tester `Imprimer puis découper`.
- Contrôler les contours et les dimensions dans Design Space ; ne pas superposer le SVG de contours à un PNG imprimable.
- `Aplatir` les SVG multicouches avant de les imprimer. La découpe physique n'est pas certifiée par des tests logiciels.
- Aucun fichier produit par V19.7 ne remplace les SVG ou PNG de V19.6 par une image issue du diagnostic.

## Tests

Lancer avec l'environnement Python de ComfyUI :

```powershell
python verify_package.py
```

Les tests incluent une exécution **réelle du code export photo** avec un masque de synthèse, une comparaison des SHA-256 avant/après instrumentation, des simulations CUDA et les tests historiques. **Aucun test ne prétend avoir exécuté les vrais modèles IA sur la RTX 3070**.

### Références de mesure PyTorch

- https://docs.pytorch.org/docs/stable/notes/cuda
- https://docs.pytorch.org/docs/stable/generated/torch.cuda.memory.mem_get_info.html
- https://docs.pytorch.org/docs/stable/generated/torch.cuda.synchronize.html

## Mise à jour V19.7.1 — Contre-expertise et corrections

La V19.7.1 remplace le profiler V19.7 **sans modifier les fichiers de découpe ni la segmentation**. Charger en priorité `example_workflows/SmartSVG_Studio_V19_7_1_Express.json` ou `..._Expert.json`. Les workflows V19.7 précédents restent reconnus si l'ancienne extension a été retirée de `custom_nodes`.

**Interprétation du nouveau rapport :**
- `chronometrage_gpu_synchronise` est `true` seulement si les synchronisations PyTorch ont réellement réussi **avant et après**, sur le même GPU. Si false, la durée est quand même mesurée en temps écoulé CPU, mais ne doit pas servir à comparer les temps GPU.
- `synchronisation_cuda_echouee_etapes` énumère les étapes qui n'ont pas pu être synchronisées. Ne jamais interpréter `mesure_gpu_reelle_observee=true` comme la preuve d'une vraie inférence de SAM2.
- `captures_gpu_partielles_etapes` signale qu'une statistique GPU manque alors que d'autres sont disponibles. Examiner `mesures_indisponibles` dans la capture concernée.
- `rss_processus_avant_bytes` et `rss_processus_apres_bytes` sont facultatifs. Ils reflètent la RAM **totale du processus ComfyUI**, pas celle du modèle seul ; ils ne sont pas disponibles sans psutil.
- `secondes_exclusives_approximatives` et `durees_exclusives_approximatives_s` retranchent les durées des sous-étapes imbriquées. Le coût de mesure et de synchronisation peut rester inclus : ce ne sont pas des temps de calcul pur.
- Le fichier de sortie conserve **par compatibilité** le préfixe `PERFORMANCES_V19_7_...json`, mais son contenu porte `version: 19.7.1-beta`.
- Un échec d'écriture du fichier de diagnostic est affiché en avertissement dans le texte de sortie ; les PNG et SVG de production restent conservés.

**Validation :** tests locaux et simulation CUDA, non pas essais réels sur RTX 3070 ou Cricut. La précision des contours n'a pas été réévaluée faute de masques IA produits sur ta machine. L'installation de cette version n'est pas indispensable pour poursuivre le travail de détourage si la V19.7 fonctionne déjà ; elle est recommandée pour mesurer sans confondre les valeurs GPU.

## V19.9 — Second passage local cible (RTX 3070 8 Go)

Nouveau noeud `SmartSVGAdaptiveV199` : peut appeler SAM2/GroundingDINO si aucun masque n'est fourni, puis appliquer **sequentiellement** BiRefNetRMBG (`Lucida` par defaut) sur maximum 2 regions objet (maximum technique : 4). Florence-2 est utilise pour restreindre les prompts quand disponible. Ce noeud fournit 4 sorties : masque original/retenu, propositions de matting, carte d'incertitude, rapport JSON.

Nouveaux noeuds `SmartSVGStudioV199Express` / `Expert`. Le regl. `raffinement_ia = desactiver` conserve exactement le chemin historique ; `diagnostic` lance le second modele mais ne change pas le PNG final ; `proposition` genere des alternatives QA ; `adopter_annotation` exige une annotation (MASK) et exige +2,5 points d'IoU vs le masque principal avant adoption.

Workflow recommande : `example_workflows/SmartSVG_Studio_V19_9_Photo_Orchestration.json` (second passage diagnostic ACTIVE, type PHOTO) ; `..._Express.json` (second passage DESACTIVE, sans surcout GPU). Modifier le modele et les parametres dans le noeud ComfyUI.

**Limites** : aucun modele n'a ete execute sur RTX 3070 dans l'environnement de developpement. L'accord IoU entre SAM2 et BiRefNet n'est pas une mesure de qualite. Lucida et les autres modeles BiRefNet peuvent etre absents selon la version de RMBG ; l'API est controlee au runtime et le mode non force utilise un repli diagnostique. La carte d'incertitude n'est pas un contour de decoupe. Les PNG QA de masques sont dans `QA_MATTING_V19_9/` au dossier de sortie global. Les SVG vectoriels historiques ne changent pas.


## V20.2 — fusion Line Art / IA / Cricut
Voir `README_V20_2.md` pour le choix des opérations, le raccordement SAM2/Florence-2 et les avertissements.
