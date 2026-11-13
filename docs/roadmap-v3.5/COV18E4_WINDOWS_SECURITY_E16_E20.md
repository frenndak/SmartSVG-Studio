# SmartSVG V3.5 — COV-18E-4 : QA SVG, validation Cricut, distribution, confidentialité et aide (E16–E20)

**13 novembre 2026 — CANDIDATE, NON NORMATIVE.** Quatrième tranche E, après [E01–E05](COV18E1_LIBRARY_ATELIER_E01_E05.md), [E06–E10](COV18E2_ACCESSIBILITY_E06_E10.md), [E11–E15](COV18E3_RECOVERY_QA_E11_E15.md). Les **20 UX E01–E20** ont une nouvelle revue contradictoire documentaire ; 0/20 certifiées, V3.4 active. Sources : V3.3/lot 23, V3.4 13–17/21/22 et audit initial #134/COV17E, snapshot main aa0ff9e7d0c53dba3fdc429c02c6198736cfe935.

## 1. Contrats de QA, matériel et Windows

| UX | Obligation historique principale | Risque identifié / décision V3.5 candidate |
|---|---|---|
| **E16 — QA SVG path/viewBox/mm** | **S-030 P0** Basic Cut fermé et géométrie contrôlée ; **S-032 P0** édition/fabrication séparées ; **S-056 P0** holes/islands/offset, coupon réel ; V34-097/100/101/108/109/129 | **RACCORDER P0** : XML sûr (DTD, liens externes, styles actifs refusés), viewBox/mm/transform, contours/hole/winding vérifiés et rapport par rôle. SVG syntaxiquement valide ≠ profil CUT sûr ni validation machine. |
| **E17 — QA fabrication, profil et matériel** | **S-009 P0** dimensions/trajets précontrôlés, **S-012 P0** découpes testées ; **S-031 P0** coupons Explore 5, **R33-022** version DS liée aux preuves, **S-057 P0** registre machine/lame/tapis/matière/tests | **GARDER P0** : tri-state KNOWN/UNKNOWN/REJECTED, rapport versionné local/DesignSpace/physique séparés. Un prévol réussi ne doit jamais afficher « prêt machine » sans preuve externe. |
| **E18 — Windows offline, package et rollback** | **S-046 P2** application autonome avec étude coût/maintenance, **S-053 P0** restauration après crash, **S-095 P0** reprise sans perte ; V34-139/140 et lot 21 | **RACCORDER P1** : installer signé/contrôlé sous Windows, désinstaller/mise à jour sans perte de projet, ComfyUI non nécessaire, rollback du binaire et migration projet séparée. Prototype standalone_desktop_v34.py ≠ installateur distribué. |
| **E19 — Confidentialité/local/opt-in réseau** | **R33-030** aucune requête réseau implicite ; **S-061 P0** sécurité fichiers hostiles ; S-054 sidecar orthogonal ; IA sous licences consenties | **GARDER P0** : offline par défaut y compris création de packs, pas d'upload d'image, pas de poids IA téléchargés au premier clic, logs/EXIF/chemins locaux exclus des rapports partagés. Autorisation explicite et révocable. |
| **E20 — Aide, tutoriels et guides contextuels** | **S-072 P0** Express souris+clavier accessible, **S-076 P0** checklist export/DS incluant avertissements A4/Letter, **S-084 P1** ouvrir bon fichier/rapport | **RAFFINER P1** : aide ancrée dans le vrai état fonctionnel, guides HTML hors ligne, profils DS versionnés et instructions manuelles pour Score/Attach/Foil. Aucune action inert/de décoration ou tutoriel d'un outil absent. |

## 2. Réemploi des modules et garde-fous

**QA existante au niveau code à inspecter lors de la qualification** : cut_path_preflight pour contrôle de chemins, template_preflight pour géométrie, artifact_qa pour rapports alpha, direct_import_v218 (le SVG diagnostic ne doit pas être superposé au PNG PTC), V34-109 prévol et V34-129 les quatre projections. **Aucun de ces composants ne remplace une mesure de coupe réelle.**

**Packaging** : V34-139 prévoit installation/rollback, mais des tests sur Windows cible et vérification des dépendances GUI restent indispensables. Les droits du dossier de destination et les chemins Unicode/OneDrive/réseau doivent être essayés. Une mise à jour de logiciel ne doit pas lancer automatiquement de migration du schéma .smartsvg V1, ni requérir ComfyUI/IA locale.

**Smart Delivery** : assemble seulement les artefacts existants contrôlés, vérifie SHA/ZIP après publication, manuel HTML local échappé, aucune divulgation de source non choisie ni usage de polices sous licence non redistribuable. Le système de livraison n'est ni un moteur de découpe, ni une API Cricut.

## 3. Parcours et recettes à mettre en œuvre (NOT_RUN)

**Novice** : exporter SVG Basic Cut → recevoir une explication de l'incertitude de la coupe et instructions DS, puis enregistrer un pack si souhaité ; installation Windows et démarrage Express sans ComfyUI. **Expert** : inspecter géométrie, rapport QA, version DS, configuration outils, hashes de fichiers et preuves indépendantes.

**Adversariaux** : (1) SVG DTD/script/remote font → refus ; (2) viewBox incohérent avec mm ou chemin non fermé → aucune approbation CUT ; (3) matière/tapis inconnu → UNKNOWN, pas PASS ; (4) ancien profil Explore 5 avec version DS nouvelle → nouvelles validations demandées ; (5) Windows update échoue après désinstallation partielle → binaire précédent récupérable, projet intact ; (6) chemin OneDrive/Unicode avec fichier verrouillé → pas de perte ni remplacement silencieux ; (7) utilisateur refuse réseau ou IA → aucune requête/modèle installé ; (8) partage Smart Delivery avec EXIF/chemin local/licence polices → filtrage et consentement ; (9) guide mentionne fonction inexistante → avertissement/absence d'action plutôt que bouton trompeur ; (10) test de coupe réel annoncé alors que seules fixtures CI sont disponibles → rejet de statut PHYSICAL_PASS.

**Preuves** : auto unit tests et sécurité XML, UI Windows native et installateur réel, import Design Space par version, coupons Explore 5 et mesures physiques distinctes, mémoire/latence et GPU uniquement lorsque cela concerne l'IA. Tous NOT_RUN dans cette étude ; aucune mesure inventée.

**Statut et suite** : E01–E20 contre-expertisées dans ces quatre fiches, 0/20 certifiées ; les 80 UX A/B/C/D/E disposent désormais chacune d'une deuxième revue documentaire candidate, **0/80 prêtes à coder certifiées**. Le contrôle de leurs DoD complets, les 6 exceptions et 10 exigences G6/G9 non rattachées, les 33 opportunités et la promotion demeurent ouverts. **Prochaine étape V35-COV-19** : contre-expertise croisée des **33 opportunités**, unifier leurs décisions avec backlog W00–W16 et Smart Delivery, puis contrôle d'exhaustivité final avant toute PR et promotion de gouvernance.
