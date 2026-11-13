# COV-18A-2b — Confrontation des critères historiques intégraux, six UX (13/11/2026)

**NON NORMATIF — audit documentaire ciblé, aucune certification ni test produit.** Complète COV18A2A ; ne remplace pas les fiches A/B, ni les 24 lots V3.4. Sources lues à la source : `docs/ROADMAP_HERITAGE_v3_3.md` blob `c310adf3e972638c5a67332719bb2105ec37e688`, `docs/ROADMAP_TRACEABILITY_v3_3.md` blob `a56edf8b2791590464a600627fbd3efdf27b9d28`, `docs/ROADMAP_MASTER_v3_3.md` blob `93d23a9e1fd1af5d4636b4a28bdccfc55649c3c7`, lot 23 V3.4, COV18A1 et COV18A2A. Les lignes ci-dessous sont des **critères hérités textuels**, pas des tests réussis.

## Confrontation précise des six hypothèses

| UX | Exigence et critère V3.3 exact | Dépendances V3.3 | Ce que la V3.5 doit prouver ; conclusion |
|---|---|---|---|
| **A02** | **S-070** (G2.2, P0) : « T-02 : 12 sujets identifiables, même ID » ; lot 23 : V34-075/132, T-V34-22-04 | G2/F02-F14/P03 ; sélection croisée | Un test d'identité sur **12 sujets** entre vignettes et canevas, après changement de sélection, retour arrière et rechargement ; le simple pinceau sur un sujet ne couvre pas T-02. **NON QUALIFIÉ** |
| **A03** | **R33-006** : « Masques float32 comme autorité de retouche » (maître §11) ; lot 23 : V34-028/133, T-V34-22-04 | G2–G3/F03 ; projet V1/Subject | Union/intersection/soustraction sont une **extension candidate**, pas une conséquence de R33-006 ; garder source float32, dimensions et IDs inchangés jusqu'au commit CAS. **NON QUALIFIÉ** |
| **A04** | **S-007** (P0) : « rejet des faux sujets » ; source intégrale : dépend de **S-005 et S-006** ; lot 23 V34-069/110/007/071/082, T-V34-22-05 | vérité terrain annotée et validation modèle | Tester un distracteur plus saillant que la cible ; faux sujet rejeté, consentement IA distinct, repli manuel. Une confiance numérique non étalonnée ne satisfait pas ce critère. **NON QUALIFIÉ** |
| **A08** | **S-016** (P1) : « avant/après objectif » ; dépend de **S-006** ; lot 23 V34-089, T-V34-22-05 | masque de référence et diagnostic raster | Comparaison objective sur fixture identique (alpha, contour, couleurs), provenance CPU et indicateur d'interpolation ; ne pas revendiquer un détail inventé. **NON QUALIFIÉ** |
| **A12** | **S-032** (G5.5, P0) : « Aucun profil confondu » ; dépend de **S-011, S-030** ; lot 23 V34-098/129/112, T-V34-22-01 | topologie SVG et contrat Basic Cut | Quatre rôles distincts : PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche, SVG éditable. Matrice par rôle avec prévol unités mm, trous, calques et provenance. Une vectorisation couleur n'est pas une preuve de CUT. **NON QUALIFIÉ** |
| **B09** | **S-036** (G6.3, P1) : « Pas de substitution silencieuse » ; dépend de **S-035** ; lot 23 **aucun ticket V34 direct** ; **S-035** exige « Composition éditable après réouverture » | G6, licence/police/glyphes et schéma projet | Font absente ou glyphes manquants = avertissement et choix explicite ; aucune sauvegarde texte V1 présumée. Sans ADR/schéma validé, **brouillon seulement**. **BLOQUÉ G6/G9** |

## Écarts substantiels corrigés dans la lecture précédente

1. **A02** : le critère n'est pas simplement « clic/lasso/ellipse ». La preuve normative est la conservation du **même ID pour 12 sujets**, alors que les gestes supplémentaires restent une décision UX candidate.
2. **A04** : l'essai sans corpus S-005/S-006 ne peut pas démontrer « rejet des faux sujets » ; il faut un négatif ciblé et une vérité terrain autorisée.
3. **B09** : S-036 interdit explicitement la substitution silencieuse ; il ne suffit pas de vérifier que le texte reste visible. La dépendance S-035 impose une réouverture éditable qui ne peut être déclarée couverte par le canevas seul.
4. **A12** : les quatre formats ne sont pas interchangeables. Aucun succès Design Space ni coupe physique n'est inféré d'un export statique.

