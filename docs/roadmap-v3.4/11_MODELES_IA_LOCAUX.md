# SmartSVG Studio V3.4 — Lot 11 : catalogue IA local, licences, téléchargements, budgets et benchmarks

**DRAFT DE SPÉCIFICATION — 29 octobre 2026.** V3.3 ACTIVE ; aucun modèle téléchargé/installé, aucune inférence RTX 3070, aucune validation Windows, Design Space ou physique. Issue #72 ; PR draft #73. Référence `main` : `fdbda304beb77d97340a8be4dd5c5e9cefde15f4` ; HEAD documentaire avant lot : `6cabc78b987b52969c22acf73d2fa387c28c8897`. Les chemins de code et de tests ci-dessous sont **futurs**, pas des fichiers créés.

## 1. Besoin, héritage et réalité lue

**Besoin :** l'utilisateur doit pouvoir réaliser « 12 escargots → stickers » et « boîte carton → Score + Basic Cut » **sans aucun modèle IA**, puis installer *volontairement* un modèle local pour une tâche précise (comprendre une image, corriger un masque, augmenter une résolution) sans transfert d'images privées, exécution de code tiers non approuvé, dépendance ComfyUI ni épuisement de 8 Go de VRAM. Il doit savoir exactement ce qu'il installe, pourquoi, combien cela coûte en espace et ce qui reste non vérifié.

**État du code sur main :** `engine/smartsvg_ai/provider_v2112.py` est un adaptateur ComfyUI RMBG/SAM2 ; `available()` inspecte des signatures sans prouver les poids, l'inférence ou la licence ; l'appel peut déclencher un téléchargement par des nœuds tiers. `auto_masks_v2111.py` propose des masques conservateurs et borne à 32/5 MP ; `mask_snapshot_g24.py` borne à 8 M float32. Aucun gestionnaire natif de modèles vérifié, ni catalogue avec hash/licence, ni preuve RTX 3070. `ETAT_ACTUEL_SMARTSVG.md` (27/10) reste non normatif ; maquette 12 escargots fictive.

**Héritage direct (sans supprimer les 141 exigences) :** S-003/005/006/007/014/018/022/027/042/046/050/053/058/062/067/070/073/074/080/084/093/095/096 ; R33-003/004/006/007/011/012/017/018/024/025/026/030/031/034/036/037/039 ; V34-017/020/024/025/032/039/050/054/059/063/064/068..077. La matrice inverse globale 141→V34→tests n'est **pas** encore achevée ; `HERITAGE_INDEX.md` reste un index, non une preuve de qualification.

**Hors périmètre de ce lot :** entraîner des modèles, télécharger des poids, choisir définitivement un modèle « meilleur », promettre la compatibilité CUDA/ONNX sur Windows, réaliser l'upscale (lot 12), certifier l'Explore 5, imposer un LLM ou livrer un installateur. L'IA propose des masques/intents ; seuls les moteurs déterministes et le CommandPort valident les géométries et mutations.

## 2. Contre-expertise du lot 10 et ADR-034-14 proposée

**Correction conceptuelle :** `mode=RULES_FIRST` et `ai_consent=NONE` dans `AnalysisRequest` ne suffisent pas à garantir le *zéro réseau* si le fournisseur legacy est appelé : les nœuds peuvent télécharger à l'exécution. Une proposition de modèle ne constitue ni un consentement de téléchargement ni une autorisation d'inférence. Le fournisseur natif reçoit **un handle de modèle déjà installé et qualifié**, jamais un repo ID ou URL libre. `max_concurrent_gpu_jobs=1` n'est pas une preuve d'absence d'OOM ; il faut un budget de ressources et un circuit de reprise. Les masques ROI du lot 10 ne sont persistés qu'après validation V2 et receipt ; aucun chargement IA ne change le SHA projet.

**ADR-034-14 — Catalogue fermé et inférence isolée, installation explicite par révision immuable :**
- A. Appeler ComfyUI-RMBG en direct : réutilisation immédiate mais téléchargements latents, contrats externes, difficulté de provenance ; **adaptateur legacy opt-in uniquement**, jamais backend par défaut.
- B. Runtime natif PyTorch, poids `safetensors` et code **local audité/épinglé** : meilleure réutilisation des modèles officiels, mais distribution Windows/CUDA volumineuse et risques `trust_remote_code` ; **premier prototype recommandé**, non choix final.
- C. ONNX Runtime avec modèles exportés et vérifiés : déploiement potentiellement plus léger, mais conversion, précision, opérateurs et post-traitement variables ; **prototype concurrent** sur même corpus et mêmes versions, pas promesse de parité.
- D. Un moteur IA universel/LLM toujours chargé : mémoire et maintenance excessives ; **REJET comme socle P0**.
- E. Règles/manuel sans modèle : **chemin P0 obligatoire**, même hors ligne et sans GPU.

