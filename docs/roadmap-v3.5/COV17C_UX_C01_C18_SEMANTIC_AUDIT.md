# V35-COV-17C — Revue UX C01–C18 : fabrication, Cricut et planches

**13 novembre 2026 — 18 décisions CANDIDATES, aucun critère machine certifié.** Les intitulés originaux viennent d'[issue #134](https://github.com/frenndak/SmartSVG-Studio/issues/134), sources V3.4 lots 14/15/17/19/20. La V3.4 reste normative; V3.5 est une conception, et les nouvelles spécifications ne valent pas preuve de productibilité.

## 1. Ports de code comparés aux intentions utilisateurs

| Port réel main@aa0ff9e7 | Blob SHA vérifié | Portée réelle vs souhaitée |
|---|---|---|
| `template_geometry_v34.py` | `3142c2e379fd28c2b506c343527b932780d6fcee` | folded_card / open_tray produisent deux géométries mm sans export, machine ou projet |
| `template_preflight_v34.py` | `4cf83b1a12d0fbaa4c0f7cd52576ceb1c50434dd` | Prévol statique fail-closed des deux patrons de whitelist seulement |
| `smartsvg_governance/cut_path_preflight.py` | `94950646a809001272525be8b58d1741c0d87487` | inspect_cut_paths est un prévol géométrique pour chemins Basic Cut ; pas test réel |
| `smartsvg_cricut/direct_import_v218.py` | `a49fc10844559d431f393a7f7f56343ebefeb1cf` | PTC PNG et copie/preflight local ; le SVG contour annexe n'est pas empilé sur PNG |
| `smartsvg_governance/artifact_qa.py` | `c47009f2a47e664dc0ee36433f7f562dc7a675f0` | QA fichiers historiques, statut REVIEW_REQUIRED/BLOCKED, pas certification DS/coupe |
| `cricut_preflight_v205.py` | `7276e1c744f45236c6215361bbf733ecf35e9cbd` | Prévol historique PNG/SVG et aperçu non destructif |
| `smartsvg_core/project_contracts.py` | `7bfd2d714384717c6ce0bb66659971881bd285c2` | Artifact.use V1 accepte 3 valeurs ; multicouche CUT reste projection externe |

**Contrats non négociables** : les quatre exports (PNG PTC, SVG Basic Cut, SVG CUT multicouche, SVG édition) sont distincts ; `Artifact.use` V1 n'en persiste que trois. Les opérations `CUT/SCORE/DRAW/PRINT/FOIL` sont une sémantique à confirmer dans Design Space, pas un cinquième format ni une assignation déduite d'une couleur. Prévol local, import Design Space et coupe physique sont **trois preuves non interchangeables**.

Sources V3.4 relues sur commit `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935` : `14_LANGAGE_FABRICATION.md` blob `3b7dd601c6f844f3a3d12b44bc971fc101133367`, `15_PROFILS_EXPLORE5.md` blob `19cf7835044936e5cf2a2f894b5a42456c8fa8b4`, `19_PLANCHES_NESTING.md` blob `e6ac52be45c79999a2ed043c44ed0c972fa8f007`, `20_BIBLIOTHEQUE_VARIANTES_CSV.md` blob `b58e891ce65edcfa5ccabe46c24968036781e92a`. Les descriptions de futurs modules/tickets de ces lots ne signifient pas code déjà exécuté.

## 2. Décision C01–C18 individuelle : capacité, limitation, tests négatifs

