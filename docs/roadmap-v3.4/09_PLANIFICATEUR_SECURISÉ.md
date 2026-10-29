# SmartSVG Studio V3.4 — Lot 09 : planificateur sécurisé, catalogue d'actions et autorisation

**DRAFT de conception, 29 octobre 2026 — aucune implémentation ni exécution d'IA.** V3.3 demeure ACTIVE. Référence de base main : fdbda304beb77d97340a8be4dd5c5e9cefde15f4 ; branche documentaire : codex/docs-roadmap-v3-4-campaign ; issue #72, PR draft #73. Les fichiers futurs ci-dessous n'existent pas du seul fait de cette spécification.

## 1. Problème, réalité du code et contre-expertise du lot 08

**Besoin :** « Fais une planche de 12 stickers », « ajoute les plis Score à cette boîte » ou « prépare un dessin au stylo » doivent produire un **plan inspectable et non mutant**, validé par des moteurs déterministes, sans donner à un modèle IA un accès général au système, au projet, au réseau ou à la Cricut. Une réponse en JSON d'un LLM n'est jamais une autorisation.

**Code réellement consulté :** engine/smartsvg_core/contracts.py expose ExpressRequest (cinq catégories historiques, largeur 15–180 mm, DPI 300/450, modes IA) et des validations de widgets, **pas** de planificateur V3.4 ; engine/smartsvg_ai/provider_v2112.py expose des fournisseurs ComfyUI/RMBG et avertit d'un téléchargement de poids possible à l'inférence ; engine/smartsvg_core/project_workspace_g22.py est un noyau de projet historique, **pas** un writer V2 transactionnel. Les composants décrits aux lots 03/05/06/07/08 sont des **ports et contrats proposés**. La maquette Atelier avec 12 escargots ne constitue pas une segmentation réelle. AGENTS.md, README, les cinq références V3.3, ETAT_ACTUEL, issue #72 et PR #73 ont été relus.

**Revue critique du lot 08, corrections normatives proposées :**
1. La fonction « accept(proposal) » du pseudocode 08 **ne suffit pas** : l'acceptation doit viser un digest canonique de plan, un snapshot, une version de catalogue et une portée d'autorisation ; ne pas faire confiance à target_command_kind fourni par un modèle.
2. « Aperçu sans mutation » n'autorise pas un job GPU ou une écriture temporaire illimitée. Les budgets CPU/RAM/VRAM, l'absence de réseau et les ressources temporaires isolées sont des préconditions.
3. « Une confirmation utilisateur » ne vaut pas consentement général à plusieurs actions de natures différentes. Une confirmation groupée n'est permise que si chaque effet et ses paramètres sont visibles et si le groupe est transactionnel.
4. Un profil machine déclaré, même exact, ne devient pas un profil **qualifié**. Un plan peut enregistrer une intention SCORE sans conclure que Design Space appliquera automatiquement Score.
5. Le modèle ne décide jamais de l'ordre des opérations physiques Cricut ; les actions internes de préparation ne sont pas une séquence de pilotage machine.
6. Les anciennes enveloppes illustratives du lot 03 (« v34.command/0.1-draft ») sont **supplantées pour le planificateur** par le contrat plus récent « smartsvg-command/1-draft » du lot 06 ; ne pas publier deux writers ou deux protocoles concurrents. Cette clarification ne modifie pas les archives.

**Héritage, sans suppression :** S-003, S-008, S-013, S-022, S-023, S-024, S-029..032, S-053, S-067..084, S-093, S-095..096 ; R33-003, R33-005, R33-008, R33-011..012, R33-017..023, R33-025, R33-032..034, R33-039..040. Dépendances V34-011/012/014/015, V34-025..031, V34-032..040, V34-041..049, V34-050..058. **Statut de tous les tickets nouveaux : SPECIFIE**, pas IMPLEMENTE/RACCORDE/QUALIFIE/STABILISE.

## 2. ADR-034-12 : le modèle suggère ; le compilateur de plan déterministe décide

**Option A :** laisser un LLM produire directement des commandes et appeler des outils → **REJET** : injection, mutations non autorisées, permissions ambiguës, reproductibilité faible.

**Option B :** formulaire uniquement → **fallback P0** et solution nominale sans IA ; moins pratique pour une requête libre complexe.

**Option C (proposée) :** IntentResolver du lot 08 (règles ou modèle local opt-in) → IntentCandidates non fiables → PlanCompiler déterministe avec **catalogue fermé** → validation de schéma + références + contraintes + simulation → PlanPreview avec impact → consentement utilisateur lié au digest → CommandPort V34-032, seul writer. **Le même compilateur est utilisé sans IA.**

