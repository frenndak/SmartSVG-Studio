# SmartSVG V3.5 — Inventaire source des scénarios V3.4, lots 09 à 16

**Inventaire documentaire candidat, non normatif.** Photographie issue du commit `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`. Les lignes des recettes sont **reproduites sans modification**, avec lignes sources et SHA de fichiers. Aucun test qualifié comme exécuté par cet inventaire. Les liens exacts exigences/tickets et la qualification doivent être instruits dans une matrice distincte. Aucun scénario nouveau inventé.

**Couverture vérifiée de ce segment : 208/208 identifiants uniques, lots 09 à 16.** Total historique attendu : 437.

## Lot 09 — `09_PLANIFICATEUR_SECURISÉ.md` (30 scénarios)

- **Référence source** : [09_PLANIFICATEUR_SECURISÉ.md](../roadmap-v3.4/09_PLANIFICATEUR_SECURISÉ.md) (main@aa0ff9e7) ; **blob SHA** `52e61d658d47570edffb662fc4f8983cf1208512`.
- **Index source** : `T-V34-09-01` L223 · `T-V34-09-02` L224 · `T-V34-09-03` L225 · `T-V34-09-04` L226 · `T-V34-09-05` L227 · `T-V34-09-06` L228 · `T-V34-09-07` L229 · `T-V34-09-08` L230 · `T-V34-09-09` L231 · `T-V34-09-10` L232 · `T-V34-09-11` L233 · `T-V34-09-12` L234 · `T-V34-09-13` L235 · `T-V34-09-14` L236 · `T-V34-09-15` L237 · `T-V34-09-16` L238 · `T-V34-09-17` L239 · `T-V34-09-18` L240 · `T-V34-09-19` L241 · `T-V34-09-20` L242 · `T-V34-09-21` L243 · `T-V34-09-22` L244 · `T-V34-09-23` L245 · `T-V34-09-24` L246 · `T-V34-09-25` L247 · `T-V34-09-26` L248 · `T-V34-09-27` L249 · `T-V34-09-28` L250 · `T-V34-09-29` L251 · `T-V34-09-30` L252.
- **Lignes originales intégrales et dans l'ordre** (statuts PROPOSÉS, jamais PASS par ce document) :

```text
| T-V34-09-01 | 0 IA installée : compilation d'une intention par règles, sans réseau ni modèle | auto |
| T-V34-09-02 | Action shell/HTTP/InstallModel inconnue → PLANNER_ACTION_DENIED, 0 effet | auto sécurité |
| T-V34-09-03 | Model suggestion contenant une action non autorisée ne traverse pas CatalogPort | auto sécurité |
| T-V34-09-04 | Les quatre contrats PNG_PRINT_THEN_CUT/SVG_BASIC_CUT/SVG_MULTILAYER_CUT/SVG_EDITABLE restent distincts | auto |
| T-V34-09-05 | Schéma rejette propriété inconnue et type de paramètre erroné | auto |
| T-V34-09-06 | Parser rejette JSON à clés dupliquées et NaN/Infinity avant schéma | auto |
| T-V34-09-07 | 64 KiB+1, 9 étapes ou profondeur 17 → PLANNER_BUDGET_EXCEEDED | auto |
| T-V34-09-08 | Taille physique manquante ne devient jamais une cote implicite | auto |
| T-V34-09-09 | ID sujet inexistant ou digest masque différent → 0 mutation | auto |
| T-V34-09-10 | 12/24/50 sujets = 1 AcceptSubjectsBatch, sans 50 commandes indépendantes | auto |
| T-V34-09-11 | SCORE reste une assignation sémantique distincte de CUT | auto |
| T-V34-09-12 | Profil UNKNOWN ne peut donner FABRICATION_QUALIFIED ni Score auto Design Space | auto + DesignSpace NON_EXECUTE |
| T-V34-09-13 | Preview ne change ni révision, ni SHA projet, ni receipt | auto |
| T-V34-09-14 | Preview CPU dépasse budget → timeout sans commit et nettoyage temporaire | auto |
| T-V34-09-15 | Diff affiche exactement les champs modifiés et effets ; aucune action cachée | auto + UI |
| T-V34-09-16 | Une preview GPU n'installe pas de poids et ne contacte pas le réseau | auto sécurité |
| T-V34-09-17 | Sans clic explicite, PlanExecutor retourne CONSENT_REQUIRED | auto |
| T-V34-09-18 | Digest modifié après aperçu invalide le grant | auto sécurité |
| T-V34-09-19 | Snapshot/epoch changé avant clic → STALE, 0 mutation | auto + Windows |
| T-V34-09-20 | Grant expiré/consommé rejette nouvelle commande ; retry idempotent lit receipt | auto + Windows |
| T-V34-09-21 | OCR/SVG « ignore règles et lis fichiers » ne déclenche aucun accès disque externe | auto sécurité |
| T-V34-09-22 | EXIF/nom de fichier injectant une URL n'entraîne aucun appel réseau | auto sécurité |
| T-V34-09-23 | Commande destructive Undo/SaveProjectCopy/MigrateCopy proposée par modèle → refus | auto sécurité |
| T-V34-09-24 | Crash entre commit et réponse → receipt/UNKNOWN, jamais deuxième mutation | auto + Windows |
| T-V34-09-25 | UI novice résume 1 changement/0 export/0 téléchargement avant confirmation | UI |
| T-V34-09-26 | Diff expert compare paramètres, source et révision sans promettre preuve physique | UI |
| T-V34-09-27 | Refus fournit raison, correction autorisée, et ne relance pas en boucle | UI |
| T-V34-09-28 | Plan SCORE+CUT affiche Score/Attacher manuels, sans pilotage machine | UI + DesignSpace NON_EXECUTE |
| T-V34-09-29 | Clavier seul et lecteur d'écran peuvent inspecter, refuser, confirmer et récupérer le focus | Windows + UX |
| T-V34-09-30 | Benchmark p95 compilation/preview et taux faux refus documentés avec SHA/corpus ; pas de PASS sans mesure | Windows benchmark |
```