**Gate ADR :** comparer B/C sur qualité des masques, temps p50/p95, pic RAM/VRAM, latence de chargement, taille installée, surface d'attaque, packaging Windows, fidélité ROI/float32, crash/reprise et licence **par checkpoint exact**. Si aucun candidat ne passe, garder E et l'adaptateur A explicitement marqué expérimental. Aucune décision finale avant prototype.

## 3. Catalogue daté des candidats — vérification documentaire du 29/10/2026

Les liens renvoient aux **éditeurs/auteurs officiels**. `MIT/Apache/BSD` est une **déclaration du dépôt à cette date**, pas une vérification juridique complète des poids, dépendances, données ou redistributions. Aucun SHA-256 de fichier, taille de téléchargement précise, VRAM mesurée ou version Windows n'a été relevé : champs **PIN_REQUIRED/UNMEASURED** et téléchargement **BLOCKED** jusqu'au manifeste exact. La révision doit être un commit complet et les hashes doivent couvrir chaque fichier (poids, configs, code approuvé). Ne pas utiliser `main` comme version installable.

| Besoin | Candidat précis / source officielle | Licence constatée / commerce | Risques et décision de conception |
|---|---|---|---|
| Compréhension, légende, détection/boîtes, OCR conditionnel | `microsoft/Florence-2-base` — https://huggingface.co/microsoft/Florence-2-base | Carte MIT ; usage commercial **potentiellement permis sous obligations MIT**, à vérifier pour révision + dépendances | Exemples officiels `trust_remote_code=True` ; **pas de chargement de code distant**. P1, seulement après audit du code local ou support natif Transformers prouvé. N'infère jamais dimensions physiques. |
| Masques guidés (points/boîtes), accessoires | `facebook/sam2.1-hiera-tiny` — https://huggingface.co/facebook/sam2.1-hiera-tiny ; code https://github.com/facebookresearch/sam2 | Carte Apache-2.0 ; code/checkpoints annoncés Apache-2.0, autres composants à inventorier | Priorité P1 d'essai pour masque guidé, pas segmentation sémantique garantie ; dépôt amont conseille WSL pour Windows, donc **compatibilité native non prouvée**. Checkpoint `sam2.1` distinct des anciens `sam2`. |
| Fond/alpha complexe | `ZhengPeng7/BiRefNet_lite` — https://huggingface.co/ZhengPeng7/BiRefNet_lite | Carte MIT ; obligations et provenance à auditer | P1 prototype avant modèle lourd ; exemple `trust_remote_code=True` à proscrire sans revue. Sortie masque sujet global, pas 12 identités garanties. |
| Fond/alpha complexe, alternative plus lourde | `ZhengPeng7/BiRefNet` — https://huggingface.co/ZhengPeng7/BiRefNet | Carte MIT ; révision exacte et dépendances à vérifier | P2 comparaison si lite insuffisant ; mémoire/qualité non mesurées, jamais chargé en même temps par défaut. |
| Fond/alpha BRIA | `briaai/RMBG-2.0` — https://huggingface.co/briaai/RMBG-2.0 ; `briaai/RMBG-1.4` — https://huggingface.co/briaai/RMBG-1.4 | RMBG-2.0 **non commercial sans accord**, carte/conditions BRIA ; RMBG-1.4 également non commercial sans accord | **REJET du catalogue recommandé pour usage commercial générique** ; affichage documentaire possible avec badge RESTRICTED et option de licence séparée explicitement prouvée. Pas d'API cloud comme contournement. |
| Upscale/restauration conditionnelle | `RealESRGAN_x4plus` du dépôt https://github.com/xinntao/Real-ESRGAN (releases officiels) | Code BSD-3-Clause ; **licence des poids et redistribution à clarifier pour l'asset exact** | P2, uniquement si un benchmark montre une amélioration sans artefacts ; upscale ne crée pas de détail fiable ni de dimension réelle. Pas de chargement implicite. |
| Petit LLM local | **Aucun recommandé au socle** | Non évalué | P2 différé : règles/formulaires/intentions d'abord, coût et risque à comparer sur corpus FR ; pas de dépendance à un modèle conversationnel. |

