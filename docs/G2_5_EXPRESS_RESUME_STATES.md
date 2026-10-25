# SmartSVG — G2.5 : états d’interface et reprise guidée sans action cachée

**Référence immuable :** docs/ROADMAP_MASTER_v3_2.md, G2.5 — architecture d’écran, états vide/chargement/erreur, panneau contextualisé. Cette PR s’empile sur G2.4 (#22) et ne modifie aucun composant de calcul, schéma d’archive, workflow ComfyUI, export SVG/PNG ou matériel Cricut.

## Expérience utilisateur ajoutée

L’espace « Projet .smartsvg » d’Express dispose désormais d’un panneau déroulant natif « Reprendre ce projet · diagnostic » permettant de comprendre son état sans connaître la structure ZIP ou les identifiants des nœuds. Le panneau présente les 4 étapes : image source, masques float32 exacts, traits V21.6, connexion du graphe ComfyUI.

Il distingue rigoureusement :

- EMPTY : aucun projet choisi/chargé ;
- LOADING : inspection serveur en cours ;
- ERROR : requête refusée ou impossible ;
- RECOVERABLE : principale absente/invalide et secours SHA-256 valide, avec confirmation obligatoire ;
- UNAVAILABLE : données illisibles, aucune restauration présumée ;
- UNKNOWN : rapport incomplet, même s’il affirme HEALTHY ;
- SOURCE_ONLY : PNG présent mais ni masques exacts ni traits ;
- STROKES_ONLY : PNG et retouches ; les masques de base exacts manquent ;
- MASKS_ONLY : PNG et masques float32 exacts ; retouches non archivées ;
- COMPLETE_MANUAL : source, masques et traits d’édition présents et fingerprints concordants, **mais graphe non reconnecté** ;
- INCOMPATIBLE : metadata de masques/retouches incohérentes, mauvais count ou source fingerprint.

L’interface reste un panneau compact replié par défaut dans le flux Express. Elle s’ouvre automatiquement en cas de secours valide, de contradiction ou de « données présentes à reconnecter ». Quatre étapes restent visibles sur demande, avec statuts « conservé », « à compléter » ou « manuel ». Éléments clavier natifs `details/summary`, statut `aria-live`, débordement borné des consignes et champ sélectionnable SHA-256.

**Bouton actif supplémentaire :** « Copier l’empreinte de révision » pour renseigner manuellement le nœud G2.4. Il n’est activé qu’après ouverture d’une archive vérifiée, jamais pour un rapport incomplet ou incompatible. Fallback utilisable par sélection/copier du champ si le presse-papiers du navigateur est indisponible.

## Contrat fail-closed

- L’inspection et la copie SHA-256 ne sont disponibles que pour les versions réellement vérifiées par le backend.
- La restauration du secours nécessite toujours un état RECOVERABLE avec SHA-256 du secours valide et une confirmation explicite. Les demandes de restauration ne sont jamais créées automatiquement.
- Les réponses de réseau arrivant après un changement de nom de projet sont invalidées. L’ancien résultat ne remplit pas le nouveau panneau et ne rend aucun bouton actif. Les mises à jour de notes/création/restauration ne présentent pas une réussite sur un projet différent.
- Le projet G2.2/2.4 est inspecté via le **même endpoint existant** `GET /smartsvg/g22/project` ; aucune nouvelle permission, route, dépendance, API réseau extérieure ou stockage client.
- Pas d’injection HTML, pas de changement de ports, aucun lancement de workflow, aucun « prêt Cricut ».
- COMPLETE_MANUAL signifie uniquement que les éléments **sauvegardés** sont cohérents ; cela ne signifie ni que le graphe ComfyUI est automatiquement restauré, ni que le Print Then Cut est validé dans Design Space.

## Gate

Tests Node.js sur la logique pure de 11 états, combinaisons source/masques/retouches, cohérence fingerprint, recovery, rapport malformé, interdiction de déclarer une découpe. Tests DOM réels simulés sur l’interface existante : 5 boutons fonctionnels, secours confirmé, copie SHA-256, panneau compact et requête en vol après changement de projet. Suites historiques G1–G2 et CPU smoke sur le commit HEAD exact.

## Limitations explicites

Pas de mesure matérielle à 1366×768 et 1920×1080, ni de session ComfyUI Windows/RTX 3070 réelle, ni de navigation clavier réelle au navigateur : seule la présence de contrôles natifs et leur comportement simulé sont couverts. Aucune reconnexion automatique du workflow. Le raccordement réel de IMAGE/MASK/retouches aux nœuds et la reprise d’activité complète sont des lots futurs de la roadmap (notamment G2.9), sous contrôle de révision et consentement explicite.

**Décision de diffusion :** PR en brouillon pour revue, sans fusion et sans déclarer une nouvelle archive d’installation.
