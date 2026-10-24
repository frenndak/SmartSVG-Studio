# SmartSVG V19.8 — Rapport de développement

**Date : 22 octobre 2026**  
**Version : 19.8 bêta**

## Fonctionnalités ajoutées

- Appariement global de masques multi-modèles selon l'IoU, indépendant de l'ordre et du nombre d'objets (jusqu'à 16).
- Rejet des correspondances ambiguës ou trop éloignées, avec conservation du masque original.
- Carte d'incertitudes par pixel : désaccords entre masques alignés et chevauchements des masques de référence.
- Mode diagnostic qui conserve exactement les données sources ; deux modes de sélection à activer explicitement.
- Mode annoté permettant un choix selon l'IoU mesuré vis-à-vis d'une vérité terrain externe fournie par l'utilisateur.
- Trois nœuds ComfyUI V19.8 (Express, Expert et comparateur autonome), trois workflows V19.8.
- Sauvegarde atomique du rapport d'appariement séparément des sorties Cricut.
- Précontrôle mémoire avant conversion en float32 et tests d'exports réels.

## Résultats et statut

- Suite de vérification : **204 tests réussis** dans l'environnement de développement.
- Ancienne V19.7.1 : 183 tests ; V19.8 : 21 tests supplémentaires.
- **38 fichiers Python hérités présents dans la nouvelle archive**, sans modification hormis `__init__.py` destiné à enregistrer les nouveaux nœuds.
- Test de production photo avec deux masques alternatifs permutés : deux fichiers PNG Cricut identiques (SHA-256) à la V19.7.1 en mode diagnostic.
- Démonstration illustrée : données purement synthétiques, **aucun modèle IA exécuté**.

## Limites

- Aucune validation sur RTX 3070 8 Go ni dans Design Space ; aucun détourage automatique sur les photos réelles démontré ici.
- L'appariement par IoU mesure une similarité, pas une justesse sémantique. Deux mauvaises prédictions peuvent se ressembler.
- Aucun inpainting de parties cachées. Les modèles doivent produire des masques alignés sur la même image source.
- Les nouveaux modes de sélection ne doivent pas être traités comme une correction automatiquement garantie : mode diagnostic recommandé.
