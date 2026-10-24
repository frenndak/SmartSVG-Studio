# SmartSVG V21.12.2 — Changelog

Base : archive d'installation **V21.12.1**, extraite et conservée comme référence de comparaison.

- **Goulot d'étranglement corrigé :** la génération des planches intermédiaires est évitée sur le nouvel Express. La génération finale après recalibration physique reste inchangée. Isolation des préférences par `ContextVar` pour ne pas contaminer les workflows historiques ou simultanés.
- **Découpes internes évitées :** fond blanc de découpe du sticker rendu plein entre ses contours externes, en conservant les PNG détourés natifs et leurs pixels d'origine. Sur les 24 Pokémon, quatre PNG imprimables ont nécessité un ajustement de l'alpha ; tous les SVG de contour extérieur sont restés identiques dans ce test.
- **Nouveau manifeste de livraison** non destructif `07_LIVRAISON_STICKERS_V21_12_2` : chemins relatifs au projet, SHA-256 des fichiers imprimables, de fabrication et SVG ; signaux d'alerte explicites.
- **Nouvel ID** `SmartSVGAutoExpressV21122`, mêmes contrôles et ports. Les anciens ID restent enregistrés. L'interface de suivi simple reconnaît également le nouvel ID.
- **Workflows** de démarrage V21.12.2 réédités. Aucun nouveau réglage Express obligatoire.
- **Tests** de non-régression ancien/nouveau PNG, SVG et planches ; contrôle de contexte ; défense contre liens symboliques / fichiers manquants ; trous internes du Print Then Cut ; test complet de 24 sujets ; contrôle de l'archive après extraction.

## Limites restantes

L'IA locale réelle, la RTX 3070 8 Go, le frontend ComfyUI du PC utilisateur et la découpe Cricut Explore 5 sont encore non testés physiquement. La vectorisation SVG multicouche des couleurs, le placement automatique sur papier et la reconnaissance du sujet voulu sont des chantiers ultérieurs, pas des fonctionnalités validées ici.