| ID source | Intitulé hérité #134 | Décision/P | Interface existante et couverture limitée | DoD conception V3.5 | Cas adversariaux obligatoires |
|---|---|---|---|---|---|
| **C01** | stickers : offset, bleed, alpha, PNG Print Then Cut | **P0 / RACCORDER** | direct_import_v218 PTC PNG et QA alpha; UI natif export bout-en-bout non établi | Choix PNG seul, dimensions/ppi/bleed + prévisualisation, zones transparentes hors cadre, pas de SVG superposé | alpha rectangle, taille inconnue, DPI source faux, guide DS absent |
| **C02** | vinyle monochrome : silhouette et simplification | **P0 / AMÉLIORER** | cut_path_preflight.inspect_cut_paths est static Basic Cut; aucune garantie vinyle réel | Silhouette extérieure + trous validés, Smart Weeding diagnostic, limite matière UNKNOWN | double coupe, îlot minuscule, chemin ouvert, miroir HTV non confirmé |
| **C03** | multicouche : palette, couches, alignement | **P1 / RACCORDER** | layers_v2113 SVG couleur éditable; V1 Artifact multicouche CUT non persistable | Couleurs en calques CUT typés externes + provenance/alignement, jamais réétiquette editable_svg | calques fusionnés, erreurs ordre/transform, matériel déduit de couleur |
| **C04** | pochoirs : îlots flottants, ponts | **P1 / RAFFINER** | prévol géométrique existant pour contours, pas ponts de pochoir natifs validés | Repérer îlots flottants, proposer ponts réversibles, inspecter topologie avant CUT | pont trop fin, îlot volatil, trous mal orientés |
| **C05** | dessin/centerline, continuité des chemins | **P1 / RAFFINER** | vectorize_flat_art contours; centerline pen / continuité non vérifiés | Réglage centerline DRAW distinct CUT, tests fermeture/continuité avant export | ligne brisée, points doublés, ink vs blade confondus |
| **C06** | CUT/SCORE/DRAW/PRINT/FOIL distincts | **P0 / GARDER** | template_geometry CUT/SCORE nominal, preflight_template sans assignation Design Space | Opérations CUT/SCORE/DRAW/PRINT/FOIL avec confirmation manuelle, ids et couleurs non autoritaires | SCORE par couleur, FOIL sans outil, CUT de guide, physique faux PASS |
| **C07** | prévol géométrique : détails fragiles, doubles contours, intersections | **P0 / AMÉLIORER** | cut_path_preflight et artifact_qa détectent sous-ensemble path/PNG, pas fabricabilité certifiée | Smart Cut Advisor non mutant, longueur/densité intersections/îlots/topologie, warnings explicables | microforme fragile, doublon caché, path invalide, seuil matériel non prouvé |
| **C08** | profils machine/matière/lame/tapis/unités | **P1 / RACCORDER** | V3.4 lot15 profils TRISTATE proposés, aucune certification matière; preflight_template connait pas outils | Profil versionné machine/mat/matière/outil avec KNOWN/UNKNOWN/REJECTED et datation | outil absent, profil périmé, matière inconnue, taille support devinée |
| **C09** | variantes fidèle/équilibré/découpe facile | **P1 / AMÉLIORER** | vectorize_flat_art et color_repair expérimentaux, pas variantes fabrication optimisées prouvées | Fidèle/équilibrée/facile comme trois projections liées à même source, métriques de pertes géométriques | trou perdu, angle lissé indument, identité variante incorrecte |
| **C10** | les QUATRE contrats séparés : PNG Print Then Cut / SVG Basic Cut / SVG Cut multicouche / SVG d'édition | **P0 / GARDER** | Artifact.use V1 3 valeurs, quatre exports métier externes; lot17 explique différence | Sélection d'intention avant serializer, contrôles PNG PTC/Basic Cut/multilayer/édition distincts | multilayer dans editable_svg V1, PTC mêlé SVG, unité absente |
| **C11** | transfert guidé Design Space, Score/Attacher, vérification dimensions | **P0 / RACCORDER** | direct_import_v218 publie fichiers PTC PNG et guide, pas session Design Space pilotée | Assistant DS versionné et manuel, Score/Attach/tailles/print guidés, aucun driver ni marks bricolés | dimension non confirmée, absence internet DS, Score non attaché, coupe non mesurée |
| **C12** | Smart Layout duplication/planche multi-pages/quantités | **P1 / RACCORDER** | V3.4 lot 19 nesting conçu; producteurs planches historiques pas moteur natif unique confirmé | Instancier pages 12/24/50, total exact des IDs, copies/quantités, reprise après échec partiel | dupliqué, perte d'instance, lot >32 masques sur V1, mémoire dépassée |
| **C13** | nesting par silhouettes, rotation, marges, contraintes | **P1 / RAFFINER** | V3.4 lot19 algorithme déterministe proposé, aucune exécution qualifiée | Nesting silhouette en mm, marges/rotation/tapis, preuve par page avec dégagement | chevauchement, îlot inversé, glissement dimensions, placement impossible |
| **C14** | placements verrouillés, édition manuelle, réoptimisation | **P1 / AMÉLIORER** | workspace CAS existant; locks de placement et repositionnement non prouvés | Placement verrouillé vs libre, reoptimiser les seuls libres sans modifier autres; undo replay | pièces bloquées déplacées, orientation perdue, collision après reprise |
| **C15** | économie de matière, reprises de lot | **P2 / RACCORDER** | V3.4 lot19 réemploi matière/reprise futur, Smart Cost non présent comme devis sûr | Matériau et coûts saisis, surface réelle et perte calculée; reprise cache/lot sans double charge | prix inventé, scraps non mesuré, relance facture double |
| **C16** | patrons cartes/boîtes/enveloppes/pochoirs, modèles paramétriques | **P1 / RACCORDER** | folded_card/open_tray et preflight_template seulement 2 patrons; pas topper/étiquette/enveloppe prouvés | Catalogue paramétrique borné + trois gabarits G6 historiques, mm; aucune modification whitelist sans tests | patron inconnu admis, languette hors planche, diorama simulé |
| **C17** | géométrie mm, languettes/plis/épaisseur/preflight | **P1 / GARDER** | template_geometry mm, prévol fail-closed; géométrie ne garantit pas papier découpé | Plis/fentes et épaisseur explicites, avertissements matériau, mesures mm et 4 sorties distinctes | NaN, auto-intersections, rainures hors pièce, outil inconnu |
| **C18** | preview patron 2D / simulation de pliage 3D éventuelle. | **P2 / REPORTER 3D** | aperçu 2D de template réellement disponible; simulation de pliage 3D non démontrée | Preview 3D optionnel sans remplacer tests score/coupon, provenance et volume limités | volume inversé, 3D trompeuse, simulation décrite comme coupe réelle |

