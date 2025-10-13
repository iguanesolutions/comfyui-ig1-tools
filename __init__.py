from typing_extensions import override
from comfy_api.latest import ComfyExtension, io

from .node_utilities import ResolutionPacker, ResolutionProperties, AspectRatioProperties
from .node_resolutionadvisor import ResolutionAdvisor
from .node_fluxreport import FluxReport


class IG1ToolsExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            ResolutionPacker,
            ResolutionProperties,
            AspectRatioProperties,
            ResolutionAdvisor,
            FluxReport,
        ]


async def comfy_entrypoint() -> IG1ToolsExtension:
    return IG1ToolsExtension()