Le planificateur n'est **pas** un agent généraliste. Pas de Python/JS généré exécuté, shell, navigateur, HTTP, accès fichier arbitraire, accès au presse-papiers, achat, installation de modèle, commande Cricut, automatisation Design Space, ni appel de plugin tiers. Aucun texte OCR/SVG/EXIF, nom de fichier, prompt ou sortie modèle ne peut élever ses privilèges.

### 2.1 Frontières et consommateurs

~~~text
UI Express/Atelier/Fabrique → AssistantPort / IntentResolver (08)
                             ↓ IntentCandidates non fiables
PlanCompilerPort (09) → CatalogPort + SchemaValidator + ProjectSnapshotPort
                             ↓ PlanDraft immuable, source et profil épinglés
PlanSimulatorPort (09) → Subject/Vector/Fabrication/Export PREVIEW ports (03)
                             ↓ Findings + ImpactDiff + coût estimé, pas de commit
ConsentGatePort (09) ← clic utilisateur explicite sur résumé figé
                             ↓ AuthorisedPlan (usage unique, session liée)
CommandPort (06) → writer V2 (05) → receipt durable → SessionPresenter (07)
~~~

**Contrat d'interface :**
- PlanCompilerPort.compile(snapshot, candidates, capabilities, catalog_version) → PlanDraft | PlanningError ; lecture seule, validation et normalisation.
- CatalogPort.resolve(action_kind, version) → ActionSpec signé/embarqué avec schéma, portée, coût, capacité et policy ; jamais catalogue généré par modèle.
- PlanSimulatorPort.simulate(plan, immutable_snapshot, budget) → PreviewResult/Findings/ImpactDiff ; moteur spécialisé en lecture seule, isolation des temporaires, pas de receipt.
- ConsentGatePort.authorize(plan_digest, session_id, current_snapshot, user_click) → OneShotGrant | DENIED ; ne peut être appelé par l'IA.
- PlanExecutorPort.submit(authorized_plan) → receipt(s) via CommandPort ; un seul writer et une transaction logique par groupe. Ne contourne jamais CAS, prévol ni verrou.
- CapabilityPort (03/04) et FabricationPort (03/14/15) → états KNOWN_SUPPORTED / KNOWN_UNSUPPORTED / UNKNOWN, avec sources/profils ; aucune affirmation matérielle à partir de la suggestion.
- JobPort (06) reçoit uniquement une demande séparée explicitement consentie pour calcul coûteux ; le planificateur n'invoque pas un fournisseur IA qui télécharge à la volée.

**Consommateurs :** Express affiche les propositions et questions, Atelier affiche le diff d'objets/calques, Fabrique affiche le prévol et le guide ; SessionPresenter relit l'autorité après receipt. Aucun second DraftStore ou writer.

## 3. Catalogue fermé et sémantique des effets

Version proposée **v34.planner-catalog/0.1-draft**, à figer après prototypes. Les types sont des **actions métier internes**, pas des instructions Cricut.

| Action proposée par l'assistant | Classe | Préconditions / sortie | Autorisation |
|---|---|---|---|
| ConfirmIntent | MUTATION_PROJECT | intention explicite, contrat PNG_PRINT_THEN_CUT / SVG_BASIC_CUT / SVG_MULTILAYER_CUT / SVG_EDITABLE | confirmation ciblée |
| AcceptSubjectsBatch | MUTATION_PROJECT | liste d'IDs de propositions réellement présents, digest de chaque masque, tout ou rien | confirmation ciblée |
| SetObjectTransform | MUTATION_PROJECT | IDs existants, matrice bornée, unités mm et ancrage explicités | confirmation ciblée |
| AssignOperation | MUTATION_PROJECT | IDs de chemins existants, opération CUT/SCORE/DRAW/PRINT/FOIL **sémantique** ; état UNKNOWN possible | confirmation ciblée, prévol ultérieur |
| SetFabricationProfile | MUTATION_PROJECT | ID de profil versionné existant ou déclaration explicite UNKNOWN ; jamais qualification implicite | confirmation ciblée |
| CreateParametricTemplate | MUTATION_PROJECT | cotes/épaisseur/variantes nécessaires **saisies**, moteur géométrique déterministe | confirmation ciblée |
| PlanExport | READ_ONLY | contrat de sortie et destination **non écrite** ; aperçu, checklist et artefacts temporaires isolés | aucune écriture ; export réel séparé |

