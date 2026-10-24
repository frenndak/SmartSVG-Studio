# Continuité du chantier SmartSVG — après V20.1.1

V20.1.1 termine une première phase de contre-expertise du **mode Line Art** ; ce n'est **pas** un changement de cap du projet.

- **V20.2 (priorité suivante)** : raccordement Line Art → segmentation sémantique Florence-2/SAM2 existante. Mapper correctement masque et coordonnées recadrées, conserver les PNG d'origine, exporter les candidats QA sans promouvoir les silhouettes par défaut. Test d'une photographie de dessin et d'un personnage sans fond.
- **V20.3** : mesure réelle du GPU RTX 3070 (8 Go) à l'aide du profiler corrigé, mesure à froid/à chaud et repli sûr en cas d'OOM ; pas d'annonce de performance non mesurée.
- **V20.4** : vrais cas mains / chopes / cheveux / barbe et occlusions annotés, comparaison IoU et F1 contours.
- **V20.5** : import des fichiers et vraie découpe sur Cricut Explore 5, marge calibrée en mm, essais physiques de stickers.

Conserver également le chantier vectoriel des planches multi-stickers, les 12 escargots et les exports Cricut historiques. Pour toute nouvelle version : archive propre, tests, rapport, compatibilité.
