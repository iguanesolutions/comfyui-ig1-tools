from typing_extensions import override
from comfy_api.latest import ComfyExtension, io

from .fluxresolution import FluxResolution


class FluxResolutionExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            FluxResolution,
        ]


# ComfyUI calls this to load your extension and its nodes.
async def comfy_entrypoint() -> FluxResolutionExtension:
    return FluxResolutionExtension()
