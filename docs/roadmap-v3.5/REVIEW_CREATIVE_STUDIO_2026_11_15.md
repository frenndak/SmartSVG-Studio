# Revue indépendante — studio créatif et réglages rééditables

15 novembre 2026 — reviewer `review_creative_studio`, sans sous-agent. **Verdict : conception et raccordement recevables pour planifier et publier le delta documentaire ; aucun Critical/Important identifié. Une précision Minor à intégrer au cadrage CP0-CST, sans bloquer la clôture documentaire.** Aucun test produit, GitHub APPROVED, G35-12 PASS, fusion ou adoption V3.5 n'est déduit de ce verdict.

## Portée, base et méthode

Base candidate communiquée : `1fde26bbf3217b3b3a7cf75f8d33c98a3a8439b9` ; main communiqué et revalidé par le coordinateur : `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`. Copies locales `canonical-v35` et `history-work`, sans métadonnées Git utilisables. Aucun appel distant de ce reviewer ; correspondance aux blobs publiés et HEAD final à vérifier par le coordinateur.

Lecture intégrale du nouveau contrat, des huit raccords MASTER/BACKLOG/PRIORITY_INDEX/ADR/QUALITY/README/PROMOTION_CHECKLIST/RUN et de la dernière entrée CST de PROGRESS. Comparaison des huit raccords aux copies de référence fournies par le coordinateur au SHA de base : ajouts CST et précision « première signature de livraison » seulement ; aucun changement des tables UX, des anciennes tranches CP ou des statuts et dépendances RUN. Lecture complémentaire de D01–D09 et du contrat des25axes ; lecture des recettes et limites SCN§§9–10. Cette revue ne revendique ni une nouvelle lecture du code produit ni une vérification personnelle distante des ports de main.

Les rapports [GLOBAL_REVIEW](GLOBAL_REVIEW_2026_11_15.md), [sa résolution](GLOBAL_REVIEW_RESOLUTION_2026_11_15.md) et [REVIEW_SCENE_DECOMPOSITION](REVIEW_SCENE_DECOMPOSITION_2026_11_15.md) ont été lus et leurs empreintes recalculées. Leurs revues historiques sont réemployées dans leurs portées et SHAs propres : aucune nouvelle comparaison individuelle des141critères,140DoD ou437assertions inchangés. Le présent rapport examine le nouveau contrat et ses raccords, sans étendre rétroactivement leurs verdicts.

## Constats et buildercheck

**Critical : aucun. Important : aucun.** Aucun choix produit matériel manquant n'empêche un builder de planifier CST0–4. L'identité du studio, les cinq parcours, le premier opérateur offset, la persistance V2 et les frontières d'assistance sont décidés. Schémas exacts, quotas, formats d'erreur, trois fixtures géométriques, tolérances, signatures/adaptateurs et runner réel sont explicitement des livrables CP0-CST/CST0 avant implémentation ; leur absence actuelle n'exige pas le code de ces futures tranches pour accepter ce delta.

| ID / sévérité | Localisation du premier état lu | Effet / précision minimale attendue |
|---|---|---|
| CST-M01 — Minor, confiance élevée | `CREATIVE_STUDIO_PRODUCT_CONTRACT.md:55`, `:59`, `:67`, `:69` ; `ADR_COMPOSITION_PERSISTENCE.md:34` | Les références géométriques stables, leur validation et l'interdiction de perte silencieuse donnent déjà une issue fermée. CP0-CST devrait rendre explicite le cas d'une entrée LIVE dont le trou/îlot protégé n'est plus identifiable : refuser l'application ou marquer NEEDS_REVIEW et demander une nouvelle sélection ; aucune réaffectation par index ou voisin supposé. La mutation directe d'une recette doit aussi appliquer locked hérité du nœud cible et annoncer les objets bloquants ; ne pas contourner ce verrou en ne modifiant que la projection. Ajouter ces deux négatifs au cadrage des recettes CST-03/06/07. C'est une précision de ces règles, pas un nouveau mécanisme ni une raison d'imposer le code maintenant. |

