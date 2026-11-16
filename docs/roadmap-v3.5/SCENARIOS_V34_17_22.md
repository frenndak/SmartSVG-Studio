# SmartSVG V3.5 — Inventaire source des scénarios V3.4, lots 17 à 22

**Inventaire documentaire candidat, non normatif.** Photographie issue du commit `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`. Les lignes des recettes sont **reproduites sans modification**, avec lignes sources et SHA de fichiers. Aucun test qualifié comme exécuté par cet inventaire. Les liens exacts exigences/tickets et la qualification doivent être instruits dans une matrice distincte. Aucun scénario nouveau inventé. Les lots 23/24 contiennent la traçabilité/passation et ne fournissent pas de nouveau tableau de recettes uniques.

**Couverture vérifiée de ce segment : 69/69 identifiants uniques, lots 17 à 22.** Total historique attendu : 437.

## Lot 17 — `17_EXPORTS_DESIGNSPACE.md` (13 scénarios)

- **Référence source** : [17_EXPORTS_DESIGNSPACE.md](../roadmap-v3.4/17_EXPORTS_DESIGNSPACE.md) (main@aa0ff9e7) ; **blob SHA** `4c13bfe529f672d68a0c66a77c07fcd0068d5170`.
- **Index source** : `T-V34-17-01` L85 · `T-V34-17-02` L86 · `T-V34-17-03` L87 · `T-V34-17-04` L88 · `T-V34-17-05` L89 · `T-V34-17-06` L90 · `T-V34-17-07` L91 · `T-V34-17-08` L92 · `T-V34-17-09` L93 · `T-V34-17-10` L94 · `T-V34-17-11` L95 · `T-V34-17-12` L96 · `T-V34-17-13` L97.
- **Lignes originales intégrales et dans l'ordre** (statuts PROPOSÉS, jamais PASS par ce document) :

```text
| T-V34-17-01 | Les quatre choix exportent des contrats distincts ; le SVG multicouche n'est jamais stocké sous `Artifact.use=editable_svg` V1 | auto |
| T-V34-17-02 | Un PNG Print Then Cut conserve pixels/alpha/empreinte ; aucun SVG de diagnostic n'est automatiquement ajouté comme seconde coupe | auto |
| T-V34-17-03 | Basic Cut refuse trou ambigu, contour ouvert non autorisé, double coupe, SVG actif et dimensions non physiques | auto |
| T-V34-17-04 | SVG multicouche conserve ordre, groupes, repère mm et IDs ; aucune conversion silencieuse en SVG d'édition | auto |
| T-V34-17-05 | SVG d'édition conserve styles/couches dans le profil autorisé ; pas de mention « Basic Cut prêt » | auto |
| T-V34-17-06 | Fixture boîte 140×110 : 5 CUT/8 SCORE identifiés, guide « Score → Attacher → vérifier mm/outils » ; aucune opération transmise par SVG | auto/UI |
| T-V34-17-07 | Stale SHA entre prévol et publication → refus sans mutation du projet ni remplacement d'un export antérieur | auto/concurrence |
| T-V34-17-08 | Échec au 2e artefact d'un paquet → manifeste succès absent, ancien paquet intact, reprise sans écrasement | auto/fault-injection |
| T-V34-17-09 | Guide A4 Explore 5 : paysage sur tapis, flèche haut-gauche, repères imprimés par Design Space, dimensions à confirmer | auto/UI |
| T-V34-17-10 | Novice clavier : choisir chacun des quatre formats, voir avertissements et ouvrir résultat sans perte de focus | UI/Windows |
| T-V34-17-11 | Import réel PNG Flat Graphic + SVG Basic/MultiCut : version Design Space, dimensions, calques et comportement constatés | DesignSpace |
| T-V34-17-12 | Import réel boîte : Score et Attacher manuels, outil/matière et positions vérifiés, capture privée de preuve | DesignSpace |
| T-V34-17-13 | Coupon Explore 5 : sticker et boîte testés, mesures et matière/outils/tapis/versions/SHA consignés | physique |
```

## Lot 18 — `18_ATELIER_GRAPHIQUE.md` (10 scénarios)

