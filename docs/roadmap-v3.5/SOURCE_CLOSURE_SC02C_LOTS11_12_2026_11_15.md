# SC-02C — Modèles IA et raster : 60 assertions conservées

15 novembre 2026. Base candidate `3e602179a1bda334916f60ffc55933311438fe53`, main observé `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`. Revue documentaire du producteur, non adoption et aucun test produit exécuté. Suite de SC-02B ; SOURCE_CLOSURE reste ouverte.

Sources : [lot11](../roadmap-v3.4/11_MODELES_IA_LOCAUX.md), blob `9a169e3c7db786d6dca1123397b13fcadde6a80e`, contrats§5–6, assertions§8 et DoD§9 ; [lot12](../roadmap-v3.4/12_RASTER_PIPELINE.md), blob `30424177571a1e5c627cbdb0630c07c63ba344e0`, contrats§4–6, assertions§7 et DoD§8. Les 60 textes originaux restent intégraux dans SCENARIOS_V34_09_16. Critères associés : V3.3 F01–F04/F07/F15 et R33-006/007/008/016/017/024/025/030/034 notamment. Les références de modèles/licences de 2026 dans la source sont historiques : avant tout usage, requalifier les textes officiels de la révision exacte, pas reconduire un ancien verdict comme actuel.

**Décision de transfert pour chaque ligne : CONSERVER son assertion intégrale et le DoD du ticket propriétaire, avec le sens et la correction ci-dessous.** Les numéros abrègent T-V34-LL-NN. Une responsabilité complémentaire candidate ne crée pas de lien historique fictif. W14 est le consommateur IA, W03/W08 le raster/export/PTC, W15 la distribution et W13 l'accessibilité. DoD commun : contrats versionnés, original protégé, tests au SHA exact avec niveaux séparés, sécurité/licences, rétrocompatibilité et rollback réel ; aucune ligne ne remplace ces obligations.

## Lot11 — 30 décisions individuelles, V34-078–086

| Assertion | Propriétaire / consommateur | Sens conservé et contre-exemple exclu |
|---|---|---|
| 11-01 | V34-078 / W14 | Sans modèle, Express et détourage manuel fonctionnent offline ; l'IA ne bloque pas le socle. |
| 11-02 | V34-078/086 / W14 | ListModels ne télécharge ni exécute quoi que ce soit. Inventaire de métadonnées distinct de l'installateur. |
| 11-03 | V34-078 / W14 | Recommandation dépend de l'intention ; boîte Score+Cut ne reçoit aucune recommandation de modèle : géométrie et règles suffisent. |
| 11-04 | V34-078/086 / W14 | Révision, hash ou licence non vérifiés bloquent installation. Hash seul ne prouve pas la provenance. |
| 11-05 | V34-078/086 / W14 | Aucun badge commercial générique pour une révision à droits restreints ou inconnus, y compris le cas historique RMBG-2.0. Licence exacte datée/revue avant admission. |
| 11-06 | V34-078/083 / W14 | Carte affiche auteur, limites, taille inconnue et absence de preuve, sans compléter par supposition. |
| 11-07 | V34-079/083 / W14 | Refuser/Plus tard/Jamais donne zéro requête ; préférence modifiable explicitement, jamais ignorée par suggestion. |
| 11-08 | V34-079 / W14 | Consentement expiré/rejoué ou révision changée exige nouvelle autorisation liée aux bons octets. |
| 11-09 | V34-079 / W14 | Chaque redirection revalide destination ; URL privée, traversal et symlink refusés, pas seulement l'URL initiale. |
| 11-10 | V34-079/086 / W14 | Fichier sans hash ou hash différent reste non activé ; quarantaine explicite. Fichier et hash remplacés ensemble exigent encore provenance approuvée. |
| 11-11 | V34-079 / W14 | Téléchargement interrompu/repris n'active aucun fragment ; vérification complète avant publication du poids. |
| 11-12 | V34-079 / W14 | Serveur sans Range recommence à zéro avec message et staging neuf ; pas de concaténation corrompue. |
| 11-13 | V34-079 / W14 | Disque plein/annulation nettoie staging et ne touche pas le projet ; ressources libérées. |
| 11-14 | V34-079 / W14 | Deux clics installer même modèle/révision donnent un receipt d'installation unique ; ce receipt n'est pas le receipt d'édition du projet. |
| 11-15 | V34-080/086 / W14 | Code distant ou pickle non approuvé impose CODE_REVIEW_REQUIRED ; présence locale ne contourne pas cette garde. |
| 11-16 | V34-080/086 / W14 | Import de poids local passe les mêmes contrôles de licence/hash/provenance/runtime que téléchargement. |
| 11-17 | V34-080/082/086 / W14 | Inférence reçoit handle local admis, jamais URL de dépôt ou révision flottante. |
| 11-18 | V34-080/082 / W14 | Provider ne peut écrire le projet ; proposition puis bus et writer transactionnel qualifiés. |
| 11-19 | V34-081/084 / W14 | Changer de modèle libère les ressources précédentes avant nouveau chargement ; preuve d'unload exigée. |
| 11-20 | V34-081/084 / W14 | Deux jobs GPU passent par réserve/budget commun ; aucun contournement par provider. |
| 11-21 | V34-081 / W14 | OOM injecté : zéro commit, repli CPU/manuel explicite et UI récupérable ; mock différent d'un essai RTX réel. |
| 11-22 | V34-081/082 / W14 | Source/projet changé pendant inférence impose STALE ; session et génération revalidées. |
| 11-23 | V34-082 / W14 | Masque NaN ou ROI invalide refusés avant allocation d'identité sujet persistante. |
| 11-24 | V34-082 / W14 | 12/24/50 propositions sans troncature ; stockage V1 interdit reste interdit, packs internes V2 explicites si nécessaires. |
| 11-25 | V34-083 / W14/W15 | Désinstaller un modèle ne casse pas la lecture d'un projet existant ; proposer voie manuelle plutôt que réinstaller silencieusement. |
| 11-26 | V34-083 / W14/W15 | Upgrade garde ancienne révision jusqu'à vérification ; rollback du modèle distinct de celui du logiciel et du projet. |
| 11-27 | V34-084 / W14 | PyTorch/ONNX/legacy comparés à même source/ROI, provenance et runtime distincts ; pas comparaison de corpus différents. |
| 11-28 | V34-084 / W14 | Qualité, p50/p95, RAM/VRAM et SHA complet mesurés ensemble ; aucun score global sans résultats. |
| 11-29 | V34-083 avec V34-045 / W13 | Clavier/lecteur écran consentent/refusent/annulent/désinstallent ; alternative accessible si widget non supporté. |
| 11-30 | V34-085 avec V34-129/130 / W03/W04 | Escargots PNG PTC et boîte Score+Cut gardent rôles/opérations distincts ; DS et physique restent preuves séparées. |

