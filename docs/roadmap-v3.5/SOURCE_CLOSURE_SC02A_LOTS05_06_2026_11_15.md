# SOURCE_CLOSURE SC-02A — rapprochement sémantique lots 05–06 (15/11/2026)

**Statut : REVUE DOCUMENTAIRE PARTIELLE ; SOURCE_CLOSURE OUVERTE.** Sources V3.4 relues directement sur main : lot 05 blob `598a0ba0ec17d2e6035ff8875d3a5ba49a2f702c`, lot 06 blob `074879c0729042a77e8addc60b8c9446c176c183`. Inventaire SCENARIOS_V34_INDEX blob `edc6e2b03a37fab908f297dc7892b2020b98c701`, SC-01 blob `d5b3a3a61fccc9a0c5ffee731fd864768ccb564a`. Les 50 assertions (20+30) sont inventoriées ; cette revue se concentre sur les contrats transversaux risquant de perdre des critères, et **ne certifie pas** les 50 assertions une par une ni les 141/140/437 globalement.

## Rapprochements vérifiés, décisions et risques

| Source, ticket, assertions | Exigence historique intégrale à conserver | Décision V3.5 et contre-exemple interdit | Oracle futur |
|---|---|---|---|
| Lot 05 V34-025/026/027 ; T-V34-05-01..12 | V1 strict, source octet-identique, masques float32, migration V2 sur copie seulement, quotas et ZIP hostile | **GARDER** writer V1 existant ; V2 uniquement explicite. Une validation de schéma ne vaut pas preuve de migration | Hash original avant/après, lecture V2, crash à chaque phase, ancien lecteur refusant V2 |
| Lot 05 V34-028 ; T-V34-05-03/04/16/17 ; lot 06 T-V34-06-21/22 | IDs/lineage stables ; 50 sujets répartis en packs **internes au même projet V2**, jamais 50 masques injectés dans V1 limité à 32 | **CORRIGER l'ambiguïté Q02** via Q04/SC-01 ; une partition d'exports en plusieurs projets ne satisfait pas l'assertion | 50 IDs uniques, packs internes, réouverture, provenance et intégrité float32 ; migration autorisée avant tout essai |
| Lot 05 V34-029 ; T-V34-05-13/14 ; lot 06 V34-033/034/040 ; T-V34-06-01..12/28 | CAS archive V1 distinct de révision V2, receipt durable transactionnel, epoch et retry idempotent | **GARDER/RAFFINER** : perte d'ACK et panne backup ne signifient pas absence de commit ; ne jamais répéter une commande incertaine | Crash après publication primaire, état COMMITTED_NEEDS_RECOVERY/UNKNOWN_AFTER_INTERRUPTION, deux writers et même command_id |
| Lot 06 V34-035/038 ; T-V34-06-13..16/24 ; lot 05 T-V34-05-04 | Undo groupé et patch bit-identique float32 ; CUT/SCORE/DRAW/PRINT préservés ; aucun Undo externe | **GARDER** : l'inverse d'un masque L8 n'est pas un inverse float32 ; un Undo n'efface ni export ni coupe | Comparaison bit-à-bit, groupe CUT+SCORE, reload, Undo/Redo, sortie externe inchangée |
| Lot 06 V34-036/039 ; T-V34-06-17..21/27/29/30 | Jobs IA CPU/GPU sans writer, propositions et succès partiels non mutantes, acceptation CAS atomique | **RACCORDER** au consentement et à la reprise ; OOM et résultats STALE ne doivent jamais modifier la source | 48/50 propositions, 0 commit avant acceptation, retry ciblé, OOM, crash sans relance silencieuse |
| Lot 06 V34-037/040 ; T-V34-06-23/25/26 | Resync des vues, rapports expurgés, preuves Windows distinctes | **AMÉLIORER** l'observabilité ; événement perdu n'est pas une deuxième mutation, diagnostic privé interdit | Deux vues, événement perdu, reconstruction au SHA, UNC/EXIF/poids exclus |