L'absence de formulation plus détaillée n'est pas un Important : §59 refuse les références absentes, §67 interdit de supprimer silencieusement un détail protégé, §9 réemploie les contrats existants et l'ADR conserve ses verrous. Le builder peut planifier le refus borné avant tout algorithme de correspondance. Aucun remapping automatique ou contournement de locked n'est autorisé par ce rapport. L'état final de ce constat figure dans le complément de résolution ci-dessous.

| Contradiction recherchée | Conclusion bornée |
|---|---|
| Base / recette / persistance | §4 et ADR§9 : géométrie et transformation au nœud ; recette ressource V2 versionnée, CP0-CST avant écriture, CP0–3 pour save/reopen rééditable. Preview/export externe V1 possible, jamais preuve de persistance ; aucun JSON maître annexe ni second writer. |
| Ordre physique et placement | §4.2, ADR§103 et CST-02 : transformation monde du motif, puis offset en mm confirmés, puis placement rigide. Rayon10mm×2+offset1mm =21mm ; offset2mm =22mm. Translation/rotation/nesting rigides ne multiplient pas la marge. D03 exige le footprint après offset. |
| Graphe et erreurs | §4.1 : base avant recette, aucune auto-sortie comme entrée ; DAG inter-objets explicite et borné. Cycle, dépendance non prise en charge, opération/version inconnue, ressource absente et NaN/Inf refusés, sans aplatissage caché. |
| LIVE / FROZEN et ressources | §4.1–4.3 : LIVE invalide et recalcul borné ; FROZEN épingle révision/ressources et mise à jour avec diff/Undo. Cache reconstruisible distinct des recettes et ressources durables, purge sans perte de réglages ni Undo promis. |
| Versions absentes au reopen | §4.2 et CST-08 : paramètres conservés, rendu à revoir, pas de substitution invisible du moteur ni export sur ancien QA. Un cache identifié n'est pas une preuve de reproduction. |
| Trous et topologie voulue | §4/CST-03 et D01 distinguent protection, perte silencieuse et changement voulu annoncé avec déverrouillage explicite/nouveau prévol ; pas d'interdiction universelle des booléens. Précision CST-M01 ci-dessus. |
| Génération affichée / acceptée | §35–37 et CST-05 : dernière génération applicable, acceptation liée au digest du rendu montré, source/session périmées refusées ; pas d'acceptation implicite d'un rendu absent. |
| Quatre sorties / cinq intentions | §5 et CST-09 : PNG PTC, Basic Cut, CUT multicouche et SVG d'édition restent quatre rôles. Collage/relief réemploie SCN et les sorties appropriées ; ni cinquième format ni quatrième Artifact.use V1. |
| CAS / receipt / Undo externe | §4.3/CST-11 et ADR§3 : CAS V1 distinct du receipt CP2 ; perte ACK, primaire publié/backup échoué et UNKNOWN réconciliés avant retry. Undo ne révoque pas un fichier livré. |
| IA, réseau et qualification | §6/CST-12/14 : manuel local, admission fiable/licence/version/hash, consentements distincts, budgets/OOM/annulation ; pas de modèle ni téléchargement implicitement admis, pas d'autorité d'écriture donnée à l'IA. Aucun gain concurrentiel chiffré ni résultat mesuré inventé. |
| Priorités / UI / livraison | CST§7, MASTER/BACKLOG/index : priorités sources P0/P1, texte et gabarits G6 conservés ; Smart Delivery mono-export première tranche P1 indépendante, studio cœur du concept. D08 benchmark Tk/Qt/Tauri avant gros éditeur reste obligatoire ; moteurs sans UI peuvent avancer. |
| Compteurs et curseur | 14 IDs de table T-V35-CST uniques recomptés ; tous NOT_RUN, distincts des17SCN et437historiques. CST0–4 ne crée ni cinq moteurs ni cinq tickets. RUN conserve GLOBAL_REVIEW DONE → PROMOTION_DOCS READY → GOVERNANCE_HANDOFF PENDING, autorité3.4 et promotion_ready=false. |

