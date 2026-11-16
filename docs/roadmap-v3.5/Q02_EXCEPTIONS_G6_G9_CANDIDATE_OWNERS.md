# V35-Q02 — Exceptions de traçabilité et obligations G6/G9 : propriétaires candidats

**14 novembre 2026 — spécification candidate, non normative.** Sources : `COMPLETION_QUEUE.md`, `SCENARIOS_V34_02_08.md`, `COVERAGE_SCENARIOS_02_04.md`, `COVERAGE_V34_TO_V35.md`, lot 23 V3.4. Les références de propriétaire ci-dessous sont des **propositions V3.5**, et **ne sont pas** des liens TEST→TICKET écrits historiquement. Les critères complets V3.3 et DoD des tickets doivent encore être confrontés avant certification. Aucun PASS produit n'est déduit.

## A. Six scénarios historiquement sans rattachement explicite

| Assertion exacte source | Propriétaire candidat (non historique) | Contrat et critère de fermeture |
|---|---|---|
| `T-V34-03-16` : Une découpe réelle ne reçoit PASS physique qu'avec mesures/protocole | Gate de preuve terrain, lot 22 et contrat fabrication lot 14 | Rapport avec version DS, machine, matière, tapis, outil, dimensions attendues/mesurées, date, opérateur ; sans essai réel : UNKNOWN/NOT_RUN, jamais PASS |
| `T-V34-06-22` : 50 sujets partitionnés en packs V2 : aucun pack V1 >32, aucun doublon ID | Gestionnaire d'identités / partitionnement export, lot 06 ; revue du schéma V1 requise | Ne **pas** créer de projet .smartsvg V2 implicite : interpréter « packs V2 » comme exigence historique à arbitrer ; si elle nécessite migration V2, gate propriétaire préalable ; unicité globale des IDs et limite historique contextualisée |
| `T-V34-06-24` : Score/Draw/Print ne se transforment jamais en CUT lors de Undo/Redo | Command bus / opérations typées, lot 06 + langage fabrication lot 14 | Undo/Redo restaure opération et identité ; aucune coercition de SCORE/DRAW/PRINT vers CUT, y compris après reload |
| `T-V34-06-25` : rapport expurgé n'expose ni chemin privé ni média/poids IA | Export diagnostics et politique confidentialité, lots 06/21/22 | Rapport redacted by default, tests chemins Windows/UNC, métadonnées, noms de fichiers et fragments de modèle ; pas de médias binaires ni poids IA |
| `T-V34-07-16` : Undo groupé Score+Cut ne promet jamais annulation physique | UI Undo / command bus, lot 07 + lot 14 | Libellé « annuler les modifications du projet » ; export ou découpe externe déjà exécuté non révoqué ; état de machine jamais inféré |
| `T-V34-07-25` : navigation 100 fois p95 <150 ms mesuré avec matériel/protocole enregistré | Bench UI Windows et navigation, lot 07 + lot 21/22 | 100 transitions, protocole reproductible, distribution et p95, matériel/DPI/résolution, traces ; cible historique, **aucune mesure exécutée** |

**Décision :** RACCORDER aux responsabilités existantes, ne pas inventer six tickets ou modifier les micro-fiches V3.4. Le rapprochement ticket exact reste `À_ARBITRER` tant que le DoD original n'est pas confirmé. Le scénario `06-22` est un **conflit potentiel** entre la formulation historique « packs V2 » et la règle V1 unique : une migration V2 est explicitement interdite sans revue/autorisation.

## B. Dix exigences V3.3 sans ticket V34 direct

| Exigence | Famille de responsabilité V3.5 | Décision candidate / DoD spécifique |
|---|---|---|
| S-036 | G6 typographie | RACCORDER W10 : conversion police→chemins sans substitution silencieuse ; relecture SVG |
| S-064 | G6 typographie | RACCORDER W10 : licence, empreinte et rendu reproductible ou avertissement |
| S-092 | G6 typographie | RACCORDER W10 : sélection/aperçu police et glyphes accentués, fallback confirmé |
| R33-028 | G6 transversal | RACCORDER W10 : licences et glyphes manquants visibles avant export |
| S-037 | G6 gabarits | RACCORDER W11 : étiquette, topper, carte ; dimensions, sauvegarde/reprise et exports par rôle |
| S-021 | G9 OCR | REPORTER P2 sans supprimer W associé : reconnaissance proposée, texte source conservé |
| S-047 | G9 OCR | RACCORDER à S-021 sans fusion d'ID : correction humaine avant remplacement |
| S-044 | G9 diorama | REPORTER P2 : plans et assemblage, prototype physique distinct |
| S-066 | G9 diorama | RACCORDER W16 : quatre plans alignables, tolérances et essais matériels |
| S-099 | G9 diorama | RACCORDER W16 : guide d'assemblage UI/offline, ordre et mesures réelles |

