"""Stable, framework-independent boundaries between UI widgets and production.

No conversion or manipulation of images occurs here. Legacy ComfyUI signatures
and pixel generation remain unchanged by the architecture migration.
"""
from __future__ import annotations
from dataclasses import dataclass
import math

PROJECTS = (
    'Auto - conserver le visuel',
    'Sticker - contour du sujet',
    'Planche - 24 images (6x4)',
    'Planche - 12 images (4x3)',
    'Carte - visuel rectangulaire',
)
IA_MODES = ('Desactivee', 'Si disponible', 'Obligatoire')
DPI_OPTIONS = ('300', '450')

class ContractError(ValueError):
    """Invalid user intent before invoking any GPU or file operation."""

@dataclass(frozen=True)
class ExpressRequest:
    project: str
    width_mm: float
    dpi: int
    ai_mode: str
    external_masks: bool

    @classmethod
    def from_widgets(cls, *, projet, largeur_mm, qualite_ppp, ia_locale,
                     masques_objets=None):
        if projet not in PROJECTS:
            raise ContractError('Projet Express inconnu')
        if ia_locale not in IA_MODES:
            raise ContractError('Mode IA Express inconnu')
        if str(qualite_ppp) not in DPI_OPTIONS:
            raise ContractError('Résolution autorisée : 300 ou 450 ppp')
        if isinstance(largeur_mm, bool):
            raise ContractError('Largeur en millimètres invalide')
        try:
            width = float(largeur_mm)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ContractError('Largeur en millimètres invalide') from exc
        if not math.isfinite(width) or not 15 <= width <= 180:
            raise ContractError('Largeur attendue entre 15 et 180 mm')
        return cls(projet, width, int(qualite_ppp), ia_locale,
                   masques_objets is not None)

    @property
    def expected_mask_source(self):
        if self.external_masks:
            return 'MASQUES_EXTERNES_FOURNIS'
        if self.ai_mode == 'Desactivee':
            return 'AUCUNE_INFÉRENCE_INTERNE_DEMANDÉE'
        return 'INFÉRENCE_INTERNE_DEMANDÉE_NON_PROUVÉE'
