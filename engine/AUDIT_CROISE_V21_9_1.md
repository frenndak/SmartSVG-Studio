# SmartSVG Studio V21.9.1 — Contre-expertise multipasses (24/10/2026)

## Corrections vérifiables

1. **Masques multiples / mémoire** : suppression des N allocations de N-1 masques par objet dans `smartsvg_native/inspector.py`; une seule carte d’occupation multi-sujets est calculée pour toutes les détections de chevauchement. Masques originaux et exports inchangés.
2. **Alertes de bord** : diagnostic des pixels réellement sélectionnés sur les quatre bords, même si une *petite* composante, et non la principale, touche le cadre.
3. **Publication native** : sérialisation séquentielle des PNG d’inspection et libération des buffers entre chaque masque ; plafond strict inchangé (64 Mo/session, 192 Mo total, 8 sessions, nettoyage ultérieur).
4. **Copie Print Then Cut** : exécution répétée idempotente si le fichier d’import est déjà identique, calcul SHA-256 par blocs de 1 Mo ; création exclusive par lien dur sur le même volume pour éviter l’écrasement concurrent entre la vérification et l’installation du fichier. Si un PNG différent existe déjà sous le même nom, refus visible et avertissement sur la présence potentielle d’un ancien fichier. Aucune donnée utilisateur n’est écrasée.
5. **Inspecteur frontend** : une nouvelle exécution ferme les résultats visuels périmés et invalide les chargements asynchrones déjà en cours ; suppression du nœud ferme sa fenêtre, restaure l’état. Réutilisation du constructeur officiel `api.apiURL('/view')`.

## Invariants protégés

- Nœuds Express, cinq paramètres, ports, masques d’entrée et sorties Cricut inchangés ; aucun algorithme historique de segmentation ni de vectorisation réécrit.
- La copie directe Cricut du PNG de fabrication est rigoureusement identique ou est signalée non prête.
- Dossier `00_IMPORTER_DANS_CRICUT` conservé et conservation des rapports, SVG et variantes HD.

## Réserves honnêtes

- Les sept images de référence n’ont pas de masques IA validés. Une segmentation réelle sur la RTX 3070, une ouverture graphique dans l’installation ComfyUI de l’utilisateur et un essai Design Space suivi d’une découpe sont **hors de portée des tests locaux**.
- Les heuristiques de trous, chevauchements et passages étroits sont conservatrices ; une alerte « OK » n’est pas une certification physique de la découpe.
- La vraie édition vectorielle multicalque dans Cricut n’est pas fournie par un PNG « Flat Graphic ». Un SVG de découpe n’est pas un SVG multicouche éditable en couleurs.
- La taille A4 utile en Print Then Cut n’est pas un rectangle plein ; Design Space calcule les repères et limites selon machine et format choisi. Contrôler à l’écran.
- La fenêtre d’inspection et l’éditeur de correction restent deux vues distinctes. Une fusion doit être conçue et testée séparément pour ne pas casser le contrat des masques.