**Matrice d'admission pour chaque checkpoint :** `model_id`, `repo_url`, `repo_revision_sha`, `artifact_path`, `sha256`, `size_bytes`, `format`, `runtime_version`, `license_spdx_or_custom`, `license_text_sha256`, `commercial_use=ALLOWED/RESTRICTED/UNKNOWN`, `dependency_sbom`, `code_review_receipt`, `vram_peak_bytes`, `ram_peak_bytes`, `windows_test_receipt`. Pour les candidats ci-dessus, **SHA, octets, VRAM, RAM, version exacte et SBOM = INCONNUS** : ne pas substituer des nombres théoriques à des mesures. Une estimation pré-installation peut être calculée depuis les métadonnées officielles après épinglage et affichée « estimation non mesurée ». `size_bytes` ne doit pas être égal à une estimation de VRAM.

**Critères d'usage :** Florence-2 n'est pas nécessaire pour découper une boîte ; SAM2 ne remplace pas la revue du masque ; BiRefNet/RMBG n'est pas un détecteur d'accessoires ; Real-ESRGAN ne rend pas un SVG éditable. L'ordre des recommandations suit l'intention et l'état de la machine, jamais une incitation à installer tous les modèles.

## 4. UX novice/expert, états et événements

**Novice :** Importer → « Vous pouvez continuer sans IA » → sur photo complexe, proposition « Améliorer le détourage avec un modèle local (facultatif) » → fiche avec éditeur, licence, volume vérifié ou inconnu, statut de qualification et boutons `[Installer maintenant]` `[Plus tard]` `[Jamais pour cette suggestion]`. Le bouton Installer est **désactivé** tant que révision/hash/licence ne sont pas qualifiés. Après consentement explicite, téléchargement contrôlé, vérification, installation atomique et essai local ; une annulation ne touche pas le projet. Si échec, `[Revenir au détourage manuel]`.

**Expert :** catalogue versionné, révision, SBOM, hash, dossier, précision FP32/FP16/quantification, backend, GPU/RAM libres, pics mesurés, journaux expurgés, désinstallation, pin/rollback et comparaison CPU/ONNX/PyTorch. Choix explicite de chemin local ; import d'un poids existant soumis aux mêmes gates (aucun `torch.load` pickle non approuvé).

~~~text
[SmartSVG / Modèles IA] [Hors ligne ✓] [Aucun modèle requis]
┌ Besoin : améliorer le masque ──────────────────────────────────────────┐
│ Sans IA : [Continuer]                                                  │
│ BiRefNet_lite [Facultatif] [Licence MIT déclarée] [Non qualifié ici]   │
│ Taille : à vérifier · RTX 3070 : non testée · Révision : à épingler     │
│ [Détails et limites] [Installer maintenant : indisponible] [Plus tard]│
└───────────────────────────────────────────────────────────────────────┘
[Confidentialité : images locales] [Aucun téléchargement automatique]
~~~

~~~text
[Expert / Registry] model_id | revision | SHA256 | licence | SBOM | status
[Backend PyTorch/ONNX/Legacy] [VRAM budget dynamique] [Un seul modèle actif]
[Inspecter la provenance] [Tester localement] [Décharger] [Supprimer]
Download: WAITING_CONSENT→FETCHING→VERIFYING→STAGED→INSTALLED
Failures: LICENSE_BLOCKED / HASH_MISMATCH / NETWORK_DENIED / OOM
~~~

**États catalogue** : UNAVAILABLE, CANDIDATE, MANIFEST_REVIEWED, LICENSE_BLOCKED, CONSENT_REQUIRED, FETCHING, PAUSED, VERIFYING, STAGED, INSTALLED_UNTESTED, READY_QUALIFIED, CORRUPT, DISABLED, REMOVING, REMOVED. `READY_QUALIFIED` est lié au **couple modèle+révision+runtime+environnement** ; la présence d'un fichier ne suffit pas. `Jamais` signifie « ne plus proposer ce modèle pour cette intention », réversible dans Préférences, pas interdiction globale permanente. Une demande d'analyse peut revenir à `MANUAL` sans modifier le catalogue.

**Commandes** : `ListModels`, `InspectModel`, `RequestInstall`, `GrantNetworkConsent`, `PauseDownload`, `ResumeDownload`, `CancelDownload`, `VerifyStaged`, `ActivateModel`, `UnloadModel`, `RemoveModel`, `RunInference`, `AbortInference`. `RunInference` n'a **aucun** droit d'installation ; les événements `ModelInstallProposed/ConsentGranted/DownloadProgress/ArtifactVerified/ModelReady/ModelFailed/ModelUnloaded/InferenceProposed/InferenceFinished/InferenceOOM` sont distincts des receipts de mutation projet. Une recommandation du planificateur lot 09 ne peut invoquer `RequestInstall`.

