# V35-COV-18D2 — Revue hostile E07–E12 : interaction, accessibilité, Undo et intégrité

**13/11/2026. CANDIDAT NON NORMATIF.** V3.4 reste ACTIVE. Sources consultées : registre V3.5 E07–E12, PROGRESS dernier bloc COV18D1, README, contrat des 25 axes, COV18D1 et COV18A3C. Les fichiers V3.4 précis et HEAD main courant n'ont **pas** pu être certifiés dans ce passage : tout rattachement V34/S ci-dessous est **à confirmer dans les DoD sources**, et ne constitue pas une preuve de couverture. Aucune API nouvelle n'est présentée comme implémentée.

## 1. Décisions et frontières, six IDs distincts

| ID original #134 | Décision / priorité | Source candidate / risque | Raffinement V3.5 et critère falsifiable |
|---|---|---|---|
| **E07** survol/context bar/gestes/raccourcis | **RACCORDER P0** | Lot UX 07/18, B04/B05 ; barre contextuelle ≠ nouvelle commande | Une même commande typée pour souris, clavier et menu ; contexte dépend de sélection stable, aucune action destructive au simple survol ; tester changement de sélection pendant popup |
| **E08** modes novice/avancé et divulgation progressive | **AMÉLIORER P0** | Lot UX 07/18 ; risque de deux interfaces divergentes | Même moteur, mêmes actions et sauvegardes ; les modes ne changent que la visibilité des options ; passage novice↔expert sans perte de brouillon |
| **E09** thèmes/panneaux/préférences | **RACCORDER P1** | Lot UX 07/21 ; préférence ≠ contenu projet | Préférences locales versionnées, repli sur valeurs sûres si corruption ; panneaux réinitialisables ; ne pas ajouter de champs au .smartsvg V1 |
| **E10** accessibilité clavier/focus/contraste/DPI/motion réduite | **AMÉLIORER P0** | Lot UX 07/21, critère Windows distinct | Focus logique déterministe, zoom DPI 200 %, 1366×768, commandes accessibles sans pointeur, états et erreurs annoncés en texte ; test UI réel obligatoire |
| **E11** Undo/Redo/brouillons/transactions/historique | **RACCORDER P0 BLOQUANT** | Lots 05/06/18, E04 ; historique UI ≠ journal writer V1 | Une transaction métier atomique sur expected_sha, avant/après contrôlés ; preview ne rejoint jamais Undo durable ; annulation avant commit ne modifie pas V1 |
| **E12** sauvegarde V1 CAS/recovery et intégrité | **GARDER + AMÉLIORER P0 BLOQUANT** | Lots 03–06/21, writer et recovery existants | Writer CAS unique, SHA source et masques float32 conservés ; relecture post-commit ; recovery idempotent et explicite, pas de migration V2 tacite |

**Contre-argument hostile :** créer un nouveau store d'Undo, un fichier projet V2 ou une seconde application « expert » simplifierait localement l'UX, mais fragmente autorité, reprise et QA ; **REJETER** pour P0. Un autosave silencieux semble pratique, mais sans atomicité/CAS et restauration mesurée il peut écraser une révision concurrente : **REPORTER** jusqu'à preuve de writer. Les six IDs ne signifient pas six nouveaux boutons.

## 2. Contrats candidats, non APIs existantes

`CommandIntent{schema_version:1,command_id,project_id,expected_project_sha256,selection_revision,action_id,parameters,origin:KEYBOARD|POINTER|MENU}` → `CommandOutcome{status:APPLIED|PREVIEW_ONLY|REJECTED|STALE|CANCELLED,project_sha256?,undo_token?,error_code?}`. `action_id` doit pointer vers le bus existant **après inspection du HEAD** ; ne jamais créer un moteur parallèle. Survol n'envoie pas CommandIntent mutant. Les paramètres de géométrie utilisent mm **seulement si l'échelle est connue**, sinon pixels source déclarés et pas de coupe prétendument calibrée.

