# SmartSVG — Backlog d'exécution évolutif

Document de suivi non figé. La référence contractuelle reste `docs/ROADMAP_MASTER_v3_2.md` (ne pas modifier son SHA). Les tickets ci-dessous sont des **propositions**, non des fonctionnalités livrées.

## Prochaines portes de validation

| Lot | Priorité | Critère d'entrée | Critère de sortie |
| --- | --- | --- | --- |
| CI-01 | P0 | PR #30 encore ouverte | Précontrôle public réussi sur HEAD exact, revue puis intégration contrôlée ; cron observé sur `main` avant de déclarer le calendrier actif |
| G1-01 | P0 | PR racines #13/#14 et dépendances vérifiées | Tests ciblés de sécurité et contrats, CI exacte, revue indépendante, intégration dans l'ordre d'ascendance |
| G2-01 | P0 | G1 réellement intégré | Sauvegarde et réouverture `.smartsvg` sans perte de source, masques ni retouches ; test de fichier corrompu |
| CUT-01 | P0 | Modes d'export séparés | PNG Print Then Cut, SVG Basic Cut et SVG éditable clairement distingués ; chemins fermés, unités mm et absence de doubles coupes vérifiés |
| SHEET-01 | P1 | Contrat CUT-01 validé | Planche de 12/24 éléments avec modes contour individuel, cadres rectangulaires et coupe extérieure ; contrôle des marges et collisions |
| UX-01 | P1 | Parcours Express disponible | Importer, inspecter, corriger, prévisualiser la coupe et exporter sans ouvrir le graphe ComfyUI ; clavier et erreurs testés |
| AI-01 | P1 | Fournisseur local et environnement documentés | Repli sûr en cas de mémoire GPU insuffisante ; tests L2 sur matériel réel avant toute promesse d'inférence |
| HW-01 | P1 | Fichiers de recette et version Design Space identifiés | Import réel et essais Cricut Explore 5 documentés par format/matériau ; aucune certification par CI seule |

## Relevé d'avancement à preuves séparées — 27 octobre 2026

**Instantané historique, à relire avant chaque décision.** `main=e2aae5b635721bcb7ff3b48df8c48b6a99e2220b` ; **18 PR ouvertes** ; aucune fusion G1/G2 constatée à cette date. Toute divergence ultérieure avec GitHub prévaut sur ce tableau. **Aucun pourcentage de roadmap n'est déduit du nombre de commits ou de tests.** Lire également [ADR-20261027-001](ADR-20261027-001.md), proposé sur cette PR : `SPEC_BASE=B0@V21.14.1` ≠ `CODE_BASE=V21.15.2` importé.

| Gate V3.2 | Travail observé | État défendable / preuve manquante |
| --- | --- | --- |
| G0.1 | Archive V21.15.2, SHA et 651 entrées du manifeste admises dans `main` | **CODE_BASE vérifiée**, mais **B0 V21.14.1 non requalifiée** : ne pas substituer les références |
| G0.2 | `engine/governance/evidence/corpus_manifest.json` : T-01 à T-09, R-01/R-02 ; sources T privées listées avec empreintes | **Inventorié**, pas de redistribution autorisée ; accès local aux originaux à confirmer pour une nouvelle recette |
| G0.3 | `truth_review_template.json` : 9/9 cas T encore `PENDING`, R-01/R-02 synthétiques validés | **BLOQUÉ PAR VÉRITÉ TERRAIN HUMAINE** ; deux annotations, arbitrage et masques cibles manquent |
| G0.4 | Risques dans le master + registres techniques | **Documentation partielle**, preuve d'une matrice des risques testés et des exceptions en environnement final non établie |
| G1.1 | `inventory_result.json` : **186 workflows analysés, 98 IDs de nœuds au snapshot importé**, 94 types custom utilisés et zéro type introuvable | **Pré-inventaire statique** de V21.15.2 ; ni résultat B0 V21.14.1 ni test réel de chargement ComfyUI |
| G1.2–G1.5 | PR #14–#17 : contrats, archive, récupération et Express | **Implémentations en branches**, CI L1 sur merges synthétiques ; rien de nouveau fusionné dans `main` |
| G2.1–G2.5 | PR #18–#24 ; certaines fonctions ne correspondent pas exactement au numéro de gate de la roadmap | **Candidats G2**, validation UX novice/clavier/navigateur réel et intégration absentes |
| G2.6 | PR #26 → #27 → #28 (inspection et repères de fragments dans l'éditeur) | **Candidat distinct**, chaîne et tests logiciels à qualifier avant ajout au parcours G2 canonique |
| G2.7–G2.9 | Exigences clavier, triple prévisualisation, reprise | **Non démontrées de bout en bout** : prévoir tests UI et persistance |
| G3 | IA locale RTX 3070, diagnostics modèles et VRAM | **L2 réel non testé** ; une IA mentionnée dans le code ne vaut pas exécution sur machine |
| G4 | PNG Print Then Cut, SVG Basic Cut, planche 12/24, Explore 5 ; PR #25 précontrôle Cut partiel | **L3 import/physique non testé**, ne pas déclarer « Cricut prête » |
| G5–G7 | Vectoriel riche, atelier créatif, fabrique et lots | **Planifiés / exploratoires** ; aucune acceptation gate constatée |
| G8–G9 | Recette V22.0, puis extensions avancées | **Non admissibles comme terminés** ; jalons futurs |

### Correspondance contractuelle entre numéros G et intitulés de PR

Un numéro de branche n'est **pas** une preuve que le gate homonyme est acquis.