## Examen des25axes sur le delta

`Recevable conception` signifie obligation et plan préservés dans ce delta ; aucun PASS produit. La profondeur des inventaires historiques repose sur les rapports réemployés, pas sur un nouvel audit universel.

| Axe | Examen et limite |
|---:|---|
| 01 —24lots | §2/7/9 : responsabilités existantes traversées, aucune unité source supprimée ; héritage réemployé. |
| 02 —141critères | §2/7/9 : conservation explicite, aucun raccourci de critère ; pas141revérifications individuelles ici. |
| 03 —140tickets | CST incréments de réalisation, pas tickets de remplacement ; tables historiques inchangées au diff des raccords. |
| 04 —80UX | Sélection, objets, contour, couleur, texte et composition approfondis ; aucun81eID ni nouveau rang prioritaire. |
| 05 —437scénarios | CST-01..14 proposés séparément des17SCN et437historiques ;14IDs uniques recomptés, NOT_RUN. |
| 06 —maturité/preuves | Bandeau et §8 : conception future, ports à inventorier, code non activé, produit non qualifié. |
| 07 —projet unique | CP0-CST/CP0–3, source/base, ressources transactionnelles et writer actif unique ; cache non autoritaire. |
| 08 —quatre exports | §5/CST-09 : quatre rôles et QA distinctes, PNG non vecteur, aucun nouvel usage V1 clandestin. |
| 09 —opérations/machine | CUT/PRINT/etc distincts du rôle et de la couleur ; mm confirmés et profil UNKNOWN, pas certification géométrique. |
| 10 —Express-first | §3 : intention, geste, diagnostic localisé et reprise ; mêmes objets novice/expert, métriques futures. |
| 11 —canevas/gestes | Session/canevas communs, vues SCN, barre contextuelle, drag/paramètre/acceptation = groupe Undo ; aucun second dessin maître. |
| 12 —accessibilité | Clavier/liste/focus/lecteur/contraste/motion,1366×768 etDPI200% ; héritage D08 conservé, vraie UI NOT_RUN. |
| 13 —annulation/reprise | §3/4 et CST-05/11 : STALE, session, crash, CAS, disque plein, annulation et fichiers déjà livrés traités. |
| 14 —IA facultative | §6 : manuel/CPU, admission/licence/provenance/consentements et OOM ; aucun modèle réel essayé. |
| 15 —raster | Intention sticker garde alpha/bleed/ppi et photo non vectorisée inutilement ; héritage raster non remplacé par la nouvelle recette. |
| 16 —vecteur | Offset physique/simplification, topologie/trous protégés, DAG et budgets, versions ; CST-M01 borne l'échec de correspondance. |
| 17 —Fabrique/séries | W12/SCN et recettes existantes, quantités/identités/verrous/reprise par unité ; texte/gabarits restent obligatoires. |
| 18 —Smart Delivery | Consommateur après export sain ; rôle P1 indépendant, aucun writer/queue/exporteur concurrent. |
| 19 —autres évolutions | Aucun rejet ni opportunité réécrit ; reconstruction/warp avancés distincts du premier offset. |
| 20 —métriques | Quatre parcours même source/taille/objectif/environnement ; temps total incluant échecs, p50/p90/p95/max et mémoire ; zéro gain observé revendiqué. |
| 21 —sécurité publique | Liste fermée/versionnée, aucun script/expression/URL d'installation, ressources/licences et copie expurgée ; pas d'audit runtime universel. |
| 22 —gouvernance/WIP | Delta docs seul ; V3.4 active, G35-12..14 PENDING, WIP et protections à revalider avant PR. Aucun distant/tâche modifié ici. |
| 23 —anti-doublons | Réemploi W02/W03/W07/W12/W13/CP/SCN/SD ; aucun nouveau moteur général, bus, queue, writer ou store maître. |
| 24 —revue/adoption | Présente revue de delta et contrôles ci-dessous ; anciens rapports bornés à leur SHA, aucune GitHub APPROVED ni adoption. |
| 25 —optimisation | Lecture du delta et raccords avec réemploi d'empreintes ; aucun axe supprimé ni réussite future exigée pour accepter la conception. |

