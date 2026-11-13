# V35-COV-17E — Revue UX E01–E20 : bibliothèque, Windows, UX, QA et récupération

**13/11/2026 — candidate, non normative.** Les vingt ID et intitulés viennent de [#134](https://github.com/frenndak/SmartSVG-Studio/issues/134) et restent inchangés ; les décisions sont **propositions**, pas des fonctionnalités prouvées ou une adoption normative. Base GitHub `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`.

## 1. Ports concrets consultés et protection du socle

| Port | Blob SHA source | Fonction réellement observée ou limite |
|---|---|---|
| `engine/standalone_desktop_v34.py` | `abdfe2f16be1b72375513f2a07769920d92e5dd7` | Shell Tk hors ComfyUI, inspecte V1 et projets; docstring explicite **prototype non packagé**, pas installation Windows complète |
| `engine/native_app_shell_v34.py` | `b5cc4f503791d6f24ac62027323cb726973b54a2` | Navigation entre pages, pas deuxième store projet |
| `engine/native_image_viewport_v34.py` | `5f2a8bb1c85cf501d8bfd521a862c0e8e1ad0110` | Zoom/pan/fit/taille réelle pour aperçu de l'image, pas encore canevas vectoriel intégral |
| `engine/native_theme_tk_v34.py` | `f11462a519b03f043ebdfc666800677d4ed5c9f7` | `ArtisanThemePicker` thème/accent/mouvement réduit et préférences locales |
| `engine/native_notes_tk_v34.py` | `bc83b8d757d2d6ed585538732acba3113b3a435a` | Notes dans projet avec brouillon et révision, pas Undo global des objets |
| `engine/native_atelier_tk_v34.py` | `921f09fbd54b68a19b3ba9688f00a0334bafe6b3` | Navigation de sujets réels et panneau pinceau, pas édition complète des calques |
| `engine/smartsvg_core/project_recovery.py` | `002427009d72935a6df31368289cba94970061da` | Writer/récupération CAS et résolution explicite des backups, sans promesse coupe |
| `engine/smartsvg_core/project_workspace_g22.py` | `13b8e40d6fcc9cf03ed2c935b38ad6eff0bcbe03` | Espace de projets V1 et notes/masques, pas catalogue bibliothèque universel |
| `engine/smartsvg_governance/artifact_qa.py` | `c47009f2a47e664dc0ee36433f7f562dc7a675f0` | QA statique PNG/SVG sans Design Space ni coupe physique |
| V3.4 lot 21/22 | `8700846208315f405b7f60266fabf8181e160ff4` / `6fa98816ae2a8048471f6625d3c099df171fb0fb` | Installation/recovery et campagnes d'essai, **spécifications historiques non exécutées par cette rédaction** |

## 2. Vingt décisions par ID, sans effacer l'héritage UX

| ID original | Libellé #134 | Décision candidate | État réel et lacune | Critère V3.5 à spécifier / DoD | Négatifs indispensables |
|---|---|---|---|---|---|
| **E01** | bibliothèque, récents, miniatures, recherche/favoris | **P1 / RACCORDER** | ManagedWorkspace crée/recherche un projet par nom, index bibliothèque complet non vérifié | LibraryView reconstruite à partir des archives V1, SHA/miniature sans source privée en cache | index corrompu, vignette mal liée, fichier disparu |
| **E02** | collections/tags/modèles/duplication | **P1 / ÉTENDRE** | V3.4 lot20 collections/tags/modèles spécifiés; pas de registre natif éprouvé | Collections non destructives, tags, favoris et duplication sous nouveau project_id et CAS | nom collision, lien externe, suppression accidentelle |
| **E03** | variantes/historique de création | **P1 / AMÉLIORER** | save_with_recovery et opérations V1; historique de variantes visuelles global pas démontré | Variante séparée sans modifier original; versions/sha, comparaison et reprise | variante liée au mauvais SHA, modification de la base, perte d'historique |
| **E04** | atelier hybride raster/vector/objets/propriétés | **P0 / GARDER** | NativeAtelierPanel Tk inspecte sujets et pinceau, pas atelier hybride complet objet/texte/vectoriel | Un canevas avec même projet/IDs, actions locales et UX expert, export au contrat choisi | demo confondue avec vrai sujet, conflit de masque, survente de fonctions |
| **E05** | canvas zoom/pan/poignées/aimants/overlays | **P0 / GARDER** | native_image_viewport_v34.py gère zoom/fit/100%/pan ; poignées/snap/overlays métier non qualifiés | Porter interactions de l'éditeur réel sous la même viewport et état brouillon, clic/clavier | zoom confondu mm, pixels surdimensionnés, overlays décalés |
| **E06** | comparaison avant-après/sliders/superposition | **P1 / AMÉLIORER** | source_preview_v34 et smartsvg_quality/previews.py créent aperçus; diff complet non prouvé | Avant/après lié aux SHAs, slider et superposition sur pixels source à 100% | preview périmée, original modifié, alpha mal orienté |
| **E07** | survol/context bar/gestes/raccourcis | **P0 / RACCORDER** | NativeAppShell Tk/navigation et contrôles pinceau; context bar/gestes unifiés non confirmés | Context bar selon sélection, raccourcis scopes, Undo visible et accessible, pas de 80 boutons | raccourci capté par champ texte, focus perdu, actions hors contexte |
| **E08** | modes novice/avancé et divulgation progressive | **P0 / GARDER** | pages existantes Accueil/Atelier/Fabrique/Projet/Apparence, novice/expert UI avancée non qualifiée | Modes Express/Expert sur un seul document/store, puissance dévoilée progressivement | mode change l'artefact, états divergents, fonctions masquées sans aide |
| **E09** | thèmes/panneaux/préférences | **P1 / RACCORDER** | native_theme_tk_v34.ArtisanThemePicker sauvegarde thème/accent/motion réduit | Préférences local-first portables, panneaux et contraste réel, rollback thèmes | config corrompue, thème illisible, redémarrage reset |
| **E10** | accessibilité clavier/focus/contraste/DPI/motion réduite | **P0 / AMÉLIORER** | Tk et thème accessibles partiellement; preuves 1366x768/DPI200/clavier/a11y complètes absentes | Test focus/clavier/lecteur d'écran, motion réduit, contrastes et réponses FR | focus masqué, zoom DPI coupe commandes, couleur seule |
| **E11** | Undo/Redo/brouillons/transactions/historique | **P0 / AMÉLIORER** | éditeur brush strokes V1, notes CAS et PR #139 Undo/Redo lecture seule DRAFT, pas Undo global stable prouvé | Undo local vs commit durable distinct, receipts révisions, recovery et undo idempotent | double undo, export retiré à tort, result stale, crash |
| **E12** | sauvegarde V1 CAS/recovery et intégrité | **P0 / GARDER** | project_archive.save_project/load_project, project_recovery.save_with_recovery et inspect_recovery_plan, CAS réel | SHA source et writer uniques, opérations atomiques, backups propres et restauration explicitement confirmée | file replaced, pending backup, hash mismatch, ZIP traversal |
| **E13** | previews async/caches bornés/requêtes périmées | **P0 / AMÉLIORER** | standalone_desktop_v34 LatestOnlyJob pour preview, aucune politique globale cache/priorités prouvée | Cache borné par SHA/identité, annulation coopérative et résultat stale ignoré avant UI/commit | cache mélange deux projets, job tardif, RAM épuisée |
| **E14** | diagnostics réparables et erreurs compréhensibles | **P0 / AMÉLIORER** | native messages FR + recovery_message; erreurs explicables uniformes non prouvées | État quoi/pourquoi/comment réparer, action réelle selon disponibilité et données privées expurgées | chemin privé affiché, faux bouton réparer, status OK après erreur |
| **E15** | QA alpha/contours/couleurs/résolution | **P0 / RACCORDER** | artifact_qa PNG alpha, source_preview, auto_hd, diagnostic locaux, pas QA globale couleurs/fidélité | Contrôle source→masque→sortie, DPI, alpha et color profile, statut et diff non faux PASS | PNG rectangulaire, pixel halo, profil manquant, preview stale |
| **E16** | QA SVG chemins/topologie/viewBox/mm | **P0 / RACCORDER** | cut_path_preflight inspecte SVG, template_preflight valide la topologie nominale ; pas compatibilité DS garantie | XML sûr, bbox/path/hole, viewBox/mm, types SVG séparés, QA locale only | DTD, zero area, open path, 4 sorties fusionnées |
| **E17** | QA fabrication/profil/machine et preuve physique séparée | **P0 / GARDER** | template_preflight, artifact_qa, direct_import_v218 déclarent validation externe non testée | Profils tri-state, rapport preuve human+machine séparé, jamais READY_TO_CUT sans données | matière UNKNOWN, Score non attaché, machine différente |
| **E18** | packaging Windows/hors ligne/update/rollback | **P1 / RACCORDER** | standalone_desktop_v34 module Tk, docstring prototype non installateur; V3.4 lot21 packaging écrit | Installer Windows test réel et rollback, import sans ComfyUI, intégrité configuration/projet | DLL absente, update corrompt V1, rollback perte données |
| **E19** | confidentialité/local/opt-in réseau | **P0 / GARDER** | workspace local et provider_v2112 risque de téléchargement premier appel; pas de réseau par défaut | Consentement modèles/transfert, secret expurgé, fichiers privés protégés, désactivation claire | upload silencieux, EXIF leak, cache privé partagé, poids modèle dans repo |
| **E20** | tutoriels/aide contextuelle. | **P1 / RAFFINER** | UX lot07/annexe et docs existants, aide intégrée Windows exhaustive non démontrée | Tutoriels contextuels reliés au vrai état produit, exemples sous licence, guides DS statiques | tutoriel suggère fonction absente, contenu distant, étapes Cricut obsolètes |

## 3. Parcours novice/expert et matrice d'états

**Novice** : ouvrir son projet récent → état sain/corrompu affiché → aperçu source et action disponible → éditer dans brouillon → sauvegarder par CAS et relire → exporter seulement une capacité réellement branchée → ouvrir un guide hors ligne. Les erreurs sont en français avec action concrète, pas de trace ou chemin privé.

**Expert** : bibliothèque reconstructible, index de projet dérivé des archives, liens `project_id/source_sha/subject_id`, snapshot de masque float32, opérations, profils `KNOWN/UNKNOWN`, QA par axe, historique local, cache borné et choix d'export typé. Les paramètres du moteur et leur provenance sont lisibles sans donner autorité à un store de l'UI.

**Matrice des états proposée** : `HOME_EMPTY`, `PROJECT_HEALTHY@SHA`, `DRAFT_DIRTY`, `SAVE_PENDING`, `PROJECT_STALE`, `RECOVERY_PENDING`, `EXPORT_UNVERIFIED`, `ERROR_REPAIRABLE`, `CAPABILITY_NOT_AVAILABLE`. On ne convertit pas `EXPORT_UNVERIFIED` en `READY_TO_CUT` ni en succès machine.

**Design system** : une seule application Windows, panneaux réduits pour 1366×768/DPI 200 %, focus et navigation clavier, alternative à un geste uniquement souris, tutoriel novice sans obstruer l'éditeur, barre contextuelle limitée à la sélection et à l'intention. Changer de thème n'est jamais une mutation du projet.

## 4. Scénarios négatifs transversaux et qualité exigée

- Session multi-projet : prévisualisation asynchrone d'ancien projet ignorée ; cache et badge SHA reliés au projet courant, aucune fuite d'images privées.
- Notes et pinceau : deux modifications simultanées conflit CAS, relecture après enregistrement, annulation du brouillon et aucun double commit. PR #139 (historique) est un brouillon de disponibilité Undo/Redo, pas preuve de Undo global.
- Recovery : ZIP corrompu, pending backup et disque plein restent bloqués ou demandent choix explicite ; l'archive originale n'est jamais effacée silencieusement.
- QA : SVG actif/script/references et PNG alpha faux, origine/source mm incohérente, profil/matière inconnu ; verdict statique ne certifie pas la machine.
- Installer Windows : lancement sans torch/ComfyUI, session utilisateur standard, profil protégé, rollback de version sans modification projets V1 ; vraie VM ou PC Windows requis.
- Aide/compatibilité Design Space : choisir une version DS datée et un lien d'aide vérifié, ne pas inférer l'import/coupe de l'existence d'un guide.
- **Preuves actuelles de cette fiche :** code et documents inspectés. `UNIT, WINDOWS_UI, GPU, DESIGN_SPACE, PHYSICAL_CUT = NOT_RUN` pour cette campagne documentaire.

## 5. Clôture de la revue des 80 candidats UX : statut précis

Avec [COV-17A](COV17A_UX_A01_A16_SEMANTIC_AUDIT.md), [COV-17B](COV17B_UX_B01_B14_SEMANTIC_AUDIT.md), [COV-17C](COV17C_UX_C01_C18_SEMANTIC_AUDIT.md), [COV-17D](COV17D_UX_D01_D12_SEMANTIC_AUDIT.md) et cette fiche : **16+14+18+12+20 = 80/80 descriptions et décisions INDIVIDUELLES CANDIDATES**. Chaque entrée dispose d'une limitation, d'un DoD et de cas négatifs dans la revue correspondante.

**Reste à faire avant qu'un ID devienne `REVIEWED/ADOPTED`** : contre-expertise indépendante, liens exacts ticket/DoD/critère V3.3, tests automatisés et Windows selon fonctionnalité, analyse de compatibilité et choix de rejet/report approuvé. Les 80 candidats ne sont ni 80 tickets nouveaux ni 80 capacités installées.

**Prochain lot V35-COV-18** : relier chaque ID A01–E20 aux exigences normatives et aux tickets V34/V35 **sur preuve explicite**; confronter chaque arbitrage aux **33 opportunités** et aux six scénarios sans ticket source ; repérer les recouvrements au lieu d'ouvrir 80 tickets ; commencer par les modes Express/Atelier/Export qui touchent P0, puis faire la contre-expertise finale des 15 gates.
