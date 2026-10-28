# SmartSVG Studio Matrice de couverture V3.3

**Navigation :** [Maître V3.3](ROADMAP_MASTER_v3_3.md) · [Registre de traçabilité](ROADMAP_TRACEABILITY_v3_3.md) · [Annexe historique](ROADMAP_HERITAGE_v3_3.md).

## 1 Mode d'emploi

Cette matrice est une checklist de conception et de recette. Chaque micro-lot copie les lignes applicables dans sa preuve et indique `PASS`, `FAIL`, `NON_EXECUTE`, `NON_APPLICABLE` ou `BLOQUE`. Seul `PASS` représente une preuve réussie. `NON_EXECUTE` et l'absence de valeur ne sont jamais assimilés à un succès.

Les références F, G, P, S et R33 renvoient respectivement aux familles, jalons, parcours, tickets historiques et exigences V3.3.

## 2 Parcours et capacités

| Parcours | Capacités minimales | Capacités d'enrichissement conservées | Gate dominant |
|---|---|---|---|
| P01 Sticker Print Then Cut | F01, F02, F03, F04, F07, F10, F14, F15 | F11, F12, F13 | G2 puis G4 |
| P02 Silhouette Basic Cut | F01, F03, F06, F10, F14, F15 | F11, F13 | G2 puis G4 |
| P03 Photo multi-sujets | F01, F02, F03, F10, F14, F15 | F04, F12 | G3 |
| P04 Planche 12 24 50 | F10, F11, F12, F14, F15 | F07, F13 | G4 puis G7 |
| P05 Composition texte | F08, F09, F10, F14, F15 | F05, F11 | G6 |
| P06 SVG multicouche | F01, F05, F06, F10, F15 | F08, F13 | G5 |
| P07 Bibliothèque variantes | F10, F14, F15 | F11, F12 | G7 |
| P08 Production personnalisée | F09, F10, F11, F12, F14, F15 | F13 | G7 |
| P09 Matériaux multiples | F05, F06, F08, F10, F13, F15 | F11, F12 | G9 |
| P10 Diagnostic récupération | F10, F14, F15 | toutes selon incident | G1 puis G8 |

## 3 Formats d'entrée

| Entrée | Contrôles obligatoires | Conservation | Erreurs attendues | Références |
|---|---|---|---|---|
| PNG | signature, chunks, CRC, dimensions, profondeur, alpha, profil | octets source et SHA | troncature, filtre invalide, bombe pixels, alpha incohérent | F01, F04, F15 |
| JPEG | marqueurs, dimensions, couleur, EXIF, orientation, fin de fichier | octets et EXIF | progressif invalide, troncature, trailing data, CMYK inattendu | F01, R33-025 |
| WebP | RIFF, taille, chunks, canvas, alpha, animation | octets et métadonnées | longueur forgée, chunk inconnu critique, animation non prise en charge | F01, F15 |
| SVG | XML sûr, namespace, `viewBox`, unités, scripts, liens, géométrie | source et profil | entités, contenu actif, URL externe, chemin hors bornes | F01, F05, F06, S-061 |
| `.smartsvg` | ZIP, noms, tailles, manifeste, SHA, schéma, références | archive originale et backup | traversal, doublon, bombe, version future, ressource absente | F10, F15, R33-009 |
| CSV | encodage, séparateur, colonnes, longueurs, formules | fichier et mapping | en-tête absent, doublon, injection tableur, glyphe absent | F12, R33-027 |
| Police | format, licence, glyphes, empreinte | référence ou paquet autorisé | absente, corrompue, licence incompatible | F09, R33-016, R33-028 |
| PDF futur | pages, chiffrement, rendu borné, contenu actif | original | mot de passe, page énorme, objet actif | F01, G9 |

## 4 Contrats de sortie

