# V35-COV-17D — Revue UX D01–D12 : IA locale, consentement et automatisation

**13/11/2026, CANDIDAT NON NORMATIF.** 12 critères de #134 reproduits sans suppression, avec décisions et DoD individuels ; les composants cités sont des fonctions observées sur `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`, **pas** 12 fonctions Windows intégrées. La V3.4 et les engagements V3.3 restent la référence.

## 1. Limites réelles des fournisseurs et du mode hors ligne

| Port réel | Blob SHA vérifié | Ce qu'il établit / limite |
|---|---|---|
| `smartsvg_ai/hardware.py` | `30354bf3fd1844cb5ffbb9085c0098c8278d8842` | `diagnostic_report` utilise un wrapper lazy, pas un runtime de modèles préinstallés |
| `smartsvg_ai/provider_v2112.py` | `5a2c5fcb889ad796eb13b2262d6cc442c300b3cd` | Adaptateur RMBG ComfyUI fail-closed ; son docstring précise que le fournisseur **peut télécharger des poids au premier appel**. Risque majeur : ne pas lancer sans décision préalable |
| `smartsvg_ai/auto_masks_v2111.py` | `4530631c75051a115f030fb0e76bc269bc3c1d74` | Génération de masques alpha/art plat + IA facultative, sans preuve d'identité sémantique du sujet |
| `smartsvg_ai/routing_v21121.py` | `b039543450d69ff94c9a9e83e6e93c5255f1b1fe` | Routeur conservateur, **pas** OCR ni reconnaissance sémantique garantie |
| `smartsvg_ai/quality_v21121.py` | `371577f2bcd389acdb18f98e0ce3e650f915c690` | Diagnostic métrique consultatif, jamais preuve de coupe ou qualité humaine |
| `smartsvg_quality/auto_hd.py` | `6ad1733e8980fa7aa0aa35a625da703ff953374e` | Dérivé PNG HD CPU, original et alpha protégés; pas de gain de détail original établi |
| `smartsvg_core/project_workspace_g22.py` | `13b8e40d6fcc9cf03ed2c935b38ad6eff0bcbe03` | ManagedWorkspace, writer CAS et reprise ; pas de second writer IA |
| Sources de conception : V3.4 lot 11, lot 09 | blobs `9a169e3c7db786d6dca1123397b13fcadde6a80e` / `52e61d658d47570edffb662fc4f8983cf1208512` | Catalogue/licences/VRAM/planificateur spécifiés ; **leur existence documentaire n'est pas un code exécuté** |

## 2. Douze décisions individuelles D01–D12

| ID historique #134 | Intitulé source | Décision provisoire | Port et limite | DoD nouveau | Négatifs à couvrir |
|---|---|---|---|---|---|
| **D01** | fournisseurs de segmentation CPU/SAM léger/SAM2/3 selon viabilité réelle | **P1 / RACCORDER** | auto_masks_v2111 + provider_v2112 RMBG ComfyUI fail-closed, modèle externe susceptible de télécharger au premier appel | Catalogue de fournisseurs attestés par signature/version/licence, bouton consentement explicite avant toute exécution/téléchargement | provider absent, signature modifiée, mémoire insuffisante, download silencieux |
| **D02** | consignes clic/lasso/pinceau/texte combinées | **P1 / AMÉLIORER** | strokes.py pour pinceau raster, auto_masks propose alpha/flat; combiner clic/lasso/texte non prouvé | Unifier inputs d'intention comme ROI/proposition non-mutante; changement SHA invalide plans | lasso vide, frappe prise comme prompt non autorisé, index sujet obsolète |
| **D03** | variantes et choix expliqué avec confirmation | **P1 / RACCORDER** | quality_v21121 métriques QA consultatives, aucune certitude sur masque dit « meilleur » | Comparer variantes/résultats avec raisons, incertitudes et acceptation, sauvegarder décision sans score inventé | toute variante échoue, alpha inversé, qualité IA déclarée certifiée |
| **D04** | matting cheveux/poils/translucide | **P2 / ÉTUDIER** | masques float32 et détourage existent ; matting semi-transparent cheveux/poils non qualifié | Matting local facultatif, transparence partielle et couleur de bord vérifiées avec ground truth sous licence | cheveux supprimés, halo, masque binaire trompeur, RAM insuffisante |
| **D05** | upscale HD conditionnel | **P1 / RAFFINER** | auto_hd CPU dérivé non destructif; super-résolution IA de détail réel non prouvée | HD conditionnelle sur taille/résolution utiles, provenance et critique des artefacts, pas d'upscale automatique imposé | pixels inventés, alpha changé, ancienne source, 600ppi étiqueté vrai |
| **D06** | génération raster/vector facultative | **P2 / ÉTUDIER** | aucune génération raster/vector native complète vérifiée dans les ports inspectés | Génération locale opt-in si licence/runtime et modèle compatible, brouillon non mutant/contrat sortie | licence interdite, modèle absent, image sous droits ajoutée, réseaux non sollicités |
| **D07** | inpainting et réparation locale | **P2 / ÉTUDIER** | color_repair_v21141 vector source-derived expérimental ; pas un inpainting génératif garanti | Proposer réparation locale/édition du pixel, comparer source et région cible, undo et provenance | détails inventés non signalés, bord masqué, ROI hors image, résultat tardif |
| **D08** | catalogue modèles : licence, versions, hash, consentement | **P1 / AMÉLIORER** | provider_v2112 disponible/signature, hardware.py diagnostic lazy; pas de catalogue licencé et consentement complet démontré | Registre de modèles version/licence/hash/taille, consentement par usage et révocation, jamais poids dans repo | hash faux, licence inconnue, fichier modèle corrompu, auto-install |
| **D09** | VRAM/CPU/repli/annulation/diagnostic | **P1 / GARDER** | hardware.py diagnostic wrapper, provider_v2112 applique masks via dépendances à tester, 8Go VRAM visés | Capacité CPU/GPU et budget exact à mesurer, OOM avec annulation non destructrice, repli manuel | OOM, torch absent, GPU non disponible, race cancel |
| **D10** | recettes et préréglages de traitement | **P1 / RACCORDER** | qualités/PNG et paramètres historiques existent, recipes persistantes vers V1 sans contrat vérifié | Recettes paramétrées versionnées hors V1 jusqu'à ADR, provenance sources et paramètres de modèle | preset source obsolète, paramètre non borné, licence manquante |
| **D11** | batch, dossiers, CSV, reprise et erreurs individuelles | **P1 / RACCORDER** | ManagedWorkspace et production_v211 sorties, batch 12/24/50 conçu, scheduler complet non vérifié | Queue unique et CSV inerte, checkpoints per item, reprendre sans doublon, limite 32 masques/package | CSV formula, item réessayé deux fois, archive trop grande, collision nom |
| **D12** | assistant contextuel et suggestions explicables. | **P1 / AMÉLIORER** | routing_v21121 est conservateur; lot 09 planificateur sécurisé spécifié, pas exécution IA automatique approuvée | Assistant explique options, plan déterministe, autorisation explicite et undo/CAS, pas plans imposés | intention ambiguë, effet destructif, exécution sans clic, explication sans preuve |