## Lot12 — 30 décisions individuelles, V34-087–095

| Assertion | Propriétaire / consommateur | Sens conservé et contre-exemple exclu |
|---|---|---|
| 12-01 | V34-087 / W03 | Crop/nettoyage/export ne modifient pas les octets/SHA originaux. |
| 12-02 | V34-087 / W03 | EXIF6/8 : source orientée, ROI/masque et inverse cohérents ; aucune double rotation. |
| 12-03 | V34-087 / W03 | Conversion ICC/CMYK déclarée ; original et profil d'origine conservés dans le projet, copies de livraison expurgées séparément. |
| 12-04 | V34-087 / W03 | Dimensions excessives/décompression hostile refusées avant rendu et allocation excessive. |
| 12-05 | V34-087 avec V34-088 / W03 | Float32 NaN/Inf/shape incorrect bloquent sans mutation ; miniature L8 jamais autorité de retouche. |
| 12-06 | V34-088/095 / W03 | Prémultiplication alpha correcte : points témoins sans frange noire sur fonds blanc ET noir. |
| 12-07 | V34-088 / W03 | Nettoyer RGB des pixels alpha zéro ne change pas le masque de coupe accepté. |
| 12-08 | V34-088/091 / W03 | Antenne/bord intentionnel reste intact tant que proposition de suppression non acceptée. |
| 12-09 | V34-088/090/095 / W03 | Mesurer composantes/trous aux seuils diagnostics0/20/128 sur PNG final relu ; masque float32 non quantifié. |
| 12-10 | V34-088/090/091 / W03 | Masque changé après preview invalide QA et export sous ancien digest. |
| 12-11 | V34-089/095 / W03 | Conversion mm×ppi/25.4 avec politique d'arrondi explicite et métadonnées ppi conservées. |
| 12-12 | V34-089/091/095 / W03 | Sans mm, aucun affichage taille physique garantie ; dimension pixel seule ne suffit pas. |
| 12-13 | V34-089/091 / W03 | Interpolation CPU300→600 ne crée pas un badge de détail natif accru. |
| 12-14 | V34-092 / W14/W03 | IA absente/refusée : rendu CPU/manuel, zéro réseau. |
| 12-15 | V34-092 / W14/W03 | OOM texture préserve source ET contour ; unload et repli explicite. |
| 12-16 | V34-088/089/092 / W03 | Changer la texture IA ne change pas le digest de coupe accepté ; alpha d'impression et géométrie CUT distingués. |
| 12-17 | V34-090/095 / W03 | PNG PTC final lie alpha et cut digest attendus ; SVG diagnostic ne se superpose pas comme deuxième coupe. |
| 12-18 | V34-088/090 / W03 | Support blanc ou offset modifiés imposent nouveau prévol ; ancien fichier ne reçoit pas une nouvelle certification. |
| 12-19 | V34-088/090 / W03 | Rectangle alpha involontaire bloque ; carte rectangulaire explicitement voulue passe par revue, pas refus universel des rectangles. |
| 12-20 | V34-088/090/095 / W03 | Douze silhouettes extérieures et trous selon choix ; aucun faux cadre global ajouté. |
| 12-21 | V34-093 / W03/W12 | 24/50 ROI traitées en lots bornés, ordre stable ; pas cinquante masques pleine image en mémoire. |
| 12-22 | V34-093 / W03 | Même cache donne dérivé identique en octets ou divergence explicitée par version ; pas promesse générale de déterminisme IA. |
| 12-23 | V34-093 / W03 | Source/ICC/ROI/masque/version modifiés invalident cache ; paramètres/rôle/profil et pipeline inclus selon DECISIONS D03. |
| 12-24 | V34-093 / W03 | Tuilage n'introduit pas de jointure hors tolérance fixée ; sinon repli non tuilé dans budget ou refus utile. |
| 12-25 | V34-090/093 / W03 | Deux exports et crash staging : publication exclusive, reçu cohérent, aucun écrasement. Receipt externe différent du receipt de commande projet. |
| 12-26 | V34-090 / W03 | Reparse/symlink/traversal/collision de nom refusés, original protégé. |
| 12-27 | V34-091/095 / W13 | Avant/après, taille, avertissements et rollback accessibles au clavier en français. |
| 12-28 | V34-090/094 / W08 | Flat Graphic : contrôler manuellement taille/contour/opération dans DS, version et preuve datées ; parsing PNG seul insuffisant. |
| 12-29 | V34-094 avec V34-122/130 / W08 | Guide A4 historique portrait puis paysage sur tapis, session unique et résultat documenté ; profil/version actuels à revalider avant revendication. |
| 12-30 | V34-094 avec V34-106/111 / W04 | Texture de boîte ne déduit ni outil Score ni commande machine ; modèle d'opérations typées garde son autorité. |