## 5. Modèle de données et interfaces — proposition non exécutée

~~~json
{
  "contract": "v34.model-manifest/0.1-draft",
  "model_id": "ZhengPeng7/BiRefNet_lite",
  "purpose": ["BACKGROUND_MASK"],
  "source": {"url": "https://huggingface.co/ZhengPeng7/BiRefNet_lite", "revision_sha": null},
  "artifacts": [{"path": "model.safetensors", "sha256": null, "size_bytes": null}],
  "license": {"declared": "MIT", "text_sha256": null, "commercial_use": "UNKNOWN", "review_state": "PENDING"},
  "runtime": {"kind": "PYTORCH", "version": null, "custom_code_approved": false},
  "resources": {"vram_peak_bytes": null, "ram_peak_bytes": null, "windows_qualified": false},
  "install_state": "CANDIDATE",
  "download_allowed": false
}
~~~

~~~json
{
  "contract": "v34.inference-request/0.1-draft",
  "job_id": "vision-11-001",
  "source_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "project_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "purpose": "BACKGROUND_MASK",
  "model_handle": "local-verified-handle-01",
  "model_revision_sha": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "input_roi": {"x": 0, "y": 0, "width": 512, "height": 512},
  "network_allowed": false,
  "output_kind": "PROPOSAL_ONLY",
  "budget": {"max_active_gpu_jobs": 1, "max_runtime_ms": 120000, "allow_cpu_fallback": true}
}
~~~

**Schema strict futur :** propriétés inconnues rejetées ; ID et chemin normalisés ; URL autorisée uniquement au gestionnaire de téléchargement avec allowlist HTTPS/redirects contrôlés ; SHA-256 hex 64 caractères obligatoire **avant** `download_allowed=true` ; `revision_sha` Git commit complet, jamais `main`; `size_bytes` entier positif ; aucune taille cachée. Le second JSON est un **exemple de contrat de requête**, pas un handle réel ni un modèle effectivement vérifié. Les `budget` sont des plafonds de conception à mesurer et ajuster, pas des benchmarks.

**Ports :**
- `ModelCatalogPort.list/get/recommend(purpose, hardware, policy)` : lecture seule, retour de statuts et motifs.
- `ModelInstallPort.plan/consent/fetch/verify/commit/remove` : stockage séparé du projet, transaction atomique ; le fetch ne reçoit pas les pixels utilisateur.
- `ModelRuntimePort.probe/load/infer/unload` : processus isolé, timeout et budgets, aucune URL et aucun accès réseau ; sortie `MaskProposal` lot 10 avec provenance modèle.
- `ResourceBudgetPort.reserve/release/measure` : admission selon RAM/VRAM disponibles, concurrence, jobs CPU/GPU ; réservation annulable.
- `LegacyComfyAdapter` : explicitement opt-in, seulement si poids déjà disponibles et absence de téléchargement vérifiée ; sinon `UNAVAILABLE`. Aucun faux succès de `available()`.
- `AnalysisPort` lot 10 : seul consommateur de propositions ; `CommandPort` lot 06 reste unique autorité de mutation `.smartsvg`.

**Persistance :** manifeste de catalogue et receipts dans stockage applicatif local versionné ; poids dans dossier utilisateur configurable, **jamais** dans `.smartsvg` ni GitHub ; projet ne conserve que `model_id`, révision/hash, paramètres et statut de preuve de la proposition. Uninstall ne supprime pas l'original ni les projets ; les projets existants restent ouvrables en mode manuel. Undo projet n'annule pas une installation : installation/suppression a son propre journal et confirmations.

## 6. Algorithme déterministe, sécurité, reprise et performance

~~~text
SPECIFICATION ONLY — Install(request):
  if policy.offline or request.choice != INSTALL_NOW: return NO_NETWORK
  manifest = catalog.get_exact_pinned_revision(request.model_id)
  if not manifest.reviewed_license or not manifest.all_artifact_sha256:
      return INSTALL_BLOCKED
  if not user_grant.valid_for(manifest.digest, destination, session, expiry):
      return CONSENT_REQUIRED
  stage = sandbox_download_https_allowlisted(manifest, quotas, resumable_chunks)
  if cancel: delete_or_quarantine_stage(); return CANCELLED
  if sha256(stage.files) != manifest.hashes: quarantine(); return HASH_MISMATCH
  if not runtime_code_audited(manifest): return CODE_REVIEW_REQUIRED
  atomic_activate(stage); record_receipt(); return INSTALLED_UNTESTED

