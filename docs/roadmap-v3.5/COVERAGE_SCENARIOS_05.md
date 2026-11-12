# COV-05a — Scénarios du lot 05 et tickets sources (V3.5 candidate)

> Audit documentaire ciblé du 13/11/2026. **V3.4 ACTIVE**, V3.5 NON NORMATIVE. main observé via recherche de commits : `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935` (à revalider par référence Git avant toute décision d'intégration). Source : [05_PROJECT_SCHEMA.md](../roadmap-v3.4/05_PROJECT_SCHEMA.md), blob `598a0ba0ec17d2e6035ff8875d3a5ba49a2f702c`, lignes 181–200 (20 scénarios) et 206–216 (7 micro-tickets V34-025..031). Index source : [SCENARIOS_V34_02_08.md](SCENARIOS_V34_02_08.md). La présente matrice n'attribue **que** les liens écrits dans les sept micro-fiches ; aucune inférence par titre ou lot.

## Matrice exhaustive (20 scénarios)

| Scénario historique | Tickets citant explicitement le scénario | Qualification |
|---|---|---|
| T-V34-05-01 | V34-025, V34-027 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-02 | V34-027, V34-031 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-03 | V34-027, V34-028 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-04 | V34-027, V34-028 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-05 | V34-025, V34-026 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-06 | V34-025, V34-026, V34-031 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-07 | V34-025, V34-026, V34-031 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-08 | V34-025, V34-026 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-09 | V34-026 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-10 | V34-027, V34-030 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-11 | V34-027, V34-030 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-12 | V34-027 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-13 | V34-029 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-14 | V34-029 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-15 | V34-029 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-16 | V34-028, V34-030 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-17 | V34-028, V34-031 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-18 | V34-026 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-19 | V34-031 | LIEN_EXPLICITE_DE_PLANIFICATION |
| T-V34-05-20 | V34-030 | LIEN_EXPLICITE_DE_PLANIFICATION |

**Bilan contrôlable : 20/20 scénarios du lot 05 rattachés explicitement à au moins un ticket ; 0 non attribué.** Ce chiffre ne s'ajoute pas aux 51/52 des lots 02–04 pour déclarer une conformité fonctionnelle : il porte seulement le sous-total documentaire à **71/72 scénarios avec lien explicite** sur lots 02–05. Les 437 scénarios restent inventoriés, non exécutés. Les 141 exigences et 140 tickets demeurent intacts ; les 10 obligations G6/G9 sans ticket restent ouvertes.

## Contre-expertise et décisions

- **GARDER P0** V34-025..029 : conserver V1 en lecture et écriture contrôlée, identité/masques float32, CAS et receipts ; le lot 05 décrit une **migration V2 proposée**, non autorisée à remplacer le format V1. Ne pas considérer les fichiers `futur` du tableau comme implémentés.
- **RACCORDER P1** V34-030/031 : erreurs et ressources visibles au niveau UX Windows, sans créer un second store, un second writer ou un moteur d'archives. Prévoir libellés français, clavier/focus, 1366×768/DPI 200 %, et reprise non destructive.
- **REVUE HOSTILE :** le lien explicite T-V34-05-18→V34-026 n'autorise pas une compatibilité Design Space ; T-V34-05-19→V34-031 n'autorise pas une impression/coupe validée. Le projet V1, les quatre contrats de sortie et les états UNKNOWN restent séparés. Un plan V2 sans preuve de migration/réouverture n'est pas une livraison.

## Recette de qualification proposée (NON EXÉCUTÉE)

Fixture synthétique V1 contenant PNG, 12 IDs et masques float32 ; lecture sans mutation, copie de migration uniquement après autorisation, comparaison des SHA et round-trip. Négatifs obligatoires : (1) ZIP traversal/collision Unicode ; (2) source modifiée/SHA CAS périmé ; (3) double command_id à payload différent ; (4) interruption/disque plein pendant publication ; (5) masque dont preuve d'identité est obsolète. Attendus : refus explicite, source inchangée, aucune fausse validation, reprise guidée et Undo si commande locale. Tests unitaires + vraie UI Windows à exécuter séparément ; Design Space/Explore 5 et coupe physique **NOT_RUN**. Aucun benchmark RTX ni test utilisateur réalisé.

**Contrat de qualité 25 axes :** héritage/identifiants, preuves, autorité V1, CAS, sécurité ZIP, rollback, UX, confidentialité, non-régression, tests et promotion sont applicables et demeurent gates ouvertes ; IA GPU, coupe physique et guide HTML ne sont pas exercés par ce simple rapprochement documentaire (leurs obligations globales ne sont pas supprimées). Les 25 contrôles doivent être revalidés intégralement avant promotion, sans transformer cette matrice en PASS.

**Prochaine action unique :** COV-05b, lot 06 `06_COMMAND_BUS.md` : relever pour chacun des 30 scénarios les citations explicites dans les micro-tickets du lot et signaler toute recette orpheline, puis lots 07–08. Aucun changement aux lots V3.4, à AGENTS ou au producteur de code.