## Empreintes du contenu relu

SHA256 locaux sous `docs/roadmap-v3.5`, au premier état lu ; le complément final identifie le seul contrat précisé ensuite. PROGRESS est une photographie avant l'éventuelle note de clôture autorisée ; ce rapport n'en change pas le contenu.

| Fichier | SHA256 |
|---|---|
| `CREATIVE_STUDIO_PRODUCT_CONTRACT.md` | `84cc9dbd597ce3da88545da27df64396e495cd8cb7470f58cedf32e885ae72a4` |
| `MASTER_PRIORISE.md` | `3b31f2b66f555f84c97f1d9b2df6bf8869d230023576c7ff73eb3166bfe06e08` |
| `BACKLOG_AND_DEPENDENCIES.md` | `a300382d6d904d5afc6faa54fb252c2352821e1a793232687ae8baa839f207a1` |
| `PRIORITY_INDEX.md` | `951caa33e0d55d08a770a3c7a3a8394b0225a062bd8a0361b71846501fe7097f` |
| `ADR_COMPOSITION_PERSISTENCE.md` | `ec5d721345693403870c587315a3b4e48997e89e1a2ac98f980eeefb48568e3e` |
| `QUALITY_TESTS_AND_EVIDENCE.md` | `aa7c7965d1be2359325e215cf73b52d10b9e3c52407b3ba13d9adcb944a11303` |
| `README.md` | `14c650fe5ec2df1c21129119fe0615adbf77355ea893430e3591e1e6f5b392e7` |
| `PROMOTION_CHECKLIST.md` | `05898e44000cc13ed60ec9b31ba58d7ac12e0e1fc41e96ef4e54fa00816029a4` |
| `RUN_STATE.json` | `1eb9f5eb68ef4f8e6a0f35158d21d74dc82bb3ce85ef4fda45e38cbaf8943991` |
| `PROGRESS.md` | `3fe96fd66b53b2b7aa1d87b0f695c331e0aa7173a7d7af32622a49abf1bc1336` |
| `GLOBAL_REVIEW_2026_11_15.md` | `c2bea5cbe8f58ff6867d9d78744ec9bd3dfd25ef0a405da70bebfae9bf6e617d` |
| `GLOBAL_REVIEW_RESOLUTION_2026_11_15.md` | `d17ecc0a5899741471243a179c6533119c2bc0c49f61387cb4faf527ba0b9434` |
| `REVIEW_SCENE_DECOMPOSITION_2026_11_15.md` | `1b828cd08868f921214e35cd3bb8a9bf7073cd512ce4217866c64960c27e247c` |
| `DECISIONS_TRANSVERSALES.md` | `7821a634715b1601d62f3c20fc14d01b327918b4ed2eeedf2dbc0696620645be` |
| `AUTOMATION_QUALITY_CONTRACT.md` | `1ca11790c721e85ce25dc4eeb101768c59645a0a4c6e738b6ac134c7d7ca3d5a` |
| `SCENE_DECOMPOSITION_AND_RELIEF_CONTRACT.md` | `69ba06117a0d15b7ef3da119dfe78206f1ecfc626260106b19105b62d470496d` |

## Contrôles documentaires et limites

Le rapport existe avant l'exécution de verify_run_state, pour ne pas produire une preuve manquante artificielle dans RUN/README. Résultats réels des trois contrôleurs et des liens locaux à consigner dans le complément ci-dessous ; aucun PASS n'est anticipé.

**Limites :** aucune recette produit CST/SCN exécutée ; aucun test studio, Windows/NTFS/UI/accessibilité réelle, CPU/GPU/modèle, Design Space, impression, coupe/montage ou benchmark exécuté. Les futures licences et modèles restent à qualifier à leur révision réelle. Aucun code, contrat, registre, curseur, état, archive, workflow, automation ou distant modifié par ce reviewer ; seul ce nouveau rapport est écrit. La publication et le contrôle des blobs finaux restent à faire par le coordinateur, puis PROMOTION_DOCS suit ses conditions WIP/CI/revue. V3.4 active.