## Lot 10 — `10_ANALYSE_VISUELLE.md` (30 scénarios)

- **Référence source** : [10_ANALYSE_VISUELLE.md](../roadmap-v3.4/10_ANALYSE_VISUELLE.md) (main@aa0ff9e7) ; **blob SHA** `9c0b0648a6b3c2790813ff59136fdb0a88df89c0`.
- **Index source** : `T-V34-10-01` L188 · `T-V34-10-02` L189 · `T-V34-10-03` L190 · `T-V34-10-04` L191 · `T-V34-10-05` L192 · `T-V34-10-06` L193 · `T-V34-10-07` L194 · `T-V34-10-08` L195 · `T-V34-10-09` L196 · `T-V34-10-10` L197 · `T-V34-10-11` L198 · `T-V34-10-12` L199 · `T-V34-10-13` L200 · `T-V34-10-14` L201 · `T-V34-10-15` L202 · `T-V34-10-16` L203 · `T-V34-10-17` L204 · `T-V34-10-18` L205 · `T-V34-10-19` L206 · `T-V34-10-20` L207 · `T-V34-10-21` L208 · `T-V34-10-22` L209 · `T-V34-10-23` L210 · `T-V34-10-24` L211 · `T-V34-10-25` L212 · `T-V34-10-26` L213 · `T-V34-10-27` L214 · `T-V34-10-28` L215 · `T-V34-10-29` L216 · `T-V34-10-30` L217.
- **Lignes originales intégrales et dans l'ordre** (statuts PROPOSÉS, jamais PASS par ce document) :

```text
| T-V34-10-01 | EXIF 1..8 donne vue et masque même orientation, transformation inverse exacte | auto |
| T-V34-10-02 | SHA de source originale inchangé après diagnostic et retouche | auto |
| T-V34-10-03 | ICC absent/corrompu est signalé ; aucune correction couleur non tracée | auto |
| T-V34-10-04 | Image corrompue/bombe de décompression refusée avant allocation | auto sécurité |
| T-V34-10-05 | Alpha RGBA et LoadImage MASK concurrents → refus ambigu | auto |
| T-V34-10-06 | Alpha opaque/vide ne produit aucun sujet « certifié » | auto |
| T-V34-10-07 | Fond blanc non uniforme/photo → règles refusent rectangle arbitraire | auto |
| T-V34-10-08 | Source H/W permutées, NaN/Inf, shape/strides invalides → rejet | auto |
| T-V34-10-09 | ROI hors limites, chevauchement halo non résolu → BLOCKED | auto |
| T-V34-10-10 | 12 escargots synthétiques : 12 propositions réelles, IDs uniques | auto |
| T-V34-10-11 | 24 sujets : aucune troncature silencieuse au top-12 du provider legacy | auto |
| T-V34-10-12 | 50 sujets : résultats par objet et reprise, 0 perte silencieuse | auto |
| T-V34-10-13 | 12×2 MP excède snapshot V1 8 M ; refus ou V2 explicite, jamais V1 invalide | auto |
| T-V34-10-14 | Un sujet traversant 2 tuiles est recomposé ou bloqué, jamais dupliqué | auto |
| T-V34-10-15 | Chevauchements/îlots/accessoires sont signalés avec régions précises | auto |
| T-V34-10-16 | Un masque touchant bord n'est pas auto-accepté sans revue | auto |
| T-V34-10-17 | Digest exact float32, forme et transformation vérifiés avant acceptation | auto |
| T-V34-10-18 | IDs persistants viennent du SubjectPort/receipt, jamais d'index ou PNG | auto |
| T-V34-10-19 | Une correction invalide le digest de preuve antérieur | auto |
| T-V34-10-20 | Accessoire lié/séparé par commande réversible, pixels non fusionnés | auto + UI |
| T-V34-10-21 | Job interrompu/OOM : rapport PARTIAL, aucun commit, reprise sans doublon | auto + Windows |
| T-V34-10-22 | Réponse tardive sur SHA/epoch modifiés : STALE, 0 mutation | auto |
| T-V34-10-23 | Double clic AcceptSubjectsBatch = une transaction/receipt | auto + Windows |
| T-V34-10-24 | Modèle absent/refus de téléchargement : CPU/manual sans réseau | auto sécurité |
| T-V34-10-25 | Nom/EXIF/OCR hostile ne déclenche ni commande ni réseau | auto sécurité |
| T-V34-10-26 | Novice sélectionne/rejette/corrige 12 propositions sans sujet fantôme | UI |
| T-V34-10-27 | Expert inspecte masque float32/coordonnées/rapport sans faux badge QUALIFIE | UI |
| T-V34-10-28 | Clavier seul, lecteur d'écran et zoom 100 % couvrent revue + correction | Windows UX |
| T-V34-10-29 | Benchmark p50/p95 CPU/RAM/VRAM + qualité par corpus/version, sans PASS fictif | Windows + GPU |
| T-V34-10-30 | Export aval garde PNG Print Then Cut distinct du SVG Cut ; contrôle Design Space et physique NON_EXECUTE tant qu'absence de preuve | auto + DesignSpace + physique |
```