## Corrections et limites

Les 18 DoD de tickets078–095 sont rapprochés : catalogue/admission, installateur, runtime, réservations, adaptateur de propositions, UI cycle de vie, benchmark/corpus/provenance ; puis admission raster, alpha, taille, prévol/publication, preview, texture IA, cache et corpus/comparaison. Aucun nouveau moteur parallèle n'est requis. Les contrôles de sécurité restent dans leurs consommateurs, même si le ticket de corpus cite tous les tests.

Le téléchargement d'un modèle est une transaction propre avec staging/hash/quarantaine et receipt d'installation ; il ne modifie pas .smartsvg. Publication d'un export est une autre transaction avec no-clobber et relecture ; elle ne remplace pas un receipt de commande projet. Les confondre créerait de faux succès ou des retries dangereux. Les trois identités/états sont séparés dans l'interface.

Les licences des modèles réellement utilisés doivent être vérifiées au moment de l'admission. Cette conception ne déclare aucun modèle libre commercialement, aucun runtime installé et aucun besoin de dépenser pour une API cloud. Les essais essentiels sont locaux/CPU ; la RTX est optionnelle et sa mémoire/qualité doivent être mesurées, pas promises.

Les 25 axes restent applicables, avec leurs frontières : inventaires et critères conservés ; source/revue/tests distincts ; V1/CAS/float32/V2 explicite ; quatre exports/opérations ; novice/expert/clavier/lecteur écran ; crash/annulation/concurrence ; IA/licence/ressources ; raster et topologie de contour ; cache/lots ; livraison externe ; métriques ; confidentialité ; anti-doublon ; gouvernance/promotion. Les essais Windows/RTX/DS/physiques sont NOT_RUN, pas implicites dans un résultat logiciel.

**Résultat borné : 60 assertions examinées individuellement, 18 DoD conservés avec oracles distincts.** Suite : SC-02D lots13–17 (vectoriel, fabrication, profils, patrons, exports), puis bibliothèque/Windows/validation et compléments des premiers lots/141critères/140DoD. SOURCE_CLOSURE ne sera close qu'avec l'ensemble réconcilié et la revue globale reste indépendante.