**Exclus du catalogue assistant :** ImportSource (geste explicite de sélection), EditMaskStrokeGroup (gestes pinceau), Undo/Redo, CommitCheckpoint, SaveProjectCopy, MigrateCopy, RequestJob/CancelJob, installation de modèle, suppression, changement de permissions, navigation externe. Ces commandes peuvent exister dans l'UI ou CommandPort, mais **ne sont pas invocables par un plan IA**. Toute action inconnue = PLANNER_ACTION_DENIED, sans fallback vers une commande générique.

**Important :** PRINT n'est pas équivalent à PNG Print Then Cut ; l'opération PRINT d'un plan de fabrication et le contrat d'export PNG sont distincts. SCORE est une intention sur une ligne de pli, pas une propriété SVG que Design Space est garanti de conserver. FOIL et DRAW restent conditionnés aux profils officiels et aux essais ultérieurs. La validation d'un brouillon n'autorise pas sa fabrication.

**Plan multi-actions :** au plus **8 étapes** dans cette première proposition, au plus **4 mutations**, ordre séquentiel strict, aucun DAG arbitraire, aucune boucle ni branchement dynamique. Une action AcceptSubjectsBatch **peut représenter logiquement** 12/24/50 sujets sans générer 50 commandes, **mais ne garantit pas que 50 masques soient matérialisables dans les formats V1 ou le moteur V21.11** : la disponibilité de propositions validées, leurs digests float32 et le support V2/ROI restent des préconditions explicites du lot 10. Sans celles-ci, bloquer l'acceptation avec un diagnostic plutôt que tronquer le lot. Un plan avec des étapes incompatibles est rejeté ; pas de réordonnancement implicite par LLM. Ces limites sont **budgets à éprouver**, non capacités garanties.

## 4. Contrats de données et validation stricte

### 4.1 Exemple PlanDraft valide de SPÉCIFICATION (pas exécuté)

~~~json
{
  "contract": "v34.plan/0.1-draft",
  "plan_id": "plan-local-0009",
  "catalog_version": "v34.planner-catalog/0.1-draft",
  "project_id": "demo-escargots",
  "base_project_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "base_logical_revision": 7,
  "source_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "profile_ref": null,
  "intent": "STICKERS_PRINT_THEN_CUT",
  "output_contract": "PNG_PRINT_THEN_CUT",
  "steps": [
    {
      "step_id": "step-01",
      "action_kind": "ConfirmIntent",
      "parameters": {"target_width_mm": 40, "requested_subjects": 12},
      "effect": "MUTATION_PROJECT",
      "origin": "RULE_MATCH"
    },
    {
      "step_id": "step-02",
      "action_kind": "PlanExport",
      "parameters": {"format": "PNG_PRINT_THEN_CUT", "paper": "A4"},
      "effect": "READ_ONLY",
      "origin": "RULE_MATCH"
    }
  ],
  "consent": {"network": false, "install_model": false, "write_project": false},
  "status": "DRAFT"
}
~~~

**Types et contraintes :** plan_id opaque unique par session, project_id référencé dans le snapshot, SHA hex minuscule 64 caractères, revision entier >=0, profile_ref ID+version ou null, intent et output_contract énumérés, steps 1..8, step_id unique, parameters objet typé par action (pas de clés inconnues), origin enum USER_EXPLICIT/RULE_MATCH/MODEL_SUGGESTION, effect **dérivé du catalogue** et jamais accepté comme autorité depuis le JSON. write_project=false dans un brouillon ; la validation ne transforme jamais ce champ en consentement. target_width_mm nombre fini >0, bornes déterminées par l'opération/profil ; le 15..180 mm d'ExpressRequest historique ne devient pas une règle universelle pour une boîte. Les dimensions absentes sont nulles/absentes et déclenchent NEEDS_INPUT, jamais inférées des pixels.

**JSON Schema recommandé :** Draft 2020-12, union discriminée par action_kind, required explicites, additionalProperties:false pour objets plats ; utiliser une fermeture correcte des propriétés composées (unevaluatedProperties:false avec tests du validateur) plutôt qu'une fermeture incorrecte de allOf. La validation de schéma **ne remplace pas** les invariants inter-champs, unités, provenance, permissions et résolution des IDs. JSON strict : rejeter clés dupliquées à la désérialisation, NaN/Infinity, profondeur excessive, chaînes surlongues, payload surdimensionné, Unicode de contrôle problématique et valeurs non normalisées. Ne pas traiter des propriétés inconnues comme des instructions d'extension.

### 4.2 Exemple de décision d'autorisation, créée par l'UI seulement

