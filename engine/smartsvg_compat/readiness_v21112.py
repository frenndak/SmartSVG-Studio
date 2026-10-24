"""Read-only environment diagnostics. Never downloads models or runs inference."""
from __future__ import annotations
import importlib.util
from ..auto_segment_v192 import _registry_class, SegmentationUnavailable


def diagnose(*, registry=None, cuda=None, modules=None):
    """Probe declared capabilities, not model execution or GPU memory sufficiency."""
    if modules is None:
        modules={name:importlib.util.find_spec(name) is not None
                 for name in ('torch','cv2','PIL')}
    if registry is None:
        try:
            import nodes
            registry=nodes.NODE_CLASS_MAPPINGS
        except (ImportError, AttributeError):
            registry={}
    if cuda is None:
        try:
            import torch
            cuda=bool(torch.cuda.is_available())
        except Exception:
            cuda=False
    missing=[name for name,exists in modules.items() if not exists]
    provider='ABSENT'
    reason='Nœud SAM2Segment non trouvé dans le registre ComfyUI'
    if 'SAM2Segment' in registry:
        try:
            _registry_class(registry)
            provider='CONTRAT_COMPATIBLE_NON_EXECUTE'
            reason='Signature du nœud compatible ; modèle, poids, VRAM et inférence NON testés'
        except (SegmentationUnavailable,ValueError,TypeError) as e:
            provider='INCOMPATIBLE'
            reason=str(e)[:240]
    if missing:
        status='DEPENDANCES_MANQUANTES'
        advice='Installer les dépendances dans le Python de ComfyUI avant de traiter des images.'
    elif provider!='CONTRAT_COMPATIBLE_NON_EXECUTE':
        status='FONDS_SIMPLES_SEULEMENT'
        advice='Le fond blanc et les alpha fonctionnent ; pour les scènes difficiles, vérifier ComfyUI-RMBG et ses nœuds.'
    else:
        status='IA_A_TESTER_EN_REEL'
        advice='Lancer un test SAM2 sur une vraie image et mesurer la VRAM avant de considérer le détourage IA comme validé.'
    return {'version':'21.11.2','statut':status,
            'python_modules':dict(modules),'cuda_visible':bool(cuda),
            'rmbg_sam2':{'statut':provider,'details':reason},
            'modele_disponible_sur_disque':'NON_VERIFIE',
            'inference_effectuee':False,'compatibilite_frontend':'NON_TESTEE',
            'decoupe_cricut_physique':'NON_TESTEE','conseil':advice}
