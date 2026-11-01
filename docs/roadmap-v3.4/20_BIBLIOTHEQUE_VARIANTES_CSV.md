# SmartSVG Studio V3.4 — Lot 20/24 : bibliothèque, modèles, variantes et CSV

**DRAFT de conception — 29 octobre 2026.** V3.3 demeure **ACTIVE**. Périmètre strictement hérité de **F09/F10/F12, P05/P07/P08, G6/G7, S-017/S-024/S-038/S-039/S-041/S-091/S-097/S-098 et R33-010/011/012**. Aucun ajout de fonction, code, archive ou tâche planifiée. **Tous les tests proposés ci-dessous : NON_EXECUTE** (auto/UI/Windows/Design Space/physique). Référence de lecture : `main@fdbda304beb77d97340a8be4dd5c5e9cefde15f4`, branche documentaire issue de `fff374e5147689165839bd76e742713d714ff147`. Relecture des lots 05, 17, 18 et 19.

## 1. État réel, contre-expertise du lot 19 et trois écarts à résoudre

1. **Le navigateur G2.2 existe mais n'est pas une bibliothèque complète.** `engine/smartsvg_core/project_workspace_g22.py::ManagedWorkspace.list_projects` parcourt les fichiers `*.smartsvg`, regroupe primaire et sidecars, trie les noms, puis retourne **au plus 100** projets ; `inspect` vérifie santé et SHA. Aucun index de tags, collections, favoris, miniatures ni recherche exhaustive n'est démontré. **Correction :** catalogue paginé/filtré à partir des projets vérifiés, index dérivé jetable et reconstructible ; le plafond de présentation actuel n'est pas une limite métier silencieuse. Ne pas afficher `.previous` et `.pending-backup` comme projets distincts ; signaler les projets à réparer.

2. **Le format V1 ne possède pas de contrat bibliothèque/variantes typé.** `project_archive.py::LoadedProject` contient `project_id`, `document`, `operations`, sources, masques, sujets, artefacts et ressources ; `SCHEMA_VERSION=smartsvg-project/1`. Le document JSON est extensible techniquement, mais cela **ne prouve pas** que tous les anciens writers préservent des champs nouveaux. `ManagedWorkspace.create` crée depuis un PNG et un profil prédéfini, **pas** depuis une archive complète. **Correction :** cloner via le chargeur et le writer validés, conserver octets originaux/float32, changer seulement l'identité de projet et la provenance *si son aller-retour est qualifié* ; jamais reconstruire un projet depuis une miniature ou appeler `create` pour « Dupliquer ». Ne pas imposer V2 pour naviguer, ouvrir ou dupliquer un projet V1 sain.

3. **Le lot 19 sait spécifier un rapport de batch, pas une autorité pour les variantes.** Le manifeste d'export et le cache de placement sont dérivés ; ils ne peuvent devenir la définition persistante d'un modèle ni d'une variante. **Correction :** modèle = projet/gabarit approuvé et versionné ; variante = paramètres validés appliqués à une révision figée ; index, miniatures et rapports = vues/reçus reconstructibles. Réutiliser le job manager du lot 19 et les quatre contrats d'export du lot 17, sans file d'attente, moteur de rendu ou prévol parallèles.

**Prouvé dans le dépôt :** `ManagedWorkspace.list_projects/inspect/create/update_notes`, `load_project/save_project`, `save_with_recovery`, `Subject` G1.2, CAS par SHA, limites ZIP V1 et les anciens exports. **Non prouvé :** bibliothèque G7 complète, tags persistants portables, moteur CSV/variantes, clonage complet, réindexation à grande échelle, récupération d'un lot CSV, performances Windows et essais Cricut. La démo des escargots de l'Atelier n'est pas un projet réel.

## 2. Autorité, frontières et dépendances minimales