## Contradictions et limites ouvertes

1. **Le terme « packs V2 » doit désigner une structure interne au même projet**, et non un ZIP Smart Delivery ou des projets .smartsvg multiples. Un seul projet V1 reste l'autorité actuelle ; V2 est une proposition gated.
2. **CAS du ZIP ≠ receipt transactionnel.** Un SHA archive inchangé peut démontrer une non-mutation ; il ne prouve pas à lui seul exactly-once après perte d'ACK.
3. **La formulation « 50 sujets » ne lève aucun quota V1.** Les limites V2 (ZIP, RAM, décompression, receipts) exigent benchmark et décision de gouvernance.
4. **Les tests T-V34-05-18/19 et T-V34-06-24 ont des consommateurs fabrication** : préserver les quatre sorties PNG PTC, SVG Basic Cut, SVG CUT multicouche, SVG édition et les opérations typées. Un prévol UNKNOWN ne devient jamais PASS Design Space/physique.
5. Le rapprochement aux **critères intégraux des 141 exigences et DoD de tous les 140 tickets reste ouvert**. Cette fiche n'établit pas que les 50 assertions ont chacune une chaîne source→DoD→oracle complète.

## Plan de validation, non exécuté

Positifs : P1 projet V1 round-trip sans mutation et float32 bit-identique ; P2 V2 explicite sur copie et 50 sujets en packs internes ; P3 Undo/Redo groupé CUT+SCORE ; P4 deux vues resynchronisées après perte d'événement.

Négatifs : N1 ZIP traversal/double JSON key → refus avant écriture ; N2 deux writers avec expected SHA identique → un seul commit ; N3 crash après publication avant ACK/backup → inspecter receipt, **aucun retry aveugle** ; N4 résultat IA STALE ou OOM → zéro mutation ; N5 50 masques dans V1 → refus sans conversion ; N6 Undo après export externe → fichier externe conservé ; N7 rapport UNC/média IA → expurgation ; N8 licence/consentement modèle absent → aucun téléchargement. Fixtures synthétiques uniquement.

TDD futur : (1) oracle archive V1 et quotas ; (2) schéma/lecture V2 sur copie après autorisation ; (3) CAS/receipts/crash ; (4) commandes/Undo et opérations typées ; (5) jobs et resync UI ; (6) qualification Windows puis Design Space/physique séparée. Les fichiers futurs mentionnés dans les lots 05–06 ne sont **pas attestés comme existants**. Aucun code créé ici.

## Contrat 25 axes — portée de SC-02A

01–05 : inventaires 24/141/140/80/437 conservés, aucune certification globale ; 06 : aucun nouveau test ; 07 : V1/SHA/CAS/float32 et migration V2 explicite ; 08–09 : quatre exports et opérations tri-state séparés ; 10–12 : UX novice/expert, Undo, focus, DPI 200 % à qualifier Windows ; 13 : crash/stale/concurrence couverts en conception ; 14 : IA facultative et consentement, CPU/manuel ; 15 : source raster et alpha conservés, pipeline colorimétrique hors tranche ; 16 : géométrie mm hors tranche, aucune inférence de coupe ; 17 : batch 50 et IDs traités, bibliothèque/CSV hors tranche ; 18–19 : Smart Delivery et opportunités hors tranche, contrats non altérés ; 20 : performances non mesurées ; 21 : données privées et licences ; 22 : aucun changement gouvernance/producteur ; 23 : pas de nouveau moteur ni ticket ; 24 : promotion interdite ; 25 : correction de l'ambiguïté packs et preuve bornée, sans raccourci d'audit.

**Suite unique SC-02B :** confronter les critères et DoD intégraux des lots 07–10 aux assertions de ces lots, consigner uniquement contradictions ou pertes vérifiées. Continuer ensuite les autres lots avant de clore SOURCE_CLOSURE. Aucun PASS Windows/GPU/DS/physique revendiqué.