SPECIFICATION ONLY — Infer(request):
  assert local_handle_is_verified(request.model_handle)
  assert network_is_denied and project_snapshot_is_pinned
  if not reserve_resources(): return CPU_OR_MANUAL
  try:
      run_isolated_runtime_with_timeout()
      validate_roi_shape_finiteness_and_provenance()
      return PROPOSAL_ONLY
  except OOM:
      unload(); release_resources(); return RETRY_SMALLER_ROI_OR_MANUAL
  finally:
      release_resources()
~~~

**Sécurité :** aucune exécution de `trust_remote_code` ni `torch.load` pickle arbitraire ; privilégier safetensors et code de runtime déjà empaqueté/audité ; conversion ONNX réalisée en environnement de build isolé, artefact ONNX lui-même contrôlé et validé, pas de conversion à la volée de scripts distants. Défense contre traversal/symlink, ZIP/bombes, redirections hors allowlist, MIME trompeur, fichiers partiels, cache partagé, téléchargements concurrents, consentement rejoué, spoofing de hash et rollback vers version malveillante. Le SHA protège l'intégrité **relative à un manifeste de confiance**, pas l'authenticité de celui-ci ; manifestes signés/revus ou provenance mainteneur exigés. Pas de collecte télémétrique ni de pixels dans les logs ; secrets d'auth éventuels dans coffre système et jamais dans projet.

**Budget RTX 3070 8 Go :** 8 Go = capacité physique nominale, **pas** VRAM libre ; vérifier au lancement `available_bytes` et consommation autres processus. Admission GPU : modèle unique par défaut, chargement paresseux, unload avant switch, limite configurable de marge, ROI/tuiles bornés, cancellation/timeout, libération des buffers et fallback CPU/manuelle. Aucun seuil fixe `6 Go garantis` ; mesurer sur vrai Windows + versions de pilotes. OOM → job PARTIAL/FAILED, aucun commit, retour UI et option de ROI plus petit, CPU ou manuel. Ne jamais augmenter silencieusement les limites V21.11/G2.4.

**Téléchargement :** consentement par modèle/révision/volume/destination, réseau bloqué par défaut ; barre de progression, pause/reprise par chunks seulement si serveur supporte `Range`/ETag stable, sinon reprise depuis zéro **annoncée** ; quota disque vérifié avant et pendant, `fsync` et renommage atomique, hash final obligatoire, fichier corrompu mis en quarantaine et jamais activé. Révocation du consentement arrête la requête ; pas d'appel implicite au hub au simple `ListModels`. Mise à jour = nouvelle révision distincte, opt-in, ancien modèle conservé jusqu'à vérification et possibilité de rollback.

**Mesures futures (non observées) :** sur corpus C10 et C11, p50/p95 latence à froid/à chaud, CPU/GPU, pic RAM/VRAM par résolution/ROI, qualité IoU/bord et temps de correction, taille disque installée, absence d'appels réseau (instrumentation), taux OOM, temps d'unload, startup sans modèle, taux de succès Windows natif. Enregistrer GPU/pilote/CUDA/PyTorch/ONNX/ComfyUI, OS, SHA code, modèle révision+hash, corpus et script. Seuils chiffrés à fixer **après baseline**, sauf invariants binaires : 0 réseau sans consentement, 0 mutation projet lors de l'installation, 0 chargement non vérifié.

## 7. Scénarios complets et corpus à créer

**A — 12 escargots → stickers :** règles alpha/composants d'abord ; si 12 sujets acceptables, aucune installation. Sur un escargot ambigu, bouton « améliorer le masque » → comparer *sans IA* et *avec modèle déjà installé* sur la même ROI, résultat **proposition**, QA float32 lot 10, revue humaine, receipt d'acceptation, export PNG Print Then Cut par moteur aval ; **aucune** génération de repères Cricut ni pilotage Design Space. Si l'utilisateur refuse le téléchargement : continuer en manuel, aucune erreur bloquante du parcours.

**B — boîte carton Score+Cut :** création paramétrique/dimensions confirmées et géométrie déterministe ; catalogue IA = **aucun besoin**. Assignation SCORE/CUT et guide Design Space Attacher manuels, profil Explore 5 à qualifier lots 14–17. Un modèle IA ne décide ni épaisseur ni pression, et aucun test physique n'est réputé réussi.