- **Source de vérité :** chaque fichier `.smartsvg` sain et sa révision SHA ; source originale et snapshots float32 inchangés. Le cache de catalogue (`project_id`, chemin géré, SHA, santé, date/nom affichés, miniature calculée, tags effectivement disponibles) est **dérivé**, versionné et supprimable. Sa corruption provoque une reconstruction, jamais la réécriture des projets.
- **Métadonnées utilisateur :** les tags/collections/favoris *portables* doivent être dans un document de projet dont l'écriture/relecture est qualifiée. Pour V1, une petite extension **proposée et facultative** de `document.json` peut être expérimentée sous CAS et tests de round-trip avec tous les writers pertinents ; si la préservation échoue, ne pas l'écrire et indiquer « préférences locales non portables » lorsque celles-ci sont utilisées. Une base de préférences locale ne peut pas être annoncée comme reconstructible depuis les seuls projets. Aucune V2 obligatoire pour le catalogue minimal.
- **Identités et duplication :** `project_id` du clone neuf et distinct ; identités `source_id/mask_id/subject_id` internes conservées **dans l'espace de noms du nouveau projet**, si les preuves de liaison restent valides ; provenance `parent_project_id` + `parent_sha256` uniquement dans un champ de document accepté et relu, sinon afficher explicitement « provenance non persistée » et ne pas promettre le lien. La copie d'un ZIP sous un autre nom sans mise à jour de `project_id` est interdite. Ne pas fabriquer de nouveau `subject_id` à partir de la position d'un masque.
- **Modèles et variantes :** projet modèle en lecture seule pendant la préparation ; rendu/aperçu d'une variante = projection dérivée de `template_sha256`, valeurs CSV et identifiant de ligne. Aucune modification de l'original ni de ses masques. Le stockage durable d'une recette dans V1 n'est autorisé que si un writer existant et un round-trip vérifié le supportent ; sinon l'export reste explicitement externe et le projet ne prétend pas mémoriser une recette non persistée. V2 reste une option de migration explicite, jamais un gate G3.3.
- **Jobs et sorties :** réutiliser la reprise par unité du lot 19 (V34-135), l'export et le manifeste publié en dernier du lot 17 (V34-129/131), les contrôles texte/police G6 et le prévol des lots 14–15. Le manifeste des 30 exports est un reçu, **pas** une seconde autorité de projet.
- **Obligatoire pour la première tranche :** lecture saine V1, SHA, liste paginée/recherche, ouverture/duplication sans écrasement, prévisualisation d'un modèle, contrôle des valeurs CSV, export via le moteur existant. **Parallélisable :** UI Atelier, retouches G3.3e-b2a, tests PNG/SVG sur fixtures, amélioration des miniatures, qualification Windows. **Non prérequis :** bootstrap autonome, IA, RTX 3070, ComfyUI en graphe, V2, bus de commandes universel, catalogue visuel intelligent.

**Réemploi concret (chemins déjà existants) :** `engine/smartsvg_core/project_workspace_g22.py`, `project_archive.py`, `project_contracts.py`, `project_recovery.py`, `editor_session_g23.py`, `mask_snapshot_g24.py`, `subject_identity_g33e.py`, `engine/web/js/smartsvg_express_atelier_preview.html`, `engine/production_v211.py`, `engine/smartsvg_cricut/direct_import_v218.py`. **Futurs emplacements possibles, non existants :** `engine/smartsvg_library/catalog_g7.py`, `engine/smartsvg_library/variants_g7.py` et une vue JS dédiée ; leurs noms sont indicatifs, à choisir après revue des modules existants.

## 3. Parcours UX et wireframe minimal

**Novice — retrouver et dupliquer :** Accueil → « Reprendre » → bibliothèque → recherche par nom/usage/matière si métadonnées disponibles → vignette avec statut `SAIN / À RÉPARER / RESSOURCE MANQUANTE` → « Ouvrir » ou « Dupliquer ». Dupliquer demande un nom distinct, affiche « Copie indépendante, original conservé », valide la santé du projet et les empreintes, puis crée une nouvelle archive par publication atomique. Si la provenance ne peut pas être enregistrée dans V1 sans perte, le message le précise avant validation. Un projet corrompu reste visible avec « Examiner/Récupérer », pas supprimé de la liste.

**Expert — 30 étiquettes personnalisées :** Ouvrir un gabarit approuvé → choisir les champs texte/numéro/date/couleur existants → importer CSV local → choisir colonnes et encodage → contrôler 30 lignes, accents, glyphes, débordements et doublons de noms → prévisualiser chaque variante → exporter par lots avec un rapport par ligne → corriger et relancer les seules lignes `FAILED/NEEDS_REVIEW`. Le fichier CSV est lu comme **donnée**, jamais exécuté ; aucune formule ni URL ne déclenche de calcul ou d'accès réseau. Le `template_sha256` reste épinglé jusqu'à la fin ; toute modification du modèle invalide la reprise.

