# Contre-expertise V19.9 → SmartSVG V20.0

Date : 22 octobre 2026

## Périmètre

Code et tests V19.9 repris depuis son ZIP installé. Reproduction **225/225 tests** avant modification. Vérification des contrats nœuds `SAM2Segment`, `AILab_Florence2`, `BiRefNetRMBG` par comparaison à leur documentation publique ComfyUI-RMBG ; les poids eux-mêmes n'ont pas été lancés.

## Défauts observés et correctifs

### A — Proposition de matting absorbant un objet voisin : risque élevé

Dans un scénario synthétique contenant deux objets proches, un fournisseur de matting non guidé retourne les deux silhouettes dans le recadrage du premier objet. V19.9 accepte cette proposition avec un **IoU ≈ 0,8505** avec l'objet cible. Cette mesure est élevée mais ne prouve pas l'appartenance des pixels ajoutés. V20.0 détecte **435 pixels d'empiétement** sur le cœur de l'autre masque, au-delà de sa marge de tolérance, et retourne `REFUSE_EMPIETEMENT_AUTRE_OBJET`. Les variantes rejetées ne remplacent jamais les PNG Cricut.

### B — Proposition hors région de référence : risque élevé

Un candidat peut ajouter une bordure entière de pixels dans un recadrage, avec une similarité toujours élevée. V20.0 vérifie l'apparition de premier plan sur les **bords internes** du recadrage qui ne sont pas déjà couverts par le masque original et refuse `REFUSE_FUITE_BORD_ROI`.

### C — Écriture partielle des aperçus QA : risque moyen

V19.9 publie plusieurs PNG et ensuite un JSON ; une panne au milieu laisse des diagnostics isolés sans rapport. V20.0 écrit d'abord sous un dossier temporaire interne au dossier QA, valide le JSON, puis **renomme le dossier entier**. Les fichiers provisoires sont supprimés si une écriture échoue. Aucun mécanisme ne garantit la durabilité sur une panne brutale du système ou du disque : seul le caractère atomique du renommage du dossier est garanti sous un système de fichiers compatible.

### D — Traçabilité du masque d'origine : risque moyen

L'ancien export QA utilisait le masque sélectionné comme référence lors d'une éventuelle adoption annotée. La nouvelle API garde et exporte le masque **avant traitement** et les propositions séparément, afin de rendre les comparaisons vérifiables.

### E — Repli ambigu si première IA absente : risque moyen

Après un échec d'orchestration sans masque externe, V19.9 pouvait repasser par une extraction de premier plan historique sans distinguer l'origine du masque. V20.0 bascule en `analyse_seule` sans IA historique, conservant l'image mais n'annonçant aucun nouveau masque sémantique.

### F — Diagnostic de l'environnement : nouveau garde-fou

Le nœud `SmartSVGEnvironmentV20` recherche les **bons identifiants techniques** dans le registre ComfyUI et montre la disponibilité CUDA sans lancer l'inférence ni télécharger les modèles. Cette vérification ne confirme pas la compatibilité réelle de chaque version RMBG ni la présence physique des poids.

## Validation

- **243/243 tests** : 225 hérités, **18 nouveaux** ; archive extraite dans un dossier vierge.
- Test adversarial avec V19.9 : proposition incorrecte acceptée ; V20 : rejet explicite.
- Test de candidate correcte et promotion supervisée : fonctionnalité conservée.
- Tests panne PNG, panne sérialisation JSON, sortie de répertoire QA par lien symbolique, dimensions erronées : pas de publication incomplète.
- Comparaison réelle du moteur d'export photo sur deux objets synthétiques : **2 PNG Cricut bit à bit identiques** entre V19.9 et V20 en mode diagnostic.
- Deux images réelles chargées en analyse seule : RGB conservé sans différence, aucun détourage non fondé.
- Moteurs historiques Python : **41 fichiers identiques (SHA-256)**. Le point d'entrée `__init__.py` change pour enregistrer V20.

## Risques non levés

1. **Pas de test CUDA sur RTX 3070** ni de test d'inférence de poids Florence-2/SAM2/BiRefNet ; toutes les simulations du modèle sont artificielles.
2. Les critères IoU et anti-empiétement sont des garanties partielles, **pas un modèle de compréhension des superpositions** : une main physiquement devant une chope peut partager un masque ; une marge trop prudente peut refuser une amélioration légitime.
3. La limite des modèles de matting génériques (Lucida, BiRefNet) sur plusieurs objets visibles dans le même recadrage demeure ; V20 choisit de refuser plutôt que risquer un mauvais masque.
4. Imports et découpes Cricut Design Space **non exécutés sur appareil physique**.
5. Les anciens modules continuent d'utiliser leurs conventions historiques, et les tests du moteur vectoriel ne garantissent pas une fidélité visuelle absolue sur toute illustration.

## Verdict

V20.0 = **bêta consolidée et contrôlée**, plus sûre que V19.9 pour examiner des alternatives de matting. Ce n'est ni une version de production certifiée Cricut ni une démonstration de la précision de l'IA sur des photos difficiles.
