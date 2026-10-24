# V21.1 — Audit en cinq passes

- Nouvelle interface `SmartSVGExpressV211` avec cinq réglages et 6 workflows clairs.
- Correctif de taille physique cohérente PNG 300/450 ppp et SVG pour toutes les sorties traitées par l'Express V21.1.
- Nouveau moteur de marge blanche : support agrandi avant dilatation des masques en bord de source.
- Refus de repli sans masque lorsque l'IA est choisie en mode obligatoire.
- Précontrôle de taille/nombre de masques avant copie GPU vers CPU.
- Publication atomique et suppression des fichiers de staging si l'export échoue.
- 27 tests adversariaux V21.1, 459 tests historiques conservés.
- Validation sur les cinq images réelles et trois masques synthétiques.
- Limites de segmentation réelle, qualité source et utilisation Cricut documentées.