**C — photo smartphone >5 MP :** EXIF/ICC et source immuable ; proposer ROI bornée et masque manuel, modèle local seulement sur demande ; éviter de charger photo entière + plusieurs modèles. **D — 50 sujets :** séquencer ROI/jobs et révisions, au plus un modèle GPU actif ; 50 propositions ne deviennent pas 50 masques V1. **E — fichier malveillant :** modèle/hash/URL/poids corrompu → refus, aucune exécution, pas de perte de projet.

**Fixtures futures :** C11-A zéro modèle, réseau interdit ; C11-B manifeste sans hash/licence ; C11-C téléchargement interrompu et serveur sans Range ; C11-D poids corrompus/hash faux ; C11-E code custom/PyTorch pickle ; C11-F deux jobs GPU et OOM injecté ; C11-G modèle supprimé alors qu'un projet le référence ; C11-H 12/24/50 ROI synthétiques ; C11-I photo EXIF/ICC ; C11-J versions PyTorch/ONNX/legacy dual-run ; C11-K licence BRIA non commerciale ; C11-L consentement révoqué/expiré et redirects ; C11-M contrôle UI clavier/FR ; C11-N archive V1 et V2 sans poids. Corpus synthétique libre de droits, jamais œuvres privées/Pokémon dans le dépôt public.

## 8. Tests d'acceptation à implémenter — TOUS NON_EXECUTE

| Test | Assertion future exacte | Preuve attendue |
|---|---|---|
| T-V34-11-01 | 0 modèle installé → Express et détourage manuel fonctionnent sans réseau | auto + Windows |
| T-V34-11-02 | `ListModels` ne télécharge ni n'exécute de code distant | auto sécurité |
| T-V34-11-03 | Recommandation liée à l'intention, 0 modèle proposé pour boîte Score+Cut | auto + UI |
| T-V34-11-04 | Modèle sans révision/hash/licence vérifiés → INSTALL_BLOCKED | auto sécurité |
| T-V34-11-05 | Licence RMBG-2.0 non commerciale → refus de badge commercial générique | auto + revue licence |
| T-V34-11-06 | Carte de modèle affiche auteur, limites, taille inconnue et preuve absente | UI |
| T-V34-11-07 | Refus/Plus tard/Jamais → 0 requête réseau, préférences réversibles | auto + UI |
| T-V34-11-08 | Consentement expiré/rejoué ou révision modifiée → CONSENT_REQUIRED | auto sécurité |
| T-V34-11-09 | Redirect hors allowlist, URL privée, traversal/symlink → refus | auto sécurité |
| T-V34-11-10 | Fichier sans hash ou hash erroné jamais activé, quarantaine explicite | auto sécurité |
| T-V34-11-11 | Téléchargement interrompu/repris ne produit aucun poids partiellement actif | auto + Windows |
| T-V34-11-12 | Serveur sans Range reprend à zéro avec message, sans corruption | auto |
| T-V34-11-13 | Disque plein/annulation → nettoyage, aucun projet modifié | auto + Windows |
| T-V34-11-14 | Double clic installer donne un seul receipt par modèle/révision | auto + Windows |
| T-V34-11-15 | `trust_remote_code`/pickle non approuvé → CODE_REVIEW_REQUIRED | auto sécurité |
| T-V34-11-16 | Import local de poids exige mêmes contrôles que téléchargement | auto sécurité |
| T-V34-11-17 | Inference reçoit handle local qualifié, jamais URL de repo | auto |
| T-V34-11-18 | Aucun modèle ne modifie `.smartsvg` sans CommandPort/receipt | auto |
| T-V34-11-19 | Changement de modèle libère ressources avant nouveau chargement | auto + GPU |
| T-V34-11-20 | Deux jobs GPU concurrents respectent ResourceBudgetPort | auto + GPU |
| T-V34-11-21 | OOM injecté → aucun commit, fallback CPU/manuel, UI réparable | auto + Windows + GPU |
| T-V34-11-22 | Réponse inférence tardive sur SHA projet modifié → STALE, 0 mutation | auto |
| T-V34-11-23 | Sortie masque NaN/ROI invalide → BLOCKED sans ID sujet | auto |
| T-V34-11-24 | 12/24/50 propositions : pas de troncature ni sérialisation V1 interdite | auto |
| T-V34-11-25 | Désinstallation modèle ne casse pas ouverture d'ancien projet | auto + Windows |
| T-V34-11-26 | Upgrade conserve ancienne révision jusqu'à vérification, rollback possible | auto + Windows |
| T-V34-11-27 | PyTorch/ONNX/legacy comparés sur même source/ROI et provenance distincte | auto + GPU futur |
| T-V34-11-28 | Benchmark p50/p95, RAM/VRAM, qualité et SHA complet publié sans PASS inventé | Windows + GPU |
| T-V34-11-29 | Clavier/lecteur d'écran : consentir, refuser, annuler, désinstaller | Windows UX |
| T-V34-11-30 | Cas escargots/boîte gardent PNG Print Then Cut et Score sémantique distincts ; preuves Design Space/physiques séparées | auto + DesignSpace/physique futurs |