- **Référence source** : [18_ATELIER_GRAPHIQUE.md](../roadmap-v3.4/18_ATELIER_GRAPHIQUE.md) (main@aa0ff9e7) ; **blob SHA** `466fd3652524fe71ca9893e2c2e109376b4c6f48`.
- **Index source** : `T-V34-18-01` L94 · `T-V34-18-02` L95 · `T-V34-18-03` L96 · `T-V34-18-04` L97 · `T-V34-18-05` L98 · `T-V34-18-06` L99 · `T-V34-18-07` L100 · `T-V34-18-08` L101 · `T-V34-18-09` L102 · `T-V34-18-10` L103.
- **Lignes originales intégrales et dans l'ordre** (statuts PROPOSÉS, jamais PASS par ce document) :

```text
| T-V34-18-01 | Sélection des 12 escargots de démonstration : aucun `Subject` ni archive créée, aucune fonction réelle prétendue | auto/UI ; V34-041/132 |
| T-V34-18-02 | Choisir `subject_id` synchronise vignette/canevas/propriétés ; réordonner les vignettes ne change jamais la cible | auto/UI ; V34-132 |
| T-V34-18-03 | Deux masques float32 A/B : `add` et `erase` sur A préservent B et tous les pixels non peints bit à bit ; SHA archive inchangé en preview | auto/CPU ; V34-132 |
| T-V34-18-04 | Preuve b1 absente/ambiguë ou SHA masque invalide : preview refusé, aucun `mask_index` déduit du DOM | auto/CPU ; V34-132 |
| T-V34-18-05 | SHA modifié, double clic, changement de sélection, réponse tardive : aucun commit ni cible différente, message et reprise | auto/UI ; V34-041/132 |
| T-V34-18-06 | Annuler un brouillon n'écrit rien ; Undo/Redo **après b2b** relit les révisions et n'efface jamais les exports | auto/intégration ; V34-035/038 |
| T-V34-18-07 | Boîte 140×110 : CUT et SCORE restent deux groupes sémantiques distincts, aucun transfert Score automatique | auto/UI ; V34-133 |
| T-V34-18-08 | Visibilité, solo, zoom et calques temporaires ne créent aucun champ V1 ; mm inconnus non inventés | auto/UI ; V34-133 |
| T-V34-18-09 | Sélection, outils, erreurs, validation et retour accessibles au clavier avec focus et annonces FR | UI/a11y puis Windows ; V34-045/133 |
| T-V34-18-10 | Conflit de notes G2.2, panne d'écriture ou backup pending : pas de faux succès, projet précédent conservé, récupération explicite | auto/fault-injection puis Windows ; V34-044/132 |
```

## Lot 19 — `19_PLANCHES_NESTING.md` (12 scénarios)

- **Référence source** : [19_PLANCHES_NESTING.md](../roadmap-v3.4/19_PLANCHES_NESTING.md) (main@aa0ff9e7) ; **blob SHA** `e6ac52be45c79999a2ed043c44ed0c972fa8f007`.
- **Index source** : `T-V34-19-01` L76 · `T-V34-19-02` L77 · `T-V34-19-03` L78 · `T-V34-19-04` L79 · `T-V34-19-05` L80 · `T-V34-19-06` L81 · `T-V34-19-07` L82 · `T-V34-19-08` L83 · `T-V34-19-09` L84 · `T-V34-19-10` L85 · `T-V34-19-11` L86 · `T-V34-19-12` L87.
- **Lignes originales intégrales et dans l'ordre** (statuts PROPOSÉS, jamais PASS par ce document) :