~~~json
{
  "contract": "v34.plan-approval/0.1-draft",
  "plan_id": "plan-local-0009",
  "plan_digest_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "catalog_version": "v34.planner-catalog/0.1-draft",
  "session_id": "session-local-01",
  "expected_project_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "expected_logical_revision": 7,
  "approved_step_ids": ["step-01"],
  "approval_origin": "EXPLICIT_UI_CLICK",
  "grant_scope": "ONE_SHOT_PROJECT_MUTATION",
  "expires_after_seconds": 120,
  "consumed": false
}
~~~

**Attention :** ce JSON est un **modèle de données illustratif**, pas un jeton forgeable. En implémentation, l'autorité du grant réside dans un magasin local interne inaccessible au modèle, lié à session + plan digest + snapshot + epoch + action list + version catalogue/profil, et n'est pas déterminée par un champ JSON submitted par le client. Le délai 120 s est une hypothèse de UX/sécurité à mesurer ; le clic doit être renouvelé si le plan ou la révision change. La comparaison utilise des octets canoniques versionnés, pas le SHA du ZIP. Un nonce consommé n'est pas réutilisable ; un retry de commande déjà commise passe par le receipt idempotent du lot 06, **pas** par un nouveau grant.

### 4.3 Codes et transitions

**États de plan :** DRAFT → NEEDS_INPUT / BLOCKED / PREVIEW_READY → AWAITING_CONFIRMATION → AUTHORIZED → SUBMITTED → COMMITTED (receipt durable), ou REJECTED/STALE/CANCELLED. Une simulation ne produit ni AUTHORIZED ni COMMITTED. Un export réel peut être EXPORTED_UNVERIFIED même si le plan de projet est COMMITTED ; la qualification Design Space et physique demeure séparée.

**Erreurs typées :** PLANNER_SCHEMA_INVALID, PLANNER_DUPLICATE_KEY, PLANNER_ACTION_DENIED, PLANNER_UNKNOWN_OBJECT, PLANNER_UNSUPPORTED_OPERATION, PLANNER_PROFILE_UNKNOWN, PLANNER_MISSING_DIMENSION, PLANNER_BUDGET_EXCEEDED, PLANNER_PROMPT_INJECTION_DATA, PLANNER_CONSENT_REQUIRED, PLANNER_APPROVAL_STALE, PLANNER_GRANT_REPLAY, PLANNER_CATALOG_CHANGED, PLANNER_SIMULATION_TIMEOUT, PLANNER_NETWORK_FORBIDDEN, PROJECT_RECOVERY_REQUIRED. Ne pas présenter ces codes comme existants dans le moteur actuel.

## 5. Algorithme déterministe, permissions et concurrence

~~~python
# PSEUDOCODE DE SPECIFICATION, NON EXECUTE
def compile_plan(intent_candidates, snapshot, catalog):
    bounded = parse_strict_json_and_validate_schema(intent_candidates)
    actions = resolve_only_known_catalog_actions(bounded, catalog)
    assert all(action.has_typed_parameters for action in actions)
    assert all(ref.exists_in(snapshot) for ref in action_refs(actions))
    assert no_untrusted_text_as_instruction(actions)
    return immutable_plan(snapshot.digest, snapshot.revision,
                          catalog.version, actions, provenance=bounded.origin)

def preview(plan, snapshot, budgets):
    if not matches_pins(plan, snapshot): return STALE
    return sandboxed_readonly_simulation(plan, budgets, no_network=True)

def authorize_and_submit(plan, preview, explicit_ui_click, current):
    if not explicit_ui_click: return CONSENT_REQUIRED
    if not matches_pins(plan, current) or not same_plan_digest(plan, preview):
        return PLANNER_APPROVAL_STALE
    if not catalog_and_profile_versions_match(plan, current):
        return PLANNER_CATALOG_CHANGED
    grant = mint_internal_one_shot_grant(plan, current.session)
    commands = deterministic_compile_to_v34_command_envelopes(plan, grant)
    return command_port.submit_atomic_group(commands, expected_sha=current.sha,
                                            expected_revision=current.revision,
                                            expected_epoch=current.epoch)
~~~

**Ordre de vérification :** limites de désérialisation → JSON Schema → allowlist → ID et SHA des ressources → permissions et consentements → contraintes métier/units → version catalogue et profil → simulation bornée → diff visible → clic explicite → revalidation CAS/epoch sous verrou → commit atomique → receipt → UI. La simulation ne peut pas produire de « preuve physique ». Si le plan est obsolète après simulation, **aucun auto-rebase** ; proposer comparer ou relancer. Si une transaction groupée n'est pas supportée par le writer V2, **désactiver la confirmation groupée** et exiger des confirmations unitaires transactionnelles, plutôt que simuler l'atomicité.

