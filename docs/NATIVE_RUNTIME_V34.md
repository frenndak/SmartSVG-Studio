# SmartSVG V3.4 — profil d'exécution du socle autonome

**État relu le 6 novembre 2026**, code après #119, référence de reprise [V3.4](roadmap-v3.4/EXECUTION_ET_INTEGRATION_2026_11_06.md). Ce profil distingue les dépendances du lecteur/Fabrique actuels de celles du moteur ComfyUI et des futurs traitements. Il ne constitue pas un installateur ni un verrou de distribution déjà qualifié.

## Socle actuellement raccordé

| Élément | Dépendance et preuve | Limite |
| --- | --- | --- |
| Entrée autonome | [standalone_desktop_v34.py](../engine/standalone_desktop_v34.py), imports directs `smartsvg_core`, bibliothèque standard Python | Ne pas lancer `engine` comme paquet : son initialiseur enregistre les nœuds historiques |
| Lecture projet, géométrie et file d'aperçu | Modules Python standard : ZIP/JSON/hash, calcul, futures/threads ; aucune installation pip requise pour ce sous-ensemble | Bornes d'archives/images conservées ; ce profil ne couvre pas vectorisation ou IA |
| Fenêtre et gabarits | `tkinter`/`ttk` et bibliothèques Tcl/Tk fournies avec l'installation Python ou par le système | Tkinter peut être absent d'une installation Python ; une session graphique est nécessaire pour ouvrir la fenêtre |
| Contrôle isolé | `python -I -S engine/standalone_desktop_v34.py --probe` | Ne charge pas Tk/ComfyUI/torch/aiohttp ; ne prouve pas l'affichage ni l'interception de tout trafic réseau |
| Preuve Windows observée | Python **3.11.9**, job `128064276580`, [workflow #119](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42267831651) ; smoke réel Tk PASS aux trois tailles | Version Tcl/Tk précise et SHA d'installateur non consignés : profil observé, pas environnement intégralement verrouillé |

Lancer depuis la racine du dépôt :

```bash
python engine/standalone_desktop_v34.py
python -I -S engine/standalone_desktop_v34.py --probe
```

Le fichier [engine/requirements.txt](../engine/requirements.txt) décrit les dépendances historiques ComfyUI/traitement (`numpy`, `Pillow`, `opencv-python`, versions minimales). **Ce n'est pas un manifeste d'installation du socle autonome.** Ses bornes ne sont pas modifiées : les anciens workflows conservent leur contrat. Ne pas installer tout le runtime legacy pour simplement utiliser le lecteur et les gabarits actuels.

## Rendre la future distribution reproductible

Ces travaux restent liés aux tickets V34-017/019/020/139/140 existants, avant toute revendication de package installable :

1. Fixer et consigner Python, architecture, provenance/SHA de distribution, versions Tcl/Tk et licences de l'environnement effectivement essayé ; vérifier un Windows propre. La version observée ci-dessus est une preuve datée, pas une recommandation permanente de version.
2. Relever les imports transitifs de chaque fonction réellement raccordée. NumPy/Pillow/OpenCV pourront devenir nécessaires aux traitements concernés ; l'accueil et le lecteur doivent garder leur chemin minimal. Les modèles IA et adaptateurs ComfyUI restent facultatifs.
3. Produire les contraintes/verrous et empreintes pour les plateformes prises en charge à partir de ces versions testées. Vérifier l'installation dans un environnement vierge, sans dépendances globales cachées ni téléchargement de modèle implicite ; ne pas inventer un lock universel depuis un seul runner.
4. Séparer code applicatif, préférences locales, projets, exports et modèles ; tester ouverture/création/sauvegarde/reprise au périmètre livré, puis mise à jour/rollback/désinstallation sans perte.
5. Archiver les preuves de démarrage hors ComfyUI, installation et hors ligne par interception ; conserver les contrôles matériels séparés. Un `pip freeze`, un import réussi ou le smoke Tk ne suffisent pas à qualifier l'installation complète.

Pour relever les versions sans ouverture de fenêtre :

```bash
python --version
python -c "import tkinter; print('Tk', tkinter.TkVersion, 'Tcl', tkinter.TclVersion); print('Tcl runtime', tkinter.Tcl().call('info', 'patchlevel'))"
```

Ces valeurs sont à joindre aux futures preuves ; la version de compilation Tk affichée ne remplace pas le relevé du runtime Tk complet dans une session graphique.
