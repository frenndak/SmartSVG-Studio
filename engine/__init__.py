"""SmartSVG Studio V21.15.2 — conservative white-sheet correction + export QA."""
from .node_v21152 import NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS
WEB_DIRECTORY='./web/js'
__all__=['NODE_CLASS_MAPPINGS','NODE_DISPLAY_NAME_MAPPINGS','WEB_DIRECTORY']


# G2.2: private file operations are opt-in. They inherit ComfyUI's access
# control. DO NOT enable for an unauthenticated Internet-facing ComfyUI.
import os as _ss_os
if _ss_os.environ.get('SMARTSVG_ENABLE_PROJECT_API') == '1':
    try:
        from server import PromptServer as _ss_PromptServer
        import folder_paths as _ss_folder_paths
        from .project_routes_g22 import register_project_routes as _ss_register_routes
        _ss_register_routes(_ss_PromptServer.instance.routes,
                            _ss_folder_paths.get_output_directory())
    except (ImportError, AttributeError, OSError, ValueError) as _ss_exc:
        # Never break all historical nodes due to an optional project UI.
        print('SmartSVG G2.2: project API unavailable: '+type(_ss_exc).__name__)
