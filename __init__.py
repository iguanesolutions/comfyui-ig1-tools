from typing_extensions import override
from comfy_api.latest import ComfyExtension, io

from .fluxresolution import FluxResolution
from .fluxreport import FluxReport
from .resolution import ResolutionPacker, ResolutionProperties


class FluxToolsExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            ResolutionPacker,
            ResolutionProperties,
            FluxResolution,
            FluxReport,
        ]


async def comfy_entrypoint() -> FluxToolsExtension:
    return FluxToolsExtension()