## Complément final — résolution CST-M01 et contrôles réels

**Verdict final : delta documentaire et raccordement recevables et publiables ; zéro Critical/Important et zéro Minor ouvert.** Le constat CST-M01 ci-dessus décrit le premier état, conservé comme photographie. Le coordinateur a ensuite ajouté deux paragraphes au seul contrat et complété CST-06/10, sans nouveau test ID. Relecture directe de §4.1–4.3 et des recettes concernées ; nouveau SHA256 local du contrat confirmé : **`62cc323a7e0b5e295fbabbbed56e9daf14f0f14fac9e5f83b2da6a48768a7dbf`**. Cette empreinte remplace uniquement celle du contrat pour le verdict final ; les autres empreintes du tableau sont inchangées.

| Résolution vérifiée | Localisation courante / effet |
|---|---|
| Correspondance des protections | Contrat:61 et CST-06:124 : après changement LIVE, correspondance non démontrable du trou/îlot protégé = NEEDS_REVIEW ; dérivé non publiable comme courant, protection conservée et nouvelle désignation explicite. Index/proximité ne réaffectent pas l'identité et ancien QA non recyclé. Les ressources/ancien résultat servent seulement à comparer. |
| Verrouillage des recettes | Contrat:63 et CST-10:128 : locked propre/hérité de l'ADR s'applique au changement/application de recette ; groupe refusé sans descendant modifié ni sous-ensemble silencieux. Preview non mutante et choix explicite de cibles autorisées possibles ; calcul ne déverrouille jamais. |

Ces précisions ferment le Minor sans élargir l'architecture, modifier les priorités ou exiger le futur code. **Aucun choix produit important supplémentaire manquant pour le builder n'est identifié.** CP0-CST/CST0 restent chargés des schémas/quotas/fixtures/runner exacts avant implémentation. Les 14 IDs de recettes restent uniques et proposés NOT_RUN.

Les contrôles suivants ont été réellement exécutés par ce reviewer après création du présent rapport, sur le contrat corrigé et les raccords figés :

| Contrôle | Résultat réel |
|---|---|
| `python canonical-v35/docs/roadmap-v3.5/verify_source_transfer.py --main-root history-work` | exit0 ; PASS littéral141critères/140DoD/26pins et références, verdicts sémantique et produit séparés. |
| `python canonical-v35/docs/roadmap-v3.5/verify_priority_register.py --pinned --main-root history-work` | exit0 ; PASS documentaire80UX/15groupes/33opportunités/24lots/141exigences/140tickets/437assertions, hors verdict produit. |
| `python canonical-v35/docs/roadmap-v3.5/verify_run_state.py` | exit0 ; PASS documentaire curseur/dépendances/preuves, V3.4 active. |
| Liens fichiers locaux des dix documents Markdown du périmètre et références RUN | 335 occurrences Markdown,123cibles uniques ;60références inputs/evidence RUN vérifiées. Zéro cible absente après résolution historique. Le seul repli, BACKLOG → `../roadmap-v3.4/README.md`, existe dans `history-work` ; ce lien n'est pas ajouté par le delta. Aucune ancre locale dans ces liens ; URLs externes hors contrôle. |

Le PASS des contrôleurs ne produit pas un verdict sémantique automatique et n'active aucune fonction. Pas de mutation de contrat/état/code/distant par ce reviewer ; seul ce rapport est écrit. Les limites produit, Windows/GPU/Design Space/physique, CI, GitHub APPROVED et publication distante ci-dessus restent intégrales. Le coordinateur doit contrôler le diff et les blobs publiés au SHA final ; aucune attestation distante personnelle n'est revendiquée ici. L'éventuelle seule note de clôture PROGRESS après ce verdict n'étend pas ces empreintes à un autre état.

**Signé `review_creative_studio`, 15 novembre 2026. Suite : PROMOTION_DOCS sous ses conditions WIP/CI/revue ; V3.4 reste active.**
