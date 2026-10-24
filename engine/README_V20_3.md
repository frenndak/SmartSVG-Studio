# SmartSVG Studio V20.3 — prévol GPU, protection VRAM et mesure non destructive

**Statut : bêta logicielle.** Basée intégralement sur V20.2 : Florence-2, SAM2, Line Art, SVG, impression/découpe et toutes les versions historiques restent présentes. Cette version ajoute un diagnostic GPU *sans exécuter de poids IA* et un nœud Line Art protégé.

## Première installation Windows

1. Fermer ComfyUI. Sauvegarder et **retirer** les anciennes copies SmartSVG de `ComfyUI/custom_nodes`, puis extraire `ComfyUI-SmartSVG-Studio-V20.3` dans `custom_nodes`.
2. Vérifier dans l'environnement Python de ComfyUI que `torch`, `opencv-python`, `numpy` et `Pillow` fonctionnent. RMBG reste requis pour les vraies inférences Florence-2/SAM2, pas pour nettoyer et vectoriser un dessin.
3. Redémarrer ComfyUI et importer `example_workflows/SmartSVG_Studio_V20_3_Diagnostic_GPU.json`.
4. Charger `SmartSVG_Studio_V20_3_LineArt_Protection_GPU.json` pour photographies de dessins, PNG transparents et scans.
5. Si le pilote CUDA est inaccessible, le mode `protege` conserve les exports classiques (sticker, contour, SVG des traits), mais **n'exécute pas** SAM2 et ne fabrique jamais de silhouette IA.

## Nouveaux nœuds

### `SmartSVGGPUPreflightV203`

Lecture **seule** des capteurs PyTorch : modèle de GPU et VRAM physique, mémoire libre globale via `torch.cuda.mem_get_info`, allocations actuelles et réserve de l'allocateur, pic *historique* de l'allocateur, erreurs de capteurs. Aucun poids téléchargé/chargé, aucun modèle exécuté, aucun cache CUDA forcé à se vider.

### `SmartSVGLineArtV203`

Reprend **tous** les champs de `SmartSVGLineArtV202`, dont `operation_cricut` avec sticker silhouette / tous les traits / stylo, en ajoutant :

| Paramètre | Valeur par défaut | Rôle |
|---|---|---|
| `politique_gpu` | `protege` | Contrôle préventif de la mémoire libre avant l'inférence *interne* |
| `vram_libre_min_gio` | `2.5` | Seuil libre indicatif (modifiable) |
| `marge_securite_gio` | `0.5` | Réserve préventive additionnelle |

Actions :

- **`protege`** : si CUDA absent, mémoire inconnue ou libre globalement sous le seuil, désactive **l'inférence interne** et conserve les exports historiques. Si le client demandait `segmentation_ia=forcer`, l'exécution est arrêtée au lieu de dégrader silencieusement la demande.
- **`diagnostic`** : signale le risque, mais laisse fonctionner la V20.2 ; un manque de VRAM peut toujours provoquer une erreur ou un arrêt de ComfyUI.
- **`strict`** : arrête explicitement le traitement avant de créer des fichiers si la mémoire libre ne franchit pas le seuil ; ne change rien aux fichiers déjà existants.

Un `masques_objets` externe **court-circuite** le garde-fou d'inférence interne : aucun modèle n'a besoin d'être relancé dans SmartSVG, mais la création d'un PNG et l'alignement des masques ont toujours un coût RAM.

## Rapport GPU

Un rapport `QA_GPU_V20_3/rapport_gpu_<id>.json` est ajouté dans le **dossier de création généré**. Il contient les lectures *avant/après*, le temps total du nœud, la décision du garde-fou, le statut de la segmentation, et les raisons d'abstention. L'écriture est atomique : un échec du sidecar n'annule pas les exports Cricut de V20.2. Le rapport est aussi joint à la sortie `rapport_export`.

Important : **le rapport ne mesure pas le pic VRAM individuel de SAM2, ni la qualité de son détourage, ni son temps isolé**. L'appel d'une fonction modèle ne prouve pas qu'elle tourne sur CUDA ; la VRAM libre globale dépend d'autres programmes. Le garde-fou ne garantit pas l'absence de `CUDA out of memory` : les variations de mémoire et besoins des modèles sont dynamiques.

## Workflows V20.3

- `SmartSVG_Studio_V20_3_Diagnostic_GPU.json` : état CUDA/VRAM sans inférence.
- `SmartSVG_Studio_V20_3_LineArt_Protection_GPU.json` : choix de découpe historique + protection automatique.
- `SmartSVG_Studio_V20_3_Photo_Ecran_GPU.json` : recadrage photo d'écran + IA interne seulement si seuil libre respecté.
- `SmartSVG_Studio_V20_3_Silhouette_GPU_Strict.json` : arrête le traitement si GPU insuffisant ; ne certifie pas le masque produit.
- `SmartSVG_Studio_V20_3_Tous_Traits_GPU.json` : SVG des détails intérieurs, sans prendre les contours IA pour des lignes de coupe.
- `SmartSVG_Studio_V20_3_Masque_Externe_GPU.json` : branchement d'un masque produit ailleurs, accessible même sans GPU local pour SmartSVG.

## Ce qu'on a réellement testé

- Batterie complète ancienne + nouveaux tests V20.3, en environnement Linux **CPU seulement**.
- Simulation des capteurs CUDA (GPU disponible, indisponible, faible VRAM, panne partielle des lectures, changement d'index).
- Comparaison binaire des fichiers d'export de la V20.2 et du nœud V20.3 sur la même image.
- Photo d'écran réelle en **mode sans inférence IA** et contrôles des signatures SHA-256.
- Vérification des workflows et installation propre depuis le ZIP.

**Non testé** : chargement réel Florence-2/SAM2/BiRefNet sur RTX 3070 8 Go, pics VRAM par modèle, finesse des vrais détourages IA, découpes physiques Explore 5, interface interactive ComfyUI sous Windows.

## Prochaine étape sans rupture de feuille de route

**V20.4 :** reprendre les masques réels obtenus sur Windows et améliorer les recouvrements personnage/objet et cheveux/barbe/transparences en utilisant les rapports V20.3. Puis **V20.5 :** contrôle Cricut des contours SVG/Print Then Cut, dimensions et séparation des opérations.

Sources techniques : documentation PyTorch sur le caching allocator CUDA (`memory_allocated`, `memory_reserved`, `max_memory_allocated`, `empty_cache`), ComfyUI `model_management` et interface RMBG 3.3.x. L'extension n'utilise pas `empty_cache` automatiquement, car ce n'est pas une libération des tenseurs actifs.