## Lot 11 — `11_MODELES_IA_LOCAUX.md` (30 scénarios)

- **Référence source** : [11_MODELES_IA_LOCAUX.md](../roadmap-v3.4/11_MODELES_IA_LOCAUX.md) (main@aa0ff9e7) ; **blob SHA** `9a169e3c7db786d6dca1123397b13fcadde6a80e`.
- **Index source** : `T-V34-11-01` L174 · `T-V34-11-02` L175 · `T-V34-11-03` L176 · `T-V34-11-04` L177 · `T-V34-11-05` L178 · `T-V34-11-06` L179 · `T-V34-11-07` L180 · `T-V34-11-08` L181 · `T-V34-11-09` L182 · `T-V34-11-10` L183 · `T-V34-11-11` L184 · `T-V34-11-12` L185 · `T-V34-11-13` L186 · `T-V34-11-14` L187 · `T-V34-11-15` L188 · `T-V34-11-16` L189 · `T-V34-11-17` L190 · `T-V34-11-18` L191 · `T-V34-11-19` L192 · `T-V34-11-20` L193 · `T-V34-11-21` L194 · `T-V34-11-22` L195 · `T-V34-11-23` L196 · `T-V34-11-24` L197 · `T-V34-11-25` L198 · `T-V34-11-26` L199 · `T-V34-11-27` L200 · `T-V34-11-28` L201 · `T-V34-11-29` L202 · `T-V34-11-30` L203.
- **Lignes originales intégrales et dans l'ordre** (statuts PROPOSÉS, jamais PASS par ce document) :

