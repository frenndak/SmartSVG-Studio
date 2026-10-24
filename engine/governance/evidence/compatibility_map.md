# G1.1 — Carte de compatibilité (pré-inventaire, aucune migration)

- Workflows présents : **186** ; JSON analysés : **186**.
- IDs SmartSVG enregistrés : **98**.
- Types inconnus : aucun dans les graphes analysés.
- Graphes identiques : 1 groupe(s).
- Anomalies statiques : 0 workflow(s)/ID(s) signalés.

## Politique de compatibilité

1. Les anciens IDs restent inchangés ; aucune substitution automatique de nœud.
2. « Candidat Express » et « historique » sont des étiquettes heuristiques, pas des garanties de bon fonctionnement.
3. Un graphe JSON analysé n’est **pas** un graphe chargé dans ComfyUI.
4. Les nœuds LoadImage, PreviewImage et InvertMask sont les types natifs autorisés par cette analyse.
5. L’ouverture effective dans ComfyUI et les sorties CNC/Cricut nécessitent des essais sur PC cible.
6. Aucune migration, aucune suppression, aucune modification des workflows sources.

## Décision

Pré-inventaire réalisé. G1.1 complet reste conditionné à la validation G0 et au chargement réel des workflows.