| Sortie | Contenu autorisé | Contrôles | Ne prouve pas | Références |
|---|---|---|---|---|
| PNG transparent | raster RGBA, taille px, profil documenté | alpha, résolution relative, halo, dimensions | import ou coupe physique | F04, F07 |
| PNG aplati Print Then Cut | rendu aplati selon profil | taille, fond, résolution, orientation | marques de capteur ou calibration | F07, S-029 |
| SVG Basic Cut | chemins sûrs, fermés, unités explicites | `viewBox`, mm, trous, doubles coupes, micro-détails | édition couleur fidèle | F06, S-030 |
| SVG Cut multicouche | chemins séparés par couche, couleur ou matière, ordre et repères d'assemblage | topologie de chaque couche, superposition, miroir, matière, tolérances et pack par couche | fidélité d'un SVG d'édition ou compatibilité universelle | F05-F06-F13, S-012, S-045, R33-023-R33-029 |
| SVG d'édition | objets, calques, couleurs et métadonnées sûres | fidélité, édition, ressources intégrées ou déclarées | découpe directe | F05, S-032, R33-008 |
| `.smartsvg` | projet, ressources, commandes, masques, manifeste | relecture, migration, atomicité | fonctionnement d'une extension externe absente | F10, S-053 |
| Rapport de prévol | constats, niveaux de preuve et limitations | provenance, SHA et environnement | certification générale | F06-F07, R33-034 |
| Pack de production | sorties, manifestes et instructions | cohérence, noms, succès partiels | fabrication réussie | F12, S-089 |

## 5 États d'interface

| État | Informations visibles | Actions autorisées | Actions interdites | Références |
|---|---|---|---|---|
| Vide | objectif, formats et confidentialité | importer, ouvrir, reprendre | exporter ou annoncer prêt | S-067, S-069 |
| Chargement | tâche et progression honnête | annuler si sûr, consulter détails | double lancement, succès prématuré | R33-014, R33-033 |
| Initialisation IA | fournisseur et raison de l'attente | annuler, choisir manuel | masquer téléchargement ou réseau | R33-017, R33-030 |
| Résultat proposé | source, révision, confiance et limites | accepter, comparer, rejeter | appliquer à une autre révision | R33-004, R33-005 |
| À vérifier | défauts localisés | examiner, corriger, changer de sortie | afficher prêt sans résolution | S-071, S-085 |
| Bloqué | cause et remède | revenir, restaurer, exporter diagnostic | continuer silencieusement | F14, R33-015 |
| Succès partiel | réussites et échecs séparés | reprendre l'échec, ouvrir rapport | effacer les réussites | R33-011, S-089 |
| Annulé | dernière révision saine | reprendre ou abandonner | publier résultat incomplet | R33-012, R33-033 |
| Expiré | session ou proposition expirée | rouvrir explicitement | agir sur ancien canal | R33-014 |
| Exporté | chemin, format et preuve atteinte | ouvrir dossier, recommencer | prétendre à la coupe | S-084, R33-034 |

## 6 Persistance et récupération

| Scénario | Résultat attendu | Preuve | Références |
|---|---|---|---|
| Création projet | archive validée puis publiée | relecture exacte | G1, F10 |
| Écrasement autorisé | ancien fichier conservé jusqu'à validation du nouveau | injection de panne pré-publication | R33-025 |
| Écrasement non autorisé | refus sans modification | comparaison octets | F10 |
| Disque plein | échec explicite, temporaire nettoyé, ancien sain | quota ou injection | R33-013 |
| Répertoire lecture seule | refus avant faux succès | test Windows et Linux | R33-013 |
| Fichier verrouillé | message et reprise possible | test Windows | G8 |
| Crash pendant sauvegarde | dernier snapshot validé récupérable | kill contrôlé | S-095 |
| Archive corrompue | refus et proposition de backup sans écrasement | mutations ZIP | F15, S-061 |
| Version future | refus sans migration destructive | fixture de schéma futur | R33-009 |
| Migration interrompue | original intact et rapport | injection par étape | R33-009, R33-025 |
| Index bibliothèque corrompu | reconstruction depuis projets | suppression index puis rebuild | R33-010 |
| Préférence UI corrompue | reset de disposition, projet intact | fixture invalide | R33-032 |