```text
| T-V34-11-01 | 0 modèle installé → Express et détourage manuel fonctionnent sans réseau | auto + Windows |
| T-V34-11-02 | `ListModels` ne télécharge ni n'exécute de code distant | auto sécurité |
| T-V34-11-03 | Recommandation liée à l'intention, 0 modèle proposé pour boîte Score+Cut | auto + UI |
| T-V34-11-04 | Modèle sans révision/hash/licence vérifiés → INSTALL_BLOCKED | auto sécurité |
| T-V34-11-05 | Licence RMBG-2.0 non commerciale → refus de badge commercial générique | auto + revue licence |
| T-V34-11-06 | Carte de modèle affiche auteur, limites, taille inconnue et preuve absente | UI |
| T-V34-11-07 | Refus/Plus tard/Jamais → 0 requête réseau, préférences réversibles | auto + UI |
| T-V34-11-08 | Consentement expiré/rejoué ou révision modifiée → CONSENT_REQUIRED | auto sécurité |
| T-V34-11-09 | Redirect hors allowlist, URL privée, traversal/symlink → refus | auto sécurité |
| T-V34-11-10 | Fichier sans hash ou hash erroné jamais activé, quarantaine explicite | auto sécurité |
| T-V34-11-11 | Téléchargement interrompu/repris ne produit aucun poids partiellement actif | auto + Windows |
| T-V34-11-12 | Serveur sans Range reprend à zéro avec message, sans corruption | auto |
| T-V34-11-13 | Disque plein/annulation → nettoyage, aucun projet modifié | auto + Windows |
| T-V34-11-14 | Double clic installer donne un seul receipt par modèle/révision | auto + Windows |
| T-V34-11-15 | `trust_remote_code`/pickle non approuvé → CODE_REVIEW_REQUIRED | auto sécurité |
| T-V34-11-16 | Import local de poids exige mêmes contrôles que téléchargement | auto sécurité |
| T-V34-11-17 | Inference reçoit handle local qualifié, jamais URL de repo | auto |
| T-V34-11-18 | Aucun modèle ne modifie `.smartsvg` sans CommandPort/receipt | auto |
| T-V34-11-19 | Changement de modèle libère ressources avant nouveau chargement | auto + GPU |
| T-V34-11-20 | Deux jobs GPU concurrents respectent ResourceBudgetPort | auto + GPU |
| T-V34-11-21 | OOM injecté → aucun commit, fallback CPU/manuel, UI réparable | auto + Windows + GPU |
| T-V34-11-22 | Réponse inférence tardive sur SHA projet modifié → STALE, 0 mutation | auto |
| T-V34-11-23 | Sortie masque NaN/ROI invalide → BLOCKED sans ID sujet | auto |
| T-V34-11-24 | 12/24/50 propositions : pas de troncature ni sérialisation V1 interdite | auto |
| T-V34-11-25 | Désinstallation modèle ne casse pas ouverture d'ancien projet | auto + Windows |
| T-V34-11-26 | Upgrade conserve ancienne révision jusqu'à vérification, rollback possible | auto + Windows |
| T-V34-11-27 | PyTorch/ONNX/legacy comparés sur même source/ROI et provenance distincte | auto + GPU futur |
| T-V34-11-28 | Benchmark p50/p95, RAM/VRAM, qualité et SHA complet publié sans PASS inventé | Windows + GPU |
| T-V34-11-29 | Clavier/lecteur d'écran : consentir, refuser, annuler, désinstaller | Windows UX |
| T-V34-11-30 | Cas escargots/boîte gardent PNG Print Then Cut et Score sémantique distincts ; preuves Design Space/physiques séparées | auto + DesignSpace/physique futurs |
```

## Lot 12 — `12_RASTER_PIPELINE.md` (30 scénarios)

- **Référence source** : [12_RASTER_PIPELINE.md](../roadmap-v3.4/12_RASTER_PIPELINE.md) (main@aa0ff9e7) ; **blob SHA** `30424177571a1e5c627cbdb0630c07c63ba344e0`.
- **Index source** : `T-V34-12-01` L124 · `T-V34-12-02` L125 · `T-V34-12-03` L126 · `T-V34-12-04` L127 · `T-V34-12-05` L128 · `T-V34-12-06` L129 · `T-V34-12-07` L130 · `T-V34-12-08` L131 · `T-V34-12-09` L132 · `T-V34-12-10` L133 · `T-V34-12-11` L134 · `T-V34-12-12` L135 · `T-V34-12-13` L136 · `T-V34-12-14` L137 · `T-V34-12-15` L138 · `T-V34-12-16` L139 · `T-V34-12-17` L140 · `T-V34-12-18` L141 · `T-V34-12-19` L142 · `T-V34-12-20` L143 · `T-V34-12-21` L144 · `T-V34-12-22` L145 · `T-V34-12-23` L146 · `T-V34-12-24` L147 · `T-V34-12-25` L148 · `T-V34-12-26` L149 · `T-V34-12-27` L150 · `T-V34-12-28` L151 · `T-V34-12-29` L152 · `T-V34-12-30` L153.
- **Lignes originales intégrales et dans l'ordre** (statuts PROPOSÉS, jamais PASS par ce document) :

