"""SmartSVG V21.4: dependency-light contracts and reporting.

This package never imports torch, cv2, PIL, or the historical node graph.
"""
from .contracts import ExpressRequest, ContractError
from .reporting import render_express_report
__all__ = ['ExpressRequest', 'ContractError', 'render_express_report']
