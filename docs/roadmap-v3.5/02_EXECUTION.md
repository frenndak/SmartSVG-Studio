# Exécution V3.5 — 15 tranches de livraison

Tous les critères ci-dessous sont des **recettes proposées, NON_EXECUTE** dans cette session. Les recettes originales restent dans les documents V3.4 liés par `backlog.json` ; elles ne sont pas remplacées par cette liste complémentaire. « Code présent » dans l'état initial ne signifie pas « tranche terminée ».

## V35-01 — Référentiel vivant et preuve d'intégration

**Entrée :** main et PR courants. **Sortie :** un point de reprise cohérent, daté, lié aux critères et au code réel. Réutiliser les registres existants ; aucune nouvelle autorité d'exécution.

- A1 : conserver exactement les 141 IDs et les 140 tickets, les relations dans les deux sens, leurs documents sources et les dix exigences historiques sans ticket V34.
- A2 : réconcilier les résumés `ETAT_ACTUEL`, README V3.4 et matrice d'exécution dans un micro-lot de suivi, à partir du même SHA ; dater les preuves historiques.
- A3 : enregistrer code, raccordement UI et preuves par axe séparément ; un script de documentation ne met jamais un statut produit à PASS.
- A4 : relire les PR #138–140 et leurs revues avant tout doublon ; fournir un point de reprise unique et la prochaine commande concrète.

## V35-02 — Projet unique, sauvegarde et récupération

**Réutiliser :** archives V1, `ManagedWorkspace`, récupération et notes natives. **Sortie :** créer, ouvrir, modifier les notes, enregistrer et retrouver la même révision.

- A1 : créer depuis un PNG synthétique, relire le projet et vérifier source, identité, SHA et absence d'écrasement.
- A2 : garder un brouillon de notes en naviguant ; demander avant abandon ; une sauvegarde de retouche ne détruit pas ce brouillon.
- A3 : writer concurrent, lecture seule, disque plein et résultat indécidable : aucun faux succès, ancienne copie conservée, relecture proposée sans retry aveugle.
- A4 : `.previous` et `.pending-backup` : plan affiché, action confirmée et reçu relié au projet exact ; aucune restauration à l'ouverture.
- A5 : préserver ressources/IDs/contrats V1 et compatibilité des lecteurs ; tout besoin de V2 doit être justifié et migré sur copie dans un lot distinct.

## V35-03 — Atelier et historique natifs

**Réutiliser :** sélection de sujet, pinceaux, save bridge et historique G3.3e. **Sortie :** corriger, sauvegarder, Annuler/Rétablir puis rouvrir sans perdre l'identité.

- A1 : sujet prouvé uniquement pour la mutation ; sélection/vignette/aperçu restent synchronisés même si leur ordre change.
- A2 : afficher disponibilité/motif Undo/Redo à la révision vérifiée ; commandes confirmées sur le writer existant, une action = une mutation.
- A3 : Undo→Redo restitue l'état logique et les ressources attendus ; nouvelle édition après Undo invalide Redo ; frontières historiques inconnues refusées explicitement.
- A4 : aperçu, pan, zoom, annulation de brouillon et fermeture sans validation n'écrivent rien ; double clic et résultat tardif ne ciblent jamais un autre sujet.
- A5 : calques/propriétés dérivés du projet unique, visibilité/solo non destructifs ; propriétés physiques uniquement lorsque l'unité est établie. Persistance de propriétés absentes de V1 : décision de schéma distincte, aucun champ clandestin.
- A6 : gestes bornés, alternatives clavier et conservation float32 hors zone peinte ; notes et exports antérieurs conservés lors de l'historique.

## V35-04 — Express et ergonomie cohérente

**Entrée :** composants natifs disponibles ; pas de nouvelle pile UI imposée. **Sortie :** atteindre Importer/Créer/Reprendre et l'objectif de fabrication avec une aide compréhensible.

- A1 : afficher les quatre usages distincts ; expliquer un prérequis manquant et permettre la correction sans perdre le projet.
- A2 : états vide, chargement, erreur, conflit, succès et résultat non vérifiable testés ; aucune réussite avant relecture.
- A3 : parcours clavier complet, focus visible, labels et erreurs associées aux champs ; tester 900×650, 1100×760 et 1280×720 puis DPI Windows 100/150/200 % séparément.
- A4 : annuler une opération longue et reprendre le travail sans interface bloquée ; mesurer les latences et distinguer simulation de résultat durable.
- A5 : réglages récents, thèmes, disposition et actions favorites restent locaux, avec valeurs par défaut récupérables si préférences corrompues.

## V35-05 — Exports natifs, provenance et transfert

**Réutiliser :** producteurs, prévol, guide Design Space et writers de publication existants. **Découpage :** 05A PNG, 05B Basic Cut, 05C multicouche, 05D édition ; livrer et vérifier chaque contrat séparément.