**Idempotence :** un command_id/epoch issu d'une confirmation n'est jamais renouvelé automatiquement pour un retry ; si crash après commit et avant réponse, interroger receipt ou état UNKNOWN_AFTER_INTERRUPTION, jamais relancer une nouvelle mutation. L'Undo inverse les mutations de projet, pas un fichier exporté ni une opération physique.

**Ressources :** compilation déterministe cible p95 < 100 ms sur 100 plans synthétiques courts, aperçu CPU p95 < 500 ms pour plans simples **à mesurer** ; aucune garantie pour vectorisation 50 sujets. Budget initial proposé 64 KiB JSON, 8 étapes, 4 mutations, profondeur JSON 16, max 200 IDs de sujet par batch ; à profiler et réduire si nécessaire. Un aperçu lourd est un job séparé opt-in, avec annulation, snapshot épinglé et limite mémoire. GPU OOM → annuler proposition IA et revenir règles/manuelle, sans toucher au projet. Aucun fournisseur legacy susceptible de télécharger des poids n'est appelé sans consentement et garantie de mode hors ligne.

## 6. UX novice, expert, refus et réparation

**Novice :**
~~~text
[SmartSVG — Escargots]  [Sans IA] [Projet non modifié]
Objectif proposé : 12 stickers imprimés — largeur 40 mm (saisie)
Étapes : 1. Confirmer intention [modifie projet]  2. Aperçu PNG [lecture seule]
Impact : 1 paramètre de projet ; 0 export ; 0 téléchargement
⚠ Zone A4 Print Then Cut non vérifiée ; contrôle dans Design Space nécessaire
[Voir avant/après] [Confirmer 1 changement] [Modifier] [Annuler]
~~~

**Expert :**
~~~text
[Plan v0.1] [Catalogue v0.1] [Snapshot r7] [Profil UNKNOWN]
step-01 ConfirmIntent / MUTATION_PROJECT / source RULE_MATCH
step-02 PlanExport / READ_ONLY / source RULE_MATCH
Diff logique : intent → STICKERS_PRINT_THEN_CUT ; target_width_mm → 40
Prévol : UNKNOWN A4_REGION_UNVERIFIED
[Inspecter paramètres typés] [Simuler sans mutation] [Refuser]
[Confirmer étapes mutantes]  (disabled si stale ou non validé)
~~~

**Refus utile :** « Je ne peux pas lancer une installation de modèle depuis une suggestion. Continuer sans IA / Ouvrir volontairement le catalogue » ; « Cette ligne de pli reste SCORE dans SmartSVG, mais Design Space doit être configuré manuellement » ; « Le projet a changé depuis l'aperçu : comparer ou recalculer ». Aucun message « succès de découpe » ou « opération Score transférée ».

**Accessibilité :** liste des changements lisible sans couleur, état du bouton et raison annoncés, focus conservé après refus, confirmation accessible clavier, pas de popup répétitive, historique des décisions expurgé facultatif. Préférences O-014 ne remplacent jamais l'approbation de dimensions, matériau, profil ou réseau.

## 7. Deux parcours de bout en bout et limites Cricut

**A — 12 escargots → stickers :** image locale et source immuable → IntentResolver suggère STICKERS_PRINT_THEN_CUT → largeur explicite 40 mm et nombre 12 → PlanCompiler ConfirmIntent + PlanExport → preview sans mutation et constat « sujets non encore acceptés » si masques absents → moteur SubjectPort propose, l'utilisateur valide les IDs réels → AcceptSubjectsBatch atomique distinct → Vector/Print engine prépare le PNG imprimable selon contrat ; aucun SVG de découpe présenté comme raster imprimé → prévol A4/zone admissible versionnée (UNKNOWN tant que non vérifiée) → export distinct après consentement → dans Design Space, import image imprimable et procédure officielle Print Then Cut. **Aucune marque capteur PDF inventée.**

**B — boîte carton → Score + Basic Cut :** demande de boîte 80×50×30 mm, préciser intérieur/extérieur et épaisseur/matière → CreateParametricTemplate déterministe (si moteur du lot 16 disponible, sinon BLOCKED sans faux patron) → AssignOperation CUT aux contours et SCORE aux plis, chemins distincts → profil Explore 5/outils/matière UNKNOWN si non vérifiés → prévol peut conserver le brouillon mais bloque toute déclaration « prêt à fabriquer » → export SVG et guide après validation → dans Design Space choisir Score sur les lignes, Attacher aux découpes et suivre les changements d'outil. **Le plan ne pilote pas Cricut et ne garantit pas le transfert automatique de SCORE.**