`UiPreferencesV1{schema_version:1,mode:NOVICE|EXPERT,theme:SYSTEM|LIGHT|DARK,reduced_motion,panels,shortcuts}` est **local et non portable** ; aucune modification du .smartsvg. Préférences invalides : `PREFERENCES_INVALID`, retour à défaut sans effacer le projet. Les raccourcis conflictuels sont refusés avec indication explicite ; les commandes d'export ne se déclenchent pas via focus de champ texte.

`EditDraft{base_sha256,selection_revision,commands[],preview_generation,dirty}` vit en mémoire/session ; `CommitRequest{expected_sha256,command_id,validated_delta}` est remis **au writer V1 existant uniquement**. États : CLEAN→DRAFT→PREVIEW_PENDING→READY_TO_COMMIT→COMMITTING→CLEAN ; toute modification externe déclenche STALE, annule les previews tardives et bloque COMMIT ; interruption pendant COMMITTING déclenche RECOVERY_REQUIRED, jamais « sauvegardé » sans relecture. `Undo` d'un brouillon ne touche pas le disque ; Undo durable n'est proposé qu'après validation du contrat writer et de la restauration, sans effacer une édition concurrente.

**Invariants :** un seul projet V1 ; CAS/SHA et masques float32 préservés ; l'historique writer préexistant reste source d'autorité ; aucun champ nouveau non validé ; quatre exports indépendants (PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche, SVG éditable) ; profils machine KNOWN/UNKNOWN ; ComfyUI et IA locale facultatifs. E07–E12 ne valident aucune commande machine, compatibilité Design Space ou découpe physique.

## 3. UX et récupération

**Novice :** sélectionner un objet → barre contextuelle avec libellés et icônes → modifier en direct dans un brouillon réversible → voir état non sauvegardé → Undo/Redo → Enregistrer avec confirmation seulement en cas de conflit/écriture externe → fermer/reprendre. **Expert :** raccourcis et inspecteur de révision, même moteur ; diagnostics CAS, provenance, type raster/vecteur et statut de prévol. Aucun prompt systématique pour zoom, sélection ou panneaux ; confirmation proportionnée pour écriture externe, destruction, installation IA ou export.

À 1366×768/DPI 200 %, panneau repliable, aucune action essentielle hors écran, focus visible et tabulation logique ; Escape ferme le menu sans perdre le brouillon ; Enter n'enregistre pas par accident dans un champ. Animations réduites et informations jamais transmises par couleur seule. États EMPTY, READY, DIRTY, PENDING, STALE, ERROR et RECOVERY_REQUIRED exposent une action de correction claire, pas une erreur générique.

## 4. TDD et preuves — PROPOSÉS, NOT_RUN

- **Positif** : même action depuis clavier, menu et pointeur → même CommandIntent, même delta et même Undo ; passage novice→expert→novice garde projet et brouillon identiques.
- **Positif** : transaction writer avec fixture V1 synthétique et masque float32 non binaire ; relecture SHA, alpha intermédiaire et provenance sans perte.
- **Négatif 1** : sélection change entre ouverture de context bar et activation → STALE_SELECTION, aucune mutation d'un autre objet.
- **Négatif 2** : raccourci export saisi dans champ texte → aucune commande export ; conflit de raccourcis refusé sans écraser le mapping précédent.
- **Négatif 3** : modification externe du projet entre preview et commit → CAS STALE, original et nouvelle version intacts ; aucun Undo d'une révision étrangère.
- **Négatif 4** : préférences corrompues/panneau hors écran → défauts sûrs, projet intact, UI récupérable au clavier.
- **Négatif 5** : double clic et commande dupliquée `command_id` → au plus un commit effectif ; résultat idempotent à démontrer sur writer réel.
- **Crash/annulation** : coupure/disque plein entre préparation et publication ; relire primaire/backup/recovery, ne jamais annoncer PASS sans réouverture ; annuler pendant preview n'écrit rien.
- **UI Windows** : navigation clavier intégrale, DPI 100/200 %, 1366×768, lecteur d'écran si support confirmé, focus après dialogue, Unicode chemins et réduction de mouvement — NOT_RUN.
- **GPU/IA** : non requis pour ces six fonctions, CPU manuel ; GPU_PASS non applicable au périmètre, aucun modèle téléchargé. **Design Space et coupe physique** : non applicables à l'interaction, gates export/terrain toujours NOT_RUN.