**Aucune de ces décisions ne remplace les critères historiques complets** ; elles indiquent des responsabilités et non une couverture certifiée. Les trois familles (texte, OCR, diorama) peuvent réutiliser les modèles existants, sous réserve d'inventaire des API réelles. Un nouveau TextNode dans les strokes V1 ou une nouvelle opération machine n'est pas autorisé par cette fiche.

## C. Contrats de conception et UX

- **Source de vérité :** projet `.smartsvg` V1 avec SHA/CAS, sujets et masques float32 inchangés. Propositions OCR et preview typographique restent transitoires avant confirmation ; modifications locales via commande Undo/Redo. Une sortie externe publiée ne peut être annulée par Undo.
- **Quatre exports indépendants :** PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche, SVG éditable ; un texte converti en chemin n'est pas un texte éditable, et les opérations CUT/SCORE/DRAW/PRINT/FOIL ne se déduisent pas d'une couleur SVG.
- **Parcours novice :** ouvrir gabarit/texte → aperçu du rendu, de la police et des dimensions → corriger manuellement → confirmer seulement la substitution risquée → enregistrer → exporter. Expert : provenance, licences, géométrie, unités mm, diagnostics et source des capacités tri-state.
- **Accessibilité :** conception à tester à 1366×768 et DPI 200 %, navigation clavier/focus, contraste et motion réduit ; erreur de police/outil inconnus lisible sans code couleur. Aucun benchmark réalisé.
- **IA :** OCR local facultatif avec modèle/version/licence/hash/consentement, fallback saisie manuelle ; aucune connexion ou téléchargement implicite. Pas de promesse de résultat OCR sur CPU/GPU sans mesure.

## D. Plan de tests proposés (tous NOT_RUN)

Positifs : texte accentué converti en chemins et SVG relu ; gabarits trois types save/reopen ; diorama quatre plans alignés dans une fixture synthétique ; Undo groupé conserve CUT/SCORE ; diagnostic expurgé ; 100 transitions Windows instrumentées.

Négatifs obligatoires : (N1) police manquante ou licence non partageable → avertissement/blocage proportionné, jamais substitution silencieuse ; (N2) OCR ambigu → aucune mutation sans validation ; (N3) plan diorama désaligné / matière inconnue → aucun PASS physique ; (N4) Undo après export externe → ne prétend pas effacer la sortie ; (N5) collision d'identités dans partition de 50 sujets → refus sans écrasement ; (N6) fuite UNC, chemin privé ou métadonnées IA → rapport refusé/expurgé ; (N7) crash après preview mais avant commit → état V1 intact ; (N8) résultat asynchrone obsolète → rejet STALE ; (N9) deux éditions concurrentes → CAS refuse le second commit et permet reprise.

Micro-lots TDD futurs : (1) assertions de provenance/identités et gardes CAS ; (2) typographie et OCR en preview non mutante ; (3) gabarits/diorama topologie et dimensions ; (4) UX/Undo/recovery ; (5) diagnostics expurgés et bench Windows ; (6) essais Design Space puis découpe/assemblage physique **séparés**. Réutilisation de ports à confirmer au HEAD, pas de création de code dans cette mission.

## E. Revue hostile et 25 contrôles

**Risque principal :** le rapprochement « même domaine » serait une fausse preuve de couverture. Chaque exception conserve son ID et son état À_ARBITRER jusqu'à la vérification des DoD et critères intégraux. Les 437 scénarios restent inventoriés, 431 liens explicites historiquement, six exceptions **non résolues comme liens historiques** ; les dix exigences restent sans ticket V34 direct. Le choix W10/W11/W16 est un candidat de conception, pas une promotion.

Axes 01–05 : inventaires conservés, qualification sémantique ouverte. 06 : statuts disjoints. 07–09 : V1, quatre exports, opérations et UNKNOWN préservés. 10–13 : UX, Undo, accessibilité et crash spécifiés, tests non exécutés. 14 : OCR facultatif ; 15–16 : raster/vectoriel inchangés, non applicable aux seules correspondances documentaires ; 17 : gabarits/diaporama concernés, batch non applicable à cette fiche sauf partition de 50 ; 18–19 : Smart Delivery et autres propositions inchangés, hors périmètre ; 20 : p95 cible à mesurer ; 21 : confidentialité et licences explicites ; 22–24 : aucun code/gouvernance/merge, ports et promotion non certifiés ; 25 : delta concret sur 16 exceptions, aucun total artificiellement fermé.

**Prochaine action unique : Q03** — ADR responsabilités objets/calques/texte/transformations vs schéma V1, projection externe et migration explicite, après lecture des signatures HEAD et des DoD exacts.
