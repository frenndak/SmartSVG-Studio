# G3.2 — Projets .smartsvg natifs dans l'Atelier Express

## Premier raccordement G2.2

L'Atelier Express plein écran propose maintenant **« Gérer mes projets .smartsvg »**. Sur la page servie par **ComfyUI local**, le clic importe les composants déjà existants `smartsvg_project_panel_g22.mjs` et `../../scripts/api.js` depuis la même origine et affiche le **vrai gestionnaire de projets G2.2**.

Fonctions accessibles depuis ce panneau :

- créer un projet nommé et une source PNG depuis un bouton volontaire ;
- ouvrir/inspecter une archive `.smartsvg` gérée dans le dossier de l'application (jamais un chemin disque arbitraire) ;
- enregistrer les notes avec contrôle du SHA256 de la révision, sans écraser silencieusement une édition concurrente ;
- examiner la santé du projet et restaurer son secours avec confirmation explicite et contrôle du hash de récupération ;
- consulter la source conservée, les masques float32 déclarés et le contrôle de contours déjà inclus dans G2.2/G2.7.

**Ce lot réutilise le gestionnaire existant, sans dupliquer une API de sauvegarde côté navigateur.** Les routes ne sont pas activées automatiquement par le simple affichage : le serveur G2.2 peut nécessiter `SMARTSVG_ENABLE_PROJECT_API=1` dans la configuration de l'installation.

## Attention aux formats

La page G3.0 accepte PNG, JPEG et WebP **uniquement pour affichage local de démonstration**. En revanche, **la création d'un projet G2.2 exige actuellement un PNG valide**. Elle ne réalise aucune conversion JPEG/WebP automatique. Le bouton gérant les projets le rappelle explicitement et dispose de **son propre sélecteur PNG**.

Le gestionnaire `project_workspace_g22.py` accepte uniquement **300 ou 450 ppp** : G3.2 a donc un sélecteur *Précision du projet* distinct, et **ne passe pas** les valeurs 150/600 ppp offertes par le sélecteur fictif de l'aperçu d'images. Le profil est choisi explicitement parmi les cinq constantes reconnues par G2.2. La largeur mm est reprise de la saisie de l'atelier (10–200 mm dans cette UI).

## Sécurité / fonctionnement

- Import dynamique et construction du composant **après clic** uniquement ; aucune requête ou action automatique à l'ouverture du grand atelier.
- I/O réseau **same-origin vers ComfyUI local** lorsqu'on utilise les boutons de projets. Le gestionnaire appelle `api.fetchApi` sous `/smartsvg/g22`, avec en-tête `X-SmartSVG-UI: 1` pour les mutations.
- Contrôles du nom, empreintes, copie de secours, refus d'archive corrompue et récupération sans perte restent gérés côté Python ; G3.2 ne les contourne pas.
- Le gestionnaire ne restaure pas de façon magique **le graphe ComfyUI, les masques édités et les connexions IMAGE** par le seul fait d'ouvrir un projet ; les routes existantes exposent des informations de reprise partielles.
- Sur un fichier HTML ouvert directement via `file://` ou un proxy tiers, le module externe peut ne pas fonctionner : afficher une explication, conserver les fonctions fictives offline.
- L'accès aux projets et l'inspecteur SVG réel G3.1 sont **indépendants** de la planche fictive de 12 escargots, avec aucune auto-exécution du moteur.

## Qualification

`tests/test_g32_project_panel_bridge.py` vérifie l'accès volontaire, les profils et DPI exactement acceptés par Python, les protections d'origine (confirmation de restauration, empreintes, POST UI) et les tests Node réels de `test_g22_project_panel.mjs`. Les anciennes suites G0/CPU/G3.0/G3.1 restent en place.

**Non encore testé** : ComfyUI Windows sur le PC cible, disponibilité de la route statique et de l'API G2.2 activée, volumes et photos réels, sortie Design Space, RTX 3070 et Cricut Explore 5.

## Suite

G3.3 : afficher les sujets et le dernier résultat d'inspection G2.6 depuis le contexte de projet, plutôt qu'une deuxième sélection fictive. Puis G3.4 : importer et normaliser les photos smartphone (EXIF/ICC) avant détourage IA explicite, en évitant les faux résultats silencieux.
