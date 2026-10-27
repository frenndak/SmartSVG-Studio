# P1 — Protection des sources gelées contre les renommages Git

Ce micro-lot reprend de l'ancienne PR #13 **uniquement** le contrôle des chemins protégés qu'une commande Git avec détection de renames pouvait contourner.

## Défaut

Le filtre `git diff --cached --name-only -z` peut n'afficher **que la destination** lors d'un renommage. Exemple : un agent renomme `source-releases/source.zip` en `engine/renamed.txt` : le filtre pouvait alors manquer la suppression du fichier gelé.

## Correction

La vérification est désormais `git diff --cached --name-only --no-renames -z` : elle inspecte séparément l'ancien chemin supprimé et le nouveau chemin ajouté. Les patterns interdisent explicitement `source-releases/**` et la provenance V21.15.2. Le garde agit **avant git commit et git push** dans le workflow Codex facultatif.

Quatre tests reproduisent la situation en créant un dépôt Git synthétique : renommage du master roadmap, de la provenance, du ZIP et du marqueur READY => tous bloqués ; renommage d'un fichier normal sous `engine/` => admis. Aucun vrai fichier source n'est supprimé ou déplacé.

Ne change ni les accès externes, ni les compteurs budgétaires P1, ni les contrôles du préflight public ni les sources gelées. La CI ne valide pas les performances Windows/GPU/Cricut.
