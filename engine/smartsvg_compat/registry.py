"""Centralized, validated construction of the V21.4 ComfyUI compatibility map."""
from __future__ import annotations


def merge_registry(legacy_classes, legacy_names, current):
    """current maps class_id -> (class, human-readable label).

    Legacy class identities are never replaced. Rejecting a collision avoids
    silently breaking saved .json workflows.
    """
    classes=dict(legacy_classes)
    names=dict(legacy_names)
    for identifier,(cls,label) in current.items():
        if identifier in classes:
            raise ValueError('Collision identifiant nœud ComfyUI : '+identifier)
        if not identifier or not isinstance(label,str) or not label.strip():
            raise ValueError('Définition de nœud invalide')
        classes[identifier]=cls;names[identifier]=label
    if set(classes)!=set(names):
        raise ValueError('Description manquante pour certains nœuds')
    return classes,names
