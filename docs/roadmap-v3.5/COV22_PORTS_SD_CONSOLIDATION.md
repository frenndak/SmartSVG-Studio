# V35-COV-22 — ports réels, Smart Delivery V1/V2 et premier pack utile

**14 novembre 2026 — conception candidate, aucune nouvelle fonction ZIP implémentée.** Reprise explicite de COV21. Ref main lu par API commit : `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`. Branche de conception au départ : `944701074c2189ee199daad01af514a07a70dd83`. Les noms de fonctions ci-dessous ont été confrontés à l'AST et au contenu des fichiers de ce main ; leurs empreintes sont consignées dans `PRIORITY_REGISTER.json`. Les deux commentaires historiques SD-V1 et SD-V2 ont été lus intégralement.

## 1. Réconciliation qui ferme les réserves de lecture COV21(a,b)

| Port de main effectivement lu | Contrat observé | Réemploi sûr et manque à concevoir |
|---|---|---|
| `smartsvg_cricut/delivery_v21122.py::delivery_manifest(report)` | Rapport historique `dossier/import_direct_cricut_v218/objets`, 1–32 objets ; contrôle fichiers/empreintes, PNG impression/fabrication et planches ; physique false | Source de règles et compatibilité historique, **pas** un routeur universel des quatre rôles ni un `DeliveryPlan` PNG-seul |
| `delivery_v21122.py::write_delivery(root, manifest)` | Écrit uniquement `07_LIVRAISON_STICKERS_V21_12_2/MANIFESTE_STICKERS.json`, staging/fsync, publication hardlink no-clobber ; refus si primitive indisponible | Conserver ce contrat ; un ZIP externe nécessite un consommateur de packaging à spécifier. Aucune promesse que cette fonction crée déjà une archive |
| `smartsvg_governance/artifact_qa.py::audit_project(report_path, *, requested_intent='sticker_contour')` | Lecture de rapports historiques PNG/SVG ; `SVG_MANQUANT` si aucun contour ; imports cv2/NumPy/Pillow ; résultat BLOCKED ou REVIEW_REQUIRED, axes externes NOT_TESTED | Réutiliser les analyses appropriées via adaptateur par rôle ; ne pas envoyer un PNG-seul dans une politique exigeant SVG et ne pas affaiblir la QA historique |
| `smartsvg_cricut/direct_import_v218.py::prepare_cricut_import(report, dpi)` | Prépare les copies/rapports historiques de transfert ; ce nom n'est pas une API de commande de Design Space | Réutiliser densité/provenance/publication selon leur contrat ; guide et import dans Design Space restent manuels |
| `smartsvg_vector/svg_publication.py::save_svg(svg, folder='', prefix='smartsvg_couleurs')` | Publie des bytes XML terminés, vérification hash et noms ; n'est pas un prévol ni routeur de contrats | Fournir un dossier explicite côté bureau ; ne pas qualifier une topologie ou une coupe à partir de la réussite de ce writer |
| `smartsvg_core/template_geometry_v34.py::folded_card(width_mm, height_mm)` et `open_tray(base_width_mm, base_depth_mm, wall_height_mm, tab_width_mm)` | Géométries mm de carte et boîte ; chemins/opérations théoriques | Ne sont ni exporteurs ni moteur de persistance de patrons ni qualification matière |
| `smartsvg_core/template_preflight_v34.py::preflight_template(proposal, usable_sheet_mm=None)` | Prévol statique borné pour patrons approuvés ; aucun SVG écrit ni opération DS assignée | Consommer son diagnostic dans le guide, conserver UNKNOWN sur matériel/DS/physique |
| `smartsvg_core/project_contracts.py::Artifact` | `use` limité à `print_then_cut_png/basic_cut_svg/editable_svg` | CUT multicouche externe typé, aucune sérialisation frauduleuse ni changement V1 implicite |

## 2. Divergences et décisions explicites

1. **Premier ZIP : un seul artefact réel suffit.** Le besoin d'inventorier les quatre producteurs ne crée pas une dépendance à leurs quatre interfaces achevées. W05 peut être conçu sur fixtures ; W06 consomme un rôle W03 réellement validé. La clôture W03 conserve les quatre contrats.
2. **Ancienne QA versus PNG-seul :** préserver le contrôle historique de paire PNG/SVG. Le futur prévol de rôle PNG valide son alpha/densité/dimensions/provenance, affiche les axes non exécutés et ne prétend pas fournir un SVG associé.
3. **Manifeste historique versus pack :** le schéma du JSON de livraison historique ne devient pas automatiquement celui du ZIP. Le schéma de pack est un contrat externe versionné ; projet V1 et exports d'origine inchangés.
4. **Rendu HTML SD2 :** fonction pure de gabarit inerte à partir de valeurs validées et échappées ; pas d'HTML arbitraire, JS, lien réseau ou lecture de chemin libre. Le guide reste facultatif ; l'export direct et SD1 sans guide restent accessibles.
5. **Atomicité :** un ZIP unique, temporaire sur le volume cible, fermé/fsync/relu puis publié sans écrasement ; un ensemble de fichiers indépendants n'est pas une transaction atomique. Filesystem non admissible = erreur réparable, pas copie finale partielle.
6. **Confidentialité :** projet source, noms privés, chemins absolus et métadonnées sensibles exclus par défaut. Un consentement d'inclusion ne confère pas une licence de redistribution.
7. **Budget :** les plafonds historiques 32 objets, inspecteur G2.7 et budgets raster appartiennent à leur API ; ils ne deviennent pas limites de Cricut, du ZIP ou des planches futures. Définir/mesurer les quotas de pack séparément.

## 3. Contrat de premier incrément SD0 → SD1

