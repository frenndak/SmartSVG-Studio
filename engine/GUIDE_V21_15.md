# SmartSVG Studio V21.15 — Lot G0 / pré-inventaire G1.1

**Socle :** V21.14.1, SHA-256 du ZIP source `b35ed631bcf6243bf0dd9b0af5b8e01dab1cfe38a5ef0f93e74f21a49df28835`.

## Fonctionnalités livrées

- Correction de deux identifiants **V19.2 Express/Expert** absents du registre chargé ; les fichiers JSON historiques ne changent pas.
- Restaurer le champ `ia_locale` sauvegardé dans l'ancien workflow **V19.2 Express** : valeur propagée à son moteur historique, aucune nouvelle exécution IA imposée.
- Inventaire automatisé de tous les JSON dans `example_workflows`, comparaison des IDs, ports requis, ports de sortie, nœuds manquants et liaisons.
- Corpus G0 : neuf références T documentées **sans diffuser les fichiers fournis**, deux fixtures négatives/positives R fournies avec leurs masques exacts.
- Grille de vérité terrain humaine et risques ; statut NO GO explicite tant que les masques T ne sont pas validés.
- Rapport `governance/evidence/` exportable CSV/JSON/Markdown ; tests de sécurité et de non-régression.

## Installer

1. Garder en lieu sûr le ZIP B0 V21.14.1 d'origine. Fermer ComfyUI.
2. Retirer **les autres versions du même custom node** de `ComfyUI/custom_nodes`. Ne pas superposer deux installations en parallèle.
3. Dézipper le dossier `ComfyUI-SmartSVG-Studio-V21.15` dans `ComfyUI/custom_nodes/`.
4. Redémarrer ComfyUI et retrouver les anciens nœuds SmartSVG et les deux V19.2 restaurés.
5. Les workflows V21.14.1 continuent de fonctionner à l'identique du point de vue des moteurs historiques. L'interface globale reste celle de ComfyUI.

## Vérification locale

Depuis le dossier du custom node :

```shell
python verify_package_v2115.py --integrity --targeted --javascript
python verify_package_v2115.py --full
```

Créer un nouvel inventaire **sans images privées** (G0.2 devient SOURCE_NOT_AVAILABLE dans le nouveau rapport, ce qui est normal) :

```shell
python tools/v2115_governance.py --output dossier_rapports
```

Ou, pour une validation locale avec les neuf photos/illustrations du projet dans un dossier privé (voir les noms attendus dans `governance/evidence/corpus_manifest.json`) :

```shell
python tools/v2115_governance.py --corpus dossier_images_prive --output dossier_rapports
```

Aucune image privée n'est recopiée dans les rapports. Conserver ces rapports séparément si les sources sont confidentielles. Les fichiers sources de test de l'utilisateur ne font **pas** partie du ZIP livré.

## Décision / limites

- **G0.1 : OK** (identité de la baseline vérifiée). **G0.2 : OK sur les neuf fichiers privés de référence**, identités et dimensions consignées.
- **G0.3 : EN ATTENTE** : neuf annotations de masques et deux évaluations humaines à finaliser ; seules les deux fixtures synthétiques ont une vérité déterministe.
- **G0.4 : registre initial produit**, sans mesure Windows/ComfyUI, GPU ou matériel.
- **G1.1 : pré-inventaire + correctif d'identifiants OK ; gate non validé** sans G0 complet, ouverture effective dans ComfyUI et tests d'exécution.
- **Aucune certification** d'import Design Space, de Print Then Cut, de SVG artistique ou de découpe sur Explore 5.
- Retour arrière : fermer ComfyUI, retirer le dossier V21.15 et restaurer le dossier issu du ZIP V21.14.1. Ne pas écraser les documents créés par les utilisateurs.