**Preuve minimale :** commit SHA du code testé, fixture/hash, version de schéma et du catalogue, OS/driver/GPU, manifest+hash modèle, licence/notice, logs réseau expurgés, mesure et assertions. Tests `auto`, `Windows`, `GPU`, `DesignSpace` et `physique` indépendants ; une simulation ne vaut pas une découpe. **Aucun test ci-dessus n'a été exécuté au présent cycle.**

## 9. Tickets V34-078..086 (tous SPECIFIE, non implémentés)

**DoD commune FUTURE :** contrats versionnés et fermés, tests cités exécutés sur SHA exact, traces de refus et rollback, aucune régression V1/ComfyUI, sécurité réseau et licence, preuves par axe ; pas de promotion à QUALIFIE sur documentation seule.

| ID et priorité | Dépendances | Livrables/fichiers FUTURS, test, preuve et rollback |
|---|---|---|
| **V34-078 P0** Catalogue/politique/licences | S-005/022/042 ; R33-017/025/030 ; V34-024/050/059 | `engine/smartsvg_app/models/catalog.py`, `tests/models/test_catalog.py` ; T01..06 ; preuve auto/licence ; DoD aucun modèle non épinglé activable ; rollback catalogue lecture seule |
| **V34-079 P0** Consentement réseau et downloader transactionnel | S-003/042/053 ; R33-003/025/030 ; V34-025/032/063/078 | `engine/smartsvg_app/models/install.py`, `tests/models/test_download.py` ; T07..14 ; preuve auto sécurité/Windows ; DoD hash/quarantaine/receipt ; rollback mode offline |
| **V34-080 P0** Runtime isolé et interdiction de code distant | S-005/022/095 ; R33-017/024/034 ; V34-017/020/078/079 | `engine/smartsvg_app/models/runtime.py`, `tests/models/test_runtime_security.py` ; T15..18 ; preuve auto sécurité ; DoD aucun `trust_remote_code`/pickle non approuvé ; rollback manuel |
| **V34-081 P0** Ressources GPU/CPU, unload/OOM | S-018/027/038 ; R33-011/012/031 ; V34-039/070/074/080 | `engine/smartsvg_app/models/budget.py`, `tests/models/test_budget.py` ; T19..22 ; preuve auto/Windows/GPU ; DoD 0 mutation sur OOM et ressources libérées ; rollback CPU/manuel |
| **V34-082 P0** Intégration AnalysisPort + ROI/identités | S-007/014/023/028 ; R33-004/006/026 ; V34-068..074/080/081 | `engine/smartsvg_app/models/vision_adapter.py` ; T17/18/22..24 ; preuve auto + UI ; DoD propositions seulement et digest float32 ; rollback règles/manuelles |
| **V34-083 P1** Catalogue UI et gestion du cycle de vie | S-025/071/084 ; R33-017/019/030 ; V34-041/049/055/078/079 | `engine/web/js/v34_model_catalog.mjs` ; T06/07/25/26/29 ; preuve Windows UX ; DoD consentement visible, rollback et suppression sûrs ; rollback écran texte |
| **V34-084 P1** Spikes PyTorch/ONNX/legacy | S-005/027/046 ; R33-017/018/031 ; V34-017/020/074/080/081 | `tests/models/benchmark_backends.py`, `docs/roadmap-v3.4/benchmarks/11_backend_decision.md` ; T19/20/27/28 ; preuve Windows/RTX réelle ; DoD ADR révisée selon mesures ; rollback aucun choix final |
| **V34-085 P1** Corpus et E2E de non-régression | S-006/018/093/095 ; R33-018/034/039 ; V34-068..084 | `tests/fixtures/v34_models_synthetic/`, `tests/models/test_models_e2e.py` ; T01..30 ; preuve auto/Windows, axes externes distincts ; DoD fixtures autorisées et mapping test→ticket ; rollback tests de règles uniquement |
| **V34-086 P1** Vérification hors ligne et provenance avant usage (O-022/023) | S-042/067/084 ; R33-025/030/034 ; V34-024/078..082 | `engine/smartsvg_app/models/provenance_gate.py` ; T02/04/05/10/15/16/17 ; preuve auto sécurité/licence ; DoD aucune activation sur manifeste non fiable ; rollback refus explicite |