**Entrées conceptuelles, pas APIs existantes :** révision du projet ou provenance de fixture explicitement qualifiée ; liste d'artefacts déjà exportés (`role`, chemin local admis au point d'usage, octets, SHA, dimensions connues/UNKNOWN, QA par axe, licence et politique de partage) ; destination ; demande du guide et locale ; consentement de publication.

**Sortie conceptuelle :** reçu externe avec chemin local du ZIP (seulement dans l'application, jamais dans le contenu partageable), SHA du ZIP, inventaire relu, version du manifeste et résultat `PUBLISHED_UNVERIFIED`. Ce statut qualifie uniquement la publication vérifiée ; Design Space et physique ont leurs propres champs NOT_RUN/UNKNOWN.

**États :** EMPTY → PLAN_VALIDATED → PREVIEW → STAGING → ZIP_VERIFIED → PUBLISHED_UNVERIFIED. STALE/HASH_MISMATCH/UNSAFE_PATH/QUOTA/EXISTS/DISK_FULL/CANCELLED/OUTCOME_UNKNOWN sont distincts. Une erreur après publication peut laisser un ZIP valide ; inspecter avant de proposer une répétition. Une annulation n'efface jamais une livraison déjà publiée.

**UX :** Exporter un fichier reste l'action simple. « Préparer un pack » devient disponible lorsqu'un vrai artefact admissible existe. Novice : rôle, destination, un résumé « 1 PNG d'impression ; aucun SVG de coupe », aperçu puis création. Expert : inventaire, unités, empreintes, avertissements, exclusions et guide. États chargement/erreur/réparation/succès, clavier, focus et DPI 200 % à spécifier/tester ; aucune popup pour cocher un choix réversible.

## 4. Micro-lots à donner au producteur après adoption applicable

| Incrément | Livrable | DoD et rollback |
|---|---|---|
| SD0-A | Types externes, validation du rôle et plan pur | Fixture PNG seule admise, rôle erroné/absent refusé, aucun writer ; retrait du port sans migration |
| SD0-B | Prévol QA par rôle et inventaire de partage | Rapport historique inchangé, sorties externes honnêtes ; désactivation du consommateur nouveau |
| SD1-A | Archive temporaire bornée et relecture | Membres et SHA réels, chemins sûrs, annulation/disque plein ; aucun ZIP final avant validation |
| SD1-B | Publication no-clobber et reçu | Deux producteurs même destination → au plus un succès ; reçu vérifié ; source et exports byte-identiques |
| SD2-A | Guide HTML pur, offline et facultatif | Parser HTML + inspection des liens ; aucun contenu actif, chemin privé ou format fictif |
| SD2-B | Panneau natif et reprise | Parcours novice/clavier/DPI, faux reçu refusé, erreur réparable ; export direct conservé |

**Négatifs minimaux :** N1 source remplacée après prévol ; N2 fichier renommé mais bytes de même taille différents ; N3 symlink/reparse/jonction/ZIP traversal ; N4 collisions Unicode/casse/noms réservés ; N5 quota, disque plein et annulation à chaque phase ; N6 publication concurrente ; N7 HTML utilisateur hostile ; N8 licence inconnue ou fichier privé non consenti ; N9 profil/version DS inconnus ; N10 reçu illisible après publication réelle ; N11 pack PNG-seul sans contour inventé ; N12 rôle CUT multicouche injecté dans Artifact V1. Les nouveaux tests ZIP/guide/UI sont **NOT_RUN**, car ces consommateurs ne sont pas implémentés dans cette passe.

## 5. Vérification exécutée et limites

**Réellement fait :** lecture du ref main actuel ; contrôle des blobs des ports ; signatures analysées par AST ; lecture intégrale SD-V1/SD-V2 ; confrontation aux lots V3.4 14–17/COV21 ; exécution de `python -m unittest discover -s tests -p 'test_delivery_manifest_atomic_g34.py' -v` sur le snapshot exact main : **31 tests historiques PASS, 0 skip, exit 0**. Ils qualifient les contrôles/manifeste historiques couverts, **pas** le futur ZIP, guide ou parcours Smart Delivery natif. `artifact_qa` n'a pas été exécuté : dépendance OpenCV absente dans ce runtime ; lecture de source seulement.

**Réserves COV21 :** (a) commentaires et (b) ports : lectures accomplies ; (c) toutes les associations critère→DoD→scénario de fabrication et (d) revue transversale/essais futurs : restent ouvertes. Ne pas transformer cette fermeture des deux réserves de lecture en « 80 UX certifiées ».

**25 axes :** 01–05 sources et inventaires conservés, critères sémantiques ouverts ; 06 preuve historique bornée ci-dessus ; 07 V1/CAS/identités préservés ; 08 quatre rôles distincts ; 09 capacités tri-state ; 10–12 UX/états/accessibilité spécifiés, UI NOT_RUN ; 13 pannes/concurrence en recettes ; 14 IA N/A (aucun modèle nécessaire) ; 15 alpha/densité/provenance par rôle ; 16 XML/topologie non déduits du writer ; 17 lots/patrons consommateurs, pas un nouveau moteur ; 18 pack conçu et non implémenté ; 19 extensions conservées dans le maître ; 20 objectifs à mesurer ; 21 licences/privacy/sécurité explicites ; 22 branche documentaire et V3.4 active ; 23 ports exacts et absence de doublon ; 24 aucune promotion ; 25 aucun contrôle supprimé pour gagner du temps.

**Prochaine action unique :** fermer le point Q01 de [COMPLETION_QUEUE.md](COMPLETION_QUEUE.md), soit les associations exactes encore manquantes des cinq contrats O-001/O-002/O-004/O-028/O-032 vers critères/DoD/scénarios, en réutilisant cette lecture des ports et des commentaires sans la refaire.
