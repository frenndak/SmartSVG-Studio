# SmartSVG Studio — reprise canonique V21 (27 octobre 2026)

**Statut : PROPOSITION D'INTÉGRATION, non fusionnée dans `main`.** Ce protocole remet à plat le développement sans jeter les corrections déjà réalisées. Il n'autorise **aucune promotion automatique en version stable**, aucune fusion sans revue et aucune diffusion des ressources utilisateurs.

## 0. Décision de version : une seule vérité par niveau

| Type de référence | Valeur vérifiée au 27/10/2026 | Usage autorisé |
| --- | --- | --- |
| **SPEC_B0** | Roadmap V3.2 figée, qui désigne **V21.14.1** comme référence historique | Objectifs, priorités, gates ; **pas** preuve d'équivalence logicielle |
| **CODE_REF** | ZIP **V21.15.2** SHA-256 `9369656f0216cebb6dccce0d0155bffa16d8c384da6a984bf848cdd8aa003c54`, **652 fichiers ZIP** et **651 empreintes manifestes** | Dernier snapshot logiciel installé/reproductible **dont la provenance est établie** |
| **MAIN** | `e2aae5b635721bcb7ff3b48df8c48b6a99e2220b` (instantané du 27/10) | Contient la source importée ; **pas** les PR #13–#31 |
| **CANDIDATES** | 18 PR encore ouvertes, avec leurs HEAD/BASE spécifiques | Code préparé et parfois L1 testé, **non livrable comme nouvelle version** |
| **NEXT_RC** | Nom réservé : `V21.16.0-rc.1` (**NON CRÉÉ**) | Ne devenir réel qu'après arbre consolidé, tests, distribution et rollback vérifiés |

Ne plus mélanger les appellations V21.15.3–V21.15.6 de correctifs isolés avec une **release installable complète**. Les correctifs de ces versions sont des candidates de PR, pas une mise à jour en chaîne universelle. Ne pas requalifier arbitrairement V21.15.2 « V22 stable ».

Voir [ADR-20261027-001](ADR-20261027-001.md) pour l'écart historique SPEC_B0 / CODE_REF.

## 1. Vérification indépendante de la source de reprise

L'archive `ComfyUI_SmartSVG_Studio_V21_15_2_Installation.zip` fournie pour la reprise est identique octet pour octet à celle référencée par `main`.

**Vérification locale du 27/10 :** SHA-256 exact, ZIP CRC OK et 652 entrées. **43 tests Python ciblés** PASS (`test_v21152`, `test_v21151_image_qa`, `test_v2115_governance`, `test_v2114`, `test_v21141_color`) et **12 scripts JS** PASS. La **suite Python globale n'est PAS validée** dans ce relevé : elle a dépassé le délai d'exécution local. Historique GitHub mentionne 876 tests, à ne pas attribuer indûment à cette exécution. Machine ComfyUI réelle, RTX 3070 et Explore 5 : **NON TESTÉES**.

Installer/retirer les versions uniquement en fermant ComfyUI, en sauvegardant le dossier de l'extension et les projets/exports, et en gardant **une seule copie active sous `custom_nodes/`**.

## 2. Recomposition du développement : ordre canonique

L'ordre ci-dessous **ne préjuge pas l'autorisation de fusion**. Après chaque parent, rafraîchir l'ascendance, exécuter des tests liés aux chemins réellement modifiés, vérifier les conflits et obtenir l'approbation autorisée prévue par la politique du dépôt.

| Priorité / ordre | PR / branche | Contenu conservé | Critère avant intégration |
| --- | --- | --- | --- |
| A0 | **#13** sécurité / gouvernance | Prévol trusted-main, limitations dépenses/WIP, chemins protégés | Revue humaine indépendante, CI exacte de confiance et règles GitHub ; aucun changement direct de `main` non approuvé |
| A1 | **#14** G1.2 contrats | SourceAsset, Mask, Subject, Artifact, QAResult, contrôles dimensions et chemins | Tests positifs/négatifs, compatibilité des contrats et revue ; HEAD & tests recalculés |
| A2 | **#15** G1.3 archive, **#16** G1.4 reprise, **#17** G1.5 Express | Archive `.smartsvg`, récupération, interface d'entrée | Tests archive adverse, round-trip retouches, rollback installation et aucune perte de fichiers |
| B0 | **#18** parcours Express, **#19** espaces projets | Import, choix, diagnostic, stockage | Tests du flux novice sans graphe et synchronisation projet/UI |
| B1 | **#20 et #21 : complémentarité sous réserve de revue** | #20 : masques par sujet ; #21 : sessions de pinceau | **Chevauchement prouvé** : `engine/project_routes_g22.py`, `engine/smartsvg_core/project_workspace_g22.py`. Composer les changements sur un même contrat de projet, exécuter sauvegarde/redo/reload et scénarios hostiles ; **ne pas fusionner les deux à l'aveugle** |
| B2 | **#22** masque float32 pleine résolution | Masques fidèles, nœud coffre et persistance | Tester sur la composition choisie B1, vérifier bit-à-bit et coût mémoire ; ne pas écraser le parser PNG durci de #15 |
| B3 | **#23 et #24 : arbitrage UX** | #23 : reprise d'états ; #24 : panneau Express ergonomique | Chevauchement sur `smartsvg_express_start_g15.js` et `smartsvg_project_panel_g22.mjs`. Tester un parcours combiné clavier/souris 1366×768, crash/reprise et état d'erreur |
| C0 | **#25 et #31** sécurité/export | QA SVG Cut et rejet d'XML actif | Croiser les deux contrôles : fichiers SVG valides, SVG actif malveillant, fermeture, dimensions en mm, micro-chemins ; pas de doublons de vérifications incohérentes |
| C1 | **#26 → #27 → #28** inspecteur | Inspection non destructive, coordonnées des fragments, liaison avec l'éditeur | Conserver la pile ordonnée ; tests de sélection, focus, corrections réversibles, accessoires conservés, aucune exportation automatique trompeuse |
| C2 | **#30** ordonnancement public gratuit | CI read-only et backlog sans API payante | Ne déclarer `schedule` fonctionnel **qu'après fusion et observation d'un vrai déclenchement sur `main`**, puis retire progressivement l'ancien orchestrateur selon la migration |

