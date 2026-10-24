# SmartSVG Studio V21.4 — refonte structurelle progressive

## Résumé

V21.4 introduit des frontières de modules et un contrat d'entrée vérifié, **sans déplacer ni réécrire brutalement** les anciens moteurs d'image. Cette prudence garantit que les projets Cricut et les workflows existants restent fonctionnels. Le travail structurel continue en V21.5 et au-delà.

## Carte des modules

```
ComfyUI __init__.py
    └── node_v214.py (façade publique / compatibilité)
        ├── smartsvg_core/contracts.py  ← validation indépendante de ComfyUI
        ├── smartsvg_core/reporting.py  ← résumé court, provenance explicite
        ├── smartsvg_ai/hardware.py     ← diagnostic léger, sans inférence
        ├── smartsvg_cricut/inspection.py ← contrôles physiques non destructifs
        │    └── smartsvg_vector/metadata.py ← SVG XML borné sans DTD
        ├── smartsvg_compat/registry.py ← anciens IDs garantis
        └── node_v2132.py et moteurs historiques inchangés
```

Les sous-dossiers `smartsvg_core`, `smartsvg_ai`, `smartsvg_vector`, `smartsvg_cricut` et `smartsvg_compat` constituent un **socle de migration**, pas la réécriture complète des moteurs anciens. Ils n'ajoutent aucun modèle IA ni connexion réseau.

## Garanties livrées

- `SmartSVGExpressV214`, `SmartSVGInstancesV214` et `SmartSVGDiagnosticV214` sont les trois nouveaux nœuds conseillés. Les identifiants historiques sont enregistrés sans être réassignés.
- Les ports d'entrée/sortie sont identiques à ceux de V21.3.2 ; seuls les catégories, noms et résumés nouveaux changent.
- Les contrats rejettent les résolutions non prévues et les largeurs non finies **avant tout accès GPU ou écriture de fichiers**.
- Les modules centraux sont importables sans PyTorch et sans poids IA (l'entrée ComfyUI historique reste évidemment tributaire des dépendances qu'elle utilisait déjà).
- Le résumé sépare `masques externes`, `IA interne demandée` et `aucune IA demandée`, **sans prétendre qu'une demande d'inférence prouve un résultat**.
- Les vérificateurs SVG rejettent les entités et les liens symboliques ; le précontrôle des dimensions est informatif, pas une attestation Cricut.
- Les tests comparent les PNG/SVG produits par deux générations de nœuds, sur la même entrée.
- Le vérificateur V21.4 compare les SHA-256 des fichiers historiques à ceux du manifeste V21.3.2. Seul l'ancien `__init__.py` est remplacé pour exposer les nouveaux nœuds.

## Travaux volontairement reportés

1. Migration progressive des moteurs réels dans les nouveaux packages, avec dépendances explicites et tests de performance.
2. Réduction *effective* du nombre de nœuds visibles via mécanisme compatible avec les versions de ComfyUI ; les  anciens restent encore présents en catégorie `Ancien`.
3. Éditeur graphique de régions/masques dans ComfyUI (V21.5–V21.6).
4. Tests GPU RTX 3070 (8 Gio) avec poids Florence-2/SAM2/BiRefNet réels et découpe physique sur Cricut.

## Installation

Sauvegarder le dossier SmartSVG précédent, ne conserver **qu'un seul** dossier SmartSVG actif dans `custom_nodes`, installer le dossier de V21.4 et redémarrer ComfyUI.

Commencer par le workflow `...V21_4_00_Diagnostic.json`, puis `...V21_4_01_Express_Simple.json`. Les autres six workflows reprennent les profils de V21.3.2.

## Vérifications

`python audit_structure_v214.py --json`

`python verify_package_v214.py --integrity-only`

`python verify_package_v214.py --suite 1` (puis 2, 3, 4).
