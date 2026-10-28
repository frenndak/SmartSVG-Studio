# Audit de promotion — SmartSVG Roadmap V3.3

**Date :** 28 octobre 2026. **Nature :** audit documentaire indépendant, non homologation du logiciel.
**PR :** #60. **Référence examinée :** `e74dbd8f1a8776f2f7371b724b40c1e6446cf670` (l'audit lui-même est une modification documentaire supplémentaire).

## Contrôles reproductibles effectués

| Contrôle | Résultat | Limite |
| --- | --- | --- |
| Familles F01 à F15 du maître | 15/15 présentes | Présence textuelle, pas statut d'implémentation |
| Jalons G0 à G9 | 10/10 présents | Aucun gate logiciel validé par ce seul contrôle |
| Parcours P01 à P10 | 10/10 avec sections | Critères matériels restent à exécuter |
| Tickets historiques S-001 à S-101 | 101/101 présents dans la table détaillée | Correspondance d'identifiants et critère canonique |
| Exigences R33-001 à R33-040 | 40/40 dans le registre | Preuves initialement non vérifiées |
| Annexe V3.3 d'héritage | Contenu historique intégral identique à la V3.2 originale, après le préambule | L'archive historique gelée demeure intacte |
| Liens locaux entre les six fichiers de la PR | Aucune cible manquante constatée | Vérification des liens Markdown locaux, pas des liens externes |
| Diff Git contre main à la date d'audit | Six fichiers ajoutés, aucun chemin protégé modifié | Vérification à répéter au HEAD final |

## CI GitHub : blocage de publication

- Aucun workflow GitHub Actions n'était associé au HEAD de la PR #60 au contrôle.
- Les triggers `pull_request.paths` des workflows existants `engine-cpu-smoke.yml`, `g0-admission-tests.yml` et `public-readonly-preflight.yml` ne correspondent pas aux nouveaux fichiers `docs/ROADMAP_*v3_3.md` ou `docs/superpowers/*/2026-10-28-roadmap-v3-3*.md`.
- Le protocole `AGENTS.md` exige une **CI pertinente fraîche et verte**, une contre-expertise, la comparaison au `main` courant et un rollback avant intégration, même en session utilisateur expressément autorisée.
- Les six échecs Windows/292 annoncés dans le texte initial de la PR sont **des constats rapportés par Codex**, non reproduits dans cette session ni qualifiés par une CI verte sur le HEAD actuel.
- La lecture des règles de protection `main` renvoie `403 Resource not accessible by integration`. Leur caractère obligatoire ne peut pas être vérifié par la connexion GitHub présente.

**Décision : `NO-GO MERGE` tant qu'une vérification CI pertinente au HEAD final n'est pas obtenue et que les éventuels gates bloquants ne sont pas résolus.** Les contrôles documentaires locaux sont positifs ; ils ne doivent jamais être présentés comme des checks GitHub officiels.

## Publication et retour arrière

1. Mettre en place, par PR **séparée** explicitement autorisée, une validation documentaire automatisée couvrant les trois registres, le maître et l'annexe d'héritage.
2. Vérifier le head final et `main` au moment de décider ; qualifier toute suite rouge sans ignorer les échecs.
3. Faire fusionner #60 uniquement selon les conditions effectives du dépôt ; V3.3 devient alors le nouveau maître actif.
4. Par **autre modification de gouvernance protégée** validée, basculer `AGENTS.md` et le producteur planifié vers `docs/ROADMAP_MASTER_v3_3.md`, sans réécrire la V3.2 ni son manifeste.
5. Rollback : revert documenté de la PR de publication et de toute modification de gouvernance dépendante. Aucun fichier produit ou projet utilisateur n'est migré par ce changement documentaire.

**Invariants :** ne prétendre ni à une validation Design Space, ni à un test réel RTX 3070, ni à une découpe physique ; ne déplacer aucune preuve privée vers le dépôt public.

## Réouverture du gate CI après PR #61 (28 octobre 2026)

La PR [#61](https://github.com/frenndak/SmartSVG-Studio/pull/61) a été **fusionnée** sur `main` au commit `96d90180d5528d12a4aa43bd4775ad5f87488f74`. Elle apporte le workflow isolé `.github/workflows/roadmap-v3-3-gate.yml` pour les chemins documentaires V3.3. Son propre preflight était **SUCCESS** sur HEAD `622bde14280ad6087b22e24127f8ec58a35ee0fd` ; l'étape de validation des documents V3.3 y était **SKIPPED**, car ceux-ci ne figuraient pas dans #61.

Le présent commit sur #60 vise à déclencher le nouveau workflow pour les **vrais documents V3.3**. Tant que le contrôle n'a pas abouti au SHA exact, la décision de fusion de #60 reste **NO-GO**. Les résultats doivent être consignés séparément, puis le `main` courant et les protections doivent être vérifiés.

## Correction du périmètre du validateur (28 octobre 2026)

La PR [#62](https://github.com/frenndak/SmartSVG-Studio/pull/62) a été **fusionnée** au commit `a1c7bf5f5f7240b1e95c8f8dc79024e00f93381a`, avec un preflight GitHub **SUCCESS** au SHA source `8857def003467c28d0fee6a5d3d12a230dab5e3f`. Elle a corrigé le faux doublon causé par les mentions de synthèse S-076 et S-085 : l'exhaustivité et l'unicité restent strictes dans les dossiers canoniques.

Cette modification de #60 redéclenche la validation CI documentaire corrigée. Aucun PASS pour les documents V3.3 ne doit être déclaré avant lecture du résultat GitHub sur le nouveau HEAD.
