# Clôture de revue globale et résolution des trois remarques

15 novembre 2026. Base de revue indépendante : `6f611a50a6eebf35f843decb87c7f6d1aeb9c6cd`, main `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`. La [revue finale](GLOBAL_REVIEW_2026_11_15.md) examine les 25 axes et conclut G35-01..11 et15 PASS documentaire, sans Critical/Important. Son empreinte SHA256 est `c2bea5cbe8f58ff6867d9d78744ec9bd3dfd25ef0a405da70bebfae9bf6e617d`. La [revue préliminaire horaire](GLOBAL_REVIEW_PRELIMINARY_2026_11_15.md), ajoutée au commit `9fc6cf489d0a0c0aa179b5e61cf3198c1beff6c2`, est conservée ; ses demandes de preuve sont traitées par la revue finale et les vérifications ci-dessous.

## Résolutions vérifiables dans le delta après revue

| Constat | Correction de conception ; aucune implémentation produit |
|---|---|
| M01 : persistance/texte encore « à décider » dans deux entrées | MASTER rang6 et §7, BACKLOG W10 renvoient à l'ADR décidée et CP0–6 futurs ; code V1 strokes distinct du TextNode V2 cible. Aucune nouvelle ADR ni writer activé. |
| M02 : « 50 partitionné » ambigu | MASTER rang8 sépare calcul/placements externes bornés V1 et 50 sujets persistés via packs internes d'un même projet V2. Limite32 V1, identités et absence de troncature conservées. |
| M03 : E2E04 V1/receipt et échec SAVE | QA E2E04 sépare CAS V1 de receipt/replay CP2/V2 ; matrice SAVE exige inspection primaire/backup/pending, receipt seulement si contrat durable, COMMITTED_NEEDS_RECOVERY ou UNKNOWN avant retry. |

Le curseur passe à **PROMOTION_DOCS READY** ; GLOBAL_REVIEW est DONE pour la conception. `candidate_status=DESIGN_REVIEWED_PENDING_INTEGRATION` décrit cette étape sans adoption. Le contrôleur de curseur accepte ce statut seulement si GLOBAL_REVIEW est DONE ; ses protections d'autorité V3.4/promotion false et dépendances restent requises. Les sorties des contrôleurs ne déclarent plus une revue sémantique forcément ouverte : elles indiquent que les verdicts sémantique/produit sont séparés de l'intégrité. Le contrôle humain reste porté par les rapports, pas par le message PASS.

## Vérification et frontière d'intégration

Avant publication, rejouer les trois commandes de l'EXECUTION_PLAYBOOK avec `--main-root history-work` pour transfert et priorités, contrôler les liens locaux et la correspondance des blobs publiés. Le nouveau guard de statut doit refuser une candidate annoncée revue si GLOBAL_REVIEW n'est pas DONE. Ces résultats sont consignés dans PROGRESS ; aucun test produit n'en est déduit.

Au dernier contrôle API : main inchangé, quatre PR code DRAFT #138/#139/#140/#144. **G35-12 reste PENDING**, WIP code au-dessus du maximum3 ; ne pas ouvrir une PR docs concurrente tant que ce prérequis n'est pas satisfait. READY désigne la préparation/pré-vérification de cette étape, pas une permission d'ouvrir ou fusionner immédiatement. G35-13 gouvernance et14 handoff restent PENDING ; V3.4 active. La revue globale n'est pas à recommencer sans changement de source, contrat ou défaut concret.

## Correction de méthode du producteur existant

Le dernier résultat de la tâche V3.4 signalait une recherche de PR renvoyant une issue et concluait métadonnées indisponibles. Cette session a obtenu par API directe la liste PR et les HEAD réels. Une consigne R10.4 a été ajoutée à la tâche existante : lire `/pulls?state=open&per_page=100`, puis `/pulls/{numero}`, les fichiers/revues/CI et main directement ; distinguer recherche défaillante et API indisponible. Relecture du prompt effectuée après mise à jour : contenu exact, cadence et activation inchangées. **Cible V3.4, opt-in et politique R1 inchangés ; aucun handoff V3.5, aucune fusion ni réussite future du producteur revendiqués.** Cette réparation de lecture aide à traiter le WIP sans étendre ses permissions.

