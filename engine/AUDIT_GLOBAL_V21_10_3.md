# Contre-expertise globale SmartSVG Studio V21.10.3

**Base de référence :** archive d'installation V21.10.2 fournie. Analyse d'une extraction isolée. Version corrective V21.10.3 après corrections ciblées ; tests depuis l'extraction et le paquet réextrait. **Validation locale seulement** : aucune installation sur le PC de l'utilisateur ni découpe physique.

## 1. Intégrité / chaîne de livraison — favorable

- Archive examinée sans chemin d'extraction transversal, manifeste SHA-256 comparé aux fichiers réellement présents.
- Nœuds historiques chargés et leurs identifiants conservés. Contrats d'entrée des cinq réglages Express et trois sorties comparés aux anciens.
- Trois workflows V21.10 structurellement vérifiés. Un contrôle de liens/ports JSON ne remplace pas un chargement réel dans ComfyUI.
- Fichiers modifiés ciblés uniquement : point d'entrée, module HD, wrapper HD, éditeur unifié, son frontend ; ajout d'un test, d'un vérificateur et des documents.

## 2. Moteurs de détourage / segmentation — sous réserve majeure

- L'extension ne garantit pas une inférence IA automatique à partir d'images JPEG/PNG opaques. La présence de composants RMBG/Florence/SAM2 n'est pas la preuve qu'ils sont configurés ou exécutés.
- Les sept images jointes sont opaques ; sans masque externe ou tracé manuel, un export rectangulaire n'est **pas** un sticker détouré autour du sujet.
- Distinguer `IMAGE` (couleurs), `MASK` (silhouette), segmentation multisu jet et export. La première validation V21.11 devra être un essai de détection sur des fichiers opaques puis contrôle visuel/quantitatif de qualité.

## 3. Masques / éditeur graphique — favorable en simulation

- Sauvegarde normalisée, empreinte associée à l'image et aux masques, rejet de corrections appliquées à une nouvelle segmentation.
- Limites : 5 Mp par image, jusqu'à 32 masques et 50 Mp cumulés. Affichage facultatif : une défaillance du panneau ne doit pas effacer une correction Python réussie.
- Aucun essai sur le vrai frontend ComfyUI ni sur le GPU 8 Go. Effet du zoom natif, comportement des écrans HiDPI et certains plugins à confirmer.

## 4. Diagnostic géométrique / dimensions — réserve corrigée dans l'affichage

- Les îlots, trous, chevauchements et bords sont des alertes de masque, pas un résultat de découpe physique.
- **Défaut de conception restant :** l'éditeur utilise 40 mm pour estimer les passages fins même si Express exporte à une autre largeur. V21.10.3 expose ce caractère hypothétique dans l'interface et le JSON.
- Pour une validation dimensionnelle exacte, V21.11 devra transmettre la largeur réelle à l'éditeur ou centraliser le rapport d'export avec le diagnostic final.

## 5. PNG HD / gestion des reprises — corrigé

- Ancien comportement : second appel sur le même dossier impossible à valider parce que le fichier HD existe déjà.
- Nouveau comportement : fichier HD réutilisable avec preuve latérale limitée et empreintes SHA-256 de l'original et du dérivé. Aucune acceptation des fichiers modifiés, orphelins ou sans preuve.
- Les noms réservés déjà présents ne sont pas écrasés. Les sorties imprimables historiques ne sont pas modifiées.
- Un upscale à 600 ppp ne recrée pas de détails absents. La version HD n'est pas substituée par défaut au PNG de découpe conservateur.

## 6. Export Print Then Cut / SVG — favorable en précontrôle, non certifié dans Design Space

- Dossier `00_IMPORTER_DANS_CRICUT` et format PNG RGBA destinés à l'import `Flat Graphic` ; le PNG reste image aplatie et l'alpha définit une géométrie de découpe présumée.
- Audit des composantes et trous alpha ; classification spécifique des cartes rectangulaires.
- Le SVG de contour distinct sert au diagnostic / découpe seule et ne doit pas être superposé au PNG Print Then Cut.
- La vraie silhouette, la taille, l'opération et l'adaptation au format papier doivent être contrôlées dans Design Space. Le précontrôle ne simule pas le logiciel Cricut.

## 7. Sécurité / gestion des ressources — satisfaisant localement avec limites

- Validations de chemins absolus de source sous dossier projet, rejets de liens symboliques explicites, protection contre l'écrasement des fichiers d'import différents.
- Limits de pixels, sujets et miniatures présentes. Les ressources mémoire en vrais lots et les chemins réseau Windows restent à mesurer.
- Les images temporaires servies par ComfyUI sont accessibles aux clients déjà autorisés du serveur ; ne pas exposer l'instance sans authentification.

## 8. Tests

- Suites historiques isolées : 720 tests Python réussis (12 groupes).
- Cas additionnels hérités du correctif V21.10.2 : 5 tests Python réussis.
- Nouveaux cas V21.10.3 : 5 tests Python réussis sur HD identique, source changée, dérivé corrompu, fichier sans preuve, largeur QA hypothétique.
- JavaScript : 43 tests de simulateur frontend réussis.
- **Total attendu avec le correctif : 730 Python + 43 JavaScript = 773 tests**, sous réserve d'une vérification de l'archive installable.

## 9. Risques restants / décision

| Priorité | Risque | Contrôle requis |
|---|---|---|
| P0 | Masque IA sur les sept images opaques | Inference sur PC, QA par sujet, comparaison visuelle et retouche |
| P0 | Compatibilité navigateur ComfyUI réel | Tester le plugin avec frontend exact et extensions tierces |
| P0 | Import réel des PNG / découpe Cricut | Vérifier Flat Graphic, dimensions, silhouette et test physique |
| P1 | Largeur réelle du contrôle géométrique | Contrat dimensionnel unifié avec Express |
| P1 | Réactivité sur grandes planches et 32 masques | Mesures CPU, mémoire, latence GPU |
| P2 | Vraies couches SVG modifiables | Spécification distincte du Print Then Cut |

**Verdict :** base de code testable et suffisamment stable pour commencer le prochain chantier **V21.11 — segmentation réellement automatique**, mais pas certifiée de bout en bout sur ComfyUI/Cricut.
