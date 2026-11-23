# SmartSVG V3.5 — Protocole CAL-CUT / CAL-PTC Explore 5

**Statut initial : PROTOCOLE PROPOSÉ, ESSAIS MATÉRIELS NOT_RUN.** Il s'agit de mesurer, pas de certifier Cricut ni d'inventer des tolérances ou fonctions de Design Space. Deux parcours **indépendants** ; n'utiliser ni macro clavier de commande machine ni API privée. Un test CI, une capture d'écran ou un XML valide ne vaut pas essai physique.

## CAL-CUT — SVG Basic Cut

**Fixtures distinctes :** carré nominal **40,00 × 40,00 mm** avec un seul contour fermé ; puis anneau avec un trou intérieur nominal **10,00 mm**, et enfin un sujet réel après ces deux coupons. Les SVG portent explicitement `width`/`height` en mm et un `viewBox` cohérent ; enregistrer source et taille confirmée séparément de tout PPI proposé (la métadonnée PPI n'est pas une dimension physique confirmée).

1. Partir d'un projet V1/Subject admissible, conserver l'image et les masques originaux, noter project SHA, revision, Subject ID et paramètres du moteur.
2. Exporter avec consentement et destination vide ; vérifier SHA-256, relecture XML hors DTD/éléments actifs/ressources distantes, topologie (composantes/trous), unités mm/viewBox, absence de masque de découpe SVG non pris en charge. Tout refus doit préserver projet et destination ; lien symbolique, overwrite et révision périmée testés séparément.
3. Ouvrir manuellement le SVG dans **la version relevée** de Design Space ; relever les dimensions X/Y affichées **avant tout redimensionnement** et les éventuels avertissements, éléments ignorés ou opérations modifiées.
4. Préparer un tapis/matériau/outil documentés ; sélectionner l'opération de coupe voulue après revue humaine. Couper le coupon puis mesurer au pied à coulisse les longueurs X/Y et le trou (si pertinent), dans au moins deux orientations pour identifier un effet directionnel.
5. Calculer `écart_import_X_mm = largeur_DS - largeur_SVG`, `écart_coupe_X_mm = mesure_physique_X - largeur_SVG` (idem Y). Noter différence de topologie ou d'attache, et répéter si l'origine de l'écart est inconnue.
6. Un verdict `PHYSICAL_PASS` exige des **tolérances d'acceptation définies, instrument étalonné/identifié et mesures enregistrées**. Tant que ces valeurs sont inconnues, état `MEASURED / ACCEPTANCE_UNKNOWN`, jamais PASS.

## CAL-PTC — PNG Print Then Cut (parcours séparé)

1. Préparer une image PNG synthétique vérifiée avec dimensions physiques confirmées, couche alpha/bleed connus et repères de mesure du motif. Contrôler les pixels/ratio et le PPI utilisé ; ne pas inférer le PPI d'une valeur EXIF arbitraire.
2. Relever la version de Design Space et les contraintes de format/impression présentées **par cette version**. Effectuer le calibrage Print Then Cut conformément aux indications de l'application et consigner son résultat ; ne pas prétendre que CAL-CUT calibrerait PTC.
3. Importer le PNG, vérifier dimensions et rendu ; imprimer à l'échelle requise sans agrandissement automatique, noter imprimante, support et paramètres.
4. Faire la coupe PTC réelle ; mesurer sur plusieurs côtés le décalage entre contour imprimé et coupe, en X/Y et selon la position dans la page. Relever les défauts de registration et les conditions d'éclairage, matériau et tapis.
5. Conserver le résultat `UNKNOWN` tant que la tolérance, le réglage et la répétabilité nécessaires n'ont pas été décidés puis vérifiés.

## Enregistrement commun des essais (une fiche par résultat)

| Champ | Valeur à renseigner |
|---|---|
| Run ID / opérateur / horodatage | |
| Type | CAL-CUT carré / anneau / sujet ; CAL-PTC |
| Build SmartSVG / commit SHA / hash export SHA-256 | |
| Projet V1 SHA / revision / Subject ID / dimensions source | |
| Design Space version / OS / pilote machine | |
| Matière / tapis / lame ou stylo / opération / profil | |
| Imprimante / papier / échelle / calibration PTC (si applicable) | |
| Nominal X/Y, affiché DS X/Y, mesuré physique X/Y, incertitude instrumentale | |
| Contours/trous/intégrité / décalage PTC / répétitions | |
| Observations / photos / anomalie reproductible | |
| Tolérance approuvée / décision PASS, FAIL, NOT_RUN ou UNKNOWN | |

Les fichiers d'essai peuvent être **synthétiques** dans le dépôt ; photos utilisateur, données privées et provenance non autorisée ne doivent jamais être publiées automatiquement dans le dépôt public.

Les résultats alimentent W04 (prévol), W07 (seuils observés), W08 (PTC) et W09 (échenillage) **sans** modifier les données avant revue. Les améliorations à l'interface Windows restent indépendantes de l'accès physique à une Explore 5.
