# G3.3e-a — Liaison probante lecture seule sujet ↔ masque float32

**Référence :** issue #67, roadmap opérationnelle V3.3, dépend de G3.3d-a (#59) et G3.3d-b (#66). Ce document décrit uniquement le micro-lot **sans écriture**, pas une certification Cricut.

## Contrats réellement existants

- `smartsvg-project/1` / G1.2 : `Subject(subject_id,source_id,mask_id,bbox_px,accessory_ids)` est un record **facultatif**. Le projet G2.4 peut être sain sans aucun `Subject` enregistré ; on ne fabrique donc pas de `subject_id`.
- G2.4 : `base_masks_f32_v1` contient un tenseur exact **[N,H,W] little-endian float32** et les masques `base-mask-00`, `base-mask-01` etc. Les `Mask.sha256` d'archive sont les empreintes des **PNG L8 d'inspection**, et **ne sont pas les empreintes des octets float32**.
- G2.6 : `sujets[].numero` est un numéro d'affichage **1-based** issu de la même séquence ordonnée. L'empreinte `source_sha256` (IMAGE+MASK) lie l'ordre et les octets à l'exécution, mais n'attribue pas une identité sémantique durable.
- G3.3d : le nom `project_name`, la révision SHA256 de l'archive et le fingerprint commun sont vérifiés en GET avant transfert, avant confirmation et après callback.

## Métadonnées de preuve exposées dans l'inspection existante

Le champ additionnel **facultatif** `project.base_masks.mask_identity` (version 1) est produit **uniquement depuis un projet sain avec snapshot G2.4**, sans charger les matrices dans le navigateur. Chaque entrée donne :
- `mask_index` : index 0-based exact dans le tenseur G2.4 ;
- `mask_id` : véritable identifiant d'archive `base-mask-XX`, lié à la position ;
- `mask_sha256_float32` : SHA256 **de la tranche brute float32**, non du PNG L8 ;
- `has_foreground` : au moins une valeur strictement positive, contrôlée en float32 ;
- `subject_id` : identifiant G1.2 **seulement s'il existe une unique référence à ce masque**, sinon `null` ;
- `accessory_ids` : relations existantes depuis le record `Subject`, jamais déduites du visuel ;
- `subject_ambiguous` : plusieurs records référencent le même masque, à refuser lors d'une liaison exploitable.

Les données sont calculées côté serveur après validation de l'archive, à partir de la ressource float32 compressée et bornée. L'inspection contrôle que la révision n'a pas changé pendant la lecture. Aucun pixel ni tableau float32 n'est envoyé dans le rapport.

## Liaison et refus

Le nœud source joint un `mask_catalog` uniquement si les métadonnées sont présentes et **toutes** cohérentes avec la révision, le nombre, les dimensions et le fingerprint. Les SHA par masque doivent être uniques, les masques non vides, l'ordre exact, les identifiants valides, les accessoires correctement référencés ; sinon la liaison est refusée avec une explication en français, sans repli vers une association inventée.

Le transfert `BroadcastChannel` reste **même origine et non authentifié cryptographiquement** : ce catalogue est une **preuve de concordance locale**, non une signature contre une extension ComfyUI malveillante. Toute confirmation exécutable continue à passer dans le nœud source et ses relectures de révision G3.3d.

L'Atelier indique `mask_id` et le préfixe du digest float32 pour chaque sujet, ou « Identité de sujet durable absente » quand aucun record `Subject` n'existe. Pour une ancienne inspection sans champ `mask_identity`, l'ancien verrouillage G3.3d sur **la révision globale du projet** reste opérationnel et l'absence de preuve par masque est explicitement affichée.

**Limite structurante :** un digest de contenu n'est pas un ID de sujet stable entre retouches. Un déplacement ou une modification de pixels peut changer l'empreinte, et un `mask_id` fondé sur une position peut changer avec l'ordre. Établir l'identité durable, les migrations et la reprise d'édition constitue un travail séparé, à soumettre à validation avant toute écriture G3.3e-b.

## Preuves à obtenir

Tests synthétiques positifs : octets float32 inchangés, associations exactes, sujet explicite, transport JSON normalisé, compatibilité anciennes archives.

Tests négatifs : deux masques identiques, masque vide, indices permutés, digest altéré, source/projet/révision différents, duplications d'ID, accessoires inconnus, session expirée, archive corrompue.

Les CI G0, CPU et preflight vérifient seulement les chemins automatisés au commit exact. Installation Windows ComfyUI, vrai navigateur, inférence RTX 3070, Design Space et coupe Explore 5 : **NON TESTÉS**. Rollback : revert du commit squash de la PR correspondante, sans migration ni écriture de projet.
