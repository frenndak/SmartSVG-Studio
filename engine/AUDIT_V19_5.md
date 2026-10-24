# Audit V19.5

## Vérifications

- La V19.4 reste le moteur de génération des PNG et des masques.
- L'analyse V19.5 se produit après la publication intermédiaire dans un dossier de staging et ne modifie aucun fichier déjà généré.
- 12 nouveaux tests couvrent les chevauchements, masques identiques, imbriqués, absents, dimensions incohérentes, scène sans modèle, restitution des pixels, identité SHA des PNG/Cricut, échec atomique et nœud ComfyUI simulé.
- Les 57 tests ciblés antérieurs V19 à V19.4 passent avec le code V19.5.
- La validation finale du ZIP doit être réalisée après extraction propre et sans les artefacts de développement.

## Limites non levées

- L'inférence Florence-2/SAM2 ne peut pas être validée sans l'installation locale équipée des checkpoints et du GPU.
- Une zone commune à deux masques n'est pas nécessairement un problème : une main et une chope peuvent se superposer.
- Les masques exclusifs proposés ne reconstruisent aucun pixel caché, ne sont pas des fichiers Cricut prêts à imprimer et peuvent créer une couture visible.
- Les tests synthétiques ne constituent pas une mesure du taux de reconnaissance sur des photographies réelles.