**Cas limites obligatoires :** dessin Pen+Cut et foil seulement si profil connu ; HTV miroir explicite et non inféré ; Smart Material sans tapis et tapis pour cartes seulement si combinaison machine/outils/matériaux versionnée ; pochoir à pont fragile bloqué au prévol ; dessin couleur « SVG éditable » vs « SVG Basic Cut » clarifié ; A4 Print Then Cut orienté selon guide Cricut versionné. Ce lot teste la **bonne décision du planificateur**, pas ces capacités physiques.

## 8. Corpus synthétique et tests de recette à implémenter (TOUS NON_EXECUTE)

**Fixtures futures, non présentes :** C09-A plan 12 escargots synthétiques sans masque ; C09-B 12 IDs validés + 1 ID absent ; C09-C boîte 80×50×30 mm, épaisseur inconnue ; C09-D SVG/EXIF/OCR hostile ; C09-E snapshot modifié entre preview/clic ; C09-F profil machine changé ; C09-G catalogue modifié ; C09-H JSON à clés dupliquées/NaN/profondeur 17 ; C09-I interruption commit et receipt ; C09-J OOM/job tardif ; C09-K 50 sujets en un batch ; C09-L tentatives d'installation/réseau/export ; C09-M contrôles UI clavier/lecteur d'écran. Toutes les illustrations sont synthétiques et libres de droits ; ne pas ajouter de Pokémon ou d'œuvre privée au dépôt public.

| Test | Assertion future précise | Axe de preuve |
|---|---|---|
| T-V34-09-01 | 0 IA installée : compilation d'une intention par règles, sans réseau ni modèle | auto |
| T-V34-09-02 | Action shell/HTTP/InstallModel inconnue → PLANNER_ACTION_DENIED, 0 effet | auto sécurité |
| T-V34-09-03 | Model suggestion contenant une action non autorisée ne traverse pas CatalogPort | auto sécurité |
| T-V34-09-04 | Les quatre contrats PNG_PRINT_THEN_CUT/SVG_BASIC_CUT/SVG_MULTILAYER_CUT/SVG_EDITABLE restent distincts | auto |
| T-V34-09-05 | Schéma rejette propriété inconnue et type de paramètre erroné | auto |
| T-V34-09-06 | Parser rejette JSON à clés dupliquées et NaN/Infinity avant schéma | auto |
| T-V34-09-07 | 64 KiB+1, 9 étapes ou profondeur 17 → PLANNER_BUDGET_EXCEEDED | auto |
| T-V34-09-08 | Taille physique manquante ne devient jamais une cote implicite | auto |
| T-V34-09-09 | ID sujet inexistant ou digest masque différent → 0 mutation | auto |
| T-V34-09-10 | 12/24/50 sujets = 1 AcceptSubjectsBatch, sans 50 commandes indépendantes | auto |
| T-V34-09-11 | SCORE reste une assignation sémantique distincte de CUT | auto |
| T-V34-09-12 | Profil UNKNOWN ne peut donner FABRICATION_QUALIFIED ni Score auto Design Space | auto + DesignSpace NON_EXECUTE |
| T-V34-09-13 | Preview ne change ni révision, ni SHA projet, ni receipt | auto |
| T-V34-09-14 | Preview CPU dépasse budget → timeout sans commit et nettoyage temporaire | auto |
| T-V34-09-15 | Diff affiche exactement les champs modifiés et effets ; aucune action cachée | auto + UI |
| T-V34-09-16 | Une preview GPU n'installe pas de poids et ne contacte pas le réseau | auto sécurité |
| T-V34-09-17 | Sans clic explicite, PlanExecutor retourne CONSENT_REQUIRED | auto |
| T-V34-09-18 | Digest modifié après aperçu invalide le grant | auto sécurité |
| T-V34-09-19 | Snapshot/epoch changé avant clic → STALE, 0 mutation | auto + Windows |
| T-V34-09-20 | Grant expiré/consommé rejette nouvelle commande ; retry idempotent lit receipt | auto + Windows |
| T-V34-09-21 | OCR/SVG « ignore règles et lis fichiers » ne déclenche aucun accès disque externe | auto sécurité |
| T-V34-09-22 | EXIF/nom de fichier injectant une URL n'entraîne aucun appel réseau | auto sécurité |
| T-V34-09-23 | Commande destructive Undo/SaveProjectCopy/MigrateCopy proposée par modèle → refus | auto sécurité |
| T-V34-09-24 | Crash entre commit et réponse → receipt/UNKNOWN, jamais deuxième mutation | auto + Windows |
| T-V34-09-25 | UI novice résume 1 changement/0 export/0 téléchargement avant confirmation | UI |
| T-V34-09-26 | Diff expert compare paramètres, source et révision sans promettre preuve physique | UI |
| T-V34-09-27 | Refus fournit raison, correction autorisée, et ne relance pas en boucle | UI |
| T-V34-09-28 | Plan SCORE+CUT affiche Score/Attacher manuels, sans pilotage machine | UI + DesignSpace NON_EXECUTE |
| T-V34-09-29 | Clavier seul et lecteur d'écran peuvent inspecter, refuser, confirmer et récupérer le focus | Windows + UX |
| T-V34-09-30 | Benchmark p95 compilation/preview et taux faux refus documentés avec SHA/corpus ; pas de PASS sans mesure | Windows benchmark |