## Contre-revue indépendante du delta après le rapport final

**15 novembre 2026 — reviewer `review_v35_global`, lecture seule hors ajout de cette section, aucun sous-agent. Verdict fortement borné : delta documentaire recevable pour publication ; M01/M02/M03 résolus ; aucun Critical, Important ou nouveau Minor identifié dans ce delta.** Le rapport initial reste inchangé, SHA256 `c2bea5cbe8f58ff6867d9d78744ec9bd3dfd25ef0a405da70bebfae9bf6e617d` recalculé et confirmé.

Comparaison par diff des six copies de référence `6f611a50a6eebf35f843decb87c7f6d1aeb9c6cd` fournies par le coordinateur : MASTER, BACKLOG, QUALITY, RUN_STATE et les deux vérificateurs. Lecture des nouveaux bandeaux README/PROMOTION_CHECKLIST/COMPLETION_QUEUE, de l'entrée PROGRESS et de la présente résolution. Aucune nouvelle revue globale ni nouvelle qualification produit n'est revendiquée.

| Point du delta | Constat de contre-revue |
|---|---|
| M01 | MASTER rang6/§7 et BACKLOG W10 distinguent correctement décision ADR/CP0–6, future implémentation/adoption et code V1 strokes. Aucun writer V2 activé et aucune nouvelle dépendance SD introduite. |
| M02 | MASTER rang8 sépare calcul/placements externes et50sujets persistés dans les packs internes d'un seul projet V2 ; plafond V1, identités et non-troncature préservés. |
| M03 | QUALITY E2E04 réserve receipt/replay durable à CP2/V2 ; cas SAVE traite primaire déjà publié, backup/pending et inspection avant retry. Il n'attribue pas de receipt durable au V1. |
| Vérificateur de curseur | Diff fonctionnel limité à l'admission du statut DESIGN_REVIEWED_PENDING_INTEGRATION sous GLOBAL_REVIEW DONE. Autorité3.4, promotion_ready=false, preuves obligatoires pour DONE, graphe/dépendances, historique source et NOT_RUN produit restent imposés. Aucun affaiblissement de ces invariants détecté. |
| Messages PASS | Dans les deux vérificateurs, le texte distingue désormais intégrité et verdict humain ; aucune assertion du registre de priorité n'a été changée pour produire un faux PASS sémantique. |
| États et bandeaux | GLOBAL_REVIEW DONE s'appuie sur les deux rapports ; PROMOTION_DOCS READY désigne la pré-vérification, G35-12..14 demeurent PENDING et V3.4 active. Le WIP4/max3 interdit encore l'ouverture concurrente immédiate. |

**Contrôles réexécutés par ce reviewer :** trois vérificateurs documentaires exit0 ; validation en mémoire du nouvel état et de l'ancien état compatible, tous deux acceptés ; trois mutations indépendantes refusées (statut revue sans GLOBAL_REVIEW DONE, active_roadmap3.5, promotion_ready=true). Le premier refus produit aussi le diagnostic de prérequis inachevé de PROMOTION_DOCS. Liens Markdown locaux :153cibles de fichiers uniques, aucune absence ; ancres et URL externes hors ce contrôle. Aucun fichier de test ni produit modifié ; Windows/GPU/Design Space/physique et performances restent NOT_RUN.

La modification du prompt du producteur et sa relecture distante sont **des preuves rapportées par le coordinateur**, pas une vérification distante effectuée par ce reviewer. Leurs limites sont correctement exposées dans la résolution : méthode de lecture API seulement, ancienne cible/cadence/autorisation maintenues, aucun handoff ni succès futur inféré. Cette contre-revue n'autorise ni modification d'automation supplémentaire ni fusion. La correspondance des blobs après publication et le HEAD courant restent à contrôler par le coordinateur, puis G35-12 suit ses propres conditions.