**Règle de réduction de backlog :** ne plus ajouter de PR fonctionnelle indépendante tant que les racines et les variantes ne sont pas intégrées ou explicitement arbitrées ; une dérogation P0 sécurité doit être motivée. Une implémentation complémentaire peut nécessiter un **unique lot de réconciliation** sur branche existante, avec tests de non-régression et journal de décision.

## 3. Protocole d'intégration correct

1. Lire en direct l'état de `main` et des PR (BASE, HEAD, conflits, CI), jamais un ancien résumé comme état actuel.
2. S'assurer que tous les parents requis ont été intégrés et que les changements combinés n'ont pas effacé de correction (trois-way diff, inventaire par chemins, tests négatifs des deux variantes).
3. Valider sur le candidat choisi avec CI **sur le vrai HEAD et définition de workflow de confiance**. Une CI `pull/N/merge` synthétique mesure une autre référence et doit être étiquetée comme telle.
4. Exiger la contre-expertise, l'approbation autorisée et les protections GitHub. Les responsables humains peuvent juger un gate **logiciel L1** sans prétendre avoir validé une fabrication L3.
5. Après fusion, constater le nouveau `main`, les invariants et les tests du dépôt **fusionné** ; réévaluer la PR fille.
6. Dès que G1/G2 cohérents et les correctifs critiques d'export ont passé les preuves L1, préparer un **seul ZIP candidat** via build déterministe, manifeste fichiers/SHA256, tests d'installation et script de rollback. Réserver l'étiquette `V21.16.0-rc.1` jusqu'à cette étape. La version principale n'est plus devinée à partir du plus grand numéro de PR.

## 4. Tests et preuves de recette de la future candidate

**L1 automatisable :** schémas et modes de couleurs, ZIP hostile/CRC, chemins d'extraction, round-trip exact `.smartsvg`, undo/redo, masques pleine résolution, cohérence des exports PNG Print Then Cut / SVG Cut / SVG éditable, unités millimétriques, SVG/XML actif, images synthétiques 12/24, contrôles de sécurité et d'accessibilité. Réparer chaque P0/P1 avant étiquetage.

**L2 réel :** lancer ComfyUI sur le PC prévu, vérifier les nœuds et workflows historiques et l'UI Express, puis charger et exécuter réellement les fournisseurs IA sur RTX 3070 8 Go ; mesurer mémoire, temps, échecs et fallback.

**L3 réel :** importer dans Design Space, vérifier dimensions réelles, réaliser la découpe sur Explore 5 avec papier et tapis identifiés, tester un sticker PNG, une silhouette Cut et une planche. Les pointillés dessinés (visuels) ne sont pas des perforations automatiquement réalisables ; ne pas transformer des dizaines de tirets en micro-coupes imprévues.

**G0.3 non acquis :** les neuf cas T-01–T-09 sont inventoriés, mais leurs masques humains de référence sont `PENDING`. Ne pas placer ces images dans un dépôt public sans droits.

## 5. Livrables et définition de version

**Aujourd'hui :** ZIP original V21.15.2, archive d'audit/réinstallation locale, registre d'avancement et PR existantes. **Aucune nouvelle version intégrée ni nouvelle version stable annoncée.**

Pour **V21.16.0-rc.1** :
- arbre Git unique / SHA traçable ;
- construction depuis ce SHA uniquement, ZIP et manifeste des fichiers/empreintes ;
- état des tests horodaté et différencié L1/L2/L3 ;
- feuille de migration, retour arrière, incompatibilités connues et checks de non-régression ;
- sources privées/non redistribuables explicitement exclues du ZIP public et licence/attributions vérifiées ;
- démonstration au minimum d'un projet enregistré puis réouvert fidèlement.

Ne pas utiliser le mot **stable** ou **prêt Cricut** avant la recette G4/L3 correspondant aux parcours revendiqués.

## 6. Conformité open source et disponibilité

Le dépôt source est **public**, mais l'absence de fichier de licence explicite vérifiée signifie qu'il ne faut pas affirmer que tout son contenu est librement redistribuable. Les modèles, poids, images, polices, logos et tests utilisateurs demandent chacun leur propre droit. Réaliser l'audit d'historique et exclure les données sensibles sans les republier.

Le journal #29 est un historique informatif, pas une approbation GitHub. Le master `docs/ROADMAP_MASTER_v3_2.md` est figé et ne doit pas changer dans ce chantier.

## Rollback de ce protocole

Ce document n'écrit rien dans `main`, ne modifie pas l'archive ni les nœuds et n'annule aucun commit historique. Le retirer de la PR #30 rétablit les documents précédents sans effet sur les fichiers utilisateur.