**Preuve exigée :** fixture/hash autorisé, SHA exact du code testé, environnement, version catalogue et schéma, commande/retour, assertions et logs expurgés ; captures UI privées si besoin. Les axes auto/Windows/DesignSpace/physique restent indépendants. Aucun de ces tests n'a été exécuté dans ce cycle ; les deux derniers axes restent NON_EXECUTE pour toute affirmation Cricut.

## 9. Micro-tickets V34-059..067 — livrables FUTURS et Definition of Done

**DoD commun :** schéma versionné, assertions des tests nommés exécutées sur SHA réel, documentation des erreurs, tests de compatibilité V1/V2, aucune écriture hors CommandPort, preuve d'environnement et rollback explicite ; aucun ticket ne devient QUALIFIE sur seule revue documentaire.

| ID/priorité | Dépendances historiques et V34 | Livrables futurs, tests, preuve et rollback |
|---|---|---|
| **V34-059 P0** Catalogue fermé et classes d'effet | S-003, S-022, S-053 ; R33-003/025/034 ; V34-011/032/050..054 | futur : engine/smartsvg_app/planner/catalog.py, tests/planner/test_catalog.py ; T-V34-09-01..04 ; preuve auto sécurité ; DoD catalogue versionné et aucune action inconnue ; rollback assistant limité aux formulaires |
| **V34-060 P0** Parseur strict + schémas discriminés | S-003, S-023, S-095 ; R33-025/034 ; V34-025/051/054/059 | futur : engine/smartsvg_app/planner/schema.py, docs/roadmap-v3.4/schemas/planner.schema.json ; T-V34-09-05..08 ; preuve auto ; DoD clés dupliquées/NaN/tailles rejetées ; rollback désactiver plan JSON |
| **V34-061 P0** Résolution d'IDs et sémantique | S-023/028..032 ; R33-008/022/023 ; V34-012/025/029/051/059/060 | futur : engine/smartsvg_app/planner/resolve.py ; T-V34-09-09..12 ; preuve auto + DesignSpace future ; DoD aucun ID inventé ni SCORE transformé en CUT ; rollback plan lecture seule |
| **V34-062 P0** Simulation isolée + diff logique | S-008/026/071 ; R33-011/019 ; V34-015/032/036/053/061 | futur : engine/smartsvg_app/planner/simulator.py, tests/planner/test_preview.py ; T-V34-09-13..16 ; preuve auto + UI ; DoD 0 mutation/receipt, quotas et timeout ; rollback désactiver simulation lourde |
| **V34-063 P0** ConsentGate one-shot et CAS | S-003/024/053 ; R33-003/005/025/039 ; V34-025/032..034/037/053/062 | futur : engine/smartsvg_app/planner/consent.py, tests/planner/test_grants.py ; T-V34-09-17..20 ; preuve auto + Windows ; DoD digest/epoch/session vérifiés, grant non forgeable ; rollback confirmation unitaire sans assistant |
| **V34-064 P0** Exécution sûre et crash recovery | S-022/053/095..096 ; R33-005/012/034 ; V34-032..040/054/063 | futur : engine/smartsvg_app/planner/executor.py, tests/planner/test_planner_security.py ; T-V34-09-21..24 ; preuve auto sécurité + Windows crash ; DoD seul CommandPort écrit, aucune double mutation ; rollback commandes manuelles |
| **V34-065 P1** Diff avant validation (O-016) | S-071/075/083 ; R33-019/020 ; V34-041/049/056/062 | futur : engine/web/js/v34_plan_diff.mjs ; T-V34-09-15/25/26 ; preuve UI/UX ; DoD effets visibles, aucun succès fictif ; rollback résumé textuel |
| **V34-066 P1** Refus réparable et guide de transfert (O-017) | S-072/077/084 ; R33-020/022/034 ; V34-049/050/056/061 | futur : engine/smartsvg_app/planner/recovery_messages.py ; T-V34-09-27/28 ; preuve UI, DesignSpace future ; DoD action de correction non mutante ; rollback codes d'erreur explicites |
| **V34-067 P1** Corpus sécurité/UX et benchmark | S-093/095/096 ; R33-018/034/039 ; V34-058..066 | futur : tests/fixtures/v34_planner_synthetic/, tests/planner/test_planner_e2e.py ; T-V34-09-01..30 ; preuve auto/Windows/UX, DesignSpace et physique distinctes ; DoD couverture de tous les tests et faux refus mesurés ; rollback pas de déploiement planificateur |

