# SmartSVG Studio — Candidat d'intégration UX/Cricut (27 octobre 2026)

**Statut : DRAFT de regroupement. Ne constitue ni une release installable finalisée, ni un MVP certifié, ni une validation matérielle.**

## Objectif du regroupement

Présenter **une seule PR candidate vers `main`** combinant les branches empilées, pour que GitHub teste le comportement sur la véritable cible de fusion plutôt que seulement sur les bases intermédiaires.

La chaîne comprend G1.3→G1.5, G2.1→G2.5, G2.6→G2.9, le précontrôle Basic Cut et la sécurité des SVG. Les alternatives historiques concurrentes #20/#23 ne sont **pas** incluses. Les fichiers de l'archive V21.15.2, les contrats source et la roadmap V3.2 restent protégés.

## Fonctionnalités candidates dans le même arbre

1. **Projets** : création, inspection, sauvegarde atomique, sauvegarde précédente récupérable, validation PNG/JPEG/WebP/ZIP, métadonnées de couleur et sécurité des chemins.
2. **Masques** : conservation byte-exacte float32 pleine résolution (G2.4), coexistence du projet et des sessions de coups de pinceau V21.6.
3. **Express** : profil, parcours guidé, états et contrôle du dernier traitement ; actions projet dans le même panneau.
4. **Inspection visuelle** : affichage des fragments suspects sur les sujets, sélection manuelle de silhouettes et cadrage dans l'éditeur sans retouche automatique.
5. **Préflight** : validation des SVG d'entrée, des chemins de contour et des exports Basic Cut ; export de sous-ensemble SVG sélectionné comme brouillon à vérifier.
6. **Récupération de crash** : copie locale bornée des traits V21.6, liée au hash image+masques, reprise après confirmation explicite et invalidation si la source change.

## Matrice GO / NO-GO d'intégration

| Porte | Condition | État au moment de rédaction |
| --- | --- | --- |
| C0 — Source/roadmap | ZIP historique, roadmap et IDs de nœuds inchangés | Vérifié par les CI de branches parentes ; à confirmer sur ce candidat |
| C1 — CI sur **main** | Fusion synthétique sans conflit ; tests G0 et CPU verts | **À exécuter sur la PR candidate** |
| C2 — Revue | Revue indépendante du diff consolidé, sécurité, permissions, stockage et mécanismes de récupération | **Non exécutée** |
| C3 — Runtime Windows | ComfyUI charge tous les nœuds, permissions de route et UI, CPU/GPU RTX 3070 vérifiés | **Non exécuté** |
| C4 — Design Space | SVG Basic Cut / PNG Print Then Cut importés avec dimensions mm exactes | **Non exécuté** |
| C5 — Explore 5 | Mesurer des découpes réelles 12 et 24 sujets, tolérance, petits fragments et matériaux | **Non exécuté** |
| C6 — Produit | Utilisateur novice accomplit création → inspection → retouche → sauvegarde → export sans intervention de développeur | **Non exécuté** |

**Interdit tant que C2–C6 échouent ou restent inconnus :** annoncer un fichier « prêt à découper », une découpe certifiée, l'IA réelle ou une expérience Express autonome de bout en bout.

## Résolution des divergences et limitations

- L'ancienne pile G1.4/G2 ne contenait pas les derniers correctifs G1.3 ; la PR #35 a réintégré le validateur récent **sans supprimer** le stockage float32 G2.4.
- Les PR #25 et #31 sont portées par #36 ; leurs responsabilités sont distinctes du navigateur G2.7.
- Les PR #26–#28 sont portées par #37 ; le conflit sur `smartsvg_editor_v216.js` est résolu en conservant **à la fois** focus G2.6, sessions G2.3 et brouillon G2.8.
- La branche `main` possède **cinq commits d'avance sur l'ancêtre** de la pile, avec des changements `engine/smartsvg_core/project_contracts.py` et tests G1.2. C'est précisément pourquoi ce regroupement doit passer les CI **contre main**.
- GitHub Actions public et les mises à jour de gouvernance de la PR #30 restent un chantier distinct, non modifié ici. Le dépôt doit rester PUBLIC.

Les validations sur la base de branche ne remplacent pas l'approbation de fusion humaine prévue par `AGENTS.md`. **Ne fusionner que sur qualification explicite C0–C6**, ou documenter clairement une livraison de prototype limitée sans garantie Cricut.
