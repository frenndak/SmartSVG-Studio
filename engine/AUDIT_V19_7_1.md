# SmartSVG Studio V19.7.1 — Contre-expertise indépendante

Date de l'audit : 22 octobre 2026.

## Source et méthode

Base exacte : `ComfyUI_SmartSVG_Studio_V19_7_Installation.zip` fourni dans la conversation.
- Extraction dans un dossier vierge, `python verify_package.py` : 171 tests réussis avant modification.
- Test adversarial : simulation PyTorch CUDA dont `synchronize()` lève une exception ; en V19.7, le rapport déclarait l'étape `OK`, `mesure_gpu_reelle_observee=true`, sans consigner l'échec de synchronisation.
- Deuxième test adversarial : `mem_get_info()` échoue mais `memory_allocated`/`memory_reserved` fonctionnent ; la V19.7 effaçait ces résultats et déclarait CUDA indisponible.
- Corrections : résultat de synchronisation explicite, indépendance des champs mémoire, suivi des périphériques, RSS CPU facultatif, temps de sous-étapes approximatifs.
- Export Cricut et modèle SAM2 / Florence-2 inchangés.

## Résultats

Suite V19.7 initiale : 171/171. Suite finale étendue : vérifier `python verify_package.py` pour le chiffre actualisé et les détails de chaque test. Inclut un traitement photo réel avec masque **synthétique** et égalité SHA-256 des PNG destinés à Cricut, sans inférence IA.

## Problèmes non résolus et risques résiduels

- Impossible de prouver ici la précision des masques sur les vraies scènes (personnage et chopes, femme et cadeau) : aucune vraie inférence SAM2/Finegrain/FeyNoBg sur le GPU utilisateur.
- Les deux modèles ne s'exécutent pas automatiquement en parallèle dans ce comparateur : leurs masques doivent toujours être comparés sur le même repère.
- Le GPU RTX 3070 réel n'a pas été utilisé. `max_memory_allocated` reste un pic **historique de processus** : pas le coût isolé d'un modèle.
- `psutil` est facultatif et peut être absent. Ne pas forcer l'installation d'un module pour collecter la RAM.
- Les durées exclusives des étapes imbriquées sont des estimations basées sur le temps écoulé ; elles ne sont pas des durées CUDA kernels.
- L'import réel et la découpe de la Cricut ne sont pas testés.

## Recommandations pour la prochaine itération

1. Recueillir sur le PC cible les profils de SAM2, FeyNoBg et Finegrain **séparément**, à froid puis après initialisation.
2. Pour les deux photographies, annoter manuellement les objets de référence et comparer les IoU/Dice et la précision du contour sans rapporter le score heuristique comme une vérité terrain.
3. Vérifier Design Space : import, échelle, calque « Aplatir », contour extérieur et essais de coupe réels.
4. Réserver la sélection automatique d'un masque à un scénario où un critère de qualité vérifié est disponible.

## Référence PyTorch

- https://docs.pytorch.org/docs/stable/notes/cuda
- https://docs.pytorch.org/docs/stable/generated/torch.cuda.synchronize
