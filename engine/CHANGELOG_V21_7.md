# Modifications SmartSVG V21.7

- Nouveau nœud `SmartSVGPrepareV217`, recadrage manuel en pourcentage et suppression prudente des bandes noires franches de captures (aucun recadrage si preuve insuffisante).
- Nouveau nœud `SmartSVGQualityV217`, contrôle CPU non destructif des composants, micro-îlots/trous, connexions étroites, bords et chevauchements ; rapport JSON explicite avec hypothèses de taille en millimètres.
- Aperçu QA borné à 1 024 px, copies limitées à 48 fichiers et durée de 72 h sous le dossier spécifique SmartSVG (nettoyage lors des exécutions suivantes). Une panne d'aperçu n'annule pas les masques vérifiés.
- Trois workflows exemples : capture manuelle, PNG transparent avec `InvertMask` et planche 12 sujets guidée par IA (modèles non fournis).
- Non-régression : identité des sorties `MASK` et `IMAGE` du nœud QA, compatibilité des classes anciennes et des workflows V21.6, pipeline synthétique 12 sujets jusqu'aux exports PNG/SVG.
- Périmètre volontairement limité : pas de modification des moteurs historiques, pas de nouvelles dépendances, pas d'inférence GPU revendiquée, pas de certification physique Cricut.
