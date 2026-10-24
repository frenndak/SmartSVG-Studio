# SmartSVG V14.1 — Rapport de correction (22 octobre 2026)

## Provenance
Correctif sur l'archive SmartSVG V14 fournie par l'utilisateur, pas une nouvelle architecture semantique. Traitement local hors ComfyUI sur la vraie planche JPG 1536 x 1024 et tests sur images artificielles.

## Anomalies corrigées
- Pont ComfyUI-RMBG tenant compte de la section `optional` et des parametres `required` de `INPUT_TYPES`, avec valeurs explicites `process_res=768`, `sensitivity=0.5` et retour `MASK` valide 0..1.
- Journal des tentatives d'inference, masques IA retenus, erreurs et modele utilise quand disponible.
- Batterie de tests autonome, sans fichier V13 manquant dans le ZIP.
- Comptage interne sous-chemins, segments et courbes (pas seulement les chemins XML).
- Fidelite mesuree par rasterisation CairoSVG face au vrai PNG Print Then Cut. Si CairoSVG absent, la mesure est marque non effectuee.
- Publication du dossier final seulement apres passage des validations; ancien rapport V14 archive comme diagnostic.

## Mesures locales sur 12 escargots, IA desactivee
- Duree du traitement dans cet environnement : 9.35 secondes (non representative de Windows/RTX).
- Stickers : 12 ; contours independants conserves d'apres tests de geometrie herites.
- SVG compact : 118 balises `path`, 1062 sous-chemins, 14302 segments SVG, 11179 courbes cubiques.
- SVG detaille : 154 chemins, 1743 sous-chemins, 27511 courbes cubiques.
- Ecart moyen RGB SVG compact / PNG original (pixels imprimables) : 25.095/255 ; pixels RGB diff >20 : 22.27%.
- IA locale : non lancee sur ce cas de test; un banc d'essai simule valide son protocole, mais **pas d'inference GPU physique**.

## Verification du code et paquets
- `python verify_package.py` : **11 tests** unitaires/integration simulee et export local reussis.
- Scenarios : image simple, planche transparente irreguliere, contrat RMBG optional, modele absent, masque non fini, backend reutilise, appel nœud complet avec fausse IA, IA forcee valide/refusee, publication refusee sur erreur vectorielle, test sans CairoSVG, verification workflow/manifest.
- Une execution supplementaire sur la vraie planche de 12 escargots s'est terminee avec 12 stickers.

## Limitations bloquantes pour un label production
- Aucune inference CUDA reelle sur RTX 3070 8 Go, aucune validation vraie de l'API RMBG installee ni de son modele telecharge dans l'environnement Windows de l'utilisateur.
- Aucune importation ou decoupe physique effectuee dans Cricut Design Space.
- Les SVG ne contiennent **pas** de parties d'objets semantiques type œil/coquille/fleur ; ils rassemblent des zones de couleur. La complexite interne reste elevee, et la fidelite visuelle est nettement inferieure au PNG pour imprimer.
- La detection automatique de grilles difficiles ou de photos avec fond complexe n'est pas garantie.

**Statut :** V14.1 correctif beta teste dans cet environnement, validation materielle encore necessaire.
