from typing_extensions import override
from comfy_api.latest import ComfyExtension, io

from .api_server import run_api_server

from .node_utilities import ResolutionPacker, ResolutionProperties, AspectRatioProperties, ImageSelector
from .node_advisor import ResolutionAdvisor
from .node_qwen import QwenImageNativesResolutions
from .node_fluxreport import FluxReport
from .node_images import LoadImage


class IG1ToolsExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            ResolutionPacker,
            ResolutionProperties,
            AspectRatioProperties,
            ImageSelector,
            ResolutionAdvisor,
            QwenImageNativesResolutions,
            FluxReport,
            LoadImage,
        ]


async def comfy_entrypoint() -> IG1ToolsExtension:
    return IG1ToolsExtension()


run_api_server()
