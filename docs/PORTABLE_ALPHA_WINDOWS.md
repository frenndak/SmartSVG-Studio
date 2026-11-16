# SmartSVG Studio V3.4 — Alpha portable Windows x64

**Prototype de test — pas une version de production, un installateur ni une validation Cricut.** Ce paquet part uniquement du code fusionné sur la révision indiquée dans `VERSION_ALPHA.txt`. Les PR ouvertes et la conception V3.5 ne sont pas incluses.

## Installation

1. Télécharger l'artefact **SmartSVG-Studio-V3.4-Alpha-Windows-x64** depuis l'onglet **Actions** du dépôt après une compilation GitHub réussie. L'archive GitHub Actions contient `SmartSVG-Studio-V3.4-Alpha-Windows-x64.zip` et `SHA256SUMS.txt`.
2. Extraire le ZIP interne dans un dossier classique, par exemple `C:\SmartSVG-Alpha\`, en conservant le répertoire `SmartSVG-Studio` et son contenu `_internal`.
3. Ouvrir `SmartSVG-Studio\SmartSVG-Studio.exe`. Il n'est pas nécessaire d'installer Python ou ComfyUI.
4. Essayer d'abord l'ouverture d'un projet **de test** et la création d'un projet depuis un **PNG de test**. Ne pas utiliser l'unique copie d'un projet important.

Ne pas exécuter l'EXE directement dans l'archive ZIP ; ne pas déplacer l'EXE hors de son dossier. Cette Alpha est non signée : Windows SmartScreen peut présenter un avertissement ; ne forcer l'exécution que si la provenance GitHub et le SHA-256 sont vérifiés.

## Fonctions et limites

- Application native Python/Tk, accueil, navigation, apparence, projets `.smartsvg`, création depuis un PNG, notes, inspection et outils d'Atelier disponibles selon le commit empaqueté.
- Aperçu de gabarits carte/boîte **théorique**, sans export garanti.
- **Non inclus/qualifiés :** conversion autonome image → SVG finie, détourage IA local autonome, parcours d'export complet vers Cricut Design Space, GPU/RTX 3070, import de production, découpe Explore 5, installateur/désinstallateur, mise à jour automatique et signature du binaire.
- Respecter les bornes PNG décrites dans `docs/NATIVE_PNG_CREATE_V34.md` du dépôt : PNG 8 bits non entrelacé, 12 Mio / 20 millions de pixels pour la création, 300 ou 450 DPI.
- Le bundle est construit et testé sur un runner GitHub Windows x64 ; **ce n'est pas un essai sur le PC utilisateur**.

## Signaler un problème

Fournir la version exacte (`VERSION_ALPHA.txt`), Windows 10/11 et sa version, l'action effectuée, le comportement observé et, si possible, une capture d'écran **sans données personnelles**. Conserver les fichiers `.smartsvg` et copies de secours. Ne jamais publier vos créations privées, modèles protégés, clés ou jetons dans le dépôt public.

## Reproduire / vérifier la compilation

Workflow : `.github/workflows/portable-alpha-windows.yml` — Python 3.11 x64, PyInstaller 6.16.0, NumPy 2.4.6, Pillow 13.0.0 et `tools/build_portable_windows.ps1`. Le script :

- Crée une distribution PyInstaller **onedir/windowed** à partir de `engine/standalone_desktop_v34.py`, sans importer le `engine/__init__.py` historique ComfyUI.
- Teste le `--probe` du binaire compilé depuis un chemin isolé, avec espaces et accents, et teste qu'une fenêtre lancée reste active pendant l'intervalle de vérification.
- Produit un ZIP avec son SHA-256 pour vérifier l'intégrité des octets téléchargés.

Le contrôle d'intégrité de l'archive de développement et les tests du moteur sont indépendants de ce test de packaging. Le statut d'acceptation exige **la conclusion SUCCESS du workflow exact HEAD et un essai manuel du ZIP extrait**.

Une GitHub Actions `success` ne certifie ni intégralité des fonctions ni comportement de la Cricut. Cette version doit rester explicitement **Alpha** jusqu'à la recette utilisateur.
