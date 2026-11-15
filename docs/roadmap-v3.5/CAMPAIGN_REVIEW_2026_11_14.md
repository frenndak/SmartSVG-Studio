# Campagne du 14 novembre — corrections de conception et limites de revue

**Statut actualisé le 15/11 : delta relu favorablement, revue globale encore ouverte. V3.4 active.**

Voir [verdict indépendant](REVIEW_DELTA_RESULT.md) et [raccord des ajouts horaires](INTEGRATION_2026_11_15.md). Le reste du rapport conserve la photographie avant verdict. Ce rapport n'est ni une APPROVED review GitHub, ni une qualification Windows. Le propriétaire a demandé la finalisation complète et le remplacement de V3.4 une fois finalisée ; cette autorisation n'est pas un résultat de test.

## 1. Relectures indépendantes réalisées

Trois relectures terminées sur le snapshot candidat antérieur `1c0a11eee2aa1d61acf7a612557308f03c341c66` : orchestration/gouvernance ; A01–A16 et B01–B14 (30 verdicts individuels) ; C01–C18 (18 verdicts individuels). Les reviewers ont lu les fichiers locaux fournis, **sans attestation indépendante de leur SHA Git** ; le producteur doit contrôler les empreintes contre GitHub. Ces revues ne portent pas sur les nouvelles corrections rédigées ensuite. La revue D/E a fourni des constats partiels puis s'est interrompue avant son tableau de 32 verdicts : **ne pas la compter complète**.

Entre-temps, la tâche horaire a publié Q04C–Q04I jusqu'à `5d5f1d3c80432c10fdf96e1fd2e14aa060d5f167`. Ces ajouts ont été récupérés et préservés ; Q04F est complété, pas supprimé. Main relu directement : `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`. Les quatre PR ouvertes sont décrites au HEAD observé dans Q04J ; aucune fusion ni test nouveau inféré.

## 2. Constats et réponse concrète

| Constat de revue | Correction candidate | Vérification à effectuer sur le delta |
|---|---|---|
| Q01/COV05 encore désignés alors que terminés | RUN_STATE + EXECUTION_PLAYBOOK, notices des entrées maîtresses, prompt de conception aligné après publication | curseur cohérent, aucun retour à une recherche de source achevée |
| Export-only présenté comme seule voie texte | ADR_COMPOSITION_PERSISTENCE et Q04_RESOLUTION, cible V2 en copie, responsabilités et tranches CP0–CP6 | persistance/rollback/contrats réels distincts, pas de changement V1 implicite |
| Convention affine et verrouillage/groupes absents | ADR scène : matrices, unités, parent/locked/hidden/opacité, tests | descendants verrouillés protégés, group/ungroup préserve monde/IDs |
| Toutes pertes de trous interdites même pour booléen voulu | D01 algèbre float32 + topologie volontaire vs simplification conservatrice | anneau rempli volontairement admis, simplification destructive refusée |
| W05 appelé fabrication | D02 W03 export/W04 fabrication/W05 SD0 | pas de propriétaire ambigu |
| Guide facultatif fait disparaître Score/Attach | contrat SD §3 : HTML facultatif, consignes minimales obligatoires | boîte 5CUT/8SCORE avec HTML désactivé |
| « Aucun export partiel » contredit reprise par page | D03 + SD §4 : fichier atomique, lot PARTIAL, ZIP atomique | 17/30 ou page2 échouée conservent sorties saines |
| 50 sujets confondus avec 50 placements | D03 identités/checkpoints, ADR packs V2 distincts | aucune extension des 32 masques V1, cache invalidé aux paramètres exacts |
| Miroir HTV par couche oublié | D02/C03 lie T-V34-14-22 | couche sans décision reste à revoir |
| C15 réduit à coût P2, C18 tout reporté, catalogue C16 vague | D07 : économie/reprise P1 ; aperçu2D P1 ; enveloppe/pochoir W11-CAT | critères hérités et source priorities intacts |
| SD0 schéma/admission encore abstraits | contrat SD versionné, quotas logiciels, règles par rôle, source/hash/licence | dimensions connues ≠ machine connue, pas d'admission QA FAIL |
| Batch ne reprend que FAILED, recette obligatoire | D04 états complets + params_digest/recipe optionnelle | INTERRUPTED/CANCELLED/NEEDS_REVIEW traités sans doublon |
| Tags utilisateur considérés reconstruisibles | D05 stockage local durable distinct du cache, portabilité honnête | suppression index ne perd aucune préférence |
| Hash qualifié de signature | D06 authenticité/provenance distinctes d'intégrité | hash valide seul ne donne pas confiance auteur |
| Comparaison frameworks remplacée par impression | D08 protocole source à six tâches et matrice100 | résultats UNKNOWN admis en conception, gate de choix avant gros éditeur |
| Tests futurs absents utilisés pour bloquer conception | D09 statuts disjoints | pas besoin de matériel déjà testé pour adopter les recettes prévues |
| Autorité auto-merge V34 supposée transférable | Playbook/promotion : transfert explicite de politique/opt-in/prompt, DRAFT-only V35 par défaut | aucune élévation silencieuse via renommage |

