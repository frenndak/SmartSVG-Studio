# SmartSVG — Backlog d'exécution évolutif

Document de suivi non figé. La référence contractuelle reste `docs/ROADMAP_MASTER_v3_2.md` (ne pas modifier son SHA). Les tickets ci-dessous sont des **propositions**, non des fonctionnalités livrées.

## Prochaines portes de validation

| Lot | Priorité | Critère d'entrée | Critère de sortie |
| --- | --- | --- | --- |
| CI-01 | P0 | PR #30 encore ouverte | Précontrôle public réussi sur HEAD exact, revue puis intégration contrôlée ; cron observé sur `main` avant de déclarer le calendrier actif |
| G1-01 | P0 | PR racines #13/#14 et dépendances vérifiées | Tests ciblés de sécurité et contrats, CI exacte, revue indépendante, intégration dans l'ordre d'ascendance |
| G2-01 | P0 | G1 réellement intégré | Sauvegarde et réouverture `.smartsvg` sans perte de source, masques ni retouches ; test de fichier corrompu |
| CUT-01 | P0 | Modes d'export séparés | PNG Print Then Cut, SVG Basic Cut et SVG éditable clairement distingués ; chemins fermés, unités mm et absence de doubles coupes vérifiés |
| SHEET-01 | P1 | Contrat CUT-01 validé | Planche de 12/24 éléments avec modes contour individuel, cadres rectangulaires et coupe extérieure ; contrôle des marges et collisions |
| UX-01 | P1 | Parcours Express disponible | Importer, inspecter, corriger, prévisualiser la coupe et exporter sans ouvrir le graphe ComfyUI ; clavier et erreurs testés |
| AI-01 | P1 | Fournisseur local et environnement documentés | Repli sûr en cas de mémoire GPU insuffisante ; tests L2 sur matériel réel avant toute promesse d'inférence |
| HW-01 | P1 | Fichiers de recette et version Design Space identifiés | Import réel et essais Cricut Explore 5 documentés par format/matériau ; aucune certification par CI seule |

## Règles pour le producteur automatique

1. Lire les PR ouvertes et leurs BASE/HEAD avant de sélectionner **un seul** micro-lot.
2. Ne pas confondre succès de la PR fille et intégration de ses parents ; choisir une seule des variantes concurrentes.
3. Écrire les tests négatifs pertinents pour le lot : archive malveillante, SVG/XML non sûr, collision de planche, dimension invalide ou perte de masque selon le périmètre.
4. Créer une PR ou enrichir une PR existante ; enregistrer SHA et CI, puis faire une contre-expertise ciblée.
5. Séparer L1 tests logiciels, L2 ComfyUI/IA réelle et L3 fabrication Cricut. Les niveaux L2/L3 ne bloquent pas les PR purement logicielles qui ne revendiquent pas ces résultats.
6. Ne pas fusionner sans revue autorisée, ne pas exposer d'assets privés, ne pas activer de dépenses API par défaut.
