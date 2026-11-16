# Q04Y — Quotas et ordre des rejets : décision bornée

15/11/2026. Main observé `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`. Le diff depuis aa0ff9e ne modifie que packaging Windows/workflow/doc associé ; `project_archive.py` et tests G13 sont inchangés. Lecture intégrale des branches `_validate_bundle`, `_payload`, `load_project` et du test précis `test_archive_bomb_exceeds_member_budget`. Les nouveaux cas ci-dessous sont des recettes, pas des tests exécutés.

| Limite existante V1 | Valeur et portée réelle |
|---|---|
| MAX_ENTRIES | 256 membres ZIP, manifeste inclus |
| MAX_MEMBER_BYTES | 64 MiB par ressource/membre ; limite de stockage, pas limite Cricut |
| MAX_TOTAL_BYTES | 256 MiB ; ressources puis payload ; chargement compte tous membres y compris manifeste |
| MAX_ARCHIVE_BYTES | 280 MiB pour le fichier archive lu |
| MAX_JSON_BYTES | 4 MiB par JSON |
| Ratio de compression | >2000 refusé à la lecture pour tout membre non vide |

Ordre côté `save_project`/bundle : IDs et enregistrements → document/opérations/JSON → types des maps → chaque chemin source obligatoire/sûr et collision exacte → masques/artefacts/snapshot → clés source inconnues → clés masque inconnues → ensemble ressources → aliases NFC/casse → chemins réservés/parent-fichier → bytes individuels → hash → type/dimensions/mode/pixels → total ressources. `_payload` applique ensuite nombre de membres et total JSON+ressources ; le manifeste est créé après ce contrôle. La relecture avant publication applique aussi les bornes du ZIP complet. Ne pas prétendre que la limite du payload hors manifeste garantit seule l'admission finale.

| Oracle isolé à ajouter si absent | Résultat de la branche source attendue |
|---|---|
| N3 retirer seulement source_paths[B], sources A/B autrement valides | MISSING_SOURCE_PATH |
| N4 ajouter seulement clé source_paths inconnue, sans ajouter ressource | UNKNOWN_SOURCE_PATH |
| N5 retirer/ajouter une ressource avec maps intactes | RESOURCE_SET_MISMATCH |
| N12 fournir une ressource >64 MiB au writer | INVALID_RESOURCE_BYTES avant calcul hash/pixels |
| N12 ouvrir ZIP avec membre déclaré >64 MiB | ZIP_BOMB_OR_OVERSIZED_MEMBER avant contrôle manifeste |
| N13 ressources valides individuellement, total >256 MiB | RESOURCES_TOO_LARGE dans bundle ; fixture synthétique bornée ou seuil injecté en test, pas images invalides qui échouent avant |
| N13 ZIP avec membres individuels admissibles et somme >256 MiB | ARCHIVE_BUDGET_EXCEEDED ; éviter ratio>2000 et membre>64 MiB qui masqueraient le cas |
| JSON+ressources à limite puis manifeste fait dépasser total | relecture du ZIP refuse avant publication ; ancien projet conservé |

Le test G13 existant écrit 64 MiB+1 de `Z` dans `assets/oversized.bin` puis attend ZIP_BOMB_OR_OVERSIZED_MEMBER. Il exerce la branche commune **taille ou ratio** ; son fichier très compressible ne permet pas d'attribuer le rejet uniquement à la taille. Pour isoler la taille : ZIP_STORED >64 MiB ; pour isoler le ratio : membre ≤64 MiB, ratio>2000 ; pour le total : plusieurs membres chacun admis et ratio admissible. Les métadonnées/manifeste ne doivent pas introduire une autre erreur avant le seuil visé. Ne jamais affaiblir les validateurs pour réussir les fixtures.

**Conclusion de conception :** les quotas et la hiérarchie des rejets sont identifiés ; aucune nouvelle exploration Q04Z n'est nécessaire pour répéter ce constat. Le contrat OCR minimal est prêt pour ses futurs micro-lots de fixture/source explicite/ROI ; une UI OCR reste non implémentée et les preuves Windows séparées. Réemploi de Q04S : sélectionner l'image source par identité/hash, jamais le PNG masque Atelier ; PAN et sélection ROI sont des modes explicites. Un résultat stale ne modifie pas V1.

Conserver l'original/float32/IDs, quatre exports distincts, limites de licence/confidentialité, rollback et cas de concurrence de Q04W/X. CPU et fixtures synthétiques suffisent aux tests de format ; GPU/Design Space/physique ne sont pas une dépendance de ce contrat. Les axes 01–25 du rapport de campagne restent applicables ; cette fiche n'ajoute aucune validation matérielle ni migration.

**Prochaine action de roadmap : RUN_STATE.json**, revue D/E restante et fermeture globale. Les tests de format à écrire appartiennent aux tranches produit ; ne pas prolonger indéfiniment la campagne documentaire OCR au détriment des autres fonctions.