```text
| T-V34-19-01 | 12 sujets synthétiques validés : 12 instances uniques dans les pages et le rapport, aucune démo fictive exportée | auto/UI |
| T-V34-19-02 | 24 sujets : aucune collision de contours de coupe, aucun hors-zone sur support **qualifié**, IDs et dimensions conservés | auto/QA |
| T-V34-19-03 | 50 instances : 50 statuts individuels sans troncature, traitement par lots ; pic de masques actifs borné | auto/Windows mémoire |
| T-V34-19-04 | Même snapshot/paramètres : placements, pages, erreurs et ordre identiques ; ordre des vignettes modifié sans effet | auto |
| T-V34-19-05 | Deux placements verrouillés inchangés après recalcul ; conflit de verrou signalé sans déplacement silencieux | auto/UI |
| T-V34-19-06 | Rotation interdite, groupe Score+Cut ou texte orienté : aucun pivot implicite ni séparation des opérations | auto/UI |
| T-V34-19-07 | Zone A4 Print Then Cut inconnue : aucune mention « compatible/garanti » ; PNG et guide distincts du SVG Cut | auto/UI puis DesignSpace |
| T-V34-19-08 | Après changement d'offset/masque/échelle/profil/SHA, cache et planche périmés refusés ; projet intact | auto/concurrence |
| T-V34-19-09 | Pause après 17/50 puis reprise : 50 états finaux, 0 instance traitée deux fois dans le manifeste publié | auto/fault-injection Windows |
| T-V34-19-10 | OOM simulé ou disque plein à la page 2 : ancien paquet intact, état PARTIAL explicite, reprise vérifiée | auto/fault-injection |
| T-V34-19-11 | Projet V1 incapable de persister 50 masques float32 : refus explicite ; exports externes bornés possibles sans falsifier V1 | auto |
| T-V34-19-12 | UI clavier : sélectionner/verrouiller/comparer/corriger/reprendre avec focus et annonces FR ; Design Space/Explore 5 restent NON_EXECUTE sans preuves séparées | UI/Windows ; DesignSpace/physique séparés |
```

## Lot 20 — `20_BIBLIOTHEQUE_VARIANTES_CSV.md` (10 scénarios)

- **Référence source** : [20_BIBLIOTHEQUE_VARIANTES_CSV.md](../roadmap-v3.4/20_BIBLIOTHEQUE_VARIANTES_CSV.md) (main@aa0ff9e7) ; **blob SHA** `b58e891ce65edcfa5ccabe46c24968036781e92a`.
- **Index source** : `T-V34-20-01` L72 · `T-V34-20-02` L73 · `T-V34-20-03` L74 · `T-V34-20-04` L75 · `T-V34-20-05` L76 · `T-V34-20-06` L77 · `T-V34-20-07` L78 · `T-V34-20-08` L79 · `T-V34-20-09` L80 · `T-V34-20-10` L81.
- **Lignes originales intégrales et dans l'ordre** (statuts PROPOSÉS, jamais PASS par ce document) :

```text
| T-V34-20-01 | Index supprimé/corrompu puis reconstruit ⇒ mêmes `project_id/SHA/santé` pour tous les projets valides, aucune archive réécrite | auto + Windows |
| T-V34-20-02 | 105 projets valides ⇒ le 101e est trouvable par recherche/pagination ; sidecars non comptés comme projets | auto + UI |
| T-V34-20-03 | Symlink, archive hostile, projet cassé ⇒ aucun parcours hors racine ; entrée non saine visible sans ouverture dangereuse | auto + Windows |
| T-V34-20-04 | Clone d'un V1 avec `Subject` et snapshot float32 ⇒ nouveau `project_id`, octets source et masque identiques, preuves et SHA internes vérifiés, original inchangé | auto + Windows |
| T-V34-20-05 | Deux duplications concurrentes vers même nom ⇒ au plus un clone sain ; aucun écrasement ni suppression de l'autre | auto + Windows |
| T-V34-20-06 | Tag/favori/provenance V1 non conservé par writer legacy ⇒ pas d'annonce « portable » ; si extension qualifiée, save/reload via writers pertinents préserve exactement les champs | auto + UI |
| T-V34-20-07 | CSV synthétique 30 lignes dont accents, doublons de prénoms et valeurs malformées ⇒ chaque ligne a un statut et un ID stable ; glyphes manquants signalés, aucun texte silencieusement perdu | auto + UI |
| T-V34-20-08 | CSV avec formule, séparateur mal formé, en-têtes dupliqués et champs géants ⇒ aucune formule exécutée, aucune requête réseau, erreurs bornées par ligne/fichier | auto |
| T-V34-20-09 | Export interrompu après 17/30, reprise même SHA ⇒ exactement 30 résultats uniques ou erreurs explicites ; nouveau SHA ⇒ refus de reprise périmée | auto + Windows |
| T-V34-20-10 | Parcours étiquette PNG puis SVG d'édition ⇒ types séparés, dimensions/provenance contrôlées, aucune certification Design Space/physique sans preuves propres | auto ; DesignSpace/physique séparés |
```