- A1 : choix explicite d'un dossier de sortie commun, nom contrôlé et politique de conflit ; annuler n'écrit rien et ne remplace aucun fichier.
- A2 : aperçu + prévol affichés depuis la révision effectivement exportée ; refuser un export devenu obsolète après modification.
- A3 : publication atomique ou statut partiel explicite ; interruption/disque plein ne détruit pas l'ancienne livraison ; relecture des fichiers émis et de leur provenance.
- A4 : PNG : alpha, dimensions pixels, densité 300/450 DPI et dimensions mm cohérentes ; pas d'invention de résolution réelle après agrandissement.
- A5 : SVG : XML/namespace/viewBox/mm, chemins, trous et contrat de couches contrôlés sur le fichier produit, pas sur un objet de travail antérieur.
- A6 : ouvrir dossier et rapport depuis le succès ; guide distinct Print Then Cut / coupe / édition, pas de promesse d'import direct ou de coupe certifiée.

## V35-06 — Fidélité vectorielle et géométrie exploitable

**Réutiliser :** vectorisation et QA historiques. **Sortie :** comparer l'original au SVG réellement reconstruit et localiser les défauts avant publication.

- A1 : jeu synthétique avec trous, îlots, courbes, régions fines, transparence et chevauchements ; scores silhouette/couleur/géométrie séparés.
- A2 : simplifier sans changer la topologie ; seuils en unités explicites ; offset et petites régions conservés ou changement signalé.
- A3 : multicouche ≠ contour ; couches et ordre explicites, géométrie couleur réellement présente dans le SVG d'édition.
- A4 : contenu SVG non supporté converti avec comparaison ou refusé ; aucun script, ressource externe ou résolution d'entité exécuté.
- A5 : dépassement de budgets traité par message/repli ; comparer avant/après à la même échelle et sur le fichier final.

## V35-07 — Fabrication, profils et gabarits

**Réutiliser :** géométrie carte/boîte, prévol et profils. **Sortie :** dimensions, opérations et guide cohérents du gabarit au fichier.

- A1 : carte pliée et boîte ouverte : paramètres mm validés, plis/languettes, CUT et SCORE séparés ; valeurs impossibles refusées sans perdre les paramètres précédents.
- A2 : export/relecture et sauvegarde/réouverture du gabarit par un contrat défini ; ne pas inventer de stockage V1 pour une opération absente du schéma.
- A3 : machine/outils/matière en état connu/inconnu/incompatible ; aucun outil compatible déduit d'un nom commercial sans preuve.
- A4 : guide d'assignation et d'attachement dans Design Space ; un changement de profil invalide les preuves dépendantes.
- A5 : qualification A4/Letter, Print Then Cut, réglages et montage sur les environnements réels concernés ; dimensions mesurées consignées avec matériel et tolérance.

## V35-08 — Segmentation et IA locale facultatives

**Réutiliser :** interfaces fournisseurs et diagnostics ; l'adaptateur ComfyUI demeure compatible. **Sortie :** proposer un masque utilisable sans rendre ComfyUI obligatoire pour le parcours essentiel.

- A1 : alpha/manuel/CPU utilisables hors ligne ; IA indisponible = explication et repli réel, pas de rectangle présenté comme sujet segmenté.
- A2 : modèles disponibles, licences, taille, version et empreinte affichés ; consentement avant téléchargement et première exécution concernée.
- A3 : ID sujet, accessoires, masques float32 et coordonnées vérifiés ; résultat périmé proposé à part ou refusé, jamais appliqué à une autre révision.
- A4 : annulation/OOM/modèle absent : projet intact, reprise explicite sans téléchargement caché ; simulations distinctes de l'inférence réelle.
- A5 : mesurer temps, RAM et VRAM sur RTX 3070 8 Go et CPU ; qualité par corpus autorisé avant choix d'un défaut. Aucune licence ou performance fournisseur n'est validée par ce dossier.

## V35-09 — Import raster, alpha et qualité HD

**Sortie :** image orientée et couleurs contrôlées, masque aligné, marge et qualité justifiées.

- A1 : PNG/JPEG avec EXIF, ICC, alpha et dimensions extrêmes ; préserver original et alignement source/masque.
- A2 : anti-halo, nettoyage et offset avec comparaison et annulation ; absence de fond détachable annoncée.
- A3 : HD conditionnelle, estimation explicite de l'information disponible et budget ; aucun réglage DPI ne prétend créer du détail.
- A4 : vues original/masque/coupe et loupe se rapportent au même sujet ; changement de source invalide les propositions dépendantes.

## V35-10 — Planches 12/24/50 et reprise de lots

- A1 : placement déterministe, mm et marges dans une région admissible connue ; rotation/verrouillage honorés, aucun chevauchement silencieux.
- A2 : comparer deux dispositions sans modifier la source ; avertir si la zone imprimable reste inconnue.
- A3 : 50 sujets partitionnés selon les limites réelles des services ; aucun dépassement du plafond historique de 32 masques par appel concerné.
- A4 : succès partiel 48/50 et deux erreurs visibles ; relancer les deux seuls échecs sans doublon, identités et cache vérifiés.
- A5 : interruption, pause et annulation relues depuis le checkpoint ; aucun fichier de sortie réussi écrasé par une reprise implicite.

