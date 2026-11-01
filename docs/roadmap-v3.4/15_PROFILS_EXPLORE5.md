# SmartSVG V3.4 — Cycle 15/24 : profils Cricut Explore 5, outils, matières et supports

**STATUT : DRAFT DE SPÉCIFICATION — NON IMPLÉMENTÉ, NON QUALIFIÉ.**
**Références :** roadmap V3.3 active (G4/F07/F13/F15, P01/P02/P04/P09, R33-022/023/034) ; [lot 14](14_LANGAGE_FABRICATION.md), [lot 04](04_MIGRATION_AUTONOME.md), [guide de livraison optimisée V3.3, déjà fusionné sur main](https://github.com/frenndak/SmartSVG-Studio/blob/main/docs/ROADMAP_EXECUTION_FASTPATH_v3_3.md). Date d'examen des sources : 29 octobre 2026.
**Directive prioritaire :** **aucune nouvelle fonction** ; préciser les profils matériels déjà prévus et éviter tout nouveau gate pour l'édition G3.3e-b2a. L'ensemble est un contrat d'adaptateur de fabrication futur, jamais un prérequis au pinceau/masques.

## 1. Contre-expertise du cycle 14 — clarifications sans extension

1. Les valeurs `KNOWN_SUPPORTED|KNOWN_UNSUPPORTED|UNKNOWN` du lot 14 décrivent une **capacité documentée d'une combinaison**, pas l'état d'un accessoire possédé ni une preuve que la machine a exécuté le projet. Un outil compatible mais absent du foyer reste `KNOWN_SUPPORTED` pour la machine et `USER_NOT_AVAILABLE` pour l'inventaire, sans convertir l'un en l'autre.
2. La capacité d'une famille de machines ne suffit pas à valider **machine + outil + opération + matière + support**. Distinguer `manufacturer_statement`, `local_observation`, `physical_proof` ; aucun `PASS` matériel par combinaison extrapolée.
3. La ligne « Foil + Pen + Score + Cut » n'est pas un unique outil magique. L'Explore 5 utilise une pince à outils pour lame, rainurage et foil ; la machine et Design Space guident le changement. Les stylos passent par le support dédié ; ne pas supposer l'exécution simultanée des opérations.
4. **Print Then Cut A4** n'est ni un rectangle complet ni la simple soustraction d'une marge uniforme. La zone dépend du format, de la machine et de la forme du projet. L'étape de vérification des dimensions dans Design Space reste externe.
5. L'identification du modèle « Explore 5 » ne permet pas de reprendre aveuglément les instructions des anciennes Explore pour les boutons de chargement ; l'interface de commande Explore 5 est distincte.
6. **Décision ADR-034-18 proposée :** une table descriptive versionnée, en lecture seule, résolue par la couche de prévol du lot 14 ; **pas de second moteur de géométrie, pas de nouvelle source de vérité et pas de base de données de matériaux indépendante**. Aucun ajout dans le schéma `.smartsvg` V1 sans migration approuvée.

## 2. Faits officiels vérifiés vs preuve de projet manquante

| Sujet | Information publiée par Cricut | Limite à afficher dans SmartSVG |
|---|---|---|
| Outils coupe Explore 5 | Premium Fine-Point Cutting Tool ; Deep Cutting Tool ; compatibilité de certaines anciennes lames/housings Fine-Point, Deep-Point, Bonded-Fabric | Les variantes et la disponibilité réelle sont à déclarer ; un matériau particulier n'est pas qualifié par la seule compatibilité d'une lame. |
| Rainurage | Scoring Tool compatible Explore 5 ; ligne passée à l'opération Score dans Design Space, puis **Attach** avec l'objet Cut | Ni les pointillés ni un trait SVG n'activent Score automatiquement ; conserver un guide. |
| Dessin | Support de stylo Explore 5 pour **stylos marqués compatibles** | Ne pas qualifier toutes les références de stylos par extrapolation. |
| Foil | Foil Transfer Tool des familles Explore/Maker, avec feuilles de transfert | Support, matière, adhésif, placement et compatibilité de la combinaison à contrôler. |
| Tapis ordinaires | LightGrip, StandardGrip, StrongGrip, FabricGrip, formats environ 12×12 et 12×24 pouces | Recommandations générales ; adhérence réelle, bonne lame et matière restent à éprouver. FabricGrip ne prouve pas l'utilisation de Rotary Blade sur Explore 5. |
| Tapis cartes | Formats 1×2 et 2×2 indiqués pour Explore 5 ; supports de cartes à tailles définies | Seules les tailles/procédures documentées sont candidates. Pas de placement arbitraire sur un tapis carte. |
| Smart Materials sans tapis | Guide Explore 5 : Smart Material Cricut 13 po (33 cm) de large, longueur minimale 6 po (15,24 cm) ; largeur découpable annoncée 12 po (30,48 cm) | Matériel tiers sans tapis non supposé compatible. Toujours vérifier le type de charge et la longueur prévue dans Design Space ; aucune pression/vitesse inventée. |
| Print Then Cut A4 | Limites variables selon format et proportion, zone non rectangulaire | N'exporter aucune « zone A4 parfaitement remplie et certifiée » sans import et recette réelle. |
| Gravure/débossage Maker-only | Non attribuer ces opérations à l'Explore 5 sans documentation contraire explicite | `KNOWN_UNSUPPORTED` pour les catégories Maker-only connues, aucune substitution en Cut/Score. |

**Provenance :** voir §9 ; les pages officielles peuvent évoluer. Le texte source fait foi à la date de consultation ; aucune capture ou essai physique fourni. Les accessoires réellement possédés par l'utilisateur ne sont **pas déduits** du matériel théoriquement compatible.

## 3. Autorités et modèle de profil minimal — SPÉCIFICATION, NON EXISTANT

**Réutiliser le contrat de capacités du lot 14**, avec index de règles versionné et deux axes distincts : capacité de combinaison et présence de matériel déclaré. Ne pas introduire d'unité métier `MaterialService` concurrente.

```json
{
  "schema": "smartsvg-machine-capability/1-draft",
  "profile_version": "explore5-official-review-2026-10-29-draft",
  "machine_id": "cricut-explore-5",
  "operation": "SCORE",
  "tool_id": "cricut-scoring-tool-explore5",
  "material_class": "cardstock",
  "support_id": "lightgrip-12x12",
  "capability": "UNKNOWN",
  "official_general_compatibility": "KNOWN_SUPPORTED",
  "availability": "NOT_DECLARED",
  "reason": "Outil compatible ; cette combinaison exacte matière/tapis non qualifiée",
  "evidence": [
    {
      "kind": "OFFICIAL_DOC",
      "url": "https://help.cricut.com/hc/en-us/articles/38613473602455-Cricut-Explore-5-How-to-use-the-Scoring-Tool",
      "checked_at": "2026-10-29"
    }
  ],
  "hardware_verified": false,
  "design_space_verified": false,
  "certified": false
}
```

**Règles de résolution (déterministes, non exécutées) :**
- Clé exacte : `(machine_id, machine_revision?, operation, tool_id, material_class, support_id, profile_version)`. Pas de collision silencieuse ni de fallback d'une génération de machine à une autre.
- `KNOWN_UNSUPPORTED` dès qu'une interdiction officielle documentée s'applique ; une disponibilité déclarée ne peut jamais l'annuler.
- `KNOWN_SUPPORTED` sur **combinaison complète** seulement si la source officielle couvre réellement tous les critères ; sinon `UNKNOWN`, même si machine et outil sont chacun compatibles.
- Une note `USER_DECLARED` n'élève jamais une information de fabricant manquante au rang de support officiel. Une preuve physique est un **axe indépendant** rattaché à la révision exacte des artefacts.
- Tout profil incomplet, périmé, non signé par une provenance lisible, ou ciblant un appareil différent retourne `UNKNOWN` + motif français. Une nouvelle version documentaire n'écrase pas automatiquement celle épinglée à un projet existant.
- Aucun `READY_TO_CUT` si la matrice est inconnue ; conserver **export brouillon** pour les opérations à vérifier, sans bloquer l'édition/sauvegarde du projet.

**Enveloppe de consultation future :** `resolveCapability(plan, profile_ref)` consomme le modèle du lot 14 et renvoie `CapabilityVerdict` existant + `availability`. Ne pas créer de commande persistante ni de nouvelle API réseau pour ce seul enrichissement. Les préférences peuvent rester locales et facultatives, hors `.smartsvg` V1 tant qu'aucune migration n'est qualifiée.

## 4. Parcours novice et expert, erreurs et retour arrière

**Express débutant :**
```text
[Projet : boîte · rainures + découpe]
Machine : Cricut Explore 5 (à confirmer)
Matière déclarée : carton léger
Tapis déclaré : [StandardGrip ▼]    Outil Score : [Je l'ai / Non / Je ne sais pas]
Opération : Score + Cut — étapes à faire dans Design Space
Profil : outil compatible / combinaison matière-support NON QUALIFIÉE
[Exporter un brouillon] [Voir guide « Score → Attacher → Vérifier les mm »]
```

**Expert :** tableau machine/opération/outil/matière/tapis, source et date de chaque verdict, cases de présence déclarée séparées, signalement de conflits et statut de preuve. Ne jamais afficher `CERTIFIÉ` sans preuve. Le clavier peut modifier les déclarations, jamais la provenance officielle. Les changements de profil invalident les prévols dépendants mais ne touchent pas aux masques, sujets ni projets sur disque sans commande dédiée.

**Cas négatifs à communiquer :** outil absent, tapis non déclaré, papier non reconnu, tôle ou épaisseur hors corpus, machine différente, ancien profil, coupe sans tapis sur vinyle non Smart, Smart Material trop court, tapis carte sans dimensions, produit Maker-only, dimensions A4 dépassées, reprise d'une prévisualisation après changement de profil. **Retour arrière :** effacer le profil déclaré et revenir à `UNKNOWN`/brouillon ; aucune migration/transaction ajoutée par le profil.

## 5. Deux exemples de plan de travail et parallélisme

**12 escargots → stickers Print Then Cut** : image et masques inchangés ; diagnostic des 12 sujets, validation des contours, planche A4 candidate ; `PRINT_THEN_CUT` comme intention composite, PNG comme sortie d'impression, contrôle de taille/import **dans** Design Space, aucune garantie par une table machine. Ce profil n'ajoute **aucun prérequis** au lot d'édition de masques G3.3e-b2a.

**Boîte → Score + Cut** : patron du lot 16 (futur), lignes de Score distinctes de Cut ; outil Scoring Tool documenté, matière et tapis déclarés sans qualification automatique, guide d'assignation Score + Attacher dans Design Space ; essai physique future avec matière/lame/outil/version. Une table `UNKNOWN` n'empêche pas de préparer un patron et une géométrie de test.

**Traitement parallèle sans faux gate :** tests de résolution des profils, contrôles d'import SVG/mm et maquettes de guides sont indépendants de l'IA et des retouches. Toute revendication de fabrication reste conditionnée aux preuves V3.3 G4 ; l'issue #71 n'a pas besoin de ce module.

## 6. Tests d'acceptation futurs — NON EXÉCUTÉS

Les assertions ci-dessous sont des **tests à implémenter**, et non des tests passés. Corpus : combinaisons synthétiques de règles/profils, documents publics cités, zéro média privé.

| ID | Assertion vérifiable | Axe |
|---|---|---|
| T-V34-15-01 | La clé complète distingue outil, matière, support et version ; aucune résolution partielle réussie | auto |
| T-V34-15-02 | Support officiel de l'outil sans preuve de combinaison complète reste UNKNOWN | auto |
| T-V34-15-03 | Machine différente n'hérite pas silencieusement du verdict Explore 5 | auto |
| T-V34-15-04 | Un outil Maker-only ne devient jamais SCORE/CUT accepté sur Explore 5 | auto |
| T-V34-15-05 | Un outil absent et une combinaison supportée restent deux statuts indépendants | auto/UI |
| T-V34-15-06 | Une déclaration utilisateur ne crée aucune fausse preuve fabricant ou physique | auto |
| T-V34-15-07 | Scoring Tool conduit au guide Design Space « Score + Attacher » | auto/UI |
| T-V34-15-08 | Support stylo vérifie le marquage de compatibilité, pas une correspondance par couleur | auto/UI |
| T-V34-15-09 | Foil garde la feuille, l'outil et la matière distincts de Cut | auto |
| T-V34-15-10 | Tapis carte inconnu : aucune simulation de placement réellement certifiée | auto/UI |
| T-V34-15-11 | Smart Material sans tapis : type/largeur/longueur minimale contrôlés ; vinyle tiers rejeté sans tapis | auto/UI |
| T-V34-15-12 | Changement de version du profil invalide le prévol précédent sans toucher au projet | auto |
| T-V34-15-13 | Une feuille A4 n'est pas traitée comme un rectangle entièrement découpable | auto/UI |
| T-V34-15-14 | Export brouillon permis avec UNKNOWN, sans étiquette machine-ready | auto |
| T-V34-15-15 | Machine réelle : l'utilisateur confirme le matériel présent, les étapes Score+Cut et le changement d'outil | Windows + Design Space |
| T-V34-15-16 | Essai carton : largeur/alignement du pli et coupe consignés, avec outil/matière/tapis/date | physique |
| T-V34-15-17 | Lecture d'une archive historique conserve les profils/masques inchangés | auto |
| T-V34-15-18 | Relecture de source officielle manquante : statut UNKNOWN, pas PASS « par défaut » | auto |

**Tests produit/CI, Windows, Design Space, RTX 3070, Cricut physique : NON_EXECUTE pour cette spécification.** Des tests existants du produit peuvent être verts ailleurs, mais aucun résultat n'est attribué à ces assertions.

## 7. Tickets de développement FUTURS — réutilisation plutôt qu'extension

Tous les tickets sont `SPECIFIE` **et doivent être réévalués pour duplication/fusion avant implémentation**. Les chemins ci-dessous n'existent pas nécessairement et ne sont pas des promesses de nouvelles applications.

| Ticket | Priorité + dépendances réelles | Livrable futur réutilisé, preuve, rollback |
|---|---|---|
| V34-116 | P1 · V34-107/106 ; R33-022 | Compléter `fabrication/capabilities.py` envisagé au lot 14 avec la clé de résolution complète et la provenance ; T01..04/18 ; rollback UNKNOWN. |
| V34-117 | P1 · V34-107/116 ; R33-022/023 | Table minimale **des outils Explore 5 documentés** lue par le résolveur existant, aucune base indépendante ; T02/04/07..09 ; rollback profils inutilisables→UNKNOWN. |
| V34-118 | P1 · V34-107/116 ; S-085 | Support/matière/tapis comme champs du même verdict ; T01/10/11 ; rollback recommandation désactivée. |
| V34-119 | P1 · V34-114/116 ; R33-014 | Contrôle facultatif du matériel déclaré dans l'écran de prévol existant, affichage de limite ; T05/06/14 ; rollback UI de brouillon sans profils. |
| V34-120 | P1 · V34-111/117 ; S-012 | Réutiliser le guide Score+Attacher du lot 14 avec les références machine vérifiées ; T07/15 ; rollback guide non qualifié. |
| V34-121 | P1 · V34-112/113/117 ; R33-022 | Cas Pen/Foil dans le même guide et résolveur, sans commande machine ; T08/09 ; rollback guide. |
| V34-122 | P1 · V34-110/118 ; S-029 | Conserver A4 comme zone Print Then Cut dépendante de Design Space ; T13/14 ; rollback avertissement de taille non qualifiée. |
| V34-123 | P1 · V34-109/116 ; R33-025 | Invalidation du prévol lors d'un changement de version de profil ; T12/17 ; rollback recalcul/UNKNOWN. |
| V34-124 | P1 · V34-111/117/118 ; R33-034 | Cas recette réelle Score+Cut (Design Space et physique) sans statut PASS tant que non réalisé ; T15/16 ; rollback preuves retirées, pas de projet modifié. |
| V34-125 | P1 · V34-107/114/118 ; R33-014 | Messages FR/accessibilité/explications `UNKNOWN` dans les panneaux existants ; T05/10/14/18 ; rollback affichage générique de prudence. |

**DoD commune :** un consommateur existant, un changement réel limité, tests ciblés et CI au SHA exact, preuve par axe distincte, compatibilité anciens projets et rollback explicite. **Anti-surconception :** si deux tickets de cette table concernent le même fichier/livraison, les regrouper dans une seule PR de parcours ; **ne pas ouvrir dix PR documentaires**.

## 8. Contre-expertise et passage au cycle 16

- **Fausse dépendance supprimée :** b2a pinceau réel / `.smartsvg` n'exige pas la matrice Cricut. G4 peut qualifier ses fichiers sur fixtures pendant G3.
- **Données non inventées :** aucune pression, vitesse, épaisseur maximale générale, coût machine ou qualité de pli chiffrée ; pas d'accessoires déclarés possédés sans confirmation.
- **Problème de versions repéré :** les guides Cricut évoluent ; réévaluer la version et l'accessibilité à l'implémentation. La date de modification peut différer entre éditions et index ; les références ci-dessous sont consultées le 29/10.
- **V3.3 et V3.4 :** aucun maître V3.3 modifié, aucun nouveau gate, aucune modification de code, pas de migration V1→V2. Les 141 exigences héritées restent référencées par HERITAGE_INDEX.md ; la traçabilité bidirectionnelle complète reste à achever au cycle 23/24.
- **Prochain lot 16 :** patron paramétrique boîte/carte déjà prévu ; géométrie de coupe vs plis, unités/épaisseur, guidage, validation de fabrication, **sans second moteur** ni simulation physique prétendue.

## 9. Sources consultées (29 octobre 2026)

1. Cricut Explore 5 — commandes et logements outils : https://help.cricut.com/hc/en-us/articles/38613203748503-Cricut-Explore-5-Button-functions-and-loading-basics
2. Cricut — lames et outils compatibles, édition observée du 03/04/2026 : https://help.cricut.com/hc/en-us/articles/360009432294-All-About-Cricut-Blades-and-Machine-Tools
3. Cricut Explore 5 — Scoring Tool et « Attach » : https://help.cricut.com/hc/en-us/articles/38613473602455-Cricut-Explore-5-How-to-use-the-Scoring-Tool
4. Cricut — tapis et recommandations de support (version consultée) : https://help.cricut.com/hc/en-us/articles/360009373414-Which-mats-can-I-use-with-my-Cricut-machine
5. Cricut Explore 5 — guide de démarrage et Smart Materials : https://help.cricut.com/hc/en-us/articles/36546544830615-Cricut-Explore-5-Quick-Start-Guide
6. Cricut — Print Then Cut : https://help.cricut.com/hc/en-us/articles/360009429814-How-large-can-I-Print-Then-Cut
7. Cricut — Smart Materials et dimensions minimales : https://help.cricut.com/hc/en-us/articles/1500007912041-All-About-Smart-Materials

Aucune source tierce, aucun réglage physique calculé ; URLs publiées comme repères vérifiables, pas comme validation du produit.