Mesures à recueillir, non inventées : p50/p95 d'une commande/Undo sur 5/20/100 objets, latence focus/context bar, temps relecture/recovery après crash, mémoire de l'historique et impact DPI. Fixtures synthétiques, pas de médias tiers ou de données personnelles.

## 5. Micro-lots et DoD

1. **TDD-E07/E08** inventorier bus de commandes et mapping clavier/pointeur existants ; matrice identité et sélection, tests sans mutation.
2. **TDD-E09/E10** préférences locales robustes, accessibilité Windows, tests DPI et focus ; benchmark Tk/Qt/Tauri séparé, aucune migration imposée.
3. **TDD-E11** cartographier le vrai writer, l'historique et le bus Undo avant contrat de transaction ; injection stale/duplicate/crash.
4. **TDD-E12** vérifier CAS, recovery, float32, idempotence et round-trip V1 sur SHA de code exact ; relecture et rollback.
5. **TDD intégration** parcours novice/expert import→atelier→reprise→quatre exports ; QA de chaque rôle et gates Windows/Design Space/physique séparés.

**DoD de la fiche** : les six IDs explicitement traités, risques et alternatives écrits, contrats proposés et trois négatifs minimum ; **DoD produit NON ATTEINT** tant que sources V34, implémentations, tests unitaires non-skip, UI Windows et critères intégraux n'ont pas été rapprochés et prouvés. Toute évolution de schéma/packaging/AGENTS exige revue et validation propriétaire.

## 6. Audit des 25 axes du contrat

01–06 : univers 24/141/140/80/437 préservés, rattachements détaillés non certifiés ; 07 V1/CAS/float32 couvert en proposition ; 08 quatre exports conservés sans tests ; 09 machine/physique hors fonction mais gates préservés ; 10–13 UI, novice/expert, clavier, Undo/recovery traités ; 14 IA non requise, consentement inchangé ; 15–16 raster/vecteur non modifiés ; 17 bibliothèque/batch hors fiche (E01–E06 et D11) ; 18 Smart Delivery hors fiche, consomme seulement exports réels ; 19 opportunités historiques à revoir après E20 ; 20 performance = protocole non mesuré ; 21 sécurité/privacy : aucune télémétrie, projet ou média tiers ajouté ; 22 gouvernance et WIP inchangés ; 23 anti-doublon bus/writer ; 24 statut preuve et relecture requis ; 25 aucune obligation raccourcie.

**Statuts disjoints** : AUDITÉ candidat E07–E12 ; SPÉCIFIÉ partiel ; REVU indépendant non prouvé ; PR_DOCS/ADOPTÉ/CODE_MAIN/FONCTION_WINDOWS_EXPOSÉE/TEST_UNITÉ_PASS_NON_SKIP/TEST_UI_WINDOWS_PASS/GPU_PASS/DESIGN_SPACE_PASS/COUPE_PHYSIQUE_PASS **non revendiqués**. Historique : 24/141/140/80/437 inventoriés, 431/437 liens source explicites, 6 exceptions, 10 exigences G6/G9 sans ticket direct ; pas de nouvelle preuve de couverture sémantique.

**Prochaine action unique : V35-COV-18D3 — E13–E20**, revue hostile des previews async, diagnostics, QA, packaging Windows, confidentialité et tutoriels, puis revue transversale O-001..O-033.
