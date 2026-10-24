"""V19.7.1: new registered aliases for corrected trustworthy telemetry.

V19.7 users keep their original node IDs/workflows; replacement installs
should never load both extension directories at the same time.
"""
from .node_v197 import (
    SmartSVGStudioV197Express, SmartSVGStudioV197Expert,
    NODE_CLASS_MAPPINGS as HISTORIC_CLASSES,
    NODE_DISPLAY_NAME_MAPPINGS as HISTORIC_NAMES,
)

class SmartSVGStudioV1971Expert(SmartSVGStudioV197Expert):
    """Same source/export logic; enhanced profiler lives in telemetry_v197."""

class SmartSVGStudioV1971Express(SmartSVGStudioV197Express):
    """Same Express inputs; enhanced profiler lives in telemetry_v197."""

NODE_CLASS_MAPPINGS={**HISTORIC_CLASSES,
    'SmartSVGStudioV1971Express':SmartSVGStudioV1971Express,
    'SmartSVGStudioV1971Expert':SmartSVGStudioV1971Expert}
NODE_DISPLAY_NAME_MAPPINGS={**HISTORIC_NAMES,
    'SmartSVGStudioV1971Express':'SmartSVG V19.7.1 Express - profil fiable',
    'SmartSVGStudioV1971Expert':'SmartSVG V19.7.1 Expert - audit GPU'}