## 3. Frontière de sécurité, modèle utilisateur et proposition sans mutation

**Règle principale** : `model_available` et `provider_signature_ok` ne prouvent **ni** `weights_present`, ni `license_accepted`, ni `download_allowed`, ni `model_executed`. Si l'adaptateur ComfyUI peut télécharger des poids au premier appel, le premier appel est interdit sans **preuve explicite de consentement et estimation préalable des ressources/réseau**, ou doit passer par un garde d'installation validé. Le bouton `Analyser avec IA` ne doit pas cacher une installation.

**Novice** : proposer détourage manuel/CPU immédiatement, mentionner ce que l'IA pourrait améliorer, demander un consentement précis sur fournisseur/taille/licence/reseau, afficher preview et alternatives, puis seul un clic explicite engage la sauvegarde. Refus ou modèle absent = poursuivre sans IA.

**Expert** : tableau de provenance par modèle (éditeur/version/hash/licence, taille, type d'entrée/sortie, VRAM CPU, cache, réseau, journal anonymisé et révocation), comparaison ROI IA vs manuel sur même source, édition des masques et annulation. Un traitement ancien ne peut jamais committer sur une nouvelle révision sans revalidation SHA/CAS.

```text
Source V1@SHA
  -> Intention manuelle ou IA [no download]
  -> Eligibility(capabilities,license,weights,consent)
  -> Proposal{base_sha,roi,model_version,mask,float32,quality_uncertainty}
  -> Preview + correction / rejet
  -> Commit CAS existant seulement sur accord et même SHA
  -> Relecture et qa, avis Windows/DS/physique indépendants
```

**États** : NO_MODEL, AVAILABLE_NO_WEIGHTS, READY_LOCAL_CONSENTED, DOWNLOAD_REQUIRES_APPROVAL, GPU_OOM, CANCELED, STALE_RESULT, PROPOSAL_READY, COMMITTED. On ne doit pas fusionner ces états en `IA activée` global. Matériel 8 Go VRAM est un **cible de banc d'essai** ici, non preuve de fonctionnement de chaque modèle.

## 4. Qualification et scénarios adversariaux

- Sans réseau, modèle, ComfyUI et PyTorch : Express, import, édition/exports manuels existants doivent démarrer sans import torch obligatoire.
- Fournisseur détecté mais poids absents : aucun téléchargement silencieux, aucune exécution, retour CPU/manuel. Licence non trouvée et hash mismatch => BLOCKED plutôt qu'UNKNOWN PASS.
- Source modifiée pendant inférence, cancellation tardive, OOM : preview ou réponse STALE, SHA initial intact, aucun double commit, récupération explicite.
- Comparaison same ROI qualité IA vs manuel, alpha float32 vs PNG publié : un score heuristique ne vaut pas certification géométrique ou coupe physique.
- Batch 12/24/50 avec per-item receipts : plafonds mémoire, idempotence, nombre total d'IDs et qualité conservée; CSV littéral sans formule/chemin active.
- **Preuves** : `DOC_SOURCE` et ports statiques vérifiés dans cette fiche ; `UNIT, WINDOWS_UI, RTX_GPU, DESIGN_SPACE, PHYSICAL_CUT = NOT_RUN` ici. Tests de vrais modèles et versions/licences nécessaires avant une affirmation « IA opérationnelle » dans l'application native.

**Suite :** `V35-COV-17E`, E01–E20 (bibliothèque, ergonomie Windows, Undo/recovery/QA et packaging), puis **une contre-expertise croisée des 80 décisions individuelles** avec les critères historiques, tickets, DoD et les 33 opportunités, sans annoncer que 80/80 sont codables du seul fait de ces tables. Priorité au travail réellement vérifiable, pas à la production de volume de texte.
