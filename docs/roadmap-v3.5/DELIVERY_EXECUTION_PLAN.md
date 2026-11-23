# SmartSVG V3.5 — Plan d'exécution A0 → C (sans nouvelle roadmap)

**Référence de livraison proposée en session propriétaire le 24/11/2026.** Conserve l'adoption V3.5, les unités W00–W16, les 141 exigences, 140 tickets, 24 lots, 80 UX et 437 scénarios hérités. Cet ordre est une **priorisation d'exécution** ; aucune exigence héritée n'est abandonnée ni reclassée implicitement. Les fonctions NOT_RUN sont distinctes des tests Python déjà exécutés.

## Autorités et règles de lecture

1. **Gouvernance :** AGENTS, READY, politique V35 et R13 sur `main`. Les agents horaires A/B ne modifient ni docs normatives, ni release/packaging, ni gouvernance.
2. **Objectif :** MASTER_PRIORISE, BACKLOG et critères W/SCN/CST/UXI/V3.3/V3.4, inchangés.
3. **Fait courant :** GET `branches/main`, PR ouvertes, leurs SHA exacts, checks, vrais jobs Windows et revues GitHub. Les instantanés de `EXECUTION_STATE.json` sont **datés**, non autorité temps réel pour SHA/PR.
4. **Qualification :** preuves unitaires/CPU, Windows test automatisé, application installée/GUI, Design Space, essais physiques et GPU **indépendantes**. `PASS`, `FAIL`, `SKIP`, `NOT_RUN`, `UNKNOWN` ne sont jamais interchangeables.

## Chemin critique (deux flux de fonctionnalité maximum, <=3 PR de code)

| Gate | Résultat utilisateur obligatoire | Conditions d'entrée et preuve de sortie | Responsable principal |
|---|---|---|---|
| **A0 — Socle requalifié** | Image PNG → projet V1 → sujet alpha admissible **ou sélection manuelle** → retouche → Undo → sauvegarde/réouverture/reprise ; original inchangé | Réutiliser le code W01/W02 actuel ; logs tests positifs, CAS périmé, collision sujet, annulation, interruption, restauration ; constater écarts réels | A Tk/UI, B backend/QA |
| **A1 — Alpha Windows** | Première sortie **réelle** PTC PNG ou Basic Cut SVG obtenue depuis l'interface, consentement explicite, export no-clobber, relecture SHA et dossier accessible ; ZIP portable identifié par version + SHA | A0 + W03/W04 sur un rôle qualifié + UI. Tester Windows propre, sans ComfyUI ni réseau, parcours clavier/focus. Production du ZIP via processus release autorisé, **pas** tâche horaire. Les quatre rôles W03 restent exigibles à sa clôture | A UI, B export/QA, mainteneur release |
| **A2 CAL-CUT** | SVG Basic Cut importé dans Design Space aux dimensions attendues, découpe physique et erreurs mesurées | A1 Basic Cut + [protocole CAL-CUT](CALIBRATION_PROTOCOL.md), photos, mesures signées et SHA ; aucun succès inféré de CI | Testeur avec Explore 5 |
| **A2 CAL-PTC** | PNG Print Then Cut imprimé et découpé avec écart de registration consigné | A1 PTC + [CAL-PTC](CALIBRATION_PROTOCOL.md), calibration propre, version DS, modèle d'imprimante | Testeur avec Explore 5 |
| **B1 — Livraison mono-export** | W05 plan SD0, W06 ZIP vérifié dès une sortie réelle, guide offline ; W08 PTC documenté et bibliothèque de base | ZIP relu, manifeste SHA, confidentialité, aucun overwrite, Windows accessible. Ne dépend pas de l'achèvement des quatre exports | A UI, B backend, release autorisée |
| **B2 — Édition durable avancée** | Scène V2, calques/texte/gabarits rééditables et quatre sorties distinctes, séries avec reprise | CP0 fixtures puis CP1 lecteur/plan, CP2 migration en copie+CAS+recovery, CP3 scène; CP4/5/6 par capacités ; aucune altération du writer V1 | Équipe par tranche, migration à procédure dédiée |
| **C — Extensions** | OCR/diorama/IA facultative/optimisations spécialisées | Gate par capacité, licence et confidentialité ; CPU manuel fonctionne sans modèle et sans GPU | Propriétaires W14/W16 |