**18/18 avis CANDIDATS individuels**. Ne créer aucun outil séparé « Smart » pour chaque ID : regrouper Prévol (C07–C09), Export/Design Space (C10–C11), Planche (C12–C15) et Fabrique (C16–C18) derrière **une seule architecture** W03/W04/W06/W07/W08/W09/W11/W12.

## 3. UX novice/expert et action-réparation

**Novice stickers :** importer PNG → apercevoir contour alpha réel → vérifier taille et DPI → sélectionner `PNG Print Then Cut` → exporter depuis source qualifiée → guide d'import comme Flat Graphic → **confirmer taille et mode dans Design Space** → coupe physique uniquement si vraie preuve. Un SVG de contour joint ne peut pas être présumé associé automatiquement au PNG. Orientation A4 et limites sont des points d'instruction versionnés, pas des valeurs Cricut universelles figées.

**Novice boîte** : dimensions en mm → preview CUT/SCORE distinct → prévol statique avec `UNKNOWN` si matière/tapis/outil non vérifiés → export de la géométrie effectivement supportée → guide pour sélectionner Score et Attacher dans DS → éventuel coupon réel mesuré. Ni `folded_card` ni `open_tray` ne certifient un résultat physique. Les gabarits historiques étiquette/topper/carte et diorama 4 plans nécessitent encore leur propre port/recette (S-037, S-044/066/099).

**Expert** : voir les quatre contrats et versions explicitement choisis, unités mm/viewBox, profils machine/matériau connus vs inconnus, SHA source, groupes/IDs CUT/SCORE, trous/îlots, limites de paths et QA. Les placements verrouillés, coûts et pertes restent distincts de la preuve de fabrication; aucun score « optimum » non étayé.

**Annuler / reprendre** : les modifications de planche ou de variante sont réversibles dans brouillon. Un export externe publié et une vraie découpe ne sont pas annulés par Ctrl+Z ; on ne promet pas de restauration physique. Les copies et exports échoués ne modifient pas `.smartsvg` source; no-clobber pour publication; crash et reprise à enregistrer par item.

## 4. Tests croisés à créer (NON EXÉCUTÉS)

1. **PNG PTC** : source et alpha SHA inchangés, ppi/mm cohérents, aucune marque de capteur inventée et pas de SVG CUT superposé ; négatifs alpha rectangle, holes, 11/12 îlots, erreur DPI.
2. **SVG quatre contrats** : inspecter XML sûr et chemin fermé/multilayer séparé/édition, unités mm, contours trous, split opérations ; négatifs DTD/scripts, alias `editable_svg` pour multicouche et Score inféré.
3. **Fabrique** : `folded_card` / `open_tray` sous paramètres positifs/mm, prévol sans mutation, refus NaN/intersection ; Design Space Score/Attach et coupon physique avec preuves distinctes.
4. **Planches 12/24/50** : identités stables, `MAX_MASKS=32` respecté, paquet d'instances ne devient pas 50 masques en V1, reprise crash/idempotence, placement sans collision.
5. **Smart Weeding / Cut Advisor** : suggestions non destructives, variantes géométriques mesurées, seuils profil/matière UNKNOWN, test de coupon avant génération de coupes supplémentaires.
6. **Smart Cost** : prix utilisateur seulement ; une estimation ne constitue jamais un coût réel garanti ni un gate du jalon A.

**Axes séparés** : `AUTO_UNIT=NOT_RUN`, `WINDOWS_UI=NOT_RUN`, `GPU=NOT_RUN`, `DESIGN_SPACE=NOT_RUN`, `PHYSICAL_CUT=NOT_RUN` dans cette fiche. Les noms d'API ci-dessus sont des ports inspectés et non la validation des 18 gestes utilisateur.

**Prochaine passe** : `V35-COV-17D` D01–D12 (IA facultative/consentement, VRAM/CPU, cache et batch), suivie d'E01–E20 et d'une revue intégrale de 80 décisions candidates contre les critères V3.3 et 33 opportunités, sans rétrograder les exigences héritées.
