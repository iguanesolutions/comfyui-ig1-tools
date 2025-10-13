from typing_extensions import override
from comfy_api.latest import ComfyExtension, io

from .node_utilities import ResolutionPacker, ResolutionProperties, AspectRatioProperties
from .node_advisor import ResolutionAdvisor
from .node_qwen import QwenImageNativesResolutions
from .node_fluxreport import FluxReport


class IG1ToolsExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            ResolutionPacker,
            ResolutionProperties,
            AspectRatioProperties,
            ResolutionAdvisor,
            QwenImageNativesResolutions,
            FluxReport,
        ]


async def comfy_entrypoint() -> IG1ToolsExtension:
    return IG1ToolsExtension()