| PR / modules candidats | Produit réellement visé | Critère V3.2 encore à vérifier |
| --- | --- | --- |
| #14 `project_contracts` / #15 `project_archive` | G1.2/G1.3 : identités et sauvegarde native | Réouverture complète + rollback, adversarial, migration de fixture |
| #16 / #17 | G1.4/G1.5 : reprise sûre et écran Express | Installation/rollback réel, compatibilité ComfyUI historique |
| #18–#19 | Express guidé et espace projet | **G2.1/G2.2 partiels** : sélectionner réellement le sujet, pas seulement sauvegarder un projet |
| #20 (masques PNG par sujet) / #21 (sessions de pinceau) | **Capacités complémentaires potentielles** du G2.2/G2.3 | Comparaison de contrats, détection des changements concurrents, persistance fidèle, annuler/refaire |
| #22 (masques float32 exacts) | Persistance G1.3 et retouches G2.3 | Comparaison bit à bit, temps/mémoire, refus des masques incomplets |
| #23 (état de reprise) / #24 (UX Express) | Deux axes de G2.5, pas un « G2.5 livré » par leur seul intitulé | Même parcours novice/écran étroit, pas de bouton inerte, correctifs combinables uniquement après conflit analysé |
| #26/#27/#28 | G2.6 : avertissements localisés, zoom et corrections réversibles | Cas adversarial, synchronisation masque/source, undo et absence de faux export |
| #25 (SVG prévol) | **Une tranche de G4.2**, pas G4 complet | Fermeture/contour en mm, import Design Space réel et coupure sur coupon |

### Micro-lots recommandés, à arbitrer à chaque cycle

| ID de suivi proposé | Priorité | Dépend de | Accepter uniquement avec… | Condition d'arrêt |
| --- | --- | --- | --- | --- |
| REX-01 — Preuve G0.3 | P0 | `corpus_manifest`, accès autorisé aux originaux | 9 cas T annotés, 2 avis ou statut de désaccord, fichiers cibles **hors dépôt public** | Droits inconnus, masques absents ou ambiguïté non arbitrée |
| REX-02 — Intégration racine | P0 | #13/#14 actuelles, protections mainteneur | CI de confiance sur commit correct, approbation indépendante réelle, aucun conflit puis intégration dans ordre | Workflow CI modifiable non attesté, revue ou HEAD périmés |
| REX-03 — Réconciliation G2.3/G2.5 | P0 | G1 fusionné, variantes #20/#21 et #23/#24 | Matrice comportement/tests, décision de composition ou exclusivité, pas de perte de masque | Conflit sur format `.smartsvg` ou historique non réversible |
| REX-04 — Assurance Print/Cut | P0 | Export PNG/SVG séparé, G2 contrôle | Géométrie Basic Cut et pixels PNG indépendants, dimensions mm, vue chemin de lame et avertissements | Une sortie décorative déguisée en Basic Cut ou double découpe cachée |
| REX-05 — Planche douze sujets | P1 | T-02 vérité terrain, G2.6, G4 prévol | **Deux modes indépendants** testés : contour silhouette et découpe **rectangulaire explicite** ; comparaison des trous, accessoires, marges et absence de faux chemin | Confusion entre ligne de pointillés visuels, perforation réelle et suite de micro-coupes ; ne pas annoncer une fonction machine sans coupon |
| REX-06 — UX débutant | P1 | Parcours G2 intégré | Test clavier + souris, 1366×768 et 1920×1080, erreurs et reprise après crash sur navigateur réel | Action masquée, perte de correction, fausse couleur « prêt » |
| REX-07 — Matériel réel | P0 pour gate G4 | Projet/exports G4, installation locale et consentement test | Journal ComfyUI/RTX3070 (L2) et Design Space + Explore 5 (L3), feuille/matière/lame/erreur mesurée | Mesures inexistantes ou inférence simulée présentée comme essai réel |

**Priorité transversale :** inventorier les droits des images/fixtures et une licence source appropriée avant toute affirmation de redistribution libre. Un dépôt public ne signifie pas « ressources réutilisables ».

### Règle de mise à jour de ce registre

À chaque relevé, indiquer `MAIN_SHA`, numéro de PR, `HEAD_SHA`, `BASE_REF`, statut draft, preuve L1/L2/L3, type de checkout (direct ou merge synthétique), date UTC et **la preuve manquante**. Ne pas écraser une observation historique : ajouter une nouvelle date avec un lien vers la PR/CI. L'issue #29 est le journal, **pas** un validateur des assertions. Le prochain cycle du producteur doit lire GitHub en direct **avant** ce document ; en cas de conflit, marquer l'état obsolète et corriger le registre par une PR existante.

## Règles pour le producteur automatique

1. Lire les PR ouvertes et leurs BASE/HEAD avant de sélectionner **un seul** micro-lot.
2. Ne pas confondre succès de la PR fille et intégration de ses parents ; choisir une seule des variantes concurrentes.
3. Écrire les tests négatifs pertinents pour le lot : archive malveillante, SVG/XML non sûr, collision de planche, dimension invalide ou perte de masque selon le périmètre.
4. Créer une PR ou enrichir une PR existante ; enregistrer SHA et CI, puis faire une contre-expertise ciblée.
5. Séparer L1 tests logiciels, L2 ComfyUI/IA réelle et L3 fabrication Cricut. Les niveaux L2/L3 ne bloquent pas les PR purement logicielles qui ne revendiquent pas ces résultats.
6. Ne pas fusionner sans revue autorisée, ne pas exposer d'assets privés, ne pas activer de dépenses API par défaut.