Ces corrections sont des décisions et contrats écrits, **pas encore une relecture indépendante favorable de leur formulation finale**. Le prochain lot est REVIEW_DELTA.

## 3. Audit des 25 axes sur ce delta

| Axe | Traitement / preuve ou limite |
|---:|---|
| 01 | 24 lots sources non modifiés ; Q04 approfondit 05/06/12/13/17/18 ; revue globale encore ouverte |
| 02 | 141 IDs/critères sources conservés ; G6/G9 responsables explicites ; Q07 sémantique restant |
| 03 | 140 tickets non renumérotés ; neuf DoD lot06 reliés ; CP/SD sont des tranches, pas tickets doublons |
| 04 | 80 UX source intactes ; 48 verdicts sur ancien snapshot, 32 D/E revue non terminée ; pas 80 certifiés |
| 05 | 437 scénarios inventoriés ; 431 liens explicites historiques inchangés ; six propriétaires candidats, pas fausse citation source |
| 06 | Main/PR exacts observés ; tests nouveaux produit NOT_RUN ; aucune preuve matérielle inventée |
| 07 | V1 intact, cible V2 explicite, writer/version unique, source/float32/Subject/CAS et reprise détaillés |
| 08 | Quatre rôles export et trois Artifact.use V1 inchangés ; adaptateurs QA par rôle |
| 09 | Opérations typées, miroir HTV, consignes manuelles ; capacité SUPPORTED/UNSUPPORTED/UNKNOWN séparée disponibilité |
| 10 | Parcours novice/expert, action utile puis résultat/reprise ; pas de multiplication de boutons |
| 11 | Matrices/groupe/lock/texte/masks et Undo explicités ; aucune nouvelle UI livrée |
| 12 | Protocole Windows 1280/1366 et DPI100–200%, clavier/focus/lecteur d'écran ; essais NOT_RUN |
| 13 | CAS, ACK perdu, pending, interruptions, publication partielle par unité et rollback documentés |
| 14 | OCR facultatif, saisie manuelle, consentements et OOM ; aucun fournisseur installé |
| 15 | Alpha/source float32 préservés ; PNG PPI/ICC et dimensions par rôle ; aucune prétendue HD native |
| 16 | Booléens intentionnels distingués de simplification, trous/mm/XML sûrs, chemins DRAW séparés |
| 17 | 12/24/50, trois gabarits et catalogue suivant, checkpoints/CSV/instances explicités |
| 18 | SD0/1/2 schema/admission/quotas/ZIP/guide/reprise ; aucun nouveau ZIP créé ou testé |
| 19 | 33 opportunités et 15 groupes intacts, huit rejets maintenus ; Q06 fermeture globale encore à revoir |
| 20 | Mesures/protocoles et budgets logiciels déclarés ; aucun chiffre de performance présenté comme observé |
| 21 | Sources synthétiques, pas média privé/police/poids distribué ; EXIF/chemins/recettes inertes et licences |
| 22 | Branche docs uniquement ; main/AGENTS/politique/READY inchangés ; prompt de conception ajusté en session autorisée, pas par agent horaire |
| 23 | Port OCR recherché de manière bornée, réemploi jobs/writer/exporteurs ; cache/préférences/scène séparés |
| 24 | Promotion suspendue tant que revues et clôture ne sont pas prouvées ; procédure et autorisation propriétaire conservées |
| 25 | Aucun contrôle supprimé pour raccourcir le prompt ; seul curseur périmé remplacé, preuves limitées explicitement |

## 4. Contrôles reproductibles et portée

Exécuter les deux contrôleurs documentaires du playbook, comparer leurs entrées aux sources épinglées, et contrôler les liens des documents ajoutés/modifiés. Tester le curseur contre données corrompues : prochaine action déjà terminée, dépendance inconnue/cyclique/non finie, preuve absente, promotion indue. Ces tests ne valent pas validation du produit ni de toute la sémantique de la roadmap.

La fin de campagne n'est annoncée qu'après publication relue. La fin de **roadmap** exige encore les actions du RUN_STATE. Une impossibilité de revue indépendante reste REVIEW_PENDING, jamais un PASS autoattribué. Ne pas ajouter une nouvelle campagne d'idées pour retarder cette clôture : corriger les écarts identifiés, achever les décisions restantes, puis promouvoir selon la procédure.