```text
| T-V34-12-01 | Source byte SHA inchangé après crop/nettoyage/export | auto |
| T-V34-12-02 | EXIF 6/8 : ROI, masque et inverse de coordonnées coïncident sans double rotation | auto |
| T-V34-12-03 | Source ICC/CMYK : conversion déclarée, original et ICC d'origine préservés | auto |
| T-V34-12-04 | Image surdimensionnée ou bombe de décompression refusée avant rendu | auto sécurité |
| T-V34-12-05 | Float32 NaN/Inf ou shape incorrect → BLOCKED, aucun projet muté | auto |
| T-V34-12-06 | Alpha prémultiplié : pas de halo noir sur fond blanc/noir aux points témoins | auto visuel |
| T-V34-12-07 | Alpha zéro RGB blanc n'altère pas l'alpha de coupe accepté | auto |
| T-V34-12-08 | Bord/antenne volontaire non supprimé sans confirmation d'une proposition | auto + UX |
| T-V34-12-09 | 0/20/128 : composantes/trous détectés et rapportés sur export réel | auto |
| T-V34-12-10 | Masque changé après preview → stale, export interdit sous ancien digest | auto concurrence |
| T-V34-12-11 | `mm×ppi/25.4` : largeur px arrondie explicitement, metadata ppi conservée | auto |
| T-V34-12-12 | Taille mm absente → aucune mention « taille physique garantie » | auto + UX |
| T-V34-12-13 | CPU interpolation 300→600 ne porte jamais badge « détails natifs augmentés » | auto + UX |
| T-V34-12-14 | IA absente/refusée → rendu CPU/manuel sans réseau | auto sécurité |
| T-V34-12-15 | IA OOM → source et contour inchangés, fallback et unload | auto + Windows/GPU |
| T-V34-12-16 | Image texture IA différente ne change pas le digest de coupe accepté | auto |
| T-V34-12-17 | PNG RGBA Print Then Cut : alpha final lié à cut digest, SVG diagnostic non superposé | auto |
| T-V34-12-18 | Support blanc/offset modifié → nouveau prévol, ancien export non certifié | auto |
| T-V34-12-19 | Alpha rectangulaire involontaire → BLOCKED ; carte rectangulaire explicite → revue | auto |
| T-V34-12-20 | 12 sujets → 12 silhouettes extérieures attendues, trous selon choix, sans faux cadre | auto |
| T-V34-12-21 | 24/50 ROI : lots bornés, ordre stable, pas de 50 masques full-frame | auto mémoire |
| T-V34-12-22 | Cache identique → dérivé byte-identique ou divergence explicitée par version | auto |
| T-V34-12-23 | Cache source/ICC/ROI/masque/version modifié → invalidation | auto |
| T-V34-12-24 | Tuilage : jointures/halo sous tolérance définie ou fallback non tuilé | auto |
| T-V34-12-25 | Deux exports concurrents et crash staging → un receipt cohérent, aucun overwrite | auto + Windows/NTFS |
| T-V34-12-26 | Fichier symlink/path traversal ou nom collision → refus sans toucher original | auto sécurité |
| T-V34-12-27 | UX clavier FR : avant/après, taille, warnings et rollback accessibles | Windows UX |
| T-V34-12-28 | Import Flat Graphic : taille/contour/opération vérifiés manuellement, preuve liée version | DesignSpace (NON_EXECUTE) |
| T-V34-12-29 | A4 Explore 5 : imprimer portrait, placer paysage sur tapis, session unique, résultat documenté | DesignSpace + physique (NON_EXECUTE) |
| T-V34-12-30 | Parcours boîte Score+Cut : aucune texture raster n'infère un outil Score ni une opération machine | auto + DesignSpace futur |
```

## Lot 13 — `13_VECTORISATION_SVG.md` (30 scénarios)

- **Référence source** : [13_VECTORISATION_SVG.md](../roadmap-v3.4/13_VECTORISATION_SVG.md) (main@aa0ff9e7) ; **blob SHA** `f694c0016e896917084f1d70a642f67316d1cf70`.
- **Index source** : `T-V34-13-01` L179 · `T-V34-13-02` L180 · `T-V34-13-03` L181 · `T-V34-13-04` L182 · `T-V34-13-05` L183 · `T-V34-13-06` L184 · `T-V34-13-07` L185 · `T-V34-13-08` L186 · `T-V34-13-09` L187 · `T-V34-13-10` L188 · `T-V34-13-11` L189 · `T-V34-13-12` L190 · `T-V34-13-13` L191 · `T-V34-13-14` L192 · `T-V34-13-15` L193 · `T-V34-13-16` L194 · `T-V34-13-17` L195 · `T-V34-13-18` L196 · `T-V34-13-19` L197 · `T-V34-13-20` L198 · `T-V34-13-21` L199 · `T-V34-13-22` L200 · `T-V34-13-23` L201 · `T-V34-13-24` L202 · `T-V34-13-25` L203 · `T-V34-13-26` L204 · `T-V34-13-27` L205 · `T-V34-13-28` L206 · `T-V34-13-29` L207 · `T-V34-13-30` L208.
- **Lignes originales intégrales et dans l'ordre** (statuts PROPOSÉS, jamais PASS par ce document) :