## Lot 21 — `21_WINDOWS_OFFLINE_RECOVERY.md` (10 scénarios)

- **Référence source** : [21_WINDOWS_OFFLINE_RECOVERY.md](../roadmap-v3.4/21_WINDOWS_OFFLINE_RECOVERY.md) (main@aa0ff9e7) ; **blob SHA** `8700846208315f405b7f60266fabf8181e160ff4`.
- **Index source** : `T-V34-21-01` L60 · `T-V34-21-02` L61 · `T-V34-21-03` L62 · `T-V34-21-04` L63 · `T-V34-21-05` L64 · `T-V34-21-06` L65 · `T-V34-21-07` L66 · `T-V34-21-08` L67 · `T-V34-21-09` L68 · `T-V34-21-10` L69.
- **Lignes originales intégrales et dans l'ordre** (statuts PROPOSÉS, jamais PASS par ce document) :

```text
| T-V34-21-01 | Lancement natif avec `ComfyUI/nodes/server/folder_paths/torch` absents ; accueil + ouverture V1 synthétique + sauvegarde manuelle, aucun import obligatoire de ces modules | auto (imports interceptés) + Windows neuf | V34-019 |
| T-V34-21-02 | Extension legacy V21.15.2 chargée avec nœuds/ports/workflows inchangés après installation et rollback documenté | auto ciblé + ComfyUI Windows | V34-020, V34-139 |
| T-V34-21-03 | Réseau interdit par interception DNS/HTTP au démarrage, import, export CPU, refus IA et ouverture projet : zéro requête, zéro poids téléchargé | auto + Windows hors ligne, trace réseau expurgée | V34-023, V34-140 |
| T-V34-21-04 | Paquet modifié, incomplet, de provenance inconnue ou SHA incorrect : refus avant activation ; installation courante et données identiques | auto + Windows ; SHA avant/après | V34-139 |
| T-V34-21-05 | Coupure injectée pendant staging/activation et binaire Windows verrouillé : ancienne ou nouvelle version valide au redémarrage, jamais installation partielle active | auto simulation + Windows réel | V34-139 |
| T-V34-21-06 | Mise à jour puis rollback logiciel : mêmes octets `.smartsvg`, `.previous`, `.pending-backup`, masques float32, modèles consentis et exports | auto + Windows, empreintes comparées | V34-139, V34-022 |
| T-V34-21-07 | Chemins Unicode/espaces, compte sans admin, disque plein, fichier en lecture seule, antivirus ou répertoire synchronisé : erreur explicite et absence d'écrasement | auto injection + Windows cas réels séparés | V34-139, V34-022 |
| T-V34-21-08 | Projet sain, corrompu, version future et `PENDING_BACKUP_REVIEW_REQUIRED` : aucune restauration sans confirmation ; après accord, SHA et projet revalidés | auto existant G1.4 étendu + Windows | V34-022, V34-140 |
| T-V34-21-09 | Rapport diagnostic exporté : aucune image/chemin privé/secret ; états « présent », « testé », « absent » distincts, clavier et messages FR utilisables | auto filtrage + Windows UX | V34-024, V34-140 |
| T-V34-21-10 | Désinstallation : aucun projet/backup/modèle utilisateur supprimé par défaut ; suppression facultative exige confirmation distincte | auto + Windows réel | V34-139 |
```

## Lot 22 — `22_VALIDATION_CORPUS_PREUVES.md` (14 scénarios)