## 7 Sessions concurrence et opérations asynchrones

| Condition | Contrat | Test attendu | Références |
|---|---|---|---|
| Double clic | une seule opération active | deux événements même tick | R33-014 |
| Deux onglets même projet | révision comparée avant application | édition concurrente | R33-004 |
| Deux projets | aucune confusion d'identité | messages intercalés | R33-003-R33-005 |
| Canal expiré | action désactivée et message explicite | horloge contrôlée | R33-014 |
| Message dupliqué | idempotence | même `operation_id` deux fois | R33-011 |
| Résultat en retard | isolé comme proposition obsolète | nouvelle révision avant réponse | R33-005 |
| Annulation pendant IA | aucun résultat appliqué après annulation | réponse tardive | R33-012 |
| Fermeture onglet | canal et ressources libérés | observation cleanup | F15 |
| Redémarrage service | job repris ou déclaré perdu, jamais faux succès | restart contrôlé | R33-012 |

## 8 IA CPU GPU et fournisseurs

| Dimension | Cas à couvrir | Mesure ou résultat | Références |
|---|---|---|---|
| Absence de modèle | voie manuelle ou diagnostic | aucune file cachée | R33-007 |
| CPU seul | résultat ou refus avec temps | temps, RAM, qualité | R33-017 |
| GPU cible | modèle réellement chargé | VRAM pic, temps, versions | S-027, S-058 |
| OOM | fallback ou refus récupérable | aucune perte projet | R33-017, R33-025 |
| Timeout | annulation et état clair | ressources libérées | R33-012 |
| Masque vide | refus ou correction manuelle | code d'erreur | F02-F03 |
| Masque plein | alerte localisée | pas d'acceptation automatique | S-071 |
| Multi-sujets | IDs stables et accessoires | corpus annoté | S-028, S-070 |
| Modèle différent | provenance visible | empreinte poids et paramètres | F15 |
| Réseau indisponible | aucune requête implicite | test hors ligne | R33-030 |

## 9 Géométrie et fabrication

| Contrôle | PNG Print Then Cut | SVG Basic Cut | SVG Cut multicouche | SVG édition | Références |
|---|---|---|---|---|---|
| Dimensions physiques | obligatoire | obligatoire | obligatoire par couche et assemblage | déclarée | F04, F06, F07 |
| `viewBox` | non applicable | obligatoire | cohérent entre toutes les couches | obligatoire | F05-F06 |
| Chemins fermés | non applicable | obligatoire selon profil | obligatoire par couche de coupe | alerte selon usage | S-030 |
| Trous et îlots | alpha et masque | topologie | topologie et superposition | fidélité | S-056 |
| Doubles coupes | non applicable | bloquant ou averti | contrôlé intra et inter-couches | information | F06 |
| Micro-détails | résolution et impression | matière et lame | matière, lame et alignement | fidélité visuelle | S-085 |
| Couleurs | profil raster | information seulement | identifiant de couche ou matière | fidélité mesurée | R33-029 |
| A4 Letter | checklist Design Space | zone projet | pack et zones cohérentes | zone de travail | S-055, S-076 |
| Miroir | selon transfert | selon matière | explicite pour chaque couche concernée | préférence non destructive | F13 |
| Assemblage | non applicable | non applicable ou simple | ordre, repères, tolérances et prototype | non applicable | S-045, R33-023 |
| Validation réelle | import et impression | import et coupe | import, coupe par couche et assemblage | ouverture dans éditeur | R33-022-R33-023 |

## 10 Accessibilité responsive et langue

