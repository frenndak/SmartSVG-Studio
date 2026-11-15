# SOURCE_CLOSURE — tranche SC-01 : six exceptions et dix exigences G6/G9

**15/11/2026 — revue sémantique bornée, NON CERTIFIÉE globale.** V3.4 reste ACTIVE. Sources consultées : `docs/ROADMAP_HERITAGE_v3_3.md` blob `c310adf3e972638c5a67332719bb2105ec37e688`, lot 06 `074879c0729042a77e8addc60b8c9446c176c183`, inventaire 437 `edc6e2b03a37fab908f297dc7892b2020b98c701`, Q02 `21d73d0cac9e2bb0e38ca4155fb08b4bb21d139d`, Q04 résolution `09f2c83c4846ed8bba6ccbf5b54f076bd83ffe4e`. Ce rapport n'est PAS une relecture intégrale ligne par ligne des 141 critères/140 DoD/437 assertions.

## Verdict sur les six exceptions historiques

| Assertion | Responsable V3.5 candidat | Décision de revue | Condition non négociable |
|---|---|---|---|
| T-V34-03-16 | W04/W15 | RACCORDER sans inventer de ticket historique | Rapport de coupe physique avec mesures ; jamais PASS par prévol |
| T-V34-06-22 | W01/W12 | **CORRIGER Q02 par Q04** | Packs internes au **même projet V2 explicite**, limite V1 32, 50 identités uniques ; ni « simple partition export » ni migration automatique |
| T-V34-06-24 | W02/W04 | RACCORDER | Undo/Redo/reload conservent SCORE/DRAW/PRINT, jamais CUT par coercition |
| T-V34-06-25 | W15 | RACCORDER | Rapport expurgé, chemins privés/UNC et poids IA exclus |
| T-V34-07-16 | W02/W13 | RACCORDER | Undo de projet ne révoque pas coupe physique/export externe |
| T-V34-07-25 | W13 | RACCORDER | 100 transitions Windows, p95 <150 ms comme cible historique, matériel et traces nécessaires |

**Correction contractuelle importante :** Q02 évoque encore « packs V2 » comme formulation à arbitrer et une partition export possible ; Q04 §4 a déjà tranché la conception : packs V2 **internes au même projet**. La solution retenue ne permet toujours aucune écriture V2 avant procédure de migration, lecteur/writer/receipts et tests. Ne pas éditer Q02 historique : ce rapport porte la décision postérieure. Les six restent **sans lien TEST→TICKET explicite dans le document historique**, même après attribution d'un propriétaire candidat.

## Dix exigences sans ticket V34 direct : aucune suppression ni faux lien

| IDs intacts | Propriétaire | Oracle de recette indispensable | État |
|---|---|---|---|
| S-036, S-064, S-092, R33-028 | W10 typographie | Police/licence/glyphes identifiés ; texte rééditable après reload ; conversion en chemins sur copie export ; avertissement si police manquante | CONCEPTION_CANDIDATE |
| S-037 | W11 gabarits | Étiquette, topper, carte **distincts**, dimensions et round-trip, essais physiques par usage lorsque revendiqués | CONCEPTION_CANDIDATE |
| S-021, S-047 | W10/W14 OCR | OCR local facultatif, proposition corrigée avant commit, source raster préservée, STALE rejeté, repli manuel | CONCEPTION_CANDIDATE |
| S-044, S-066, S-099 | W16 diorama | Quatre plans alignables, ordre et guide d'assemblage, tolérances ; assemblage physique mesuré distinct de la simulation | CONCEPTION_CANDIDATE |

**Décision hostile :** « propriétaire W10/W11/W16 » ne vaut pas « DoD intégral satisfait ». Le texte éditable persisté dépend de la migration V2 explicitement autorisée ; un SVG de chemins n'est pas une scène texte rééditable. L'OCR ne doit pas inférer une police ni modifier le projet sans confirmation. Le guide HTML de livraison ne remplace pas le guide d'assemblage diorama. La preuve Design Space ne vaut pas preuve de coupe ni montage.

## Contrat de validation de cette tranche

Positifs **prévus, NOT_RUN** : P1 50 sujets/IDs uniques avec packs V2 internes et relecture, après autorisation de migration ; P2 typographie française accentuée round-trip ; P3 trois gabarits sauvegardés/réouverts ; P4 diorama quatre plans + guide, puis protocole physique séparé.

Négatifs **prévus, NOT_RUN** : N1 ancienne archive V1 et 50 sujets → refus sans migration implicite ; N2 Undo après export ou coupe → sortie externe inchangée et message exact ; N3 licence police/glyphe absent → avertissement, aucune substitution silencieuse ; N4 OCR tardif après changement de source SHA → STALE sans mutation ; N5 rapport diagnostics avec chemin UNC et métadonnées IA → expurgation ; N6 crash pendant publication V2 ou rotation backup → inspection receipt/CAS avant retry ; N7 deux writers concurrents → au plus un commit ; N8 mauvais alignement quatre plans → aucun PASS physique. Fixtures synthétiques uniquement, licences vérifiées.

Micro-lots **futurs**, aucun code écrit : (1) établir matrice clause historique exacte→propriétaire→DoD→assertion ; (2) fixtures V1/V2 et tests de refus/migration ; (3) texte/OCR et Undo ; (4) gabarits et diorama ; (5) UI Windows 1366×768/DPI 200 %, clavier/focus ; (6) protocole DS et coupon physique. CPU/manuellement possible pour texte/OCR ; GPU facultatif et consentement obligatoire ; aucune mesure de performance ni certification matérielle revendiquée.

## Audit 25 axes (portée SC-01)

01–05 : inventaires 24/141/140/80/437 conservés, non certifiés sémantiquement ; 06 : aucune preuve produit nouvelle ; 07 : V1/CAS préservé, V2 seulement explicite ; 08 : PNG PTC, SVG Basic Cut, SVG CUT multicouche, SVG édition séparés ; 09 : opérations et profils tri-state, coupe physique NOT_RUN ; 10–12 : parcours novice/expert, Undo, accessibilité à tester ; 13 : crash, stale, concurrence et rollback prévus ; 14 : OCR facultatif, consentement/licence/CPU ; 15 : raster source protégé, tests alpha/ICC hors tranche ; 16 : contours/mm/diorama, tests géométriques à définir ; 17 : gabarits et séries 50, CSV hors tranche ; 18 : Smart Delivery hors tranche, contrat préservé ; 19 : opportunités hors tranche, aucune rejetée ici ; 20 : p95 cible non mesurée ; 21 : licences et données privées ; 22 : aucune modification gouvernance/producteur ; 23 : aucun nouveau moteur/ticket ; 24 : pas de promotion ; 25 : correction explicite Q02→Q04, aucune réduction des exigences.

**Statut : SC-01 DOCUMENTÉ, SOURCE_CLOSURE toujours OUVERTE.** Prochaine action unique : **SC-02** — rapprochement par critères intégraux des 141 exigences et 140 DoD avec le registre V3.5, puis contrôle des 437 assertions par lot en ne rouvrant que les divergences réelles. Ne pas marquer SOURCE_CLOSURE DONE avant cette preuve.