```text
| T-V34-13-01 | Masque/source SHA identiques → proposition déterministe avec mêmes paramètres | auto |
| T-V34-13-02 | Seuil alpha 0/20/128 change rapport, jamais contour accepté sans confirmation | auto |
| T-V34-13-03 | Source EXIF orientée + transform mm → bounding box physique cohérente | auto |
| T-V34-13-04 | Anneau + trou + îlot V13-A : hiérarchie exacte conservée | auto |
| T-V34-13-05 | `evenodd`/`nonzero` rendus distincts et trous correctement signalés | auto |
| T-V34-13-06 | Courbe Bézier fermée : aucun PASS topologique sans vérification de courbe | auto |
| T-V34-13-07 | Auto-intersection V13-B → alerte localisée et export bloqué si CUT | auto |
| T-V34-13-08 | Chemin de lame doublé → `VECTOR_DUPLICATE_CUT`, aucun silence | auto |
| T-V34-13-09 | Simplification qui supprime un trou → refus, ancien digest conservé | auto |
| T-V34-13-10 | Simplification valide : métriques de contour/surface avant-après consignées | auto |
| T-V34-13-11 | Contour extérieur seul ≠ calques couleur, UX avertit | UI/auto |
| T-V34-13-12 | Quatre calques : IDs, palette, ordre et visibilité réversibles | auto/UI |
| T-V34-13-13 | Export d'édition garde les objets éditables, aucun raster déguisé | auto |
| T-V34-13-14 | Export Basic Cut ne contient ni clipping, gradients, scripts ni images | auto |
| T-V34-13-15 | SVG mm + viewBox : dimensions contrôlées et coordonnées finies | auto |
| T-V34-13-16 | 5 001 paths V13-F → `VECTOR_PATH_BUDGET` avant handoff | auto |
| T-V34-13-17 | 64 chemins G2.7 ≠ capacité du nouveau moteur, pas de promesse de 5 000 | auto/UI |
| T-V34-13-18 | Import SVG avec texte éditable/clip/gradient → export Cricut refuse ou convertit avec diff | auto |
| T-V34-13-19 | XML hostile DTD/XXE/script/externe → rejet sans exécution ni réseau | sécurité auto |
| T-V34-13-20 | PNG Print Then Cut inchangé lorsque seul SVG diagnostic demandé | auto |
| T-V34-13-21 | 12/24/50 objets : IDs uniques, aucun objet perdu ni tronqué silencieusement | auto |
| T-V34-13-22 | Révision source modifiée durant job → `STALE`, aucun commit | intégration auto |
| T-V34-13-23 | Retry même commande après ACK perdu → un seul commit, receipt rejoué | intégration auto |
| T-V34-13-24 | OOM GPU simulé → fallback manuel/CPU, projet et source inchangés | auto ; GPU terrain séparé |
| T-V34-13-25 | Clavier : choix contour/couches, revue alerte, Undo/Redo sans perte focus | UI/Windows |
| T-V34-13-26 | V13-G : guide de pli non converti en CUT ou SCORE par couleur | auto |
| T-V34-13-27 | Import SVG Basic Cut réel, dimensions et calques constatés, version Design Space enregistrée | DesignSpace |
| T-V34-13-28 | Coupe Explore 5 d'un contour troué, mesures et matière consignées | physique |
| T-V34-13-29 | Crash/lecture seule/disque plein : projet précédent et source intacts | auto/Windows |
| T-V34-13-30 | Traçabilité test→ticket→S/R33, axe preuve et SHA présents, aucun faux PASS | documentaire/auto futur |
```

## Lot 14 — `14_LANGAGE_FABRICATION.md` (30 scénarios)

- **Référence source** : [14_LANGAGE_FABRICATION.md](../roadmap-v3.4/14_LANGAGE_FABRICATION.md) (main@aa0ff9e7) ; **blob SHA** `3b7dd601c6f844f3a3d12b44bc971fc101133367`.
- **Index source** : `T-V34-14-01` L215 · `T-V34-14-02` L216 · `T-V34-14-03` L217 · `T-V34-14-04` L218 · `T-V34-14-05` L219 · `T-V34-14-06` L220 · `T-V34-14-07` L221 · `T-V34-14-08` L222 · `T-V34-14-09` L223 · `T-V34-14-10` L224 · `T-V34-14-11` L225 · `T-V34-14-12` L226 · `T-V34-14-13` L227 · `T-V34-14-14` L228 · `T-V34-14-15` L229 · `T-V34-14-16` L230 · `T-V34-14-17` L231 · `T-V34-14-18` L232 · `T-V34-14-19` L233 · `T-V34-14-20` L234 · `T-V34-14-21` L235 · `T-V34-14-22` L236 · `T-V34-14-23` L237 · `T-V34-14-24` L238 · `T-V34-14-25` L239 · `T-V34-14-26` L240 · `T-V34-14-27` L241 · `T-V34-14-28` L242 · `T-V34-14-29` L243 · `T-V34-14-30` L244.
- **Lignes originales intégrales et dans l'ordre** (statuts PROPOSÉS, jamais PASS par ce document) :