| Axe | Cas minimal | Critère | Références |
|---|---|---|---|
| Clavier | P01 et une erreur | aucune action essentielle inaccessible | S-072, R33-019 |
| Focus | dialogues, erreurs, retour | visible et logique | S-078 |
| Drag | déplacer, redimensionner, sélectionner | alternative boutons ou clavier | S-077 |
| Contraste | texte, focus, états | WCAG 2.2 AA cible | F14 |
| Couleur | prêt, erreur, sélection | texte ou icône redondante | F14 |
| Zoom UI | 125 et 150 % | action principale visible | S-094, R33-018 |
| 1366×768 | Express et Atelier | pas de contrôle critique masqué | S-068 |
| Petit écran | consultation et actions essentielles | pas de chevauchement ni scroll horizontal global | R33-018 |
| Lecteur d'écran | import, choix, export | labels et annonces utiles | F14 |
| Cibles | boutons et poignées | taille confortable ou alternative | F14 |
| Français | messages, formats, unités | vocabulaire cohérent et actionnable | R33-020 |
| Animation | progression et transition | réduction respectée | F14 |

## 11 Performance et capacité

| Charge | Mesures | Comportement attendu | Références |
|---|---|---|---|
| Image petite | temps import et aperçu | réponse visuelle rapide | R33-026 |
| Image très grande | RAM, décodage, aperçu | limites avant épuisement | F01, F15 |
| 32 sujets | temps de rendu des cartes | sélection fluide et bornée | F02 |
| 12 24 50 sujets | temps, RAM, disque | progression, pause et reprise | F11-F12 |
| Masque float32 | RAM et sauvegarde | aucune quantification cachée | R33-006 |
| SVG complexe | chemins, temps de prévol | refus ou simplification explicite | F06 |
| Historique long | taille projet et undo | budget et compactage réversible | F03-F10 |
| Bibliothèque large | index et recherche | reconstruction et résultats stables | R33-010 |
| GPU OOM | VRAM et reprise | fallback ou blocage explicite | R33-017 |
| Disque faible | espace estimé | avertissement avant lot | R33-013-R33-026 |

Les objectifs de latence restent des hypothèses jusqu'aux mesures sur la machine cible. Les rapports doivent publier p50, p90, maximum, taille d'entrée et environnement.

## 12 Sécurité confidentialité et licences

| Risque | Contrôle | Preuve | Références |
|---|---|---|---|
| Traversal archive | normalisation et allowlist | fixtures adversariales | S-061 |
| XML actif | parseur sûr et rejet | scripts, entités et URL | F15 |
| Bombe ZIP image | budgets avant extraction | ratios et pixels extrêmes | F15 |
| Injection HTML | DOM sûr et texte | payloads adversariaux | F15 |
| Canal même origine | consentement et durée bornée | message tiers et expiration | R33-014 |
| Fuite de média | aucune donnée dans logs ou dépôt | audit diff et rapports | R33-024 |
| Requête réseau | consentement explicite | test hors ligne | R33-030 |
| Secret | scan et revue | CI et diff | F15 |
| Police ou modèle | licence et provenance | inventaire versionné | R33-016-R33-028 |
| Extension tierce | autorité limitée | menace et permissions | F15 |
| Rapport support | expurgation | fixture avec chemins personnels | R33-015 |

## 13 Installation mise à jour et compatibilité

| Contexte | Scénario | Résultat attendu | Références |
|---|---|---|---|
| Windows cible neuf | installation sans cache | dépendances et routes disponibles | G8, R33-021 |
| Mise à jour | version précédente vers courante | projets et préférences préservés ou migrés | R33-009-R33-021 |
| Rollback | retour version précédente | projet original ou copie compatible | R33-021-R33-036 |
| Chemin avec espaces | installation et projet | aucune commande cassée | G8 |
| Chemin Unicode | import export et projet | noms conservés ou refus précis | R33-027 |
| Droits limités | lecture et écriture autorisées seulement | aucun contournement | F15 |
| Antivirus | fichiers temporaires retardés | erreur récupérable | G8 |
| Port occupé | démarrage | diagnostic et choix sûr | G8 |
| ComfyUI ancien récent | API et frontend | matrice de compatibilité | S-063, R33-038 |
| Python Node navigateur | versions supportées | refus précoce ou fonctionnement | R33-038 |
| Hors ligne | Express et édition manuelle | aucune dépendance cachée | R33-007-R33-030 |

## 14 Validation Design Space et physique