**Mapping inverse du lot :** T01..06→078 ; T07..14→079 ; T15..18→080 ; T19..22→081 ; T17/18/22..24→082 ; T06/07/25/26/29→083 ; T19/20/27/28→084 ; T01..30→085 ; T02/04/05/10/15/16/17→086. Chaque ticket remonte aux exigences S/R33 listées. Aucun ID historique ni ticket V34 antérieur n'est requalifié silencieusement.

## 10. Opportunités, risques, arbitrages et contrôle de complétude

**O-022 P1 retenue :** « comparer avant d'installer » avec carte de gains/limites *mesurés* sur une même ROI, et mode sans IA toujours visible ; raffine S-005/027 et V34-084, distinct de O-006 (comparateur ancien runtime). **O-023 P1 retenue :** « diagnostic de provenance du modèle déjà présent » avant toute inférence, détectant hash/licence/runtime obsolètes ; raffine S-042, R33-030 et V34-086, distinct de O-007 (diagnostic général de capacités). **O-024 REJET :** installation silencieuse du « meilleur modèle » lors de l'import ; incompatible avec consentement et licence, alternative = catalogue facultatif. Le détail et le score figurent dans `OPPORTUNITIES.md`.

**Risques ouverts P0 :** absence de manifestes épinglés et hash exacts ; ambiguïté de licence des assets Real-ESRGAN ; support Windows natif SAM2 ; code custom Florence/BiRefNet ; packaging `engine/__init__` ; downloader sécurisé non implémenté ; ROI V2 et writer non qualifiés ; RTX 3070 non testée ; exigences 141→tickets/tests non totalement reliées. **Décisions différées :** backend PyTorch/ONNX, checkpoint par tâche, quantification, seuils VRAM/latence/qualité, politique de redistribution, licence commerciale par poids ; aucune hypothèse ne devient une promesse.

**Contre-expertise inverse :** test→ticket→contrat→S/R33 vérifiable dans ce lot ; exigences héritées conservées mais mapping global à achever ; modèles = propositions et non dépendances P0 ; les quatre sorties PNG/SVG historiques restent distinctes ; aucun accès réseau sur simple import ; aucune preuve physique ou Windows inventée. Réviser si une licence change ou si le corpus montre un modèle moins bon que le manuel.

## 11. Sources externes officielles, consultées le 29 octobre 2026

- Microsoft Florence-2-base, carte MIT et exemples `trust_remote_code` : https://huggingface.co/microsoft/Florence-2-base
- Meta SAM2.1 Hiera Tiny, carte Apache-2.0 et usage points/boîtes : https://huggingface.co/facebook/sam2.1-hiera-tiny ; code, licences et notes Windows/WSL : https://github.com/facebookresearch/sam2
- Auteur BiRefNet et BiRefNet_lite, cartes MIT et code personnalisé : https://huggingface.co/ZhengPeng7/BiRefNet ; https://huggingface.co/ZhengPeng7/BiRefNet_lite
- BRIA RMBG-2.0, licence non commerciale/accord commercial requis : https://huggingface.co/briaai/RMBG-2.0 ; RMBG-1.4 : https://huggingface.co/briaai/RMBG-1.4
- Auteur Real-ESRGAN, dépôt BSD-3-Clause, assets à qualifier : https://github.com/xinntao/Real-ESRGAN
- Hugging Face Hub, révision de téléchargement explicite et cache : https://huggingface.co/docs/huggingface_hub/en/guides/download ; Transformers, chargement de poids safetensors vs pickle : https://huggingface.co/docs/transformers/en/models

**Sources GitHub SmartSVG relues :** issue #72, AGENTS.md, README.md, cinq documents V3.3 (MASTER/TRACEABILITY/COVERAGE/HERITAGE/AUDIT), ETAT_ACTUEL, PROGRESS, lots 09–10, HERITAGE_INDEX, OPPORTUNITIES, provider_v2112, auto_masks_v2111, mask_snapshot_g24, subject_identity_g33e. Les sources officielles donnent des licences **déclarées** ; aucune installation ni mesure n'a été faite.

**Prochain lot 12 :** moteur raster : alpha/fonds, nettoyage, anti-halo, upscale conditionnelle, formats d'impression, résolution et tests sur corpus, en réutilisant le catalogue IA **facultatif** et les contrats ROI sans les figer avant prototypes.
