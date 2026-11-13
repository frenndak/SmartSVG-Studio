# File de clôture V3.5 — travail restant concret

**14 novembre 2026 — CANDIDAT.** La priorisation et les inventaires ne valent pas fin de conception. Cette file donne un ordre de clôture sans nouvelle campagne de reformulation. Le maître [MASTER_PRIORISE.md](MASTER_PRIORISE.md) ordonne la livraison produit ; la présente file ordonne les **travaux documentaires restants**. Ils ne sont pas la même chose.

| Point | Priorité de clôture | Manque à résoudre | Livrable de sortie et preuve attendue |
|---|---|---|---|
| **Q01** | immédiate, reprise COV22 | Les cinq contrats de transfert ont des ports et commentaires désormais relus ; toutes leurs associations exactes aux critères/DoD/tests ne sont pas closes | Matrice clause par clause O-001/002/004/028/032 → critère source → V34/DoD → scénario local → contre-exemple ; aucun lien seulement « même domaine » |
| **Q02** | haute | Six scénarios sans TEST→TICKET explicite et dix obligations G6/G9 sans V34 direct | Utiliser COV16 et les rapprochements corrigés : propriétaire **candidat** distinct, intégralité du critère, tests et décision d'exception ; aucune réécriture des sources |
| **Q03** | haute | Modèle objets/calques/texte/transformations et rôle d'Artifact V1 | ADR par responsabilité : ce que V1 porte déjà, brouillon en mémoire, projection externe et cas nécessitant une migration ; aucun TextNode inventé dans strokes |
| **Q04** | haute | Toutes les 80 capacités ont des fiches, mais la chaîne sémantique complète n'est pas certifiée | Lire les derniers COV18 corrigés, traiter les divergences de priorité/mapping et lier une fiche finie par ID à ses critères/tests ; ne pas refaire les 80 premiers audits |
| **Q05** | haute | Smart Delivery reste un contrat externe, QA historique non universelle | Compléter le plan SD0/SD1/SD2 par rôle et prévol ciblé, erreurs et quotas configurables ; ne pas attendre quatre exporteurs achevés pour spécifier PNG-seul |
| **Q06** | ensuite | Les 33 opportunités et 15 groupes #142 sont classés mais pas tous reliés à un delta codable et au coût | Achever raisons de fusion/rejet, entrée/sortie, états, DoD, risque et tranche ; conserver les huit rejets et les fonctionnalités facultatives |
| **Q07** | transverse | Les 437 assertions sont inventoriées ; la présence de références ne prouve pas la couverture des critères | Réconciliation assertion par assertion depuis les trois inventaires, statuts EXACT/PARTIEL/À_ARBITRER ; citer les contre-exemples, pas un compteur de liens seul |
| **Q08** | avant clôture de conception | Architecture UI, accessibilité, performances et packaging doivent être décidés à partir de preuves disponibles | ADR, critères et protocole de benchmark ; résultats NOT_RUN si non disponibles. Un futur benchmark n'est pas requis pour terminer tous les contrats indépendants |
| **Q09** | avant proposition d'adoption | Revue indépendante globale et 25 contrôles non tous fermés | Rapport contradictoire borné, défauts corrigés ou arbitrés, intégrité reproductible, références immuables des sources ; aucune adoption par déduction |
| **Q10** | après Q01–Q09 et règles WIP | PR documentaire unique, puis gouvernance séparée | Réconcilier/retirer #143 de la voie maîtresse, préparer une PR depuis la branche existante quand autorisé ; V3.4 reste active jusqu'à promotion vérifiée |

## Les six exceptions et les dix obligations ne disparaissent pas

Scénarios source concernés : `T-V34-03-16`, `T-V34-06-22`, `T-V34-06-24`, `T-V34-06-25`, `T-V34-07-16`, `T-V34-07-25`. Les propriétaires futurs proposés ne doivent pas être présentés comme liens écrits dans la source V3.4.

G6 : `S-036/S-064/S-092/R33-028` → typographie/polices/glyphes et conversion (W10), `S-037` → trois usages métiers (W11). G9 : `S-021/S-047` → OCR contrôlé ; `S-044/S-066/S-099` → diorama quatre plans et assemblage (W16). Les titres sources et leurs critères prévalent sur ce résumé de navigation.

## Contrat de passage de témoin

À chaque fin de lot : préciser le point Q traité, la différence apportée, les références de sources inchangées/changées, les tests documentaires réellement exécutés et les tests produit proposés, le prochain point exact. Une difficulté de code futur se spécifie ; une preuve terrain manquante reste manquante. Réduire les relectures et les répétitions, sans supprimer de négatif ou de fonction.

**Prochaine action : Q01**, puis Q02 si aucun conflit de source ne l'empêche. Ne pas transformer cette file en nouvelle liste de dix tickets ou en permission de modifier AGENTS/les tâches/le produit depuis la tâche de conception.
