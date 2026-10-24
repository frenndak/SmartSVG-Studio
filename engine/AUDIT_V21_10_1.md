# SmartSVG Studio V21.10.1 — Contre-expertise croisée et correctifs

**Périmètre** : révision du contenu réel de l'archive V21.10, nœud `SmartSVGUnifiedEditorV2110`, modèles JS, publication des masques natifs, moteur de rejeu Python, diagnostic des chevauchements et export Cricut hérités. Les sept images précédemment partagées ne sont pas des masques IA, et les tests ne simulent pas un résultat de segmentation produit sur RTX 3070.

## Passe 1 — Contrats et compatibilité

- Le nœud unifié conserve `SmartSVGUnifiedEditorV2110`, ses 2 entrées et 3 sorties, ainsi que le format version 1 des retouches dans le workflow. Aucun changement de schéma ni migration nécessaires.
- Les **cinq paramètres Express** et le dossier `00_IMPORTER_DANS_CRICUT` restent inchangés ; les PNG/SVG de fabrication sont générés par les moteurs existants.
- Anciens workflows et nœuds restent enregistrés. Seul le fichier `__init__.py` du point d'entrée est ajusté pour identifier la version corrective.

## Passe 2 — Latence de l'éditeur (correctif P0)

**Défaut démontrable dans V21.10** : `render()` reconstruisait toute la superposition des masques et exécutait `getImageData()` sur un canvas pouvant atteindre 1600 × 1100 px à chaque déplacement du pinceau ; les traits enregistrés étaient également rejoués à chaque mouvement.

**Correction** : un calque d'aperçu des contours est mis en cache, avec invalidation explicite lors d'un zoom/déplacement, redimensionnement, changement de sujet/masque, annulation ou validation d'un trait. Le tracé en cours bénéficie d'un retour temporaire distinct, vert (ajout) ou orange (retrait), sans réanalyse complète à chaque pixel de mouvement. **Le calcul final reste celui de Pillow/Python** ; les couleurs temporaires ne sont pas exportées. Le test navigateur simulé vérifie qu'un glissement ne provoque aucune relecture raster et que la validation du trait puis le zoom déclenchent chacun exactement une mise à jour.

## Passe 3 — Mémoire des chevauchements (correctif P1)

**Défaut** : la matrice de comptage multi-masques créée par `np.count_nonzero(binary,axis=0)` était un entier généralement 64 bits (jusqu'à 40 Mo sur un visuel 5 Mp).

**Correction** : `np.sum(binary,axis=0,dtype=np.uint8)` : sur au plus 32 sujets, le compteur 8 bits est exact (0..32), utilise 5 Mo à 5 Mp et ne modifie pas la détection. Nouveau test avec 32 masques superposés, contrôle de l'alerte `MASQUES_CHEVAUCHANTS` et de la valeur maximale du compteur.

## Passe 4 — Conservation des retouches (correctifs P1)

- Escape ou clic sur le fond de la fenêtre : confirmation lorsque des modifications n'ont pas été sauvegardées (sans avertissement gênant en l'absence de changement). Le bouton explicite « Fermer sans sauvegarder » conserve sa signification.
- Une exception dans le rappel ComfyUI de sauvegarde rétablit la valeur précédente du champ `retouches_json` et maintient la fenêtre ouverte. Test de l'échec provoqué.
- Si l'image native du masque ne peut pas être chargée, l'interface refuse de présenter la sauvegarde comme réussie.
- Une limite de 1500 points sur un trait long est maintenant signalée pendant le geste.

## Passe 5 — Sécurité et erreurs

- JSON des corrections toujours validé et lié par empreinte SHA-256 à l'image et aux masques initiaux ; l'éditeur ne rejoue jamais les retouches sur une segmentation incompatible.
- Les URLs d'aperçu restent construits avec `api.apiURL('/view')` et le validateur strict de références.
- Les erreurs de publication et d'affichage n'altèrent pas la sortie `MASK` calculée ; une erreur de rejeu demeure bloquante.
- Il reste un risque de perte de modifications non enregistrées si un nœud est supprimé ou réexécuté pendant l'édition : cette fermeture de cycle ComfyUI est forcée pour ne pas retenir des masques périmés.

## Passe 6 — Cricut Design Space

- La fabrication n'a pas été modifiée. Pour **Imprimer puis découper**, choisir les PNG transparents de `00_IMPORTER_DANS_CRICUT`, en mode *Flat Graphic / Image aplatie* : un SVG de contour séparé n'est pas à empiler sur le PNG pour un seul sticker.
- Un PNG peut être valide tout en représentant une **carte rectangulaire** si aucun détourage n'a été fourni. Un PNG raster ne convertit pas non plus chaque détail en calque SVG éditable.
- La taille réellement importée, les contours, le format papier, la calibration et la découpe physique doivent être vérifiés dans Design Space et sur la Cricut Explore 5. **Aucun essai matériel n'a été effectué.**

## Passe 7 — Tests et limites

- 720 tests Python exécutés, répartis en sous-suites (629 historiques premiers groupes, puis 17+20+12+11+14+7+10 autres tests).
- 43 tests JavaScript réussis, y compris plusieurs vérifications nouvelles au sein des tests existants (cache, fermeture non sauvegardée, échec de la sauvegarde).
- Vérification du paquet final : manifeste SHA-256, fichiers inchangés par rapport à V21.10 sauf allowlist, workflows V21.10 préservés, exécution des tests ciblés après extraction.
- **Pas de validation du DOM réel** sur la version installée de ComfyUI / Nodes 2.0, de l'upscaling IA réel sur RTX 3070, ni d'import Print Then Cut en situation réelle.

## Verdict

**GO conditionnel pour la V21.10.1** : correctifs ciblés utiles sans bouleverser les cinq réglages Express, les nœuds historiques ou le contrat PNG/SVG. Les défauts de performance et de sûreté de la sauvegarde sont atténués et testés ; la certification matérielle reste ouverte.
