# SmartSVG Studio V21.7 — préparation de captures et contrôle qualité Cricut

**V21.7 bêta : modules non destructifs supplémentaires.** Conserve l'éditeur de masques V21.6.1, Express V21.5.1 et tous les identifiants historiques. Aucun moteur de vectorisation n'a été modifié.

## Démarrer en 3 étapes

1. **Préparer l'image** avec `SmartSVGPrepareV217` (facultatif) : conserver, supprimer des bandes noires franches ou recadrer manuellement en pourcentage. **Ce nœud vient avant les outils produisant les masques.** Il ne peut pas recevoir directement un masque déjà calculé, pour éviter tout décalage des coordonnées.
2. **Sélectionner les sujets / corriger les masques** avec ton workflow IA existant ou `SmartSVGMaskEditorV216` (pinceau ajouter/retirer, annuler/rétablir, zoom V21.6.1). Sur les PNG alpha, `LoadImage.MASK` donne un masque inversé de la transparence : utiliser le workflow avec `InvertMask`. Sur un JPG/PNG opaque, partir du workflow manuel ou du guidage IA.
3. **Contrôler** avec `SmartSVGQualityV217` : connecter IMAGE et MASK issus de l'éditeur, régler `largeur_mm` à la même largeur que celle prévue dans Express, lire les alertes et regarder l'aperçu facultatif. **Connecter ses sorties inchangées à Express** pour lancer l'export PNG/SVG après validation.

## Les 3 workflows V21.7

- `example_workflows/SmartSVG_Studio_V21_7_01_Capture_Recadrer_Puis_Corriger.json` : photo/capture opaque (dont canard). Recadrage automatique prudent, premier démarrage avec Express **désactivé** jusqu'à création du masque. Charger l'image, exécuter, dessiner dans le nœud éditeur, enregistrer, réactiver Express, relancer.
- `example_workflows/SmartSVG_Studio_V21_7_02_PNG_Alpha_QA_Cricut.json` : dessin PNG réellement transparent : `LoadImage` → `InvertMask` → éditeur → contrôle qualité → Express. **Si ton fichier ne possède pas de transparence, utiliser la version capture/manuelle à la place.**
- `example_workflows/SmartSVG_Studio_V21_7_03_Planche_12_Guidage_IA_QA.json` : planche de 12 sujets. `Florence-2` + segmentation guidée du nœud historique si modèles présents, éditeur de masque → QA → Express. **Le modèle IA et la quantité de sujets reconnus ne sont pas garantis** ; privilégier correction/séparation manuelle au besoin et vérifier le rapport IA.

## Sens des alertes

| Code | Interprétation |
|---|---|
| `MASQUE_VIDE` | Blocage logique : rien n'est sélectionné pour ce sujet. |
| `ILOTS_DETACHES` | Plusieurs composants séparés ; parfois intentionnels (fleurs, détails). |
| `MICRO_ILOTS` | Composants dont l'aire estimée est inférieure à 0,35 mm². |
| `MICRO_TROUS` | Trous potentiellement problématiques de moins de 0,35 mm². |
| `PASSAGE_FIN_A_VERIFIER` | Une ouverture morphologique conservatrice peut séparer la silhouette ; inspection conseillée. |
| `PRECISION_INSUFFISANTE_POUR_TEST_PASSAGE_FIN` | L'échantillonnage de l'image ne permet pas de mesurer raisonnablement l'épaisseur ciblée. |
| `MASQUE_TOUCHE_BORD_IMAGE` | Un masque touche la limite de l'image, possible sujet tronqué. |
| `MASQUES_CHEVAUCHANTS` | Au moins deux masques occupent les mêmes pixels ; risque de répétition des découpes. |

**Important :** l'aire et la largeur sont des estimations à partir du masque, avant les traitements internes d'Express, le contour de bleed et l'interprétation de Cricut Design Space. Aucun îlot ou trou n'est effacé automatiquement, et le nœud n'a pas de fonction « certificat Cricut ».

## Installation

1. Fermer ComfyUI ; sauvegarder les workflows et retirer les anciennes versions de SmartSVG de `custom_nodes` (les déplacer **hors** de ce dossier).
2. Extraire le dossier `ComfyUI-SmartSVG-Studio-V21.7` dans `ComfyUI/custom_nodes/`, redémarrer ComfyUI et actualiser le navigateur.
3. Charger un des trois workflows ci-dessus. Choisir ton image dans `LoadImage`.
4. Au besoin, lancer le contrôle d'intégrité : `python verify_package_v217.py --integrity-only`.

## Tests et limites

- Tests Python/JavaScript, schémas de workflow, manifeste SHA-256. Le vérificateur lance chaque suite séparément avec `--suite 1` à `--suite 6`, et les tests JavaScript avec `--javascript` (Node.js >= 18 uniquement pour les tests).
- **Sur les sept images communiquées** : algorithme de recadrage CPU évalué avec suppression prudente des bandes noires du canard ; six autres exemples volontairement non recadrés. Les résultats d'inférence SAM2/Florence-2 réels, la qualité du détourage obtenu, le frontend réel ComfyUI/Nodes 2.0 et une découpe Explore 5 restent non testés.
- Les vues QA enregistrées sous `ComfyUI/output/SmartSVG_Studio_QA` peuvent être ouvertes par les utilisateurs autorisés sur le serveur. Les vues sont nettoyées à l'exécution suivante : limite de 48 PNG contrôlés par leur préfixe et suppression au-delà de 72 heures. Ne pas exposer ComfyUI sans protection.
- Préparation et QA plafonnées à **5 Mp par image**, **32 masques**, **50 Mp cumulés** pour la QA ; 1 image par appel. Les masques sont conservés intacts, et les aperçus restent facultatifs.
- Un SVG qui enveloppe un PNG imprimé n'est pas équivalent à une véritable vectorisation interne éditable des couleurs, traits et texte. Toujours importer et inspecter dans Cricut Design Space avant fabrication.
