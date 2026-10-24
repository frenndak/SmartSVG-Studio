# G1.2 — Contrats d'échange pour projets SmartSVG (prototype)

**Périmètre :** micro-lot G1.2 de la roadmap V3.2. La baseline V21.15.2, ses nœuds ComfyUI, l'archive source, les exports de production et la roadmap figée ne sont pas modifiés.

## Modèle

Module autonome, Python standard uniquement : engine/smartsvg_core/project_contracts.py.

| Record | Identité / invariants |
|---|---|
| SourceAsset | ID stable, SHA-256, dimensions positives en pixels, mode couleur, provenance |
| Mask | ID, source propriétaire, SHA-256, dimensions identiques à la source, L8, polarité explicite subject_white |
| Subject | ID stable, source, masque, bbox (x,y,largeur,hauteur) en pixels; accessoires référencés par ID |
| Artifact | ID, objets, usage explicite print_then_cut_png / basic_cut_svg / editable_svg, chemin relatif, SHA-256, taille en mm, PPI obligatoire pour le PNG imprimable |
| QAResult | Axes distincts visuel / géométrie / import Design Space / coupe physique, états not_tested/passed/failed, provenance de preuve pour import et coupe |

validate_project_records(...) vérifie les références, doublons, dimensions, liens d'accessoires et la cohérence entre les objets. record_dict(...) crée des données JSON sérialisables. Le schéma se nomme smartsvg-contracts/1 et ne dépend pas du numéro de version du programme.

## Limites : important

- Il s'agit de la **validation des métadonnées**, pas de l'inspection des pixels, de la fermeture des trajets SVG, de la présence réelle des fichiers ni d'une inspection antivirus des archives.
- Un champ d'empreinte SHA-256 valide n'établit pas que le fichier original possède cette empreinte : la comparaison des octets sera ajoutée au chargeur de projet G1.3.
- Les liens d'accessoires identifient des éléments existants sur la même source; le regroupement / la géométrie effective restent à vérifier dans le moteur.
- L'environnement real et un identifiant de preuve ne certifient **pas** qu'un test a réellement été exécuté. Seul un contrôle de preuves documentées et indépendantes peut valider les assertions physiques.
- Aucun export n'est automatiquement marqué « compatible Cricut », et aucun changement de comportement des anciens workflows n'est introduit.

## Validation et rollback

Depuis engine/ : python -m unittest discover -s tests -p 'test_project_contracts_g12.py' -v

Depuis la racine du dépôt : python -m unittest discover -s tests -p 'test_g12_project_contracts.py' -v

**Gate local :** 8 tests positifs et négatifs passent; revue externe du diff et CI privée encore nécessaires avant fusion. Rollback : supprimer uniquement les fichiers ajoutés par cette PR. Ne pas reconditionner ni modifier la V21.15.2 figée.

## Prochain micro-lot

**G1.3** : lecture/écriture atomique du conteneur .smartsvg, ressources relatives, comparaison des empreintes aux octets, chargement sécurisé des masques, migrations et tests de reprise. Ce travail reste indépendant jusqu'à validation de G1.2.