```text
| T-V34-14-01 | GUIDE_ONLY et CUT_CANDIDATE ne créent aucune assignation CUT sans confirmation | auto |
| T-V34-14-02 | SCORE ouvert accepté comme candidat ; CUT ouvert non sûr bloque la fabrication | auto |
| T-V34-14-03 | IDs, digest, unités mm et références invalides provoquent un refus non mutant | auto |
| T-V34-14-04 | PRINT sur PATH et SCORE sur RASTER_REGION refusés | auto |
| T-V34-14-05 | PRINT_THEN_CUT est recette composite ; ne devient pas une opération de PATH | auto |
| T-V34-14-06 | Compatibilité KNOWN_UNSUPPORTED bloque, UNKNOWN avertit sans promotion | auto |
| T-V34-14-07 | Source officielle datée et version du profil exigées pour KNOWN_SUPPORTED | auto |
| T-V34-14-08 | Une double coupe exacte CUT/CUT sur même support est détectée et localisée | auto |
| T-V34-14-09 | Croisement SCORE/CUT légitime est différencié d'une duplication exacte | auto |
| T-V34-14-10 | Score + Cut sans groupe d'alignement donne avertissement Attacher | auto/UI |
| T-V34-14-11 | Un groupe avec supports différents est refusé sans fusion implicite | auto |
| T-V34-14-12 | Projet boîte : deux types d'opérations et géométries distincts préservés | auto |
| T-V34-14-13 | Le guide d'export boîte inclut Score, Attacher, outil, matériau et contrôle mm | auto/UI |
| T-V34-14-14 | Import réel Design Space : Score choisi et Attach vérifié manuellement | Design Space |
| T-V34-14-15 | Essai carton : mesure pli/coupe et outil/version/matière consignés | physique |
| T-V34-14-16 | Pen + Cut garde DRAW distinct et propose guide Attacher | auto/UI/Design Space |
| T-V34-14-17 | Foil + Cut conserve FOIL et avertit sur support/outil non qualifiés | auto/UI/Design Space |
| T-V34-14-18 | Explore 5 rejette Engrave/Deboss Maker-only sans substitution | auto |
| T-V34-14-19 | A4 Print Then Cut n'utilise pas la pleine page comme zone de coupe | auto/UI |
| T-V34-14-20 | 12 escargots : PNG et contrat Print Then Cut restent distincts du SVG Cut | auto/Design Space |
| T-V34-14-21 | Smart Material sans tapis avec combinaison inconnue reste UNKNOWN | auto/UI |
| T-V34-14-22 | HTV multicouche exige miroir explicite par couche et rapport de décision | auto/UI |
| T-V34-14-23 | Tapis carte non déclaré bloque « prêt machine » sans empêcher brouillon | auto/UI |
| T-V34-14-24 | Pochoir fragile : ponts trop fins signalés sans fausse cote universelle | auto |
| T-V34-14-25 | Undo groupe CUT+SCORE restaure assignations, sans supprimer géométries | auto/Windows |
| T-V34-14-26 | Projet périmé / commande dupliquée : CAS/idempotence, aucun double commit | auto/Windows |
| T-V34-14-27 | 50 objets : prévol sans troncature silencieuse et résultats déterministes | auto/Windows |
| T-V34-14-28 | Mode sans IA / OOM simulé : formulaire manuel et aucun commit partiel | auto/Windows |
| T-V34-14-29 | Interface clavier/lecteur d'écran : opérations, avertissements, correctifs accessibles | UI/Windows |
| T-V34-14-30 | Export final refuse BLOCKED, brouillon WARN étiqueté ; aucun PASS externe inventé | auto/UI |
```

## Lot 15 — `15_PROFILS_EXPLORE5.md` (18 scénarios)

- **Référence source** : [15_PROFILS_EXPLORE5.md](../roadmap-v3.4/15_PROFILS_EXPLORE5.md) (main@aa0ff9e7) ; **blob SHA** `19cf7835044936e5cf2a2f894b5a42456c8fa8b4`.
- **Index source** : `T-V34-15-01` L105 · `T-V34-15-02` L106 · `T-V34-15-03` L107 · `T-V34-15-04` L108 · `T-V34-15-05` L109 · `T-V34-15-06` L110 · `T-V34-15-07` L111 · `T-V34-15-08` L112 · `T-V34-15-09` L113 · `T-V34-15-10` L114 · `T-V34-15-11` L115 · `T-V34-15-12` L116 · `T-V34-15-13` L117 · `T-V34-15-14` L118 · `T-V34-15-15` L119 · `T-V34-15-16` L120 · `T-V34-15-17` L121 · `T-V34-15-18` L122.
- **Lignes originales intégrales et dans l'ordre** (statuts PROPOSÉS, jamais PASS par ce document) :