| Niveau | Informations obligatoires | Décision possible | Références |
|---|---|---|---|
| Prévol local | format, dimensions, chemins, avertissements | localement contrôlé | F06-F07 |
| Import Design Space | version, OS, profil, capture privée, résultat | import testé | R33-022 |
| Impression | imprimante, papier, échelle, orientation | impression testée | G4 |
| Découpe | machine, lame, tapis, matière, réglages | matière testée | R33-023 |
| Mesure | écarts, défauts, répétitions | contexte qualifié | S-031-S-057 |
| Généralisation | corpus et contextes multiples | limitée aux contextes couverts | R33-035 |

La réussite d'un niveau ne doit pas modifier le libellé des autres niveaux. Une coupe réussie sur une matière ne certifie pas toutes les matières.

## 15 Matrice des pannes et récupération

| Panne | Données à préserver | Réponse utilisateur | Reprise | Références |
|---|---|---|---|---|
| Import malformé | projet courant | fichier refusé et cause | choisir autre source | F01-F15 |
| Sauvegarde échouée | dernier projet sain | erreur, emplacement, diagnostic | réessayer ou changer dossier | R33-013-R33-025 |
| Export échoué | projet et exports précédents | succès antérieurs inchangés | relancer export | S-095 |
| UI fermée | révisions validées | proposition de reprise | ouvrir dernier snapshot | F10 |
| Service arrêté | projet et état job | état inconnu explicite | interroger ou relancer idempotent | R33-011-R33-012 |
| IA OOM | source et masque validé | fallback ou manuel | reprendre sans réimport | R33-007-R33-017 |
| Lot partiel | éléments réussis | liste des échecs | relance unitaire | S-089 |
| Migration échouée | archive originale | rapport et refus | ancienne version ou copie | R33-009 |
| Index perdu | projets | bibliothèque indisponible temporaire | reconstruire | R33-010 |
| Conflit révision | deux états | refuser l'application silencieuse | comparer ou recharger | R33-004-R33-005 |

## 16 Couverture des preuves par jalon

| Jalon | Tests automatiques | Windows | Design Space | Physique | Humain |
|---|---|---|---|---|---|
| G0 | inventaires et hashes | si outils Windows | non | non | droits et corpus |
| G1 | contrats et adversarial | fichiers et permissions | non | non | recovery review |
| G2 | UI DOM E2E | navigateur et zoom | instructions seulement | non | novice et accessibilité |
| G3 | fournisseurs et sessions | CPU GPU réel | non | non | qualité masque |
| G4 | prévol et formats | exports réels | obligatoire | obligatoire | recette fabrication |
| G5 | rendu et géométrie | éditeurs réels | selon sortie | multicouche | fidélité visuelle |
| G6 | commandes et persistance | navigateur et polices | sorties ciblées | prototypes | composition novice |
| G7 | lots et reprise | charge et stockage | échantillons | selon production | opérateur récurrent |
| G8 | suite complète | installations | matrice | matrice | recette finale |
| G9 | selon extension | contexte déclaré | selon extension | selon extension | validation dédiée |

## 17 Checklist de clôture d'un micro-lot

- [ ] Identifiants S ou R33 et parcours renseignés.
- [ ] Autorité de chaque donnée définie.
- [ ] Entrées, sorties et limites validées.
- [ ] États vide, chargement, erreur, annulation et reprise traités.
- [ ] Persistance, migration et rollback évalués.
- [ ] Sessions concurrentes et résultats obsolètes évalués.
- [ ] Clavier, focus, zoom et petit écran évalués.
- [ ] Confidentialité, licences et réseau évalués.
- [ ] Tests ciblés puis suites proportionnelles exécutés.
- [ ] Preuves liées au head exact.
- [ ] Validations non exécutées marquées `NON_EXECUTE`.
- [ ] Contre-expertise du diff réalisée.
- [ ] CI fraîche et conflits avec `main` vérifiés.
- [ ] Documentation d'état mise à jour sans modifier la roadmap figée.