**A1 (logiciel utilisable) et A2 (qualification matérielle) sont séparés.** L'absence d'appareil ne bloque pas CP0 ou des tests sur fixtures, mais interdit toute promesse de coupe certifiée. W07 peut produire des diagnostics descriptifs sur géométrie réelle avant calibration ; les seuils matière restent UNKNOWN. W09 n'ajoute des lignes physiques que quand le coupon est qualifié.

## Décisions transversales d'exécution

- **Framework W13 :** conserver Tk pour les micro-tranches utiles. Avant un grand éditeur de calques, benchmark borné Tk baseline vs PySide6/Qt et Tauri : lancement à froid offline, canvas 12 sujets, focus/clavier, 1366×768 et DPI 200 %, latence, sauvegarde V1 isolée, dépendances/licences et ZIP Windows. Publier score/protocole/limites et ADR de choix ; aucune migration sur simple intuition.
- **Persistance :** l'ADR `ADR_COMPOSITION_PERSISTENCE.md` existe. CP0/CP1 peuvent progresser en conception/fixtures hors premier export ; **CP2 n'est pas activé sans qualification**. CP3 précède W10 texte durable, W11 gabarits et certaines séries W12. Pas de TextNode caché dans V1 et pas de second writer.
- **W15a :** ZIP portable versionné et traçable dès A1 ; W15b : installeur, mises à jour, rollback et migration lors de B2 selon preuves. Une Alpha historique ne décrit pas automatiquement la dernière version.
- **W16 :** responsabilités détaillées dans BACKLOG §4. W12 possède le parsing CSV générique, W14 l'OCR fournisseur, W16 les usages spécialisés. Pas de duplication.
- **Pilotage :** deux flux produits actifs maximum (p. ex. UI + backend), <=3 PR de code, finir les intégrations prioritaires avant nouveaux sous-lots. Éviter un quota de PR. Une PR admissible = unité testable, pas un indicateur autonome de valeur.
- **Fiches :** micro-tranche P0 simple : besoin observable, entrées/sorties et invariants, tests succès/échec/concurrence, owner/PR+SHA, rollback. Les fiches plus longues sont réservées aux changements format/protection/physique ou capacités nouvelles à risque.
- **Gel des idées :** conserver les fonctionnalités héritées dans leur priorité prévue ; nouveaux concepts après A1 dans la file de recherche, sans devenir des critères bloquants. Les statuts « différé » concernent la **livraison**, jamais une suppression normative implicite.

## Risques et signaux observables

| Risque | Signal déclencheur | Responsable | Mesure |
|---|---|---|---|
| Import Design Space variable | SVG rejeté, taille changée, éléments transformés | W03/W04 + testeur | Profil de sortie/version DS, régression sur fixtures, rapport de calibration |
| Corruption/reprise de projet | CAS divergente, crash/ACK ambigu, original modifié | W01/W02 | Refus et réconciliation du writer canonique, tests Windows |
| Migration V2 prématurée | Deux writers actifs, ressource perdue | CP0–CP3 | Copie source immuable, receipts, cas adversariaux avant activation |
| Distribution périmée | ZIP SHA différent du code testé, dépendance ComfyUI | W15/release | Build identifié + matrice environnement propre et rollback |
| OOM/latence IA | GPU indisponible, mémoire dépassée | W14 | Geste manuel/CPU toujours viable, refus explicite |
| Embouteillage de revues | PR gelée sans examen, WIP saturé | A/B R13 | Revue inter-cycle et clôture d'abord, limiter les flux |
| Licences/provenance | Modèle/asset ou fonte non autorisé | W14/W10 | Identifier licence/SHA, refus d'importation redistribuable douteuse |

Une fois les gates atteints, conserver les preuves factuelles et le lien vers le build/commit ; ne jamais prétendre qu'une fiche de conception ou une CI Linux représente une qualification machine.
