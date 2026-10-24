# Contre-expertise V11 → V12

## Défauts et incertitudes traités

1. **Risque de fichier partiel “prêt”** : en V11, des fichiers PNG/SVG étaient écrits avant la dernière étape d'analyse ; un crash tardif pouvait laisser des éléments à l'emplacement de travail. En V12, ils restent dans un dossier temporaire ; publication groupée seulement après une validation de fichiers sur disque.
2. **Sorties difficiles à retrouver** : les nombreux `element_XX_...` étaient mélangés aux planches. Ils sont désormais archivés sous `DETAILS_ELEMENTS`.
3. **Confusion de copies** : élimination des anciens alias d'impression/découpe en double ; seule la planche d'import principale est mise en avant.
4. **Absence de manifeste vérifiable** : chaque export possède maintenant une liste SHA-256 des fichiers publiés et un `PRET_V12.json` écrit en dernier.
5. **Détails fins** : ajout d'une analyse par ouverture morphologique d'environ 0,8 mm. Il s'agit d'une heuristique de fragilité, non d'une garantie de découpe.
6. **Faux avertissement de qualité** : l'arrondi de marge imposé par la grille de pixels est classé comme une information, pas comme une alerte de production.
7. **Rapport périmé / mauvais numéro de version** : `rapport_V12.json` et son statut référence désormais le dossier final ; l'ancienne clé de compatibilité indique le nouveau rapport.
8. **Objets IA** : ne pas confondre détection de silhouette et Magic Layers. Le SVG couleur n'invente pas de reconstruction anatomique.

## Tests automatiques actuels

- Image seule, planche 4 × 3 réelle, planche transparente irrégulière, trou intérieur, contact diagonal, masques vides, collision de stickers, fond presque uniforme.
- Absence d'IA forcée, masque IA forcé rejeté, masque forcé accepté (simulateur), une instance IA simulée pour plusieurs dessins.
- Erreur injectée avant la première sauvegarde et rejet injecté après génération : aucun PNG imprimable publié en sortie finale.
- Contrôle XML SVG, limite 5 000 chemins, absence de bitmap, largeur physique, empreintes SHA-256.

## Reste à prouver avant une version “production”

- Installation réelle de la V12 sur Windows 11 et plugin RMBG actuellement installé.
- Test CUDA / VRAM / redémarrage en cas de mémoire GPU insuffisante.
- Essai réel Print Then Cut (alignement capteur, papier autocollant, calibrage, lame, imprimante).
- Test des sources très complexes (photos, images semi-transparentes, plusieurs personnages collés, feuilles sans grille).
- Import du SVG éditable dans Design Space sur le poste de l'utilisateur ; il y a une différence entre XML vectoriel valide et ergonomie réelle des groupes.

**Conclusion :** V12 distribuable comme version bêta expérimentale ; aucun succès de découpe physique n'est présumé.
