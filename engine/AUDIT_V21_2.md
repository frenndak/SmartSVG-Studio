# V21.2 — Fiche QA par objet et parcours IA exploitable

**Nature** : ajout non destructif au mode V21.1. Les fichiers imprimables restent générés par le même moteur ; la V21.2 lit les fichiers publiables, en vérifie la cohérence et publie le rapport QA avec le projet **dans une unique transaction**.

## Améliorations concrètes

1. Même interface Express à cinq choix ; nouveau nœud `SmartSVGExpressV212`, ancien `SmartSVGExpressV211` conservé.
2. `05_CONTROLE_V21_2/APERÇU_GLOBAL.png` : côte à côte image source, détourage éventuel, PNG imprimable ; affiche la taille et le verdict.
3. `OBJET_XX_AVANT_APRES.png` pour inspecter chaque personnage séparément (jusqu'à 32 objets).
4. `CONTROLE_QUALITE.json` : dimensions PNG à DPI déclaré, dimensions SVG, fragmentation, trous, alpha doux, contact avec les bords et empreinte SHA-256.
5. Comparaison technique PNG/SVG : écart de taille supérieur à ~un pixel imprimé → `RISQUE_ELEVE` ; pas de score de confiance sémantique inventé.
6. Sécurités : chemin contenu dans projet, rejet des liens symboliques, limite mémoire avant décodage PNG, taille maximale SVG, nettoyage de transaction à l'échec.
7. `RAPPORT_V21_2.json` expose les chemins définitifs, sans fuite de chemins de staging ; les anciens rapports sont mis à jour pour les chemins finaux.
8. Un workflow d'**essai SAM2 local** permet à l'utilisateur de tester l'intégration, le repli et les diagnostics sur son propre GPU. Il ne télécharge ni n'exécute les poids en environnement CPU de validation.

## Régression

- L'identité binaire des trois sorties V21.1 (PNG Cricut, SVG et PNG détouré natif) est vérifiée pour un même masque.
- L'ancien test V21.1 et les moteurs précédents sont conservés.

## Risques qui restent ouverts

- SAM2 et BiRefNet n'ont pas été exécutés sur la machine de l'utilisateur : précision et VRAM non mesurées.
- Des chemins SVG sur des composants multiples peuvent amener Design Space à plusieurs découpes ; le rapport le signale.
- Une bonne géométrie ne prouve ni la bonne classe sémantique ni un bon contour dans les cheveux.
- Une page de 24 stickers suppose toujours une inspection à taille réelle et un essai physique.

## Retouche détectée pendant la validation des cinq images

Une carte rectangulaire remplit normalement son canevas : « touche le bord » ne doit **pas** être une alerte de découpe dangereuse pour ce mode. La version finale V21.2 neutralise cette fausse alerte et conserve le signal sur les vrais stickers à contour avec marge. Le nouveau test `test_rectangle_cut_edge_not_falsely_flagged` couvre la distinction.