## V35-11 — Bibliothèque, variantes et CSV

- A1 : miniatures/recherche/filtres depuis un index reconstructible ; suppression de l'index ne supprime pas les projets.
- A2 : duplication avec nouveaux IDs adaptés, sans modifier le projet source ; reprise du dernier projet et contexte contrôlée.
- A3 : CSV : encodage, champs requis, valeurs manquantes, doublons et noms de sortie testés ; aperçu avant traitement et aucune formule exécutée.
- A4 : variantes liées à leurs paramètres et à la révision source ; relance ciblée, résultat partiel et rapport exploitables.
- A5 : ressources manquantes ou corrompues localisées ; une erreur d'index ne transforme pas une archive saine en projet perdu.

## V35-12 — Texte, polices et dioramas hérités

Cette tranche donne un propriétaire opérationnel aux **dix exigences sans ticket V34**. Elles gardent leurs critères V3.3 et ne sont ni supprimées ni renvoyées à une hypothétique version ultérieure.

- A1 : S-021/S-047 : OCR comme proposition vérifiable ; erreur OCR corrigeable, aucune substitution automatique du texte original.
- A2 : S-036/S-064/S-092 : licences, police absente, glyphes manquants, aperçu et conversion en tracés ; fichier partagé portable ou limite explicite.
- A3 : S-037 : gabarits métiers réutilisables avec dimensions et paramètres ; source préservée lors d'une nouvelle création.
- A4 : S-044/S-066/S-099 : quatre plans de diorama alignables, repères et guide d'assemblage dans l'UI ; test physique distinct de l'aperçu.
- A5 : R33-028, « Polices licences et glyphes manquants visibles » : licence et absence de glyphe signalées dans l'interface avant validation, sans substitution silencieuse ; reprendre ses critères complets V3.3 avant implémentation.

## V35-13 — Aide contextuelle et planification explicite

- A1 : aide liée au champ/erreur/objectif ; fonctions indisponibles expliquées ; pas d'assistant obligatoire pour une commande manuelle.
- A2 : plan à partir d'un catalogue fermé, simulation montrant entrées/sorties/effets ; identité et révision liées au plan.
- A3 : aucun texte externe, modèle ou contenu de projet n'autorise seul une mutation ; refus d'action inconnue et confirmation adaptée aux effets.
- A4 : annulation, changement de projet ou de révision invalide le plan ; repli manuel toujours disponible.
- A5 : préférences et diagnostics locaux expurgés ; pas de réseau ou coût implicite.

## V35-14 — Installation Windows, hors ligne et maintenance

- A1 : installer/lancer sur Windows sans ComfyUI, torch ou GPU pour le parcours essentiel ; inventaire précis des dépendances et licences avant packaging.
- A2 : test en environnement vierge, chemins accentués/espaces, répertoires non inscriptibles et lancement sans réseau ; erreur actionnable si composant optionnel absent.
- A3 : démarrage, fermeture et processus workers propres ; mise à jour interrompue récupérable et rollback conservant les projets.
- A4 : diagnostics locaux expurgés exportés volontairement ; aucune image ou donnée privée ajoutée au dépôt.
- A5 : les modifications dépendances/packaging et toute publication restent des lots distincts selon l'autorité du dépôt ; une CI Windows n'est pas une installation utilisateur qualifiée.

## V35-15 — Recette transversale et preuve d'usage

- A1 : quatre parcours sur fixtures autorisées : PNG transparent→Print Then Cut, masque manuel→Basic Cut, dessin couleur→multicouche/édition, boîte→CUT/SCORE ; créer→corriger→sauver→rouvrir→exporter dans chaque parcours pertinent.
- A2 : exécuter positifs, entrées invalides, résultats obsolètes, interruption/reprise et concurrence aux frontières modifiées ; aucun skip critique caché dans un total.
- A3 : Windows UI/DPI/accessibilité, inférence CPU/GPU, Design Space et découpe physique possèdent chacun SHA, versions, protocole et résultat ; aucun axe ne valide les autres.
- A4 : novice et utilisateur régulier accomplissent les objectifs ; erreurs, temps et reprises observés, puis corrections testées. Les cibles de latence des sources restent à mesurer, pas des résultats acquis.
- A5 : pas de « V3.5 complète » avant couverture des critères hérités et nouveaux pertinents ; les blocages matériels sont nommés par parcours sans immobiliser les développements indépendants.

## Fin de chaque micro-lot

Livrer le comportement observable, les fichiers touchés, critères exacts, commandes réellement exécutées et résultats, limites, diff relu et prochaine action. Repartir du HEAD actuel et des PR ouvertes. Rollback par retrait de l'adaptateur/UI du lot en gardant les services et fichiers antérieurs ; toute migration de données exige sa propre preuve de retour sûr. Aucun pourcentage de complétion estimé à partir du nombre de PR.