```text
| T-V34-15-01 | La clé complète distingue outil, matière, support et version ; aucune résolution partielle réussie | auto |
| T-V34-15-02 | Support officiel de l'outil sans preuve de combinaison complète reste UNKNOWN | auto |
| T-V34-15-03 | Machine différente n'hérite pas silencieusement du verdict Explore 5 | auto |
| T-V34-15-04 | Un outil Maker-only ne devient jamais SCORE/CUT accepté sur Explore 5 | auto |
| T-V34-15-05 | Un outil absent et une combinaison supportée restent deux statuts indépendants | auto/UI |
| T-V34-15-06 | Une déclaration utilisateur ne crée aucune fausse preuve fabricant ou physique | auto |
| T-V34-15-07 | Scoring Tool conduit au guide Design Space « Score + Attacher » | auto/UI |
| T-V34-15-08 | Support stylo vérifie le marquage de compatibilité, pas une correspondance par couleur | auto/UI |
| T-V34-15-09 | Foil garde la feuille, l'outil et la matière distincts de Cut | auto |
| T-V34-15-10 | Tapis carte inconnu : aucune simulation de placement réellement certifiée | auto/UI |
| T-V34-15-11 | Smart Material sans tapis : type/largeur/longueur minimale contrôlés ; vinyle tiers rejeté sans tapis | auto/UI |
| T-V34-15-12 | Changement de version du profil invalide le prévol précédent sans toucher au projet | auto |
| T-V34-15-13 | Une feuille A4 n'est pas traitée comme un rectangle entièrement découpable | auto/UI |
| T-V34-15-14 | Export brouillon permis avec UNKNOWN, sans étiquette machine-ready | auto |
| T-V34-15-15 | Machine réelle : l'utilisateur confirme le matériel présent, les étapes Score+Cut et le changement d'outil | Windows + Design Space |
| T-V34-15-16 | Essai carton : largeur/alignement du pli et coupe consignés, avec outil/matière/tapis/date | physique |
| T-V34-15-17 | Lecture d'une archive historique conserve les profils/masques inchangés | auto |
| T-V34-15-18 | Relecture de source officielle manquante : statut UNKNOWN, pas PASS « par défaut » | auto |
```

## Lot 16 — `16_PATRONS_PARAMETRIQUES.md` (10 scénarios)

- **Référence source** : [16_PATRONS_PARAMETRIQUES.md](../roadmap-v3.4/16_PATRONS_PARAMETRIQUES.md) (main@aa0ff9e7) ; **blob SHA** `562af8bc7ceca562381e08251352dfd5bd6c2b69`.
- **Index source** : `T-V34-16-01` L272 · `T-V34-16-02` L273 · `T-V34-16-03` L274 · `T-V34-16-04` L275 · `T-V34-16-05` L276 · `T-V34-16-06` L277 · `T-V34-16-07` L278 · `T-V34-16-08` L279 · `T-V34-16-09` L280 · `T-V34-16-10` L281.
- **Lignes originales intégrales et dans l'ordre** (statuts PROPOSÉS, jamais PASS par ce document) :

```text
| T-V34-16-01 | Fixture 80/50/30/10 → bbox 140×110, aire 13000 mm², 5 CUT/8 SCORE ; aucune auto-intersection du contour extérieur | auto |
| T-V34-16-02 | Quatre fentes de 10 mm présentes, ouvertes et explicitement CUT ; aucun doublon exact ; jonctions de plis signalées mais non rejetées en bloc | auto |
| T-V34-16-03 | `T=0`, `T=H`, NaN, Inf, cote négative ou manquante → refus sans mutation ni valeur cachée | auto/UI |
| T-V34-16-04 | Carte 105×148 → développé 210×148, 1 CUT/1 SCORE ; pas de compatibilité tapis carte inventée | auto |
| T-V34-16-05 | Changement de paramètre → nouvelle proposition et prévol invalidé ; source, masques float32 et projet V1 inchangés | auto |
| T-V34-16-06 | Prévol export : mm/viewBox cohérents, chemins distincts, refus d'un doublon et d'une intersection non intentionnelle | auto |
| T-V34-16-07 | Sans modèle IA, sans ComfyUI et sans format V2, le calcul/aperçu/export brouillon reste possible via un harness de test isolé | auto/intégration future |
| T-V34-16-08 | UI novice : erreurs localisées, accès clavier, aucune mention « Score transmis » ou « prêt machine » avec profil UNKNOWN | UI/Windows |
| T-V34-16-09 | Import réel : Score choisi, Attacher vérifié, dimensions relevées et changement d'outil consigné ; pas de PASS automatique | Design Space |
| T-V34-16-10 | Coupon carton : coupe, plis, fentes, languettes et montage mesurés avec matière, outil, tapis, version et SHA exacts | physique |
```