```text
[Bibliothèque] [Rechercher…] [Favoris] [Collections] [Trier ▾] [Recharger]
[Projets 1–N / pages]  [Vignette] [Nom] [Révision SHA…] [Santé] [Ouvrir]
[Projet sélectionné] [Dupliquer] [Variante] [Dossier de sortie] [Récupérer…]
[Modèle] [Champs disponibles] [Importer CSV] [Associer colonnes]
[30 lignes : 27 prêtes · 2 à revoir · 1 bloquée] [Prévisualiser ligne]
[Produire] [Pause] [Reprendre] [Rapport par ligne] [Relancer les erreurs]
[Message : index reconstruit / projet obsolète / caractère non pris en charge]
```

**Règle d'interface :** masquer les actions incompatibles avec la santé du projet, mais garder la récupération accessible. « Reprendre le dernier travail » vérifie à nouveau le SHA ; jamais de restauration silencieuse d'une copie antérieure. Les états et erreurs sont en français, lisibles au clavier et exposés via une zone de statut accessible.

## 4. Contrats de traitement et erreurs (spécification, NON implémentée)

**Catalogue :** énumérer uniquement le répertoire géré autorisé ; rejeter les symlinks, chemins hors racine et noms non conformes ; grouper primaire/previous/pending par nom ; utiliser `inspect_project` puis `load_project` pour les sains ; construire des fiches paginées avec SHA et statut. Une miniature est produite uniquement depuis une ressource admise et bornée ; ne jamais charger tous les masques/ZIP en mémoire pour une grille. Clé cache = SHA du projet + version de rendu ; entrée absente/corrompue ⇒ recalcul. Suppression de l'index ⇒ mêmes projets et états après réindexation, à l'exception des préférences explicitement locales non portables.

**Dupliquer :** nom cible validé selon `ManagedWorkspace.NAME` (1–48 caractères ASCII alphanumériques, `_` ou `-`, sans suffixe réservé) ; relecture de la source sous son SHA ; vérifier qu'aucune cible/sidecar n'existe ; charger l'archive, préparer une copie indépendante en changeant `project_id` ; vérifier la cohérence des ressources, des références et des preuves float32 ; publier via `save_with_recovery` avec refus d'écrasement, relire et vérifier l'archive cible, l'original et leurs SHA. **Point à prototyper :** le writer de récupération ne doit pas remplacer une cible apparue entre contrôle et publication ; un verrou et une création exclusive doivent protéger cette fenêtre de concurrence. En cas d'échec, original inchangé, aucun clone annoncé, temporaires nettoyés sans supprimer une cible étrangère. Une migration V2 reste un acte séparé.

**Variantes CSV :** détection contrôlée UTF-8/UTF-8-BOM ; délimiteur explicite `;` ou `,` ; refus des fichiers binaires, colonnes ambiguës, en-têtes dupliqués après normalisation Unicode NFC, champs requis manquants, lignes démesurées, nombre de lignes supérieur au budget mesuré et colonnes non mappées lorsqu'elles affectent le résultat. Ne pas deviner un texte caché ou un glyphe manquant. Les champs `prenom/numero/date/couleur` sont des exemples hérités, pas un nouveau moteur d'expressions. Les cellules commençant par `=`, `+`, `-`, `@` restent du **texte littéral** (et sont échappées si un rapport CSV est ouvert dans un tableur) ; jamais d'évaluation. Chaque sortie possède un identifiant déterministe basé sur SHA du modèle + identifiant de ligne + valeurs canoniques + paramètres d'export ; ne pas utiliser seulement le prénom comme nom de fichier. Les erreurs de ligne n'annulent pas les sorties déjà validées, mais le manifeste final indique `PARTIAL`. Reprise seulement si SHA modèle, mapping, paramètres et profil inchangés ; sinon `STALE_RESTART_REQUIRED`.

**Quatre exports :** PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche et SVG d'édition restent des contrats différents. Les étiquettes CSV n'autorisent aucune supposition sur le support ni sur les dimensions ; prévol des profils/units et guide Design Space existants. Une sortie non qualifiée est `EXPORTED_UNVERIFIED`, jamais « prête à découper » sans preuve.

| Situation | Comportement attendu / message utilisateur |
|---|---|
| Index absent/corrompu | « Reconstruction du catalogue » ; aucun projet modifié ; mêmes fiches saines après rescan |
| Plus de 100 projets | Pagination complète ; aucune disparition silencieuse du 101e |
| Projet/sidecar corrompu ou symlink | Projet signalé, lien dangereux ignoré, récupération explicite uniquement |
| Clone concurrent ou nom déjà utilisé | `PROJECT_ALREADY_EXISTS` ; original et cible existante inchangés |
| Changement de SHA pendant copie ou rendu | `PROJECT_CHANGED` ; abandon sans écriture ni rebind d'identité |
| Tags non préservés par writer V1 | Désactiver l'écriture portable ; préférences locales clairement signalées, pas de faux lien de provenance |
| CSV invalide, glyphe absent, texte débordant | Ligne `NEEDS_REVIEW/FAILED`, diagnostic précis ; autres lignes conservées |
| Annulation, disque plein, export partiel | `PARTIAL/CANCELLED`, reprise vérifiée, aucun écrasement des anciens exports |
| Source, masque float32 ou profil modifié | Invalider aperçu/cache et résultat périmé ; demander nouvelle validation |

