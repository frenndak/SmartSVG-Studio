# V21.5 — Interface visuelle V1

- Ajout d'une extension navigateur **JavaScript** chargée via `WEB_DIRECTORY` et `app.registerExtension`.
- Ajout d'un widget DOM **non sérialisable**, ajouté uniquement à `SmartSVGExpressV215`, avec compteurs, étapes, avertissements, navigation des aperçus et copie du dossier.
- Backend `smartsvg_ui`: présentation JSON bornée, miniatures QA confinées au répertoire du projet et au dossier de sortie officiel ComfyUI.
- Aucun des anciens moteurs PNG/SVG/IA modifié ; nouveaux IDs ComfyUI V21.5 et 8 workflows.
- Mode dégradé si DOMWidget absent ou previews indisponibles : fonctionnement du moteur Python inchangé.
- Limites V21.5 : **pas d'éditeur de masques/contours**, **pas d'inférence GPU réelle**, **pas d'essai Cricut physique**.
