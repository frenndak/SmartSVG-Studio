# SmartSVG Studio — G1.4 : sauvegarde récupérable et messages d'erreur

**Branche :** feat/g1-4-safe-project-recovery. **Dépendances :** G1.2 (#14) → G1.3 (#15), tous deux en revue. Aucun changement de la baseline V21.15.2 ni des APIs ComfyUI historiques.

## Usage pour les développeurs

Module : engine/smartsvg_core/project_recovery.py (Python standard). Utilise G1.3 pour toutes les écritures, validations et lectures du format .smartsvg.

    from smartsvg_core.project_recovery import (
        inspect_project, save_with_recovery, recover_previous, recovery_message
    )
    save_with_recovery("projet.smartsvg", project)
    state = inspect_project("projet.smartsvg")
    if state.status == "PROJECT_RECOVERABLE":
        # Montrer les détails du projet et demander la confirmation à l'utilisateur.
        recover_previous("projet.smartsvg", confirmed=True)

La restauration sans confirmation échoue. Une sauvegarde principale encore valide ne peut pas être remplacée par l'ancienne version via cette API.

## Flux et invariants

- Première sauvegarde : crée projet.smartsvg.
- Nouvelle sauvegarde : valide le fichier principal, **refuse de remplacer un secours endommagé ou associé à un autre projet**, copie ses octets dans projet.previous.smartsvg via un temporaire sur le même volume, vérifie sa capacité à être relu et seulement ensuite publie le nouveau projet.
- En cas de coupure avant publication : projet.smartsvg et/ou projet.previous.smartsvg contiennent une version précédemment valide.
- En cas de coupure après publication : le fichier principal est complet, et la version antérieure peut être conservée comme secours.
- En cas de corruption du principal : inspect_project renvoie PROJECT_RECOVERABLE si le précédent peut être relu.
- recover_previous restaure sur confirmation uniquement si le projet principal est absent ou invalide. Le fichier précédent est conservé.
- Le verrou OS latéral .lock protège les écritures simultanées et se libère automatiquement à la mort du processus. Le fichier .lock vide/persistant n'indique pas qu'une opération est en cours.
- Le statut UI et la raison d'action sont toujours distincts de la certification Cricut : physical_cut_verified reste faux.

## Diagnostics utilisateur FR

- PROJECT_HEALTHY : projet lisible.
- PROJECT_MISSING : aucun fichier présent.
- PROJECT_RECOVERABLE : copie précédente exploitable, restauration proposée explicitement.
- PROJECT_UNRECOVERABLE : copies absentes ou invalides, préserver les données pour diagnostic.
- PROJECT_LOCKED : une autre opération détient le verrou ; réessayer.
- SAVE_FAILED : défaillance d'écriture ou disque.
- RECOVERY_CONFIRMATION_REQUIRED : aucune restauration implicite.
- RECOVERY_WOULD_OVERWRITE_VALID_PROJECT : blocage de perte d'une bonne version.
- PROJECT_CHANGED_DURING_SAVE : identité projet ou bytes modifiés.
- NO_VALID_RECOVERY_SNAPSHOT : absence d'une version récupérable.
- BACKUP_CONFLICT : secours existant étranger/corrompu, conservation obligatoire.
- INVALID_RECOVERY_PATH : chemin hors contrat.

Les codes et consignes sont fournis par recovery_message() et destinés à l'UI Express, qui n'est pas encore branchée.

## Tests et sécurité

19 scénarios synthétiques dédiés :
- sauvegarde initiale, écrasement contrôlé et copie précédente bit-à-bit ;
- trois révisions, restauration volontaire, refus du remplacement d'un projet valide ;
- copie corrompue, projet corrompu, principal manquant, secours étranger ou endommagé ;
- simulation d'échec de copie / publication avec conservation du dernier état et nettoyage des temporaires ;
- verrou concurrent, identité de projet, chemins invalides ;
- messages FR et absence de revendication de coupe physique.

**Limites documentées :**
- Le moteur ne détecte pas les interventions d'un programme externe qui écrirait sans respecter le verrou ; l'environnement intégrateur doit éviter les modifications concurrentes des fichiers.
- Une sauvegarde précédente unique est conservée : pas encore d'historique de N versions, d'auto-save périodique ni de résolution de conflits synchronisés.
- Les contrôles ZIP internes viennent de G1.3 ; aucun SVG n'est ouvert ou exécuté par le module de récupération.
- Résilience simulée : pas de coupure électrique réelle testée, pas de mesure Windows NTFS/OneDrive, ni de récupération UI ComfyUI ; ces validations sont distinctes.
- Si une sauvegarde échoue après publication, il faut inspecter le projet et son précédent avant toute nouvelle tentative.

## Gate

Exécuter les tests de la PR exact-HEAD via SmartSVG G0 Admission Tests et le CPU Smoke historique. Vérifier 19 scénarios G1.4, 18 G1.3 et 8 G1.2, conservation de l'archive V21.15.2 et absence de modification des nœuds ComfyUI.

**Suite :** intégration des messages d'erreur dans un écran Express et tests de bout-en-bout incluant reprise clavier et interface Windows.