## 5. Tests de recette proposés (tous NON_EXECUTE)

| Test | Assertion exacte attendue | Preuve future |
|---|---|---|
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

**Fixtures :** projets V1 synthétiques avec/sans `Subject` et snapshot float32, 105 petits projets temporaires, index volontairement corrompu, symlink de test, deux writers concurrents, CSV synthétique 30 lignes dont accents/erreurs/formules littérales, 12 escargots synthétiques non présentés comme photos réelles, boîte paramétrique du lot 16. Aucun visuel privé ou poids de modèle dans le dépôt public. Mesurer p50/p95 d'ouverture/recherche/miniature et pic RAM sur bibliothèque volumineuse ; seuils à fixer **après mesure**, pas de chiffre fictif.

## 6. Tickets d'implémentation utiles, sans nouvelle dépendance

| Ticket | Priorité / héritage | Livrable pressenti (non existant) | Test, preuve, DoD |
|---|---|---|---|
| **V34-136 — Catalogue reconstructible** | P1 ; S-024/S-041/S-091, R33-010 ; réemploi G2.2 et V34-035 | Projection paginée/recherche/miniatures/santé depuis `.smartsvg`, sans store d'autorité | T-V34-20-01/02/03 ; auto+Windows+UI ; reconstruction sans mutation ni troncature, erreurs visibles |
| **V34-137 — Duplication et variantes de projet** | P1 ; S-017/S-041/S-097/S-098, R33-010 ; dépend V34-136 pour UX, **pas pour moteur** | Clone sûr sous CAS, identités et provenance qualifiées, vue modèles/variantes réutilisant G6 | T-V34-20-04/05/06 ; auto+Windows ; original/float32 inchangés, clone relu, conflit sûr, aucun champ V1 non qualifié |
| **V34-138 — CSV et reprise personnalisée** | P1 ; S-038/S-039/S-091, R33-011/012 ; dépend G6 texte + V34-135 (jobs) + V34-129/131 (exports), **pas V2/IA** | Validation CSV, aperçu par ligne, sorties typées et relance ciblée via jobs/export existants | T-V34-20-07/08/09/10 ; auto+UI+Windows puis DesignSpace/physique séparés ; 30 lignes traçables, pas de doublon/écrasement |

**DoD commune :** tests ajoutés au dépôt moteur par une future PR d'implémentation, comparaison des SHA source/projet, preuve de rollback et réouverture, contrôles de sécurité, messages FR/accessibilité, absence de deuxième writer/cache/job manager ; statut `SPECIFIE` jusqu'à code et preuves. Les tests documentés ici ne sont pas des tests passés.

## 7. Contre-expertise croisée, risques et reprise

- **Lot 19 → 20 :** la reprise par instance ne doit pas être dupliquée pour les lignes CSV ; une même logique de job et de manifeste externe doit servir les planches et variantes. Une variante ne peut jamais modifier rétroactivement la géométrie validée d'une planche déjà exportée.
- **Lot 05 → 20 :** le schéma V2 et ses receipts sont des propositions. Le catalogue et le clonage V1 doivent être qualifiés séparément ; les métadonnées non conservables ne doivent pas devenir des promesses cachées.
- **Lot 17 → 20 :** un export CSV partiel n'est pas un succès global ; le manifeste final publié en dernier indique les SHA et erreurs par ligne, sans réécrire un `.smartsvg` pour enregistrer chaque PNG.
- **Risques ouverts :** fidélité des métadonnées V1 dans tous les writers, création exclusive sous Windows et répertoires synchronisés, police/licence et dépassement de texte, performances >100 projets, reprise après crash et portabilité des favoris. Les tests Windows/RTX/Design Space/physiques restent NON_EXECUTE.
- **Prochain lot 21 :** installation Windows, hors ligne, sécurité de démarrage, mises à jour et récupération, en s'appuyant sur le writer et les contrats existants ; aucune réécriture universelle ni gate ajouté à G3.3.