**Mapping inverse minimal du lot :** tests 01..04→059 ; 05..08→060 ; 09..12→061 ; 13..16→062 ; 17..20→063 ; 21..24→064 ; 25..26→065 ; 27..28→066 ; 29..30→067. Les tickets 065/066 sont des raffinements UX, non des dépendances P0. Chaque ticket remonte aux exigences S/R33 listées ; l'index exhaustif 141→tickets/tests sera consolidé au lot 23/24, sans prétendre qu'il est déjà complet.

## 10. Découpage vertical, risques, opportunités et contre-expertise inverse

**Vertical slice A (P0) :** règles « stickers » → plan ConfirmIntent → preview → clic → receipt → retour Express ; 0 modèle installé, 0 réseau. **B (P0) :** objet géométrique existant → AssignOperation SCORE/CUT → prévol UNKNOWN → guide manuel, pas de « prêt à couper ». **C (P1) :** diff ergonomique et refus réparable ; ne pas retarder A/B. Le catalogue ne dépend pas d'un LLM ni d'une migration complète des modules IA.

**Opportunités nouvelles étudiées :**
- **O-016 P1 RETENU_POUR_SPEC :** aperçu d'impact *exact des mutations projet* avant approbation (diff de champs/IDs et estimation Undo), distinct de O-013 qui explique **pourquoi une suggestion existe**. UI « Voir les changements » ; gain = éviter les surprises ; effort moyen ; risque de diff incomplet ; recette T-V34-09-15/25/26 et V34-065.
- **O-017 P1 RETENU_POUR_SPEC :** refus réparateur avec prochaine action sûre (renseigner dimensions, choisir contrat, recharger snapshot), distinct de O-007 diagnostic de capacités et O-013 explication d'une suggestion. UI « Bloqué : épaisseur manquante » → « Saisir l'épaisseur » ; gain = réduire les impasses ; effort faible/moyen ; risque d'incitation à contourner prévol ; recette T-V34-09-27/28 et V34-066.
- **O-018 REJET :** assistant qui accepte et exécute automatiquement tous les plans en arrière-plan, sans confirmation. Gain de clics insuffisant face aux risques d'erreur matière/outil, données privées et mutation ; alternative = validation groupée transactionnelle explicite. Aucun ticket.

**Revue adversariale :** rejet de schémas ambigus, clés dupliquées, faux grants, injections via OCR/SVG/EXIF, double clic, changements SHA/epoch/catalogue/profil, job tardif/OOM, faux score Cricut, confusion entre brouillon et export, tailles implicites, duplication de 50 actions, changement d'état UI sans receipt, et surconception (catalogue réduit, pas de DAG générique). **Risque P0 restant :** writer V2 non implémenté, API de transaction groupée à prouver, graphe import autonome non exhaustif, prévol matériel non qualifié, validation des schémas cross-runtime et essais Windows. **Rollback :** désactiver planificateur, garder formulaire et commandes historiques, sans migration forcée ni modification de projets existants.

**Sources externes consultées le 29 octobre 2026 :** JSON Schema, Understanding JSON Schema Draft 2020-12, https://json-schema.org/UnderstandingJSONSchema.pdf (validation structurelle, fermeture de propriétés) ; OWASP, LLM Prompt Injection Prevention Cheat Sheet, https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html (moindre privilège, sortie modèle non fiable, contrôle aux frontières d'outils). Sources Cricut déjà datées dans le lot 08 : https://help.cricut.com/hc/en-us/articles/38613473602455-Cricut-Explore-5-How-to-use-the-Scoring-Tool et https://help.cricut.com/hc/en-us/articles/360009380514-How-to-use-Attach-in-Design-Space . Ces sources n'établissent ni test réel ni certification.

**Prochain lot 10 :** analyse visuelle multi-sujets/accessoires, détection, regroupement, qualité de masques, propositions partielles, fallback manuel, photos smartphone et dessins complexes. Réutiliser le planificateur proposé et les IDs de sujets V2 ; ne pas confondre détection et acceptation.