- **Référence source** : [22_VALIDATION_CORPUS_PREUVES.md](../roadmap-v3.4/22_VALIDATION_CORPUS_PREUVES.md) (main@aa0ff9e7) ; **blob SHA** `6fa98816ae2a8048471f6625d3c099df171fb0fb`.
- **Index source** : `T-V34-22-01` L44 · `T-V34-22-02` L45 · `T-V34-22-03` L46 · `T-V34-22-04` L47 · `T-V34-22-05` L48 · `T-V34-22-06` L49 · `T-V34-22-07` L50 · `T-V34-22-08` L51 · `T-V34-22-09` L52 · `T-V34-22-10` L53 · `T-V34-22-11` L54 · `T-V34-22-12` L55 · `T-V34-22-13` L56 · `T-V34-22-14` L57.
- **Lignes originales intégrales et dans l'ordre** (statuts PROPOSÉS, jamais PASS par ce document) :

```text
| T-V34-22-01 | Quatre sorties | 4 artefacts synthétiques : PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche et SVG d'édition restent typés distinctement, mm/viewBox vérifiés et aucun statut machine-ready. | auto | V34-005/129/130 |
| T-V34-22-02 | Projet float32 | Save/reload V1 avec 2 Subject : identités, sources, SHA et octets float32 strictement identiques, aucune mutation du fichier source. | auto | V34-018/022/132 |
| T-V34-22-03 | Crash et archive hostile | ZIP hostile, disque plein, lock et interruption de sauvegarde : refus sans perte du dernier projet sain ni effacement des sidecars ; recovery sous CAS et confirmation. | auto + Windows | V34-022/140 |
| T-V34-22-04 | Retouche du bon sujet | Geste add/erase sur Subject A : B inchangé bit-à-bit ; A inchangé hors zone ; révision obsolète refusée, cancel sans écriture. | auto + UI | V34-132/133 |
| T-V34-22-05 | Planches 12 escargots | 12 sujets synthétiques distincts : 12 IDs uniques, pas de collision/hors-page, dimensions mm ; PNG Print Then Cut sans faux repères capteur SmartSVG. | auto + UI | V34-129/134/135 |
| T-V34-22-06 | A4 et Design Space | Importer PNG, relever version Design Space et taille ; feuille A4 placée en paysage sur tapis, repères imprimés par Design Space et non SmartSVG. | Design Space + Windows | V34-122/129/130 |
| T-V34-22-07 | Coupon stickers | Imprimer et découper 12 stickers en une session Design Space ; relever 12 contours, erreurs, mesures, matière, tapis, imprimante et calibration ; critères pré-déclarés. | physique | V34-124/129/135 |
| T-V34-22-08 | Boîte paramétrique | Boîte 80×50×30 mm, languettes 10 mm : développé 140×110 mm ; CUT extérieur/fentes ≠ SCORE plis ; conflit de segments détecté. | auto + UI | V34-106/109/126/127/128 |
| T-V34-22-09 | Boîte Score/Attach | Importer SVG, sélectionner manuellement Score, garder Basic Cut, Attacher ; contrôler dimensions et superposition, version Design Space, capture expurgée. | Design Space + Windows | V34-111/120/124/130 |
| T-V34-22-10 | Coupon carton | Couper/rainurer/plier un coupon : consigner changement d'outil, matière, tapis, dimensions de plis et coupes, écarts et tolérances déclarées avant essai. | physique | V34-124/128 |
| T-V34-22-11 | Batch 50 et reprise | 12/24/50 instances par lots bornés ; interruption après 17/50 puis reprise sans doublon au même SHA ; SHA modifié = refus ; pic RAM/VRAM mesuré. | auto + Windows (+ GPU si activé) | V34-074/134/135 |
| T-V34-22-12 | IA facultative | Aucun modèle installé : mode manuel/CPU ; téléchargement refusé/corrompu, OOM et interruption : projet intact, réseau jamais implicite, fallback explicite. | auto + Windows (+ GPU si modèle) | V34-078/079/086/140 |
| T-V34-22-13 | Bibliothèque et CSV | 105 projets synthétiques sans troncature ; index corrompu reconstruit ; 30 lignes CSV (accents, formules, erreurs) et reprise 17/30 sans exécution de formule ni doublon. | auto + UI + Windows | V34-136/137/138 |
| T-V34-22-14 | Windows et UX | Démarrage natif sans ComfyUI, offline intercepté, package altéré refusé, rollback sans perte ; clavier, zoom 125/150 %, messages FR et rapport expurgé. | auto + Windows + UX | V34-019/020/139/140 |
```
