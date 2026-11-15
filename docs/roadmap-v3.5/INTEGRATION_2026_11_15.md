# Raccord de reprise — 15 novembre 2026

Base distante relue : `500c24b0f155dda6b5142d24a3bba7da645c4f5f`. Main direct : `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`. Le seul diff main depuis aa0ff9e concerne le packaging Windows portable (#145), son workflow et sa documentation ; aucun changement des ports/archive/contrats examinés dans cette consolidation. Ce constat n'est pas un test du ZIP Windows.

## Travail horaire conservé

Q04J–Q04X sont conservés. Ils affinent les ports OCR, la sélection d'une source PNG réelle (pas le masque Atelier), les coordonnées source/viewport, latest-only, les tests Tk réels et les fixtures V1 multisources. Q04J_OCR_PR_PORT_DECISION est la lecture datée en session et le contrat général ; Q04J_OCR_PR_PORT_AUDIT et K–X conservent le détail horaire. Aucun port OCR supposé existant : futur adaptateur explicite, saisie manuelle possible, image identifiée par source_id/source_sha/project_sha et génération.

La cible persistante définie par ADR_COMPOSITION_PERSISTENCE complète Q04F ; export-only reste une étape partielle, pas l'achèvement G6.3. Les phrases de report de persistance dans K–X décrivent les limites du code V1, pas l'interdiction de concevoir sa migration.

Quatre fiches existaient sous `docs/roadmap-v3-5/` au lieu de `docs/roadmap-v3.5/`. Des copies exactes sont publiées dans le dossier canonique pour réparer la navigation, sans supprimer ni modifier les originaux historiques :

| Fiche | Blob source copié |
|---|---|
| Q04P_TK_TEST_EVIDENCE_CLASSIFICATION.md | 39db6d1bfe6ec27e5496c478a6a3624563701107 |
| Q04Q_TK_TEST_REAL_DISCOVERY.md | 05b902164f85b8b8b2cd8038570b408a2ca6917b |
| Q04R_TK_ROI_ORACLE_AND_PAN_CONFLICT.md | 021d238e8482376d468aa8cd16a32fe43162c491 |
| Q04X_ARCHIVE_G13_TEST_REUSE_MATRIX.md | 99dd18294bb59fb7eda4f79c62c368005d004e0a |

Utiliser désormais le chemin avec point. Un doublon de fichier de lecture ne crée aucun scénario/ticket/feature supplémentaire. Q04X était publié mais absent du journal : cette entrée réconcilie ce manque.

## Contrôles et limites

[Q04Y](Q04Y_ARCHIVE_QUOTAS_ERROR_ORDER.md) précise quotas membre/total/JSON/ZIP et ordre exact des erreurs. La branche commune taille/ratio n'est plus présentée comme preuve isolée de taille. Commande réellement exécutée sur les fichiers archive/tests inchangés du snapshot local aa0ff9e : `python -m unittest discover -s tests -p test_g13_project_archive.py` : **53 tests, 0 échec, 0 skip**, Linux Python 3.12. Ce sont les tests existants ; aucun nouveau round-trip deux PNG ni port OCR n'a été implémenté. Aucun résultat Windows/GPU/Design Space/physique ajouté.

Revue indépendante du delta : voir REVIEW_DELTA_RESULT, empreinte vérifiée avant mises à jour de statut. Les ajouts horaires et Q04Y ne sont pas automatiquement inclus dans son verdict ; revue globale encore ouverte. Les retours complémentaires D/E et opportunités ne sont pas disponibles dans cette reprise, donc leurs étapes restent ouvertes.

**Suite unique : REVIEW_DE dans RUN_STATE.json.** Les contrats OCR/format ont maintenant un découpage de réalisation ; ne pas les transformer en une série infinie de lectures de fichiers. Conserver tous les contrôles de qualité, lire les changements de sources si leur SHA évolue, et terminer les autres fonctions ainsi que la réconciliation sémantique avant promotion. Autorité V3.4 inchangée.