## Contrats et protocoles de tests candidats (NOT_RUN)

**TDD-1, identité A02/A03 :** fixture synthétique de 12 Subjects avec deux îlots et un trou, source SHA, révision et masques float32 ; choisir sujet 1 puis 12 par vignette et canevas, vérifier identité persistante, Undo et absence de mutation d'un autre masque. **Négatifs :** doublon subject_id ; masque dimensionnellement incompatible ; résultat asynchrone d'une ancienne révision. CAS refusé = aucun write.

**TDD-2, sémantique A04 et raster A08 :** image synthétique annotée avec faux sujet visuellement dominant, masque de référence, alpha semi-transparent ; comparer sorties CPU/manuel et IA consentie seulement si installée, avec mesures reproductibles sur le même corpus. **Négatifs :** modèle absent/téléchargement refusé ; OOM ; suraccentuation de halos malgré score de netteté favorable. Mesures p50/p95/RAM/VRAM à recueillir, jamais inventées.

**TDD-3, sorties A12 et typographie B09 :** exporter un document synthétique par chacun des quatre rôles, contrôler type, unités, calques, topologie, XML sûr, licences et SHA ; une police absente bloque toute substitution silencieuse, un glyphe manquant est signalé. **Négatifs :** SVG avec entités externes ; dimensions NaN ; fonte non redistribuable ; export simultané au changement de révision. Aucun code machine n'est émis ; profil KNOWN/UNKNOWN conservé.

**Transitions** : `source@revision → brouillon non mutant → preview → validation → commit CAS autorisé / rejet → reprise`. Crash, disque plein et annulation : pas de fichier partiel publié, ancien projet V1 relisible. Les ports exacts et DoD V34 de chaque ticket restent à inspecter **dans leurs fichiers de lot** ; les tests transversaux T-V34-22 ne les remplacent pas. Aucune API future n'est inventée.

**UX** : novice, sélectionner puis comparer visuellement et annuler ; expert, inspecter identité, SHA, unités et rapport. Clavier/focus, contraste, mouvement réduit, 1366×768 et DPI 200 % : **tests UI Windows à planifier**, non exécutés. Design Space, RTX et coupe physique sont hors test de cette passe, **NOT_RUN**, sans prétendre « non applicables » à la qualification finale.

## Contrôle explicite 25 axes R3

01–05 : univers historiques 24/141/140/80/437 conservés, six IDs ciblés seulement, aucun PASS ; 06 : preuves séparées ; 07 : CAS/float32/V1 ; 08 : quatre exports ; 09 : tri-state sans pilotage ; 10–12 : UX/clavier/DPI futurs ; 13 : annulation/concurrence/crash ; 14 : IA opt-in/CPU ; 15 : alpha/HD ; 16 : topologie et XML ; 17 : Fabrique/batch **non concernés par ces six interactions**, exigences intactes ; 18 : Smart Delivery **non concerné par ce sous-lot**, exigences intactes ; 19 : opportunités #141 **non arbitrées ici**, suivi distinct ; 20 : mesures futures ; 21 : corpus synthétique et licences ; 22 : docs branch only ; 23 : pas de second writer ; 24 : aucune adoption, revue, CI ou promotion ; 25 : critères V3.3 conservés sans compression. Les DoD exacts et recettes locales restent une lacune explicitement ouverte.

**État** : 6/30 A/B confrontés aux critères textuels V3.3 dans cette tranche, **0/30 certifiés** ; 431/437 liens source explicites et six exceptions, dix exigences G6/G9 sans ticket direct inchangés. Tests produits, Windows, GPU, Design Space, physique : **NOT_RUN**.

**Prochaine action unique : COV-18A-2c** — retrouver les six tickets sources et leurs DoD complets dans les lots V3.4 concernés, puis identifier leurs scénarios locaux exacts ; ne pas étendre aux 24 autres avant d'avoir noté les écarts par assertion.
